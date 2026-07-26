# Continuity Releases, Updates, and Recovery

This guide explains how to install and update Continuity without replacing project-owned configuration or ignored private state. The canonical release source is `https://github.com/bshirley7/continuity-skills`.

## Supported environment

The release candidate supports macOS and Linux with Python 3.11 or newer. Operational features use:

- `git` for source identity, worktrees, and remote execution leases.
- `gh` for release verification, pull-request evidence, and authenticated human identity.
- `ssh-keygen` for signed plan approvals.
- `age` for encrypted private-state backup and restore.

Run these before enabling scheduled execution:

```bash
git --version
gh auth status
ssh-keygen -Y help >/dev/null
age --version
```

## Canonical source and legacy remotes

Existing clones that still use the former repository name should migrate explicitly:

```bash
git remote -v
git remote set-url origin https://github.com/bshirley7/continuity-skills.git
git fetch origin --tags
```

This changes only the Continuity source clone. A project repository keeps its own application remote.

## New project installation

Check out a specific release tag in the Continuity source clone, then run the installer against the target project:

```bash
git -C /path/to/continuity-skills fetch origin --tags
git -C /path/to/continuity-skills checkout v0.1.0-rc.1

python3 /path/to/continuity-skills/installer/install.py \
  --project-root /path/to/project \
  --project-id project-identifier \
  --integration-branch main \
  --interactive
```

The installer records the release and every suite-managed file in `.continuity/install-manifest.json`. It snapshots files before applying them and prints the snapshot identifier. It does not enable execution unless `--enable-execution` is supplied. After committing the installation transaction, it verifies the active GitHub CLI account and its `project` scope. A terminal launches `gh auth login --web` or `gh auth refresh` only when needed; GitHub CLI retains the credential and Continuity never stores the token. Cancellation or an unavailable terminal leaves the installation intact and returns the exact required command in `github_auth.next_command`.

New releases may add suite-owned skills or opt-in project settings. The installer preserves prior settings and user-owned skills, installs newly added suite skills, regenerates the project-local behavior skill and enabled surface adapters, and applies a safe default for each new setting. This adds `$continuity-workflow` and its slash-command adapters to existing projects without replacing custom skills. For the GitHub CLI merge capability, existing projects receive `github_cli_merge_enabled: false`; no project begins merging through Codex merely because it updated.

Legacy installations that stored newly introduced GitHub readiness fields as JSON `null` are migrated to safe defaults (`github_required_checks: []`, `github_required_reviewers: 1`, and `github_cli_merge_enabled: false`). Other invalid non-null values remain errors rather than being silently rewritten.

When post-update doctor finds a legacy note missing lifecycle timestamps, portfolio update may run `note migrate-lifecycle` once and retry doctor. The migration derives `created_at` only from the containing capture's valid `captured_at` and derives `updated_at` from the latest valid recorded revision, falling back to the derived creation time. Present but malformed timestamps, or notes without valid capture provenance, remain blocked for manual review.

## Ownership boundaries

An update may replace only release-managed copies under `.agents/continuity/`, `.agents/references/`, and `.agents/skills/continuity-*`, plus the managed blocks in `AGENTS.md` and `.gitignore`.

The following remain project-owned and are merged or regenerated from project settings rather than replaced with release defaults:

- `.continuity/config.json`
- `.continuity/project.json`
- `.continuity/project-behavior.json`
- `.continuity/trusted-approvers`
- `docs/project-memory/`
- `docs/project-roadmap/`
- project validation, security, schedule, and agent-surface choices
- user-owned skills whose names are outside the suite-owned `continuity-*` namespace

Ignored private state under `.continuity/private/` and `.continuity-portfolio/` is never a release input and is never deleted by an update.

## Check and update

Run all update commands from the target project:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json suite status
.agents/continuity/bin/continuity --project-root "$PWD" --json suite update --check
.agents/continuity/bin/continuity --project-root "$PWD" --json suite update --version v0.1.0-rc.1 --dry-run
.agents/continuity/bin/continuity --project-root "$PWD" --json suite update --version v0.1.0-rc.1
```

The default update path downloads the tagged archive through `gh`, verifies its GitHub build-provenance attestation, verifies every release-manifest hash, stages the installation, snapshots the current managed files, applies the release, and confirms the user-facing GitHub CLI authentication needed by repository and Projects workflows. A healthy authenticated session is silent. Use `--skip-github-auth` for deliberately unattended or offline updates; dry runs never launch authentication.

After an update that adds project settings, confirm that existing skills were preserved and the generated behavior contract is current:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
.agents/continuity/bin/continuity --project-root "$PWD" --json project recommendations
```

Opt in to GitHub CLI merge only through a reviewed configuration answers file containing `"github_cli_merge_enabled": true`. Re-run doctor afterward. This setting does not change the required GitHub checks or reviewer count and does not enable administrator bypass or auto-merge.

For a reviewed local source clone or an offline transfer:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json suite update \
  --source /path/to/continuity-skills \
  --dry-run
```

Local-source mode verifies the release manifest but cannot substitute for GitHub artifact attestation. Use it only for development or a separately authenticated offline release.

## Update all enrolled projects

Use the controller-level portfolio command when multiple enrolled projects should receive the same release. It discovers projects below each supplied workspace root and delegates to every project's installed `suite update` transaction. Separate checkouts with the same project ID are updated independently by path. A checkout using the legacy `.agents/project-continuity/` layout is bootstrapped through the current source installer and then verified through the newly installed project-local CLI.

Preview the current controller release across all projects:

```bash
python3 /path/to/continuity-suite/bin/continuity --json portfolio update \
  --root /path/to/workspace
```

Apply it only after reviewing the per-project preview:

```bash
python3 /path/to/continuity-suite/bin/continuity --json portfolio update \
  --root /path/to/workspace \
  --apply
```

For a tagged production release, use `--version <tag> --apply`. Repeat `--root` for separate workspace trees or `--project-id` to restrict the rollout. Legacy bootstrap requires the default controller source or an explicit `--source`; update that checkout to the current layout before switching it to tagged-only updates.

The command is dry-run by default. It validates the release, isolates every project, records the installed project doctor's pre-update health, performs the existing snapshot-backed update, runs doctor again, and automatically invokes that project's rollback snapshot if post-update health fails. Pre-update behavior-hash drift may be repaired by a compatible configuration migration, but post-update doctor must be healthy. A blocked or rolled-back project produces a partial portfolio result without changing another project's result. Managed-file drift still requires the separately reviewed `--overwrite-managed` flag.

## Managed-file drift

Continuity aborts before modifying anything when a suite-managed file differs from its installed hash. Export the drift report and inspect it:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" suite drift export \
  --output /tmp/continuity-managed-drift.json
```

Contribute intentional suite changes to the canonical Continuity repository. If the local edits are disposable, rerun the update with `--overwrite-managed`. The installer snapshots those edits before replacing them:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" suite update \
  --version v0.1.0-rc.1 \
  --overwrite-managed
```

Do not use overwrite to hide unexplained drift.

## Rollback

List snapshots under `.continuity/private/upgrades/`, then restore the selected identifier:

```bash
ls .continuity/private/upgrades
.agents/continuity/bin/continuity --project-root "$PWD" suite rollback \
  --snapshot 20260715T220000Z
```

Rollback restores the files and directories that existed before the update and removes ownership-scoped paths that the snapshot recorded as absent. The transaction includes managed control files, Continuity skills and references, generated Claude/Cursor/Windsurf adapters, project configuration, trust configuration, shared-note structure, and seeded memory and roadmap roots. An armed rollback guard restores this snapshot after a failure at any installation stage. Run `suite status` and `project doctor` immediately afterward.

## Private-state backup and restore

Keep the `age` identity outside every project repository. Create and verify an encrypted archive before the first scheduled run and before consequential upgrades:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" state backup \
  --recipient age1example \
  --signer github-login \
  --signing-key "$HOME/.ssh/id_ed25519" \
  --verify-identity "$HOME/.config/age/keys.txt" \
  --output "$HOME/.continuity/backups/project-before-pilot.tar.gz.age"

.agents/continuity/bin/continuity --project-root "$PWD" state verify \
  --archive "$HOME/.continuity/backups/project-before-pilot.tar.gz.age" \
  --identity "$HOME/.config/age/keys.txt"
```

Always inspect a restore first:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" state restore \
  --archive "$HOME/.continuity/backups/project-before-pilot.tar.gz.age" \
  --identity "$HOME/.config/age/keys.txt" \
  --recipient age1example \
  --signer github-login \
  --signing-key "$HOME/.ssh/id_ed25519" \
  --dry-run
```

Backup and restore acquire the project-state lock and refuse to run while a goal, scheduler run, or project execution lock is active. Production backup policy requires immediate decryption and inventory verification through `--verify-identity`. The non-dry restore verifies the integration-branch-anchored SSH trust store, project identity, and every payload hash, creates and verifies a new signed encrypted safety backup of current state, stages extraction, and replaces private state. It restores no committed application files.

## External audit checkpoint

The private JSONL chains detect partial corruption. Anchor their current heads outside the project so a complete local history rewrite is also detectable:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" state checkpoint-create \
  --signer github-login \
  --signing-key "$HOME/.ssh/id_ed25519"

.agents/continuity/bin/continuity --project-root "$PWD" state checkpoint-verify
```

The default checkpoint is `~/.continuity/audit-checkpoints/<project-id>.json` with a sibling SSH signature. It contains only ledger paths, record counts, and chain heads. It must remain outside the repository and private-state tree. Current ledgers may extend the checkpoint, but truncation or a rewritten prefix fails verification. `project doctor` and execution preflight fail closed when the production checkpoint requirement is enabled and the external anchor is missing or invalid.

## Post-update acceptance

An update is operationally complete only after these pass:

```bash
.agents/continuity/bin/continuity --project-root "$PWD" --json suite status
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
.agents/continuity/bin/continuity --project-root "$PWD" memory audit
.agents/continuity/bin/continuity --project-root "$PWD" roadmap audit
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
```

When Codex scheduling is enabled, also run `scheduler adapter codex verify`. Do not enable unattended dispatch while any check reports unhealthy.
