# Execution Evidence

Read this reference before preflight, at alignment checkpoints, when scope drift is discovered, and before final test handoff.

## Checkpoint record

Each major checkpoint should state:

- approved slice or scope completed;
- files and behavior changed;
- tests or inspections run and their results;
- decisions applied and source evidence;
- discoveries routed outside the current scope;
- remaining frontier, blockers, and runtime;
- whether workflow state and approval remain current.

## Scope decisions

Continue when the implementation detail is necessary to satisfy approved acceptance criteria and stays within documented architecture and risk. Stop when the discovery changes user behavior, data ownership, architecture, dependencies, restricted effects, acceptance, or roadmap impact.

Route a useful unrelated improvement to a new capture. Do not include it because the same file is already open.

## Evidence artifacts

- `request-alignment.md`: approved request, scope, exclusions, decisions, and source IDs.
- `implementation-report.md`: changed behavior, architecture, files, slices, and deviations.
- `validation-and-security.md`: candidate checks, final checks, code review, security findings, and residual risk.
- `product-conformance.md`: source hierarchy, audited journeys, portable evidence, scoped findings, result hash, and disposition.
- `memory-impact.md`: exact memory used, contradictions, additions, verification, or reason for no change.
- `roadmap-impact.md`: exact roadmap IDs, approved impact, completed update, or reason for no change.
- `evidence.md`: commands, hashes, checkpoints, PR, and compliance-stage references.

Artifacts must report evidence, not repeat the plan in future tense.

## Partial and blocked outcomes

Use `partially-completed` when a bounded approved portion is implemented and evidenced but the complete goal cannot proceed. Use `blocked` when no valid frontier can continue. Preserve the worktree, draft PR when useful, exact blocker, completed slices, failed evidence, and safe next action.

## Handoff checklist

- Final implementation matches the approved goal and active slice frontier.
- New scope is captured separately.
- Documentation, memory, roadmap, and all seven artifacts are complete.
- Product and evidence changes are committed and the worktree is clean.
- `$continuity-test` receives the exact worktree, branch, commit, plan, commands, and expected acceptance evidence.
