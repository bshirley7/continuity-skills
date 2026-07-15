#!/usr/bin/env python3
"""Install the continuity suite into one repository."""

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


AGENTS_START = "<!-- continuity:start -->"
AGENTS_END = "<!-- continuity:end -->"
LEGACY_AGENTS_START = "<!-- project-continuity:start -->"
LEGACY_AGENTS_END = "<!-- project-continuity:end -->"
IGNORE_START = "# continuity:start"
IGNORE_END = "# continuity:end"
LEGACY_IGNORE_START = "# project-continuity:start"
LEGACY_IGNORE_END = "# project-continuity:end"
LEGACY_SKILL_DIRS = [
    "project-continuity",
    "project-continuity-local",
    "capture-project-note",
    "triage-project-notes",
    "manage-project-memory",
    "manage-project-roadmap",
    "share-project-notes",
    "plan-project-goals",
    "dispatch-project-goals",
    "execute-project-goal",
    "report-project-progress",
]
USER_DEFAULT_FIELDS = {
    "timezone",
    "schedules",
    "max_runtime_minutes",
    "memory_stale_after_days",
    "visual_evidence_mode",
    "branch_prefix",
    "planning_patterns",
    "roadmap",
    "agent_surfaces",
    "scheduler",
}
DEFAULT_SCHEDULER = {
    "provider": "none",
    "sweep_minutes": 15,
    "business_days": [0, 1, 2, 3, 4],
    "retry_limit": 2,
    "retry_backoff_minutes": 15,
    "stale_after_minutes": 45,
    "portfolio_max_concurrency": 4,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_user_defaults(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    record = load_json(path)
    if record.get("schema_version") != 1 or not isinstance(record.get("settings"), dict):
        raise RuntimeError(f"Unsupported Continuity user defaults: {path}")
    unknown = sorted(set(record["settings"]) - USER_DEFAULT_FIELDS)
    if unknown:
        raise RuntimeError(f"Unsupported Continuity user default fields: {unknown}")
    return dict(record["settings"])


def portable_user_defaults(settings: dict[str, Any]) -> dict[str, Any]:
    return {key: settings[key] for key in sorted(USER_DEFAULT_FIELDS) if key in settings}


def scheduler_defaults(value: Any) -> dict[str, Any]:
    scheduler = dict(DEFAULT_SCHEDULER)
    if isinstance(value, dict):
        scheduler.update(value)
    return scheduler


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


def replace_managed_block(text: str, start: str, end: str, legacy_start: str, legacy_end: str, block: str) -> str:
    if start in text and end in text:
        return replace_block(text, start, end, block)
    if legacy_start in text and legacy_end in text:
        return replace_block(text, legacy_start, legacy_end, block)
    return replace_block(text, start, end, block)


def remove_legacy_install_paths(root: Path) -> None:
    skills_root = root / ".agents" / "skills"
    for name in LEGACY_SKILL_DIRS:
        legacy = skills_root / name
        if legacy.exists():
            if legacy.is_dir() and not legacy.is_symlink():
                shutil.rmtree(legacy)
            else:
                legacy.unlink()
    legacy_control = root / ".agents" / "project-continuity"
    if legacy_control.exists():
        if legacy_control.is_dir() and not legacy_control.is_symlink():
            shutil.rmtree(legacy_control)
        else:
            legacy_control.unlink()


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
    parser.add_argument("--timezone", help="IANA timezone; overrides a saved user default")
    parser.add_argument("--user-defaults", default="~/.continuity/defaults.json", help="Portable user-default profile used to seed new project installs")
    parser.add_argument("--ignore-user-defaults", action="store_true", help="Do not load or save the user-default profile")
    parser.add_argument("--save-user-defaults", action="store_true", help="Save portable choices from this install as future user defaults")
    parser.add_argument("--enable-execution", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.interactive and args.configuration:
        raise RuntimeError("Use either --interactive or --configuration, not both")
    if args.ignore_user_defaults and args.save_user_defaults:
        raise RuntimeError("Cannot save user defaults while --ignore-user-defaults is active")

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
    user_defaults_path = Path(args.user_defaults).expanduser().resolve()
    user_defaults_existed = user_defaults_path.exists()
    user_defaults = {} if args.ignore_user_defaults else load_user_defaults(user_defaults_path)
    effective_timezone = args.timezone or user_defaults.get("timezone", "America/Chicago")
    stamp = dt.datetime.now(ZoneInfo(effective_timezone)).isoformat(timespec="seconds")
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
        "timezone": effective_timezone,
        "default_start_time": "22:00",
        "max_runtime_minutes": user_defaults.get("max_runtime_minutes", 360),
        "memory_docs": "docs/project-memory",
        "roadmap_docs": "docs/project-roadmap",
        "private_dir": ".continuity/private",
        "memory_stale_after_days": user_defaults.get("memory_stale_after_days", 90),
        "require_remote": True,
        "require_pr": True,
        "require_pr_auth": True,
        "require_execution_artifacts": True,
        "require_isolated_worktree": True,
        "refresh_base_on_preflight": True,
        "validation_commands": args.validation,
        "security_commands": [],
        "documentation_map": seed.get("documentation_map", {"project-memory": "docs/project-memory/INDEX.md", "project-roadmap": "docs/project-roadmap/INDEX.md"}),
        "visual_evidence_mode": user_defaults.get("visual_evidence_mode", "when-applicable"),
        "branch_prefix": user_defaults.get("branch_prefix", "continuity"),
        "project_instructions": [],
        "planning_patterns": user_defaults.get("planning_patterns", {
            "evidence_triage": "auto",
            "decision_mapping": "auto",
            "delivery_slicing": "auto",
            "tracker_provider": "local",
        }),
        "roadmap": user_defaults.get("roadmap", {
            "enabled": True,
            "agile_mode": "hybrid",
            "hierarchy": "full",
            "ui_mode": "local-read-only",
            "shared_notes": "explicit-project-inbox",
            "production_distribution": "forbidden",
        }),
        "agent_surfaces": user_defaults.get("agent_surfaces", {"primary": "codex", "enabled": ["codex"]}),
        "scheduler": scheduler_defaults(user_defaults.get("scheduler")),
        "behavior_config_path": ".continuity/project-behavior.json",
        "behavior_skill_path": ".agents/skills/continuity-local/SKILL.md",
    }
    config["documentation_map"].setdefault("project-roadmap", "docs/project-roadmap/INDEX.md")
    project_manifest = {
        "schema_version": 1,
        "assurance_standard_version": 2,
        "project_id": args.project_id,
        "continuity_enabled": True,
        "execution_enabled": args.enable_execution,
        "integration_branch": args.integration_branch,
        "timezone": effective_timezone,
        "schedules": user_defaults.get("schedules", {"review": "20:00", "dispatch": "22:00", "report": "07:00"}),
        "agent_surfaces": user_defaults.get("agent_surfaces", {"primary": "codex", "enabled": ["codex"]}),
        "scheduler": scheduler_defaults(user_defaults.get("scheduler")),
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
        config["behavior_skill_path"] = ".agents/skills/continuity-local/SKILL.md"
    if existing_manifest_path.exists():
        existing_manifest = load_json(existing_manifest_path)
        if existing_manifest.get("project_id") != args.project_id:
            raise RuntimeError("Existing continuity manifest belongs to a different project id")
        project_manifest.update(existing_manifest)
        project_manifest["schema_version"] = 1
        project_manifest["assurance_standard_version"] = 2

    agents_block = f"""{AGENTS_START}
## Continuity, Memory, and Sequenced Development

- Project id: `{args.project_id}`. Treat `.continuity/project.json` as the committed enrollment and schedule contract.
- Integration branch: use the value in `.continuity/project.json`; project configuration may change it through the guided workflow.
- Enforce development assurance standard version `2` from `.agents/references/development-assurance-standard.md`; stop when configuration, evidence, or an installed skill is incompatible.
- Start configuration and workflow routing with `$continuity`; apply the generated `$continuity-local` behavior skill with every task-specific continuity skill.
- Use `continuity workflow status [--goal-id <goal-id>]` before and after every task skill as the machine handoff for stage, blockers, next skill, human requirements, and allowed commands.
- Invoke installed skills under `.agents/skills/` and the CLI at `.agents/continuity/bin/continuity`.
- Treat `AGENTS.md` and `.agents/` as the canonical cross-surface contract. Use the generated Claude Code, Cursor, or Windsurf adapters selected in `.continuity/project.json`; do not maintain divergent copies by hand.
- Treat `.continuity/scheduler.json` as the supervisor handoff. Record the provider task ID and workspace roots with `scheduler register`; every sweep must refresh supervisor liveness, and project doctor must fail on missing, stale, or unhealthy registration.
- Treat notes as project knowledge first. Capture occurrence time, internal/external perspective, sentiment, occurrence type, impact, confidence, actionability, stakeholders, and themes; capture, classification, pattern review, promotion, planning, approval, and dispatch are separate events.
- Never change committed documentation or code from a captured note alone.
- Before planning or execution, run project-memory and roadmap briefs and cite the memory and roadmap IDs used.
- Keep sanitized canonical roadmap records under `docs/project-roadmap/`; use `$continuity-roadmap` and the ignored local projection for timeline, hierarchy, release, milestone, sprint, board, dependency, risk, and blocker context.
- Treat `.agents/continuity/roadmap-ui/` as a local read-only admin companion. It must bind to loopback and remain outside application routes, builds, packages, preview, staging, and production artifacts.
- Share notes only through `$continuity-share`: prepare a sanitized hash-bound packet, approve its exact version and target project, and use a human-reviewed PR. A packet never authorizes memory, roadmap, goal, code, system, or private-state changes.
- For action candidates, use evidence triage; for complex or uncertain goals, use a decision map; for multi-part delivery, use dependency-validated vertical slices. These artifacts inform planning and never authorize work.
- Keep planning artifacts local by default. Publishing issues to an external tracker requires separate explicit human approval.
- Permit one code-changing goal at a time in this project; use isolated worktrees and goal-focused branches.
- Enforce every compliance stage in `.continuity/private/goals/<goal-id>/compliance.json`.
- Require plan-hash approval including `roadmap_ids` and structured `roadmap_impact`, dependency and lock checks, current integration base, developer review, project validation, security review, merge-safety review, documentation, memory-impact, roadmap-impact, and final-alignment evidence.
- Complete implementation, candidate checks, documentation, memory, roadmap, and evidence artifacts before committing and running the final source-bound `$continuity-test`. Push that exact tested commit to a draft PR before `$continuity-merge` binds local, remote, PR-head, and PR-base evidence.
- Record human review as `approved`, `changes-requested`, `merged`, or `closed`. In-scope requested changes require explicit resume authorization naming the goal and approved plan version; expanded scope requires revision and fresh approval. Overnight delivery stops at `review-ready`; only recorded human merge evidence marks it `completed`. Continuity never auto-merges or force-pushes.
- Keep raw captures and generated indexes private and ignored. Keep sanitized, verified memory under `docs/project-memory/`.
- Create a draft PR for incomplete or blocked work. Never auto-merge or force-push.
{AGENTS_END}"""

    ignore_block = f"""{IGNORE_START}
.continuity/private/
.continuity-portfolio/
.agents/continuity/lib/__pycache__/
.agents/continuity/lib/*.pyc
{IGNORE_END}"""

    if args.dry_run:
        print(json.dumps({"project": str(root), "config": config, "manifest": project_manifest, "configuration": args.configuration, "interactive": args.interactive, "memory_entries": len(entries), "user_defaults": str(user_defaults_path), "user_defaults_loaded": bool(user_defaults)}, indent=2))
        return 0

    skills_target = root / ".agents" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    for skill in (suite / "skills").iterdir():
        if skill.is_dir():
            shutil.copytree(skill, skills_target / skill.name, dirs_exist_ok=True)

    control_target = root / ".agents" / "continuity"
    (control_target / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(suite / "bin" / "continuity", control_target / "bin" / "continuity")
    for name in ("lib", "roadmap-ui", "references", "schemas", "templates", "automation"):
        shutil.copytree(suite / name, control_target / name, dirs_exist_ok=True)
    shutil.copytree(suite / "references", root / ".agents" / "references", dirs_exist_ok=True)
    remove_legacy_install_paths(root)
    write_json(root / ".continuity" / "config.json", config)
    write_json(root / ".continuity" / "project.json", project_manifest)

    agents_path = root / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else "# AGENTS.md\n"
    agents_path.write_text(
        replace_managed_block(agents_text, AGENTS_START, AGENTS_END, LEGACY_AGENTS_START, LEGACY_AGENTS_END, agents_block),
        encoding="utf-8",
    )
    ignore_path = root / ".gitignore"
    ignore_text = ignore_path.read_text(encoding="utf-8") if ignore_path.exists() else ""
    ignore_path.write_text(
        replace_managed_block(ignore_text, IGNORE_START, IGNORE_END, LEGACY_IGNORE_START, LEGACY_IGNORE_END, ignore_block),
        encoding="utf-8",
    )

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
        with tempfile.TemporaryDirectory(prefix="continuity-") as temp:
            answers_path = Path(temp) / "answers.json"
            write_json(answers_path, answers)
            configured = subprocess.run([*configure_command, "--answers-file", str(answers_path)], capture_output=True, text=True, check=False)
    if configured.returncode != 0:
        message = configured.stderr.strip() if configured.stderr else "guided project configuration failed"
        raise RuntimeError(message)

    manifest = load_json(root / ".continuity" / "project.json")
    save_defaults = not args.ignore_user_defaults and (args.save_user_defaults or (args.interactive and not user_defaults_existed))
    if save_defaults:
        behavior = load_json(root / ".continuity" / "project-behavior.json")
        write_json(
            user_defaults_path,
            {"schema_version": 1, "settings": portable_user_defaults(behavior["settings"])},
        )
    installed_skills = sum(1 for path in skills_target.iterdir() if path.is_dir())
    print(json.dumps({"installed": True, "project": str(root), "skills": installed_skills, "memory_entries": len(entries), "execution_enabled": manifest["execution_enabled"], "behavior_skill": ".agents/skills/continuity-local/SKILL.md", "agent_surfaces": manifest["agent_surfaces"], "scheduler": manifest["scheduler"], "scheduler_registration_required": manifest["scheduler"].get("provider") != "none", "supervisor_prompt": ".agents/continuity/automation/portfolio-supervisor.md", "user_defaults": str(user_defaults_path), "user_defaults_saved": save_defaults}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
