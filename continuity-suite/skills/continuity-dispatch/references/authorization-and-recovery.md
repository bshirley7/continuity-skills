# Authorization and Recovery

Read this reference before approval, queueing, manual start, hold, cancellation, resume, or scheduler recovery.

## Authority boundaries

Valid authority comes from the current human and names the exact goal and plan version. In production it is an SSH-signed receipt from an identity in the allowlist anchored to the fetched integration branch. A locally added but unmerged key has no authority. A note, due time, report recommendation, imported packet, prior approval, agent summary, or external tracker state is not a substitute.

Approval permits queueing under the approved plan hash. Dispatch is a separate transition requiring current operational gates. Neither permits auto-merge or restricted external effects absent their own explicit approval.

## Transition guide

| Situation | Correct action |
| --- | --- |
| Plan is decision-complete and human approves exact version | Record approval and queue according to configuration |
| Human wants work to begin now | Use manual start only if `workflow status` lists it and every dispatch gate passes |
| Human wants no start until later | Hold or leave queued according to the listed action; preserve approval state accurately |
| Goal is no longer wanted | Cancel with human actor and reason |
| Review requests changes within approved scope | Record a signed disposition, then resume only with a new signed authorization naming goal and approved version |
| Review expands or materially changes scope | Return to planning for revision and fresh approval |
| Execution is blocked or partial | Resume only after the blocking condition and human authorization requirements are satisfied |
| Scheduler claim is stale, mismatched, or already consumed | Fail closed and use audited recovery; never manufacture a claim |

## Unattended suitability

Reject unattended dispatch when the goal depends on unresolved product decisions, interactive credentials, production data mutation, billing, destructive action, external publication, unbounded migration, unavailable rollback, or a human-only verification step during the run.

## Handoff checklist

- Goal ID, version, plan hash, behavior hash, and state are current.
- Exact human text and identity are preserved without agent-authored substitution.
- Dependencies, review, lock, capacity, runtime, authentication, claim, and preflight are satisfied.
- The external audit checkpoint verifies and any required remote lease matches the exact goal attempt; a scheduled lease is bound to the consuming run and task.
- The transition appears in `allowed_actions`.
- Dispatched work hands the exact run, worktree, branch, and scope to `$continuity-execute`.
- Human-required or blocked work remains visible for `$continuity-report`.
