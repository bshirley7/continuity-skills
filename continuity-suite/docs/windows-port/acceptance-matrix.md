# Native Windows Acceptance Matrix

Status values: `not-started`, `in-progress`, `passing`, `blocked`, `not-applicable`.
Every `passing` row must cite direct current evidence. The overall port is not
complete while any required row lacks passing evidence.

| ID | Requirement | Status | Required evidence |
| --- | --- | --- | --- |
| 1.1 | Native Windows process locking | passing | `test_runtime`: separate-process exclusion, termination release, concurrent append |
| 1.2 | Atomic persistence and interruption recovery | passing | `test_runtime`: replacement retry, killed writer, stale-temp recovery |
| 1.3 | Canonical project-relative paths | passing | shared POSIX serializer, manifest-path test, full suite |
| 1.4 | UTF-8 and locale independence | passing | Unicode path/content plus CLI output under forced legacy `cp1252` stdio |
| 1.5 | Windows ACL protection | passing | native effective-rights inspection covers `Everyone`, `Authenticated Users`, `BUILTIN\\Users`, and `BUILTIN\\Guests`; install/reinstall transactionally hardens root, child directory, and file DACLs and rolls back on unsafe trees or failed verification |
| 1.6 | Long path behavior | passing | >260-character Unicode atomic-write round trip |
| 1.7 | Case-insensitive collisions | passing | normalized collision detector plus installer preflight |
| 1.8 | Symlink/junction/reparse containment | passing | real Windows junction escape rejection |
| 1.9 | OneDrive workspace support | passing | OneDrive runtime smoke plus path-with-spaces install/doctor |
| 1.10 | UNC/mapped-drive policy | passing | explicit fail-closed remote-drive profile and test |
| 1.11 | Transient sharing violations | passing | bounded idempotent replacement retry test |
| 1.12 | Cancellation and crash recovery | passing | killed-lock/writer tests plus Job Object-backed grandchild termination on timeout |
| 1.G | Stage 1 completion gate | passing | every native Windows row passes; hosted Ubuntu and macOS regressions pass on Python 3.11 and 3.14 in [run 29563386124](https://github.com/bshirley7/continuity-skills/actions/runs/29563386124) |
| 2.1 | Native installer and deterministic interpreter | passing | OneDrive install binds `sys.executable`; doctor verifies it |
| 2.2 | PowerShell, CMD, and VS Code launchers | passing | both installed launchers preserve argv/exit codes from a different cwd; CMD bypasses restricted PowerShell policy |
| 2.3 | Dependency discovery and diagnostics | passing | doctor reports Python/Git/gh/age/age-keygen/ssh-keygen and conditional requirements |
| 2.4 | Release and line-ending determinism | passing | `.gitattributes`, deterministic rebuild, POSIX manifest keys |
| 2.5 | Drift, reinstall, upgrade, rollback, legacy migration | passing | focused lifecycle test passes natively on Windows |
| 2.6 | Safe uninstall | passing | dry-run-first uninstall preserves private state and user skill |
| 2.7 | Cross-platform project migration | passing | simulated POSIX interpreter binding is safely rebound on Windows while private state and POSIX path keys survive |
| 2.G | Stage 2 completion gate | passing | OneDrive install/doctor, CMD/PowerShell, autocrlf matrix, lifecycle, migration, and uninstall tests pass |
| 3.1 | Capture and triage | passing | complete native suite workflow coverage |
| 3.2 | Memory and roadmap | passing | complete native suite workflow coverage |
| 3.3 | Planning, reporting, sharing, disabled approval | passing | complete native suite workflow coverage |
| 3.4 | Private-state and chat-context isolation | passing | private sentinel is Git-ignored and absent from AGENTS, CLAUDE, skill, and command auto-context surfaces |
| 3.5 | Canonical machine handoffs across agents | passing | Codex/Claude skill trees match byte-for-byte and CMD/PowerShell return the same non-authorizing handoff |
| 3.G | Stage 3 completion gate | passing | all 63 end-to-end `ContinuityTest` workflows pass natively on Windows |
| 4.1 | Local execution locks | passing | process lock and project-lock tests |
| 4.2 | Remote lease lifecycle across two clones | passing | local bare remote, two clones, contention/release/reacquire |
| 4.3 | Renewal, binding, expiry, replay, wrong-goal/attempt, skew | passing | remote renewal/binding commits, ancestry validation, stale-receipt rejection, skew fail-closed, expiry recovery |
| 4.G | Stage 4 completion gate | passing | complete two-clone lease scenario passed five consecutive native Windows runs |
| 5.1 | Official age.exe and age-keygen.exe discovery | passing | WinGet installed official `FiloSottile.age` v1.3.1; both executables report v1.3.1 and doctor discovers them; independently downloaded Windows archive matches upstream SHA-256 `c56e8c…8154`; expired publisher certificate is recorded as non-passing rather than misrepresented |
| 5.2 | Encrypt, verify, restore, rollback | passing | official native tools encrypted and immediately verified state in a Unicode OneDrive path with spaces; independent verify, dry-run, restore, verified safety backup, rollback, ciphertext tamper rejection, stale-checkpoint rejection, and protocol adversarial fixtures pass |
| 5.3 | Backup interruption, staging, ACLs, secret redaction | passing | staged publish cleanup, secure temp DACL checks, journaled crash recovery, no-overwrite and redaction assertions |
| 5.G | Stage 5 completion gate | passing | official native age v1.3.1 lifecycle passes with execution disabled, external signed checkpoint, confined staging, secure DACLs, no-overwrite behavior, rollback, and no exact key leakage across 521 evidence files |
| 6.1 | Native gh.exe and isolated mocks | passing | official gh.exe 2.83.2 executes natively; isolated mocks never contact GitHub; active GitHub.com auth plus the read-only user API succeeded on 2026-07-17 |
| 6.2 | GitHub.com/Enterprise identity and PR binding | passing | live read-only lookup resolved exactly `bshirley7/continuity-skills` with default branch `main`; Enterprise, repository/URL/account mismatch, check, reviewer, base, and full-head binding tests pass |
| 6.3 | Exact guarded human merge | passing | Enterprise-hosted mock binds origin/PR/base/head/account, exact authorization, and `--match-head-commit`; wrong account/text fail before mutation and no auto/admin flags occur |
| 6.G | Stage 6 completion gate | passing | native authenticated read-only identity/repository verification and the complete network-isolated guarded-delivery matrix pass; no live merge or repository mutation was used as acceptance evidence |
| 7.1 | Provider render/register/heartbeat/claims | passing | Codex and Claude Desktop definitions use absolute native shell-free argv and self-contained prompts with an explicit raw-literal placeholder contract; path/metachar transport, real registration, provider-native heartbeats, and one-time claims pass |
| 7.2 | Capacity, retry, stale recovery, process cancellation | passing | portfolio capacity race, retry/backoff, stale run/lock/lease recovery, and Job Object process-tree cancellation pass |
| 7.3 | No-op provider conformance | passing | ChatGPT desktop 26.715.2305.0 kept the registered local Codex task paused while two manual provider-native sweeps ran; one due report claim completed as a no-op and the second sweep returned no due/retry work. The live adapter verifier observes two distinct sweeps, one successful no-op, and current-behavior replay/stale/second-clone rejection artifacts; the focused Windows protocol rehearsal also verifies the signed-receipt path. Provider task ID is retained only as private state and referenced here by SHA-256 `f51fecc373a8c104554601fb5485d12a98fe19495355fbfd4d39354fec4ac0f4`. |
| 7.G | Stage 7 completion gate | passing | `scheduler adapter codex verify` is healthy with two provider-native sweeps, one claimed no-op, and all three fail-closed probes; `project doctor` is healthy, the task remains paused, and project execution remains disabled |
| 8.1 | Codex discovery and invocation in VS Code | passing | authenticated Codex extension 26.707.91948 in a trusted native VS Code window rooted at `C:\Users\Nick\OneDrive\Documents\DEV\continuity\Continuity Age Acceptance Ω` showed all 14 Continuity entries through `/skills` and invoked `$continuity-report` in report-only mode without mutation |
| 8.2 | Claude discovery and invocation in VS Code | passing | authenticated Claude Code extension 2.1.212 loaded 14 project skills and 14 matching legacy commands from the same exact project root; `/skills` discovery and `/continuity-report` report-only invocation passed without mutation |
| 8.3 | Multi-root, cwd, trust, reload, remote distinctions | passing | nested-cwd and unrelated-cwd/explicit-root tests pass; installed trust/first-root/remote-host behavior and current official product contracts are documented with fail-closed operating rules |
| 8.4 | Simultaneous agents and canonical authority | passing | simultaneous CMD and PowerShell capture mutations both persist under the same native lock; byte-identical adapters and non-authorizing machine handoff are asserted |
| 8.G | Stage 8 completion gate | passing | Codex and Claude discovered and invoked the same canonical project-local Continuity suite in the corrected trusted Unicode/path-with-spaces workspace; execution remained disabled, the invocation was read-only, and no private operational state was exposed |
| 9.1 | Malicious paths/refs/config/archive defense | passing | portable NFC/path-device/ADS/control checks, case/Unicode collision detection, bounded streaming archive extraction, strict rollback metadata and junction confinement, adversarial tests |
| 9.2 | Option/command injection defense | passing | validated Git remote/ref/object/branch and SemVer selectors; native direct argv parser rejects shells, batch wrappers, operators, and inline credential flags |
| 9.3 | ACL, credentials, dependencies, secret redaction | passing | native ACL tests, filtered validation environment, centralized persisted/error redaction, exact tzdata 2026.3 pin with two SHA-256 hashes |
| 9.4 | Windows threat model | passing | `docs/security-threat-model.md` covers assets, adversaries, trust boundaries, controls, operator duties, and residual risk |
| 9.G | Stage 9 completion gate | passing | security-focused suite plus complete 119-test native regression passes without weakened gates |
| 10.1 | Complete native Windows suite | passing | final native audit after scheduler placeholder hardening: 119 tests passed in 491.345 seconds on Python 3.13.6 with the updated acceptance documentation and release manifest |
| 10.2 | Linux and macOS suites | passing | Ubuntu and macOS pass on Python 3.11 and 3.14 at exact audit head `d977490adcd7eeb8664c5a74b13107c2b58f9b0b` in [run 29564361138](https://github.com/bshirley7/continuity-skills/actions/runs/29564361138) |
| 10.3 | CI matrix and no safety skips | passing | all six Windows/macOS/Ubuntu × Python 3.11/3.14 jobs pass distribution validation, the complete suite, and diff hygiene in [run 29564361138](https://github.com/bshirley7/continuity-skills/actions/runs/29564361138); the hosted-only OneDrive environmental smoke is separately covered by the real native OneDrive run |
| 10.4 | Skill, compile, manifest, docs, dependency checks | passing | 13 skills, 9 Python sources, 129 local Markdown links, one two-hash exact dependency, and 139 release files validate |
| 10.5 | Requirement-by-requirement completion audit | in-progress | `final-audit.md` now reconciles the provider-native Scheduled evidence; final source, manifest, native-suite, and six-cell CI evidence must be refreshed for the placeholder-hardening commit |
| 10.G | Stage 10 completion gate | in-progress | every functional acceptance gate passes; final native validation and hosted Windows/macOS/Ubuntu matrix must pass on the updated exact branch head before release readiness is complete |
