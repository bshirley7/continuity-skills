from __future__ import annotations

import json
import os
import re
import shutil
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
import runtime as runtime_lib  # noqa: E402
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
        local_cli = self.root / ".agents" / "continuity" / "bin" / "continuity"
        local_cli.parent.mkdir(parents=True)
        local_cli.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        for skill in (SUITE / "skills").iterdir():
            if skill.is_dir():
                target = self.root / ".agents" / "skills" / skill.name
                target.mkdir(parents=True, exist_ok=True)
                target.joinpath("SKILL.md").write_text("---\nname: fixture\ndescription: fixture\n---\n", encoding="utf-8")
        (self.root / "test_smoke.py").write_text(
            "import unittest\n\nclass SmokeTest(unittest.TestCase):\n    def test_fixture(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
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
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CONTINUITY_ALLOW_TIME_OVERRIDE": "1"},
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
        selected_notes = source_note_ids if source_note_ids is not None else []
        payload = {
            "title": title,
            "scope": "Document and implement the approved bridge safety update.",
            "exclusions": ["Do not replace Electron"],
            "acceptance_criteria": ["Validation passes", "Memory impact is documented"],
            "memory_ids": ["memory-current", "memory-promoted", "memory-replacement"],
            "source_note_ids": selected_notes,
            "note_dispositions": [
                {
                    "note_id": note_id,
                    "disposition": "current-goal",
                    "reason": "The note is required by the current goal.",
                    "delivery_slice_ids": [],
                }
                for note_id in selected_notes
            ],
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
        self.assertIn("captured_at", capture)
        self.assertEqual(len(capture["items"]), 4)
        self.assertTrue(all(item["execution_authorized"] is False for item in capture["items"]))
        self.assertTrue(all(item["routing_status"] == "captured" for item in capture["items"]))
        self.assertTrue(all(item["work_status"] == "open" for item in capture["items"]))
        self.assertTrue(all(item["created_at"] and item["updated_at"] for item in capture["items"]))
        self.assertIn(".continuity/private/captures", capture["path"])

    def test_meeting_notes_create_one_batch_with_multiple_atomic_items(self) -> None:
        payload = {
            "source_type": "meeting",
            "source_ref": "meeting:synthetic-weekly-review-2026-07-15",
            "source_timestamp": "2026-07-15T15:00:00-05:00",
            "items": [
                {
                    "kind": "insight", "text": "The status view is easier to scan; preserve its current density.",
                    "perspective": "external", "sentiment": "positive", "occurrence_type": "feedback",
                    "impact": "medium", "confidence": "high", "actionability": "context",
                    "stakeholders": ["reviewer"], "themes": ["status-view", "scanability"],
                },
                {
                    "kind": "execution-candidate", "text": "Move the risk summary above dependencies in the next pass.",
                    "perspective": "external", "sentiment": "neutral", "occurrence_type": "need",
                    "impact": "medium", "confidence": "high", "actionability": "plan",
                    "stakeholders": ["product-owner"], "themes": ["risk-summary", "dependencies"],
                },
                {
                    "kind": "decision", "text": "Export remains outside the current objective.",
                    "perspective": "mixed", "sentiment": "neutral", "occurrence_type": "decision",
                    "impact": "medium", "confidence": "high", "actionability": "context",
                    "stakeholders": ["project-team"], "themes": ["scope", "export"],
                },
                {
                    "kind": "question", "text": "Should external reviewers see internal confidence labels?",
                    "perspective": "external", "sentiment": "unknown", "occurrence_type": "need",
                    "impact": "unknown", "confidence": "medium", "actionability": "monitor",
                    "stakeholders": ["reviewer"], "themes": ["visibility", "confidence-labels"],
                },
                {
                    "kind": "backlog-candidate", "text": "Consider saved-filter presets in a later objective.",
                    "perspective": "internal", "sentiment": "neutral", "occurrence_type": "observation",
                    "impact": "low", "confidence": "medium", "actionability": "plan",
                    "stakeholders": ["project-team"], "themes": ["filters", "later-work"],
                },
            ],
        }
        path = self.root / "meeting-notes.json"
        self.write_json(path, payload)
        capture = json.loads(self.cli("note", "capture", "--items-file", str(path)).stdout)
        self.assertEqual(capture["source_type"], "meeting")
        self.assertEqual(capture["capture_mode"], "batch")
        self.assertEqual(capture["item_count"], 5)
        self.assertEqual(len({item["item_id"] for item in capture["items"]}), 5)
        self.assertTrue(all(item["occurred_at"] == payload["source_timestamp"] for item in capture["items"]))
        self.assertTrue(all(item["execution_authorized"] is False for item in capture["items"]))
        handoff = json.loads(self.cli("workflow", "status", "--capture-id", capture["capture_id"]).stdout)["capture"]
        self.assertEqual(len(handoff["items"]), 5)
        duplicate = json.loads(self.cli("note", "capture", "--items-file", str(path)).stdout)
        self.assertEqual(duplicate["capture_id"], capture["capture_id"])
        self.assertTrue(duplicate["deduplicated"])

        singular = json.loads(self.cli("note", "capture", "--text", "One meeting callout.", "--source-type", "meeting", "--source-ref", "meeting:single-callout").stdout)
        self.assertEqual(singular["source_type"], "meeting")
        self.assertEqual(singular["capture_mode"], "singular")
        self.assertEqual(singular["item_count"], 1)

    def test_occurrence_dimensions_private_similarity_and_pattern_guidance(self) -> None:
        payload = {
            "source_type": "conversation",
            "source_ref": "thread:pattern",
            "items": [
                {
                    "kind": "insight", "text": "The client changed the navigation requirement again.",
                    "perspective": "external", "sentiment": "negative", "occurrence_type": "change",
                    "impact": "high", "confidence": "high", "actionability": "plan",
                    "stakeholders": ["client-a"], "themes": ["navigation", "adaptability"],
                },
                {
                    "kind": "insight", "text": "Client feedback revised the navigation direction.",
                    "perspective": "external", "sentiment": "mixed", "occurrence_type": "change",
                    "impact": "medium", "confidence": "high", "actionability": "monitor",
                    "stakeholders": ["client-a"], "themes": ["navigation", "adaptability"],
                },
                {
                    "kind": "insight", "text": "The adaptable component handled another client revision well.",
                    "perspective": "mixed", "sentiment": "positive", "occurrence_type": "change",
                    "impact": "medium", "confidence": "high", "actionability": "context",
                    "stakeholders": ["client-a"], "themes": ["navigation", "adaptability"],
                },
            ],
        }
        path = self.root / "pattern-capture.json"
        self.write_json(path, payload)
        capture = json.loads(self.cli("note", "capture", "--items-file", str(path)).stdout)
        self.assertEqual(capture["items"][0]["perspective"], "external")
        self.assertEqual(capture["items"][0]["occurrence_type"], "change")
        patterns = json.loads(self.cli("note", "patterns").stdout)["patterns"]
        stakeholder = next(item for item in patterns if item["axis"] == "stakeholder:client-a")
        self.assertEqual(stakeholder["count"], 3)
        self.assertIn("adaptability", stakeholder["recommendation"])
        disposition = json.loads(
            self.cli(
                "note", "pattern-review", stakeholder["pattern_id"], "--disposition", "accepted",
                "--actor", "fixture-user", "--evidence", "Adaptability is a current planning concern.",
            ).stdout
        )
        self.assertEqual(len(disposition["pattern_hash"]), 64)
        self.assertEqual(disposition["disposition"], "accepted")
        accepted_morning = json.loads(self.cli("report", "morning").stdout)
        self.assertNotIn(stakeholder["pattern_id"], {item.get("pattern_id") for item in accepted_morning["decisions_needed"]})
        self.cli(
            "note", "pattern-review", stakeholder["pattern_id"], "--disposition", "deferred",
            "--actor", "fixture-user", "--evidence", "Review later.", expected=2,
        )
        deferred = json.loads(
            self.cli(
                "note", "pattern-review", stakeholder["pattern_id"], "--disposition", "deferred",
                "--actor", "fixture-user", "--evidence", "Review later.", "--review-after", "2099-01-01T09:00:00-06:00",
            ).stdout
        )
        self.assertEqual(deferred["review_after"], "2099-01-01T09:00:00-06:00")
        deferred_morning = json.loads(self.cli("report", "morning").stdout)
        self.assertNotIn(stakeholder["pattern_id"], {item.get("pattern_id") for item in deferred_morning["decisions_needed"]})
        self.cli(
            "note", "pattern-review", stakeholder["pattern_id"], "--disposition", "deferred",
            "--actor", "fixture-user", "--evidence", "Review is due.", "--review-after", "2020-01-01T09:00:00-06:00",
        )
        due_morning = json.loads(self.cli("report", "morning").stdout)
        self.assertIn(stakeholder["pattern_id"], {item.get("pattern_id") for item in due_morning["decisions_needed"]})
        indexed = json.loads(self.cli("memory", "index", "--scope", "all").stdout)
        self.assertGreaterEqual(indexed["entries"], 5)
        similar = json.loads(self.cli("memory", "similar", "changing customer requirements", "--scope", "all").stdout)
        self.assertTrue(any(item["memory_id"] == capture["items"][0]["item_id"] for item in similar))

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
        self.assertEqual(routed["work_status"], "open")
        self.assertIn("updated_at", routed)
        self.assertFalse(routed["execution_authorized"])
        self.cli("note", "triage", capture["capture_id"], item["item_id"], "--kind", "explicit-instruction", "--action", "promote")
        queue = self.root / ".continuity" / "private" / "queues" / "planning.jsonl"
        self.assertEqual(len(queue.read_text(encoding="utf-8").splitlines()), 1)
        self.cli(
            "note", "triage", capture["capture_id"], capture["items"][2]["item_id"],
            "--kind", "question", "--action", "defer", expected=2,
        )
        deferred = json.loads(
            self.cli("note", "triage", capture["capture_id"], capture["items"][2]["item_id"], "--kind", "question", "--action", "defer", "--review-after", "2099-07-21").stdout
        )
        self.assertEqual(deferred["work_status"], "deferred")
        deferred_question = capture["items"][2]["item_id"]
        morning = json.loads(self.cli("report", "morning").stdout)
        self.assertNotIn(deferred_question, {item.get("note_id") for item in morning["decisions_needed"]})

    def test_derived_note_queue_ignores_stale_snapshots_and_resolves_questions(self) -> None:
        capture = self.create_capture()
        instruction = capture["items"][3]
        self.cli("note", "triage", capture["capture_id"], instruction["item_id"], "--action", "promote")
        self.assertEqual(len(json.loads(self.cli("note", "queue", "--queue", "planning").stdout)), 1)
        goal = self.create_goal("Queue truth", [instruction["item_id"]])
        self.assertEqual(json.loads(self.cli("note", "queue", "--queue", "planning").stdout), [])
        queue_history = self.root / ".continuity" / "private" / "queues" / "planning.jsonl"
        self.assertTrue(queue_history.read_text(encoding="utf-8").strip())
        question = capture["items"][2]
        self.cli("note", "triage", capture["capture_id"], question["item_id"], "--kind", "question", "--action", "route")
        resolved = json.loads(
            self.cli("note", "resolve", capture["capture_id"], question["item_id"], "--resolution", "Keep it internal.", "--actor", "fixture-user").stdout
        )
        self.assertEqual(resolved["work_status"], "completed")
        self.assertEqual(json.loads(self.cli("note", "queue", "--queue", "questions").stdout), [])
        self.assertEqual(goal["state"], "awaiting-feedback")

    def test_note_status_is_derived_across_hold_resume_cancel_and_revision(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        first = self.create_goal("First note goal", [note_id])
        second = self.create_goal("Second note goal", [note_id])
        self.approve(first)
        self.cli("goal", "hold", first["goal_id"])
        held = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == note_id)
        self.assertEqual(held["work_status"], "planned")
        self.cli("goal", "resume", first["goal_id"])
        self.cli("goal", "cancel", second["goal_id"])
        linked = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == note_id)
        self.assertEqual(linked["work_status"], "queued")
        self.cli("goal", "cancel", first["goal_id"])
        cancelled = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == note_id)
        self.assertEqual(cancelled["work_status"], "cancelled")
        third = self.create_goal("Revision removes note", [note_id])
        revision = self.root / "remove-source-note.json"
        self.write_json(revision, {"source_note_ids": []})
        self.cli(
            "goal", "revise", third["goal_id"], "--goal-file", str(revision),
            "--author", "fixture-user", "--summary", "Move the note to another aligned goal",
        )
        revised_note = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == note_id)
        self.assertEqual(revised_note["goal_links"][third["goal_id"]]["state"], "unlinked")
        self.assertIn(third["goal_id"], revised_note["related_goal_ids"])
        standalone_note_id = capture["items"][0]["item_id"]
        fourth = self.create_goal("Standalone revision", [standalone_note_id])
        self.write_json(revision, {"source_note_ids": []})
        self.cli(
            "goal", "revise", fourth["goal_id"], "--goal-file", str(revision),
            "--author", "fixture-user", "--summary", "Remove the only source note",
        )
        standalone = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == standalone_note_id)
        self.assertEqual(standalone["work_status"], "open")
        self.assertEqual(standalone["goal_links"][fourth["goal_id"]]["state"], "unlinked")

    def test_legacy_note_links_block_resolution_and_migrate_idempotently(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][2]["item_id"]
        goal = self.create_goal("Legacy note migration", [note_id])
        capture_path = next((self.root / ".continuity" / "private" / "captures").glob("**/*.json"))
        stored = json.loads(capture_path.read_text(encoding="utf-8"))
        item = next(value for value in stored["items"] if value["item_id"] == note_id)
        item.pop("goal_links", None)
        self.write_json(capture_path, stored)
        self.cli(
            "note", "resolve", capture["capture_id"], note_id,
            "--resolution", "Should remain attached to active work.", expected=2,
        )
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertIn(note_id, doctor["legacy_note_ids"])
        migrated = json.loads(self.cli("note", "migrate-links", "--actor", "fixture-user").stdout)
        self.assertEqual(migrated["migrated"], 1)
        self.assertEqual(migrated["remaining_legacy_note_ids"], [])
        repeated = json.loads(self.cli("note", "migrate-links", "--actor", "fixture-user").stdout)
        self.assertEqual(repeated["migrated"], 0)
        persisted = json.loads(capture_path.read_text(encoding="utf-8"))
        migrated_item = next(value for value in persisted["items"] if value["item_id"] == note_id)
        self.assertEqual(migrated_item["goal_links"][goal["goal_id"]]["state"], "awaiting-feedback")
        self.assertIn("goal_links_migrated_at", migrated_item)

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
        planned_note = [note for note in json.loads(self.cli("note", "list").stdout) if note["item_id"] == note_id][0]
        self.assertEqual(planned_note["work_status"], "planned")
        self.assertIn(goal["goal_id"], planned_note["related_goal_ids"])
        self.approve(goal)
        queued_note = [note for note in json.loads(self.cli("note", "list").stdout) if note["item_id"] == note_id][0]
        self.assertEqual(queued_note["work_status"], "queued")
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
        capture = self.create_capture()
        source_note_id = capture["items"][3]["item_id"]
        goal = self.create_goal(source_note_ids=[source_note_id])
        (self.root / "capture.json").unlink()
        (self.root / "goal-Improve-bridge-safety.json").unlink()
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/test")
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/test")
        self.cli("run", "update", goal["goal_id"], "--state", "review-ready", expected=2)
        self.cli("test", "run", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/test")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "Evidence passed",
            "--worktree", str(self.root), "--branch", "continuity/test",
            "--code-review-evidence", "diff reviewed", "--security-evidence", "trust boundaries reviewed", "--update-gates",
        )
        self.cli(
            "merge", "assess", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/test",
            "--evidence", "clean branch reviewed", "--update-gate",
        )
        stages = [
            "implementation",
            "documentation",
            "memory-impact",
            "roadmap-impact",
            "final-alignment",
        ]
        for stage in stages:
            self.cli("goal", "gate", goal["goal_id"], stage, "--status", "passed", "--evidence", f"fixture:{stage}")
        self.cli("run", "update", goal["goal_id"], "--state", "validating")
        review_ready = json.loads(self.cli("run", "update", goal["goal_id"], "--state", "review-ready", "--summary", "All gates passed").stdout)
        self.assertEqual(review_ready["state"], "review-ready")
        goal_record = json.loads((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json").read_text())
        self.assertEqual(goal_record["state"], "review-ready")
        self.cli(
            "merge", "record-human", goal["goal_id"], "--pr-url", "https://github.com/example/project/pull/1",
            "--merged-by", "fixture-user", "--disposition", "merged", "--merge-commit", "abc123", "--evidence", "Human reviewed and merged PR #1",
        )
        completed_goal = json.loads((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json").read_text())
        self.assertEqual(completed_goal["state"], "completed")
        completed_note = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == source_note_id)
        self.assertEqual(completed_note["work_status"], "completed")
        completed_lifecycle = json.loads(self.cli("workflow", "status", "--note-id", source_note_id).stdout)["note"]["lifecycle"]
        self.assertEqual(completed_lifecycle["summary_status"], "completed")
        self.assertEqual(completed_lifecycle["current_stage"], "completed")
        self.assertEqual(completed_lifecycle["goal_tracks"][0]["goal_state"], "completed")
        self.assertIn("completed", {event["stage"] for event in completed_lifecycle["timeline"]})
        self.cli("goal", "start", goal["goal_id"], expected=2)

    def test_quality_and_merge_reports_update_gates_and_morning_status(self) -> None:
        goal = self.create_goal("Quality gates")
        goal_payload = self.root / "goal-Quality-gates.json"
        if goal_payload.exists():
            goal_payload.unlink()
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/quality-gates")
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/quality-gates")
        plan = json.loads(self.cli("test", "plan", goal["goal_id"], "--worktree", str(self.root)).stdout)
        self.assertIn("python3 -m unittest", plan["validation_commands"])
        self.assertTrue(plan["evergreen_checks"])
        self.cli(
            "test",
            "record",
            goal["goal_id"],
            "--status",
            "passed",
            "--summary",
            "Missing security evidence",
            "--code-review-evidence",
            "diff reviewed",
            "--validation-evidence",
            "python3 -m unittest exited 0",
            expected=2,
        )
        machine = json.loads(
            self.cli(
                "test", "run", goal["goal_id"], "--worktree", str(self.root),
                "--branch", "continuity/quality-gates",
            ).stdout
        )
        self.assertEqual(machine["status"], "passed", machine)
        self.assertTrue(machine["source_fingerprint"])
        report = json.loads(
            self.cli(
                "test",
                "record",
                goal["goal_id"],
                "--status",
                "passed",
                "--summary",
                "Quality gates passed",
                "--worktree",
                str(self.root),
                "--branch",
                "continuity/quality-gates",
                "--code-review-evidence",
                "diff reviewed for maintainability and scope",
                "--validation-evidence",
                "python3 -m unittest exited 0",
                "--security-evidence",
                "manual security review found no touched trust boundary risk",
                "--update-gates",
            ).stdout
        )
        self.assertEqual(report["status"], "passed")
        compliance_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "compliance.json"
        compliance = json.loads(compliance_path.read_text(encoding="utf-8"))
        self.assertEqual(compliance["stages"]["code-review"]["status"], "passed")
        self.assertEqual(compliance["stages"]["validation"]["status"], "passed")
        self.assertEqual(compliance["stages"]["security-review"]["status"], "passed")
        fake_bin = self.root.parent / "fake-bin"
        fake_bin.mkdir()
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            "#!/bin/sh\nprintf '%s\\n' '{\"state\":\"OPEN\",\"headRefName\":\"continuity/quality-gates\",\"baseRefName\":\"main\",\"headRefOid\":\"deadbeef\"}'\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        original_path = os.environ.get("PATH", "")
        pr_config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        pr_config["require_pr"] = True
        self.write_json(self.root / ".continuity" / "config.json", pr_config)
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        try:
            mismatch = json.loads(
                self.cli(
                    "merge", "assess", goal["goal_id"], "--branch", "continuity/quality-gates",
                    "--worktree", str(self.root), "--pr-url", "https://github.com/example/project/pull/1",
                ).stdout
            )
            self.assertEqual(mismatch["status"], "failed")
            self.assertIn("PR head commit does not match the tested local commit", mismatch["failures"])
        finally:
            os.environ["PATH"] = original_path
            pr_config["require_pr"] = False
            self.write_json(self.root / ".continuity" / "config.json", pr_config)
        merge = json.loads(
            self.cli(
                "merge",
                "assess",
                goal["goal_id"],
                "--branch",
                "continuity/quality-gates",
                "--worktree",
                str(self.root),
                "--evidence",
                "base and branch state reviewed",
                "--update-gate",
            ).stdout
        )
        self.assertEqual(merge["status"], "passed", merge)
        compliance = json.loads(compliance_path.read_text(encoding="utf-8"))
        self.assertEqual(compliance["stages"]["merge-safety"]["status"], "passed")
        for stage in ("implementation", "documentation", "memory-impact", "roadmap-impact", "final-alignment"):
            self.cli("goal", "gate", goal["goal_id"], stage, "--status", "passed", "--evidence", f"fixture:{stage}")
        self.cli("run", "update", goal["goal_id"], "--state", "validating")
        review_ready = json.loads(
            self.cli("run", "update", goal["goal_id"], "--state", "review-ready", "--summary", "Ready for human review").stdout
        )
        self.assertEqual(review_ready["state"], "review-ready")
        morning = json.loads(self.cli("report", "morning").stdout)
        self.assertEqual(morning["decisions_needed"][0]["goal_id"], goal["goal_id"])
        self.assertEqual(morning["workflow_status"][0]["workflow"]["current_stage"], "human-review")
        self.assertEqual({item["disposition"] for item in morning["decisions_needed"][0]["allowed_dispositions"]}, {"approved", "changes-requested", "merged", "closed"})
        self.assertIn("queue_counts", morning)
        self.assertIn("memory_health", morning)
        self.assertIn("roadmap_health", morning)
        human = json.loads(
            self.cli(
                "merge",
                "record-human",
                goal["goal_id"],
                "--pr-url",
                "https://github.com/example/project/pull/1",
                "--merged-by",
                "fixture-user",
                "--disposition",
                "merged",
                "--merge-commit",
                "abc123",
                "--evidence",
                "human reviewed and merged PR #1",
            ).stdout
        )
        self.assertEqual(human["status"], "merged")
        completed_morning = json.loads(self.cli("report", "morning").stdout)
        self.assertEqual(completed_morning["completed_overnight"][0]["goal_id"], goal["goal_id"])
        compliance = json.loads(compliance_path.read_text(encoding="utf-8"))
        self.assertEqual(compliance["stages"]["human-review"]["status"], "passed")
        project_report = self.cli("report", "project").stdout
        self.assertIn("Latest test report", project_report)
        self.assertIn("Latest merge assessment", project_report)

    def test_human_authorized_github_cli_merge_is_sha_bound_and_opt_in(self) -> None:
        config_path = self.root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config.update(
            {
                "github_required_checks": ["Continuity CI"],
                "github_required_reviewers": 1,
                "github_cli_merge_enabled": True,
            }
        )
        self.write_json(config_path, config)
        self.git("add", ".continuity/config.json")
        self.git("commit", "-m", "enable guarded cli merge fixture")

        goal = self.create_goal("Guarded CLI merge")
        payload = self.root / "goal-Guarded-CLI-merge.json"
        if payload.exists():
            payload.unlink()
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/guarded-cli-merge")
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config.update({"require_pr": True, "require_pr_auth": True})
        self.write_json(config_path, config)
        self.git("add", ".continuity/config.json")
        self.git("commit", "-m", "require authenticated PR fixture")
        pr_url = "https://github.com/example/project/pull/42"
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/guarded-cli-merge")
        self.cli("run", "update", goal["goal_id"], "--state", "validating", "--pr-url", pr_url)
        machine = json.loads(
            self.cli(
                "test", "run", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/guarded-cli-merge"
            ).stdout
        )
        self.assertEqual(machine["status"], "passed")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "CLI merge evidence passed",
            "--worktree", str(self.root), "--branch", "continuity/guarded-cli-merge",
            "--code-review-evidence", "complete diff reviewed", "--security-evidence", "merge boundary reviewed", "--update-gates",
        )
        head_sha = self.git("rev-parse", "HEAD")
        merge_commit = "b" * 40
        fake_bin = self.root.parent / "guarded-merge-bin"
        fake_bin.mkdir()
        state_path = self.root.parent / "guarded-merge-state"
        state_path.write_text("open\n", encoding="utf-8")
        log_path = self.root.parent / "guarded-merge-gh.log"
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$*\" >> '{log_path}'\n"
            "if [ \"$1\" = \"api\" ] && [ \"$2\" = \"user\" ]; then\n"
            "  printf '%s\\n' 'fixture-user'\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"pr\" ] && [ \"$2\" = \"merge\" ]; then\n"
            f"  printf '%s\\n' 'merged' > '{state_path}'\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"pr\" ] && [ \"$2\" = \"view\" ]; then\n"
            f"  if [ \"$(cat '{state_path}')\" = \"merged\" ]; then\n"
            f"    printf '%s\\n' '{{\"state\":\"MERGED\",\"headRefName\":\"continuity/guarded-cli-merge\",\"baseRefName\":\"main\",\"headRefOid\":\"{head_sha}\",\"isDraft\":false,\"mergeStateStatus\":\"CLEAN\",\"reviewDecision\":\"APPROVED\",\"reviews\":[{{\"state\":\"APPROVED\",\"author\":{{\"login\":\"fixture-reviewer\"}}}}],\"statusCheckRollup\":[{{\"name\":\"Continuity CI\",\"conclusion\":\"SUCCESS\"}}],\"mergeCommit\":{{\"oid\":\"{merge_commit}\"}},\"mergedBy\":{{\"login\":\"fixture-user\"}}}}'\n"
            "  else\n"
            f"    printf '%s\\n' '{{\"state\":\"OPEN\",\"headRefName\":\"continuity/guarded-cli-merge\",\"baseRefName\":\"main\",\"headRefOid\":\"{head_sha}\",\"isDraft\":false,\"mergeStateStatus\":\"CLEAN\",\"reviewDecision\":\"APPROVED\",\"reviews\":[{{\"state\":\"APPROVED\",\"author\":{{\"login\":\"fixture-reviewer\"}}}}],\"statusCheckRollup\":[{{\"name\":\"Continuity CI\",\"conclusion\":\"SUCCESS\"}}],\"mergeCommit\":null,\"mergedBy\":null}}'\n"
            "  fi\n"
            "  exit 0\n"
            "fi\n"
            "exit 1\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        try:
            assessment = json.loads(
                self.cli(
                    "merge", "assess", goal["goal_id"], "--worktree", str(self.root),
                    "--branch", "continuity/guarded-cli-merge", "--pr-url", pr_url,
                    "--evidence", "authenticated PR and branch reviewed", "--update-gate",
                ).stdout
            )
            self.assertEqual(assessment["status"], "passed", assessment)
            for stage in ("implementation", "documentation", "memory-impact", "roadmap-impact", "final-alignment"):
                self.cli("goal", "gate", goal["goal_id"], stage, "--status", "passed", "--evidence", f"fixture:{stage}")
            self.cli(
                "run", "update", goal["goal_id"], "--state", "review-ready",
                "--summary", "Ready for exact CLI merge", "--pr-url", pr_url,
            )
            workflow = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
            self.assertIn("execute-cli-merge", {action["disposition"] for action in workflow["allowed_actions"]})
            authorization_text = f"Merge {goal['goal_id']} PR {pr_url} at {head_sha} using squash"
            self.cli(
                "merge", "execute", goal["goal_id"], "--pr-url", pr_url, "--head-sha", head_sha,
                "--merge-method", "squash", "--authorized-by", "fixture-user",
                "--authorization-text", "Merge something else", expected=2,
            )
            self.assertEqual(state_path.read_text(encoding="utf-8").strip(), "open")
            merged = json.loads(
                self.cli(
                    "merge", "execute", goal["goal_id"], "--pr-url", pr_url, "--head-sha", head_sha,
                    "--merge-method", "squash", "--authorized-by", "fixture-user",
                    "--authorization-text", authorization_text,
                ).stdout
            )
        finally:
            os.environ["PATH"] = original_path
        self.assertEqual(merged["status"], "merged")
        self.assertEqual(merged["merge_commit"], merge_commit)
        goal_dir = self.root / ".continuity" / "private" / "goals" / goal["goal_id"]
        authorization = json.loads((goal_dir / "merge-authorization.json").read_text(encoding="utf-8"))
        self.assertEqual(authorization["head_sha"], head_sha)
        self.assertEqual(authorization["authorization_text"], authorization_text)
        self.assertEqual(json.loads((goal_dir / "goal.json").read_text(encoding="utf-8"))["state"], "completed")
        gh_log = log_path.read_text(encoding="utf-8")
        self.assertIn(f"--match-head-commit {head_sha}", gh_log)
        self.assertNotIn("--admin", gh_log)
        self.assertNotIn("--auto", gh_log)

    def test_workflow_status_and_changes_requested_reopen_same_goal(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        self.cli("note", "triage", capture["capture_id"], note_id, "--action", "promote")
        goal = self.create_goal("Review rework", [note_id])
        (self.root / "capture.json").unlink()
        (self.root / "goal-Review-rework.json").unlink()
        initial = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual(initial["current_stage"], "plan-review")
        self.assertEqual({action["disposition"] for action in initial["allowed_actions"]}, {"approve", "revise", "hold", "cancel"})
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/review-rework")
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/review-rework")
        attempt_artifact = self.root / "attempt-evidence.md"
        attempt_artifact.write_text("attempt one evidence\n", encoding="utf-8")
        self.git("add", "attempt-evidence.md")
        self.git("commit", "-m", "add attempt evidence")
        self.cli("test", "run", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/review-rework")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "Current evidence",
            "--worktree", str(self.root), "--branch", "continuity/review-rework",
            "--code-review-evidence", "diff reviewed", "--security-evidence", "trust boundaries reviewed", "--update-gates",
        )
        self.cli(
            "merge", "assess", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/review-rework",
            "--evidence", "clean branch reviewed", "--update-gate",
        )
        for stage in ("implementation", "documentation", "memory-impact", "roadmap-impact", "final-alignment"):
            self.cli("goal", "gate", goal["goal_id"], stage, "--status", "passed", "--evidence", f"fixture:{stage}")
        self.cli("run", "update", goal["goal_id"], "--state", "validating")
        self.cli(
            "run", "update", goal["goal_id"], "--state", "review-ready", "--summary", "Ready for review",
            "--artifact", str(attempt_artifact),
        )
        stale_source = self.root / "changed-after-review.txt"
        stale_source.write_text("stale review evidence\n", encoding="utf-8")
        self.cli(
            "merge", "record-human", goal["goal_id"], "--pr-url", "https://github.com/example/project/pull/2",
            "--merged-by", "fixture-user", "--disposition", "approved", "--evidence", "Approve stale work.",
            expected=2,
        )
        stale_status = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual({action["disposition"] for action in stale_status["allowed_actions"]}, {"changes-requested", "closed"})
        self.assertEqual({action["disposition"] for action in stale_status["blocked_actions"]}, {"approved", "merged"})
        stale_morning = json.loads(self.cli("report", "morning").stdout)
        self.assertIn(goal["goal_id"], {item.get("goal_id") for item in stale_morning["blocked_or_at_risk"]})
        disposition = json.loads(
            self.cli(
                "merge", "record-human", goal["goal_id"], "--pr-url", "https://github.com/example/project/pull/2",
                "--merged-by", "fixture-user", "--disposition", "changes-requested", "--evidence", "Adjust the in-scope error copy.",
            ).stdout
        )
        self.assertEqual(disposition["status"], "changes-requested")
        goal_dir = self.root / ".continuity" / "private" / "goals" / goal["goal_id"]
        changed = json.loads((goal_dir / "goal.json").read_text(encoding="utf-8"))
        self.assertEqual(changed["state"], "changes-requested")
        self.assertEqual(changed["execution_attempt"], 2)
        self.assertTrue((goal_dir / "attempts" / "attempt-1" / "test-report.json").exists())
        self.assertTrue((goal_dir / "attempts" / "attempt-1" / "compliance.json").exists())
        self.assertFalse((goal_dir / "test-report.json").exists())
        current_execution = json.loads((goal_dir / "execution.json").read_text(encoding="utf-8"))
        self.assertEqual(current_execution["state"], "rework-queued")
        self.assertEqual(current_execution["execution_attempt"], 2)
        self.assertNotIn("artifacts", current_execution)
        self.assertNotIn("started_at", current_execution)
        self.assertNotIn("branch", current_execution)
        self.assertNotIn("worktree", current_execution)
        archived_execution = json.loads((goal_dir / "attempts" / "attempt-1" / "execution.json").read_text(encoding="utf-8"))
        self.assertIn("attempt-evidence.md", archived_execution["artifacts"])
        status = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual({action["disposition"] for action in status["allowed_actions"]}, {"resume-in-scope", "revise-scope", "cancel"})
        self.assertEqual(set(status["human_requirements"]), {"resume-in-scope", "revise-scope", "cancel"})
        self.assertEqual(status["evidence"]["prior_attempts"][0]["attempt"], 1)
        stale_source.unlink()
        self.cli("goal", "resume", goal["goal_id"], expected=2)
        resumed = json.loads(
            self.cli(
                "goal", "resume", goal["goal_id"], "--actor", "fixture-user",
                "--authorization-text", f"Resume {goal['goal_id']} under approved plan v1",
            ).stdout
        )
        self.assertEqual(resumed["state"], "queued")
        self.assertEqual(resumed["execution_attempt"], 2)
        linked_note = next(item for item in json.loads(self.cli("note", "list").stdout) if item["item_id"] == note_id)
        self.assertEqual(linked_note["work_status"], "queued")
        feedback = [item for item in json.loads(self.cli("note", "list").stdout) if item.get("occurrence_type") == "feedback"]
        self.assertTrue(any(goal["goal_id"] in item.get("related_goal_ids", []) for item in feedback))

    def test_review_ready_can_close_or_cancel_without_current_delivery_evidence(self) -> None:
        closed_goal = self.create_goal("Close stale review")
        closed_path = self.root / ".continuity" / "private" / "goals" / closed_goal["goal_id"] / "goal.json"
        closed_record = json.loads(closed_path.read_text(encoding="utf-8"))
        closed_record["state"] = "review-ready"
        self.write_json(closed_path, closed_record)
        closed = json.loads(
            self.cli(
                "merge", "record-human", closed_goal["goal_id"],
                "--pr-url", "https://github.com/example/project/pull/3", "--merged-by", "fixture-user",
                "--disposition", "closed", "--evidence", "Human closed stale review work.",
            ).stdout
        )
        self.assertEqual(closed["status"], "closed")
        self.assertFalse(closed["review_evidence_current"])
        self.assertTrue(closed["stale_evidence"])
        self.assertEqual(json.loads(closed_path.read_text(encoding="utf-8"))["state"], "cancelled")

        cancelled_goal = self.create_goal("Cancel stale review")
        cancelled_path = self.root / ".continuity" / "private" / "goals" / cancelled_goal["goal_id"] / "goal.json"
        cancelled_record = json.loads(cancelled_path.read_text(encoding="utf-8"))
        cancelled_record["state"] = "review-ready"
        self.write_json(cancelled_path, cancelled_record)
        self.cli("goal", "cancel", cancelled_goal["goal_id"], expected=2)
        cancelled = json.loads(
            self.cli(
                "goal", "cancel", cancelled_goal["goal_id"], "--actor", "fixture-user",
                "--reason", "Human cancelled review-ready work without delivery.",
            ).stdout
        )
        self.assertEqual(cancelled["state"], "cancelled")
        cancelled_review = json.loads(
            (self.root / ".continuity" / "private" / "goals" / cancelled_goal["goal_id"] / "human-review.json").read_text(encoding="utf-8")
        )
        self.assertEqual(cancelled_review["status"], "closed")

    def test_scope_revision_and_blocked_recovery_require_explicit_human_action(self) -> None:
        goal = self.create_goal("Blocked recovery")
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.cli("run", "update", goal["goal_id"], "--state", "blocked", "--summary", "Dependency unavailable")
        self.cli("goal", "resume", goal["goal_id"], expected=2)
        resumed = json.loads(
            self.cli(
                "goal", "resume", goal["goal_id"], "--actor", "fixture-user",
                "--authorization-text", f"Resume {goal['goal_id']} under approved plan v1",
            ).stdout
        )
        self.assertEqual(resumed["state"], "queued")
        preflight = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "preflight.json"
        self.assertTrue(preflight.exists())
        self.assertTrue(json.loads(preflight.read_text(encoding="utf-8"))["passed"])
        revision_path = self.root / "scope-revision.json"
        self.write_json(revision_path, {"scope": "Expanded scope requiring a new approval."})
        revised = json.loads(
            self.cli("goal", "revise", goal["goal_id"], "--goal-file", str(revision_path), "--author", "fixture-user", "--summary", "Scope expanded").stdout
        )
        self.assertEqual(revised["plan_version"], 2)
        self.assertEqual(revised["state"], "awaiting-feedback")
        self.assertFalse((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "approval.json").exists())
        self.cli(
            "goal", "resume", goal["goal_id"], "--actor", "fixture-user",
            "--authorization-text", f"Resume {goal['goal_id']} under approved plan v1", expected=2,
        )

    def test_queued_goal_cannot_skip_execution_or_restart_terminal(self) -> None:
        goal = self.create_goal()
        self.approve(goal)
        self.cli("run", "update", goal["goal_id"], "--state", "review-ready", "--summary", "claimed", expected=2)
        self.cli("run", "update", goal["goal_id"], "--state", "running", expected=2)

    def test_machine_test_evidence_rejects_source_drift_and_shell_syntax(self) -> None:
        goal = self.create_goal("Bind machine evidence")
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/bind-machine-evidence")
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/bind-machine-evidence")
        machine = json.loads(
            self.cli("test", "run", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/bind-machine-evidence").stdout
        )
        self.assertEqual(machine["status"], "passed")
        agents = self.root / "AGENTS.md"
        original = agents.read_text(encoding="utf-8")
        agents.write_text(original + "\nChanged after machine evidence.\n", encoding="utf-8")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "stale claim",
            "--worktree", str(self.root), "--code-review-evidence", "reviewed",
            "--security-evidence", "manual trust boundary review", expected=2,
        )
        agents.write_text(original, encoding="utf-8")
        untracked = self.root / "new-untracked-source.txt"
        untracked.write_text("first version\n", encoding="utf-8")
        refreshed = json.loads(
            self.cli(
                "test", "run", goal["goal_id"], "--worktree", str(self.root),
                "--branch", "continuity/bind-machine-evidence",
            ).stdout
        )
        self.assertEqual(refreshed["status"], "passed")
        untracked.write_text("changed after test\n", encoding="utf-8")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "untracked drift",
            "--worktree", str(self.root), "--code-review-evidence", "reviewed",
            "--security-evidence", "manual trust boundary review", expected=2,
        )
        untracked.unlink()
        current_machine = json.loads(
            self.cli(
                "test", "run", goal["goal_id"], "--worktree", str(self.root),
                "--branch", "continuity/bind-machine-evidence",
            ).stdout
        )
        self.assertEqual(current_machine["status"], "passed")
        self.git("checkout", "-b", "continuity/different-branch")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "branch drift",
            "--worktree", str(self.root), "--code-review-evidence", "reviewed",
            "--security-evidence", "manual trust boundary review", expected=2,
        )
        self.git("checkout", "continuity/bind-machine-evidence")
        self.cli("test", "run", goal["goal_id"], "--worktree", str(self.root), "--branch", "continuity/bind-machine-evidence")
        self.git("commit", "--allow-empty", "-m", "Change commit identity")
        self.cli(
            "test", "record", goal["goal_id"], "--status", "passed", "--summary", "commit drift",
            "--worktree", str(self.root), "--code-review-evidence", "reviewed",
            "--security-evidence", "manual trust boundary review", expected=2,
        )
        unrelated = self.root.parent / "unrelated-repository"
        unrelated.mkdir()
        subprocess.run(["git", "-C", str(unrelated), "init", "-b", "main"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(unrelated), "config", "user.email", "tests@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(unrelated), "config", "user.name", "Tests"], check=True)
        (unrelated / "README.md").write_text("unrelated\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(unrelated), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(unrelated), "commit", "-m", "fixture"], check=True, capture_output=True)
        self.cli(
            "test", "run", goal["goal_id"], "--worktree", str(unrelated),
            "--branch", "main", expected=2,
        )
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["validation_commands"] = ["python3 -c 'print(1)' && echo unsafe"]
        self.write_json(self.root / ".continuity" / "config.json", config)
        unsafe = json.loads(self.cli("test", "run", goal["goal_id"], "--worktree", str(self.root)).stdout)
        self.assertEqual(unsafe["status"], "failed")
        self.assertIn("without shell syntax", unsafe["failures"][0])

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

    def test_doctor_flags_legacy_goal_state_for_explicit_revision(self) -> None:
        goal = self.create_goal("Legacy migration")
        goal_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json"
        legacy = json.loads(goal_path.read_text(encoding="utf-8"))
        legacy["state"] = "proposed-plan"
        self.write_json(goal_path, legacy)
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertIn(goal["goal_id"], doctor["legacy_goal_ids"])
        self.assertFalse(doctor["healthy"])
        revision = self.root / "legacy-revision.json"
        self.write_json(revision, {"scope": "Explicitly migrated legacy scope."})
        migrated = json.loads(
            self.cli(
                "goal", "revise", goal["goal_id"], "--goal-file", str(revision),
                "--author", "fixture-user", "--summary", "Migrate legacy state",
            ).stdout
        )
        self.assertEqual(migrated["state"], "awaiting-feedback")
        self.assertEqual(migrated["plan_version"], 2)

    def test_planning_patterns_are_validated_hashed_and_non_authorizing(self) -> None:
        payload = {
            "goal_id": "goal-patterns",
            "title": "Plan a verified renderer change",
            "scope": "Deliver the approved renderer behavior in safe increments.",
            "acceptance_criteria": ["Each slice is independently verified"],
            "memory_ids": ["memory-current"],
            "source_note_ids": [],
            "note_dispositions": [],
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
            "source_note_ids": [],
            "note_dispositions": [],
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
            "source_note_ids": [],
            "note_dispositions": [],
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
        imported = first["imported"][0]
        self.assertTrue(imported["capture_id"])
        routed = json.loads(
            self.cli(
                "note", "triage", imported["capture_id"], imported["item_ids"][0],
                "--kind", "context", "--action", "route",
            ).stdout
        )
        self.assertEqual(routed["queue"], "knowledge")
        self.assertFalse(routed["execution_authorized"])

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

    def test_scheduler_registration_run_ledger_idempotency_and_recovery(self) -> None:
        config = json.loads((self.root / ".continuity" / "config.json").read_text())
        config["scheduler"] = {
            "provider": "external",
            "sweep_minutes": 15,
            "business_days": [0, 1, 2, 3, 4],
            "retry_limit": 2,
            "retry_backoff_minutes": 15,
            "stale_after_minutes": 45,
            "portfolio_max_concurrency": 4,
        }
        config["behavior_configuration_hash"] = "a" * 64
        self.write_json(self.root / ".continuity" / "config.json", config)
        registered = json.loads(
            self.cli("scheduler", "register", "--task-id", "supervisor-fixture", "--root", self.temp.name, "--actor", "fixture-user").stdout
        )
        self.assertEqual(registered["state"], "registered")
        mismatched_roots = json.loads(
            self.cli(
                "portfolio", "actions", "--root", str(self.root), "--action", "review",
                "--at", "2026-07-15T20:30:00-05:00", "--supervisor-task-id", "supervisor-fixture",
                "--sweep-id", "sweep-wrong-roots",
            ).stdout
        )
        self.assertEqual(mismatched_roots[0]["status"], "blocked")
        self.assertIn("workspace roots", mismatched_roots[0]["reason"])
        def reserve(action: str, at: str, sweep_id: str) -> dict[str, object]:
            records = json.loads(
                self.cli(
                    "portfolio", "actions", "--root", self.temp.name, "--action", action,
                    "--at", at, "--supervisor-task-id", "supervisor-fixture", "--sweep-id", sweep_id,
                ).stdout
            )
            candidates = [record for record in records if record.get("status") in {"due", "retry"}]
            self.assertTrue(candidates, records)
            candidate = candidates[0]
            claims_path = self.root / ".continuity" / "private" / "scheduler-due-actions.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            claims[candidate["claim_token"]]["expires_at"] = "2999-01-01T00:00:00-06:00"
            self.write_json(claims_path, claims)
            return candidate

        review_claim = reserve("review", "2026-07-15T20:30:00-05:00", "sweep-review-15")
        run = json.loads(
            self.cli(
                "scheduler", "run-start", "review", "--idempotency-key", review_claim["idempotency_key"],
                "--claim-token", review_claim["claim_token"], "--task-id", "child-task-1",
            ).stdout
        )
        self.cli("scheduler", "run-heartbeat", run["run_id"], "--summary", "Still reviewing")
        self.cli("scheduler", "run-finish", run["run_id"], "--status", "succeeded", "--summary", "Review completed")
        self.cli(
            "scheduler", "run-start", "review", "--idempotency-key", review_claim["idempotency_key"],
            "--claim-token", review_claim["claim_token"], "--task-id", "duplicate-task", expected=2,
        )
        report_claim = reserve("report", "2026-07-16T07:30:00-05:00", "sweep-report-16")
        stale = json.loads(
            self.cli(
                "scheduler", "run-start", "report", "--idempotency-key", report_claim["idempotency_key"],
                "--claim-token", report_claim["claim_token"], "--task-id", "child-task-2",
            ).stdout
        )
        runs_path = self.root / ".continuity" / "private" / "scheduler-runs.jsonl"
        with runs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({**stale, "status": "heartbeat", "at": "2020-01-01T00:00:00-06:00", "summary": "stale fixture"}) + "\n")
        recovered = json.loads(self.cli("scheduler", "recover", "--run-id", stale["run_id"], "--actor", "fixture-user").stdout)
        self.assertEqual(recovered[0]["status"], "stale")
        goal = self.create_goal("Recover stale execution")
        self.approve(goal)
        goal_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json"
        queued_goal = json.loads(goal_path.read_text(encoding="utf-8"))
        queued_goal["scheduled_for"] = "2020-01-01T22:00:00-06:00"
        self.write_json(goal_path, queued_goal)
        dispatch_waiting = json.loads(
            self.cli(
                "portfolio", "actions", "--root", self.temp.name, "--action", "dispatch",
                "--at", "2026-07-16T22:30:00-05:00", "--supervisor-task-id", "supervisor-fixture",
                "--sweep-id", "sweep-dispatch-waiting",
            ).stdout
        )
        self.assertEqual(dispatch_waiting[0]["status"], "waiting-for-review")
        review_16_claim = reserve("review", "2026-07-16T20:30:00-05:00", "sweep-review-16")
        review_16 = json.loads(
            self.cli(
                "scheduler", "run-start", "review", "--idempotency-key", review_16_claim["idempotency_key"],
                "--claim-token", review_16_claim["claim_token"], "--task-id", "review-task-16",
            ).stdout
        )
        self.cli("scheduler", "run-finish", review_16["run_id"], "--status", "succeeded", "--summary", "Review completed")
        dispatch_claim = reserve("dispatch", "2026-07-16T22:30:00-05:00", "sweep-dispatch-16")
        execution_run = json.loads(
            self.cli(
                "scheduler", "run-start", "dispatch", "--idempotency-key", dispatch_claim["idempotency_key"],
                "--claim-token", dispatch_claim["claim_token"], "--task-id", "execution-task", "--goal-id", goal["goal_id"],
            ).stdout
        )
        self.cli("goal", "start", goal["goal_id"])
        self.cli(
            "run", "update", goal["goal_id"], "--state", "running", "--task-id", "execution-task",
            "--branch", "continuity/recover-stale-execution",
        )
        self.cli(
            "scheduler", "run-finish", execution_run["run_id"], "--status", "succeeded",
            "--summary", "Incorrect early success", expected=2,
        )
        with runs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({**execution_run, "status": "heartbeat", "at": "2020-01-01T00:00:00-06:00", "summary": "stale execution fixture"}) + "\n")
        execution_recovery = json.loads(
            self.cli("scheduler", "recover", "--run-id", execution_run["run_id"], "--actor", "fixture-user").stdout
        )
        self.assertEqual(execution_recovery[0]["goal_recovery"], "blocked-and-lock-released")
        recovered_goal = json.loads(goal_path.read_text())
        self.assertEqual(recovered_goal["state"], "blocked")
        self.assertFalse((self.root / ".continuity" / "private" / "project.lock.json").exists())
        race_claim = reserve("review", "2026-07-19T20:30:00-05:00", "sweep-race")
        command = [
            "python3", str(CLI), "--project-root", str(self.root), "--json", "scheduler", "run-start", "review",
            "--idempotency-key", str(race_claim["idempotency_key"]), "--claim-token", str(race_claim["claim_token"]),
            "--task-id", "race-child-task",
        ]
        first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_out, first_err = first.communicate(timeout=10)
        second_out, second_err = second.communicate(timeout=10)
        self.assertEqual(sorted([first.returncode, second.returncode]), [0, 2], first_err + second_err)
        successful = json.loads(first_out if first.returncode == 0 else second_out)
        self.cli("scheduler", "run-finish", successful["run_id"], "--status", "succeeded", "--summary", "Race winner completed")
        registration_path = self.root / ".continuity" / "private" / "scheduler-registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration["last_heartbeat_at"] = "2020-01-01T00:00:00-06:00"
        self.write_json(registration_path, registration)
        self.assertEqual(json.loads(self.cli("scheduler", "status").stdout)["state"], "stale")
        self.cli(
            "portfolio", "actions", "--root", self.temp.name, "--action", "report",
            "--at", "2026-07-20T07:30:00-05:00", "--supervisor-task-id", "supervisor-fixture",
            "--sweep-id", "sweep-revive",
        )
        self.assertEqual(json.loads(self.cli("scheduler", "status").stdout)["state"], "registered")

    def test_subject_specific_workflow_handoffs_override_project_queue_priority(self) -> None:
        planning_capture = self.create_capture()
        planning_note_id = planning_capture["items"][3]["item_id"]
        self.cli(
            "note", "triage", planning_capture["capture_id"], planning_note_id,
            "--kind", "execution-candidate", "--action", "route",
        )
        subject_payload = {
            "source_type": "conversation",
            "source_ref": "thread:subject-handoff",
            "items": [{"kind": "context", "text": "Preserve the current review ordering."}],
        }
        subject_path = self.root / "subject-capture.json"
        self.write_json(subject_path, subject_payload)
        subject_capture = json.loads(self.cli("note", "capture", "--items-file", str(subject_path)).stdout)
        subject_note_id = subject_capture["items"][0]["item_id"]

        project_status = json.loads(self.cli("workflow", "status").stdout)
        self.assertEqual(project_status["next_skill"], "continuity-plan")
        capture_status = json.loads(
            self.cli("workflow", "status", "--capture-id", subject_capture["capture_id"]).stdout
        )["capture"]
        self.assertEqual(capture_status["next_skill"], "continuity-triage")
        self.assertEqual(capture_status["handoff"]["subject_ids"]["note_ids"], [subject_note_id])

        note_status = json.loads(self.cli("workflow", "status", "--note-id", subject_note_id).stdout)["note"]
        self.assertEqual(note_status["current_stage"], "capture-review")
        self.assertEqual(note_status["next_skill"], "continuity-triage")
        self.assertFalse(note_status["handoff"]["authorization"]["execution_authorized"])
        self.assertEqual(note_status["handoff"]["evidence"]["occurred_at_confidence"], "capture-time")

        self.cli(
            "note", "triage", subject_capture["capture_id"], subject_note_id,
            "--kind", "context", "--action", "route", "--occurred-at-confidence", "approximate",
        )
        routed = json.loads(self.cli("workflow", "status", "--note-id", subject_note_id).stdout)["note"]
        self.assertEqual(routed["current_stage"], "knowledge-ready")
        self.assertEqual(routed["next_skill"], "continuity-memory")
        self.assertEqual(routed["handoff"]["evidence"]["occurred_at_confidence"], "approximate")

        handoff_schema = json.loads((SUITE / "schemas" / "workflow-handoff.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(set(handoff_schema["required"]).issubset(routed["handoff"]))
        self.assertTrue(set(handoff_schema["properties"]["authorization"]["required"]).issubset(routed["handoff"]["authorization"]))

        memory = json.loads(self.cli("workflow", "status", "--memory-id", "memory-current").stdout)["memory"]
        self.assertEqual(memory["current_stage"], "memory-current")
        self.assertEqual(memory["next_skill"], "continuity-plan")
        historical = json.loads(self.cli("workflow", "status", "--memory-id", "memory-history").stdout)["memory"]
        self.assertEqual(historical["next_skill"], "continuity-memory")
        self.assertTrue(historical["blockers"])

        self.write_roadmap("objective-reference", "Reference objective", "program", "active")
        roadmap = json.loads(self.cli("workflow", "status", "--roadmap-id", "objective-reference").stdout)["roadmap"]
        self.assertEqual(roadmap["next_skill"], "continuity-plan")
        self.assertEqual(roadmap["handoff"]["subject_ids"]["roadmap_id"], "objective-reference")

        packet = json.loads(
            self.cli(
                "note", "share", "prepare", subject_note_id,
                "--target-project", "test-project", "--sender", "fixture",
            ).stdout
        )
        packet_status = json.loads(self.cli("workflow", "status", "--packet-id", packet["packet_id"]).stdout)["packet"]
        self.assertEqual(packet_status["state"], "prepared")
        self.assertEqual(packet_status["handoff"]["human_requirements"], ["approve-packet"])
        self.cli(
            "note", "share", "approve", packet["packet_id"], "--version", str(packet["version"]),
            "--approved-by", "fixture",
            "--authorization-text", f"Approve {packet['packet_id']} version {packet['version']} for test-project",
        )
        approved_packet = json.loads(self.cli("workflow", "status", "--packet-id", packet["packet_id"]).stdout)["packet"]
        self.assertEqual(approved_packet["state"], "approved")
        self.assertEqual({action["disposition"] for action in approved_packet["allowed_actions"]}, {"publish-packet"})

    def test_machine_shaped_reference_examples_are_accepted_by_the_cli(self) -> None:
        capture_example = SUITE / "skills" / "continuity-capture" / "references" / "capture-input.example.json"
        capture = json.loads(self.cli("note", "capture", "--items-file", str(capture_example)).stdout)
        self.assertEqual(len(capture["items"]), 2)
        self.assertEqual(capture["items"][0]["occurred_at_confidence"], "exact")
        self.assertEqual(capture["items"][1]["occurred_at_confidence"], "capture-time")
        self.assertTrue(all(item["execution_authorized"] is False for item in capture["items"]))

        goal_example = SUITE / "skills" / "continuity-plan" / "references" / "goal-input.example.json"
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(goal_example)).stdout)
        self.assertEqual(goal["state"], "awaiting-feedback")
        self.assertFalse(goal["triage_brief"]["execution_authorized"])
        self.assertFalse(goal["decision_map"]["execution_authorized"])
        self.assertEqual(goal["delivery_slices"][0]["status"], "planning-candidate")
        status = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual(status["handoff"]["subject_ids"]["goal_id"], goal["goal_id"])
        self.assertIn("approve", status["handoff"]["human_requirements"])

    def test_note_lifecycle_dispositions_relationships_and_dated_stages(self) -> None:
        capture = self.create_capture()
        current_note, later_note, context_note, duplicate_note = (
            capture["items"][3], capture["items"][2], capture["items"][0], capture["items"][1]
        )
        for item in capture["items"]:
            action = "promote" if item["item_id"] == current_note["item_id"] else "route"
            self.cli("note", "triage", capture["capture_id"], item["item_id"], "--action", action)
        payload = {
            "goal_id": "goal-note-lifecycle",
            "title": "Preserve the preload bridge lifecycle",
            "scope": "Implement the approved preload bridge lifecycle behavior.",
            "acceptance_criteria": ["The bridge lifecycle remains explicit"],
            "memory_ids": ["memory-current"],
            "source_note_ids": [item["item_id"] for item in capture["items"]],
            "note_dispositions": [
                {"note_id": current_note["item_id"], "disposition": "current-goal", "reason": "Defines the current outcome.", "delivery_slice_ids": ["slice-lifecycle"]},
                {"note_id": later_note["item_id"], "disposition": "later", "reason": "Belongs in a later planning pass.", "delivery_slice_ids": [], "review_after": "2030-01-02T09:00:00-06:00"},
                {"note_id": context_note["item_id"], "disposition": "context-only", "reason": "Planning context, not delivery scope.", "delivery_slice_ids": []},
                {"note_id": duplicate_note["item_id"], "disposition": "duplicate", "reason": "Represented by the canonical instruction.", "delivery_slice_ids": [], "canonical_note_id": current_note["item_id"]},
            ],
            "delivery_slices": [
                {"ticket_id": "slice-lifecycle", "title": "Preserve lifecycle behavior", "delivers": "The explicit bridge lifecycle behavior.", "acceptance_criteria": ["Lifecycle behavior is verified"], "blocked_by": []}
            ],
            "plan_reviewed": True,
        }
        goal_path = self.root / "goal-note-lifecycle.json"
        self.write_json(goal_path, payload)
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(goal_path)).stdout)
        plan = (self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "plan.md").read_text(encoding="utf-8")
        self.assertIn("Note dispositions", plan)
        self.assertIn("review after: 2030-01-02T09:00:00-06:00", plan)

        statuses = {
            item["item_id"]: json.loads(self.cli("workflow", "status", "--note-id", item["item_id"]).stdout)["note"]
            for item in capture["items"]
        }
        self.assertEqual(statuses[current_note["item_id"]]["lifecycle"]["current_stage"], "plan-review")
        self.assertEqual(statuses[current_note["item_id"]]["lifecycle"]["summary_status"], "planned")
        self.assertEqual(statuses[later_note["item_id"]]["lifecycle"]["current_stage"], "planned-later")
        self.assertEqual(statuses[later_note["item_id"]]["lifecycle"]["summary_status"], "deferred")
        self.assertEqual(statuses[context_note["item_id"]]["lifecycle"]["current_stage"], "context-only")
        self.assertEqual(statuses[duplicate_note["item_id"]]["lifecycle"]["current_stage"], "duplicate")
        self.assertTrue(statuses[current_note["item_id"]]["lifecycle"]["stage_entered_at"])

        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.cli("run", "update", goal["goal_id"], "--state", "running", "--branch", "continuity/note-lifecycle")
        running = json.loads(self.cli("workflow", "status", "--note-id", current_note["item_id"]).stdout)["note"]
        self.assertEqual(running["lifecycle"]["current_stage"], "implementation")
        self.assertEqual(running["lifecycle"]["summary_status"], "running")
        timeline_stages = {item["stage"] for item in running["lifecycle"]["timeline"]}
        self.assertTrue({"triage-needed", "plan-review", "dispatch-ready", "execution-start", "implementation"}.issubset(timeline_stages))
        later_running = json.loads(self.cli("workflow", "status", "--note-id", later_note["item_id"]).stdout)["note"]
        self.assertEqual(later_running["lifecycle"]["current_stage"], "planned-later")

        related_payload = {
            "source_type": "conversation",
            "source_ref": "thread:related-goal",
            "items": [{"item_id": "note-related-lifecycle", "kind": "execution-candidate", "text": "Preserve the preload bridge lifecycle and implement the approved explicit bridge lifecycle behavior."}],
        }
        related_path = self.root / "related-note.json"
        self.write_json(related_path, related_payload)
        related_capture = json.loads(self.cli("note", "capture", "--items-file", str(related_path)).stdout)
        related_id = related_capture["items"][0]["item_id"]
        self.cli("note", "triage", related_capture["capture_id"], related_id, "--action", "promote")
        candidates = json.loads(self.cli("note", "related-goals", related_id, "--min-score", "0").stdout)
        self.assertEqual(candidates[0]["goal_id"], goal["goal_id"])
        default_candidates = json.loads(self.cli("note", "related-goals", related_id).stdout)
        self.assertTrue(default_candidates, candidates)
        self.assertFalse(default_candidates[0]["already_linked"], default_candidates)
        unlinked = json.loads(self.cli("workflow", "status", "--note-id", related_id).stdout)["note"]
        self.assertEqual(unlinked["lifecycle"]["planning_disposition"], "not-considered")
        self.assertTrue(unlinked["lifecycle"]["relationship_candidates"], unlinked)
        morning = json.loads(self.cli("report", "morning").stdout)
        self.assertIn(
            related_id,
            {item["note_id"] for item in morning["note_lifecycle"]["unconfirmed_relationships"]},
            morning["note_lifecycle"],
        )
        self.assertGreaterEqual(morning["note_lifecycle"]["stage_counts"]["implementation"], 1)
        related = json.loads(
            self.cli(
                "note", "relate", related_id, "--goal-id", goal["goal_id"], "--disposition", "context-only",
                "--reason", "Related context outside approved scope.", "--actor", "fixture-user",
            ).stdout
        )
        self.assertEqual(related["lifecycle"]["planning_disposition"], "context-only")
        self.assertFalse(related["execution_authorized"])
        self.assertFalse(
            {"dispatch-ready", "execution-start", "implementation"}.intersection(
                event["stage"] for event in related["lifecycle"]["timeline"]
            ),
            related["lifecycle"]["timeline"],
        )
        stored_goal = json.loads((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json").read_text(encoding="utf-8"))
        self.assertNotIn(related_id, stored_goal["source_note_ids"])
        due = json.loads(
            self.cli(
                "note", "relate", related_id, "--goal-id", goal["goal_id"], "--disposition", "later",
                "--reason", "Review in a later planning pass.", "--review-after", "2020-01-01T09:00:00-06:00",
                "--actor", "fixture-user",
            ).stdout
        )
        self.assertEqual(due["lifecycle"]["current_stage"], "planning-ready")
        self.assertEqual(due["lifecycle"]["summary_status"], "open")

    def test_note_dispositions_fail_closed_and_legacy_records_require_explicit_migration(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        base = {
            "goal_id": "goal-disposition-validation",
            "title": "Validate note dispositions",
            "scope": "Validate explicit note planning decisions.",
            "acceptance_criteria": ["Invalid note decisions fail closed"],
            "source_note_ids": [note_id],
        }
        path = self.root / "goal-disposition-validation.json"
        self.write_json(path, {**base, "note_dispositions": [{"note_id": note_id, "disposition": "later", "reason": "Later work", "delivery_slice_ids": []}]})
        self.cli("goal", "create", "--goal-file", str(path), expected=2)
        self.write_json(path, {**base, "source_note_ids": ["missing-note"], "note_dispositions": [{"note_id": "missing-note", "disposition": "current-goal", "reason": "Invalid source", "delivery_slice_ids": []}]})
        self.cli("goal", "create", "--goal-file", str(path), expected=2)
        self.write_json(path, base)
        self.cli("goal", "create", "--goal-file", str(path), expected=2)
        self.write_json(
            path,
            {
                **base,
                "note_dispositions": [
                    {
                        "note_id": note_id,
                        "disposition": "current-goal",
                        "reason": "Explicitly included in the current goal.",
                        "delivery_slice_ids": [],
                    }
                ],
            },
        )
        created = json.loads(self.cli("goal", "create", "--goal-file", str(path)).stdout)
        self.assertFalse(created["note_dispositions"][0]["execution_authorized"])
        goal_path = self.root / ".continuity" / "private" / "goals" / created["goal_id"] / "goal.json"
        legacy = json.loads(goal_path.read_text(encoding="utf-8"))
        legacy.pop("note_dispositions")
        self.write_json(goal_path, legacy)
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertIn(created["goal_id"], doctor["legacy_note_disposition_goal_ids"])
        readable = json.loads(self.cli("workflow", "status", "--note-id", note_id).stdout)["note"]
        self.assertEqual(readable["lifecycle"]["planning_disposition"], "current-goal")
        revision = self.root / "normalize-note-dispositions.json"
        self.write_json(
            revision,
            {
                "note_dispositions": [
                    {
                        "note_id": note_id,
                        "disposition": "later",
                        "reason": "Move the note to a dated later pass.",
                        "delivery_slice_ids": [],
                        "review_after": "2030-02-01T09:00:00-06:00",
                    }
                ]
            },
        )
        migrated = json.loads(
            self.cli(
                "goal", "revise", created["goal_id"], "--goal-file", str(revision),
                "--author", "fixture-user", "--summary", "Normalize legacy note dispositions",
            ).stdout
        )
        self.assertEqual(migrated["note_dispositions"][0]["disposition"], "later")
        self.assertNotEqual(migrated["plan_hash"], created["plan_hash"])

    def test_note_timeline_is_bound_to_relationship_plan_version(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        self.cli("note", "triage", capture["capture_id"], note_id, "--action", "promote")
        goal = self.create_goal("Timeline provenance", [note_id])
        revision_path = self.root / "timeline-revision.json"
        self.write_json(
            revision_path,
            {
                "scope": "Implement the explicitly revised bridge safety outcome.",
                "note_dispositions": [
                    {
                        "note_id": note_id,
                        "disposition": "current-goal",
                        "reason": "The note remains explicit scope in plan version two.",
                        "delivery_slice_ids": [],
                    }
                ],
            },
        )
        revised = json.loads(
            self.cli(
                "goal", "revise", goal["goal_id"], "--goal-file", str(revision_path),
                "--author", "fixture-user", "--summary", "Clarify the approved scope",
            ).stdout
        )
        self.assertEqual(revised["plan_version"], 2)
        lifecycle = json.loads(self.cli("workflow", "status", "--note-id", note_id).stdout)["note"]["lifecycle"]
        goal_events = [event for event in lifecycle["timeline"] if event.get("goal_id") == goal["goal_id"]]
        lifecycle_events = [event for event in goal_events if event["event"].startswith(("goal.", "run.", "test.", "merge."))]
        self.assertNotIn("goal.created", {event["event"] for event in lifecycle_events})
        self.assertIn("goal.revised", {event["event"] for event in lifecycle_events})
        self.assertTrue(all(event["plan_version"] == 2 for event in lifecycle_events), lifecycle_events)

    def test_note_lifecycle_preserves_multiple_goal_tracks_without_flattening(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        self.cli("note", "triage", capture["capture_id"], note_id, "--action", "promote")
        active = self.create_goal("Active note track", [note_id])
        self.approve(active)
        self.cli("goal", "start", active["goal_id"])
        self.cli("run", "update", active["goal_id"], "--state", "running", "--branch", "continuity/active-note-track")
        waiting = self.create_goal("Waiting note track", [note_id])
        lifecycle = json.loads(self.cli("workflow", "status", "--note-id", note_id).stdout)["note"]["lifecycle"]
        self.assertEqual(lifecycle["summary_status"], "running")
        self.assertEqual(lifecycle["current_stage"], "multi-goal")
        tracks = {track["goal_id"]: track for track in lifecycle["goal_tracks"]}
        self.assertEqual(tracks[active["goal_id"]]["current_stage"], "implementation")
        self.assertEqual(tracks[waiting["goal_id"]]["current_stage"], "plan-review")

    def test_signed_approval_is_verified_and_tampering_fails_closed(self) -> None:
        key = self.root.parent / "approver"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["require_signed_approvals"] = True
        config["approval_allowed_signers"] = ".continuity/trusted-approvers"
        self.write_json(self.root / ".continuity" / "config.json", config)
        trusted = json.loads(
            self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub").stdout
        )
        self.assertEqual(trusted["identity"], "fixture-user")
        goal = self.create_goal("Signed authority")
        approval = json.loads(
            self.cli(
                "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
                "--authorization-text", f"Approve {goal['goal_id']} plan v1", "--signing-key", str(key),
            ).stdout
        )["approval"]
        self.assertEqual(approval["signature_format"], "openssh-sshsig-v1")
        verified = json.loads(self.cli("approval", "verify", goal["goal_id"]).stdout)
        self.assertTrue(verified["verified"])
        approval_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "approval.json"
        tampered = json.loads(approval_path.read_text(encoding="utf-8"))
        tampered["authorization_text"] += " altered"
        self.write_json(approval_path, tampered)
        self.cli("goal", "start", goal["goal_id"], expected=2)

    def test_trusted_approvers_must_match_fetched_integration_branch(self) -> None:
        key = self.root.parent / "anchored-approver"
        other_key = self.root.parent / "unanchored-approver"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(other_key)], check=True)
        remote = self.root.parent / "approval-remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "main")
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config.update({"require_remote": True, "require_signed_approvals": True, "approval_allowed_signers": ".continuity/trusted-approvers"})
        self.write_json(self.root / ".continuity" / "config.json", config)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        self.git("add", ".continuity/config.json", ".continuity/trusted-approvers")
        self.git("commit", "-m", "anchor trusted approver")
        self.git("push", "origin", "main")
        goal = self.create_goal("Anchored authority")
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", "--signing-key", str(key),
        )
        self.assertTrue(json.loads(self.cli("approval", "verify", goal["goal_id"]).stdout)["verified"])
        self.cli("approval", "trust", "add", "--identity", "unreviewed-user", "--public-key", str(other_key) + ".pub")
        self.cli("approval", "verify", goal["goal_id"], expected=2)

    def test_rework_requires_signed_human_disposition_and_resume_receipt(self) -> None:
        key = self.root.parent / "disposition-approver"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config.update({"require_signed_approvals": True, "approval_allowed_signers": ".continuity/trusted-approvers"})
        self.write_json(self.root / ".continuity" / "config.json", config)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        goal = self.create_goal("Signed rework")
        self.cli(
            "goal", "approve", goal["goal_id"], "--version", "1", "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {goal['goal_id']} plan v1", "--signing-key", str(key),
        )
        goal_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json"
        current = json.loads(goal_path.read_text(encoding="utf-8"))
        current["state"] = "review-ready"
        self.write_json(goal_path, current)
        command = (
            "merge", "record-human", goal["goal_id"], "--pr-url", "https://github.com/example/project/pull/8",
            "--merged-by", "fixture-user", "--disposition", "changes-requested", "--evidence", "Revise in-scope copy.",
        )
        self.cli(*command, expected=2)
        self.cli(*command, "--signing-key", str(key))
        archived = goal_path.parent / "attempts" / "attempt-1"
        self.assertTrue((archived / "human-review.sig").is_file())
        resume_text = f"Resume {goal['goal_id']} under approved plan v1"
        self.cli("goal", "resume", goal["goal_id"], "--actor", "fixture-user", "--authorization-text", resume_text, expected=2)
        resumed = json.loads(self.cli("goal", "resume", goal["goal_id"], "--actor", "fixture-user", "--authorization-text", resume_text, "--signing-key", str(key)).stdout)
        self.assertEqual(resumed["state"], "queued")
        receipt = json.loads((goal_path.parent / "resume-authorization.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["execution_attempt"], 2)
        self.assertTrue((goal_path.parent / "resume-authorization.sig").is_file())

    def test_signed_shared_packet_approval_is_verified_before_publish(self) -> None:
        key = self.root.parent / "packet-approver"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["require_signed_approvals"] = True
        config["approval_allowed_signers"] = ".continuity/trusted-approvers"
        self.write_json(self.root / ".continuity" / "config.json", config)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        capture = self.create_capture()
        prepared = json.loads(
            self.cli(
                "note", "share", "prepare", capture["items"][0]["item_id"],
                "--target-project", "test-project", "--sender", "fixture-user",
            ).stdout
        )
        self.cli(
            "note", "share", "approve", prepared["packet_id"], "--version", str(prepared["version"]),
            "--approved-by", "fixture-user",
            "--authorization-text", f"Approve {prepared['packet_id']} version {prepared['version']} for test-project",
            "--signing-key", str(key),
        )
        published = json.loads(self.cli("note", "share", "publish", prepared["packet_id"], "--dry-run").stdout)
        self.assertTrue(published["dry_run"])
        packet_path = self.root / prepared["private_path"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet["approval"]["authorization_text"] += " altered"
        self.write_json(packet_path, packet)
        status = json.loads(self.cli("workflow", "status", "--packet-id", prepared["packet_id"]).stdout)["packet"]
        self.assertFalse(status["approval_current"])
        self.assertTrue(status["blockers"])
        self.cli("note", "share", "publish", prepared["packet_id"], "--dry-run", expected=2)

    def test_private_jsonl_tampering_is_detected_by_doctor(self) -> None:
        self.create_capture()
        ledger = self.root / ".continuity" / "private" / "events.jsonl"
        text = ledger.read_text(encoding="utf-8")
        self.assertIn("sha256-chain-v1", text)
        tampered = text.replace("capture.created", "capture.changed", 1)
        self.assertNotEqual(tampered, text)
        ledger.write_text(tampered, encoding="utf-8")
        with self.assertRaises(runtime_lib.RuntimeIntegrityError):
            runtime_lib.append_integrity_jsonl(ledger, {"event": "capture.retry"})
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertFalse(doctor["healthy"])
        self.assertTrue(any("record hash mismatch" in problem for problem in doctor["problems"]))

    def test_doctor_requires_named_hosted_checks_before_pr_execution(self) -> None:
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["require_pr"] = True
        config["github_required_checks"] = []
        self.write_json(self.root / ".continuity" / "config.json", config)
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertFalse(doctor["healthy"])
        self.assertIn("execution is enabled but no required GitHub checks are configured", doctor["problems"])

    def test_remote_lease_ref_serializes_workstations_without_force_push(self) -> None:
        goal = self.create_goal("Lease serialization")
        self.approve(goal)
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["require_remote_lease"] = True
        self.write_json(self.root / ".continuity" / "config.json", config)
        remote = self.root.parent / "remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "main")
        self.cli("goal", "start", goal["goal_id"], expected=2)
        acquired = json.loads(
            self.cli("scheduler", "lease", "acquire", "--owner", "operator-one", "--goal-id", goal["goal_id"], "--remote", "origin").stdout
        )
        self.assertEqual(acquired["status"], "active")
        self.cli("scheduler", "lease", "acquire", "--owner", "operator-two", "--goal-id", goal["goal_id"], "--remote", "origin", expected=2)
        dispatched = json.loads(self.cli("goal", "start", goal["goal_id"]).stdout)
        self.assertEqual(dispatched["remote_lease"]["attempt_id"], "1")
        runtime_lib.append_integrity_jsonl(
            self.root / ".continuity" / "private" / "scheduler-runs.jsonl",
            {
                "schema_version": 1, "run_id": "run-review", "project_id": "test-project",
                "action": "review", "status": "started", "at": "2026-07-15T10:00:00-05:00",
                "idempotency_key": "test-project:review:2026-07-15", "attempt": 1,
                "task_id": "review-task", "goal_id": None, "summary": "Review started.",
            },
        )
        self.cli("scheduler", "run-finish", "run-review", "--status", "succeeded", "--summary", "Review complete.")
        still_active = json.loads((self.root / ".continuity" / "private" / "remote-lease.json").read_text(encoding="utf-8"))
        self.assertEqual(still_active["status"], "active")
        self.cli("scheduler", "lease", "release", "--reason", "wrong binding", "--goal-id", "goal-other", "--attempt-id", "1", expected=2)
        active = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(active["state"], "active")
        released = json.loads(self.cli("scheduler", "lease", "release", "--reason", "pilot complete", "--goal-id", goal["goal_id"], "--attempt-id", "1").stdout)
        self.assertEqual(released["status"], "released")
        available = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(available["state"], "available")

    def test_encrypted_state_backup_verifies_and_restores_through_staging(self) -> None:
        fake_bin = self.root.parent / "fake-age-bin"
        fake_bin.mkdir()
        fake_age = fake_bin / "age"
        fake_age.write_text(
            "#!/usr/bin/env python3\nimport shutil, sys\nout = sys.argv[sys.argv.index('-o') + 1]\nshutil.copyfile(sys.argv[-1], out)\n",
            encoding="utf-8",
        )
        fake_age.chmod(0o755)
        identity = self.root.parent / "age-identity.txt"
        identity.write_text("fixture identity\n", encoding="utf-8")
        signer_key = self.root.parent / "backup-signer"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(signer_key)], check=True)
        self.cli("approval", "trust", "add", "--identity", "fixture-backup", "--public-key", str(signer_key) + ".pub")
        archive = self.root.parent / "state.tar.gz.age"
        original_path = os.environ.get("PATH", "")
        original_home = os.environ.get("HOME")
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        os.environ["HOME"] = str(self.root.parent)
        try:
            first = self.create_capture()
            backed_up = json.loads(self.cli("state", "backup", "--recipient", "age1fixture", "--signer", "fixture-backup", "--signing-key", str(signer_key), "--verify-identity", str(identity), "--output", str(archive)).stdout)
            self.assertTrue(backed_up["encrypted"])
            self.assertTrue(backed_up["verification"]["verified"])
            verified = json.loads(self.cli("state", "verify", "--archive", str(archive), "--identity", str(identity)).stdout)
            self.assertTrue(verified["verified"])
            second = json.loads(self.cli("note", "capture", "--text", "Created after backup.").stdout)
            dry_run = json.loads(self.cli("state", "restore", "--archive", str(archive), "--identity", str(identity), "--recipient", "age1fixture", "--signer", "fixture-backup", "--signing-key", str(signer_key), "--dry-run").stdout)
            self.assertTrue(dry_run["dry_run"])
            restored = json.loads(self.cli("state", "restore", "--archive", str(archive), "--identity", str(identity), "--recipient", "age1fixture", "--signer", "fixture-backup", "--signing-key", str(signer_key)).stdout)
            self.assertTrue(restored["restored"])
            notes = json.loads(self.cli("note", "list").stdout)
            self.assertIn(first["items"][0]["item_id"], {item["item_id"] for item in notes})
            self.assertNotIn(second["items"][0]["item_id"], {item["item_id"] for item in notes})
        finally:
            os.environ["PATH"] = original_path
            if original_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original_home

    def test_backup_requires_quiescence_and_external_checkpoint_detects_rewrite(self) -> None:
        goal = self.create_goal("Quiescence guard")
        goal_path = self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json"
        active = json.loads(goal_path.read_text(encoding="utf-8"))
        active["state"] = "running"
        self.write_json(goal_path, active)
        blocked = self.cli(
            "state", "backup", "--recipient", "age1fixture", "--signer", "fixture-user",
            "--signing-key", str(self.root.parent / "missing-key"), expected=2,
        )
        self.assertIn("requires quiescent project state", blocked.stderr)
        active["state"] = "awaiting-feedback"
        self.write_json(goal_path, active)

        key = self.root.parent / "checkpoint-signer"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        self.create_capture()
        checkpoint_path = self.root.parent / "external-audit-checkpoint.json"
        created = json.loads(
            self.cli(
                "state", "checkpoint-create", "--signer", "fixture-user", "--signing-key", str(key),
                "--output", str(checkpoint_path),
            ).stdout
        )
        self.assertTrue(created["verified"])
        self.assertTrue(json.loads(self.cli("state", "checkpoint-verify", "--checkpoint", str(checkpoint_path)).stdout)["verified"])
        ledger = self.root / ".continuity" / "private" / "events.jsonl"
        ledger.unlink()
        runtime_lib.append_integrity_jsonl(ledger, {"at": "2026-07-15T10:00:00-05:00", "event": "history.rewritten"})
        self.cli("state", "checkpoint-verify", "--checkpoint", str(checkpoint_path), expected=2)

    def test_codex_adapter_and_sanitized_portfolio_report_are_machine_bounded(self) -> None:
        key = self.root.parent / "adapter-probe-signer"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        config["scheduler"] = {
            "provider": "codex", "sweep_minutes": 15, "business_days": [0, 1, 2, 3, 4],
            "retry_limit": 2, "retry_backoff_minutes": 15, "stale_after_minutes": 45,
            "portfolio_max_concurrency": 1,
        }
        config["require_signed_approvals"] = True
        config["approval_allowed_signers"] = ".continuity/trusted-approvers"
        self.write_json(self.root / ".continuity" / "config.json", config)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        manifest_path = self.root / ".continuity" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["scheduler"] = config["scheduler"]
        manifest["agent_surfaces"] = {"primary": "codex", "enabled": ["codex"]}
        self.write_json(manifest_path, manifest)
        rendered = json.loads(self.cli("scheduler", "adapter", "codex", "render", "--root", str(self.root.parent)).stdout)
        self.assertEqual(rendered["provider"], "codex")
        self.assertIn("portfolio actions", rendered["prompt"])
        private = self.root / ".continuity" / "private"
        self.write_json(
            private / "scheduler-registration.json",
            {
                "schema_version": 1, "provider": "codex", "registered_at": "2099-07-15T09:00:00-05:00",
                "last_heartbeat_at": "2099-07-15T09:30:00-05:00", "last_sweep_id": "sweep-two",
                "registered_by": "fixture", "supervisor_task_id": "codex-supervisor",
                "workspace_roots": [str(self.root.parent)], "behavior_configuration_hash": config.get("behavior_configuration_hash"),
                "sweep_minutes": 15, "supervisor_prompt": ".agents/continuity/automation/portfolio-supervisor.md",
            },
        )
        for sweep in ("sweep-one", "sweep-two"):
            runtime_lib.append_integrity_jsonl(
                private / "events.jsonl",
                {"at": "2099-07-15T09:30:00-05:00", "event": "scheduler.supervisor-heartbeat", "sweep_id": sweep},
            )
        runtime_lib.append_integrity_jsonl(
            private / "scheduler-runs.jsonl",
            {
                "schema_version": 1, "run_id": "run-no-op", "project_id": "test-project", "action": "report",
                "status": "succeeded", "at": "2099-07-15T09:31:00-05:00", "idempotency_key": "report-no-op",
                "attempt": 1, "task_id": "report-task", "goal_id": None, "summary": "No work required.",
            },
        )
        before_probes = json.loads(self.cli("scheduler", "adapter", "codex", "verify").stdout)
        self.assertFalse(before_probes["healthy"])
        self.assertTrue(any("missing observed conformance probe" in problem for problem in before_probes["problems"]))
        for probe in ("claim-replay-rejected", "stale-registration-rejected", "remote-lease-contention-rejected"):
            self.cli(
                "scheduler", "adapter", "codex", "record-probe", "--probe", probe, "--status", "passed",
                "--evidence", f"Observed {probe} in isolated provider test.", "--artifact-sha256", "a" * 64,
                "--actor", "fixture-user", "--signing-key", str(key),
            )
        conformance = json.loads(self.cli("scheduler", "adapter", "codex", "verify").stdout)
        self.assertTrue(conformance["healthy"], conformance)
        self.cli("note", "capture", "--text", "Private customer token should never enter portfolio output.")
        portfolio = subprocess.run(
            ["python3", str(CLI), "--json", "portfolio", "report", "--sanitized", "--root", str(self.root.parent)],
            capture_output=True, text=True, check=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        ).stdout
        payload = json.loads(portfolio)
        self.assertEqual(payload["sanitization_policy"], "continuity-portfolio-allowlist-v1")
        self.assertNotIn("Private customer", portfolio)
        self.assertNotIn(str(self.root), portfolio)


class ReferenceTest(unittest.TestCase):
    def test_skill_references_are_nonempty_linked_and_resolvable(self) -> None:
        skills_root = SUITE / "skills"
        shared_references = {
            "workflow-handoffs.md",
            "decision-lenses.md",
            "output-quality-rubrics.md",
            "worked-lifecycle-example.md",
        }
        self.assertTrue(shared_references.issubset({path.name for path in (SUITE / "references").glob("*.md")}))

        for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            skill_text = skill_file.read_text(encoding="utf-8")
            self.assertIn("../../references/workflow-handoffs.md", skill_text, skill_dir.name)
            self.assertIn("../../references/output-quality-rubrics.md", skill_text, skill_dir.name)

            linked_targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", skill_text)
            for target in linked_targets:
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (skill_file.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.is_file(), f"{skill_dir.name} has broken reference link: {target}")
                self.assertGreater(len(resolved.read_text(encoding="utf-8").strip()), 100, str(resolved))

            if skill_dir.name == "continuity":
                continue
            local_references = sorted(path for path in (skill_dir / "references").iterdir() if path.is_file())
            self.assertTrue(local_references, f"{skill_dir.name} requires an applied reference")
            for reference in local_references:
                self.assertIn(f"references/{reference.name}", skill_text, f"{reference} is not linked from SKILL.md")


class InstallerTest(unittest.TestCase):
    def test_installer_signed_approval_opt_in_creates_trust_store(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            subprocess.run(
                [
                    "python3",
                    str(INSTALLER),
                    "--project-root",
                    str(root),
                    "--project-id",
                    "signed-project",
                    "--integration-branch",
                    "main",
                    "--ignore-user-defaults",
                    "--require-signed-approvals",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(config["require_signed_approvals"])
            self.assertTrue((root / ".continuity" / "trusted-approvers").is_file())

    def test_installer_rolls_back_every_fault_injection_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            command = [
                "python3", str(INSTALLER), "--project-root", str(root), "--project-id", "transaction-project",
                "--integration-branch", "main", "--ignore-user-defaults",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            agents = root / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\nUser-owned marker.\n", encoding="utf-8")
            custom_cursor = root / ".cursor" / "commands" / "custom.md"
            custom_cursor.parent.mkdir(parents=True, exist_ok=True)
            custom_cursor.write_text("user-owned cursor command\n", encoding="utf-8")
            baseline_agents = agents.read_bytes()
            baseline_config = (root / ".continuity" / "config.json").read_bytes()
            for stage in ("managed-files", "project-contract", "seed-content", "surface-configuration", "install-manifest"):
                failed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "CONTINUITY_INSTALL_FAIL_AFTER": stage},
                )
                self.assertNotEqual(failed.returncode, 0, stage)
                self.assertEqual(agents.read_bytes(), baseline_agents, stage)
                self.assertEqual((root / ".continuity" / "config.json").read_bytes(), baseline_config, stage)
                self.assertEqual(custom_cursor.read_text(encoding="utf-8"), "user-owned cursor command\n", stage)

    def test_installer_detects_managed_drift_and_supports_snapshot_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            command = [
                "python3", str(INSTALLER), "--project-root", str(root), "--project-id", "upgrade-project",
                "--integration-branch", "main", "--ignore-user-defaults",
            ]
            first = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
            self.assertEqual(first["suite_version"], "0.1.0-rc.1")
            install_manifest = json.loads((root / ".continuity" / "install-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(install_manifest["installed_files"])
            installed_cli = root / ".agents" / "continuity" / "bin" / "continuity"
            installed_cli.write_text(installed_cli.read_text(encoding="utf-8") + "\n# local drift\n", encoding="utf-8")
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("Suite-managed file drift detected", rejected.stderr)
            overwritten = json.loads(subprocess.run([*command, "--overwrite-managed"], check=True, capture_output=True, text=True).stdout)
            snapshot = overwritten["upgrade_snapshot"]
            self.assertNotIn("local drift", installed_cli.read_text(encoding="utf-8"))
            rollback = json.loads(
                subprocess.run(
                    ["python3", str(INSTALLER), "--project-root", str(root), "--rollback-snapshot", snapshot],
                    check=True, capture_output=True, text=True,
                ).stdout
            )
            self.assertTrue(rollback["restored"])
            self.assertIn("local drift", installed_cli.read_text(encoding="utf-8"))

    def test_installer_is_idempotent_and_creates_memory_and_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "AGENTS.md").write_text(
                "# Example project\n\n"
                "<!-- project-continuity:start -->\n"
                "legacy managed block\n"
                "<!-- project-continuity:end -->\n",
                encoding="utf-8",
            )
            (root / ".gitignore").write_text(
                ".DS_Store\n\n"
                "# project-continuity:start\n"
                ".agents/project-continuity/lib/__pycache__/\n"
                "# project-continuity:end\n",
                encoding="utf-8",
            )
            (root / ".agents" / "skills" / "project-continuity").mkdir(parents=True)
            (root / ".agents" / "skills" / "project-continuity" / "SKILL.md").write_text("legacy", encoding="utf-8")
            (root / ".agents" / "skills" / "manage-project-memory").mkdir(parents=True)
            (root / ".agents" / "skills" / "manage-project-memory" / "SKILL.md").write_text("legacy", encoding="utf-8")
            (root / ".agents" / "project-continuity" / "bin").mkdir(parents=True)
            (root / ".agents" / "project-continuity" / "bin" / "continuity").write_text("legacy", encoding="utf-8")
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
                "--ignore-user-defaults",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            config_after_first_install = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertFalse(config_after_first_install["require_signed_approvals"])
            self.assertFalse(config_after_first_install["github_cli_merge_enabled"])
            self.assertFalse((root / ".continuity" / "trusted-approvers").exists())
            legacy_behavior_path = root / ".continuity" / "project-behavior.json"
            legacy_behavior = json.loads(legacy_behavior_path.read_text(encoding="utf-8"))
            legacy_behavior["settings"].pop("github_cli_merge_enabled", None)
            legacy_behavior_path.write_text(json.dumps(legacy_behavior, indent=2) + "\n", encoding="utf-8")
            config_after_first_install.pop("github_cli_merge_enabled", None)
            custom_skill = root / ".agents" / "skills" / "project-custom-skill" / "SKILL.md"
            custom_skill.parent.mkdir(parents=True)
            custom_skill.write_text("---\nname: project-custom-skill\ndescription: user-owned fixture\n---\n", encoding="utf-8")
            installed_skill_names = {path.name for path in (root / ".agents" / "skills").iterdir() if path.is_dir()}
            shutil.rmtree(root / ".agents" / "skills" / "continuity-workflow")
            for command_root in (root / ".claude" / "commands", root / ".cursor" / "commands"):
                (command_root / "continuity-workflow.md").unlink(missing_ok=True)
            install_manifest_path = root / ".continuity" / "install-manifest.json"
            legacy_install_manifest = json.loads(install_manifest_path.read_text(encoding="utf-8"))
            for field in ("release_files", "installed_files"):
                legacy_install_manifest[field] = {
                    path: digest
                    for path, digest in legacy_install_manifest[field].items()
                    if "continuity-workflow" not in path
                }
            install_manifest_path.write_text(json.dumps(legacy_install_manifest, indent=2) + "\n", encoding="utf-8")
            config_after_first_install["require_signed_approvals"] = True
            (root / ".continuity" / "config.json").write_text(json.dumps(config_after_first_install, indent=2) + "\n", encoding="utf-8")
            (root / ".continuity" / "trusted-approvers").write_text(
                "# Add trusted SSH approvers with `continuity approval trust add`.\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    "python3", str(CLI), "--json", "portfolio", "update",
                    "--root", str(root.parent), "--source", str(SUITE),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            preview_payload = json.loads(preview_result.stdout)
            self.assertEqual(preview_payload["counts"]["planned"], 1, preview_payload)
            self.assertFalse((root / ".agents" / "skills" / "continuity-workflow").exists())
            update_result = subprocess.run(
                [
                    "python3", str(CLI), "--json", "portfolio", "update",
                    "--root", str(root.parent), "--source", str(SUITE), "--apply",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            update_payload = json.loads(update_result.stdout)
            self.assertEqual(update_payload["status"], "completed")
            self.assertEqual(update_payload["counts"]["updated"], 1)
            self.assertEqual(update_payload["projects"][0]["project_id"], "sample-project")
            self.assertTrue(update_payload["projects"][0]["after"]["healthy"])
            upgraded_config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            upgraded_behavior = json.loads(legacy_behavior_path.read_text(encoding="utf-8"))
            self.assertFalse(upgraded_config["github_cli_merge_enabled"])
            self.assertFalse(upgraded_behavior["settings"]["github_cli_merge_enabled"])
            self.assertTrue(installed_skill_names.issubset({path.name for path in (root / ".agents" / "skills").iterdir() if path.is_dir()}))
            self.assertTrue(custom_skill.is_file())
            self.assertTrue((root / ".agents" / "skills" / "continuity-workflow" / "SKILL.md").is_file())
            upgraded_doctor = subprocess.run(
                [str(root / ".agents" / "continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(json.loads(upgraded_doctor.stdout)["healthy"])
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("continuity:start"), 1)
            self.assertNotIn("project-continuity:start", agents)
            self.assertIn("Run manual end-to-end work through `$continuity-workflow`", agents)
            self.assertTrue((root / ".agents" / "skills" / "continuity" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-local" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-memory" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-roadmap" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-share" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-test" / "SKILL.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-merge" / "SKILL.md").exists())
            self.assertFalse((root / ".agents" / "skills" / "project-continuity").exists())
            self.assertFalse((root / ".agents" / "skills" / "manage-project-memory").exists())
            self.assertTrue((root / ".agents" / "continuity" / "bin" / "continuity").exists())
            self.assertTrue((root / ".agents" / "continuity" / "automation" / "nightly-review.md").exists())
            self.assertTrue((root / ".agents" / "continuity" / "automation" / "provider-adapter-contract.md").exists())
            self.assertFalse((root / ".agents" / "project-continuity").exists())
            for command_root in (root / ".claude" / "commands", root / ".cursor" / "commands"):
                self.assertTrue((command_root / "continuity-capture.md").exists())
                self.assertTrue((command_root / "continuity-triage.md").exists())
                self.assertTrue((command_root / "continuity-workflow.md").exists())
                command_text = (command_root / "continuity-capture.md").read_text(encoding="utf-8")
                self.assertIn("Slash command: `/continuity-capture`", command_text)
                self.assertIn(".agents/skills/continuity-capture/SKILL.md", command_text)
                self.assertIn(".agents/skills/continuity-local/SKILL.md", command_text)
                self.assertIn("pause only at an explicit `human_required` approval boundary", command_text)
            self.assertTrue((root / ".agents" / "references" / "development-assurance-standard.md").exists())
            self.assertTrue((root / ".agents" / "references" / "workflow-handoffs.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-plan" / "references" / "goal-planning-lenses.md").exists())
            for source in (SUITE / "references").rglob("*"):
                if source.is_file():
                    self.assertTrue((root / ".agents" / "references" / source.relative_to(SUITE / "references")).is_file())
            for skill_source in (SUITE / "skills").iterdir():
                if not skill_source.is_dir():
                    continue
                for source in (skill_source / "references").glob("*"):
                    if source.is_file():
                        self.assertTrue((root / ".agents" / "skills" / skill_source.name / "references" / source.name).is_file())
            self.assertTrue((root / "docs" / "project-memory" / "INDEX.md").exists())
            self.assertTrue((root / "docs" / "project-roadmap" / "INDEX.md").exists())
            self.assertTrue((root / ".agents" / "continuity" / "roadmap-ui" / "app.js").exists())
            manifest = json.loads((root / ".continuity" / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_id"], "sample-project")
            self.assertFalse(manifest["execution_enabled"])
            self.assertEqual(manifest["assurance_standard_version"], 2)
            self.assertEqual(manifest["agent_surfaces"], {"primary": "codex", "enabled": ["codex"]})
            self.assertEqual(manifest["scheduler"]["provider"], "none")
            self.assertEqual(manifest["scheduler"]["sweep_minutes"], 15)
            self.assertEqual(json.loads((root / ".continuity" / "scheduler.json").read_text(encoding="utf-8"))["registration_state"], "not-requested")
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
            self.assertIn(".continuity-write.lock", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn(".agents/continuity/lib/__pycache__/", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertNotIn("project-continuity:start", (root / ".gitignore").read_text(encoding="utf-8"))
            config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(config["require_pr"])
            self.assertTrue(config["require_execution_artifacts"])
            self.assertTrue(config["require_isolated_worktree"])
            self.assertEqual(config["assurance_standard_version"], 2)
            self.assertEqual(config["behavior_configuration_hash"], behavior["configuration_hash"])
            self.assertEqual(config["behavior_skill_path"], ".agents/skills/continuity-local/SKILL.md")
            self.assertFalse(config["require_signed_approvals"])
            recommendations = subprocess.run(
                [str(root / ".agents" / "continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "recommendations"],
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
                        "agent_surfaces": {
                            "primary": "claude-code",
                            "enabled": ["codex", "claude-code", "cursor", "windsurf"],
                        },
                        "scheduler": {"provider": "claude-code"},
                    }
                ),
                encoding="utf-8",
            )
            configured = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
            self.assertEqual(updated_behavior["settings"]["agent_surfaces"]["primary"], "claude-code")
            self.assertEqual(updated_behavior["settings"]["scheduler"]["provider"], "claude-code")
            local_skill = (root / ".agents" / "skills" / "continuity-local" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(updated_behavior["configuration_hash"], local_skill)
            self.assertIn("@AGENTS.md", (root / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertTrue((root / ".claude" / "skills" / "continuity-plan" / "SKILL.md").exists())
            self.assertTrue((root / ".claude" / "skills" / "continuity-plan" / "references" / "goal-planning-lenses.md").exists())
            self.assertTrue((root / ".claude" / "references" / "continuity-contract.md").exists())
            self.assertTrue((root / ".claude" / "references" / "workflow-handoffs.md").exists())
            self.assertTrue((root / ".cursor" / "rules" / "continuity.mdc").exists())
            self.assertTrue((root / ".cursor" / "commands" / "continuity-plan.md").exists())
            self.assertTrue((root / ".claude" / "commands" / "continuity-plan.md").exists())
            self.assertTrue((root / ".windsurf" / "skills" / "continuity-plan" / "SKILL.md").exists())
            self.assertTrue((root / ".windsurf" / "skills" / "continuity-plan" / "references" / "goal-planning-lenses.md").exists())
            for surface_root in (root / ".claude", root / ".windsurf"):
                for source in (SUITE / "references").rglob("*"):
                    if source.is_file():
                        self.assertTrue((surface_root / "references" / source.relative_to(SUITE / "references")).is_file())
                for skill_source in (SUITE / "skills").iterdir():
                    if not skill_source.is_dir():
                        continue
                    for source in (skill_source / "references").glob("*"):
                        if source.is_file():
                            self.assertTrue((surface_root / "skills" / skill_source.name / "references" / source.name).is_file())
            self.assertEqual(json.loads((root / ".continuity" / "scheduler.json").read_text(encoding="utf-8"))["registration_state"], "requires-user-registration")
            registration = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "--json",
                    "scheduler",
                    "register",
                    "--task-id",
                    "supervisor-test-task",
                    "--root",
                    temp,
                    "--actor",
                    "test-user",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(registration.stdout)["state"], "registered")
            audit_lines = (root / ".continuity" / "private" / "configuration-audit.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(audit_lines), 2)
            self.assertEqual(json.loads(audit_lines[-1])["actor"], "test-user")
            claude_plan = root / ".claude" / "skills" / "continuity-plan" / "SKILL.md"
            claude_plan.write_text(claude_plan.read_text(encoding="utf-8") + "\nstale adapter\n", encoding="utf-8")
            stale_adapter_doctor = subprocess.run(
                [str(root / ".agents" / "continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(json.loads(stale_adapter_doctor.stdout)["healthy"])
            self.assertIn("Claude Code skill adapter is missing or stale", stale_adapter_doctor.stdout)
            subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
                    "--project-root",
                    str(root),
                    "project",
                    "configure",
                    "--answers-file",
                    str(answers_path),
                    "--actor",
                    "adapter-repair-test",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            unsafe_answers = Path(temp) / "unsafe-answers.json"
            unsafe_answers.write_text(json.dumps({"force_push": "allowed"}), encoding="utf-8")
            rejected = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
            unsafe_answers.write_text(json.dumps({"agent_surfaces": {"primary": "cursor", "enabled": ["cursor"]}, "scheduler": {"provider": "claude-code"}}), encoding="utf-8")
            rejected_scheduler = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
            self.assertEqual(rejected_scheduler.returncode, 2)
            self.assertIn("scheduler.provider must name an enabled agent surface", rejected_scheduler.stderr)

            subprocess.run(command, check=True, capture_output=True, text=True)
            preserved_behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(preserved_behavior["settings"]["schedules"]["dispatch"], "21:30")
            drifted_config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            drifted_config["validation_commands"] = ["unreviewed command"]
            (root / ".continuity" / "config.json").write_text(json.dumps(drifted_config, indent=2) + "\n", encoding="utf-8")
            drift_doctor = subprocess.run(
                [str(root / ".agents" / "continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(json.loads(drift_doctor.stdout)["healthy"])
            self.assertIn("drifted from project behavior", drift_doctor.stdout)
            subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
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
            subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
                    "--project-root", str(root), "scheduler", "register",
                    "--task-id", "supervisor-test-task", "--root", temp, "--actor", "repair-test",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            doctor = subprocess.run(
                [str(root / ".agents" / "continuity" / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
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
            queued = subprocess.run(
                ["python3", str(CLI), "--json", "portfolio", "queue", "--root", temp],
                check=True,
                capture_output=True,
                text=True,
            )
            queue_records = json.loads(queued.stdout)
            self.assertEqual(queue_records[0]["state"], "no-goals")
            second_root = Path(temp) / "project-two"
            shutil.copytree(root, second_root)
            second_config_path = second_root / ".continuity" / "config.json"
            second_config = json.loads(second_config_path.read_text(encoding="utf-8"))
            second_config["project_id"] = "sample-project-two"
            second_config["scheduler"]["portfolio_max_concurrency"] = 1
            second_config_path.write_text(json.dumps(second_config, indent=2) + "\n", encoding="utf-8")
            second_manifest_path = second_root / ".continuity" / "project.json"
            second_manifest = json.loads(second_manifest_path.read_text(encoding="utf-8"))
            second_manifest["project_id"] = "sample-project-two"
            second_manifest["scheduler"]["portfolio_max_concurrency"] = 1
            second_manifest_path.write_text(json.dumps(second_manifest, indent=2) + "\n", encoding="utf-8")
            actions = subprocess.run(
                [
                    "python3", str(CLI), "--json", "portfolio", "actions", "--root", temp,
                    "--action", "review", "--at", "2026-07-19T20:30:00-05:00",
                    "--supervisor-task-id", "supervisor-test-task", "--sweep-id", "installer-sweep-one",
                ],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "CONTINUITY_ALLOW_TIME_OVERRIDE": "1"},
            )
            action_records = json.loads(actions.stdout)
            self.assertEqual([record["status"] for record in action_records], ["due", "capacity-deferred"])
            due_action = next(record for record in action_records if record["status"] == "due")
            self.assertEqual(due_action["project_id"], "sample-project")
            self.assertEqual(due_action["action"], "review")
            scheduled_run = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
                    "--project-root", str(root), "--json", "scheduler", "run-start", "review",
                    "--idempotency-key", due_action["idempotency_key"], "--claim-token", due_action["claim_token"],
                    "--task-id", "review-child-task",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            scheduled_run_record = json.loads(scheduled_run.stdout)
            subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity"),
                    "--project-root", str(root), "scheduler", "run-finish", scheduled_run_record["run_id"],
                    "--status", "succeeded", "--summary", "Nightly review completed",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            actions_after_success = subprocess.run(
                [
                    "python3", str(CLI), "--json", "portfolio", "actions", "--root", temp,
                    "--action", "review", "--at", "2026-07-19T20:30:00-05:00",
                    "--supervisor-task-id", "supervisor-test-task", "--sweep-id", "installer-sweep-two",
                ],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "CONTINUITY_ALLOW_TIME_OVERRIDE": "1"},
            )
            after_records = json.loads(actions_after_success.stdout)
            self.assertFalse(any(record.get("project_id") == "sample-project" for record in after_records))
            self.assertTrue(any(record.get("project_id") == "sample-project-two" for record in after_records))

    def test_installer_reuses_portable_user_defaults_without_sharing_project_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            defaults_path = Path(temp) / "continuity-defaults.json"
            defaults_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "settings": {
                            "timezone": "UTC",
                            "schedules": {"review": "18:00", "dispatch": "19:00", "report": "06:30"},
                            "agent_surfaces": {"primary": "cursor", "enabled": ["cursor", "generic"]},
                            "scheduler": {"provider": "external"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            root = Path(temp) / "profile-project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "README.md").write_text("# Profile project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            result = subprocess.run(
                [
                    "python3",
                    str(INSTALLER),
                    "--project-root",
                    str(root),
                    "--project-id",
                    "profile-project",
                    "--integration-branch",
                    "main",
                    "--user-defaults",
                    str(defaults_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            installed = json.loads(result.stdout)
            self.assertFalse(installed["user_defaults_saved"])
            behavior = json.loads((root / ".continuity" / "project-behavior.json").read_text(encoding="utf-8"))
            self.assertEqual(behavior["settings"]["timezone"], "UTC")
            self.assertEqual(behavior["settings"]["schedules"]["dispatch"], "19:00")
            self.assertEqual(behavior["settings"]["agent_surfaces"]["primary"], "cursor")
            self.assertEqual(behavior["settings"]["scheduler"]["provider"], "external")
            self.assertTrue((root / ".cursor" / "commands" / "continuity.md").exists())
            self.assertFalse((root / ".claude" / "skills" / "continuity").exists())
            self.assertEqual(behavior["settings"]["validation_commands"], [])
            self.assertEqual(behavior["settings"]["project_instructions"], [])


if __name__ == "__main__":
    unittest.main()
