#!/usr/bin/env python3
"""Install the project-continuity suite into one repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
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
    parser.add_argument("--configuration", help="Optional JSON answers for guided project behavior configuration")
    parser.add_argument("--interactive", action="store_true", help="Ask guided project behavior questions after installation")
    parser.add_argument("--validation", action="append", default=[])
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--enable-execution", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.interactive and args.configuration:
        raise RuntimeError("Use either --interactive or --configuration, not both")

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
        "assurance_standard_version": 2,
        "project_id": args.project_id,
        "integration_branch": args.integration_branch,
        "timezone": args.timezone,
        "default_start_time": "22:00",
        "max_runtime_minutes": 360,
        "memory_docs": "docs/project-memory",
        "roadmap_docs": "docs/project-roadmap",
        "private_dir": ".continuity/private",
        "memory_stale_after_days": 90,
        "require_remote": True,
        "require_pr": True,
        "require_pr_auth": True,
        "require_execution_artifacts": True,
        "require_isolated_worktree": True,
        "refresh_base_on_preflight": True,
        "validation_commands": args.validation,
        "security_commands": [],
        "documentation_map": seed.get("documentation_map", {"project-memory": "docs/project-memory/INDEX.md", "project-roadmap": "docs/project-roadmap/INDEX.md"}),
        "visual_evidence_mode": "when-applicable",
        "branch_prefix": "continuity",
        "project_instructions": [],
        "planning_patterns": {
            "evidence_triage": "auto",
            "decision_mapping": "auto",
            "delivery_slicing": "auto",
            "tracker_provider": "local",
        },
        "roadmap": {
            "enabled": True,
            "agile_mode": "hybrid",
            "hierarchy": "full",
            "ui_mode": "local-read-only",
            "shared_notes": "explicit-project-inbox",
            "production_distribution": "forbidden",
        },
        "behavior_config_path": ".continuity/project-behavior.json",
        "behavior_skill_path": ".agents/skills/project-continuity-local/SKILL.md",
    }
    config["documentation_map"].setdefault("project-roadmap", "docs/project-roadmap/INDEX.md")
    project_manifest = {
        "schema_version": 1,
        "assurance_standard_version": 2,
        "project_id": args.project_id,
        "continuity_enabled": True,
        "execution_enabled": args.enable_execution,
        "integration_branch": args.integration_branch,
        "timezone": args.timezone,
        "schedules": {"review": "20:00", "dispatch": "22:00", "report": "07:00"},
        "max_concurrency": 1,
    }

    existing_config_path = root / ".continuity" / "config.json"
    existing_manifest_path = root / ".continuity" / "project.json"
    if existing_config_path.exists():
        existing_config = load_json(existing_config_path)
        if existing_config.get("project_id") != args.project_id:
            raise RuntimeError("Existing continuity configuration belongs to a different project id")
        config.update(existing_config)
        config["schema_version"] = 1
        config["assurance_standard_version"] = 2
        config["roadmap_docs"] = "docs/project-roadmap"
        config.setdefault("documentation_map", {})["project-roadmap"] = "docs/project-roadmap/INDEX.md"
        config.setdefault("roadmap", {
            "enabled": True,
            "agile_mode": "hybrid",
            "hierarchy": "full",
            "ui_mode": "local-read-only",
            "shared_notes": "explicit-project-inbox",
            "production_distribution": "forbidden",
        })
        config["behavior_config_path"] = ".continuity/project-behavior.json"
        config["behavior_skill_path"] = ".agents/skills/project-continuity-local/SKILL.md"
    if existing_manifest_path.exists():
        existing_manifest = load_json(existing_manifest_path)
        if existing_manifest.get("project_id") != args.project_id:
            raise RuntimeError("Existing continuity manifest belongs to a different project id")
        project_manifest.update(existing_manifest)
        project_manifest["schema_version"] = 1
        project_manifest["assurance_standard_version"] = 2

    agents_block = f"""{AGENTS_START}
## Project Continuity, Memory, and Sequenced Development

- Project id: `{args.project_id}`. Treat `.continuity/project.json` as the committed enrollment and schedule contract.
- Integration branch: use the value in `.continuity/project.json`; project configuration may change it through the guided workflow.
- Enforce development assurance standard version `2` from `.agents/references/development-assurance-standard.md`; stop when configuration, evidence, or an installed skill is incompatible.
- Start configuration and workflow routing with `$project-continuity`; apply the generated `$project-continuity-local` behavior skill with every task-specific continuity skill.
- Invoke installed skills under `.agents/skills/` and the CLI at `.agents/project-continuity/bin/continuity`.
- Treat notes as project knowledge first. Capture, classification, promotion, planning, approval, and dispatch are separate events.
- Never change committed documentation or code from a captured note alone.
- Before planning or execution, run project-memory and roadmap briefs and cite the memory and roadmap IDs used.
- Keep sanitized canonical roadmap records under `docs/project-roadmap/`; use `$manage-project-roadmap` and the ignored local projection for timeline, hierarchy, release, milestone, sprint, board, dependency, risk, and blocker context.
- Treat `.agents/project-continuity/roadmap-ui/` as a local read-only admin companion. It must bind to loopback and remain outside application routes, builds, packages, preview, staging, and production artifacts.
- Share notes only through `$share-project-notes`: prepare a sanitized hash-bound packet, approve its exact version and target project, and use a human-reviewed PR. A packet never authorizes memory, roadmap, goal, code, system, or private-state changes.
- For action candidates, use evidence triage; for complex or uncertain goals, use a decision map; for multi-part delivery, use dependency-validated vertical slices. These artifacts inform planning and never authorize work.
- Keep planning artifacts local by default. Publishing issues to an external tracker requires separate explicit human approval.
- Permit one code-changing goal at a time in this project; use isolated worktrees and goal-focused branches.
- Enforce every compliance stage in `.continuity/private/goals/<goal-id>/compliance.json`.
- Require plan-hash approval including `roadmap_ids` and structured `roadmap_impact`, dependency and lock checks, current integration base, developer review, project validation, security review, merge-safety review, documentation, memory-impact, roadmap-impact, and final-alignment evidence.
- Keep raw captures and generated indexes private and ignored. Keep sanitized, verified memory under `docs/project-memory/`.
- Create a draft PR for incomplete or blocked work. Never auto-merge or force-push.
{AGENTS_END}"""

    ignore_block = f"""{IGNORE_START}
.continuity/private/
.agents/project-continuity/lib/__pycache__/
.agents/project-continuity/lib/*.pyc
{IGNORE_END}"""

    if args.dry_run:
        print(json.dumps({"project": str(root), "config": config, "manifest": project_manifest, "configuration": args.configuration, "interactive": args.interactive, "memory_entries": len(entries)}, indent=2))
        return 0

    skills_target = root / ".agents" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    for skill in (suite / "skills").iterdir():
        if skill.is_dir():
            shutil.copytree(skill, skills_target / skill.name, dirs_exist_ok=True)

    control_target = root / ".agents" / "project-continuity"
    (control_target / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(suite / "bin" / "continuity", control_target / "bin" / "continuity")
    for name in ("lib", "roadmap-ui", "references", "schemas", "templates", "automation"):
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

    roadmap_root = confined(root, config["roadmap_docs"], "roadmap_docs")
    roadmap_root.mkdir(parents=True, exist_ok=True)
    roadmap_index = roadmap_root / "INDEX.md"
    if not roadmap_index.exists():
        roadmap_index.write_text(
            f"# {args.project_id} Project Roadmap\n\n"
            "This is the committed entry point for sanitized roadmap context. Markdown records under `entities/` are authoritative; ignored SQLite and JSON projections are derived local state.\n\n"
            "No roadmap records have been promoted yet. Create or revise records only through an approved goal with hash-bound `roadmap_ids` and `roadmap_impact`.\n",
            encoding="utf-8",
        )
    shared_index = root / ".continuity" / "shared-notes" / "README.md"
    if not shared_index.exists():
        shared_index.parent.mkdir(parents=True, exist_ok=True)
        shared_index.write_text(
            "# Shared note packets\n\nSanitized, explicitly approved packets merged by human-reviewed PR live under `packets/`. Packets are context only and never authorize execution or canonical documentation changes.\n",
            encoding="utf-8",
        )

    configure_command = [
        str(control_target / "bin" / "continuity"),
        "--project-root",
        str(root),
        "--json",
        "project",
        "configure",
        "--actor",
        "installer",
    ]
    if args.interactive:
        configure_command.append("--interactive")
        configured = subprocess.run(configure_command, check=False, text=True)
    else:
        answers = load_json(Path(args.configuration).expanduser().resolve()) if args.configuration else {}
        with tempfile.TemporaryDirectory(prefix="project-continuity-") as temp:
            answers_path = Path(temp) / "answers.json"
            write_json(answers_path, answers)
            configured = subprocess.run([*configure_command, "--answers-file", str(answers_path)], capture_output=True, text=True, check=False)
    if configured.returncode != 0:
        message = configured.stderr.strip() if configured.stderr else "guided project configuration failed"
        raise RuntimeError(message)

    manifest = load_json(root / ".continuity" / "project.json")
    installed_skills = sum(1 for path in skills_target.iterdir() if path.is_dir())
    print(json.dumps({"installed": True, "project": str(root), "skills": installed_skills, "memory_entries": len(entries), "execution_enabled": manifest["execution_enabled"], "behavior_skill": ".agents/skills/project-continuity-local/SKILL.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
