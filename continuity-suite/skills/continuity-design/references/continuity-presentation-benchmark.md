# Continuity-Design presentation benchmark

Use this benchmark to test the complete `$continuity-design` process on one stable presentation problem. It evaluates process quality, product truth, concept and sequence range, media synthesis, responsive document behavior, capture integrity, and finished craft. It does not authorize implementation, publication, or external distribution.

## Fixed benchmark

- Definition: [continuity-presentation-benchmark.json](continuity-presentation-benchmark.json)
- Brief: [continuity-presentation-challenge.md](continuity-presentation-challenge.md)
- Run template: [continuity-presentation-benchmark-run.example.json](continuity-presentation-benchmark-run.example.json)
- Run schema: [design-presentation-benchmark-run.schema.json](../../../schemas/design-presentation-benchmark-run.schema.json)
- Method: [presentation-design-methodology.md](presentation-design-methodology.md)

Hash the definition, brief, source `SKILL.md`, every checkpoint, every refinement pass, and every evidence artifact. Keep run bundles private. Do not commit third-party screenshots, copied reference studies, generated exploration, private prototypes, approval records, or reviewer notes.

## Run phases

1. **Diagnose the creative pathway and freeze the run.** Ask whether to create new concepts from scratch, review an existing design, or refine a selected concept when the answer would change the work. Default to `fresh-concepts` unless the user explicitly requests review or refinement. Record the hash-bound diagnosis, basis, and known prior creative-artifact hashes used for reuse detection. Review and refinement additionally bind the user's exact instruction, inherited design ID, and every inherited artifact hash. Then record the definition and brief hashes, source commit and skill hash, and one seed. Select exactly two reference families and keep the seed unchanged.
2. **Diagnose and research.** Run project doctor, infer collaboration depth and `document-editorial` specialization, distinguish live presentation from read-ahead use, announce research, and retain private provenance.
3. **Generative exploration.** In the default fresh pathway, create new research, moodboard, generative laboratory, concept manifest, and comparison artifacts rather than replaying a prior sequence. Build four to eight project-derived lenses and eight to twelve seeds across at least three media. Declare slide-role, typography, art-direction, composition, sequence-grammar, and motion range before polishing HTML. Classify generated work as concept-forming, supporting, or rejected.
4. **Precision reference translation.** Reconstruct both reference families separately. Complete at least two correction passes per source, compile at least eight measured constraints per source, build literal project substitutions, and obtain a distinct review of the comparison ladder.
5. **Directions.** Create one to three comparable concepts. Every direction must show a complete sequence, four or more slide roles and silhouettes, a peak, a quiet or rest state, projected and read-ahead behavior, a sequence contact sheet, slide-by-slide proof that all copy and data is visible and readable, and a passed concept slop report. At least one direction must be compelling and at least one must use concept-forming media.
6. **Autonomous craft passes.** Run three bounded passes when autonomous refinement is in scope. Give each pass one hypothesis, exact artifact, numbered visual delta, preserved-strength record, self-assessment, affected-evidence rerun, and bound slop report. A pass may fail and teach; the final formal pass must pass. Passes do not select a direction.
7. **Native consultation.** Attach each selectable concept's consultation summary, concrete brand guideline, guideline hash, concept-evidence hash, and passed palette/type/license/asset/motion/carrier/responsive/provenance consistency record. Render the private board and preserve normalized numbered feedback with its exact design/revision/board/evidence binding. Material feedback must advance the revision, bind a reviewed before/after delta, refresh the affected concept and sequence evidence, and finish with a later current board and explicit ready-for-selection round. Save the `design-consultation` checkpoint. Advisory preference is never selection.
8. **Human selection.** Present ready concepts and pass history. Record only the human's explicit selection or combination. When the selection names concept-forming media as the reason, bind that media and its defining visual qualities as part of the decision.
9. **Private presentation.** Resolve the selected sequence in private HTML/CSS. Mark every frame with `data-continuity-slide` and every data-bearing region with `data-continuity-data`. For selected concept-forming media, verify the real alpha or background pixels and compare the selected source, first integration, and final integration at the same crop; replacement with a lower-capability derivative or material-loss treatment is a hard failure. Capture every slide individually at the settled viewport, verify format and frame identity, run the browser probe against every slide and required viewport, then assemble the contact sheet. Review 1440px projection, 768px read-ahead, 390px read-ahead, interaction, reduced motion, accessibility, claims, capture integrity, copy/data readability, and selected-media fidelity. Any hidden, clipped, out-of-frame, undersized, low-contrast, or font-fallback copy or data is a hard failure.
10. **Exact approval.** Bind the exact design, visual-reference, selected brand-guideline, slop, and approval-bundle hashes. Stop after design approval.
11. **Outside score.** An identified human reviewer scores every dimension, including consultation coherence and brand durability, and dispositions every hard failure. A score of at least 75 with no hard failure is benchmark-passing.

Informal presentation experiments and legacy sequence replays remain useful but must be labeled `exploratory`. They cannot satisfy the default fresh pathway. An agent self-assessment, a contact sheet, a consultation board around inherited directions, or a source-clean slop scan alone is not a passing benchmark. A truthful failed gate is a valid finding, not an invitation to self-suppress evidence.

## Evidence hygiene

Do not trust filename extensions. Verify encoded media type, dimensions, intended viewport, slide identity, and source hash. Build contact sheets from individually settled frames. Scrolling full-page capture may repeat or omit slides when scroll snapping, transforms, sticky frames, or lazy rendering are present; it is navigation evidence only.

Review live and read-ahead modes separately. A projected slide can depend on narration; a read-ahead page cannot. The narrow document may reflow rather than shrink a 16:9 frame, but it must preserve truth, hierarchy, identity, evidence, and reading order.

## Evaluation

```bash
python scripts/evaluate_design_presentation.py \
  --source-root . \
  --run-root /path/to/private/run \
  --definition skills/continuity-design/references/continuity-presentation-benchmark.json \
  --manifest /path/to/private/run/run.json
```

The report separates `stage_valid`, `benchmark_passed`, and `merge_eligible`. Direction-stage validity still requires human selection next. No benchmark stage authorizes implementation or publication.
