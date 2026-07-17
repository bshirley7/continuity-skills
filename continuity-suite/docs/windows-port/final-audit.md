# Native Windows Final Capability Audit

Recorded: 2026-07-17
Local host: native Windows, OneDrive NTFS workspace, Python 3.13.6
Execution, scheduling, live GitHub mutation, and merging: disabled

This audit reconciles the original Windows-port goal with the current local
evidence. It does not mark the overall goal complete while external acceptance
rows remain blocked.

## Local release-readiness result

- The complete native suite passes: 117 tests in 332.623 seconds.
- The security-focused adversarial suite passes without a shell-backed
  validation or security command.
- Thirteen canonical skills validate; Codex and Claude installed-project tests
  additionally validate the generated `continuity-local` skill and all Claude
  adapters.
- Nine Python entry points/modules compile, 129 local Markdown links resolve,
  one Python dependency is exactly pinned with two SHA-256 hashes, and 138
  139 release-managed files match the deterministic manifest.
- The release archive now includes `requirements.txt`; the previous workflow
  omitted it even though native Windows requires the timezone database.
- CI now defines Windows, macOS, and Linux jobs for Python 3.11 and 3.14,
  installs hashed dependencies, runs the cross-platform distribution audit and
  full suite, and performs diff hygiene. Official GitHub actions are pinned to
  full verified release commit SHAs with persisted checkout credentials off.

## Documented capability reconciliation

| Documented capability | Local Windows evidence | Remaining external evidence |
| --- | --- | --- |
| Install, configure, doctor, reinstall, update, rollback, uninstall, migration | fresh OneDrive/path-with-spaces installs; CMD and PowerShell launchers; drift, rollback, uninstall, autocrlf, and migration tests | none for local/source installs; tagged download remains covered by hosted release workflow |
| `$continuity`, capture, triage, memory, roadmap, plan, dispatch-disabled, execute-disabled, test, merge-assess, report, share, workflow | all local end-to-end tests pass; canonical platform-neutral state and authority handoffs asserted | authenticated provider UI invocation for Codex and Claude |
| Atomic persistence, locking, concurrent agents, crash and cancellation recovery | process locks, concurrent ledgers/captures, interrupted writes, restore journal, and Windows Job Object tests pass | none |
| Remote leases and scheduler protocol | repeated two-clone bare-remote lifecycle plus signed local no-op conformance passes | one real Codex automation or Claude Desktop local task observation |
| Encrypted backup, verification, restore, rollback | signed age-protocol fixtures, archive adversarial tests, ACLs, stale/tamper/crash recovery pass | official native `age.exe` and `age-keygen.exe` run |
| GitHub.com, Enterprise, PR assessment, Projects, guarded merge | network-isolated host/repository/account/base/head/check/reviewer/merge tests pass; official `gh.exe` executes | repaired authenticated read-only identity/repository call; no live merge is required by this port audit |
| Codex and Claude VS Code integration | all project skills/adapters/commands, trust/cwd/multi-root rules, byte parity, simultaneous mutation, and private-context isolation tested | `/skills` discovery and one read-only invocation in each authenticated extension |
| Release integrity and cross-platform compatibility | deterministic manifest, portable paths, hashed dependency, native suite, and six-cell CI definition pass locally | green hosted Linux, macOS, and Windows matrix on the proposed commit |
| Security boundaries | threat model plus path/ref/archive/config/command/secret/ACL/rollback/credential adversarial coverage passes | external tool/provider gates above must use the same controls; no bypass is acceptable |

## Explicit remaining gates

The following evidence cannot be manufactured by local fixtures:

1. Install or otherwise provide the reviewed official native `age.exe` and
   `age-keygen.exe`, then run the real encrypted backup/verify/restore gate.
2. Repair the expired `github.com` GitHub CLI credential and run only the
   read-only host/account/repository verification gate.
3. In a trusted VS Code project window, verify all Continuity entries in
   Codex and Claude `/skills`, then invoke one read-only status/report skill in
   each provider.
4. Create and observe one explicitly authorized local Codex automation or
   Claude Desktop scheduled no-op task with execution disabled.
5. Publish the proposed source to a branch or PR and collect green Python 3.11
   and 3.14 jobs on Windows, macOS, and Linux.

No live PR merge, force push, administrator bypass, auto-merge, product-code
execution, cloud routine, or production side effect is needed for these gates.

## Exact external acceptance sequence

After the operator separately authorizes each applicable action:

1. Re-run `project doctor` and retain its sanitized JSON output.
2. Run the official age backup, verify, dry-run restore, restore, and rollback
   scenario in a disposable enrolled project whose path contains spaces.
3. Run `gh auth status --hostname github.com --active` and
   `gh api user --hostname github.com --jq .login`; do not use `--show-token`.
4. Complete the two VS Code read-only provider smokes and record provider,
   extension version, project root, skill name, and canonical handoff result.
5. Complete the scheduler no-op observation and verify its signed provider
   conformance receipt with execution still disabled.
6. Push only after reviewing the complete diff and user-owned files. Inspect all
   six hosted CI jobs; retry only infrastructure failures, never product or
   safety failures.
7. Update the acceptance matrix with direct run URLs/artifact identifiers and
   exact tool versions. Only then reassess the overall completion gate.

## Completion decision

Stages 1–4 and 9 pass locally. Stages 5–8 have complete local implementations
but retain the explicit external gates above. Stage 10's native and static
release checks pass, while hosted Linux/macOS/Windows evidence is pending.
Therefore the overall goal remains incomplete by design.
