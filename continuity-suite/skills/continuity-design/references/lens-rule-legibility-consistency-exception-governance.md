# Rule legibility, consistency, and exception governance

## Generalized principles

- Model a policy as an explicit decision function: identify authoritative purpose and basis, subject, resource, operation, environment, target and applicability, required attributes and their provenance, condition logic, effect, obligations and advice, missing and indeterminate behavior, priority and combining algorithm, default outcome, enforcement point, version, effective time, and accountable owner; keep normative requirement distinct from explanatory guidance and implementation mechanism.
- Make precedence and conflict deterministically legible: expose hierarchy, specificity, inheritance, order, overrides, deny or permit priority, one-applicable requirements, incompatible obligations, circularity and unreachable rules; show the same representative case through each applicable rule and the combination path; treat no match, missing attributes, error, indeterminate, deny, permit, conditional outcome, and not applicable as distinct states.
- Treat attribute evidence as part of the rule, not invisible input: for consequential attributes preserve definition, allowable values, source authority, subject, collection or assertion method, assurance, freshness, validity, jurisdiction, purpose limitation, transformation, quality, missing semantics, dispute state, and update path; surface which exact values drove a case outcome and fail safely when required evidence is stale, contradictory, unauthorized, or unavailable.
- Test policy as a bounded behavioral specification: cover intended permits and denials, boundaries, defaults, missing and malformed attributes, conflicts, obligations, exceptions, historical incidents, protected and vulnerable groups, adversarial cases, unchanged behavior, and property invariants; bind results and coverage to exact rule, data, attribute and engine versions, then use shadow or staged evaluation to compare expected and actual distributions before enforcement.
- Govern exceptions and corrective action as evidence-bearing feedback: require a narrow case, reason, risk, reviewer authority and independence, compensating controls, effective and expiry time, monitoring, revocation, affected parties, decision and appeal; distinguish exception from rule change and enforcement failure; aggregate exception use, inconsistent outcomes, overrides, incidents and complaints to find root causes, repair deficient policy, verify remediation, and preserve prior decisions without normalizing permanent bypass.

## Method

- Define purpose, authority, subjects, resources, operations, environments, applicability, attributes, conditions, effects, obligations, missing and error semantics, precedence, defaults, enforcement, owner, version, and timing.
- Build a precedence and conflict map covering hierarchy, inheritance, specificity, order, combining algorithms, incompatible obligations, circularity, unreachable rules, and every terminal decision state.
- Inventory each decision attribute's definition, values, authority, subject, method, assurance, freshness, jurisdiction, purpose, transformation, quality, dispute, and correction path.
- Create version-bound positive, negative, boundary, missing, malformed, conflict, exception, regression, invariant, group-impact, incident, and adversarial test cases.
- Run shadow or staged comparison against representative production distributions and inspect decision deltas, obligations, affected populations, error and indeterminate states, and enforcement compatibility.
- Review exception, override, appeal, complaint, incident, false outcome, and enforcement-failure patterns; assign root cause, corrective action, owner, deadline, verification, and policy revision.

## Ethical safeguards

- Do not disguise discretion, policy gaps, missing evidence, inconsistent enforcement, or human override as deterministic system output.
- Do not use proxy attributes, stale classifications, disputed records, protected traits, or correlated variables without explicit authority, necessity, quality, fairness review, and correction.
- Do not expose sensitive decision inputs or complete subject profiles merely to explain one rule outcome; reveal the minimum evidence needed for understanding, contesting, and oversight.
- Do not implement exceptions through secret allowlists, permanent bypasses, falsified attributes, altered history, or reviewer shopping.
- Do not optimize policy success around denial rate, compliance count, cost reduction, or enforcement volume while excluding false outcomes, disparate burden, appeals, incidents, workarounds, and unmet purpose.
- Do not treat acknowledgement, absence of complaint, technical conformance, or one passing simulation as proof that a policy is understood, lawful, fair, effective, or correctly enforced.

## Variation levers

- Use plain-language policy with structured decision tables for human-administered rules and executable policy with verified equivalent explanations for automated enforcement.
- Use conservative defaults for high-consequence safety and access boundaries, while providing explicit not-applicable and escalation states where automatic denial would create harm.
- Use local bounded exceptions for genuinely exceptional cases and revise the base policy when exception frequency or pattern demonstrates a deficient rule.
- Increase independent review, group-impact analysis, shadow duration, rollout staging, explanation, appeal, and remediation evidence with consequence and discretion.

## Tensions and tradeoffs

- Simple rules improve comprehension while complex realities require more attributes, conditions, precedence, and exceptions.
- Strict consistency reduces arbitrary outcomes while uniform rules can reproduce inequity or ignore material context.
- Detailed explanations improve contestability while exposing sensitive attributes, security controls, or evasion opportunities.
- Fail-closed behavior limits unauthorized outcomes while missing or stale evidence can deny legitimate high-consequence needs.
- Temporary exceptions preserve operations while accumulating into an ungoverned parallel policy.

## Failure modes

- A policy cannot be stated as an inspectable function of subject, resource, operation, environment, attributes, conditions, effect, obligations, precedence, and default.
- Overlapping rules produce different outcomes depending on hidden order or implementation details.
- A decision uses stale, ambiguous, transformed, disputed, or unauthorized attributes without showing their role.
- Testing covers happy-path examples but omits boundaries, conflicts, defaults, missing data, exceptions, group impacts, and regressions.
- An exception has no governing rule, bounded scope, independent review, compensating control, expiry, monitoring, appeal, or history.
- Decision evidence records only final allow or deny and cannot reconstruct version, facts, rule path, obligations, exception, and enforcement.
- Recurring overrides and false outcomes are treated as operator behavior rather than evidence of policy deficiency.

## Anti-patterns

- Policy as prose only.
- Hidden rule order.
- Attribute without provenance.
- Happy-path policy test.
- Exception forever.
- Secret allowlist.
- Decision without evidence.
- Blame the override.

## Acceptance and review questions

- Can the policy be inspected as purpose, authority, subject, resource, operation, environment, applicability, attributes, conditions, effect, obligations, missing behavior, precedence, default, enforcement, version, time, and owner?
- Are hierarchy, inheritance, specificity, order, combining, conflicts, circularity, unreachable rules, and every terminal decision state deterministic and case-explainable?
- Does each material attribute expose definition, values, authority, subject, method, assurance, freshness, jurisdiction, purpose, transformation, quality, dispute, and correction?
- Do version-bound tests cover permits, denials, boundaries, defaults, missing and malformed data, conflicts, obligations, exceptions, regressions, invariants, groups, incidents, and adversarial cases?
- Does staged evidence show decision and obligation deltas, affected populations, error and indeterminate states, group burdens, and enforcement compatibility before activation?
- Are exceptions, overrides, appeals, complaints, incidents, false outcomes, root causes, corrective actions, verification, and policy revisions governed and historically linked?
