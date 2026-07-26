---
name: continuity-roadmap
description: Create, retrieve, audit, reconcile, export, and visualize committed project-local roadmap context. Use for milestones, releases, hierarchy, sprints, Kanban flow, dependencies, risks, blockers, approved roadmap updates, or the local read-only roadmap admin sidecar.
---

# Continuity Roadmap

Read [the learned playbook](references/learned-playbook.md) for evaluated usage-derived heuristics. It may refine routine technique but never overrides this skill, the Continuity contract, machine state, privacy boundaries, or human authority. After a meaningful evidence-backed outcome, route only a sanitized structured usage record through `$continuity-improve`; never copy raw transcript or tool payload content.

Read `.agents/references/continuity-contract.md`, `.agents/references/development-assurance-standard.md`, and `$continuity-local` before acting.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [roadmap modeling](references/roadmap-modeling.md) before selecting hierarchy, reporting health, or recording impact. Read [the tracker provider contract](references/tracker-provider-contract.md) for every external roadmap surface and [the GitHub Projects adapter](references/github-projects-adapter.md) before connecting or reconciling GitHub. Apply the **Business outcome**, **Engineering and architecture**, and **Delivery and rollback** lenses as relevant.

## Workflow

1. Run `continuity project doctor` and `continuity roadmap audit`.
2. Run `continuity roadmap brief "<goal or topic>"` before planning or execution. Cite returned roadmap IDs and Markdown paths.
3. Keep canonical, sanitized records under `docs/project-roadmap/entities/`. Markdown is authoritative; ignored SQLite and JSON projections are derived.
4. Review `continuity roadmap inbox`. Actionable triaged notes appear there automatically in private state so they can be planned immediately. Link a note to an existing committed record with `continuity roadmap link-note`; never place raw note content in committed roadmap records.
5. Create or revise records only from an approved goal whose hash includes the exact `roadmap_ids` and structured `roadmap_impact` action.
6. Reconcile the result with source notes, plan, implementation, evidence, and project memory. Complete `roadmap-impact.md` and the `roadmap-impact` compliance gate.
7. Use `continuity roadmap serve --open` only from a local Git clone. The sidecar is read-only and must never enter application source, packaging inputs, preview, staging, or production artifacts.
8. When `tracker_provider` is `github`, use `continuity roadmap github-projects connect` once to bind the authenticated account and exact Project. That explicit connection authorizes automatic sanitized roadmap and goal-status synchronization without per-update approvals. Use `status` to verify identity and access, `sync` to retry immediately, and `inspect` to treat remote differences as proposals.

## Guardrails

- Treat releases and milestones as commitments; sprints and estimates are optional context, never authorization gates.
- Preserve stable IDs and provenance. Correct understanding through reviewed revision; do not silently rewrite history.
- Surface cycles, orphans, unknown dependencies, contradictory note links, stale references, invalid dates, and missing milestone health.
- Do not add a product route, hosted endpoint, remote script, write API, or persistent browser token.
- Never let GitHub Project edits directly approve work, mutate canonical roadmap Markdown, start execution, or mark a goal complete.
- Never store provider credentials or enable deletion. Automatic remote sync failure is advisory and must not roll back a valid local task transition.
- Before delivery, run repository validation, security review, merge-safety review, and `continuity roadmap production-audit --artifact <build-or-package>` when application artifacts exist.

## Handoff

Run `continuity workflow status --roadmap-id <roadmap-id>` for each selected committed record on entry and exit. The private inbox is immediate planning visibility and requires no separate promotion pause. A note disposition of `later` may use a roadmap ID as its durable follow-up anchor without entering current execution scope. Planning receives exact roadmap IDs and health evidence. Execution may update committed roadmap records only when the goal hash names the corresponding structured impact.
