---
name: report-project-progress
description: Generate evidence-backed completion reports, active-run updates, morning portfolio reports, memory-health summaries, compliance status, and feedback requests. Use when work finishes, at the morning checkpoint, or whenever the user asks for project status.
---

# Report Project Progress

Report recorded state without converting notes, feedback, or pending plans into implied commitments.

Read [the continuity contract](../../references/continuity-contract.md), project manifests, feedback, evidence, compliance ledgers, and `.continuity/config.json`.

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" report project
.agents/project-continuity/bin/continuity --project-root "$PWD" memory audit
```

The morning report is mandatory even when no goal ran. Include notes retained as context, documentation candidates, deferred items, open questions, memory health, plans awaiting feedback, queued and held work, active runs, validation, completed or partial outcomes, blockers, PRs, compliance stages, and feedback needed.

Never claim completion, mergeability, security, or review readiness without evidence. Publish a completion report immediately when work ends and preserve later feedback for the next cycle.
