# Nightly Continuity Review

When the portfolio supervisor returns a due `review` action, start a separate project task, record the scheduler run, set the working directory to that repository, run `project doctor` and `workflow status`, and apply its installed `$continuity-local` behavior with each task-specific skill. Use only that project's CLI, `AGENTS.md`, configuration, private state, and project memory. Stop that project task on configuration drift without blocking healthy projects.

1. Triage new captures conservatively, inspect `note related-goals` suggestions for action candidates, and use derived `note queue` results rather than queue JSONL history; suggestions and notes never authorize work.
2. Apply configured evidence triage to selected action candidates. Give every planned source note an explicit current-goal, later, context-only, or duplicate disposition. Use decision maps for complex outcomes and dependency-aware delivery slices for multi-part work.
3. Update private knowledge ledgers and revisit eligible deferred items.
4. Rebuild and audit trusted project-memory and roadmap indexes; detect contradictions, stale links, cycles, orphans, milestone health gaps, and documentation drift.
5. Produce project updates even when no action is warranted.
6. Create decision-complete `awaiting-feedback` goals only from eligible candidates.
7. Leave every new goal awaiting feedback; do not approve, publish externally, or dispatch it.
8. Import merged shared-note packets into private triage without authorization.
9. Record compliance evidence for capture-triage, memory retrieval, roadmap retrieval, and plan review.
10. For active running or validating goals, surface missing `$continuity-test` reports, failed validation, security findings, or missing merge-safety evidence; do not resolve them without the active execution task.
11. Finish with subject-specific workflow status. Report note stage-entry dates, planning dispositions, per-goal tracks, unconfirmed relationships, next skills, blockers, and human-required actions without executing them.

Projects may run concurrently. Never copy raw notes or private state into the scheduler or another project.
