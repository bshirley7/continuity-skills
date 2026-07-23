<p align="center">
  <img src="docs/assets/continuity-wordmark.svg" alt="Continuity" width="720">
</p>

# Continuity Suite

Continuity turns project conversations and notes into searchable memory, roadmap context, reviewable plans, supervised off-hours execution, and next-business-day decision reports.

## Start Here

- For a first local install, configuration, and skill-use walkthrough, read [Quickstart](docs/quickstart.md).
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
The installer also creates `.claude/commands/continuity-*.md` and `.cursor/commands/continuity-*.md` shims so compatible hosts can invoke the same workflows as slash commands such as `/continuity-workflow`, `/continuity-capture`, and `/continuity-triage`.

The guided installer can save portable user defaults in `~/.continuity/defaults.json`, then generate isolated project controls for Codex, Claude Code, Cursor, Windsurf, or another `AGENTS.md`-aware surface. One provider-owned portfolio supervisor calculates due actions, refreshes an expiring heartbeat, atomically reserves capacity, and issues one-time project claims. Repository-specific commands, instructions, notes, approvals, roadmap state, and execution enrollment never move into the user-default profile.

To update every enrolled project beneath one or more workspace roots, run `continuity portfolio update --root <workspace>` for a doctor-first dry-run, then repeat with `--apply`. Each checkout updates independently, including duplicate project IDs in separate worktrees and legacy controller layouts. Projects receive a post-update doctor check and automatically roll back if that check becomes unhealthy.

## Daily Skill Calls

```text
$continuity           configure, audit, and route the suite
$continuity-workflow  run a manual request sequentially until approval or completion
$continuity-capture   capture a callout, meeting batch, PRD, or feature request
$continuity-triage    classify notes into context, questions, decisions, roadmap, or plans
$continuity-memory    search or promote trusted project memory
$continuity-roadmap   inspect or update approved roadmap context
$continuity-plan      create approval-ready plans
$continuity-dispatch  approve, queue, or manually start approved goals
$continuity-execute   execute one approved dispatched goal
$continuity-test      run and record quality, validation, and security gates
$continuity-product-audit reconcile observed product behavior with approved project intent
$continuity-merge     assess PR readiness and execute or record an exact human-authorized merge
$continuity-report    summarize status, blockers, memory, roadmap, and evidence
$continuity-share     prepare sanitized note packets for explicit sharing
$continuity-improve   refine learned playbooks from evaluated usage without changing protected contracts
$continuity-design    create and approve an exact design document from offline guidance (optional collection)
```

Every skill uses `continuity workflow status` as its shared machine handoff. Manual work is owned by `$continuity-workflow`, which continues through every machine-selected non-human skill and remediation loop without returning a status-only handoff to the user. It pauses only when the machine handoff declares an explicit human-required approval, then resumes from canonical state after that approval is recorded. Exact note status includes a derived dated lifecycle, planning disposition, separate goal tracks, and non-authorizing relationship candidates. Plans classify every source note as current-goal, later, context-only, or duplicate; only current-goal notes adopt execution state. Unqualified status remains project routing context only.

Shared references explain that machine contract, while each task skill includes a compact applied guide with decision boundaries, examples, anti-examples, quality checks, and stage-specific handoff requirements. The references improve judgment but never override CLI state or create authorization.

Every installed skill separates its protected `SKILL.md` contract from an evolvable `references/learned-playbook.md`. `$continuity-improve` records sanitized private outcomes, discovers recurring successful and adverse patterns, stages bounded playbook candidates, and accepts a candidate only when fixed validation improves, untouched test evidence does not regress, protected invariants pass, and a human reviews the result. It never edits the live skill, auto-adopts guidance, or turns usage into execution authority; an approved package still requires a separately approved suite-source goal and normal release validation.

Notes and feedback are captured first with time, occurrence, perspective, sentiment, impact, confidence, actionability, stakeholder, and theme metadata. A pointed-to PRD or feature request remains one source capture with an exact private snapshot, document hash, revision lineage, and structurally anchored atomic items. Official project documents can appear in trusted retrieval as product intent; supplied references stay private. Neither form proves implementation behavior or authorizes work.

Projects that need design direction can enable the optional collection with `--collection design`. `$continuity-design` composes one to three directions from project context and reviewed offline references, requires explicit selection or combination, and promotes only an exactly approved private draft to `docs/design/design.md`. React and web work defaults to a complete private prototype that inventories the installed implementation system, maps component reuse and custom expression, plans assets, renders desktop, tablet, and mobile evidence, and closes artifact critique before approval. The prototype remains outside product routes and build inputs. The catalog layers broad foundation packs with independently versioned, evidence-backed category packs and loads only the overlays matching the design input. When `lenses` is omitted, an offline routing table applies a universal UX baseline and context-matched lenses, recording matched terms and reasons in the private draft; an explicit non-empty `lenses` array retains manual selection for bounded specialist or compatibility use. The committed `.continuity/design.json` binds its ID, revision, hash, and all selected catalog-pack versions. Design approval authorizes only that document; implementation still requires a separately approved goal bound to the exact design hash.

Overnight code delivery stops at `review-ready`. The morning report surfaces per-goal evidence and exact human dispositions: approve, request changes, merge, or close. An opt-in interactive command can bind human authorization to the exact PR, full head SHA, merge method, and authenticated GitHub identity, then perform and verify a direct `gh` merge without administrator bypass or auto-merge. In-scope requested changes reopen the same goal through explicit authorization; expanded scope requires revision and fresh approval. Only recorded human merge evidence marks a goal `completed`.
