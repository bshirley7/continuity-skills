# Health

## Generalized principles

- Anchor every health recommendation to the care need, evidence or guideline basis, due state, prior completion source, and a safe route to book, reconcile, defer, or ask for clinical help.
- Keep clinical measurements self-describing through name, value, unit, reference range, time, trend, source, and interpretation, separating educational context from individualized medical advice.
- Separate patient-reported behavior, observed symptoms, clinician-authored findings, automated interpretation, and completed-care claims so one evidence class cannot silently stand in for another.
- Make medication state operational by preserving medicine identity, dose, schedule, taken, late, missed, changed, stopped, and prescriber or support routes without reducing adherence to a single score.
- Before a clinical appointment or submission, show the exact patient, clinician or service, time, modality, preparation, consent, privacy consequence, cancellation condition, and recovery path.
- Treat consent as an inspectable agreement tied to the service, disclosure, signer, date, modality, data use, and withdrawal or support path rather than as an unexplained checkbox.
- Bind provider follow-up to the exact patient and encounter while keeping task, owner, urgency, due state, supporting evidence, completion, and audit history independently visible.
- Use calm hierarchy without muting risk: distinguish routine, due, overdue, abnormal, urgent, unavailable, and unverified states through text and structure rather than color or reassurance alone.

## Variation levers

- Use patient-facing plain language with expandable clinical detail and provider-facing density with explicit provenance.
- Use reference ranges for measurements, schedules for medication, timelines for care events, and queues for accountable follow-up.
- Use inline consent for bounded low-risk services and a dedicated review for diagnostic, treatment, recording, or data-sharing consequences.
- Use preventive recommendations when guideline and completion evidence are available and a reconciliation flow when records may be incomplete.
- Use calm confirmation for routine care and stronger interruption for urgent, abnormal, or unverified states.
- Use aggregated adherence summaries only when users can inspect the underlying dated events.

## Tensions and tradeoffs

- Simplified language improves comprehension while risking loss of clinical qualification.
- Preventive prompts support care continuity while becoming coercive when evidence or dismissal is weak.
- Dense clinical data supports expert review while overwhelming patients.
- Automated interpretation accelerates orientation while creating false authority.
- Persistent warnings preserve safety while contributing to alert fatigue.
- Shared patient-provider views improve continuity while requiring strict role and privacy boundaries.

## Failure modes

- A recommendation lacks clinical basis, due state, or record source.
- A result shows a status without value, unit, range, time, or provenance.
- Patient-entered and clinician-verified information are visually indistinguishable.
- Medication tracking collapses late, missed, changed, and stopped into one adherence score.
- Consent omits service scope, signer, data use, or withdrawal path.
- A diagnostic upload cannot be reviewed or retaken before submission.
- A clinical task lacks patient, accountable owner, urgency, due state, or evidence.
- Routine visual calm suppresses abnormal or urgent meaning.

## Anti-patterns

- Calling a care item complete without exposing its source.
- Using green or red as the only clinical interpretation.
- Presenting generalized education as personalized advice.
- Celebrating adherence while hiding missed-event detail.
- Collecting clinical consent through a generic checkbox.
- Submitting a diagnostic image without exact preview.
- Treating a clinical note generator as the final authority.
- Using a generic productivity queue for urgent patient follow-up.

## Acceptance and review questions

- Can each recommendation be traced to need, basis, due state, and record source?
- Do results preserve value, unit, range, time, trend, source, and interpretation?
- Are patient reports, observations, automation, and clinician findings distinct?
- Are medication identity, schedule, event state, and support routes complete?
- Are appointment, consent, privacy, preparation, and cancellation terms visible together?
- Can users inspect and correct diagnostic submissions before commitment?
- Do provider tasks expose patient, owner, urgency, due state, evidence, and history?
- Are routine, abnormal, urgent, unavailable, and unverified states structurally distinct?
