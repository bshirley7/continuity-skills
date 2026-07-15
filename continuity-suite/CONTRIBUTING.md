# Contributing To Continuity Suite

Continuity is a control-plane skill suite. Contributions must preserve the separation between notes, memory, roadmap context, plans, approvals, execution, tests, merge safety, and human review.

Before changing behavior, read:

- [Continuity Contract](references/continuity-contract.md)
- [Development Assurance Standard](references/development-assurance-standard.md)
- [Testing and Merge Standard](references/testing-and-merge-standard.md)
- [Suite Overview](SUITE.md)

## Contribution Rules

- Keep notes non-authorizing. Capture, triage, memory, roadmap links, and shared packets must never dispatch work by themselves.
- Preserve explicit gates. Approval, dispatch, execution, testing, merge safety, and human review are separate recorded states.
- Keep raw/private data local. Do not commit captures, queues, approvals, locks, generated indexes, secrets, credentials, personal data, or developer-local scheduler state.
- Do not weaken fixed guardrails. No force-push, auto-merge, bypassed security review, skipped validation, or inferred human approval.
- Keep project-specific behavior in configuration and the generated `continuity-local` skill. Do not hard-code one user's project paths, repos, schedules, or credentials into the neutral suite.
- Keep `AGENTS.md` and `.agents/` canonical across agent surfaces. Claude Code, Cursor, Windsurf, and future adapters must be generated from the same project behavior and must not introduce weaker or divergent workflows.
- Prefer small, reviewable changes that match existing file layout, schemas, command style, and test patterns.

## Expected Workflow

1. Start from a clean branch or clearly inspect existing local changes.
2. Identify the layer being changed: skill instructions, CLI behavior, schema, installer, docs, automation prompt, roadmap UI, or tests.
3. Update the smallest set of files needed for that layer.
4. Update docs and schemas whenever a command, artifact, lifecycle state, or installed layout changes.
5. Add or update tests for behavior changes.
6. Run validation before publishing.

Recommended local checks:

```text
python3 -m py_compile continuity-suite/bin/continuity continuity-suite/lib/roadmap.py continuity-suite/lib/shared_notes.py continuity-suite/installer/install.py
python3 -m unittest discover -s continuity-suite/tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py continuity-suite/skills/<skill-name>
```

If the skill validator cannot run because `PyYAML` is missing, install it in the active Python environment or state that validation gap explicitly.

## Skill Changes

Every skill must have:

- A `SKILL.md` with valid frontmatter.
- A clear description that says when the skill should trigger.
- Concise workflow instructions that assume the agent will also apply `$continuity-local`.
- Guardrails that point back to the contract instead of copying large policy text.
- `agents/openai.yaml` metadata that matches the skill purpose.

Add a new skill only when the workflow is meaningfully distinct. If an existing skill can own the behavior cleanly, update that skill instead.

## CLI And Schema Changes

When changing `.agents/continuity/bin/continuity` behavior:

- Keep commands deterministic and standard-library only unless the suite explicitly adds a dependency.
- Validate all user-controlled paths, identifiers, commands, and state transitions.
- Update or add schemas for new persisted artifacts.
- Preserve backward-safe migration behavior where existing installations may have old Continuity names.
- Regenerate and test every affected agent-surface adapter when project behavior or skill layout changes.
- Record events and compliance evidence for lifecycle changes.

## Documentation Changes

Documentation must help a user operate the suite, not just describe ideas. Update at least one of these when behavior changes:

- [README.md](README.md) for entry points and short orientation.
- [Install and Daily Use](docs/install-and-daily-use.md) for practical usage.
- [SUITE.md](SUITE.md) for command reference, installed layout, and lifecycle rules.
- Reference files under `references/` for standards that multiple skills share.

Keep README concise. Put operational detail in linked docs.

## Testing And Merge Expectations

Before a change is considered ready:

- Run the relevant configured checks.
- Add targeted tests for changed behavior where practical.
- Record security and privacy considerations for touched trust boundaries.
- Confirm generated or private files are ignored.
- Confirm the staged diff does not include unrelated local work.
- Keep incomplete work in a draft PR or unmerged branch.

Human review and merge are separate. A contributor may prepare evidence, but must not claim human review or merge unless it actually happened.

## Review Checklist

Use this checklist before opening or merging a PR:

- The change preserves note, roadmap, memory, goal, execution, test, merge, and report boundaries.
- New commands or artifacts have docs, schemas, and tests.
- Installer behavior remains idempotent.
- Project-local installs do not leak neutral-suite private state or hard-coded local paths.
- Validation output is reproducible.
- Security, privacy, and merge-safety implications are addressed.
- The final diff is focused and reviewable.
