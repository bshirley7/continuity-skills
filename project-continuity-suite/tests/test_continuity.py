from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path


SUITE = Path(__file__).resolve().parents[1]
CLI = SUITE / "bin" / "continuity"
INSTALLER = SUITE / "installer" / "install.py"
sys.path.insert(0, str(SUITE / "lib"))
import roadmap as roadmap_lib  # noqa: E402
import shared_notes as shared_notes_lib  # noqa: E402


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
            "assurance_standard_version": 2,
            "project_id": "test-project",
            "integration_branch": "main",
            "timezone": "America/Chicago",
            "default_start_time": "22:00",
            "max_runtime_minutes": 360,
            "memory_docs": "docs/project-memory",
            "roadmap_docs": "docs/project-roadmap",
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
                "assurance_standard_version": 2,
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

    def write_roadmap(self, roadmap_id: str, title: str, kind: str, status: str, *, parents: list[str] | None = None, dependencies: list[str] | None = None, health: str = "on-track") -> None:
        path = self.root / "docs" / "project-roadmap" / "entities" / f"{roadmap_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        value = {
            "roadmap_id": roadmap_id,
            "title": title,
            "kind": kind,
            "status": status,
            "summary": f"Roadmap context for {title}.",
            "parent_ids": parents or [],
            "depends_on": dependencies or [],
            "health": health,
            "created_at": "2026-07-13T10:00:00-05:00",
            "updated_at": "2026-07-13T10:00:00-05:00",
        }
        path.write_text(roadmap_lib.render_entry(roadmap_lib.normalize_entry(value)), encoding="utf-8")

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
            "roadmap-impact",
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

    def test_planning_patterns_are_validated_hashed_and_non_authorizing(self) -> None:
        payload = {
            "goal_id": "goal-patterns",
            "title": "Plan a verified renderer change",
            "scope": "Deliver the approved renderer behavior in safe increments.",
            "acceptance_criteria": ["Each slice is independently verified"],
            "memory_ids": ["memory-current"],
            "source_note_ids": ["note-patterns"],
            "plan_reviewed": True,
            "triage_brief": {
                "summary": "Verify the renderer request before planning.",
                "classification": "execution-candidate",
                "claim_status": "confirmed",
                "current_behavior": "The renderer uses the existing bridge.",
                "desired_behavior": "The renderer uses the approved safer behavior.",
                "acceptance_criteria": ["The existing bridge remains compatible"],
                "scope_exclusions": ["Do not replace Electron"],
                "evidence": ["memory-current", "fixture inspection"],
                "codebase_checks": {
                    "redundancy": {"status": "clear", "evidence": ["No existing implementation found"]},
                    "prior_decisions": {"status": "clear", "evidence": ["No conflicting current memory"]},
                },
            },
            "decision_map": {
                "destination": "A decision-complete renderer safety plan.",
                "decisions": [
                    {
                        "decision_id": "decision-bridge",
                        "title": "Preserve bridge compatibility",
                        "question": "Must the existing bridge contract remain compatible?",
                        "status": "resolved",
                        "resolution": "Yes, preserve compatibility.",
                        "blocked_by": [],
                    }
                ],
                "unresolved_territory": [],
                "out_of_scope": ["Replacing Electron"],
            },
            "delivery_slices": [
                {
                    "ticket_id": "slice-contract",
                    "title": "Preserve the bridge contract",
                    "delivers": "The safer behavior behind the existing contract.",
                    "acceptance_criteria": ["Contract tests pass"],
                    "blocked_by": [],
                },
                {
                    "ticket_id": "slice-evidence",
                    "title": "Capture renderer evidence",
                    "delivers": "Reviewable validation evidence for the behavior.",
                    "acceptance_criteria": ["Evidence identifies the verified behavior"],
                    "blocked_by": ["slice-contract"],
                },
            ],
        }
        path = self.root / "goal-patterns.json"
        self.write_json(path, payload)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout)
        self.assertFalse(goal["triage_brief"]["execution_authorized"])
        self.assertTrue(all(item["status"] == "planning-candidate" for item in goal["delivery_slices"]))
        plan = (self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "plan.md").read_text(encoding="utf-8")
        self.assertIn("Decision map", plan)
        self.assertIn("Delivery slices", plan)
        approved = self.approve(goal)
        self.assertEqual(approved["approval"]["plan_hash"], approved["goal"]["plan_hash"])

    def test_unresolved_decisions_and_invalid_delivery_graph_block_approval(self) -> None:
        unresolved = {
            "goal_id": "goal-unresolved",
            "title": "Unresolved plan",
            "scope": "Wait for a required product decision.",
            "acceptance_criteria": ["Decision is recorded"],
            "memory_ids": ["memory-current"],
            "source_note_ids": ["note-unresolved"],
            "plan_reviewed": True,
            "decision_map": {
                "destination": "A decided product behavior.",
                "decisions": [{"decision_id": "decision-human", "title": "Choose behavior", "question": "Which behavior should ship?", "status": "human-required", "blocked_by": []}],
                "unresolved_territory": [],
                "out_of_scope": [],
            },
        }
        path = self.root / "goal-unresolved.json"
        self.write_json(path, unresolved)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout)
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", expected=2,
        )
        cycle = dict(unresolved)
        cycle.update({"goal_id": "goal-cycle", "decision_map": None, "delivery_slices": [
            {"ticket_id": "slice-a", "title": "A", "delivers": "A", "acceptance_criteria": ["A"], "blocked_by": ["slice-b"]},
            {"ticket_id": "slice-b", "title": "B", "delivers": "B", "acceptance_criteria": ["B"], "blocked_by": ["slice-a"]},
        ]})
        cycle_path = self.root / "goal-cycle.json"
        self.write_json(cycle_path, cycle)
        self.cli("goal", "create", "--goal-file", str(cycle_path), expected=2)

    def test_machine_planning_artifacts_cannot_drift_from_review_plan(self) -> None:
        payload = {
            "goal_id": "goal-artifact-drift",
            "title": "Artifact parity",
            "scope": "Keep the human plan aligned with machine planning artifacts.",
            "acceptance_criteria": ["Parity is enforced"],
            "memory_ids": ["memory-current"],
            "source_note_ids": ["note-parity"],
            "plan_reviewed": True,
            "delivery_slices": [{"ticket_id": "slice-parity", "title": "Enforce parity", "delivers": "Matching human and machine plans.", "acceptance_criteria": ["Drift is rejected"], "blocked_by": []}],
        }
        path = self.root / "goal-artifact-drift.json"
        self.write_json(path, payload)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout)
        plan_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "plan.md"
        plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("Matching human and machine plans.", "Unreviewed drift."), encoding="utf-8")
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", expected=2,
        )

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

    def test_roadmap_index_brief_hierarchy_and_audit(self) -> None:
        self.write_roadmap("program-core", "Core program", "program", "active")
        self.write_roadmap("initiative-safe", "Safe renderer", "initiative", "active", parents=["program-core"])
        self.write_roadmap("milestone-ready", "Renderer ready", "milestone", "planned", parents=["initiative-safe"], dependencies=["program-core"])
        indexed = json.loads(self.cli("roadmap", "index").stdout)
        self.assertEqual(indexed["entries"], 3)
        audit = json.loads(self.cli("roadmap", "audit").stdout)
        self.assertTrue(audit["healthy"], audit)
        brief = self.cli("roadmap", "brief", "renderer").stdout
        self.assertIn("initiative-safe", brief)
        self.assertIn("docs/project-roadmap/entities/initiative-safe.md", brief)
        shown = json.loads(self.cli("roadmap", "show", "milestone-ready").stdout)
        self.assertEqual(shown["parent_ids"], ["initiative-safe"])

    def test_roadmap_audit_detects_cycle_orphan_and_stale_link(self) -> None:
        self.write_roadmap("initiative-a", "A", "initiative", "active", parents=["initiative-b"])
        self.write_roadmap("initiative-b", "B", "initiative", "active", parents=["initiative-a"])
        self.write_roadmap("story-orphan", "Orphan", "story", "ready")
        link = self.root / ".continuity" / "private" / "roadmap" / "note-links.jsonl"
        link.parent.mkdir(parents=True, exist_ok=True)
        link.write_text(json.dumps({"note_id": "missing", "roadmap_id": "initiative-a", "relation": "supports"}) + "\n", encoding="utf-8")
        audit = json.loads(self.cli("roadmap", "audit").stdout)
        self.assertFalse(audit["healthy"])
        self.assertTrue(audit["cycles"])
        self.assertIn("story-orphan", audit["orphans"])
        self.assertTrue(audit["stale_note_links"])

    def test_roadmap_validates_dates_estimates_sprints_and_filters(self) -> None:
        self.write_roadmap("program-core", "Core", "program", "active")
        self.write_roadmap("sprint-1", "Sprint one", "sprint", "active")
        story_path = self.root / "docs" / "project-roadmap" / "entities" / "story-one.md"
        story_path.write_text(roadmap_lib.render_entry(roadmap_lib.normalize_entry({
            "roadmap_id": "story-one", "title": "Story one", "kind": "story", "status": "ready", "summary": "A deliverable story.",
            "parent_ids": ["program-core"], "sprint_ids": ["sprint-1"], "estimate_points": 5, "owners": ["dev-a"], "tags": ["renderer"],
            "health": "on-track", "start_date": "2026-07-13", "target_date": "2026-07-20", "created_at": "2026-07-13T10:00:00-05:00", "updated_at": "2026-07-13T10:00:00-05:00",
        })), encoding="utf-8")
        filtered = json.loads(self.cli("roadmap", "list", "--kind", "story", "--owner", "dev-a", "--tag", "renderer", "--sprint", "sprint-1").stdout)
        self.assertEqual([item["roadmap_id"] for item in filtered], ["story-one"])
        bad = self.root / "bad-roadmap.json"
        self.write_json(bad, {"roadmap_id": "bad", "title": "Bad", "kind": "story", "status": "ready", "summary": "Bad dates.", "estimate_points": 7, "start_date": "2026-07-30", "target_date": "2026-07-01", "created_at": "now", "updated_at": "now"})
        with self.assertRaises(roadmap_lib.RoadmapError):
            roadmap_lib.normalize_entry(json.loads(bad.read_text(encoding="utf-8")))

    def test_private_note_links_to_roadmap_without_authorization(self) -> None:
        self.write_roadmap("program-core", "Core program", "program", "active")
        capture = self.create_capture()
        note_id = capture["items"][0]["item_id"]
        linked = json.loads(self.cli("roadmap", "link-note", note_id, "--to", "program-core", "--relation", "supports").stdout)
        self.assertFalse(linked["execution_authorized"])
        self.assertFalse((self.root / "docs" / "project-roadmap" / "entities" / "program-core.md").read_text(encoding="utf-8").find(note_id) >= 0)

    def test_goal_roadmap_contract_is_hash_bound_and_gates_updates(self) -> None:
        payload = {
            "goal_id": "goal-roadmap",
            "title": "Create roadmap milestone",
            "scope": "Create the approved milestone documentation.",
            "acceptance_criteria": ["Milestone is committed"],
            "memory_ids": ["memory-current"],
            "roadmap_ids": ["milestone-new"],
            "roadmap_impact": {"entries": [{"roadmap_id": "milestone-new", "action": "create", "rationale": "Track the approved delivery commitment."}], "documentation_required": True, "summary": "Create one milestone."},
            "plan_reviewed": True,
        }
        goal_file = self.root / "roadmap-goal.json"
        self.write_json(goal_file, payload)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(goal_file)).stdout)
        approved = self.approve(goal)
        self.assertEqual(approved["approval"]["plan_hash"], approved["goal"]["plan_hash"])
        entry_file = self.root / "milestone.json"
        self.write_json(entry_file, {"roadmap_id": "milestone-new", "title": "New milestone", "kind": "milestone", "status": "planned", "summary": "Approved delivery milestone.", "parent_ids": [], "health": "on-track", "created_at": "2026-07-13T10:00:00-05:00", "updated_at": "2026-07-13T10:00:00-05:00"})
        created = json.loads(self.cli("roadmap", "create", "--entry-file", str(entry_file), "--goal-id", goal["goal_id"]).stdout)
        self.assertEqual(created["roadmap_id"], "milestone-new")
        goal_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json"
        mutated = json.loads(goal_path.read_text(encoding="utf-8")); mutated["roadmap_impact"]["summary"] = "Unapproved change"; self.write_json(goal_path, mutated)
        self.cli("goal", "start", goal["goal_id"], expected=2)

    def test_roadmap_change_invalidates_pre_dispatch_approval(self) -> None:
        self.write_roadmap("program-core", "Core program", "program", "active")
        payload = {"goal_id": "goal-roadmap-stale", "title": "Use roadmap context", "scope": "Plan against current roadmap context.", "acceptance_criteria": ["Context remains current"], "memory_ids": ["memory-current"], "roadmap_ids": ["program-core"], "roadmap_impact": {"entries": [{"roadmap_id": "program-core", "action": "none", "rationale": "Context only."}], "documentation_required": False, "summary": "No roadmap change."}, "plan_reviewed": True}
        path = self.root / "stale-roadmap-goal.json"; self.write_json(path, payload)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout); self.approve(goal)
        roadmap_path = self.root / "docs" / "project-roadmap" / "entities" / "program-core.md"
        roadmap_path.write_text(roadmap_path.read_text(encoding="utf-8") + "\nChanged after approval.\n", encoding="utf-8")
        self.cli("goal", "start", goal["goal_id"], expected=2)

    def test_shared_note_packet_requires_exact_approval_and_stays_non_authorizing(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][1]["item_id"]
        self.cli("note", "share", "prepare", note_id, "--target-project", "test-project", "--sender", "bad\nsender", expected=2)
        prepared = json.loads(self.cli("note", "share", "prepare", note_id, "--target-project", "test-project", "--sender", "fixture").stdout)
        self.assertFalse(prepared["execution_authorized"])
        self.assertIn("source_ref_hash", prepared["provenance"][0])
        self.assertNotIn("source_ref", prepared["provenance"][0])
        self.cli("note", "share", "approve", prepared["packet_id"], "--version", str(prepared["version"]), "--approved-by", "fixture", "--authorization-text", "wrong", expected=2)
        self.cli("note", "share", "approve", prepared["packet_id"], "--version", str(prepared["version"]), "--approved-by", "fixture", "--authorization-text", f"Approve {prepared['packet_id']} version {prepared['version']} for test-project")
        published = json.loads(self.cli("note", "share", "publish", prepared["packet_id"], "--dry-run").stdout)
        self.assertTrue(published["dry_run"])
        self.assertFalse(published["execution_authorized"])
        self.assertTrue(published["branch"].startswith("continuity-notes/"))
        revised = json.loads(self.cli("note", "share", "prepare", note_id, "--packet-id", prepared["packet_id"], "--target-project", "test-project", "--sender", "fixture").stdout)
        self.assertEqual(revised["version"], prepared["version"] + 1)
        self.cli("note", "share", "publish", prepared["packet_id"], "--dry-run", expected=2)
        self.assertTrue((self.root / ".continuity" / "private" / "shared-notes" / "outbox" / prepared["packet_id"] / "versions" / f"v{prepared['version']}.json").exists())

    def test_shared_note_secret_detection_and_import_deduplication(self) -> None:
        payload = {"source_type": "manual", "source_ref": "secret-test", "items": [{"kind": "context", "text": "api_key=super-secret-value"}]}
        path = self.root / "secret-capture.json"; self.write_json(path, payload)
        capture = json.loads(self.cli("note", "capture", "--items-file", str(path)).stdout)
        self.cli("note", "share", "prepare", capture["items"][0]["item_id"], "--target-project", "test-project", "--sender", "fixture", expected=2)
        clean = self.create_capture()
        prepared = json.loads(self.cli("note", "share", "prepare", clean["items"][0]["item_id"], "--target-project", "test-project", "--sender", "fixture").stdout)
        packet = json.loads((self.root / prepared["private_path"]).read_text(encoding="utf-8"))
        packet_dir = self.root / ".continuity" / "shared-notes" / "packets" / "2026"; packet_dir.mkdir(parents=True)
        packet_dir.joinpath("packet-fixture-v1.md").write_text(shared_notes_lib.render_packet(packet), encoding="utf-8")
        first = json.loads(self.cli("note", "share", "import").stdout)
        second = json.loads(self.cli("note", "share", "import").stdout)
        self.assertEqual(len(first["imported"]), 1)
        self.assertEqual(len(second["imported"]), 0)

    def test_sidecar_is_loopback_authorized_read_only_and_strict(self) -> None:
        self.write_roadmap("program-core", "Core program", "program", "active")
        try:
            server = roadmap_lib.create_server(self.root, self.config, token="fixture-token", asset_root=SUITE / "roadmap-ui")
        except PermissionError:
            self.skipTest("The current sandbox does not permit loopback socket binding")
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            request = urllib.request.Request(base + "/api/v1/roadmap", headers={"Authorization": "Bearer fixture-token"})
            with urllib.request.urlopen(request, timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
                self.assertTrue(json.loads(response.read())["entities"])
            source_request = urllib.request.Request(base + "/api/v1/source/program-core", headers={"Authorization": "Bearer fixture-token"})
            with urllib.request.urlopen(source_request, timeout=3) as response:
                source = json.loads(response.read())
                self.assertEqual(source["roadmap_id"], "program-core")
                self.assertIn("roadmap_id: program-core", source["content"])
            with self.assertRaises(urllib.error.HTTPError) as unauthorized:
                urllib.request.urlopen(base + "/api/v1/roadmap", timeout=3)
            self.assertEqual(unauthorized.exception.code, 401)
            unauthorized.exception.close()
            post = urllib.request.Request(base + "/api/v1/roadmap", data=b"{}", method="POST")
            with self.assertRaises(urllib.error.HTTPError) as readonly:
                urllib.request.urlopen(post, timeout=3)
            self.assertEqual(readonly.exception.code, 405)
            readonly.exception.close()
            cross_origin = urllib.request.Request(base + "/api/v1/roadmap", headers={"Authorization": "Bearer fixture-token", "Origin": "https://example.invalid"})
            with self.assertRaises(urllib.error.HTTPError) as rejected:
                urllib.request.urlopen(cross_origin, timeout=3)
            self.assertEqual(rejected.exception.code, 403)
            rejected.exception.close()
            traversal = urllib.request.Request(base + "/..%2f..%2fetc/passwd")
            with self.assertRaises(urllib.error.HTTPError) as confined:
                urllib.request.urlopen(traversal, timeout=3)
            self.assertEqual(confined.exception.code, 400)
            confined.exception.close()
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=3)

    def test_sidecar_uses_safe_dom_and_production_audit_detects_leakage(self) -> None:
        javascript = (SUITE / "roadmap-ui" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("innerHTML", javascript)
        self.assertNotIn("localStorage", javascript)
        self.assertNotIn("sessionStorage", javascript)
        artifact = self.root / "dist"; artifact.mkdir(); artifact.joinpath("app.js").write_text("console.log('product')", encoding="utf-8")
        clean = json.loads(self.cli("roadmap", "production-audit", "--artifact", str(artifact)).stdout)
        self.assertTrue(clean["clean"])
        artifact.joinpath("leak.js").write_text("const route='/api/v1/roadmap'", encoding="utf-8")
        leaked = json.loads(self.cli("roadmap", "production-audit", "--artifact", str(artifact)).stdout)
        self.assertFalse(leaked["clean"])

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
            self.assertTrue((root / ".agents" / "skills" / "manage-project-roadmap" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "share-project-notes" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "project-continuity" / "bin" / "continuity").exists())
            self.assertTrue((root / ".agents" / "project-continuity" / "automation" / "nightly-review.md").exists())
            self.assertTrue((root / ".agents" / "references" / "development-assurance-standard.md").exists())
            self.assertTrue((root / "docs" / "project-memory" / "INDEX.md").exists())
            self.assertTrue((root / "docs" / "project-roadmap" / "INDEX.md").exists())
            self.assertTrue((root / ".agents" / "project-continuity" / "roadmap-ui" / "app.js").exists())
            manifest = json.loads((root / ".continuity" / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_id"], "sample-project")
            self.assertFalse(manifest["execution_enabled"])
            self.assertEqual(manifest["assurance_standard_version"], 2)
            behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(behavior["fixed_guardrails"]["security_review"], "required")
            self.assertEqual(behavior["fixed_guardrails"]["force_push"], "forbidden")
            self.assertFalse(behavior["fixed_guardrails"]["planning_artifacts_authorize_execution"])
            self.assertEqual(behavior["fixed_guardrails"]["external_tracker_publish"], "explicit-human-approval-required")
            self.assertFalse(behavior["fixed_guardrails"]["shared_notes_authorize_execution"])
            self.assertEqual(behavior["fixed_guardrails"]["hosted_roadmap_surface"], "forbidden")
            self.assertEqual(behavior["settings"]["planning_patterns"]["tracker_provider"], "local")
            self.assertEqual(behavior["settings"]["roadmap"]["ui_mode"], "local-read-only")
            self.assertEqual(manifest["behavior_configuration_hash"], behavior["configuration_hash"])
            self.assertIn(".continuity/private/", (root / ".gitignore").read_text(encoding="utf-8"))
            config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(config["require_pr"])
            self.assertTrue(config["require_execution_artifacts"])
            self.assertTrue(config["require_isolated_worktree"])
            self.assertEqual(config["assurance_standard_version"], 2)
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
                        "planning_patterns": {
                            "evidence_triage": "required",
                            "decision_mapping": "auto",
                            "delivery_slicing": "auto",
                            "tracker_provider": "local",
                        },
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
            self.assertEqual(updated_behavior["settings"]["planning_patterns"]["evidence_triage"], "required")
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
            unsafe_answers.write_text(json.dumps({"planning_patterns": {"evidence_triage": "bypass", "decision_mapping": "auto", "delivery_slicing": "auto", "tracker_provider": "local"}}), encoding="utf-8")
            rejected_pattern = subprocess.run(
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
            self.assertEqual(rejected_pattern.returncode, 2)
            self.assertIn("planning_patterns.evidence_triage", rejected_pattern.stderr)

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
