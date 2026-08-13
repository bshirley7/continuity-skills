"""Shared rendered-quality checks for Continuity Design benchmarks."""

from __future__ import annotations

import hashlib
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


def validate_quality_review(run_root: Path, value: Any, direction_id: str, artifact: Callable, read: Callable, dimensions: Callable) -> dict[str, Any]:
    """Require an independent visual-first quality decision before consultation."""
    normalized = artifact(run_root, value, f"Design quality review {direction_id}")
    review = read(run_root / normalized["path"], f"Design quality review {direction_id}")
    hard = review.get("hard_rejections")
    story = review.get("value_story")
    if (
        review.get("schema_version") != 1 or review.get("status") != "passed"
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
    return {"review": normalized, "design_score": review["design_score"], "ai_slop_grade": review["ai_slop_grade"], "wide_evidence": wide, "narrow_evidence": narrow}
