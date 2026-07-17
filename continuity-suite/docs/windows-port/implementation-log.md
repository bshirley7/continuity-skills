# Native Windows Implementation Log

## 2026-07-16 — Baseline and preservation

- Read the user-provided staged objective, README, suite contract, release and
  recovery guide, provider contract, current diff, test inventory, and release
  manifest.
- Identified all existing uncommitted files as Windows-port work created in the
  current user-directed effort; preserved them.
- Recorded native tools. Python, Git, GitHub CLI, VS Code, Codex, and Claude are
  installed. `age` and `age-keygen` are absent. PowerShell policy blocks the npm
  `.ps1` shims for Codex and Claude, requiring `.cmd`-aware discovery.
- Ran the complete native Windows suite: 81 tests, 76 passing, 4 failures, 1
  error in 193.532 seconds.
- Classified the remaining failures as one remote-lease product defect, three
  cross-platform external-tool fixture defects, and one Windows cleanup defect.
- Created the baseline capability map and full staged acceptance matrix.

Next: implement Stage 1 platform tests and harden the platform abstraction
before changing production integration behavior.

## 2026-07-16 — Platform, lifecycle, and baseline defect closure

- Replaced the Windows CRT lock's fixed retry behavior with explicit blocking
  nonblocking-lock retries and transient-error classification.
- Added bounded retry for idempotent atomic replacement and stale temporary-file
  cleanup after a killed writer.
- Added process-level tests for exclusion, lock release on termination, killed
  atomic writers, and 60 concurrent integrity-ledger records.
- Added canonical project-relative POSIX serialization and migrated persisted
  paths across the CLI, roadmap, shared notes, GitHub Projects, installer, and
  release manifest.
- Added long Unicode path, OneDrive, case-collision, junction escape, and
  UNC/mapped-drive fail-closed tests.
- Bound installed launchers to the installing Python interpreter, added exact
  CMD exit-code propagation, and added dependency reporting to doctor.
- Added LF enforcement and deterministic, platform-neutral release manifests.
- Repaired the Windows installer/upgrade test harness and added a native
  OneDrive path-with-spaces installation test.
- Added dry-run-first `suite uninstall`; verified preservation of private state
  and a user-owned skill.
- Fixed remote leases by sending raw UTF-8 bytes to Git plumbing. Windows text
  pipes had created `lease.json\r` tree entries. Extended the test to two
  independent clones contending through a local bare remote.
- Replaced POSIX-only `gh` and `age` fixtures with isolated cross-platform
  executable test doubles. Tests no longer fall through to real GitHub.
- Regenerated release integrity metadata.
- Full native Windows result: 98 tests passed in 243.425 seconds.

Remaining direct evidence includes Windows ACL policy, full child-process-tree
cancellation, cross-platform migration, official age executables, installed
GitHub CLI integration, provider conformance, VS Code Codex/Claude discovery,
security expansion, and Linux/macOS CI.

## 2026-07-16 â€” Stage 1 Windows edge-case closure

- Added native effective-rights inspection for the private-state NTFS DACL.
  `project doctor` now reports the result and fails when `Everyone` or
  `BUILTIN\\Users` can modify sensitive state.
- Forced stable UTF-8 CLI output independent of a legacy Windows console or
  redirected-pipe code page; the CMD launcher also pins Python UTF-8 mode.
- Added an alternate-encoding subprocess test that round-trips a Unicode path
  through CLI diagnostics as UTF-8.
- Replaced direct-child-only validation timeouts with a no-shell process-tree
  runner. On Windows, a synchronization wrapper is placed in a kill-on-close
  Job Object before the configured command starts, eliminating the descendant
  assignment race. POSIX uses a dedicated process session and process-group
  termination.
- Routed validation evidence, nested project CLI, and source-installer calls
  through the process-tree runner.
- Proved that a timed-out parent cannot leave a grandchild running. The first
  `taskkill` implementation failed this test and was replaced rather than
  weakening the assertion.
- Focused Stage 1 and validation evidence result: 17 tests passed.

All native Windows Stage 1 rows now have direct evidence. Its cross-platform
regression clause remains open until the Linux/macOS CI gate runs in Stage 10.

## 2026-07-16 â€” Stage 2 native lifecycle completion

- Added a release-managed PowerShell launcher with the same installer-bound
  interpreter selection, UTF-8 mode, argv forwarding, and exit-code behavior as
  the CMD launcher.
- Verified both launchers from a working directory outside a OneDrive project
  whose path contains spaces. A restricted PowerShell environment can invoke
  `continuity.cmd` without changing machine policy.
- Added a migration test that simulates a POSIX interpreter binding, reinstalls
  on Windows, preserves private state, rebinds to the native interpreter, and
  retains platform-neutral `/` install-manifest keys.
- Added a three-mode (`true`, `false`, `input`) `core.autocrlf` checkout test;
  every exported tree rebuilds the identical release manifest.
- Added a native Windows operations guide and linked it from the README,
  quickstart, and release guide.
- Combined Stage 2 result: eight release, native installer, managed-drift,
  rollback, idempotence, migration, launcher, and uninstall tests passed.

Stage 2's native completion gate passes. WSL 2 is enabled but no Linux
distribution is installed, so Linux/macOS regression evidence remains assigned
to the Stage 10 CI matrix rather than being inferred locally.

## 2026-07-16 â€” Stages 3 and 4 local authority and lease closure

- Ran all 63 end-to-end local workflow tests on native Windows; capture,
  triage, memory, roadmap, planning, disabled approval, reporting, sharing,
  scheduler, backup protocol, and guarded delivery fixtures passed.
- Added an installed-project authority test with Codex and Claude enabled.
  Their skill trees match byte-for-byte, CMD and PowerShell return the same
  canonical machine handoff, execution remains unauthorized, private state is
  Git-ignored, and a unique private sentinel is absent from every automatically
  loaded instruction, skill, and command surface.
- Added fast-forward-only remote lease renewal and committed scheduler binding
  for the exact run, task, and idempotency key. Binding is no longer merely a
  local receipt field.
- Bound every lease record's `previous_lease_commit` to the actual single Git
  parent. Merge-shaped or ancestry-mismatched histories fail closed.
- Added a five-minute conservative clock-skew acquisition grace, future-clock
  diagnostics, strict timestamp validation, bounded TTLs, expired-lease stale
  recovery, and stale local receipt replay rejection.
- Fixed scheduled finish and stale recovery so they release only the exact
  bound goal/attempt/run/task lease before recording the final run event. A
  binding mismatch cannot release another run's lease.
- The complete two-clone lease scenario passed five consecutive Windows runs;
  its scheduler-bound recovery scenario also passed.

Stages 3 and 4 now satisfy their native completion gates without enabling
execution or introducing force-push behavior.

## 2026-07-16 â€” Stage 5 local backup and recovery hardening

- Replaced permissive `tarfile.extractall` calls with a bounded extractor that
  accepts only regular files and directories, rejects traversal, backslashes,
  links, special files, duplicate/case-colliding paths, file-as-directory
  trees, and oversized archives, and preserves executable modes on POSIX.
- Tightened backup inventory validation to require at least one confined,
  portable private-state path and a SHA-256 value for every entry. Unlisted
  payload files now fail verification.
- Plaintext backup, verification, and restore workspaces now validate their
  effective Windows DACL before use.
- Encryption writes to a random sibling staging file, performs required
  decryption/signature/inventory verification before publication, refuses to
  overwrite an existing archive, atomically publishes only a complete file,
  and removes partial staging after failure.
- Restore now prepares the complete replacement tree before mutation and uses
  an ignored, ACL-checked transaction journal with rollback copies. Doctor
  reports a pending transaction, and `state recover-restore` deterministically
  restores pre-crash canonical state.
- A production restore whose signed backup does not extend the configured
  external audit checkpoint now fails as stale before replacing private state.
- Native fixture tests reject partial encryption, corrupted archives, missing
  payload, invalid signatures, stale signed backups, unsafe overwrite, and a
  simulated crash that left partial replacement state. Valid backup, immediate
  verification, dry-run restore, safety backup, restore, and rollback pass.

The remaining Stage 5 boundary is external: this host does not have `age.exe`
or `age-keygen.exe`. The official project currently publishes age v1.3.1 and
recommends `winget install --id FiloSottile.age`; Winget cannot run in this
non-interactive logon session, so a reviewed user-local official binary install
is required before the native executable gate can run.

- Post-hardening full native Windows regression: 105 tests passed in 269.273
  seconds after deterministic manifest regeneration and a clean diff check.

## 2026-07-17 — Stage 6 host, repository, and account binding

- Verified the installed official `gh.exe` 2.83.2 binary. Its read-only auth
  status reports the active `github.com` account but rejects the expired token;
  no login, account switch, token access, or GitHub mutation was attempted.
- Replaced `github.com`-only PR parsing with canonical GitHub.com and GitHub
  Enterprise parsing. PR delivery now fails unless its host, owner, and
  repository match the local `origin` remote exactly (case-insensitively).
- Pinned PR inspection and merge calls to an explicit
  `HOST/OWNER/REPOSITORY` and PR number. The returned canonical PR URL, base,
  head branch, full 40-character head SHA, draft state, immediate mergeability,
  required checks, and effective approving reviewers are revalidated.
- Pinned active-account verification to the same host and bound that host,
  repository, PR number, account, and head SHA into assessment and exact merge
  authorization evidence. A different active account fails before mutation.
- Extended the optional GitHub Projects adapter so its host is approval-bound,
  `GH_HOST` is explicit, GraphQL uses `--hostname`, and the active host account
  is verified before requests. Shared-note publication now applies the same
  host/repository/account binding.
- Network-isolated Enterprise guarded-merge, GitHub.com/Enterprise parser,
  account, returned-URL, checks, reviewers, and GitHub Projects suites pass.
  The guarded fixture proves that neither `--auto` nor `--admin` is emitted.

Stage 6's remaining evidence is external and credential-bound: the user must
repair or replace the active `github.com` credential before a native read-only
identity/repository query can pass. Live PR creation or merge is neither needed
nor authorized for this porting audit.

## 2026-07-17 — Stage 7 Windows scheduler and provider protocol

- Replaced shell-oriented rendered command text with an absolute native
  launcher plus canonical `supervisor_argv` and `registration_argv` arrays.
  Providers must execute the array with `shell=false`; a Windows test preserves
  a workspace path containing spaces, `&`, parentheses, and an apostrophe from
  an unrelated current directory.
- Added a Claude Code provider adapter alongside Codex with render,
  signed-probe recording, and verification commands. Its definition explicitly
  targets a Claude Desktop local scheduled task; cloud routines are rejected as
  substitutes because fresh clones cannot access ignored local state.
- Ran an actual local scheduler protocol with execution disabled: registered a
  stable task, observed three sweeps, consumed and completed one claimed no-op
  review, rejected reuse of its claim, rejected a run under a stale
  registration, and rejected a second clone contending for an active lease.
- Stored the three rejection outputs as private artifacts, signed their exact
  SHA-256-bound conformance receipts with a trusted test key, and obtained a
  healthy `scheduler adapter codex verify` result.
- Re-ran the existing capacity, retry, heartbeat, early-dispatch-success,
  stale-recovery, lease-binding/release, and simultaneous-claim race tests after
  the adapter changes; all pass on native Windows.

The provider-native observation remains external. No Codex automation, Claude
Desktop task, cloud routine, or Windows Task Scheduler entry was created, and
repository execution remains disabled.

## 2026-07-17 — Stage 8 VS Code, Codex, and Claude interoperability

- Inspected the installed native tools without starting a model-backed task:
  VS Code 1.128.1, Codex extension 26.707.91948, Claude Code extension
  2.1.212, Codex CLI 0.20.0, and Claude CLI 2.1.118. The installed Codex
  extension contains explicit `AGENTS.md`, `SKILL.md`, workspace-trust,
  workspace-folder, and remote-host handling. The Claude extension declares
  untrusted workspaces unsupported and contains explicit `CLAUDE.md`,
  `.claude/skills`, `.claude/commands`, first-workspace-root, additional-root,
  and remote-host handling.
- Cross-checked the installed implementation against current official Codex,
  Claude Code, and VS Code documentation. Codex scans `.agents/skills` toward
  the repository root; Claude scans `.claude/skills`, supports `@AGENTS.md` as
  the Windows-safe import, and gives skills precedence over same-named legacy
  commands. Both require a new session for newly introduced project startup
  instructions; newly created Claude skill roots also require a restart.
- Added a dedicated VS Code interoperability guide covering exact project
  configuration, trust, discovery, invocation, reloads, working directories,
  multi-root fail-closed policy, simultaneous agents, private-context limits,
  and remote extension-host distinctions. The supported multi-root policy is
  one active Continuity project per conversation with an explicit absolute
  `--project-root` for every command.
- Extended the native installed-project acceptance test to enumerate all 13
  suite skills plus `continuity-local`, validate each skill's invocable name
  and description, require every Claude command shim, compare every Claude
  skill tree byte-for-byte with its canonical `.agents/skills` source, and
  require the `@AGENTS.md` import.
- Verified upward discovery from a nested path and explicit root selection from
  an unrelated workspace folder through both native launchers. Simultaneous
  Codex-side CMD and Claude-side PowerShell capture processes both completed
  through the shared native state lock with distinct persisted capture IDs.
  The focused Stage 8 test passed in 12.219 seconds.
- The private sentinel remains Git-ignored and absent from `AGENTS.md`,
  `CLAUDE.md`, canonical and adapted skills, and command shims. The shared
  workflow handoff continues to report execution unauthorized.

The remaining Stage 8 evidence is an external provider boundary. No
model-backed Codex or Claude request was sent. A human must open a trusted
project window, verify all Continuity entries in each provider's `/skills`
selector, and run one read-only skill such as status/report before this stage's
provider-native gate can pass.

## 2026-07-17 — Stage 9 security and adversarial hardening

- Added one portable relative-path policy across runtime confinement, release
  and backup manifests, roadmap and GitHub Projects state, archive extraction,
  installer payloads, and rollback snapshots. It rejects traversal,
  backslashes, absolute/drive paths, Windows device names (including superscript
  COM/LPT aliases), alternate data streams, trailing dots/spaces, illegal or
  bidirectional/control characters, non-NFC Unicode, oversized segments, and
  case/Unicode collisions.
- Changed archive processing from eager `getmembers()` loading to bounded
  streaming enumeration. Limits now stop hostile member tables immediately;
  only portable regular files and directories can reach a fresh confined
  extraction tree.
- Added strict Git remote-name, branch, remote-tracking-ref, full object-ID, and
  release SemVer validation before values can become Git or GitHub CLI
  arguments. `git show` revision operands use the end-of-options boundary, and
  remote lease parents are validated before ancestry comparison.
- Switched configured checks to native Windows `CommandLineToArgvW` parsing.
  Validation and security commands reject command shells, `.cmd`/`.bat`
  wrappers, shell operators, and inline credential flags; executables are run
  as direct argv with credential-shaped environment variables removed.
- Added centralized diagnostic redaction for private keys, age identities,
  authorization headers, credential assignments, URL passwords, GitHub,
  OpenAI, GitLab, npm, PyPI, Slack, AWS, and JWT token shapes. Evidence command
  output and CLI/installer errors pass through it before persistence or display.
- Hardened upgrade rollback so the complete snapshot name, location, reparse
  status, metadata, collisions, overlaps, payload type, and every source are
  validated before any project entry is removed. A real Windows snapshot
  junction and malicious traversal metadata are rejected without changing the
  victim file.
- Pinned `tzdata` to the installed 2026.3 release with the official wheel and
  source archive SHA-256 hashes. Added a security threat model covering assets,
  adversaries, provider and filesystem boundaries, residual same-user and
  untrusted-code risk, and the operator checklist.
- The focused adversarial tests pass, the affected GitHub Projects and installer
  suites pass, and the complete native Windows regression passed all 117 tests
  in 332.623 seconds. Execution stayed disabled; no credential repair,
  dependency install, model-backed request, provider registration, GitHub
  mutation, or other external side effect occurred.

Stage 9's local completion gate passes. The remaining blocked items belong to
the explicit external Stage 5–8 boundaries and the Stage 10 cross-platform CI
matrix; security controls were not relaxed to bypass them.

## 2026-07-17 — Stage 10 local acceptance and release readiness

- Ran the complete native Windows suite after the final distribution audit: all
  117 tests passed in 332.623 seconds on Python 3.13.6. No safety-critical
  Windows skip was added.
- Added a cross-platform distribution validator that compiles every Python
  module and extensionless CLI entry point, validates skill frontmatter and
  local references, resolves all local Markdown links without root escape,
  requires exact hashed Python dependencies, and compares the complete release
  manifest in memory without rewriting it.
- Found and fixed a release-packaging defect: `requirements.txt` was absent
  from both the deterministic release manifest and tagged archive even though
  Windows needs its timezone data. It is now release-managed and copied into
  every tagged artifact.
- Expanded CI from Linux/macOS to a six-cell Windows, macOS, and Linux matrix on
  Python 3.11 and 3.14. Every cell installs the hash-locked requirements, runs
  the distribution audit and complete suite, and checks diff hygiene.
- Updated official workflow dependencies to the current reviewed releases and
  pinned their full verified commit SHAs: checkout v6.0.2, setup-python v6.2.0,
  and attest-build-provenance v4.1.1. Checkout credential persistence is off;
  ordinary CI has only `contents: read`.
- Added the final capability audit with exact external acceptance sequence.
  Current static evidence validates 13 skills, 9 Python sources, 129 local
  Markdown links, one exactly pinned dependency with two hashes, and 139
  release-managed files.
- Installed the GitHub connector for future read-only hosted-run inspection.
  It found no pull-request workflow run attached to the current upstream main
  commit. No branch, commit, push, PR, run retry, or other GitHub mutation was
  performed.

Stage 10 remains blocked at its external completion gate. The proposed commit
must be published before the six hosted jobs can produce Linux, macOS, and
Windows evidence; official age, repaired gh identity, provider-native no-op,
and authenticated Codex/Claude VS Code smokes also remain explicitly
human-controlled. The overall Windows goal is therefore not marked complete.
