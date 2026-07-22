# Keyboard and expert workflows

## Generalized principles

- Make command surfaces searchable, grouped, scope-aware, keyboard-navigable, and visibly selected, with action labels and shortcut hints that remain understandable without memorization.
- Preserve explicit focus, selection, active object, mode, and parent scope across keyboard navigation so speed never makes the target of an action ambiguous.
- Document shortcuts by user task with platform-appropriate notation, conflict handling, discoverable invocation, and pointer-accessible equivalents.
- For batch operations, expose selection count, selection scope, filters, paging implications, affected objects, available actions, and consequence before commitment.
- Support expert acceleration as a parallel path over the same semantic actions, permissions, validation, feedback, and undo model used by pointer and assistive interaction.
- Keep recovery close to speed: provide predictable escape, undo, cancellation, focus restoration, and confirmation for destructive or broad commands.

## Variation levers

- Use command palettes for broad searchable action access.
- Use inline shortcut hints for frequent contextual actions.
- Use customizable bindings only with conflict detection and reset.
- Use range and select-all controls with explicit filtered or global scope.
- Require confirmation only when scope or consequence is not easily reversible.

## Tensions and tradeoffs

- More shortcuts improve speed while increasing discovery burden.
- Global commands improve reach while weakening context.
- Custom bindings support experts while fragmenting support and documentation.
- Dense focus indicators aid certainty while adding visual noise.
- Confirmation protects broad actions while slowing routine work.

## Failure modes

- Focus is invisible or lost after an action.
- The selected command target is ambiguous.
- Shortcut labels use the wrong platform notation.
- A command palette hides unavailable-action reasons.
- Select all silently crosses filters or pages.
- Keyboard and pointer paths invoke different semantics.
- Escape, undo, or focus restoration is inconsistent.

## Anti-patterns

- Memorization-only shortcuts.
- Command names without object scope.
- Hover-only shortcut discovery.
- Focus ring removed for aesthetics.
- Select all with hidden population.
- Single-key destructive command.
- Custom binding without conflict warning.
- Keyboard-only expert feature.
- Modal confirmation for every command.

## Acceptance and review questions

- Are commands searchable, grouped, scoped, navigable, selected, and labeled with discoverable shortcuts?
- Are focus, selection, active object, mode, and parent scope always visible?
- Are shortcuts task-organized, platform-correct, conflict-aware, and available through pointer or assistive paths?
- Do batch actions expose count, scope, filters, paging, affected objects, and consequence?
- Do all input paths share semantics, permission, validation, feedback, and undo?
- Are escape, cancellation, undo, and focus restoration predictable?
- Is guidance limited to visible expert-workflow behavior rather than claiming hidden input handling?
