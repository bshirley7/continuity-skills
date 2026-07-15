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
- Treat registration as a lease, not proof of permanent health. Every authenticated sweep must refresh the matching task, provider, workspace-root, configuration-hash, and behavior-hash heartbeat. Expired or mismatched liveness is unhealthy.
- Reserve due work atomically under the shared portfolio lock. Count active runs and unconsumed reservations against capacity, issue short-lived one-time claims, and require the child task to consume the exact project, action, idempotency key, due goal, and supervisor claim before it starts.
- Keep scheduler registration receipts, workspace roots, run events, task IDs, heartbeats, claims, and recovery records private and project-local.
- Keep raw captures, queues, approvals, generated indexes, configuration audit records, and task locks under `.continuity/private/`.
- Keep trusted, sanitized project memory under `docs/project-memory/`.
- Keep canonical, sanitized roadmap Markdown under `docs/project-roadmap/`; ignored SQLite and JSON projections may merge committed records with local goal and note-link context.
- Keep approved shared packets under `.continuity/shared-notes/packets/`. Packets are context only and never authorize execution or canonical changes.
- Exclude private state from Git and default memory search.
- Preserve provenance and append-only feedback. Never silently overwrite changed understanding.

## Note classifications

Use exactly one primary classification for every atomic item: `context`, `insight`, `decision`, `question`, `documentation-candidate`, `backlog-candidate`, `execution-candidate`, or `explicit-instruction`.

Preserve the capture time and classify occurrence type, internal/external perspective, sentiment, impact, confidence, actionability, stakeholders, themes, and any explicit pattern key. Positive outcomes are evidence worth preserving, not noise. Repeated changes, behaviors, needs, risks, and failures should inform adaptability and future planning without becoming automatic instructions.

Set `execution_authorized: false` during capture and triage. Classify ambiguity as context, a question, or a held candidate.

## Goal states

Use: `awaiting-feedback`, `queued`, `dispatched`, `running`, `validating`, `review-ready`, `changes-requested`, `completed`, `partially-completed`, `blocked`, `cancelled`, or `held`. `proposed-plan` and `approved` are readable legacy states that require explicit `goal revise` migration; new operations do not emit them.

Approval and dispatch are separate events. Bind approval to the exact plan version and SHA-256 material hash. Any plan or machine-goal edit invalidates approval.
Only the human's explicit approval text and identity may populate an approval record; an agent must never generate or infer them. State transitions are enforced. `changes-requested`, `blocked`, and `partially-completed` may reopen only through explicit authorization naming the goal and approved plan version. Reopening archives the prior attempt, starts a fresh execution manifest, and invalidates downstream evidence; changed scope requires revision and fresh approval.
Overnight execution ends at `review-ready` after every pre-human-review gate and PR artifact passes. Human disposition is structured as `approved`, `changes-requested`, `merged`, or `closed`. Only recorded human merge evidence moves a goal to `completed`.

Fresh source-bound evidence is required for `approved` and `merged`. A human may still record `changes-requested` or `closed` when delivery evidence is stale or unavailable because those dispositions do not authorize delivery; the human-review record preserves the evidence failure. `goal cancel --actor <human> --reason <reason>` also remains available from `review-ready` as an audited fallback when no PR disposition can be recorded.

Use `continuity workflow status` as the machine handoff contract. Select an exact capture, note, memory, roadmap, packet, or goal whenever an ID is available; project-wide status is routing context only. Skills must inspect the applicable status on entry and report it on exit. Its stage, subject IDs, inputs, outputs, decisions, blockers, evidence, next skill, human requirements, allowed command templates, and blocked actions do not authorize human-required actions by themselves. An action may appear in `allowed_actions` only when its current state and evidence prerequisites pass; unavailable actions belong in `blocked_actions` with exact reasons.

## Planning artifacts

- Use an evidence triage brief to verify action candidates against current behavior, existing implementations, and prior decisions.
- Use a decision map when a destination still contains material unresolved decisions. Human-required decisions cannot be answered by the agent or treated as execution discretion.
- Use acyclic, dependency-aware end-to-end delivery slices for multi-part outcomes. Every slice remains `planning-candidate` and `execution_authorized: false` before parent-goal approval and dispatch.
- Give every source note exactly one approval-hashed disposition: `current-goal`, `later`, `context-only`, or `duplicate`. New goal and scope-changing revision inputs fail closed when dispositions are omitted. Later work requires a review date or roadmap anchor. Only current-goal notes adopt goal execution state.
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
- Execute configured validation and security commands without a shell, prove the worktree belongs to the enrolled repository and its actual branch matches the goal execution record, record argv/output/status, and bind the machine run to the approved plan hash, project behavior hash, commit, repository identity, and a source fingerprint covering tracked and untracked content. A passing report or merge assessment must reject absent or stale machine evidence. The enforced delivery order is implementation, candidate checks, documentation/memory/roadmap/evidence artifacts, commit, final source-bound tests, push and draft PR, PR/head/base-bound merge assessment, `review-ready`, then human disposition.
- Record quality evidence through the structured test report and merge-safety evidence through the structured merge assessment when those skills are installed.
- Use parameterized APIs and subprocess argument arrays. Never construct shell commands from captured note text.
- Never log, commit, or place secrets or raw private captures in PR documentation.
- Never force-push, auto-merge, disable safeguards, or use destructive Git recovery without explicit authorization.
- Stop on an unapproved product decision, failed required gate, stale approval, unmet dependency, or merge conflict.
- Stop on production data changes, credentials, billing, infrastructure mutation, external publishing, destructive actions, or any other restricted side effect unless the exact action has fresh human approval in the current goal.

## Memory contract

Committed Markdown is canonical trusted memory. SQLite FTS5 and local similarity features are rebuildable ignored indexes. Private/all-scope retrieval may include raw captures and their occurrence dimensions for triage and pattern analysis, but those results are not trusted planning evidence until promotion. Every structured canonical entry records stable ID, title, type, system, summary, status, tags, aliases, timestamps, verified code state, sources, relationships, confidence, and unresolved gaps.

Use statuses `current`, `proposed`, `disputed`, `superseded`, or `historical`. Supersede rather than delete. Default search includes trusted memory only.

## Roadmap and shared-note contract

Committed roadmap Markdown is canonical. A goal must retrieve relevant roadmap context and include exact `roadmap_ids` plus structured `roadmap_impact` in its approval hash. Releases and milestones express commitments; sprints and estimates are optional and never authorize execution. The local admin sidecar is read-only, loopback-only, and excluded from application source and every preview, staging, or production artifact.

Raw captures remain private. Sharing requires a selected sanitized packet, exact version and target approval, an isolated branch, privacy and secret checks, and a human-reviewed PR. Imported packet items become private atomic captures with stable packet provenance and `execution_authorized: false`; they can be triaged and searched normally but cannot update roadmap, memory, goals, code, systems, or another developer's private state.

Canonical capture records, plan-hashed note dispositions, per-goal links, goal records, compliance evidence, test and merge reports, and the append-only event ledger determine note lifecycle. `work_status` remains a compatibility summary. `workflow status --note-id` derives the exact stage, stage-entry time, planning disposition, per-goal tracks, local relationship suggestions, and timeline without creating a second mutable status. Goal execution events enter a note timeline only for a `current-goal` link, on or after that link's `decided_at`, and for the applicable plan version. Queue JSONL files are audit history only.

Local similarity may recommend related nonterminal goals. A recommendation never creates scope. Current-goal inclusion requires goal creation or revision and fresh approval; explicit later, context-only, or duplicate relationships remain non-authorizing. Morning reports surface only medium- or high-confidence candidates and cap the number requiring human review; the direct related-goals command remains available for broader investigation.

## Completion evidence

Every goal PR must include request alignment, implementation report, validation and security results, memory impact, roadmap impact, and evidence. A review-ready PR requires all automated and agent review gates to pass. Human review and merge remain user actions.
