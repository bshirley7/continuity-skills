---
name: continuity-design
description: Create, compare, select, and approve an exact project design direction using project captures, approved memory, PRDs, feature requests, existing design context, and installed offline reference packs. Use when asked to establish UX/UI direction, create or revise docs/design/design.md, resolve design tradeoffs, or bind implementation planning to an approved design. Design approval publishes only the exact design document and never authorizes implementation.
---

# Continuity Design

Work entirely offline from the installed reference catalog. Do not browse for design examples or access an external maintenance system from this skill.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), [decision lenses](../../references/decision-lenses.md), and the [Continuity contract](../../references/continuity-contract.md). Machine state and approval boundaries remain authoritative.

## Preconditions

1. Run `continuity project doctor` and confirm the `design` collection is enabled and healthy.
2. Retrieve relevant captures, trusted memory, PRDs, feature requests, and any existing `docs/design/design.md`.
3. Read [catalog.json](references/catalog.json). For each selected axis, read its foundation reference and any category references matching the design input. Category packs refine their foundation; they do not replace it.
4. Treat existing favorable behavior and explicit non-regression requirements as constraints, not as disposable context.

## Direction workflow

1. Prepare a private design input from [design-input.example.json](references/design-input.example.json).
2. Choose the adaptive direction count:
   - one when theme, message structure, and constraints are settled;
   - two when one material tradeoff remains;
   - three when multiple axes or material ambiguities remain.
3. Draft each direction through the selected industry, section/flow, theme, message structure, and UX lenses. Make the tradeoffs legible and distinct.
4. Apply category-pack acceptance questions as review gates. When foundation and category guidance differ in specificity, use the category guidance without weakening foundation safety or accessibility constraints.
5. For document or image targets, use only principles listed in `modality_independent_principles` and mark the result `inferred`. An empty list means that pack supplies no guidance for those modalities.
6. Run `continuity design draft --input <design-input.json>`.
7. Require the user to select a direction or explicitly combine directions with `continuity design select`.
8. Present the exact private draft and its SHA-256 hash. Do not promote it without exact approval.
9. After the user approves the exact ID, revision, and hash, run `continuity design approve`. This writes `docs/design/design.md` and `.continuity/design.json`.

## Approval boundary

The required authorization text is printed by `design select` and must name the design ID, revision, and exact hash. Approval authorizes publication of that exact document only. It does not create, approve, revise, dispatch, or execute a goal.

A later design revision creates new evidence. It never changes an existing goal automatically. When implementation is later planned, include the approved design ID in `design_ids`; `$continuity-plan` derives and hash-binds the exact design revision.

## References

- [industries.md](references/industries.md)
- [sections-and-flows.md](references/sections-and-flows.md)
- [themes.md](references/themes.md)
- [message-structures.md](references/message-structures.md)
- [ux-lenses.md](references/ux-lenses.md)

Category references are discovered through [catalog.json](references/catalog.json). Current reviewed overlays include [Finance](references/industry-finance.md), [Professional services](references/industry-professional-services.md), [Marketing](references/section-flow-marketing.md), [Conversion](references/section-flow-conversion.md), [Onboarding](references/section-flow-onboarding.md), [Checkout](references/section-flow-checkout.md), [Corporate website](references/section-flow-corporate-website.md), [Editorial](references/theme-editorial.md), [Calm clarity](references/theme-calm-clarity.md), [Value first](references/message-structure-value-first.md), [Hierarchy](references/lens-hierarchy.md), and [Trust](references/lens-trust.md).
