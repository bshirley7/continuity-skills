---
name: continuity-plan
description: Convert selected documentation, research, backlog, or execution candidates into cohesive, versioned, approval-ready project goals. Use when the user or scheduled review wants a plan that distinguishes contextual knowledge from proposed instructions.
---

# Continuity Plan

Planning does not authorize work. Create a decision-complete proposal and leave it awaiting explicit approval.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the planning patterns](../../references/planning-patterns.md), `$continuity-local`, `.continuity/config.json`, `AGENTS.md`, and the documentation map.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [goal planning lenses](references/goal-planning-lenses.md) for every goal proposal. Use the [CLI-valid synthetic goal input](references/goal-input.example.json) when a machine-shaped example is needed. Select the applicable cross-functional questions from [decision lenses](../../references/decision-lenses.md); do not add irrelevant sections merely for completeness.

## Required assurance

- Identify applicable repository, language, framework, privacy, security, compatibility, migration, accessibility, performance, validation, rollout, and rollback standards before proposing execution.
- Define bounded scope, exclusions, dependencies, acceptance criteria, evidence, and stop conditions. Separate unresolved decisions and newly discovered work rather than guessing.
- Audit source-note eligibility, cited memory freshness, assurance-standard version, unattended suitability, required security review, and validation coverage. Planning never records approval.

## Workflow

1. Confirm every source item is eligible for planning.
2. Run `memory brief` and `roadmap brief` for the goal and record every memory and roadmap ID used. When an approved design applies, retrieve `.continuity/design.json`, verify `docs/design/design.md`, and include its ID in `design_ids`; the CLI derives the exact revision, hash, and catalog pack versions. Map the applicable design thesis, preservation rules, prohibited patterns, implementation guidance, and drift checks into delivery slices and observable acceptance criteria. Do not turn stylistic guidance into unrelated scope.
3. Apply the configured planning patterns. Use the evidence triage brief for verified action context. For complex or uncertain work, create a decision map with one destination, explicit decisions, dependency edges, unresolved territory, and out-of-scope boundaries. Do not plan execution across unresolved or human-required decisions.
4. Group only work supporting one cohesive outcome. Split unrelated intents.
5. For a multi-part outcome, create dependency-aware end-to-end delivery slices. Each slice must be independently verifiable, small enough for one focused run, and blocked only by genuine prerequisites. Use an expand-migrate-contract sequence for wide changes that cannot remain valid as vertical slices.
6. Distinguish context, trusted memory, roadmap context, new insights, proposed instructions, scope, exclusions, dependencies, decisions, documentation impact, structured roadmap impact, acceptance, validation, security, merge-safety, and evidence.
7. Apply repository architecture and developer best practices. Review the plan for correctness, maintainability, privacy, security, testing, rollout, and rollback implications.
8. Set unattended suitability and runtime, defaulting to six hours.
9. Give every `source_note_id` exactly one explicit `note_disposition`: `current-goal`, `later`, `context-only`, or `duplicate`. Omission fails closed for new goals and source-changing revisions. Later work requires `review_after` or a roadmap anchor. Map current-goal notes to delivery slices when applicable and state why every disposition was selected.
10. Create synchronized Markdown and machine-readable goal records with a feedback ledger. Include `triage_brief`, `decision_map`, `delivery_slices`, `note_dispositions`, `roadmap_ids`, optional `design_ids`, and `roadmap_impact`; the CLI validates them, renders derived source and design references into the plan, and includes them in the approval hash.
11. Record evidence for `capture-triage`, `memory-retrieval`, `roadmap-retrieval`, and `plan-review` compliance stages.
12. Leave the goal `awaiting-feedback`.

Only `current-goal` notes adopt the goal's delivery state. Inclusion in a plan means `planned`, never `in progress`; that begins only when the canonical run reaches `running`. Later, context-only, and duplicate notes remain outside approved execution scope. Human merge evidence alone moves current-goal notes to `completed`.

Create a validated goal JSON payload, then run:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal create --goal-file <path>
.agents/continuity/bin/continuity --project-root "$PWD" goal gate <goal-id> <stage> --status passed --evidence <evidence>
```

Any revision uses `goal revise`, creates an archived prior version, and invalidates prior approval. Surface blocking decisions instead of guessing.

Do not publish decision or delivery tickets externally as a side effect of planning. Local artifacts are the default. GitHub, Linear, or another tracker requires a separate explicit human publication approval; tracker-ready never means execution-ready.

`proposed-plan` and `approved` are legacy readable states only. New goals emit `awaiting-feedback`, and approval emits `queued`. Migrate a legacy goal through an explicit `goal revise` and fresh approval; `project doctor` reports any legacy records.

## Handoff

Run `continuity workflow status` on entry and `continuity workflow status --goal-id <goal-id>` after creation or revision. Hand off an `awaiting-feedback` goal to `$continuity-dispatch` for one of the machine-listed human actions; never infer approval.
