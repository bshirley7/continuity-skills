---
name: continuity-design
description: Create, compare, select, and approve an exact project design direction using project captures, approved memory, PRDs, feature requests, existing design context, and installed offline reference packs. Use when asked to establish UX/UI direction, create or revise docs/design/design.md, resolve design tradeoffs, or bind implementation planning to an approved design. Design approval publishes only the exact design document and never authorizes implementation.
---

# Continuity Design

Work entirely offline from the installed reference catalog. Do not browse for design examples or access an external maintenance system from this skill.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), [decision lenses](../../references/decision-lenses.md), and the [Continuity contract](../../references/continuity-contract.md). Machine state and approval boundaries remain authoritative.

## Preconditions

1. Run `continuity project doctor` and confirm the `design` collection is enabled and healthy.
2. Retrieve relevant captures, trusted memory, PRDs, feature requests, product documentation, application structure, existing interface or artifact context, and any existing `docs/design/design.md`. Use that evidence to reconstruct the working title, intent, audiences, and target modalities; do not require the user to know or supply those fields.
3. Read [catalog.json](references/catalog.json). Treat industry, section, theme, message-structure, and lens labels as optional internal retrieval aids, not questions the user must answer or concepts the design must name. Read category references when the user explicitly supplies a matching concept or the project context makes a reference materially useful. Category packs refine their foundation; they do not replace it. Apply [lens-routing.json](references/lens-routing.json) privately as a review aid when lenses are not explicit. Record inferred checks and pack provenance in private machine state without requiring the design document to name them.
4. Treat existing favorable behavior and explicit non-regression requirements as constraints, not as disposable context.

## Direction workflow

1. Prepare a private design input from [design-input.example.json](references/design-input.example.json). Derive its working title, intent, audiences, and targets from the request and retrieved project evidence. Treat them as agent-authored working fields, not user intake requirements. Record uncertain but useful conclusions in `working_assumptions` and unresolved material questions in `open_questions`. Preserve the user's natural language. Do not ask the user to classify the work by industry, section, theme, message structure, lens, style taxonomy, or other design terminology. Include any such field only when the user explicitly supplies it. Use `consequences`, `workflow_signals`, `interaction_signals`, and `risk_signals` internally when those conditions are evident.
2. Proceed with the strongest evidence available. Do not stop merely because the title, intent, audience, target, style, or desired approach is incomplete. Choose a provisional scope, make uncertainty visible, and produce useful directions. Ask concise questions alongside the result when an answer would materially improve the next revision; incorporate later answers through normal design revision.
3. Choose the adaptive direction count:
   - one when the intended approach and constraints are settled;
   - two when one material tradeoff remains;
   - three when multiple materially different approaches remain plausible.
4. Derive each direction creatively from the project intent, audience, content, constraints, existing experience, and consequential context. Do not turn the catalog taxonomy into the concept, outline, headings, or vocabulary of the result unless the user explicitly requested those concepts. Use inferred packs as silent creative context and review checks, not as a recipe or a checklist the design must recite. Resolve tensions through [composition precedence](references/composition-precedence.json); never resolve them by prompt order or by averaging incompatible guidance. Translate the resulting direction into every required dimension in [design-grammar.md](references/design-grammar.md) using concrete design decisions. Autonomy, comprehension, accessibility, refusal, correction, exit, and recovery remain non-negotiable safeguards rather than required stylistic callouts.
5. Apply category-pack acceptance questions as review gates. When foundation and category guidance differ in specificity, use the category guidance without weakening foundation safety or accessibility constraints.
6. Apply every pack according to its `modalities` entry for the requested target:
   - `validated` means the pack contains direct evidence for that modality;
   - `inferred` means apply only its `modality_independent_principles` and label the application inferred;
   - `not-applicable` means do not apply that pack to the target.
   Report `mixed` when a target combines validated and inferred packs. An empty modality-independent list supplies no inferred guidance. `campaign` and `platform` are evidence contexts used by applicable packs, not additional publication targets or implementation authority.
7. Run `continuity design draft --input <design-input.json>`.
8. Require the user to select a direction or explicitly combine directions with `continuity design select`.
9. Present the exact private draft and its SHA-256 hash. Do not promote it without exact approval.
10. After the user approves the exact ID, revision, and hash, run `continuity design approve`. This writes `docs/design/design.md` and `.continuity/design.json`.

## Approval boundary

The required authorization text is printed by `design select` and must name the design ID, revision, and exact hash. Approval authorizes publication of that exact document only. It does not create, approve, revise, dispatch, or execute a goal.

A later design revision creates new evidence. It never changes an existing goal automatically. When implementation is later planned, include the approved design ID in `design_ids`; `$continuity-plan` derives and hash-binds the exact design revision.

## References

- [industries.md](references/industries.md)
- [sections-and-flows.md](references/sections-and-flows.md)
- [themes.md](references/themes.md)
- [message-structures.md](references/message-structures.md)
- [ux-lenses.md](references/ux-lenses.md)
- [lens-routing.json](references/lens-routing.json)
- [composition-precedence.json](references/composition-precedence.json)
- [evaluation-scenarios.json](references/evaluation-scenarios.json) (offline validation only)
- [design-grammar.md](references/design-grammar.md)

Reviewed psychology overlays include [Perception, salience, and affordance](references/lens-perception-salience-affordance.md), [Choice, comparison, and decision integrity](references/lens-choice-comparison-decision-integrity.md), [Mental models, comprehension, and transfer](references/lens-mental-model-comprehension-transfer.md), [Research bias and evidence validity](references/lens-research-bias-evidence-validity.md), [Motivation, progress, and temporal agency](references/lens-motivation-progress-temporal-agency.md), [Memory, learning, and experience continuity](references/lens-memory-learning-experience-continuity.md), [Feedback, feedforward, and temporal state](references/lens-feedback-feedforward-temporal-state.md), and [Social influence and persuasion integrity](references/lens-social-influence-persuasion-integrity.md).

Category references are discovered through [catalog.json](references/catalog.json). Current reviewed overlays include [Consumer](references/industry-consumer.md), [B2B and SaaS](references/industry-b2b-saas.md), [Finance](references/industry-finance.md), [Health](references/industry-health.md), [Commerce](references/industry-commerce.md), [Media and social](references/industry-media-social.md), [Travel](references/industry-travel.md), [Education](references/industry-education.md), [Developer and AI](references/industry-developer-ai.md), [Professional services](references/industry-professional-services.md), [Geospatial operations](references/industry-geospatial-operations.md), [Media production](references/industry-media-production.md), [Marketing](references/section-flow-marketing.md), [Conversion](references/section-flow-conversion.md), [Onboarding](references/section-flow-onboarding.md), [Checkout](references/section-flow-checkout.md), [Dashboards](references/section-flow-dashboards.md), [Discovery](references/section-flow-discovery.md), [Creation](references/section-flow-creation.md), [Collaboration](references/section-flow-collaboration.md), [Settings](references/section-flow-settings.md), [Permissions](references/section-flow-permissions.md), [Empty and error states](references/section-flow-empty-error-states.md), [Corporate website](references/section-flow-corporate-website.md), [Editorial](references/theme-editorial.md), [Premium](references/theme-premium.md), [Calm clarity](references/theme-calm-clarity.md), [Minimal](references/theme-minimal.md), [Expressive](references/theme-expressive.md), [Data-dense](references/theme-data-dense.md), [Technical](references/theme-technical.md), [Playful](references/theme-playful.md), [Cinematic](references/theme-cinematic.md), [Utilitarian](references/theme-utilitarian.md), [Value first](references/message-structure-value-first.md), [Problem and solution](references/message-structure-problem-solution.md), [Guided narrative](references/message-structure-guided-narrative.md), [Proof first](references/message-structure-proof-first.md), [Hierarchy](references/lens-hierarchy.md), [Comprehension](references/lens-comprehension.md), [Usability](references/lens-usability.md), [Accessibility](references/lens-accessibility.md), [Interaction](references/lens-interaction.md), [Responsiveness](references/lens-responsiveness.md), [Trust](references/lens-trust.md), [Design tokens](references/lens-design-tokens.md), [Typography](references/lens-typography.md), [Component architecture](references/lens-component-architecture.md), [Theming](references/lens-theming.md), [Design-system governance](references/lens-system-governance.md), [Adaptive layout](references/lens-adaptive-layout.md), [Motion and feedback](references/lens-motion-feedback.md), [Direct manipulation](references/lens-direct-manipulation.md), and [Keyboard and expert workflows](references/lens-keyboard-expert-workflows.md).
