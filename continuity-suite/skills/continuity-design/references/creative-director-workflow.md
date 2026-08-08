# Creative-director workflow

Use this workflow when the user needs a direction, not only a contract. One sentence is enough to begin. Tell the user they may react to visuals instead of supplying design vocabulary.

## 1. Diagnose

- Inspect the product, current implementation, brand material, audiences, strengths, debt, constraints, and behavior to preserve.
- Infer `guided`, `collaborative`, or `creative-peer`. Ask one calibration question only when the working relationship remains materially unclear.
- Infer `brand-marketing`, `product-system`, `document-editorial`, `image-art-direction`, `cinematic-experience`, or `mixed`.
- Preserve the user's exact language as feedback evidence; translate it into private design decisions without making the user learn a taxonomy.

## 2. Analyze and research

Default to a short adaptive research pass. Announce the pass and offer an opt-out. Use `offline`, `user-supplied-only`, or `declined` when appropriate. The agent may use web or image search, but the shared runtime never performs network access.

For named references, record a provisional decomposition of composition, typography, density, imagery, motion, and voice. State the likely appeal and a project-specific transformation. Never silently imitate the reference.

Build a private moodboard of 12–20 numbered tiles across two or three axes:

- subject or material;
- treatment or light;
- graphic or spatial language.

Record source, capture time, intended lesson, ownership, and `prohibited_copying: true` for every tile. Keep third-party screenshots and moodboards private and non-shipping. Render the board with `continuity design visual-render --input <moodboard.json>`.

## 3. Teach visually

Render only the useful contrasts with `continuity design visual-atlas --input <request.json>`. The self-contained private HTML/SVG plate shows type, palette, composition, density, surface, motion intent, and a counterexample. Ask the user to react to plate numbers.

## 4. Concept

- If material direction is unclear, create two or three equally developed boards and preselect no winner.
- If direction is clear, recommend one board and show one or two deliberately contrasting studies.
- Keep fidelity comparable. A palette or font swap is not a new direction.

Every board must contain a thesis, one signature move, palette, real-copy type specimen, wide composition, narrow transformation, imagery or material treatment, motion storyboard or explicit no-motion decision, preservation promise, tradeoff, anti-reference, and passed concept-stage slop report. Render comparisons with `visual-render`, then validate the manifest with `concept-validate`.

For atlases, moodboards, concept comparisons, and visual deltas, capture browser evidence at mobile, tablet, and desktop widths. Run `scripts/artifact-browser-probe.js` in each viewport, review the three captures together, and retain their file hashes in the private evidence package. A source-valid HTML page without inspected browser output is not complete visual evidence.

## 5. Feedback and refinement

Ask for reactions against numbered elements: `keep`, `change`, `avoid`, or `uncertain`, plus why. Render a visual delta showing what changed, what stayed, and why. Record it with `feedback-record`.

Preserve accepted, rejected, and unresolved decisions. Contract-changing feedback creates a new revision, clears prior selection, and invalidates affected concept and slop evidence. Continue until the user explicitly marks the concept set ready for selection; do not optimize for the fewest turns.

## 6. Approve, version, and scale

Run the slop gate on every concept, the selected private prototype, and the implementation-facing artifact. Selection requires ready concept evidence. Exact approval requires a passed prototype report and binds:

- design-document hash;
- approved visual-reference hash;
- slop ruleset version and hash;
- combined approval-bundle hash.

Promote only project-owned, supplied-with-rights, or generated references into `docs/design/references/`. Preserve rejected choices in the durable alignment contract. Design approval still never authorizes implementation.
