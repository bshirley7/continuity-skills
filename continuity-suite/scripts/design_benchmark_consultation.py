"""Shared workflow-v4 consultation checks for Continuity Design benchmarks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable


HASH = re.compile(r"^[a-f0-9]{64}$")
REACTIONS = {"keep", "change", "avoid", "uncertain"}
GUIDELINE_CHECKS = {
    "palette", "typography", "licensed_assets", "motion", "primary_carrier",
    "responsive_probes", "provenance",
}


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _artifact_json(
    run_root: Path,
    value: Any,
    label: str,
    artifact: Callable[[Path, Any, str], dict[str, str]],
    read: Callable[[Path, str], dict[str, Any]],
) -> tuple[dict[str, str], dict[str, Any]]:
    normalized = artifact(run_root, value, label)
    return normalized, read(run_root / normalized["path"], label)


def validate_concept_contracts(
    run_root: Path,
    concepts: list[dict[str, Any]],
    artifact: Callable[[Path, Any, str], dict[str, str]],
    read: Callable[[Path, str], dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """Validate concrete consultation/guideline artifacts for every v4 concept."""
    contracts: dict[str, dict[str, str]] = {}
    for concept in concepts:
        direction_id = concept.get("direction_id")
        if not _text(direction_id):
            raise ValueError("Every workflow-v4 benchmark concept requires a direction_id")
        _, summary = _artifact_json(run_root, concept.get("consultation_summary"), f"Consultation summary {direction_id}", artifact, read)
        safe = summary.get("safe_choices")
        risks = summary.get("creative_risks")
        if (
            not _text(summary.get("memorable_thing"))
            or not _text(summary.get("coherence_rationale"))
            or not isinstance(safe, list) or not 2 <= len(safe) <= 3
            or any(not isinstance(item, dict) or not _text(item.get("decision")) or not _text(item.get("rationale")) for item in safe)
            or not isinstance(risks, list) or not 2 <= len(risks) <= 3
            or any(
                not isinstance(item, dict)
                or any(not _text(item.get(key)) for key in ("move", "rationale", "gain", "cost", "boundary"))
                for item in risks
            )
        ):
            raise ValueError(f"Concept {direction_id} lacks a complete workflow-v4 consultation summary")

        _, guideline = _artifact_json(run_root, concept.get("brand_guideline"), f"Brand guideline {direction_id}", artifact, read)
        guideline_hash = concept.get("brand_guideline_hash")
        concept_evidence_hash = concept.get("concept_evidence_hash")
        if not HASH.fullmatch(str(guideline_hash or "")) or guideline_hash != canonical_hash(guideline):
            raise ValueError(f"Concept {direction_id} brand guideline hash is missing or stale")
        if not HASH.fullmatch(str(concept_evidence_hash or "")):
            raise ValueError(f"Concept {direction_id} lacks a current concept-evidence hash")
        required_guideline_sections = {"identity", "color", "typography", "spatial", "form_assets", "motion", "voice", "application_modes", "governance"}
        if not required_guideline_sections <= set(guideline):
            raise ValueError(f"Concept {direction_id} brand guideline is incomplete")

        _, validation = _artifact_json(run_root, concept.get("brand_guideline_validation"), f"Brand guideline validation {direction_id}", artifact, read)
        checks = validation.get("checks")
        if (
            validation.get("status") != "passed"
            or validation.get("direction_id") != direction_id
            or validation.get("brand_guideline_hash") != guideline_hash
            or validation.get("concept_evidence_hash") != concept_evidence_hash
            or not isinstance(checks, dict)
            or set(checks) != GUIDELINE_CHECKS
            or any(value != "passed" for value in checks.values())
        ):
            raise ValueError(f"Concept {direction_id} brand guideline drifts from validated concept evidence")
        contracts[direction_id] = {
            "brand_guideline_hash": guideline_hash,
            "concept_evidence_hash": concept_evidence_hash,
        }
    return contracts


def validate_consultation(
    run_root: Path,
    value: Any,
    concept_contracts: dict[str, dict[str, str]],
    artifact: Callable[[Path, Any, str], dict[str, str]],
    read: Callable[[Path, str], dict[str, Any]],
) -> dict[str, Any]:
    """Validate board/feedback/delta ordering and return the final binding."""
    if not isinstance(value, dict) or not _text(value.get("design_id")):
        raise ValueError("Workflow-v4 benchmark requires design consultation evidence")
    if value.get("private") is not True or value.get("execution_authorized") is not False:
        raise ValueError("Benchmark consultation must remain private and non-authorizing")
    rounds = value.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        raise ValueError("Benchmark consultation requires at least one feedback round")

    design_id = value["design_id"]
    previous_revision = None
    material_count = 0
    final: dict[str, Any] | None = None
    for number, item in enumerate(rounds, 1):
        if not isinstance(item, dict) or item.get("round") != number:
            raise ValueError("Consultation feedback rounds must be consecutive and one-based")
        board = artifact(run_root, item.get("board"), f"Consultation board round {number}")
        _, snapshot = _artifact_json(run_root, item.get("snapshot"), f"Consultation snapshot round {number}", artifact, read)
        _, feedback = _artifact_json(run_root, item.get("feedback"), f"Consultation feedback round {number}", artifact, read)
        _, record = _artifact_json(run_root, item.get("record"), f"Consultation feedback record round {number}", artifact, read)
        revision = snapshot.get("revision")
        board_hash = snapshot.get("board_hash")
        evidence_hash = snapshot.get("concept_evidence_hash")
        if (
            snapshot.get("private") is not True
            or snapshot.get("execution_authorized") is not False
            or snapshot.get("design_id") != design_id
            or not isinstance(revision, int) or revision < 1
            or not HASH.fullmatch(str(board_hash or ""))
            or not HASH.fullmatch(str(evidence_hash or ""))
        ):
            raise ValueError(f"Consultation snapshot round {number} has an invalid binding")
        board_text = (run_root / board["path"]).read_text(encoding="utf-8")
        if board_hash not in board_text or evidence_hash not in board_text:
            raise ValueError(f"Consultation board round {number} is not bound to its snapshot")
        if previous_revision is not None and revision != previous_revision:
            raise ValueError(f"Consultation round {number} does not use the revision created by prior feedback")
        if any(feedback.get(key) != expected for key, expected in {
            "design_id": design_id,
            "revision": revision,
            "board_hash": board_hash,
            "concept_evidence_hash": evidence_hash,
        }.items()):
            raise ValueError(f"Consultation feedback round {number} is stale")
        if feedback.get("ready_for_selection") is True and feedback.get("actor_type") != "human":
            raise ValueError("Only human consultation feedback may mark a concept set ready for selection")
        reactions = feedback.get("reactions")
        if (
            not isinstance(reactions, list) or not reactions
            or any(
                not isinstance(reaction, dict)
                or reaction.get("reaction") not in REACTIONS
                or not _text(reaction.get("element_id"))
                or not _text(reaction.get("why"))
                for reaction in reactions
            )
        ):
            raise ValueError(f"Consultation feedback round {number} lacks structured rationale")
        material = feedback.get("contract_changed") is True or any(reaction["reaction"] in {"change", "avoid"} for reaction in reactions)
        ready = feedback.get("ready_for_selection") is True
        if material and ready:
            raise ValueError("Material consultation feedback cannot be ready for selection")
        if (
            record.get("design_id") != design_id
            or record.get("feedback_round") != number
            or record.get("execution_authorized") is not False
        ):
            raise ValueError(f"Consultation feedback record round {number} is not bound")
        if material:
            material_count += 1
            if record.get("revision") != revision + 1 or record.get("visual_delta_status") != "pending" or record.get("status") != "refining":
                raise ValueError(f"Material consultation round {number} did not advance revision with a pending delta")
            _, delta_input = _artifact_json(run_root, item.get("delta_input"), f"Consultation delta input round {number}", artifact, read)
            _, delta_record = _artifact_json(run_root, item.get("delta_record"), f"Consultation delta record round {number}", artifact, read)
            if delta_input.get("status") != "passed" or any(not _text(delta_input.get(key)) for key in ("reviewer", "reviewed_at")):
                raise ValueError(f"Consultation delta round {number} lacks passed human review")
            for key in ("path", "before", "after"):
                artifact(run_root, delta_input.get(key), f"Consultation delta {key} round {number}")
            if delta_input["before"]["sha256"] == delta_input["after"]["sha256"]:
                raise ValueError(f"Consultation delta round {number} has identical before and after evidence")
            if (
                delta_record.get("design_id") != design_id
                or delta_record.get("revision") != revision + 1
                or delta_record.get("feedback_round") != number
                or delta_record.get("visual_delta_status") != "bound"
                or delta_record.get("execution_authorized") is not False
            ):
                raise ValueError(f"Consultation delta round {number} is not bound to material feedback")
            previous_revision = revision + 1
        else:
            if item.get("delta_input") is not None or item.get("delta_record") is not None:
                raise ValueError(f"Keep-only consultation round {number} cannot claim a material delta")
            if record.get("revision") != revision or record.get("visual_delta_status") != "not-required":
                raise ValueError(f"Keep-only consultation round {number} has an invalid feedback result")
            previous_revision = revision
        final = {"snapshot": snapshot, "feedback": feedback, "record": record}

    assert final is not None
    if final["feedback"].get("ready_for_selection") is not True or final["record"].get("status") != "awaiting-selection":
        raise ValueError("Benchmark consultation must finish explicitly ready for selection")
    final_snapshot = final["snapshot"]
    snapshot_concepts = final_snapshot.get("concepts")
    if not isinstance(snapshot_concepts, list):
        raise ValueError("Final consultation snapshot lacks concepts")
    snapshot_contracts = {
        item.get("direction_id"): item.get("brand_guideline_hash")
        for item in snapshot_concepts if isinstance(item, dict) and item.get("direction_id")
    }
    expected_contracts = {key: item["brand_guideline_hash"] for key, item in concept_contracts.items()}
    if snapshot_contracts != expected_contracts:
        raise ValueError("Final consultation board does not contain the current concept guidelines")
    final_evidence_hashes = {item["concept_evidence_hash"] for item in concept_contracts.values()}
    if len(final_evidence_hashes) != 1 or final_snapshot.get("concept_evidence_hash") not in final_evidence_hashes:
        raise ValueError("Final consultation board is stale against concept evidence")
    return {
        "design_id": design_id,
        "revision": final["record"]["revision"],
        "board_hash": final_snapshot["board_hash"],
        "concept_evidence_hash": final_snapshot["concept_evidence_hash"],
        "round_count": len(rounds),
        "material_round_count": material_count,
        "preferred_direction_id": final["feedback"].get("preferred_direction_id"),
    }
