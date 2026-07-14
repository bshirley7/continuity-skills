# Install and Daily Use

This guide explains where to run Continuity installation, what gets installed into a project, how to choose schedules and project requirements, and how to use the installed skills in a daily routine.

## Where To Run Installation

Run the installer from the Continuity suite checkout and pass the target project path with `--project-root`.

Example from this repository:

```text
cd /Volumes/OPENFRONT/00_skills
python3 continuity-suite/installer/install.py \
  --project-root /Volumes/OPENFRONT/example-project \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck" \
  --validation "pnpm test"
```

If your terminal is already inside the target project, you can still run the installer by using the absolute path to the suite:

```text
cd /Volumes/OPENFRONT/example-project
python3 /Volumes/OPENFRONT/00_skills/continuity-suite/installer/install.py \
  --project-root "$PWD" \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck"
```

So the answer is: initial install comes from the main Continuity suite checkout, pointed at the project folder. After installation, daily use happens inside the project.

## What Gets Installed

Continuity writes project-local control files into the target project:

```text
.agents/skills/                         Continuity skills
.agents/skills/continuity-local/        generated project-specific behavior skill
.agents/continuity/                     project-local CLI, schemas, templates, automation prompts
.agents/references/continuity-contract.md
.agents/references/development-assurance-standard.md
.agents/references/testing-and-merge-standard.md
.continuity/project.json                schedule and enrollment manifest
.continuity/config.json                 project configuration
.continuity/project-behavior.json       hash-bound project-specific behavior
.continuity/scheduler.json              scheduler handoff and registration state
.continuity/private/                    ignored notes, queues, goals, locks, indexes
docs/project-memory/                    committed searchable memory
docs/project-roadmap/                   committed roadmap records
.continuity/shared-notes/packets/       reviewed shared-note packets
```

The installer also updates managed blocks in `AGENTS.md` and `.gitignore`.

## User Defaults And Project Isolation

Continuity separates reusable personal defaults from repository-specific controls.

The default user profile is:

```text
~/.continuity/defaults.json
```

It may contain only portable preferences: timezone, review/dispatch/report times, runtime and memory-age defaults, visual-evidence mode, branch prefix, planning and roadmap modes, enabled agent surfaces, and scheduler provider. It never contains repository paths, validation or security commands, documentation maps, project instructions, notes, approvals, roadmap records, credentials, execution enrollment, or private state.

The first `--interactive` install saves portable choices automatically when the profile does not exist. Later installs load that profile as their starting point but still generate an isolated project behavior record. Use `--save-user-defaults` to intentionally replace the profile with portable choices from a later install, `--user-defaults <path>` to use a different profile, or `--ignore-user-defaults` for a fully project-only install.

## Install With Guided Configuration

Use `--interactive` when you want the installer to ask for schedules and project-specific requirements:

```text
python3 continuity-suite/installer/install.py \
  --project-root /Volumes/OPENFRONT/example-project \
  --project-id example-project \
  --integration-branch main \
  --interactive \
  --validation "pnpm typecheck"
```

The guided setup asks for:

```text
Integration branch
IANA timezone
Daily review time
Default dispatch time
Morning report time
Maximum unattended runtime
Memory verification age
Validation commands
Security commands
Documentation map
Visual evidence mode
Goal branch prefix
Additional project-specific instructions
Planning pattern modes
Roadmap behavior
Primary and enabled agent surfaces
Persistent scheduler provider
Execution enabled
```

Keep execution disabled unless you intentionally want approved goals to be eligible for scheduled or manual execution.

## Install With An Answers File

Use `--configuration` for repeatable setup:

```json
{
  "timezone": "America/Chicago",
  "schedules": {
    "review": "20:00",
    "dispatch": "22:00",
    "report": "07:00"
  },
  "validation_commands": [
    "pnpm typecheck",
    "pnpm test"
  ],
  "security_commands": [],
  "documentation_map": {
    "project-memory": "docs/project-memory/INDEX.md",
    "project-roadmap": "docs/project-roadmap/INDEX.md",
    "architecture": "docs/architecture.md"
  },
  "visual_evidence_mode": "when-applicable",
  "branch_prefix": "continuity",
  "project_instructions": [
    "Run backend contract checks before frontend build when API contracts change."
  ],
  "planning_patterns": {
    "evidence_triage": "auto",
    "decision_mapping": "auto",
    "delivery_slicing": "auto",
    "tracker_provider": "local"
  },
  "roadmap": {
    "enabled": true,
    "agile_mode": "hybrid",
    "hierarchy": "full",
    "ui_mode": "local-read-only",
    "shared_notes": "explicit-project-inbox",
    "production_distribution": "forbidden"
  },
  "agent_surfaces": {
    "primary": "codex",
    "enabled": ["codex", "claude-code", "cursor", "windsurf"]
  },
  "scheduler": {
    "provider": "codex",
    "sweep_minutes": 15,
    "business_days": [0, 1, 2, 3, 4],
    "retry_limit": 2,
    "retry_backoff_minutes": 15,
    "stale_after_minutes": 45,
    "portfolio_max_concurrency": 4
  },
  "execution_enabled": false
}
```

Then run:

```text
python3 continuity-suite/installer/install.py \
  --project-root /Volumes/OPENFRONT/example-project \
  --project-id example-project \
  --integration-branch main \
  --configuration /path/to/answers.json
```

## Reconfigure After Installation

From inside the installed project:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project recommendations
.agents/continuity/bin/continuity --project-root "$PWD" project configure --interactive --actor "your-name"
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
```

For deterministic changes:

```text
.agents/continuity/bin/continuity \
  --project-root "$PWD" \
  --json project configure \
  --answers-file /path/to/answers.json \
  --actor "your-name"
```

Do not hand-edit `.agents/skills/continuity-local/SKILL.md`. It is generated from `.continuity/project-behavior.json`.

## Choose An Agent Surface

`AGENTS.md`, `.agents/skills/`, and `.agents/continuity/` remain canonical regardless of the selected surface. Continuity generates thin native adapters and regenerates them whenever project configuration changes.

| Surface | Generated project entrypoint | Typical invocation |
| --- | --- | --- |
| Codex | `AGENTS.md` and `.agents/skills/` | `$continuity-plan` |
| Claude Code | `CLAUDE.md` importing `AGENTS.md`, plus `.claude/skills/` | `/continuity-plan` |
| Cursor | `.cursor/rules/continuity.mdc` and `.cursor/commands/continuity-*.md` | `/continuity-plan` |
| Windsurf | `AGENTS.md` and `.windsurf/skills/` | `@continuity-plan` |
| Generic | `AGENTS.md` and the project-local CLI | Ask the agent to use `continuity-plan` |

Choose one primary surface and one or more enabled surfaces. Teams may enable several surfaces in the same repository. Do not edit generated adapter copies directly; update the canonical skill or project behavior and rerun configuration. `project doctor` reports missing adapters.

## Daily Routine

Use these skill calls in normal work:

```text
Morning:
  $continuity-report

During the day:
  $continuity-capture

When notes need sorting:
  $continuity-triage

When planning work:
  $continuity-memory
  $continuity-roadmap
  $continuity-plan

When a plan is explicitly approved:
  $continuity-dispatch

When an approved dispatched goal is assigned:
  $continuity-execute
  $continuity-test
  $continuity-merge
```

Feedback follows the same note path:

```text
feedback -> $continuity-capture -> $continuity-triage -> memory candidate -> approved memory promotion
```

Raw feedback remains private and non-authorizing. Searchable memory contains only curated, sanitized, promoted knowledge.

## Note Lifecycle

Every captured atomic note has its own timestamps and work status:

```text
created_at       when the atomic note was created or imported
updated_at       when Continuity last changed its routing or work state
routing_status   captured, route, defer, archive, or promote
work_status      open, deferred, planned, queued, dispatched, running, validating,
                 review-ready, completed, partially-completed, blocked, cancelled,
                 not-applicable, or archived
```

Use `routing_status` to understand where the note went. Use `work_status` to understand whether the underlying work is still incomplete.

Notes do not move to a branch or PR directly. A note that requires action becomes useful for execution only after triage connects it to roadmap context and `$continuity-plan` creates an approval-ready goal. When a goal is created from `source_note_ids`, those notes move to `planned`. Approval moves them to `queued`; dispatch moves them to `dispatched`; execution updates move them through `running`, `validating`, `review-ready`, `partially-completed`, `blocked`, or `cancelled`. Human merge evidence moves review-ready work to `completed`.

If a note is too separate from the current branch or PR, keep it open, deferred, or roadmap-linked for a later pass. The user can later retrieve incomplete roadmap-linked work and manually run:

```text
$continuity-roadmap
$continuity-plan
$continuity-dispatch
```

That keeps unrelated work from being forced into the wrong PR while preserving a clear path to act on it later.

## Scheduled Tasks

The project stores schedule intent in `.continuity/project.json`:

```json
{
  "schedules": {
    "review": "20:00",
    "dispatch": "22:00",
    "report": "07:00"
  }
}
```

The selected scheduler owns actual persistent task registration. Continuity records the provider and operating policy in the hash-bound project behavior:

```text
codex        register Codex scheduled tasks or automations
claude-code  register Claude Code Desktop tasks or cloud routines
external     use cron, launchd, GitHub Actions, CI, or another scheduler
none         keep schedule intent without registering recurring tasks
```

The policy includes the supervisor sweep interval, business days, retry allowance and backoff, stale-run timeout, and portfolio concurrency cap. Review and dispatch run only on nights preceding configured business days; the decision report runs on configured business-day mornings.

Selecting a provider does not silently create a machine-level job. Create one recurring supervisor task in the selected surface using:

```text
.agents/continuity/automation/portfolio-supervisor.md
```

Run it at the configured `sweep_minutes` interval. Give the task the developer-local workspace roots it may scan. After the scheduling surface returns its task ID, record the receipt inside every enrolled project covered by that supervisor:

```text
.agents/continuity/bin/continuity --project-root /path/to/project scheduler register \
  --task-id <provider-task-id> \
  --root /workspace/root \
  --actor <identity>
```

The receipt is ignored private state. It contains only provider, task ID, roots, timestamps, and the behavior hash. `project doctor` reports `requires-user-registration`, `registered`, or `stale`, and also fails on stale scheduled runs.

Scheduler tasks should use:

```text
.agents/continuity/automation/portfolio-supervisor.md
.agents/continuity/automation/nightly-review.md
.agents/continuity/automation/default-dispatch.md
.agents/continuity/automation/morning-report.md
```

Portfolio-level scheduler commands operate over developer-configured workspace roots:

```text
continuity --json portfolio discover --root /workspace/root
continuity --json portfolio due --root /workspace/root
continuity --json portfolio queue --root /workspace/root
continuity --json portfolio actions --root /workspace/root --root /another/workspace/root
```

`portfolio actions` calculates what is due from each project's timezone and schedule. It suppresses completed idempotency keys, enforces retry backoff, identifies stale runs, omits dispatch when no approved goal is due, and applies the smallest portfolio concurrency cap across all roots passed in one call. Excess runnable work is returned as `capacity-deferred` for a later sweep. The supervisor starts one project-scoped task per `due` or `retry` action, records `scheduler run-start`, sends heartbeats, and records `scheduler run-finish`. A dispatch run cannot finish successfully until its goal reaches `review-ready`.

For stale work, run `scheduler recover`. Recovery marks the matching run stale and may block only its matching active goal and release only its matching lock. It does not resume work or infer a decision. For Codex or Claude Code, the supervisor must be able to start authenticated project tasks. An external scheduler must invoke an authenticated agent surface; a plain cron process can calculate due actions but cannot perform model-driven review or implementation by itself.

## Execution Layer

The project-specific execution layer is the generated skill:

```text
.agents/skills/continuity-local/SKILL.md
```

Every task-specific Continuity skill must apply `$continuity-local`. It contains the project-specific schedules, validation commands, security commands, documentation map, roadmap behavior, agent surfaces, scheduler provider, branch prefix, project instructions, and execution enrollment.

Execution remains blocked unless:

```text
execution_enabled: true
```

and the goal is explicitly approved, due or manually started, dependency-satisfied, locked to one active code-changing goal, preflight-compliant, and hash-aligned with the reviewed plan.

## Quality And Merge Gates

Continuity has two explicit post-implementation skills:

```text
$continuity-test
$continuity-merge
```

`$continuity-test` combines project-specific checks from `validation_commands`, goal-specific `required_checks`, configured `security_commands`, targeted regressions, code review, and evidence-based security review. It records a report with:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test plan <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" test record <goal-id> --status <passed|failed> --summary "<result>" --update-gates
```

`$continuity-merge` assesses PR readiness and merge safety after the test report passes. It checks branch focus, base freshness, working tree cleanliness, PR evidence, and compliance status:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge assess <goal-id> --branch <branch> --pr-url <pull-request-url> --update-gate
```

After overnight delivery passes every gate, record `review-ready` and stop. After a human reviews or merges the PR, record that fact separately:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --evidence "<review evidence>"
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --merge-commit <sha> --evidence "<merge evidence>"
```

Review without a merge leaves the goal `review-ready`. A recorded merge commit moves it to `completed`. Continuity can report readiness, failures, and missing evidence. It must not auto-merge, force-push, or treat an agent's judgment as human review.

## Verify An Install

From inside the target project:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
.agents/continuity/bin/continuity --project-root "$PWD" memory audit
.agents/continuity/bin/continuity --project-root "$PWD" roadmap audit
```

From the Continuity suite checkout:

```text
python3 -m unittest discover -s continuity-suite/tests -v
python3 -m py_compile continuity-suite/bin/continuity continuity-suite/lib/*.py continuity-suite/installer/install.py
```
