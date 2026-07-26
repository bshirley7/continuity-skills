# Empty and Error States

## Generalized principles

- Classify the state before designing it: distinguish first use, healthy zero activity, zero results under a query or filter, unavailable data, access restriction, validation failure, transient failure, and partial completion so the explanation and recovery match the actual condition.
- State what happened, which object or step is affected, and the known cause in operational language; when the cause is unknown, say what is known without replacing uncertainty with a generic message.
- Preserve valid input, selected scope, query, filters, account identity, draft work, itinerary, order summary, and surrounding navigation so recovery does not require reconstructing the task.
- Map each recovery action to a plausible cause and label its consequence: retry, edit a field, change one search dimension, reset a filter, switch method or account, reauthenticate, request access, repair selected items, or contact support.
- For consequential retries, disclose whether the prior action completed, failed before commitment, may still be pending, or affected only a subset; prevent ambiguous repeated submissions and preserve a receipt or diagnostic reference when outcome is uncertain.
- Summarize batch and partial outcomes with submitted, succeeded, changed, skipped, failed, and pending counts, then make the affected rows or objects inspectable and allow correction or retry of only the unresolved subset.
- Anchor errors to the field, row, step, object, or permission that caused them, while providing a concise summary that links to every affected location when failures span a long page or batch.
- Teach first-use and healthy empty states by explaining what will appear, preserving the future structure, naming prerequisites, and offering a focused creation path plus a sample, template, import, or guided alternative when useful.
- Keep primary recovery, safe alternatives, cancellation, and escalation distinct; escalation should include time, affected scope, non-secret diagnostics, and a way to resume without discarding preserved work.
- Retain evidence of preceding destructive or state-changing actions only when it explains the current state, and connect that history explicitly so a success notification does not make an empty or failed state appear contradictory.

## Variation levers

- Use a compact centered empty state for one obvious first action and an in-context scaffold when users need to understand future structure, filters, or scope.
- Use suggested alternatives for exploratory search, selective filter reset for constrained search, and edit-search controls when multiple dimensions may explain zero results.
- Use inline field errors for local correction, a top summary for multiple errors, and a row or object table for batch failures.
- Use immediate retry for known transient failures, alternate method or account for capability failures, and escalation when the user cannot independently correct the cause.
- Use a modal for a focused blocking failure, an inline region for recoverable local errors, and a dedicated result page for consequential or multi-object outcomes.
- Use all-or-nothing execution when partial completion would create risk, and explicit partial import when valid items can safely commit independently.
- Use a preserved draft for repairable source data, a receipt for committed transactions, and a diagnostic identifier for uncertain external-system outcomes.
- Use templates and examples when they accelerate learning, but keep direct creation available for experienced users.

## Tensions and tradeoffs

- Specific causes improve recovery while revealing security-sensitive details or internal system behavior.
- Preserving input reduces rework while retaining sensitive data longer than necessary.
- Automatic retry reduces friction while risking duplicate consequential actions.
- Partial completion preserves valid work while creating reconciliation and rollback complexity.
- Detailed row-level errors support repair while overwhelming users when the same rule fails repeatedly.
- Suggested alternatives maintain momentum while distracting from correcting the original query.
- Examples and templates teach structure while biasing users toward a predefined solution.
- Persistent success history explains state changes while becoming misleading when it is no longer causally relevant.

## Failure modes

- First use, healthy zero activity, zero results, unavailable data, denied access, validation, transient failure, and partial completion are visually or verbally conflated.
- A message says only that something went wrong without naming affected scope, known cause, or uncertainty.
- Retry discards valid input, query, filters, selection, account, draft, or transaction context.
- The recovery action does not correspond to the likely cause or hides its consequence.
- A consequential retry does not state whether the prior action completed, remains pending, or affected a subset.
- A batch result omits submitted, succeeded, changed, skipped, failed, or pending scope.
- Errors are detached from the field, row, step, object, or permission that must change.
- An empty state offers only decoration or a generic call to action without teaching what belongs there.
- Escalation discards work, lacks affected scope, or exposes secrets instead of safe diagnostics.
- A stale notification or unrelated history makes the current empty or error state appear contradictory.

## Anti-patterns

- Using one generic empty-state component for first use, filtering, permissions, and outages.
- Showing a vague error followed by an unlabeled retry button.
- Clearing an entire form after one invalid field or failed payment attempt.
- Resetting every search constraint when only one filter caused zero results.
- Retrying a charge, submission, or import without clarifying prior outcome.
- Reporting a partially completed batch as either complete or failed with no counts.
- Rendering hundreds of repeated errors without grouping, locations, or an exportable repair artifact.
- Replacing an empty workspace with a full-page marketing pitch.
- Making support the primary path for a locally correctable problem.
- Leaving success toasts visible after the state they describe has become ambiguous.

## Acceptance and review questions

- Is the state correctly classified as first use, healthy zero, zero results, unavailable, access-blocked, validation, transient failure, or partial completion?
- Does the message identify what happened, affected scope, known cause, and uncertainty?
- Are valid input, query, filters, selection, account, draft, and transaction context preserved appropriately?
- Does each recovery action map to a plausible cause and disclose its consequence?
- For consequential actions, is prior completion, pending status, failure point, and retry safety clear?
- Do batch outcomes expose submitted, succeeded, changed, skipped, failed, and pending counts plus affected items?
- Can users move from the summary to the exact field, row, step, object, or permission that needs attention?
- Does an empty state explain future content, prerequisites, and a focused creation or guided path?
- Are alternatives, cancellation, and escalation distinct, and can users resume with preserved work?
- Is preceding history retained only when it causally explains the current state?
