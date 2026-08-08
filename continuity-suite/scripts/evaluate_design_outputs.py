#!/usr/bin/env python3
"""Evaluate blinded, paired design artifacts without using workflow completion as a quality proxy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Benchmark manifest must be an object")
    return value


def _artifact(root: Path, value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or not isinstance(value.get("path"), str):
        raise ValueError(f"{label} artifact requires path and sha256")
    path = (root / value["path"]).resolve()
    try:
        relative = path.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label} artifact escapes the benchmark root") from exc
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != value.get("sha256"):
        raise ValueError(f"{label} artifact is missing or changed: {relative}")
    return {"path": relative, "sha256": value["sha256"]}


def evaluate(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _read(manifest_path)
    dimensions = manifest.get("dimensions")
    thresholds = manifest.get("thresholds")
    cases = manifest.get("cases")
    if manifest.get("schema_version") != 1 or not isinstance(dimensions, list) or len(set(dimensions)) != len(dimensions) or len(dimensions) < 3:
        raise ValueError("Benchmark requires at least three unique dimensions")
    if not isinstance(thresholds, dict) or not isinstance(cases, list):
        raise ValueError("Benchmark requires thresholds and cases")
    required_thresholds = {"minimum_cases", "minimum_reviewers_per_case", "minimum_mean_lift", "minimum_candidate_win_rate", "maximum_dimension_regression"}
    if set(thresholds) != required_thresholds:
        raise ValueError("Benchmark thresholds are incomplete")
    if (
        not isinstance(thresholds["minimum_cases"], int) or thresholds["minimum_cases"] < 3
        or not isinstance(thresholds["minimum_reviewers_per_case"], int) or thresholds["minimum_reviewers_per_case"] < 2
        or not isinstance(thresholds["minimum_mean_lift"], (int, float))
        or not isinstance(thresholds["minimum_candidate_win_rate"], (int, float)) or not 0 <= thresholds["minimum_candidate_win_rate"] <= 1
        or not isinstance(thresholds["maximum_dimension_regression"], (int, float)) or thresholds["maximum_dimension_regression"] > 0
    ):
        raise ValueError("Benchmark thresholds require at least three cases, two reviewers, and valid lift, win-rate, and regression bounds")
    seen_cases: set[str] = set()
    dimension_deltas = {dimension: [] for dimension in dimensions}
    pair_wins = pair_total = 0
    normalized_cases = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str) or case["case_id"] in seen_cases:
            raise ValueError("Benchmark case IDs must be unique")
        brief_hash = case.get("brief_hash")
        if not isinstance(brief_hash, str) or len(brief_hash) != 64:
            raise ValueError(f"Benchmark case {case['case_id']} requires a brief hash")
        baseline = _artifact(root, case.get("baseline"), "Baseline")
        candidate = _artifact(root, case.get("candidate"), "Candidate")
        if baseline["sha256"] == candidate["sha256"]:
            raise ValueError(f"Benchmark case {case['case_id']} must compare distinct renders")
        ratings = case.get("ratings")
        if not isinstance(ratings, list) or len(ratings) < thresholds["minimum_reviewers_per_case"]:
            raise ValueError(f"Benchmark case {case['case_id']} lacks independent reviewers")
        reviewer_ids: set[str] = set()
        normalized_ratings = []
        for rating in ratings:
            if not isinstance(rating, dict) or rating.get("blind") is not True or not isinstance(rating.get("reviewer_id"), str) or rating["reviewer_id"] in reviewer_ids:
                raise ValueError(f"Benchmark case {case['case_id']} requires unique blinded reviewers")
            baseline_scores = rating.get("baseline_scores")
            candidate_scores = rating.get("candidate_scores")
            if not isinstance(baseline_scores, dict) or not isinstance(candidate_scores, dict) or set(baseline_scores) != set(dimensions) or set(candidate_scores) != set(dimensions):
                raise ValueError("Every reviewer must score every benchmark dimension")
            deltas = {}
            for dimension in dimensions:
                left, right = baseline_scores[dimension], candidate_scores[dimension]
                if not isinstance(left, int) or not isinstance(right, int) or not 1 <= left <= 5 or not 1 <= right <= 5:
                    raise ValueError("Benchmark scores must be integers from one to five")
                delta = right - left
                deltas[dimension] = delta
                dimension_deltas[dimension].append(delta)
            mean_delta = sum(deltas.values()) / len(dimensions)
            pair_wins += mean_delta > 0
            pair_total += 1
            normalized_ratings.append({"reviewer_id": rating["reviewer_id"], "blind": True, "deltas": deltas, "mean_delta": round(mean_delta, 4)})
            reviewer_ids.add(rating["reviewer_id"])
        normalized_cases.append({"case_id": case["case_id"], "brief_hash": brief_hash, "baseline": baseline, "candidate": candidate, "ratings": normalized_ratings})
        seen_cases.add(case["case_id"])
    means = {dimension: sum(values) / len(values) for dimension, values in dimension_deltas.items() if values}
    overall = sum(means.values()) / len(means) if means else 0.0
    win_rate = pair_wins / pair_total if pair_total else 0.0
    healthy = (
        len(cases) >= thresholds["minimum_cases"]
        and overall >= thresholds["minimum_mean_lift"]
        and win_rate >= thresholds["minimum_candidate_win_rate"]
        and all(value >= thresholds["maximum_dimension_regression"] for value in means.values())
    )
    return {"schema_version": 1, "blind": True, "case_count": len(cases), "pair_count": pair_total, "mean_lift": round(overall, 4), "candidate_win_rate": round(win_rate, 4), "dimension_lift": {key: round(value, 4) for key, value in means.items()}, "cases": normalized_cases, "healthy": healthy}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.root.resolve(), args.manifest.resolve())
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
