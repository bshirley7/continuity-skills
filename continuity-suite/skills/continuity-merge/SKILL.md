---
name: continuity-merge
description: Assess PR readiness, merge safety, base freshness, human-review evidence, and post-review dispositions for Continuity goals. Use after the final tested commit is pushed to a draft PR, or when recording that a human approved, requested changes, merged, or closed a PR.
---

# Continuity Merge

Use this skill for merge-safety and human-review records. Continuity may assess readiness and record evidence, but it must not auto-merge, force-push, or infer human approval.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the testing and merge standard](../../references/testing-and-merge-standard.md), `$continuity-local`, `.continuity/config.json`, `AGENTS.md`, the approved plan, latest test report, and compliance ledger before acting.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [review and disposition](references/review-and-disposition.md) before assessment or human-review recording. Apply the **Evidence and confidence** and **Delivery and rollback** lenses; use the local disposition guide for the human boundary.

## Required assurance

- Require a passed Continuity test report before recording merge-safety as passed.
- Refresh or verify the integration base before PR handoff according to project policy.
- Confirm the branch is goal-focused, not the integration branch, and free of unrelated or private-state changes.
- Keep incomplete or blocked work in a draft PR with explicit blockers.
- Require successful configured GitHub checks before `review-ready`. Treat authenticated reviewer count and review decision as morning disposition gates, not as prerequisites for preparing the human handoff.
- Require authenticated GitHub human review and merge evidence. Never trust a caller-supplied identity by itself, auto-merge, force-push, or mark human review complete from agent judgment alone.

## Workflow

1. Run `continuity project doctor`.
2. Confirm the latest `$continuity-test` report passed for the current clean local commit, and that the same commit is pushed as the draft PR head.
3. Assess merge safety after hosted checks finish. The assessment verifies the PR head/base, merge state, unresolved change requests, configured check names, and every observed check result:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge assess <goal-id> \
  --worktree <execution-worktree> \
  --branch <goal-branch> \
  --pr-url <pull-request-url> \
  --evidence "<base refresh, diff, and PR readiness evidence>" \
  --update-gate
```

4. If the assessment fails, keep the PR draft or blocked and route unrelated follow-up into notes, roadmap, or a later goal.
5. If the assessment passes, hand off for human PR review. Completion may be review-ready, but merge remains a human action.
6. After human review, record exactly one disposition: `approved` leaves the goal `review-ready`; `changes-requested` archives the attempt, starts a fresh execution manifest, invalidates downstream evidence, and opens controlled rework; `merged` moves it to `completed`; `closed` cancels it. Fresh source-bound evidence is mandatory for `approved` and `merged`. Record `changes-requested` or `closed` even when delivery evidence is stale, preserving the stale-evidence reasons because neither disposition authorizes delivery.

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> \
  --pr-url <pull-request-url> \
  --merged-by "<human identity>" \
  --disposition <approved|changes-requested|merged|closed> \
  --merge-commit <sha-only-if-merged> \
  --evidence "<review or merge evidence>" \
  --signing-key <trusted-ssh-private-key>
```

Record only facts that happened. Every disposition in a signed-approval project requires an SSH receipt bound to the anchored trust store, exact goal, approved plan hash/version, execution attempt, actor, evidence, timestamp, and nonce. For `approved` or `merged`, the CLI also verifies the current `gh` identity, GitHub review decision, unique approving reviewer threshold, checks, PR base, and merge commit as applicable. If the human has not reviewed or merged, leave `human-review` pending.

## Handoff

Run `continuity workflow status --goal-id <goal-id>` on entry and exit. Human review and merge evidence determine the linked note's dated human-review, remediation, cancellation, or completion stage; do not write it independently. Follow only `allowed_actions`; report blocked actions without attempting them. Scope changes return to planning, and no disposition authorizes auto-merge.
