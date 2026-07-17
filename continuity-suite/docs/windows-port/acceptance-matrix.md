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
| 1.5 | Windows ACL protection | passing | native effective-rights inspection for `Everyone` and `BUILTIN\\Users`; doctor fails insecure private state |
| 1.6 | Long path behavior | passing | >260-character Unicode atomic-write round trip |
| 1.7 | Case-insensitive collisions | passing | normalized collision detector plus installer preflight |
| 1.8 | Symlink/junction/reparse containment | passing | real Windows junction escape rejection |
| 1.9 | OneDrive workspace support | passing | OneDrive runtime smoke plus path-with-spaces install/doctor |
| 1.10 | UNC/mapped-drive policy | passing | explicit fail-closed remote-drive profile and test |
| 1.11 | Transient sharing violations | passing | bounded idempotent replacement retry test |
| 1.12 | Cancellation and crash recovery | passing | killed-lock/writer tests plus Job Object-backed grandchild termination on timeout |
| 1.G | Stage 1 completion gate | in-progress | every native Windows row passes; POSIX regression CI remains a Stage 10 dependency |
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
| 7.1 | Provider render/register/heartbeat/claims | passing | Codex and Claude Desktop definitions use absolute native shell-free argv; path/metachar transport, real registration, three heartbeats, and one-time claims pass |
| 7.2 | Capacity, retry, stale recovery, process cancellation | passing | portfolio capacity race, retry/backoff, stale run/lock/lease recovery, and Job Object process-tree cancellation pass |
| 7.3 | No-op provider conformance | in-progress | direct local protocol run observes three sweeps, one claimed no-op, and signed real replay/stale/second-clone contention rejections; provider-native task remains uncreated |
| 7.G | Stage 7 completion gate | blocked | local conformance verifier passes with execution disabled; creating and observing a real Codex automation or Claude Desktop task requires explicit external provider action |
| 8.1 | Codex discovery and invocation in VS Code | in-progress | installed Codex extension 26.707.91948 recognizes `AGENTS.md`/`SKILL.md`; all 14 project skills have valid names and canonical paths; an authenticated `/skills` and invocation smoke remains external |
| 8.2 | Claude discovery and invocation in VS Code | in-progress | installed Claude Code extension 2.1.212 recognizes `CLAUDE.md`, `.claude/skills`, and `.claude/commands`; all 14 adapters and commands match canonical skills; authenticated `/skills` and invocation smoke remains external |
| 8.3 | Multi-root, cwd, trust, reload, remote distinctions | passing | nested-cwd and unrelated-cwd/explicit-root tests pass; installed trust/first-root/remote-host behavior and current official product contracts are documented with fail-closed operating rules |
| 8.4 | Simultaneous agents and canonical authority | passing | simultaneous CMD and PowerShell capture mutations both persist under the same native lock; byte-identical adapters and non-authorizing machine handoff are asserted |
| 8.G | Stage 8 completion gate | blocked | local installation/discovery contracts pass; model-backed Codex and Claude VS Code `/skills` plus one read-only skill invocation require authenticated external provider use |
| 9.1 | Malicious paths/refs/config/archive defense | passing | portable NFC/path-device/ADS/control checks, case/Unicode collision detection, bounded streaming archive extraction, strict rollback metadata and junction confinement, adversarial tests |
| 9.2 | Option/command injection defense | passing | validated Git remote/ref/object/branch and SemVer selectors; native direct argv parser rejects shells, batch wrappers, operators, and inline credential flags |
| 9.3 | ACL, credentials, dependencies, secret redaction | passing | native ACL tests, filtered validation environment, centralized persisted/error redaction, exact tzdata 2026.3 pin with two SHA-256 hashes |
| 9.4 | Windows threat model | passing | `docs/security-threat-model.md` covers assets, adversaries, trust boundaries, controls, operator duties, and residual risk |
| 9.G | Stage 9 completion gate | passing | security-focused suite plus complete 117-test native regression passes without weakened gates |
| 10.1 | Complete native Windows suite | passing | 117 tests passed in 332.623 seconds on Python 3.13.6 after the final distribution audit |
| 10.2 | Linux and macOS suites | blocked | commit `fa00d685767c452fc78dc167307762d831b7ae5b` is published on `windows-compatibility-update`; the workflow intentionally runs feature branches only through `pull_request`, so no hosted run exists until a PR is explicitly authorized |
| 10.3 | CI matrix and no safety skips | in-progress | GitHub parses the published branch workflow as Windows/macOS/Linux × Python 3.11/3.14 with hashed dependency install, complete suite, distribution audit, and diff hygiene; no run exists because the branch is not yet a PR |
| 10.4 | Skill, compile, manifest, docs, dependency checks | passing | 13 skills, 9 Python sources, 129 local Markdown links, one two-hash exact dependency, and 139 release files validate |
| 10.5 | Requirement-by-requirement completion audit | in-progress | `final-audit.md` reconciles every capability and names three remaining external evidence gates; blocked rows cannot yet pass |
| 10.G | Stage 10 completion gate | blocked | local Windows, official native age, authenticated read-only GitHub, and release-readiness evidence pass; provider, VS Code, and hosted cross-platform gates remain |
