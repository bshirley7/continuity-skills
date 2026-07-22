# AI memory and context management

## Generalized principles

- Model context as an inspectable inventory of distinct state: current prompt and session, conversation history, saved facts, preferences and custom instructions, inferred attributes, project or task context, uploaded files, connected sources, workspace knowledge, organization policy, feedback, analytics, safety records, and model-improvement data; show which are temporary, retained, searchable, reusable, shared, exported, or used to adapt future behavior instead of collapsing them into one memory label.
- Give every context item provenance and scope: identify exact content or concise representation, subject, author or inference origin, source object and version, collection time, freshness, confidence where inferred, purpose, permitted operations, active account, identity, project, task, agent, workspace and organization, eligible audiences, geographic or policy boundary, retention and expiry, and whether it influences retrieval, response generation, ranking, automation, personalization, analytics, safety review, or model improvement.
- Make active context visible where it changes an outcome: before or beside a response or task, show which memories, instructions, files, sources, conversations, policies and inferred signals are in scope, why they were selected, what was excluded or unavailable, and whether a source is stale, conflicting or permission-limited; support temporary exclusion, source replacement, context reset, private or no-memory mode, and a preview of the narrower behavior.
- Support correction and forgetting at the level where the problem exists: edit, dispute, annotate, expire, pause, disconnect or delete one item, source, conversation, project, inferred attribute, instruction or purpose without requiring an account-wide reset; distinguish clearing a visible chat from deleting history, saved memory, source copies, embeddings, logs, backups, feedback, derived profiles and model-improvement use, then verify what changed, what remains, why, for how long and where downstream correction propagates.
- Govern shared and derived context as a lifecycle rather than a personal preference: keep subject, contributor, owner, controller, administrator, processor and recipient distinct; do not let one participant's sharing authorize memory about others; expose inherited organization policy, permissions, sync and indexing state, last use, downstream agents, exceptions and audit history; preserve export, portability, objection, deletion, offboarding, incident response and accountable verification across source, index, memory and derived behavior.

## Variation levers

- Use compact item-level memory controls for personal assistants and richer source, permission, indexing, policy and audit views for shared enterprise knowledge.
- Default to session-only context for sensitive, unfamiliar or one-off work and require deliberate promotion into cross-session or shared memory.
- Use automatic expiry for transient facts and explicit review or renewal for sensitive, inferred, disputed or high-impact context.
- Increase source-level access review, administrator controls, subject rights, propagation evidence and independent audit with shared scope and consequence.

## Tensions and tradeoffs

- Persistent context reduces repetition while increasing stale, inappropriate and cross-context reuse.
- Item-level control improves agency while creating privacy labor and incomplete mental models of derived data.
- Rich source provenance improves correction while exposing sensitive workspace structure or third-party information.
- Organization policy can protect shared data while overriding individual preferences or hiding who controls the context.
- Deletion improves agency while backups, safety records, legal holds, trained models and shared copies may limit immediate or complete removal.

## Failure modes

- One memory switch ambiguously governs chat history, saved facts, personalization, connected sources, analytics and model improvement.
- A remembered or inferred fact has no source, subject, purpose, scope, freshness, confidence, expiry or correction path.
- The assistant uses hidden context without showing which memory, source, instruction or policy changed the result.
- Turning memory off prevents new saving but silently leaves prior memory active or retained.
- Deleting a conversation removes it from navigation but not from memory, indexes, derived profiles, feedback or downstream use.
- A user can delete everything but cannot correct or exclude one wrong item without losing valid continuity.
- A workspace source becomes available to broader agents, tasks or people than the source's original permission context.
- One participant's message or file becomes remembered information about another person without authority or notice.
- The interface claims deletion without showing completion, retained exceptions, propagation, timing or verification.

## Anti-patterns

- One memory switch.
- Inference without provenance.
- Hidden active context.
- Off but still remembered.
- Delete only the sidebar.
- All-or-nothing forgetting.
- Workspace scope leak.
- One person's consent for everyone.
- Deletion without verification.

## Acceptance and review questions

- Are session context, history, saved memory, instructions, inferences, files, sources, workspace knowledge, policy, feedback, analytics, safety records and model improvement represented separately?
- Does each item expose content, subject, provenance, source version, time, freshness, confidence, purpose, operations, scope, audience, retention, expiry and behavioral effect?
- Can people inspect the active context behind an outcome and temporarily exclude, replace or reset it without destructive loss?
- Can they correct, dispute, annotate, expire, pause, disconnect or delete at item, source, conversation, project, inference, instruction and purpose level?
- Does deletion distinguish visible history, memory, source copies, indexes, logs, backups, profiles, feedback and improvement use, with honest propagation evidence?
- Are shared subjects, contributors, owners, administrators, processors, recipients, permissions, policy, indexing, downstream use, export, objection, deletion and offboarding governed?
