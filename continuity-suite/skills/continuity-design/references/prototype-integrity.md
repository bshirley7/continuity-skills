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

For React and React-based web work, `complete-prototype` is the default unless the user explicitly asks for exploration only. Inspect the configured framework, styling and token systems, installed UI, motion, data, and icon libraries, component roots, preview harnesses, and asset roots. Record only evidenced capabilities. Map each material experience need to `reuse`, `compose`, `extend`, `custom`, or `missing-capability`; a UI library provides behavior and semantics but must not silently determine the finished expression.

A complete prototype contains a coherent representative page or smallest complete workflow, representative labeled content, relevant states, an explicit asset strategy, and desktop, tablet, and mobile compositions. It remains under `.continuity/private/`, outside production routes and build inputs. It does not authorize dependency installation or application changes.

For a media-led prototype, record supplied media as an asset with source provenance and actual metadata. Bind observable media beats to standalone chapters, direct navigation, reduced-motion and no-video equivalents, and a credible final action. Demonstrate loading, buffering, failure, interruption, reverse navigation, mobile recomposition, and the quiet static carrier. A polished poster frame or successful forward scrub does not prove the joined film-and-interface experience.

## Validation matrix

Choose scenarios from the artifact and its risks. For responsive UI, normally include narrow and wide layouts, visible focus, keyboard-only operation, 200% zoom, long labels, localization expansion, reduced motion, realistic content, and all relevant states. Also test sticky or fixed actions for content obstruction and safe-area conflicts.

Record each scenario as `required`, `passed`, or `not-applicable`. A passed result needs evidence; a not-applicable result needs rationale. Do not label a prototype implementation-facing while required checks remain open.

## Artifact assurance

Bind each HTML and PNG to the exact approved design through a project-relative artifact manifest. Put the design ID, revision, design hash, maturity, and fixture status in HTML metadata; hash every artifact file; and record screenshot roles.

Map each material design claim to a demonstrated artifact file or HTML anchor, or mark it omitted. Attach the relevant decided insight IDs to those claims. An implementation-facing artifact must demonstrate every decided insight; provisional and omitted insights remain visible without being misrepresented as implemented. For differentiated audiences, demonstrate every audience route before claiming implementation readiness. A description of a route in `design.md` is not evidence that its interface exists.

For responsive HTML, run [artifact-browser-probe.js](../scripts/artifact-browser-probe.js) at desktop and mobile viewports through the available browser automation tool. Store the returned JSON as validation evidence, capture both screenshot roles, and record `horizontal-overflow` and `sticky-action-obstruction` results.

Before approval, run `continuity design prototype-validate --manifest <manifest.json>` against the selected private draft. Complete the artifact-critique pass and revise the design when rendered evidence exposes drift, incompleteness, library-default leakage, weak asset treatment, poor type or spacing craft, or an interchangeable signature. After exact approval, run `continuity design artifact-validate --manifest <manifest.json>` against the canonical record. Treat failures, missing audience routes, unlabeled fixtures, missing required validation or probe results, absent required responsive screenshots, incomplete states, pending critique, and unbound design claims as readiness blockers. Validation never authorizes implementation.
