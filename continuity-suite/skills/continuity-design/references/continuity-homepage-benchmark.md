# Continuity-Design homepage benchmark

Use this benchmark to test the complete `$continuity-design` process on one stable, demanding homepage problem. It evaluates process quality, design judgment, creative range, truthfulness, and finished craft. It does not authorize implementation and is not a substitute for the separate blinded paired-output benchmark.

## Fixed benchmark

- Definition: [continuity-homepage-benchmark.json](continuity-homepage-benchmark.json)
- Brief: [continuity-homepage-challenge.md](continuity-homepage-challenge.md)
- Run template: [continuity-homepage-benchmark-run.example.json](continuity-homepage-benchmark-run.example.json)
- Run schema: [design-homepage-benchmark-run.schema.json](../../../schemas/design-homepage-benchmark-run.schema.json)

Hash the definition, brief, source `SKILL.md`, every checkpoint, and every evidence artifact. Keep actual run bundles private. Do not commit third-party screenshots, private prototypes, approval records, or reviewer notes.

## Run phases

1. **Freeze the run.** Record the benchmark definition and brief hashes, source commit and skill hash, and one seed. Select exactly two references. Do not change the seed after directions are generated.
2. **Diagnose and research.** Run project doctor, inspect the supplied project context and implementation system, announce research, decompose both references, and retain private provenance.
3. **Generative exploration.** Before web composition, build four-to-eight project-derived lenses and eight-to-twelve inexpensive seeds across at least three media, including image generation or editing. First declare a range plan spanning at least four art-direction families, three rendered typography strategies in three families, three composition families, four page grammars, three interaction or motion strategies, and five page-depth roles including opening, proof, closure, and a quiet or edge state. Create two-to-four style-frame alternatives for each promising generated family, explicitly select and reject variants, cross-pollinate at least two pairs, shortlist three-to-six seeds, and save the validated `generative-concept-laboratory` checkpoint. The checkpoint must report its laboratory hash and every range count.
4. **Directions.** Cluster the laboratory into one-to-three comparable-fidelity concepts. Across a multi-concept set, require a distinct typography strategy, art-direction family, composition family, page grammar, and interaction or motion strategy for each concept, with at least two typography families. Every concept must define a complete journey of at least five stages, show its signature across at least three roles, include full-page comparison coverage, disposition generated media as extracted system rules, and carry its own mobile, tablet, and desktop runtime probes. It must pass the separate creative-range, multimodal impact, and native concept slop reviews. At least one concept must be judged compelling before selection. Save the `concept-directions` checkpoint and evaluate the manifest with status `directions`.
5. **Human selection.** Present the directions without silently selecting. Record the human selection or combination and the `direction-selection` checkpoint. Evaluate with status `selected`.
6. **Private prototype.** Resolve only the selected direction. Retain desktop, tablet, mobile, interaction, reduced-motion, and accessibility evidence. Run browser probes, prototype validation, artifact critique, and the prototype slop gate. Evaluate with status `prototype-validated`.
7. **Exact design approval.** Present the exact design, visual-reference, and approval-bundle hashes. Record only the user's explicit approval through Continuity. Add the `design-approval` checkpoint and evaluate with status `approved`. Stop `$continuity-design`; do not implement the homepage.
8. **Score outside the design process.** At least one identified human reviewer scores every weighted dimension and dispositions every hard-failure rule with evidence. Evaluate with status `scored`. Only a score of 75 or greater with no hard failure is benchmark-passing.

The evaluator validates evidence binding and stage completeness. It does not generate creative work, select a direction, approve a design, or manufacture reviewer judgment.

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
