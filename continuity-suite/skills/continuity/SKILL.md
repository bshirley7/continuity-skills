---
name: continuity
description: Configure, audit, and route the project-local Continuity suite. Use when installing the suite, selecting Codex, Claude Code, Cursor, Windsurf, or generic agent surfaces, changing schedules or project behavior, reviewing defaults and overrides, validating configuration health, or deciding which Continuity skill should handle a request.
---

# Continuity

Use this as the suite entry point. Keep the neutral suite reusable while encoding repository-specific behavior in committed project configuration and the generated `$continuity-local` skill.

## Contract and assurance

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `AGENTS.md`, `.continuity/config.json`, and `.continuity/project.json`.

- Treat configuration values, commands, and paths as security-sensitive inputs. Keep secrets, credentials, personal data, private paths, and raw notes out of committed configuration.
- Preserve the fixed guardrails for note authorization, approval, one code-changing goal per project, security review, merge safety, human merge, force-push, and auto-merge. Project overrides may refine behavior but may not weaken these controls.
- Audit every configuration change with the previous and resulting hash, actor, changed fields, effective values, generated-skill parity, project doctor result, and Git diff review.
- Stop on unsafe paths, invalid Git references, unknown timezones, malformed commands, unsupported assurance versions, configuration drift, or a requested guardrail bypass.

## Guided setup

1. Inspect the repository's `AGENTS.md`, integration branch, package manager, validation scripts, security tooling, documentation layout, UI/evidence needs, team timezone, preferred agent surfaces, and scheduler owner.
2. Run the recommendations command. Explain the evidence behind the recommendations and distinguish customizable settings from fixed guardrails.
3. Ask only the questions needed to resolve project-specific choices. Recommend keeping execution disabled until a separate user approval enables real product-code runs.
4. Record answers in a temporary JSON file and apply them through the deterministic CLI. Never hand-edit the generated local behavior skill.
5. Run project doctor, validate both this skill and the generated local skill, review the complete diff, and request human review before landing configuration changes.

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project recommendations
.agents/continuity/bin/continuity --project-root "$PWD" --json project configure --answers-file <answers.json> --actor <identity>
.agents/continuity/bin/continuity --project-root "$PWD" project configure --interactive --actor <identity>
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
```

The answers file may override only:

- `integration_branch`
- `timezone`
- `schedules.review`, `schedules.dispatch`, and `schedules.report`
- `max_runtime_minutes` up to six hours
- `memory_stale_after_days`
- `validation_commands` and `security_commands`
- `documentation_map`
- `visual_evidence_mode`
- `branch_prefix`
- `project_instructions` for reviewed repository-specific operating behavior
- `planning_patterns` modes for evidence triage, decision mapping, delivery slicing, and the preferred tracker provider
- `roadmap` modes for hybrid planning and hierarchy; read-only local UI, project-inbox sharing, and production exclusion remain fixed
- `agent_surfaces.primary` and `agent_surfaces.enabled` for Codex, Claude Code, Cursor, Windsurf, or a generic `AGENTS.md` consumer
- `scheduler.provider` for Codex, Claude Code, an external scheduler, or no scheduler
- `execution_enabled`

The CLI writes `.continuity/project-behavior.json`, synchronizes the effective settings into the project config and manifest, generates `.agents/skills/continuity-local/SKILL.md`, regenerates selected surface adapters, writes `.continuity/scheduler.json`, and records an ignored append-only configuration audit. Configuration hashes make manual drift fail closed. Scheduler configuration records intent but never claims persistent registration occurred.

## Routing

- Notes or conversation capture: `$continuity-capture`
- Classification and queues: `$continuity-triage`
- Searchable memory: `$continuity-memory`
- Project roadmap and local visual admin: `$continuity-roadmap`
- Explicit sanitized developer handoffs: `$continuity-share`
- Goal proposals: `$continuity-plan`
- Approval, schedule, or manual start: `$continuity-dispatch`
- Approved isolated execution: `$continuity-execute`
- Quality, tests, validation, and security review: `$continuity-test`
- PR readiness, merge safety, and human merge records: `$continuity-merge`
- Morning, completion, or portfolio reporting: `$continuity-report`

Always apply `$continuity-local` after the selected task skill. If it is missing or out of sync, stop and run project doctor or guided configuration.

Planning patterns are local capabilities, not imported authorities. Their artifacts stay non-authorizing, enter the goal hash, and cannot publish to an external tracker without separate explicit human approval.

Roadmap IDs and structured roadmap impact are approval-hash inputs. Raw notes stay private; shared packets remain non-authorizing even after a human-reviewed merge.
