"""Durably connected GitHub Projects projection for roadmap and goal status."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

import roadmap
import runtime


class GitHubProjectsError(RuntimeError):
    pass


FIELD_TYPES = {
    "continuity_id": "TEXT",
    "kind": "SINGLE_SELECT",
    "status": "SINGLE_SELECT",
    "health": "SINGLE_SELECT",
    "priority": "SINGLE_SELECT",
    "phase": "SINGLE_SELECT",
    "start_date": "DATE",
    "target_date": "DATE",
    "parent_ids": "TEXT",
    "depends_on": "TEXT",
}
REQUIRED_FIELD_KEYS = {"continuity_id", "kind", "status", "health"}
OPTION_FIELD_KEYS = {"kind", "status", "health", "priority", "phase"}
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"
OPTION_COLORS = ("GRAY", "BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PURPLE", "PINK")
REQUIRED_CONNECTION_SCOPES = {"project"}
CONNECTION_CAPABILITIES = {
    "read": True,
    "write": True,
    "create_project": True,
    "edit_project": True,
    "create_item": True,
    "edit_item": True,
    "delete_item": False,
}
GOAL_STATUS_MAP = {
    "proposed-plan": "proposed",
    "awaiting-feedback": "planned",
    "approved": "planned",
    "queued": "planned",
    "held": "paused",
    "dispatched": "in-progress",
    "running": "in-progress",
    "validating": "validating",
    "review-ready": "validating",
    "changes-requested": "in-progress",
    "partially-completed": "at-risk",
    "blocked": "blocked",
    "completed": "completed",
    "cancelled": "cancelled",
}
GOAL_HEALTH_MAP = {
    "held": "unknown",
    "changes-requested": "at-risk",
    "partially-completed": "at-risk",
    "blocked": "blocked",
    "completed": "complete",
    "cancelled": "complete",
}


def _github_host(value: Any) -> str:
    host = str(value or "github.com").strip().lower()
    labels = host.split(".")
    if (
        len(host) > 253
        or any(not label or len(label) > 63 or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) for label in labels)
    ):
        raise GitHubProjectsError("GitHub hostname must be a canonical hostname without a scheme or path")
    return host


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _confined(root: Path, value: str, label: str) -> Path:
    try:
        relative = Path(runtime.validate_portable_relative_path(value, label=label))
    except runtime.RuntimeIntegrityError as exc:
        raise GitHubProjectsError(str(exc)) from exc
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise GitHubProjectsError(f"{label} escapes the project root")
    return target


def _private_root(root: Path, config: dict[str, Any]) -> Path:
    return _confined(root, str(config.get("private_dir", ".continuity/private")), "private_dir")


def connection_path(root: Path, config: dict[str, Any]) -> Path:
    return _private_root(root, config) / "integrations" / "github-projects" / "connection.json"


def load_connection(root: Path, config: dict[str, Any], *, required: bool = True) -> dict[str, Any] | None:
    path = connection_path(root, config)
    if not path.is_file():
        if required:
            raise GitHubProjectsError("GitHub Projects is not connected; run roadmap github-projects connect")
        return None
    value = _load_json(path)
    _validate_schema(value, "github-projects-connection.schema.json", "GitHub Projects connection")
    if not isinstance(value, dict) or value.get("project_id") != config.get("project_id"):
        raise GitHubProjectsError("GitHub Projects connection belongs to a different Continuity project")
    _github_host(value.get("destination", {}).get("host", "github.com"))
    return value


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GitHubProjectsError(f"Unable to read JSON from {path}: {exc}") from exc


def _string_map(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or any(
        not isinstance(key, str) or not key.strip() or not isinstance(item, str) or not item.strip()
        for key, item in value.items()
    ):
        raise GitHubProjectsError(f"{label} must be an object of non-empty string mappings")
    return {str(key): str(item) for key, item in value.items()}


def _validate_schema(value: Any, name: str, label: str) -> None:
    try:
        runtime.validate_schema_file(value, SCHEMA_ROOT / name, label)
    except runtime.RuntimeIntegrityError as exc:
        raise GitHubProjectsError(str(exc)) from exc


def load_settings(root: Path, config: dict[str, Any], settings_value: str) -> tuple[Path, dict[str, Any]]:
    if config.get("planning_patterns", {}).get("tracker_provider") != "github":
        raise GitHubProjectsError("Project tracker_provider must be github before preparing a GitHub Projects export")
    path = _confined(root, settings_value, "GitHub Projects settings")
    if not path.is_file():
        raise GitHubProjectsError(f"GitHub Projects settings are unavailable: {path.relative_to(root.resolve()).as_posix()}")
    value = _load_json(path)
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise GitHubProjectsError("GitHub Projects settings require schema_version 1")
    _validate_schema(value, "github-projects-settings.schema.json", "GitHub Projects settings")
    if value.get("provider") != "github-projects" or value.get("mode") != "export-only":
        raise GitHubProjectsError("GitHub Projects settings must use provider github-projects and mode export-only")
    if value.get("item_mode") != "draft-issue":
        raise GitHubProjectsError("The first GitHub Projects adapter supports item_mode draft-issue only")
    value = dict(value)
    value["host"] = _github_host(value.get("host"))
    if value.get("owner_type") not in {"organization", "user"}:
        raise GitHubProjectsError("owner_type must be organization or user")
    owner = value.get("owner")
    if not isinstance(owner, str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", owner):
        raise GitHubProjectsError("owner must be a valid GitHub login")
    if not isinstance(value.get("project_number"), int) or value["project_number"] < 1:
        raise GitHubProjectsError("project_number must be a positive integer")
    publish_statuses = value.get("publish_statuses")
    if not isinstance(publish_statuses, list) or not publish_statuses or any(
        not isinstance(item, str) or item not in roadmap.ROADMAP_STATUSES for item in publish_statuses
    ):
        raise GitHubProjectsError("publish_statuses must explicitly list supported roadmap statuses")
    if len(publish_statuses) != len(set(publish_statuses)):
        raise GitHubProjectsError("publish_statuses must not contain duplicates")
    fields = _string_map(value.get("fields"), "fields")
    missing = sorted(REQUIRED_FIELD_KEYS - set(fields))
    unknown = sorted(set(fields) - set(FIELD_TYPES))
    if missing or unknown:
        raise GitHubProjectsError(f"GitHub Projects fields are invalid; missing={missing}, unknown={unknown}")
    value["fields"] = fields
    value["kind_options"] = _string_map(value.get("kind_options"), "kind_options")
    value["status_options"] = _string_map(value.get("status_options"), "status_options")
    value["health_options"] = _string_map(value.get("health_options"), "health_options")
    for key in ("priority", "phase"):
        map_name = f"{key}_options"
        if key in fields:
            value[map_name] = _string_map(value.get(map_name), map_name)
    return path, value


def _export_entry(project_id: str, entry: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    roadmap_id = str(entry["roadmap_id"])
    selected = {
        "roadmap_id": roadmap_id,
        "title": str(entry["title"]),
        "summary": str(entry["summary"]),
        "kind": str(entry["kind"]),
        "status": str(entry["status"]),
        "health": str(entry.get("health", "unknown")),
        "priority": str(entry.get("priority") or "unprioritized"),
        "parent_ids": sorted(str(item) for item in entry.get("parent_ids", [])),
        "depends_on": sorted(str(item) for item in entry.get("depends_on", [])),
        "start_date": entry.get("start_date"),
        "target_date": entry.get("target_date"),
        "path": str(entry["path"]),
    }
    for key, map_name in (
        ("kind", "kind_options"),
        ("status", "status_options"),
        ("health", "health_options"),
        ("priority", "priority_options"),
        ("phase", "phase_options"),
    ):
        if key not in settings["fields"]:
            continue
        source_value = selected["status"] if key == "phase" else selected[key]
        if source_value not in settings[map_name]:
            raise GitHubProjectsError(f"{map_name} does not map {source_value!r} for {roadmap_id}")
    revision = _hash(selected)
    continuity_id = f"{project_id}:{roadmap_id}"
    body_lines = [
        str(selected["summary"]),
        "",
        "## Continuity roadmap projection",
        "",
        f"- Continuity ID: `{continuity_id}`",
        f"- Kind: `{selected['kind']}`",
        f"- Status: `{selected['status']}`",
        f"- Health: `{selected['health']}`",
        f"- Priority: `{selected['priority']}`",
        f"- Parents: {', '.join(selected['parent_ids']) or 'none'}",
        f"- Dependencies: {', '.join(selected['depends_on']) or 'none'}",
        f"- Canonical source: `{selected['path']}`",
        "",
        "This item is an operational projection. Canonical roadmap changes require Continuity reconciliation and approval.",
        "",
        f"<!-- continuity-project:{project_id};roadmap:{roadmap_id};revision:{revision} -->",
    ]
    fields: dict[str, str | None] = {"continuity_id": continuity_id}
    for key in OPTION_FIELD_KEYS:
        if key not in settings["fields"]:
            continue
        source_value = selected["status"] if key == "phase" else selected[key]
        fields[key] = settings[f"{key}_options"][source_value]
    for key in ("start_date", "target_date"):
        if key in settings["fields"]:
            fields[key] = str(selected[key]) if selected[key] else None
    for key in ("parent_ids", "depends_on"):
        if key in settings["fields"]:
            fields[key] = ", ".join(selected[key])
    return {
        "continuity_id": continuity_id,
        "roadmap_id": roadmap_id,
        "projection_type": "roadmap",
        "source_revision": revision,
        "title": selected["title"],
        "body": "\n".join(body_lines),
        "fields": fields,
    }


def _goal_records(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    goals_root = _private_root(root, config) / "goals"
    records: list[dict[str, Any]] = []
    if not goals_root.is_dir():
        return records
    for path in sorted(goals_root.glob("*/goal.json")):
        value = _load_json(path)
        if isinstance(value, dict) and value.get("goal_id") and value.get("title"):
            records.append(value)
    return records


def _export_goal(project_id: str, goal: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    goal_id = str(goal["goal_id"])
    state = str(goal.get("state", "awaiting-feedback"))
    status = GOAL_STATUS_MAP.get(state, "at-risk")
    health = GOAL_HEALTH_MAP.get(state, "on-track")
    raw_priority = str(goal.get("priority") or "normal").casefold()
    priority = {
        "urgent": "high",
        "critical": "critical",
        "high": "high",
        "normal": "medium",
        "medium": "medium",
        "low": "low",
    }.get(raw_priority, "unprioritized")
    kind = "story"
    selected = {
        "goal_id": goal_id,
        "title": str(goal["title"]),
        "plan_version": int(goal.get("plan_version", 1)),
        "plan_hash": str(goal.get("plan_hash") or "unavailable"),
        "execution_attempt": int(goal.get("execution_attempt", 1)),
        "kind": kind,
        "status": status,
        "health": health,
        "priority": priority,
        "roadmap_ids": sorted(str(item) for item in goal.get("roadmap_ids", [])),
        "depends_on": sorted(str(item) for item in goal.get("depends_on", [])),
    }
    for key, source_value in (
        ("kind", kind),
        ("status", status),
        ("health", health),
        ("priority", priority),
        ("phase", status),
    ):
        if key in settings["fields"] and source_value not in settings[f"{key}_options"]:
            raise GitHubProjectsError(f"{key}_options does not map {source_value!r} for goal {goal_id}")
    revision = _hash(selected)
    continuity_id = f"{project_id}:goal:{goal_id}"
    body_lines = [
        "Continuity task status projection.",
        "",
        "## Current state",
        "",
        f"- Goal: `{goal_id}`",
        f"- Plan version: `{selected['plan_version']}`",
        f"- Execution attempt: `{selected['execution_attempt']}`",
        f"- Status: `{state}`",
        f"- Roadmap: {', '.join(selected['roadmap_ids']) or 'none'}",
        f"- Dependencies: {', '.join(selected['depends_on']) or 'none'}",
        "",
        "This card contains sanitized operational status only. Captured notes, request text, approval text, and private evidence are not published.",
        "Remote edits are reconciliation proposals and cannot authorize or complete local work.",
        "",
        f"<!-- continuity-project:{project_id};goal:{goal_id};revision:{revision} -->",
    ]
    fields: dict[str, str | None] = {"continuity_id": continuity_id}
    for key, source_value in (
        ("kind", kind),
        ("status", status),
        ("health", health),
        ("priority", priority),
        ("phase", status),
    ):
        if key in settings["fields"]:
            fields[key] = settings[f"{key}_options"][source_value]
    if "parent_ids" in settings["fields"]:
        fields["parent_ids"] = ", ".join(selected["roadmap_ids"])
    if "depends_on" in settings["fields"]:
        fields["depends_on"] = ", ".join(selected["depends_on"])
    for key in ("start_date", "target_date"):
        if key in settings["fields"]:
            fields[key] = None
    return {
        "continuity_id": continuity_id,
        "goal_id": goal_id,
        "projection_type": "goal",
        "source_revision": revision,
        "title": selected["title"],
        "body": "\n".join(body_lines),
        "fields": fields,
    }


def plan_material(root: Path, config: dict[str, Any], settings_path: Path, settings: dict[str, Any]) -> dict[str, Any]:
    selected = [
        item
        for item in roadmap.entries(root, config)
        if item.get("status") in set(settings["publish_statuses"])
    ]
    items = [_export_entry(str(config["project_id"]), item, settings) for item in selected]
    connection = load_connection(root, config, required=False)
    projections = ["roadmap"]
    connection_id = None
    if connection is not None:
        destination = connection["destination"]
        if (
            destination["owner_type"] != settings["owner_type"]
            or destination["owner"].casefold() != str(settings["owner"]).casefold()
            or destination["project_number"] != settings["project_number"]
        ):
            raise GitHubProjectsError("GitHub Projects settings do not match the durable connection destination")
        projections = list(connection["sync_policy"]["projections"])
        connection_id = connection["connection_id"]
        if "goals" in projections:
            publish_statuses = set(settings["publish_statuses"])
            items.extend(
                _export_goal(str(config["project_id"]), goal, settings)
                for goal in _goal_records(root, config)
                if GOAL_STATUS_MAP.get(str(goal.get("state")), "at-risk") in publish_statuses
            )
    items.sort(key=lambda item: item["continuity_id"])
    return {
        "schema_version": 1,
        "provider": "github-projects",
        "project_id": str(config["project_id"]),
        "assurance_standard_version": config.get("assurance_standard_version"),
        "behavior_configuration_hash": config.get("behavior_configuration_hash"),
        "destination": {
            "host": settings["host"],
            "owner_type": settings["owner_type"],
            "owner": settings["owner"],
            "project_number": settings["project_number"],
        },
        "settings_path": runtime.project_relative_posix(settings_path, root),
        "mode": "export-only",
        "item_mode": "draft-issue",
        "connection_id": connection_id,
        "projections": projections,
        "publish_statuses": list(settings["publish_statuses"]),
        "field_names": dict(settings["fields"]),
        "items": items,
    }


def authorization_text(plan_hash: str, destination: dict[str, Any]) -> str:
    return (
        f"Approve GitHub Projects export {plan_hash} to "
        f"{destination['host']}/{destination['owner_type']}:{destination['owner']}#{destination['project_number']}"
    )


def plan_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{64}", plan_hash):
        raise GitHubProjectsError("plan_hash must be a 64-character lowercase SHA-256 value")
    return _private_root(root, config) / "integrations" / "github-projects" / "plans" / f"{plan_hash}.json"


def approval_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    return _private_root(root, config) / "integrations" / "github-projects" / "approvals" / f"{plan_hash}.json"


def signature_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    return approval_path(root, config, plan_hash).with_suffix(".sig")


def build_plan(root: Path, config: dict[str, Any], settings_value: str) -> dict[str, Any]:
    settings_path, settings = load_settings(root, config, settings_value)
    material = plan_material(root, config, settings_path, settings)
    digest = _hash(material)
    target = plan_path(root, config, digest)
    if target.is_file():
        existing = _load_json(target)
        if not isinstance(existing, dict) or existing.get("material") != material:
            raise GitHubProjectsError("Stored GitHub Projects plan does not match its plan hash")
        return existing
    plan = {
        "schema_version": 1,
        "plan_hash": digest,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "authorization_text": authorization_text(digest, material["destination"]),
        "material": material,
    }
    _validate_schema(plan, "github-projects-export-plan.schema.json", "GitHub Projects export plan")
    runtime.atomic_write_json(target, plan)
    return plan


def load_plan(root: Path, config: dict[str, Any], plan_hash: str, *, require_fresh: bool = False) -> dict[str, Any]:
    target = plan_path(root, config, plan_hash)
    if not target.is_file():
        raise GitHubProjectsError(f"GitHub Projects export plan is unavailable: {plan_hash}")
    value = _load_json(target)
    _validate_schema(value, "github-projects-export-plan.schema.json", "GitHub Projects export plan")
    if not isinstance(value, dict) or value.get("plan_hash") != plan_hash or _hash(value.get("material")) != plan_hash:
        raise GitHubProjectsError("GitHub Projects export plan failed its content hash")
    if require_fresh:
        material = value["material"]
        settings_path, settings = load_settings(root, config, str(material["settings_path"]))
        current = plan_material(root, config, settings_path, settings)
        if _hash(current) != plan_hash:
            raise GitHubProjectsError("Canonical roadmap or GitHub Projects settings changed after approval; prepare a new plan")
    return value


def approval_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    keys = (
        "schema_version",
        "project_id",
        "plan_hash",
        "destination",
        "behavior_configuration_hash",
        "approved_at",
        "approved_by",
        "authorization_text",
        "nonce",
    )
    material = {key: receipt[key] for key in keys if key in receipt}
    return (_canonical_json(material) + "\n").encode()


def validate_approval(
    root: Path,
    config: dict[str, Any],
    plan: dict[str, Any],
    verify_signature: Callable[[bytes, Path, str], Any] | None = None,
) -> dict[str, Any]:
    path = approval_path(root, config, plan["plan_hash"])
    if not path.is_file():
        raise GitHubProjectsError("GitHub Projects export requires an exact human approval receipt")
    receipt = _load_json(path)
    _validate_schema(receipt, "github-projects-approval.schema.json", "GitHub Projects approval")
    expected_text = plan["authorization_text"]
    expected = {
        "project_id": config["project_id"],
        "plan_hash": plan["plan_hash"],
        "destination": plan["material"]["destination"],
        "authorization_text": expected_text,
        "behavior_configuration_hash": config.get("behavior_configuration_hash"),
    }
    mismatches = sorted(key for key, value in expected.items() if receipt.get(key) != value)
    if receipt.get("schema_version") != 1 or mismatches:
        raise GitHubProjectsError(f"GitHub Projects approval is stale or mismatched: {mismatches}")
    if config.get("require_signed_approvals", False):
        if receipt.get("signature_format") != "openssh-sshsig-v1" or verify_signature is None:
            raise GitHubProjectsError("This project requires a signed GitHub Projects export approval")
        verify_signature(approval_receipt_bytes(receipt), signature_path(root, config, plan["plan_hash"]), str(receipt.get("approved_by", "")))
    return receipt


def bootstrap_plan_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{64}", plan_hash):
        raise GitHubProjectsError("plan_hash must be a 64-character lowercase SHA-256 value")
    return _private_root(root, config) / "integrations" / "github-projects" / "bootstrap" / "plans" / f"{plan_hash}.json"


def bootstrap_approval_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    return _private_root(root, config) / "integrations" / "github-projects" / "bootstrap" / "approvals" / f"{plan_hash}.json"


def bootstrap_signature_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    return bootstrap_approval_path(root, config, plan_hash).with_suffix(".sig")


def bootstrap_application_path(root: Path, config: dict[str, Any], plan_hash: str) -> Path:
    return _private_root(root, config) / "integrations" / "github-projects" / "bootstrap" / "applications" / f"{plan_hash}.json"


def _unique(values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        item = str(value)
        if item not in result:
            result.append(item)
    return result


def _bootstrap_field_specs(settings: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for key, name in settings["fields"].items():
        options = _unique(settings.get(f"{key}_options", {}).values()) if key in OPTION_FIELD_KEYS else []
        specs.append({"key": key, "name": name, "data_type": FIELD_TYPES[key], "options": options})
    required_names = {"Status", "Priority", "Phase", "Continuity ID"}
    missing = sorted(required_names - {spec["name"] for spec in specs})
    if missing:
        raise GitHubProjectsError(f"GitHub Projects bootstrap template is missing required fields: {missing}")
    return specs


def build_bootstrap_plan(
    root: Path,
    config: dict[str, Any],
    *,
    owner_type: str,
    owner: str,
    title: str | None = None,
    visibility: str = "PRIVATE",
    settings_value: str = ".continuity/github-projects.json",
    hostname: str = "github.com",
) -> dict[str, Any]:
    if config.get("planning_patterns", {}).get("tracker_provider") != "github":
        raise GitHubProjectsError("Project tracker_provider must be github before preparing a GitHub Projects bootstrap")
    if owner_type not in {"organization", "user"}:
        raise GitHubProjectsError("owner_type must be organization or user")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", owner):
        raise GitHubProjectsError("owner must be a valid GitHub login")
    hostname = _github_host(hostname)
    visibility = visibility.upper()
    if visibility not in {"PRIVATE", "PUBLIC"}:
        raise GitHubProjectsError("visibility must be PRIVATE or PUBLIC")
    settings_path = _confined(root, settings_value, "GitHub Projects settings")
    if settings_path.exists():
        raise GitHubProjectsError(f"GitHub Projects settings already exist: {runtime.project_relative_posix(settings_path, root)}")
    template = _load_json(TEMPLATE_ROOT / "github-projects-settings.json")
    if not isinstance(template, dict):
        raise GitHubProjectsError("GitHub Projects settings template is invalid")
    settings = dict(template)
    settings.update({"host": hostname, "owner_type": owner_type, "owner": owner})
    settings.pop("project_number", None)
    project_title = (title or f"{config['project_id']} roadmap").strip()
    if not project_title or len(project_title) > 256:
        raise GitHubProjectsError("GitHub Project title must contain 1 to 256 characters")
    material = {
        "schema_version": 1,
        "provider": "github-projects",
        "operation": "bootstrap",
        "project_id": str(config["project_id"]),
        "destination": {"host": hostname, "owner_type": owner_type, "owner": owner},
        "project": {
            "title": project_title,
            "visibility": visibility,
            "description": f"Continuity operational roadmap projection for {config['project_id']}",
        },
        "settings_path": runtime.project_relative_posix(settings_path, root),
        "settings": settings,
        "fields": _bootstrap_field_specs(settings),
    }
    digest = _hash(material)
    target = bootstrap_plan_path(root, config, digest)
    if target.is_file():
        existing = _load_json(target)
        if not isinstance(existing, dict) or existing.get("material") != material:
            raise GitHubProjectsError("Stored GitHub Projects bootstrap plan does not match its plan hash")
        return existing
    plan = {
        "schema_version": 1,
        "plan_hash": digest,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "authorization_text": (
            f"Approve GitHub Projects bootstrap {digest} to create {visibility} project "
            f"{project_title!r} on {hostname} for {owner_type}:{owner}"
        ),
        "material": material,
    }
    _validate_schema(plan, "github-projects-bootstrap-plan.schema.json", "GitHub Projects bootstrap plan")
    runtime.atomic_write_json(target, plan)
    return plan


def load_bootstrap_plan(root: Path, config: dict[str, Any], plan_hash: str) -> dict[str, Any]:
    target = bootstrap_plan_path(root, config, plan_hash)
    if not target.is_file():
        raise GitHubProjectsError(f"GitHub Projects bootstrap plan is unavailable: {plan_hash}")
    value = _load_json(target)
    _validate_schema(value, "github-projects-bootstrap-plan.schema.json", "GitHub Projects bootstrap plan")
    if not isinstance(value, dict) or value.get("plan_hash") != plan_hash or _hash(value.get("material")) != plan_hash:
        raise GitHubProjectsError("GitHub Projects bootstrap plan failed its content hash")
    return value


def validate_bootstrap_approval(
    root: Path,
    config: dict[str, Any],
    plan: dict[str, Any],
    verify_signature: Callable[[bytes, Path, str], Any] | None = None,
) -> dict[str, Any]:
    path = bootstrap_approval_path(root, config, plan["plan_hash"])
    if not path.is_file():
        raise GitHubProjectsError("GitHub Projects bootstrap requires an exact human approval receipt")
    receipt = _load_json(path)
    _validate_schema(receipt, "github-projects-approval.schema.json", "GitHub Projects bootstrap approval")
    expected = {
        "project_id": config["project_id"],
        "plan_hash": plan["plan_hash"],
        "destination": plan["material"]["destination"],
        "authorization_text": plan["authorization_text"],
        "behavior_configuration_hash": config.get("behavior_configuration_hash"),
    }
    mismatches = sorted(key for key, value in expected.items() if receipt.get(key) != value)
    if receipt.get("schema_version") != 1 or mismatches:
        raise GitHubProjectsError(f"GitHub Projects bootstrap approval is stale or mismatched: {mismatches}")
    if config.get("require_signed_approvals", False):
        if receipt.get("signature_format") != "openssh-sshsig-v1" or verify_signature is None:
            raise GitHubProjectsError("This project requires a signed GitHub Projects bootstrap approval")
        verify_signature(
            approval_receipt_bytes(receipt),
            bootstrap_signature_path(root, config, plan["plan_hash"]),
            str(receipt.get("approved_by", "")),
        )
    return receipt


class GitHubClient:
    def __init__(
        self,
        executable: str | None = None,
        *,
        host: str = "github.com",
        timeout_seconds: int = 90,
    ) -> None:
        self.executable = executable or shutil.which("gh") or ""
        if not self.executable:
            raise GitHubProjectsError("GitHub CLI is required to inspect or apply a GitHub Projects export")
        self.host = _github_host(host)
        self.timeout_seconds = timeout_seconds
        self.authenticated_login: str | None = None

    def _environment(self) -> dict[str, str]:
        return {**os.environ, "GH_HOST": self.host}

    def _verify_identity(self) -> None:
        if self.authenticated_login is not None:
            return
        result = subprocess.run(
            [self.executable, "api", "user", "--hostname", self.host, "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=self._environment(),
        )
        login = result.stdout.strip()
        if result.returncode != 0 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,254}", login):
            raise GitHubProjectsError(f"GitHub CLI has no valid active account for {self.host}")
        self.authenticated_login = login

    def _run_json(self, arguments: list[str]) -> dict[str, Any]:
        try:
            result = subprocess.run(
                [self.executable, *arguments],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                env=self._environment(),
            )
        except subprocess.TimeoutExpired as exc:
            raise GitHubProjectsError(f"GitHub CLI request timed out after {self.timeout_seconds} seconds") from exc
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown GitHub CLI error"
            raise GitHubProjectsError(f"GitHub CLI request failed: {message}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise GitHubProjectsError("GitHub CLI returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise GitHubProjectsError("GitHub CLI response must be a JSON object")
        return payload

    def command_json(self, arguments: list[str]) -> dict[str, Any]:
        self._verify_identity()
        return self._run_json(arguments)

    def authenticated_identity(self) -> dict[str, Any]:
        status = self._run_json(["auth", "status", "--hostname", self.host, "--active", "--json", "hosts"])
        accounts = (status.get("hosts") or {}).get(self.host)
        if not isinstance(accounts, list):
            raise GitHubProjectsError(f"GitHub CLI did not return an active {self.host} account")
        active = next((item for item in accounts if isinstance(item, dict) and item.get("active")), None)
        if not isinstance(active, dict) or active.get("state") != "success":
            login = active.get("login") if isinstance(active, dict) else "unknown"
            raise GitHubProjectsError(
                f"GitHub CLI account {login} is not authenticated; run `gh auth login --hostname {self.host} --web --scopes project`"
            )
        scopes = sorted(str(item) for item in active.get("scopes", []) if str(item))
        missing = sorted(REQUIRED_CONNECTION_SCOPES - set(scopes))
        if missing:
            raise GitHubProjectsError(
                f"GitHub Projects connection requires the project scope; run `gh auth refresh --hostname {self.host} --scopes project`"
            )
        viewer = self._run_json(["api", "user"])
        login = str(viewer.get("login") or "")
        database_id = viewer.get("id")
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", login):
            raise GitHubProjectsError("GitHub API did not return a valid authenticated login")
        if isinstance(database_id, bool) or not isinstance(database_id, int) or database_id < 1:
            raise GitHubProjectsError("GitHub API did not return a stable authenticated account ID")
        if login.casefold() != str(active.get("login") or "").casefold():
            raise GitHubProjectsError("GitHub CLI status and API viewer identities do not match")
        self.authenticated_login = login
        return {
            "login": login,
            "database_id": database_id,
            "scopes": scopes,
            "host": self.host,
            "credential_source": str(active.get("tokenSource") or "gh-credential-store"),
        }

    def create_project(self, owner: str, title: str) -> dict[str, Any]:
        return self.command_json(["project", "create", "--owner", owner, "--title", title, "--format", "json"])

    def edit_project(self, number: int, owner: str, visibility: str, description: str) -> dict[str, Any]:
        return self.command_json(
            [
                "project", "edit", str(number), "--owner", owner,
                "--visibility", visibility, "--description", description, "--format", "json",
            ]
        )

    def create_project_field(
        self,
        number: int,
        owner: str,
        name: str,
        data_type: str,
        options: list[str],
    ) -> dict[str, Any]:
        arguments = [
            "project", "field-create", str(number), "--owner", owner,
            "--name", name, "--data-type", data_type, "--format", "json",
        ]
        if options:
            arguments.extend(["--single-select-options", ",".join(options)])
        return self.command_json(arguments)

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        self._verify_identity()
        try:
            result = subprocess.run(
                [self.executable, "api", "graphql", "--hostname", self.host, "--input", "-"],
                input=json.dumps({"query": query, "variables": variables}),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                env=self._environment(),
            )
        except subprocess.TimeoutExpired as exc:
            raise GitHubProjectsError(f"GitHub Projects API request timed out after {self.timeout_seconds} seconds") from exc
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown GitHub CLI error"
            raise GitHubProjectsError(f"GitHub Projects API request failed: {message}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise GitHubProjectsError("GitHub Projects API returned invalid JSON") from exc
        if payload.get("errors"):
            raise GitHubProjectsError(f"GitHub Projects GraphQL error: {payload['errors']}")
        if not isinstance(payload.get("data"), dict):
            raise GitHubProjectsError("GitHub Projects API response is missing data")
        return payload["data"]


def _project_query(owner_type: str) -> str:
    owner_field = "organization" if owner_type == "organization" else "user"
    return f"""
query($login: String!, $number: Int!, $cursor: String) {{
  owner: {owner_field}(login: $login) {{
    project: projectV2(number: $number) {{
      id
      number
      title
      url
      public
      viewerCanUpdate
      fields(first: 100) {{
        nodes {{
          ... on ProjectV2Field {{ id name dataType }}
          ... on ProjectV2SingleSelectField {{ id name dataType options {{ id name color description }} }}
        }}
        pageInfo {{ hasNextPage }}
      }}
      items(first: 100, after: $cursor) {{
        nodes {{
          id
          type
          content {{ ... on DraftIssue {{ id title body }} }}
          fieldValues(first: 100) {{
            nodes {{
              ... on ProjectV2ItemFieldTextValue {{ text field {{ ... on ProjectV2Field {{ name }} }} }}
              ... on ProjectV2ItemFieldDateValue {{ date field {{ ... on ProjectV2Field {{ name }} }} }}
              ... on ProjectV2ItemFieldSingleSelectValue {{ name optionId field {{ ... on ProjectV2SingleSelectField {{ name }} }} }}
            }}
            pageInfo {{ hasNextPage }}
          }}
        }}
        pageInfo {{ hasNextPage endCursor }}
      }}
    }}
  }}
}}
"""


def fetch_project(client: GitHubClient, destination: dict[str, Any]) -> dict[str, Any]:
    cursor: str | None = None
    combined: dict[str, Any] | None = None
    while True:
        data = client.graphql(
            _project_query(str(destination["owner_type"])),
            {"login": destination["owner"], "number": destination["project_number"], "cursor": cursor},
        )
        project = (data.get("owner") or {}).get("project")
        if not isinstance(project, dict):
            raise GitHubProjectsError("GitHub Project was not found or is not accessible")
        if project.get("fields", {}).get("pageInfo", {}).get("hasNextPage"):
            raise GitHubProjectsError("GitHub Project has more than 100 fields; narrow the Project before syncing")
        page_items = project.get("items", {}).get("nodes", [])
        for item in page_items:
            if item.get("fieldValues", {}).get("pageInfo", {}).get("hasNextPage"):
                raise GitHubProjectsError("A GitHub Project item has more than 100 field values")
        if combined is None:
            combined = {**project, "items": {"nodes": []}}
        combined["items"]["nodes"].extend(page_items)
        page = project.get("items", {}).get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
        if not cursor:
            raise GitHubProjectsError("GitHub Projects pagination did not provide an end cursor")
    if combined is None:
        raise GitHubProjectsError("GitHub Projects API returned no Project snapshot")
    return combined


def _field_name(value: dict[str, Any]) -> str | None:
    field = value.get("field")
    return field.get("name") if isinstance(field, dict) else None


def _item_values(item: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for value in item.get("fieldValues", {}).get("nodes", []):
        name = _field_name(value)
        if not name:
            continue
        for key in ("text", "date", "name"):
            if value.get(key) is not None:
                values[name] = str(value[key])
                break
    return values


def _field_index(project: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields: dict[str, dict[str, Any]] = {}
    for field in project.get("fields", {}).get("nodes", []):
        if not isinstance(field, dict) or not field.get("name"):
            continue
        name = str(field["name"])
        if name in fields:
            raise GitHubProjectsError(f"GitHub Project contains duplicate field name {name!r}")
        fields[name] = field
    return fields


def _single_select_inputs(existing: list[dict[str, Any]], names: list[str]) -> list[dict[str, Any]]:
    by_name = {str(option.get("name")): option for option in existing}
    inputs: list[dict[str, Any]] = []
    for index, name in enumerate(names):
        current = by_name.get(name, {})
        option = {
            "name": name,
            "color": str(current.get("color") or OPTION_COLORS[index % len(OPTION_COLORS)]),
            "description": str(current.get("description") or f"Continuity value: {name}"),
        }
        if current.get("id"):
            option["id"] = str(current["id"])
        inputs.append(option)
    return inputs


def _update_single_select_options(
    client: GitHubClient,
    field: dict[str, Any],
    names: list[str],
) -> None:
    query = """
mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]) {
  updateProjectV2Field(input: {fieldId: $fieldId, singleSelectOptions: $options}) {
    projectV2Field { ... on ProjectV2SingleSelectField { id name } }
  }
}
"""
    client.graphql(
        query,
        {"fieldId": field["id"], "options": _single_select_inputs(field.get("options", []), names)},
    )


def _configure_project_fields(
    client: GitHubClient,
    destination: dict[str, Any],
    desired_fields: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str], list[str]]:
    snapshot = fetch_project(client, destination)
    fields = _field_index(snapshot)
    created_fields: list[str] = []
    updated_fields: list[str] = []
    for desired in desired_fields:
        name = str(desired["name"])
        data_type = str(desired["data_type"])
        options = [str(option) for option in desired["options"]]
        current = fields.get(name)
        if current is None:
            client.create_project_field(
                int(destination["project_number"]),
                str(destination["owner"]),
                name,
                data_type,
                options,
            )
            created_fields.append(name)
            continue
        if current.get("dataType") != data_type:
            raise GitHubProjectsError(f"GitHub Project field {name!r} must use type {data_type}")
        if data_type == "SINGLE_SELECT":
            current_names = [str(option.get("name")) for option in current.get("options", [])]
            if current_names != options:
                _update_single_select_options(client, current, options)
                updated_fields.append(name)

    snapshot = fetch_project(client, destination)
    available = _field_index(snapshot)
    for desired in desired_fields:
        current = available.get(str(desired["name"]))
        if not current or current.get("dataType") != desired["data_type"]:
            raise GitHubProjectsError(f"GitHub Project connection did not create compatible field {desired['name']!r}")
        if desired["data_type"] == "SINGLE_SELECT":
            current_names = [str(option.get("name")) for option in current.get("options", [])]
            if current_names != desired["options"]:
                raise GitHubProjectsError(f"GitHub Project connection did not configure options for {desired['name']!r}")
    return snapshot, created_fields, updated_fields


def _bootstrap_checkpoint(
    root: Path,
    config: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    target = bootstrap_application_path(root, config, plan["plan_hash"])
    if not target.is_file():
        return {
            "schema_version": 1,
            "project_id": plan["material"]["project_id"],
            "plan_hash": plan["plan_hash"],
            "status": "approved",
        }
    value = _load_json(target)
    if not isinstance(value, dict) or value.get("plan_hash") != plan["plan_hash"]:
        raise GitHubProjectsError("GitHub Projects bootstrap checkpoint is invalid")
    return value


def apply_bootstrap(
    root: Path,
    config: dict[str, Any],
    plan: dict[str, Any],
    client: GitHubClient | None = None,
) -> dict[str, Any]:
    material = plan["material"]
    client = client or GitHubClient(host=str(material["destination"].get("host", "github.com")))
    target = _confined(root, str(material["settings_path"]), "GitHub Projects settings")
    checkpoint_path = bootstrap_application_path(root, config, plan["plan_hash"])
    checkpoint = _bootstrap_checkpoint(root, config, plan)
    if checkpoint.get("status") == "completed":
        if not target.is_file():
            raise GitHubProjectsError("Completed GitHub Projects bootstrap is missing its settings file")
        return checkpoint
    if target.exists():
        if checkpoint.get("status") != "settings-written" or not isinstance(checkpoint.get("project"), dict):
            raise GitHubProjectsError(f"GitHub Projects settings already exist: {runtime.project_relative_posix(target, root)}")
        expected_settings = dict(material["settings"])
        expected_settings["project_number"] = int(checkpoint["project"]["number"])
        if _load_json(target) != expected_settings:
            raise GitHubProjectsError("GitHub Projects settings changed after bootstrap wrote them")
        export_plan = build_plan(root, config, str(material["settings_path"]))
        result = {
            **checkpoint,
            "status": "completed",
            "export_plan_hash": export_plan["plan_hash"],
            "export_authorization_text": export_plan["authorization_text"],
            "next_action": f"Approve and apply export plan {export_plan['plan_hash']}",
        }
        runtime.atomic_write_json(checkpoint_path, result)
        return result

    destination = material["destination"]
    project = checkpoint.get("project")
    if not isinstance(project, dict):
        project = client.create_project(str(destination["owner"]), str(material["project"]["title"]))
        if not isinstance(project.get("number"), int) or project["number"] < 1 or not project.get("id"):
            raise GitHubProjectsError("GitHub CLI did not return the created Project number and ID")
        checkpoint.update({"status": "project-created", "project": project})
        runtime.atomic_write_json(checkpoint_path, checkpoint)

    project_number = int(project["number"])
    client.edit_project(
        project_number,
        str(destination["owner"]),
        str(material["project"]["visibility"]),
        str(material["project"]["description"]),
    )
    project_destination = {
        "owner_type": destination["owner_type"],
        "owner": destination["owner"],
        "project_number": project_number,
    }
    _snapshot, created_fields, updated_fields = _configure_project_fields(
        client,
        project_destination,
        material["fields"],
    )

    settings = dict(material["settings"])
    settings["project_number"] = project_number
    _validate_schema(settings, "github-projects-settings.schema.json", "GitHub Projects settings")
    plan_material(root, config, target, settings)
    runtime.atomic_write_json(target, settings)
    checkpoint.update(
        {
            "status": "settings-written",
            "destination": project_destination,
            "settings_path": material["settings_path"],
            "created_fields": sorted(set(created_fields)),
            "updated_fields": sorted(set(updated_fields)),
        }
    )
    runtime.atomic_write_json(checkpoint_path, checkpoint)
    export_plan = build_plan(root, config, str(material["settings_path"]))
    result = {
        **checkpoint,
        "status": "completed",
        "export_plan_hash": export_plan["plan_hash"],
        "export_authorization_text": export_plan["authorization_text"],
        "next_action": f"Approve and apply export plan {export_plan['plan_hash']}",
    }
    runtime.atomic_write_json(checkpoint_path, result)
    return result


def _project_connection_destination(
    host: str,
    owner_type: str,
    owner: str,
    project: dict[str, Any],
) -> dict[str, Any]:
    host = _github_host(host)
    number = project.get("number")
    node_id = project.get("id")
    url = project.get("url")
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise GitHubProjectsError("GitHub Project did not return a valid project number")
    if not isinstance(node_id, str) or not node_id:
        raise GitHubProjectsError("GitHub Project did not return a stable node ID")
    if not isinstance(url, str) or not url.startswith(f"https://{host}/"):
        raise GitHubProjectsError("GitHub Project did not return a valid GitHub URL")
    if project.get("viewerCanUpdate") is not True:
        raise GitHubProjectsError("The authenticated GitHub account cannot edit the selected Project")
    return {
        "host": host,
        "owner_type": owner_type,
        "owner": owner,
        "project_number": number,
        "project_node_id": node_id,
        "project_url": url,
        "visibility": "PUBLIC" if project.get("public") is True else "PRIVATE",
    }


def connection_status(
    root: Path,
    config: dict[str, Any],
    client: GitHubClient | None = None,
) -> dict[str, Any]:
    connection = load_connection(root, config)
    assert connection is not None
    client = client or GitHubClient(host=str(connection["destination"].get("host", "github.com")))
    identity = client.authenticated_identity()
    expected_user = connection["authenticated_user"]
    expected_host = _github_host(connection["destination"].get("host", "github.com"))
    if _github_host(identity.get("host", "github.com")) != expected_host:
        raise GitHubProjectsError(f"Active GitHub host does not match connected host {expected_host}")
    if (
        identity["database_id"] != expected_user["database_id"]
        or identity["login"].casefold() != str(expected_user["login"]).casefold()
    ):
        raise GitHubProjectsError(
            f"Active GitHub account {identity['login']} does not match connected account {expected_user['login']}"
        )
    destination = connection["destination"]
    project = fetch_project(client, destination)
    if project.get("id") != destination["project_node_id"]:
        raise GitHubProjectsError("Connected GitHub Project node ID no longer matches the configured destination")
    if project.get("viewerCanUpdate") is not True:
        raise GitHubProjectsError("The connected GitHub account no longer has Project write access")
    return {
        "connected": True,
        "provider": "github-projects",
        "connection_id": connection["connection_id"],
        "authenticated_user": expected_user,
        "destination": destination,
        "project_title": project.get("title"),
        "capabilities": connection["capabilities"],
        "sync_policy": connection["sync_policy"],
        "identity_verified": True,
        "project_access_verified": True,
        "token_stored_by_continuity": False,
    }


def connect(
    root: Path,
    config: dict[str, Any],
    *,
    owner_type: str,
    owner: str,
    project_number: int | None = None,
    title: str | None = None,
    visibility: str = "PRIVATE",
    settings_value: str = ".continuity/github-projects.json",
    hostname: str = "github.com",
    client: GitHubClient | None = None,
) -> dict[str, Any]:
    if config.get("planning_patterns", {}).get("tracker_provider") != "github":
        raise GitHubProjectsError("Project tracker_provider must be github before connecting GitHub Projects")
    if owner_type not in {"organization", "user"}:
        raise GitHubProjectsError("owner_type must be organization or user")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", owner):
        raise GitHubProjectsError("owner must be a valid GitHub login")
    if project_number is not None and (isinstance(project_number, bool) or project_number < 1):
        raise GitHubProjectsError("project_number must be a positive integer")
    hostname = _github_host(hostname)
    client = client or GitHubClient(host=hostname)
    identity = client.authenticated_identity()
    if _github_host(identity.get("host", "github.com")) != hostname:
        raise GitHubProjectsError(f"Active GitHub host does not match requested host {hostname}")
    if owner_type == "user" and identity["login"].casefold() != owner.casefold():
        raise GitHubProjectsError(
            f"User-owned Projects must be connected to the authenticated account {identity['login']}"
        )
    existing_connection = load_connection(root, config, required=False)
    if existing_connection is not None:
        requested_number = project_number or existing_connection["destination"]["project_number"]
        if (
            existing_connection["authenticated_user"]["database_id"] == identity["database_id"]
            and _github_host(existing_connection["destination"].get("host", "github.com")) == hostname
            and existing_connection["destination"]["owner_type"] == owner_type
            and existing_connection["destination"]["owner"].casefold() == owner.casefold()
            and existing_connection["destination"]["project_number"] == requested_number
        ):
            return connection_status(root, config, client)
        raise GitHubProjectsError(
            "A different GitHub Projects connection already exists; changing account or destination requires an explicit reconnect"
        )

    settings_path = _confined(root, settings_value, "GitHub Projects settings")
    created_project = False
    created_fields: list[str] = []
    updated_fields: list[str] = []
    if project_number is None:
        if settings_path.exists():
            raise GitHubProjectsError(
                "GitHub Projects settings already exist; pass their project number to attach the durable connection"
            )
        bootstrap = build_bootstrap_plan(
            root,
            config,
            owner_type=owner_type,
            owner=owner,
            title=title,
            visibility=visibility,
            settings_value=settings_value,
            hostname=hostname,
        )
        result = apply_bootstrap(root, config, bootstrap, client)
        project_number = int(result["destination"]["project_number"])
        created_project = True
        created_fields = list(result.get("created_fields", []))
        updated_fields = list(result.get("updated_fields", []))
        _settings_path, settings = load_settings(root, config, settings_value)
    else:
        if settings_path.is_file():
            _settings_path, settings = load_settings(root, config, settings_value)
            if (
                settings["host"] != hostname
                or settings["owner_type"] != owner_type
                or str(settings["owner"]).casefold() != owner.casefold()
                or settings["project_number"] != project_number
            ):
                raise GitHubProjectsError("Existing GitHub Projects settings do not match the requested destination")
        else:
            template = _load_json(TEMPLATE_ROOT / "github-projects-settings.json")
            if not isinstance(template, dict):
                raise GitHubProjectsError("GitHub Projects settings template is invalid")
            settings = dict(template)
            settings.update({"host": hostname, "owner_type": owner_type, "owner": owner, "project_number": project_number})
            _validate_schema(settings, "github-projects-settings.schema.json", "GitHub Projects settings")
        destination = {"host": hostname, "owner_type": owner_type, "owner": owner, "project_number": project_number}
        project = fetch_project(client, destination)
        if project.get("viewerCanUpdate") is not True:
            raise GitHubProjectsError("The authenticated GitHub account cannot edit the selected Project")
        project, created_fields, updated_fields = _configure_project_fields(
            client,
            destination,
            _bootstrap_field_specs(settings),
        )
        runtime.atomic_write_json(settings_path, settings)

    destination = {"host": hostname, "owner_type": owner_type, "owner": owner, "project_number": project_number}
    project = fetch_project(client, destination)
    connected_destination = _project_connection_destination(hostname, owner_type, owner, project)
    connection_material = {
        "provider": "github-projects",
        "project_id": str(config["project_id"]),
        "authenticated_user": {"login": identity["login"], "database_id": identity["database_id"]},
        "destination": connected_destination,
        "capabilities": CONNECTION_CAPABILITIES,
        "sync_policy": {
            "automatic": True,
            "projections": ["roadmap", "goals"],
            "remote_edits": "proposals-only",
            "allow_delete": False,
        },
    }
    connection = {
        "schema_version": 1,
        **connection_material,
        "connection_id": _hash(connection_material),
        "connected_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "credential_source": "gh-credential-store",
        "authorization": {
            "mode": "durable-connection",
            "renew_only_for": [
                "authenticated account change",
                "destination Project change",
                "visibility change",
                "capability expansion",
                "enabling deletion",
            ],
        },
    }
    _validate_schema(connection, "github-projects-connection.schema.json", "GitHub Projects connection")
    runtime.atomic_write_json(connection_path(root, config), connection)
    synced = sync(root, config, settings_value=settings_value, client=client)
    return {
        **connection_status(root, config, client),
        "created_project": created_project,
        "created_fields": sorted(set(created_fields)),
        "updated_fields": sorted(set(updated_fields)),
        "initial_sync": synced,
    }


def sync(
    root: Path,
    config: dict[str, Any],
    *,
    settings_value: str = ".continuity/github-projects.json",
    client: GitHubClient | None = None,
) -> dict[str, Any]:
    connection = load_connection(root, config)
    assert connection is not None
    client = client or GitHubClient(host=str(connection["destination"].get("host", "github.com")))
    status = connection_status(root, config, client)
    plan = build_plan(root, config, settings_value)
    if plan["material"].get("connection_id") != status["connection_id"]:
        raise GitHubProjectsError("GitHub Projects export is not bound to the active durable connection")
    result = apply(plan, client)
    record = {
        **result,
        "connection_id": status["connection_id"],
        "synced_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "authorization_mode": "durable-connection",
        "automatic_sync": True,
        "delete_performed": False,
    }
    application = _private_root(root, config) / "integrations" / "github-projects" / "applications" / f"{plan['plan_hash']}.json"
    runtime.atomic_write_json(application, record)
    runtime.atomic_write_json(
        _private_root(root, config) / "integrations" / "github-projects" / "last-sync.json",
        record,
    )
    return record


def _resolved_fields(plan: dict[str, Any], project: dict[str, Any]) -> dict[str, dict[str, Any]]:
    available = _field_index(project)
    resolved: dict[str, dict[str, Any]] = {}
    for key, name in plan["material"]["field_names"].items():
        field = available.get(name)
        if not field:
            raise GitHubProjectsError(f"GitHub Project is missing configured field {name!r}")
        expected = FIELD_TYPES[key]
        if field.get("dataType") != expected:
            raise GitHubProjectsError(f"GitHub Project field {name!r} must use type {expected}")
        resolved[key] = field
    for item in plan["material"]["items"]:
        for key in OPTION_FIELD_KEYS:
            desired = item["fields"].get(key)
            if desired is None:
                continue
            options = {str(option.get("name")): option for option in resolved[key].get("options", [])}
            if desired not in options:
                raise GitHubProjectsError(
                    f"GitHub Project field {resolved[key]['name']!r} is missing option {desired!r}"
                )
    return resolved


def _managed_items(plan: dict[str, Any], project: dict[str, Any]) -> dict[str, dict[str, Any]]:
    continuity_name = plan["material"]["field_names"]["continuity_id"]
    managed: dict[str, dict[str, Any]] = {}
    for item in project.get("items", {}).get("nodes", []):
        value = _item_values(item).get(continuity_name)
        if not value:
            continue
        if value in managed:
            raise GitHubProjectsError(f"GitHub Project contains duplicate Continuity ID {value!r}")
        if item.get("type") != "DRAFT_ISSUE" or not isinstance(item.get("content"), dict):
            raise GitHubProjectsError(f"Managed Continuity item {value!r} must remain a draft issue")
        managed[value] = item
    return managed


def inspect(plan: dict[str, Any], client: GitHubClient | None = None) -> dict[str, Any]:
    client = client or GitHubClient(host=str(plan["material"]["destination"].get("host", "github.com")))
    project = fetch_project(client, plan["material"]["destination"])
    _resolved_fields(plan, project)
    managed = _managed_items(plan, project)
    differences: list[dict[str, Any]] = []
    for desired in plan["material"]["items"]:
        current = managed.get(desired["continuity_id"])
        if current is None:
            differences.append({"continuity_id": desired["continuity_id"], "change": "create"})
            continue
        content = current["content"]
        if content.get("title") != desired["title"]:
            differences.append({"continuity_id": desired["continuity_id"], "change": "title", "remote": content.get("title"), "canonical": desired["title"]})
        if content.get("body") != desired["body"]:
            differences.append({"continuity_id": desired["continuity_id"], "change": "body", "remote": content.get("body"), "canonical": desired["body"]})
        values = _item_values(current)
        for key, desired_value in desired["fields"].items():
            name = plan["material"]["field_names"][key]
            if values.get(name) != desired_value:
                differences.append({"continuity_id": desired["continuity_id"], "change": key, "remote": values.get(name), "canonical": desired_value})
    return {
        "project_id": plan["material"]["project_id"],
        "plan_hash": plan["plan_hash"],
        "destination": plan["material"]["destination"],
        "project_title": project.get("title"),
        "difference_count": len(differences),
        "differences": differences,
        "remote_changes_authorize_canonical_updates": False,
        "next_action": "Treat remote differences as reconciliation proposals; do not change canonical roadmap state without approved roadmap impact.",
    }


def _create_draft(client: GitHubClient, project_id: str, title: str, body: str) -> dict[str, Any]:
    query = """
mutation($projectId: ID!, $title: String!, $body: String!) {
  addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
    projectV2Item { id type content { ... on DraftIssue { id title body } } }
  }
}
"""
    data = client.graphql(query, {"projectId": project_id, "title": title, "body": body})
    item = (data.get("addProjectV2DraftIssue") or {}).get("projectV2Item")
    if not isinstance(item, dict) or not item.get("id") or not isinstance(item.get("content"), dict):
        raise GitHubProjectsError("GitHub did not return the created Project draft issue")
    item["fieldValues"] = {"nodes": []}
    return item


def _update_draft(client: GitHubClient, draft_id: str, title: str, body: str) -> None:
    query = """
mutation($draftIssueId: ID!, $title: String!, $body: String!) {
  updateProjectV2DraftIssue(input: {draftIssueId: $draftIssueId, title: $title, body: $body}) {
    draftIssue { id }
  }
}
"""
    client.graphql(query, {"draftIssueId": draft_id, "title": title, "body": body})


def _update_field(
    client: GitHubClient,
    project_id: str,
    item_id: str,
    field: dict[str, Any],
    desired: str,
) -> None:
    value: dict[str, Any]
    if field["dataType"] == "SINGLE_SELECT":
        options = {str(option.get("name")): str(option.get("id")) for option in field.get("options", [])}
        value = {"singleSelectOptionId": options[desired]}
    elif field["dataType"] == "DATE":
        value = {"date": desired}
    else:
        value = {"text": desired}
    query = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
  updateProjectV2ItemFieldValue(input: {projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value}) {
    projectV2Item { id }
  }
}
"""
    client.graphql(
        query,
        {"projectId": project_id, "itemId": item_id, "fieldId": field["id"], "value": value},
    )


def _clear_field(client: GitHubClient, project_id: str, item_id: str, field_id: str) -> None:
    query = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!) {
  clearProjectV2ItemFieldValue(input: {projectId: $projectId, itemId: $itemId, fieldId: $fieldId}) {
    projectV2Item { id }
  }
}
"""
    client.graphql(query, {"projectId": project_id, "itemId": item_id, "fieldId": field_id})


def apply(plan: dict[str, Any], client: GitHubClient | None = None) -> dict[str, Any]:
    client = client or GitHubClient(host=str(plan["material"]["destination"].get("host", "github.com")))
    project = fetch_project(client, plan["material"]["destination"])
    fields = _resolved_fields(plan, project)
    managed = _managed_items(plan, project)
    created = 0
    updated_drafts = 0
    updated_fields = 0
    unchanged = 0
    results: list[dict[str, Any]] = []
    for desired in plan["material"]["items"]:
        current = managed.get(desired["continuity_id"])
        item_changes = 0
        if current is None:
            current = _create_draft(client, str(project["id"]), desired["title"], desired["body"])
            created += 1
            item_changes += 1
        else:
            content = current["content"]
            if content.get("title") != desired["title"] or content.get("body") != desired["body"]:
                _update_draft(client, str(content["id"]), desired["title"], desired["body"])
                updated_drafts += 1
                item_changes += 1
        current_values = _item_values(current)
        for key, desired_value in desired["fields"].items():
            name = plan["material"]["field_names"][key]
            if current_values.get(name) == desired_value:
                continue
            if desired_value is None:
                if name not in current_values:
                    continue
                _clear_field(client, str(project["id"]), str(current["id"]), str(fields[key]["id"]))
            else:
                _update_field(client, str(project["id"]), str(current["id"]), fields[key], desired_value)
            updated_fields += 1
            item_changes += 1
        if item_changes == 0:
            unchanged += 1
        results.append({"continuity_id": desired["continuity_id"], "changes": item_changes})
    return {
        "project_id": plan["material"]["project_id"],
        "plan_hash": plan["plan_hash"],
        "destination": plan["material"]["destination"],
        "project_title": project.get("title"),
        "created": created,
        "updated_drafts": updated_drafts,
        "updated_fields": updated_fields,
        "unchanged": unchanged,
        "items": results,
        "canonical_source_changed": False,
    }
