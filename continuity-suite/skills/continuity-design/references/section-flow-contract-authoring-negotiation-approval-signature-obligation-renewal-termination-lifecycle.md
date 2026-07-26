# Contract authoring, negotiation, approval, signature, obligation, renewal, and termination lifecycle

## Generalized principles

- Preserve one versioned agreement identity across the lifecycle: identify parties and legal entities, agreement type and purpose, jurisdiction and language, owner, governing template and clauses, related transaction, effective and expiry conditions, current version and status; bind intake, authoring, negotiation, approval, signature, obligations, amendments, renewal, termination and records to it; and never let a filename, envelope, signer tile or visual signature become the agreement identity by itself.
- Make templates, clauses and variables inspectable inputs rather than invisible automation: show source, owner, jurisdiction, version, approved use, dependencies, required fields, fallback text and last review; preserve manual changes and field provenance; warn when upstream data is stale or incomplete; and never imply that a populated template is legally or operationally ready without review.
- Separate intake, authoring, internal review, counterparty negotiation, approval, signature preparation and execution: show actor, exact version, required evidence, open work, next action and blocked transition at each state; support draft preservation and return; and never turn document creation, comment resolution, approval, send or one signature into a later state automatically.
- Represent negotiation as a source-linked change process: preserve proposed and accepted text, author and party, timestamp, reason, comment thread, affected clauses and obligations, unresolved issues, counterproposal, version comparison and explicit resolution; protect confidential internal notes; and never flatten redlines into an untraceable latest document or treat silence as acceptance.
- Bind every approval to the exact agreement version and scope: identify reviewer, organizational role and authority, outcome, conditions, exceptions, evidence, clauses and commercial limits covered, timestamp and expiry; invalidate or reroute approval after material change; preserve abstention and escalation; and never infer authority from access, seniority, prior participation or a generic approved badge.
- Configure execution around party, signer and evidence requirements: distinguish legal party, contact, reviewer, approver, signer, witness, notary and copy recipient; show signing order, authority basis, authentication level, required fields, document and attachment versions, deadline and fallback; preview each recipient's experience; and never assume an email address, placed field or drawn mark proves identity, authority, intent or completion.
- Make signature status granular and evidentiary: distinguish prepared, sent, delivered, viewed, authenticated, partially signed, declined, expired, voided and completed; identify actor, time, reason, retry and correction; preserve certificate, audit trail and exact final package; give every party durable access; and never use sent, opened, signed-looking or one-party-complete as whole-agreement finality.
- Separate execution, effectiveness, performance and completion: show signatures still required, conditions precedent, effective date, service or delivery start, payment and reporting milestones, notice windows, responsible owner, evidence and dependencies; generate tasks from exact terms without replacing them; and never imply that a fully signed agreement is already effective, performed, paid or closed.
- Treat amendments, extensions and renewals as linked agreement events: identify change authority and basis, affected clauses and obligations, prior and new terms, commercial and operational consequences, effective date, approval and signature requirements, notice window and supersession; preserve the unchanged agreement and version chain; and never overwrite signed terms or use continued access as silent consent to a material change.
- Close agreements through explicit termination, survival and remedy: distinguish expiry, non-renewal, termination for convenience or cause, rescission, replacement and administrative closure; show notice, authority, effective date, cure, payment, return, data and access offboarding, surviving obligations, disputes, records and reopening; confirm closure durably; and never let account deletion, contract status or final payment erase continuing duties or evidence.

## Variation levers

- Increase identity, witness, notarization, jurisdiction and formal-execution controls where law or transaction consequence requires them.
- Increase clause provenance, redline comparison, privilege and approval controls for negotiated organizational agreements.
- Increase comprehension, language, accessibility, withdrawal and cooling-off safeguards for asymmetric or consumer agreements.
- Increase milestone, acceptance, payment, service-level and remedy controls for operational contracts.
- Increase notice, renewal, data return, access revocation and transition controls for subscriptions and technology services.

## Tensions and tradeoffs

- Fast templating versus exact terms and field provenance.
- Collaborative drafting versus privileged or party-confidential commentary.
- Negotiation flexibility versus stable version and approval lineage.
- Low-friction signing versus proportionate identity, authority and intent evidence.
- Automated obligation extraction versus fidelity to governing text.
- Easy renewal versus informed notice, choice and exit.

## Failure modes

- A populated template is presented as review-complete.
- Comments and redlines are detached from their exact version.
- Approval survives a material agreement change.
- A signer email or drawn mark is treated as authority proof.
- Sent, viewed or one-party-signed is shown as complete.
- Full signature is mistaken for effectiveness or performance.
- Renewal silently changes or extends material obligations.
- Closure erases surviving duties, remedies or evidence.

## Anti-patterns

- Template as legal verdict.
- Latest-file negotiation.
- Evergreen approval.
- Signature theater.
- Sent-means-agreed.
- Signed-means-done.
- Silent evergreen renewal.
- Closed means forgotten.

## Acceptance and review questions

- Can people identify the parties, purpose, jurisdiction, owner, governing sources, exact version, term and current agreement state?
- Are template, clause and variable provenance, completeness and manual changes inspectable?
- Are authoring, review, negotiation, approval, signature preparation and execution distinct?
- Can every redline, comment and resolution be traced to party, author, clause, version, time and reason?
- Is each approval bound to exact version, authority, scope, conditions and material-change handling?
- Are legal parties, contacts, reviewers, approvers, signers, witnesses and copy recipients represented separately?
- Do signature states expose delivery, viewing, authentication, partial completion, refusal, expiry and durable evidence?
- Are execution, effectiveness, obligations, performance, payment and closure distinct?
- Do amendments and renewals preserve prior terms, authority, notice, consent and version lineage?
- Does termination expose notice, cure, survival, remedy, offboarding and retained records?
