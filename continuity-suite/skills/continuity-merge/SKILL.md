---
name: continuity-merge
description: Assess PR readiness, merge safety, base freshness, human-review evidence, and post-review dispositions for Continuity goals. Use after the final tested commit is pushed to a draft PR, or when recording that a human approved, requested changes, merged, or closed a PR.
---

# Continuity Merge

Use this skill for merge-safety, exact interactive merge authorization, and human-review records. Continuity must not auto-merge, use administrator bypass, force-push, or infer human approval. A project may opt in to a direct GitHub CLI merge only when a human supplies the exact PR-, head-SHA-, and method-bound authorization in an interactive agent session.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the testing and merge standard](../../references/testing-and-merge-standard.md), `$continuity-local`, `.continuity/config.json`, `AGENTS.md`, the approved plan, latest test report, and compliance ledger before acting.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [review and disposition](references/review-and-disposition.md) before assessment or human-review recording. Apply the **Evidence and confidence** and **Delivery and rollback** lenses; use the local disposition guide for the human boundary.

## Required assurance

- Require a passed Continuity test report and current passed or explicitly not-applicable product-conformance gate before recording merge-safety as passed.
- Refresh or verify the integration base before PR handoff according to project policy.
- Confirm the branch is goal-focused, not the integration branch, and free of unrelated or private-state changes.
- Keep incomplete or blocked work in a draft PR with explicit blockers.
- Require successful configured GitHub checks before `review-ready`. Treat authenticated reviewer count and review decision as morning disposition gates, not as prerequisites for preparing the human handoff.
- Require authenticated GitHub human review and merge evidence. Never trust a caller-supplied identity by itself, auto-merge, use `--admin`, force-push, or mark human review complete from agent judgment alone.

## Workflow

1. Run `continuity project doctor`.
2. Confirm the latest `$continuity-test` report and `$continuity-product-audit` candidate record passed for the current clean local commit, or that product conformance is explicitly not applicable. Confirm that the same commit is pushed as the draft PR head.
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
6. When `.continuity/config.json` has `github_cli_merge_enabled: true`, an interactive human may authorize and execute the exact assessed PR head without opening GitHub. Copy the full head SHA and use authorization text that exactly matches the command contract:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge execute <goal-id> \
  --pr-url <pull-request-url> \
  --head-sha <full-40-character-head-sha> \
  --merge-method <merge|squash|rebase> \
  --authorized-by <authenticated-github-login> \
  --authorization-text "Merge <goal-id> PR <pull-request-url> at <full-40-character-head-sha> using <merge-method>"
```

The command rechecks the open non-draft PR, base, exact head, immediately mergeable state, hosted checks, reviewer threshold, and authenticated `gh` identity; invokes `gh pr merge` with `--match-head-commit`; then verifies and records the merged disposition. It never passes `--admin` or `--auto`. Add `--signing-key` when signed approvals are required. If GitHub accepts the command but leaves the PR pending, keep the goal `review-ready` and record the merge only after GitHub reports it.
7. After separate human review or merge, record exactly one disposition: `approved` leaves the goal `review-ready`; `changes-requested` archives the attempt, starts a fresh execution manifest, invalidates downstream evidence, and opens controlled rework; `merged` moves it to `completed`; `closed` cancels it. Fresh source-bound evidence is mandatory for `approved` and `merged`. Record `changes-requested` or `closed` even when delivery evidence is stale, preserving the stale-evidence reasons because neither disposition authorizes delivery.

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> \
  --pr-url <pull-request-url> \
  --merged-by "<human identity>" \
  --disposition <approved|changes-requested|merged|closed> \
  --merge-commit <sha-only-if-merged> \
  --evidence "<review or merge evidence>"
```

Record only facts that happened. In a signed-approval project, add `--signing-key <trusted-ssh-private-key>` so every disposition has an SSH receipt bound to the anchored trust store, exact goal, approved plan hash/version, execution attempt, actor, evidence, timestamp, and nonce. For `approved` or `merged`, the CLI also verifies the current `gh` identity, GitHub review decision, unique approving reviewer threshold, checks, PR base, and merge commit as applicable. If the human has not reviewed or merged, leave `human-review` pending.

## Handoff

Run `continuity workflow status --goal-id <goal-id>` on entry and exit. Human review and merge evidence determine the linked note's dated human-review, remediation, cancellation, or completion stage; do not write it independently. Follow only `allowed_actions`; report blocked actions without attempting them. Scope changes return to planning, and no disposition authorizes auto-merge or administrator bypass.
