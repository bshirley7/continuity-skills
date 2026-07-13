---
name: plan-project-goals
description: Convert selected documentation, research, backlog, or execution candidates into cohesive, versioned, approval-ready project goals. Use when the user or scheduled review wants a plan that distinguishes contextual knowledge from proposed instructions.
---

# Plan Project Goals

Planning does not authorize work. Create a decision-complete proposal and leave it awaiting explicit approval.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$project-continuity-local`, `.continuity/config.json`, `AGENTS.md`, and the documentation map.

## Required assurance

- Identify applicable repository, language, framework, privacy, security, compatibility, migration, accessibility, performance, validation, rollout, and rollback standards before proposing execution.
- Define bounded scope, exclusions, dependencies, acceptance criteria, evidence, and stop conditions. Separate unresolved decisions and newly discovered work rather than guessing.
- Audit source-note eligibility, cited memory freshness, assurance-standard version, unattended suitability, required security review, and validation coverage. Planning never records approval.

## Workflow

1. Confirm every source item is eligible for planning.
2. Run `memory brief` for the goal and record every memory ID used.
3. Group only work supporting one cohesive outcome. Split unrelated intents.
4. Distinguish context, trusted memory, new insights, proposed instructions, scope, exclusions, dependencies, decisions, documentation impact, acceptance, validation, security, merge-safety, and evidence.
5. Apply repository architecture and developer best practices. Review the plan for correctness, maintainability, privacy, security, testing, rollout, and rollback implications.
6. Set unattended suitability and runtime, defaulting to six hours.
7. Create synchronized Markdown and machine-readable goal records with a feedback ledger.
8. Record evidence for `capture-triage`, `memory-retrieval`, and `plan-review` compliance stages.
9. Leave the goal `awaiting-feedback`.

Create a validated goal JSON payload, then run:

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" goal create --goal-file <path>
.agents/project-continuity/bin/continuity --project-root "$PWD" goal gate <goal-id> <stage> --status passed --evidence <evidence>
```

Any revision uses `goal revise`, creates an archived prior version, and invalidates prior approval. Surface blocking decisions instead of guessing.
