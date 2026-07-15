# Decision Lenses

Use only the lenses triggered by the current work. A lens improves judgment; it does not create authority or require speculative work. Record `not-applicable` with a concrete reason when a configured compliance stage requires a disposition.

## Selection table

| Lens | Apply when | Questions | Typical evidence |
| --- | --- | --- | --- |
| Evidence and confidence | Always | What is observed, reported, inferred, disputed, or unknown? Is the source current and traceable? | Capture provenance, code or documentation inspection, memory citations, timestamps |
| Business outcome | A goal, campaign, objective, priority, cost, or success measure is involved | What outcome changes? Why now? What is preserved? What would make the work not worth doing? | Objective, metric, stakeholder decision, roadmap commitment |
| User and stakeholder | Behavior, workflow, feedback, accessibility, or adoption is affected | Who experiences the change? What need or friction is addressed? What positive behavior must not regress? | Feedback, acceptance scenario, support evidence, accessibility checks |
| Product behavior | User-visible or system-visible behavior changes | What is current versus desired behavior? What are boundaries, failure states, and exclusions? | Evidence triage brief, behavior examples, acceptance criteria |
| Engineering and architecture | Code, data, dependencies, migrations, or interfaces change | Which established patterns apply? What contracts, dependencies, compatibility, or maintainability risks exist? | Repository guidance, interfaces, dependency graph, migration plan |
| Security and privacy | Trust boundaries, data, authentication, secrets, paths, subprocesses, dependencies, or external effects are touched | What can be controlled by an attacker or untrusted source? What data should not be collected, logged, committed, or shared? | Threat review, scanner output, data flow, permission and redaction checks |
| Reliability and operations | Scheduled, background, stateful, networked, or recoverable behavior changes | How does it fail, retry, recover, remain observable, and avoid duplicate work? | Idempotency, timeout, heartbeat, rollback, monitoring, failure tests |
| Delivery and rollback | Work will be dispatched, released, migrated, or handed to review | Can the change be delivered incrementally? What makes the final evidence stale? How is it reversed or safely stopped? | Delivery slices, branch and PR evidence, rollback steps, source fingerprint |
| Adaptability | Requirements, feedback, or decisions have changed repeatedly | Which boundary should remain configurable or modular? What is the smallest flexibility justified by evidence? | Occurrence patterns, revision history, dependency boundary |

## Skill selection

- Capture: evidence and confidence, privacy, and stakeholder lenses.
- Triage: evidence and confidence, product behavior, actionability, and adaptability.
- Memory: evidence and confidence, freshness, and contradiction handling.
- Roadmap: business outcome, sequencing, dependencies, and health.
- Plan: business, user, product, engineering, security, reliability, delivery, and adaptability as triggered.
- Dispatch: authorization, readiness, reversibility, runtime, and operational capacity.
- Execute: product, engineering, security, reliability, scope alignment, and delivery.
- Test: product risk, regression, security, data integrity, compatibility, accessibility, and operations.
- Merge: evidence currency, branch and base integrity, release risk, rollback, and human disposition.
- Report: decision value, evidence confidence, exception salience, privacy, and next action.
- Share: recipient need, minimization, provenance, privacy, and non-authorization.

## Use rules

1. Start with evidence and confidence.
2. Select additional lenses from the actual change, not from a desire to make the output appear comprehensive.
3. Ask a lens question only when its answer can change scope, acceptance, risk, sequencing, validation, or handoff.
4. Preserve favorable evidence and existing successful behavior alongside failures and requests.
5. Treat recurring changes as evidence for bounded adaptability, not as a personality judgment or permission to generalize prematurely.
6. Convert unresolved material questions into explicit decisions with owners. Do not bury them in assumptions.
