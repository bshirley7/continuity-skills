#!/usr/bin/env python3
"""Validate and score a hash-bound Continuity-Design homepage benchmark run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


STAGES = {"directions": 1, "selected": 2, "prototype-validated": 3, "approved": 4, "scored": 5}


def _read(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(root: Path, value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or not isinstance(value.get("path"), str):
        raise ValueError(f"{label} requires path and sha256")
    path = (root / value["path"]).resolve()
    try:
        relative = path.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label} escapes the run root") from exc
    if not path.is_file() or value.get("sha256") != _sha256(path):
        raise ValueError(f"{label} is missing or changed: {relative}")
    return {"path": relative, "sha256": value["sha256"]}


def _definition(path: Path) -> dict[str, Any]:
    value = _read(path, "Benchmark definition")
    required = {
        "schema_version", "benchmark_id", "workflow", "brief_path", "stage_checkpoints",
        "required_checkpoints", "required_evidence_roles", "seed_options", "rubric",
        "hard_failures", "passing_score", "minimum_human_reviewers",
    }
    if set(value) != required or value.get("schema_version") != 1:
        raise ValueError("Benchmark definition has an unsupported shape")
    if value.get("benchmark_id") != "continuity-design-homepage-v1" or value.get("workflow") != "$continuity-design":
        raise ValueError("Benchmark definition identity is invalid")
    return value


def _validate_seed(seed: Any, options: dict[str, Any]) -> dict[str, Any]:
    expected = {"audience", "posture", "hero", "references", "edge_case"}
    if not isinstance(seed, dict) or set(seed) != expected:
        raise ValueError("Benchmark seed must contain only the five fixed creative variables")
    for key in ("audience", "posture", "hero", "edge_case"):
        if seed[key] not in options[key]:
            raise ValueError(f"Benchmark seed {key} is outside the definition")
    references = seed["references"]
    if not isinstance(references, list) or len(references) != 2 or len(set(references)) != 2 or any(item not in options["references"] for item in references):
        raise ValueError("Benchmark seed requires exactly two distinct defined references")
    return seed


def evaluate(source_root: Path, run_root: Path, definition_path: Path, manifest_path: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    run_root = run_root.resolve()
    definition_path = definition_path.resolve()
    definition = _definition(definition_path)
    manifest = _read(manifest_path.resolve(), "Benchmark run manifest")
    if manifest.get("schema_version") != 1 or manifest.get("benchmark_id") != definition["benchmark_id"] or manifest.get("workflow") != definition["workflow"]:
        raise ValueError("Benchmark run identity does not match its definition")
    stage = manifest.get("status")
    if stage not in STAGES:
        raise ValueError("Benchmark run has an unsupported status")
    if manifest.get("execution_authorized") is not False:
        raise ValueError("Homepage benchmark runs never authorize implementation")
    if manifest.get("definition_sha256") != _sha256(definition_path):
        raise ValueError("Benchmark definition changed after the run was created")
    brief_path = (definition_path.parent / definition["brief_path"]).resolve()
    if manifest.get("brief_sha256") != _sha256(brief_path):
        raise ValueError("Benchmark brief changed after the run was created")

    source = manifest.get("source")
    if not isinstance(source, dict) or set(source) != {"branch", "commit", "skill_path", "skill_sha256"}:
        raise ValueError("Benchmark source binding is incomplete")
    if not isinstance(source["branch"], str) or not source["branch"].strip() or not re.fullmatch(r"[a-f0-9]{40}", str(source["commit"])):
        raise ValueError("Benchmark source requires a branch and full commit SHA")
    skill_path = (source_root / str(source["skill_path"])).resolve()
    try:
        skill_path.relative_to(source_root)
    except ValueError as exc:
        raise ValueError("Benchmark skill path escapes the source root") from exc
    if not skill_path.is_file() or source.get("skill_sha256") != _sha256(skill_path):
        raise ValueError("Benchmark skill source is missing or changed")

    seed = _validate_seed(manifest.get("seed"), definition["seed_options"])
    doctor_artifact = _artifact(run_root, manifest.get("doctor"), "Project doctor evidence")
    doctor = _read(run_root / doctor_artifact["path"], "Project doctor evidence")
    if doctor.get("healthy") is not True:
        raise ValueError("Project doctor evidence is not healthy")

    checkpoints = manifest.get("checkpoints")
    if not isinstance(checkpoints, list):
        raise ValueError("Benchmark checkpoints must be a list")
    normalized_checkpoints: dict[str, dict[str, str]] = {}
    for item in checkpoints:
        if not isinstance(item, dict) or not isinstance(item.get("checkpoint_id"), str) or not isinstance(item.get("created_at"), str) or not item["created_at"].strip():
            raise ValueError("Every benchmark checkpoint requires checkpoint_id, created_at, path, and sha256")
        checkpoint_id = item["checkpoint_id"]
        if checkpoint_id in normalized_checkpoints or checkpoint_id not in definition["required_checkpoints"]:
            raise ValueError("Benchmark checkpoints must be unique and defined")
        normalized_checkpoints[checkpoint_id] = _artifact(run_root, item, f"Checkpoint {checkpoint_id}")
    required_for_stage = set(definition["stage_checkpoints"][stage])
    missing_checkpoints = sorted(required_for_stage - set(normalized_checkpoints))
    if missing_checkpoints:
        raise ValueError(f"Benchmark stage {stage} lacks checkpoints: {missing_checkpoints}")

    concepts = manifest.get("concepts")
    if not isinstance(concepts, list) or not 1 <= len(concepts) <= 3:
        raise ValueError("Homepage benchmark requires one to three concepts")
    concept_ids: set[str] = set()
    normalized_concepts = []
    for concept in concepts:
        if not isinstance(concept, dict) or not isinstance(concept.get("direction_id"), str) or not concept["direction_id"].strip():
            raise ValueError("Every benchmark concept requires a direction_id")
        direction_id = concept["direction_id"]
        if direction_id in concept_ids:
            raise ValueError("Benchmark concept direction IDs must be unique")
        board = _artifact(run_root, concept.get("board"), f"Concept board {direction_id}")
        slop = _artifact(run_root, concept.get("slop_report"), f"Concept slop report {direction_id}")
        slop_value = _read(run_root / slop["path"], f"Concept slop report {direction_id}")
        if slop_value.get("status") != "passed" or slop_value.get("stage") != "concept":
            raise ValueError(f"Concept {direction_id} lacks a passed concept-stage slop report")
        normalized_concepts.append({"direction_id": direction_id, "board": board, "slop_report": slop})
        concept_ids.add(direction_id)

    selection = manifest.get("selection")
    if STAGES[stage] >= STAGES["selected"]:
        if not isinstance(selection, dict) or selection.get("actor_type") != "human" or not isinstance(selection.get("selected_by"), str) or not isinstance(selection.get("selected_at"), str):
            raise ValueError("Selected benchmark stages require an explicit human selection")
        selected_ids = selection.get("direction_ids")
        if not isinstance(selected_ids, list) or not selected_ids or len(set(selected_ids)) != len(selected_ids) or not set(selected_ids) <= concept_ids:
            raise ValueError("Benchmark selection must reference one or more supplied concepts")
    elif selection is not None:
        raise ValueError("Direction-stage benchmark cannot preselect a concept")

    normalized_evidence: dict[str, dict[str, str]] = {}
    prototype_validation = manifest.get("prototype_validation")
    if STAGES[stage] >= STAGES["prototype-validated"]:
        prototype_artifact = _artifact(run_root, prototype_validation, "Prototype validation")
        prototype_value = _read(run_root / prototype_artifact["path"], "Prototype validation")
        if prototype_value.get("validated") is not True or prototype_value.get("ai_slop_check", {}).get("status") != "passed":
            raise ValueError("Prototype validation must be current and include a passed AI-slop check")
        evidence = manifest.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError("Prototype benchmark evidence must be a list")
        for item in evidence:
            if not isinstance(item, dict) or item.get("role") not in definition["required_evidence_roles"]:
                raise ValueError("Benchmark evidence has an unsupported role")
            role = item["role"]
            if role in normalized_evidence or item.get("media_type") not in definition["required_evidence_roles"][role]:
                raise ValueError("Benchmark evidence roles must be unique and use an allowed media type")
            normalized_evidence[role] = _artifact(run_root, item, f"Evidence {role}")
        missing_evidence = sorted(set(definition["required_evidence_roles"]) - set(normalized_evidence))
        if missing_evidence:
            raise ValueError(f"Prototype benchmark lacks evidence roles: {missing_evidence}")
    else:
        if prototype_validation is not None or manifest.get("evidence") != []:
            raise ValueError("Pre-prototype benchmark stages cannot claim prototype evidence")

    approval = manifest.get("approval")
    if STAGES[stage] >= STAGES["approved"]:
        if not isinstance(approval, dict) or approval.get("actor_type") != "human":
            raise ValueError("Approved benchmark stages require explicit human approval")
        approval_artifact = _artifact(run_root, approval.get("record"), "Design approval record")
        approval_value = _read(run_root / approval_artifact["path"], "Design approval record")
        required_approval = ("design_id", "revision", "design_hash", "visual_reference_hash", "approval_bundle_hash")
        if any(approval.get(key) != approval_value.get(key) for key in required_approval) or approval_value.get("status") != "approved" or approval_value.get("execution_authorized") is not False:
            raise ValueError("Design approval record does not match the benchmark approval binding")
    elif approval is not None:
        raise ValueError("Pre-approval benchmark stages cannot claim design approval")

    total_weight = sum(item["weight"] for item in definition["rubric"])
    if total_weight != 100:
        raise ValueError("Homepage benchmark rubric must total 100 points")
    rubric_weights = {item["dimension"]: item["weight"] for item in definition["rubric"]}
    reviews = manifest.get("reviews")
    hard_reviews = manifest.get("hard_failure_reviews")
    raw_score = capped_score = None
    hard_failures = []
    if stage == "scored":
        if not isinstance(reviews, list) or len(reviews) < definition["minimum_human_reviewers"]:
            raise ValueError("Scored benchmark lacks the required human reviewers")
        reviewer_ids: set[str] = set()
        totals = []
        for review in reviews:
            if not isinstance(review, dict) or review.get("actor_type") != "human" or not isinstance(review.get("reviewer_id"), str) or review["reviewer_id"] in reviewer_ids:
                raise ValueError("Benchmark reviews require unique identified human reviewers")
            scores = review.get("scores")
            if not isinstance(scores, dict) or set(scores) != set(rubric_weights):
                raise ValueError("Every benchmark review must score every rubric dimension")
            for dimension, score in scores.items():
                if not isinstance(score, (int, float)) or not 0 <= score <= rubric_weights[dimension]:
                    raise ValueError(f"Benchmark score for {dimension} exceeds its weight")
            if not isinstance(review.get("rationale"), str) or not review["rationale"].strip():
                raise ValueError("Every benchmark review requires rationale")
            totals.append(sum(scores.values()))
            reviewer_ids.add(review["reviewer_id"])
        defined_hard = {item["rule_id"] for item in definition["hard_failures"]}
        if not isinstance(hard_reviews, list) or {item.get("rule_id") for item in hard_reviews if isinstance(item, dict)} != defined_hard:
            raise ValueError("Scored benchmark must disposition every hard-failure rule")
        for item in hard_reviews:
            if item.get("result") not in {"pass", "fail"} or not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
                raise ValueError("Hard-failure reviews require pass or fail and a rationale")
            if item["result"] == "fail":
                hard_failures.append(item["rule_id"])
        raw_score = round(sum(totals) / len(totals), 2)
        capped_score = min(raw_score, definition["passing_score"] - 1) if hard_failures else raw_score
    else:
        if reviews != [] or hard_reviews != []:
            raise ValueError("Only a scored benchmark may contain reviewer scores")

    benchmark_passed = bool(stage == "scored" and capped_score is not None and capped_score >= definition["passing_score"] and not hard_failures)
    next_gate = {
        "directions": "human-direction-selection",
        "selected": "private-prototype-and-validation",
        "prototype-validated": "exact-human-design-approval",
        "approved": "outside-design-human-scoring",
        "scored": "complete" if benchmark_passed else "benchmark-remediation",
    }[stage]
    return {
        "schema_version": 1,
        "benchmark_id": definition["benchmark_id"],
        "run_id": manifest.get("run_id"),
        "status": stage,
        "stage_valid": True,
        "concept_count": len(normalized_concepts),
        "checkpoint_count": len(normalized_checkpoints),
        "evidence_roles": sorted(normalized_evidence),
        "seed": seed,
        "score": capped_score,
        "raw_score": raw_score,
        "hard_failures": hard_failures,
        "benchmark_passed": benchmark_passed,
        "merge_eligible": benchmark_passed,
        "next_gate": next_gate,
        "execution_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--definition", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.source_root, args.run_root, args.definition, args.manifest)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["stage_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
