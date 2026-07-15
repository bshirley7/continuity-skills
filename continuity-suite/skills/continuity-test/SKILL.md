---
name: continuity-test
description: Plan, run, record, and report project-specific validation plus Continuity's evergreen testing, code-review, and security standards. Use during execution loops, before push or PR handoff, in morning reports, or whenever the user asks for quality, tests, validation, sloppy-code detection, or security-risk review.
---

# Continuity Test

Use this skill as the structured quality gate for a Continuity goal. It complements `$continuity-execute`; it does not authorize scope expansion, dispatch, PR creation, or merge.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), [the testing and merge standard](../../references/testing-and-merge-standard.md), `$continuity-local`, `.continuity/config.json`, `AGENTS.md`, the approved plan, and the current compliance ledger before acting.

## Required assurance

- Treat configured validation and security commands as project-specific requirements, not suggestions.
- Add targeted regression tests for the changed behavior when the repository can support them.
- Review the diff for correctness, maintainability, data integrity, compatibility, accessibility, performance, privacy, security, and supply-chain risk.
- Stop on failed commands, unreviewed findings, missing evidence, stale approval, or discovered work that belongs in a separate note, roadmap item, or goal.
- Never mark `code-review`, `validation`, or `security-review` passed without reproducible evidence.

## Workflow

1. Run `continuity project doctor` and stop on drift.
2. Generate the goal quality plan:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test plan <goal-id> --worktree <execution-worktree>
```

3. Execute the listed `validation_commands`, goal `required_checks`, and configured `security_commands` through the no-shell machine runner. The runner verifies the enrolled repository, recorded worktree, and actual goal branch, then records argv, output, exit code, plan hash, commit, repository identity, and a tracked-plus-untracked source fingerprint:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test run <goal-id> --worktree <execution-worktree> --branch <goal-branch>
```

4. Add any targeted tests required by the diff, update the goal checks when needed, then rerun the machine runner. Perform an evidence-based code review and manual trust-boundary review. Capture concrete findings, fixed issues, and residual risk.
5. Record the result. A passed record is rejected unless the machine evidence still matches the enrolled repository, goal worktree and branch, approved plan, behavior configuration, configured commands, and current source fingerprint:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test record <goal-id> \
  --status <passed|failed> \
  --summary "<concise result>" \
  --worktree <execution-worktree> \
  --branch <goal-branch> \
  --code-review-evidence "<diff review evidence>" \
  --validation-evidence "<command and result>" \
  --security-evidence "<security review evidence>" \
  --update-gates
```

6. If failed, leave the goal running, validating, blocked, or partially completed as appropriate. Do not paper over failures to reach PR.
7. Treat an early pass as candidate evidence only while source or evidence artifacts may still change. After documentation, memory, roadmap, and evidence artifacts are complete, commit them and run the machine runner plus `test record` again on the final clean source state.
8. Push and create or update the draft PR only after that final test record. If passed and still current, continue to `$continuity-merge`.

Morning reports should include the latest Continuity test report, failed findings, missing evidence, and whether any active goal lacks a current test report.

## Handoff

Run `continuity workflow status --goal-id <goal-id>` on entry and exit. A failed or stale result returns to `$continuity-execute`; a final passed result on the committed source state permits the push/PR step and then `$continuity-merge`.
