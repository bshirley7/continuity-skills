<p align="center">
  <img src="docs/assets/continuity-wordmark.svg" alt="Continuity" width="720">
</p>

# Continuity Suite

Continuity turns one explicit `/goal` request into triaged project context, immediate roadmap visibility, a bounded plan, and working code. The same suite retains stricter supervised controls for unattended execution and consequential actions.

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
- For Codex and Claude Code discovery, workspace trust, multi-root windows, reloads, simultaneous agents, and Remote Development, read [VS Code, Codex, and Claude Code](docs/vscode-codex-claude.md).
- For contribution rules and review expectations, read [Contributing](CONTRIBUTING.md).
- For native installation, launchers, OneDrive, and PowerShell behavior, read [Native Windows Setup and Operation](docs/windows.md).
- For assets, trust boundaries, adversaries, controls, and residual risk, read [Security Threat Model](docs/security-threat-model.md).
- For the current Windows capability reconciliation and remaining external acceptance gates, read [Native Windows Final Capability Audit](docs/windows-port/final-audit.md).

## Short Answer

On Windows, install the timezone data dependency before running the suite:

```text
python -m pip install -r continuity-suite/requirements.txt
```

Continuity uses native Windows file locking when run under Windows and POSIX
file locking on macOS and Linux.

On Windows, use the installed `continuity.cmd` launcher from PowerShell,
Command Prompt, or a VS Code terminal. A `continuity.ps1` launcher is also
installed for environments that permit project scripts. Neither requires
changing a machine-wide PowerShell execution policy; see the Windows guide.

Initial installation is normally run from the Continuity suite checkout and pointed at a project folder:

```text
python3 continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id stable-project-id \
  --integration-branch main \
  --validation "project validation command"
```

After installation, routine action starts with `/goal <request>`. Granular `$continuity-*` skills and the project-local CLI at `.agents/continuity/bin/continuity` remain available for scheduled, resumed, diagnostic, and specialist work.
The installer creates `.claude/commands/goal.md`, `.cursor/commands/goal.md`, and the granular Continuity shims.

The guided installer can save portable user defaults in `~/.continuity/defaults.json`, then generate isolated project controls for Codex, Claude Code, Cursor, Windsurf, or another `AGENTS.md`-aware surface. One provider-owned portfolio supervisor calculates due actions, refreshes an expiring heartbeat, atomically reserves capacity, and issues one-time project claims. Repository-specific commands, instructions, notes, approvals, roadmap state, and execution enrollment never move into the user-default profile.

To update every enrolled project beneath one or more workspace roots, run `continuity portfolio update --root <workspace>` for a doctor-first dry-run, then repeat with `--apply`. Each checkout updates independently, including duplicate project IDs in separate worktrees and legacy controller layouts. Projects receive a post-update doctor check and automatically roll back if that check becomes unhealthy.

## Daily Skill Calls

```text
/goal                 go from one explicit request to working code
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

Every skill uses `continuity workflow status` as its shared machine handoff. Routine interactive work is owned by `/goal`, which captures and triages the request, projects actionable notes into the private roadmap inbox, binds the exact request to the smallest aligned plan, and starts implementation without separate approval or start pauses. `$continuity-workflow` continues scheduled, resumed, or stricter flows. Both pause only for genuine authority changes or consequential actions.

Shared references explain that machine contract, while each task skill includes a compact applied guide with decision boundaries, examples, anti-examples, quality checks, and stage-specific handoff requirements. The references improve judgment but never override CLI state or create authorization.

Every installed skill separates its protected `SKILL.md` contract from an evolvable `references/learned-playbook.md`. `$continuity-improve` records sanitized private outcomes, discovers recurring successful and adverse patterns, stages bounded playbook candidates, and accepts a candidate only when fixed validation improves, untouched test evidence does not regress, protected invariants pass, and a human reviews the result. It never edits the live skill, auto-adopts guidance, or turns usage into execution authority; an approved package still requires a separately approved suite-source goal and normal release validation.

Notes and feedback are captured with time, occurrence, perspective, sentiment, impact, confidence, actionability, stakeholder, and theme metadata, then triaged in the same `/goal` run. Actionable triaged items appear immediately in the private roadmap inbox. A pointed-to PRD or feature request remains one source capture with an exact private snapshot, document hash, revision lineage, and structurally anchored atomic items. Capture and roadmap visibility alone never authorize work; `/goal` authority comes from the exact user request bound to the resulting plan hash.

Projects that need design direction can enable the optional collection with `--collection design`. `$continuity-design` composes one to three directions from project context and reviewed offline references, requires explicit selection or combination, and promotes only an exactly approved private draft to `docs/design/design.md`. React and web work defaults to a complete private prototype that inventories the installed implementation system, maps component reuse and custom expression, plans assets, renders desktop, tablet, and mobile evidence, and closes artifact critique before approval. The prototype remains outside product routes and build inputs. The catalog layers broad foundation packs with independently versioned, evidence-backed category packs and loads only the overlays matching the design input. When `lenses` is omitted, an offline routing table applies a universal UX baseline and context-matched lenses, recording matched terms and reasons in the private draft; an explicit non-empty `lenses` array retains manual selection for bounded specialist or compatibility use. The committed `.continuity/design.json` binds its ID, revision, hash, and all selected catalog-pack versions. Design approval authorizes only that document; implementation still requires a separately approved goal bound to the exact design hash.

Overnight code delivery stops at `review-ready`. The morning report surfaces per-goal evidence and exact human dispositions: approve, request changes, merge, or close. An opt-in interactive command can bind human authorization to the exact PR, full head SHA, merge method, and authenticated GitHub identity, then perform and verify a direct `gh` merge without administrator bypass or auto-merge. In-scope requested changes reopen the same goal through explicit authorization; expanded scope requires revision and fresh approval. Only recorded human merge evidence marks a goal `completed`.
