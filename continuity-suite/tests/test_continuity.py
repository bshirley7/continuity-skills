from __future__ import annotations

import argparse
import hashlib
import io
import datetime as dt
import json
import os
import re
import runpy
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo


SUITE = Path(__file__).resolve().parents[1]
CLI = SUITE / "bin" / "continuity"
INSTALLER = SUITE / "installer" / "install.py"
sys.path.insert(0, str(SUITE / "lib"))
import roadmap as roadmap_lib  # noqa: E402
import runtime as runtime_lib  # noqa: E402
import shared_notes as shared_notes_lib  # noqa: E402


def remove_tree(path: Path) -> None:
    def make_writable(function: object, value: str, _error: object) -> None:
        os.chmod(value, stat.S_IWRITE)
        function(value)

    shutil.rmtree(path, onerror=make_writable)


def installed_cli_args(root: Path) -> list[str]:
    return [sys.executable, str(root / ".agents" / "continuity" / "bin" / "continuity")]


def install_python_tool(directory: Path, name: str, source: str) -> Path:
    script = directory / f"{name}-fixture.py"
    script.write_text(source, encoding="utf-8")
    if os.name == "nt":
        launcher = directory / f"{name}.cmd"
        launcher.write_text(f'@echo off\n"{sys.executable}" "{script}" %*\nexit /b %errorlevel%\n', encoding="utf-8")
    else:
        launcher = directory / name
        launcher.write_text(f"#!/usr/bin/env python3\n{source}", encoding="utf-8")
        launcher.chmod(0o755)
    return launcher


def collection_skills(*collection_ids: str) -> set[str]:
    skills: set[str] = set()
    for collection_id in collection_ids:
        payload = json.loads((SUITE / "collections" / f"{collection_id}.json").read_text(encoding="utf-8"))
        skills.update(payload["skills"])
    return skills


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
            "product_audit_stale_after_days": 30,
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

    def mark_product_audit_not_applicable(self, goal_id: str) -> None:
        self.cli(
            "goal",
            "gate",
            goal_id,
            "product-conformance",
            "--status",
            "not-applicable",
            "--evidence",
            "Fixture goal has no independently auditable product surface.",
        )

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

    def test_prd_capture_preserves_snapshot_memory_provenance_and_goal_binding(self) -> None:
        source = self.root / "docs" / "product" / "review-workspace-prd.md"
        source.parent.mkdir(parents=True)
        source.write_text(
            "# Review workspace PRD\n\n## Problem\nReviewers lose approval context.\n\n"
            "## REQ-1\nShow risk context beside approval details. Keyboard behavior must remain unchanged.\n",
            encoding="utf-8",
        )
        payload = {
            "source_type": "file",
            "source_file": str(source),
            "document_type": "prd",
            "document_id": "prd-review-workspace",
            "document_title": "Review workspace PRD",
            "document_version": "1.0",
            "source_authority": "project-intent",
            "items": [
                {
                    "kind": "insight", "text": "Reviewers lose approval context.",
                    "source_anchor": {"source_item_key": "problem.approval-context", "heading_path": ["Problem"], "section": "problem"},
                    "occurrence_type": "need", "actionability": "context",
                    "stakeholders": ["reviewer"], "themes": ["approval-context"],
                },
                {
                    "kind": "execution-candidate",
                    "text": "REQ-1: Show risk context beside approval details. Acceptance: keyboard behavior remains unchanged.",
                    "source_anchor": {"source_item_key": "requirement.req-1", "heading_path": ["REQ-1"], "section": "requirements", "requirement_id": "REQ-1"},
                    "occurrence_type": "need", "actionability": "plan",
                    "stakeholders": ["reviewer"], "themes": ["risk-context", "keyboard-behavior"],
                },
            ],
        }
        input_path = self.root / "prd-capture.json"
        self.write_json(input_path, payload)
        capture = json.loads(self.cli("note", "capture", "--items-file", str(input_path)).stdout)
        self.assertEqual(capture["source_type"], "file")
        self.assertEqual(capture["document_type"], "prd")
        self.assertEqual(capture["document_revision"], 1)
        self.assertEqual(capture["source_authority"], "project-intent")
        self.assertEqual(capture["source_ref"], "docs/product/review-workspace-prd.md")
        self.assertEqual(len(capture["source_hash"]), 64)
        self.assertEqual(capture["revision_counts"]["added"], 2)
        snapshot = self.root / capture["raw_snapshot_ref"]
        self.assertEqual(snapshot.read_bytes(), source.read_bytes())
        self.assertTrue(all(item["execution_authorized"] is False for item in capture["items"]))
        self.assertTrue(all(item["revision_status"] == "added" for item in capture["items"]))

        status = json.loads(self.cli("workflow", "status", "--capture-id", capture["capture_id"]).stdout)["capture"]
        self.assertEqual(status["document_id"], "prd-review-workspace")
        self.assertEqual(status["source_hash"], capture["source_hash"])
        self.assertNotIn(source.read_text(encoding="utf-8"), json.dumps(status))

        self.cli("memory", "index", "--scope", "trusted")
        trusted = json.loads(self.cli("memory", "search", "approval context", "--scope", "trusted").stdout)
        document_memory = next(item for item in trusted if item["memory_id"] == capture["document_memory_id"])
        self.assertEqual(document_memory["entry_type"], "source-document:prd")
        self.assertEqual(document_memory["scope"], "trusted")
        self.assertIn("product intent", document_memory["summary"])
        memory_status = json.loads(self.cli("workflow", "status", "--memory-id", capture["document_memory_id"]).stdout)["memory"]
        self.assertEqual(memory_status["current_stage"], "memory-current")
        self.assertEqual(memory_status["handoff"]["evidence"]["source_hash"], capture["source_hash"])

        goal = self.create_goal("Implement PRD requirement", [capture["items"][1]["item_id"]])
        self.assertEqual(len(goal["source_capture_refs"]), 1)
        self.assertEqual(goal["source_capture_refs"][0]["capture_id"], capture["capture_id"])
        self.assertEqual(goal["source_capture_refs"][0]["source_hash"], capture["source_hash"])
        plan = (self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "plan.md").read_text(encoding="utf-8")
        self.assertIn("Source documents", plan)
        self.assertIn(capture["source_hash"], plan)

    def test_feature_request_revisions_link_deltas_without_requeueing_unchanged_items(self) -> None:
        source = self.root / "feature-request.txt"
        source.write_text(
            "Saved filters\n\nNeed: reviewers recreate filters.\nRequest: save one preset.\nQuestion: sync across devices?\n",
            encoding="utf-8",
        )

        def capture_payload(items: list[dict]) -> dict:
            payload = {
                "source_type": "file",
                "source_file": str(source),
                "document_type": "feature-request",
                "document_id": "feature-saved-filters",
                "document_title": "Saved filters",
                "source_authority": "supplied-reference",
                "items": items,
            }
            input_path = self.root / "feature-request-capture.json"
            self.write_json(input_path, payload)
            return json.loads(self.cli("note", "capture", "--items-file", str(input_path)).stdout)

        first = capture_payload([
            {
                "kind": "context", "text": "Reviewers recreate filters.",
                "source_anchor": {"source_item_key": "need.recreate-filters", "heading_path": ["Need"]},
                "occurrence_type": "need", "actionability": "context", "stakeholders": ["reviewer"], "themes": ["filters"],
            },
            {
                "kind": "execution-candidate", "text": "Save one filter preset.",
                "source_anchor": {"source_item_key": "request.save-preset", "heading_path": ["Request"]},
                "occurrence_type": "need", "actionability": "plan", "stakeholders": ["reviewer"], "themes": ["filters", "presets"],
            },
            {
                "kind": "question", "text": "Should presets sync across devices?",
                "source_anchor": {"source_item_key": "question.device-sync", "heading_path": ["Question"]},
                "occurrence_type": "need", "actionability": "monitor", "stakeholders": ["reviewer"], "themes": ["device-sync"],
            },
        ])
        goal = self.create_goal("Plan saved filters", [first["items"][1]["item_id"]])
        original_ref = dict(goal["source_capture_refs"][0])
        original_plan_hash = goal["plan_hash"]

        source.write_text(
            "Saved filters\n\nRequest: save three presets.\nQuestion: sync across devices?\nExclusion: no sharing.\n",
            encoding="utf-8",
        )
        second = capture_payload([
            {
                "kind": "execution-candidate", "text": "Save up to three filter presets.",
                "source_anchor": {"source_item_key": "request.save-preset", "heading_path": ["Request"]},
                "occurrence_type": "need", "actionability": "plan", "stakeholders": ["reviewer"], "themes": ["filters", "presets"],
            },
            {
                "kind": "question", "text": "Should presets sync across devices?",
                "source_anchor": {"source_item_key": "question.device-sync", "heading_path": ["Question"]},
                "occurrence_type": "need", "actionability": "monitor", "stakeholders": ["reviewer"], "themes": ["device-sync"],
            },
            {
                "kind": "decision", "text": "Sharing presets is outside this feature request.",
                "source_anchor": {"source_item_key": "exclusion.preset-sharing", "heading_path": ["Exclusion"]},
                "occurrence_type": "constraint", "actionability": "context", "stakeholders": ["reviewer"], "themes": ["sharing", "scope"],
            },
        ])
        self.assertEqual(second["document_revision"], 2)
        self.assertEqual(second["previous_capture_id"], first["capture_id"])
        self.assertNotEqual(second["source_hash"], first["source_hash"])
        self.assertEqual(second["revision_counts"], {"added": 1, "changed": 1, "removed": 1, "unchanged": 1})
        by_status = {item["revision_status"]: item for item in second["items"]}
        self.assertEqual(by_status["unchanged"]["routing_status"], "archive")
        self.assertEqual(by_status["unchanged"]["work_status"], "archived")
        self.assertEqual(by_status["changed"]["supersedes_item_id"], first["items"][1]["item_id"])
        self.assertEqual(by_status["removed"]["supersedes_item_id"], first["items"][0]["item_id"])
        self.assertEqual(by_status["removed"]["text"], "Reviewers recreate filters.")

        duplicate = capture_payload(second["items"][:3])
        self.assertEqual(duplicate["capture_id"], second["capture_id"])
        self.assertTrue(duplicate["deduplicated"])

        self.cli("memory", "index", "--scope", "all")
        all_results = json.loads(self.cli("memory", "search", "Saved filters", "--scope", "all").stdout)
        document_results = [item for item in all_results if item["entry_type"] == "source-document:feature-request"]
        self.assertEqual({item["status"] for item in document_results}, {"current", "historical"})
        trusted_results = json.loads(self.cli("memory", "search", "Saved filters", "--scope", "trusted").stdout)
        self.assertFalse(any(item["entry_type"] == "source-document:feature-request" for item in trusted_results))
        private_results = json.loads(self.cli("memory", "search", "Saved filters", "--scope", "private").stdout)
        self.assertTrue(any(item["entry_type"] == "source-document:feature-request" for item in private_results))

        stored_goal = json.loads((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "goal.json").read_text(encoding="utf-8"))
        self.assertEqual(stored_goal["source_capture_refs"][0], original_ref)
        self.assertEqual(stored_goal["plan_hash"], original_plan_hash)

    def test_document_capture_rejects_unsupported_source_formats(self) -> None:
        source = self.root / "requirements.pdf"
        source.write_bytes(b"not really a pdf")
        payload = {
            "source_type": "file",
            "source_file": str(source),
            "document_type": "prd",
            "document_id": "prd-invalid-format",
            "items": [{
                "kind": "context", "text": "Invalid source.",
                "source_anchor": {"source_item_key": "context.invalid", "heading_path": ["Context"]},
            }],
        }
        input_path = self.root / "invalid-document-capture.json"
        self.write_json(input_path, payload)
        result = self.cli("note", "capture", "--items-file", str(input_path), expected=2)
        self.assertIn("supports only Markdown and plain-text files", result.stderr)

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
        inbox = json.loads(self.cli("roadmap", "inbox").stdout)
        projected = next(candidate for candidate in inbox if candidate["note_id"] == item["item_id"])
        self.assertEqual(projected["status"], "triaged")
        self.assertEqual(projected["visibility"], "private-inbox")
        self.assertFalse(projected["execution_authorized"])
        projection = json.loads((self.root / ".continuity" / "private" / "roadmap" / "projection.json").read_text(encoding="utf-8"))
        self.assertIn(item["item_id"], {candidate["note_id"] for candidate in projection["roadmap_inbox"]})
        brief = self.cli("roadmap", "brief", "approved bridge change").stdout
        self.assertIn("Triaged roadmap inbox", brief)
        self.assertIn(item["item_id"], brief)
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

    def test_goal_activate_binds_one_request_and_dispatches_routine_interactive_work(self) -> None:
        capture = self.create_capture()
        instruction = capture["items"][3]
        self.cli(
            "note", "triage", capture["capture_id"], instruction["item_id"],
            "--kind", "explicit-instruction", "--action", "promote",
        )
        goal_file = self.root / "fast-goal.json"
        self.write_json(
            goal_file,
            {
                "title": "Implement the bridge change",
                "scope": "Implement the requested bridge change without replacing Electron.",
                "exclusions": ["Do not deploy or merge"],
                "acceptance_criteria": ["The bridge behavior is implemented", "Validation passes"],
                "source_note_ids": [instruction["item_id"]],
                "note_dispositions": [
                    {
                        "note_id": instruction["item_id"],
                        "disposition": "current-goal",
                        "reason": "This is the exact implementation requested through /goal.",
                        "delivery_slice_ids": [],
                    }
                ],
                "memory_ids": ["memory-current"],
                "authorization_mode": "goal-request",
                "risk_level": "routine",
                "restricted_side_effects": [],
                "plan_reviewed": True,
                "plan_review_evidence": "The plan is a faithful, bounded translation of the explicit request.",
                "memory_reviewed": True,
            },
        )
        goal = json.loads(self.cli("goal", "create", "--goal-file", str(goal_file)).stdout)
        manifest_path = self.root / ".continuity" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["execution_enabled"] = False
        self.write_json(manifest_path, manifest)
        config_path = self.root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["require_signed_approvals"] = True
        self.write_json(config_path, config)
        activated = json.loads(self.cli("goal", "activate", goal["goal_id"]).stdout)
        self.assertEqual(activated["goal"]["state"], "dispatched")
        self.assertEqual(activated["approval"]["approved_by"], "interactive-user")
        self.assertEqual(activated["approval"]["authorization_source"], "goal-request")
        self.assertEqual(activated["approval"]["signature_format"], "legacy-unsigned")
        self.assertEqual(activated["dispatch"]["execution_mode"], "interactive-fast")
        self.assertIn(
            "interactive-goal-request:execution-authorized; unattended-execution-disabled",
            json.loads((self.root / ".continuity" / "private" / "goals" / goal["goal_id"] / "preflight.json").read_text(encoding="utf-8"))["evidence"],
        )
        self.assertEqual(activated["authorization_envelope"]["mode"], "interactive-goal-request")
        status = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual(status["current_stage"], "execution-start")
        self.assertEqual(status["human_requirements"], [])
        inbox = json.loads(self.cli("roadmap", "inbox", "--status", "planned").stdout)
        self.assertIn(instruction["item_id"], {candidate["note_id"] for candidate in inbox})

    def test_goal_proceed_treats_plan_approval_as_dispatch_authority_without_extra_signing(self) -> None:
        goal = self.create_goal("Proceed without repeated signing")
        config_path = self.root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["require_signed_approvals"] = True
        self.write_json(config_path, config)
        status = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual([action["disposition"] for action in status["allowed_actions"]], ["proceed"])
        self.assertEqual(status["human_requirements"], [])
        self.assertNotIn("--authorization-text", status["allowed_actions"][0]["command"])
        self.assertNotIn("--signing-key", status["allowed_actions"][0]["command"])
        proceeded = json.loads(self.cli("goal", "proceed", goal["goal_id"]).stdout)
        self.assertEqual(proceeded["goal"]["state"], "dispatched")
        self.assertEqual(proceeded["approval"]["authorization_source"], "plan-proceed")
        self.assertEqual(proceeded["approval"]["signature_format"], "legacy-unsigned")
        self.assertEqual(proceeded["dispatch"]["execution_mode"], "interactive-fast")
        self.assertEqual(proceeded["authorization_envelope"]["mode"], "interactive-plan-proceed")

    def test_goal_activate_rejects_risk_and_restricted_side_effects(self) -> None:
        for title, risk, effects in (
            ("Elevated fast goal", "elevated", []),
            ("External fast goal", "routine", ["deploy to production"]),
        ):
            goal_file = self.root / f"{title.replace(' ', '-')}.json"
            self.write_json(
                goal_file,
                {
                    "title": title,
                    "scope": "Prepare work that requires a separate authority decision.",
                    "acceptance_criteria": ["The bounded work is complete"],
                    "memory_ids": ["memory-current"],
                    "authorization_mode": "goal-request",
                    "risk_level": risk,
                    "restricted_side_effects": effects,
                    "plan_reviewed": True,
                    "memory_reviewed": True,
                },
            )
            goal = json.loads(self.cli("goal", "create", "--goal-file", str(goal_file)).stdout)
            rejected = self.cli("goal", "activate", goal["goal_id"], expected=2)
            self.assertIn("require separate", rejected.stderr)

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
        self.mark_product_audit_not_applicable(goal["goal_id"])
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
        install_python_tool(
            fake_bin,
            "gh",
            "import json,sys\n"
            "args=sys.argv[1:]\n"
            "if args[:2] == ['api','user']:\n print('fixture-user'); raise SystemExit(0)\n"
            "if args[:2] == ['pr','view']:\n print(json.dumps({'url':'https://github.com/example/project/pull/1','state':'OPEN','headRefName':'continuity/quality-gates','baseRefName':'main','headRefOid':'deadbeef','isDraft':False,'mergeStateStatus':'CLEAN','reviewDecision':'APPROVED','reviews':[],'statusCheckRollup':[]})); raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
        )
        original_path = os.environ.get("PATH", "")
        pr_config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        pr_config["require_pr"] = True
        self.write_json(self.root / ".continuity" / "config.json", pr_config)
        self.git("remote", "add", "origin", "https://github.com/example/project.git")
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
        self.mark_product_audit_not_applicable(goal["goal_id"])
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

    def test_candidate_product_audit_is_source_bound_and_routes_findings(self) -> None:
        goal = self.create_goal("Audit candidate")
        (self.root / "goal-Audit-candidate.json").unlink()
        self.approve(goal)
        self.cli("goal", "start", goal["goal_id"])
        self.git("checkout", "-b", "continuity/audit-candidate")
        self.cli(
            "run",
            "update",
            goal["goal_id"],
            "--state",
            "running",
            "--branch",
            "continuity/audit-candidate",
        )
        artifact = self.root / "product-conformance.md"
        artifact.write_text(
            "# Product conformance\n\nThe approved candidate journey is aligned.\n",
            encoding="utf-8",
        )
        self.git("add", "product-conformance.md")
        self.git("commit", "-m", "add product conformance evidence")
        self.cli(
            "test",
            "run",
            goal["goal_id"],
            "--worktree",
            str(self.root),
            "--branch",
            "continuity/audit-candidate",
        )
        self.cli(
            "test",
            "record",
            goal["goal_id"],
            "--status",
            "passed",
            "--summary",
            "Candidate tests passed",
            "--worktree",
            str(self.root),
            "--branch",
            "continuity/audit-candidate",
            "--code-review-evidence",
            "diff reviewed",
            "--security-evidence",
            "trust boundaries reviewed",
            "--update-gates",
        )
        audit_input = self.root.parent / "candidate-audit-input.json"
        self.write_json(
            audit_input,
            {
                "title": "Candidate product conformance",
                "profile": "candidate",
                "purpose": "Verify the current approved goal.",
                "target": {"environment": "local", "reference": "execution worktree"},
                "sources": [],
                "journeys": [
                    {
                        "journey_id": "approved-outcome",
                        "title": "Approved outcome",
                        "requirements": ["The approved candidate outcome is observable."],
                        "viewports": ["default"],
                    }
                ],
            },
        )
        plan = json.loads(
            self.cli(
                "audit",
                "plan",
                "--input",
                str(audit_input),
                "--goal-id",
                goal["goal_id"],
            ).stdout
        )
        self.assertFalse(plan["execution_authorized"])
        self.cli(
            "audit",
            "start",
            plan["audit_id"],
            "--worktree",
            str(self.root),
            "--branch",
            "continuity/audit-candidate",
        )
        source_id = plan["sources"][0]["source_id"]
        audit_result = self.root.parent / "candidate-audit-result.json"
        self.write_json(
            audit_result,
            {
                "audit_id": plan["audit_id"],
                "summary": "The approved candidate outcome is aligned.",
                "coverage": {"planned": 1, "observed": 1, "blocked": 0},
                "evidence": [
                    {
                        "evidence_id": "candidate-artifact",
                        "kind": "document",
                        "description": "Sanitized conformance artifact.",
                        "captured_at": "2026-07-18T12:00:00+00:00",
                        "path": "product-conformance.md",
                    }
                ],
                "findings": [
                    {
                        "finding_id": "approved-outcome",
                        "requirement_ref": "approved-outcome",
                        "title": "Approved outcome is present",
                        "status": "aligned",
                        "severity": "info",
                        "confidence": "high",
                        "scope": "current-goal",
                        "gate_impact": "none",
                        "source_refs": [source_id],
                        "evidence_refs": ["candidate-artifact"],
                        "summary": "The audited artifact records the approved result.",
                        "recommendation": "Retain the current behavior.",
                    }
                ],
            },
        )
        record = json.loads(
            self.cli(
                "audit",
                "record",
                plan["audit_id"],
                "--result-file",
                str(audit_result),
                "--worktree",
                str(self.root),
                "--branch",
                "continuity/audit-candidate",
                "--artifact",
                str(artifact),
                "--update-gate",
            ).stdout
        )
        self.assertEqual(record["status"], "passed")
        self.assertFalse(record["execution_authorized"])
        compliance = json.loads(
            (
                self.root
                / ".continuity"
                / "private"
                / "goals"
                / goal["goal_id"]
                / "compliance.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(compliance["stages"]["product-conformance"]["status"], "passed")
        self.cli("run", "update", goal["goal_id"], "--state", "validating")
        workflow = json.loads(
            self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout
        )["goal"]
        self.assertEqual(workflow["current_stage"], "merge-safety")
        audit_workflow = json.loads(
            self.cli("workflow", "status", "--audit-id", plan["audit_id"]).stdout
        )["audit"]
        self.assertEqual(audit_workflow["next_skill"], "continuity-report")

    def test_product_audit_mismatch_cannot_force_pass_and_capture_is_non_authorizing(self) -> None:
        audit_input = self.root.parent / "baseline-audit-input.json"
        self.write_json(
            audit_input,
            {
                "title": "Baseline product audit",
                "profile": "baseline",
                "purpose": "Establish current conformance.",
                "target": {"environment": "code", "reference": "fixture repository"},
                "sources": [
                    {
                        "source_id": "fixture-intent",
                        "source_type": "project-intent",
                        "authority": "canonical",
                        "applicability": "Current fixture behavior.",
                        "time_horizon": "current",
                        "reference": "AGENTS.md",
                    }
                ],
                "journeys": [
                    {
                        "journey_id": "fixture-surface",
                        "title": "Fixture surface",
                        "requirements": ["The expected product behavior is observable."],
                    }
                ],
            },
        )
        plan = json.loads(
            self.cli("audit", "plan", "--input", str(audit_input)).stdout
        )
        self.cli(
            "audit",
            "start",
            plan["audit_id"],
            "--worktree",
            str(self.root),
            "--branch",
            "main",
        )
        result_path = self.root.parent / "baseline-audit-result.json"
        result = {
            "audit_id": plan["audit_id"],
            "status": "passed",
            "summary": "The expected product behavior is missing.",
            "coverage": {"planned": 1, "observed": 1, "blocked": 0},
            "evidence": [
                {
                    "evidence_id": "fixture-source",
                    "kind": "document",
                    "description": "The current fixture contract.",
                    "captured_at": "2026-07-18T12:00:00+00:00",
                    "path": "AGENTS.md",
                }
            ],
            "findings": [
                {
                    "finding_id": "missing-behavior",
                    "requirement_ref": "fixture-surface",
                    "title": "Expected behavior is missing",
                    "status": "missing",
                    "severity": "high",
                    "confidence": "high",
                    "scope": "current-goal",
                    "gate_impact": "blocking",
                    "source_refs": ["fixture-intent"],
                    "evidence_refs": ["fixture-source"],
                    "summary": "The current surface does not expose the expected behavior.",
                    "recommendation": "Route the mismatch through planning before implementation.",
                }
            ],
        }
        self.write_json(result_path, result)
        self.cli(
            "audit",
            "record",
            plan["audit_id"],
            "--result-file",
            str(result_path),
            "--worktree",
            str(self.root),
            "--branch",
            "main",
            expected=2,
        )
        result.pop("status")
        self.write_json(result_path, result)
        recorded = json.loads(
            self.cli(
                "audit",
                "record",
                plan["audit_id"],
                "--result-file",
                str(result_path),
                "--worktree",
                str(self.root),
                "--branch",
                "main",
            ).stdout
        )
        self.assertEqual(recorded["status"], "failed")
        capture = json.loads(
            self.cli("audit", "capture-findings", plan["audit_id"]).stdout
        )
        self.assertTrue(capture["captured"])
        self.assertFalse(capture["execution_authorized"])
        note = json.loads(self.cli("note", "list").stdout)[0]
        self.assertFalse(note["execution_authorized"])
        capture_record = next(
            json.loads(path.read_text(encoding="utf-8"))
            for path in (self.root / ".continuity" / "private" / "captures").rglob("*.json")
            if json.loads(path.read_text(encoding="utf-8")).get("capture_id")
            == capture["findings_capture"]["capture_id"]
        )
        self.assertEqual(capture_record["source_type"], "product-audit")

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
        pr_url = "https://ghe.example.test/example/project/pull/42"
        self.git("remote", "add", "origin", "git@ghe.example.test:example/project.git")
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
        install_python_tool(
            fake_bin,
            "gh",
            "import json,sys\n"
            "from pathlib import Path\n"
            f"state=Path({str(state_path)!r})\nlog=Path({str(log_path)!r})\n"
            "args=sys.argv[1:]\n"
            "with log.open('a',encoding='utf-8') as handle: handle.write(' '.join(args)+'\\n')\n"
            "if args[:2] == ['api','user']:\n print('fixture-user'); raise SystemExit(0)\n"
            "if args[:2] == ['pr','merge']:\n state.write_text('merged\\n',encoding='utf-8'); raise SystemExit(0)\n"
            "if args[:2] == ['pr','view']:\n"
            f" merged=state.read_text(encoding='utf-8').strip()=='merged'\n payload={{'url':{pr_url!r},'state':'MERGED' if merged else 'OPEN','headRefName':'continuity/guarded-cli-merge','baseRefName':'main','headRefOid':{head_sha!r},'isDraft':False,'mergeStateStatus':'CLEAN','reviewDecision':'APPROVED','reviews':[{{'state':'APPROVED','author':{{'login':'fixture-reviewer'}}}}],'statusCheckRollup':[{{'name':'Continuity CI','conclusion':'SUCCESS'}}],'mergeCommit':{{'oid':{merge_commit!r}}} if merged else None,'mergedBy':{{'login':'fixture-user'}} if merged else None}}\n print(json.dumps(payload)); raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
        )
        original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        try:
            self.mark_product_audit_not_applicable(goal["goal_id"])
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
            self.cli(
                "merge", "execute", goal["goal_id"], "--pr-url", pr_url, "--head-sha", head_sha,
                "--merge-method", "squash", "--authorized-by", "different-active-account",
                "--authorization-text", authorization_text, expected=2,
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
        self.assertIn("api user --hostname ghe.example.test", gh_log)
        self.assertIn("--repo ghe.example.test/example/project", gh_log)
        self.assertIn(f"--match-head-commit {head_sha}", gh_log)
        self.assertNotIn("--admin", gh_log)
        self.assertNotIn("--auto", gh_log)

    def test_github_host_repository_account_and_review_matrix_is_fail_closed(self) -> None:
        cli_module = runpy.run_path(str(CLI))
        continuity_error = cli_module["ContinuityError"]
        self.git("remote", "add", "origin", "https://github.com/Example/Project.git")
        public = cli_module["github_pr_context"](
            self.root,
            "https://github.com/example/project/pull/17",
        )
        self.assertEqual(public["spec"], "github.com/example/project")
        self.assertEqual(public["number"], 17)

        self.git("remote", "set-url", "origin", "git@ghe.example.test:Example/Project.git")
        enterprise_url = "https://ghe.example.test/example/project/pull/91"
        enterprise = cli_module["github_pr_context"](self.root, enterprise_url)
        self.assertEqual(enterprise["host"], "ghe.example.test")
        self.assertEqual(enterprise["spec"], "ghe.example.test/example/project")
        self.assertEqual(shared_notes_lib._parse_github_pr_url(enterprise_url)["spec"], enterprise["spec"])
        with self.assertRaises(shared_notes_lib.SharedNoteError):
            shared_notes_lib._parse_github_pr_url(
                "https://user:secret@ghe.example.test/example/project/pull/91"
            )
        with self.assertRaisesRegex(continuity_error, "does not match origin repository"):
            cli_module["github_pr_context"](
                self.root,
                "https://ghe.example.test/example/other-project/pull/91",
            )
        for unsafe in (
            "http://ghe.example.test/example/project/pull/91",
            "https://user:secret@ghe.example.test/example/project/pull/91",
            "https://ghe.example.test/example/project/pull/91?account=other",
            "https://ghe.example.test/example/project/pull/0",
            "https://ghe.example.test/example/project/pull/91/",
            "https://ghe.example.test/example/project/pull/91/extra",
        ):
            with self.assertRaises(continuity_error, msg=unsafe):
                cli_module["parse_github_pr_url"](unsafe)

        reviews = [
            {"state": "APPROVED", "author": {"login": "Reviewer-One"}},
            {"state": "APPROVED", "author": {"login": "reviewer-two"}},
            {"state": "CHANGES_REQUESTED", "author": {"login": "REVIEWER-ONE"}},
            {"state": "COMMENTED", "author": {"login": "reviewer-two"}},
        ]
        self.assertEqual(cli_module["github_approved_reviewers"](reviews), {"reviewer-two"})
        check_summary = cli_module["github_check_summary"](
            [
                {"name": "Continuity CI", "conclusion": "SUCCESS"},
                {"name": "Security", "status": "IN_PROGRESS"},
            ],
            ["Continuity CI", "Security", "Required Missing"],
        )
        self.assertFalse(check_summary["passed"])
        self.assertIn("Required Missing", check_summary["missing"])
        self.assertTrue(any("IN_PROGRESS" in failure for failure in check_summary["failures"]))

        fake_bin = self.root.parent / "github-matrix-bin"
        fake_bin.mkdir()
        payload_path = self.root.parent / "github-matrix-payload.json"
        log_path = self.root.parent / "github-matrix-gh.log"
        payload = {
            "url": enterprise_url,
            "state": "OPEN",
            "headRefName": "continuity/example",
            "baseRefName": "main",
            "headRefOid": "a" * 40,
        }
        self.write_json(payload_path, payload)
        install_python_tool(
            fake_bin,
            "gh",
            "import sys\n"
            "from pathlib import Path\n"
            f"payload=Path({str(payload_path)!r})\nlog=Path({str(log_path)!r})\n"
            "args=sys.argv[1:]\n"
            "with log.open('a',encoding='utf-8') as handle: handle.write(' '.join(args)+'\\n')\n"
            "if args[:2] == ['api','user']:\n print('enterprise-user'); raise SystemExit(0)\n"
            "if args[:2] == ['pr','view']:\n print(payload.read_text(encoding='utf-8')); raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
        )
        original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        try:
            self.assertEqual(
                cli_module["github_authenticated_login"](self.root, enterprise),
                "enterprise-user",
            )
            details = cli_module["github_pr_details"](
                self.root,
                enterprise_url,
                ["state", "headRefOid"],
                context=enterprise,
            )
            self.assertEqual(details["headRefOid"], "a" * 40)
            payload["url"] = "https://ghe.example.test/example/other-project/pull/91"
            self.write_json(payload_path, payload)
            with self.assertRaisesRegex(continuity_error, "different repository"):
                cli_module["github_pr_details"](
                    self.root,
                    enterprise_url,
                    ["state"],
                    context=enterprise,
                )
        finally:
            os.environ["PATH"] = original_path
        gh_log = log_path.read_text(encoding="utf-8")
        self.assertIn("api user --hostname ghe.example.test", gh_log)
        self.assertIn("pr view 91 --repo ghe.example.test/example/project", gh_log)

    def test_workflow_status_and_changes_requested_reopen_same_goal(self) -> None:
        capture = self.create_capture()
        note_id = capture["items"][3]["item_id"]
        self.cli("note", "triage", capture["capture_id"], note_id, "--action", "promote")
        goal = self.create_goal("Review rework", [note_id])
        (self.root / "capture.json").unlink()
        (self.root / "goal-Review-rework.json").unlink()
        initial = json.loads(self.cli("workflow", "status", "--goal-id", goal["goal_id"]).stdout)["goal"]
        self.assertEqual(initial["current_stage"], "plan-review")
        self.assertEqual([action["disposition"] for action in initial["allowed_actions"]], ["proceed"])
        self.assertEqual(initial["human_requirements"], [])
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
        self.mark_product_audit_not_applicable(goal["goal_id"])
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
        config["require_remote_lease"] = True
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
        scheduler_remote = self.root.parent / "scheduler-remote.git"
        subprocess.run(["git", "init", "--bare", str(scheduler_remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(scheduler_remote))
        self.git("push", "-u", "origin", "main")
        self.cli(
            "scheduler", "lease", "acquire", "--owner", "scheduler-fixture", "--goal-id", goal["goal_id"],
            "--remote", "origin",
        )
        dispatch_claim = reserve("dispatch", "2026-07-16T22:30:00-05:00", "sweep-dispatch-16")
        execution_run = json.loads(
            self.cli(
                "scheduler", "run-start", "dispatch", "--idempotency-key", dispatch_claim["idempotency_key"],
                "--claim-token", dispatch_claim["claim_token"], "--task-id", "execution-task", "--goal-id", goal["goal_id"],
            ).stdout
        )
        bound_lease = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)["lease"]
        self.assertEqual(bound_lease["bound_run_id"], execution_run["run_id"])
        self.assertEqual(bound_lease["bound_task_id"], "execution-task")
        self.assertEqual(bound_lease["bound_idempotency_key"], dispatch_claim["idempotency_key"])
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
        self.assertEqual(json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)["state"], "available")
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

    def test_codex_adapter_observes_signed_no_op_replay_staleness_and_remote_contention(self) -> None:
        key = self.root.parent / "observed-adapter-signer"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
        config_path = self.root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["scheduler"] = {
            "provider": "codex",
            "sweep_minutes": 15,
            "business_days": [0, 1, 2, 3, 4],
            "retry_limit": 2,
            "retry_backoff_minutes": 15,
            "stale_after_minutes": 45,
            "portfolio_max_concurrency": 1,
        }
        config["behavior_configuration_hash"] = "b" * 64
        config["require_signed_approvals"] = True
        config["approval_allowed_signers"] = ".continuity/trusted-approvers"
        self.write_json(config_path, config)
        manifest_path = self.root / ".continuity" / "project.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["execution_enabled"] = False
        manifest["scheduler"] = config["scheduler"]
        manifest["agent_surfaces"] = {"primary": "codex", "enabled": ["codex", "claude-code"]}
        self.write_json(manifest_path, manifest)
        self.cli("approval", "trust", "add", "--identity", "fixture-user", "--public-key", str(key) + ".pub")
        self.cli(
            "scheduler", "register", "--task-id", "observed-codex-supervisor",
            "--root", self.temp.name, "--actor", "fixture-user",
        )

        def reserve_review(at: str, sweep_id: str) -> dict[str, object]:
            records = json.loads(
                self.cli(
                    "portfolio", "actions", "--root", self.temp.name, "--action", "review",
                    "--at", at, "--supervisor-task-id", "observed-codex-supervisor", "--sweep-id", sweep_id,
                ).stdout
            )
            claim = next(record for record in records if record.get("project_id") == "test-project" and record.get("status") in {"due", "retry"})
            claims_path = self.root / ".continuity" / "private" / "scheduler-due-actions.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            claims[claim["claim_token"]]["expires_at"] = "2999-01-01T00:00:00-06:00"
            self.write_json(claims_path, claims)
            return claim

        first_claim = reserve_review("2026-07-15T20:30:00-05:00", "observed-sweep-one")
        no_op = json.loads(
            self.cli(
                "scheduler", "run-start", "review", "--idempotency-key", first_claim["idempotency_key"],
                "--claim-token", first_claim["claim_token"], "--task-id", "observed-child-one",
                "--summary", "Observed no-op review started.",
            ).stdout
        )
        self.cli(
            "scheduler", "run-finish", no_op["run_id"], "--status", "succeeded",
            "--summary", "Observed no-op review: no eligible changes or decisions.",
        )
        replay = self.cli(
            "scheduler", "run-start", "review", "--idempotency-key", first_claim["idempotency_key"],
            "--claim-token", first_claim["claim_token"], "--task-id", "observed-replay", expected=2,
        )
        second_claim = reserve_review("2026-07-16T20:30:00-05:00", "observed-sweep-two")
        registration_path = self.root / ".continuity" / "private" / "scheduler-registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration["last_heartbeat_at"] = "2020-01-01T00:00:00-06:00"
        self.write_json(registration_path, registration)
        stale = self.cli(
            "scheduler", "run-start", "review", "--idempotency-key", second_claim["idempotency_key"],
            "--claim-token", second_claim["claim_token"], "--task-id", "observed-stale", expected=2,
        )
        self.cli(
            "portfolio", "actions", "--root", self.temp.name, "--action", "review",
            "--at", "2026-07-19T20:30:00-05:00", "--supervisor-task-id", "observed-codex-supervisor",
            "--sweep-id", "observed-sweep-three",
        )

        goal = self.create_goal("Observed remote lease contention")
        remote = self.root.parent / "observed-adapter-remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "main")
        self.cli(
            "scheduler", "lease", "acquire", "--owner", "workstation-one",
            "--goal-id", goal["goal_id"], "--remote", "origin",
        )
        workstation_two = self.root.parent / "observed-workstation-two"
        subprocess.run(
            ["git", "clone", "--branch", "main", str(remote), str(workstation_two)],
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "-C", str(workstation_two), "config", "user.email", "tests@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(workstation_two), "config", "user.name", "Continuity Tests"], check=True)
        source_goal = self.root / ".continuity" / "private" / "goals" / goal["goal_id"]
        target_goal = workstation_two / ".continuity" / "private" / "goals" / goal["goal_id"]
        target_goal.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_goal, target_goal)
        contention = subprocess.run(
            [
                "python3", str(CLI), "--project-root", str(workstation_two), "scheduler", "lease", "acquire",
                "--owner", "workstation-two", "--goal-id", goal["goal_id"], "--remote", "origin",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(contention.returncode, 2, contention.stderr)
        self.assertIn("active remote lease", contention.stderr)

        artifacts = {
            "claim-replay-rejected": {"returncode": replay.returncode, "stderr": replay.stderr.strip()},
            "stale-registration-rejected": {"returncode": stale.returncode, "stderr": stale.stderr.strip()},
            "remote-lease-contention-rejected": {"returncode": contention.returncode, "stderr": contention.stderr.strip()},
        }
        artifact_root = self.root / ".continuity" / "private" / "reports" / "conformance-artifacts"
        for probe, artifact in artifacts.items():
            artifact_path = artifact_root / f"{probe}.json"
            self.write_json(artifact_path, artifact)
            digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            self.cli(
                "scheduler", "adapter", "codex", "record-probe", "--probe", probe, "--status", "passed",
                "--evidence", f"Observed from direct local protocol execution: {artifact_path.relative_to(self.root).as_posix()}",
                "--artifact-sha256", digest, "--actor", "fixture-user", "--signing-key", str(key),
            )
        verified = json.loads(self.cli("scheduler", "adapter", "codex", "verify").stdout)
        self.assertTrue(verified["healthy"], verified)
        self.assertGreaterEqual(verified["observed_sweeps"], 2)
        self.assertEqual(verified["observed_no_op_runs"], 1)

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

    def test_missing_note_lifecycle_timestamps_migrate_from_provenance(self) -> None:
        capture = self.create_capture()
        capture_path = next(
            path
            for path in (self.root / ".continuity" / "private" / "captures").glob("**/*.json")
            if path.name == f"{capture['capture_id']}.json"
        )
        record = json.loads(capture_path.read_text(encoding="utf-8"))
        note = record["items"][0]
        note.pop("created_at", None)
        note.pop("updated_at", None)
        revision_at = "2099-01-01T00:00:00-06:00"
        note["revision_history"] = [{"at": revision_at, "previous": {}, "current": {}}]
        self.write_json(capture_path, record)
        before = json.loads(self.cli("project", "doctor").stdout)
        self.assertTrue(any("missing or invalid lifecycle timestamp" in problem for problem in before["problems"]))

        migrated = json.loads(self.cli("note", "migrate-lifecycle", "--actor", "fixture-user").stdout)
        self.assertEqual(migrated["migrated"], 1)
        updated = json.loads(capture_path.read_text(encoding="utf-8"))["items"][0]
        self.assertEqual(updated["created_at"], record["captured_at"])
        self.assertEqual(updated["updated_at"], revision_at)
        after = json.loads(self.cli("project", "doctor").stdout)
        self.assertFalse(any("missing or invalid lifecycle timestamp" in problem for problem in after["problems"]))

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
        self.assertEqual(status["handoff"]["human_requirements"], [])
        self.assertEqual([action["disposition"] for action in status["allowed_actions"]], ["proceed"])

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
        cli_module = runpy.run_path(str(CLI))
        revision_times = iter(["2026-07-16T10:00:00-05:00", "2026-07-16T10:00:01-05:00"])
        cli_module["iso_now"] = lambda _config: next(revision_times)
        previous_root = os.environ.get("CONTINUITY_PROJECT_ROOT")
        os.environ["CONTINUITY_PROJECT_ROOT"] = str(self.root)
        try:
            revised = cli_module["goal_revise"](
                argparse.Namespace(
                    goal_id=goal["goal_id"],
                    goal_file=str(revision_path),
                    author="fixture-user",
                    summary="Clarify the approved scope",
                )
            )
        finally:
            if previous_root is None:
                os.environ.pop("CONTINUITY_PROJECT_ROOT", None)
            else:
                os.environ["CONTINUITY_PROJECT_ROOT"] = previous_root
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
        self.cli(
            "scheduler", "lease", "acquire", "--owner", "operator-one", "--goal-id", goal["goal_id"],
            "--attempt-id", "2", "--remote", "origin", expected=2,
        )
        self.cli(
            "scheduler", "lease", "renew", "--goal-id", goal["goal_id"], "--attempt-id", "2",
            "--ttl-minutes", "60", expected=2,
        )
        renewed = json.loads(
            self.cli(
                "scheduler", "lease", "renew", "--goal-id", goal["goal_id"], "--attempt-id", "1",
                "--ttl-minutes", "60",
            ).stdout
        )
        self.assertNotEqual(renewed["lease_commit"], acquired["lease_commit"])
        self.assertEqual(renewed["previous_lease_commit"], acquired["lease_commit"])
        local_lease_path = self.root / ".continuity" / "private" / "remote-lease.json"
        self.write_json(local_lease_path, acquired)
        self.cli(
            "scheduler", "lease", "release", "--reason", "stale replay", "--goal-id", goal["goal_id"],
            "--attempt-id", "1", expected=2,
        )
        self.write_json(local_lease_path, renewed)
        workstation_two = self.root.parent / "workstation-two"
        subprocess.run(["git", "clone", "--branch", "main", str(remote), str(workstation_two)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(workstation_two), "config", "user.name", "Continuity Tests"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(workstation_two), "config", "user.email", "tests@example.invalid"],
            check=True,
            capture_output=True,
        )
        shutil.copy2(self.root / ".continuity" / "config.json", workstation_two / ".continuity" / "config.json")
        shutil.copy2(self.root / ".continuity" / "project.json", workstation_two / ".continuity" / "project.json")
        shutil.copytree(self.root / ".continuity" / "private", workstation_two / ".continuity" / "private")

        def second_cli(*arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
            result = subprocess.run(
                [sys.executable, str(CLI), "--project-root", str(workstation_two), "--json", *arguments],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CONTINUITY_ALLOW_TIME_OVERRIDE": "1"},
            )
            self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
            return result

        second_cli("scheduler", "lease", "acquire", "--owner", "operator-two", "--goal-id", goal["goal_id"], "--remote", "origin", expected=2)
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
        self.cli("scheduler", "lease", "release", "--reason", "wrong attempt", "--goal-id", goal["goal_id"], "--attempt-id", "2", expected=2)
        active = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(active["state"], "active")
        released = json.loads(self.cli("scheduler", "lease", "release", "--reason", "pilot complete", "--goal-id", goal["goal_id"], "--attempt-id", "1").stdout)
        self.assertEqual(released["status"], "released")
        self.cli("scheduler", "lease", "release", "--reason", "duplicate release", "--goal-id", goal["goal_id"], "--attempt-id", "1", expected=2)
        available = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(available["state"], "available")
        acquired_two = json.loads(second_cli("scheduler", "lease", "acquire", "--owner", "operator-two", "--goal-id", goal["goal_id"], "--remote", "origin").stdout)
        self.assertEqual(acquired_two["status"], "active")
        released_two = json.loads(second_cli("scheduler", "lease", "release", "--reason", "second workstation complete", "--goal-id", goal["goal_id"], "--attempt-id", "1").stdout)
        self.assertEqual(released_two["status"], "released")
        final = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(final["state"], "available")

        def push_lease_record(record: dict[str, object], parent: str) -> str:
            blob_result = subprocess.run(
                ["git", "-C", str(self.root), "hash-object", "-w", "--stdin"],
                input=(runtime_lib.canonical_json(record) + "\n").encode("utf-8"),
                capture_output=True,
                check=True,
            )
            blob = blob_result.stdout.decode("utf-8").strip()
            tree_result = subprocess.run(
                ["git", "-C", str(self.root), "mktree"],
                input=f"100644 blob {blob}\tlease.json\n".encode("utf-8"),
                capture_output=True,
                check=True,
            )
            tree = tree_result.stdout.decode("utf-8").strip()
            commit_result = subprocess.run(
                ["git", "-C", str(self.root), "commit-tree", tree, "-p", parent, "-m", "lease edge-case fixture"],
                input=b"",
                capture_output=True,
                check=True,
            )
            commit = commit_result.stdout.decode("utf-8").strip()
            subprocess.run(
                ["git", "-C", str(self.root), "push", "origin", f"{commit}:refs/continuity/leases/test-project"],
                capture_output=True,
                check=True,
            )
            return commit

        future_record = {
            "schema_version": 1,
            "project_id": "test-project",
            "goal_id": goal["goal_id"],
            "attempt_id": "1",
            "owner_fingerprint": acquired_two["owner_fingerprint"],
            "status": "active",
            "acquired_at": "2999-01-01T00:00:00-06:00",
            "expires_at": "2999-01-01T01:00:00-06:00",
            "previous_lease_commit": final["commit"],
        }
        future_commit = push_lease_record(future_record, final["commit"])
        self.cli("scheduler", "lease", "status", "--remote", "origin", expected=2)
        self.cli(
            "scheduler", "lease", "acquire", "--owner", "clock-skewed", "--goal-id", goal["goal_id"],
            "--remote", "origin", expected=2,
        )
        expired_record = {
            **future_record,
            "acquired_at": "2020-01-01T00:00:00-06:00",
            "expires_at": "2020-01-01T00:01:00-06:00",
            "previous_lease_commit": future_commit,
        }
        push_lease_record(expired_record, future_commit)
        expired = json.loads(self.cli("scheduler", "lease", "status", "--remote", "origin").stdout)
        self.assertEqual(expired["state"], "available")
        stale_recovery = json.loads(
            self.cli(
                "scheduler", "lease", "acquire", "--owner", "operator-three", "--goal-id", goal["goal_id"],
                "--remote", "origin",
            ).stdout
        )
        self.assertEqual(stale_recovery["previous_lease_commit"], expired["commit"])
        self.cli(
            "scheduler", "lease", "release", "--reason", "stale recovery complete", "--goal-id", goal["goal_id"],
            "--attempt-id", "1",
        )

    def test_encrypted_state_backup_verifies_and_restores_through_staging(self) -> None:
        fake_bin = self.root.parent / "fake-age-bin"
        fake_bin.mkdir()
        install_python_tool(
            fake_bin,
            "age",
            "import os,shutil,sys\nargs=sys.argv[1:]\nout=args[args.index('-o')+1]\nshutil.copyfile(args[-1],out)\nif os.environ.get('CONTINUITY_FAKE_AGE_FAIL') == '1' and '-d' not in args: raise SystemExit(9)\n",
        )
        identity = self.root.parent / "age-identity.txt"
        identity.write_text("fixture identity\n", encoding="utf-8")
        signer_key = self.root.parent / "backup-signer"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(signer_key)], check=True)
        self.cli("approval", "trust", "add", "--identity", "fixture-backup", "--public-key", str(signer_key) + ".pub")
        archive = self.root.parent / "state.tar.gz.age"
        original_path = os.environ.get("PATH", "")
        original_home = os.environ.get("HOME")
        original_userprofile = os.environ.get("USERPROFILE")
        os.environ["PATH"] = f"{fake_bin}{os.pathsep}{original_path}"
        os.environ["HOME"] = str(self.root.parent)
        os.environ["USERPROFILE"] = str(self.root.parent)
        try:
            first = self.create_capture()
            backed_up = json.loads(self.cli("state", "backup", "--recipient", "age1fixture", "--signer", "fixture-backup", "--signing-key", str(signer_key), "--verify-identity", str(identity), "--output", str(archive)).stdout)
            self.assertTrue(backed_up["encrypted"])
            self.assertTrue(backed_up["verification"]["verified"])
            original_archive_hash = runtime_lib.sha256_file(archive)
            self.cli(
                "state", "backup", "--recipient", "age1fixture", "--signer", "fixture-backup",
                "--signing-key", str(signer_key), "--verify-identity", str(identity),
                "--output", str(archive), expected=2,
            )
            self.assertEqual(runtime_lib.sha256_file(archive), original_archive_hash)

            def rewrite_archive(destination: Path, transform: object) -> None:
                with tarfile.open(archive, "r:gz") as source, tarfile.open(destination, "w:gz") as target:
                    for member in source.getmembers():
                        if not member.isfile():
                            target.addfile(member)
                            continue
                        extracted = source.extractfile(member)
                        self.assertIsNotNone(extracted)
                        data = extracted.read() if extracted is not None else b""
                        replacement = transform(member.name, data)
                        if replacement is None:
                            continue
                        item = tarfile.TarInfo(member.name)
                        item.size = len(replacement)
                        item.mode = member.mode
                        target.addfile(item, io.BytesIO(replacement))

            invalid_signature = self.root.parent / "invalid-signature.tar.gz.age"
            def alter_manifest(name: str, data: bytes) -> bytes:
                if name != "backup-manifest.json":
                    return data
                manifest = json.loads(data)
                manifest["created_at"] = "2026-07-16T00:00:00-05:00"
                return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
            rewrite_archive(invalid_signature, alter_manifest)
            self.cli("state", "verify", "--archive", str(invalid_signature), "--identity", str(identity), expected=2)

            incomplete = self.root.parent / "incomplete-backup.tar.gz.age"
            removed_payload = False
            def remove_payload(name: str, data: bytes) -> bytes | None:
                nonlocal removed_payload
                if name.startswith("payload/") and not removed_payload:
                    removed_payload = True
                    return None
                return data
            rewrite_archive(incomplete, remove_payload)
            self.assertTrue(removed_payload)
            self.cli("state", "verify", "--archive", str(incomplete), "--identity", str(identity), expected=2)

            tampered = self.root.parent / "tampered-backup.tar.gz.age"
            tampered_bytes = bytearray(archive.read_bytes())
            tampered_bytes[len(tampered_bytes) // 2] ^= 0xFF
            tampered.write_bytes(tampered_bytes)
            self.cli("state", "verify", "--archive", str(tampered), "--identity", str(identity), expected=2)
            interrupted_archive = self.root.parent / "interrupted backup with spaces.tar.gz.age"
            os.environ["CONTINUITY_FAKE_AGE_FAIL"] = "1"
            try:
                self.cli(
                    "state", "backup", "--recipient", "age1fixture", "--signer", "fixture-backup",
                    "--signing-key", str(signer_key), "--verify-identity", str(identity),
                    "--output", str(interrupted_archive), expected=2,
                )
            finally:
                os.environ.pop("CONTINUITY_FAKE_AGE_FAIL", None)
            self.assertFalse(interrupted_archive.exists())
            self.assertEqual(list(interrupted_archive.parent.glob(f".{interrupted_archive.name}.*.tmp")), [])
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
            self.cli("note", "capture", "--text", "Audit event created after the archived backup.")
            checkpoint = self.root.parent / "post-backup-checkpoint.json"
            self.cli(
                "state", "checkpoint-create", "--signer", "fixture-backup", "--signing-key", str(signer_key),
                "--output", str(checkpoint),
            )
            config = json.loads((self.root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            config["require_audit_checkpoints"] = True
            config["audit_checkpoint_path"] = str(checkpoint)
            self.write_json(self.root / ".continuity" / "config.json", config)
            self.cli(
                "state", "restore", "--archive", str(archive), "--identity", str(identity),
                "--recipient", "age1fixture", "--signer", "fixture-backup", "--signing-key", str(signer_key),
                "--dry-run", expected=2,
            )
        finally:
            os.environ["PATH"] = original_path
            if original_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original_home
            if original_userprofile is None:
                os.environ.pop("USERPROFILE", None)
            else:
                os.environ["USERPROFILE"] = original_userprofile

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

    def test_interrupted_restore_transaction_recovers_original_private_state(self) -> None:
        private = self.root / ".continuity" / "private"
        private.mkdir(parents=True, exist_ok=True)
        sentinel = private / "restore-recovery-sentinel.txt"
        sentinel.write_text("canonical-before-crash", encoding="utf-8")
        transaction = self.root / ".continuity-restore"
        previous = transaction / "previous" / ".continuity" / "private"
        previous.parent.mkdir(parents=True)
        os.replace(private, previous)
        private.mkdir(parents=True)
        partial = private / "partial-new-state.txt"
        partial.write_text("partial", encoding="utf-8")
        self.write_json(
            transaction / "transaction.json",
            {
                "schema_version": 1,
                "transaction_id": "restore-crash-fixture",
                "created_at": "2026-07-16T12:00:00Z",
                "replacements": [
                    {"path": ".continuity/private", "original_present": True, "restored_present": True},
                    {"path": ".continuity-portfolio", "original_present": False, "restored_present": False},
                ],
            },
        )
        doctor = json.loads(self.cli("project", "doctor").stdout)
        self.assertFalse(doctor["healthy"])
        self.assertTrue(doctor["restore_transaction"]["pending"])
        blocked = self.cli("note", "list", expected=2)
        self.assertIn("interrupted state restore blocks normal operation", blocked.stderr)
        recovered = json.loads(self.cli("state", "recover-restore").stdout)
        self.assertTrue(recovered["recovered"])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "canonical-before-crash")
        self.assertFalse(partial.exists())
        self.assertFalse(transaction.exists())

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
        special_workspace = self.root.parent / "Portfolio & root (quoted)'"
        special_workspace.mkdir()
        rendered = json.loads(self.cli("scheduler", "adapter", "codex", "render", "--root", str(special_workspace)).stdout)
        self.assertEqual(rendered["provider"], "codex")
        self.assertIn("portfolio actions", rendered["prompt"])
        self.assertEqual(
            rendered["literal_placeholders"],
            {
                "supervisor_task_id": "__CONTINUITY_SUPERVISOR_TASK_ID__",
                "sweep_id": "__CONTINUITY_SWEEP_ID__",
                "provider_task_id": "__CONTINUITY_PROVIDER_TASK_ID__",
                "markdown_escaping_forbidden": True,
            },
        )
        self.assertIn(json.dumps(rendered["supervisor_argv"], ensure_ascii=False, indent=2), rendered["prompt"])
        self.assertEqual(rendered["prompt"].count(rendered["literal_placeholders"]["supervisor_task_id"]), 1)
        self.assertEqual(rendered["prompt"].count(rendered["literal_placeholders"]["sweep_id"]), 1)
        self.assertNotIn("CONTINUITY\\_", rendered["prompt"])
        self.assertNotIn("**CONTINUITY", rendered["prompt"])
        self.assertIn("raw saved prompt", rendered["human_action_required"])
        self.assertFalse(rendered["shell_required"])
        self.assertTrue(rendered["cwd_independent"])
        entrypoint = (self.root / ".agents" / "continuity" / "bin" / "continuity").resolve()
        if os.name == "nt":
            configured_interpreter = (
                self.root / ".continuity" / "private" / "python-interpreter.txt"
            ).read_text(encoding="utf-8").strip()
            self.assertEqual(rendered["launcher"], str(Path(configured_interpreter).resolve()))
            self.assertEqual(rendered["supervisor_argv"][:2], [rendered["launcher"], str(entrypoint)])
        else:
            self.assertEqual(rendered["launcher"], str(entrypoint))
        self.assertIn(str(special_workspace.resolve()), rendered["supervisor_argv"])
        launcher_root = Path(rendered["launcher"]).parent
        install_python_tool(
            launcher_root,
            "continuity",
            "import json,sys\nprint(json.dumps(sys.argv[1:]))\n",
        )
        unrelated_cwd = self.root.parent / "unrelated cwd"
        unrelated_cwd.mkdir()
        transported = subprocess.run(
            rendered["supervisor_argv"],
            cwd=unrelated_cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(transported.stdout), rendered["supervisor_argv"][1:])
        self.assertIn("__CONTINUITY_PROVIDER_TASK_ID__", rendered["registration_argv"])
        if os.name == "nt":
            self.assertFalse(any(argument.endswith("continuity.cmd") for argument in rendered["supervisor_argv"][:2]))
            self.assertTrue(rendered["registration_command"].startswith("& '"))
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
        self.assertIn("product_audit_status", payload["projects"][0], payload)
        self.assertEqual(payload["projects"][0]["product_audit_status"], "attention")
        self.assertTrue(payload["projects"][0]["product_audit_baseline_required"])
        self.assertNotIn("Private customer", portfolio)
        self.assertNotIn(str(self.root), portfolio)

        config["scheduler"] = {**config["scheduler"], "provider": "claude-code"}
        self.write_json(self.root / ".continuity" / "config.json", config)
        manifest["scheduler"] = config["scheduler"]
        manifest["agent_surfaces"] = {"primary": "claude-code", "enabled": ["claude-code"]}
        self.write_json(manifest_path, manifest)
        claude_rendered = json.loads(
            self.cli("scheduler", "adapter", "claude-code", "render", "--root", str(special_workspace)).stdout
        )
        self.assertEqual(claude_rendered["provider"], "claude-code")
        self.assertEqual(claude_rendered["supervisor_argv"], rendered["supervisor_argv"])
        self.assertEqual(claude_rendered["literal_placeholders"], rendered["literal_placeholders"])
        self.assertIn(json.dumps(claude_rendered["supervisor_argv"], ensure_ascii=False, indent=2), claude_rendered["prompt"])
        self.assertEqual(claude_rendered["prompt"].count(claude_rendered["literal_placeholders"]["sweep_id"]), 1)
        self.assertIn("Claude Desktop local scheduled task", claude_rendered["human_action_required"])
        self.assertIn("Do not substitute a cloud routine", claude_rendered["human_action_required"])
        claude_verify = json.loads(self.cli("scheduler", "adapter", "claude-code", "verify").stdout)
        self.assertFalse(claude_verify["healthy"])
        self.assertTrue(any("registration" in problem for problem in claude_verify["problems"]))


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
            catalog_references: set[str] = set()
            if skill_dir.name == "continuity-design":
                catalog = json.loads((skill_dir / "references" / "catalog.json").read_text(encoding="utf-8"))
                catalog_references = {str(pack["reference"]) for pack in catalog["packs"]}
            for reference in local_references:
                self.assertTrue(
                    f"references/{reference.name}" in skill_text or reference.name in catalog_references,
                    f"{reference} is not linked from SKILL.md or the design catalog",
                )


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
            interpreter = root / ".continuity" / "private" / "python-interpreter.txt"
            baseline_interpreter = interpreter.read_bytes()
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
                self.assertEqual(interpreter.read_bytes(), baseline_interpreter, stage)
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
            self.assertEqual(first["suite_version"], "0.1.0-rc.3")
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
            legacy_root = root.parent / "legacy-project"
            shutil.copytree(root, legacy_root)
            shutil.rmtree(legacy_root / ".agents" / "continuity")
            legacy_control = legacy_root / ".agents" / "project-continuity" / "bin"
            legacy_control.mkdir(parents=True)
            (legacy_control / "continuity").write_text("legacy control\n", encoding="utf-8")
            shutil.rmtree(legacy_root / ".agents" / "skills" / "continuity-workflow")
            for command_root in (legacy_root / ".claude" / "commands", legacy_root / ".cursor" / "commands"):
                (command_root / "continuity-workflow.md").unlink(missing_ok=True)
            legacy_bootstrap_manifest_path = legacy_root / ".continuity" / "install-manifest.json"
            legacy_bootstrap_manifest = json.loads(legacy_bootstrap_manifest_path.read_text(encoding="utf-8"))
            legacy_bootstrap_manifest["installed_files"] = {
                path: digest
                for path, digest in legacy_bootstrap_manifest["installed_files"].items()
                if not path.startswith(".agents/continuity/") and "continuity-workflow" not in path
            }
            legacy_bootstrap_manifest_path.write_text(json.dumps(legacy_bootstrap_manifest, indent=2) + "\n", encoding="utf-8")
            config_after_first_install = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            self.assertFalse(config_after_first_install["require_signed_approvals"])
            self.assertFalse(config_after_first_install["github_cli_merge_enabled"])
            self.assertFalse((root / ".continuity" / "trusted-approvers").exists())
            legacy_behavior_path = root / ".continuity" / "project-behavior.json"
            legacy_behavior = json.loads(legacy_behavior_path.read_text(encoding="utf-8"))
            legacy_behavior["settings"].pop("github_cli_merge_enabled", None)
            legacy_behavior["settings"]["github_required_checks"] = None
            legacy_behavior["settings"]["github_required_reviewers"] = None
            legacy_behavior_path.write_text(json.dumps(legacy_behavior, indent=2) + "\n", encoding="utf-8")
            config_after_first_install.pop("github_cli_merge_enabled", None)
            config_after_first_install["github_required_checks"] = None
            config_after_first_install["github_required_reviewers"] = None
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
            self.assertEqual(preview_payload["counts"]["planned"], 2, preview_payload)
            self.assertFalse((root / ".agents" / "skills" / "continuity-workflow").exists())
            self.assertFalse((legacy_root / ".agents" / "continuity").exists())
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
            self.assertEqual(update_payload["status"], "completed", update_payload)
            self.assertEqual(update_payload["counts"]["updated"], 2)
            self.assertEqual({item["project_id"] for item in update_payload["projects"]}, {"sample-project"})
            self.assertTrue(all(item["after"]["healthy"] for item in update_payload["projects"]))
            self.assertTrue((legacy_root / ".agents" / "continuity" / "bin" / "continuity").is_file())
            self.assertFalse((legacy_root / ".agents" / "project-continuity").exists())
            self.assertTrue((legacy_root / ".agents" / "skills" / "continuity-workflow" / "SKILL.md").is_file())
            remove_tree(legacy_root)
            upgraded_config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
            upgraded_behavior = json.loads(legacy_behavior_path.read_text(encoding="utf-8"))
            self.assertFalse(upgraded_config["github_cli_merge_enabled"])
            self.assertEqual(upgraded_config["github_required_checks"], [])
            self.assertEqual(upgraded_config["github_required_reviewers"], 1)
            self.assertFalse(upgraded_behavior["settings"]["github_cli_merge_enabled"])
            self.assertEqual(upgraded_behavior["settings"]["github_required_checks"], [])
            self.assertEqual(upgraded_behavior["settings"]["github_required_reviewers"], 1)
            self.assertTrue(installed_skill_names.issubset({path.name for path in (root / ".agents" / "skills").iterdir() if path.is_dir()}))
            self.assertTrue(custom_skill.is_file())
            self.assertTrue((root / ".agents" / "skills" / "continuity-workflow" / "SKILL.md").is_file())
            upgraded_doctor = subprocess.run(
                [*installed_cli_args(root), "--project-root", str(root), "--json", "project", "doctor"],
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
            self.assertTrue((root / ".agents" / "skills" / "goal" / "SKILL.md").exists())
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
                self.assertTrue((command_root / "goal.md").exists())
                self.assertTrue((command_root / "continuity-capture.md").exists())
                self.assertTrue((command_root / "continuity-triage.md").exists())
                self.assertTrue((command_root / "continuity-workflow.md").exists())
                command_text = (command_root / "continuity-capture.md").read_text(encoding="utf-8")
                self.assertIn("Slash command: `/continuity-capture`", command_text)
                self.assertIn(".agents/skills/continuity-capture/SKILL.md", command_text)
                self.assertIn(".agents/skills/continuity-local/SKILL.md", command_text)
                self.assertIn("pause only at an explicit `human_required` approval boundary", command_text)
                goal_command = (command_root / "goal.md").read_text(encoding="utf-8")
                self.assertIn("Slash command: `/goal`", goal_command)
                self.assertIn("continue into coding without separate approval or start pauses", goal_command)
            self.assertTrue((root / ".agents" / "references" / "development-assurance-standard.md").exists())
            self.assertTrue((root / ".agents" / "references" / "workflow-handoffs.md").exists())
            self.assertTrue((root / ".agents" / "skills" / "continuity-plan" / "references" / "goal-planning-lenses.md").exists())
            default_skills = collection_skills("core", "projects")
            self.assertTrue((root / ".agents" / "skills" / "continuity-product-audit" / "SKILL.md").is_file())
            for source in (SUITE / "references").rglob("*"):
                if source.is_file():
                    self.assertTrue((root / ".agents" / "references" / source.relative_to(SUITE / "references")).is_file())
            for skill_source in (SUITE / "skills").iterdir():
                if not skill_source.is_dir():
                    continue
                if skill_source.name not in default_skills:
                    self.assertFalse((root / ".agents" / "skills" / skill_source.name).exists())
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
                [*installed_cli_args(root), "--project-root", str(root), "--json", "project", "recommendations"],
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
                    *installed_cli_args(root),
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
                    if skill_source.name not in default_skills:
                        self.assertFalse((surface_root / "skills" / skill_source.name).exists())
                        continue
                    for source in (skill_source / "references").glob("*"):
                        if source.is_file():
                            self.assertTrue((surface_root / "skills" / skill_source.name / "references" / source.name).is_file())
            self.assertEqual(json.loads((root / ".continuity" / "scheduler.json").read_text(encoding="utf-8"))["registration_state"], "requires-user-registration")
            registration = subprocess.run(
                [
                    *installed_cli_args(root),
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
                [*installed_cli_args(root), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(json.loads(stale_adapter_doctor.stdout)["healthy"])
            self.assertIn("Claude Code skill adapter is missing or stale", stale_adapter_doctor.stdout)
            subprocess.run(
                [
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
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
                [*installed_cli_args(root), "--project-root", str(root), "--json", "project", "doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(json.loads(drift_doctor.stdout)["healthy"])
            self.assertIn("drifted from project behavior", drift_doctor.stdout)
            subprocess.run(
                [
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
                    "--project-root", str(root), "scheduler", "register",
                    "--task-id", "supervisor-test-task", "--root", temp, "--actor", "repair-test",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            doctor = subprocess.run(
                [*installed_cli_args(root), "--project-root", str(root), "--json", "project", "doctor"],
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
            review_day = dt.datetime.now(ZoneInfo("America/Chicago")).date() + dt.timedelta(days=1)
            while review_day.weekday() >= 5:
                review_day += dt.timedelta(days=1)
            review_at = dt.datetime.combine(review_day, dt.time(20, 30), ZoneInfo("America/Chicago")).isoformat()
            actions = subprocess.run(
                [
                    "python3", str(CLI), "--json", "portfolio", "actions", "--root", temp,
                    "--action", "review", "--at", review_at,
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
                    *installed_cli_args(root),
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
                    *installed_cli_args(root),
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
                    "--action", "review", "--at", review_at,
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


class SecurityBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = runpy.run_path(str(CLI))
        cls.installer_api = runpy.run_path(str(INSTALLER))

    def test_external_selectors_reject_option_injection(self) -> None:
        error = self.api["ContinuityError"]
        for value in ("--upload-pack=owned", "https://example.test/repo", "../origin", "."):
            with self.subTest(remote=value), self.assertRaises(error):
                self.api["validate_git_remote_name"](value)
        for value in ("--repo", "latest", "1.2", "1.2.3;owned"):
            with self.subTest(version=value), self.assertRaises(error):
                self.api["validate_release_version"](value)
        self.assertEqual(self.api["validate_release_version"]("v1.2.3-rc.1"), "v1.2.3-rc.1")
        with self.assertRaises(error):
            self.api["validate_git_object_id"]("--format=%H")
        for value in ("--help", "main:owned", "refs/../owned", "branch.lock", "main\\owned"):
            with self.subTest(branch=value), self.assertRaises(error):
                self.api["validate_git_branch"](SUITE, value)
            with self.assertRaises(RuntimeError):
                self.installer_api["validate_git_branch"](SUITE, value)
        self.assertEqual(self.api["validate_git_branch"](SUITE, "main"), "main")

    def test_validation_commands_reject_shell_launchers(self) -> None:
        error = self.api["ContinuityError"]
        for command in (
            "cmd.exe /d /c echo owned",
            "powershell.exe -NoProfile -Command Get-ChildItem",
            "pwsh -Command Get-ChildItem",
            "bash -c 'echo owned'",
            "npm.cmd test",
            "tool.exe --token inline-secret",
        ):
            with self.subTest(command=command), self.assertRaises(error):
                self.api["command_argv"](command)
        self.assertEqual(self.api["command_argv"]("python -m unittest"), ["python", "-m", "unittest"])
        quoted = self.api["command_argv"](r'"C:\Program Files\Python\python.exe" -m unittest')
        self.assertEqual(quoted[0], r"C:\Program Files\Python\python.exe")

    def test_evidence_commands_filter_environment_and_redact_output(self) -> None:
        secret = "ghp_012345678901234567890123456789012345"
        with tempfile.TemporaryDirectory(prefix="continuity evidence ") as directory:
            root = Path(directory)
            script = root / "emit secret.py"
            script.write_text(
                "import os\nprint(os.environ.get('CONTINUITY_TEST_API_TOKEN', 'missing'))\n"
                f"print('token={secret}')\n",
                encoding="utf-8",
            )
            command = f'"{Path(sys.executable).as_posix()}" "{script.as_posix()}"'
            previous = os.environ.get("CONTINUITY_TEST_API_TOKEN")
            os.environ["CONTINUITY_TEST_API_TOKEN"] = secret
            try:
                result = self.api["execute_evidence_command"](command, root, 15)
            finally:
                if previous is None:
                    os.environ.pop("CONTINUITY_TEST_API_TOKEN", None)
                else:
                    os.environ["CONTINUITY_TEST_API_TOKEN"] = previous
            self.assertTrue(result["passed"], result)
            self.assertIn("missing", result["stdout"])
            self.assertIn("[REDACTED]", result["stdout"])
            self.assertNotIn(secret, json.dumps(result))

    def test_archive_extraction_rejects_windows_portability_hazards_and_stops_at_limit(self) -> None:
        error = self.api["ContinuityError"]

        def write_archive(path: Path, names: list[str]) -> None:
            with tarfile.open(path, "w") as archive:
                for name in names:
                    payload = b"x"
                    member = tarfile.TarInfo(name)
                    member.size = len(payload)
                    archive.addfile(member, io.BytesIO(payload))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, unsafe in enumerate(("../escape", "folder\\file", "CON.txt", "file.txt:stream", "trail.", "cafe\u0301.txt")):
                path = root / f"unsafe-{index}.tar"
                write_archive(path, [unsafe])
                with tarfile.open(path, "r") as archive, self.subTest(name=unsafe), self.assertRaises(error):
                    self.api["safe_extract_tar"](archive, root / f"extract-{index}", "Fixture archive")

            limited = root / "limited.tar"
            write_archive(limited, ["one.txt", "two.txt", "three.txt"])
            original_limit = self.api["MAX_ARCHIVE_FILES"]
            self.api["safe_extract_tar"].__globals__["MAX_ARCHIVE_FILES"] = 2
            try:
                with tarfile.open(limited, "r") as archive, self.assertRaisesRegex(error, "exceeds extraction limits"):
                    self.api["safe_extract_tar"](archive, root / "limited-extract", "Fixture archive")
            finally:
                self.api["safe_extract_tar"].__globals__["MAX_ARCHIVE_FILES"] = original_limit

            conflict = root / "file-directory-conflict.tar"
            write_archive(conflict, ["parent", "parent/child.txt"])
            with tarfile.open(conflict, "r") as archive, self.assertRaisesRegex(
                error, "uses a file as an archive directory: parent"
            ):
                self.api["safe_extract_tar"](archive, root / "conflict-extract", "Fixture archive")

    def test_remote_lease_retry_reconciles_published_acquisition_and_binding(self) -> None:
        config = {
            "project_id": "fixture-project",
            "private_dir": ".continuity/private",
            "timezone": "UTC",
            "scheduler": {"stale_after_minutes": 45},
        }
        owner_fingerprint = self.api["canonical_hash"]({"owner": "fixture-owner"})[:24]
        acquired = {
            "schema_version": 1,
            "project_id": "fixture-project",
            "goal_id": "goal-one",
            "attempt_id": "1",
            "owner_fingerprint": owner_fingerprint,
            "status": "active",
            "acquired_at": "2026-07-25T12:00:00+00:00",
            "expires_at": "2026-07-25T13:00:00+00:00",
            "previous_lease_commit": None,
        }
        writes: list[dict[str, object]] = []
        globals_map = self.api["scheduler_lease_acquire"].__globals__
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            globals_map,
            {
                "load_context": lambda: (Path(directory), config),
                "load_goal": lambda _root, _config, _goal_id: (Path(directory), {"execution_attempt": 1}),
                "remote_lease_record": lambda _root, _config, _remote: ("a" * 40, acquired),
                "remote_lease_is_protected": lambda _record, _config: True,
                "json_dump": lambda _path, value: writes.append(value),
                "append_jsonl": lambda _path, _value: None,
            },
        ):
            reconciled = self.api["scheduler_lease_acquire"](
                argparse.Namespace(
                    owner="fixture-owner",
                    goal_id="goal-one",
                    attempt_id=None,
                    remote="origin",
                    ttl_minutes=None,
                )
            )
        self.assertEqual(reconciled["lease_commit"], "a" * 40)
        self.assertEqual(writes[-1]["lease_commit"], "a" * 40)

        bound = {
            **acquired,
            "bound_run_id": "run-stable",
            "bound_task_id": "task-one",
            "bound_idempotency_key": "fixture:dispatch:one",
            "previous_lease_commit": "a" * 40,
        }
        writes.clear()
        with mock.patch.dict(
            self.api["bind_remote_lease_to_run"].__globals__,
            {
                "remote_lease_record": lambda _root, _config, _remote: ("b" * 40, bound),
                "json_dump": lambda _path, value: writes.append(value),
            },
        ):
            reconciled = self.api["bind_remote_lease_to_run"](
                Path("/fixture"),
                config,
                {**acquired, "remote": "origin", "lease_commit": "a" * 40},
                run_id="run-stable",
                task_id="task-one",
                idempotency_key="fixture:dispatch:one",
            )
        self.assertEqual(reconciled["lease_commit"], "b" * 40)
        self.assertEqual(writes[-1]["bound_run_id"], "run-stable")

    def test_rollback_validates_all_metadata_before_changing_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            victim = root / "victim.txt"
            victim.write_text("preserve", encoding="utf-8")
            snapshot = root / ".continuity" / "private" / "upgrades" / "20260717T120000Z"
            (snapshot / "payload").mkdir(parents=True)
            (snapshot / "snapshot.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "created_at": "2026-07-17T12:00:00+00:00",
                        "present": [{"path": "../escape.txt", "type": "file"}],
                        "absent": ["victim.txt"],
                        "prior_manifest": {},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                self.installer_api["restore_upgrade_snapshot"](root, snapshot)
            self.assertEqual(victim.read_text(encoding="utf-8"), "preserve")

    def test_rollback_rejects_colliding_overlapping_and_mismatched_snapshot_entries(self) -> None:
        valid = {"schema_version": 1, "present": [], "absent": [], "prior_manifest": {}}
        cases = {
            "mixed": {**valid, "present": ["one.txt", {"path": "two.txt", "type": "file"}]},
            "duplicate": {**valid, "present": [{"path": "same.txt", "type": "file"}], "absent": ["same.txt"]},
            "case-collision": {
                **valid,
                "present": [{"path": "Name.txt", "type": "file"}, {"path": "name.txt", "type": "file"}],
            },
            "overlap": {
                **valid,
                "present": [{"path": "parent", "type": "directory"}, {"path": "parent/child.txt", "type": "file"}],
            },
            "invalid-type": {**valid, "present": [{"path": "entry", "type": "device"}]},
        }
        for label, metadata in cases.items():
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                self.installer_api["_validated_snapshot_metadata"](metadata)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            victim = root / "victim.txt"
            victim.write_text("preserve", encoding="utf-8")
            snapshot = root / ".continuity" / "private" / "upgrades" / "20260717T130000Z"
            source = snapshot / "payload" / "expected-file.txt"
            source.mkdir(parents=True)
            (snapshot / "snapshot.json").write_text(
                json.dumps(
                    {
                        **valid,
                        "present": [{"path": "expected-file.txt", "type": "file"}],
                        "absent": ["victim.txt"],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "Invalid snapshot file source"):
                self.installer_api["restore_upgrade_snapshot"](root, snapshot)
            self.assertEqual(victim.read_text(encoding="utf-8"), "preserve")

    def test_windows_dependency_is_exactly_pinned_and_hashed(self) -> None:
        requirements = (SUITE / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("tzdata==2026.3", requirements)
        self.assertNotIn("tzdata>=", requirements)
        self.assertEqual(requirements.count("--hash=sha256:"), 2)

    @unittest.skipUnless(os.name == "nt", "Windows junction rollback boundary")
    def test_rollback_rejects_a_snapshot_junction(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_directory:
            root = Path(directory)
            upgrades = root / ".continuity" / "private" / "upgrades"
            upgrades.mkdir(parents=True)
            outside = Path(outside_directory)
            (outside / "payload").mkdir()
            (outside / "snapshot.json").write_text(
                json.dumps({"schema_version": 1, "present": [], "absent": [], "prior_manifest": {}}),
                encoding="utf-8",
            )
            junction = upgrades / "20260717T120000Z"
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            try:
                with self.assertRaisesRegex(RuntimeError, "junction"):
                    self.installer_api["restore_upgrade_snapshot"](root, junction)
            finally:
                os.rmdir(junction)


if __name__ == "__main__":
    unittest.main()
