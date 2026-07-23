# Output Quality Rubrics

Use these rubrics as an internal self-review before handing work to another Continuity skill. Evaluate each applicable dimension as `meets`, `partial`, or `missing`, then record only actionable findings in the stage's existing evidence, blocker, or compliance record. Do not create a parallel approval or quality state. A missing dimension blocks handoff only when it maps to a required machine gate, compliance stage, approved acceptance criterion, or explicit project requirement.

## Shared dimensions

- **Traceable:** Claims cite stable IDs, paths, timestamps, hashes, commands, or source references.
- **Current:** Evidence freshness is known; stale or disputed evidence is labeled.
- **Bounded:** Scope, exclusions, and newly discovered work are separated.
- **Decision-complete:** Material unresolved decisions are named with an owner and block the affected path.
- **Actionable:** The next skill receives exact inputs and does not need to reconstruct intent from raw conversation.
- **Secure and private:** Secrets, personal data, raw notes, local private state, and unsafe instructions are excluded.
- **State-accurate:** Status and allowed actions match `continuity workflow status`.
- **Proportionate:** Detail matches risk and complexity; no irrelevant lens or artifact is added for appearance.

## Stage minimums

| Stage | Required quality properties |
| --- | --- |
| Capture | Atomic, source-traceable, timestamped, conservatively classified, deduplicated, private, non-authorizing |
| Triage | One primary kind, explicit route, preserved provenance, ambiguity held, eligibility current, planning evidence verified when required |
| Memory | Stable ID, canonical source, status, confidence, citations, freshness, relationships, unresolved gaps |
| Roadmap | Stable IDs, hierarchy, dependencies, health, committed versus proposed distinction, structured impact |
| Plan | One cohesive outcome, current evidence, explicit decisions, per-note dispositions, scope and exclusions, slices, acceptance, risks, validation, rollback, unattended suitability |
| Dispatch | Exact human authority, current hash and state, dependencies, capacity, lock, idempotency, runtime, preflight readiness |
| Execute | Approved scope only, checkpoint evidence, focused diff, tests, seven artifacts including product conformance, clean final state, discoveries routed separately |
| Product audit | Explicit source authority and time horizon, representative coverage, portable evidence, source-bound hashes, scoped findings, non-authorizing capture |
| Test | Reproducible commands, current source fingerprint, targeted regression, code review, security review, failures and residual risk |
| Merge | Tested head equals pushed and PR head, correct base, focused diff, current gates, draft status when incomplete, factual human evidence |
| Report | Decisions first, exact subject and recommendation, supporting evidence, allowed disposition, blocker detail, privacy-safe summary |
| Share | Selected atomic content, minimum necessary text, redaction, exact target and version, immutable hash, non-authorizing import |
| Design | Inspected current-state evidence, strengths and gaps, project-specific distinct directions, explicit tradeoffs, preservation and non-goals, target-appropriate grammar, implementation guidance, observable drift checks, accessibility, modality limits, selected exact draft, catalog versions, immutable hash, non-authorizing approval |
| Improve | Sanitized objective usage evidence, stable patterns, exact skill and playbook hashes, bounded playbook-only edits, disjoint validation and test cases, strict improvement, no test regression, protected invariants, retained rejection evidence, explicit human review, non-authorizing package |

## Blocking defects

Do not hand off when any of these apply:

- an identifier, source, approval, plan version, commit, branch, PR, or target is guessed;
- positive or negative feedback is stripped of qualifiers or provenance;
- an assumption resolves a human-required decision;
- source material and interpretation are indistinguishable;
- an action candidate is presented as an instruction;
- acceptance criteria cannot be tested or observed;
- failed, skipped, flaky, stale, or unavailable evidence is presented as passed;
- private content appears in a committed, shared, or portfolio artifact;
- the stated next action is not machine-listed as allowed.

## Review response

When a rubric is partial or missing, report:

1. the affected dimension;
2. the exact missing or stale evidence;
3. whether the issue blocks the whole handoff or only one branch;
4. the skill or human action needed to resolve it;
5. what remains valid and should be preserved.
