# Review and approval lifecycle

## Generalized principles

- Bind every request to an exact review object: show a stable request ID, requester, purpose, artifact or resource, version or hash, affected scope, material changes, requested decision, evidence and checks, policy or criteria, urgency, desired effective time, and expiry; any material edit creates a linked revision and invalidates prior approval rather than moving the approval to the latest version.
- Make the approval route an inspectable control rather than a list of names: distinguish reviewer, approver, advisor, observer, requester, and executor; expose required role and authority, order or parallelism, quorum, deadline, alternate or delegation, conflict and recusal state, escalation, and which decisions remain outstanding.
- Give reviewers one evidence-bound workspace containing the exact submitted version, material diff, unresolved comments, checks and evidence, applicable criteria, affected scope and consequence, prior decisions and conditions, requester responses, and distinct actions for approve, approve with permitted conditions, request changes, reject, recuse, or authorized delegation.
- Record a decision as durable evidence: preserve decision maker, role and authority, exact object and version, outcome, reasons, evidence considered, conditions, scope, effective and expiry time, dependencies, timestamp, and attestation; never promote a comment, reaction, view, silence, reviewer count, or generated summary into approval.
- Keep approval, release, execution, publication, payment, access grant, and completion as separate lifecycle states: recheck the exact approved version and live preconditions before acting, show partial or failed downstream effects, preserve withdrawal, expiry, revocation, supersession, and resubmission, and retain the complete linked history without rewriting earlier decisions.

## Variation levers

- Use a lightweight single-reviewer route for low-risk reversible work and add independent approvers, quorum, sequencing, expiry, and evidence controls as consequence, irreversibility, value, or regulation increases.
- Use inline review for one bounded artifact and a queue plus detail workspace when reviewers manage many heterogeneous requests.
- Permit conditional approval only when conditions are explicit, testable, owned, time-bounded, and enforced before downstream action.
- Allow delegation only within documented authority and preserve the original assignment, delegate, reason, scope, and time.

## Tensions and tradeoffs

- More reviewers may broaden perspective while diffusing responsibility and encouraging rubber-stamp behavior.
- Fast approval reduces delay while weakening evidence review, independence, and reason quality.
- Immutable review objects protect integrity while increasing revision and resubmission overhead.
- Detailed audit records support accountability while excessive personal or sensitive data expands privacy risk.
- Automated routing improves consistency while hiding authority assumptions, conflicts, and exceptional context.

## Failure modes

- Approval silently follows the latest version after material content changes.
- The requester, reviewer, approver, and executor can be the same person without a visible exception or compensating control.
- A reviewer decides without a material diff, policy criteria, evidence status, affected scope, or unresolved objections.
- Rejection or conditional approval records no reason, scope, owner, or correction route.
- A reaction, comment, view, reviewer count, or generated summary is treated as authorization.
- Approved immediately means published, deployed, paid, or granted without an exact-version and live-precondition check.
- Expired, revoked, withdrawn, or superseded approval remains actionable or disappears from history.

## Anti-patterns

- Approval follows latest.
- Reaction means approved.
- Self-approval by default.
- Review without diff.
- Reject without reason.
- Delegate without authority.
- Approved means executed.
- Expired approval still acts.

## Acceptance and review questions

- Is the request bound to an exact object, version, scope, change set, requested decision, evidence, criteria, urgency, effective time, and expiry?
- Are reviewer, approver, advisor, observer, requester, executor, authority, order, quorum, deadline, delegation, conflict, recusal, escalation, and outstanding state explicit?
- Can reviewers inspect the exact version, diff, evidence, checks, criteria, consequence, objections, prior decisions, and requester responses before choosing a semantically precise outcome?
- Does every decision preserve actor, authority, version, outcome, reasons, evidence, conditions, scope, timing, dependencies, and attestation?
- Are approval, execution, publication, payment, access grant, completion, withdrawal, expiry, revocation, supersession, and resubmission distinct and linked?
- Does any material change invalidate earlier approval and require review of the new exact version?
