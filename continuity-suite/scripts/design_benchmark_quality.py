"""Shared rendered-quality checks for Continuity Design benchmarks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable


HASH = re.compile(r"^[a-f0-9]{64}$")
HARD_REJECTIONS = {
    "generic_card_grid_first_impression", "beautiful_image_weak_brand",
    "strong_headline_without_action", "busy_imagery_behind_text",
    "repeated_mood_statements", "purposeless_carousel",
    "stacked_cards_as_layout", "default_primary_typeface",
    "undersized_body_copy", "desktop_stack_on_mobile",
}
VISUAL_REVIEW_CORE = {
    "decoration_has_job", "directions_structurally_distinct", "identity_specific",
    "not_category_reflex", "not_library_default", "reference_transformed",
    "signature_identifiable", "signature_survives_states",
}
QUALITY_DIMENSIONS = {
    "hierarchy", "product_proof", "interaction_or_sequence",
    "responsive_transformation", "identity", "craft",
}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _bound_artifact(run_root: Path, value: Any, label: str, artifact: Callable) -> dict[str, str]:
    """Resolve a hash-bound artifact whether its report path is run- or project-relative."""
    try:
        return artifact(run_root, value, label)
    except ValueError as direct_error:
        if not isinstance(value, dict) or not _text(value.get("path")) or not HASH.fullmatch(str(value.get("sha256") or "")):
            raise direct_error
        requested = Path(value["path"])
        candidates: list[Path] = []
        parts = requested.parts
        if run_root.name in parts:
            suffix = Path(*parts[parts.index(run_root.name) + 1 :])
            candidate = (run_root / suffix).resolve()
            if candidate.is_relative_to(run_root.resolve()) and candidate.is_file():
                candidates.append(candidate)
        for candidate in run_root.rglob(requested.name):
            resolved = candidate.resolve()
            if resolved.is_relative_to(run_root.resolve()) and resolved.is_file() and resolved not in candidates:
                candidates.append(resolved)
        matches = [
            candidate for candidate in candidates
            if hashlib.sha256(candidate.read_bytes()).hexdigest() == value["sha256"]
        ]
        if len(matches) != 1:
            raise direct_error
        return {"path": matches[0].relative_to(run_root.resolve()).as_posix(), "sha256": value["sha256"]}


def _png(run_root: Path, value: Any, label: str, artifact: Callable, dimensions: Callable) -> dict[str, str]:
    normalized = _bound_artifact(run_root, value, label, artifact)
    path = run_root / normalized["path"]
    if path.suffix.lower() != ".png":
        raise ValueError(f"{label} must be encoded PNG evidence")
    dimensions(path)
    return normalized


def validate_slop_report(run_root: Path, report: dict[str, Any], label: str, artifact: Callable, dimensions: Callable) -> None:
    """Reject status stubs that did not come from the complete slop workflow."""
    if (
        report.get("schema_version") != 1 or report.get("status") != "passed"
        or report.get("stage") != "concept" or not _text(report.get("ruleset_version"))
        or not _text(report.get("checked_at")) or not _text(report.get("target"))
        or any(not HASH.fullmatch(str(report.get(key) or "")) for key in ("ruleset_hash", "report_hash", "source_bundle_hash"))
        or not isinstance(report.get("files"), list) or not report["files"]
    ):
        raise ValueError(f"{label} is not a complete Continuity slop-check report")
    for index, item in enumerate(report["files"], 1):
        _bound_artifact(run_root, item, f"{label} source file {index}", artifact)
    review = report.get("visual_review")
    if not isinstance(review, dict) or not VISUAL_REVIEW_CORE <= set(review):
        raise ValueError(f"{label} lacks the required screenshot-bound visual review")
    for question in sorted(VISUAL_REVIEW_CORE):
        answer = review[question]
        if (
            not isinstance(answer, dict) or answer.get("result") not in {"pass", "not-applicable"}
            or not _text(answer.get("reviewer")) or not _text(answer.get("reviewed_at"))
            or not _text(answer.get("rationale")) or not isinstance(answer.get("evidence"), list)
            or not answer["evidence"]
        ):
            raise ValueError(f"{label} visual review {question} is incomplete")
        for index, evidence in enumerate(answer["evidence"], 1):
            _png(run_root, evidence, f"{label} {question} evidence {index}", artifact, dimensions)


def validate_quality_review(run_root: Path, value: Any, direction_id: str, artifact: Callable, read: Callable, dimensions: Callable, *, require_attestation: bool = False) -> dict[str, Any]:
    """Require an independent visual-first quality decision before consultation."""
    normalized = artifact(run_root, value, f"Design quality review {direction_id}")
    review = read(run_root / normalized["path"], f"Design quality review {direction_id}")
    hard = review.get("hard_rejections")
    story = review.get("value_story")
    if (
        review.get("schema_version") not in {1, 2} or review.get("status") != "passed"
        or review.get("direction_id") != direction_id
        or review.get("reviewer_type") not in {"human", "independent-agent"}
        or not _text(review.get("producer_id")) or not _text(review.get("reviewer_id"))
        or review.get("producer_id") == review.get("reviewer_id") or not _text(review.get("reviewed_at"))
        or not isinstance(review.get("design_score"), (int, float)) or isinstance(review.get("design_score"), bool)
        or review["design_score"] < 75 or review.get("ai_slop_grade") not in {"A", "B"}
        or not isinstance(hard, dict) or set(hard) != HARD_REJECTIONS or any(item is not False for item in hard.values())
        or not isinstance(story, dict)
        or any(not _text(story.get(key)) for key in ("user_outcome", "primary_action", "product_proof", "five_second_reaction"))
        or not isinstance(review.get("findings"), list)
    ):
        raise ValueError(f"Concept {direction_id} lacks an independent passing design-quality review")
    wide = _png(run_root, review.get("wide_evidence"), f"Design quality review {direction_id} wide evidence", artifact, dimensions)
    narrow = _png(run_root, review.get("narrow_evidence"), f"Design quality review {direction_id} narrow evidence", artifact, dimensions)
    if wide["sha256"] == narrow["sha256"]:
        raise ValueError(f"Concept {direction_id} quality review reuses wide evidence as its narrow transformation")
    result = {"review": normalized, "design_score": review["design_score"], "ai_slop_grade": review["ai_slop_grade"], "wide_evidence": wide, "narrow_evidence": narrow}
    if require_attestation and review.get("schema_version") != 2:
        raise ValueError(f"Concept {direction_id} requires an attested dimension-level quality review")
    if review.get("schema_version") == 2:
        scores = review.get("dimension_scores")
        attestation = review.get("review_attestation")
        dispositions = review.get("warning_dispositions")
        if (
            not isinstance(scores, dict) or set(scores) != QUALITY_DIMENSIONS
            or any(not isinstance(score, (int, float)) or isinstance(score, bool) or score < 70 or score > 100 for score in scores.values())
            or abs(sum(scores.values()) / len(scores) - review["design_score"]) > 10
            or not isinstance(review.get("comparative_rank"), int) or not 1 <= review["comparative_rank"] <= 3
            or not isinstance(review.get("confidence"), (int, float)) or isinstance(review.get("confidence"), bool) or not 0.5 <= review["confidence"] <= 1
            or not isinstance(attestation, dict) or attestation.get("independent_from_producer") is not True
            or attestation.get("method") not in {"human-session", "independent-agent-run", "blinded-panel"}
            or not _text(attestation.get("run_id"))
            or not isinstance(dispositions, list)
        ):
            raise ValueError(f"Concept {direction_id} lacks dimension floors or independent review attestation")
        raw_review = _bound_artifact(run_root, attestation.get("raw_review"), f"Design quality review {direction_id} raw attestation", artifact)
        normalized_dispositions = []
        for index, disposition in enumerate(dispositions, 1):
            if not isinstance(disposition, dict) or not _text(disposition.get("rule_id")) or not _text(disposition.get("rationale")):
                raise ValueError(f"Concept {direction_id} warning disposition {index} is incomplete")
            evidence = disposition.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                raise ValueError(f"Concept {direction_id} warning disposition {index} lacks bound evidence")
            normalized_evidence = [
                _bound_artifact(run_root, item, f"Design quality review {direction_id} warning {index} evidence", artifact)
                for item in evidence
            ]
            normalized_dispositions.append({"rule_id": disposition["rule_id"], "rationale": disposition["rationale"].strip(), "evidence": normalized_evidence})
        result.update({
            "dimension_scores": scores,
            "comparative_rank": review["comparative_rank"],
            "confidence": review["confidence"],
            "review_run_id": attestation["run_id"],
            "raw_review": raw_review,
            "warning_disposition_fingerprint": hashlib.sha256(json.dumps(normalized_dispositions, sort_keys=True).encode()).hexdigest() if normalized_dispositions else None,
        })
    return result


def validate_quality_review_set(reviews: list[dict[str, Any]]) -> None:
    """Prevent one attestation or copy-pasted warning waiver from standing in for independent concept review."""
    raw_hashes = [item.get("raw_review", {}).get("sha256") for item in reviews]
    ranks = [item.get("comparative_rank") for item in reviews]
    fingerprints = [item.get("warning_disposition_fingerprint") for item in reviews if item.get("warning_disposition_fingerprint")]
    if any(raw_hashes) and len(set(raw_hashes)) != len(raw_hashes):
        raise ValueError("Every concept requires its own raw independent quality-review attestation")
    if any(rank is not None for rank in ranks) and sorted(ranks) != list(range(1, len(reviews) + 1)):
        raise ValueError("Comparative quality-review ranks must uniquely cover the complete concept set")
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Identical warning dispositions across concepts require a house-tell review instead of copied waivers")


def validate_runtime_evidence(
    run_root: Path,
    concept: dict[str, Any],
    direction_id: str,
    artifact: Callable,
    read: Callable,
    *,
    presentation: bool = False,
) -> dict[str, Any]:
    """Validate raw collision-aware browser output instead of producer-authored pass booleans."""
    probes = concept.get("runtime_probes")
    expected_widths = {"mobile": 390, "tablet": 768, "desktop": 1440}
    if not isinstance(probes, list) or len(probes) != 3:
        raise ValueError(f"Concept {direction_id} requires mobile, tablet, and desktop raw runtime probes")
    normalized: dict[str, dict[str, str]] = {}
    payloads: dict[str, dict[str, Any]] = {}
    target_hashes: set[str] = set()
    source_hashes: set[str] = set()
    required_roles = {"opening", "proof", "interaction", "closure"}
    for value in probes:
        viewport = value.get("viewport") if isinstance(value, dict) else None
        if viewport not in expected_widths or viewport in normalized:
            raise ValueError(f"Concept {direction_id} runtime probes must uniquely cover mobile, tablet, and desktop")
        evidence = _bound_artifact(run_root, value, f"Concept {direction_id} {viewport} runtime probe", artifact)
        probe = read(run_root / evidence["path"], f"Concept {direction_id} {viewport} runtime probe")
        roles = {
            role
            for item in probe.get("signature_elements", []) if isinstance(item, dict) and item.get("visible") is True
            for role in item.get("roles", []) if isinstance(role, str)
        }
        opening = [
            item for item in probe.get("opening_signature_elements", [])
            if isinstance(item, dict) and item.get("visible") is True and item.get("viewport_intersection_ratio", 0) >= 0.1
        ]
        if (
            probe.get("schema_version") != 4
            or probe.get("probe_kind") != "continuity-artifact-browser-probe"
            or probe.get("passed") is not True
            or probe.get("viewport", {}).get("width") != expected_widths[viewport]
            or probe.get("horizontal_overflow") is not False
            or probe.get("sticky_or_fixed_obstructions") != []
            or probe.get("text_clipping") != []
            or probe.get("content_collisions") != []
            or not required_roles <= roles
            or not {"quiet-state", "edge-state"}.intersection(roles)
            or (viewport in {"mobile", "desktop"} and not opening)
        ):
            raise ValueError(f"Concept {direction_id} {viewport} runtime evidence lacks collision-free signature and opening-carrier proof")
        if presentation and (
            probe.get("presentation_readability_passed") is not True
            or not isinstance(probe.get("presentation_slides"), list)
            or len(probe["presentation_slides"]) < 4
        ):
            raise ValueError(f"Presentation concept {direction_id} lacks readable raw slide-role evidence")
        target_hashes.add(str(probe.get("target_document_sha256") or ""))
        source_hashes.add(str(probe.get("source_bundle_sha256") or ""))
        normalized[viewport] = evidence
        payloads[viewport] = probe
    if len(target_hashes) != 1 or "" in target_hashes or len(source_hashes) != 1 or "" in source_hashes:
        raise ValueError(f"Concept {direction_id} runtime probes are stale or do not bind one source bundle")

    interaction_mode = concept.get("interaction_mode")
    state_probes = concept.get("interaction_state_probes")
    if interaction_mode == "static":
        if not _text(concept.get("static_interaction_rationale")):
            raise ValueError(f"Concept {direction_id} static interaction requires an explicit rationale")
        state_count = 0
    else:
        if not isinstance(state_probes, list) or len(state_probes) < 2:
            raise ValueError(f"Concept {direction_id} requires at least two raw interaction-state probes")
        state_payloads = []
        invariant_fingerprints = set()
        state_fingerprints = set()
        for index, value in enumerate(state_probes, 1):
            evidence = _bound_artifact(run_root, value, f"Concept {direction_id} interaction state {index}", artifact)
            probe = read(run_root / evidence["path"], f"Concept {direction_id} interaction state {index}")
            if (
                probe.get("schema_version") != 4 or probe.get("passed") is not True
                or str(probe.get("target_document_sha256") or "") not in target_hashes
                or str(probe.get("source_bundle_sha256") or "") not in source_hashes
                or not isinstance(probe.get("interaction_states"), list) or not probe["interaction_states"]
                or not isinstance(probe.get("interaction_invariants"), list) or not probe["interaction_invariants"]
            ):
                raise ValueError(f"Concept {direction_id} interaction state {index} is stale or lacks measurable state and invariant evidence")
            invariant_fingerprints.add(hashlib.sha256(json.dumps(probe["interaction_invariants"], sort_keys=True).encode()).hexdigest())
            state_fingerprints.add(hashlib.sha256(json.dumps(probe["interaction_states"], sort_keys=True).encode()).hexdigest())
            state_payloads.append(evidence)
        if len(invariant_fingerprints) != 1 or len(state_fingerprints) < 2:
            raise ValueError(f"Concept {direction_id} interaction must visibly change state without changing protected invariants")
        state_count = len(state_payloads)
    return {
        "runtime_probes": normalized,
        "target_document_sha256": next(iter(target_hashes)),
        "source_bundle_sha256": next(iter(source_hashes)),
        "interaction_state_count": state_count,
    }


def validate_native_concept_set(
    run_root: Path,
    value: Any,
    direction_ids: set[str],
    laboratory_hash: str,
    reference_translation_hash: str,
    artifact: Callable,
    read: Callable,
) -> dict[str, Any]:
    """Bind the benchmark to the actual native concept-validate command result."""
    normalized = _bound_artifact(run_root, value, "Native concept-set validation", artifact)
    report = read(run_root / normalized["path"], "Native concept-set validation")
    if (
        report.get("schema_version") != 1
        or report.get("validator") != "continuity design concept-validate"
        or report.get("validation_status") != "passed"
        or report.get("workflow_version") != 4
        or report.get("execution_authorized") is not False
        or report.get("concept_count") != len(direction_ids)
        or set(report.get("concept_ids", [])) != direction_ids
        or report.get("generative_laboratory_hash") != laboratory_hash
        or report.get("reference_translation_hash") != reference_translation_hash
        or report.get("per_concept_runtime_probes") is not True
        or report.get("range_audit_status") != "passed"
        or report.get("grammar_congruence_status") != "passed"
        or report.get("journey_structure_status") != "passed"
        or report.get("impact_review_status") != "passed"
        or not HASH.fullmatch(str(report.get("portfolio_report_hash") or ""))
        or not HASH.fullmatch(str(report.get("concept_manifest_hash") or ""))
    ):
        raise ValueError("Benchmark lacks a current passed native concept-validate result")
    return normalized


def validate_handoff_proof(
    run_root: Path,
    value: Any,
    direction_id: str,
    artifact: Callable,
    read: Callable,
    dimensions: Callable,
) -> dict[str, Any]:
    """Require one concrete screenshot-bound before/evidence/decision/after handoff."""
    normalized = _bound_artifact(run_root, value, f"Concept {direction_id} handoff proof", artifact)
    report = read(run_root / normalized["path"], f"Concept {direction_id} handoff proof")
    steps = report.get("steps")
    if (
        report.get("schema_version") != 1 or report.get("status") != "passed"
        or report.get("direction_id") != direction_id or not isinstance(steps, dict)
        or set(steps) != {"before", "evidence", "decision", "after", "decision_actor", "protected_invariant"}
        or any(not _text(steps.get(key)) for key in steps)
    ):
        raise ValueError(f"Concept {direction_id} lacks a concrete end-to-end handoff proof")
    evidence = report.get("evidence")
    if not isinstance(evidence, list) or len(evidence) < 2:
        raise ValueError(f"Concept {direction_id} handoff proof requires before and after rendered evidence")
    rendered = [
        _png(run_root, item, f"Concept {direction_id} handoff evidence {index}", artifact, dimensions)
        for index, item in enumerate(evidence, 1)
    ]
    if len({item["sha256"] for item in rendered}) != len(rendered):
        raise ValueError(f"Concept {direction_id} handoff proof must show a real rendered change")
    return {"report": normalized, "evidence": rendered}
