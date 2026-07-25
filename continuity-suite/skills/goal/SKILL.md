---
name: goal
description: Turn one explicit user request into the fastest safe path to working code. Use for /goal, when the user asks to start or implement a task now, or when captured notes should be triaged, reflected in the roadmap, planned, and executed without separate routine handoff pauses.
---

# Goal

Use `/goal <request>` as the primary interactive entry point for action. One invocation is one durable authorization envelope for routine work inside the stated scope; it is not a request to stop after capture, triage, planning, approval, or dispatch.

Read [the learned playbook](references/learned-playbook.md), [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), the Continuity contract, the development assurance standard, `$continuity-local`, `AGENTS.md`, and the project configuration. Keep machine state authoritative, but make routine bookkeeping automatic and invisible to the user.

## Action-forward workflow

1. Run project doctor once and classify its findings by the action they protect. Configuration or managed-file drift, private-ledger corruption, an unsafe path, or an active conflicting code goal is a hard blocker. Scheduler registration, remote lease, verified-backup, external-checkpoint, and GitHub-auth readiness are advisory until this interactive run reaches the unattended or external operation they protect. `execution_enabled: false` disables scheduled and unattended dispatch, not an exact interactive `/goal` request. Routine missing context is not a blocker: inspect the repository and continue with the smallest faithful interpretation.
2. Inspect current code, relevant trusted memory, and the roadmap before drafting scope. Reuse current evidence and do not rerun unchanged checks merely to create another stop point.
3. Capture the request as one private source with semantically atomic notes. In the same run, triage every captured item:
   - promote the requested implementation as `explicit-instruction`;
   - route supporting facts and decisions to knowledge;
   - defer later ideas with a review date or roadmap anchor;
   - hold only a genuinely unresolved product decision.
4. Confirm actionable triaged items appear in `continuity roadmap inbox`. The private roadmap inbox is immediate planning visibility; committed roadmap records still change only through the goal's approved roadmap impact.
5. Create the smallest decision-complete goal. Set:
   - `authorization_mode: "goal-request"`
   - `risk_level: "routine"`
   - `restricted_side_effects: []`
   - `plan_reviewed: true`
   - `memory_reviewed: true`
   - exact source-note dispositions and only relevant memory and roadmap IDs.
6. Preserve the user's exact `/goal` request in a private temporary file and run:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal activate <goal-id> \
  --requested-by "<user identity>" \
  --request-file <exact-request.txt>
```

`goal activate` binds the exact request to the plan hash, records approval, performs the interactive preflight, dispatches the goal, and returns the execution prompt. Continue immediately into implementation. Do not ask for a second “approve” or “start now” decision.
7. Create or reuse the isolated goal worktree and code the approved scope. Run proportionate candidate checks while coding, then complete source-bound validation, security review, documentation/memory/roadmap impact, product conformance when applicable, and merge-safety evidence.
8. Return once with the implemented outcome, validation, remaining risks, and the next genuine human decision. A pull-request merge, deployment, publication, destructive action, new cost, credential use, private-data disclosure, or other restricted external side effect still requires its exact action-specific authority.

## When the envelope must stop

Do not use fast activation when the proposed plan contains an unresolved decision, material ambiguity, elevated or consequential risk, a restricted side effect, signed-approval policy, or scope beyond the user's request. Record `authorization_mode: "separate-approval"` or the appropriate higher risk, prepare the evidence, and ask only for the one decision that unlocks safe work.

During execution, continue without renewed approval for fixes, tests, formatting, generated-file refreshes, merge-conflict remediation, and other reversible work already inside scope. Renew authority only for material scope expansion, a higher risk ceiling, destructive or irreversible action, private-data disclosure, new cost, or a restricted external effect.

## Handoff

Use `continuity workflow status --goal-id <goal-id>` as a diagnostic and resumption record, not as a reason to yield between routine stages. Scheduled and unattended work continues to use `$continuity-workflow` and `$continuity-dispatch`; `/goal` is the optimized interactive path.
