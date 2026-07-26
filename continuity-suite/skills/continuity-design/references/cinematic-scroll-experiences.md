# Cinematic scroll experiences

Use this method when a supplied or planned film, render, macro journey, spatial sequence, or other continuous media asset is the primary carrier for a commercial or narrative web experience. Apply it with the cinematic theme, guided-narrative structure, motion art-direction lens, prototype integrity, and web artifact quality. It is a conditional method, not a default landing-page template.

## 1. Preserve the media as evidence

Record the media file, source, rights or usage status when known, intrinsic dimensions, duration from loaded metadata, audio and caption state, focal regions, major visual transitions, compression constraints, and material uncertainties. Classify supplied media as supplied evidence; do not describe generated or inferred imagery as photographed fact.

Do not regenerate, interpolate, crop destructively, recolor, or replace supplied media during design work unless that exact transformation is in scope. Never infer an eight- or ten-second duration from a brief when the asset can report its actual duration.

If the media is absent, design the journey as provisional art direction. Specify its continuity, camera path, physical materials, lighting, depth, pace, and start-to-end transformation without claiming the film exists.

## 2. Run a private narrative-spine burst

Before converging on the one to three reviewable Continuity directions, generate six to ten radically different narrative spines under the same media constraint. Each spine must change the commercial offering, audience promise, chapter logic, subject-derived interface language, conversion goal, and climax—not merely the brand name or palette.

For every candidate, record compactly:

- the inferred brand and real commercial offering;
- the audience, decision, and credible conversion goal;
- the continuous physical journey and why it belongs to the offering;
- four or five observable media beats;
- the commercial job of each beat;
- one subject-derived navigation or instrumentation idea;
- one bounded expressive risk;
- implementation and accessibility risks;
- what makes the concept replaceable or specific.

Reject candidates whose film is only atmosphere, whose interface could be pasted onto unrelated footage, whose climax has no credible action, or whose narrative depends on inaccessible timing. Collapse the strongest candidates into the direction count required by the normal Continuity ambiguity assessment. The private burst expands creative search; it does not create ten approval options.

## 3. Build a beat-to-chapter contract

Scrub or inspect the media and create a time-ordered matrix. Use normalized progress as the durable design unit and timecodes as asset-specific evidence.

For each beat, bind:

- normalized range and observed time range;
- visible material, camera, lighting, or spatial change;
- narrative chapter and standalone heading;
- concise claim, mechanism, proof, qualification, or offer;
- interface response and why it is physically motivated;
- navigation position and direct skip path;
- reduced-motion and no-video equivalent;
- responsive recomposition;
- next action or transition.

Do not split one sentence across many scroll screens. Each chapter must still communicate when scanned, skipped, deep-linked, read without video, or encountered after a failed seek. The film supplies spatial continuity; the interface supplies meaning, orientation, proof, and action.

## 4. Derive the interface from the subject world

Use inspected or supplied materials, instruments, measurements, processes, labels, geometry, and language to form the interface. Examples include calibration marks, batch or folio notation, material cross-sections, dosage or energy scales, leader lines, apertures, specimen labels, coordinate systems, and process-state readouts.

Require each borrowed device to encode something true: chapter position, media time, quantity, source, scope, state, evidence, or action. Decorative gauges and fake scientific labels weaken the design. Keep annotations sparse enough that the media remains the primary visual anchor.

Specify exact roles for:

- the dominant media field;
- the primary typographic relationship;
- concept-derived navigation;
- annotations and measurements;
- one meaningful visualization or interactive instrument;
- quiet regions and negative space;
- the commercial action and its proof or qualification.

The signature must survive without the logo, primary color, media, or motion. Define a quiet static carrier for reduced-motion, loading, error, repeat-visit, and narrow-screen contexts.

## 5. Keep the commercial story credible

Infer a specific product, institution, service, release, reservation, application, or inquiry rather than a vague luxury brand. Define the conversion goal before choreography. Write finished editorial copy, not design commentary.

Move from orientation through mechanism and evidence to a credible climax. Place qualifications, eligibility, price, availability, limitations, and regulated-claim boundaries before the action they govern. A cinematic ending must resolve into a real button, link, form, reservation, purchase, download, or contact path with an immediate exit and alternative route.

## 6. Compile a stack-grounded media architecture

Inspect the actual project before selecting libraries. Do not impose React, Vite, Tailwind, GSAP, Lenis, a router, or any other dependency merely because a reference implementation used it. Reuse the installed framework, motion system, tokens, components, preview harness, and media utilities when they meet the contract. Record missing capability instead of installing during design work.

Keep responsibilities separable even when implementation names differ:

- media loading, duration, buffering, error state, and playhead control;
- document or container progress measurement;
- scroll coordination and route reset;
- chapter choreography and subject-specific interface;
- optional guided tour controls;
- prompt or reconstruction handoff outside the production experience.

For native scroll-scrubbed video, require an implementation plan that:

- reads actual duration from metadata;
- maps normalized progress to a target time rather than seeking directly on every scroll event;
- uses one animation-frame playhead with frame-rate-independent damping;
- coalesces pending targets and retains only the newest request while seeking;
- prevents stale requests from moving the film backward unintentionally;
- uses decoder callbacks where available without making them a hard dependency;
- bounds refreshes, observers, listeners, animation frames, and seek work;
- keeps source attachment stable through framework development-mode cleanup;
- handles buffering, decode failure, autoplay restrictions, Safari, iOS, resize, and route changes;
- documents damping, seek thresholds, and fallback behavior as tunable constants.

If smooth scrolling is used, drive it from the existing animation clock rather than a second competing frame loop. Preserve keyboard scrolling, anchors, browser history, direct chapter navigation, touch behavior, focus, and user interruption. Scroll smoothing must never become scroll hijacking.

## 7. Make tours optional and interruptible

A guided auto-tour may help presentation or review, but it is never the only path through the content. Require start, pause, resume, restart, completion, speed, and live progress states; visible focus; an announced status; and immediate pause or stop on wheel, touch, drag, navigation keys, Escape, or route change.

Normalize tour progress to the scrollable range, keep timing independent of document height, and avoid framework re-rendering on every animation frame. Reduced-motion mode may use chapter stepping or omit the tour entirely. Do not add a tour unless it serves a real presentation, onboarding, or accessibility-tested need.

## 8. Produce a reconstruction capsule

Bind a concise, self-contained reconstruction capsule to the private prototype or artifact manifest. Include the brand premise, commercial purpose, chapter matrix, interface language, media identity and path, stack-grounded architecture, motion and reduced-motion behavior, responsive transformations, controls, content provenance, and validation requirements.

Do not force a public `/prompt/` route or expose private reasoning in the product. A production prompt archive is a project decision; the reusable benefit is a durable handoff that another implementer can reconstruct without inventing a second design.

## 9. Validate the joined experience

Review the film and interface together at desktop, intermediate, and mobile widths. Capture individual frames and a contact sheet spanning the journey. Validate:

- chapter-to-media synchronization at start, middle, end, rapid scroll, reverse scroll, resize, and route return;
- bounded seeks, decoder stability, buffer visibility, error recovery, and acceptable frame pacing;
- headline and annotation contrast over every relevant frame, not one poster frame;
- visible progress, navigation, pause or exit, and direct access to the final action;
- keyboard, touch, zoom, safe areas, focus, reduced motion, no-video mode, and content without JavaScript-enhanced smoothing;
- standalone chapter comprehension and accurate proof or qualifications;
- mobile recomposition that preserves the concept rather than shrinking the desktop overlay;
- no horizontal overflow, fixed-control obstruction, media-control collision, or unreadably small instrumentation;
- signature recognition beyond the opening frame and through loading, error, quiet, and final states;
- resource use appropriate to repeated visits, battery, and constrained networks.

An implementation-facing prototype cannot pass on screenshots alone. Record motion behavior, media state, interruption, failure, and reduced-motion evidence. Unresolved decoder, accessibility, content-provenance, or conversion-path errors block implementation-facing maturity.

## Rejected imports

Do not import these prompt habits into Continuity Design:

- a fixed duration, page height, chapter count, framework, library, route list, or component filename;
- one-shot generation that bypasses direction selection, exact approval, or artifact critique;
- a video-first concept whose commercial purpose is invented after implementation;
- cinematic polish that hides evidence, terms, controls, loading, failure, or exit;
- mandatory smoothing, parallax, autoplay, or auto-tour;
- generated brand claims, clinical proof, certifications, scarcity, or guaranteed outcomes;
- a public reconstruction route when a private design handoff is sufficient.
