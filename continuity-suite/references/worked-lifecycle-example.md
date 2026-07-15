# Worked Lifecycle Example

This synthetic example demonstrates information flow. It is not a command authorization template and names no real project, person, or organization.

## Source conversation

A stakeholder says that the current review screen is easy to scan, asks for status labels to be reorganized, and notes that label grouping has changed twice during the campaign. They want the next revision available for review the following morning.

## Capture

Split the conversation into three atomic items:

1. Positive feedback: the current review screen is easy to scan. Classify sentiment as positive, occurrence as feedback, and actionability as contextual.
2. Requested behavior: reorganize status labels. Use a conservative action-candidate kind until triage verifies intent and current behavior.
3. Repeated change: label grouping changed twice. Record the stated occurrence and an adaptability theme without describing the stakeholder's personality.

Each item keeps the source, `occurred_at`, capture time, qualifiers, and `execution_authorized: false`.

## Triage

- Route the positive feedback to knowledge so planning preserves scanability.
- Verify the current label behavior and create an evidence triage brief for the requested change.
- Route the repeated-change observation to pattern review. It may recommend a bounded configuration boundary, but does not require one.
- If “available tomorrow” is not explicit approval of an exact plan, retain it as timing context.

Handoff: exact note IDs, verified current and desired behavior, preservation requirement, uncertainty, and no authorization.

## Memory and roadmap

Memory retrieval finds a current design principle that dense operational screens must remain quickly scannable. Cite its exact memory ID and verification status.

Roadmap retrieval finds an objective for improving review efficiency. Cite its roadmap ID and current health. The requested label change supports that objective but does not alter the commitment by itself.

## Plan

Create one cohesive goal: reorganize status labels while preserving scanability. Apply the user, product, engineering, adaptability, and delivery lenses.

- Scope: label grouping behavior and focused regression coverage.
- Exclusions: redesigning the entire screen or introducing a general customization system without evidence.
- Decision: use the smallest existing configuration or component boundary that can absorb likely grouping changes.
- Note dispositions: the requested grouping change is `current-goal`; favorable scanability feedback is `context-only`; unrelated customization is `later` with a roadmap or review-date anchor.
- Acceptance: required statuses remain present, grouping matches the approved definition, scan order remains usable, and existing interactions continue to work.
- Validation: repository checks, targeted behavior tests, and visual evidence if configured.
- Rollback: revert the focused grouping change without data migration.

The goal remains `awaiting-feedback`. Timing context does not approve it.

## Approval and dispatch

A human reviews the exact plan version and approves it using the machine command. Approval queues the goal. Scheduled dispatch later verifies the same-date review, plan hash, dependencies, project lock, capacity, runtime, claim, and preflight before starting an isolated task.

## Execution and testing

Implementation changes only the approved label grouping boundary, adds focused tests, preserves scanability, and records checkpoints. Documentation, memory impact, roadmap impact, and all evidence artifacts are committed before the final test run.

The final machine test record binds the clean source fingerprint, approved plan, behavior configuration, commit, branch, and command set. The tested commit is pushed to a draft PR, then merge safety verifies local head, remote head, PR head, and base.

## Morning report

The report leads with the human decision:

- Subject: the exact goal and draft PR.
- State: `review-ready`, not completed.
- Result: label grouping changed; scanability behavior preserved; tests and security review passed.
- Evidence: plan version, test record, merge assessment, and PR.
- Allowed dispositions: only the commands returned by `workflow status`.

## Requested changes

If the human requests a different grouping within the approved behavior boundary, record `changes-requested` and require explicit resume through dispatch. The prior attempt is archived and downstream evidence becomes stale.

If the human instead requests user-configurable grouping, the scope has expanded. Return to planning, revise the goal, reassess architecture and security implications, and obtain fresh approval. Never treat either response as permission to auto-merge.

## Anti-example

“The stakeholder keeps changing their mind, so build a flexible label framework overnight” is invalid because it labels a person, invents scope, discards positive evidence, skips verification and approval, and turns a pattern into execution authority.
