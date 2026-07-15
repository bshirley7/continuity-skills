# Capture Examples

Read this reference when source content contains multiple ideas, feedback, uncertainty, timing, sensitive detail, or language that could be mistaken for authorization.

For a complete input accepted by `note capture --items-file`, see [capture-input.example.json](capture-input.example.json). It is synthetic structure, not project evidence or authorization.

## Atomicity

Source: “The approval view is clearer now, but move the warning beneath the total and consider adding export later.”

Create three items:

1. Positive feedback about clarity, retained as evidence of behavior to preserve.
2. A requested warning-position change, provisionally action-oriented but non-authorizing.
3. An uncertain future export idea, provisionally backlog or context.

Do not collapse these into “Improve the approval view.” That loses sentiment, sequencing, and scope.

## Evidence versus interpretation

Good:

- Evidence: “The requester changed the grouping requirement in revisions 2 and 3.”
- Interpretation: “A bounded configuration boundary may reduce rework.”
- Confidence: medium, because two changes show recurrence but not a universal need.

Bad: “The requester is indecisive, so everything should be configurable.”

Describe occurrences and possible design implications, not personality.

## Timing versus authorization

“It would be useful to see this tomorrow” is timing context. “Approve goal OBJ-14 version 2 for scheduled dispatch” may be authorization only when supplied by the human and accepted by the dispatch command. Capture never sets `execution_authorized: true`.

## Conservative metadata

- Use `positive`, `negative`, `mixed`, or `neutral` only when supported by source wording; otherwise use `unknown`.
- Use the event time for `occurred_at` when stated and set `occurred_at_confidence: exact`. Otherwise preserve capture time and use `capture-time`, `approximate`, or `unknown` as supported by the source.
- Keep stakeholder roles broad when identity is unnecessary.
- Preserve qualifiers such as “possibly,” “after launch,” or “only for administrators.”
- Do not infer impact, priority, or urgency from emphasis alone.

## Privacy minimization

Capture the minimum content needed to preserve the project signal. Replace unnecessary credentials, personal details, customer records, private URLs, and local paths with a redaction marker and a source reference. Never reproduce a secret to prove it was redacted.

## Handoff checklist

- Every item is independently classifiable.
- Positive and negative evidence are preserved symmetrically.
- Source, timestamps, project mapping, and deduplication key are present.
- Original wording and interpretation remain distinguishable.
- Ambiguity is visible to triage.
- Every item remains private and `execution_authorized: false`.
