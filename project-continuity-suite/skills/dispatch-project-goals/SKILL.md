---
name: dispatch-project-goals
description: Approve, queue, schedule, start, hold, cancel, resume, and inspect project goals while enforcing hashes, dependencies, project locks, compliance stages, and concurrency. Use when the user approves a plan, requests an immediate run, or changes queued work.
---

# Dispatch Project Goals

Keep approval and dispatch as separate recorded transitions. Never infer either from conversational enthusiasm or note capture.

Read [the continuity contract](../../references/continuity-contract.md) and `.continuity/config.json`.

## Approval

Require explicit approval naming the goal and plan version. Reject stale, modified, superseded, held, incomplete, or compliance-deficient plans.

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> --version <version> --approved-by "<human identity>" --authorization-text "<exact user approval naming goal and plan version>"
```

Approval queues the goal for 10:00 PM America/Chicago by default. It does not start execution unless the user explicitly requests dispatch.
Use `goal revise <goal-id> --goal-file <revision.json> --author <identity> --summary <reason>` for changes; this archives the prior version, invalidates approval, and returns the goal to feedback.

## Dispatch

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" goal due
.agents/project-continuity/bin/continuity --project-root "$PWD" goal start <goal-id>
.agents/project-continuity/bin/continuity --project-root "$PWD" goal hold <goal-id>
.agents/project-continuity/bin/continuity --project-root "$PWD" goal cancel <goal-id>
.agents/project-continuity/bin/continuity --project-root "$PWD" goal resume <goal-id>
```

Before dispatch, enforce approval hash, dependencies, integration branch, `AGENTS.md`, remote requirements, compliance evidence, runtime allowance, and the project lock. Allow different projects concurrently but one code-changing goal per project. Manual start never bypasses guardrails.
