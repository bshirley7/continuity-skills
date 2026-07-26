"""Project-local roadmap storage, projection, audits, and read-only sidecar."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import secrets
import sqlite3
import subprocess
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import runtime as runtime_lib


ROADMAP_KINDS = {"program", "initiative", "release", "milestone", "epic", "story", "bug", "spike", "chore", "sprint"}
ROADMAP_STATUSES = {"proposed", "inbox", "triaged", "ready", "planned", "active", "in-progress", "validating", "paused", "at-risk", "blocked", "completed", "done", "closed", "cancelled", "historical"}
ROADMAP_HEALTH = {"unknown", "on-track", "at-risk", "off-track", "blocked", "complete"}
NOTE_RELATIONS = {"supports", "contradicts", "blocks", "updates", "suggests"}
IMPACT_ACTIONS = {"create", "revise", "verify", "status", "none"}
REQUIRED_FIELDS = {"roadmap_id", "title", "kind", "status", "summary", "created_at", "updated_at"}


class RoadmapError(RuntimeError):
    pass


def _dump(path: Path, value: Any) -> None:
    runtime_lib.atomic_write_json(path, value)


def _load(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _confined(root: Path, value: str, label: str) -> Path:
    try:
        path = Path(runtime_lib.validate_portable_relative_path(value, label=label))
    except runtime_lib.RuntimeIntegrityError as exc:
        raise RoadmapError(str(exc)) from exc
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise RoadmapError(f"{label} escapes the project root")
    return resolved


def _private(root: Path, config: dict[str, Any]) -> Path:
    return _confined(root, config.get("private_dir", ".continuity/private"), "private_dir")


def _roadmap_root(root: Path, config: dict[str, Any]) -> Path:
    return _confined(root, config.get("roadmap_docs", "docs/project-roadmap"), "roadmap_docs")


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if value.lstrip("-").isdigit():
        return int(value)
    if value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    return value.strip("\"'")


def parse_entry(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}, text
    end = text.find("\n---\n", 4)
    metadata: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            metadata[key.strip()] = _parse_scalar(value)
    return metadata, text[end + 5 :]


def render_entry(entry: dict[str, Any]) -> str:
    ordered = [
        "roadmap_id", "title", "kind", "status", "summary", "parent_ids", "depends_on",
        "release_ids", "milestone_ids", "sprint_ids", "priority", "estimate_points", "health",
        "owners", "tags", "risks", "goals", "delivery_slices", "memory_ids", "note_ids",
        "shared_packet_ids", "evidence", "start_date", "target_date", "created_at", "updated_at",
        "verified_against", "confidence",
    ]
    lines = ["---"]
    for key in ordered:
        if key not in entry:
            continue
        value = entry[key]
        rendered = json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) else str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(["---", "", f"# {entry['title']}", "", entry.get("body", entry["summary"]).rstrip(), ""])
    return "\n".join(lines)


def _as_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise RoadmapError(f"{label} must be an array of non-empty strings")
    return value


def normalize_entry(value: dict[str, Any], *, existing_id: str | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RoadmapError("Roadmap entry must be a JSON object")
    missing = sorted(REQUIRED_FIELDS - set(value))
    if missing:
        raise RoadmapError(f"Roadmap entry is missing: {', '.join(missing)}")
    entry = dict(value)
    identifier = str(entry["roadmap_id"])
    if not identifier or len(identifier) > 128 or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for character in identifier):
        raise RoadmapError("roadmap_id must use letters, numbers, dots, underscores, or hyphens")
    if existing_id and identifier != existing_id:
        raise RoadmapError("A roadmap revision cannot change its stable roadmap_id")
    if entry["kind"] not in ROADMAP_KINDS:
        raise RoadmapError(f"Unsupported roadmap kind: {entry['kind']}")
    if entry["status"] not in ROADMAP_STATUSES:
        raise RoadmapError(f"Unsupported roadmap status: {entry['status']}")
    if not isinstance(entry["title"], str) or not entry["title"].strip() or not isinstance(entry["summary"], str) or not entry["summary"].strip():
        raise RoadmapError("Roadmap title and summary must be non-empty strings")
    for key in ("parent_ids", "depends_on", "release_ids", "milestone_ids", "sprint_ids", "owners", "tags", "risks", "goals", "delivery_slices", "memory_ids", "note_ids", "shared_packet_ids", "evidence"):
        entry[key] = _as_list(entry.get(key), key)
    if identifier in entry["parent_ids"] or identifier in entry["depends_on"]:
        raise RoadmapError("A roadmap entry cannot parent or depend on itself")
    if entry.get("health", "unknown") not in ROADMAP_HEALTH:
        raise RoadmapError(f"Unsupported roadmap health: {entry.get('health')}")
    entry["health"] = entry.get("health", "unknown")
    estimate = entry.get("estimate_points")
    if estimate is not None and (isinstance(estimate, bool) or not isinstance(estimate, int) or estimate not in {1, 2, 3, 5, 8, 13, 20, 40, 100}):
        raise RoadmapError("estimate_points must be a supported planning estimate")
    for key in ("start_date", "target_date"):
        if entry.get(key):
            try:
                dt.date.fromisoformat(str(entry[key]))
            except ValueError as exc:
                raise RoadmapError(f"{key} must use YYYY-MM-DD") from exc
    if entry.get("start_date") and entry.get("target_date") and entry["start_date"] > entry["target_date"]:
        raise RoadmapError("start_date cannot be later than target_date")
    return entry


def entries(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    root = root.resolve()
    base = _roadmap_root(root, config)
    result: list[dict[str, Any]] = []
    if not base.exists():
        return result
    for path in sorted((base / "entities").glob("*.md")):
        metadata, body = parse_entry(path)
        metadata["body"] = body
        metadata["path"] = path.relative_to(root).as_posix()
        metadata["visibility"] = "committed"
        result.append(metadata)
    return result


def inbox_entries(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    """Project actionable, triaged notes into the private roadmap inbox."""
    result: list[dict[str, Any]] = []
    actionable_kinds = {
        "documentation-candidate": "chore",
        "backlog-candidate": "story",
        "execution-candidate": "story",
        "explicit-instruction": "story",
    }
    for path in sorted((_private(root, config) / "captures").glob("**/*.json")):
        capture = _load(path, {})
        if not isinstance(capture, dict):
            continue
        for item in capture.get("items", []):
            if not isinstance(item, dict) or item.get("kind") not in actionable_kinds:
                continue
            routing_status = item.get("routing_status")
            if routing_status not in {"route", "promote", "defer"}:
                continue
            note_id = str(item.get("item_id", ""))
            text = str(item.get("text", "")).strip()
            if not note_id or not text:
                continue
            active_goal_links = [
                goal_id
                for goal_id, link in item.get("goal_links", {}).items()
                if isinstance(link, dict)
                and link.get("disposition") == "current-goal"
                and link.get("state") not in {"cancelled", "completed", "unlinked"}
            ]
            status = "planned" if active_goal_links else "inbox" if routing_status == "defer" else "triaged"
            title = text.splitlines()[0].strip()
            if len(title) > 96:
                title = title[:93].rstrip() + "..."
            result.append(
                {
                    "roadmap_id": f"inbox-{note_id}",
                    "note_id": note_id,
                    "title": title,
                    "kind": actionable_kinds[item["kind"]],
                    "note_kind": item["kind"],
                    "status": status,
                    "health": "unknown",
                    "summary": text,
                    "goals": sorted(active_goal_links),
                    "parent_ids": [],
                    "depends_on": [],
                    "memory_ids": [],
                    "note_ids": [note_id],
                    "evidence": [f"capture:{capture.get('capture_id')}"],
                    "actionability": item.get("actionability"),
                    "impact": item.get("impact"),
                    "confidence": item.get("confidence"),
                    "themes": item.get("themes", []),
                    "review_after": item.get("review_after"),
                    "updated_at": item.get("updated_at") or capture.get("captured_at"),
                    "visibility": "private-inbox",
                    "execution_authorized": False,
                }
            )
    return result


def audit(root: Path, config: dict[str, Any], *, persist: bool = True) -> dict[str, Any]:
    issues: dict[str, list[Any]] = {name: [] for name in ("invalid", "duplicates", "unknown_parents", "unknown_dependencies", "unknown_links", "cycles", "orphans", "milestone_health", "sprint", "estimates", "dates", "contradictions", "stale_note_links")}
    normalized: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for raw in entries(root, config):
        try:
            item = normalize_entry(raw)
        except RoadmapError as exc:
            bucket = "dates" if "date" in str(exc) else "estimates" if "estimate_points" in str(exc) else "invalid"
            issues[bucket].append({"path": raw.get("path"), "error": str(exc)})
            continue
        identifier = item["roadmap_id"]
        if identifier in seen:
            issues["duplicates"].append({"roadmap_id": identifier, "paths": [seen[identifier], raw["path"]]})
        else:
            seen[identifier] = raw["path"]
        normalized.append(item)
    ids = set(seen)
    kinds = {item["roadmap_id"]: item["kind"] for item in normalized}
    graph: dict[str, list[str]] = {}
    for item in normalized:
        identifier = item["roadmap_id"]
        for parent in item["parent_ids"]:
            if parent not in ids:
                issues["unknown_parents"].append({"roadmap_id": identifier, "reference": parent})
        for dependency in item["depends_on"]:
            if dependency not in ids:
                issues["unknown_dependencies"].append({"roadmap_id": identifier, "reference": dependency})
        for field, expected_kind in (("release_ids", "release"), ("milestone_ids", "milestone"), ("sprint_ids", "sprint")):
            for reference in item[field]:
                if reference not in ids or kinds.get(reference) != expected_kind:
                    issues["unknown_links"].append({"roadmap_id": identifier, "field": field, "reference": reference, "expected_kind": expected_kind})
        graph[identifier] = [*item["parent_ids"], *item["depends_on"]]
        if item["kind"] not in {"program", "release", "sprint"} and not item["parent_ids"]:
            issues["orphans"].append(identifier)
        if item["kind"] == "milestone" and item["status"] in {"active", "at-risk", "blocked"} and item["health"] == "unknown":
            issues["milestone_health"].append(identifier)
        if item["sprint_ids"] and item["kind"] in {"program", "initiative", "release", "milestone", "sprint"}:
            issues["sprint"].append(identifier)
        if item.get("estimate_points") is not None and item["kind"] not in {"epic", "story", "bug", "spike", "chore"}:
            issues["estimates"].append(identifier)
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            issues["cycles"].append(trail + [node])
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, []):
            if target in ids:
                visit(target, trail + [node])
        visiting.remove(node)
        visited.add(node)
    for identifier in ids:
        visit(identifier, [])
    known_notes = set()
    for capture in (_private(root, config) / "captures").glob("**/*.json"):
        for item in _load(capture, {}).get("items", []):
            known_notes.add(item.get("item_id"))
    for link in _iter_jsonl(_private(root, config) / "roadmap" / "note-links.jsonl"):
        if link.get("note_id") not in known_notes or link.get("roadmap_id") not in ids:
            issues["stale_note_links"].append(link)
        elif link.get("relation") == "contradicts":
            issues["contradictions"].append(link)
    report = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "entries": len(normalized), **issues}
    report["healthy"] = not any(issues.values())
    if persist:
        _dump(_private(root, config) / "reports" / "roadmap-health.json", report)
    return report


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return [{key: item for key, item in value.items() if key != "_integrity"} for value in runtime_lib.load_jsonl(path)]
    except runtime_lib.RuntimeIntegrityError as exc:
        raise RoadmapError(str(exc)) from exc


def _append_jsonl(path: Path, value: Any) -> None:
    try:
        runtime_lib.append_integrity_jsonl(path, value)
    except runtime_lib.RuntimeIntegrityError as exc:
        raise RoadmapError(str(exc)) from exc


def projection(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    committed = entries(root, config)
    inbox = inbox_entries(root, config)
    goals = []
    for path in (_private(root, config) / "goals").glob("*/goal.json"):
        goal = _load(path, {})
        goals.append({key: goal.get(key) for key in ("goal_id", "title", "state", "roadmap_ids", "roadmap_impact", "updated_at")})
    links = _iter_jsonl(_private(root, config) / "roadmap" / "note-links.jsonl")
    packets = []
    for path in sorted((root / ".continuity" / "shared-notes" / "packets").glob("**/*.md")):
        metadata, _body = parse_entry(path)
        packets.append({**metadata, "path": runtime_lib.project_relative_posix(path, root), "visibility": "committed"})
    value = {
        "schema_version": 1,
        "project_id": config["project_id"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "entities": committed,
        "roadmap_inbox": inbox,
        "goals": goals,
        "note_links": links,
        "shared_packets": packets,
    }
    target = _private(root, config) / "roadmap" / "projection.json"
    _dump(target, value)
    db = _private(root, config) / "roadmap" / "projection.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db)
    connection.executescript("DROP TABLE IF EXISTS roadmap; DROP TABLE IF EXISTS roadmap_fts; CREATE TABLE roadmap (roadmap_id TEXT PRIMARY KEY, title TEXT, kind TEXT, status TEXT, summary TEXT, path TEXT, body TEXT); CREATE VIRTUAL TABLE roadmap_fts USING fts5(roadmap_id UNINDEXED, title, kind, status, summary, body, tokenize='unicode61');")
    for item in committed:
        row = (str(item.get("roadmap_id", "")), str(item.get("title", "")), str(item.get("kind", "")), str(item.get("status", "")), str(item.get("summary", "")), str(item.get("path", "")), str(item.get("body", "")))
        if row[0]:
            connection.execute("INSERT OR REPLACE INTO roadmap VALUES (?,?,?,?,?,?,?)", row)
            connection.execute("INSERT INTO roadmap_fts VALUES (?,?,?,?,?,?)", (row[0], row[1], row[2], row[3], row[4], row[6]))
    connection.commit()
    connection.close()
    return value


def search(root: Path, config: dict[str, Any], query: str, limit: int = 12) -> list[dict[str, Any]]:
    value = projection(root, config)
    tokens = [token.lower() for token in query.replace("/", " ").replace("-", " ").split() if token]
    results = []
    for item in value["entities"]:
        haystack = " ".join(str(item.get(key, "")) for key in ("roadmap_id", "title", "kind", "status", "summary", "tags", "body")).lower()
        if not tokens or all(token in haystack for token in tokens) or str(item.get("roadmap_id")) == query:
            score = (0 if item.get("status") in {"active", "in-progress", "ready", "planned"} else 1, str(item.get("target_date", "9999")))
            results.append((score, item))
    return [item for _score, item in sorted(results, key=lambda pair: pair[0])[:limit]]


def _find_entry(root: Path, config: dict[str, Any], identifier: str) -> dict[str, Any]:
    matches = [entry for entry in entries(root, config) if entry.get("roadmap_id") == identifier]
    if len(matches) != 1:
        raise RoadmapError(f"Expected one roadmap entry {identifier}; found {len(matches)}")
    return matches[0]


def _goal_allows(root: Path, config: dict[str, Any], goal_id: str, roadmap_id: str, action: str) -> dict[str, Any]:
    goal_path = _private(root, config) / "goals" / goal_id / "goal.json"
    approval_path = goal_path.parent / "approval.json"
    goal = _load(goal_path, {})
    approval = _load(approval_path, {})
    if goal.get("state") not in {"approved", "queued", "dispatched", "running", "validating"} or not approval:
        raise RoadmapError("Roadmap changes require an approved goal")
    if approval.get("plan_version") != goal.get("plan_version"):
        raise RoadmapError("Roadmap goal approval version is stale")
    immutable_keys = {
        "schema_version", "goal_id", "project_id", "title", "plan_version", "priority", "depends_on",
        "source_note_ids", "note_dispositions", "memory_ids", "roadmap_ids", "roadmap_impact", "roadmap_fingerprint", "scope", "exclusions",
        "acceptance_criteria", "documentation_updates", "required_checks", "runtime_limit_minutes",
        "authorization_mode", "risk_level", "restricted_side_effects",
        "triage_brief", "decision_map", "delivery_slices",
    }
    machine = {key: goal.get(key) for key in sorted(immutable_keys)}
    if "source_capture_refs" in goal:
        machine["source_capture_refs"] = goal.get("source_capture_refs", [])
    if "design_refs" in goal:
        machine["design_refs"] = goal.get("design_refs", [])
    plan_path = goal_path.parent / "plan.md"
    if not plan_path.is_file():
        raise RoadmapError("Roadmap goal plan is missing")
    current_hash = hashlib.sha256((json.dumps(machine, sort_keys=True) + "\n" + plan_path.read_text(encoding="utf-8")).encode()).hexdigest()
    if approval.get("plan_hash") != current_hash or goal.get("plan_hash") != current_hash:
        raise RoadmapError("Roadmap goal approval is stale because approved material changed")
    if roadmap_id not in goal.get("roadmap_ids", []):
        raise RoadmapError("Roadmap entry is outside the approved goal roadmap_ids")
    allowed = [item for item in goal.get("roadmap_impact", {}).get("entries", []) if item.get("roadmap_id") == roadmap_id and item.get("action") == action]
    if not allowed:
        raise RoadmapError(f"Approved goal does not authorize roadmap action {action} for {roadmap_id}")
    return goal


def command_index(root: Path, config: dict[str, Any], _args: argparse.Namespace) -> dict[str, Any]:
    value = projection(root, config)
    return {
        "entries": len(value["entities"]),
        "inbox": len(value["roadmap_inbox"]),
        "goals": len(value["goals"]),
        "note_links": len(value["note_links"]),
        "shared_packets": len(value["shared_packets"]),
        "projection": runtime_lib.project_relative_posix(_private(root, config) / "roadmap" / "projection.json", root),
    }


def command_list(root: Path, config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    result = entries(root, config)
    for key in ("kind", "status", "health", "owner", "tag", "sprint"):
        value = getattr(args, key, None)
        if not value:
            continue
        field = {"owner": "owners", "tag": "tags", "sprint": "sprint_ids"}.get(key, key)
        result = [item for item in result if value == item.get(field) or value in item.get(field, [])]
    return [{key: item.get(key) for key in ("roadmap_id", "title", "kind", "status", "health", "target_date", "path", "visibility")} for item in result]


def command_inbox(root: Path, config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    result = inbox_entries(root, config)
    if getattr(args, "status", None):
        result = [item for item in result if item.get("status") == args.status]
    if getattr(args, "kind", None):
        result = [item for item in result if item.get("kind") == args.kind]
    return result


def command_show(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    return _find_entry(root, config, args.roadmap_id)


def command_brief(root: Path, config: dict[str, Any], args: argparse.Namespace) -> str:
    matches = search(root, config, args.query, args.limit)
    tokens = [token.lower() for token in args.query.replace("/", " ").replace("-", " ").split() if token]
    inbox_matches = [
        item
        for item in inbox_entries(root, config)
        if not tokens
        or all(
            token
            in " ".join(
                str(item.get(key, ""))
                for key in ("title", "summary", "kind", "note_kind", "themes")
            ).lower()
            for token in tokens
        )
    ][: args.limit]
    lines = [f"# Project Roadmap Brief: {args.query}", ""]
    if not matches and not inbox_matches:
        lines.append("No matching committed roadmap context or triaged inbox candidate was found.")
    for item in matches:
        lines.extend([f"## {item.get('title')} ({item.get('roadmap_id')})", "", str(item.get("summary", "")), "", f"- Kind: {item.get('kind')}", f"- Status: {item.get('status')}", f"- Health: {item.get('health', 'unknown')}", f"- Dependencies: {', '.join(item.get('depends_on', [])) or 'none'}", f"- Memory: {', '.join(item.get('memory_ids', [])) or 'none'}", f"- Source: `{item.get('path')}`", ""])
    if inbox_matches:
        lines.extend(["## Triaged roadmap inbox", ""])
        for item in inbox_matches:
            lines.extend(
                [
                    f"### {item.get('title')} ({item.get('note_id')})",
                    "",
                    str(item.get("summary", "")),
                    "",
                    f"- Status: {item.get('status')}",
                    f"- Actionability: {item.get('actionability')}",
                    f"- Impact: {item.get('impact')}",
                    f"- Goals: {', '.join(item.get('goals', [])) or 'none'}",
                    "- Authority: planning context only",
                    "",
                ]
            )
    return "\n".join(lines)


def command_audit(root: Path, config: dict[str, Any], _args: argparse.Namespace) -> dict[str, Any]:
    return audit(root, config)


def command_link_note(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.relation not in NOTE_RELATIONS:
        raise RoadmapError("Unsupported note-roadmap relation")
    _find_entry(root, config, args.roadmap_id)
    found = False
    for path in (_private(root, config) / "captures").glob("**/*.json"):
        if any(item.get("item_id") == args.note_id for item in _load(path, {}).get("items", [])):
            found = True
            break
    if not found:
        raise RoadmapError(f"Unknown private note: {args.note_id}")
    record = {"schema_version": 1, "linked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "note_id": args.note_id, "roadmap_id": args.roadmap_id, "relation": args.relation, "execution_authorized": False}
    path = _private(root, config) / "roadmap" / "note-links.jsonl"
    if record | {"linked_at": None} not in [{**row, "linked_at": None} for row in _iter_jsonl(path)]:
        _append_jsonl(path, record)
    return record


def _entry_from_file(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        value = _load(path, {})
    else:
        value, body = parse_entry(path)
        value["body"] = body
    return normalize_entry(value)


def command_create(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    item = _entry_from_file(Path(args.entry_file).expanduser().resolve())
    _goal_allows(root, config, args.goal_id, item["roadmap_id"], "create")
    target = _roadmap_root(root, config) / "entities" / f"{item['roadmap_id']}.md"
    if target.exists():
        raise RoadmapError("Roadmap entry already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_entry(item), encoding="utf-8")
    return {"roadmap_id": item["roadmap_id"], "path": runtime_lib.project_relative_posix(target, root), "goal_id": args.goal_id}


def command_revise(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    current = _find_entry(root, config, args.roadmap_id)
    item = _entry_from_file(Path(args.entry_file).expanduser().resolve())
    item = normalize_entry(item, existing_id=args.roadmap_id)
    _goal_allows(root, config, args.goal_id, args.roadmap_id, "revise")
    target = root / current["path"]
    target.write_text(render_entry(item), encoding="utf-8")
    return {"roadmap_id": item["roadmap_id"], "path": runtime_lib.project_relative_posix(target, root), "goal_id": args.goal_id}


def command_export(root: Path, config: dict[str, Any], args: argparse.Namespace) -> Any:
    if args.scope != "committed":
        raise RoadmapError("Only committed roadmap export is supported")
    value = {"schema_version": 1, "project_id": config["project_id"], "scope": "committed", "entities": entries(root, config)}
    if args.output:
        destination = Path(args.output).expanduser().resolve()
        destination.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"output": str(destination), "entries": len(value["entities"])}
    return value


def production_audit(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    artifact = Path(args.artifact).expanduser().resolve()
    if not artifact.exists():
        raise RoadmapError("Production artifact does not exist")
    markers = ("project-roadmap", "continuity roadmap serve", "CONTINUITY_ROADMAP_TOKEN", "roadmap-ui", "/api/v1/roadmap")
    findings: list[dict[str, str]] = []
    paths = [artifact] if artifact.is_file() else [path for path in artifact.rglob("*") if path.is_file()]
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for marker in markers:
            if marker in text:
                findings.append({"path": str(path), "marker": marker})
    return {"artifact": str(artifact), "clean": not findings, "findings": findings, "policy": "roadmap sidecar must be excluded from preview, staging, and production artifacts"}


class SidecarHandler(BaseHTTPRequestHandler):
    server_version = "ContinuityRoadmap/1"

    def _headers(self, status: int, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.end_headers()

    def _valid_request_context(self) -> bool:
        host = self.headers.get("Host", "")
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if host not in expected:
            self._headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(b'{"error":"invalid host"}')
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
            self._headers(HTTPStatus.FORBIDDEN)
            self.wfile.write(b'{"error":"cross-origin request rejected"}')
            return False
        return True

    def _authorized(self) -> bool:
        if time.monotonic() >= self.server.token_expires_at:
            return False
        expected = f"Bearer {self.server.bearer_token}"
        return secrets.compare_digest(self.headers.get("Authorization", ""), expected)

    def do_GET(self) -> None:  # noqa: N802
        if not self._valid_request_context():
            return
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if ".." in Path(path).parts or "\\" in path or "%2f" in self.path.lower() or "%5c" in self.path.lower():
            self._headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(b'{"error":"invalid path"}')
            return
        if path.startswith("/api/"):
            if not self._authorized():
                self._headers(HTTPStatus.UNAUTHORIZED)
                self.wfile.write(b'{"error":"bearer authorization required"}')
                return
            if path == "/api/v1/roadmap":
                body = json.dumps(self.server.snapshot, sort_keys=True).encode()
            elif path == "/api/v1/health":
                body = b'{"status":"ok","read_only":true}'
            elif path.startswith("/api/v1/source/"):
                identifier = path.removeprefix("/api/v1/source/")
                target = self.server.source_map.get(identifier)
                try:
                    resolved = target.resolve(strict=True) if target else None
                except OSError:
                    resolved = None
                if not resolved or not resolved.is_file() or not resolved.is_relative_to(self.server.roadmap_root.resolve()):
                    self._headers(HTTPStatus.NOT_FOUND)
                    self.wfile.write(b'{"error":"source not found"}')
                    return
                body = json.dumps({"roadmap_id": identifier, "path": runtime_lib.project_relative_posix(target, self.server.project_root), "content": resolved.read_text(encoding="utf-8")}).encode()
            else:
                self._headers(HTTPStatus.NOT_FOUND)
                self.wfile.write(b'{"error":"not found"}')
                return
            self._headers(HTTPStatus.OK)
            self.wfile.write(body)
            return
        assets = {"/": ("index.html", "text/html; charset=utf-8"), "/index.html": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/styles.css": ("styles.css", "text/css; charset=utf-8")}
        if path not in assets:
            self._headers(HTTPStatus.NOT_FOUND)
            self.wfile.write(b"not found")
            return
        name, content_type = assets[path]
        try:
            target = (self.server.asset_root / name).resolve(strict=True)
        except OSError:
            target = self.server.asset_root / "missing"
        if not target.is_relative_to(self.server.asset_root.resolve()) or not target.is_file():
            self._headers(HTTPStatus.NOT_FOUND)
            self.wfile.write(b"not found")
            return
        self._headers(HTTPStatus.OK, content_type)
        self.wfile.write(target.read_bytes())

    def _readonly(self) -> None:
        self._headers(HTTPStatus.METHOD_NOT_ALLOWED)
        self.wfile.write(b'{"error":"read-only sidecar"}')

    do_POST = do_PUT = do_PATCH = do_DELETE = _readonly  # type: ignore[assignment]

    def log_message(self, format: str, *args: Any) -> None:
        return


class RoadmapServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True

    def __init__(self, address: tuple[str, int], snapshot: dict[str, Any], bearer_token: str, asset_root: Path, project_root: Path, roadmap_root: Path):
        if address[0] != "127.0.0.1":
            raise RoadmapError("Roadmap sidecar must bind to 127.0.0.1")
        self.snapshot = snapshot
        self.bearer_token = bearer_token
        self.token_expires_at = time.monotonic() + 1800
        self.asset_root = asset_root
        self.project_root = project_root.resolve()
        self.roadmap_root = roadmap_root.resolve()
        self.source_map = {str(item.get("roadmap_id")): self.project_root / str(item.get("path")) for item in snapshot.get("entities", []) if item.get("roadmap_id") and item.get("path")}
        super().__init__(address, SidecarHandler)


def create_server(root: Path, config: dict[str, Any], *, port: int = 0, token: str | None = None, asset_root: Path | None = None) -> RoadmapServer:
    if port < 0 or port > 65535:
        raise RoadmapError("Invalid port")
    assets = asset_root or Path(__file__).resolve().parents[1] / "roadmap-ui"
    if not assets.is_dir():
        raise RoadmapError(f"Roadmap UI assets are missing: {assets}")
    try:
        project_root = root.resolve()
        return RoadmapServer(("127.0.0.1", port), projection(project_root, config), token or secrets.token_urlsafe(32), assets, project_root, _roadmap_root(project_root, config))
    except PermissionError:
        raise
    except OSError as exc:
        raise RoadmapError(f"Could not start loopback roadmap sidecar: {exc}") from exc


def command_serve(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    server = create_server(root, config, port=args.port)
    url = f"http://127.0.0.1:{server.server_port}/#token={server.bearer_token}"
    print(json.dumps({"url": url, "read_only": True, "pid": os.getpid(), "token_ttl_seconds": 1800}), flush=True)
    if args.open:
        webbrowser.open(url, new=2)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return {"stopped": True}
