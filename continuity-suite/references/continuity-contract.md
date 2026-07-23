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
- Never allow project configuration to weaken the fixed authorization, concurrency, security, product-conformance, merge-safety, force-push, auto-merge, or human-merge guardrails.
- Record configuration changes in the ignored append-only audit ledger and fail closed on manual drift.
- Install and update from tagged, attested, hash-manifested releases. Abort on locally modified suite-managed files, snapshot before replacement, and never treat project configuration or ignored private state as release-owned.

## Data boundaries

- Keep skills, configuration, schedule intent, notes, memory, approvals, execution, and evidence authoritative inside the enrolled project.
- Treat any developer-local scheduler as a discovery and triggering layer only. It may aggregate sanitized reports but must not own project instructions or private state.
- Register one provider-owned portfolio supervisor in developer-local state. It must calculate due project actions from each project's timezone and schedule, enforce idempotency, retries, stale-run recovery, and portfolio concurrency, and start an isolated project task for every due action.
- Treat registration as a lease, not proof of permanent health. Every authenticated sweep must refresh the matching task, provider, workspace-root, configuration-hash, and behavior-hash heartbeat. Expired or mismatched liveness is unhealthy.
- Reserve due work atomically under the shared portfolio lock. Count active runs and unconsumed reservations against capacity, issue short-lived one-time claims, and require the child task to consume the exact project, action, idempotency key, due goal, and supervisor claim before it starts.
- Keep scheduler registration receipts, workspace roots, run events, task IDs, heartbeats, claims, and recovery records private and project-local.
- Before scheduled code-changing dispatch, acquire the project's fast-forward-only remote lease. A concurrent acquisition, stale local receipt, or unavailable remote fails closed. Review and reporting remain read-only and do not require an execution lease.
- Protect private JSON writes with atomic replacement and serialize private mutations. Append integrity metadata to new JSONL records and fail doctor checks on chain, sequence, or record-hash corruption.
- Back up private state only to verified encrypted archives. Keep encryption identities outside projects and stage every restore after project and payload verification.
- Keep raw captures, queues, approvals, generated indexes, configuration audit records, and task locks under `.continuity/private/`.
- Keep trusted, sanitized project memory under `docs/project-memory/`.
- Keep canonical, sanitized roadmap Markdown under `docs/project-roadmap/`; ignored SQLite and JSON projections may merge committed records with local goal and note-link context.
- Keep approved shared packets under `.continuity/shared-notes/packets/`. A packet approval must bind the packet ID, exact version, target project, content hash, identity, approval text, timestamp, and nonce. In a signed-approval project, it must also be SSH-signed by a project-trusted approver. Re-verify the receipt before publication. Packets are context only and never authorize execution or canonical changes.
- Exclude private state from Git and default memory search.
- Preserve provenance and append-only feedback. Never silently overwrite changed understanding.

## Note classifications

Use exactly one primary classification for every atomic item: `context`, `insight`, `decision`, `question`, `documentation-candidate`, `backlog-candidate`, `execution-candidate`, or `explicit-instruction`.

Preserve the capture time and classify occurrence type, internal/external perspective, sentiment, impact, confidence, actionability, stakeholders, themes, and any explicit pattern key. Positive outcomes are evidence worth preserving, not noise. Repeated changes, behaviors, needs, risks, and failures should inform adaptability and future planning without becoming automatic instructions.

## Skill improvement

Treat each installed `SKILL.md` as the protected operational contract and its `references/learned-playbook.md` as the only usage-evolvable layer. Record only sanitized structured outcomes bound to the exact skill and playbook hashes. Raw transcripts, prompts, responses, tool arguments, tool output, note content, credentials, personal data, customer data, and absolute paths are never improvement input.

Repeated usage may produce a non-authorizing pattern and a bounded learned-playbook candidate. Frequency, user silence, agent confidence, and model preference do not prove correctness. Candidate selection requires fixed validation improvement, an untouched non-regressing test set, passed authority/privacy/protected-contract/state-accuracy invariants, no recorded regressions, and explicit human review. Rejected candidates remain evidence. Review and packaging never edit installed skills, authorize execution, or publish a release; applying an approved package requires a separately approved suite-source goal and normal validation, review, merge, release, and installation controls.

A single source may yield one or many atomic notes. For meeting, conversational, or aggregated feedback input, retain one stable source reference and source timestamp while assigning a stable item ID and lifecycle to every semantically distinct decision, need, feedback item, question, risk, or later idea. Do not split mechanically by line or bullet, and do not merge items merely because they arrived in one message. Record multi-item input as `capture_mode: batch`; keep each item's routing, planning disposition, goal relationships, timestamps, and work status independent.

Set `execution_authorized: false` during capture and triage. Classify ambiguity as context, a question, or a held candidate.

## Goal states

Use: `awaiting-feedback`, `queued`, `dispatched`, `running`, `validating`, `review-ready`, `changes-requested`, `completed`, `partially-completed`, `blocked`, `cancelled`, or `held`. `proposed-plan` and `approved` are readable legacy states that require explicit `goal revise` migration; new operations do not emit them.

Approval and dispatch are separate events. Bind approval to the exact plan version, SHA-256 material hash, behavior hash, project, approver identity, timestamp, and nonce. Any plan or machine-goal edit invalidates approval.
Only the human's explicit approval text and recorded identity may populate a current approval record; an agent must never generate or infer them or select a signing key. In a signed-approval project, the approval must also carry an SSH signature from a project-trusted approver, and in remote production mode the local approver allowlist must match its fetched integration-branch copy byte-for-byte. `approval trust add` prepares a tracked change but grants no authority until protected human review merges it and the integration branch is fetched. Unsigned local approvals remain readable history but cannot authorize execution in a signed-approval project.

State transitions are enforced. Every human disposition and every in-scope resume in a signed-approval project carries an SSH-signed receipt bound to project, goal, plan hash/version, execution attempt, identity, timestamp, nonce, and the applicable evidence or authorization text. `changes-requested`, `blocked`, and `partially-completed` may reopen only through that explicit signed authorization naming the goal and approved plan version. Reopening archives the prior attempt, starts a fresh execution manifest, and invalidates downstream evidence; changed scope requires revision and fresh approval.
Overnight execution ends at `review-ready` after every pre-human-review gate and PR artifact passes. Human disposition is structured as `approved`, `changes-requested`, `merged`, or `closed`. Only recorded human merge evidence moves a goal to `completed`.

Fresh source-bound evidence is required for `approved` and `merged`. A human may still record `changes-requested` or `closed` when delivery evidence is stale or unavailable because those dispositions do not authorize delivery; the human-review record preserves the evidence failure. `goal cancel --actor <human> --reason <reason>` also remains available from `review-ready` as an audited fallback when no PR disposition can be recorded.

When remote leasing is required, every code-changing start requires an active remote lease for the exact goal execution attempt. Scheduled start additionally binds the lease to the provider run, task, idempotency key, owner fingerprint, and remote lease commit. Only the matching dispatch finish or an explicit exact goal-attempt release may release it.

All project-local CLI operations serialize through the project-state lock. Backup, restore, and signed checkpoint creation additionally require no active execution goal, scheduler run, or project execution lock. Production backups must be decrypted and inventory-verified immediately. A signed checkpoint outside the repository anchors JSONL record counts and chain heads; current ledgers may extend it but may not truncate or rewrite its anchored prefix.

Use `continuity workflow status` as the machine handoff contract. Select an exact capture, note, memory, roadmap, packet, or goal whenever an ID is available; project-wide status is routing context only. Skills must inspect the applicable status on entry and report it on exit. Its stage, subject IDs, inputs, outputs, decisions, blockers, evidence, next skill, human requirements, allowed command templates, and blocked actions do not authorize human-required actions by themselves. An action may appear in `allowed_actions` only when its current state and evidence prerequisites pass; unavailable actions belong in `blocked_actions` with exact reasons.

Manual end-to-end work uses `$continuity-workflow` as a sequential orchestrator. A task skill stopping on a failed gate stops that unsafe stage transition, not the overall workflow: return control to the orchestrator, record the failure, route to the machine-selected remediation skill, and continue after fresh evidence passes. Do not yield between routine skill handoffs or for status alone. Pause only when the current handoff or selected action explicitly sets `human_required: true`, and resume from canonical state after the human records an allowed approval. If a non-human fault has no safe immediate repair, keep the workflow pending at the same stage with a durable diagnostic; never bypass the gate or report false completion.

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
11. product-conformance
12. merge-safety
13. documentation
14. memory-impact
15. roadmap-impact
16. final-alignment
17. human-review

Use `passed`, `failed`, `pending`, or `not-applicable`. A `not-applicable` result requires a concrete reason. Do not mark a goal review-ready while any pre-human-review stage is pending or failed, and do not mark it completed without passed human-review and merge evidence.

## Developer and security guardrails

- Read the repository `AGENTS.md`, configured documentation map, and memory brief before planning or changing files.
- Confirm the current integration branch and remote state before implementation and again before PR handoff.
- Confirm the active remote execution lease before scheduled implementation and release it when the run finishes.
- Use an isolated worktree and a goal-focused branch.
- Preserve a clean separation between approved scope and newly discovered work.
- Prefer the project’s established architecture, types, interfaces, tests, and dependency-management conventions.
- Review the diff for correctness, maintainability, accessibility, performance, privacy, and security as applicable.
- Run project-prescribed tests, type checks, builds, linters, format checks, and targeted regression tests.
- Run evidence-based security review for touched languages and frameworks. Check secrets, dependencies, data handling, authentication/authorization, injection, unsafe paths, subprocess use, migrations, and supply-chain changes as relevant.
- Execute configured validation and security commands without a shell, prove the worktree belongs to the enrolled repository and its actual branch matches the goal execution record, record argv/output/status, and bind the machine run to the approved plan hash, project behavior hash, commit, repository identity, and a source fingerprint covering tracked and untracked content. Reconcile applicable product behavior against approved goals, project-intent documents, documentation, memory, insights, and roadmap through a candidate product audit bound to the same source state. A passing report, product audit, or merge assessment must reject absent or stale machine evidence. The enforced delivery order is implementation, candidate checks, documentation/memory/roadmap/evidence artifacts, commit, final source-bound tests, product conformance, push and draft PR, PR/head/base-bound merge assessment, `review-ready`, then human disposition.
- Record quality evidence through the structured test report and merge-safety evidence through the structured merge assessment when those skills are installed.
- Require successful configured hosted checks before review-ready, then verify authenticated GitHub identity, review decision, and reviewer threshold before recording approval or merge.
- Use parameterized APIs and subprocess argument arrays. Never construct shell commands from captured note text.
- Never log, commit, or place secrets or raw private captures in PR documentation.
- Never force-push, use administrator bypass, auto-merge, disable safeguards, or use destructive Git recovery. An opted-in direct GitHub CLI merge is allowed only from `review-ready`, after an interactive human authorization is bound to the exact goal, PR URL, full assessed head SHA, merge method, and authenticated GitHub identity; recheck every hosted and reviewer gate immediately before the side effect and verify the merge afterward.
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

Every goal PR must include request alignment, implementation report, validation and security results, product conformance, memory impact, roadmap impact, and evidence. A review-ready PR requires all local, hosted, and agent review gates to pass. Human review and merge remain user actions; an explicitly enabled interactive CLI merge is a user action only when its exact authorization is persisted and GitHub verifies the same head and actor. Portfolio output must use the deterministic sanitized CLI allowlist rather than agent-authored aggregation.
