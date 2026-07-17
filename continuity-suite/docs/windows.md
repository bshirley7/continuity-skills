# Native Windows Setup and Operation

Continuity supports native Windows with Python 3.11 or newer. Run it from a
local NTFS project directory. OneDrive-synchronized NTFS folders are supported;
UNC paths and mapped network drives fail closed because their locking and
atomic-replacement semantics cannot be guaranteed.

## Prerequisites

Install Python 3.11 or newer and Git for Windows. Then install Continuity's
Python dependency from the suite checkout:

```powershell
python.exe -m pip install -r .\continuity-suite\requirements.txt
```

The requirements file pins the Windows timezone database to an exact release
and verifies either official distribution with SHA-256 hashes. Do not remove
hash checking to work around an installation failure; investigate the package
source, proxy, cache, interpreter, and reviewed dependency version instead.

`project doctor` discovers Git, GitHub CLI, `age`, `age-keygen`, and
`ssh-keygen`. Missing optional tools do not make a planning-only installation
unhealthy. They become required only when the corresponding execution,
GitHub, signed-approval, or verified-backup policy is enabled.

## Install Into a Project

Use absolute paths when the suite and project are in different folders:

```powershell
$Suite = (Resolve-Path .\continuity-suite).Path
$Project = (Resolve-Path C:\Users\Nick\OneDrive\Documents\DEV\my-project).Path
python.exe "$Suite\installer\install.py" `
  --project-root $Project `
  --project-id my-project `
  --integration-branch main `
  --ignore-user-defaults
```

Do not pass `--enable-execution` for the initial install. The installer records
the exact working Python interpreter in
`.continuity/private/python-interpreter.txt`; both Windows launchers use it so
VS Code terminal PATH changes do not silently switch environments.

## Run the Project-Local CLI

The CMD launcher is the most policy-independent entry point and works from
PowerShell, Command Prompt, and a VS Code integrated terminal:

```powershell
& "$Project\.agents\continuity\bin\continuity.cmd" `
  --project-root $Project --json project doctor
```

There is also a PowerShell launcher:

```powershell
& "$Project\.agents\continuity\bin\continuity.ps1" `
  --project-root $Project workflow status
```

If the machine's PowerShell execution policy blocks local scripts, keep using
`continuity.cmd`. Do not weaken the machine-wide policy just for Continuity. A
managed environment may permit the project script, or a one-process diagnostic
can use `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <path>` when
that is allowed by organizational policy. Both launchers forward argument
boundaries and the CLI's exact exit code.

Configured validation and security checks are parsed with native Windows argv
rules and must resolve to an executable without a shell. `cmd.exe`, PowerShell,
POSIX shells, `.cmd`, and `.bat` wrappers are rejected. Prefer native tool
executables, `python.exe -m <module>`, or `node.exe <reviewed-script.js>`; do
not wrap a check in `npm.cmd`, a batch file, a PowerShell script, pipes, or
redirection. Inline credential flags are also rejected, and credential-shaped
environment variables are removed from these child processes.

From Command Prompt:

```bat
"C:\path with spaces\project\.agents\continuity\bin\continuity.cmd" --project-root "C:\path with spaces\project" --json project doctor
```

## GitHub.com and GitHub Enterprise

Continuity derives the delivery host and repository from the project's
`origin` remote. Use one canonical HTTPS, SSH, or Git URL that identifies
exactly `OWNER/REPOSITORY`. Pull-request URLs must use that same host, owner,
and repository. Every `gh` PR command is passed the explicit
`HOST/OWNER/REPOSITORY`; identity checks use the same explicit host. An
ambient `GH_HOST`, a different current directory, or another authenticated
account therefore cannot silently redirect verification.

Check the active account without printing its token:

```powershell
gh.exe auth status --hostname github.com --active
gh.exe api user --hostname github.com --jq .login
```

For GitHub Enterprise, replace `github.com` with the hostname used by
`origin`. Authenticate or switch accounts interactively outside unattended
Continuity work:

```powershell
gh.exe auth login --hostname ghe.example.com
gh.exe auth switch --hostname ghe.example.com --user YOUR-LOGIN
```

Do not use `--show-token`, place tokens in project configuration, or switch an
account during an unattended run. A missing, expired, or wrong active account
fails preflight. GitHub Projects bootstrap also records its hostname in the
approval-bound settings; pass `--hostname ghe.example.com` when preparing an
Enterprise bootstrap.

## OneDrive, Paths, and Filesystem Policy

- Keep the checkout available offline while Continuity is active. A cloud-only
  placeholder is not a usable project file.
- Spaces, Unicode names, and paths longer than 260 characters are supported by
  Continuity's Python persistence layer.
- File replacement retries only transient Windows sharing violations, such as
  short antivirus or sync-client holds. Persistent access failures remain
  errors.
- Project-relative paths are persisted with `/`, so canonical state can move
  between Windows, macOS, and Linux.
- Reinstall after moving a project between operating systems. Reinstallation
  preserves private state and rebinds the project-local launcher to the current
  Python interpreter.
- A case-insensitive path collision fails installation. A junction or symlink
  that resolves outside the project cannot be used as a confined project path.
- UNC and mapped-drive roots are unsupported and `project doctor` reports the
  reason. Clone or copy the repository to a local NTFS folder instead.

## Codex and Claude Scheduled Supervisors

Render the selected provider definition before creating any provider task:

```powershell
& "$Project\.agents\continuity\bin\continuity.cmd" --project-root $Project --json scheduler adapter codex render --root C:\path\to\workspace
& "$Project\.agents\continuity\bin\continuity.cmd" --project-root $Project --json scheduler adapter claude-code render --root C:\path\to\workspace
```

The definition contains an absolute `continuity.cmd` launcher and structured
`supervisor_argv` and `registration_argv` arrays. Provider integrations must
invoke the array directly with `shell=false`; do not reconstruct it through
PowerShell, CMD, or string concatenation. This preserves spaces, Unicode, and
shell metacharacters and makes the task independent of its starting folder.

Use the Claude definition only for a Claude Desktop local scheduled task. A
Claude cloud routine uses a fresh clone and cannot see ignored local Continuity
state. Provider task creation is always a human action. Leave execution
disabled until two sweeps, a claimed no-op, signed replay/staleness/contention
probes, and `scheduler adapter <provider> verify` all pass.

## VS Code Agent Sessions

Enable Codex and Claude Code as project surfaces through `project configure`;
do not install project behavior into a global user skill directory. Open the
project root in a trusted VS Code window, run `project doctor`, and start new
agent conversations after the initial install. Codex reads `AGENTS.md` and
`.agents/skills/`; Claude reads the generated `CLAUDE.md` import and
byte-identical `.claude/skills/` adapters.

Use a separate VS Code window per enrolled project when practical. In a
multi-root window, put the target project first and pass its absolute
`--project-root` to every Continuity command. A WSL, container, SSH, tunnel, or
Codespaces window is a remote runtime and must have its own platform-correct
Continuity install; it must not reuse the native Windows Python binding.

See [VS Code, Codex, and Claude Code](vscode-codex-claude.md) for exact trust,
discovery, invocation, reload, concurrency, private-context, and Remote
Development rules.

See the [Security Threat Model](security-threat-model.md) before enabling
execution, a scheduler provider, signed approvals, GitHub delivery, or backup
and recovery policy.

## Updates, Rollback, and Removal

Use the project-local CMD launcher for the same dry-run-first lifecycle used on
other platforms:

```powershell
& "$Project\.agents\continuity\bin\continuity.cmd" --project-root $Project --json suite status
& "$Project\.agents\continuity\bin\continuity.cmd" --project-root $Project --json suite update --source C:\path\to\continuity-skills --dry-run
& "$Project\.agents\continuity\bin\continuity.cmd" --project-root $Project --json suite uninstall
```

Apply an update or uninstall only after reviewing its preview. Uninstall removes
suite-managed controls and adapters but preserves ignored private state,
project memory, roadmap content, and user-owned skills.

## Troubleshooting

- If `continuity.ps1` is blocked, invoke `continuity.cmd` explicitly.
- If doctor says the installer-bound Python is unavailable, reinstall with the
  intended `python.exe`.
- If timezone loading fails, rerun the requirements installation with that same
  interpreter.
- If doctor reports broad write access on `.continuity/private`, repair the
  inherited NTFS permissions before using sensitive approval or backup state.
- If GitHub authentication fails, repair the active account for the exact
  `origin` hostname with `gh.exe auth login` or `gh.exe auth switch`, then rerun
  the read-only `gh.exe api user --hostname <host> --jq .login` check.
- Run commands from any working directory, but always pass the exact project
  root when scripting or when using a multi-root VS Code workspace.
