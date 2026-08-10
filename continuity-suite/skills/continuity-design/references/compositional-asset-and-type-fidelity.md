# Compositional Asset and Type Fidelity

Use this gate whenever a reference or generated study depends on subject occlusion, embedded display type, layered material, or unusually characteristic typography. A strong reference is not reduced to a palette and category label; identify the exact relationship that makes it work and rebuild that relationship with editable project-owned parts.

## Extract the relationship first

Record which element sits behind, within, and in front of each other element; the shared crop and focal point; the display face's width, height, weight, spacing, line breaks, and role; and the narrow transformation. Name what remains literal during the first close study and what changes to carry the project's own message. Do not substitute “condensed,” “editorial,” or “technical” for measured character.

## Generate usable planes

When type and subject overlap, use image generation or editing to produce a registered asset family rather than one finished flattened hero:

1. A background plate with the same canvas, crop, light, and focal registration as the final composition.
2. Live HTML typography and content whenever text must remain accessible, responsive, and editable.
3. A foreground subject or material plane with real alpha transparency and transparent corners.
4. Optional annotation, shadow, texture, or interaction planes only when they perform a named compositional job.

Generate at the intended slot dimensions. Inspect the alpha result, edges, crop, and occlusion. A checkerboard preview, written claim of transparency, or two identical composites does not prove separate planes. Third-party moodboard imagery remains private and non-shipping.

## Preserve selected-media impact

When a human prefers one concept because its generated or supplied media is more visually impactful, that preference binds the media—not merely its subject label. Retain the selected file or create a provenance-preserving edit at equal or greater visual capability. A simplified SVG, generic vector reconstruction, CSS primitive, or flatter substitute is drift even when it depicts the same object.

Inspect the asset's actual channels and corner pixels before choosing an integration method. A visible checkerboard can be baked into RGB pixels rather than alpha. Use one of three explicit strategies: retain the image in its native frame, use a verified alpha-bearing asset, or make a background-matched edit that preserves the subject and its provenance. Do not use `mix-blend-mode`, filters, masks, overlays, or aggressive crops merely to hide a bad background when they also suppress the color, texture, depth, shadow, scale, or material contrast that made the asset concept-forming.

Bind a comparable-crop triptych of the selected source, first integration, and final integration. Review it at every affected viewport and record whether the subject's defining material impact was retained or strengthened. If the integration changes, invalidate the prior visual review and slop report and rerun them.

## Prove implementation consumption

Every workflow-v3 concept records a `composition_asset_plan`. For a layered relationship it includes independently hash-bound background, live-type, and foreground planes; unique z-indexes; identical background and foreground dimensions; an RGBA foreground with transparent and opaque pixels and four transparent corners; and responsive crop behavior. The complete prototype exposes every plane with `data-continuity-composition-plane` and consumes each asset path. Declaring a layer without using it fails validation.

## Prove typographic character

Every workflow-v3 concept records a `typographic_transfer` using real project copy. Include the exact face, source and license evidence, source character being preserved, project-specific transformation, type-to-media relationship, narrow behavior, and bounded metric tolerances. Run `continuity design probe-prepare --target <prototype.html>` before capture. It resolves local HTML, CSS, JavaScript, TypeScript, JSX, and TSX dependencies—including `@/` and `tsconfig.json` or `jsconfig.json` path aliases—injects the three fingerprint meta tags, and returns the exact `runtime_source_files` declaration. Continuity hashes normalized HTML plus every reachable source file; both fingerprint meta values are normalized before the HTML hash is calculated, avoiding self-reference. Run the shipped `scripts/artifact-browser-probe.js` after fonts settle for both the prepared reference reconstruction and prepared candidate desktop concept, then bind both JSON outputs without modification; [typography-render-probe.example.json](typography-render-probe.example.json) shows that browser output shape. The probe records the document URL, target and source-bundle fingerprints, rendered DOM element, computed family, matching loaded `FontFace`, rendered copy, cap-height ratio, word-width ratio, line count, actual plane URLs, visibility, computed z-indexes, and geometry. Exact type metrics must report `measurement_method: canvas-2d`; a constrained browser without canvas access may still capture signatures, invariants, geometry, accessibility, and responsive evidence, but its typographic transfer remains explicitly unavailable and cannot pass the silhouette gate. The validator rejects evidence captured from a different document or an older React, script, style, or source bundle; calculates type deltas and plane intersections; and gives `passed: true` or source-text markers no independent authority.

The same probe records rendered signature carriers and protected interaction semantics. Mark every signature carrier with `data-continuity-signature="<signature-id>"` and its journey role with `data-continuity-signature-role`; mark copy or state that an interaction must never rewrite with a unique `data-continuity-invariant`. Concept validation measures opening visibility at desktop and mobile, requires the signature across the declared journey roles at every viewport, and compares invariant snapshots across default and changed interaction states. Written coverage claims do not substitute for those DOM measurements.

A font that merely belongs to the same category does not pass when the direction depends on a distinctive silhouette. If the exact face cannot ship, create and measure a deliberate alternative; do not silently accept a browser fallback or horizontally distort an unrelated face.

## Review as composition, not inventory

Compare the source, close reconstruction, adapted composition, and narrow result together. Ask whether the subject still organizes the frame, live type participates in depth rather than floating over a backdrop, the type silhouette carries the intended energy, the selected media retains its defining material impact after integration, and the project message continues the same visual grammar. Then run the AI-slop gate with editable-depth, font-transfer, approved-layer-plan, approved-typographic-character, selected-media-fidelity, background-integration, and material-contrast findings explicitly dispositioned. Selection binds the type-transfer and composition-plan hashes into the approval bundle; prototype and implementation manifests must carry those exact hashes so later stages cannot silently flatten the approved direction.
