"""Native, evidence-gated skill improvement for Continuity.

The operational contract in SKILL.md is immutable to this lifecycle. Usage-derived
changes are staged only against references/learned-playbook.md, evaluated on fixed
validation/test evidence, and packaged after explicit human review. Nothing here
mutates an installed skill or authorizes execution.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import runtime as runtime_lib


class SkillImprovementError(RuntimeError):
    pass


REQUIRED_INVARIANTS = {
    "authority-preserved",
    "privacy-preserved",
    "protected-contract-unchanged",
    "state-accuracy-preserved",
}
OUTCOMES = {"success", "failure", "mixed", "blocked", "unknown"}
REVIEW_DISPOSITIONS = {"approved", "rejected", "held"}
PLAYBOOK_HEADER = "# Learned Playbook"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise SkillImprovementError(f"Invalid {label}: use 1-128 letters, numbers, dots, underscores, or hyphens")
    return value


def _private_root(root: Path, config: dict[str, Any]) -> Path:
    relative = Path(config.get("private_dir", ".continuity/private"))
    if relative.is_absolute():
        raise SkillImprovementError("private_dir must be project-relative")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise SkillImprovementError("private_dir escapes the project root")
    return resolved / "skill-improvement"


def _input_path(value: str, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise SkillImprovementError(f"{label} does not exist: {path}")
    return path


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillImprovementError(f"Cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SkillImprovementError(f"{label} must be a JSON object")
    return value


def _validate(value: dict[str, Any], schema_root: Path, name: str, label: str) -> None:
    try:
        runtime_lib.validate_schema_file(value, schema_root / name, label)
    except (OSError, json.JSONDecodeError, runtime_lib.RuntimeIntegrityError) as exc:
        raise SkillImprovementError(str(exc)) from exc


def _sha(path: Path) -> str:
    return runtime_lib.sha256_file(path)


def _skill_paths(root: Path, skill_name: str) -> tuple[Path, Path]:
    skill_name = _identifier(skill_name, "skill name")
    directory = root / ".agents" / "skills" / skill_name
    skill = directory / "SKILL.md"
    playbook = directory / "references" / "learned-playbook.md"
    if not skill.is_file():
        raise SkillImprovementError(f"Installed skill is missing: {skill_name}")
    if not playbook.is_file():
        raise SkillImprovementError(f"Installed learned playbook is missing: {skill_name}")
    return skill, playbook


def _strip_integrity(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "_integrity"}


def _usage_records(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    path = _private_root(root, config) / "usage.jsonl"
    try:
        return [_strip_integrity(item) for item in runtime_lib.load_jsonl(path)]
    except runtime_lib.RuntimeIntegrityError as exc:
        raise SkillImprovementError(str(exc)) from exc


def _proposal_dir(root: Path, config: dict[str, Any], proposal_id: str) -> Path:
    return _private_root(root, config) / "proposals" / _identifier(proposal_id, "proposal ID")


def baseline(root: Path, config: dict[str, Any], args: Any) -> dict[str, Any]:
    skill, playbook = _skill_paths(root, args.skill_name)
    return {
        "skill_name": args.skill_name,
        "skill_path": str(skill.relative_to(root)),
        "playbook_path": str(playbook.relative_to(root)),
        "skill_sha256": _sha(skill),
        "playbook_sha256": _sha(playbook),
        "protected_contract": "SKILL.md",
        "evolvable_layer": "references/learned-playbook.md",
    }


def record_usage(root: Path, config: dict[str, Any], args: Any, schema_root: Path) -> dict[str, Any]:
    source = _read_object(_input_path(args.input, "usage input"), "usage input")
    skill_name = _identifier(str(source.get("skill_name", "")), "skill name")
    skill, playbook = _skill_paths(root, skill_name)
    source.setdefault("recorded_at", _now())
    if not source.get("usage_id"):
        material = "\x1f".join(
            [skill_name, str(source.get("recorded_at", "")), str(source.get("task_kind", "")), str(source.get("summary", ""))]
        )
        source["usage_id"] = "usage-" + hashlib.sha256(material.encode()).hexdigest()[:12]
    source["usage_id"] = _identifier(str(source["usage_id"]), "usage ID")
    source["execution_authorized"] = False
    if source.get("outcome") not in OUTCOMES:
        raise SkillImprovementError(f"Unsupported usage outcome: {source.get('outcome')}")
    if source.get("privacy_reviewed") is not True:
        raise SkillImprovementError("Usage must be sanitized and privacy_reviewed before recording")
    _validate(source, schema_root, "skill-usage.schema.json", "skill usage")
    if source["skill_sha256"] != _sha(skill) or source["playbook_sha256"] != _sha(playbook):
        raise SkillImprovementError("Usage hashes do not match the currently installed skill and playbook")

    existing = {item["usage_id"]: item for item in _usage_records(root, config)}
    if source["usage_id"] in existing:
        if existing[source["usage_id"]] != source:
            raise SkillImprovementError(f"Usage ID already exists with different content: {source['usage_id']}")
        return {**source, "deduplicated": True}
    try:
        runtime_lib.append_integrity_jsonl(_private_root(root, config) / "usage.jsonl", source)
    except runtime_lib.RuntimeIntegrityError as exc:
        raise SkillImprovementError(str(exc)) from exc
    return {**source, "deduplicated": False}


def patterns(root: Path, config: dict[str, Any], args: Any) -> dict[str, Any]:
    skill_name = _identifier(args.skill_name, "skill name")
    _skill_paths(root, skill_name)
    minimum = max(1, int(args.min_count))
    records = [item for item in _usage_records(root, config) if item.get("skill_name") == skill_name]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        for key in record.get("pattern_keys", []):
            grouped.setdefault(key, []).append(record)
    results: list[dict[str, Any]] = []
    for key, members in grouped.items():
        if len(members) < minimum:
            continue
        signals = [member.get("signals", {}) for member in members]
        adverse = sum(1 for member in members if member.get("outcome") in {"failure", "mixed", "blocked"})
        corrections = sum(1 for signal in signals if signal.get("user_corrected"))
        retries = sum(int(signal.get("retries", 0)) for signal in signals)
        tool_failures = sum(int(signal.get("tool_failures", 0)) for signal in signals)
        kind = "improvement-opportunity" if adverse or corrections or retries or tool_failures else "successful-pattern"
        results.append(
            {
                "pattern_key": key,
                "kind": kind,
                "occurrences": len(members),
                "adverse_outcomes": adverse,
                "user_corrections": corrections,
                "retries": retries,
                "tool_failures": tool_failures,
                "first_recorded_at": min(member["recorded_at"] for member in members),
                "last_recorded_at": max(member["recorded_at"] for member in members),
                "usage_refs": sorted(member["usage_id"] for member in members),
                "execution_authorized": False,
            }
        )
    results.sort(key=lambda item: (-item["occurrences"], -item["adverse_outcomes"], item["pattern_key"]))
    return {"skill_name": skill_name, "minimum_count": minimum, "usage_count": len(records), "patterns": results}


def _validate_candidate_playbook(text: str) -> None:
    if not text.startswith(PLAYBOOK_HEADER + "\n"):
        raise SkillImprovementError(f"Candidate playbook must start with {PLAYBOOK_HEADER!r}")
    if len(text.splitlines()) > 500:
        raise SkillImprovementError("Candidate learned playbook exceeds 500 lines")
    forbidden = [
        r"(?i)execution_authorized\s*[:=]\s*true",
        r"(?i)disable\s+(?:the\s+)?(?:safety|security|privacy|approval)",
        r"(?i)ignore\s+(?:the\s+)?(?:continuity\s+)?contract",
        r"(?i)force[- ]push",
        r"(?i)auto[- ]merge",
    ]
    if any(re.search(pattern, text) for pattern in forbidden):
        raise SkillImprovementError("Candidate playbook contains a prohibited authority or safety instruction")


def propose(root: Path, config: dict[str, Any], args: Any, schema_root: Path) -> dict[str, Any]:
    proposal = _read_object(_input_path(args.input, "proposal input"), "proposal input")
    candidate_path = _input_path(args.candidate, "candidate playbook")
    skill_name = _identifier(str(proposal.get("skill_name", "")), "skill name")
    skill, playbook = _skill_paths(root, skill_name)
    proposal_id = _identifier(str(proposal.get("proposal_id", "")), "proposal ID")
    proposal["target_layer"] = "evolvable-playbook"
    proposal["execution_authorized"] = False
    proposal.setdefault("created_at", _now())
    _validate(proposal, schema_root, "skill-improvement-proposal.schema.json", "skill improvement proposal")
    if proposal["base_skill_sha256"] != _sha(skill):
        raise SkillImprovementError("Proposal base_skill_sha256 does not match the protected SKILL.md")
    if proposal["base_playbook_sha256"] != _sha(playbook):
        raise SkillImprovementError("Proposal base_playbook_sha256 does not match the learned playbook")
    if len(proposal["operations"]) > proposal["edit_budget"]:
        raise SkillImprovementError("Proposal operations exceed edit_budget")
    if not REQUIRED_INVARIANTS.issubset(set(proposal["evaluation_plan"]["required_invariants"])):
        missing = sorted(REQUIRED_INVARIANTS - set(proposal["evaluation_plan"]["required_invariants"]))
        raise SkillImprovementError(f"Proposal evaluation plan is missing protected invariants: {missing}")

    usage = {item["usage_id"]: item for item in _usage_records(root, config)}
    unknown = sorted(set(proposal["usage_refs"]) - set(usage))
    if unknown:
        raise SkillImprovementError(f"Proposal references unknown usage records: {unknown}")
    mismatched = sorted(ref for ref in proposal["usage_refs"] if usage[ref].get("skill_name") != skill_name)
    if mismatched:
        raise SkillImprovementError(f"Proposal references usage from another skill: {mismatched}")
    proposal_usage_refs = set(proposal["usage_refs"])
    for index, operation in enumerate(proposal["operations"], start=1):
        unscoped = sorted(set(operation["usage_refs"]) - proposal_usage_refs)
        if unscoped:
            raise SkillImprovementError(
                f"Proposal operation {index} references usage outside the proposal: {unscoped}"
            )
    backed_patterns = {key for ref in proposal["usage_refs"] for key in usage[ref].get("pattern_keys", [])}
    unbacked = sorted(set(proposal["pattern_keys"]) - backed_patterns)
    if unbacked:
        raise SkillImprovementError(f"Proposal pattern keys lack usage evidence: {unbacked}")
    for pattern_key in proposal["pattern_keys"]:
        occurrences = sum(pattern_key in usage[ref].get("pattern_keys", []) for ref in proposal["usage_refs"])
        if occurrences < 2:
            raise SkillImprovementError(
                f"Proposal pattern is not recurring in at least two usage records: {pattern_key}"
            )
    evaluation_plan = proposal["evaluation_plan"]
    overlap = sorted(set(evaluation_plan["validation_case_refs"]) & set(evaluation_plan["test_case_refs"]))
    if overlap:
        raise SkillImprovementError(f"Validation and test cases must be disjoint: {overlap}")

    candidate_text = candidate_path.read_text(encoding="utf-8")
    _validate_candidate_playbook(candidate_text)
    candidate_sha = hashlib.sha256(candidate_text.encode()).hexdigest()
    if candidate_sha == _sha(playbook):
        raise SkillImprovementError("Candidate playbook is identical to the current playbook")
    proposal["candidate_playbook_sha256"] = candidate_sha
    target = _proposal_dir(root, config, proposal_id)
    if target.exists():
        stored = _read_object(target / "proposal.json", "stored proposal")
        if stored != proposal or (target / "candidate-learned-playbook.md").read_text(encoding="utf-8") != candidate_text:
            raise SkillImprovementError(f"Proposal ID already exists with different content: {proposal_id}")
        return {**proposal, "status": derive_status(target), "deduplicated": True}
    runtime_lib.atomic_write_json(target / "proposal.json", proposal)
    runtime_lib.atomic_write_text(target / "base-SKILL.md", skill.read_text(encoding="utf-8"))
    runtime_lib.atomic_write_text(target / "base-learned-playbook.md", playbook.read_text(encoding="utf-8"))
    runtime_lib.atomic_write_text(target / "candidate-learned-playbook.md", candidate_text)
    runtime_lib.append_integrity_jsonl(
        _private_root(root, config) / "events.jsonl",
        {"event": "skill-improvement.proposed", "proposal_id": proposal_id, "skill_name": skill_name, "at": proposal["created_at"]},
    )
    return {**proposal, "status": "proposed", "deduplicated": False}


def _load_proposal(target: Path) -> dict[str, Any]:
    path = target / "proposal.json"
    if not path.is_file():
        raise SkillImprovementError(f"Unknown skill-improvement proposal: {target.name}")
    return _read_object(path, "stored proposal")


def derive_status(target: Path) -> str:
    if (target / "review.json").is_file():
        return _read_object(target / "review.json", "review record")["disposition"]
    if (target / "evaluation.json").is_file():
        return "review-ready" if _read_object(target / "evaluation.json", "evaluation record")["accepted"] else "rejected-by-gate"
    return "proposed"


def evaluate(root: Path, config: dict[str, Any], args: Any, schema_root: Path) -> dict[str, Any]:
    target = _proposal_dir(root, config, args.proposal_id)
    proposal = _load_proposal(target)
    result = _read_object(_input_path(args.result_file, "evaluation result"), "evaluation result")
    result["proposal_id"] = proposal["proposal_id"]
    result.setdefault("evaluated_at", _now())
    _validate(result, schema_root, "skill-improvement-evaluation.schema.json", "skill improvement evaluation")
    if result["candidate_playbook_sha256"] != proposal["candidate_playbook_sha256"]:
        raise SkillImprovementError("Evaluation candidate hash does not match the staged proposal")
    evaluation_plan = proposal["evaluation_plan"]
    if result["metric"] != evaluation_plan["metric"]:
        raise SkillImprovementError("Evaluation metric does not match the staged proposal")
    if set(result["validation"]["case_refs"]) != set(evaluation_plan["validation_case_refs"]):
        raise SkillImprovementError("Evaluation validation cases do not match the fixed proposal cases")
    if set(result["test"]["case_refs"]) != set(evaluation_plan["test_case_refs"]):
        raise SkillImprovementError("Evaluation test cases do not match the fixed proposal cases")
    invariant_ids = [item["invariant_id"] for item in result["invariants"]]
    if len(invariant_ids) != len(set(invariant_ids)):
        raise SkillImprovementError("Evaluation invariant IDs must be unique")
    invariant_map = {item["invariant_id"]: item for item in result["invariants"]}
    required = set(evaluation_plan["required_invariants"])
    missing = sorted(required - set(invariant_map))
    if missing:
        raise SkillImprovementError(f"Evaluation is missing required invariants: {missing}")
    validation = result["validation"]
    test = result["test"]
    minimum_gain = evaluation_plan["minimum_validation_gain"]
    validation_gain = validation["candidate_score"] - validation["baseline_score"]
    validation_passed = validation_gain >= minimum_gain and validation["candidate_score"] > validation["baseline_score"]
    test_passed = test["candidate_score"] >= test["baseline_score"]
    invariants_passed = all(invariant_map[item]["status"] == "passed" for item in required)
    accepted = validation_passed and test_passed and invariants_passed and not result["regressions"]
    result["accepted"] = accepted
    result["gate"] = {
        "validation_gain": validation_gain,
        "minimum_validation_gain": minimum_gain,
        "validation_passed": validation_passed,
        "test_passed": test_passed,
        "invariants_passed": invariants_passed,
        "regressions_absent": not result["regressions"],
    }
    path = target / "evaluation.json"
    if path.exists():
        stored = _read_object(path, "stored evaluation")
        if stored != result:
            raise SkillImprovementError("Proposal already has a different evaluation")
        return {**result, "deduplicated": True}
    runtime_lib.atomic_write_json(path, result)
    runtime_lib.append_integrity_jsonl(
        _private_root(root, config) / "events.jsonl",
        {"event": "skill-improvement.evaluated", "proposal_id": proposal["proposal_id"], "accepted": accepted, "at": result["evaluated_at"]},
    )
    return {**result, "deduplicated": False}


def review(root: Path, config: dict[str, Any], args: Any) -> dict[str, Any]:
    target = _proposal_dir(root, config, args.proposal_id)
    proposal = _load_proposal(target)
    evaluation_path = target / "evaluation.json"
    if not evaluation_path.is_file():
        raise SkillImprovementError("Proposal must be evaluated before human review")
    evaluation = _read_object(evaluation_path, "stored evaluation")
    disposition = args.disposition
    if disposition not in REVIEW_DISPOSITIONS:
        raise SkillImprovementError(f"Unsupported review disposition: {disposition}")
    if disposition == "approved" and not evaluation.get("accepted"):
        raise SkillImprovementError("A proposal rejected by the evaluation gate cannot be approved")
    if not args.actor.strip() or args.actor.strip().lower() == "agent":
        raise SkillImprovementError("Skill-improvement review requires an explicit human actor")
    if not args.authorization_text.strip():
        raise SkillImprovementError("Skill-improvement review requires explicit authorization text")
    value = {
        "proposal_id": proposal["proposal_id"],
        "disposition": disposition,
        "actor": args.actor.strip(),
        "authorization_text": args.authorization_text.strip(),
        "evidence": list(args.evidence or []),
        "reviewed_at": _now(),
        "execution_authorized": False,
    }
    path = target / "review.json"
    if path.exists():
        stored = _read_object(path, "stored review")
        comparable = {key: item for key, item in stored.items() if key != "reviewed_at"}
        current = {key: item for key, item in value.items() if key != "reviewed_at"}
        if comparable != current:
            raise SkillImprovementError("Proposal already has a different human review")
        return {**stored, "deduplicated": True}
    runtime_lib.atomic_write_json(path, value)
    runtime_lib.append_integrity_jsonl(
        _private_root(root, config) / "events.jsonl",
        {"event": "skill-improvement.reviewed", "proposal_id": proposal["proposal_id"], "disposition": disposition, "actor": value["actor"], "at": value["reviewed_at"]},
    )
    return {**value, "deduplicated": False}


def show(root: Path, config: dict[str, Any], args: Any) -> dict[str, Any]:
    base = _private_root(root, config) / "proposals"
    if args.proposal_id:
        target = _proposal_dir(root, config, args.proposal_id)
        proposal = _load_proposal(target)
        value: dict[str, Any] = {"proposal": proposal, "status": derive_status(target)}
        for name in ("evaluation", "review"):
            path = target / f"{name}.json"
            if path.is_file():
                value[name] = _read_object(path, f"stored {name}")
        value["candidate_path"] = str((target / "candidate-learned-playbook.md").relative_to(root))
        return value
    values = []
    if base.is_dir():
        for target in sorted(path for path in base.iterdir() if path.is_dir()):
            proposal = _load_proposal(target)
            values.append(
                {
                    "proposal_id": proposal["proposal_id"],
                    "skill_name": proposal["skill_name"],
                    "title": proposal["title"],
                    "created_at": proposal["created_at"],
                    "status": derive_status(target),
                }
            )
    return {"proposals": values}


def package(root: Path, config: dict[str, Any], args: Any) -> dict[str, Any]:
    target = _proposal_dir(root, config, args.proposal_id)
    proposal = _load_proposal(target)
    if derive_status(target) != "approved":
        raise SkillImprovementError("Only an evaluated and human-approved proposal can be packaged")
    output = Path(args.output)
    if output.is_absolute():
        raise SkillImprovementError("Package output must be project-relative")
    destination = (root / output).resolve()
    if not destination.is_relative_to(root.resolve()):
        raise SkillImprovementError("Package output escapes the project root")
    if destination.exists():
        raise SkillImprovementError(f"Package output already exists: {destination}")
    destination.mkdir(parents=True)
    for name in ("candidate-learned-playbook.md", "proposal.json", "evaluation.json"):
        shutil.copy2(target / name, destination / name)
    review_path = target / "review.json"
    review = _read_object(review_path, "stored review")
    review_summary = {
        "proposal_id": proposal["proposal_id"],
        "disposition": review["disposition"],
        "reviewed_at": review["reviewed_at"],
        "review_record_sha256": _sha(review_path),
        "execution_authorized": False,
    }
    runtime_lib.atomic_write_json(destination / "review-summary.json", review_summary, mode=0o644)
    manifest = {
        "schema_version": 1,
        "proposal_id": proposal["proposal_id"],
        "skill_name": proposal["skill_name"],
        "protected_skill_sha256": proposal["base_skill_sha256"],
        "base_playbook_sha256": proposal["base_playbook_sha256"],
        "candidate_playbook_sha256": proposal["candidate_playbook_sha256"],
        "review_disposition": "approved",
        "review_record_sha256": review_summary["review_record_sha256"],
        "execution_authorized": False,
        "next_action": "Create or revise an approved Continuity goal to apply this package in the suite source and rerun release validation.",
    }
    runtime_lib.atomic_write_json(destination / "manifest.json", manifest, mode=0o644)
    return {**manifest, "package_path": str(destination.relative_to(root))}


def command(root: Path, config: dict[str, Any], args: Any, schema_root: Path) -> dict[str, Any]:
    handlers = {
        "baseline": lambda: baseline(root, config, args),
        "usage-record": lambda: record_usage(root, config, args, schema_root),
        "patterns": lambda: patterns(root, config, args),
        "propose": lambda: propose(root, config, args, schema_root),
        "evaluate": lambda: evaluate(root, config, args, schema_root),
        "review": lambda: review(root, config, args),
        "show": lambda: show(root, config, args),
        "package": lambda: package(root, config, args),
    }
    handler = handlers.get(args.command)
    if handler is None:
        raise SkillImprovementError(f"Unknown skill-improvement command: {args.command}")
    try:
        return handler()
    except (runtime_lib.RuntimeIntegrityError, OSError) as exc:
        raise SkillImprovementError(str(exc)) from exc
