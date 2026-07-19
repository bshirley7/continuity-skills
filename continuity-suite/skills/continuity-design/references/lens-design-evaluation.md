# Design evaluation

## Generalized principles

- Define the evaluation contract before reviewing: artifact and revision, audience, task scenario, environment, constraints, success conditions, heuristic or requirement set, evidence sources, exclusions, and decision owner.
- Record each finding as observed behavior against an explicit criterion, anchored to the exact artifact location and state, with reproduction context, supporting evidence, affected audience, consequence, and a falsifiable resolution condition.
- Separate evidence types and measures: observed task behavior, participant explanation, expert heuristic judgment, automated check, accessibility inspection, analytics, and stakeholder preference answer different questions and should not be combined into one score.
- Assign severity from user impact, frequency, reach, task criticality, duration or persistence, workaround quality, accessibility or legal consequence, and evidence confidence; keep implementation effort and organizational priority as separate planning fields.
- Make comparisons valid by holding task, audience, device, content, data, instrumentation, and success definition constant or labeling every material difference; compare against a baseline and decision threshold rather than visual preference alone.
- Close the loop by recording disposition, owner, target revision, implemented change, retest method, verification evidence, residual risk, regressions checked, and final decision; approval binds only the exact reviewed revision.

## Variation levers

- Use a lightweight checklist for low-risk familiar patterns and a scenario-based protocol for novel, high-consequence, or cross-modal work.
- Use heuristic inspection early, representative task testing during iteration, and regression evidence before release.
- Pair aggregate measures with traceable individual observations and segment only when the sample supports the distinction.
- Use a shared severity rubric while allowing domain-specific consequences such as accessibility exclusion, financial loss, privacy exposure, or interrupted care.
- Review one direction against criteria or compare several directions against the same contract, baseline, and threshold.

## Tensions and tradeoffs

- A structured protocol improves reproducibility while increasing review effort.
- Broad heuristic coverage finds systemic risks while diluting attention from the primary task.
- Aggregate metrics make patterns visible while obscuring individual barriers and outliers.
- One severity rubric improves consistency while flattening domain-specific consequences.
- Fast stakeholder review supports momentum while encouraging preference-based decisions.
- Approval creates accountability while becoming stale as soon as the artifact changes.

## Failure modes

- The artifact version or state under review is not recorded.
- Feedback is expressed as preference without criterion, evidence, or user consequence.
- A finding cannot be reproduced from its record.
- Automated checks are treated as complete accessibility evidence.
- Averages hide failed tasks or excluded users.
- Severity is based on implementation effort or reviewer authority.
- Comparisons change multiple variables without disclosure.
- A resolved label replaces verification.
- Approval silently applies to a later revision.

## Anti-patterns

- Looks good to me.
- Best practices without a named criterion.
- One composite design score.
- Screenshot-only accessibility review.
- Average success without failure distribution.
- Priority equals severity.
- Comment count equals impact.
- Resolved without retest.
- Approval without revision binding.
- Competitive similarity as the only benchmark.

## Acceptance and review questions

- Does the review contract name artifact revision, audience, task, environment, constraints, success, criteria, evidence, exclusions, and owner?
- Is every finding anchored, reproducible, evidence-backed, consequence-specific, and paired with a falsifiable resolution condition?
- Are task behavior, participant explanation, expert judgment, automated checks, accessibility inspection, analytics, and preference kept distinct?
- Does severity reflect user impact, frequency, reach, criticality, persistence, workaround, regulated consequence, and confidence independently of effort?
- Do comparisons control or disclose differences in task, audience, device, content, data, instrumentation, and success definition?
- Does closure record disposition, owner, target revision, change, retest, verification, residual risk, regressions, and decision?
- Is approval bound only to the exact reviewed artifact revision?
