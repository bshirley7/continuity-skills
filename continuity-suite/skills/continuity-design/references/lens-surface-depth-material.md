# Surface, depth, and material

## Generalized principles

- Define a semantic surface model before styling components: name the base canvas, inset region, persistent panel, content container, interactive control, selected region, floating utility, transient overlay, blocking dialog, evidence frame, and atmospheric layer; specify which may occlude, receive focus, scroll, dismiss, persist, or contain another surface.
- Use the smallest sufficient set of depth cues—tonal contrast, boundary, spacing, position, scale, shadow, blur, translucency, texture, and motion—and bind each cue to hierarchy, interaction, state, or atmosphere; do not let visual elevation imply semantic priority, certainty, security, or completion without supporting evidence.
- Keep content and controls legible across every surface combination: test text, icons, focus, disabled state, charts, imagery, transparency, overlap, scrolled content, dark and light themes, high contrast, reduced transparency, and variable backgrounds; provide opaque or simplified fallbacks when effects impair meaning.
- Map transient depth to interaction behavior: make trigger, scope, focus order, background availability, dismissal, escape, outside interaction, confirmation, and restored position explicit for menus, popovers, sheets, floating tools, and dialogs; appearance alone must not define modality.
- Derive expressive material from product content, brand character, and environment: use texture, lighting, translucency, photographic material, and layered staging where they clarify physicality, creativity, atmosphere, or product evidence; restrain them in dense, repeated, consequential, low-power, or performance-sensitive work.
- Specify surface behavior as tokens and compositions rather than isolated effects: define background and foreground roles, contrast, border, elevation, opacity, shadow spread, blur, texture, nesting, clipping, theme transformation, performance budget, and deprecated combinations; review cumulative depth across a complete page or task.

## Variation levers

- Use tonal steps and borders for dense operational systems where heavy shadows create noise.
- Use modest elevation for transient controls and clear occlusion relationships.
- Use stronger material and texture on identity, editorial, or product-presentation surfaces.
- Use translucency only when background context remains useful and contrast is controlled.
- Increase surface separation in variable imagery, low-vision, high-glare, and map contexts.
- Flatten nested regions when spacing and typography already communicate grouping.

## Tensions and tradeoffs

- More surfaces clarify grouping while creating card and panel clutter.
- Elevation improves separation while implying unsupported importance or interactivity.
- Translucency preserves context while reducing contrast and increasing rendering cost.
- Texture and material create identity while competing with content and localization.
- Dark tonal systems feel immersive while making boundaries and disabled states harder to distinguish.
- Floating tools preserve canvas space while occluding content and fragmenting attention.

## Failure modes

- Every component receives its own card, shadow, or background.
- Depth levels have no semantic or interaction meaning.
- A visually elevated item is not interactive, important, or in front behaviorally.
- Translucent or image-backed surfaces fail contrast under realistic content.
- Dialogs, sheets, menus, and popovers differ visually but not in defined focus and dismissal behavior.
- Dark mode is produced by inversion without surface hierarchy testing.
- Nested surfaces create ambiguous scroll, focus, and ownership.
- Blur, shadow, texture, and transparency exceed performance or reduced-transparency constraints.

## Anti-patterns

- Card for everything.
- Shadow as hierarchy.
- Glass by default.
- Elevation without modality.
- Dark-theme inversion.
- Texture behind evidence.
- Floating-control archipelago.
- Nested-surface scroll trap.
- Effect tokens without composition rules.

## Acceptance and review questions

- Are canvas, panel, container, control, selection, floating, overlay, dialog, evidence, and atmospheric surface roles explicit?
- Does every depth cue communicate a defined hierarchy, interaction, state, or atmospheric purpose?
- Do text, controls, focus, charts, imagery, transparency, overlap, themes, and accessibility settings remain legible?
- Are trigger, scope, focus, modality, dismissal, escape, confirmation, and restored context defined for transient surfaces?
- Is expressive material tied to product or brand truth and reduced where density, consequence, or performance requires restraint?
- Are surface tokens, nesting, clipping, themes, fallbacks, performance, and deprecated combinations governed?
- Has cumulative depth been reviewed across complete realistic tasks rather than isolated cards?
