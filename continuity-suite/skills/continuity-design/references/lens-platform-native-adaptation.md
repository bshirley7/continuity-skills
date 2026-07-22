# Platform-native adaptation

## Generalized principles

- Separate product invariants from platform expression: preserve the same domain objects, task meaning, state model, permissions, evidence, vocabulary, and brand character while allowing navigation containers, controls, density, materials, motion, shortcuts, menus, dialogs, and system integrations to follow the conventions people already understand on each platform.
- Design from a platform-context matrix rather than device names: enumerate available window size, aspect, orientation, posture, viewing distance, density, text scale, locale, input set, precision, hover, hardware keyboard, system chrome, safe areas, multitasking, performance, connectivity, and assistive settings; derive layout and interaction changes from capabilities and constraints.
- Adapt information architecture by preserving task and object continuity: reflow, reposition, reveal, combine, split, or relocate supporting panes as space changes; keep primary objects, selections, edits, navigation identity, and consequential actions stable, and avoid hiding required capability or resetting context merely because a window crosses a breakpoint.
- Map one navigation model to native containers: define destinations, hierarchy, history, deep links, back behavior, selection, search, modal boundaries, multi-window ownership, and restoration independently, then express them with the platform's familiar tab, bar, rail, sidebar, menu, window, or stack patterns without changing destination semantics.
- Provide input-equivalent completion with input-appropriate optimization: every core task must work through supported keyboard and assistive paths as well as touch or pointer; use platform focus order and visuals, target sizes, hover and context affordances, shortcuts, direct manipulation, gesture alternatives, text-entry behavior, and feedback appropriate to precision and posture.
- Use system capabilities through native expectations and graceful fallback: integrate sharing, files, media, camera, location, authentication, payments, notifications, widgets, search, settings, permissions, drag and drop, clipboard, background work, and automation only when they serve the task; explain consequence at the decision point and preserve a coherent path when a capability is absent or denied.
- Preserve state across platform lifecycle and configuration change: retain in-progress work, selection, scroll or spatial context, navigation, undo history, pending operations, and synchronization status across resize, rotation, folding, backgrounding, sleep, interruption, process recreation, multi-window, and device handoff; distinguish restored, stale, conflicting, and unavailable state visibly.
- Express a semantic design system through platform adapters: define product-level roles for typography, color, spacing, shape, elevation, icon meaning, state, motion, density, and components, then map them to native tokens and controls with documented intentional differences; avoid pixel-identical cloning, arbitrary divergence, and custom replacements that lose platform accessibility or behavior.
- Test complete tasks across a representative platform matrix: include minimum and maximum windows, intermediate resize, orientation and posture changes, split screen, large text, localization, high contrast, reduced motion, screen reader, keyboard-only, pointer, touch, stylus where supported, interruption, offline, denied capability, restore, multi-window, performance, and upgrade; verify functional parity and intentional differences.

## Method

- Inventory product invariants: objects, tasks, states, vocabulary, permissions, evidence, brand traits, and consequential actions.
- Build the platform-context matrix across windows, postures, viewing distance, inputs, assistive settings, system surfaces, lifecycle, and capabilities.
- Define platform-independent information architecture, destination identity, history, deep links, state, and restoration.
- Map layouts, navigation, controls, density, materials, motion, menus, dialogs, and shortcuts to each platform's native conventions.
- Specify responsive transformations and thresholds from content fit and task continuity rather than device labels.
- Define input-equivalent paths and input-specific acceleration for touch, pointer, keyboard, stylus, voice, remote, and assistive technology.
- Map semantic design tokens and component roles through documented platform adapters and exceptions.
- Prototype complete narrow, wide, resized, interrupted, denied, offline, restored, multi-window, localized, and accessibility-critical flows.
- Run the representative platform test matrix and record parity, intentional divergence, fallbacks, performance, and unresolved constraints.

## Ethical safeguards

- Do not remove core capability, safety information, privacy control, or recovery because a platform or window is constrained.
- Do not force people to change platform, input method, orientation, text scale, or assistive setting to complete a core task.
- Do not use custom controls or gestures where native behavior materially improves accessibility, predictability, security, or consent.
- Do not request system capabilities, permissions, notifications, background work, or data access merely to imitate another platform.
- Do not preserve brand consistency by overriding user contrast, text, motion, input, locale, or system preferences.
- Do not claim cross-platform parity from matching screenshots while state, navigation, input, lifecycle, or accessibility diverges.

## Variation levers

- Use platform-native components directly for common actions and system surfaces; introduce branded composition around content and distinctive product moments.
- Increase density, persistent navigation, keyboard acceleration, multi-selection, and concurrent panes for large-window expert work.
- Increase direct manipulation, target size, transient navigation, and focused single-task sequencing for compact touch contexts.
- Reveal supporting panes and comparison context as window capacity grows while preserving primary object identity.
- Use capability-specific enhancement for stylus, fold posture, widgets, shortcuts, or multi-window without making it the only path.
- Share semantic tokens and state models broadly while allowing platform typography, geometry, materials, and motion to vary intentionally.
- Increase restoration, conflict, offline, and handoff detail as tasks become longer, collaborative, or consequential.

## Tensions and tradeoffs

- Cross-platform consistency reduces relearning while native conventions improve local predictability.
- Shared components lower implementation cost while losing platform behavior, accessibility, and polish.
- Compact layouts focus attention while hiding comparison and expert controls.
- Large windows support concurrency while increasing visual density and state coordination.
- Input-specific acceleration improves expertise while creating undiscoverable or unequal paths.
- State restoration preserves continuity while restoring stale, sensitive, or unsafe context.
- Platform capabilities differentiate the experience while fragmenting product parity and support.

## Failure modes

- One platform's screenshots become the specification for every other platform.
- Device names and fixed breakpoints substitute for window, content, input, and capability reasoning.
- Responsive behavior scales or stacks pixels without preserving object, task, selection, and navigation continuity.
- Navigation chrome changes by platform but back, history, modal, deep-link, and restoration semantics are undefined.
- A touch path exists while keyboard, pointer, stylus, remote, voice, or assistive completion is incomplete.
- System capabilities are copied across platforms with unnecessary permission requests or no denied-state fallback.
- Resize, rotation, backgrounding, process recreation, or multi-window silently loses work and context.
- Brand components replace native controls and discard accessibility, focus, feedback, or expected behavior.
- Quality is reviewed at a few static sizes instead of through complete tasks and configuration transitions.

## Anti-patterns

- Screenshot porting.
- Device-name responsiveness.
- Pixel reflow without task continuity.
- Navigation chrome without semantics.
- Touch-complete only.
- Capability imitation.
- Lifecycle amnesia.
- Brand over native behavior.
- Breakpoint screenshot QA.

## Acceptance and review questions

- Are product invariants explicit, and are platform-specific differences intentional rather than accidental?
- Does the platform-context matrix cover windows, posture, distance, density, locale, inputs, assistive settings, system surfaces, lifecycle, and capabilities?
- Do layout transformations preserve task, object, selection, edit, navigation, and consequence continuity across every size?
- Are destination identity, hierarchy, history, back, deep links, modal boundaries, multi-window ownership, and restoration mapped to native navigation?
- Can every core task be completed through supported keyboard, assistive, touch, and pointer paths with appropriate acceleration and feedback?
- Do system capabilities follow native expectations, explain consequence, request proportionately, and fail gracefully when absent or denied?
- Does state survive configuration and lifecycle changes while visibly distinguishing restored, stale, conflicting, and unavailable conditions?
- Do semantic tokens and components map to native systems without pixel cloning, arbitrary divergence, or lost accessibility?
- Has the full task matrix been tested across window extremes, transitions, inputs, accessibility, locale, interruption, offline, denial, restore, and performance?
