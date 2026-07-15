# Goal Planning Lenses

Read this reference for every goal proposal. Apply only the sections triggered by the objective and record unresolved material decisions instead of guessing.

For a complete input accepted by `goal create --goal-file`, see [goal-input.example.json](goal-input.example.json). It uses synthetic evidence and remains non-authorizing until a human separately approves the created plan version.

## Outcome review

- Name one cohesive business or operational outcome.
- Explain current versus desired behavior and why the work is valuable now.
- Preserve favorable feedback and successful behavior as explicit non-regression constraints.
- Define what is outside the goal and what would require a separate objective.

## Decision review

For each material decision, record the question, selected answer, evidence, owner, status, and affected slices. Human-required decisions block only the dependent frontier. Do not hide a decision in an implementation step.

## Engineering review

- Cite established architecture, interfaces, data ownership, and repository instructions.
- Identify dependencies, compatibility, migration, accessibility, performance, privacy, and security concerns as applicable.
- Prefer the smallest abstraction justified by current evidence.
- When repeated changes exist, identify a bounded adaptability point and explain why broader flexibility is excluded.

## Delivery review

- Use end-to-end slices that are independently verifiable.
- State acceptance criteria as observable behavior or reproducible evidence.
- Name candidate and final validation, security review, rollout, rollback, and stop conditions.
- State unattended suitability, runtime, restricted side effects, and human checkpoints.
- Keep external tracker publication separate from planning and execution authority.

## Note disposition review

Every source note must have one machine disposition and a concrete reason:

- `current-goal`: required by current scope; list affected delivery slices when present.
- `later`: excluded from current scope; require either an ISO review date or a retrieved roadmap ID.
- `context-only`: informs decisions or constraints but does not adopt execution state.
- `duplicate`: name the canonical note; preserve provenance without creating duplicate work.

The plan renders and hashes these dispositions. Moving a note into or out of current scope requires `goal revise` and fresh approval. `planned` means awaiting approval or delivery; only a canonical `running` transition means work is in progress.

## Goal quality example

Good: “Reorganize status labels within the existing review component while preserving scanability. Exclude user-defined layouts. Verify required labels, grouping order, keyboard behavior, and the repository's standard checks.”

Weak: “Improve labels and make the component flexible.” The outcome, boundary, evidence, acceptance, and justified flexibility are unclear.

## Handoff checklist

- Source note IDs are currently eligible.
- Triage brief verifies current and desired behavior.
- Exact current memory and roadmap IDs are cited.
- One outcome, scope, exclusions, dependencies, and decisions are explicit.
- Slices are acyclic and independently verifiable.
- Every source note has one complete disposition, and later work has a durable follow-up anchor.
- Acceptance, validation, security, rollout, rollback, evidence, and documentation impact are complete.
- The goal is `awaiting-feedback`; planning has not generated approval text.
