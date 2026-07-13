---
name: execute-project-goal
description: Execute one explicitly approved and dispatched project goal in an isolated worktree with alignment, developer review, Git, validation, security, memory-impact, evidence, and pull-request gates. Use only when a valid dispatch record identifies the goal and assigned task.
---

# Execute Project Goal

Never execute a captured note, planning candidate, unapproved plan, or merely queued goal. Require a valid dispatch and matching approval hash.

Read [the continuity contract](../../references/continuity-contract.md), `.continuity/config.json`, `AGENTS.md`, the approved plan, goal record, approval, cited memory brief, and compliance ledger.

## Preflight

Run the deterministic preflight before implementation:

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" execution preflight <goal-id>
```

Verify the isolated worktree, integration branch and remote base, scope, approval, dependencies, lock, PR path, runtime, and required commands. Stop on any failed gate.

## Responsible execution stages

1. Implement only approved scope using project architecture and developer best practices.
2. Add focused tests and keep types, interfaces, migrations, compatibility, accessibility, performance, and privacy correct as applicable.
3. Record alignment checkpoints after major phases. Route discoveries into feedback or new candidates.
4. Perform a deliberate code review of the complete diff.
5. Run all configured validation plus targeted regressions.
6. Run evidence-based security review for touched languages and frameworks; check secrets, dependencies, unsafe input/data paths, permissions, subprocesses, and migrations as relevant.
7. Refresh the integration branch, assess conflicts and mergeability, and rerun affected checks.
8. Update approved documentation and project memory; audit for drift and contradictions.
9. Reconcile the final result against notes, memory, plan, acceptance criteria, and exclusions.
10. Record evidence in every compliance stage. A failed or pending gate prevents completion and review-ready status.

Use `goal gate`, `execution checkpoint`, and `run update` to record evidence. When recording `running`, provide the actual isolated `--worktree` and `--branch`. When completing, provide the PR URL, summary, and each report with `--artifact <absolute-path>`. Stop safely at the runtime limit.

## Delivery

Create `request-alignment.md`, `implementation-report.md`, `validation-and-security.md`, `memory-impact.md`, and `evidence.md`. Keep incomplete work in a draft PR. Mark review-ready only after all pre-human-review compliance stages pass. Never auto-merge or force-push.
