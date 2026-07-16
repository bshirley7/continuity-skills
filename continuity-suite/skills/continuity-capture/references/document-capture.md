# Document Capture

Read this reference only when the user points to a PRD or feature-request document. The original file is the source of truth for stated product intent at capture time. Do not edit it, promote it to execution authority, or mistake desired behavior for verified implementation behavior.

## Source preparation

1. Accept only local UTF-8 Markdown or plain-text files for v1.
2. Read the complete source before splitting it.
3. Use one capture for one complete document revision.
4. Set `source_type: file` and `document_type: prd` or `feature-request` independently.
5. Use a stable `document_id` across revisions. Prefer an explicit document identifier; otherwise derive one from the project-relative source reference and document type.
6. Use `project-intent` only when the user identifies an in-project file as official product intent. Use `supplied-reference` for every other source.
7. Preserve an optional document-provided version separately from Continuity's revision sequence.

For source examples, read [the synthetic PRD](prd-source.example.md) and [the synthetic feature request](feature-request-source.example.txt). For prepared CLI payloads, read [the PRD input](prd-capture-input.example.json) and [the feature-request input](feature-request-capture-input.example.json).

## Stable anchors

Give every atomic item:

- `source_item_key`: a stable identifier used to relate revisions;
- `heading_path`: the source heading hierarchy;
- `section`: the semantic source section when useful;
- `requirement_id`: the document's explicit requirement identifier when present.

Prefer explicit requirement IDs. Otherwise use a stable key based on heading path and purpose, such as `objectives.reduce-review-time` or `requirements.req-export-audit`. Do not use line numbers, list positions, or capture timestamps as stable keys.

The CLI compares these keys with the prior snapshot. It marks identical text `unchanged`, changed text `changed`, new keys `added`, and missing prior keys `removed`. Unchanged items are archived and linked to their prior item instead of re-entering queues. Removed items remain visible as derived revision evidence.

## PRD decomposition

- Capture the problem, audience, objectives, and success measures as context or insights.
- Capture decisions, constraints, and non-goals as decisions.
- Keep one cohesive requirement and its supporting acceptance criteria in one `execution-candidate` or `backlog-candidate` item.
- Capture risks and unresolved decisions independently.
- Route explicitly later milestones or capabilities as backlog candidates.
- Preserve favorable behavior and non-regression requirements as their own context items.

## Feature-request decomposition

- Preserve the user need, evidence, and current behavior as context.
- Keep the requested behavior and its acceptance criteria in one action candidate.
- Separate exclusions, constraints, dependencies, risks, and unresolved questions.
- Preserve optional parent PRD or roadmap references as provenance, not authorization.

## Boundaries

- Do not create items for headings, boilerplate, or every sentence.
- Do not detach acceptance criteria from the requirement they qualify.
- Do not infer priority, approval, or implementation state from document formality.
- Do not expose raw snapshot content in status or reports.
- Do not create goals automatically. Send eligible atomic candidates through triage and planning.
