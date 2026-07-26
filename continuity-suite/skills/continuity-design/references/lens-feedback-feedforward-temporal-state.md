# Feedback, feedforward, and temporal state

## Generalized principles

- Provide feedforward before commitment: state the action, target, scope, material consequence, reversibility, required inputs, expected duration or uncertainty, and what will count as success; make unavailable actions and prerequisites legible, and scale review or confirmation to consequence rather than asking for ritual confirmation everywhere.
- Close the causal loop after every meaningful action with feedback that identifies the triggering action, affected object, accepted or rejected input, current lifecycle state, time, and next available move; distinguish local acknowledgment, server acceptance, processing, verification, publication, and downstream completion instead of collapsing them into a generic success signal.
- Represent temporal state as evidence: expose when a state began, when it was last observed or updated, whose system owns it, whether it is live, cached, estimated, partial, stale, paused, retried, or terminal, and what can change next; never use motion, optimistic display, or elapsed time as proof of completion.
- Match feedback delivery to urgency and actionability: keep routine status near the affected object, announce nonvisual equivalents without stealing focus, reserve interruption for immediate consequential decisions, persist information until it can be perceived and acted on, and prevent repeated or competing announcements from obscuring the task.
- Make errors specific, attributable, and recoverable: identify what failed, preserve valid work, separate user input from system or dependency failure, explain the applicable rule in plain language, offer a feasible correction or alternative, and show whether retry is safe, idempotent, delayed, or likely to duplicate effects.
- Choose feedback timing from the task, consequence, and learning goal rather than assuming immediate is always superior: acknowledge actions immediately when causality or safety requires it, provide corrective content while it remains attributable, and test immediate, delayed, cumulative, and user-requested feedback because durable learning and metacognitive accuracy vary by task and population.
- Test the whole state transition, not just the visual message: verify control availability, focus and announcement behavior, persisted data, duplicate-action protection, cancellation, undo, retry, timeout, offline return, late response, out-of-order response, partial success, stale views, and handoff to another actor or system.

## Method

- Model each consequential action as states and transitions with initiator, target, authority, timestamps, uncertainty, reversibility, and terminal evidence.
- For every control, specify feedforward, immediate acknowledgment, intermediate status, success evidence, failure evidence, and recovery.
- Inventory channels, focus behavior, persistence, announcement priority, repeated updates, cross-device state, and notification escalation.
- Prototype slow, failed, partial, stale, offline, canceled, retried, duplicated, late, and out-of-order paths as first-class states.
- Test action prediction, causal attribution, state comprehension, error recovery, assistive-technology exposure, and delayed return.
- Measure duplicate actions, silent failures, false success, recovery time, interruption burden, abandoned work, and subgroup differences.

## Ethical safeguards

- Do not claim success before the authoritative completion evidence exists.
- Do not use optimistic state where reversal could cause financial, legal, safety, privacy, publication, or data-loss consequences.
- Do not blame the person for system, policy, model, network, dependency, or ambiguous validation failures.
- Do not hide uncertainty, staleness, partial success, retries, or downstream work behind reassuring motion or celebratory copy.
- Do not use alerts, haptics, sound, urgency, or repeated announcements to manufacture importance or pressure.
- Do not erase valid input after failure or make retry likely to duplicate a consequential action.

## Variation levers

- Use inline passive state for routine reversible work and interruptive review for imminent consequential commitment.
- Use determinate progress only with a meaningful denominator; otherwise show activity, phase, uncertainty, and a safe way to leave.
- Increase provenance, timestamps, and lifecycle detail with asynchronous duration, cross-system ownership, and consequence.
- Use immediate acknowledgment for causality and safety; vary corrective or learning feedback timing based on evidence and testing.
- Offer compact status by default with expandable diagnostics, history, and recovery detail for expert or failed states.
- Increase persistence and redundant modalities when information is critical, transient, or easy to miss.

## Tensions and tradeoffs

- Immediate acknowledgment supports causality while premature success creates false certainty.
- Detailed lifecycle state supports trust while overwhelming routine workflows.
- Persistent feedback aids access and recovery while increasing clutter.
- Interruptive alerts protect consequential decisions while habituation makes real warnings easier to ignore.
- Optimistic interaction feels responsive while reconciliation can violate expectations or duplicate effects.
- Delayed corrective feedback may aid some learning while weakening action attribution or safety.

## Failure modes

- A button shows success when the request was merely queued.
- A spinner continues with no phase, freshness, failure, or exit information.
- A status change is visible but never announced through assistive technology.
- An alert interrupts for routine confirmation while a destructive background failure is silent.
- An error says the input is invalid without identifying the field, rule, preserved data, or correction.
- Retry sends a second payment, publication, invitation, or destructive command.
- A late response overwrites newer state and appears current.

## Anti-patterns

- Queued means done.
- Spinner as evidence.
- Success without authority.
- Alert everything.
- Invalid with no remedy.
- Retry and hope.
- Late state wins.
- Color-only status.

## Acceptance and review questions

- Before commitment, can a person predict the target, scope, consequence, reversibility, duration, prerequisites, and success evidence?
- After action, does feedback distinguish acknowledgment, acceptance, processing, verification, publication, and downstream completion?
- Does every asynchronous state expose provenance, freshness, uncertainty, partiality, ownership, and possible next transitions?
- Is delivery matched to urgency without focus theft, inaccessible status, premature disappearance, or announcement overload?
- Do errors preserve work, attribute the failure correctly, explain the rule, and offer safe correction, alternative, undo, or retry?
- Was feedback timing chosen and tested for causality, safety, learning, delayed judgment, and population differences?
- Have slow, stale, offline, duplicate, late, canceled, partial, out-of-order, and cross-actor transitions been tested end to end?
