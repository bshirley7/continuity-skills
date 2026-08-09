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
3. **Directions.** Save brief interpretation, reference synthesis, and one-to-three comparable-fidelity concept checkpoints. Run native concept slop checks. Evaluate the manifest with status `directions`.
4. **Human selection.** Present the directions without silently selecting. Record the human selection or combination and the `direction-selection` checkpoint. Evaluate with status `selected`.
5. **Private prototype.** Resolve only the selected direction. Retain desktop, tablet, mobile, interaction, reduced-motion, and accessibility evidence. Run browser probes, prototype validation, artifact critique, and the prototype slop gate. Evaluate with status `prototype-validated`.
6. **Exact design approval.** Present the exact design, visual-reference, and approval-bundle hashes. Record only the user's explicit approval through Continuity. Add the `design-approval` checkpoint and evaluate with status `approved`. Stop `$continuity-design`; do not implement the homepage.
7. **Score outside the design process.** At least one identified human reviewer scores every weighted dimension and dispositions every hard-failure rule with evidence. Evaluate with status `scored`. Only a score of 75 or greater with no hard failure is benchmark-passing.

The evaluator validates evidence binding and stage completeness. It does not generate creative work, select a direction, approve a design, or manufacture reviewer judgment.

## Seed strategy

Keep product truth, fixture data, constraints, deliverables, hard failures, and rubric fixed. Vary only audience, posture, hero mechanism, two references, and one edge case. For diversity testing, run six seeds and require at least four composition families and three hero mechanisms. For reliability, repeat one unchanged seed three times. For sensitivity, change only one seed dimension.

## Evaluation

```bash
python scripts/evaluate_design_homepage.py \
  --source-root . \
  --run-root /path/to/private/run \
  --definition skills/continuity-design/references/continuity-homepage-benchmark.json \
  --manifest /path/to/private/run/run.json
```

The report separates `stage_valid`, `benchmark_passed`, and `merge_eligible`. A direction-stage run can be valid while correctly requiring human selection. Approval can be valid while correctly requiring an outside score. No intermediate state is described as a completed benchmark.
