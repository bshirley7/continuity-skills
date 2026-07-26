# Security operations

## Generalized principles

- Separate source severity, operational priority, confidence, exposure, business consequence, lifecycle state, and response urgency; show the evidence and rubric behind each rather than relying on color or one composite risk score.
- Keep investigation scope explicit across organization, environment, identity, account, credential, device, session, asset, service, dependency, data, location, and time window; show inclusion, exclusion, ownership, sensitivity, and known downstream exposure.
- Preserve evidence as traceable observations with source, provenance, observed and ingestion time, freshness, confidence basis, correlation method, and integrity; distinguish automated detection, analyst interpretation, hypothesis, decision, action, result, and correction.
- Make operational ownership and investigation state explicit: commander or lead, assignee, collaborators, current phase, next checkpoint, pending evidence, blockers, handoff, escalation, communication state, and decision authority.
- Preview containment and recovery actions with target, scope, blast radius, access or service disrupted, dependencies, evidence preserved, authorization, propagation, partial-failure behavior, verification, rollback, and residual risk.
- Maintain an immutable, queryable operational record connecting actor and authority, evidence, hypothesis, decision, action, target, before and after state, time, source, outcome, communication, recovery, and later correction; bind resolution to verification rather than status alone.

## Variation levers

- Use dense queues for trained operators while keeping state definitions, keyboard paths, and detail inspection immediately available.
- Use progressive disclosure for raw evidence, but never hide severity rationale, affected scope, ownership, or containment state.
- Use graph, timeline, table, or geographic views according to whether relationships, sequence, comparison, or location is the primary question.
- Require stronger authorization, dual control, or staged execution as blast radius, privilege, irreversibility, or regulated consequence increases.
- Support automation recommendations while requiring explicit authority, preview, evidence preservation, and human-verifiable outcomes for consequential response.

## Tensions and tradeoffs

- Dense information accelerates expert response while increasing cognitive load and missed context.
- Automated correlation reduces investigation time while creating false confidence and opaque causality.
- Aggressive containment reduces exposure while disrupting legitimate access, evidence, or service.
- Central incident command improves coordination while creating bottlenecks and unclear local authority.
- Broad audit retention improves reconstruction while increasing sensitive-data exposure and access obligations.
- One severity model improves triage consistency while flattening asset, identity, and business-specific consequence.

## Failure modes

- Severity, confidence, priority, and status are conflated.
- Color is the only encoding of operational consequence.
- An alert has no evidence provenance or freshness.
- Asset scope omits dependencies or downstream exposure.
- A hypothesis is presented as confirmed evidence.
- Containment does not state blast radius or evidence impact.
- Ownership and next checkpoint are absent.
- Partial response failure leaves target state ambiguous.
- Resolution is recorded without verification.
- Audit export loses query context or chain of custody.

## Anti-patterns

- Critical because red.
- One risk score explains everything.
- Affected systems unknown without a search path.
- Automated correlation equals causation.
- Contain now, explain later.
- Resolved means closed.
- Everyone owns the incident.
- Timeline as an undifferentiated activity feed.
- Audit log without before state.
- Security theater confirmation.

## Acceptance and review questions

- Are severity, priority, confidence, exposure, consequence, state, and urgency distinct and evidence-backed?
- Is investigation scope explicit across identities, assets, dependencies, data, locations, environments, and time?
- Does every observation retain provenance, timing, freshness, confidence basis, correlation, and integrity while remaining distinct from interpretation?
- Are ownership, authority, phase, checkpoint, blockers, handoffs, escalation, and communication state visible?
- Do containment and recovery previews name target, blast radius, disruption, dependencies, evidence, authorization, propagation, failure, verification, rollback, and residual risk?
- Does the operational record connect evidence, decisions, actions, outcomes, communications, recovery, and corrections immutably?
- Is resolution supported by explicit verification evidence?
