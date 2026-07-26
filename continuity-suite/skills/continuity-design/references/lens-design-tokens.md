# Design tokens

## Generalized principles

- Define visual choices by semantic role—surface, text, action, status, focus, border, chart series, heading, body, spacing, and density—then map modes and brands onto those roles instead of exposing unrelated raw values.
- Preview system changes across representative real content, interaction states, and modes so users can inspect hierarchy, contrast, tables, charts, controls, and dense work before saving.
- Treat accessibility as a constraint on theme generation and customization by preserving contrast, focus, readable typography, non-color state cues, and dedicated high-visibility or system-following modes.
- Attach spacing, size, radius, border, shadow, and motion decisions to component anatomy, variants, states, and responsive constraints rather than treating them as a flat decorative palette.
- Treat density and data formatting as semantic system layers with viewport, scanning, locale, precision, export, and downstream asset consequences that require preview and migration guidance.
- Evolve visual systems through explicit save state, legacy mapping, migration notices, and bounded overrides so existing artifacts and behaviors do not silently change.

## Variation levers

- Offer system-following light and dark modes before optional brand themes.
- Use semantic seed palettes for broad theming and bounded role-level overrides for expert tools.
- Provide compact and comfortable density as coherent modes rather than arbitrary per-screen spacing.
- Preview representative prose, forms, tables, charts, alerts, and component states.
- Allow mode-specific values when one mapping cannot preserve contrast or hierarchy.

## Tensions and tradeoffs

- Customization increases ownership while weakening consistency.
- Automatic contrast correction protects readability while reducing exact brand control.
- Semantic abstraction improves coherence while making raw values less visible.
- Compact density improves scanning while reducing touch and reading comfort.
- Legacy mappings preserve artifacts while slowing system cleanup.

## Failure modes

- Theme controls expose raw colors with no semantic roles.
- A preview omits forms, tables, charts, focus, errors, or dark mode.
- Brand accents override contrast or status meaning.
- Spacing and radius vary independently across component states.
- Density changes silently alter assets or layout.
- Formatting ignores locale, precision, units, or export.
- Existing artifacts change without migration or legacy mapping.

## Anti-patterns

- Hex-value theming without roles.
- One idealized preview card.
- Accent color used for every state.
- Dark mode created by inversion alone.
- Per-screen spacing overrides.
- Density as font-size only.
- Chart palettes with no series semantics.
- Silent token replacement.

## Acceptance and review questions

- Are colors, typography, spacing, elevation, radius, state, charts, and density organized by semantic role?
- Can users preview real content, controls, states, tables, charts, and modes before saving?
- Do customization and generated themes preserve contrast, focus, readability, and non-color cues?
- Are layout and appearance decisions attached to component anatomy, variants, states, and responsive constraints?
- Do density and formatting account for viewport, locale, precision, export, and downstream effects?
- Are legacy behavior, migration, overrides, and save state explicit?
- Is guidance limited to visible system behavior rather than claiming unobserved implementation structure?
