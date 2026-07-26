# Direct manipulation

## Generalized principles

- Expose manipulation as a complete contract: identifiable object, available affordance, active tool or mode, valid target or range, live preview, constraint feedback, commit boundary, and recovery path.
- Preserve object identity and scope across canvas, layer, group, timeline, and property views so users know exactly what a gesture will affect before it changes.
- Pair direct gestures with precise inspectable controls—numeric values, alignment, snapping, handles, keyboard movement, range bounds, and zoom—so manipulation supports both exploration and exact work.
- Preview outcome continuously while distinguishing transient manipulation from persisted state; make cancel, reset, undo, and redo proportional to consequence and available after commitment.
- Make invalid targets, boundaries, collisions, locked content, unavailable actions, and destructive consequences visible during manipulation rather than only after drop or save.
- Provide equivalent non-pointer paths for selection, reorder, movement, resizing, value adjustment, and commitment with visible focus and announced state changes.

## Variation levers

- Use handles when the manipulable dimension or object boundary is not otherwise obvious.
- Use snapping and alignment guides for spatial precision, with a way to inspect or override values.
- Use live preview for reversible continuous changes and staged preview for expensive or consequential operations.
- Use explicit tool modes for draw, measure, pan, zoom, and selection when gestures would conflict.
- Provide both coarse touch control and precise numeric or keyboard alternatives.

## Tensions and tradeoffs

- Directness improves learnability while hidden gestures reduce discoverability.
- Snapping speeds alignment while frustrating precision.
- Live preview improves confidence while increasing processing cost.
- Persistent handles expose affordance while cluttering dense canvases.
- Mode-based tools prevent conflict while creating mode errors.

## Failure modes

- No visible indication of the draggable or resizable region.
- Drop targets appear only after an invalid drop.
- Selection changes during manipulation without explanation.
- Canvas and property values disagree.
- Snapping has no cue or override.
- A destructive gesture commits immediately with no recovery.
- Touch targets are too small for coarse input.
- Keyboard users cannot perform the same transformation.

## Anti-patterns

- Invisible drag-only control.
- Cursor as the only active-mode signal.
- Mystery meat handles.
- Snap without guide.
- Gesture with no preview.
- Auto-save destructive crop with no original.
- Undo that changes scope unpredictably.
- Pinch-only zoom.
- Reorder with no announced position.
- Canvas-only precision.

## Acceptance and review questions

- Are object, affordance, active mode, valid targets, constraints, preview, commit, and recovery visible?
- Does selection preserve object, group, layer, canvas, and timeline scope?
- Are precise values, keyboard alternatives, snapping, alignment, bounds, and zoom available where needed?
- Are transient preview and persisted state distinguishable?
- Do cancel, reset, undo, and redo match the consequence of the operation?
- Are invalid targets, locks, collisions, boundaries, and destructive effects exposed before commitment?
- Can non-pointer users perform and verify equivalent transformations?
- Is guidance limited to visible interaction evidence rather than claiming unobserved gesture implementation?
