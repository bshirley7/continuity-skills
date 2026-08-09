# Design improvement cycle

Use the improvement cycle to repeat diagnose, change, benchmark, critique, and human-review passes without losing provenance or pretending that automation can judge taste conclusively. Declare the cycle mode explicitly when intent matters:

- `artifact-refinement` improves one selected or inherited design. Later passes require human-requested changes.
- `fresh-design-experiments` tests the workflow across independent designs. Every pass must begin from a new creative seed, reference-family set, moodboard, generative laboratory, concept set, and comparison artifact.

## Loop

1. Freeze the exact source branch, commit, skill hash, baseline benchmark evaluation, and baseline self-assessment.
2. Convert the self-assessment into atomic findings. Every finding needs an observation, a concrete workflow or craft action, and an observable success metric.
3. Implement only the findings selected for the pass. Bind each change to its finding IDs and exact changed artifacts.
4. Run source tests, the fixed homepage benchmark, AI-slop checks, and a fresh multimodal self-assessment. A validated pass requires a stage-valid benchmark and named passing source tests.
5. Stop at the human gate. The cycle may report `awaiting-human`; it cannot mark its own work accepted, select a direction, approve a design, merge a branch, or authorize implementation.
6. In `artifact-refinement`, wait for human-requested changes before another pass. In `fresh-design-experiments`, continue with an independent experiment while every prior design remains pending human review; do not treat the next experiment as acceptance or refinement of the previous one.
7. For fresh experiments, compare every new output with all prior outputs. Change at least five design dimensions, preserve only product-truth constraints, and record conclusions that could improve the workflow rather than the individual design.

Record and validate the loop with:

```bash
continuity design improvement-cycle --manifest <cycle.json>
```

The runtime is deliberately network-free. The creative agent may use research, browser capture, image generation, and multimodal review to create private evidence; the command validates hashes, sequence, novelty, results, and authority boundaries. In fresh-experiment mode it rejects reused briefs, research records, moodboards, laboratories, concept manifests, comparisons, creative seeds, and identical reference-family sets. Limit a cycle to eight passes so an unresolved creative disagreement becomes an explicit product decision rather than silent automation churn.

Automation is valuable for resuming state, rejecting stale evidence, running deterministic checks, and identifying the next gate. It is not evidence that the visual output improved. Keep human selection and approval exact, and use blinded paired review when making a material output-quality claim.
