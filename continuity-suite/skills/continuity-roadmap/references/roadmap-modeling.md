# Roadmap Modeling

Read this reference when selecting hierarchy, recording dependencies or health, linking notes and goals, or describing structured roadmap impact.

## Modeling levels

- **Objective:** express a top-level measurable or observable outcome in a `program` title and summary, or in an `initiative` beneath a program; `objective` is a planning concept, not a roadmap `kind`.
- **Campaign:** model a top-level campaign as a `program` or a bounded campaign beneath it as an `initiative`; `campaign` is not a roadmap `kind`.
- **Milestone:** a reviewable commitment or capability boundary.
- **Release:** a delivery boundary with readiness and rollback implications.
- **Work item:** a bounded contribution; it does not replace a Continuity goal or authorize execution.

Use only the levels needed by the project configuration. Do not create hierarchy to make a small objective appear more complete.

Supported kinds are `program`, `initiative`, `release`, `milestone`, `epic`, `story`, `bug`, `spike`, `chore`, and `sprint`.

## Relationship rules

- `supports`: evidence or work contributes to an existing roadmap outcome.
- `blocks`: the source prevents progress until resolved.
- `contradicts`: evidence conflicts with the current roadmap assumption.
- `updates`: an approved goal changes canonical roadmap truth.
- `suggests`: a note proposes consideration without commitment.

Private links influence review and projection but do not mutate committed roadmap records.

## Health lens

Health must cite evidence. Describe scope confidence, dependency state, decision state, delivery evidence, and risk rather than using an unexplained color or percentage. A milestone with no recent activity may still be healthy; a recently active milestone may be blocked by an unresolved decision.

## Impact examples

Good: “Goal OBJ-14 supports milestone RM-07. On successful human merge, update RM-07 validation evidence and leave its target date unchanged.”

Bad: “Mark the roadmap item complete because implementation started.”

Use `none` when work does not alter canonical roadmap truth, and explain why. A goal may cite roadmap context without requiring a roadmap edit.

## Handoff checklist

- Exact roadmap IDs and canonical paths are cited.
- Hierarchy and dependency edges are valid and acyclic where required.
- Commitment, proposal, local projection, and private note evidence are distinct.
- Structured impact names the intended action and timing.
- Planning receives current health and contradictions.
- Execution receives only impact already present in the approved goal hash.
