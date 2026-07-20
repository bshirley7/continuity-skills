# Situation awareness and resilient control

## Generalized principles

- Support all three situation-awareness horizons: help operators perceive relevant state and change through source, time, freshness, threshold and missingness; comprehend meaning through scope, dependency, consequence, confidence and operating mode; and project plausible evolution through trend, rate, capacity, propagation, deadlines, forecast assumptions, and explicit uncertainty.
- Direct scarce attention according to required response, time-to-consequence, confidence, novelty, scope, and user impact rather than raw event volume: suppress duplicates, correlate without hiding evidence, distinguish advisory, exception, warning, and emergency, preserve nonvisual encoding, make every alarm actionable, and expose overload, stale sensing, blind spots, and suppressed signals.
- Maintain a shared but challengeable common operating picture: define essential information, canonical time and state, known, inferred, unknown and disputed content, objectives, affected scope, resources, ownership, decisions, actions and outcomes, data age, and the route to raw evidence; make changes and conflicting reports visible instead of silently converging them.
- Preserve resilient human control under degradation and automation: display operating mode, authority, decision-aid rationale and limits, current and queued automated actions, target and blast radius, acceptance and completion feedback, partial failure, safe stop, manual fallback, rollback, and the conditions for transferring or resuming control; require stronger independent action for safety-critical and irreversible commands.
- Design response as a learning control loop: coordinate explicit command, operations, communication, planning and specialist roles; verify containment, restoration and residual risk against objectives and affected users; preserve a blameless evidence timeline; and convert detection, mitigation, coordination and communication lessons into owned changes whose effectiveness is later measured.

## Method

- Define operational objectives, normal and degraded states, critical decisions, time horizons, essential information, sensing sources, freshness, uncertainty, dependencies, and potentially affected scope.
- Classify alerts by required action, time-to-consequence, confidence, novelty, impact, persistence, correlation, escalation, suppression, and acknowledgment semantics.
- Specify the common operating picture, canonical timeline, command and specialist roles, objectives, resources, task ownership, communication cadence, decision authority, handoff, and dissent or correction route.
- Map automation modes, recommendations, rationale, authority, target, blast radius, pending effects, completion feedback, partial failure, safe stop, fallback, rollback, and control transfer.
- Test event floods, missing and stale data, contradictory sources, false positives, cascading dependencies, workload peaks, fatigue, shift handoff, automation surprise, partial recovery, and recurrence.
- Measure correct detection, comprehension and projection, missed and nuisance alerts, time to meaningful action, false certainty, workload, handoff loss, mitigation side effects, recovery verification, recurrence, and completed learning.

## Ethical safeguards

- Do not use color, sound, animation, event count, or opaque composite scores as the sole evidence of urgency, confidence, consequence, or required action.
- Do not hide stale, missing, suppressed, inferred, simulated, or contradictory operational data behind a polished common picture.
- Do not automate consequential mitigation from uncertain correlation without visible rationale, authority, scope, safe stop, effect evidence, and human override appropriate to risk.
- Do not blame individual operators for failures produced by alarm floods, poor staffing, hidden modes, inadequate controls, ambiguous authority, or unsafe organizational incentives.
- Do not optimize mean response or closure time while excluding false positives, unintended mitigation, unresolved impact, fatigue, recurrence, and learning completion.
- Do not expose sensitive operational, personal, security, or safety evidence beyond the roles and duration necessary for response, review, and accountable retention.

## Variation levers

- Increase sensing diversity, redundancy, explicit uncertainty, dual coding, independent confirmation, safe-state controls, and authorization as consequence and irreversibility rise.
- Use compact expert displays for trained frequent operators and guided situation summaries with direct evidence paths for occasional or cross-functional responders.
- Use one lead and lightweight coordination for bounded exceptions, then activate specialized operations, planning, communication, safety, legal, or domain roles as complexity grows.
- Use automation for high-volume stable detection and reversible response, and preserve human judgment for ambiguous, novel, cascading, ethical, or high-consequence conditions.

## Tensions and tradeoffs

- More telemetry improves coverage while increasing noise, workload, correlation bias, and false confidence.
- A unified picture improves coordination while flattening uncertainty, local knowledge, and conflicting evidence.
- Automation shortens response while degrading mode awareness, practiced skill, and ability to intervene safely.
- Strong command clarifies authority while discouraging dissent and creating a decision bottleneck.
- Rapid restoration reduces immediate impact while bypassing reconciliation, residual-risk review, and systemic learning.

## Failure modes

- Operators can see current values but cannot understand meaning, consequence, likely evolution, freshness, or uncertainty.
- Alarm priority reflects system category or color rather than required action and time-to-consequence.
- A common operating picture silently replaces disputed or stale source evidence with one confident narrative.
- Automation changes operational state without clear mode, target, rationale, authority, pending effect, completion, failure, or override.
- Command roles exist but objectives, resource state, decision authority, task ownership, handoff, and communication cadence are unclear.
- Recovery is declared without user-impact, health, reconciliation, residual-risk, observation-window, or recurrence evidence.
- Lessons are documented but changes lack owners, deadlines, deployment verification, and measured effectiveness.

## Anti-patterns

- Telemetry without meaning.
- Alarm by color.
- One picture, false certainty.
- Automation surprise.
- Command without objectives.
- Restore and disappear.
- Blame the operator.
- Lessons without control change.

## Acceptance and review questions

- Can operators perceive relevant state and change, comprehend current meaning, and project plausible evolution with source, time, freshness, scope, confidence, dependency, and uncertainty?
- Are alerts prioritized by response, time-to-consequence, confidence, novelty, impact, and persistence with actionable, accessible, overload-aware presentation?
- Does the common picture expose essential information, known and disputed state, objectives, resources, decisions, actions, outcomes, age, and raw evidence?
- Are automation mode, rationale, limits, authority, target, blast radius, pending effects, feedback, partial failure, safe stop, fallback, rollback, and control transfer visible?
- Are command, operations, communication, planning, specialist, objective, task, resource, handoff, and dissent responsibilities explicit?
- Does recovery verify objectives, affected users, health, reconciliation, residual risk, observation, recurrence, learning ownership, deployment, and effectiveness?
