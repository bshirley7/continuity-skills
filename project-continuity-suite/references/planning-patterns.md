# Evidence Triage, Decision Mapping, and Delivery Slicing

Use these project-local patterns to improve planning quality without weakening the continuity authorization boundary.

## Selection

- Use evidence triage for a possible action whose claim, current behavior, overlap, or prior decisions need verification.
- Use a decision map when the destination is known but material product, architecture, research, or human decisions remain unresolved.
- Use delivery slices when an approved outcome contains multiple independently verifiable increments or dependency edges.
- Skip all three for retained context that does not warrant action. Record why a configured `required` pattern is not applicable only when the project contract permits it.

Project configuration controls each pattern with `disabled`, `auto`, or `required`. `auto` is the recommended default. Local artifacts are the default tracker surface.

## Evidence triage brief

Produce a durable, behavior-oriented brief that records:

- the note classification and claim status;
- current and desired behavior;
- concrete acceptance criteria and exclusions;
- evidence used to verify or contradict the claim;
- checks for an existing implementation and relevant prior decisions.

Use project domain language and stable interfaces. Avoid brittle line numbers and implementation recipes. A brief remains `execution_authorized: false` and can only become input to a goal plan.

## Decision map

Name one destination, then map only decisions that can be stated precisely now. Give each decision a stable ID, human-readable title, explicit question, status, and blockers. Keep unresolved territory separate from decisions that are ready to resolve, and keep out-of-scope work separate from both.

Resolve decisions into cited planning evidence. Do not use a decision-map task as permission to implement the destination. Human-required decisions remain blocked until the human answers; the agent must not impersonate the human side of the decision.

## Delivery slices

Slice an outcome into narrow end-to-end behaviors that are independently demonstrable or verifiable. Each slice records what it delivers, acceptance criteria, and only the dependencies that genuinely block it. The graph must be acyclic.

Prefer a complete vertical behavior over a layer-only task. For a wide migration that cannot stay valid as vertical slices, use expand, bounded migrations, and contract sequencing while keeping each safe checkpoint explicit.

Every slice remains `planning-candidate` and `execution_authorized: false`. The accepted graph is part of the parent goal's approval hash. Changing a slice or dependency requires a new plan version and approval.

## Tracker boundary

Keep maps, briefs, and slices in project-local private goal state by default. A configured GitHub or Linear provider indicates the preferred future publication surface; it does not authorize publication. Creating or modifying external tracker items requires a separate, explicit human approval describing the destination and intended changes.

## Provenance

These adapted patterns were informed by the MIT-licensed `wayfinder`, `triage`, and `to-tickets` skills in [mattpocock/skills](https://github.com/mattpocock/skills), reviewed at commit `66898f60e8c744e269f8ce06c2b2b99ce7660d5f`. This suite uses original continuity-specific contracts and implementation. The upstream skills are not bundled, invoked, or granted authority by this adaptation.
