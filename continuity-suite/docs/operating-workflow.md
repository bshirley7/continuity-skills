# Continuity Operating Workflow

This guide describes the complete Continuity operating model for projects, campaigns, objectives, and other repository-backed initiatives. It explains what happens during the working day, what may happen during off-hours, what requires human review, and how the next business day begins with a concise decision surface.

Continuity is designed to preserve momentum without transferring business authority to an unattended agent. It can organize context, prepare plans, execute explicitly approved repository work, validate the result, and prepare a draft pull request. It must stop before merge or business completion until a human records the applicable disposition.

## Intended Use Case

Continuity is useful when work develops across conversations, notes, feedback, implementation sessions, reviews, and changing priorities. The suite is intended to reduce the amount of context a person must reconstruct at the beginning of each day.

The operating model assumes that:

- Important context may arrive before, during, or after implementation.
- Positive feedback, negative feedback, changed requirements, risks, decisions, and successful outcomes are all useful evidence.
- Some notes should remain context while others should become questions, roadmap candidates, or planning candidates.
- Off-hours execution is valuable only when the scope and authority were established beforehand.
- The next business day should begin with decisions, evidence, and exceptions rather than a raw activity log.
- A project may be part of a larger campaign or objective, but private notes and execution controls remain isolated to the project where the work occurs.

Continuity can support non-code campaigns and objectives through capture, memory, roadmap, planning, and reporting. Its unattended execution controls are repository-oriented. External publication, financial actions, customer communication, production deployment, and other consequential side effects require separately configured and explicitly approved integrations.

## Core Operating Principles

### Continuity before autonomy

The purpose is to preserve context and continue approved work, not to let an agent choose the business direction. Notes, patterns, and recommendations can inform a decision but cannot authorize execution.

### Evidence before interpretation

Record what happened, when it happened, who or what supplied the information, and how it affected the work. Avoid converting a recurring situation into a permanent judgment about a person or organization.

### Symmetric feedback

Capture positive and negative feedback with the same care. A successful outcome may identify behavior worth preserving. A failure or repeated change may indicate a need for adaptability, clearer acceptance criteria, or a different sequence of work.

### Bounded off-hours work

Off-hours execution is limited to an exact approved goal, an approved plan version, a configured runtime, a single project lock, and an isolated worktree. Discoveries outside that boundary become notes or later planning candidates.

### Human authority at consequential boundaries

A human must approve the plan. Continuity may prepare and test a draft pull request, but it does not auto-merge, use administrator bypass, force-push, infer approval, or mark business completion from agent judgment. A project may separately opt in to an interactive, exact SHA-bound direct GitHub CLI merge after every gate passes.

### Private by default

Raw captures, approvals, locks, scheduler receipts, run ledgers, and working indexes stay in ignored project-local state. Only reviewed memory, roadmap records, code, documentation, and intentionally prepared packets enter version control.

### Portable control, isolated application

Reusable preferences may apply across a portfolio, but commands, notes, schedules, validation requirements, and execution state belong to each installed project. Codex, Claude Code, Cursor, Windsurf, or another surface must route back through the same project-local contract.

## System Vocabulary

| Term | Meaning |
| --- | --- |
| Portfolio | The configured collection of project folders a supervisor may inspect. |
| Project | One isolated repository-backed area with its own configuration, notes, goals, schedules, and evidence. |
| Campaign or objective | A higher-level outcome represented through roadmap records and links to one or more project goals. |
| Capture | A timestamped source record containing one or more atomic notes. |
| Note | A single context item, decision, question, insight, documentation candidate, backlog candidate, or execution candidate. |
| Project memory | Reviewed, committed knowledge that is trusted for future retrieval and planning. |
| Roadmap record | Committed project, campaign, objective, milestone, release, risk, or work-item context. |
| Goal | A versioned, approval-ready unit of work with scope, exclusions, acceptance criteria, and evidence references. |
| Execution attempt | One dispatched implementation pass for a goal. Rework archives the prior attempt and starts a fresh evidence set. |
| Workflow status | The machine-readable handoff containing stage, blockers, next skill, actions, requirements, and evidence. |
| Review-ready | Work that passed implementation, testing, security, documentation, memory, roadmap, and merge-safety gates and is waiting for a human disposition. |

## Authority Model

Continuity separates information, recommendation, authorization, execution, and completion.

| Record or action | What it permits |
| --- | --- |
| Capture or note | Search, classification, pattern analysis, and later human review. |
| Pattern recommendation | Planning input only. |
| Roadmap link | Relationship and prioritization context only. |
| Draft goal | Plan review, revision, hold, or cancellation. |
| Exact human plan approval | Queue eligibility for that goal and plan version. |
| Valid dispatch | One bounded execution attempt. |
| Passed test and merge evidence | Transition to `review-ready`. |
| Human `approved` disposition | Records review approval but does not mark the goal complete. |
| Human `changes-requested` disposition | Opens controlled rework and invalidates downstream evidence. |
| Human `merged` disposition with verified merge evidence | Marks the goal `completed`. |
| Human `closed` disposition | Cancels the goal without claiming delivery. |

No lower row can be inferred from a higher row. In particular, a note is not a plan, a plan is not approval, approval is not dispatch, and a passing test is not permission to merge.

## Installation And Project Enrollment

Run installation from a Continuity suite checkout and point it at the project folder:

```text
python3 /path/to/continuity-checkout/continuity-suite/installer/install.py \
  --project-root /path/to/project \
  --project-id stable-project-id \
  --integration-branch main \
  --interactive
```

The guided configuration establishes:

- Integration branch and branch prefix
- Timezone and business days
- Nightly review, dispatch, and morning report times
- Maximum unattended runtime
- Validation and security commands
- Documentation and memory locations
- Roadmap and planning behavior
- Primary and enabled agent surfaces
- Scheduler provider
- Portfolio concurrency
- Whether repository execution is enabled

Installation updates the project agent instructions and installs the project-local skills, CLI, schemas, references, and automation prompts. It does not silently create a provider-level scheduled task.

Production installation and updates use tagged, attested release archives and `.continuity/install-manifest.json`. Follow [Releases, Updates, and Recovery](releases-updates-and-recovery.md); never replace a drifted suite-managed file or private state implicitly. Use [the production pilot](production-pilot.md) for the first off-hours run.

After installation, verify the project:

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json project doctor
.agents/continuity/bin/continuity --project-root "$PWD" --json workflow status
.agents/continuity/bin/continuity --project-root "$PWD" memory audit
.agents/continuity/bin/continuity --project-root "$PWD" roadmap audit
```

Execution should remain disabled until the project commands, security requirements, branch policy, and human review process are correct.

## Scheduler Activation

Schedule intent and scheduler activation are separate. Selecting `codex`, `claude-code`, or `external` records which provider should own the recurring supervisor; it does not prove that the provider task exists.

To activate scheduled operation:

1. Create one recurring supervisor in the selected provider.
2. Use `.agents/continuity/automation/portfolio-supervisor.md` as its operating prompt.
3. Give it only the workspace roots it is allowed to inspect.
4. Run it at the configured sweep interval.
5. Record the provider task ID and the exact roots in every covered project.

```text
.agents/continuity/bin/continuity --project-root /path/to/project scheduler register \
  --task-id provider-task-id \
  --root /path/to/workspace \
  --actor human-operator
```

6. Run `project doctor` and confirm the scheduler state is `registered`.
7. Observe at least two successful sweeps and one claimed no-op review or report action.
8. Confirm claim replay, stale registration, and second-workstation lease contention are rejected; record each observation with `scheduler adapter codex record-probe` and concrete evidence.
9. Configure provider-native failure notification where available.

For Codex, generate the provider-native definition with `scheduler adapter codex render`, then require `scheduler adapter codex verify` to pass. Before every code-changing start, acquire the exact goal-attempt remote lease. Scheduled start binds it to the consuming run and task; only that dispatch completion may release it. Review and report actions remain read-only and cannot release the execution lease.

When the scheduler provider is `none`, schedule intent is retained but all review, dispatch, and report commands are manual.

A plain cron or `launchd` process can calculate due actions and detect stale state, but it cannot perform model-driven review or implementation unless it invokes an authenticated, conformant agent surface.

## The Daily Operating Cycle

### 1. Capture information during normal work

Use `$continuity-capture` whenever a conversation, work session, PRD, or feature request produces durable context. Capture facts and feedback while their source and time are still clear.

Useful capture categories include:

- A decision and its rationale
- A new requirement or changed requirement
- Positive or negative feedback
- A successful behavior worth preserving
- A failure, risk, constraint, or dependency
- A question that blocks planning
- A documentation correction
- A possible future action
- An explicit instruction that may need planning

Example:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note capture \
  --text "The review favored the adaptable workflow and requested a simpler approval step." \
  --source-type conversation \
  --source-ref "review-session"
```

Capture does not authorize documentation or implementation.

For pasted meeting notes, treat the message as one source and split it into semantic atomic items before capture. Do not create one item per bullet mechanically: preserve each distinct decision, requirement, positive or negative feedback item, question, risk, and later idea as its own item. Keep related explanation with the item it qualifies. The result is one `capture_mode: batch` record with independently triageable item IDs, a shared meeting reference and source timestamp, and `execution_authorized: false` on every item.

For a PRD or feature request, point `$continuity-capture` to one local UTF-8 Markdown or plain-text file. The skill reads the document-capture reference, prepares one `--items-file` payload containing `source_file`, `document_type`, stable `document_id`, authority, and stable source anchors, then uses the same capture command. Keep requirement acceptance criteria together, preserve constraints and non-goals as decisions, and split risks and open questions independently. The CLI stores the exact private snapshot, calculates its hash, and links later revisions without editing the source. `project-intent` is reserved for an official in-project document; all other document sources use `supplied-reference`.

An identical document ID and hash returns the prior capture. A changed hash creates a new revision. Stable source-item keys let the CLI archive unchanged items, relate changed items, and retain removed items as explicit revision evidence. Planning from any extracted item derives the originating capture, document revision, and source hash into the goal's approval material.

Example batch input:

```json
{
  "source_type": "meeting",
  "source_ref": "meeting:objective-review-2030-04-10",
  "source_timestamp": "2030-04-10T14:00:00-05:00",
  "items": [
    {
      "kind": "insight",
      "text": "Reviewers found the status view easier to scan; preserve its density.",
      "perspective": "external",
      "sentiment": "positive",
      "occurrence_type": "feedback",
      "impact": "medium",
      "confidence": "high",
      "actionability": "context",
      "stakeholders": ["reviewers"],
      "themes": ["status-view", "scanability"]
    },
    {
      "kind": "execution-candidate",
      "text": "Move the risk summary above dependencies in the next pass.",
      "perspective": "external",
      "sentiment": "neutral",
      "occurrence_type": "need",
      "impact": "medium",
      "confidence": "high",
      "actionability": "plan",
      "stakeholders": ["objective-owner"],
      "themes": ["risk-summary", "dependencies"]
    }
  ]
}
```

```text
.agents/continuity/bin/continuity --project-root "$PWD" note capture \
  --items-file meeting-notes.json
.agents/continuity/bin/continuity --project-root "$PWD" workflow status \
  --capture-id <capture-id>
```

A batch is limited to 250 items, with 20,000 characters per item. Source documents are additionally limited to 2,000,000 bytes. Split larger material by meeting or source instead of truncating it. A single callout remains a normal `capture_mode: singular` capture.

### 2. Triage each atomic note

Use `$continuity-triage` to classify what the note is and where it belongs.

```text
.agents/continuity/bin/continuity --project-root "$PWD" note list
.agents/continuity/bin/continuity --project-root "$PWD" note triage \
  <capture-id> <item-id> \
  --kind <kind> \
  --action <route|defer|archive|promote>
```

Record occurrence dimensions when they are known:

- `perspective`: internal, external, mixed, or unknown
- `sentiment`: positive, negative, mixed, neutral, or unknown
- `occurrence_type`: feedback, behavior, decision, change, need, risk, success, failure, constraint, or observation
- `impact`: low, medium, high, critical, or unknown
- `confidence`: low, medium, high, or unknown
- `actionability`: context, monitor, plan, or urgent-review
- Stakeholders, themes, and an optional stable pattern key

Deferral requires an explicit review date:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note triage \
  <capture-id> <item-id> \
  --action defer \
  --review-after 2030-04-15T09:00:00-05:00
```

Current queues are derived from canonical captures. Files in `.continuity/private/queues/` are historical snapshots and must not be treated as current planning truth.

### 3. Retrieve memory and roadmap context

Use `$continuity-memory` and `$continuity-roadmap` before planning. Search private captures when looking for similar situations, but use reviewed canonical memory as trusted planning evidence.

```text
.agents/continuity/bin/continuity --project-root "$PWD" memory search "approval workflow"
.agents/continuity/bin/continuity --project-root "$PWD" memory similar "requirements changed repeatedly" --scope all
.agents/continuity/bin/continuity --project-root "$PWD" roadmap brief "current objective"
.agents/continuity/bin/continuity --project-root "$PWD" roadmap audit
```

Linking a note to a campaign or objective supplies context. It does not authorize work.

### 4. Convert selected candidates into a decision-complete plan

Use `$continuity-plan` only for notes that were deliberately promoted into planning. The plan should define:

- The business or operational outcome
- Current behavior and desired behavior
- Scope and explicit exclusions
- Acceptance criteria
- Required tests and security review
- Documentation, memory, and roadmap impact
- Relevant source note, memory, and roadmap IDs
- Open decisions and human-required decisions
- Dependency-aware delivery slices when the outcome is too large for one pass
- Runtime and external-side-effect limits

Create the goal from a reviewed JSON file:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal create \
  --goal-file /path/to/reviewed-goal.json
```

The new goal remains `awaiting-feedback`. Nightly review may prepare a goal, but it may not approve it.

### 5. Approve the exact plan version

A human reviews the plan, its evidence, its exclusions, and its intended outcome. Approval must name the goal and plan version explicitly.

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal approve <goal-id> \
  --version 1 \
  --approved-by "human identity" \
  --authorization-text "Approve <goal-id> plan v1"
```

Approval binds to the material plan hash. Editing the plan, machine goal, planning artifacts, or relevant roadmap context invalidates approval.

Approval normally queues the goal for the configured dispatch time. It does not start implementation by itself.

### 6. Run the nightly review

At the review schedule, the supervisor starts one isolated review task per due project. The review task:

- Runs `project doctor` and `workflow status`
- Triages new captures conservatively
- Reconsiders deferred notes whose review date is due
- Rebuilds memory and roadmap indexes
- Detects contradictions, stale links, cycles, and documentation drift
- Prepares decision-complete goals when evidence supports them
- Produces a report even when no action is warranted

The nightly review does not approve goals, infer missing decisions, publish externally, or dispatch unapproved work.

### 7. Dispatch one approved goal

At the dispatch schedule, the portfolio supervisor calculates due work and issues a short-lived, one-time claim. The project task must consume the exact claim before execution.

Dispatch requires:

- Same-date review success
- A queued and due goal
- Current plan approval
- Completed dependencies
- Healthy configuration and scheduler state
- No conflicting project lock
- Successful preflight
- Available portfolio capacity

Continuity permits at most one code-changing goal per project at a time. Separate projects may run concurrently within the portfolio cap.

A human may start an eligible queued goal earlier:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal start <goal-id>
```

### 8. Execute in an isolated worktree

Use `$continuity-execute` only after dispatch. The enforced delivery order is:

1. Preflight
2. Isolated worktree and goal branch
3. Approved implementation
4. Candidate tests during implementation
5. Documentation, memory, roadmap, and evidence artifacts
6. Final alignment against scope, exclusions, and acceptance criteria
7. Commit all implementation and evidence artifacts
8. Final source-bound test run
9. Push the exact tested commit
10. Create or update the draft pull request
11. Assess local head, remote head, pull-request head, and integration base
12. Mark the goal `review-ready`

Any out-of-scope discovery becomes a note, question, roadmap candidate, or later goal. It is not silently added to the current implementation.

### 9. Bind tests to the final source

Use `$continuity-test` after all implementation and evidence files are committed:

```text
.agents/continuity/bin/continuity --project-root "$PWD" test run <goal-id> \
  --worktree /path/to/isolated-worktree \
  --branch continuity/example-goal
```

The machine record binds the result to the repository, branch, commit, source fingerprint, plan hash, behavior configuration, commands, and evidence hash. A tracked or untracked source change, new commit, branch change, plan change, or command change makes the result stale.

Candidate tests run earlier are useful for implementation but do not replace this final source-bound run.

### 10. Assess merge safety and stop

Use `$continuity-merge` only after the exact tested commit is pushed to a draft pull request:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge assess <goal-id> \
  --worktree /path/to/isolated-worktree \
  --branch continuity/example-goal \
  --pr-url https://github.com/example-organization/example-repository/pull/123 \
  --update-gate
```

The assessment verifies the clean worktree, branch, tested commit, remote head, pull-request head, pull-request base, and required compliance stages.

Successful off-hours work stops at `review-ready`. Continuity does not merge or claim business completion.

### 11. Begin the next business day with the morning report

The morning report leads with three surfaces:

1. Decisions needed
2. Completed overnight
3. Blocked or at risk

It then supplies per-goal workflow state, allowed and blocked dispositions, pull-request and evidence references, test and security status, merge state, compliance blockers, queue counts, memory and roadmap health, active runs, recurring patterns, and prepared next work.

```text
.agents/continuity/bin/continuity --project-root "$PWD" --json report morning
.agents/continuity/bin/continuity --project-root "$PWD" report project
```

`review-ready` is successful preparation for a decision. It is not completion.

### 12. Record the human disposition

After reviewing the pull request and evidence, record one factually accurate disposition:

```text
.agents/continuity/bin/continuity --project-root "$PWD" merge record-human <goal-id> \
  --pr-url <pull-request-url> \
  --merged-by "human identity" \
  --disposition <approved|changes-requested|merged|closed> \
  --evidence "review evidence"
```

Disposition behavior:

- `approved`: Records human approval and leaves the goal `review-ready` until merge is recorded.
- `changes-requested`: Archives the attempt, starts a fresh execution manifest, invalidates downstream evidence, and places the same goal into controlled rework.
- `merged`: Requires current evidence and verified merge commit information, then marks the goal `completed`.
- `closed`: Cancels the goal without claiming delivery.

`approved` and `merged` require current source-bound evidence. `changes-requested` and `closed` remain recordable when delivery evidence is stale because they do not authorize delivery.

If no pull-request disposition can be recorded, an audited cancellation fallback is available:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal cancel <goal-id> \
  --actor "human identity" \
  --reason "closure reason"
```

## Controlled Rework

When a human requests changes, distinguish changes inside the approved scope from expanded scope.

For an in-scope correction, explicitly resume the same plan version:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal resume <goal-id> \
  --actor "human identity" \
  --authorization-text "Resume <goal-id> under approved plan v1"
```

The resume receipt binds the goal, approved plan hash/version, execution attempt, actor, authorization text, timestamp, scope assertion, and nonce. In a signed-approval project, add `--signing-key <trusted-ssh-private-key>` so the receipt also binds a trusted SSH approver. The prior attempt remains archived. Dispatch, preflight, execution, tests, merge assessment, and review evidence must be regenerated for the new attempt.

For changed or expanded scope, revise the plan instead:

```text
.agents/continuity/bin/continuity --project-root "$PWD" goal revise <goal-id> \
  --goal-file /path/to/revision.json \
  --author "human identity" \
  --summary "reason for scope revision"
```

Revision creates a new plan version and requires fresh approval.

## Workflow Status And Skill Handoffs

Every Continuity skill reads workflow status on entry and reports it on exit:

```text
.agents/continuity/bin/continuity --project-root "$PWD" workflow status
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --capture-id <capture-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --note-id <note-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --memory-id <memory-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --roadmap-id <roadmap-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --packet-id <packet-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --goal-id <goal-id>
```

The record includes:

- Current state and stage
- Next recommended skill
- Completed and pending compliance stages
- Current blockers
- `allowed_actions`
- `blocked_actions` with reasons
- Human requirements
- Execution attempt and evidence references
- For notes: summary status, exact stage, `stage_entered_at`, routing, planning disposition, per-goal tracks, relationship candidates, and timeline

An allowed action may still name required human values or a live check such as preflight or pull-request verification. Workflow status does not itself authorize a human-required action.

Manual requests use `$continuity-workflow` as the orchestrator. It invokes the current `next_skill`, records that skill's canonical output, refreshes subject-specific status, and continues immediately. Individual gate failures can stop stage advancement, but they return to the owning remediation skill instead of ending the overall run. Only a handoff or action marked `human_required: true` pauses the sequence. After the human records an allowed action, rerun `$continuity-workflow` with the same subject and it resumes from durable state.

The installed `workflow-handoffs.md` reference explains the machine-derived information envelope each skill passes forward: exact subject IDs, cited inputs, durable outputs, decisions, evidence, blockers, authorization state, next skill, and machine-listed actions. Use the narrowest subject selector so unrelated queue priority cannot redirect the handoff. Each task skill also has a local applied reference covering its boundary cases and examples. These documents interpret the workflow record; the CLI remains authoritative when prose and machine state disagree.

Before handoff, the skill uses the shared output rubric as an internal self-review. Evidence should be traceable, current, bounded, decision-complete, actionable, private, state-accurate, and proportionate to risk. Record actionable findings through existing evidence and compliance fields. A missing dimension blocks only when it maps to an existing gate, acceptance criterion, or project requirement; the rubric creates no parallel approval state.

## Notes, Patterns, And Long-Term Learning

Note lifecycle is derived from routing, approval-hashed note dispositions, all linked goals, compliance, run, test, merge, human-review, and event records. A note may be linked to multiple goals without losing history. Skills update their canonical stage records and never maintain note progress independently.

Every plan assigns each source note exactly one explicit disposition. New goals and source-changing revisions fail closed when any disposition is omitted. `current-goal` follows delivery; `later` requires a review date or roadmap anchor; `context-only` informs without adopting execution state; `duplicate` points to the canonical note. Run `note related-goals` before deciding, but treat similarity as non-authorizing evidence. Morning reports show only confidence-qualified candidates and cap the review list; use the direct command when broader investigation is useful.

Timeline provenance follows the relationship, not merely the current existence of a link. Goal execution events are included only for a `current-goal` relationship, at or after its decision timestamp, and for its plan version. A later, context-only, or duplicate note cannot appear to have participated in implementation, testing, or merge stages.

Use pattern review to handle recurring signals deliberately:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note patterns --min-count 2
.agents/continuity/bin/continuity --project-root "$PWD" note pattern-review <pattern-id> \
  --disposition <accepted|deferred|dismissed> \
  --actor "human identity" \
  --evidence "decision rationale"
```

Deferred patterns require `--review-after`. Accepted and dismissed patterns remain out of morning decisions until their evidence hash changes. A pattern may recommend adaptability or preservation, but it never authorizes work.

If `project doctor` reports legacy note links, migrate them explicitly:

```text
.agents/continuity/bin/continuity --project-root "$PWD" note migrate-links --actor "human identity"
```

Run the command again and confirm that it migrates zero additional items.

## Failure And Recovery Behavior

### No eligible work

The review and morning report still run. A no-work night is a valid result and should produce a concise report rather than fabricated activity.

### Failed project health

Stop work for that project, report the exact doctor failure, and continue healthy projects independently.

### Failed tests or security review

Keep the goal validating, blocked, or partially completed. Do not create a passing report from prose or agent judgment.

### Stale source or pull-request evidence

Do not approve or record merge. Rerun the final tests and merge assessment after restoring a clean, current source state. A human may still request changes or close the goal.

### Runtime expiration

Record `blocked` or `partially-completed`, preserve the draft branch and evidence, release the project lock when appropriate, and require an explicit human resume decision.

### Stale scheduler or child run

Use `scheduler status` and `scheduler recover`. Recovery may mark only the matching run and goal stale, release only its matching lock, and must not infer approval or resume execution.

### Supervisor stops entirely

The project detects a stale lease when `project doctor` or another sweep runs. Because a stopped supervisor cannot report its own failure, configure provider-native task failure notifications or an independent local health check.

## Morning Human Review Checklist

For each reported goal:

1. Confirm the stated business outcome still matters.
2. Review the plan version, scope, and exclusions.
3. Inspect the implementation summary and changed files.
4. Confirm the final test record matches the current commit.
5. Review security findings and unresolved risks.
6. Confirm documentation, memory, and roadmap impact.
7. Review the draft pull request and merge-safety evidence.
8. Choose only a currently permitted disposition.
9. Route unrelated discoveries into later notes or goals.
10. Record the actual merge only after it occurs.

The report should reduce the decision to a small number of high-value choices. It should not require the human to reconstruct the entire overnight session.

## Operating Modes

### Manual mode

Use scheduler provider `none`. Capture, triage, planning, dispatch, testing, and reporting are invoked manually. This is appropriate while evaluating the suite or when unattended work is not desired.

### Single-project scheduled mode

Register one provider supervisor with one workspace root and one enrolled project. Use a portfolio concurrency cap of one while validating the complete cycle.

### Portfolio mode

Register one provider supervisor for several workspace roots. Each project retains its own timezone, schedules, commands, private state, and execution lock. The supervisor applies the smallest participating concurrency cap and never centralizes raw notes.

### Campaign or objective coordination

Represent the shared outcome in roadmap records. Link project notes and goals to that context, but keep execution approval and evidence project-local. Portfolio summaries contain sanitized status, not raw captures or private ledgers.

## Operational Readiness Checklist

Do not consider scheduled Continuity active until all applicable items are true:

- Installation completed successfully.
- `project doctor` is healthy.
- Project behavior and configuration hashes match.
- Validation and security commands are correct.
- Execution enrollment is intentional.
- The provider supervisor task actually exists.
- Scheduler registration records the correct task ID and workspace roots.
- The supervisor heartbeat is current.
- Two consecutive sweeps succeeded.
- A no-op claim was consumed exactly once.
- Replay and expiration checks failed closed.
- The nightly review produced a report.
- Dispatch refused unapproved work.
- A test goal stopped at `review-ready`.
- The morning report exposed human decisions.
- No automated merge or restricted side effect occurred.
- Provider-native failure notification or an independent health check is configured.

## Definition Of Success

Continuity is working as intended when:

- Important context survives across sessions without becoming accidental instruction.
- Good and bad feedback both improve future planning.
- Roadmap and memory context remain searchable and cited.
- Only decision-complete, explicitly approved work runs unattended.
- Off-hours execution produces a clean draft pull request and current evidence.
- Failures stop locally and remain understandable.
- The next business day begins with a concise set of business decisions.
- The human retains authority over scope, approval, merge, publication, and completion.
