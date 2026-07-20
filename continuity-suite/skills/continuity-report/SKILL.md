---
name: continuity-report
description: Generate evidence-backed completion reports, active-run updates, morning portfolio reports, memory-health summaries, compliance status, and feedback requests. Use when work finishes, at the morning checkpoint, or whenever the user asks for project status.
---

# Continuity Report

Report recorded state without converting notes, feedback, or pending plans into implied commitments.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$continuity-local`, project manifests, feedback, evidence, compliance ledgers, and `.continuity/config.json`.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [morning report examples](references/morning-report-examples.md) before generating a morning or completion report. Apply the **Evidence and confidence**, **Business outcome**, and **Security and privacy** lenses as relevant; use the local examples for decision value and exception salience.

## Required assurance

- Derive every status, completion, validation, security, mergeability, and memory claim from recorded evidence; distinguish passed, pending, failed, blocked, partial, and not-applicable states precisely.
- Redact secrets, personal data, raw captures, private ledger content, credentials, and sensitive operational details from project and portfolio reports.
- Audit report completeness against notes, memory IDs, plan hash, feedback, acceptance criteria, exclusions, changed files, validation, security review, merge safety, documentation, and memory impact. Surface stale or contradictory evidence.
- For design-bound goals, report the exact design revision, affected surfaces or artifacts, verified alignment, approved deviations, unresolved drift, and design debt without presenting subjective claims as machine-verified.

```text
.agents/continuity/bin/continuity --project-root "$PWD" report project
.agents/continuity/bin/continuity --project-root "$PWD" --json report morning
.agents/continuity/bin/continuity --project-root "$PWD" memory audit
.agents/continuity/bin/continuity --project-root "$PWD" audit due
.agents/continuity/bin/continuity --project-root "$PWD" note patterns --min-count 2
.agents/continuity/bin/continuity --json portfolio report --sanitized --root <workspace-root>
```

The morning report is mandatory even when no goal ran. Lead with `decisions_needed`, `completed_overnight`, and `blocked_or_at_risk`. Every decision must name its goal, note, or audit, recommendation, evidence or PR, and human disposition. Treat `review-ready` as awaiting human review, not completion. Include note counts by exact lifecycle stage, stage-entry dates, later-work anchors, blocked or remediation tracks, and confidence-qualified unconfirmed relationship suggestions alongside configuration, scheduler, memory, roadmap, product-audit freshness and findings, test, security, merge, and compliance health. Cap relationship decisions at the suite limit; broader low-confidence results belong in explicit triage. Suggestions never authorize execution.

For a portfolio report, use `portfolio report --sanitized`. Its deterministic allowlist emits counts and health states only; it cannot emit raw captures, note text, local paths, private ledgers, approval text, task IDs, claims, evidence links, credentials, or locks. Do not replace that command with agent-authored aggregation.

Never claim completion, mergeability, security, or review readiness without evidence. Publish a completion report immediately when work ends and preserve later feedback for the next cycle.

Every reported decision must include `allowed_dispositions` copied from the machine workflow contract or a valid note disposition command. Include `blocked_dispositions` and exact evidence failures separately; never present them as executable. Honor future `review_after` dates and the latest matching pattern disposition so deferred, accepted, or dismissed decisions do not recur prematurely. Include per-goal workflow stage, current machine evidence, security and merge state, compliance blockers, evidence references, queue counts, memory and roadmap health, and active scheduler runs. Do not emit prose-only remediation.

## Handoff

Run `continuity workflow status` before generating a report and after any human disposition is recorded. Reports recommend the returned next skill and exact command template but never execute a human-required action.
