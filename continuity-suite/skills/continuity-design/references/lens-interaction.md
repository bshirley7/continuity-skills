# Interaction

## Generalized principles

- Give every actionable element a perceivable affordance and distinct default, focus, hover, pressed, selected, disabled, loading, success, and error states, using more than color when state changes meaning or availability.
- Model interactions as explicit transitions with a source state, trigger, target state, timing, prerequisites, and completion condition so users and builders can predict what an action will make true.
- Keep interaction context continuous: preserve the affected object, underlying place, current selection, staged changes, and dismissal or return path while menus, popovers, modals, and command surfaces are open.
- For direct manipulation, expose handles or selectable regions, item identity, the active object, valid targets, exact insertion or resize preview, constraints, and a clear commit, cancel, or undo boundary.
- Communicate latency with the most meaningful available units: aggregate and per-item state, completed and remaining work, percentage or stage, expected time when reliable, transfer or processing detail when useful, and a clear final outcome.
- Make cancellation honest and state-aware by explaining whether it stops queued work, interrupts active work, preserves completed results, discards staged changes, or leaves an external operation running.
- Separate optimistic acknowledgement from durable completion: show pending or syncing state after immediate feedback, reconcile partial or failed outcomes, and do not let a success notification contradict unresolved work.
- Provide equivalent pointer and keyboard paths for frequent operations with visible focus, current option, shortcut hints, predictable navigation, activation, dismissal, and return to the prior place.
- Enable commit only after a valid meaningful change, preview the exact resulting mapping or order, and distinguish save, confirm, publish, merge, or create according to the transition being performed.
- Use motion and transient feedback to explain continuity, direction, hierarchy, and completion, while ensuring the durable state remains understandable when animation is reduced, interrupted, or missed.

## Variation levers

- Use inline state changes for local reversible actions, a popover for bounded configuration, and a modal for staged or consequential transitions.
- Use immediate feedback for fast actions, determinate progress for measurable work, staged status for multi-step operations, and background notification when users may safely leave.
- Use drag for spatial reordering with handles and insertion previews, plus keyboard move controls or explicit position editing for equivalent access.
- Use cancel for staged changes, undo for committed reversible changes, and confirmation for irreversible or dependency-changing transitions.
- Use optimistic updates when rollback is safe and authoritative completion is expected quickly; otherwise retain a pending state.
- Use aggregate progress for orientation and per-item progress when users can inspect, retry, cancel, or reconcile individual outcomes.
- Use shortcuts beside visible commands for discoverability and a palette for broad command sets.
- Use animation for spatial continuity and state change, but pair it with persistent labels, position, and status.

## Tensions and tradeoffs

- More interaction states improve clarity while increasing implementation and testing cost.
- Immediate optimistic feedback feels fast while risking temporary disagreement with authoritative state.
- Detailed progress supports control while adding noise and encouraging unnecessary monitoring.
- Cancellation increases autonomy while some operations cannot stop atomically.
- Direct manipulation feels natural while it can hide precision, constraints, and keyboard access.
- Modals focus consequential work while obscuring broader context.
- Shortcut-heavy interfaces accelerate expert use while reducing novice discoverability.
- Motion explains continuity while creating distraction, latency, or accessibility barriers.

## Failure modes

- Controls lack distinguishable focus, selected, disabled, loading, success, or error states.
- An action's trigger, target state, prerequisite, timing, or completion condition is unclear.
- Opening an overlay loses the affected object, selection, staged changes, or return path.
- Drag and drop lacks handles, identity, valid targets, insertion preview, constraints, or recovery.
- Asynchronous work exposes only a spinner or a success toast without meaningful progress and outcome.
- Cancel does not explain what stops, remains, or has already completed.
- Optimistic acknowledgement is mistaken for durable completion.
- Keyboard focus, shortcuts, activation, dismissal, or pointer-equivalent behavior are missing.
- Commit is available without a valid change or uses a generic label that hides the transition.
- Meaning depends on an animation users can miss or reduce.

## Anti-patterns

- Using color alone to distinguish interactive state.
- Showing a disabled control with no explanation of its prerequisite.
- Opening a menu without visible focus or a reliable escape path.
- Dragging an item without an insertion marker.
- Reporting zero completed while hiding active per-item progress.
- Offering cancel when the operation cannot actually stop.
- Showing success while tests or uploads remain pending.
- Providing keyboard shortcuts that are not discoverable near their commands.
- Using save for creation, merging, publication, and destructive confirmation alike.
- Using animation as the only evidence that an action occurred.

## Acceptance and review questions

- Are default, focus, hover, pressed, selected, disabled, loading, success, and error states perceivable?
- Are source state, trigger, target state, timing, prerequisites, and completion explicit?
- Do overlays preserve object, place, selection, staged changes, dismissal, and return?
- Does direct manipulation expose handles, identity, valid targets, preview, constraints, and recovery?
- Does asynchronous work show meaningful aggregate and per-item progress, duration, and final outcome?
- Does cancellation state exactly what stops, remains, completes, or is discarded?
- Are acknowledgement, pending, partial, failed, and durable completion distinct?
- Are pointer and keyboard paths equivalent with visible focus and shortcut guidance?
- Is commit enabled only for a valid change and labeled with the actual transition?
- Does durable meaning survive reduced, interrupted, or missed motion?
