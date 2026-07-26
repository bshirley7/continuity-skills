# Experimental validity and exposure ethics

## Generalized principles

- Test whether the design can answer the stated decision question before exposing anyone: require a falsifiable hypothesis, appropriate control, unit and method of assignment, representative eligibility, stable measurement, exact treatment versions, primary outcome and guardrails, minimum meaningful effect, power or precision rationale, planned duration and analysis, interference and carryover assessment, and a decision policy that permits no-change or inconclusive outcomes.
- Make validity diagnostics block overconfident interpretation: expose allocation and sample-ratio mismatch, missing or delayed telemetry, assignment and exposure differences, contamination, attrition, identity resolution, process instability, instrumentation changes, multiple testing, optional stopping, repeated peeking, novelty, seasonality, carryover and model-assumption failures; quarantine or qualify results when their cause is unresolved.
- Communicate evidence without binary significance theater: show estimand, population, metric formula, numerator and denominator, base rates, absolute and relative effects, interval estimates, sample and exposure counts, practical importance, uncertainty and assumptions; distinguish planned from exploratory analyses and no evidence from evidence of no meaningful effect; correct for multiplicity and avoid selecting only favorable metrics, windows or segments.
- Evaluate exposure as an intervention affecting people, not merely traffic: identify who bears risk and who receives benefit, foreseeable physical, psychological, financial, privacy, accessibility, autonomy, social and legal harms, vulnerable or underrepresented groups, cumulative and third-party effects, voluntariness and reasonable expectations; minimize exposure, prohibit deceptive or inherently inappropriate treatments, provide consent or notice where required, preserve withdrawal and redress, and never let a positive aggregate metric excuse disproportionate harm.
- Bind rollout decisions to exact evidence and continuing safeguards: predefine harm and health thresholds, pause and rollback conditions, review authority and escalation; record deviations, exclusions, subgroup effects, uncertainty, dissent and reasons; separate experimental evidence from authorization; ramp exposure progressively when appropriate; verify recovery after rollback; and monitor durability, adaptation, complaints and delayed harms after the formal test ends.

## Method

- Write the decision, hypothesis, exact treatments, assignment unit, eligibility, exposure, estimand, primary outcome, guardrails, minimum effect, power or precision, duration, stopping and decision policy before launch.
- Map each metric to its population, numerator, denominator, event source, latency, missingness, direction, expected range and practical consequence.
- Test randomization, allocation, sample ratio, exposure, contamination, interference, instrumentation, process stability, assumptions and planned-versus-exploratory status before interpreting effects.
- Inventory who is exposed, who is excluded, who may be indirectly affected, what burdens and benefits occur, and whether vulnerability, power or deception changes the required safeguards.
- Review absolute and relative effects, intervals, practical importance, guardrails, subgroup coverage, multiple comparisons, novelty, carryover and long-term risk together.
- Bind the decision, rollout, pause or rollback to the exact evidence snapshot and verify continuing safeguards and delayed outcomes.

## Ethical safeguards

- Do not experiment with deceptive, coercive, discriminatory, unsafe or rights-violating treatments merely because exposure is temporary or measurable.
- Do not treat ordinary product use or a broad privacy notice as unlimited permission for unrelated, sensitive or high-risk experimentation.
- Do not select vulnerable, captive, low-power or easily manipulated populations because they are convenient or less likely to complain.
- Do not hide an experiment, withhold material risks or omit debriefing when incomplete disclosure is unnecessary or creates more than minimal risk.
- Do not optimize engagement, conversion, revenue or retention by degrading comprehension, autonomy, privacy, accessibility, welfare or exit.
- Do not search many metrics, segments, windows and stopping points and present the most favorable result as a planned finding.
- Do not continue exposure after a credible harm threshold, safety signal or data-integrity failure merely to reach significance.
- Do not interpret aggregate benefit as evidence that every subgroup benefits or that concentrated harm is acceptable.
- Do not allow an experiment result to authorize deployment, policy, payment, publication or irreversible action without the required separate authority.

## Variation levers

- Use stronger review, consent, monitoring, subgroup analysis and stop rules as sensitivity, vulnerability, irreversibility, deception and consequence increase.
- Use fixed-horizon, sequential or adaptive methods only when their assumptions and stopping logic are explicit and matched to the analysis.
- Use progressive exposure and durable holdouts when operational and long-term risks justify them, while reviewing the ethics of withholding or extending treatment.
- Use qualitative research and complaint, accessibility and support evidence alongside metrics when lived effects cannot be captured by event telemetry alone.

## Tensions and tradeoffs

- Disclosure and consent support autonomy while changing behavior and potentially reducing the validity of some research.
- Large samples detect small effects while exposing more people and encouraging trivial effects to appear important.
- Long tests reveal adaptation and delayed effects while prolonging exposure to inferior or harmful treatment.
- Subgroup analysis reveals concentrated effects while increasing multiplicity, privacy risk and unstable conclusions.
- Automatic stopping and rollback reduce harm while brittle thresholds can react to noise or miss harms absent from telemetry.

## Failure modes

- The interface validates field completion but not whether the design can identify the intended causal effect.
- Sample-size guidance ignores base rate, minimum meaningful effect, power, clustering, attrition or multiple variants.
- A result remains actionable despite unresolved sample-ratio mismatch or instrumentation change.
- A p-value or win probability becomes a binary truth badge without effect size, interval, assumptions or practical importance.
- The denominator changes between setup, monitoring and results without a visible semantic warning.
- Exploratory segment findings are promoted as confirmed and used for targeting.
- Only the primary success metric is shown while guardrails, complaints and accessibility outcomes are hidden.
- People cannot avoid, withdraw from or obtain redress for sensitive or harmful exposure.
- A favorable average masks concentrated harm or exclusion in a vulnerable or underrepresented group.
- The experiment ends but exposure persists without an evidence-bound rollout decision or delayed-harm monitoring.

## Anti-patterns

- Valid form means valid experiment.
- Power by sample count alone.
- Trust results despite broken allocation.
- Significance as truth badge.
- Drifting denominator.
- Exploratory means confirmed.
- One metric wins.
- No exit from exposure.
- Average hides harm.
- Test ended, treatment continues.

## Acceptance and review questions

- Can the proposed design identify the intended effect with an appropriate control, assignment unit, eligibility, stable measurement, exact treatments, outcome, guardrails, minimum effect, precision, duration and analysis?
- Are allocation, sample ratio, exposure, missing data, contamination, interference, instrumentation, stability, multiplicity, peeking, novelty, carryover and assumption failures visible before interpretation?
- Are population, estimand, formulas, denominators, base rates, absolute and relative effects, intervals, sample and exposure counts, practical importance and planned versus exploratory status explicit?
- Who bears exposure and harm, who receives benefit, which groups are vulnerable or underrepresented, and what consent, notice, minimization, withdrawal, protection and redress are required?
- Do primary outcomes, guardrails, complaints, accessibility, subgroup effects and delayed harms inform the decision together rather than allowing one aggregate metric to dominate?
- Is rollout or rollback separately authorized, exact-evidence bound, progressively controlled, recoverable and monitored after the formal experiment ends?
