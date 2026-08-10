# Native AI-slop gate

Run `continuity design slop-check --target <file-or-directory> --manifest <manifest.json>` at concept, prototype, and implementation stages. The scanner is deterministic, standard-library only, and network-free. It combines source inspection with agent-supplied rendered-artifact and project-context findings.

This gate does not prove creative range. Run the generative concept laboratory and its creative-range review first. A concept may be free of known slop and still be timid, repetitive, or generic.

## Decision model

- Hard failures and project drift block the stage until the detected condition is absent. They cannot be accepted or marked not applicable.
- Every default-risk warning must be resolved by changing the artifact, marked not applicable with rationale and evidence, or accepted as intentional.
- Intentional acceptance must use the hash-bound `craft_findings` shape with a project rationale and design-contract reference.
- Inline comments and free-form suppression markers have no authority.
- Patterns are not universal bans. The gate detects unexplained defaults; evidenced, approved use remains possible.

Findings emit a stable rule ID, class, severity, location, evidence, and remediation. The report binds its ruleset, scanned file hashes, finding dispositions, structured visual-review answers, hashed PNG evidence regions, stage, and final status.

## Hard failures

- Audible autoplay.
- Motion-heavy or WebGL output without reduced-motion and static fallbacks.
- Primary content hidden until JavaScript or animation succeeds.
- `transition: all`, unbounded raw scroll work, or equivalent hazards.
- Approved contract drift.
- Unqualified generated or illustrative claims.
- Third-party reference imagery promoted as a product asset.
- Presentation claims, metrics, testimonials, customers, traction, or performance assertions without current provenance and visible qualification.
- Presentation evidence whose encoded media type, dimensions, viewport, or frame identity does not match its manifest.

## Default-risk reflexes

Review unexplained purple-to-blue gradients, gradient headlines, warm cream, common model-default type, decorative glass, uniform rounded containers, bento grids, repeated eyebrows, meaningless numbering, excessive centering, fade-up repetition, hero metrics, decorative glows, stock imagery, generic promotional copy, em-dash cadence, and the fashionable black-neon terminal counter-default.

Also review translation collapse: source-defining media replaced by primitive CSS decoration, loss of defining scale or material energy, convergence on a familiar hero-and-sections template, declared mechanics absent from the render, and useful generated studies discarded without an equivalent translation. Ruleset 1.4 additionally detects primary material demoted to a copy backdrop, substituted typographic grammar, flattened compositional depth, unverified typographic character, hybrid references without exact individual baselines, self-certified fidelity, incomplete narrow comparison, weak visible lineage, unresolved type contrast over variable imagery, stale portfolio reviews, excessive house-style overlap, an unchallenged strongest prior, supporting-only media, collapsed close/far distance, unresolved reference difficulty, hero-only journey evidence, collapsed approved asset planes, and lost approved typographic character.

Ruleset 1.5 adds presentation-specific review for repeated title-and-body templates, fewer than four structural slide roles, missing narrative peaks, missing quiet or rest states, collapsed projected and read-ahead modes, unsupported deck claims, and invalid capture evidence. These rules apply only when `presentation_fidelity` is supplied; a web page is not treated as a presentation merely because it uses sections.

## Project drift

Review unapproved tokens or patterns, a signature that disappears beyond the hero, reference imitation without transformation, reintroduced rejected choices, component-library retreat, Continuity house tells that dominate the approved project identity, and loss of a mechanic already passed by the reference-translation gate.

Supply deterministic context markers in `project_context`: `unapproved_markers`, `required_signature_markers`, `reference_transformations`, `rejected_choices`, and `continuity_house_tells`. These are literal contract-derived markers, not arbitrary regex suppressions. Add rendered judgments that cannot be expressed as markers to `context_findings` with a stable project-drift rule ID.

Supply `portfolio_diversity` booleans for the current portfolio audit, house-overlap limit, strongest-prior challenge, concept-forming media, close/far distance, reference-class difficulty, and journey/state depth. For reference-led concepts, also supply `translation_fidelity` booleans for editable depth, verified font transfer, the approved layer plan, and approved typographic character. A false approved-state value emits blocking project drift; omitting these fields is supported only for legacy workflow records.

For presentation or pitch-deck work, supply `presentation_fidelity`: measured slide-role count, repeated-template ratio, narrative-peak and quiet-state evidence, separate live-presentation and read-ahead reviews, claim provenance, and capture-integrity verification. Build contact sheets from verified individual frames. Do not trust a scrolling full-page stitch when slide snapping, sticky frames, or transforms can duplicate or omit slides.

## Required visual review

Answer all eight questions in `visual_review`. Each answer requires `result`, `reviewer`, `reviewed_at`, and one or more hashed PNG evidence objects with a named region. A failed answer requires a finding and automatically creates the mapped slop finding. An unsupported prose assertion is invalid.

1. Can the signature be identified within five seconds?
2. Does the identity remain project-specific when the product name is removed?
3. Does it avoid both the category default and its fashionable opposite?
4. Are concepts structurally distinct rather than cosmetically varied?
5. Does implementation avoid retreating to library defaults?
6. Does the signature survive mobile, quiet, error, and reduced-motion states?
7. Is a reference mechanic transformed rather than its identity copied?
8. Does every decorative choice perform a necessary job?

Use `critical`, `error`, `warning`, and `info` proportionally. Re-run the gate whenever a source file, visual reference, design hash, approval bundle, or affected feedback decision changes.

For workflow-v3 concepts, visual answers are necessary but not sufficient. `concept-validate` separately requires browser-measured signature coverage across opening, proof, interaction, quiet-or-edge, and closure, including initial desktop and mobile visibility, plus protected interaction semantics captured before and after a material state change. A self-authored `pass` cannot override a missing carrier or a changed authority label.
