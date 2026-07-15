# Morning Report Examples

Read this reference for every morning report and whenever a project report contains review-ready, blocked, partial, stale, or no-work outcomes.

## Decision format

Each decision contains:

- exact goal, note, pattern, packet, or PR subject;
- current state and why it matters now;
- concise recommendation;
- evidence references and known gaps;
- exact `allowed_dispositions` from machine state;
- blocked dispositions and reasons, kept separate;
- next skill after the human choice.

## Review-ready example

“Goal OBJ-14 is review-ready at draft PR URL. Final source-bound tests and merge assessment passed for commit SHA. Review the preserved scanability behavior and revised label grouping. Allowed dispositions: the exact approved, changes-requested, merged, or closed commands returned by workflow status.”

Do not say “completed overnight” before human merge evidence.

## Blocked example

“Goal OBJ-22 stopped before implementation because the approved plan references a superseded roadmap record. No product files changed. Recommendation: return to planning with RM-09 and revise the goal. Manual start is blocked by the stale plan hash.”

Preserve what remains valid rather than describing the whole attempt as failed.

## No-work example

“No goals were due or dispatched. Project doctor passed, scheduler registration is healthy, queues contain two knowledge items and no planning candidates, and no human decisions are required.”

A no-work report still covers liveness, queue state, memory and roadmap health, and risks. It does not invent work to make the report useful.

## Note lifecycle example

“Note NOTE-14 is `planned-later` since 2026-07-14T20:15:00-05:00, anchored to review after 2026-07-21T09:00:00-05:00. It is not part of the running goal. Note NOTE-22 has one medium-confidence unconfirmed related-goal suggestion; inspect the local similarity evidence before recording a planning disposition.”

Do not describe `planned`, `queued`, or `dispatched` as “in progress.” Reserve that phrase for an exact `implementation` or later active execution stage.

Do not place low-confidence similarity results in the morning decision list. Do not exceed the suite relationship-review cap; direct the user to `note related-goals` for a broader investigation.

## Mixed portfolio example

Aggregate sanitized counts and decision summaries only. Report one healthy no-work project, one review-ready objective, and one unhealthy configuration as separate outcomes. Do not include raw notes, private IDs that expose content, approvals, locks, local paths, or ledgers.

## Handoff checklist

- Decisions, overnight outcomes, and blockers lead the report.
- Every completion, test, security, merge, queue, memory, and roadmap claim has evidence.
- Stale, pending, failed, partial, and not-applicable states remain distinct.
- Recommendations map to valid commands or named next skills.
- The report takes no human-required action.
