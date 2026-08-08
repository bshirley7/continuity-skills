#!/usr/bin/env python3
"""Run the bounded offline Continuity Design scenario evaluation."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "lib"))

import design  # noqa: E402
import design_slop  # noqa: E402

SOURCE_REFERENCES = SUITE / "skills" / "continuity-design" / "references"
INSTALLED_REFERENCES = SUITE.parent / "skills" / "continuity-design" / "references"
DEFAULT_REFERENCES = SOURCE_REFERENCES if SOURCE_REFERENCES.is_dir() else INSTALLED_REFERENCES
DEFAULT_CATALOG = DEFAULT_REFERENCES / "catalog.json"
DEFAULT_SCENARIOS = DEFAULT_REFERENCES / "evaluation-scenarios.json"
ACTION_VERBS = {
    "allow",
    "choose",
    "clarify",
    "create",
    "derive",
    "distinguish",
    "establish",
    "explain",
    "give",
    "help",
    "keep",
    "make",
    "name",
    "preserve",
    "provide",
    "set",
    "shape",
    "show",
    "support",
    "use",
}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _words(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _direction_text(direction: dict[str, Any]) -> str:
    values = [direction["summary"], *direction["principles"], *direction["variation_levers"], *direction["tradeoffs"]]
    for rules in direction["design_grammar"].values():
        values.extend(rules)
    return " ".join(values)


def _maximum_similarity(directions: list[dict[str, Any]]) -> float:
    if len(directions) < 2:
        return 0.0
    similarities: list[float] = []
    for left, right in itertools.combinations(directions, 2):
        left_words = _words(_direction_text(left))
        right_words = _words(_direction_text(right))
        union = left_words | right_words
        similarities.append(len(left_words & right_words) / len(union) if union else 1.0)
    return max(similarities)


def _implementation_usefulness(directions: list[dict[str, Any]]) -> float:
    checks: list[bool] = []
    for direction in directions:
        checks.extend(
            [
                len(direction["summary"].split()) >= 8,
                len(direction["principles"]) >= 2,
                bool(direction["variation_levers"]),
                bool(direction["tradeoffs"]),
            ]
        )
        for rules in direction["design_grammar"].values():
            checks.append(bool(rules))
            for rule in rules:
                words = _words(rule)
                checks.append(len(words) >= 8 and bool(words & ACTION_VERBS))
    return sum(checks) / len(checks) if checks else 0.0


def evaluate(catalog_path: Path, scenario_path: Path) -> dict[str, Any]:
    suite = _read_json(scenario_path)
    if suite.get("schema_version") != 1 or not isinstance(suite.get("scenarios"), list):
        raise ValueError("Scenario suite is invalid")
    thresholds = suite.get("thresholds", {})
    required_thresholds = {
        "minimum_routing_precision",
        "minimum_routing_recall",
        "minimum_safeguard_coverage",
        "minimum_conflict_resolution_coverage",
        "maximum_direction_similarity",
        "minimum_implementation_usefulness",
    }
    if set(thresholds) != required_thresholds or any(
        not isinstance(value, (int, float)) or not 0 <= value <= 1
        for value in thresholds.values()
    ):
        raise ValueError("Scenario suite thresholds are invalid")
    catalog = design.load_catalog(catalog_path)
    routing = design.load_lens_routing(catalog_path, catalog)
    composition = design.load_composition_precedence(catalog_path, catalog)
    baseline = set(routing["baseline"])
    available_lenses = set(
        next(pack for pack in catalog["packs"] if pack["axis"] == "lens" and pack["role"] == "foundation")["categories"]
    )
    available_conflicts = {item["conflict_id"] for item in composition["conflicts"]}
    scenario_ids: set[str] = set()
    modalities: set[str] = set()
    industry_groups: set[str] = set()
    for scenario in suite["scenarios"]:
        scenario_id = scenario.get("scenario_id")
        input_value = scenario.get("input")
        modality = scenario.get("modality")
        expected = set(scenario.get("expected_lenses", []))
        forbidden = set(scenario.get("forbidden_lenses", []))
        safeguards = set(scenario.get("required_safeguards", []))
        expected_conflicts = set(scenario.get("expected_conflicts", []))
        expected_content_classifications = set(scenario.get("expected_content_classifications", []))
        if (
            not isinstance(scenario_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]+", scenario_id)
            or scenario_id in scenario_ids
            or not isinstance(input_value, dict)
            or modality not in design.TARGETS
            or modality not in input_value.get("targets", [])
            or not isinstance(scenario.get("industry_group"), str)
            or not scenario["industry_group"].strip()
            or expected & forbidden
            or not (expected | forbidden | safeguards).issubset(available_lenses)
            or not expected_conflicts <= available_conflicts
            or not expected_content_classifications <= design.CONTENT_CLASSIFICATIONS
        ):
            raise ValueError(f"Scenario is invalid: {scenario_id}")
        scenario_ids.add(scenario_id)
        modalities.add(modality)
        industry_groups.add(scenario["industry_group"])
    if len(suite["scenarios"]) < 15 or modalities != design.TARGETS or len(industry_groups) < 10:
        raise ValueError("Scenario suite is not representative across industries and modalities")
    scenario_results: list[dict[str, Any]] = []
    true_positive = false_positive = expected_total = 0
    safeguards_found = safeguards_total = 0
    conflicts_found = conflicts_total = 0
    maximum_similarity = 0.0
    usefulness_values: list[float] = []
    briefing_guidance_checks: list[bool] = []
    collaboration_checks: list[bool] = []
    reference_checks: list[bool] = []
    fidelity_checks: list[bool] = []

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        config = {
            "project_id": "design-evaluation",
            "private_dir": ".continuity/private",
            "collections": ["core", "projects", "design"],
        }
        for index, scenario in enumerate(suite["scenarios"]):
            scenario_id = scenario["scenario_id"]
            payload = dict(scenario["input"])
            payload["design_id"] = f"evaluation-{index + 1:02d}-{scenario_id}"
            creative_fields = {"collaboration_profile", "specialization", "research", "reference_decomposition", "concept_presentation_mode", "rejected_decisions"}
            if creative_fields.intersection(payload):
                seed_payload = {key: value for key, value in payload.items() if key not in creative_fields}
                seed_payload["design_id"] = f"{payload['design_id']}-authored-seed"
                seed_path = root / f"{scenario_id}-authored-seed.json"
                seed_path.write_text(json.dumps(seed_payload), encoding="utf-8")
                seed = design.draft(root, config, catalog_path, seed_path)
                payload.update({
                    "workflow_version": 2,
                    "direction_count": 1,
                    "direction_count_basis": "The benchmark supplies one settled organizing idea and tests contrast separately.",
                    "concept_presentation_mode": "director-led",
                    "research": payload.get("research", {"mode": "offline", "status": "not-started", "announced": True, "opt_out_offered": True, "moodboard": []}),
                    "direction_assessment": {"material_ambiguities": [], "resolved_by_evidence": []},
                    "modality_assessment": {
                        "observed_signals": [f"The scenario targets {scenario['modality']} output."],
                        "selected_targets": payload["targets"],
                        "rationale": "The benchmark modality is explicit.",
                        "conflicts": [],
                    },
                    "directions": [seed["directions"][0]],
                })
            input_path = root / f"{scenario_id}.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            draft = design.draft(root, config, catalog_path, input_path)
            briefing_guidance_checks.append(draft.get("collaboration_profile") in design.COLLABORATION_PROFILES and draft.get("specialization") in design.DESIGN_SPECIALIZATIONS)
            collaboration_checks.append(
                scenario.get("expected_collaboration_profile") is None
                or draft.get("collaboration_profile") == scenario["expected_collaboration_profile"]
            )
            reference_checks.append(
                not payload.get("reference_decomposition")
                or len(draft.get("reference_decomposition", [])) == len(payload["reference_decomposition"])
            )
            fidelity_checks.append(all(
                set(direction.get("design_grammar", {})) == set(design.TARGET_GRAMMAR_DIMENSIONS[scenario["modality"]])
                and all(direction["design_grammar"].values())
                for direction in draft["directions"]
            ))
            selected = set(draft["lenses"])
            contextual = selected - baseline
            expected = set(scenario.get("expected_lenses", []))
            forbidden = set(scenario.get("forbidden_lenses", []))
            safeguards = set(scenario.get("required_safeguards", []))
            missing = sorted(expected - contextual)
            unexpected = sorted(contextual - expected)
            forbidden_selected = sorted(forbidden & selected)
            missing_safeguards = sorted(safeguards - selected)
            expected_conflicts = set(scenario.get("expected_conflicts", []))
            active_conflicts = {
                item["conflict_id"]
                for item in draft["composition_resolution"]["active_conflicts"]
                if item.get("resolution") and item.get("dominant_precedence_id")
            }
            missing_conflicts = sorted(expected_conflicts - active_conflicts)
            unexpected_conflicts = sorted(active_conflicts - expected_conflicts)
            expected_count = scenario.get("expected_direction_count")
            expected_content_classifications = set(scenario.get("expected_content_classifications", []))
            actual_content_classifications = {item["classification"] for item in draft.get("content_provenance", [])}
            content_integrity_ok = expected_content_classifications <= actual_content_classifications
            direction_count_ok = expected_count is None or len(draft["directions"]) == expected_count
            similarity = _maximum_similarity(draft["directions"])
            usefulness = _implementation_usefulness(draft["directions"])
            maximum_similarity = max(maximum_similarity, similarity)
            usefulness_values.append(usefulness)
            true_positive += len(expected & contextual)
            false_positive += len(unexpected)
            expected_total += len(expected)
            safeguards_found += len(safeguards & selected)
            safeguards_total += len(safeguards)
            conflicts_found += len(expected_conflicts & active_conflicts)
            conflicts_total += len(expected_conflicts)
            scenario_results.append(
                {
                    "scenario_id": scenario_id,
                    "industry_group": scenario["industry_group"],
                    "modality": scenario["modality"],
                    "selected_contextual_lenses": sorted(contextual),
                    "missing_expected_lenses": missing,
                    "unexpected_lenses": unexpected,
                    "forbidden_lenses_selected": forbidden_selected,
                    "missing_safeguards": missing_safeguards,
                    "active_conflicts": sorted(active_conflicts),
                    "missing_expected_conflicts": missing_conflicts,
                    "unexpected_conflicts": unexpected_conflicts,
                    "direction_count": len(draft["directions"]),
                    "direction_count_ok": direction_count_ok,
                    "content_integrity_ok": content_integrity_ok,
                    "maximum_direction_similarity": round(similarity, 4),
                    "implementation_usefulness": round(usefulness, 4),
                    "passed": not (
                        missing
                        or unexpected
                        or forbidden_selected
                        or missing_safeguards
                        or missing_conflicts
                        or unexpected_conflicts
                        or not direction_count_ok
                        or not content_integrity_ok
                    ),
                }
            )

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0
    recall = true_positive / expected_total if expected_total else 1.0
    safeguard_coverage = safeguards_found / safeguards_total if safeguards_total else 1.0
    conflict_resolution_coverage = conflicts_found / conflicts_total if conflicts_total else 1.0
    implementation_usefulness = min(usefulness_values, default=0.0)
    fixture_root = DEFAULT_REFERENCES / "slop-fixtures"
    fixture_expectations = _read_json(fixture_root / "expectations.json")
    slop_true_positive = slop_expected = slop_false_positive = 0
    for name, expected_rules in fixture_expectations.items():
        actual = {item["rule_id"] for item in design_slop._scan_text(name, (fixture_root / name).read_text(encoding="utf-8"))}
        expected = set(expected_rules)
        slop_true_positive += len(actual & expected)
        slop_expected += len(expected)
        slop_false_positive += len(actual - expected)
    slop_recall = slop_true_positive / slop_expected if slop_expected else 1.0
    slop_false_positive_rate = slop_false_positive / max(1, sum(len(value) for value in fixture_expectations.values()) + slop_false_positive)
    metrics = {
        "routing_precision": round(precision, 4),
        "routing_recall": round(recall, 4),
        "safeguard_coverage": round(safeguard_coverage, 4),
        "conflict_resolution_coverage": round(conflict_resolution_coverage, 4),
        "maximum_direction_similarity": round(maximum_similarity, 4),
        "minimum_implementation_usefulness": round(implementation_usefulness, 4),
        "briefing_guidance_coverage": round(sum(briefing_guidance_checks) / len(briefing_guidance_checks), 4),
        "collaboration_adaptation": round(sum(collaboration_checks) / len(collaboration_checks), 4),
        "visual_evidence_coverage": 1.0 if all(hasattr(design, name) for name in ("visual_atlas", "visual_render", "concept_validate", "feedback_record")) else 0.0,
        "reference_decomposition_coverage": round(sum(reference_checks) / len(reference_checks), 4),
        "genericity_resistance": round(1.0 - maximum_similarity, 4),
        "direction_fidelity_parity": round(sum(fidelity_checks) / len(fidelity_checks), 4),
        "slop_detection_recall": round(slop_recall, 4),
        "slop_false_positive_rate": round(slop_false_positive_rate, 4),
        "scenario_count": len(scenario_results),
        "passed_scenario_count": sum(1 for result in scenario_results if result["passed"]),
    }
    threshold_results = {
        "routing_precision": precision >= thresholds["minimum_routing_precision"],
        "routing_recall": recall >= thresholds["minimum_routing_recall"],
        "safeguard_coverage": safeguard_coverage >= thresholds["minimum_safeguard_coverage"],
        "conflict_resolution_coverage": conflict_resolution_coverage >= thresholds["minimum_conflict_resolution_coverage"],
        "direction_distinctness": maximum_similarity <= thresholds["maximum_direction_similarity"],
        "implementation_usefulness": implementation_usefulness >= thresholds["minimum_implementation_usefulness"],
    }
    return {
        "schema_version": 1,
        "offline": True,
        "quality_scope": "contract-routing-and-regression-only",
        "output_quality_evidence": "not-measured-run-evaluate-design-outputs",
        "thresholds": thresholds,
        "metrics": metrics,
        "threshold_results": threshold_results,
        "scenarios": scenario_results,
        "healthy": all(threshold_results.values()) and all(result["passed"] for result in scenario_results),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.catalog.resolve(), args.scenarios.resolve())
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
