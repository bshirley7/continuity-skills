# Data continuity, convergence, and user confidence

## Generalized principles

- Model continuity as an explicit state machine rather than a connectivity icon: distinguish local persistence, queued intent, attempted transmission, remote receipt, durable acceptance, downstream processing, convergence and final outcome; bind each state to the exact object, revision and action; expose timestamps, provenance and uncertainty; and never use success language for a stage whose later guarantees have not been met.
- Preserve user intent before optimizing convergence: make local work durable and inspectable, retain stable action identity and ordering, preserve drafts and both sides of divergence, support export and recovery independent of service availability, and avoid resolution strategies that silently discard semantically distinct work merely because one timestamp or server is newer.
- Make retry safe from interface through infrastructure: classify transient, permanent, validation, authorization and conflict failures; use stable request identity and idempotent effects; bound automatic retries with delay and load spreading; keep cancellation and status coherent; prevent duplicate financial, communication or legal side effects; and surface a recoverable decision when automation cannot prove the outcome.
- Treat stale and partially available state as a decision-quality concern: show source, last successful synchronization, pending changes, unavailable dependencies and degraded capabilities; permit safe reading or reversible local work where useful; require fresh validation before consequential commitment; and provide an alternate route when connectivity, device support or service availability would otherwise exclude the user.
- Resolve conflict at the grain of human intent: identify interacting fields, structures, ordering, formatting, ownership and side effects; merge automatically only where compatibility is established; otherwise compare in meaningful context, preserve authorship and both versions, preview the resulting state, support authorized combine, duplicate, defer or compensate choices, and keep reversible lineage after resolution.
- Validate confidence under real failure sequences, not a single airplane-mode screen: test process death, device restart, network flapping, metered and slow links, clock skew, stale credentials, storage pressure, concurrent edits, duplicates, reordered and late messages, partial downstream success, cancellation and service shutdown; measure lost intent, duplicate effects, false completion, convergence time, recovery success and comprehension of status.

## Method

- Map every durability and authority boundary from local interaction through final business effect, with the evidence that proves each transition.
- Classify each read and mutation by offline safety, freshness need, reversibility, duplicate consequence, dependency and conflict grain.
- Design local preservation, stable action identity, queue inspection, safe retry, cancellation, degraded capability and alternate-route behavior.
- Define conflict detection and resolution around semantic intent, then preserve both source versions and resulting lineage.
- Exercise adversarial disconnection and partial-failure sequences and verify user comprehension, data integrity and recoverability end to end.

## Ethical safeguards

- Do not imply that local save, queueing or server receipt means a legal, financial or operational process completed.
- Do not silently discard one person's work through last-write-wins when concurrent intent may be meaningful.
- Do not retry non-idempotent actions in ways that can duplicate payment, consent, signature, message, order or deletion.
- Do not expose cached high-consequence values as current without origin and freshness.
- Do not make reliable service depend on expensive bandwidth, unlimited storage, constant power or one device class.
- Do not retain sensitive offline data indefinitely or on a shared device without visible scope, protection and removal.
- Do not resolve ambiguity by forcing users to reconstruct lost work or understand implementation-level diffs.
- Do not hide degraded mode, delayed processing, partial completion or permanent failure.
- Do not make cancellation appear complete while irreversible or downstream steps remain active.

## Variation levers

- Raise freshness, confirmation and human-resolution requirements with consequence, shared authority, irreversibility and semantic coupling.
- Use automatic background convergence for reversible low-risk work and explicit queues for actions whose timing, recipient or context can become stale.
- Select field, block, object or transaction-level conflict handling according to the smallest unit whose intent can be understood independently.
- Balance local retention and prefetch against device sharing, storage, battery, metered connection, regulation and sensitivity.

## Tensions and tradeoffs

- Fast optimistic interaction increases continuity while allowing work against stale permissions, inventory or policy.
- A cloud authority simplifies convergence while weakening user ownership and availability when the service disappears.
- Automatic retries mask transient failure while producing overload or duplicate effects when identity and limits are wrong.
- Fine-grained merge preserves more work while increasing complexity and the chance of semantically invalid combinations.
- Detailed sync status builds trust while exposing technical concepts and creating notification fatigue.

## Failure modes

- One checkmark collapses local save, remote receipt and final completion.
- An online indicator is used as proof that the latest object state is current.
- Automatic retry repeats an irreversible effect after the response was lost.
- A newer timestamp overwrites a valid concurrent change without evidence or recovery.
- Offline work vanishes after process death, logout, storage pressure or account switching.
- A read-only or degraded mode omits the actions and deadlines users can no longer complete.
- Conflict UI shows raw serialized data instead of human intent and consequence.
- Cancellation stops the interface but not queued or downstream work.
- Testing covers clean disconnect and reconnect but not flapping, late, duplicate or reordered events.

## Anti-patterns

- Universal success checkmark.
- Connectivity equals freshness.
- Blind retry.
- Newest timestamp wins.
- Ephemeral offline work.
- Degradation without route.
- Implementation diff as decision.
- Cosmetic cancellation.
- Airplane-mode-only testing.

## Acceptance and review questions

- What exact evidence distinguishes local persistence, queued intent, remote acceptance, downstream processing, convergence and final outcome?
- Can the user inspect, export and recover local intent and both sides of divergence independently of service availability?
- Are retries bounded and idempotent across every side effect, with coherent status, cancellation and human recovery for uncertain outcomes?
- Do cached and degraded states expose origin, freshness, missing capabilities and required revalidation before consequential action?
- Does conflict handling preserve semantic intent, authorship, both versions, consequence preview and reversible lineage at the correct grain?
- Have realistic failure sequences demonstrated no silent loss, duplicate effects or false completion and successful comprehension and recovery?
