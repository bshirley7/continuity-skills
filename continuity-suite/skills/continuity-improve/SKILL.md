---
name: continuity-improve
description: Learn from actual Continuity skill usage through private structured outcomes, recurring-pattern discovery, bounded learned-playbook proposals, fixed validation and test evaluation, protected invariants, and explicit human review. Use when a skill repeatedly succeeds, fails, needs correction, wastes steps, or should be refined from evidence without changing its protected contract.
---

# Continuity Improve

Improve installed Continuity skills from observed usage without letting usage rewrite authority. `SKILL.md` is the protected operational contract. Only `references/learned-playbook.md` is evolvable through this lifecycle, and even an accepted proposal remains non-authorizing until separately implemented through an approved suite-source goal.

Read [usage and evaluation](references/usage-and-evaluation.md), [the Continuity contract](../../references/continuity-contract.md), [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and the target skill before acting. Read [the learned playbook](references/learned-playbook.md) for validated guidance specific to this skill; it never overrides this file, CLI state, or human authority.

## Protected boundary

- Never rewrite an installed `SKILL.md`, authority rule, privacy rule, schema, required gate, or prohibited action from usage evidence.
- Never treat frequency, user silence, agent self-assessment, or a model preference as proof of improvement.
- Never copy raw transcripts, secrets, personal data, tool payloads, private note text, local paths, or credentials into usage records, proposals, evaluation artifacts, packages, messages, or commits.
- Never auto-adopt a learned playbook. Evaluation and human review produce a proposal package, not execution authority.
- Rejected proposals and negative outcomes remain evidence; do not repeatedly regenerate the same failed strategy without new evidence.

## Usage loop

1. Get the exact protected and evolvable hashes:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve baseline <skill-name>
```

2. After a meaningful outcome, create a sanitized record from [the usage example](references/usage.example.json). Bind it to objective evidence such as workflow status, a test report, a product audit, an explicit user correction, or a reproducible failure. Then record it privately:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve usage-record --input <usage.json>
```

3. Discover recurring successful and adverse patterns. A pattern is a learning candidate, never an instruction:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve patterns <skill-name> --min-count 2
```

## Proposal loop

1. Select evidence-backed pattern keys and exact usage IDs. Separate one-off project facts from reusable skill guidance.
2. Draft a complete candidate `learned-playbook.md`. Keep instructions general, testable, concise, and subordinate to the protected skill contract.
3. Create a bounded proposal from [the proposal example](references/proposal.example.json). Every add, replace, or delete operation must name its usage evidence, expected outcome, validation cases, untouched test cases, and protected invariants.
4. Stage the proposal privately:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve propose \
  --input <proposal.json> \
  --candidate <candidate-learned-playbook.md>
```

The CLI rejects stale skill or playbook hashes, unknown usage evidence, unbacked patterns, excessive edits, missing invariants, unchanged candidates, and candidate text that attempts to weaken protected controls.

## Evaluation and review

1. Run the base and candidate playbooks on fixed validation and test cases. Validation may select the candidate; test cases remain untouched until the final gate. Score observable task success, state accuracy, evidence completeness, privacy, corrections, retries, tool failures, and cost only when each metric has a stable definition.
2. Record the result from [the evaluation example](references/evaluation.example.json):

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve evaluate <proposal-id> \
  --result-file <evaluation.json>
```

The candidate passes only when validation improves by the proposal threshold, the test score does not regress, all required invariants pass, and no regression is recorded.

3. Inspect the proposal, candidate, per-case evidence, failures, and gate arithmetic:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve show <proposal-id>
```

4. A human may approve, reject, or hold the evaluated proposal. Approval is review evidence, not implementation authority:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve review <proposal-id> \
  --disposition <approved|rejected|held> \
  --actor <human-identity> \
  --authorization-text "<exact review text>" \
  --evidence "<review evidence>"
```

5. Package only an accepted and human-approved proposal. The package binds the private review record by hash and omits reviewer identity, authorization text, and review evidence:

```text
.agents/continuity/bin/continuity --project-root "$PWD" improve package <proposal-id> \
  --output <project-relative-output-directory>
```

Apply a package only through a separately approved Continuity goal in the suite source, then rerun skill validation, full tests, release-manifest generation, and applicable product audits. Monitor later usage by exact released skill and playbook hashes; supersede or revert guidance when new evidence shows regression.

## Handoff

Report the target skill, usage and pattern IDs, protected and candidate hashes, validation and test movement, invariant results, regressions, human disposition, package path when present, and the exact separately authorized next action. Never report a staged, accepted, reviewed, or packaged proposal as installed or released.
