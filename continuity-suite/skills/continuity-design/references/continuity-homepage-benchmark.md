# Continuity-Design homepage benchmark

Use this benchmark to test the complete `$continuity-design` process on one stable, demanding homepage problem. It evaluates process quality, design judgment, creative range, truthfulness, and finished craft. It does not authorize implementation and is not a substitute for the separate blinded paired-output benchmark.

## Fixed benchmark

- Definition: [continuity-homepage-benchmark.json](continuity-homepage-benchmark.json)
- Brief: [continuity-homepage-challenge.md](continuity-homepage-challenge.md)
- Run template: [continuity-homepage-benchmark-run.example.json](continuity-homepage-benchmark-run.example.json)
- Run schema: [design-homepage-benchmark-run.schema.json](../../../schemas/design-homepage-benchmark-run.schema.json)
- Quality review example: [benchmark-quality-review.example.json](benchmark-quality-review.example.json)

Hash the definition, brief, source `SKILL.md`, every checkpoint, and every evidence artifact. Keep actual run bundles private. Do not commit third-party screenshots, private prototypes, approval records, or reviewer notes.

## Run phases

1. **Diagnose the creative pathway and freeze the run.** Ask whether to create new concepts from scratch, review an existing design, or refine a selected concept when the answer would change the work. Default to `fresh-concepts` when review or refinement was not explicitly requested. Record a hash-bound diagnosis with `default-fresh` or `explicit-user-instruction` basis and the known prior creative-artifact hashes used for reuse detection. Review and refinement additionally require the user's exact instruction, inherited design ID, and inherited artifact hashes. Then record the benchmark definition and brief hashes, source commit and skill hash, and one seed. Select exactly two references. Do not change the seed after directions are generated.
2. **Diagnose and research.** Run project doctor, inspect the supplied project context and implementation system, announce research, decompose both references, and retain private provenance.
3. **Generative exploration.** In the default fresh pathway, create new research, a new moodboard, a new generative laboratory, a new concept manifest, and a new comparison artifact. Do not reuse their hashes from a prior design or benchmark. Before web composition, build four-to-eight project-derived lenses and eight-to-twelve inexpensive seeds across at least three media, including image generation or editing. First declare a range plan spanning at least four art-direction families, three rendered typography strategies in three families, three composition families, four page grammars, three interaction or motion strategies, and five page-depth roles including opening, proof, closure, and a quiet or edge state. Create two-to-four style-frame alternatives for each promising generated family, explicitly select and reject variants, cross-pollinate at least two pairs, shortlist three-to-six seeds, and save the validated `generative-concept-laboratory` checkpoint. The checkpoint must report its laboratory hash and every range count.
4. **Precision reference translation.** Before full concept expansion, reconstruct each named source separately in responsive HTML/CSS. Complete two visual-difference correction passes, compile at least eight located and measured grammar constraints, build a literal Continuity substitution, and introduce one to four controlled divergence dimensions per candidate. Compare source, reconstruction, literal baseline, and adaptation at wide and narrow widths with a reviewer distinct from the preparer. Preserve real or generated source-defining media; hybridized baselines, self-certification, primary-material demotion, and primitive CSS substitution fail. Validate with `reference-validate` and save the precision-schema checkpoint with the translation hash and all ladder counts.
5. **Directions and pre-consultation quality gate.** A fresh benchmark always expands exactly three comparable-fidelity concepts; one-to-three remains available only for explicitly requested review or refinement. Require distinct typography, art direction, composition, page grammar, and interaction or motion systems, with at least two typography families. Every concept must bind one unique validated reference adaptation, a complete five-stage journey, its signature across three roles, full-page comparison coverage, generated-media disposition, and concept-specific mobile, tablet, and desktop probes. Run the actual native slop command; a JSON status stub is invalid. Then obtain a screenshot-bound quality review from a human or independent agent whose identity differs from the producer. The review must score at least 75, receive AI-slop grade A or B, clear every GStack-derived hard rejection, and name the user outcome, primary action, realistic product proof, and five-second reaction. Save the `concept-directions` checkpoint only after all three concepts pass.
6. **Native consultation.** Attach each selectable concept's consultation summary, concrete brand guideline, guideline hash, concept-evidence hash, and passed consistency record. The board leads with large comparable opening visuals, then keeps each concept's wide and narrow evidence beside its numbered feedback. Rationale and guideline detail remain progressively disclosed. The human may request refinement, more-like, remix, different directions, or mark a keep-only set ready. An agent may advise but cannot mark readiness. Material feedback and iteration requests advance the revision, require a real distinct before/after comparison, refresh affected evidence, and finish with a later human ready-for-selection round. Save the `design-consultation` checkpoint. Advisory preference is never selection.
7. **Human selection.** Present the ready directions without silently selecting. Record the human selection or combination and the `direction-selection` checkpoint. Evaluate with status `selected`.
8. **Private prototype.** Resolve only the selected direction. Retain desktop, tablet, mobile, interaction, reduced-motion, and accessibility evidence. Run browser probes, prototype validation, artifact critique, and the prototype slop gate. Evaluate with status `prototype-validated`.
9. **Exact design approval.** Present the exact design, visual-reference, selected brand-guideline, and approval-bundle hashes. Record only the user's explicit approval through Continuity. Add the `design-approval` checkpoint and evaluate with status `approved`. Stop `$continuity-design`; do not implement the homepage.
10. **Score outside the design process.** At least one identified human reviewer scores every original visual and product-quality dimension and dispositions every hard-failure rule with evidence. Consultation completeness and brand durability are mandatory gates, not points that can compensate for weaker design. Evaluate with status `scored`. Only a score of 75 or greater with no hard failure is benchmark-passing.

The evaluator validates evidence binding and stage completeness. It does not generate creative work, select a direction, approve a design, or manufacture reviewer judgment.

Treat informal visual explorations and legacy concept replays as `exploratory` runs in notes and reporting. They may diagnose the workflow, but they are not stage-valid fresh benchmark evidence unless the frozen run uses exactly two references and completes every checkpoint required for its claimed stage. Do not describe screenshots, a passed slop scan, an agent self-assessment, or a consultation board around inherited concepts alone as a benchmark pass.

## Seed strategy

Keep product truth, fixture data, constraints, deliverables, hard failures, and rubric fixed. Vary only audience, posture, hero mechanism, two references, and one edge case. For diversity testing, run six benchmark seeds and require at least four composition families, four art-direction families, four typography families, and three hero mechanisms across the batch. For reliability, repeat one unchanged benchmark seed three times. For sensitivity, change only one seed dimension.

## Evaluation

```bash
python scripts/evaluate_design_homepage.py \
  --source-root . \
  --run-root /path/to/private/run \
  --definition skills/continuity-design/references/continuity-homepage-benchmark.json \
  --manifest /path/to/private/run/run.json
```

The report separates `stage_valid`, `benchmark_passed`, and `merge_eligible`. A direction-stage run can be valid while correctly requiring human selection. Approval can be valid while correctly requiring an outside score. No intermediate state is described as a completed benchmark.

For iterative workflow development, bind this evaluation and its self-assessment into the [design improvement cycle](improvement-cycle.md). The cycle can resume deterministic work and preserve findings, but every pass stops for human judgment.
