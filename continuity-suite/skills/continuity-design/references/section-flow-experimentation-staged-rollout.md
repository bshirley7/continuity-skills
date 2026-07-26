# Experimentation and staged rollout

## Generalized principles

- Make the experiment a versioned decision contract: preserve the decision question, falsifiable hypothesis, rationale and prior evidence, accountable owner and reviewers, exact control and treatment artifacts, unit and method of assignment, eligibility and exclusions, traffic allocation, exposure event, primary outcome, guardrails, segments, minimum meaningful effect, analysis model, power or precision target, planned duration, stopping rules, risk controls, rollback path and decision policy; material changes create a linked revision rather than rewriting the running test.
- Keep assignment, exposure and denominator semantics continuously inspectable: distinguish eligible, assigned, reached, exposed, engaged, converted and analyzed populations; show randomization unit, sticky assignment, mutual exclusion, holdouts, allocation, ramp history, bot and employee treatment, missing events, late data, sample-ratio mismatch, contamination and cross-device or cross-session identity limits before presenting an effect estimate.
- Present evidence as a decision input rather than a winner badge: show metric definition, direction, numerator and denominator, absolute and relative effects, uncertainty, sample and exposure counts, time window, data freshness, guardrail outcomes, planned and exploratory analyses, subgroup coverage, novelty and carryover risk, quality diagnostics and practical significance; distinguish no evidence, insufficient evidence, evidence of no material effect and evidence of harm.
- Link experiment state to staged operational control: distinguish draft, validated, approved, scheduled, running, paused, degraded, stopped, inconclusive, harmful, completed, rolling out, rolled back and archived states; expose environment, target audience, current and historical allocation, dependencies, health and harm guardrails, responsible actor, automatic and manual stop conditions, rollback target and verification before increasing exposure or declaring completion.
- Close the loop with a durable decision and learning record: bind ship, iterate, stop, rollback or no-change decisions to the exact experiment revision and evidence snapshot; record interpretation, uncertainty, tradeoffs, affected and underrepresented groups, observed harms, deviations, reasons and dissent; separate experiment completion from product authorization; monitor post-rollout durability and guardrails; and make prior findings discoverable without treating them as timeless truth.

## Variation levers

- Use lightweight contracts for low-risk reversible presentation tests and independent review, explicit consent or prohibition for sensitive, deceptive, vulnerable or high-consequence exposure.
- Use simple fixed allocation for stable low-risk settings and progressive ramping with automatic guardrails for operationally risky changes.
- Increase subgroup planning, duration, long-term measures and qualitative follow-up when effects may differ by vulnerability, accessibility, geography or repeated exposure.
- Use compact routine summaries for trained experimenters with direct access to exact definitions, diagnostics, revisions, code and decision evidence.

## Tensions and tradeoffs

- Fast iteration increases learning velocity while encouraging underpowered tests, peeking and repeated exposure.
- A single primary metric sharpens interpretation while omitting important harms and distributional effects.
- Progressive rollout limits blast radius while time trends and changing populations complicate causal interpretation.
- Granular segmentation can reveal heterogeneity while increasing false discoveries, privacy risk and discriminatory targeting.
- Persistent holdouts support long-term measurement while withholding a beneficial change or preserving a harmful control.

## Failure modes

- The test begins without a decision question, hypothesis, minimum meaningful effect, stopping rule or decision policy.
- Variant labels exist but the exact artifacts, configuration versions or exposure event are not bound.
- Assigned users, exposed users and metric denominators are treated as the same population.
- A sample-ratio mismatch, missing telemetry, contamination or changing allocation is hidden beneath a result card.
- A statistically significant relative lift is shown without absolute effect, uncertainty, volume, duration or practical importance.
- A non-significant result is described as proof that variants are equal.
- Exploratory segments and metrics are presented as if they were planned confirmatory analyses.
- A winner is selected while guardrails, accessibility, complaints or vulnerable-group outcomes worsen.
- The flag reaches full exposure without health monitoring, stop conditions, rollback target or accountable approval.
- Experiment completion silently authorizes permanent release.
- The decision record omits deviations, uncertainty, dissent, harm and post-rollout verification.

## Anti-patterns

- Hypothesis after results.
- Variant without version.
- Assignment equals exposure.
- Hidden ratio mismatch.
- Relative lift without base rate.
- Not significant means equal.
- Segment fishing.
- Winner despite harm.
- Ramp without rollback.
- Experiment equals authorization.
- Learning without decision record.

## Acceptance and review questions

- Is the decision question, hypothesis, exact variants, assignment, eligibility, exposure, primary metric, guardrails, minimum effect, duration, stopping rule, rollback and decision policy bound to one immutable experiment revision?
- Can reviewers distinguish eligible, assigned, reached, exposed, engaged, converted and analyzed populations and inspect allocation, identity, contamination, missing-data and sample-ratio diagnostics?
- Are absolute and relative effects, uncertainty, denominators, duration, freshness, practical importance, guardrails, subgroup coverage and planned versus exploratory analyses visible?
- Are experiment lifecycle, feature-flag state, environment, exposure ramp, operational health, harm thresholds, stop conditions and rollback represented together?
- Does choosing a treatment create an evidence-bound decision record without automatically authorizing deployment or full rollout?
- Are post-rollout durability, harms, complaints, accessibility and underrepresented groups monitored and linked back to the original learning?
