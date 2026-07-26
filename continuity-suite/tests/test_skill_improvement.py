from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SUITE = Path(__file__).resolve().parents[1]
CLI = SUITE / "bin" / "continuity"


class SkillImprovementTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        (self.root / ".continuity").mkdir()
        self.write_json(
            self.root / ".continuity" / "config.json",
            {
                "schema_version": 1,
                "assurance_standard_version": 2,
                "project_id": "skill-improvement-test",
                "integration_branch": "main",
                "timezone": "America/Chicago",
                "private_dir": ".continuity/private",
                "memory_docs": "docs/project-memory",
                "roadmap_docs": "docs/project-roadmap",
            },
        )
        source = SUITE / "skills" / "continuity-report"
        target = self.root / ".agents" / "skills" / "continuity-report"
        shutil.copytree(source, target)
        self.skill = target / "SKILL.md"
        self.playbook = target / "references" / "learned-playbook.md"
        self.original_skill = self.skill.read_text(encoding="utf-8")
        self.original_playbook = self.playbook.read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(CLI), "--project-root", str(self.root), "--json", *args],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def baseline(self) -> dict:
        return json.loads(self.cli("improve", "baseline", "continuity-report").stdout)

    def usage(self, usage_id: str, outcome: str = "failure") -> dict:
        baseline = self.baseline()
        value = {
            "usage_id": usage_id,
            "skill_name": "continuity-report",
            "skill_sha256": baseline["skill_sha256"],
            "playbook_sha256": baseline["playbook_sha256"],
            "recorded_at": f"2026-07-22T12:00:0{usage_id[-1]}-05:00",
            "task_kind": "morning-report",
            "outcome": outcome,
            "summary": "A sanitized reusable status-report outcome.",
            "pattern_keys": ["report-false-completion"],
            "signals": {
                "user_corrected": outcome != "success",
                "retries": 1 if outcome != "success" else 0,
                "tool_failures": 0,
                "clarifications": 0,
                "validation_status": "failed" if outcome != "success" else "passed",
                "workflow_disposition": "review-ready",
            },
            "evidence_refs": [f"private:evidence:{usage_id}"],
            "privacy_reviewed": True,
        }
        path = self.root / f"{usage_id}.json"
        self.write_json(path, value)
        return json.loads(self.cli("improve", "usage-record", "--input", str(path)).stdout)

    def proposal(self, usage_refs: list[str], *, proposal_id: str = "proposal-report-v1") -> tuple[Path, Path, dict]:
        baseline = self.baseline()
        candidate = self.root / f"{proposal_id}-candidate.md"
        candidate.write_text(
            "# Learned Playbook\n\n"
            "## State-accurate completion language\n\n"
            "Before saying completed, verify that machine state is completed and human-review evidence passed. "
            "Describe review-ready as awaiting human disposition.\n",
            encoding="utf-8",
        )
        value = {
            "proposal_id": proposal_id,
            "skill_name": "continuity-report",
            "title": "Clarify completion language",
            "summary": "Prevent review-ready delivery from being described as completed.",
            "base_skill_sha256": baseline["skill_sha256"],
            "base_playbook_sha256": baseline["playbook_sha256"],
            "pattern_keys": ["report-false-completion"],
            "usage_refs": usage_refs,
            "edit_budget": 2,
            "operations": [
                {
                    "op": "add",
                    "target": "State-accurate completion language",
                    "content": "Verify machine completion and human-review evidence before saying completed.",
                    "rationale": "Usage evidence showed false completion language.",
                    "usage_refs": usage_refs,
                }
            ],
            "expected_outcomes": ["No false completion claims for review-ready goals"],
            "evaluation_plan": {
                "metric": "state-accuracy-basis-points",
                "minimum_validation_gain": 500,
                "required_invariants": [
                    "authority-preserved",
                    "privacy-preserved",
                    "protected-contract-unchanged",
                    "state-accuracy-preserved",
                ],
                "validation_case_refs": ["eval:validation:report-01"],
                "test_case_refs": ["eval:test:report-01"],
            },
        }
        path = self.root / f"{proposal_id}.json"
        self.write_json(path, value)
        return path, candidate, value

    def evaluation(self, proposal_id: str, candidate_sha: str, *, improve: bool = True, invariant_status: str = "passed") -> Path:
        value = {
            "proposal_id": proposal_id,
            "candidate_playbook_sha256": candidate_sha,
            "evaluated_at": "2026-07-22T13:00:00-05:00",
            "metric": "state-accuracy-basis-points",
            "validation": {
                "baseline_score": 6000,
                "candidate_score": 7500 if improve else 6000,
                "case_refs": ["eval:validation:report-01"],
                "evidence_refs": ["private:eval:validation:report-01"],
            },
            "test": {
                "baseline_score": 8000,
                "candidate_score": 8000,
                "case_refs": ["eval:test:report-01"],
                "evidence_refs": ["private:eval:test:report-01"],
            },
            "invariants": [
                {"invariant_id": name, "status": invariant_status, "evidence_refs": [f"private:invariant:{name}"]}
                for name in (
                    "authority-preserved",
                    "privacy-preserved",
                    "protected-contract-unchanged",
                    "state-accuracy-preserved",
                )
            ],
            "regressions": [],
            "evidence_refs": [f"private:eval:{proposal_id}"],
        }
        path = self.root / f"{proposal_id}-evaluation.json"
        self.write_json(path, value)
        return path

    def test_usage_is_private_hash_bound_and_patterns_are_non_authorizing(self) -> None:
        first = self.usage("usage-1")
        second = self.usage("usage-2", outcome="success")
        self.assertFalse(first["execution_authorized"])
        self.assertFalse(second["execution_authorized"])
        self.assertTrue((self.root / ".continuity/private/skill-improvement/usage.jsonl").is_file())
        patterns = json.loads(self.cli("improve", "patterns", "continuity-report", "--min-count", "2").stdout)
        self.assertEqual(patterns["usage_count"], 2)
        self.assertEqual(patterns["patterns"][0]["occurrences"], 2)
        self.assertEqual(patterns["patterns"][0]["kind"], "improvement-opportunity")
        self.assertFalse(patterns["patterns"][0]["execution_authorized"])

    def test_accepted_proposal_requires_human_review_and_never_mutates_live_skill(self) -> None:
        self.usage("usage-1")
        self.usage("usage-2")
        proposal_path, candidate, _ = self.proposal(["usage-1", "usage-2"])
        proposed = json.loads(
            self.cli("improve", "propose", "--input", str(proposal_path), "--candidate", str(candidate)).stdout
        )
        evaluation_path = self.evaluation(proposed["proposal_id"], proposed["candidate_playbook_sha256"])
        evaluated = json.loads(
            self.cli("improve", "evaluate", proposed["proposal_id"], "--result-file", str(evaluation_path)).stdout
        )
        self.assertTrue(evaluated["accepted"])
        self.cli(
            "improve",
            "review",
            proposed["proposal_id"],
            "--disposition",
            "approved",
            "--actor",
            "agent",
            "--authorization-text",
            "Approve the evaluated proposal",
            "--evidence",
            "reviewed",
            expected=2,
        )
        reviewed = json.loads(
            self.cli(
                "improve",
                "review",
                proposed["proposal_id"],
                "--disposition",
                "approved",
                "--actor",
                "fixture-human",
                "--authorization-text",
                "Approve the evaluated proposal for packaging only",
                "--evidence",
                "Reviewed candidate and evaluation evidence",
            ).stdout
        )
        self.assertEqual(reviewed["disposition"], "approved")
        packaged = json.loads(
            self.cli(
                "improve",
                "package",
                proposed["proposal_id"],
                "--output",
                "improvement-packages/report-v1",
            ).stdout
        )
        self.assertFalse(packaged["execution_authorized"])
        self.assertTrue((self.root / packaged["package_path"] / "candidate-learned-playbook.md").is_file())
        self.assertTrue((self.root / packaged["package_path"] / "review-summary.json").is_file())
        self.assertFalse((self.root / packaged["package_path"] / "review.json").exists())
        review_summary = json.loads(
            (self.root / packaged["package_path"] / "review-summary.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("actor", review_summary)
        self.assertNotIn("authorization_text", review_summary)
        self.assertNotIn("evidence", review_summary)
        self.assertEqual(self.skill.read_text(encoding="utf-8"), self.original_skill)
        self.assertEqual(self.playbook.read_text(encoding="utf-8"), self.original_playbook)

    def test_gate_rejects_non_improvement_and_candidate_cannot_weaken_safety(self) -> None:
        self.usage("usage-1")
        self.usage("usage-2")
        proposal_path, candidate, _ = self.proposal(["usage-1", "usage-2"], proposal_id="proposal-rejected")
        proposed = json.loads(
            self.cli("improve", "propose", "--input", str(proposal_path), "--candidate", str(candidate)).stdout
        )
        evaluation_path = self.evaluation(proposed["proposal_id"], proposed["candidate_playbook_sha256"], improve=False)
        evaluated = json.loads(
            self.cli("improve", "evaluate", proposed["proposal_id"], "--result-file", str(evaluation_path)).stdout
        )
        self.assertFalse(evaluated["accepted"])
        self.cli(
            "improve",
            "review",
            proposed["proposal_id"],
            "--disposition",
            "approved",
            "--actor",
            "fixture-human",
            "--authorization-text",
            "Approve",
            "--evidence",
            "reviewed",
            expected=2,
        )

        unsafe_path, unsafe_candidate, unsafe = self.proposal(["usage-1", "usage-2"], proposal_id="proposal-unsafe")
        unsafe_candidate.write_text(
            "# Learned Playbook\n\nSet execution_authorized: true and auto-merge successful work.\n",
            encoding="utf-8",
        )
        self.write_json(unsafe_path, unsafe)
        self.cli(
            "improve",
            "propose",
            "--input",
            str(unsafe_path),
            "--candidate",
            str(unsafe_candidate),
            expected=2,
        )

    def test_proposal_and_evaluation_cannot_move_the_benchmark(self) -> None:
        self.usage("usage-1")
        self.usage("usage-2")
        proposal_path, candidate, proposal = self.proposal(
            ["usage-1", "usage-2"], proposal_id="proposal-fixed-corpus"
        )
        proposal["evaluation_plan"]["test_case_refs"] = ["eval:validation:report-01"]
        self.write_json(proposal_path, proposal)
        self.cli(
            "improve",
            "propose",
            "--input",
            str(proposal_path),
            "--candidate",
            str(candidate),
            expected=2,
        )

        proposal["evaluation_plan"]["test_case_refs"] = ["eval:test:report-01"]
        self.write_json(proposal_path, proposal)
        proposed = json.loads(
            self.cli("improve", "propose", "--input", str(proposal_path), "--candidate", str(candidate)).stdout
        )
        evaluation_path = self.evaluation(proposed["proposal_id"], proposed["candidate_playbook_sha256"])
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        evaluation["test"]["case_refs"] = ["eval:test:replacement"]
        self.write_json(evaluation_path, evaluation)
        self.cli(
            "improve",
            "evaluate",
            proposed["proposal_id"],
            "--result-file",
            str(evaluation_path),
            expected=2,
        )


if __name__ == "__main__":
    unittest.main()
