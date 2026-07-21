# Prototype integrity

Use these rules whenever a design direction includes a prototype, representative content, multiple audiences, or a claim of implementation readiness.

## Content provenance

Classify material content as `inspected`, `supplied`, `inferred`, or `illustrative`. Keep a stable content ID, the statement, its source references when available, allowed uses, and any qualification that must travel with it.

- Require a source reference for inspected content.
- Qualify inferred and illustrative content explicitly.
- Treat fixture values as illustrative even when they look realistic.
- Never turn a plausible metric, testimonial, client result, queue count, or operational status into observed fact.
- Prefer representative content over placeholder filler, but preserve the distinction between realism and evidence.

## Audience architecture

Choose an explicit audience mode when needs differ materially:

- `shared-core`: one architecture serves common intent; name the common core.
- `differentiated`: shared foundations lead to two or more explicit routes with distinct needs.
- `unresolved`: the conflict is material but evidence is insufficient; state the conflict and provide provisional value without silently averaging it away.

## Prototype scope

State what the artifact demonstrates and omits. Use `directional` for an organizing idea, `behavioral` for bounded interaction evidence, and `implementation-facing` only when demonstrated surfaces and states are explicit and validation evidence is complete.

Fixture data, one successful path, or a polished responsive shell never proves workflow completeness. Name omitted error, empty, loading, offline, stale, permission, interruption, recovery, and destructive-action states when relevant.

## Validation matrix

Choose scenarios from the artifact and its risks. For responsive UI, normally include narrow and wide layouts, visible focus, keyboard-only operation, 200% zoom, long labels, localization expansion, reduced motion, realistic content, and all relevant states. Also test sticky or fixed actions for content obstruction and safe-area conflicts.

Record each scenario as `required`, `passed`, or `not-applicable`. A passed result needs evidence; a not-applicable result needs rationale. Do not label a prototype implementation-facing while required checks remain open.
