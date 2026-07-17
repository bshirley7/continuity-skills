# Native Windows Port Baseline

Recorded: 2026-07-16
Repository commit: `23748d1603c50130d62e7ccb91af5651db94401e`
Branch: `main`
Host: native Windows, OneDrive workspace, Python 3.13.6

## Existing work

The worktree already contains uncommitted Windows-port changes created during
the current user-directed effort. They are preserved as user-owned work:

- conditional `msvcrt`/`fcntl` locking and Windows-safe directory sync;
- Windows platform recognition in doctor and release metadata;
- initial POSIX serialization for capture, roadmap, GitHub settings, and
  install-manifest paths;
- native-Python installer invocation plus a `continuity.cmd` launcher;
- a Windows `tzdata` dependency and introductory README note;
- regenerated release integrity metadata.

No unrelated pre-existing edits were identified.

## Native toolchain

| Tool | Baseline |
| --- | --- |
| Python | 3.13.6 at `C:/Users/Nick/AppData/Local/Programs/Python/Python313/python.exe` |
| Git | 2.49.0.windows.1 |
| GitHub CLI | 2.83.2 installed |
| age / age-keygen | missing |
| VS Code | installed |
| Codex CLI | installed through npm; PowerShell shim blocked by current execution policy |
| Claude CLI | installed through npm; PowerShell shim blocked by current execution policy |

The npm packages also supply `.cmd` launchers, so PowerShell execution policy is
a launcher-selection issue rather than proof that the CLIs are unavailable.

## Test baseline

Command:

```text
python -m unittest discover -s continuity-suite/tests -q
```

Result: 81 tests run in 193.532 seconds; 76 passed, 4 failed, 1 errored.

| Failure | Classification | Relevant area |
| --- | --- | --- |
| Remote lease record is unreadable after fetch | product defect | `bin/continuity`, remote Git lease protocol |
| Encrypted backup cannot find `age` fixture | Windows test harness plus missing external tool | state backup/restore, tests |
| Guarded merge reaches real GitHub | Windows test harness isolation defect | `gh` discovery and merge tests |
| PR mismatch test reaches real GitHub | Windows test harness isolation defect | `gh` discovery and merge tests |
| Legacy-project cleanup cannot remove read-only Git object | Windows test cleanup defect | installer/portfolio test harness |

The release docs still claim only macOS and Linux support, command examples are
primarily POSIX, and the full Windows production contract is not yet proven.

## Capability map

| Capability | Baseline status | Responsible sources | Existing evidence | Windows risk | External tools |
| --- | --- | --- | --- | --- | --- |
| Install and configure | smoke-tested | `installer/install.py`, `lib/runtime.py` | fresh install and doctor previously passed | interpreter binding, paths, rollback cleanup | Python, Git, tzdata |
| Locking and atomic persistence | partial | `lib/runtime.py` | main suite exercises writes | no separate-process contention or crash tests | none |
| Capture and triage | passing baseline | `bin/continuity` | unit/integration tests | remaining backslash serialization sites | none |
| Memory and roadmap | passing baseline | `bin/continuity`, `lib/roadmap.py` | unit/integration tests | canonical paths and sidecar paths | SQLite in Python |
| Planning and approvals | passing baseline | `bin/continuity` | unit/integration tests | timezone and path portability | Git, tzdata, optional SSH |
| Reporting and sharing | passing baseline | `bin/continuity`, `lib/shared_notes.py` | unit/integration tests | path serialization and subprocess fixtures | Git, SSH for signed flows |
| Remote leases | failing | `bin/continuity` | lease test fails | custom-ref fetch/object lookup on Windows | Git |
| Backup and restore | unverified on Windows | `bin/continuity` | POSIX-oriented fixture fails | executable discovery, ACLs, staging, cleanup | age, age-keygen, SSH |
| GitHub PR/merge | unverified on Windows | `bin/continuity`, `lib/github_projects.py` | tests escape mock and reach network | `.exe`/`.cmd` discovery and enterprise hosts | gh, Git |
| Scheduler/provider | tests otherwise pass | `bin/continuity`, `automation/` | scheduler tests pass except lease dependency | Windows task invocation and process trees | provider CLI, Git |
| Codex/Claude adapters | generated but not end-to-end verified | installer and skill adapters | structural tests | PowerShell policy, reload/discovery, concurrent agents | Codex/Claude/VS Code |
| Upgrades and rollback | functional, cleanup error | installer and suite commands | behavior passes until test teardown | read-only Git objects, line endings | Git, gh for tagged releases |
| Release integrity | partial Windows declaration | manifest builder/schema | manifest validates | CRLF/autocrlf determinism not proven | Git |
| Security boundaries | existing suite contract applies | contract, runtime, CLI | broad tests | ACLs, junctions, option injection | Git, gh, age, SSH |

## Immediate conclusions

1. Execution must remain disabled until remote leases, backup/restore, GitHub
   verification, and provider conformance are proven on Windows.
2. Stage 1 needs explicit process-level and failure-injection tests rather than
   relying only on the existing integration suite.
3. Test doubles must be executable on both POSIX and Windows and must never fall
   through to real external services.
4. OneDrive, ACL, long-path, UNC, junction, cancellation, and cross-platform CI
   evidence are currently absent.
