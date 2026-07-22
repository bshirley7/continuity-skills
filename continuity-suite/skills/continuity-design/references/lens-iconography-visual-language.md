# Iconography and visual language

## Generalized principles

- Define an icon semantic inventory before drawing forms: classify each symbol as destination, object, action, mode, status, relationship or decoration; assign one canonical concept and plain-language name; distinguish visually similar concepts such as add, create, upload, attach, share, send, move and export; and never reuse one glyph for different meanings merely because space is scarce.
- Use recognition before novelty: prefer familiar platform or domain conventions for common actions, add visible labels for primary destinations and unfamiliar, abstract or consequential controls, provide immediate tooltip or equivalent help for compact expert tools, and reserve custom symbols for product-specific concepts whose meaning is taught and consistently reinforced.
- Build one coherent visual family without forcing identical geometry: control artboard, optical size, stroke or fill weight, corner character, perspective, detail, negative space and text alignment; simplify at small sizes; compensate for visual weight; preserve contrast across themes and states; and allow platform-appropriate variants while keeping the semantic identity stable.
- Encode interaction state redundantly: distinguish default, hover, focus, pressed, selected, active mode, disabled, unavailable, pending, success, warning, error, offline and stale through an appropriate combination of label, container, shape, contrast, position, motion and programmatic state; do not make outline versus fill, color, animation or a slash carry the only meaning.
- Compose icon systems through hierarchy and grouping: separate navigation from creation, object tools from view controls, editing from sharing, local actions from global actions and routine from destructive or external effects; use placement, spacing, separators, containers and labels to create scan paths; and avoid giving every toolbar glyph equal emphasis or placing a primary action inside an undifferentiated icon row.
- Treat every interactive icon as a complete control: provide an accurate accessible name based on the action or destination rather than the picture, preserve visible-label and accessible-name consistency, use semantic control roles, adequate touch target and spacing, keyboard access, visible focus, clear disabled rationale and feedback; hide decorative or text-redundant icons from assistive output.
- Pair consequential and operational symbols with exact language and evidence: name the affected object, state, severity, scope and next action; distinguish acknowledgement from completion and warning from prohibition; show time or freshness where state can age; and never let a shield, checkmark, lock, cloud, warning triangle or trash glyph substitute for security, validation, synchronization, approval or deletion facts.
- Localize and govern symbols as content: review metaphors, gestures, people, letters, currency, reading direction and regulatory meaning by locale; mirror directional symbols when semantics require it but not inherently fixed objects; provide nongendered and non-stigmatizing representations; version semantic tokens separately from vector assets; document replacements and deprecations; and test comprehension with intended audiences rather than relying on internal familiarity.

## Variation levers

- Use persistent labels for navigation, novice and consequential contexts; allow compact symbols for repeated expert tools when names remain immediately available and keyboard accessible.
- Increase shape, text and container redundancy as status, risk, theme variability, visual impairment or environmental distraction increases.
- Adapt visual weight and platform conventions across mobile and web while preserving the same semantic token, accessible name and action contract.
- Use pictorial richness for illustration and empty-state storytelling, but reduce interface controls to the detail required for reliable recognition at their smallest use size.

## Tensions and tradeoffs

- A distinctive custom icon family strengthens brand while reducing transfer from familiar platform conventions.
- Icon-only controls increase density while shifting work to memory, hover and visual acuity.
- Consistent geometry creates polish while optical sameness can make different concepts harder to distinguish.
- Color and animation increase state salience while failing in monochrome, reduced-motion and assistive contexts.
- A large library increases coverage while making synonymy, duplication and semantic drift harder to govern.

## Failure modes

- The same symbol means different actions in navigation, toolbar and status contexts.
- Different symbols represent the same action with no semantic or platform reason.
- A custom metaphor is used without a visible label, tooltip or learning path.
- Icons share nominal dimensions but look misaligned, too heavy, too detailed or illegible at actual size.
- Selected, disabled, active, warning or stale state depends only on color, fill or animation.
- Navigation, creation, formatting, sharing and destructive actions appear in one flat icon row.
- An icon button has no semantic name, keyboard focus, adequate target or state feedback.
- A checkmark, lock, shield, cloud or warning symbol overclaims system state.
- A directional, textual, cultural or human symbol is reused unchanged across incompatible locales.
- An asset is replaced without changing or reviewing its semantic token, labels, documentation and affected states.

## Anti-patterns

- One glyph, many meanings.
- Synonym icon drift.
- Mystery custom symbol.
- Mathematical alignment only.
- Color-only icon state.
- Flat toolbar soup.
- Picture without control semantics.
- Trust badge iconography.
- Universal metaphor assumption.
- Asset swap without semantic review.

## Acceptance and review questions

- Does every icon have one canonical semantic role and plain-language name, with adjacent concepts visibly and linguistically distinct?
- Are familiar symbols preferred and unfamiliar, abstract or consequential symbols supported by visible labels, immediate help and consistent reinforcement?
- Does the family maintain optical size, weight, detail, alignment and contrast across actual sizes, platforms, themes and states?
- Are selection, mode, disabled, pending, warning, error, offline and stale states redundant beyond color, fill, motion or glyph variation?
- Do hierarchy and grouping distinguish navigation, creation, objects, views, editing, sharing, global, local and destructive effects?
- Does each interactive symbol have an accurate accessible name, semantic role, target, keyboard path, focus, feedback and appropriate assistive exposure?
- Are consequential and operational symbols paired with exact object, state, scope, freshness, evidence and recovery language?
- Have cultural, directional, textual, human and regulatory meanings been localized, audience-tested, tokenized, versioned and governed?
