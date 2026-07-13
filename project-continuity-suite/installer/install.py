#!/usr/bin/env python3
"""Install the project-continuity suite into one repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


AGENTS_START = "<!-- project-continuity:start -->"
AGENTS_END = "<!-- project-continuity:end -->"
IGNORE_START = "# project-continuity:start"
IGNORE_END = "# project-continuity:end"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def confined(root: Path, value: str, label: str) -> Path:
    relative = Path(value)
    if relative.is_absolute():
        raise RuntimeError(f"{label} must be project-relative")
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise RuntimeError(f"{label} escapes the project root")
    return target


def replace_block(text: str, start: str, end: str, block: str) -> str:
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip()
        return f"{before}\n\n{block.rstrip()}\n\n{after}".rstrip() + "\n"
    return text.rstrip() + "\n\n" + block.rstrip() + "\n"


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def render_memory(entry: dict[str, Any], stamp: str, commit: str) -> str:
    metadata = {
        "memory_id": entry["memory_id"],
        "title": entry["title"],
        "type": entry["type"],
        "system": entry.get("system", "project"),
        "summary": entry["summary"],
        "status": entry.get("status", "current"),
        "tags": entry.get("tags", []),
        "aliases": entry.get("aliases", []),
        "created_at": stamp,
        "updated_at": stamp,
        "last_verified_at": stamp,
        "verified_against": commit,
        "sources": entry.get("sources", []),
        "related": entry.get("related", []),
        "supersedes": entry.get("supersedes", []),
        "confidence": entry.get("confidence", "high"),
        "unresolved_gaps": entry.get("unresolved_gaps", []),
    }
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {json.dumps(value) if isinstance(value, (list, dict)) else value}")
    lines.extend(["---", "", f"# {entry['title']}", "", entry.get("body", entry["summary"]).rstrip(), ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--integration-branch", required=True)
    parser.add_argument("--seed", help="Optional project-specific memory seed kept outside this distribution")
    parser.add_argument("--validation", action="append", default=[])
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--enable-execution", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", args.project_id):
        raise RuntimeError("project-id must use 1-128 letters, numbers, dots, underscores, or hyphens")

    suite = Path(__file__).resolve().parents[1]
    root = Path(args.project_root).expanduser().resolve()
    if root == Path("/") or not root.is_dir():
        raise RuntimeError("Refusing unsafe or missing project root")
    git(root, "rev-parse", "--is-inside-work-tree")
    git(root, "check-ref-format", "--branch", args.integration_branch)
    commit = git(root, "rev-parse", "HEAD")
    seed = load_json(Path(args.seed).expanduser().resolve()) if args.seed else {}
    stamp = dt.datetime.now(ZoneInfo(args.timezone)).isoformat(timespec="seconds")
    entries = seed.get("entries") or [
        {
            "path": "INDEX.md",
            "memory_id": "project-memory-index",
            "title": f"{args.project_id} Project Memory",
            "type": "index",
            "system": "project",
            "summary": "Trusted entry point for curated, verified project knowledge.",
            "tags": ["index", "orientation"],
            "sources": ["AGENTS.md"],
            "confidence": "medium",
            "body": "No substantive project knowledge has been promoted yet. Curate current-state, architecture, decisions, constraints, operations, open questions, and history through approved documentation goals.",
        }
    ]

    config = {
        "schema_version": 1,
        "assurance_standard_version": 1,
        "project_id": args.project_id,
        "integration_branch": args.integration_branch,
        "timezone": args.timezone,
        "default_start_time": "22:00",
        "max_runtime_minutes": 360,
        "memory_docs": "docs/project-memory",
        "private_dir": ".continuity/private",
        "memory_stale_after_days": 90,
        "require_remote": True,
        "require_pr": True,
        "require_pr_auth": True,
        "require_execution_artifacts": True,
        "require_isolated_worktree": True,
        "refresh_base_on_preflight": True,
        "validation_commands": args.validation,
        "documentation_map": seed.get("documentation_map", {"project-memory": "docs/project-memory/INDEX.md"}),
    }
    project_manifest = {
        "schema_version": 1,
        "assurance_standard_version": 1,
        "project_id": args.project_id,
        "continuity_enabled": True,
        "execution_enabled": args.enable_execution,
        "integration_branch": args.integration_branch,
        "timezone": args.timezone,
        "schedules": {"review": "20:00", "dispatch": "22:00", "report": "07:00"},
        "max_concurrency": 1,
    }

    agents_block = f"""{AGENTS_START}
## Project Continuity, Memory, and Sequenced Development

- Project id: `{args.project_id}`. Treat `.continuity/project.json` as the committed enrollment and schedule contract.
- Integration branch: `{args.integration_branch}`
- Enforce development assurance standard version `1` from `.agents/references/development-assurance-standard.md`; stop when configuration, evidence, or an installed skill is incompatible.
- Invoke installed skills under `.agents/skills/` and the CLI at `.agents/project-continuity/bin/continuity`.
- Treat notes as project knowledge first. Capture, classification, promotion, planning, approval, and dispatch are separate events.
- Never change committed documentation or code from a captured note alone.
- Before planning or execution, run a project-memory brief and cite the memory IDs used.
- Permit one code-changing goal at a time in this project; use isolated worktrees and goal-focused branches.
- Enforce every compliance stage in `.continuity/private/goals/<goal-id>/compliance.json`.
- Require plan-hash approval, dependency and lock checks, current integration base, developer review, project validation, security review, merge-safety review, documentation, memory-impact, and final-alignment evidence.
- Keep raw captures and generated indexes private and ignored. Keep sanitized, verified memory under `docs/project-memory/`.
- Create a draft PR for incomplete or blocked work. Never auto-merge or force-push.
{AGENTS_END}"""

    ignore_block = f"""{IGNORE_START}
.continuity/private/
{IGNORE_END}"""

    if args.dry_run:
        print(json.dumps({"project": str(root), "config": config, "manifest": project_manifest, "memory_entries": len(entries)}, indent=2))
        return 0

    skills_target = root / ".agents" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    for skill in (suite / "skills").iterdir():
        if skill.is_dir():
            shutil.copytree(skill, skills_target / skill.name, dirs_exist_ok=True)

    control_target = root / ".agents" / "project-continuity"
    (control_target / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(suite / "bin" / "continuity", control_target / "bin" / "continuity")
    for name in ("references", "schemas", "templates", "automation"):
        shutil.copytree(suite / name, control_target / name, dirs_exist_ok=True)
    shutil.copytree(suite / "references", root / ".agents" / "references", dirs_exist_ok=True)
    write_json(root / ".continuity" / "config.json", config)
    write_json(root / ".continuity" / "project.json", project_manifest)

    agents_path = root / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else "# AGENTS.md\n"
    agents_path.write_text(replace_block(agents_text, AGENTS_START, AGENTS_END, agents_block), encoding="utf-8")
    ignore_path = root / ".gitignore"
    ignore_text = ignore_path.read_text(encoding="utf-8") if ignore_path.exists() else ""
    ignore_path.write_text(replace_block(ignore_text, IGNORE_START, IGNORE_END, ignore_block), encoding="utf-8")

    memory_root = confined(root, config["memory_docs"], "memory_docs")
    memory_root.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        target = confined(memory_root, entry["path"], f"seed entry {entry.get('memory_id', 'unknown')}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(render_memory(entry, stamp, commit), encoding="utf-8")

    print(json.dumps({"installed": True, "project": str(root), "skills": 7, "memory_entries": len(entries), "execution_enabled": args.enable_execution}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
