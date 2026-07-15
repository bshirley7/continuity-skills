# Continuity Suite

Continuity turns project conversations and notes into searchable memory, roadmap context, reviewable plans, supervised off-hours execution, and next-business-day decision reports.

## Start Here

- For the exact installation and daily-use workflow, read [Install and Daily Use](docs/install-and-daily-use.md).
- For the complete day-to-night-to-morning operating model, read [Operating Workflow](docs/operating-workflow.md).
- For tagged updates, managed-file drift, encrypted backup, and rollback, read [Releases, Updates, and Recovery](docs/releases-updates-and-recovery.md).
- For the first controlled off-hours run, use the [Next-Business-Day Production Pilot](docs/production-pilot.md).
- For the full suite contract, installed layout, guardrails, and command reference, read [SUITE.md](SUITE.md).
- For the safety model every skill follows, read [Continuity Contract](references/continuity-contract.md).
- For skill inputs, outputs, blockers, and next-stage expectations, read [Workflow Handoffs](references/workflow-handoffs.md).
- For judgment prompts and measurable output standards, read [Decision Lenses](references/decision-lenses.md) and [Output Quality Rubrics](references/output-quality-rubrics.md).
- For quality and merge gates, read [Testing and Merge Standard](references/testing-and-merge-standard.md).
- For Codex, Claude Code, and external scheduler requirements, read [Provider Adapter Contract](automation/provider-adapter-contract.md).
- For contribution rules and review expectations, read [Contributing](CONTRIBUTING.md).

## Short Answer

Initial installation is normally run from the Continuity suite checkout and pointed at a project folder:

```text
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id stable-project-id \
  --integration-branch main \
  --validation "project validation command"
```

After installation, day-to-day use happens inside the project with `$continuity-*` skills and the installed project-local CLI at `.agents/continuity/bin/continuity`.
The installer also creates `.claude/commands/continuity-*.md` and `.cursor/commands/continuity-*.md` shims so compatible hosts can invoke the same workflows as slash commands such as `/continuity-capture` and `/continuity-triage`.

The guided installer can save portable user defaults in `~/.continuity/defaults.json`, then generate isolated project controls for Codex, Claude Code, Cursor, Windsurf, or another `AGENTS.md`-aware surface. One provider-owned portfolio supervisor calculates due actions, refreshes an expiring heartbeat, atomically reserves capacity, and issues one-time project claims. Repository-specific commands, instructions, notes, approvals, roadmap state, and execution enrollment never move into the user-default profile.

## Daily Skill Calls

```text
$continuity           configure, audit, and route the suite
$continuity-capture   capture one callout or a batch of meeting notes and feedback
$continuity-triage    classify notes into context, questions, decisions, roadmap, or plans
$continuity-memory    search or promote trusted project memory
$continuity-roadmap   inspect or update approved roadmap context
$continuity-plan      create approval-ready plans
$continuity-dispatch  approve, queue, or manually start approved goals
$continuity-execute   execute one approved dispatched goal
$continuity-test      run and record quality, validation, and security gates
$continuity-merge     assess PR readiness and record human merge review
$continuity-report    summarize status, blockers, memory, roadmap, and evidence
$continuity-share     prepare sanitized note packets for explicit sharing
```

Every skill uses `continuity workflow status` as its shared machine handoff. Exact note status includes a derived dated lifecycle, planning disposition, separate goal tracks, and non-authorizing relationship candidates. Plans classify every source note as current-goal, later, context-only, or duplicate; only current-goal notes adopt execution state. Unqualified status remains project routing context only.

Shared references explain that machine contract, while each task skill includes a compact applied guide with decision boundaries, examples, anti-examples, quality checks, and stage-specific handoff requirements. The references improve judgment but never override CLI state or create authorization.

Notes and feedback are captured first with time, occurrence, perspective, sentiment, impact, confidence, actionability, stakeholder, and theme metadata. Private search, similarity, and pattern review can use those captures immediately; only reviewed and promoted records enter canonical trusted project memory.

Overnight code delivery stops at `review-ready`. The morning report surfaces per-goal evidence and exact human dispositions: approve, request changes, record merge, or close. In-scope requested changes reopen the same goal through explicit authorization; expanded scope requires revision and fresh approval. Only recorded human merge evidence marks a goal `completed`.
