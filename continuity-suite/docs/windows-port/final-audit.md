# Native Windows Final Capability Audit

Recorded: 2026-07-17
Local host: native Windows, OneDrive NTFS workspace, Python 3.13.6
Execution, provider scheduling, and merging: disabled; source-branch
publication and draft PR creation were separately authorized

This audit reconciles the original Windows-port goal with the current local
evidence. Every functional acceptance gate now has direct evidence. The overall
goal remains open until the updated placeholder-hardening commit passes final
native validation and the complete hosted matrix at its exact head.

## Local release-readiness result

- The complete native suite passes after scheduler placeholder hardening: 119
  tests in 491.345 seconds.
- The security-focused adversarial suite passes without a shell-backed
  validation or security command.
- Thirteen canonical skills validate; Codex and Claude installed-project tests
  additionally validate the generated `continuity-local` skill and all Claude
  adapters.
- Nine Python entry points/modules compile, 129 local Markdown links resolve,
  one Python dependency is exactly pinned with two SHA-256 hashes, and 139
  release-managed files match the deterministic manifest.
- The release archive now includes `requirements.txt`; the previous workflow
  omitted it even though native Windows requires the timezone database.
- CI now defines Windows, macOS, and Linux jobs for Python 3.11 and 3.14,
  installs hashed dependencies, runs the cross-platform distribution audit and
  full suite, and performs diff hygiene. Official GitHub actions are pinned to
  full verified release commit SHAs with persisted checkout credentials off.
- All six jobs pass at exact audit head
  `d977490adcd7eeb8664c5a74b13107c2b58f9b0b` in
  [run 29564361138](https://github.com/bshirley7/continuity-skills/actions/runs/29564361138).

## Documented capability reconciliation

| Documented capability | Local Windows evidence | Remaining external evidence |
| --- | --- | --- |
| Install, configure, doctor, reinstall, update, rollback, uninstall, migration | fresh OneDrive/path-with-spaces installs; CMD and PowerShell launchers; drift, rollback, uninstall, autocrlf, and migration tests | none for local/source installs; tagged download remains covered by hosted release workflow |
| `$continuity`, capture, triage, memory, roadmap, plan, dispatch-disabled, execute-disabled, test, merge-assess, report, share, workflow | all local end-to-end tests pass; canonical platform-neutral state and authority handoffs asserted; authenticated Codex and Claude report-only invocations passed | none |
| Atomic persistence, locking, concurrent agents, crash and cancellation recovery | process locks, concurrent ledgers/captures, interrupted writes, restore journal, and Windows Job Object tests pass | none |
| Remote leases and scheduler protocol | repeated two-clone bare-remote lifecycle, signed isolated protocol rehearsal, two real paused Codex Scheduled sweeps, one claimed report no-op, and current-behavior replay/stale/contention evidence pass | none |
| Encrypted backup, verification, restore, rollback | official native age v1.3.1 plus signed protocol fixtures pass backup, independent verification, dry-run restore, restore, safety rollback, ACL, stale/tamper/crash, and secret-isolation gates | none |
| GitHub.com, Enterprise, PR assessment, Projects, guarded merge | network-isolated host/repository/account/base/head/check/reviewer/merge tests pass; official `gh.exe` 2.83.2 and authenticated read-only GitHub.com identity/repository calls succeed | no live merge is required by this port audit |
| Codex and Claude VS Code integration | all project skills/adapters/commands, trust/cwd/multi-root rules, byte parity, simultaneous mutation, and private-context isolation tested; Codex 26.707.91948 and Claude Code 2.1.212 discovered all 14 canonical project skills and invoked `continuity-report` read-only from the exact trusted Unicode workspace | none |
| Release integrity and cross-platform compatibility | deterministic manifest, portable paths, hashed dependency, and native suite pass locally; all six hosted Windows/macOS/Ubuntu jobs pass on Python 3.11 and 3.14 at exact compatibility head | none; the final evidence-only documentation commit must retain the same green matrix |
| Security boundaries | threat model plus path/ref/archive/config/command/secret/ACL/rollback/credential adversarial coverage passes | external tool/provider gates above must use the same controls; no bypass is acceptable |

## Completed external acceptance evidence

- Official WinGet package `FiloSottile.age` v1.3.1 is installed. The separately
  downloaded 10,741,348-byte Windows archive matches upstream SHA-256
  `c56e8ce22f7e80cb85ad946cc82d198767b056366201d3e1a2b93d865be38154`.
  Both executables report v1.3.1. Their historical publisher certificate is
  outside its validity period on the current clock, so the audit records
  Authenticode as non-passing and relies on the exact official archive digest.
- In a disposable Unicode OneDrive project whose path contains spaces,
  execution remained disabled and doctor remained healthy while official
  native age performed immediate verified backup, independent verification,
  dry-run restore, restore, verified safety backup, and safety-backup rollback.
  Existing-output, ciphertext-tamper, and signed-checkpoint stale-history cases
  failed closed. The final restored state contained all three expected notes,
  no restore journal remained, and exact age/SSH private material was absent
  from 521 project, checkpoint, report, metadata, and encrypted-archive files.
- Draft PR [#2](https://github.com/bshirley7/continuity-skills/pull/2) binds
  base `main` to head `windows-compatibility-update`; its exact head
  `d977490adcd7eeb8664c5a74b13107c2b58f9b0b` passes Windows, macOS, and Ubuntu
  on Python 3.11 and 3.14 in
  [run 29564361138](https://github.com/bshirley7/continuity-skills/actions/runs/29564361138).
  The PR remains draft and `main` was not changed.
- In a trusted native VS Code window rooted exactly at
  `C:\Users\Nick\OneDrive\Documents\DEV\continuity\Continuity Age Acceptance Ω`,
  Codex extension 26.707.91948 showed all 14 Continuity entries through
  `/skills` and invoked `$continuity-report` in report-only mode. Claude Code
  extension 2.1.212 loaded the same 14 project skills and 14 matching legacy
  commands, showed the suite through `/skills`, and invoked
  `/continuity-report` in report-only mode. The operator confirmed both passes;
  execution stayed disabled and neither invocation mutated project state.
- ChatGPT desktop 26.715.2305.0 created a local Codex Scheduled supervisor and
  kept it paused. After raw prompt verification corrected a Markdown-escaped
  double-underscore sweep placeholder, two manual runs produced two distinct
  supervisor heartbeats. The first claimed and completed one report no-op; the
  second returned no due or retry claims. `scheduler adapter codex verify`
  observes both sweeps, the no-op, and current-behavior replay, stale
  registration, and second-clone remote-lease contention artifacts. The task
  remains paused, active runs are zero, execution remains disabled, and its
  private ID is represented only by SHA-256
  `f51fecc373a8c104554601fb5485d12a98fe19495355fbfd4d39354fec4ac0f4`.

## Remaining release validation

No functional or provider-native acceptance item remains. The final updated
branch head must still pass:

1. Deterministic release-manifest regeneration and distribution validation.
2. The complete native Windows suite and static checks.
3. The six-cell Windows, macOS, and Ubuntu hosted matrix on Python 3.11 and
   3.14 at the exact final head.

No live PR merge, force push, administrator bypass, auto-merge, product-code
execution, cloud routine, or production side effect is needed.

## Exact final validation sequence

1. Regenerate the manifest and run the native distribution, compile, link,
   dependency, skill, and full-suite checks.
2. Commit only the reviewed compatibility files, excluding unrelated
   `debug.log`, and push the compatibility branch without changing `main`.
3. Require all six hosted matrix jobs to pass at that exact commit, then update
   the final evidence rows and reassess overall completion.

## Completion decision

Stages 1–9 pass with current evidence, including the provider-native Stage 7
no-op. Stage 10 remains in progress only because the placeholder-hardening and
evidence updates must pass the final native and hosted matrix at the exact
updated branch head. Therefore the overall goal is not yet complete.
