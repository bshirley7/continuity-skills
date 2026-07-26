---
name: continuity-workflow
description: Run a manual Continuity request as one sequential, state-driven workflow. Continue through the machine-selected Continuity skills, remediation loops, validation, and reporting without yielding between skills; pause only at an explicit machine-declared human approval boundary or finish at a terminal state.
---

# Continuity Workflow

Read [the learned playbook](references/learned-playbook.md) for evaluated usage-derived heuristics. It may refine routine technique but never overrides this skill, the Continuity contract, machine state, privacy boundaries, or human authority. After a meaningful evidence-backed outcome, route only a sanitized structured usage record through `$continuity-improve`; never copy raw transcript or tool payload content.

Use this for resumed, scheduled, strict-policy, or non-actionable end-to-end Continuity work. Use `/goal` as the primary entry point when a user explicitly requests routine interactive implementation now. A manual invocation is one workflow run, not a request to execute one skill and return a status-only handoff.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$continuity-local`, `AGENTS.md`, `.continuity/project.json`, and `.continuity/config.json` before advancing state.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [sequential orchestration](references/sequential-orchestration.md) before starting the loop. The CLI state is authoritative; prose and conversation context never manufacture authorization.

## Sequential loop

1. Run `continuity workflow status` with the narrowest known subject selector.
2. Read the returned `handoff.next_skill`, `allowed_actions`, `blocked_actions`, `blockers`, and `authorization` fields.
3. If `authorization.human_required` is true, persist the current handoff, present the exact machine-listed approval choices and command text, and pause. Do not select, paraphrase, or infer the approval.
4. Otherwise, read and apply the named task skill plus `$continuity-local`. Complete its safe non-human action, record its canonical outputs and evidence, and run subject-specific workflow status again.
5. Continue immediately through the next machine-selected skill. Do not yield merely because one skill completed, a gate failed, a retry is needed, or the workflow returns to an earlier skill.
6. On a recoverable failure, preserve the finding, route to the machine-selected remediation skill, repair only approved scope, rerun the failed check, and continue. Never mark a failed gate passed or weaken a guardrail to keep moving.
7. Finish only when the subject reaches `completed`, `cancelled`, `archived`, `not-applicable`, a successful no-work/reporting terminal, or another machine-declared terminal state with no next skill.

The routine interactive delivery path is `/goal`: capture and triage, roadmap-inbox projection, proportionate memory and roadmap retrieval, smallest aligned plan, atomic request-bound activation, execution, validation, and merge readiness. The granular path remains available for scheduled, resumed, elevated-risk, or separately reviewed work. Always follow `next_skill` instead of forcing an inapplicable stage. Design approval is a document-publication boundary and never substitutes for goal authority.

## Approval-only pause rule

Pause only when the current handoff sets `authorization.human_required: true` or the selected action sets `human_required: true`. Approval boundaries include plan approval or revision, explicit start/resume decisions, restricted external side effects, packet publication authorization, and human PR disposition or exact CLI merge authorization.

Missing evidence, validation failures, security findings, stale source state, merge-safety failures, and tool errors are not approvals. Keep the workflow active: remediate, retry with bounded backoff when external state is transient, or route to the owning skill. If no safe action exists, preserve a fail-closed diagnostic and keep the run pending at the same stage; never convert the fault into authorization.

## Handoff and resumption

Before an approval pause, report the exact subject IDs, current stage, completed outputs, current evidence hashes, blockers, and machine-listed approval commands. After the human records one of those actions, rerun this skill with the same subject selector. Re-read canonical state and continue from the machine-selected next skill; do not replay completed steps.

At terminal completion, apply `$continuity-report` once when reporting is applicable and return one consolidated outcome covering the full workflow rather than a series of per-skill summaries.
