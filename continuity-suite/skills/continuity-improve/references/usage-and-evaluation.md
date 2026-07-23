# Usage And Evaluation

## What counts as usage evidence

Record a usage result only when the target skill and playbook hashes are known and the outcome has an inspectable basis. Suitable evidence includes machine workflow state, command exit status, test or audit records, explicit user correction, a documented retry, or a verified successful handoff. Agent confidence and user silence are not outcome evidence.

Use stable, reusable pattern keys. Prefer `report-false-completion`, `dispatch-empty-due-stop`, or `audit-missing-evidence` over project names, people, file paths, or prose copied from a session.

## Privacy boundary

Usage input is private but must still be sanitized. Summarize the reusable behavior and cite an opaque private evidence reference. Do not retain raw prompts, responses, tool arguments, tool output, note content, credentials, personal data, customer data, or absolute paths. `privacy_reviewed: true` is an assertion by the recording actor, not an automated guarantee.

## Evaluation corpus

Maintain three disjoint sets outside the generated proposal:

- training examples explain the recurring pattern and may guide candidate drafting;
- validation examples select among candidates;
- test examples provide the final untouched regression check.

Dreamed or synthetic cases may expand training coverage but must not enter validation or test. Keep case IDs stable across proposal iterations. If a case changes materially, version it instead of silently replacing it.

Scores use integer basis points from 0 to 10,000. Define the metric before running either base or candidate. A candidate must improve validation by at least the proposal threshold and may not score below the base playbook on test.

## Required invariants

Every proposal must test:

- `protected-contract-unchanged`: the installed `SKILL.md` hash remains exact;
- `authority-preserved`: the candidate cannot infer approval, execution authority, or human disposition;
- `privacy-preserved`: no private or sensitive content appears in output or artifacts;
- `state-accuracy-preserved`: claims and allowed actions match machine state and evidence.

Add skill-specific invariants when a workflow has higher-risk boundaries. Any failed required invariant rejects the candidate regardless of aggregate score.

## Promotion boundary

The improvement lifecycle produces a proposal package containing sanitized inputs, evaluation results, and a hash-bound review summary. The underlying reviewer identity, authorization text, and review evidence remain private. Packaging does not edit the installed playbook, modify suite source, create a goal, grant approval, authorize execution, publish a release, or update installations. Those remain separate Continuity actions with their normal evidence and human controls.
