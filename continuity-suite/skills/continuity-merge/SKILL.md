---
name: continuity-merge
description: Assess PR readiness, merge safety, base freshness, human-review evidence, and post-review dispositions for Continuity goals. Use after the final tested commit is pushed to a draft PR, or when recording that a human approved, requested changes, merged, or closed a PR.
---

# Continuity Merge

Use this skill for merge-safety and human-review records. Continuity may assess readiness and record evidence, but it must not auto-merge, force-push, or infer human approval.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the testing and merge standard](../../references/testing-and-merge-standard.md), `$continuity-local`, `.continuity/config.json`, `AGENTS.md`, the approved plan, latest test report, and compliance ledger before acting.

## Required assurance

- Require a passed Continuity test report before recording merge-safety as passed.
- Refresh or verify the integration base before PR handoff according to project policy.
- Confirm the branch is goal-focused, not the integration branch, and free of unrelated or private-state changes.
- Keep incomplete or blocked work in a draft PR with explicit blockers.
- Require explicit human review and merge evidence. Never auto-merge, force-push, or mark human review complete from agent judgment alone.

## Workflow

1. Run `continuity project doctor`.
2. Confirm the latest `$continuity-test` report passed for the current clean local commit, and that the same commit is pushed as the draft PR head.
3. Assess merge safety:

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
  --evidence "<review or merge evidence>"
```

Record only facts that happened. If the human has not reviewed or merged, leave `human-review` pending.

## Handoff

Run `continuity workflow status --goal-id <goal-id>` on entry and exit. Follow only `allowed_actions`; report `blocked_actions` and their evidence failures without attempting them. `changes-requested` returns to `$continuity-dispatch` for explicit in-scope resume or `$continuity-plan` for scope revision; no review disposition authorizes auto-merge.
