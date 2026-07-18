"""Deterministic product-conformance records for Continuity."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import runtime as runtime_lib


class ProductAuditError(RuntimeError):
    pass


PROFILES = {"baseline", "candidate", "release", "drift"}
RESULT_STATUSES = {"passed", "failed", "partial", "blocked"}
FINDING_STATUSES = {
    "aligned",
    "partial",
    "missing",
    "contradicted",
    "regressed",
    "unverifiable",
    "future-roadmap",
    "out-of-scope",
}
SEVERITIES = {"info", "low", "medium", "high", "critical"}
CONFIDENCE = {"low", "medium", "high"}
SCOPES = {"current-goal", "later", "context-only", "out-of-scope"}
GATE_IMPACTS = {"blocking", "advisory", "none"}
SOURCE_TYPES = {
    "approved-goal",
    "approved-design",
    "project-intent",
    "documentation",
    "memory",
    "roadmap",
    "insight",
    "code",
    "other",
}
SOURCE_AUTHORITIES = {"current-approved", "canonical", "advisory", "observed"}
TIME_HORIZONS = {"current", "candidate", "future", "historical", "unknown"}
EVIDENCE_KINDS = {
    "screenshot",
    "dom",
    "accessibility",
    "interaction",
    "command",
    "document",
    "code",
    "other",
}
MISMATCH_STATUSES = {"partial", "missing", "contradicted", "regressed", "unverifiable"}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise ProductAuditError(f"Invalid {label}: {value}")
    return value


def _load(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ProductAuditError(f"{label} is unavailable: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductAuditError(f"{label} must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ProductAuditError(f"{label} must be a JSON object")
    return value


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _audit_root(root: Path, config: dict[str, Any]) -> Path:
    return root / config.get("private_dir", ".continuity/private") / "audits"


def _audit_dir(root: Path, config: dict[str, Any], audit_id: str) -> Path:
    return _audit_root(root, config) / _identifier(audit_id, "audit ID")


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProductAuditError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ProductAuditError(f"{label} must be an array of non-empty strings")
    if len(value) < minimum:
        raise ProductAuditError(f"{label} requires at least {minimum} item(s)")
    return [item.strip() for item in value]


def _validate_sources(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ProductAuditError("Audit planning requires at least one source of intent")
    sources: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ProductAuditError(f"Audit source {index} must be an object")
        source_id = _identifier(_nonempty(item.get("source_id"), f"audit source {index} source_id"), "source ID")
        if source_id in seen:
            raise ProductAuditError(f"Duplicate audit source ID: {source_id}")
        seen.add(source_id)
        source_type = item.get("source_type")
        authority = item.get("authority")
        time_horizon = item.get("time_horizon", "unknown")
        if source_type not in SOURCE_TYPES:
            raise ProductAuditError(f"Unsupported source_type for {source_id}: {source_type}")
        if authority not in SOURCE_AUTHORITIES:
            raise ProductAuditError(f"Unsupported authority for {source_id}: {authority}")
        if time_horizon not in TIME_HORIZONS:
            raise ProductAuditError(f"Unsupported time_horizon for {source_id}: {time_horizon}")
        normalized = {
            "source_id": source_id,
            "source_type": source_type,
            "authority": authority,
            "applicability": _nonempty(item.get("applicability"), f"audit source {source_id} applicability"),
            "time_horizon": time_horizon,
            "reference": _nonempty(item.get("reference"), f"audit source {source_id} reference"),
        }
        if item.get("content_hash") is not None:
            content_hash = str(item["content_hash"])
            if not re.fullmatch(r"[a-f0-9]{64}", content_hash):
                raise ProductAuditError(f"Audit source {source_id} content_hash must be SHA-256")
            normalized["content_hash"] = content_hash
        if item.get("revision") is not None:
            normalized["revision"] = _nonempty(str(item["revision"]), f"audit source {source_id} revision")
        sources.append(normalized)
    return sources


def _validate_journeys(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ProductAuditError("Audit planning requires at least one journey or product surface")
    journeys: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ProductAuditError(f"Audit journey {index} must be an object")
        journey_id = _identifier(
            _nonempty(item.get("journey_id"), f"audit journey {index} journey_id"),
            "journey ID",
        )
        if journey_id in seen:
            raise ProductAuditError(f"Duplicate audit journey ID: {journey_id}")
        seen.add(journey_id)
        journeys.append(
            {
                "journey_id": journey_id,
                "title": _nonempty(item.get("title"), f"audit journey {journey_id} title"),
                "requirements": _string_list(
                    item.get("requirements", []),
                    f"audit journey {journey_id} requirements",
                    minimum=1,
                ),
                "viewports": _string_list(
                    item.get("viewports", ["default"]),
                    f"audit journey {journey_id} viewports",
                    minimum=1,
                ),
            }
        )
    return journeys


def _validate_target(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProductAuditError("Audit target must be an object")
    environment = value.get("environment")
    if environment not in {"local", "preview", "staging", "production", "document", "code"}:
        raise ProductAuditError(f"Unsupported audit target environment: {environment}")
    target: dict[str, Any] = {"environment": environment}
    for key in ("url", "branch", "commit_sha", "build_hash", "reference"):
        if value.get(key) is not None:
            target[key] = _nonempty(value[key], f"audit target {key}")
    if environment in {"preview", "staging", "production"} and not target.get("url"):
        raise ProductAuditError(f"Audit target environment {environment} requires a URL")
    return target


def create_plan(
    root: Path,
    config: dict[str, Any],
    input_path: Path,
    *,
    goal_binding: dict[str, Any] | None = None,
    additional_sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = _load(input_path, "audit input")
    profile = payload.get("profile")
    if profile not in PROFILES:
        raise ProductAuditError(f"Audit profile must be one of {sorted(PROFILES)}")
    requested_id = payload.get("audit_id")
    material_for_id = {
        "project_id": config["project_id"],
        "profile": profile,
        "title": payload.get("title"),
        "goal_id": goal_binding.get("goal_id") if goal_binding else payload.get("goal_id"),
        "target": payload.get("target"),
    }
    audit_id = _identifier(
        str(requested_id or f"audit-{_hash(material_for_id)[:12]}"),
        "audit ID",
    )
    directory = _audit_dir(root, config, audit_id)
    if directory.exists():
        raise ProductAuditError(f"Audit already exists: {audit_id}")
    sources = _validate_sources([*payload.get("sources", []), *(additional_sources or [])])
    goal_id = goal_binding.get("goal_id") if goal_binding else payload.get("goal_id")
    if profile == "candidate" and not goal_id:
        raise ProductAuditError("Candidate audits require a goal binding")
    stamp = _now()
    plan = {
        "schema_version": 1,
        "audit_id": audit_id,
        "project_id": config["project_id"],
        "goal_id": goal_id,
        "profile": profile,
        "title": _nonempty(payload.get("title"), "audit title"),
        "purpose": _nonempty(payload.get("purpose"), "audit purpose"),
        "status": "planned",
        "target": _validate_target(payload.get("target")),
        "sources": sources,
        "journeys": _validate_journeys(payload.get("journeys")),
        "capture_adapter": _nonempty(payload.get("capture_adapter", "manual"), "capture_adapter"),
        "constraints": _string_list(payload.get("constraints", []), "audit constraints"),
        "created_at": stamp,
        "updated_at": stamp,
        "execution_authorized": False,
    }
    if goal_binding:
        plan["goal_binding"] = goal_binding
    plan["plan_hash"] = _hash(
        {
            key: plan[key]
            for key in (
                "audit_id",
                "project_id",
                "goal_id",
                "profile",
                "title",
                "purpose",
                "target",
                "sources",
                "journeys",
                "capture_adapter",
                "constraints",
                "goal_binding",
            )
            if key in plan
        }
    )
    directory.mkdir(parents=True)
    runtime_lib.atomic_write_json(directory / "plan.json", plan)
    runtime_lib.append_integrity_jsonl(
        directory / "events.jsonl",
        {"at": plan["created_at"], "event": "audit.planned", "audit_id": audit_id},
    )
    return plan


def load_plan(root: Path, config: dict[str, Any], audit_id: str) -> dict[str, Any]:
    return _load(_audit_dir(root, config, audit_id) / "plan.json", "audit plan")


def start(
    root: Path,
    config: dict[str, Any],
    audit_id: str,
    *,
    actor: str,
    target_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    directory = _audit_dir(root, config, audit_id)
    plan = load_plan(root, config, audit_id)
    if plan.get("status") not in {"planned", "blocked"}:
        raise ProductAuditError(f"Audit {audit_id} cannot start from {plan.get('status')}")
    plan["status"] = "running"
    plan["started_at"] = _now()
    plan["updated_at"] = plan["started_at"]
    plan["started_by"] = _nonempty(actor, "audit actor")
    if target_binding:
        plan["target_binding"] = target_binding
    runtime_lib.atomic_write_json(directory / "plan.json", plan)
    runtime_lib.append_integrity_jsonl(
        directory / "events.jsonl",
        {"at": plan["started_at"], "event": "audit.started", "audit_id": audit_id, "actor": actor},
    )
    return plan


def _validate_evidence(root: Path, value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ProductAuditError("Audit evidence must be an array")
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ProductAuditError(f"Audit evidence {index} must be an object")
        evidence_id = _identifier(
            _nonempty(item.get("evidence_id"), f"audit evidence {index} evidence_id"),
            "evidence ID",
        )
        if evidence_id in seen:
            raise ProductAuditError(f"Duplicate audit evidence ID: {evidence_id}")
        seen.add(evidence_id)
        kind = item.get("kind")
        if kind not in EVIDENCE_KINDS:
            raise ProductAuditError(f"Unsupported audit evidence kind: {kind}")
        normalized: dict[str, Any] = {
            "evidence_id": evidence_id,
            "kind": kind,
            "description": _nonempty(item.get("description"), f"audit evidence {evidence_id} description"),
            "captured_at": _nonempty(item.get("captured_at"), f"audit evidence {evidence_id} captured_at"),
        }
        reference = item.get("reference")
        path_value = item.get("path")
        if not reference and not path_value:
            raise ProductAuditError(f"Audit evidence {evidence_id} requires reference or path")
        if reference:
            normalized["reference"] = _nonempty(reference, f"audit evidence {evidence_id} reference")
        if path_value:
            relative = Path(_nonempty(path_value, f"audit evidence {evidence_id} path"))
            if relative.is_absolute():
                raise ProductAuditError(f"Audit evidence {evidence_id} path must be project-relative")
            path = (root / relative).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                raise ProductAuditError(f"Audit evidence {evidence_id} path is unavailable or escapes the project")
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            expected_hash = item.get("sha256")
            if expected_hash is not None and expected_hash != actual_hash:
                raise ProductAuditError(f"Audit evidence {evidence_id} SHA-256 does not match its file")
            normalized["path"] = str(relative)
            normalized["sha256"] = actual_hash
        elif item.get("sha256") is not None:
            sha256 = str(item["sha256"])
            if not re.fullmatch(r"[a-f0-9]{64}", sha256):
                raise ProductAuditError(f"Audit evidence {evidence_id} sha256 must be SHA-256")
            normalized["sha256"] = sha256
        evidence.append(normalized)
    return evidence


def _validate_findings(
    value: Any,
    source_ids: set[str],
    evidence_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ProductAuditError("Audit result requires at least one conformance finding")
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ProductAuditError(f"Audit finding {index} must be an object")
        finding_id = _identifier(
            _nonempty(item.get("finding_id"), f"audit finding {index} finding_id"),
            "finding ID",
        )
        if finding_id in seen:
            raise ProductAuditError(f"Duplicate audit finding ID: {finding_id}")
        seen.add(finding_id)
        status = item.get("status")
        severity = item.get("severity")
        confidence = item.get("confidence")
        scope = item.get("scope")
        gate_impact = item.get("gate_impact")
        if status not in FINDING_STATUSES:
            raise ProductAuditError(f"Unsupported finding status for {finding_id}: {status}")
        if severity not in SEVERITIES:
            raise ProductAuditError(f"Unsupported finding severity for {finding_id}: {severity}")
        if confidence not in CONFIDENCE:
            raise ProductAuditError(f"Unsupported finding confidence for {finding_id}: {confidence}")
        if scope not in SCOPES:
            raise ProductAuditError(f"Unsupported finding scope for {finding_id}: {scope}")
        if gate_impact not in GATE_IMPACTS:
            raise ProductAuditError(f"Unsupported gate_impact for {finding_id}: {gate_impact}")
        if gate_impact == "blocking" and scope != "current-goal":
            raise ProductAuditError(f"Only current-goal findings may block product conformance: {finding_id}")
        if status in {"aligned", "future-roadmap", "out-of-scope"} and gate_impact == "blocking":
            raise ProductAuditError(f"Finding {finding_id} cannot block with status {status}")
        finding_sources = _string_list(item.get("source_refs", []), f"finding {finding_id} source_refs", minimum=1)
        unknown_sources = sorted(set(finding_sources) - source_ids)
        if unknown_sources:
            raise ProductAuditError(f"Finding {finding_id} references unknown sources: {unknown_sources}")
        finding_evidence = _string_list(item.get("evidence_refs", []), f"finding {finding_id} evidence_refs")
        unknown_evidence = sorted(set(finding_evidence) - evidence_ids)
        if unknown_evidence:
            raise ProductAuditError(f"Finding {finding_id} references unknown evidence: {unknown_evidence}")
        if status != "unverifiable" and not finding_evidence:
            raise ProductAuditError(f"Finding {finding_id} requires observed evidence")
        findings.append(
            {
                "finding_id": finding_id,
                "requirement_ref": _nonempty(item.get("requirement_ref"), f"finding {finding_id} requirement_ref"),
                "title": _nonempty(item.get("title"), f"finding {finding_id} title"),
                "status": status,
                "severity": severity,
                "confidence": confidence,
                "scope": scope,
                "gate_impact": gate_impact,
                "source_refs": finding_sources,
                "evidence_refs": finding_evidence,
                "summary": _nonempty(item.get("summary"), f"finding {finding_id} summary"),
                "recommendation": _nonempty(item.get("recommendation"), f"finding {finding_id} recommendation"),
            }
        )
    return findings


def _result_status(coverage: dict[str, int], findings: list[dict[str, Any]]) -> str:
    if coverage["observed"] == 0 and coverage["blocked"] >= coverage["planned"]:
        return "blocked"
    if any(
        item["gate_impact"] == "blocking" and item["status"] in MISMATCH_STATUSES
        for item in findings
    ):
        return "failed"
    if coverage["observed"] < coverage["planned"] or coverage["blocked"] > 0:
        return "partial"
    return "passed"


def record(
    root: Path,
    config: dict[str, Any],
    audit_id: str,
    result_path: Path,
    *,
    actor: str,
    current_binding: dict[str, Any] | None = None,
    sanitized_artifact: dict[str, Any] | None = None,
    evidence_root: Path | None = None,
) -> dict[str, Any]:
    directory = _audit_dir(root, config, audit_id)
    plan = load_plan(root, config, audit_id)
    if plan.get("status") not in {"running", "failed", "partial", "blocked"}:
        raise ProductAuditError(f"Audit {audit_id} cannot record from {plan.get('status')}")
    payload = _load(result_path, "audit result")
    if payload.get("audit_id") not in {None, audit_id}:
        raise ProductAuditError("Audit result names a different audit_id")
    coverage_value = payload.get("coverage")
    if not isinstance(coverage_value, dict):
        raise ProductAuditError("Audit result coverage must be an object")
    coverage: dict[str, int] = {}
    for key in ("planned", "observed", "blocked"):
        value = coverage_value.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ProductAuditError(f"Audit coverage {key} must be a non-negative integer")
        coverage[key] = value
    if coverage["planned"] < 1:
        raise ProductAuditError("Audit coverage planned must be at least 1")
    if coverage["observed"] + coverage["blocked"] != coverage["planned"]:
        raise ProductAuditError(
            "Audit coverage observed plus blocked must equal planned observations"
        )
    evidence = _validate_evidence(evidence_root or root, payload.get("evidence", []))
    findings = _validate_findings(
        payload.get("findings"),
        {item["source_id"] for item in plan["sources"]},
        {item["evidence_id"] for item in evidence},
    )
    computed_status = _result_status(coverage, findings)
    requested_status = payload.get("status")
    if requested_status is not None and requested_status not in RESULT_STATUSES:
        raise ProductAuditError(f"Unsupported requested audit status: {requested_status}")
    if requested_status == "passed" and computed_status != "passed":
        raise ProductAuditError(
            f"Cannot force a passed product audit; computed status is {computed_status}"
        )
    status = requested_status if requested_status in {"failed", "partial", "blocked"} else computed_status
    stamp = _now()
    record_value = {
        "schema_version": 1,
        "audit_id": audit_id,
        "project_id": config["project_id"],
        "goal_id": plan.get("goal_id"),
        "profile": plan["profile"],
        "status": status,
        "summary": _nonempty(payload.get("summary"), "audit result summary"),
        "coverage": coverage,
        "findings": findings,
        "evidence": evidence,
        "source_set_hash": _hash(plan["sources"]),
        "plan_hash": plan["plan_hash"],
        "goal_binding": plan.get("goal_binding"),
        "target_binding": current_binding or plan.get("target_binding"),
        "actor": _nonempty(actor, "audit actor"),
        "recorded_at": stamp,
        "updated_at": stamp,
        "execution_authorized": False,
        "findings_capture": None,
    }
    if sanitized_artifact:
        record_value["sanitized_artifact"] = sanitized_artifact
    record_value["result_hash"] = _hash(
        {
            key: record_value[key]
            for key in (
                "audit_id",
                "project_id",
                "goal_id",
                "profile",
                "status",
                "summary",
                "coverage",
                "findings",
                "evidence",
                "source_set_hash",
                "plan_hash",
                "goal_binding",
                "target_binding",
                "sanitized_artifact",
            )
            if key in record_value
        }
    )
    runtime_lib.atomic_write_json(directory / "record.json", record_value)
    plan["status"] = status
    plan["updated_at"] = stamp
    plan["result_hash"] = record_value["result_hash"]
    runtime_lib.atomic_write_json(directory / "plan.json", plan)
    runtime_lib.append_integrity_jsonl(
        directory / "events.jsonl",
        {"at": stamp, "event": "audit.recorded", "audit_id": audit_id, "status": status},
    )
    runtime_lib.append_integrity_jsonl(
        _audit_root(root, config).parent / "reports" / "product-audits.jsonl",
        record_value,
    )
    return record_value


def load_record(root: Path, config: dict[str, Any], audit_id: str) -> dict[str, Any] | None:
    path = _audit_dir(root, config, audit_id) / "record.json"
    return _load(path, "audit record") if path.is_file() else None


def show(root: Path, config: dict[str, Any], audit_id: str | None = None) -> Any:
    if audit_id:
        plan = load_plan(root, config, audit_id)
        return {"plan": plan, "record": load_record(root, config, audit_id)}
    records = []
    for path in sorted(_audit_root(root, config).glob("*/plan.json")):
        plan = _load(path, "audit plan")
        records.append(
            {
                "audit_id": plan["audit_id"],
                "profile": plan["profile"],
                "goal_id": plan.get("goal_id"),
                "status": plan["status"],
                "title": plan["title"],
                "updated_at": plan["updated_at"],
            }
        )
    return records


def compare(
    root: Path,
    config: dict[str, Any],
    audit_id: str,
    against: str,
) -> dict[str, Any]:
    current = load_record(root, config, audit_id)
    previous = load_record(root, config, against)
    if current is None or previous is None:
        raise ProductAuditError("Both audits must have recorded results before comparison")
    current_map = {item["finding_id"]: item for item in current["findings"]}
    previous_map = {item["finding_id"]: item for item in previous["findings"]}
    added = sorted(set(current_map) - set(previous_map))
    removed = sorted(set(previous_map) - set(current_map))
    changed = [
        {
            "finding_id": finding_id,
            "from_status": previous_map[finding_id]["status"],
            "to_status": current_map[finding_id]["status"],
            "from_severity": previous_map[finding_id]["severity"],
            "to_severity": current_map[finding_id]["severity"],
        }
        for finding_id in sorted(set(current_map) & set(previous_map))
        if (
            current_map[finding_id]["status"],
            current_map[finding_id]["severity"],
            current_map[finding_id]["gate_impact"],
        )
        != (
            previous_map[finding_id]["status"],
            previous_map[finding_id]["severity"],
            previous_map[finding_id]["gate_impact"],
        )
    ]
    return {
        "audit_id": audit_id,
        "against": against,
        "status": current["status"],
        "against_status": previous["status"],
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": len(set(current_map) & set(previous_map)) - len(changed),
        "comparison_hash": _hash(
            {"audit_id": audit_id, "against": against, "added": added, "removed": removed, "changed": changed}
        ),
    }


def attach_capture(
    root: Path,
    config: dict[str, Any],
    audit_id: str,
    *,
    capture_id: str,
    note_ids: list[str],
) -> dict[str, Any]:
    directory = _audit_dir(root, config, audit_id)
    record_value = load_record(root, config, audit_id)
    if record_value is None:
        raise ProductAuditError("Audit findings cannot be captured before a result is recorded")
    binding = {
        "capture_id": _identifier(capture_id, "capture ID"),
        "note_ids": [_identifier(value, "note ID") for value in note_ids],
        "attached_at": _now(),
        "execution_authorized": False,
    }
    record_value["findings_capture"] = binding
    runtime_lib.atomic_write_json(directory / "record.json", record_value)
    runtime_lib.append_integrity_jsonl(
        directory / "events.jsonl",
        {
            "at": binding["attached_at"],
            "event": "audit.findings-captured",
            "audit_id": audit_id,
            "capture_id": capture_id,
        },
    )
    return binding


def latest_for_goal(
    root: Path,
    config: dict[str, Any],
    goal_id: str,
) -> dict[str, Any] | None:
    matches = [
        value
        for value in show(root, config)
        if value.get("goal_id") == goal_id and value.get("profile") == "candidate"
    ]
    if not matches:
        return None
    latest = max(matches, key=lambda value: value.get("updated_at", ""))
    return load_record(root, config, latest["audit_id"])


def due(root: Path, config: dict[str, Any], stale_after_days: int) -> dict[str, Any]:
    current = dt.datetime.now(dt.timezone.utc)
    due_records: list[dict[str, Any]] = []
    audits = show(root, config)
    for item in audits:
        try:
            updated = dt.datetime.fromisoformat(str(item["updated_at"]))
        except ValueError:
            updated = current - dt.timedelta(days=stale_after_days + 1)
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=dt.timezone.utc)
        age_days = max(0, (current - updated).days)
        if item["status"] in {"planned", "running", "failed", "partial", "blocked"} or age_days >= stale_after_days:
            due_records.append({**item, "age_days": age_days})
    return {
        "stale_after_days": stale_after_days,
        "baseline_required": not any(
            item.get("profile") in {"baseline", "release", "drift"}
            and item.get("status") == "passed"
            for item in audits
        ),
        "due": sorted(due_records, key=lambda value: (value["status"], -value["age_days"], value["audit_id"])),
    }


def workflow(root: Path, config: dict[str, Any], audit_id: str) -> dict[str, Any]:
    plan = load_plan(root, config, audit_id)
    record_value = load_record(root, config, audit_id)
    status = str(plan["status"])
    mismatch_findings = [
        item
        for item in (record_value or {}).get("findings", [])
        if item.get("status") in MISMATCH_STATUSES
    ]
    captured = bool((record_value or {}).get("findings_capture"))
    if status == "planned":
        next_skill = "continuity-product-audit"
        allowed_actions = ["start-audit"]
    elif status == "running":
        next_skill = "continuity-product-audit"
        allowed_actions = ["record-audit"]
    elif mismatch_findings and not captured:
        next_skill = "continuity-product-audit"
        allowed_actions = ["capture-findings"]
    elif mismatch_findings:
        next_skill = "continuity-triage"
        allowed_actions = ["triage-captured-findings", "compare-audits"]
    else:
        next_skill = "continuity-report"
        allowed_actions = ["report-audit", "compare-audits"]
    return {
        "audit_id": audit_id,
        "goal_id": plan.get("goal_id"),
        "profile": plan["profile"],
        "status": status,
        "result_hash": (record_value or {}).get("result_hash"),
        "finding_counts": {
            finding_status: sum(
                1
                for item in (record_value or {}).get("findings", [])
                if item.get("status") == finding_status
            )
            for finding_status in sorted(FINDING_STATUSES)
        },
        "findings_capture": (record_value or {}).get("findings_capture"),
        "next_skill": next_skill,
        "allowed_actions": allowed_actions,
        "human_required": False,
        "execution_authorized": False,
    }
