# Presentation and pitch-deck design methodology

Use this method when the target is a slide deck, presentation document, keynote-style narrative, or browser-rendered deck. HTML and CSS may be the private review carrier, but the modality remains `document-editorial` unless the artifact is also an interactive product surface. A deck is not a homepage cut into slides.

## 1. Freeze truth and speaking context

Record the audience, decision the presentation supports, speaker or independent-reader context, allotted time when known, evidence supplied, claims that remain unavailable, and the exact next action the deck may request. Distinguish:

- `live-presentation`: a speaker controls pace and can provide connective tissue;
- `read-ahead`: the document must stand alone without narration;
- `mixed`: both modes are required and must be reviewed separately.

Do not invent market size, customers, testimonials, traction, revenue, savings, performance, or certainty to complete a familiar pitch arc. When evidence is absent, change the narrative claim or show a qualified no-evidence state.

## 2. Research sequence and visual mechanics

Decompose references at the level of spreads, sequences, transitions, crop relationships, type scale, density changes, material recurrence, and rhetorical pacing. A single attractive cover does not prove a deck system. For each useful mechanic, capture at least one opening, proof, quiet or transition, and closure example when the source provides them.

Build a private moodboard and concept laboratory as usual. Classify generated studies as:

- `concept-forming`: changes the thesis, sequence, composition, and at least one downstream rule;
- `supporting`: strengthens an already formed system;
- `rejected`: retained with the reason it did not improve the direction.

At least one developed presentation concept must use owned, supplied, or generated media as concept-forming. Extract at least three non-image rules from it so its contribution survives when the image is absent.

## 3. Define a sequence grammar

Before polishing slides, define the narrative spine and a slide-role inventory. Use at least four structural roles; demanding decks normally use five to seven. Useful roles include:

- opening or proposition;
- interruption or tension;
- proof or evidence;
- system explanation;
- comparison or choice;
- quiet, rest, or transition;
- consequence or authority boundary;
- closure or request.

Give every role a composition rule, density range, type behavior, media role, transition behavior, and read-ahead equivalent. Do not make every slide a title, paragraph, and image in the same shell. In a multi-concept set, directions must differ in sequence grammar as well as typography, art direction, and composition.

Map the argument before filling slots. A strong sequence needs:

1. an intelligible opening promise;
2. rising specificity rather than repeated restatement;
3. one visible rhetorical and compositional peak;
4. at least one quiet or evidence-led rest;
5. a closure whose requested action follows from the proof.

## 4. Build concepts at comparable depth

Each direction board must show more than a cover. Include readable crops for opening, interruption or tension, proof, system explanation, quiet or edge, and closure, plus a sequence contact sheet. Use real presentation copy. Record:

- narrative thesis and sequence outline;
- slide-role inventory and role count;
- repeated-template ratio;
- primary carrier and signature move;
- type, color, material, image, and motion systems;
- concept-forming media lineage;
- projected and read-ahead transformations;
- preservation promise, tradeoff, anti-reference, and weakest moment.

Require at least four visibly different slide silhouettes. A silhouette is structural: a font size, palette, or image swap does not create a new one.

## 5. Refine with bounded autonomous passes

Before asking for direction feedback, an agent may run up to three self-directed craft passes when the user requested autonomous quality improvement. Preserve each pass as a private immutable artifact. Every pass requires:

- one primary hypothesis;
- exact changes;
- strengths deliberately preserved;
- a numbered visual delta;
- a fresh self-assessment;
- responsive and slop evidence invalidation and rerun where affected.

Change the variable under test rather than redesigning indiscriminately. Useful pass order is narrative truth, proof depth, then rhythm and peak hierarchy. These passes improve the candidate; they never select, approve, or claim that taste improved without human or blinded comparison evidence.

## 6. Validate the artifact, not the source claim

Render every slide individually at the settled presentation viewport. Verify encoded media type, dimensions, viewport, slide identity, and source hash before accepting a capture. Assemble the contact sheet only from verified individual frames. Do not treat a scrolling full-page stitch as deck evidence when snapping, sticky frames, transforms, or lazy rendering may duplicate or omit slides.

Review at minimum:

- desktop projection at the intended aspect ratio;
- tablet read-ahead at 768px width;
- mobile read-ahead at 390px width;
- keyboard and touch navigation;
- reduced-motion behavior;
- semantic labels, focus behavior, contrast, reading order, and image alternatives.

The mobile or tablet document may reflow instead of preserving one projected frame per viewport. Preserve argument, hierarchy, identity, and evidence while adapting density and sequence.

## 7. Run the presentation slop context

Supply `presentation_fidelity` to `continuity design slop-check`:

- `slide_role_count`;
- `repeated_template_ratio`;
- `narrative_peak_present`;
- `quiet_or_rest_present`;
- `live_presentation_review_complete`;
- `read_ahead_review_complete`;
- `claims_provenance_complete`;
- `capture_integrity_verified`.

Use [presentation-slop-context.example.json](presentation-slop-context.example.json) as the presentation-specific fragment inside the normal [slop manifest](slop-manifest.example.json).

Also inspect fake metrics, gratuitous quote slides, decorative charts, unreadable cinematic typography, generic investor chronology, repeated title-plus-body shells, and image-as-wallpaper. These are unexplained default risks rather than universal bans.

## 8. Stop at the human gate

Present the concept comparison, pass history, final contact sheet, responsive evidence, slop report, and unresolved findings. Ask for numbered `keep`, `change`, `avoid`, or `uncertain` reactions. A failed exploratory slop report can be a truthful benchmark finding; it cannot be called selection-ready. Exact design approval still authorizes only the deck design contract, never product implementation, publication, fundraising claims, or external distribution.
