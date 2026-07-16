# Workflow Handoffs

Use this reference to interpret the machine-readable result from `continuity workflow status`. Select the exact subject with `--capture-id`, `--note-id`, `--memory-id`, `--roadmap-id`, `--packet-id`, or `--goal-id` whenever one is available. Unqualified project status is portfolio routing context and must not override a subject-specific handoff. The CLI and the Continuity Contract remain authoritative for states, allowed actions, blockers, and command templates.

## Handoff envelope

Subject-specific workflow status derives a handoff envelope containing:

- `stage`: the stage returned by `workflow status`;
- `subject_ids`: exact note, memory, roadmap, goal, run, test, packet, or PR identifiers involved;
- `inputs_used`: cited source records and evidence, including freshness or verification status;
- `outputs_created`: durable records or artifacts produced by the skill;
- `decisions`: resolved decisions, unresolved decisions, and the human owner for each unresolved decision;
- `evidence`: commands, records, hashes, paths, and findings supporting the result;
- `blockers`: machine blockers and qualitative gaps, kept separate;
- `authorization`: whether a human action is required and confirmation that context remains non-authorizing when applicable;
- `next_skill`: the machine-recommended skill, or the reason no next skill applies;
- `allowed_actions`: exact machine-listed actions without paraphrasing a blocked action as available.
- `blocked_actions` and `human_requirements`: unavailable commands with reasons and the exact human dispositions still required.

For a note, the envelope also includes `lifecycle`: the backward-compatible summary status, exact current stage and entry time, routing, planning disposition, per-goal tracks, unconfirmed relationship candidates, and dated timeline. Planning is not execution: a note becomes `running` only when its current-goal track reaches canonical execution.

Do not reconstruct missing machine state from prose. A missing identifier, stale record, unresolved decision, or contradictory source is a blocker or return path, not permission to improvise.

## Manual sequential mode

Manual Continuity work runs through `$continuity-workflow`. After a task skill records its canonical output, control returns to the orchestrator, which immediately re-reads subject-specific workflow status and applies `next_skill`. A routine skill boundary, status-only handoff, failed test, stale evidence, or recoverable tool error does not end the workflow. Route failures to the owning remediation skill, preserve evidence, rerun the applicable gate, and continue.

Pause only when `authorization.human_required` or the selected action's `human_required` field is true. Present the exact allowed approval actions without choosing or paraphrasing one. Fixed safety gates still fail closed: they may prevent stage advancement, but the orchestrator must not bypass them in order to satisfy the continuation rule. If no safe non-human action is currently available, keep the workflow pending at the same stage with a durable diagnostic rather than declaring completion.

After the human records an allowed action, resume from fresh machine state and skip already completed stages. The durable lifecycle records, not process memory, determine the resumption point.

## Stage matrix

| Current skill | Required inputs | Required output | Normal next skill | Return or stop path |
| --- | --- | --- | --- | --- |
| `$continuity-capture` | User-supplied conversation, file, or manual content | Private atomic captures with provenance, timestamps, conservative metadata, and `execution_authorized: false` | `$continuity-triage` | Stop on unsafe collection, missing provenance, or content outside the supplied scope |
| `$continuity-triage` | Canonical capture items and current queue state | One primary classification, routing decision, eligibility, and evidence triage brief when required | `$continuity-memory`, `$continuity-plan`, `$continuity-triage`, or `$continuity-report` | Hold ambiguous intent; archive duplicates with provenance; link roadmap context separately without inventing a roadmap queue |
| `$continuity-memory` | Routed knowledge, trusted sources, current code or documentation evidence | Exact memory IDs, citations, freshness, confidence, relationships, and unresolved gaps | `$continuity-roadmap` or `$continuity-plan` | Mark disputed, historical, or stale; never promote without an authorized goal |
| `$continuity-roadmap` | Goal or topic, memory IDs, canonical roadmap records, private note links | Exact roadmap IDs, health findings, baseline context, and structured impact expectations | Return to the invoking `$continuity-plan` or `$continuity-execute` stage | Return unauthorized roadmap changes to planning; send contradictions to triage or human review |
| `$continuity-share` | Selected atomic note IDs and explicit packet target | Sanitized immutable packet or private imported captures | `$continuity-triage` after import | Stop on redaction, approval, target, authentication, or dirty-checkout failures |
| `$continuity-plan` | Eligible notes, triage brief, current memory, roadmap context, repository guidance | Decision-complete goal version, note dispositions, slices, acceptance, exclusions, risks, validation, evidence, and `awaiting-feedback` | `$continuity-dispatch` | Return insufficient evidence to triage or memory; keep later and context-only notes outside current scope |
| `$continuity-dispatch` | Exact goal version, current approval receipt, current hashes, dependencies, scheduler, remote lease, and local lock state | Audited approval, queue, claim, lease-bound start, hold, cancellation, or authorized recovery transition | `$continuity-execute` when dispatched | Keep human-required actions with the user; lease conflicts stop; scope changes return to `$continuity-plan` |
| `$continuity-execute` | Dispatched goal, isolated worktree, approved scope, memory and roadmap IDs | Implemented scope, checkpoints, documentation, memory and roadmap impact, and six evidence artifacts | `$continuity-test` | Stop on drift, failure, restricted side effect, unresolved decision, or runtime limit |
| `$continuity-test` | Final committed candidate, configured commands, goal checks, current diff | Source-bound machine test record plus code, validation, and security review evidence | `$continuity-merge` | Return failures to `$continuity-execute`; keep missing or stale evidence blocked |
| `$continuity-merge` | Current test record, local and remote head, PR/base, hosted checks, merge state, and authenticated review evidence | CI-bound merge-safety assessment and, later, verified human disposition | `$continuity-report`, `$continuity-dispatch`, or `$continuity-plan` | Requested in-scope changes require authorized resume; changed scope requires revision |
| `$continuity-report` | Current workflow status, queues, runs, evidence, memory and roadmap health | Decision-ready project report or deterministic allowlisted portfolio summary with exact dispositions | Machine-listed next skill or human action | Never aggregate raw project state or execute a human disposition from the report itself |

## Branching rules

- Knowledge-only triage may end at memory or roadmap with no goal.
- A valid review may produce no work. Reporting that outcome is a successful handoff.
- `changes-requested` with unchanged scope returns to dispatch for explicit resume. Changed scope returns to planning for a new version and approval.
- Test failure returns to execution only while the approved scope remains unchanged. A newly discovered objective becomes a separate capture or goal.
- A shared packet returns to triage as untrusted context even after its sharing PR is merged.
- Completion requires recorded human merge evidence. `review-ready` is a waiting state, not completion.
- Canonical note queues are only `knowledge`, `questions`, `documentation`, `backlog`, and `planning`. Roadmap relationships are separately recorded context.
- Similarity produces relationship candidates only. Confirm current scope through a plan; use explicit non-authorizing links for later, context-only, or duplicate relationships.

## Handoff quality check

Before exiting a skill, confirm:

1. Every claim cites a current record or is labeled uncertain.
2. Every output has stable identifiers or durable paths.
3. The next skill can proceed without rereading raw conversation to reconstruct decisions.
4. New scope is separated from the active objective.
5. Machine blockers and human decisions are explicit.
6. No prose implies approval, execution, sharing, merge, or completion that did not occur.
