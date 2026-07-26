# Visual state language

## Generalized principles

- Define a state model before styling: identify the object, actor, lifecycle, interaction, availability, validation, severity, freshness, synchronization, permission, and completion dimensions; name mutually exclusive states and valid transitions so one color, badge, or adjective is not forced to represent several different facts.
- Give every material state a canonical name, plain-language meaning, entry condition, permitted actions, next states, persistence, timestamp or freshness where relevant, and recovery path; use the same semantics across component, list, detail, notification, activity, and audit views.
- Encode state redundantly through an appropriate combination of text, icon, shape, contrast, position, boundary, surface, motion, and programmatic semantics; preserve visible focus and never rely on color, opacity, hover, animation, or disabled appearance alone.
- Separate interaction state from product state: distinguish hover, focus, pressed, selected, expanded, dragged, and editing from pending, synchronized, complete, failed, stale, unavailable, warning, and blocked so users can tell both what they are doing and what the system knows.
- Represent asynchronous and distributed work as evidence-backed lifecycle states: distinguish accepted, queued, transferring, validating, processing, partial, complete, failed, canceled, interrupted, offline, stale, conflicting, and synchronized; attach status to the affected object and do not equate acknowledgement, optimistic update, or progress with durable completion.
- Make unavailable and disabled states explainable: preserve the label, identify why an action cannot currently occur, distinguish permission, prerequisite, unsupported context, policy, temporary processing, and permanent absence, and provide the nearest safe resolution rather than hiding the action or reducing contrast beyond legibility.
- Test the complete state matrix across light, dark, high-contrast, reduced-motion, zoom, localization, keyboard, touch, screen reader, loading, empty, error, offline, stale, and realistic dense combinations; verify transitions and recovery, not only isolated default-state components.

## Variation levers

- Use persistent object-linked status for consequential, asynchronous, or long-running work.
- Use compact labels and icons for dense expert systems when exact meaning remains immediately available.
- Increase explanatory language and recovery guidance for infrequent, sensitive, or high-consequence states.
- Use motion as a secondary transition cue, never the sole representation of change.
- Reserve strong warning and critical treatments for conditions requiring attention or blocking action.
- Show freshness and provenance whenever state can age, synchronize, or conflict.

## Tensions and tradeoffs

- More state detail improves accuracy while increasing visual and cognitive load.
- Subtle state differences preserve visual calm while reducing discoverability and accessibility.
- Persistent status supports confidence while consuming attention after it is no longer actionable.
- Disabled controls preserve layout and discoverability while frustrating users when no reason is available.
- Optimistic feedback improves responsiveness while risking false completion.
- A compact badge system supports scanning while collapsing multidimensional operational facts.

## Failure modes

- The same color represents selection, success, synchronization, and availability.
- A status label has no defined object, entry condition, next state, or timestamp.
- Hover, focus, selected, active, and editing are visually interchangeable.
- Acknowledgement or progress looks identical to durable completion.
- Disabled actions are illegible and provide no reason or resolution.
- Warning, urgency, validation, and failure use the same treatment.
- Stale, offline, missing, partial, and synchronized data look equivalent.
- List, detail, notification, and activity views use different names for the same state.
- The component library documents defaults but not transitions or combined states.

## Anti-patterns

- One color, many meanings.
- Badge without state model.
- Hover equals selection.
- Toast equals completion.
- Opacity-only disabled state.
- Red means everything bad.
- Spinner as unnamed state.
- Freshness without timestamp.
- Default-state component catalog.
- State vocabulary drift.

## Acceptance and review questions

- Are object, actor, lifecycle, interaction, availability, validation, severity, freshness, synchronization, permission, and completion dimensions explicit?
- Does every material state have a canonical name, meaning, entry condition, actions, next states, persistence, freshness, and recovery?
- Are state cues redundant beyond color, opacity, hover, animation, or disabled appearance?
- Are interaction states distinct from product, operational, and data states?
- Are asynchronous, offline, stale, conflicting, partial, failed, canceled, and synchronized states evidence-backed and object-linked?
- Do unavailable and disabled actions retain legibility, reason, and nearest safe resolution?
- Is state vocabulary consistent across component, list, detail, notification, activity, and audit views?
- Has the full state matrix and transition behavior been tested across themes, accessibility settings, inputs, localization, density, and failures?
