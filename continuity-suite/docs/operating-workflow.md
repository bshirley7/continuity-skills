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

A human must approve the plan. Continuity may prepare and test a draft pull request, but it does not auto-merge, force-push, infer approval, or mark business completion from agent judgment.

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
8. Confirm that a replayed or expired claim is rejected.
9. Configure provider-native failure notification where available.

When the scheduler provider is `none`, schedule intent is retained but all review, dispatch, and report commands are manual.

A plain cron or `launchd` process can calculate due actions and detect stale state, but it cannot perform model-driven review or implementation unless it invokes an authenticated, conformant agent surface.

## The Daily Operating Cycle

### 1. Capture information during normal work

Use `$continuity-capture` whenever a conversation or work session produces durable context. Capture facts and feedback while their source and time are still clear.

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

The prior attempt remains archived. Dispatch, preflight, execution, tests, merge assessment, and review evidence must be regenerated for the new attempt.

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

An allowed action may still name required human values or a live check such as preflight or pull-request verification. Workflow status does not itself authorize a human-required action.

## Notes, Patterns, And Long-Term Learning

Note status is derived from both its routing state and all linked goals. A note may be linked to multiple goals without losing history. Hold, resume, cancellation, revision, rework, and completion update the derived status.

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
