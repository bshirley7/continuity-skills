---
name: continuity-execute
description: Execute one explicitly approved and dispatched project goal in an isolated worktree with alignment, developer review, Git, validation, security, memory-impact, roadmap-impact, evidence, and pull-request gates. Use only when a valid dispatch record identifies the goal and assigned task.
---

# Continuity Execute

Never execute a captured note, planning candidate, unapproved plan, or merely queued goal. Require a valid dispatch and matching approval hash.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the planning patterns](../../references/planning-patterns.md), `$continuity-local`, `.continuity/project.json`, `.continuity/config.json`, `AGENTS.md`, the approved plan, goal record, approval, cited memory and roadmap briefs, and compliance ledger.

## Required assurance

- Identify every touched language, framework, trust boundary, input, credential, data store, external action, and migration; apply the repository's current security and engineering guidance for each.
- Use least privilege, validated inputs, encoded outputs, parameterized data access, safe path confinement, subprocess argument arrays, secret-safe logging, pinned dependency workflows, and fail-closed error handling as applicable.
- Audit the complete diff for correctness, maintainability, tests, data integrity, compatibility, accessibility, performance, privacy, security, supply-chain risk, documentation, and rollback. Record reproducible commands and results; unsupported claims do not pass a gate.
- Stop on any scope expansion, stale approval, unsafe base state, conflict, validation failure, security finding, evidence gap, or assurance-version mismatch.

## Preflight

Run the deterministic preflight before implementation:

```text
.agents/continuity/bin/continuity --project-root "$PWD" execution preflight <goal-id>
```

Verify the isolated worktree, integration branch and remote base, scope, approval, dependencies, lock, PR path, runtime, and required commands. Stop on any failed gate.

## Responsible execution stages

1. Implement only approved scope using project architecture and developer best practices.
   Follow the approved delivery frontier: start only slices whose blockers are complete, and never interpret an unresolved decision-map item as implementation discretion.
2. Add focused tests and keep types, interfaces, migrations, compatibility, accessibility, performance, and privacy correct as applicable.
3. Record alignment checkpoints after major phases. Route discoveries into feedback or new candidates.
4. Apply `$continuity-test` for deliberate code review, configured validation, targeted regressions, configured security commands, and evidence-based security review.
5. Apply `$continuity-merge` to refresh or verify the integration branch, assess conflicts and mergeability, and rerun affected checks before PR handoff.
6. Record failures as findings, blockers, or partial completion instead of pushing them into review.
7. Update approved documentation, roadmap, and project memory; audit for drift and contradictions.
8. Reconcile the final result against notes, memory, roadmap, plan, acceptance criteria, and exclusions. Scan product artifacts to prove the roadmap sidecar remains excluded.
9. Record evidence in every compliance stage. A failed or pending gate prevents completion and review-ready status.

Use `goal gate`, `execution checkpoint`, and `run update` to record evidence. When recording `running`, provide the actual isolated `--worktree` and `--branch`. When completing, provide the PR URL, summary, and each report with `--artifact <absolute-path>`. Stop safely at the runtime limit.

## Delivery

Create `request-alignment.md`, `implementation-report.md`, `validation-and-security.md`, `memory-impact.md`, `roadmap-impact.md`, and `evidence.md`. Keep incomplete work in a draft PR. Mark review-ready only after `$continuity-test`, `$continuity-merge`, and all pre-human-review compliance stages pass. Never auto-merge or force-push.
