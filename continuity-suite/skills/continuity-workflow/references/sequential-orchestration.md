# Sequential Orchestration

This reference defines how a manual Continuity invocation crosses task-skill boundaries without losing auditability or approval controls.

## Continuation contract

- `continuity workflow status` is the durable cursor. Recompute it after every state mutation and use the narrowest subject selector.
- `handoff.next_skill` selects the next task skill. The orchestrator does not maintain a second lifecycle or hard-code a stage when machine state selects another route.
- A completed task skill returns control to `$continuity-workflow`, not to the user. The orchestrator continues until an approval pause or terminal state.
- Failed gates return to the owning remediation skill. They block stage advancement but do not terminate the workflow or authorize bypass.
- Completed steps are replay-safe because the orchestrator re-reads canonical state instead of assuming that the previous process survived.

## Pause conditions

The workflow pauses when the handoff or selected action explicitly sets `human_required: true`. Show the exact allowed actions and retain all subject IDs and hashes needed to resume safely.

Do not pause merely for a routine skill boundary, status report, recoverable command failure, failing test, stale evidence, or a return from merge safety to implementation. Resolve those through the machine-selected skill and continue.

If a non-human fault has no immediately safe repair, keep the workflow pending at its current stage, record the diagnostic, and retry only within configured runtime and backoff limits. Never relabel a fault as an approval or weaken a fixed guardrail.

## Resumption

After a human records an allowed approval or disposition, start from fresh subject-specific workflow status. Verify approval hashes, execution attempt, source head, and other current evidence before continuing. Never replay the approval from conversation text or reuse a stale command template.

## Terminal states

Terminal states include completed, cancelled, archived, not-applicable, and successful no-work/reporting outcomes. Review-ready is not terminal because it requires a human disposition. Held, blocked, partially-completed, changes-requested, and queued states remain active or approval-pending according to their machine handoff.
