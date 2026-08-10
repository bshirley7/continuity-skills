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

1. **Freeze the run.** Record the definition and brief hashes, source commit and skill hash, and one seed. Select exactly two reference families and keep the seed unchanged.
2. **Diagnose and research.** Run project doctor, infer collaboration depth and `document-editorial` specialization, distinguish live presentation from read-ahead use, announce research, and retain private provenance.
3. **Generative exploration.** Build four to eight project-derived lenses and eight to twelve seeds across at least three media. Declare slide-role, typography, art-direction, composition, sequence-grammar, and motion range before polishing HTML. Classify generated work as concept-forming, supporting, or rejected.
4. **Precision reference translation.** Reconstruct both reference families separately. Complete at least two correction passes per source, compile at least eight measured constraints per source, build literal project substitutions, and obtain a distinct review of the comparison ladder.
5. **Directions.** Create one to three comparable concepts. Every direction must show a complete sequence, four or more slide roles and silhouettes, a peak, a quiet or rest state, projected and read-ahead behavior, a sequence contact sheet, and a passed concept slop report. At least one direction must be compelling and at least one must use concept-forming media.
6. **Autonomous craft passes.** Run three bounded passes when autonomous refinement is in scope. Give each pass one hypothesis, exact artifact, numbered visual delta, preserved-strength record, self-assessment, affected-evidence rerun, and bound slop report. A pass may fail and teach; the final formal pass must pass. Passes do not select a direction.
7. **Human selection.** Present concepts and pass history. Record only the human's explicit selection or combination.
8. **Private presentation.** Resolve the selected sequence in private HTML/CSS. Capture every slide individually at the settled viewport, verify format and frame identity, then assemble the contact sheet. Review 1440px projection, 768px read-ahead, 390px read-ahead, interaction, reduced motion, accessibility, claims, and capture integrity.
9. **Exact approval.** Bind the exact design, visual-reference, slop, and approval-bundle hashes. Stop after design approval.
10. **Outside score.** An identified human reviewer scores every dimension and dispositions every hard failure. A score of at least 75 with no hard failure is benchmark-passing.

Informal presentation experiments remain useful but must be labeled `exploratory`. An agent self-assessment, a contact sheet, or a source-clean slop scan alone is not a passing benchmark. A truthful failed gate is a valid finding, not an invitation to self-suppress evidence.

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
