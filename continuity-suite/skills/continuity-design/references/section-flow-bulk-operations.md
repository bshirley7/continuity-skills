# Bulk operations and change review

## Generalized principles

- Keep selection scope continuously visible through exact count, selected-versus-all distinction, active filters, excluded or ineligible items, destination or cohort, and a clear way to inspect, adjust, or clear the selection before action.
- Before commitment, describe the operation, target type and count, fields or capabilities changing, prior and replacement semantics, keep-as-is or clear behavior, destination, inheritance, dependent objects, permanence, and recovery route.
- Represent long-running batch work as durable operational state with queued, running, cancelable, partially complete, complete, or failed status; preserve safe navigation, progress, retry, and evidence for items that did not change.
- Close every bulk action with result accounting that separates requested, changed, unchanged, skipped, ineligible, failed, moved, archived, or deleted items and preserves actor, time, destination, undo or recovery, and an inspectable history.

## Variation levers

- Use immediate inline edits for small reversible sets and staged review or background jobs for large, relational, permission-changing, or destructive sets.
- Require stronger preview and confirmation when selection spans filtered results, hidden pages, inherited access, child objects, external communications, or irreversible deletion.
- Provide per-field keep, replace, clear, and merge semantics according to the data model instead of treating every bulk edit as overwrite.

## Tensions and tradeoffs

- Select-all accelerates high-volume work while making hidden scope and filter drift easier to miss.
- Compact bulk controls preserve workspace context while limiting consequence explanation.
- Background execution supports scale while weakening immediate feedback and cancellation.
- Undo reduces fear while being difficult or impossible for external effects, permission propagation, and permanent deletion.

## Failure modes

- Selection count is visible but the interface does not distinguish current page, filtered set, or all matching items.
- A replacement value silently overwrites mixed prior values or clears fields that were meant to remain unchanged.
- Confirmation names the action but not targets, destination, dependencies, inheritance, or recovery.
- A progress overlay blocks work without durable status, safe exit, cancellation, or later history.
- Success feedback gives one count while hiding skipped, failed, ineligible, or partially changed items.

## Anti-patterns

- Select all, scope unknown.
- Bulk overwrite by surprise.
- Confirmation without targets.
- Spinner batch.
- One-count success.
- Undo that cannot undo.
- Archive as disappearance.

## Acceptance and review questions

- Does selection distinguish exact count, page, filtered set, all matches, exclusions, and ineligible items?
- Can people inspect and adjust the target set before commitment?
- Are operation, prior and replacement semantics, destination, inheritance, dependencies, permanence, and recovery explicit?
- Does long-running work preserve durable status, safe exit, cancellation, retry, and failure evidence?
- Does completion account separately for requested, changed, unchanged, skipped, ineligible, failed, archived, moved, and deleted items?
- Are actor, time, destination, undo or recovery, and history inspectable after the action?
