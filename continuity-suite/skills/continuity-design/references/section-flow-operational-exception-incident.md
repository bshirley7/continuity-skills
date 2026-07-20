# Operational exception and incident handling

## Generalized principles

- Turn a signal into a qualified operational object without overstating certainty: preserve detector or reporter, source and observed time, freshness, threshold or expected state, raw evidence, confidence, recurrence, affected object and environment, potential scope and consequence, related changes, and the distinction among notification, anomaly, exception, suspected incident, and confirmed incident.
- Create a shared situation view organized around what is known, inferred, unknown, changing, and next: show severity and priority rationale, affected and potentially affected scope, user or business impact, dependencies, current operating state, timeline, hypotheses with evidence, recent actions and outcomes, ownership, command roles, open questions, next checkpoint, and data freshness.
- Separate coordination from diagnosis while keeping them linked: define incident lead or decision authority, operations, communication, investigation, safety or compliance, and specialist roles; assign bounded tasks with owner, objective, due or checkpoint, dependencies, status, evidence, and handoff; preserve one canonical chronology across chat, alerts, tasks, changes, and stakeholder updates.
- Control mitigation by affected state and blast radius: before retry, override, rerun, pause, disable, rollback, compensate, isolate, or restore, expose target and scope, current and expected state, authority, evidence preserved, dependencies, external effects, duplication risk, partial-failure behavior, monitoring window, rollback or safe-stop route, and how success and unintended impact will be verified.
- Treat recovery and learning as evidence-bearing phases: distinguish contained, mitigated, restored, monitored, resolved, closed, and recurrent; require service or process health, affected-record reconciliation, user-impact review, residual risk, and observation-window evidence before closure, then preserve a blameless chronology, contributing conditions, detection and response gaps, decisions, communication, follow-up owners and due dates, and verification that improvements took effect.

## Variation levers

- Use a lightweight exception record for isolated reversible failures and activate formal command roles, communication cadence, and operational periods as scope, duration, uncertainty, or consequence grows.
- Increase independent authorization, evidence preservation, safe-stop controls, stakeholder communication, and recovery monitoring with safety, financial, legal, privacy, or broad service impact.
- Use queues and tables for repeated comparable exceptions, timelines for sequence, graphs for dependency and propagation, and dedicated workspaces for multi-source investigation.
- Automate bounded collection, correlation, routing, and reversible response while retaining visible confidence, authority, manual override, effect evidence, and escalation for ambiguous or consequential action.

## Tensions and tradeoffs

- Early declaration mobilizes response while increasing false-positive and alert-fatigue cost.
- Central command improves coordination while becoming a bottleneck or suppressing specialist dissent.
- Aggressive mitigation limits impact while disrupting healthy scope, destroying evidence, or creating secondary failures.
- A single common operating picture supports alignment while becoming stale, overconfident, or detached from raw evidence.
- Rapid closure reduces operational load while hiding recurrence, incomplete reconciliation, and unverified follow-up.

## Failure modes

- A threshold breach or user report is immediately labeled a confirmed cause or incident.
- Severity, priority, confidence, impact, urgency, and lifecycle state collapse into one color or score.
- The current view cannot distinguish observation, hypothesis, decision, action, result, and correction.
- Everyone is listed as a responder but command, authority, ownership, checkpoints, and handoffs are absent.
- A retry, rollback, override, isolation, or restoration action omits blast radius, external effects, duplicate risk, evidence impact, safe stop, and verification.
- Resolved means an alert cleared or an operator changed status, without health, reconciliation, residual-risk, or observation-window evidence.
- A post-incident document exists but follow-up actions lack owners, deadlines, verification, or linkage to the original evidence.

## Anti-patterns

- Alert equals incident.
- Red explains severity.
- Dashboard as truth.
- Everyone owns response.
- Mitigate without blast radius.
- Alert cleared equals recovered.
- Postmortem without follow-through.
- Recurrence becomes a new mystery.

## Acceptance and review questions

- Does the operational object preserve source, time, freshness, expected state, evidence, confidence, recurrence, scope, consequence, changes, and qualification state?
- Can responders distinguish known, inferred, unknown, changing, next, impact, dependency, timeline, hypothesis, action, owner, checkpoint, and freshness?
- Are command, operations, communication, investigation, specialist, task, handoff, and canonical chronology responsibilities explicit?
- Do consequential controls expose target, scope, authority, preserved evidence, dependencies, effects, duplicate risk, partial failure, monitoring, safe stop, rollback, and verification?
- Are containment, mitigation, restoration, monitoring, resolution, closure, and recurrence distinct and evidence-backed?
- Does learning preserve chronology, conditions, gaps, decisions, communication, actions, owners, dates, and verified improvement?
