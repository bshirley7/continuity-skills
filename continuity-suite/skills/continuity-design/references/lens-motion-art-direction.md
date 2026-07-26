# Motion art direction

## Generalized principles

- Define the purpose of every motion event before choosing timing or effect: classify it as feedback, state change, spatial continuity, hierarchy, attention guidance, progress, direct manipulation, teaching, or bounded expression; identify the affected object, initiating action, information conveyed, next task, frequency, consequence, cancellation, and non-motion equivalent.
- Preserve object and spatial continuity: animate persistent elements from their prior state or location to the next, keep direction consistent with navigation and gesture, reveal relationships through shared movement, and avoid destroying and recreating stable context when a transition can show what changed.
- Use semantic motion roles rather than independent animations: define productive and expressive families, entrance, exit, emphasis, relocation, expansion, replacement, and feedback tokens with bounded properties, easing, duration, sequencing, and platform adaptation; use equivalent meaning for equivalent events and intentional difference only when semantics differ.
- Match motion magnitude and duration to distance, size, complexity, frequency, consequence, and user intent; begin feedback promptly, keep frequent interactions brief, make exits clear space efficiently, avoid blocking the next action, and let people cancel, interrupt, reverse, or continue working whenever motion is not itself the task.
- Choreograph one clear focal event: order stable context before dynamic detail, coordinate related elements, stagger only when it improves comprehension, bound total sequence time, avoid simultaneous competing motion, and end with the important content, state, or action settled and available.
- Reserve expressive motion for low-frequency and meaningful moments whose emotional or brand role is explicit; keep routine, dense, assistive, financial, health, security, permission, error, and irreversible workflows efficient and restrained, and never let celebration overstate completion, safety, value, or user consent.
- Design reduced- and no-motion behavior as a complete equivalent mode: honor platform preferences, remove unnecessary translation, zoom, parallax, oscillation, autoplay, and large-area movement, preserve information through text, structure, state, focus, opacity, or instant replacement, allow pause or stop for persistent movement, and verify the full task with motion disabled.
- Validate motion in context and implementation: test realistic content, frame rate, input latency, interruption, repeated exposure, responsive transformation, battery and resource constraints, assistive technology, zoom, reduced motion, flashes, large-area movement, and failure or cancellation; evaluate comprehension, task time, comfort, control, and recovery rather than delight alone.
- For scroll-linked native video, separate scroll measurement from media seeking: update only a target time from normalized progress, ease one internal playhead with frame-rate-independent damping, retain only the newest target while the decoder is seeking, drain pending work after seek completion, and prevent stale requests from causing unintended reverse movement.
- For looping hero and chapter media, define the completed action, seam, repeat rhythm, focal safe area, offscreen suspension, preload and poster behavior, persistent-motion control, and reduced-motion equivalent. Keep copy meaningful at every loop phase and prevent multiple decoders from competing without a narrative reason.
- Coordinate smooth scrolling, media playhead work, chapter timelines, and optional tours through one inspected animation clock. Do not create competing frame loops, repeatedly refresh scroll geometry, or make smoothing a prerequisite for keyboard, anchor, touch, or browser-native navigation.

## Method

- Inventory every animated event by trigger, object, source state, destination state, purpose, frequency, consequence, and platform.
- Remove events with no information, continuity, feedback, teaching, or bounded expressive purpose.
- Assign semantic entrance, exit, relocation, replacement, emphasis, manipulation, progress, or expressive roles.
- Specify property, path, origin, destination, duration, easing, sequence, interruption, cancellation, and settled state.
- Define reduced-motion and no-motion equivalents before approval, including focus and programmatic state behavior.
- Walk complete high-frequency, consequential, error, recovery, background-update, and responsive flows with motion enabled and disabled.
- Measure comprehension, orientation, task delay, repeated-exposure burden, discomfort, dropped frames, cancellation, and recovery.
- Inspect actual media duration, buffering, decode and seek state, Safari and iOS behavior, route cleanup, development-mode cleanup, rapid and reverse scroll, resize, and source stability. Document damping and seek thresholds as bounded implementation constants.
- For looping media, inspect first load, every repeat seam, autoplay rejection, tab visibility, offscreen suspension, route return, mobile crop, data saving, reduced motion, and simultaneous decoder use.

## Ethical safeguards

- Do not use motion to manufacture urgency, scarcity, obligation, reward, progress, or consent.
- Do not make important information available only during an animation or require precise tracking of moving content.
- Do not block input or force repeated viewing when motion adds no task-relevant meaning.
- Do not use celebration before durable completion or in sensitive outcomes where it can trivialize uncertainty or harm.
- Do not override reduced-motion preferences for brand expression, advertising, engagement, or visual polish.
- Do not use flashing, large-area movement, parallax, oscillation, or autoplay without applicable safety assessment and user control.

## Variation levers

- Use near-immediate productive motion for frequent control feedback and routine state changes.
- Use longer but bounded transitions when distance, scale, or information architecture requires spatial tracking.
- Use shared-element continuity when object identity persists across views.
- Use fade or instant replacement when translation adds no useful spatial meaning.
- Use expressive choreography only for rare onboarding, creation, identity, or milestone moments.
- Reduce motion amplitude, distance, sequence count, and concurrent focal points as density, frequency, consequence, or sensitivity increases.

## Tensions and tradeoffs

- Motion explains continuity while delaying access to the settled state.
- Consistent motion creates familiarity while becoming monotonous or inappropriate across contexts.
- Physical realism improves predictability while feeling slow or overly theatrical in expert tools.
- Expressive motion builds identity while competing with task content and accessibility.
- Sequencing guides attention while serializing information people could otherwise scan immediately.
- Reduced motion protects comfort while poorly designed alternatives can remove orientation or feedback.

## Failure modes

- Animation is added because a component supports it rather than because the transition has a purpose.
- Objects enter and exit from directions unrelated to navigation, gesture, or spatial model.
- Every component chooses independent durations, easing, and properties.
- Frequent interactions replay expressive or blocking motion.
- Several elements animate simultaneously with no focal hierarchy.
- Celebration appears before durable completion or in sensitive states.
- Reduced motion removes information, focus movement, or confirmation instead of only unnecessary movement.
- Motion is reviewed as an isolated prototype without repeated use, failure, interruption, performance, or assistive settings.

## Anti-patterns

- Animation because available.
- Teleporting object identity.
- Independent easing zoo.
- Expressive hover tax.
- Competing choreography.
- Premature celebration.
- Reduced motion means no feedback.
- Motion demo instead of task test.
- Unbounded seek queue.
- New seek on every scroll callback.
- Independent smoothing, media, and tour frame loops.
- Hardcoded duration copied from a generation brief.
- Visible loop jump, blank repeat frame, or several autoplaying chapter films decoding offscreen.
- Frame-locked copy that becomes incoherent when a visitor enters halfway through a loop.

## Acceptance and review questions

- What feedback, state, continuity, hierarchy, attention, progress, teaching, manipulation, or bounded expressive purpose justifies each motion event?
- Do persistent objects and navigation directions preserve spatial and semantic continuity?
- Are semantic motion roles, properties, easing, duration, sequence, interruption, and platform adaptation defined consistently?
- Does magnitude and duration fit size, distance, complexity, frequency, consequence, and user intent without delaying work?
- Does choreography maintain one focal event and settle on the important content, state, or action?
- Is expressive motion limited to explicit low-frequency moments and restrained in routine or consequential work?
- Does reduced- and no-motion behavior preserve complete information, focus, state, control, and task completion?
- Have performance, repeated exposure, interruption, cancellation, accessibility, flash safety, comfort, and recovery been tested in context?
- Does scroll-linked media coalesce seeks, retain the newest target, avoid stale reversal, and remain stable under buffering, rapid input, route changes, Safari, and iOS?
- Is there one coordinated animation clock, with native scrolling, anchors, keyboard input, touch, and reduced motion preserved?
- Do loops repeat a meaningful action cleanly, remain controllable and phase-independent, suspend responsibly, and preserve a useful poster or static equivalent?
