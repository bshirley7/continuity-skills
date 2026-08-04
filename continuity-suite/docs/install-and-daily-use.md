# Install and Daily Use

This guide explains where to run Continuity installation, what gets installed into a project, how to choose schedules and project requirements, and how to use the installed skills in a daily routine. For a shorter first local install path, read [Quickstart](quickstart.md). Read [Continuity Operating Workflow](operating-workflow.md) for the complete day-to-night-to-morning process, authority model, recovery behavior, and operational readiness checklist.

## Where To Run Installation

Run the installer from the Continuity suite checkout and pass the target project path with `--project-root`.

Example from a Continuity suite checkout:

```text
cd /path/to/continuity-checkout
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck" \
  --validation "pnpm test"
```

Enable the optional design collection when the project needs reviewed design directions before implementation planning:

```text
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id example-project \
  --integration-branch main \
  --collection design
```

The design workflow uses installed offline references, keeps drafts private, and publishes only an exact hash-approved `docs/design/design.md`. For React and web work it defaults to a complete private prototype: Continuity inspects the installed framework, UI libraries, components, tokens, and assets; maps reuse, composition, extension, and custom work; renders representative desktop, tablet, and mobile output; completes artifact critique; and validates the candidate before approval. For cinematic media storytelling, it identifies the intended outcome before the playback technique, expands creative search through a private narrative-spine burst, binds actual media beats or loops to standalone commercial chapters, derives interface language from the subject, and chooses among looping hero, chapter loops, normal playback, scroll-linked playback, and still equivalents. Validation covers loop seams, posters, autoplay rejection, persistent-motion control, decoder and resource behavior, reduced-motion and no-video modes, plus bounded seeking when scroll-linked playback is actually used. The private prototype stays outside product routes and build inputs. Neither the prototype nor design approval authorizes implementation.

If your terminal is already inside the target project, you can still run the installer by using the absolute path to the suite:

```text
cd /path/to/project
python3 /path/to/continuity-checkout/continuity-suite/installer/install.py \
  --project-root "$PWD" \
  --project-id example-project \
  --integration-branch main \
  --validation "pnpm typecheck"
```

So the answer is: initial install comes from the main Continuity suite checkout, pointed at the project folder. After installation, daily use happens inside the project.

Every applied install and update checks GitHub CLI authentication after the project files are safely installed. If the active `github.com` account is already healthy and has the `project` scope, nothing interrupts the install. Otherwise, an attached terminal automatically receives GitHub's browser/device login or scope-refresh flow:

```text
gh auth login --hostname github.com --web --scopes project
gh auth refresh --hostname github.com --scopes project
```

GitHub CLI owns the credential and Continuity never reads, prints, or stores the token. If no interactive terminal is available, the install completes and its JSON result reports `authentication-required` with the exact command to run; it never waits indefinitely. Use `--skip-github-auth` only for an intentionally unattended or offline installation. The same option is available on `suite update` and `portfolio update`.

## What Gets Installed

Continuity writes project-local control files into the target project:

```text
.agents/skills/                         Continuity skills
.agents/skills/continuity-local/        generated project-specific behavior skill
.agents/continuity/                     project-local CLI, schemas, templates, automation prompts
.agents/references/continuity-contract.md
.agents/references/development-assurance-standard.md
.agents/references/testing-and-merge-standard.md
.agents/references/workflow-handoffs.md
.agents/references/decision-lenses.md
.agents/references/output-quality-rubrics.md
.agents/skills/continuity-*/references/  applied examples and stage guidance
.claude/commands/continuity-*.md        slash-command shims, for example /continuity-capture
.cursor/commands/continuity-*.md        slash-command shims, for example /continuity-triage
.continuity/project.json                schedule and enrollment manifest
.continuity/config.json                 project configuration
.continuity/project-behavior.json       hash-bound project-specific behavior
.continuity/scheduler.json              scheduler handoff and registration state
.continuity/private/                    ignored notes, queues, goals, locks, indexes
docs/project-memory/                    committed searchable memory
docs/project-roadmap/                   committed roadmap records
.continuity/shared-notes/packets/       reviewed shared-note packets
docs/design/design.md                   exact approved design document when Design is enabled
```

The installer also updates managed blocks in `AGENTS.md` and `.gitignore` and returns a `github_auth` result describing the authenticated login or required next action.

The shared references define suite-wide contracts, handoffs, lenses, and quality standards. Skill-local references provide applied decision tables and examples for only that stage. Codex and Claude Code adapters receive both sets; Cursor, Windsurf, and generic surfaces route through the same canonical project-local files.

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
  --project-root /path/to/project \
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
Required GitHub check names
Required approving GitHub reviewer count
Exact human-authorized GitHub CLI merge enabled
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

The local first-run prerequisite is `git` on macOS or Linux. The installer creates project configuration and leaves execution disabled unless `--enable-execution` is supplied. Daily local use records explicit human approvals with the approving identity and authorization text; terminal commands still run through the host's normal user approval flow.

SSH-signed approvals are optional hardening for unattended scheduling and action-specific consequential transitions, not a universal interactive requirement. Routine `/goal` and `goal proceed` work records a hash-bound conversation receipt without asking the human to sign again. Use `--require-signed-approvals` when the project should cryptographically enforce approver identity for unattended approvals, dispositions, resume authorizations, and shared-packet approvals. In that mode, configure a trusted approver before enabling unattended execution:

```text
.agents/continuity/bin/continuity --project-root "$PWD" approval trust add --identity <github-login> --public-key <ssh-public-key>
```

This command prepares a tracked trust-store change; it does not authorize the new key immediately. Commit `.continuity/trusted-approvers`, merge it through protected human review on the integration branch, and fetch that branch. Signed operations compare the local file byte-for-byte with `origin/<integration-branch>` and fail closed on drift.

For production execution, also plan for `gh` when hosted pull-request state must be verified and `age` when encrypted private-state backups are required. Configure an external audit checkpoint and immediately verified encrypted backup before enabling production execution.

For safe tagged upgrades, managed-file conflict handling, encrypted backup, and rollback, follow [Releases, Updates, and Recovery](releases-updates-and-recovery.md). Do not use repeated unpinned installation from a moving branch as the production update process.

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
  "github_required_checks": ["typecheck", "test"],
  "github_required_reviewers": 1,
  "github_cli_merge_enabled": false,
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

Replace `typecheck` and `test` with the exact check-run names reported by the project repository. Continuity requires every named check to be present and successful, and it also blocks on any other observed check that is pending or unsuccessful. `project doctor` keeps PR-based execution unhealthy when execution is enabled but this list is empty.

Then run:

```text
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
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
| Codex | `AGENTS.md`, `.agents/skills/`, plus installed slash-command shims for compatible hosts | `$continuity-plan` or `/continuity-plan` where slash commands are supported |
| Claude Code | Default `.claude/commands/continuity-*.md`; enabling the surface also adds `CLAUDE.md` and `.claude/skills/` | `/continuity-plan` |
| Cursor | Default `.cursor/commands/continuity-*.md`; enabling the surface also adds `.cursor/rules/continuity.mdc` | `/continuity-plan` |
| Windsurf | `AGENTS.md` and `.windsurf/skills/` | `@continuity-plan` |
| Generic | `AGENTS.md` and the project-local CLI | Ask the agent to use `continuity-plan` |

Choose one primary surface and one or more enabled surfaces. Teams may enable several surfaces in the same repository. Slash-command shims are installed for every project so `/continuity-capture`, `/continuity-triage`, and the other Continuity workflows can route back to the canonical `.agents/skills/` contracts without duplicating skill source. Do not edit generated adapter copies directly; update the canonical skill or project behavior and rerun configuration. `project doctor` reports missing adapters.

For multiple enrolled repositories, use the controller's `portfolio update --root <workspace>` preview and add `--apply` only after reviewing every project result. The portfolio command preserves per-project snapshots, configuration migration, custom-skill ownership, doctor checks, and automatic rollback rather than copying files across repositories directly.

## Daily Routine

Use these skill calls in normal work:

```text
Morning:
  $continuity-report
  /continuity-report
  continuity workflow status

During the day:
  $continuity-capture
  /continuity-capture

When notes need sorting:
  $continuity-triage
  /continuity-triage

When planning work:
  $continuity-memory
  $continuity-roadmap
  $continuity-plan
  /continuity-memory
  /continuity-roadmap
  /continuity-plan

When a plan is explicitly approved:
  $continuity-dispatch
  /continuity-dispatch

When an approved dispatched goal is assigned:
  $continuity-execute
  $continuity-test
  $continuity-product-audit
  $continuity-merge
  /continuity-execute
  /continuity-test
  /continuity-product-audit
  /continuity-merge
```

Feedback follows the same note path:

```text
feedback -> $continuity-capture -> $continuity-triage -> memory candidate -> approved memory promotion
```

Raw feedback remains private and non-authorizing. Trusted-scope memory contains only curated, sanitized, promoted knowledge. Explicit private/all indexing also makes raw captures searchable by text and local concept similarity without treating them as canonical truth.

One `$continuity-capture` call may contain one callout, a complete set of meeting notes, or one pointed-to PRD or feature request. For a document, Continuity reads the complete local Markdown/plain-text source, preserves an exact ignored snapshot and hash, separates its context, decisions, requirements, risks, questions, and later work into anchored atomic items, and returns one capture ID plus every item ID. A changed hash creates a linked revision; unchanged items do not re-enter queues. The source remains product intent rather than implementation evidence, and no capture authorizes action. See [The Daily Operating Cycle](operating-workflow.md#1-capture-information-during-normal-work) for the input format and command.

Use the machine handoff before and after any skill:

```text
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --note-id <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --memory-id <memory-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --roadmap-id <roadmap-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --packet-id <packet-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --audit-id <audit-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
```

Use `--capture-id` immediately after capture to receive all per-item handoffs. Use the narrowest available selector after that. Project-wide status prioritizes the current queues for general routing; it does not override the selected subject's stage or next skill.

## Optional GitHub Projects connection

GitHub Projects is an optional hosted operational surface, not a replacement for canonical roadmap Markdown. It keeps task status accessible when the local roadmap server is not running. Configure `planning_patterns.tracker_provider` as `github`, authenticate the intended account with the `project` scope, and connect once:

```text
gh auth login --hostname github.com --web --scopes project
.agents/continuity/bin/continuity --project-root "$PWD" roadmap github-projects connect \
  --owner-type user --owner <authenticated-login> --title "<project title>" --visibility PRIVATE
.agents/continuity/bin/continuity --project-root "$PWD" roadmap github-projects status
```

Add `--project-number <number>` to attach an existing Project instead of creating one. The command verifies the active login, stable GitHub account ID, `project` scope, exact owner, stable Project ID, and Project update access. It configures fields, records read/write/create/edit capabilities with deletion disabled, and performs the first sync without reading or storing the token.

```text
.agents/continuity/bin/continuity --project-root "$PWD" roadmap github-projects sync
```

The connection invocation is durable authorization for automatic sanitized roadmap and goal-status updates to that one Project. Goal and approved-roadmap lifecycle transitions trigger best-effort synchronization; a remote failure is recorded as advisory and never rolls back the local transition. Renew only for a different account, destination, visibility, capability set, deletion policy, or published data class. Raw notes, exact requests, approval text, private evidence, memory, and credentials are never projected. Remote edits remain reconciliation proposals and cannot authorize or complete local work.

The older bootstrap and plan/approve/apply commands remain available for unconnected one-off exports. New integrations should follow the provider-neutral tracker contract used by GitHub so Notion, Trello, Jira, or another provider can be added without creating a second planning or authorization workflow.

`workflow status` reports the current stage, completed evidence, blockers, next skill, human requirements, and exact allowed command templates. A submitted `/goal` or the user's “proceed” instruction is the routine interactive approval boundary; the matching `goal activate` or `goal proceed` command records it and continues without another user prompt.

For a manual end-to-end run, invoke `$continuity-workflow` or `/continuity-workflow` with the request and any known subject ID. The runner re-reads this handoff after every task skill and immediately continues through `next_skill`. A failed test, stale artifact, merge-safety finding, or recoverable tool error routes into remediation and does not end the workflow. The run pauses only when workflow status explicitly sets `human_required: true`; after the recorded approval, invoke the same workflow again and it resumes from canonical state without replaying completed stages.

## Note Lifecycle

Every captured atomic note has its own timestamps and work status:

```text
created_at       when the atomic note was created or imported
updated_at       when Continuity last changed its routing or work state
occurred_at      when the described situation or feedback occurred
perspective      internal, external, mixed, or unknown
sentiment        positive, negative, mixed, neutral, or unknown
occurrence_type  feedback, behavior, decision, change, need, risk, success, failure,
                 constraint, or observation
impact           low, medium, high, critical, or unknown
confidence       low, medium, high, or unknown
actionability    context, monitor, plan, or urgent-review
stakeholders     people or groups involved, when known
themes           stable concepts used for retrieval and pattern aggregation
routing_status   captured, route, defer, archive, or promote
work_status      open, deferred, planned, queued, dispatched, running, validating,
                 review-ready, completed, partially-completed, blocked, cancelled,
                 not-applicable, or archived
```

Use `routing_status` to understand where the note went. Use `work_status` as a compact compatibility summary. Use `workflow status --note-id <note-id>` for the exact current stage, when that stage began, planning disposition, separate goal tracks, relationship candidates, and complete dated timeline.

Use `memory similar "<situation>" --scope all` for local vector-space concept retrieval across canonical memory, complete document snapshots, and private atomic captures. Official in-project documents appear as trusted `project-intent`; supplied references remain private. Both are labeled as product intent rather than verified implementation behavior. Use `note patterns` to aggregate repeated stakeholder/theme occurrences and produce recommendations such as preserving repeated positive outcomes, mitigating repeated negative signals, or designing revision-prone work for adaptability. These outputs inform triage and planning only.

Notes do not move to a branch or PR directly. During planning, every source note must be explicitly marked `current-goal`, `later`, `context-only`, or `duplicate`, with a reason. New goal inputs fail closed when a source note lacks a disposition; the CLI never silently treats omitted new input as current scope. Later work requires a review date or roadmap anchor. Only current-goal notes become `planned`, and they become `running` only after canonical execution begins. The plan renders these decisions and binds them into its approval hash.

Use `note related-goals <note-id>` to inspect local similarity suggestions. Similarity never creates a task link. Confirm current scope through `goal create` or `goal revise`; use `note relate` for explicit later, context-only, or duplicate relationships:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note related-goals <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" note relate <note-id> --goal-id <goal-id> --disposition later --reason <reason> --review-after <iso-date-time> --actor <human>
```

The lifecycle timeline is derived from existing capture, triage, goal, compliance, run, test, merge, and human-review timestamps. Goal execution events appear only when the note was `current-goal` for that plan version and the event occurred after the relationship decision. Context-only, later, and duplicate links therefore cannot inherit implementation history. No extra scheduler or parallel status database is required.

Use `note queue --queue <knowledge|questions|documentation|backlog|planning>` for current work. Files under `.continuity/private/queues/` are append-only audit snapshots, not authoritative planning inputs. Later notes return when their review date is due; roadmap-anchored later work remains on its roadmap path. `project doctor` reports legacy links, goals missing explicit note dispositions, missing notes, malformed timestamps, and link disagreements.

If a note is too separate from the current branch or PR, keep it open, deferred, or roadmap-linked for a later pass. The user can later retrieve incomplete roadmap-linked work and manually run:

```text
$continuity-roadmap
$continuity-plan
$continuity-dispatch
```

That keeps unrelated work from being forced into the wrong PR while preserving a clear path to act on it later.

### Share selected context

Raw notes remain private. To share selected atomic context with collaborators on the same project, prepare a sanitized packet, review it, and have a trusted human approve the exact packet version:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note share prepare <note-id> --target-project <project-id> --sender <identity>
.agents/continuity/bin/continuity --project-root "$PWD" note share approve <packet-id> --version <version> --approved-by <identity> --authorization-text "Approve <packet-id> version <version> for <project-id>"
.agents/continuity/bin/continuity --project-root "$PWD" note share publish <packet-id>
```

In a signed-approval project, add `--signing-key "$HOME/.ssh/id_ed25519"` and use an identity already present in `.continuity/trusted-approvers`. Publication re-verifies any required SSH signature and packet hash, then creates an isolated branch and human-reviewed PR. Imported packet items enter normal triage as dated, non-authorizing private captures; packet approval never approves a goal or execution.

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
claude-code  register a Claude Desktop local scheduled task
external     use cron, launchd, GitHub Actions, CI, or another scheduler
none         keep schedule intent without registering recurring tasks
```

The policy includes the supervisor sweep interval, business days, retry allowance and backoff, stale-run timeout, and portfolio concurrency cap. Review and dispatch run only on nights preceding configured business days; the decision report runs on configured business-day mornings.

Selecting a provider does not silently create a machine-level job. Create one recurring supervisor task in the selected surface using:

```text
.agents/continuity/automation/portfolio-supervisor.md
```

For Codex, render the exact provider definition instead of transcribing schedules and roots:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json scheduler adapter codex render --root /workspace/root
```

For Claude Desktop, use the parallel
`scheduler adapter claude-code render` command. A Claude cloud routine cannot
replace this local-state adapter because it starts from a fresh clone.

Use the rendered self-contained `prompt` verbatim. Keep the provider task
paused while creating it, replace only the supervisor-task placeholder with
the returned task ID, and inspect the provider's raw saved prompt before
registration. The remaining sweep placeholder must equal
`literal_placeholders.sweep_id` exactly once. Markdown bold markers or
backslash-escaped underscores invalidate the task definition and must be
corrected before the first run.

After creating the selected provider task and registering its returned task ID, exercise and record `claim-replay-rejected`, `stale-registration-rejected`, and `remote-lease-contention-rejected` with `scheduler adapter <provider> record-probe`. Each production record requires concrete evidence and the evidence artifact SHA-256. In a signed-approval project, also include `--signing-key` from an integration-branch-anchored approver. Require `scheduler adapter <provider> verify` to observe and verify those current-behavior probe records, two sweeps, and one claimed no-op review or report run before enabling dispatch.

Run it at the configured `sweep_minutes` interval. Give the task the developer-local workspace roots it may scan. After the scheduling surface returns its task ID, record the receipt inside every enrolled project covered by that supervisor:

```text
.agents/continuity/bin/continuity --project-root /path/to/project scheduler register \
  --task-id <provider-task-id> \
  --root /workspace/root \
  --actor <identity>
```

The receipt is ignored private state. It contains only provider, task ID, roots, timestamps, sweep heartbeat, and the behavior hash. Registration is an expiring lease: `project doctor` reports `requires-user-registration`, `registered`, or `stale`, and fails when the supervisor heartbeat or a scheduled run is stale. A receipt alone is not proof that a provider task is still operating.

Scheduler tasks should use:

```text
.agents/continuity/automation/portfolio-supervisor.md
.agents/continuity/automation/provider-adapter-contract.md
.agents/continuity/automation/nightly-review.md
.agents/continuity/automation/default-dispatch.md
.agents/continuity/automation/morning-report.md
```

Portfolio-level scheduler commands operate over developer-configured workspace roots:

```text
continuity --json portfolio discover --root /workspace/root
continuity --json portfolio due --root /workspace/root
continuity --json portfolio queue --root /workspace/root
continuity --json portfolio actions --root /workspace/root --root /another/workspace/root \
  --supervisor-task-id <registered-task-id> --sweep-id <unique-sweep-id>
```

`portfolio actions` refreshes the expiring supervisor heartbeat and calculates what is due from each project's timezone and schedule. It suppresses completed idempotency keys, enforces retry backoff, identifies stale runs, requires the same-date review to succeed before scheduled dispatch, and applies the smallest portfolio concurrency cap against both active runs and unconsumed reservations. Each `due` or `retry` result has a short-lived one-time claim token. Excess work is `capacity-deferred`; dispatch awaiting review is `waiting-for-review`. The child task passes the exact idempotency key and claim token to `scheduler run-start`, which atomically consumes it before work. Fabricated, expired, duplicate, wrong-goal, and over-capacity starts fail closed.

Before any code-changing start, acquire the project remote lease. The lease is an unmerged fast-forward-only Git ref and contains only project, goal, attempt, expiry, and an owner fingerprint. The CLI derives the exact current execution attempt from the goal. `scheduler run-start` binds it locally to the consuming provider run, task, and idempotency key. A concurrent acquisition, wrong goal attempt, or unreachable remote fails closed:

```text
.agents/continuity/bin/continuity --project-root "$PWD" scheduler lease acquire --owner <operator> --goal-id <goal-id> --remote origin
```

Only completion of the bound dispatch run releases its lease; review and report completion cannot release an execution lease. Use `scheduler lease status` for inspection. Explicit release requires the exact binding: `scheduler lease release --reason <reason> --goal-id <goal-id> --attempt-id <attempt-id>`.

Portfolio reporting must use the deterministic allowlist command:

```text
.agents/continuity/bin/continuity --json portfolio report --sanitized --root /workspace/root
```

It emits project-level counts and health states without raw note text, paths, approvals, task IDs, claims, locks, credentials, or private evidence links.

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

Continuity has three explicit post-implementation skills:

```text
$continuity-test
$continuity-product-audit
$continuity-merge
```

`$continuity-test` combines project-specific checks from `validation_commands`, goal-specific `required_checks`, configured `security_commands`, targeted regressions, code review, and evidence-based security review. It records a report with:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test plan <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" test run <goal-id> --worktree <worktree> --branch <branch>
.agents/continuity/bin/continuity --project-root "$PWD" test record <goal-id> --status <passed|failed> --summary "<result>" --update-gates
```

`test run` executes configured validation, goal-specific, and security commands directly without shell syntax. It verifies that the worktree belongs to the enrolled repository and is on the branch recorded for the goal, then records argv, output, exit status, approved plan hash, behavior hash, commit, repository identity, and a source fingerprint that includes tracked diffs and untracked-file content. `test record --status passed` and merge assessment fail when that evidence is absent or any binding has changed.

The enforced delivery order is: preflight; isolated worktree; implementation; candidate checks; documentation, memory, roadmap, and evidence artifacts; commit; final source-bound test run; source-bound product-conformance audit or explicit not-applicable evidence; push and draft PR; PR/head/base-bound merge assessment; `review-ready`; human disposition. Any source or branch change after the final run makes its evidence stale.

`$continuity-product-audit` compares a baseline, candidate, release, or drift
target with applicable approved goals, PRDs, documentation, memory, insights,
and roadmap sources. It records portable evidence, source authority and time
horizon, classified findings, coverage, hashes, and non-authorizing finding
captures. Only current-goal mismatches can block the product-conformance gate.

`$continuity-merge` assesses PR readiness and merge safety only after the final tested commit is pushed to a draft PR. It checks branch focus, base freshness, working tree cleanliness, remote and PR head identity, PR base, evidence, and compliance status:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge assess <goal-id> --branch <branch> --pr-url <pull-request-url> --update-gate
```

If the PR was merged before Continuity recorded `review-ready`, rerun the same assessment. It accepts that recovery path only when GitHub verifies the exact tested head and merge commit, the merge commit is reachable from the remote integration branch, and every current local, hosted, reviewer, and conformance gate passes. Then record `review-ready` and the verified `merged` human disposition normally; do not cancel delivered work or edit private state.

After overnight delivery passes every gate, record `review-ready` and stop. After a human reviews or merges the PR, record that fact separately:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --disposition approved --evidence "<review evidence>"
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --disposition changes-requested --evidence "<requested change>"
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --disposition merged --merge-commit <sha> --evidence "<merge evidence>"
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> --pr-url <pull-request-url> --merged-by "<identity>" --disposition closed --evidence "<closure reason>"
```

Add `--signing-key <ssh-private-key>` only when `.continuity/config.json` has `require_signed_approvals: true`.

For projects that explicitly set `github_cli_merge_enabled: true`, a human can approve the merge inside an interactive Codex task and let Continuity perform the direct GitHub CLI action. First read the exact PR URL and head SHA from `workflow status --goal-id <goal-id>`, choose a merge method, and supply authorization text matching the command exactly:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge execute <goal-id> \
  --pr-url <pull-request-url> \
  --head-sha <full-40-character-head-sha> \
  --merge-method squash \
  --authorized-by <authenticated-github-login> \
  --authorization-text "Merge <goal-id> PR <pull-request-url> at <full-40-character-head-sha> using squash"
```

This command uses `gh pr merge --squash --match-head-commit <sha>` only after rechecking the current merge assessment, non-draft PR, base, exact head, required checks, reviewer threshold, immediately mergeable state, and authenticated GitHub identity. It never uses `--admin`, `--auto`, or force-push. The setting defaults to `false`, and scheduled or unattended work still stops at `review-ready`. Signed-approval projects also require `--signing-key` and verify the project trust anchor before the merge.

`approved` leaves the goal `review-ready`. `changes-requested` archives the attempt, creates a fresh execution manifest, and invalidates downstream gates. `approved` and `merged` require current source-bound evidence. `changes-requested` and `closed` remain recordable when that evidence is stale because they do not authorize delivery; their review records retain the stale-evidence reasons. If no PR disposition can be recorded, `goal cancel <goal-id> --actor <identity> --reason <reason>` provides an audited review-ready closure fallback. In-scope rework resumes only with explicit authorization naming the same goal and approved plan version:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal resume <goal-id> --actor "<identity>" --authorization-text "Resume <goal-id> under approved plan v<version>"
```

Add `--signing-key <ssh-private-key>` here as well when signed approvals are enabled.

The merge authorization, disposition, and resume receipts bind the goal, approved plan hash/version, execution attempt, actor, PR and head where applicable, evidence or authorization text, timestamp, and nonce. Signed-approval projects additionally bind the SSH signature and anchored trusted approver. Expanded scope uses `goal revise` and fresh approval. `merged` moves the goal to `completed`; `closed` cancels it. Continuity must not auto-merge, use administrator bypass, force-push, or treat an agent's judgment as human review.

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
