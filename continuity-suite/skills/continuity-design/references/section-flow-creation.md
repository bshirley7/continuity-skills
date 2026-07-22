# Creation

## Generalized principles

- Keep artifact identity, editable draft state, save or sync status, and consequential release state visibly distinct, using a review boundary before publish, activate, send, share broadly, deploy, or export.
- Maintain one selection and state model across structure, working surface or editor, properties, timeline, preview, and history so changes in one representation remain located and explainable in the others.
- Expose a valid starting model through blank, template, import, prompt, or existing-artifact paths, carrying inherited constraints and required first inputs into the workspace rather than presenting an unexplained empty surface.
- Attach validation to the exact field, node, step, asset, audience, or output setting that blocks progress, explain the consequence, and provide a direct route to repair before the release action.
- Make preview a faithful inspection mode for the selected audience, device, ratio, state, or execution path, and preserve a direct return to the same editable context without treating preview as proof that all release conditions pass.
- Provide persistent save state, undo and redo, history, or recoverable versions according to the cost of change, and distinguish submitted, processing, saved, autosaved, unsaved, published, and failed states.
- For automation and time-based artifacts, expose sequence, branching, timing, selected step, input data, execution mode, approval conditions, and test evidence so the user can predict what will happen and when.
- For generated artifacts, bind each output to its prompt, references, model, parameters, cost, transformations, and generation state so users can compare, reproduce, revise, and attribute differences.
- Reveal controls progressively by current selection, mode, and task while preserving stable access to structure, assets, properties, preview, and release; do not expose every control with equal prominence.
- At release, summarize output scope, audience or access, timing, quality, destination, ownership, restrictions, and irreversible or costly consequences, then show progress and a recoverable result state.

## Variation levers

- Use a single editor for linear content, a split preview for rendered pages, a spatial surface plus inspector for visual artifacts, and a working surface plus timeline for time-based work.
- Use manual save when explicit checkpoints matter, autosave for continuous low-risk editing, and named versions when comparison, rollback, or approval matters.
- Use templates when structure is repeatable, blank starts when expert control is primary, import when existing material should retain lineage, and prompting when generation is a bounded assistive path.
- Use inline preview for local changes and a dedicated preview mode when audience, device, state, or execution context must be simulated faithfully.
- Use local validation while editing, whole-artifact validation before review, and execution tests with representative inputs before activation.
- Use one-step release for reversible personal artifacts and staged review for public, costly, automated, regulated, or broadly shared outcomes.
- Use history as a list for linear revisions, a timeline for temporal media, and a configuration-linked gallery for generated outputs.
- Use contextual panels for selected-object properties and persistent global controls for identity, save state, preview, collaborators, and release.

## Tensions and tradeoffs

- Autosave reduces loss while making it harder to identify intentional checkpoints and undo broad changes.
- Live preview improves confidence while consuming workspace and suggesting greater fidelity than the preview can guarantee.
- Progressive controls reduce overload while hiding capabilities and making expert workflows slower.
- Templates accelerate starts while importing invisible assumptions, ownership, ratio, structure, or audience constraints.
- Generated assistance reduces effort while weakening provenance, reproducibility, and authorship clarity.
- Inline release actions preserve momentum while increasing the risk of accidental publication or activation.
- Rich history supports recovery while making current state, branches, and authoritative version harder to distinguish.
- One shared selection model improves coherence while becoming difficult across nested, temporal, conditional, or generated structures.

## Failure modes

- Draft, saved, syncing, published, active, and failed states are visually indistinguishable.
- The primary editor action publishes, activates, sends, or exports without a review boundary.
- The working surface, hierarchy, properties, timeline, and preview refer to different selections or versions.
- An empty workspace does not explain the valid first input or available starting paths.
- Validation appears only after release is attempted or points to no specific repair location.
- Preview hides a different audience, device, ratio, branch, or stale artifact state.
- Undo, history, or recovery cannot restore a meaningful prior artifact after a broad change.
- An automation test omits the input record, branch, timing, or approval condition used.
- A generated result loses the prompt, references, model, parameters, cost, or transformation lineage.
- Release omits destination, audience, access, timing, quality, ownership, restriction, or processing state.

## Anti-patterns

- Using Publish as the only way to save progress.
- Showing a green saved indicator while a release configuration remains invalid or stale.
- Treating preview as validation.
- Opening a generic error summary with no links to the blocking fields or nodes.
- Resetting the selected object, playhead, branch, or scroll position when a panel opens.
- Offering a blank working surface with every tool visible and no structural starting cue.
- Letting templates silently determine audience, ownership, ratio, access, or output destination.
- Storing generated outputs as a gallery without configuration lineage.
- Making automation activation visually equivalent to adding another draft step.
- Closing the editor during long-running export or generation without a durable job state.

## Acceptance and review questions

- Are artifact identity, draft state, save status, and release state visibly distinct?
- Is there an explicit review boundary before consequential publication, activation, sending, sharing, deployment, or export?
- Do structure, working surface, properties, timeline, preview, and history share one selection and version state?
- Does the workspace explain valid blank, template, import, prompt, or existing-artifact starting paths and their inherited constraints?
- Does each blocking validation issue identify the exact repair location and consequence?
- Does preview identify audience, device, ratio, state, branch, or execution path and return to the same edit context?
- Are saved, autosaved, unsaved, processing, published, failed, and recoverable states correctly distinguished?
- Can automation users inspect sequence, branching, timing, inputs, approval conditions, and test evidence before activation?
- Can generated outputs be reproduced or compared through attached prompt, references, model, parameters, cost, and transformations?
- Does release summarize destination, audience, access, timing, quality, ownership, restrictions, and processing outcome?
