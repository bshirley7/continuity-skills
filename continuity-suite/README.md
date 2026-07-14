# Continuity Suite

Continuity turns project conversations and notes into searchable memory, roadmap context, reviewable plans, supervised off-hours execution, and next-business-day decision reports.

## Start Here

- For the exact installation and daily-use workflow, read [Install and Daily Use](docs/install-and-daily-use.md).
- For the full suite contract, installed layout, guardrails, and command reference, read [SUITE.md](SUITE.md).
- For the safety model every skill follows, read [Continuity Contract](references/continuity-contract.md).
- For quality and merge gates, read [Testing and Merge Standard](references/testing-and-merge-standard.md).
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

The guided installer can save portable user defaults in `~/.continuity/defaults.json`, then generate isolated project controls for Codex, Claude Code, Cursor, Windsurf, or another `AGENTS.md`-aware surface. One provider-owned portfolio supervisor calculates due actions and records private task/run health. Repository-specific commands, instructions, notes, approvals, roadmap state, and execution enrollment never move into the user-default profile.

## Daily Skill Calls

```text
$continuity           configure, audit, and route the suite
$continuity-capture   capture project notes or feedback
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

Notes and feedback are captured first. They become searchable project memory only after triage and approved promotion.

Overnight code delivery stops at `review-ready`. The morning report surfaces decisions, completed work, and blockers; only recorded human merge evidence marks a goal `completed`.
