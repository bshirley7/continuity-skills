---
name: continuity-dispatch
description: Approve, queue, schedule, start, hold, cancel, resume, and inspect project goals while enforcing hashes, dependencies, project locks, compliance stages, and concurrency. Use when the user approves a plan, requests an immediate run, or changes queued work.
---

# Continuity Dispatch

Keep approval and dispatch as separate recorded transitions. Never infer either from conversational enthusiasm or note capture.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$continuity-local`, `.continuity/project.json`, and `.continuity/config.json`.

## Required assurance

- Accept only explicit human approval that names the exact goal and plan version. Never synthesize an approver, approval text, or dispatch instruction.
- Fail closed on stale hashes, unsupported assurance versions, disabled execution, illegal states, unresolved decision-map items, invalid delivery-slice graphs, unmet dependencies, active locks, expired runtime, missing authentication, or failed preflight evidence.
- Audit approval, scheduler dispatch, and execution as separate transitions, including actor, timestamp, plan hash, schedule, idempotency key, dependency state, project lock, task ID, heartbeat, and outcome.

## Approval

Require explicit approval naming the goal and plan version. Reject stale, modified, superseded, held, incomplete, or compliance-deficient plans.

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> --version <version> --approved-by "<human identity>" --authorization-text "<exact user approval naming goal and plan version>"
```

Approval queues the goal for 10:00 PM America/Chicago by default. It does not start execution unless the user explicitly requests dispatch.
The approval hash includes any evidence triage brief, decision map, and delivery-slice graph rendered into the plan. Editing any of them requires `goal revise` and a fresh approval.
Use `goal revise <goal-id> --goal-file <revision.json> --author <identity> --summary <reason>` for changes; this archives the prior version, invalidates approval, and returns the goal to feedback.

## Dispatch

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal due
.agents/continuity/bin/continuity --project-root "$PWD" goal start <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal hold <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal cancel <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal resume <goal-id>
```

Before dispatch, require the project-local manifest to have both `continuity_enabled` and `execution_enabled`, then enforce approval hash, dependencies, integration branch, `AGENTS.md`, remote requirements, compliance evidence, runtime allowance, and the project lock. Allow different projects concurrently but one code-changing goal per project. Manual start never bypasses guardrails.

For scheduled work, record `scheduler run-start`, send heartbeats, and finish the run explicitly. Once execution begins, the assigned execution task must use `$continuity-test` before PR handoff and `$continuity-merge` before marking merge safety passed. Successful overnight delivery ends at `review-ready`; failed quality or merge-safety reports keep the goal validating, blocked, or partially completed. Only later human merge evidence moves it to `completed`.
