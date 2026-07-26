# Web artifact quality

Use this offline review for generated web and UI artifacts after creative direction is established. It is a quality floor, not an aesthetic generator. Do not let conformance erase the approved signature.

## Required implementation-facing evidence

Record passing evidence at desktop, mobile, and at least one intermediate width for:

- no horizontal overflow, clipped text, content collision, or sticky obstruction;
- readable color contrast and meaning that survives without color;
- accessible names and visible focus for every interactive control;
- semantic controls, labels, landmarks, heading order, and state announcements;
- reduced-motion behavior without lost meaning or blocked completion;
- touch targets, keyboard paths, error recovery, and disabled-state explanation;
- images with dimensions, appropriate alternatives, and deliberate loading behavior;
- locale-sensitive numbers, dates, money, truncation, and text expansion where relevant.

An unresolved error or critical finding blocks implementation-facing maturity. A warning may be accepted only with project-specific rationale and evidence that the choice is intentional.

## Content and provenance

Inventory visible factual, official, final, verified, monetary, identity, warning, remedy, and contact claims. Bind each claim to content provenance. Illustrative or inferred claims require a visible qualification at the point of use. Only inspected evidence may be presented as verified. Missing evidence must render as a no-evidence, pending, source-required, or clearly illustrative state.

## State and asset completion

Render every state required by the component and completion contracts. Listing a state in `design.md` is not evidence that it works. Resolve every material asset as an artifact with bound evidence, a deliberate omission consistent with the approved direction, or a blocker. An unresolved asset blocker prevents implementation-facing maturity.

## Media-led output

For a cinematic media artifact, bind the source media identity, intrinsic metadata, playback grammar, and narrative job. Record evidence for loading, buffering, decode failure, resize, route return, direct chapter access, reduced motion, quiet static, and no-video behavior. For looping hero or chapter media, validate the repeat seam, poster transition, autoplay rejection, pause or stop, offscreen suspension, copy at different loop phases, mobile focal crop, repeat burden, and simultaneous-decoder budget. For scroll-linked playback, additionally validate rapid and reverse scroll, bounded seek work, and keyboard and touch interruption. Capture a journey contact sheet in addition to isolated screenshots. An implementation-facing artifact must demonstrate readable overlays across relevant frames, authored responsive recomposition, reachable controls and final action, and useful content without autoplay or enhanced smoothing.
