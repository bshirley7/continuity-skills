# Theming

## Generalized principles

- Define light, dark, and system-following modes as coordinated semantic mappings for surfaces, text, borders, actions, focus, status, elevation, and media rather than as palette inversion.
- Layer brand expression onto stable semantic roles and interaction contracts so logos, accents, typography, and imagery can vary without changing meaning, priority, or expected behavior.
- Treat accessibility preferences as authoritative overrides that remain effective across every brand and appearance mode, including contrast, text scale, focus visibility, color differentiation, and motion behavior.
- Preview theme changes on representative content, controls, navigation, status, focus, validation, charts, and dense work instead of relying on isolated swatches or a single idealized card.
- Model density as a coordinated component mode affecting spacing, row height, typography, hit targets, truncation, and information exposure while preserving task hierarchy and accessibility.
- Specify how user preference, operating-system preference, product defaults, organization policy, and saved personal choices resolve when they disagree.

## Variation levers

- Offer light, dark, and system-following modes before optional branded presets.
- Allow bounded semantic accent and typography choices while protecting status, focus, and destructive roles.
- Provide compact and comfortable density as coherent named modes.
- Preview both favorable and adverse states in every theme.
- Allow user accessibility overrides to supersede organization or brand styling.

## Tensions and tradeoffs

- Brand flexibility can weaken semantic consistency.
- Dark themes can reduce glare while obscuring elevation and disabled states.
- High contrast can conflict with intended visual subtlety.
- Compact density improves scanning while stressing targets and readability.
- System-following behavior respects preference while making appearance time-dependent.

## Failure modes

- Dark mode is generated through inversion alone.
- Brand accents replace status or focus semantics.
- High-contrast behavior is tested only in the default theme.
- A preview omits errors, disabled controls, selection, charts, or dense tables.
- Density changes only font size or padding and leaves component behavior inconsistent.
- Preference precedence is undocumented or resets unexpectedly.

## Anti-patterns

- Raw color replacement without semantic roles.
- One preview card for an entire product.
- Brand color used for every interactive state.
- Accessibility as a separate theme users must rediscover.
- Compact mode with undersized targets.
- Theme-specific component forks.
- Silent preference overrides.

## Acceptance and review questions

- Are light, dark, and system modes semantic mappings rather than inversions?
- Does brand customization preserve state meaning, focus, hierarchy, and behavior?
- Do accessibility preferences override every brand and appearance mode predictably?
- Does preview cover representative content, controls, states, navigation, data, and dense work?
- Is density coordinated across spacing, typography, targets, truncation, and information exposure?
- Is precedence among user, system, product, and organization preferences explicit?
- Is guidance limited to visible theme behavior rather than claiming unobserved implementation structure?
