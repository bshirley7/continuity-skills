#!/usr/bin/env python3
"""Shared creative-pathway checks for Continuity Design benchmarks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable


FRESH = "fresh-concepts"
REVIEW = "existing-design-review"
REFINE = "selected-concept-refinement"
MODES = {FRESH, REVIEW, REFINE}
FRESH_EVIDENCE = {
    "research", "moodboard", "generative_laboratory", "concept_manifest", "comparison",
}
HASH = re.compile(r"^[a-f0-9]{64}$")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_creative_pathway(
    run_root: Path,
    value: Any,
    concepts: list[dict[str, Any]],
    artifact: Callable[[Path, Any, str], dict[str, str]],
    read: Callable[[Path, str], dict[str, Any]],
) -> dict[str, Any]:
    """Require fresh concepts by default and explicit authority for inherited work."""
    if not isinstance(value, dict) or set(value) != {"mode", "diagnosis", "fresh_evidence"}:
        raise ValueError("Workflow-v4 benchmarks require an early creative-pathway diagnosis")
    mode = value.get("mode")
    if mode not in MODES:
        raise ValueError("Benchmark creative pathway is unsupported")
    diagnosis_ref = artifact(run_root, value.get("diagnosis"), "Creative pathway diagnosis")
    diagnosis = read(run_root / diagnosis_ref["path"], "Creative pathway diagnosis")
    if diagnosis.get("status") != "resolved" or diagnosis.get("mode") != mode or not _text(diagnosis.get("question")):
        raise ValueError("Benchmark creative pathway diagnosis is incomplete")

    basis = diagnosis.get("decision_basis")
    instruction = diagnosis.get("user_instruction")
    inherited_design_id = diagnosis.get("inherited_design_id")
    inherited = diagnosis.get("inherited_artifacts")
    prior_hashes = diagnosis.get("prior_artifact_hashes")
    origins = {concept.get("creative_origin") for concept in concepts}
    if not isinstance(prior_hashes, list) or any(not HASH.fullmatch(str(item)) for item in prior_hashes):
        raise ValueError("Benchmark creative pathway diagnosis requires prior artifact hashes")

    if mode == FRESH:
        if len(concepts) != 3:
            raise ValueError("Fresh benchmark runs require exactly three complete design concepts")
        if basis not in {"default-fresh", "explicit-user-instruction"}:
            raise ValueError("Fresh benchmark concepts require the default-fresh or explicit-user-instruction basis")
        if inherited_design_id is not None or inherited != []:
            raise ValueError("Fresh benchmark concepts cannot inherit a prior design or concept artifact")
        if origins != {"fresh"}:
            raise ValueError("Fresh benchmark runs require every concept to declare fresh creative origin")
        evidence = value.get("fresh_evidence")
        if not isinstance(evidence, dict) or set(evidence) != FRESH_EVIDENCE:
            raise ValueError("Fresh benchmark runs require new research, moodboard, laboratory, concept, and comparison evidence")
        normalized = {
            key: artifact(run_root, evidence[key], f"Fresh creative pathway {key.replace('_', ' ')}")
            for key in sorted(FRESH_EVIDENCE)
        }
        hashes = [item["sha256"] for item in normalized.values()]
        if len(set(hashes)) != len(hashes):
            raise ValueError("Fresh benchmark pathway evidence must use distinct artifacts")
        reused = sorted(set(hashes) & set(prior_hashes))
        if reused:
            raise ValueError("Fresh benchmark pathway reuses prior creative evidence")
    else:
        if basis != "explicit-user-instruction" or not _text(instruction):
            raise ValueError("Review or refinement benchmarks require an explicit user instruction")
        if not _text(inherited_design_id) or not isinstance(inherited, list) or not inherited:
            raise ValueError("Review or refinement benchmarks require inherited design provenance")
        if value.get("fresh_evidence") is not None:
            raise ValueError("Review or refinement benchmarks cannot claim a fresh-start evidence bundle")
        expected_origin = "inherited-review" if mode == REVIEW else "inherited-refinement"
        if origins != {expected_origin}:
            raise ValueError(f"Benchmark pathway {mode} requires every concept to declare {expected_origin} origin")
        inherited_refs = [artifact(run_root, item, f"Inherited creative artifact {index}") for index, item in enumerate(inherited, 1)]
        if not {item["sha256"] for item in inherited_refs} <= set(prior_hashes):
            raise ValueError("Review or refinement diagnosis does not bind inherited artifact hashes")

    return {"mode": mode, "decision_basis": basis, "diagnosis": diagnosis_ref}
