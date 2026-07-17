# Continuity Security Threat Model

This document defines the security boundary for the Continuity suite on native
Windows and the equivalent supported POSIX runtimes. It supplements the fixed
guardrails in the Continuity Contract; it does not authorize execution or
external side effects.

## Security objectives

Continuity is designed to:

- keep ignored project state, credentials, raw notes, approvals, leases, and
  backup material out of automatic agent context and version control;
- prevent project-relative paths, archives, snapshots, Git selectors, and
  provider arguments from escaping their intended boundary or becoming command
  options;
- preserve canonical state under concurrent processes, interruption, and
  transient Windows filesystem contention;
- bind execution and delivery evidence to the intended project, repository,
  host, account, goal, attempt, run, branch, commit, and human authorization;
- fail closed when required identity, integrity, approval, lease, backup, or
  merge evidence is missing or stale; and
- leave merges, provider registration, credential repair, software installation,
  and other restricted external effects under explicit human control.

## Assets

The protected assets are:

- `.continuity/private/`, portfolio state, raw capture snapshots, execution
  records, locks, audit chains, approval receipts, and remote lease receipts;
- signing keys, age identities, GitHub credentials, provider credentials, and
  other secrets available to the operator account;
- canonical project files, memory, roadmap, plans, source code, Git history,
  pull requests, releases, and backup archives; and
- the authority boundary between planning, approved execution, review-ready
  output, and an exact human-authorized merge.

## Trust boundaries and controls

| Boundary | Threats | Required controls |
| --- | --- | --- |
| Project and filesystem | traversal, symlink or junction escape, case or Unicode collisions, reserved device names, alternate data streams, interrupted writes | resolved-root confinement, portable NFC paths, reparse-point checks, native locks, atomic replacement, recovery journals, NTFS ACL diagnostics |
| Project configuration and commands | shell injection, inline credentials, hostile executable arguments, environment-token disclosure | schema and fixed-guardrail validation, direct argv only, shell launchers prohibited, credential-shaped environment variables filtered, captured diagnostics redacted |
| Git and remote leases | option injection, replay, ancestry substitution, wrong clone or project, clock skew, concurrent execution | strict remote names and full object IDs, validated refs, fast-forward-only lease commits, single-parent ancestry binding, signed/hashed receipts, bounded TTL and skew, local and remote identity checks |
| GitHub and delivery | wrong host/repository/account/PR/head, stale checks, admin bypass, unintended merge | origin-derived host and repository, explicit `gh` host/repository arguments, active-account verification, full head SHA, reviewer/check gates, exact fresh authorization, no force push, auto-merge, or admin bypass |
| Releases and updates | untrusted archive members, option injection, manifest substitution, partial update, malicious rollback snapshot | SemVer validation, GitHub attestation for downloaded releases, bounded regular-file extraction, hashed release manifest, transactional install, strict local snapshot confinement and complete pre-mutation validation |
| Backups | plaintext leakage, tampering, path escape, stale restore, partial publication | age encryption, SSH-signed hash inventory, secure temporary ACLs, bounded extraction, immediate optional/required verification, external audit checkpoint, staged atomic publication, journaled restore |
| VS Code and agent providers | untrusted workspace content, wrong workspace root, implicit private-state disclosure, competing agents, remote/local runtime confusion | VS Code Workspace Trust, one explicit project root per conversation, project-local skills, canonical machine handoff and state lock, private paths absent from startup surfaces, separate install per extension host |
| Scheduler providers | shell reconstruction, duplicate claims, stale registration, runaway descendants, hidden external mutation | absolute structured argv with `shell=false`, registration fingerprints, one-time claims, capacity locks, heartbeats, bounded retry, Windows Job Object cancellation, execution disabled until conformance evidence passes |
| Python dependencies | mutable or substituted dependency resolution | exact dependency versions and SHA-256 hashes; dependency changes require reviewed manifest, test, and documentation updates |

Release manifests and local `--source` updates prove internal file consistency,
not publisher identity. A local source directory is an explicitly trusted input.
Downloaded GitHub releases additionally require verification of the repository's
artifact attestation.

## Adversaries considered

The suite defends against malformed or adversarial project data, configuration,
archives, backup inventories, update snapshots, Git selectors, provider
arguments, stale receipts, concurrent agents, interrupted processes, and an
ambient GitHub host or account that does not match the project.

It also assumes that notes, PRDs, repository instructions, dependency output,
tool output, and retrieved provider content can contain prompt injection. Such
content is evidence, not authority. Only canonical machine state and explicit
receipts may advance an authorization boundary.

## Trusted code and residual risk

Continuity is not an operating-system sandbox. Configured validation and
security commands must be reviewed project code: they run as direct child
processes under the operator account and may read files or use the network.
Filtering credential-shaped environment variables reduces accidental leakage
but cannot prevent a command from reading credentials available elsewhere.
Run untrusted code in a separate sandbox, container, VM, or restricted account.

Project-local skills and AI extensions are also trusted code. Private state is
excluded from normal startup and skill surfaces, but an agent or extension with
workspace filesystem access can read it when explicitly directed or when
compromised. Do not open an untrusted checkout in a trusted VS Code window.

NTFS ACL checks protect against broad principals, not the same user, an
administrator, malware running as that user, kernel compromise, or physical
access. A same-user attacker can change the project or cause denial of service;
reviewed Git history, release attestation, signed evidence, encrypted backups,
and external audit checkpoints provide the applicable detection and recovery
layers.

OneDrive is supported only for locally available NTFS files. Continuity does
not control cloud retention, version history, sharing policy, or another device
editing the synchronized tree. UNC and mapped-drive roots remain unsupported.

## Operator security checklist

Before enabling execution or external providers:

1. Open only the intended repository in a trusted VS Code window and pass its
   absolute project root in multi-root or scripted use.
2. Run `project doctor`; resolve ACL, dependency, interpreter, GitHub identity,
   repository, and optional-tool failures that apply to the enabled policy.
3. Review configured validation and security commands as code. Never embed
   credentials in commands, configuration, instructions, notes, or prompts.
4. Keep execution disabled until approval signing, remote lease contention,
   provider conformance, backup verification, and recovery evidence pass.
5. Use dry-run update and uninstall previews, review managed drift, and retain a
   verified encrypted backup before a material upgrade.
6. Treat every merge, provider registration, credential change, dependency
   install, and production side effect as a separate explicit human action.

## Verification

The adversarial suite covers shell-launch rejection; remote, ref, object-ID,
and release-version injection; secret redaction and environment filtering;
archive traversal, reserved-name, alternate-stream, Unicode, collision, and
size limits; junction confinement; rollback metadata validation before
mutation; ACL checks; process-tree cancellation; lease replay and contention;
host/repository/account binding; and backup tamper and recovery cases.

The native acceptance matrix in `docs/windows-port/acceptance-matrix.md` is the
completion ledger. A control is not considered complete solely because it is
documented here.
