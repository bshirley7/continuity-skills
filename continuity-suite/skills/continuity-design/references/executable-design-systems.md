# Executable design systems

Use this reference for implementation-facing UI and web directions. Keep the design contract compact and project-specific; do not create an editor, CMS, utility framework, or parallel runtime.

## Capability digest

Summarize only inspected capabilities that materially affect the direction: existing tokens, fonts and weights, breakpoints, components, interaction and motion support, assets, preview harnesses, and missing capabilities. Pair this digest with the component map. Never infer an installed library or asset.

## Relational surface grammar

Tokens alone do not explain how a design behaves. For each material surface role, define its parent relationship, fill, boundary, elevation, radius, density, typography, and state behavior. Distinguish reading or working fields, navigation, controls, transient layers, selected regions, consequential states, and recovery surfaces when applicable. Use boundaries, depth, and color because they communicate hierarchy or state—not merely because a library offers them.

## Responsive delta matrix

Treat responsiveness as recomposition rather than uniform shrinking. For every primary carrier and material workflow region, state what happens at desktop, tablet, and mobile and what must remain invariant. Preserve meaning, semantic order, current state, required actions, recovery, and signature recognition. Test the viewports together as well as separately.

## Clean semantic output

Keep the target-native source editable and conventional for the project. Use semantic landmarks, headings, lists, labels, and controls. Avoid unnecessary wrappers, editor scaffolding, gratuitous runtime, accumulated CSS overrides, and library-default styling presented as finished identity. Screenshots are evidence; the target-native source and approved `design.md` remain authoritative.

## Change impact

Before revising a shared token, component recipe, carrier rule, or responsive transformation, identify affected surfaces and states, favorable behavior at risk, required migration or fallback, and evidence that must be recaptured. A design revision creates new planning evidence; it does not silently change an approved implementation goal.
