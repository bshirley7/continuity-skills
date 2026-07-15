# Continuity Next-Business-Day Pilot

This runbook validates one low-risk objective from private note capture through a tested draft pull request and next-business-day human review. It is deliberately limited to one enrolled project and one reversible goal.

## Pilot eligibility

Choose work that has bounded files, explicit acceptance criteria, fast validation, and no production deployment. Exclude destructive migrations, credentials, billing, production data, broad dependency upgrades, emergency work, and changes requiring external publication beyond a draft pull request.

## One-time readiness

1. Install the reviewed `v0.1.0-rc.1` release and run the post-update acceptance commands.
2. Configure Codex as the primary agent surface and scheduler provider. Set `github_required_checks` to the exact hosted check-run names required by the project repository and keep at least one required approving reviewer.
3. Add a trusted SSH approver:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" approval trust add \
  --identity github-login \
  --public-key "$HOME/.ssh/id_ed25519.pub"
```

`approval trust add` only prepares a trust-store change. Commit `.continuity/trusted-approvers`, merge it through protected human review on the integration branch, and fetch `origin/<integration-branch>`. Production approval, disposition, backup, and checkpoint verification fail when the local trust store differs from that fetched branch anchor.

4. Create and immediately verify an encrypted state backup, then create the external signed audit checkpoint:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" state backup \
  --recipient age1example --verify-identity "$HOME/.config/age/keys.txt" \
  --signer github-login --signing-key "$HOME/.ssh/id_ed25519"

.agents/continuity/bin/continuity --project-root "$PWD" state checkpoint-create \
  --signer github-login --signing-key "$HOME/.ssh/id_ed25519"
```
5. Render the Codex automation definition:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json \
  scheduler adapter codex render --root /path/to/workspace
```

6. Create or update the Codex automation with the exact returned title, interval, roots, and prompt. Register its returned task ID with the returned command.
7. Observe two sweeps and one claimed review or report no-op. Exercise claim replay rejection, stale-registration rejection, and second-workstation lease contention in an isolated rehearsal. Record each observed result with `scheduler adapter codex record-probe --probe <probe> --status passed --evidence <evidence> --artifact-sha256 <sha256> --actor <identity> --signing-key <trusted-ssh-private-key>`, then require this command to become healthy:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json \
  scheduler adapter codex verify
```

## Prepare the note and goal

Capture the occurrence with its actual timestamp and dimensions. Triage it without granting authority. Retrieve cited memory and roadmap context, then create one decision-complete goal with the note marked `current-goal`.

Before approval, confirm:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --note-id <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
```

Sign the exact plan receipt:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> \
  --version <plan-version> \
  --approved-by github-login \
  --authorization-text "Approve <goal-id> plan v<plan-version>" \
  --signing-key "$HOME/.ssh/id_ed25519"
```

Verify it independently:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" approval verify <goal-id>
```

## Off-hours sequence

The responsible defaults are review at `20:00`, dispatch at `22:00`, and report at `07:00` in the project timezone.

1. The review sweep triages new notes, refreshes memory and roadmap health, and prepares eligible work. It does not execute notes.
2. Before dispatch, the supervisor acquires the project remote lease:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" scheduler lease acquire \
  --owner codex-supervisor \
  --goal-id <goal-id> \
  --remote origin
```

3. `scheduler run-start` binds that lease to the exact goal attempt, provider run, task ID, owner fingerprint, and lease commit. Direct `goal start` enforces the same goal-attempt lease. The claimed dispatch also validates the signed approval, plan and behavior hashes, external audit checkpoint, current integration base, dependencies, and one-goal project lock.
4. Execution uses an isolated worktree and goal branch. It completes code, documentation, memory, roadmap, and evidence changes before the final commit.
5. The final test run binds validation and security evidence to the committed source fingerprint.
6. The tested commit is pushed to a draft pull request. Required GitHub checks must pass and merge conflicts or unresolved change requests must be absent.
7. The goal moves to `review-ready` and stops. Only the matching dispatch run may release its bound remote lease. Review or report completion cannot release it. Continuity never merges.

Any missing approval, failed check, stale source binding, lease conflict, scheduler failure, or runtime limit produces a blocked or partial draft handoff instead of inferred continuation.

## Morning review

Generate both project-local detail and the deterministic portfolio-safe summary:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json report morning
.agents/continuity/bin/continuity --json portfolio report --sanitized --root /path/to/workspace
```

Review the plan identity, note stage, changed files, tests, security evidence, CI state, draft pull request, blockers, and exact allowed dispositions. `approved` and `merged` require the configured number of authenticated GitHub approving reviewers. `changes-requested` reopens only in-scope work; expanded scope requires goal revision and a newly signed approval.

Every `merge record-human` disposition and every in-scope `goal resume` must include `--signing-key <trusted-ssh-private-key>` in a signed-approval project. The resulting receipts bind the goal, plan hash/version, execution attempt, actor, evidence, timestamp, and nonce.

## Pilot acceptance

The release candidate passes the pilot only when:

- The note timeline shows capture, triage, planning, signed approval, dispatch, execution, validation, review-ready, and human disposition with timestamps.
- The draft pull request matches the final tested commit and required CI checks.
- No raw note, local path, task identifier, claim, approval text, or private evidence appears in the sanitized portfolio report.
- A second workstation cannot acquire the active remote lease.
- The encrypted backup verifies and the update snapshot can be rolled back in a rehearsal.
- The signed external audit checkpoint verifies and rejects a fully rewritten local ledger.
- Installer fault injection after every managed stage restores project contracts, generated adapters, configuration, and seeded documentation.
- The morning human can approve, request changes, merge, or close using a command emitted by workflow status.

After the morning review, record problems as notes, keep execution disabled for unresolved critical or high findings, and publish `v0.1.0` only after the fixes and rollback rehearsal pass.
