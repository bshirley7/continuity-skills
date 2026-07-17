from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


SUITE = Path(__file__).resolve().parents[1]
CLI = SUITE / "bin" / "continuity"
sys.path.insert(0, str(SUITE / "lib"))
import github_projects  # noqa: E402
import roadmap  # noqa: E402
import runtime  # noqa: E402


class FakeGitHubClient:
    def __init__(self) -> None:
        self.fields = [
            {"id": "field-continuity", "name": "Continuity ID", "dataType": "TEXT"},
            {"id": "field-kind", "name": "Kind", "dataType": "SINGLE_SELECT", "options": [{"id": "kind-milestone", "name": "Milestone"}]},
            {"id": "field-status", "name": "Status", "dataType": "SINGLE_SELECT", "options": [{"id": "status-ready", "name": "Ready"}, {"id": "status-blocked", "name": "Blocked"}]},
            {"id": "field-health", "name": "Health", "dataType": "SINGLE_SELECT", "options": [{"id": "health-track", "name": "On track"}, {"id": "health-blocked", "name": "Blocked"}]},
            {"id": "field-start", "name": "Start date", "dataType": "DATE"},
            {"id": "field-target", "name": "Target date", "dataType": "DATE"},
            {"id": "field-parents", "name": "Parent IDs", "dataType": "TEXT"},
            {"id": "field-depends", "name": "Depends on", "dataType": "TEXT"},
        ]
        self.items: list[dict[str, Any]] = []
        self.calls: list[str] = []
        self.project = {
            "id": "project-node",
            "number": 12,
            "title": "Development Portfolio",
            "url": "https://github.com/orgs/example-org/projects/12",
        }

    def create_project(self, owner: str, title: str) -> dict[str, Any]:
        self.project["title"] = title
        self.calls.append(f"project-create:{owner}")
        return dict(self.project)

    def edit_project(self, number: int, owner: str, visibility: str, description: str) -> dict[str, Any]:
        self.project.update({"number": number, "public": visibility == "PUBLIC", "shortDescription": description})
        self.calls.append(f"project-edit:{owner}:{visibility}")
        return dict(self.project)

    def create_project_field(
        self,
        number: int,
        owner: str,
        name: str,
        data_type: str,
        options: list[str],
    ) -> dict[str, Any]:
        field = {"id": f"field-{len(self.fields) + 1}", "name": name, "dataType": data_type}
        if options:
            field["options"] = [
                {"id": f"option-{len(self.fields) + 1}-{index}", "name": option, "color": "GRAY", "description": ""}
                for index, option in enumerate(options)
            ]
        self.fields.append(field)
        self.calls.append(f"field-create:{name}")
        return field

    def _field_values(self, values: dict[str, str]) -> list[dict[str, Any]]:
        fields = {field["name"]: field for field in self.fields}
        result = []
        for name, value in values.items():
            field = fields[name]
            if field["dataType"] == "SINGLE_SELECT":
                option = next(option for option in field["options"] if option["name"] == value)
                result.append({"name": value, "optionId": option["id"], "field": {"name": name}})
            elif field["dataType"] == "DATE":
                result.append({"date": value, "field": {"name": name}})
            else:
                result.append({"text": value, "field": {"name": name}})
        return result

    def _project(self) -> dict[str, Any]:
        nodes = []
        for item in self.items:
            nodes.append(
                {
                    "id": item["id"],
                    "type": "DRAFT_ISSUE",
                    "content": dict(item["content"]),
                    "fieldValues": {"nodes": self._field_values(item["values"]), "pageInfo": {"hasNextPage": False}},
                }
            )
        return {
            "id": self.project["id"],
            "title": self.project["title"],
            "fields": {"nodes": self.fields, "pageInfo": {"hasNextPage": False}},
            "items": {"nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}},
        }

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if "updateProjectV2Field" in query:
            field = next(field for field in self.fields if field["id"] == variables["fieldId"])
            field["options"] = [
                {
                    "id": option.get("id", f"option-{field['id']}-{index}"),
                    "name": option["name"],
                    "color": option["color"],
                    "description": option["description"],
                }
                for index, option in enumerate(variables["options"])
            ]
            self.calls.append(f"field-options:{field['name']}")
            return {"updateProjectV2Field": {"projectV2Field": {"id": field["id"], "name": field["name"]}}}
        if "addProjectV2DraftIssue" in query:
            number = len(self.items) + 1
            item = {
                "id": f"item-{number}",
                "content": {"id": f"draft-{number}", "title": variables["title"], "body": variables["body"]},
                "values": {},
            }
            self.items.append(item)
            self.calls.append("create")
            return {"addProjectV2DraftIssue": {"projectV2Item": {"id": item["id"], "type": "DRAFT_ISSUE", "content": dict(item["content"])}}}
        if "updateProjectV2DraftIssue" in query:
            item = next(item for item in self.items if item["content"]["id"] == variables["draftIssueId"])
            item["content"].update({"title": variables["title"], "body": variables["body"]})
            self.calls.append("update-draft")
            return {"updateProjectV2DraftIssue": {"draftIssue": {"id": variables["draftIssueId"]}}}
        if "updateProjectV2ItemFieldValue" in query:
            item = next(item for item in self.items if item["id"] == variables["itemId"])
            field = next(field for field in self.fields if field["id"] == variables["fieldId"])
            value = variables["value"]
            if "singleSelectOptionId" in value:
                option = next(option for option in field["options"] if option["id"] == value["singleSelectOptionId"])
                item["values"][field["name"]] = option["name"]
            else:
                item["values"][field["name"]] = str(value.get("date", value.get("text")))
            self.calls.append(f"field:{field['name']}")
            return {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": item["id"]}}}
        if "clearProjectV2ItemFieldValue" in query:
            item = next(item for item in self.items if item["id"] == variables["itemId"])
            field = next(field for field in self.fields if field["id"] == variables["fieldId"])
            item["values"].pop(field["name"], None)
            self.calls.append(f"clear:{field['name']}")
            return {"clearProjectV2ItemFieldValue": {"projectV2Item": {"id": item["id"]}}}
        return {"owner": {"project": self._project()}}


class GitHubProjectsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.config = {
            "schema_version": 1,
            "assurance_standard_version": 2,
            "project_id": "test-project",
            "integration_branch": "main",
            "timezone": "America/Chicago",
            "private_dir": ".continuity/private",
            "memory_docs": "docs/project-memory",
            "roadmap_docs": "docs/project-roadmap",
            "planning_patterns": {
                "evidence_triage": "auto",
                "decision_mapping": "auto",
                "delivery_slicing": "auto",
                "tracker_provider": "github",
            },
        }
        self.write_json(self.root / ".continuity" / "config.json", self.config)
        self.write_settings()
        self.write_roadmap("RM-1", "Ship adapter", "ready")
        self.write_roadmap("RM-2", "Unapproved idea", "proposed")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def write_settings(self) -> None:
        self.write_json(
            self.root / ".continuity" / "github-projects.json",
            {
                "schema_version": 1,
                "provider": "github-projects",
                "owner_type": "organization",
                "owner": "example-org",
                "project_number": 7,
                "mode": "export-only",
                "item_mode": "draft-issue",
                "publish_statuses": ["ready", "blocked"],
                "fields": {
                    "continuity_id": "Continuity ID",
                    "kind": "Kind",
                    "status": "Status",
                    "health": "Health",
                    "start_date": "Start date",
                    "target_date": "Target date",
                    "parent_ids": "Parent IDs",
                    "depends_on": "Depends on",
                },
                "kind_options": {"milestone": "Milestone"},
                "status_options": {"ready": "Ready", "blocked": "Blocked"},
                "health_options": {"on-track": "On track", "blocked": "Blocked"},
            },
        )

    def write_roadmap(self, roadmap_id: str, title: str, status: str) -> None:
        target = self.root / "docs" / "project-roadmap" / "entities" / f"{roadmap_id}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        entry = roadmap.normalize_entry(
            {
                "roadmap_id": roadmap_id,
                "title": title,
                "kind": "milestone",
                "status": status,
                "summary": f"Canonical summary for {title}.",
                "parent_ids": [],
                "depends_on": [],
                "health": "on-track",
                "start_date": "2026-07-01",
                "target_date": "2026-08-01",
                "created_at": "2026-07-01T10:00:00-05:00",
                "updated_at": "2026-07-16T10:00:00-05:00",
            }
        )
        target.write_text(roadmap.render_entry(entry), encoding="utf-8")

    def build_plan(self) -> dict[str, Any]:
        return github_projects.build_plan(self.root, self.config, ".continuity/github-projects.json")

    def write_approval(self, plan: dict[str, Any]) -> None:
        runtime.atomic_write_json(
            github_projects.approval_path(self.root, self.config, plan["plan_hash"]),
            {
                "schema_version": 1,
                "project_id": "test-project",
                "plan_hash": plan["plan_hash"],
                "destination": plan["material"]["destination"],
                "approved_at": "2026-07-16T10:00:00-05:00",
                "approved_by": "fixture-user",
                "authorization_text": plan["authorization_text"],
                "nonce": "a" * 32,
                "signature_format": "legacy-unsigned",
            },
        )

    def write_bootstrap_approval(self, plan: dict[str, Any]) -> None:
        runtime.atomic_write_json(
            github_projects.bootstrap_approval_path(self.root, self.config, plan["plan_hash"]),
            {
                "schema_version": 1,
                "project_id": "test-project",
                "plan_hash": plan["plan_hash"],
                "destination": plan["material"]["destination"],
                "approved_at": "2026-07-16T10:00:00-05:00",
                "approved_by": "fixture-user",
                "authorization_text": plan["authorization_text"],
                "nonce": "b" * 32,
                "signature_format": "legacy-unsigned",
            },
        )

    def test_plan_is_deterministic_filtered_and_sanitized(self) -> None:
        first = self.build_plan()
        second = self.build_plan()
        self.assertEqual(first["plan_hash"], second["plan_hash"])
        self.assertEqual([item["roadmap_id"] for item in first["material"]["items"]], ["RM-1"])
        item = first["material"]["items"][0]
        self.assertEqual(item["continuity_id"], "test-project:RM-1")
        self.assertNotIn("note", item)
        self.assertIn("operational projection", item["body"])

    def test_stale_plan_is_rejected(self) -> None:
        plan = self.build_plan()
        self.write_roadmap("RM-1", "Changed title", "ready")
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, "changed after approval"):
            github_projects.load_plan(self.root, self.config, plan["plan_hash"], require_fresh=True)

    def test_approval_is_required_and_exact(self) -> None:
        plan = self.build_plan()
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, "requires an exact human approval"):
            github_projects.validate_approval(self.root, self.config, plan)
        self.write_approval(plan)
        receipt = github_projects.validate_approval(self.root, self.config, plan)
        self.assertEqual(receipt["approved_by"], "fixture-user")

    def test_apply_is_idempotent_and_inspection_is_non_authorizing(self) -> None:
        plan = self.build_plan()
        self.write_approval(plan)
        github_projects.validate_approval(self.root, self.config, plan)
        client = FakeGitHubClient()
        first = github_projects.apply(plan, client)
        self.assertEqual(first["created"], 1)
        self.assertGreater(first["updated_fields"], 0)
        second = github_projects.apply(plan, client)
        self.assertEqual(second["created"], 0)
        self.assertEqual(second["updated_drafts"], 0)
        self.assertEqual(second["updated_fields"], 0)
        self.assertEqual(second["unchanged"], 1)
        inspection = github_projects.inspect(plan, client)
        self.assertEqual(inspection["difference_count"], 0)
        self.assertFalse(inspection["remote_changes_authorize_canonical_updates"])
        client.items[0]["values"]["Status"] = "Blocked"
        drift = github_projects.inspect(plan, client)
        self.assertEqual(drift["difference_count"], 1)
        self.assertEqual(drift["differences"][0]["change"], "status")
        self.assertFalse(drift["remote_changes_authorize_canonical_updates"])

    def test_cli_approval_requires_exact_returned_text(self) -> None:
        plan_result = subprocess.run(
            ["python3", str(CLI), "--project-root", str(self.root), "--json", "roadmap", "github-projects", "plan"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=True,
        )
        plan = json.loads(plan_result.stdout)
        rejected = subprocess.run(
            [
                "python3", str(CLI), "--project-root", str(self.root), "--json", "roadmap", "github-projects", "approve", plan["plan_hash"],
                "--approved-by", "fixture-user", "--authorization-text", "approve something else",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)
        approved = subprocess.run(
            [
                "python3", str(CLI), "--project-root", str(self.root), "--json", "roadmap", "github-projects", "approve", plan["plan_hash"],
                "--approved-by", "fixture-user", "--authorization-text", plan["authorization_text"],
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=True,
        )
        self.assertEqual(json.loads(approved.stdout)["plan_hash"], plan["plan_hash"])

    def test_tracker_provider_must_be_github(self) -> None:
        self.config["planning_patterns"]["tracker_provider"] = "local"
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, "tracker_provider must be github"):
            self.build_plan()

    def test_missing_settings_fail_with_project_relative_path(self) -> None:
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, r"\.continuity/missing\.json"):
            github_projects.build_plan(self.root, self.config, ".continuity/missing.json")

    def test_bootstrap_creates_project_fields_settings_and_export_handoff(self) -> None:
        (self.root / ".continuity" / "github-projects.json").unlink()
        plan = github_projects.build_bootstrap_plan(
            self.root,
            self.config,
            owner_type="organization",
            owner="example-org",
            title="Test project roadmap",
            hostname="ghe.example.test",
        )
        self.assertEqual(plan["material"]["destination"]["host"], "ghe.example.test")
        field_names = {field["name"] for field in plan["material"]["fields"]}
        self.assertTrue({"Status", "Priority", "Phase", "Continuity ID"}.issubset(field_names))
        self.write_bootstrap_approval(plan)
        github_projects.validate_bootstrap_approval(self.root, self.config, plan)
        client = FakeGitHubClient()
        result = github_projects.apply_bootstrap(self.root, self.config, plan, client)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["destination"]["project_number"], 12)
        settings = json.loads((self.root / ".continuity" / "github-projects.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["project_number"], 12)
        self.assertEqual(settings["host"], "ghe.example.test")
        self.assertIn("field-create:Priority", client.calls)
        self.assertIn("field-create:Phase", client.calls)
        self.assertIn("field-options:Status", client.calls)
        export = github_projects.load_plan(self.root, self.config, result["export_plan_hash"])
        self.assertEqual(export["material"]["destination"]["project_number"], 12)
        again = github_projects.apply_bootstrap(self.root, self.config, plan, client)
        self.assertEqual(again["export_plan_hash"], result["export_plan_hash"])

    def test_bootstrap_requires_exact_approval(self) -> None:
        (self.root / ".continuity" / "github-projects.json").unlink()
        plan = github_projects.build_bootstrap_plan(
            self.root,
            self.config,
            owner_type="user",
            owner="fixture-user",
        )
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, "requires an exact human approval"):
            github_projects.validate_bootstrap_approval(self.root, self.config, plan)
        self.write_bootstrap_approval(plan)
        receipt = github_projects.validate_bootstrap_approval(self.root, self.config, plan)
        self.assertEqual(receipt["plan_hash"], plan["plan_hash"])

    def test_cli_bootstrap_plan_and_approval(self) -> None:
        (self.root / ".continuity" / "github-projects.json").unlink()
        planned = subprocess.run(
            [
                "python3", str(CLI), "--project-root", str(self.root), "--json",
                "roadmap", "github-projects", "bootstrap", "plan",
                "--owner-type", "organization", "--owner", "example-org",
                "--title", "Test project roadmap",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=True,
        )
        plan = json.loads(planned.stdout)
        approved = subprocess.run(
            [
                "python3", str(CLI), "--project-root", str(self.root), "--json",
                "roadmap", "github-projects", "bootstrap", "approve", plan["plan_hash"],
                "--approved-by", "fixture-user", "--authorization-text", plan["authorization_text"],
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=True,
        )
        self.assertEqual(json.loads(approved.stdout)["plan_hash"], plan["plan_hash"])

    def test_github_client_uses_gh_project_commands(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps({"id": "PVT_test", "number": 4}),
            stderr="",
        )
        authenticated = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="enterprise-user\n",
            stderr="",
        )

        def fake_run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            return authenticated if command[1:3] == ["api", "user"] else completed

        with mock.patch.object(subprocess, "run", side_effect=fake_run) as run:
            client = github_projects.GitHubClient("/usr/local/bin/gh", host="ghe.example.test")
            client.create_project("example-org", "Roadmap")
            self.assertEqual(
                run.call_args.args[0],
                [
                    "/usr/local/bin/gh", "project", "create", "--owner", "example-org",
                    "--title", "Roadmap", "--format", "json",
                ],
            )
            self.assertEqual(run.call_args.kwargs["env"]["GH_HOST"], "ghe.example.test")
            self.assertEqual(client.authenticated_login, "enterprise-user")
            client.create_project_field(4, "example-org", "Priority", "SINGLE_SELECT", ["High", "Low"])
            self.assertEqual(
                run.call_args.args[0],
                [
                    "/usr/local/bin/gh", "project", "field-create", "4", "--owner", "example-org",
                    "--name", "Priority", "--data-type", "SINGLE_SELECT", "--format", "json",
                    "--single-select-options", "High,Low",
                ],
            )

    def test_bootstrap_retry_reuses_checkpointed_project(self) -> None:
        (self.root / ".continuity" / "github-projects.json").unlink()
        plan = github_projects.build_bootstrap_plan(
            self.root,
            self.config,
            owner_type="organization",
            owner="example-org",
        )
        self.write_bootstrap_approval(plan)
        client = FakeGitHubClient()
        original_edit = client.edit_project
        failures = 0

        def fail_once(number: int, owner: str, visibility: str, description: str) -> dict[str, Any]:
            nonlocal failures
            if failures == 0:
                failures += 1
                raise github_projects.GitHubProjectsError("simulated edit failure")
            return original_edit(number, owner, visibility, description)

        client.edit_project = fail_once  # type: ignore[method-assign]
        with self.assertRaisesRegex(github_projects.GitHubProjectsError, "simulated edit failure"):
            github_projects.apply_bootstrap(self.root, self.config, plan, client)
        result = github_projects.apply_bootstrap(self.root, self.config, plan, client)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(client.calls.count("project-create:example-org"), 1)


if __name__ == "__main__":
    unittest.main()
