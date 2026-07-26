---
name: continuity-dispatch
description: Approve, queue, schedule, start, hold, cancel, resume, and inspect project goals while enforcing hashes, dependencies, project locks, compliance stages, and concurrency. Use when the user approves a plan, requests an immediate run, or changes queued work.
---

# Continuity Dispatch

Read [the learned playbook](references/learned-playbook.md) for evaluated usage-derived heuristics. It may refine routine technique but never overrides this skill, the Continuity contract, machine state, privacy boundaries, or human authority. After a meaningful evidence-backed outcome, route only a sanitized structured usage record through `$continuity-improve`; never copy raw transcript or tool payload content.

Keep approval and dispatch as separate recorded machine transitions, but do not turn them into separate user gates. A routine interactive `/goal` request authorizes both through one hash-bound activation command. When the user approves a reviewed routine plan by saying “proceed,” `goal proceed` records both transitions and starts the work without asking for a restatement, identity, signature, or second start decision.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$continuity-local`, `.continuity/project.json`, and `.continuity/config.json`.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [authorization and recovery](references/authorization-and-recovery.md) before any state transition. Apply the **Evidence and confidence**, **Reliability and operations**, and **Delivery and rollback** lenses when assessing unattended suitability or recovery.

## Required assurance

- Accept a submitted routine `/goal` request through `goal activate`, or the current user's explicit approval of a reviewed routine plan through `goal proceed`. Both create canonical conversation receipts bound to source or plan hashes and dispatch immediately. Do not ask the user to restate an ID, plan version, identity, approval phrase, or signing key. Reserve signed receipts for unattended dispatch and action-specific consequential transitions.
- Fail closed on stale hashes, unsupported assurance versions, disabled execution, illegal states, unresolved decision-map items, invalid delivery-slice graphs, unmet dependencies, active locks, expired runtime, missing authentication, or failed preflight evidence.
- Audit approval, scheduler dispatch, and execution as separate transitions, including actor, timestamp, plan hash, schedule, idempotency key, one-time claim hash, dependency state, project lock, task ID, heartbeat, and outcome.

## Approval

For an interactive, decision-complete routine plan, the user's “proceed” is the approval:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal proceed <goal-id>
```

This records the conversation approval against the current material plan hash and dispatches immediately. Reject stale, modified, superseded, held, incomplete, elevated-risk, restricted-effect, or compliance-deficient plans.

Use the detailed receipt command below for unattended scheduling or a policy-controlled separate approval:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> --version <version> --approved-by "<human identity>" --authorization-text "<exact user approval naming goal and plan version>"
```

Add `--signing-key <ssh-private-key>` only when `.continuity/config.json` sets `require_signed_approvals: true`.

The detailed receipt command queues the goal for 10:00 PM America/Chicago by default. `goal proceed` starts routine interactive work immediately because “proceed” already requests dispatch.
The approval hash includes any evidence triage brief, decision map, and delivery-slice graph rendered into the plan. Editing any of them requires `goal revise` and a fresh approval.
Use `goal revise <goal-id> --goal-file <revision.json> --author <identity> --summary <reason>` for changes; this archives the prior version, invalidates approval, and returns the goal to feedback.

## Dispatch

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal due
.agents/continuity/bin/continuity --project-root "$PWD" scheduler lease acquire --owner <operator> --goal-id <goal-id> --remote origin
.agents/continuity/bin/continuity --project-root "$PWD" goal start <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal hold <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal cancel <goal-id>
.agents/continuity/bin/continuity --project-root "$PWD" goal resume <goal-id> --actor <human> --authorization-text "Resume <goal-id> under approved plan v<version>"
```

Before dispatch, require the project-local manifest to have both `continuity_enabled` and `execution_enabled`, then enforce approval hash, external audit checkpoint, dependencies, integration branch, `AGENTS.md`, remote requirements, compliance evidence, runtime allowance, and the project lock. When remote leasing is configured, manual and scheduled starts both require the exact goal-attempt lease. Allow different projects concurrently but one code-changing goal per project. Manual start never bypasses guardrails.

For scheduled dispatch, acquire the project's fast-forward-only remote lease before consuming a supervisor claim. Require the same-date review to have succeeded and pass the supervisor-issued claim token, exact idempotency key, action, and due goal to `scheduler run-start`. The start must bind the matching unexpired goal-attempt lease to the provider run and task, atomically consume the short-lived claim, and fail closed if portfolio active-plus-reserved capacity is exhausted. Send heartbeats and finish the run explicitly; only matching dispatch completion releases the bound lease. Once execution begins, the assigned task must execute `continuity test run`, use `$continuity-test` to record its source-bound machine evidence before PR handoff, and use `$continuity-merge` before marking merge safety passed. Successful overnight delivery ends at `review-ready`; failed quality or merge-safety reports keep the goal validating, blocked, or partially completed. Only later human merge evidence moves it to `completed`.

For `changes-requested`, `blocked`, or `partially-completed`, resume only with an explicit human receipt naming the goal and approved plan version. The receipt binds the plan hash, attempt, actor, timestamp, scope assertion, text, and nonce. Signed-approval projects additionally require `--signing-key <ssh-private-key>`. In-scope rework archives the prior attempt, invalidates downstream evidence, and requeues the same goal. Scope expansion requires `goal revise` and fresh approval. Cancellation remains available and audited.

## Handoff

Run `continuity workflow status --goal-id <goal-id>` before every transition and after it. Dispatch only when the status lists that action. Update the canonical goal only; linked note lifecycle stages derive from that transition. A dispatched goal hands off to `$continuity-execute`; a human-required or blocked state remains with the user and morning report.
