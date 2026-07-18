# Media production

## Generalized principles

- Keep asset identity, source, rights, metadata, version, proxy or original status, usage context, and preview available from library through edit, review, render, and publication.
- Synchronize selection and time across asset bin, canvas or monitor, layers or tracks, timeline, playhead, properties, comments, and output so every edit has an unambiguous target.
- Separate reversible edit instructions from source media and expose original, current version, unsaved changes, history, reset, undo, redo, and explicit destructive boundaries.
- Model rendering, generation, upload, processing, review, approval, publication, and delivery as distinct states tied to the exact asset and version rather than one generic completion signal.
- Bind collaboration feedback to an exact version and, where relevant, frame, timecode, layer, region, or object; distinguish discussion, requested change, approval, and resolved status.
- Treat export as a specification of version, range, format, dimensions, codec or quality, destination, rights, overwrite behavior, and progress with a durable resulting artifact.

## Variation levers

- Use proxies for responsive editing while keeping original and output status explicit.
- Use timeline views for temporal composition and layer views for spatial or semantic stacking.
- Use nondestructive edits by default with explicit flattening or replacement boundaries.
- Use version comparison when review or approval spans material changes.
- Move long renders to background status only with durable task identity and return paths.

## Tensions and tradeoffs

- Rich metadata improves reuse while slowing ingestion.
- Live preview improves confidence while consuming processing resources.
- Nondestructive history protects work while increasing version complexity.
- Collaboration accelerates review while multiplying ambiguous feedback.
- High-quality output increases wait time and storage cost.

## Failure modes

- Proxy and original are indistinguishable.
- Selection differs between timeline, preview, and properties.
- A trim or effect overwrites source without warning.
- Comments are detached from version or time context.
- Render success does not identify the resulting file.
- Publication occurs from the wrong version.
- Rights or attribution disappear during export.

## Anti-patterns

- Untitled asset pile.
- Timeline with no selected-track cue.
- Destructive autosave.
- Comment without version or timecode.
- Generic rendering spinner.
- Export preset with hidden codec or dimensions.
- Published draft mistaken for approved master.
- Generated result with no prompt or version relationship.
- Download action with unknown rights.

## Acceptance and review questions

- Are asset identity, source, rights, metadata, version, original or proxy status, usage, and preview preserved?
- Are selection and time synchronized across library, preview, layers, timeline, properties, comments, and output?
- Are edits nondestructive by default with original, history, reset, undo, redo, and destructive boundaries visible?
- Are generation, processing, review, approval, publication, and delivery distinct version-bound states?
- Are comments bound to exact version, time, frame, layer, region, or object?
- Does export identify version, range, format, quality, destination, rights, overwrite behavior, progress, and resulting artifact?
- Is guidance limited to visible production behavior rather than claiming hidden media processing?
