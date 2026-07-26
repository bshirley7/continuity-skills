# Usability

## Generalized principles

- Keep task context persistent across search, filters, selection, detail, and action: show the active scope, selected count, current object, saved-versus-temporary state, and the result of each operation without forcing users to reconstruct their place.
- Design frequent work for recognition and batching through decision-relevant columns, composable filters, saved views, direct row actions, multi-selection, and bulk operations whose affected scope remains visible.
- Match control availability to current state and selection, disable or defer impossible actions with an explanation, and keep the primary next action visually distinct from secondary, cancel, and destructive choices.
- Prevent form errors with purpose text, appropriate input controls, examples, sensible inherited defaults, conditional fields, and validation close to the source while preserving every valid value and a usable back path.
- For complex validation, connect a concise global blocker to exact local evidence, then provide copyable values, numbered repair steps, retry or verification controls, and an unambiguous statement of whether progress can continue.
- In editors, synchronize direct canvas selection, structure, contextual properties, preview, zoom, and stable undo, redo, save, and publish controls so users can act without losing mode or target.
- Preserve work by making autosave or pending state visible, supporting save-and-exit or drafts, providing undo or restoration for reversible changes, and warning before navigation or actions that would discard unsaved work.
- Make long-running work legible through named completed, active, remaining, failed, and delivery stages, expected duration when known, safe cancellation, and a clear distinction between generated, saved, activated, published, and delivered states.
- When an action affects dependent workflow steps, offer explicit downstream choices and explain what will continue, stop, be canceled, be removed, remain preserved, or become inaccessible.
- Layer guidance into the task through contextual explanations, visual previews, examples, and searchable insertion choices, while preserving a fast path for users who already know the operation.

## Variation levers

- Use direct row actions for frequent low-risk changes, bulk bars for selected sets, and a focused review for high-impact operations.
- Use saved views for recurring scopes and temporary filters for one-time investigation, labeling the difference explicitly.
- Use inline validation for local fields, a summary for multiple errors, and a dedicated repair view for cross-system verification.
- Use inherited defaults when prior data is authoritative and an explicit alternative when users may need to diverge.
- Use autosave for continuous low-risk edits and explicit save or publish for meaningful state transitions.
- Use direct manipulation for spatial edits, structured panels for precise properties, and searchable insert menus for broad component libraries.
- Use determinate stages for decomposable tasks, time estimates for bounded generation, and indeterminate feedback only when no reliable unit exists.
- Use undo for easily reversible actions and confirmation for destructive, externally visible, or dependency-changing actions.

## Tensions and tradeoffs

- More visible actions improve speed while increasing density and accidental activation risk.
- Bulk operations reduce effort while amplifying the consequence of a mistaken selection.
- Sensible defaults accelerate completion while hiding inherited assumptions.
- Immediate validation supports correction while interrupting entry before users finish.
- Autosave protects work while making commit and publication boundaries less obvious.
- Contextual guidance reduces confusion while obscuring the working canvas.
- Direct manipulation feels immediate while structured property controls support precision.
- Confirmation prevents costly mistakes while creating habituation when overused.

## Failure modes

- Search, filters, selection, detail, or action causes users to lose their task scope or place.
- A dense list omits the fields or direct actions needed for routine decisions.
- Controls remain active when their prerequisites are unmet or selection is ambiguous.
- Forms use avoidable free text, hide purpose, clear valid data, or place errors far from their source.
- A global validation failure does not link to local evidence and concrete repair.
- An editor loses selection, mode, viewport, or recovery controls when a property tool opens.
- Saved, unsaved, draft, generated, activated, published, and delivered states are conflated.
- Long-running work exposes only a spinner without meaningful progress or cancellation.
- An action changes dependent work without previewing or choosing the downstream effect.
- Guidance blocks expert use or appears detached from the object and action it explains.

## Anti-patterns

- Clearing filters after opening and closing a row.
- Showing a bulk destructive action without the selected count.
- Using one overflow menu for every frequent row action.
- Clearing a complete form because one field is invalid.
- Reporting a section error without highlighting the failing inputs.
- Moving undo, save, or publish controls as selection changes.
- Calling autosaved work published.
- Showing an indefinite spinner for a task with inspectable stages.
- Deleting a parent object without naming dependent external effects.
- Forcing a full tutorial before allowing direct action.

## Acceptance and review questions

- Do search, filters, selection, detail, and actions preserve active scope and place?
- Can routine decisions and safe actions be completed directly from lists and queues?
- Do controls reflect prerequisites, selection, and consequence, with one clear next action?
- Do forms use appropriate controls, purpose, examples, defaults, local validation, preserved values, and back navigation?
- Can users trace each global blocker to local evidence and concrete repair?
- Do editors synchronize canvas, structure, properties, preview, recovery, save, and publication state?
- Are autosave, pending, draft, generated, activated, published, and delivered states distinct?
- Does long-running work expose meaningful stages, duration or progress, cancellation, and final delivery?
- Are dependent downstream effects explicit and selectable before workflow-changing actions?
- Does guidance attach to the current object while retaining an expert fast path?
