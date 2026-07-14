# Continuity Contract

## Governing rule

Treat notes as project knowledge first. Only a deliberately promoted, decision-complete, explicitly approved, and dispatched goal authorizes execution.

## Assurance standard

Every skill must read and apply `development-assurance-standard.md`. The project configuration, project manifest, dispatch record, and goal compliance ledger must use the supported assurance-standard version. Missing or incompatible versions fail closed before execution or completion.

## Project behavior configuration

- Use `$continuity` as the guided configuration and routing entry point.
- Store effective project-specific settings in `.continuity/project-behavior.json` and generate `.agents/skills/continuity-local/SKILL.md` from that committed record.
- Apply the generated local behavior skill with every task-specific continuity skill. Configuration, manifest, behavior record, and generated skill hashes must agree.
- Permit explicit overrides only for documented project settings such as schedules, validation, documentation map, evidence mode, branch prefix, runtime, and execution enrollment.
- Never allow project configuration to weaken the fixed authorization, concurrency, security, merge-safety, force-push, auto-merge, or human-merge guardrails.
- Record configuration changes in the ignored append-only audit ledger and fail closed on manual drift.

## Data boundaries

- Keep skills, configuration, schedule intent, notes, memory, approvals, execution, and evidence authoritative inside the enrolled project.
- Treat any developer-local scheduler as a discovery and triggering layer only. It may aggregate sanitized reports but must not own project instructions or private state.
- Register one provider-owned portfolio supervisor in developer-local state. It must calculate due project actions from each project's timezone and schedule, enforce idempotency, retries, stale-run recovery, and portfolio concurrency, and start an isolated project task for every due action.
- Keep scheduler registration receipts, workspace roots, run events, task IDs, heartbeats, and recovery records private and project-local. A selected provider without a current registration receipt is unhealthy.
- Keep raw captures, queues, approvals, generated indexes, configuration audit records, and task locks under `.continuity/private/`.
- Keep trusted, sanitized project memory under `docs/project-memory/`.
- Keep canonical, sanitized roadmap Markdown under `docs/project-roadmap/`; ignored SQLite and JSON projections may merge committed records with local goal and note-link context.
- Keep approved shared packets under `.continuity/shared-notes/packets/`. Packets are context only and never authorize execution or canonical changes.
- Exclude private state from Git and default memory search.
- Preserve provenance and append-only feedback. Never silently overwrite changed understanding.

## Note classifications

Use exactly one primary classification for every atomic item: `context`, `insight`, `decision`, `question`, `documentation-candidate`, `backlog-candidate`, `execution-candidate`, or `explicit-instruction`.

Set `execution_authorized: false` during capture and triage. Classify ambiguity as context, a question, or a held candidate.

## Goal states

Use: `awaiting-feedback`, `approved`, `queued`, `dispatched`, `running`, `validating`, `review-ready`, `completed`, `partially-completed`, `blocked`, `cancelled`, or `held`.

Approval and dispatch are separate events. Bind approval to the exact plan version and SHA-256 material hash. Any plan or machine-goal edit invalidates approval.
Only the human's explicit approval text and identity may populate an approval record; an agent must never generate or infer them. State transitions are enforced and terminal states cannot be restarted.
Overnight execution ends at `review-ready` after every pre-human-review gate and PR artifact passes. Human review without merge leaves the goal review-ready. Only recorded human merge evidence moves it to `completed`.

## Planning artifacts

- Use an evidence triage brief to verify action candidates against current behavior, existing implementations, and prior decisions.
- Use a decision map when a destination still contains material unresolved decisions. Human-required decisions cannot be answered by the agent or treated as execution discretion.
- Use acyclic, dependency-aware end-to-end delivery slices for multi-part outcomes. Every slice remains `planning-candidate` and `execution_authorized: false` before parent-goal approval and dispatch.
- Include planning artifacts in the immutable goal material hash. Changing content or edges invalidates approval.
- Keep artifacts local by default. A configured external tracker is a preferred surface only; creating or modifying tracker items requires separate explicit human approval.

## Required compliance stages

Record evidence for every responsible development stage:

1. capture-triage
2. memory-retrieval
3. roadmap-retrieval
4. plan-review
5. approval
6. execution-preflight
7. implementation
8. code-review
9. validation
10. security-review
11. merge-safety
12. documentation
13. memory-impact
14. roadmap-impact
15. final-alignment
16. human-review

Use `passed`, `failed`, `pending`, or `not-applicable`. A `not-applicable` result requires a concrete reason. Do not mark a goal review-ready while any pre-human-review stage is pending or failed, and do not mark it completed without passed human-review and merge evidence.

## Developer and security guardrails

- Read the repository `AGENTS.md`, configured documentation map, and memory brief before planning or changing files.
- Confirm the current integration branch and remote state before implementation and again before PR handoff.
- Use an isolated worktree and a goal-focused branch.
- Preserve a clean separation between approved scope and newly discovered work.
- Prefer the project’s established architecture, types, interfaces, tests, and dependency-management conventions.
- Review the diff for correctness, maintainability, accessibility, performance, privacy, and security as applicable.
- Run project-prescribed tests, type checks, builds, linters, format checks, and targeted regression tests.
- Run evidence-based security review for touched languages and frameworks. Check secrets, dependencies, data handling, authentication/authorization, injection, unsafe paths, subprocess use, migrations, and supply-chain changes as relevant.
- Record quality evidence through the structured test report and merge-safety evidence through the structured merge assessment when those skills are installed.
- Use parameterized APIs and subprocess argument arrays. Never construct shell commands from captured note text.
- Never log, commit, or place secrets or raw private captures in PR documentation.
- Never force-push, auto-merge, disable safeguards, or use destructive Git recovery without explicit authorization.
- Stop on an unapproved product decision, failed required gate, stale approval, unmet dependency, or merge conflict.
- Stop on production data changes, credentials, billing, infrastructure mutation, external publishing, destructive actions, or any other restricted side effect unless the exact action has fresh human approval in the current goal.

## Memory contract

Committed Markdown is canonical. SQLite FTS5 is a rebuildable ignored index. Every structured entry records stable ID, title, type, system, summary, status, tags, aliases, timestamps, verified code state, sources, relationships, confidence, and unresolved gaps.

Use statuses `current`, `proposed`, `disputed`, `superseded`, or `historical`. Supersede rather than delete. Default search includes trusted memory only.

## Roadmap and shared-note contract

Committed roadmap Markdown is canonical. A goal must retrieve relevant roadmap context and include exact `roadmap_ids` plus structured `roadmap_impact` in its approval hash. Releases and milestones express commitments; sprints and estimates are optional and never authorize execution. The local admin sidecar is read-only, loopback-only, and excluded from application source and every preview, staging, or production artifact.

Raw captures remain private. Sharing requires a selected sanitized packet, exact version and target approval, an isolated branch, privacy and secret checks, and a human-reviewed PR. Imported packets enter private triage with `execution_authorized: false` and cannot update roadmap, memory, goals, code, systems, or another developer's private state.

## Completion evidence

Every goal PR must include request alignment, implementation report, validation and security results, memory impact, roadmap impact, and evidence. A review-ready PR requires all automated and agent review gates to pass. Human review and merge remain user actions.
