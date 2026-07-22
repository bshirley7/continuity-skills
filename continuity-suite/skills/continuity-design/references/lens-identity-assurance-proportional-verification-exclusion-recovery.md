# Identity assurance, proportional verification, and exclusion recovery

## Generalized principles

- Evaluate necessity at the claim level before evaluating interface friction: define the relying party, capability, threat, consequence and exact attribute or binding that must be established; choose an assurance level proportional to harm; justify why self-assertion, an existing account, a signed attribute, selective disclosure or a lower-intrusion control is insufficient; separate identity proofing from suitability and entitlement; and reject data collection whose only rationale is future convenience, profiling or generalized trust.
- Trace assurance as an evidence argument: identify each self-asserted attribute, credential and issuing source; record evidence strength, authenticity validation, attribute-source comparison, consistency resolution, person-binding method, liveness or presence evidence, reviewer and date; state what the resulting confidence does and does not support; and prevent a platform badge, model score or successful capture from being promoted into universal identity, character or safety assurance.
- Require proportional, legible disclosure: tell people which attributes and artifacts are mandatory, the purpose and consequence of each, who verifies and receives them, whether a processor or source is involved, what derived biometric or risk data is created, how long samples, templates and records persist, and which later uses are prohibited; prefer attribute confirmation and selective disclosure over full document transfer; and provide a durable sharing history and rights route.
- Design multiple proofing pathways for the actual population: inventory document, issuer, country, language, name, gender marker, address, age, disability, device, connectivity, camera, mobility, literacy and assistance constraints; offer remote, assisted, in-person, digital-credential and alternative-evidence routes where risk allows; make equivalent assurance explicit; and measure whether a nominally neutral requirement excludes displaced, undocumented, transgender, rural, low-income, older, younger or disabled people.
- Treat biometric output as a probabilistic comparison with consequence-scaled safeguards: document reference and probe, one-to-one or one-to-many use, image-quality controls, threshold, false acceptance and rejection behavior, demographic and environmental performance, liveness method and human intervention; never describe a threshold result as fact; preserve non-biometric recovery where feasible; and do not deny consequential access solely because an automated comparison is inconclusive.
- Make correction and exclusion recovery specific to the failed layer: repair capture quality without restarting, correct self-asserted or mislabelled attributes, resolve source conflict, accept another credential, change device or channel, escalate inaccessible authentication, and route adverse or inconclusive assurance to trained human review and grievance; distinguish unsupported evidence, insufficient confidence, suspected fraud and actual ineligibility; preserve submitted evidence and deadlines; and avoid language that stigmatizes a legitimate mismatch.
- Govern identity and credential lifecycle beyond initial success: bind verified attributes to issuer, holder, relying party, scope, method, time and policy version; define expiry, refresh, suspension, revocation, supersession and recovery; notify material changes; support correction at the authoritative source and downstream propagation; minimize re-proofing and repeated collection; separate deletion of unnecessary samples from retention of proportionate audit evidence; and prevent purpose expansion across services.
- Audit assurance as an access and rights system, not only fraud loss or completion rate: measure step abandonment, capture retries, unsupported evidence, source mismatches, manual-review rates, time blocked, false acceptance, false rejection, overturn, grievance, re-verification burden, data retained and unauthorized reuse; segment by credential, device, channel, geography, language, disability, age, race, sex and gender identity where lawful and safe; and require accountable remediation when one group bears systematically higher exclusion or surveillance.

## Method

- Name the exact claim, relying party, capability, threat and consequence.
- Map every assertion, credential, validation source, person-binding method, derived signal and authorization decision.
- Compare the selected assurance path with less intrusive and alternative pathways.
- Walk successful, poor-quality, unsupported, mismatched, inconclusive, suspected-fraud, ineligible and expired cases.
- Review biometric thresholds, image conditions, demographic performance and human-review safeguards.
- Test the complete process with assistive technology, interrupted sessions, weak connectivity and authorized assistance.
- Trace samples, templates, attributes, decisions, sharing, correction, expiry, revocation and deletion across providers.
- Audit exclusion, delay, retry, overturn, privacy and burden outcomes alongside fraud outcomes.

## Ethical safeguards

- Do not collect full identity when a bounded attribute or lower-assurance claim is sufficient.
- Do not conflate proofing, account authorization, eligibility, character and safety.
- Do not hide biometric templates, derived signals, third parties or retention behind a camera prompt.
- Do not require one document, device, biometric or channel when an equivalent inclusive path is feasible.
- Do not present a biometric threshold result as a factual identity verdict.
- Do not restart the entire process for a repairable quality or data error.
- Do not silently reuse verification evidence for profiling or unrelated services.
- Do not optimize completion and fraud metrics while ignoring false rejection and unequal exclusion.

## Variation levers

- Raise assurance and independent review with financial, employment, housing, health, safety or public-benefit consequence.
- Lower disclosure when a signed attribute or age-over-threshold proof satisfies the use case.
- Increase alternative sources and assisted pathways when credential coverage is uneven.
- Increase biometric testing and human safeguards as automated comparison influences access.
- Reduce persistence and cross-service reuse for transaction-specific verification.

## Tensions and tradeoffs

- Higher assurance reduces some impersonation risks while increasing exclusion and surveillance.
- Selective disclosure protects privacy while limiting downstream fraud analysis and reuse.
- Persistent credentials reduce repeated burden while increasing linkability and stale confidence.
- Diagnostic failure messages aid recovery while detailed controls can reveal attack boundaries.
- Human review repairs automation error while adding delay, discretion and sensitive-data access.
- Broad badges simplify trust cues while overstating the narrow claim actually verified.

## Failure modes

- The service cannot state which identity claim is necessary for the requested capability.
- A successful capture is treated as proof of authenticity and person binding.
- A full credential is collected to prove only an age threshold.
- One document and camera path excludes legitimate users.
- A biometric non-match causes automatic permanent denial.
- A name or gender-marker mismatch is framed as deception.
- Re-verification repeats all evidence without risk justification.
- Completion rises while false rejection, review delay and subgroup exclusion remain unmeasured.

## Anti-patterns

- Assurance-by-friction.
- Capture-equals-proof.
- Full-document default.
- Single-path identity gate.
- Non-match finality.
- Mismatch criminalization.
- Perpetual re-proofing.
- Fraud-only verification scorecard.

## Acceptance and review questions

- Is identity proof necessary for an exact claim and consequence, at a proportionate assurance level, after less intrusive options are considered?
- Can the team reconstruct the evidence, source, validation, binding, reviewer, time and limits behind every assurance claim?
- Are mandatory attributes, processors, derived data, retention, prohibited uses, selective disclosure and rights clear before collection?
- Do equivalent pathways cover real document, identity, disability, device, connectivity and assistance constraints?
- Are biometric thresholds, uncertainty, demographic performance and consequential safeguards explicit and tested?
- Does each failure layer have a specific, non-stigmatizing correction, alternative or review path without evidence loss?
- Are expiry, refresh, revocation, correction, propagation, sample deletion and purpose boundaries governed across the lifecycle?
- Are false rejection, exclusion, delay, retries, overturn, retention and subgroup burden audited with fraud outcomes?
