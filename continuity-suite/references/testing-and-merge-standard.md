# Testing and Merge Standard

Apply this standard to every Continuity execution before PR handoff and merge review.

## Evergreen test standard

- Start from the approved goal, acceptance criteria, exclusions, cited memory, roadmap IDs, and current diff.
- Run candidate checks during implementation, but run the authoritative configured `validation_commands`, goal `required_checks`, and security commands through `continuity test run` only after documentation, memory, roadmap, and evidence artifacts are committed.
- Execute commands as direct argument arrays without shell operators. Verify that the worktree belongs to the enrolled repository and its actual branch matches the goal execution record. Record output and exit status, and bind the run to repository identity, the approved plan hash, behavior hash, commit, tracked and untracked source fingerprint, and exact command set.
- Reject a passing report and merge-safety assessment if machine evidence is absent or any tracked or untracked source, commit, branch, plan, behavior, or configured command has changed since the run.
- Prefer repository-native commands and existing test patterns. Add new tests where behavior changed and the repo has a practical test surface.
- Cover success, failure, boundary, regression, data integrity, compatibility, accessibility, performance, and privacy concerns when applicable.
- Include manual or visual verification only as evidence for behavior that cannot be fully covered by automated checks.
- Treat failures, flaky results, skipped checks, and missing test surfaces as reportable findings with explicit follow-up or risk.

## Code review standard

- Review the complete diff, not only the files touched intentionally.
- Check scope alignment, unnecessary churn, dead code, brittle abstractions, error handling, migration safety, observability, documentation drift, and rollback.
- Confirm no raw notes, private Continuity state, credentials, local paths, or private scheduler data enter committed product files or PR evidence.
- Route unrelated work into a captured note, roadmap item, or later goal instead of expanding the active branch.

## Security review standard

- Identify touched trust boundaries, inputs, outputs, secrets, auth paths, data stores, subprocesses, network calls, migrations, dependency changes, and external side effects.
- Run configured security commands when present.
- Perform an evidence-based manual security review even when no scanner exists.
- Check injection, path traversal, unsafe deserialization, authorization gaps, credential exposure, logging leaks, dependency and supply-chain risk, and privilege changes.
- A security gate passes only with concrete reviewed evidence or fails with findings.

## Merge-safety standard

- Refresh or verify the integration base before PR handoff.
- Confirm the goal branch is focused, reviewable, and not the integration branch.
- Confirm the working tree has no unrelated product changes and no private Continuity state staged for commit.
- Confirm the tested local head equals the pushed remote branch and draft PR head, and that the PR base equals the configured integration branch.
- Require every configured GitHub check and every observed hosted check to finish successfully before `review-ready`. Reject conflicting, dirty, behind, or unknown merge state and unresolved changes-requested reviews.
- Confirm tests, code review, validation, security review, documentation, memory impact, roadmap impact, and final alignment are passed or explicitly not applicable.
- Keep incomplete, failed, or blocked work in a draft PR with visible blockers.
- Human PR review and merge are separate from automated delivery. Reviewer threshold and authenticated review decision are enforced when recording the morning `approved` or `merged` disposition. Continuity must stop at `review-ready`, must not auto-merge or force-push, and may record `completed` only after verified human merge evidence.

## Report standard

Every quality or merge report should include actor, timestamp, goal ID, branch, worktree, commands or review methods, results, findings, evidence paths, residual risk, and the compliance gates updated.
