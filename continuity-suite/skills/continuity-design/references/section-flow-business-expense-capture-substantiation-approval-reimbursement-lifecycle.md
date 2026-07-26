# Business expense capture, substantiation, approval, and reimbursement lifecycle

## Generalized principles

- Preserve one versioned expense identity while separating the source transaction from the claim: identify payer and beneficiary, employee or contractor, merchant, date and place, original amount and currency, payment method and transaction reference, business purpose, category, tax, project and cost owner, attendees where necessary, receipt and other evidence, policy revision, report, reviewers, reimbursement and accounting state; bind corrections and decisions to it; and never let a card swipe, receipt image, report row or reimbursement label become the expense by itself.
- Offer policy guidance at the moment of spending and claiming: explain eligible purpose, category, amount and receipt thresholds, preferred methods, limits, exceptions, approvers, tax or payroll effects, effective dates and jurisdiction in plain language; preview consequences before commitment; preserve the policy version applied; and never make a colored icon, score or after-the-fact rejection the first usable explanation.
- Make substantiation proportional and complementary: reuse trustworthy transaction data, require only evidence needed for amount, time, place, purpose and relationship, distinguish receipt presence from sufficient proof, support per diem and mileage rules, missing-receipt explanation and alternative evidence, protect confidential details, and never force duplicate entry or treat image upload and automated extraction as verification.
- Keep submitter, spender, beneficiary and claimant roles explicit: show when someone creates or edits an expense on another person's behalf, preserve source and authority, require the affected person to inspect or attest where appropriate, prevent self-approval and hidden reassignment, and never infer consent, business purpose or repayment responsibility from administrative access.
- Represent calculations as inspectable derivations: for split expenses, tax, tips, currency conversion, mileage and per diem, show source amount, unit, route or eligible period, rate and version, rounding, included and excluded components, reporting currency, allocation and resulting claim; preserve manual correction and reason; and never let a generated total, map route or converted amount conceal its basis.
- Separate automated policy checks from accountable adjudication: expose the exact rule, evidence, threshold, severity, confidence, affected amount and remedy; distinguish warning, missing information, exception request, auto-approval, human approval, rejection and suspected duplicate; let people explain and challenge; preserve overrides and reviewer independence; and never label an employee noncompliant or fraudulent from a model, category guess or threshold alone.
- Make review line-specific, reasoned and recoverable: let reviewers inspect the source transaction, evidence, business purpose, policy and allocation; approve, reject, return or partially accept exact lines with reasons and required correction; reveal authority and conflicts; invalidate affected approval after material edits; preserve conversation and prior decisions; and never turn report-level approval into unexplained acceptance of every line.
- Keep submitted, approved, payable, scheduled, sent, deposited, failed, returned, offset and marked-reimbursed states distinct: identify payment method, funding source, amount and currency, rate and fee, expected and actual dates, payment reference and exception owner; notify the claimant of changed evidence; reconcile accounting separately; and never let approval, payroll inclusion or an administrator's manual mark prove that the worker received funds.
- Support accessible, privacy-bounded capture and correction: provide keyboard, file, text and manual alternatives to camera, map and drag interactions; label receipt and policy states programmatically; preserve drafts and offline-safe uploads; minimize attendee, calendar, location and receipt data; show who can access it; support redaction and confidential evidence; and never require surveillance-grade context to prove ordinary business purpose.
- Measure reimbursement fairness and operational burden, not only policy compliance and spend: track employee-funded amount and age, completion time, returned and rejected reasons, missing-receipt alternatives, approval and payment latency, correction loops, accessibility failures, exception consistency and burden by worker and expense context; protect individuals from surveillance and retaliation; and never optimize savings by shifting cash-flow, documentation or error costs onto workers.

## Variation levers

- Increase transaction matching, cardholder controls and merchant evidence for company-card expenses.
- Increase cash-flow protection, payout visibility and missing-receipt alternatives for employee-paid expenses.
- Increase route, rate, vehicle, passenger and privacy controls for mileage claims.
- Increase eligible period, meals provided, location rate and partial-day logic for per diem.
- Increase funding, grant, contract, tax and independent-review evidence for public or restricted funds.

## Tensions and tradeoffs

- Fast capture versus sufficient and accurate substantiation.
- Automated policy enforcement versus contextual fairness and appeal.
- Fraud prevention versus worker dignity and presumption of good faith.
- Detailed evidence versus privacy and confidential business relationships.
- Central controls versus local rates, jurisdictions and accessibility needs.
- Finance efficiency versus employee cash flow and administrative burden.

## Failure modes

- A card transaction or receipt is mistaken for a complete expense claim.
- Policy is explained only after rejection.
- Workers re-enter data already present in trusted sources.
- An administrator silently submits or changes another person's claim.
- Mileage, per diem or currency totals hide rates and assumptions.
- An automated flag becomes an allegation or final decision.
- Report approval conceals rejected or unsupported line items.
- Approved or marked reimbursed is presented as money received.

## Anti-patterns

- Swipe as expense.
- Surprise policy.
- Receipt theater.
- Invisible proxy claimant.
- Magic reimbursement math.
- Flag as verdict.
- Blanket report approval.
- Approved means paid.

## Acceptance and review questions

- Can one expense be traced without confusing transaction, receipt, claim, report, approval, reimbursement or accounting entry?
- Is the exact applicable policy explained before spend and submission, including thresholds, exceptions and consequences?
- Does substantiation reuse source data, accept proportional alternatives and distinguish receipt presence from sufficient proof?
- Are submitter, spender, beneficiary and claimant roles and authority visible?
- Can people reconstruct tax, split, currency, mileage and per diem calculations from source and rate versions?
- Are automated flags explainable, challengeable and separate from human adjudication?
- Can reviewers decide exact lines with reasons, correction paths, conflict controls and preserved history?
- Are approval and every payment state distinguished through actual transfer evidence?
- Can capture and correction work without camera, map, color or pointer-only interaction and without excess personal data?
- Do metrics expose employee cash-flow, delay, correction loops, accessibility, consistency and administrative burden?
