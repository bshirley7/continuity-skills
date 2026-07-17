# Native Windows Final Capability Audit

Recorded: 2026-07-17
Local host: native Windows, OneDrive NTFS workspace, Python 3.13.6
Execution, provider scheduling, and merging: disabled; source-branch
publication and draft PR creation were separately authorized

This audit reconciles the original Windows-port goal with the current local
evidence. It does not mark the overall goal complete while external acceptance
rows remain blocked.

## Local release-readiness result

- The complete native suite passes: 119 tests in 318.261 seconds.
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
- All six jobs pass at exact compatibility head
  `277aa404b869cb34c71ffe10becefad022c433d0` in
  [run 29563386124](https://github.com/bshirley7/continuity-skills/actions/runs/29563386124).

## Documented capability reconciliation

| Documented capability | Local Windows evidence | Remaining external evidence |
| --- | --- | --- |
| Install, configure, doctor, reinstall, update, rollback, uninstall, migration | fresh OneDrive/path-with-spaces installs; CMD and PowerShell launchers; drift, rollback, uninstall, autocrlf, and migration tests | none for local/source installs; tagged download remains covered by hosted release workflow |
| `$continuity`, capture, triage, memory, roadmap, plan, dispatch-disabled, execute-disabled, test, merge-assess, report, share, workflow | all local end-to-end tests pass; canonical platform-neutral state and authority handoffs asserted | authenticated provider UI invocation for Codex and Claude |
| Atomic persistence, locking, concurrent agents, crash and cancellation recovery | process locks, concurrent ledgers/captures, interrupted writes, restore journal, and Windows Job Object tests pass | none |
| Remote leases and scheduler protocol | repeated two-clone bare-remote lifecycle plus signed local no-op conformance passes | one real Codex automation or Claude Desktop local task observation |
| Encrypted backup, verification, restore, rollback | official native age v1.3.1 plus signed protocol fixtures pass backup, independent verification, dry-run restore, restore, safety rollback, ACL, stale/tamper/crash, and secret-isolation gates | none |
| GitHub.com, Enterprise, PR assessment, Projects, guarded merge | network-isolated host/repository/account/base/head/check/reviewer/merge tests pass; official `gh.exe` 2.83.2 and authenticated read-only GitHub.com identity/repository calls succeed | no live merge is required by this port audit |
| Codex and Claude VS Code integration | all project skills/adapters/commands, trust/cwd/multi-root rules, byte parity, simultaneous mutation, and private-context isolation tested | `/skills` discovery and one read-only invocation in each authenticated extension |
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
  `277aa404b869cb34c71ffe10becefad022c433d0` passes Windows, macOS, and Ubuntu
  on Python 3.11 and 3.14. The PR remains draft and `main` was not changed.

## Explicit remaining gates

The following evidence cannot be manufactured by local fixtures:

1. In a trusted VS Code project window, verify all Continuity entries in
   Codex and Claude `/skills`, then invoke one read-only status/report skill in
   each provider.
2. Create and observe one explicitly authorized local Codex automation or
   Claude Desktop scheduled no-op task with execution disabled.

No live PR merge, force push, administrator bypass, auto-merge, product-code
execution, cloud routine, or production side effect is needed for these gates.

## Exact external acceptance sequence

After the operator separately authorizes each applicable action:

1. Complete the two VS Code read-only provider smokes and record provider,
   extension version, project root, skill name, and canonical handoff result.
2. Complete the scheduler no-op observation and verify its signed provider
   conformance receipt with execution still disabled.
3. Update the acceptance matrix with direct run URLs/artifact identifiers and
   exact tool versions. Only then reassess the overall completion gate.

## Completion decision

Stages 1–6 and 9 pass with current evidence. Stages 7 and 8 have complete local
implementations but retain the explicit interactive gates above. Stage 10's
native, static, and hosted cross-platform checks pass; its final audit remains
open until those Stage 7 and 8 rows pass on the final commit.
Therefore the overall goal remains incomplete by design.
