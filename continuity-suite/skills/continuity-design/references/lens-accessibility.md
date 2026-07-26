# Accessibility

## Generalized principles

- Keep names, labels, instructions, required or optional status, current values, and errors persistently associated with their controls; placeholders and entered content must not become the only way to identify a field.
- Communicate validation through specific text, location, icon or shape, and control state rather than color alone, preserve valid input, and connect grouped error summaries to the exact fields or workflow branches that need attention.
- Make important visual data redundant through direct labels, values, units, legends, symbols, patterns, ranges, written comparisons, and an inspectable table or list alternative so hue, position, or shape is never the sole carrier of meaning.
- Provide synchronized alternatives for time-based media through captions, speaker-aware transcripts, searchable text, chapter structure, controllable speed and playback, and a non-media route to the same essential information.
- Treat captions and transcripts as maintained content with visible availability and controls to generate, correct, replace, synchronize, export, disable, and remove them without making the media itself the only editing surface.
- Expose visible focus and selected state, logical grouping, current context, invocation, activation, dismissal, and return behavior for dialogs, menus, and command surfaces, preserving the underlying place while the overlay is open.
- Offer equivalent keyboard and pointer paths for frequent navigation, selection, activation, playback, editing, and dismissal, placing discoverable shortcut guidance near the commands it accelerates.
- Use readable type, sufficient contrast, spacing, clear hierarchy, and controls large enough to identify and activate across dense, dark, bright, and data-rich contexts; de-emphasis must not erase essential instructions or status.
- Allow users to control automatic movement, playback, timing, disclosure, and interruption, retaining pause, skip, close, cancel, back, and save-for-later paths where the task can safely support them.
- Keep one shared experience across input and perception needs by layering labels, alternatives, focus, shortcuts, and controls into the primary interface rather than creating a separate reduced-function accessibility path.

## Variation levers

- Use inline validation for local correction and a linked summary when errors span multiple fields, sections, or branches.
- Use direct labels for a small number of chart series, a persistent legend for many series, and a table or list for exact inspection.
- Use captions for synchronized speech, transcripts for navigation and search, and structured chapters for long-form media.
- Use shortcut hints beside frequent commands and a complete reference for broader editing or playback systems.
- Use modal focus for bounded consequential tasks and non-modal panels when users must compare the overlay with underlying content.
- Use text, icon, border, and state together for errors; use label, symbol, and value together for data categories.
- Use pause and manual advance for instructional motion and auto-scroll only as an explicit controllable preference.
- Use compact density for expert scanning only when essential labels, focus, contrast, and activation targets remain perceivable.

## Tensions and tradeoffs

- Persistent labels and instructions improve clarity while increasing visual density.
- Redundant chart encoding improves perception while reducing available plotting space.
- Detailed transcripts improve access and search while requiring correction and governance.
- Visible shortcut guidance supports discovery while adding interface noise.
- Strong focus and error treatments improve perception while competing with brand styling.
- Large activation targets improve motor access while reducing density for expert workflows.
- Automatic movement can maintain context while causing distraction or loss of control.
- One shared experience supports parity while requiring flexible layouts and layered complexity.

## Failure modes

- A field loses its identity after input because only placeholder or value remains.
- Required, optional, invalid, disabled, or completed state is communicated only by color.
- A chart or map has no labels, units, written comparison, or non-visual data route.
- Video or audio lacks captions, searchable transcript, speed control, or equivalent text.
- Captions and transcripts cannot be corrected, replaced, synchronized, or exported.
- An overlay lacks visible focus, grouping, dismissal, or return context.
- Frequent pointer actions have no discoverable keyboard equivalent.
- Low contrast, small type, tight spacing, or small targets obscure essential state and action.
- Automatic playback, scrolling, movement, or timing cannot be paused or controlled.
- An accessibility option moves users into a separate incomplete experience.

## Anti-patterns

- Using placeholder text as the only field label.
- Marking errors with a red outline but no message.
- Encoding chart series only through similar colors.
- Publishing spoken content without captions or transcript.
- Generating a transcript with no correction workflow.
- Opening a dialog without visible focus or escape.
- Hiding all keyboard shortcuts in distant documentation.
- Using low-contrast secondary text for required instructions.
- Auto-scrolling a transcript with no pause control.
- Offering an accessibility mode that omits core features.

## Acceptance and review questions

- Do labels, instructions, required or optional state, values, and errors remain associated with every control?
- Are validation and status perceivable through text and structure rather than color alone?
- Do visualizations provide labels, values, units, legends, redundant symbols, and a table or list alternative?
- Does time-based media provide synchronized captions, searchable transcript, playback control, chapters, and equivalent text?
- Can captions and transcripts be generated, corrected, replaced, synchronized, exported, disabled, and removed?
- Do overlays expose focus, grouping, invocation, activation, dismissal, and return context?
- Are frequent pointer interactions available and discoverable by keyboard?
- Are contrast, type, spacing, hierarchy, and activation targets sufficient in every supported theme and density?
- Can users pause or control automatic movement, playback, timing, disclosure, and interruption?
- Does the primary experience retain full capability across input and perception needs?
