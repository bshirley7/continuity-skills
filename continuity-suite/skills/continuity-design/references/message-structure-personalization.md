# Personalization

## Generalized principles

- Explain what each personalization input changes, where it applies, how long it persists, and whether it was explicitly supplied, inferred from behavior, inherited from policy, or derived from current context.
- Use personalization to set reversible starting points, ordering, examples, density, or assistance without hiding the full capability set or treating role, experience, and interest answers as permanent identity.
- Give users correction at the level of the signal and outcome—item, topic, source, goal, role, default, inferred fact, or remembered detail—and state what future behavior the correction will affect.
- Separate personal preferences from team defaults, organization policy, shared data, customer-facing behavior, and legally required settings; make precedence and blocked overrides explicit.
- Provide a usable non-personalized or default path plus controls to pause, reset, inspect, export, or delete personalization inputs without making core access conditional on optional profiling.
- Label personalized, contextual, sponsored, generally popular, and editorially selected content distinctly enough that users can understand why it appeared and evaluate its relevance or incentive.

## Variation levers

- Collect only the minimum onboarding inputs needed for an immediate useful starting state.
- Use direct controls for stable preferences and lightweight feedback for evolving recommendations.
- Offer organization-managed defaults with clearly identified personal override boundaries.
- Use local or session-only personalization when persistence is unnecessary.
- Show a compact reason-for-this-item explanation with deeper provenance and control on demand.

## Tensions and tradeoffs

- More input can improve relevance while increasing burden and privacy exposure.
- Inference reduces setup while increasing surprise and error.
- Granular controls improve agency while obscuring the combined outcome.
- Persistent memory improves continuity while increasing correction and deletion obligations.
- Organization defaults improve consistency while reducing personal fit.
- A personalized feed improves relevance while narrowing exposure and obscuring incentives.

## Failure modes

- A preference is collected without explaining the resulting change.
- An inferred trait is presented as fact or permanent identity.
- Users cannot distinguish personal, team, and organization scope.
- Feedback changes one item but not the underlying signal users intended to correct.
- Reset or deletion leaves undisclosed derived state active.
- Core access is blocked until optional profile questions are answered.
- Sponsored, popular, contextual, and personalized items appear indistinguishable.

## Anti-patterns

- Mandatory interest quiz.
- Personalized for you with no explanation.
- Role treated as identity.
- Dismiss button with unknown future effect.
- One toggle for many data uses.
- Reset that preserves hidden inference.
- Organization policy presented as personal choice.
- Sensitive inference from weak behavior.
- Personalization dark pattern.
- No neutral default experience.

## Acceptance and review questions

- Does each input state what changes, where, for how long, and whether it is supplied, inferred, inherited, or contextual?
- Are personalized starting points reversible without hiding capabilities or fixing users to an identity?
- Can users correct the exact item, signal, goal, role, default, inference, or memory and understand the future effect?
- Are personal, team, organization, shared-data, customer-facing, and required scopes clearly separated?
- Is there a usable default path and a way to pause, reset, inspect, export, or delete personalization?
- Are personalized, contextual, sponsored, popular, and editorial selections distinguishable?
- Do deletion and reset explain what derived or retained state remains?
