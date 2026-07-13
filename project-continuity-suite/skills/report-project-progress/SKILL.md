---
name: report-project-progress
description: Generate evidence-backed completion reports, active-run updates, morning portfolio reports, memory-health summaries, compliance status, and feedback requests. Use when work finishes, at the morning checkpoint, or whenever the user asks for project status.
---

# Report Project Progress

Report recorded state without converting notes, feedback, or pending plans into implied commitments.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), project manifests, feedback, evidence, compliance ledgers, and `.continuity/config.json`.

## Required assurance

- Derive every status, completion, validation, security, mergeability, and memory claim from recorded evidence; distinguish passed, pending, failed, blocked, partial, and not-applicable states precisely.
- Redact secrets, personal data, raw captures, private ledger content, credentials, and sensitive operational details from project and portfolio reports.
- Audit report completeness against notes, memory IDs, plan hash, feedback, acceptance criteria, exclusions, changed files, validation, security review, merge safety, documentation, and memory impact. Surface stale or contradictory evidence.

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" report project
.agents/project-continuity/bin/continuity --project-root "$PWD" memory audit
```

The morning report is mandatory even when no goal ran. Include notes retained as context, documentation candidates, deferred items, open questions, memory health, plans awaiting feedback, queued and held work, active runs, validation, completed or partial outcomes, blockers, PRs, compliance stages, and feedback needed.

For a portfolio report, discover project-local manifests beneath developer-configured workspace roots. Run each report from that repository using its installed skill and CLI. Aggregate only sanitized summaries; do not centralize raw captures, private ledgers, approvals, or locks.

Never claim completion, mergeability, security, or review readiness without evidence. Publish a completion report immediately when work ends and preserve later feedback for the next cycle.
