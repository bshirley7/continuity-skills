---
name: continuity-product-audit
description: Audit a website, application, documentation surface, or shipped product against its approved goal, PRD and project-intent documents, canonical documentation, project memory and insights, and roadmap. Use for baseline discovery, candidate delivery conformance, release review, recurring drift review, screenshot or journey audits, and whenever Continuity should reconcile observed product behavior with recorded intent.
---

# Continuity Product Audit

Use this skill to reconcile what the product actually does with what the project
currently says it should do. The audit produces source-bound evidence and
non-authorizing findings; it does not approve a goal, expand scope, dispatch
work, or merge a change.

Read [the Continuity contract](../../references/continuity-contract.md),
[the development assurance standard](../../references/development-assurance-standard.md),
[workflow handoffs](../../references/workflow-handoffs.md),
[output quality rubrics](../../references/output-quality-rubrics.md),
[source reconciliation and evidence](references/source-reconciliation-and-evidence.md),
`$continuity-local`, `AGENTS.md`, `.continuity/config.json`, and the applicable
goal, PRD, documentation, memory, roadmap, and product target before acting.

## Choose the profile

- `baseline`: establish how the existing product aligns with current project
  intent before planning or a production phase.
- `candidate`: gate a specific approved goal after final tests and before
  merge-safety. This profile requires a goal binding.
- `release`: review a release candidate or deployed release across the
  representative product surface.
- `drift`: revisit a prior baseline or release after source, product, or time
  changes.

Use `audit due` during review cycles. The configured
`product_audit_stale_after_days` controls when existing audits return to the
decision queue.

## Reconcile sources before observing

1. Run project doctor and subject-specific workflow status.
2. Build an audit input from the approved goal and relevant sources. For a
   goal-bound audit, the CLI automatically adds the exact plan hash, source
   document revisions, memory IDs, and roadmap IDs. Add other applicable
   sources explicitly.
3. Assign every source an authority, applicability statement, and time horizon.
   Current approved scope outranks advisory or future material. Never turn a
   future roadmap item into a current delivery requirement.
4. Define representative user journeys or product surfaces and concrete
   requirements. Include success, boundary, failure, responsive, accessibility,
   and stateful behavior when applicable.

Start from [the audit input example](references/audit-input.example.json):

```text
.agents/continuity/bin/continuity --project-root "$PWD" audit plan \
  --input <audit-input.json> \
  --goal-id <goal-id>
```

## Observe through a portable adapter

The Continuity record is adapter-neutral. Use the best available browser,
device, accessibility, command, DOM, screenshot, document, or code-inspection
tool, but preserve evidence as stable project-relative files or references.
Record the adapter name in `capture_adapter`; do not make a specific browser
plugin part of the authority model.

Before observation:

```text
.agents/continuity/bin/continuity --project-root "$PWD" audit start <audit-id> \
  --worktree <execution-worktree> \
  --branch <goal-branch>
```

For every planned journey:

1. Observe the target named in the plan.
2. Capture enough evidence to reproduce the conclusion.
3. Map each finding to explicit source IDs and evidence IDs.
4. Classify it as `aligned`, `partial`, `missing`, `contradicted`, `regressed`,
   `unverifiable`, `future-roadmap`, or `out-of-scope`.
5. Set scope to `current-goal`, `later`, `context-only`, or `out-of-scope`.
   Only a current-goal mismatch may have `gate_impact: blocking`.

Keep credentials, raw user data, authenticated private URLs, and private
captures out of committed evidence and `product-conformance.md`.

## Record and route

Create the sanitized `product-conformance.md` artifact from the installed
template and a machine result based on
[the audit result example](references/audit-result.example.json). Continuity
computes the final status from coverage and findings; a caller cannot force a
failed, partial, or blocked audit to pass.

```text
.agents/continuity/bin/continuity --project-root "$PWD" audit record <audit-id> \
  --result-file <audit-result.json> \
  --worktree <execution-worktree> \
  --branch <goal-branch> \
  --artifact <product-conformance.md> \
  --update-gate
```

A passed candidate result is bound to the goal plan, behavior configuration,
repository, branch, commit, tracked and untracked source fingerprint, source
set, artifact hash, and result hash. Any later source change makes it stale.
For a genuinely non-product goal, record `product-conformance` as
`not-applicable` with concrete evidence instead of fabricating an audit.

Capture mismatch findings back into private Continuity triage:

```text
.agents/continuity/bin/continuity --project-root "$PWD" audit capture-findings <audit-id>
.agents/continuity/bin/continuity --project-root "$PWD" workflow status --audit-id <audit-id>
```

Captured findings always have `execution_authorized: false`. Current-goal
blockers return to execution within approved scope; later findings must pass
through triage and planning. Compare recurring audits without rewriting history:

```text
.agents/continuity/bin/continuity --project-root "$PWD" audit compare <audit-id> \
  --against <prior-audit-id>
```

## Completion check

Before handing off, confirm the source hierarchy is explicit, planned coverage
is fully accounted for, every non-unverifiable finding cites evidence, only
current-goal mismatches block, sensitive evidence remains private, mismatch
findings are captured when appropriate, and workflow status names the next
skill. Candidate success routes to `$continuity-merge`; failures route through
the machine-selected remediation loop.
