#!/usr/bin/env python3
"""Validate and score a hash-bound Continuity-Design presentation benchmark run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any


STAGES = {"directions": 1, "selected": 2, "prototype-validated": 3, "approved": 4, "scored": 5}
VIEWPORT_WIDTHS = {"desktop-projection": 1440, "tablet-read-ahead": 768, "mobile-read-ahead": 390}


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


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError(f"Presentation evidence is not an encoded PNG: {path.name}")
    width, height = struct.unpack(">II", data[16:24])
    if width < 1 or height < 1:
        raise ValueError(f"Presentation PNG has invalid dimensions: {path.name}")
    return width, height


def _definition(path: Path) -> dict[str, Any]:
    value = _read(path, "Presentation benchmark definition")
    required = {
        "schema_version", "benchmark_id", "workflow", "brief_path", "stage_checkpoints",
        "required_checkpoints", "required_evidence_roles", "seed_options", "rubric",
        "hard_failures", "passing_score", "minimum_human_reviewers",
        "minimum_refinement_passes", "minimum_slide_roles",
    }
    if set(value) != required or value.get("schema_version") != 1:
        raise ValueError("Presentation benchmark definition has an unsupported shape")
    if value.get("benchmark_id") != "continuity-design-presentation-v1" or value.get("workflow") != "$continuity-design":
        raise ValueError("Presentation benchmark definition identity is invalid")
    return value


def _validate_seed(seed: Any, options: dict[str, Any]) -> dict[str, Any]:
    expected = {"audience", "posture", "narrative", "read_mode", "references"}
    if not isinstance(seed, dict) or set(seed) != expected:
        raise ValueError("Presentation benchmark seed must contain only the five fixed creative variables")
    for key in ("audience", "posture", "narrative", "read_mode"):
        if seed[key] not in options[key]:
            raise ValueError(f"Presentation benchmark seed {key} is outside the definition")
    references = seed["references"]
    if not isinstance(references, list) or len(references) != 2 or len(set(references)) != 2 or any(item not in options["references"] for item in references):
        raise ValueError("Presentation benchmark seed requires exactly two distinct defined reference families")
    return seed


def evaluate(source_root: Path, run_root: Path, definition_path: Path, manifest_path: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    run_root = run_root.resolve()
    definition_path = definition_path.resolve()
    definition = _definition(definition_path)
    manifest = _read(manifest_path.resolve(), "Presentation benchmark run manifest")
    if manifest.get("schema_version") != 1 or manifest.get("benchmark_id") != definition["benchmark_id"] or manifest.get("workflow") != definition["workflow"]:
        raise ValueError("Presentation benchmark run identity does not match its definition")
    stage = manifest.get("status")
    if stage not in STAGES:
        raise ValueError("Presentation benchmark run has an unsupported status")
    if manifest.get("execution_authorized") is not False:
        raise ValueError("Presentation benchmark runs never authorize implementation or publication")
    if manifest.get("definition_sha256") != _sha256(definition_path):
        raise ValueError("Presentation benchmark definition changed after the run was created")
    brief_path = (definition_path.parent / definition["brief_path"]).resolve()
    if manifest.get("brief_sha256") != _sha256(brief_path):
        raise ValueError("Presentation benchmark brief changed after the run was created")

    source = manifest.get("source")
    if not isinstance(source, dict) or set(source) != {"branch", "commit", "skill_path", "skill_sha256"}:
        raise ValueError("Presentation benchmark source binding is incomplete")
    if not isinstance(source["branch"], str) or not source["branch"].strip() or not re.fullmatch(r"[a-f0-9]{40}", str(source["commit"])):
        raise ValueError("Presentation benchmark source requires a branch and full commit SHA")
    skill_path = (source_root / str(source["skill_path"])).resolve()
    try:
        skill_path.relative_to(source_root)
    except ValueError as exc:
        raise ValueError("Presentation benchmark skill path escapes the source root") from exc
    if not skill_path.is_file() or source.get("skill_sha256") != _sha256(skill_path):
        raise ValueError("Presentation benchmark skill source is missing or changed")

    seed = _validate_seed(manifest.get("seed"), definition["seed_options"])
    doctor_artifact = _artifact(run_root, manifest.get("doctor"), "Project doctor evidence")
    if _read(run_root / doctor_artifact["path"], "Project doctor evidence").get("healthy") is not True:
        raise ValueError("Project doctor evidence is not healthy")

    checkpoints = manifest.get("checkpoints")
    if not isinstance(checkpoints, list):
        raise ValueError("Presentation benchmark checkpoints must be a list")
    normalized_checkpoints: dict[str, dict[str, str]] = {}
    for item in checkpoints:
        if not isinstance(item, dict) or not isinstance(item.get("checkpoint_id"), str) or not isinstance(item.get("created_at"), str) or not item["created_at"].strip():
            raise ValueError("Every presentation checkpoint requires checkpoint_id, created_at, path, and sha256")
        checkpoint_id = item["checkpoint_id"]
        if checkpoint_id in normalized_checkpoints or checkpoint_id not in definition["required_checkpoints"]:
            raise ValueError("Presentation benchmark checkpoints must be unique and defined")
        normalized_checkpoints[checkpoint_id] = _artifact(run_root, item, f"Checkpoint {checkpoint_id}")
    missing = sorted(set(definition["stage_checkpoints"][stage]) - set(normalized_checkpoints))
    if missing:
        raise ValueError(f"Presentation benchmark stage {stage} lacks checkpoints: {missing}")

    laboratory = _read(run_root / normalized_checkpoints["generative-concept-laboratory"]["path"], "Generative concept laboratory checkpoint")
    laboratory_hash = laboratory.get("laboratory_hash")
    if (
        laboratory.get("status") != "complete"
        or not 4 <= laboratory.get("lens_count", 0) <= 8
        or not 8 <= laboratory.get("seed_count", 0) <= 12
        or laboratory.get("media_count", 0) < 3
        or laboratory.get("generated_seed_count", 0) < 1
        or laboratory.get("slide_role_family_count", 0) < definition["minimum_slide_roles"]
        or not re.fullmatch(r"[a-f0-9]{64}", str(laboratory_hash or ""))
    ):
        raise ValueError("Presentation benchmark requires a broad, completed generative laboratory with slide-role range")
    translation = _read(run_root / normalized_checkpoints["reference-translation"]["path"], "Reference translation checkpoint")
    translation_hash = translation.get("reference_translation_hash")
    if (
        translation.get("status") != "passed"
        or translation.get("reference_study_count") != 2
        or translation.get("correction_pass_count", 0) < 4
        or translation.get("constraint_count", 0) < 16
        or translation.get("independent_review_status") != "passed"
        or translation.get("comparison_status") != "passed"
        or not re.fullmatch(r"[a-f0-9]{64}", str(translation_hash or ""))
    ):
        raise ValueError("Presentation benchmark requires two separately reconstructed and independently reviewed references")

    concepts = manifest.get("concepts")
    if not isinstance(concepts, list) or not 1 <= len(concepts) <= 3:
        raise ValueError("Presentation benchmark requires one to three concepts")
    concept_ids: set[str] = set()
    type_families: set[str] = set()
    art_families: set[str] = set()
    composition_families: set[str] = set()
    sequence_grammars: set[str] = set()
    concept_forming = 0
    compelling = 0
    normalized_concepts: list[dict[str, Any]] = []
    for concept in concepts:
        if not isinstance(concept, dict) or not isinstance(concept.get("direction_id"), str) or not concept["direction_id"].strip():
            raise ValueError("Every presentation concept requires a direction_id")
        direction_id = concept["direction_id"]
        if direction_id in concept_ids:
            raise ValueError("Presentation concept direction IDs must be unique")
        board = _artifact(run_root, concept.get("board"), f"Concept board {direction_id}")
        contact_sheet = _artifact(run_root, concept.get("contact_sheet"), f"Concept contact sheet {direction_id}")
        _png_dimensions(run_root / contact_sheet["path"])
        slop = _artifact(run_root, concept.get("slop_report"), f"Concept slop report {direction_id}")
        slop_value = _read(run_root / slop["path"], f"Concept slop report {direction_id}")
        if slop_value.get("status") != "passed" or slop_value.get("stage") != "concept":
            raise ValueError(f"Presentation concept {direction_id} lacks a passed concept slop report")
        presentation_fidelity = slop_value.get("presentation_fidelity")
        if (
            not isinstance(presentation_fidelity, dict)
            or presentation_fidelity.get("copy_readability_verified") is not True
            or presentation_fidelity.get("data_readability_verified") is not True
        ):
            raise ValueError(f"Presentation concept {direction_id} lacks passed copy and data readability evidence")
        if concept.get("generative_laboratory_hash") != laboratory_hash or concept.get("reference_translation_hash") != translation_hash:
            raise ValueError(f"Presentation concept {direction_id} is not bound to the laboratory and translation evidence")
        if concept.get("creative_range_status") != "passed" or concept.get("impact_review_status") != "passed":
            raise ValueError(f"Presentation concept {direction_id} lacks creative-range or impact review")
        if concept.get("impact_strength") == "compelling":
            compelling += 1
        elif concept.get("impact_strength") != "credible":
            raise ValueError(f"Presentation concept {direction_id} has an unsupported impact strength")
        media_status = concept.get("concept_forming_media_status")
        if media_status not in {"passed", "supporting", "rejected"}:
            raise ValueError(f"Presentation concept {direction_id} lacks a generated-media disposition")
        if media_status == "passed":
            concept_forming += 1
        if (
            concept.get("slide_role_count", 0) < definition["minimum_slide_roles"]
            or concept.get("silhouette_count", 0) < definition["minimum_slide_roles"]
            or not isinstance(concept.get("repeated_template_ratio"), (int, float))
            or isinstance(concept.get("repeated_template_ratio"), bool)
            or not 0 <= concept["repeated_template_ratio"] <= 0.5
            or concept.get("narrative_peak_present") is not True
            or concept.get("quiet_or_rest_present") is not True
            or concept.get("projection_review_status") != "passed"
            or concept.get("read_ahead_review_status") != "passed"
            or concept.get("claims_provenance_complete") is not True
            or concept.get("capture_integrity_verified") is not True
            or concept.get("copy_readability_verified") is not True
            or concept.get("data_readability_verified") is not True
            or concept.get("runtime_probe_count") != 3
        ):
            raise ValueError(f"Presentation concept {direction_id} lacks role, pacing, mode, claim, or capture evidence")
        required_system = ("typography_family", "art_direction_family", "composition_family", "sequence_grammar")
        if any(not isinstance(concept.get(key), str) or not concept[key].strip() for key in required_system):
            raise ValueError(f"Presentation concept {direction_id} lacks a complete expression and sequence system")
        type_families.add(concept["typography_family"])
        art_families.add(concept["art_direction_family"])
        composition_families.add(concept["composition_family"])
        sequence_grammars.add(concept["sequence_grammar"])
        concept_ids.add(direction_id)
        normalized_concepts.append({"direction_id": direction_id, "board": board, "contact_sheet": contact_sheet, "slop_report": slop})
    if concept_forming < 1 or compelling < 1:
        raise ValueError("Presentation benchmark requires concept-forming media and at least one compelling concept")
    if len(concepts) > 1 and (
        len(type_families) < 2
        or len(art_families) != len(concepts)
        or len(composition_families) != len(concepts)
        or len(sequence_grammars) != len(concepts)
    ):
        raise ValueError("Presentation concepts must differ in type, art direction, composition, and sequence grammar")

    passes = manifest.get("refinement_passes")
    if not isinstance(passes, list) or len(passes) < definition["minimum_refinement_passes"]:
        raise ValueError("Presentation benchmark lacks the required autonomous refinement passes")
    normalized_passes = []
    for index, item in enumerate(passes, 1):
        if not isinstance(item, dict) or item.get("pass") != index:
            raise ValueError("Presentation refinement passes must be consecutive and one-based")
        direction_ids = item.get("direction_ids")
        if not isinstance(direction_ids, list) or not direction_ids or not set(direction_ids) <= concept_ids:
            raise ValueError(f"Presentation refinement pass {index} must name developed concepts")
        if not isinstance(item.get("hypothesis"), str) or not item["hypothesis"].strip():
            raise ValueError(f"Presentation refinement pass {index} requires one hypothesis")
        strengths = item.get("preserved_strengths")
        if not isinstance(strengths, list) or not strengths or any(not isinstance(value, str) or not value.strip() for value in strengths):
            raise ValueError(f"Presentation refinement pass {index} requires preserved strengths")
        if item.get("slop_status") not in {"passed", "failed"} or item.get("affected_evidence_rerun") is not True:
            raise ValueError(f"Presentation refinement pass {index} requires a slop status")
        slop_report = _artifact(run_root, item.get("slop_report"), f"Refinement pass {index} slop report")
        slop_value = _read(run_root / slop_report["path"], f"Refinement pass {index} slop report")
        if slop_value.get("stage") != "concept" or slop_value.get("status") != item["slop_status"]:
            raise ValueError(f"Presentation refinement pass {index} slop status is not bound to its report")
        visual_delta = _artifact(run_root, item.get("visual_delta"), f"Refinement pass {index} visual delta")
        _png_dimensions(run_root / visual_delta["path"])
        normalized_passes.append({
            "pass": index,
            "artifact": _artifact(run_root, item.get("artifact"), f"Refinement pass {index} artifact"),
            "visual_delta": visual_delta,
            "self_assessment": _artifact(run_root, item.get("self_assessment"), f"Refinement pass {index} self-assessment"),
            "slop_report": slop_report,
        })
    if passes[-1].get("slop_status") != "passed":
        raise ValueError("The final presentation refinement pass must have a passed slop report")

    selection = manifest.get("selection")
    if STAGES[stage] >= STAGES["selected"]:
        if not isinstance(selection, dict) or selection.get("actor_type") != "human" or not isinstance(selection.get("selected_by"), str) or not isinstance(selection.get("selected_at"), str):
            raise ValueError("Selected presentation stages require explicit human selection")
        selected_ids = selection.get("direction_ids")
        if not isinstance(selected_ids, list) or not selected_ids or not set(selected_ids) <= concept_ids:
            raise ValueError("Presentation selection must reference supplied concepts")
    elif selection is not None:
        raise ValueError("Direction-stage presentation benchmark cannot preselect a concept")

    normalized_evidence: dict[str, dict[str, str]] = {}
    prototype_validation = manifest.get("prototype_validation")
    if STAGES[stage] >= STAGES["prototype-validated"]:
        prototype = _artifact(run_root, prototype_validation, "Presentation validation")
        prototype_value = _read(run_root / prototype["path"], "Presentation validation")
        if prototype_value.get("validated") is not True or prototype_value.get("ai_slop_check", {}).get("status") != "passed":
            raise ValueError("Presentation validation must be current and include a passed AI-slop check")
        evidence = manifest.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError("Presentation evidence must be a list")
        for item in evidence:
            if not isinstance(item, dict) or item.get("role") not in definition["required_evidence_roles"]:
                raise ValueError("Presentation evidence has an unsupported role")
            role = item["role"]
            if role in normalized_evidence or item.get("media_type") not in definition["required_evidence_roles"][role]:
                raise ValueError("Presentation evidence roles must be unique and use an allowed media type")
            artifact = _artifact(run_root, item, f"Evidence {role}")
            if item["media_type"] == "image/png":
                width, _ = _png_dimensions(run_root / artifact["path"])
                if role in VIEWPORT_WIDTHS and (item.get("viewport_width") != VIEWPORT_WIDTHS[role] or width != VIEWPORT_WIDTHS[role]):
                    raise ValueError(f"Presentation evidence {role} does not match its required viewport")
            normalized_evidence[role] = artifact
        missing_roles = sorted(set(definition["required_evidence_roles"]) - set(normalized_evidence))
        if missing_roles:
            raise ValueError(f"Presentation benchmark lacks evidence roles: {missing_roles}")
        integrity = _read(run_root / normalized_evidence["capture-integrity"]["path"], "Capture integrity evidence")
        if integrity.get("status") != "passed" or integrity.get("individual_frames_verified") is not True or integrity.get("contact_sheet_source") != "verified-individual-frames":
            raise ValueError("Presentation capture-integrity evidence does not prove verified individual frames")
        readability = _read(run_root / normalized_evidence["readability-audit"]["path"], "Presentation readability evidence")
        viewport_reviews = readability.get("viewports")
        if (
            readability.get("status") != "passed"
            or readability.get("all_copy_readable") is not True
            or readability.get("all_data_readable") is not True
            or not isinstance(readability.get("slide_count"), int)
            or readability.get("slide_count", 0) < 1
            or not isinstance(viewport_reviews, list)
            or {item.get("viewport_width") for item in viewport_reviews if isinstance(item, dict)} != set(VIEWPORT_WIDTHS.values())
            or any(
                item.get("slide_count") != readability["slide_count"]
                or item.get("all_copy_readable") is not True
                or item.get("all_data_readable") is not True
                or item.get("browser_probe_passed") is not True
                for item in viewport_reviews
                if isinstance(item, dict)
            )
            or len(viewport_reviews) != len(VIEWPORT_WIDTHS)
        ):
            raise ValueError("Presentation readability evidence does not prove readable copy and data on every slide and required viewport")
    elif prototype_validation is not None or manifest.get("evidence") != []:
        raise ValueError("Pre-prototype presentation stages cannot claim prototype evidence")

    approval = manifest.get("approval")
    if STAGES[stage] >= STAGES["approved"]:
        if not isinstance(approval, dict) or approval.get("actor_type") != "human":
            raise ValueError("Approved presentation stages require explicit human approval")
        approval_artifact = _artifact(run_root, approval.get("record"), "Design approval record")
        approval_value = _read(run_root / approval_artifact["path"], "Design approval record")
        binding = ("design_id", "revision", "design_hash", "visual_reference_hash", "approval_bundle_hash")
        if any(approval.get(key) != approval_value.get(key) for key in binding) or approval_value.get("status") != "approved" or approval_value.get("execution_authorized") is not False:
            raise ValueError("Presentation approval record does not match its exact bundle")
    elif approval is not None:
        raise ValueError("Pre-approval presentation stages cannot claim design approval")

    weights = {item["dimension"]: item["weight"] for item in definition["rubric"]}
    if sum(weights.values()) != 100:
        raise ValueError("Presentation benchmark rubric must total 100 points")
    reviews = manifest.get("reviews")
    hard_reviews = manifest.get("hard_failure_reviews")
    raw_score = capped_score = None
    hard_failures: list[str] = []
    if stage == "scored":
        if not isinstance(reviews, list) or len(reviews) < definition["minimum_human_reviewers"]:
            raise ValueError("Scored presentation benchmark lacks the required human reviewers")
        reviewer_ids: set[str] = set()
        totals = []
        for review in reviews:
            if not isinstance(review, dict) or review.get("actor_type") != "human" or not isinstance(review.get("reviewer_id"), str) or review["reviewer_id"] in reviewer_ids:
                raise ValueError("Presentation reviews require unique identified human reviewers")
            scores = review.get("scores")
            if not isinstance(scores, dict) or set(scores) != set(weights):
                raise ValueError("Every presentation review must score every rubric dimension")
            if any(not isinstance(score, (int, float)) or not 0 <= score <= weights[dimension] for dimension, score in scores.items()):
                raise ValueError("A presentation review score exceeds its rubric weight")
            if not isinstance(review.get("rationale"), str) or not review["rationale"].strip():
                raise ValueError("Every presentation review requires rationale")
            totals.append(sum(scores.values()))
            reviewer_ids.add(review["reviewer_id"])
        required_hard = {item["rule_id"] for item in definition["hard_failures"]}
        if not isinstance(hard_reviews, list) or {item.get("rule_id") for item in hard_reviews if isinstance(item, dict)} != required_hard:
            raise ValueError("Scored presentation benchmark must disposition every hard failure")
        for item in hard_reviews:
            if item.get("result") not in {"pass", "fail"} or not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
                raise ValueError("Presentation hard-failure reviews require pass or fail and rationale")
            if item["result"] == "fail":
                hard_failures.append(item["rule_id"])
        raw_score = round(sum(totals) / len(totals), 2)
        capped_score = min(raw_score, definition["passing_score"] - 1) if hard_failures else raw_score
    elif reviews != [] or hard_reviews != []:
        raise ValueError("Only a scored presentation benchmark may contain reviewer scores")

    benchmark_passed = bool(stage == "scored" and capped_score is not None and capped_score >= definition["passing_score"] and not hard_failures)
    next_gate = {
        "directions": "human-direction-selection",
        "selected": "private-presentation-and-validation",
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
        "refinement_pass_count": len(normalized_passes),
        "compelling_concept_count": compelling,
        "concept_forming_media_count": concept_forming,
        "sequence_grammar_count": len(sequence_grammars),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
