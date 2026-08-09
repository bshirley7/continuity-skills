# Design improvement cycle

Use the improvement cycle to repeat diagnose, change, benchmark, critique, and human-review passes without losing provenance or pretending that automation can judge taste conclusively.

## Loop

1. Freeze the exact source branch, commit, skill hash, baseline benchmark evaluation, and baseline self-assessment.
2. Convert the self-assessment into atomic findings. Every finding needs an observation, a concrete workflow or craft action, and an observable success metric.
3. Implement only the findings selected for the pass. Bind each change to its finding IDs and exact changed artifacts.
4. Run source tests, the fixed homepage benchmark, AI-slop checks, and a fresh multimodal self-assessment. A validated pass requires a stage-valid benchmark and named passing source tests.
5. Stop at the human gate. The cycle may report `awaiting-human`; it cannot mark its own work accepted, select a direction, approve a design, merge a branch, or authorize implementation.
6. If the human requests changes, preserve the rationale and begin the next sequential pass. If accepted, end the cycle or open a newly scoped cycle.

Record and validate the loop with:

```bash
continuity design improvement-cycle --manifest <cycle.json>
```

The runtime is deliberately network-free. The creative agent may use research, browser capture, image generation, and multimodal review to create private evidence; the command validates hashes, sequence, results, and authority boundaries. Limit a cycle to eight passes so an unresolved creative disagreement becomes an explicit product decision rather than silent automation churn.

Automation is valuable for resuming state, rejecting stale evidence, running deterministic checks, and identifying the next gate. It is not evidence that the visual output improved. Keep human selection and approval exact, and use blinded paired review when making a material output-quality claim.
