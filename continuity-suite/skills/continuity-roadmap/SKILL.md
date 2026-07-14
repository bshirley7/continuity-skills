---
name: continuity-roadmap
description: Create, retrieve, audit, reconcile, export, and visualize committed project-local roadmap context. Use for milestones, releases, hierarchy, sprints, Kanban flow, dependencies, risks, blockers, approved roadmap updates, or the local read-only roadmap admin sidecar.
---

# Continuity Roadmap

Read `.agents/references/continuity-contract.md`, `.agents/references/development-assurance-standard.md`, and `$continuity-local` before acting.

## Workflow

1. Run `continuity project doctor` and `continuity roadmap audit`.
2. Run `continuity roadmap brief "<goal or topic>"` before planning or execution. Cite returned roadmap IDs and Markdown paths.
3. Keep canonical, sanitized records under `docs/project-roadmap/entities/`. Markdown is authoritative; ignored SQLite and JSON projections are derived.
4. Link private notes with `continuity roadmap link-note`; never place raw note content in committed roadmap records.
5. Create or revise records only from an approved goal whose hash includes the exact `roadmap_ids` and structured `roadmap_impact` action.
6. Reconcile the result with source notes, plan, implementation, evidence, and project memory. Complete `roadmap-impact.md` and the `roadmap-impact` compliance gate.
7. Use `continuity roadmap serve --open` only from a local Git clone. The sidecar is read-only and must never enter application source, packaging inputs, preview, staging, or production artifacts.

## Guardrails

- Treat releases and milestones as commitments; sprints and estimates are optional context, never authorization gates.
- Preserve stable IDs and provenance. Correct understanding through reviewed revision; do not silently rewrite history.
- Surface cycles, orphans, unknown dependencies, contradictory note links, stale references, invalid dates, and missing milestone health.
- Do not add a product route, hosted endpoint, remote script, write API, or persistent browser token.
- Before delivery, run repository validation, security review, merge-safety review, and `continuity roadmap production-audit --artifact <build-or-package>` when application artifacts exist.
