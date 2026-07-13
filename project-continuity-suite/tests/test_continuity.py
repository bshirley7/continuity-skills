from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SUITE = Path(__file__).resolve().parents[1]
CLI = SUITE / "bin" / "continuity"
INSTALLER = SUITE / "installer" / "install.py"


class ContinuityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Continuity Tests")
        (self.root / "AGENTS.md").write_text("# Test project\n", encoding="utf-8")
        (self.root / ".continuity").mkdir()
        self.config = {
            "schema_version": 1,
            "assurance_standard_version": 1,
            "project_id": "test-project",
            "integration_branch": "main",
            "timezone": "America/Chicago",
            "default_start_time": "22:00",
            "max_runtime_minutes": 360,
            "memory_docs": "docs/project-memory",
            "private_dir": ".continuity/private",
            "memory_stale_after_days": 90,
            "require_remote": False,
            "require_pr": False,
            "require_pr_auth": False,
            "require_execution_artifacts": False,
            "require_isolated_worktree": False,
            "refresh_base_on_preflight": False,
            "validation_commands": ["python3 -m unittest"],
            "documentation_map": {},
        }
        self.write_json(self.root / ".continuity" / "config.json", self.config)
        self.write_json(
            self.root / ".continuity" / "project.json",
            {
                "schema_version": 1,
                "assurance_standard_version": 1,
                "project_id": "test-project",
                "continuity_enabled": True,
                "execution_enabled": True,
                "integration_branch": "main",
                "timezone": "America/Chicago",
                "schedules": {"review": "20:00", "dispatch": "22:00", "report": "07:00"},
                "max_concurrency": 1,
            },
        )
        self.memory_root = self.root / "docs" / "project-memory"
        self.memory_root.mkdir(parents=True)
        self.write_memory(
            "current.md",
            memory_id="memory-current",
            title="Current Architecture",
            status="current",
            summary="The current renderer uses a safe preload bridge.",
            body="The Electron renderer communicates through the preload bridge.",
        )
        self.write_memory(
            "historical.md",
            memory_id="memory-history",
            title="Historical Architecture",
            status="historical",
            summary="An old renderer design used a direct bridge.",
            body="This historical approach is superseded.",
        )
        self.git("add", ".")
        self.git("commit", "-m", "fixture")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def write_memory(self, name: str, *, memory_id: str, title: str, status: str, summary: str, body: str) -> None:
        text = f"""---
memory_id: {memory_id}
title: {title}
type: architecture
system: desktop
summary: {summary}
status: {status}
tags: ["renderer", "electron"]
aliases: ["ui architecture"]
created_at: 2026-07-01T10:00:00-05:00
updated_at: 2026-07-13T10:00:00-05:00
last_verified_at: 2026-07-13T10:00:00-05:00
verified_against: fixture-sha
sources: ["AGENTS.md"]
related: []
supersedes: []
confidence: high
unresolved_gaps: []
---

# {title}

{body}
"""
        (self.memory_root / name).write_text(text, encoding="utf-8")

    def cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(CLI), "--project-root", str(self.root), "--json", *args],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def create_capture(self) -> dict:
        payload = {
            "source_type": "conversation",
            "source_ref": "thread:test",
            "items": [
                {"kind": "context", "text": "The renderer uses a preload bridge."},
                {"kind": "decision", "text": "Keep context isolation enabled."},
                {"kind": "question", "text": "Should the API expose this state?"},
                {"kind": "explicit-instruction", "text": "Implement the approved bridge change."},
            ],
        }
        path = self.root / "capture.json"
        self.write_json(path, payload)
        return json.loads(self.cli("note", "capture", "--items-file", str(path)).stdout)

    def create_goal(self, title: str = "Improve bridge safety", source_note_ids: list[str] | None = None) -> dict:
        payload = {
            "title": title,
            "scope": "Document and implement the approved bridge safety update.",
            "exclusions": ["Do not replace Electron"],
            "acceptance_criteria": ["Validation passes", "Memory impact is documented"],
            "memory_ids": ["memory-current", "memory-promoted", "memory-replacement"],
            "source_note_ids": source_note_ids or ["note-1"],
            "documentation_updates": ["docs/project-memory"],
            "plan_reviewed": True,
            "plan_review_evidence": "Reviewed for scope and developer compliance",
        }
        path = self.root / f"goal-{title.replace(' ', '-')}.json"
        self.write_json(path, payload)
        return json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout)

    def approve(self, goal: dict) -> dict:
        return json.loads(
            self.cli(
                "goal",
                "approve",
                goal["goal_id"],
                "--version",
                str(goal["plan_version"]),
                "--approved-by",
                "fixture-user",
                "--authorization-text",
                f"Approve {goal['goal_id']} plan v{goal['plan_version']}",
            ).stdout
        )

    def test_capture_is_atomic_private_and_never_authorized(self) -> None:
        capture = self.create_capture()
        self.assertFalse(capture["execution_authorized"])
        self.assertEqual(len(capture["items"]), 4)
        self.assertTrue(all(item["execution_authorized"] is False for item in capture["items"]))
        self.assertIn(".continuity/private/captures", capture["path"])

    def test_capture_deduplicates_same_source_and_content(self) -> None:
        first = self.create_capture()
        second = self.create_capture()
        self.assertEqual(first["capture_id"], second["capture_id"])
        self.assertTrue(second["deduplicated"])

    def test_triage_routes_without_authorization(self) -> None:
        capture = self.create_capture()
        item = capture["items"][3]
        routed = json.loads(
            self.cli("note", "triage", capture["capture_id"], item["item_id"], "--kind", "explicit-instruction", "--action", "promote").stdout
        )
        self.assertEqual(routed["queue"], "planning")
        self.assertFalse(routed["execution_authorized"])
        self.cli("note", "triage", capture["capture_id"], item["item_id"], "--kind", "explicit-instruction", "--action", "promote")
        queue = self.root / ".continuity" / "private" / "queues" / "planning.jsonl"
        self.assertEqual(len(queue.read_text(encoding="utf-8").splitlines()), 1)

    def test_memory_index_search_brief_and_default_privacy(self) -> None:
        indexed = json.loads(self.cli("memory", "index").stdout)
        self.assertEqual(indexed["entries"], 2)
        rows = json.loads(self.cli("memory", "search", "renderer bridge").stdout)
        self.assertEqual(rows[0]["memory_id"], "memory-current")
        self.assertIn("current.md#current-architecture", rows[0]["citation"])
        brief = self.cli("memory", "brief", "renderer bridge").stdout
        self.assertIn("memory-current", brief)
        self.assertIn("Source:", brief)
        current = self.memory_root / "current.md"
        current.write_text(current.read_text(encoding="utf-8").replace("safe preload bridge", "hardened preload bridge"), encoding="utf-8")
        refreshed = json.loads(self.cli("memory", "search", "hardened preload").stdout)
        self.assertEqual(refreshed[0]["memory_id"], "memory-current")

    def test_memory_search_escapes_fts_operators(self) -> None:
        self.cli("memory", "index")
        rows = json.loads(self.cli("memory", "search", 'renderer OR "drop table"').stdout)
        self.assertIsInstance(rows, list)

    def test_memory_audit_flags_malformed_and_duplicate_entries(self) -> None:
        (self.memory_root / "bad.md").write_text("# Missing frontmatter\n", encoding="utf-8")
        self.write_memory(
            "duplicate.md",
            memory_id="memory-current",
            title="Duplicate",
            status="current",
            summary="Duplicate id.",
            body="Duplicate.",
        )
        report = json.loads(self.cli("memory", "audit").stdout)
        self.assertFalse(report["healthy"])
        self.assertTrue(report["missing_frontmatter"])
        self.assertIn("memory-current", report["duplicates"])

    def test_approved_memory_promotion_verification_and_supersession(self) -> None:
        payload = {
            "source_type": "conversation",
            "source_ref": "thread:memory",
            "items": [{"kind": "documentation-candidate", "text": "The renderer must keep context isolation enabled."}],
        }
        capture_path = self.root / "memory-capture.json"
        self.write_json(capture_path, payload)
        capture = json.loads(self.cli("note", "capture", "--items-file", str(capture_path)).stdout)
        note_id = capture["items"][0]["item_id"]
        goal = self.create_goal("Curate renderer memory", [note_id])
        self.approve(goal)
        promoted = json.loads(
            self.cli(
                "memory",
                "promote",
                note_id,
                "--goal-id",
                goal["goal_id"],
                "--memory-id",
                "memory-promoted",
                "--title",
                "Renderer Isolation",
                "--type",
                "decision",
                "--system",
                "desktop",
                "--summary",
                "The renderer preserves context isolation.",
            ).stdout
        )
        self.assertEqual(promoted["status"], "proposed")
        verified = json.loads(
            self.cli(
                "memory",
                "verify",
                "memory-promoted",
                "--goal-id",
                goal["goal_id"],
                "--commit",
                "verified-sha",
                "--mark-current",
            ).stdout
        )
        self.assertEqual(verified["verified_against"], "verified-sha")
        self.write_memory(
            "replacement.md",
            memory_id="memory-replacement",
            title="Renderer Isolation Replacement",
            status="current",
            summary="The replacement renderer isolation contract.",
            body="Replacement content.",
        )
        result = json.loads(
            self.cli(
                "memory",
                "supersede",
                "memory-promoted",
                "--with",
                "memory-replacement",
                "--goal-id",
                goal["goal_id"],
            ).stdout
        )
        self.assertEqual(result["replacement"], "memory-replacement")
        old_text = (self.memory_root / "proposed" / "memory-promoted.md").read_text(encoding="utf-8")
        self.assertIn("status: superseded", old_text)

    def test_approval_queues_for_ten_pm_and_plan_edit_invalidates(self) -> None:
        goal = self.create_goal()
        approved = self.approve(goal)
        self.assertEqual(approved["goal"]["state"], "queued")
        self.assertIn("T22:00", approved["goal"]["scheduled_for"])
        goal_dir = self.root / ".continuity" / "private" / "goals" / goal["goal_id"]
        with (goal_dir / "plan.md").open("a", encoding="utf-8") as handle:
            handle.write("\nChanged after approval.\n")
        self.cli("goal", "start", goal["goal_id"], expected=2)
        self.assertFalse((self.root / ".continuity" / "private" / "project.lock.json").exists())

    def test_approval_requires_explicit_provenance_and_valid_schedule(self) -> None:
        goal = self.create_goal()
        self.cli("goal", "approve", goal["goal_id"], "--version", "1", expected=2)
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", "Approve something else plan v1", expected=2,
        )
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", "--schedule", "not-a-date", expected=2,
        )
        approval = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "approval.json"
        self.assertFalse(approval.exists())

    def test_assurance_standard_is_required_for_approval(self) -> None:
        goal = self.create_goal()
        ledger = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "compliance.json"
        compliance = json.loads(ledger.read_text(encoding="utf-8"))
        compliance.pop("assurance_standard_version")
        self.write_json(ledger, compliance)
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", expected=2,
        )

    def test_preflight_and_project_lock_enforce_one_goal(self) -> None:
        first = self.create_goal("First goal")
        self.approve(first)
        dispatch = json.loads(self.cli("goal", "start", first["goal_id"]).stdout)
        self.assertEqual(dispatch["goal_id"], first["goal_id"])
        second = self.create_goal("Second goal")
        self.approve(second)
        self.cli("goal", "start", second["goal_id"], expected=2)
        lock = json.loads((self.root / ".continuity" / "private" / "project.lock.json").read_text())
        self.assertEqual(lock["goal_id"], first["goal_id"])

    def test_completion_requires_all_responsible_stages(self) -> None:
        goal = self.create_goal()
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/test")
        self.cli("run", "update", goal["goal_id"], "--state", "completed", expected=2)
        stages = [
            "implementation",
            "code-review",
            "validation",
            "security-review",
            "merge-safety",
            "documentation",
            "memory-impact",
            "final-alignment",
        ]
        for stage in stages:
            self.cli("goal", "gate", goal["goal_id"], stage, "--status", "passed", "--evidence", f"fixture:{stage}")
        self.cli("run", "update", goal["goal_id"], "--state", "validating")
        completed = json.loads(self.cli("run", "update", goal["goal_id"], "--state", "completed", "--summary", "All gates passed").stdout)
        self.assertEqual(completed["state"], "completed")
        self.cli("goal", "start", goal["goal_id"], expected=2)

    def test_queued_goal_cannot_skip_execution_or_restart_terminal(self) -> None:
        goal = self.create_goal()
        self.approve(goal)
        self.cli("run", "update", goal["goal_id"], "--state", "completed", "--summary", "claimed", expected=2)
        self.cli("run", "update", goal["goal_id"], "--state", "running", expected=2)

    def test_goal_revision_preserves_history_and_invalidates_approval(self) -> None:
        goal = self.create_goal()
        self.approve(goal)
        revision = self.root / "revision.json"
        self.write_json(revision, {"scope": "Revised, bounded scope.", "plan_markdown": "# Revised plan\n\nExplicitly bounded.\n"})
        revised = json.loads(self.cli("goal", "revise", goal["goal_id"], "--goal-file", str(revision), "--author", "fixture-user", "--summary", "Narrowed scope").stdout)
        self.assertEqual(revised["plan_version"], 2)
        self.assertEqual(revised["state"], "awaiting-feedback")
        goal_dir = self.root / ".continuity" / "private" / "goals" / goal["goal_id"]
        self.assertTrue((goal_dir / "revisions" / "v1" / "plan.md").exists())
        self.assertFalse((goal_dir / "approval.json").exists())

    def test_goal_create_rejects_invalid_machine_fields(self) -> None:
        path = self.root / "invalid-goal.json"
        self.write_json(path, {"title": "Bad", "scope": "Bad", "acceptance_criteria": "not-an-array", "plan_version": 0, "runtime_limit_minutes": -1})
        self.cli("goal", "create", "--goal-file", str(path), expected=2)
        self.write_json(path, {"goal_id": "../../escape", "title": "Bad", "scope": "Bad", "acceptance_criteria": ["No escape"]})
        self.cli("goal", "create", "--goal-file", str(path), expected=2)

    def test_configuration_paths_cannot_escape_project(self) -> None:
        self.config["private_dir"] = "../escaped"
        self.write_json(self.root / ".continuity" / "config.json", self.config)
        self.cli("goal", "list", expected=2)

    def test_report_exists_with_no_goals_and_memory_status(self) -> None:
        self.cli("memory", "audit")
        report = self.cli("report", "project").stdout
        self.assertIn("No tracked goals", report)
        self.assertIn("Project memory", report)


class InstallerTest(unittest.TestCase):
    def test_installer_is_idempotent_and_creates_memory_and_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "AGENTS.md").write_text("# Example project\n", encoding="utf-8")
            (root / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            command = [
                "python3",
                str(INSTALLER),
                "--project-root",
                str(root),
                "--project-id",
                "sample-project",
                "--integration-branch",
                "main",
                "--validation",
                "pnpm typecheck",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            subprocess.run(command, check=True, capture_output=True, text=True)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("project-continuity:start"), 1)
            self.assertTrue((root / ".agents" / "skills" / "project-continuity" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "project-continuity-local" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "manage-project-memory" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "project-continuity" / "bin" / "continuity").exists())
            self.assertTrue((root / ".agents" / "project-continuity" / "automation" / "nightly-review.md").exists())
            self.assertTrue((root / ".agents" / "references" / "development-assurance-standard.md").exists())
            self.assertTrue((root / "docs" / "project-memory" / "INDEX.md").exists())
            manifest = json.loads((root / ".continuity" / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_id"], "sample-project")
            self.assertFalse(manifest["execution_enabled"])
            self.assertEqual(manifest["assurance_standard_version"], 1)
            behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(behavior["fixed_guardrails"]["security_review"], "required")
            self.assertEqual(behavior["fixed_guardrails"]["force_push"], "forbidden")
            self.assertEqual(manifest["behavior_configuration_hash"], behavior["configuration_hash"])
            self.assertIn(".continuity/private/", (root / ".gitignore").read_text(encoding="utf-8"))
            config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(config["require_pr"])
            self.assertTrue(config["require_execution_artifacts"])
            self.assertTrue(config["require_isolated_worktree"])
            self.assertEqual(config["assurance_standard_version"], 1)
            self.assertEqual(config["behavior_configuration_hash"], behavior["configuration_hash"])
            self.assertEqual(config["behavior_skill_path"], ".agents/skills/project-continuity-local/SKILL.md")
            recommendations = subprocess.run(
                [str(root / ".agents" / "project-continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "recommendations"],
                check=True,
                capture_output=True,
                text=True,
            )
            recommended = json.loads(recommendations.stdout)
            self.assertFalse(recommended["recommended"]["execution_enabled"])
            self.assertEqual(recommended["fixed_guardrails"]["max_code_changing_goals_per_project"], 1)

            answers_path = Path(temp) / "behavior-answers.json"
            answers_path.write_text(
                json.dumps(
                    {
                        "schedules": {"dispatch": "21:30"},
                        "visual_evidence_mode": "always",
                        "validation_commands": ["pnpm typecheck", "pnpm test"],
                        "project_instructions": ["Run backend contract checks before the frontend build."],
                    }
                ),
                encoding="utf-8",
            )
            configured = subprocess.run(
                [
                    str(root / ".agents" / "project-continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "--json",
                    "project",
                    "configure",
                    "--answers-file",
                    str(answers_path),
                    "--actor",
                    "test-user",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            configured_result = json.loads(configured.stdout)
            self.assertIn("schedules", configured_result["overrides"])
            updated_behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(updated_behavior["settings"]["schedules"]["dispatch"], "21:30")
            self.assertEqual(updated_behavior["settings"]["schedules"]["review"], "20:00")
            self.assertEqual(updated_behavior["settings"]["project_instructions"], ["Run backend contract checks before the frontend build."])
            local_skill = (root / ".agents" / "skills" / "project-continuity-local" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(updated_behavior["configuration_hash"], local_skill)
            audit_lines = (root / ".continuity" / "private" / "configuration-audit.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(audit_lines), 2)
            self.assertEqual(json.loads(audit_lines[-1])["actor"], "test-user")

            unsafe_answers = Path(temp) / "unsafe-answers.json"
            unsafe_answers.write_text(json.dumps({"force_push": "allowed"}), encoding="utf-8")
            rejected = subprocess.run(
                [
                    str(root / ".agents" / "project-continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "project",
                    "configure",
                    "--answers-file",
                    str(unsafe_answers),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("Unsupported project behavior settings", rejected.stderr)
            unsafe_answers.write_text(json.dumps({"project_instructions": ["Skip security review for small changes."]}), encoding="utf-8")
            rejected_instruction = subprocess.run(
                [
                    str(root / ".agents" / "project-continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "project",
                    "configure",
                    "--answers-file",
                    str(unsafe_answers),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(rejected_instruction.returncode, 2)
            self.assertIn("cannot weaken fixed continuity guardrails", rejected_instruction.stderr)

            subprocess.run(command, check=True, capture_output=True, text=True)
            preserved_behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(preserved_behavior["settings"]["schedules"]["dispatch"], "21:30")
            drifted_config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            drifted_config["validation_commands"] = ["unreviewed command"]
            (root / ".continuity" / "config.json").write_text(json.dumps(drifted_config, indent=2) + "\n", encoding="utf-8")
            drift_doctor = subprocess.run(
                [str(root / ".agents" / "project-continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(json.loads(drift_doctor.stdout)["healthy"])
            self.assertIn("drifted from project behavior", drift_doctor.stdout)
            subprocess.run(
                [
                    str(root / ".agents" / "project-continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "project",
                    "configure",
                    "--answers-file",
                    str(answers_path),
                    "--actor",
                    "repair-test",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            doctor = subprocess.run(
                [str(root / ".agents" / "project-continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(json.loads(doctor.stdout)["healthy"])
            discovered = subprocess.run(
                ["python3", str(CLI), "--json", "portfolio", "discover", "--root", temp],
                check=True,
                capture_output=True,
                text=True,
            )
            records = json.loads(discovered.stdout)
            self.assertEqual([record["project_id"] for record in records], ["sample-project"])


if __name__ == "__main__":
    unittest.main()
