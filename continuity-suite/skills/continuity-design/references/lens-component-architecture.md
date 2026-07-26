# Component architecture

## Generalized principles

- Define each component through stable anatomy, named properties, bounded variants, and explicit states so optional content and behavior remain understandable without duplicating near-identical components.
- Compose specialized controls through shared contracts for size, spacing, label, assistance, validation, focus, disabled behavior, loading, and action hierarchy.
- Preserve semantic structure in data components through stable column roles, selection, status, filtering, pagination, row actions, and table-level actions even as density and content vary.
- Make layered components communicate trigger or parent context, focus scope, dismissal behavior, action priority, and consequence rather than relying on visual elevation alone.
- Treat responsive behavior as a component contract: identify what resizes, wraps, stacks, truncates, scrolls, becomes optional, or moves to a secondary surface.
- Validate component coherence across favorable, empty, error, disabled, loading, selected, destructive, and dense states; a polished default state is insufficient.

## Variation levers

- Use named size, density, emphasis, and intent variants instead of unconstrained per-instance overrides.
- Keep optional anatomy as explicit properties when the component identity remains stable.
- Promote a composition to a new component only when its semantics, interaction contract, or ownership meaningfully differs.
- Choose inline, popover, drawer, or modal treatment according to scope, interruption cost, and consequence.
- Adapt dense data surfaces through column priority, controlled truncation, horizontal scrolling, and secondary detail surfaces.

## Tensions and tradeoffs

- Flexible properties increase reuse while expanding invalid combinations.
- A small component inventory improves consistency while over-generalization obscures domain meaning.
- Dense data presentation improves scanning while increasing responsive and accessibility pressure.
- Overlays focus attention while weakening spatial continuity and increasing dismissal complexity.
- Local overrides accelerate delivery while eroding system predictability.

## Failure modes

- Variants encode unrelated concepts or multiply combinatorially.
- Optional slots collapse spacing or reading order unpredictably.
- Form fields diverge in label, assistance, validation, focus, disabled, or loading behavior.
- Tables use bespoke row layouts that break column comparison and bulk action logic.
- Overlay scope, focus, dismissal, or destructive consequence is unclear.
- Responsive behavior is left to incidental wrapping and clipping.
- Only the ideal default state is documented or tested.

## Anti-patterns

- One component per tiny visual difference.
- Boolean-property explosion.
- Unbounded style overrides.
- Placeholder-only form labels.
- Error text that changes layout without reservation.
- Clickable rows with hidden or competing actions.
- Modal for every secondary task.
- Destructive primary actions styled like routine confirmation.
- Desktop component simply shrunk for small screens.

## Acceptance and review questions

- Does each component have stable anatomy, named properties, bounded variants, and explicit states?
- Are labels, assistance, validation, focus, disabled, loading, submission, and recovery behavior coherent across forms?
- Do data components preserve semantic columns, selection, filters, status, pagination, row actions, and bulk actions?
- Do layered components make trigger context, focus scope, dismissal, consequence, and action priority clear?
- Is responsive behavior specified for resizing, wrapping, stacking, truncation, scrolling, optional content, and secondary surfaces?
- Have empty, error, disabled, loading, selected, destructive, dense, and favorable states been reviewed?
- Is the guidance limited to visible component behavior rather than claiming hidden implementation architecture?
