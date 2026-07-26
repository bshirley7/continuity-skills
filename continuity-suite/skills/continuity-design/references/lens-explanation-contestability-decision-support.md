# Explanation, contestability, and decision support

## Generalized principles

- Define the explanation contract before choosing a visualization or rationale: identify recipient and affected person, decision or output, intended use, consequence, timing, prior knowledge, language and accessibility needs, likely questions, decision authority, privacy and security constraints, explanation purpose, evidence needed for challenge, and route to correction, human review, appeal and remedy; provide different views for operators, decision owners, affected people, auditors and developers without changing the underlying facts.
- Require every explanation to satisfy evidence, meaningfulness, fidelity and knowledge-limit tests: attach reasons or evidence to the exact output; make them understandable and actionable for the recipient; verify that they reflect the process or evidence actually used rather than a plausible generated story; disclose conditions, uncertainty and limits under which the system should abstain, defer or require verification.
- Layer case-specific explanation around consequence and contestability: state what happened and what it means, decisive factors and applicable criteria, data and sources used, material omitted or missing inputs, comparison and counterfactual where valid, uncertainty and relevant performance, fairness and group-impact safeguards, accountable roles, and concrete steps to correct data, add evidence, challenge use, request qualified human review, appeal and obtain remedy.
- Treat explanation as decision support, not persuasion or proof: separate system output, source evidence, statistical confidence, explanation, recommendation, human judgment and final action; present alternatives, no-action baseline, disagreement and known failure cases; do not use visual polish, conversational fluency, source count, feature importance or an explanation label to manufacture trust, and test whether explanations improve correct acceptance and correct rejection rather than agreement alone.
- Close the contestability loop with durable correction evidence: preserve exact output, model or rule and data versions, recipient-facing explanation, source and factor record, reviewer and authority, challenge and supporting evidence, independent reassessment, changed or upheld decision with reasons, downstream correction, notification, remedy and recurrence prevention; measure access, comprehension, successful correction, reversals, response time, burden, retaliation risk and group differences.

## Method

- Identify recipients, affected people, consequence, timing, authority, accessibility, likely questions, privacy constraints, explanation purpose and contest route.
- Separate output, evidence, confidence, rationale, criteria, recommendation, human judgment and final action before selecting presentation.
- Test evidence attachment, recipient meaningfulness, process fidelity, knowledge limits, uncertainty, abstention and verification requirements.
- Build layered outcome, rationale, data, fairness, safety-performance, impact and responsibility explanations around case-specific facts.
- Provide correction, additional evidence, disagreement, human review, appeal, remedy and status tracking with bounded disclosure.
- Evaluate comprehension, correct acceptance and rejection, correction success, reversals, burden, delayed outcomes and group differences.

## Ethical safeguards

- Do not generate a plausible rationale and present it as a faithful account of model, rule, retrieval or human decision process.
- Do not use explanation detail, confidence styling, citations or institutional language to pressure agreement or imply certainty.
- Do not expose sensitive personal data, protected attributes, trade secrets, security controls or other people's records beyond what understanding and challenge require.
- Do not offer a human-review route if the reviewer merely repeats the same automated output, lacks authority, or cannot consider new evidence.
- Do not place the burden of discovering invisible errors, missing data or system limitations entirely on the affected person.
- Do not optimize explanation success through satisfaction, trust, agreement or reduced appeals while excluding comprehension, correct rejection, correction and remedy.
- Do not let explanation substitute for lawful basis, fairness, accuracy, validation, oversight, accountability or prevention of harm.
- Do not retaliate, degrade service, increase friction or train adverse inferences from a person's challenge, refusal or appeal.

## Variation levers

- Use concise outcome and action explanations for routine reversible assistance and richer case, process and governance evidence for consequential or disputed decisions.
- Use example, counterfactual, factor, rule, source or uncertainty explanations only when they faithfully match the system and recipient's question.
- Increase independent review, disclosure, correction support, appeal, remedy and audit evidence with consequence, opacity and power imbalance.
- Use progressive disclosure to protect comprehension and privacy while keeping the route to full relevant evidence visible.

## Tensions and tradeoffs

- More detail can improve transparency while reducing comprehension and increasing false confidence.
- Case-specific disclosure supports challenge while risking privacy, security, gaming or exposure of others.
- Simple explanations are usable while omitting interactions, uncertainty or limitations that change the conclusion.
- Counterfactual guidance can support correction while implying that changing one factor guarantees an outcome.
- Fast human review reduces delay while becoming a rubber stamp when evidence, independence or authority are weak.

## Failure modes

- The same generic explanation is shown to every recipient regardless of question, consequence, authority or accessibility.
- The rationale is fluent but not demonstrably connected to the process, evidence or factors that produced the output.
- Confidence or feature importance is displayed without calibration, reference class, uncertainty or actionable meaning.
- The interface shows why but not what data, criteria, consequence, limitation, accountable party or correction path applies.
- An affected person can read an explanation but cannot correct inputs, add evidence, challenge use, obtain qualified review, appeal or remedy.
- A reviewer sees the machine conclusion before independently considering material case evidence and becomes anchored to it.
- Explanation evaluation measures trust or agreement but not comprehension, correct rejection, correction, reversal, burden or group impact.
- A changed decision does not repair downstream records, notify affected parties or prevent recurrence.

## Anti-patterns

- One explanation for everyone.
- Plausible rationale.
- Confidence as meaning.
- Why without remedy.
- Human rubber stamp.
- Counterfactual promise.
- Trust means success.
- Appeal without correction.
- Explanation replaces accountability.

## Acceptance and review questions

- Is the explanation tailored to recipient, affected person, output, intended use, consequence, timing, accessibility, likely question, authority, privacy and contest route?
- Does it pass evidence, meaningfulness, fidelity and knowledge-limit tests for the exact case?
- Are output, evidence, confidence, explanation, recommendation, human judgment and final action distinct?
- Does the case explanation cover outcome, consequence, factors, criteria, data, missing inputs, uncertainty, performance, fairness, roles and limitations?
- Can people correct data, add evidence, challenge use, obtain qualified independent review, appeal, track status and receive effective remedy?
- Does evaluation measure comprehension, correct acceptance and rejection, correction, reversals, burden, delayed effects and group differences rather than trust or agreement alone?
