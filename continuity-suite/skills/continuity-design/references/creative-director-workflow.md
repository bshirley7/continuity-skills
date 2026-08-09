# Creative-director workflow

Use this workflow when the user needs a direction, not only a contract. One sentence is enough to begin. Tell the user they may react to visuals instead of supplying design vocabulary.

## 1. Diagnose

- Inspect the product, current implementation, brand material, audiences, strengths, debt, constraints, and behavior to preserve.
- Infer `guided`, `collaborative`, or `creative-peer`. Ask one calibration question only when the working relationship remains materially unclear. Apply the corresponding collaboration contract to recommendation posture, explanation depth, feedback scope, and challenge style.
- Infer `brand-marketing`, `product-system`, `document-editorial`, `image-art-direction`, `cinematic-experience`, or `mixed`.
- Preserve the user's exact language as feedback evidence; translate it into private design decisions without making the user learn a taxonomy.

## 2. Analyze and research

Default to a short adaptive research pass. Announce the pass and offer an opt-out. Use `offline`, `user-supplied-only`, or `declined` when appropriate. The agent may use web or image search, but the shared runtime never performs network access.

For named references, record a provisional decomposition of composition, typography, density, imagery, motion, and voice. State the likely appeal and a project-specific transformation. Never silently imitate the reference.

Build a private moodboard of 12–20 numbered tiles across two or three axes:

- subject or material;
- treatment or light;
- graphic or spatial language.

Save and hash each captured image. Record source, capture time, intended lesson, project mechanic, ownership, and `prohibited_copying: true` for every tile. Use at least two axes and three sources; duplicate captures do not count. Keep third-party screenshots and moodboards private and non-shipping. Render the board with `continuity design visual-render --input <moodboard.json>` and later disposition every tile against a concept.

## 3. Teach visually

Render only the useful contrasts with `continuity design visual-atlas --input <request.json>`. Supply the same real project copy to every plate. Each self-contained private plate must change the organizing idea, type roles, composition, density, surface, motion intent, responsive transformation, and counterexample—not merely palette. Ask the user to react to plate numbers.

## 4. Generative concept laboratory

Before composing web pages or polished boards, run the [generative concept laboratory](generative-concept-laboratory.md). First declare a range plan spanning at least four art-direction families, three typography strategies in three families, three composition families, and five page-depth roles. Generate eight to twelve inexpensive experiments across four to eight project-derived lenses and at least three media when available. Image generation and editing are ideation tools: use them to discover hierarchy, material, cropping, type, motion, interaction, and deeper-page relationships, not merely to decorate a chosen concept. Cross-pollinate at least two seed pairs, shortlist three to six, and validate the hash-bound record with `concept-lab-validate`.

Delay responsive HTML until seeds are clustered. This prevents every divergent idea from inheriting the same layout, type pairing, rules, and restrained palette. If generated imagery contributes to a direction, extract at least three repeatable non-image system decisions from it.

## 5. Concept

- If material direction is unclear, create two or three equally developed boards and preselect no winner.
- If direction is clear, create one selectable recommended board and one or two non-selectable contrast studies that each test a named uncertainty.
- Keep fidelity comparable. A palette or font swap is not a new direction.

Every board must contain a thesis, impact thesis, primary carrier, emotional register, seed lineage, system extractions, one signature move, palette, real-copy type specimen, a planned typography system, a planned media system, a distinct composition family, a journey of at least five stages, concept-specific mobile/tablet/desktop runtime probes, distinct PNG wide composition, distinct PNG narrow transformation, imagery or material treatment, motion storyboard or explicit no-motion decision, preservation promise, tradeoff, anti-reference, and passed concept-stage slop report bound to those exact renders. Before slop review, pass the separate creative-range gate: unique five-second reactions, every pair different in at least three material dimensions, distinct type/art/composition systems, an adversarial pass per concept, and an explicit house-tell review where project identity wins. Show each tall full-page capture as a journey ribbon in the comparison. Then perform page-grammar congruence review against the complete prototype: the prototype must mark every behavior required by its grammar family, each behavior must span at least two declared journey stages, and the reviewer must record both the strongest match and weakest mismatch. A written grammar claim without those artifact markers fails. Render comparisons with `visual-render`, then validate the manifest with `concept-validate`.

For atlases, moodboards, concept comparisons, visual deltas, and every individual concept, capture valid browser-rendered PNG evidence at mobile, tablet, and desktop widths. Save the JSON returned by `scripts/artifact-browser-probe.js` in each viewport and bind its file hash; free-form claims that the probe passed are invalid. Review each concept's three captures together, then review the comparison set. Reusing the comparison probe as concept evidence is invalid. A source-valid HTML page without inspected browser output is not complete visual evidence.

## 6. Feedback and refinement

Ask for reactions against numbered elements: `keep`, `change`, `avoid`, or `uncertain`, plus why. Render a visual delta showing what changed, what stayed, and why. Record it with `feedback-record`.

Preserve accepted, rejected, and unresolved decisions in the active revision as well as its archive. Every `change` or `avoid` reaction is material unless refreshed evidence proves otherwise; it creates a new revision, clears prior selection, and invalidates affected concept and slop evidence. Redraft the same invalidated revision so feedback is carried forward rather than incrementing twice. Continue until the user explicitly marks the refreshed concept set ready for selection; do not optimize for the fewest turns.

## 7. Approve, version, and scale

Run the slop gate on every concept, the selected private prototype, and the implementation-facing artifact. Selection requires ready concept evidence. Exact approval requires a passed prototype report and binds:

- design-document hash;
- approved visual-reference hash;
- slop ruleset version and hash;
- combined approval-bundle hash.

Promote only project-owned, supplied-with-rights, or generated references into `docs/design/references/`. Preserve rejected choices in the durable alignment contract. Design approval still never authorizes implementation.
