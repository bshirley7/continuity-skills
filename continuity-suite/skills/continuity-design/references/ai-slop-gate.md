# Native AI-slop gate

Run `continuity design slop-check --target <file-or-directory> --manifest <manifest.json>` at concept, prototype, and implementation stages. The scanner is deterministic, standard-library only, and network-free. It combines source inspection with agent-supplied rendered-artifact and project-context findings.

## Decision model

- Hard failures and project drift block the stage.
- Every default-risk warning must be resolved with evidence, marked not applicable, or accepted as intentional.
- Intentional acceptance must use the hash-bound `craft_findings` shape with a project rationale and design-contract reference.
- Inline comments and free-form suppression markers have no authority.
- Patterns are not universal bans. The gate detects unexplained defaults; evidenced, approved use remains possible.

Findings emit a stable rule ID, class, severity, location, evidence, and remediation. The report binds its ruleset, scanned file hashes, finding dispositions, visual-review answers, stage, and final status.

## Hard failures

- Audible autoplay.
- Motion-heavy or WebGL output without reduced-motion and static fallbacks.
- Primary content hidden until JavaScript or animation succeeds.
- `transition: all`, unbounded raw scroll work, or equivalent hazards.
- Approved contract drift.
- Unqualified generated or illustrative claims.
- Third-party reference imagery promoted as a product asset.

## Default-risk reflexes

Review unexplained purple-to-blue gradients, gradient headlines, warm cream, common model-default type, decorative glass, uniform rounded containers, bento grids, repeated eyebrows, meaningless numbering, excessive centering, fade-up repetition, hero metrics, decorative glows, stock imagery, generic promotional copy, em-dash cadence, and the fashionable black-neon terminal counter-default.

## Project drift

Review unapproved tokens or patterns, a signature that disappears beyond the hero, reference imitation without transformation, reintroduced rejected choices, component-library retreat, and Continuity house tells that dominate the approved project identity.

Supply deterministic context markers in `project_context`: `unapproved_markers`, `required_signature_markers`, `reference_transformations`, `rejected_choices`, and `continuity_house_tells`. These are literal contract-derived markers, not arbitrary regex suppressions. Add rendered judgments that cannot be expressed as markers to `context_findings` with a stable project-drift rule ID.

## Required visual review

Answer all eight questions in `visual_review`:

1. Can the signature be identified within five seconds?
2. Would changing the product name make the design fit an unrelated company?
3. Is it the category default or its fashionable opposite?
4. Are concepts structurally distinct rather than cosmetically varied?
5. Did implementation retreat to library defaults?
6. Does the signature survive mobile, quiet, error, and reduced-motion states?
7. Is a reference mechanic transformed rather than its identity copied?
8. Does every decorative choice perform a necessary job?

Use `critical`, `error`, `warning`, and `info` proportionally. Re-run the gate whenever a source file, visual reference, design hash, approval bundle, or affected feedback decision changes.
