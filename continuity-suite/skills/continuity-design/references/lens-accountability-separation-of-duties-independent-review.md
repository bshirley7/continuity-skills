# Accountability, separation of duties, and independent review

## Generalized principles

- Begin with the control objective and map incompatible duties across request, create, modify, review, approve, execute, reconcile, administer, and audit: assign roles and system permissions so one actor cannot both cause and conceal a material error, abuse, or unauthorized change; document exceptions and compensating controls when staffing makes full separation impractical.
- Make authority narrower than identity: after authenticating the actor, verify role, competence, subject, object, scope, value, environment, time, conditions, and delegability for the specific decision or action; use least privilege, deny by default, recheck at every consequential transition, and fail safely when authority is absent, stale, conflicted, or ambiguous.
- Design independent review as substantive challenge rather than ceremonial distance: give the reviewer sufficient organizational independence, competence, time, exact evidence, criteria, conflict disclosure, recusal, correction, dissent, and protection from retaliation; scale independence and dual control to consequence, irreversibility, uncertainty, and power imbalance.
- Bind authorization to what was actually reviewed: present all significant object, scope, consequence, version, and transaction data; require an outcome-specific act with clear meaning; invalidate authorization after any material change; limit validity by time and state; and verify the same approved object and conditions again before execution.
- Preserve a protected accountability record sufficient to reconstruct and test the decision: capture actor and role, authority basis, exact object and version, event and outcome, evidence and criteria considered, reason, conditions, time, location or system context, delegation or recusal, subsequent execution, exceptions, and corrections while minimizing unrelated personal data and preventing alteration from obscuring prior records.

## Method

- Define the control objective, material harms, protected assets, consequential transitions, required evidence, and tolerated residual risk.
- Map request, creation, modification, custody, review, approval, execution, reconciliation, administration, and audit duties; identify incompatible combinations across systems, not only within one screen.
- Specify authority by actor, role, competence, subject, object, scope, value, environment, time, conditions, delegation, conflict, recusal, and emergency exception.
- Bind review to the exact object and version, significant data, criteria, evidence, decision semantics, validity period, and pre-execution recheck.
- Design immutable-enough decision and execution records, access controls, retention, privacy limits, exception review, reconciliation, and tamper or bypass detection.
- Test self-approval, shared accounts, stale authority, material edits, reviewer shopping, unauthorized delegation, coerced review, rubber stamps, bypasses, expired decisions, partial execution, and hidden conflicts.

## Ethical safeguards

- Do not present ceremonial reviewer counts, passive views, reactions, silence, or automated confidence as independent approval.
- Do not allow requester-selected reviewer shopping, undisclosed conflicts, self-approval, unbounded delegation, or retaliation against recusal, dissent, rejection, or escalation.
- Do not make a reviewer accountable for material facts, system changes, or downstream actions that were hidden, altered, or outside the review boundary.
- Do not use audit evidence as unrestricted worker surveillance; collect and retain only what is necessary for the control, investigation, rights, and accountability purpose.
- Do not leave consequential requests indefinitely pending without status, reason, escalation, reassignment, withdrawal, or expiry.
- Do not let automated routing or recommendation obscure who holds authority, what evidence was considered, which conflicts apply, or who remains accountable.

## Variation levers

- Use role separation and periodic reconciliation for routine reversible activity; add dual control, independent review, stronger attestation, shorter validity, and execution interlocks as consequence rises.
- When small teams cannot fully segregate duties, use transparent exceptions plus compensating controls such as independent after-the-fact review, reconciliation, alerts, sampling, rotation, and owner-visible audit.
- Use attribute and relationship checks when authority depends on object, tenant, geography, value, project, reporting line, or conflict rather than role alone.
- Use privacy-minimized audit summaries for ordinary visibility and protected detail access for authorized investigation.

## Tensions and tradeoffs

- Stronger separation reduces fraud and concealed error while increasing delay, staffing cost, and handoff complexity.
- Independent reviewers improve challenge while losing local context or becoming detached from operational consequence.
- Exact-object binding protects integrity while requiring resubmission after legitimate late changes.
- Rich audit evidence improves reconstruction while increasing privacy, security, and retention burden.
- Strict least privilege limits abuse while brittle authority models block urgent legitimate work.

## Failure modes

- The same actor can request, approve, execute, and reconcile a consequential action without a visible exception.
- Authentication is mistaken for authority to approve the specific object, scope, value, or environment.
- Review independence is nominal while conflicts, competence, evidence, coercion, or retaliation remain unaddressed.
- Authorization remains valid after material data, version, scope, conditions, authority, or time changes.
- The record proves that a button was pressed but not what was reviewed, why, under which authority, or what happened afterward.
- Delegation erases the original assignment, authority boundary, reason, actor, or time.
- Control success is measured by approval speed or completion count rather than prevented, detected, corrected, and recurrent failures.

## Anti-patterns

- Maker approves maker.
- Login equals authority.
- Independent in name only.
- Approval follows edits.
- Button press as evidence.
- Delegation erases custody.
- Audit as surveillance.
- Fast approval is success.

## Acceptance and review questions

- Are the control objective, material harms, protected assets, consequential transitions, evidence, and residual risk explicit?
- Are incompatible request, create, modify, review, approve, execute, reconcile, administer, and audit duties separated or transparently compensated?
- Is authority specific to actor, role, competence, object, scope, value, environment, time, conditions, delegation, conflict, and recusal?
- Does independent review provide real distance, competence, evidence access, criteria, challenge, correction, dissent, and protection from retaliation?
- Is authorization bound to exact significant data, version, state, decision meaning, validity, and a fresh pre-execution check?
- Can the protected record reconstruct actor, authority, object, evidence, criteria, reason, conditions, time, delegation, recusal, execution, exception, and correction without unnecessary surveillance?
