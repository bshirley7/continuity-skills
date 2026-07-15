---
name: continuity-memory
description: Index, search, brief, audit, verify, curate, promote, and supersede searchable project memory stored as canonical Markdown. Use when trustworthy project context is needed, project documentation should be curated, or memory freshness and contradictions must be audited.
---

# Continuity Memory

Treat committed Markdown under `docs/project-memory/` as canonical. Treat the ignored SQLite FTS5 database as a rebuildable search index. Private/all scope also indexes raw capture items with their structured occurrence dimensions; this makes feedback searchable without promoting it to canonical truth.

Read [the continuity contract](../../references/continuity-contract.md), [the development assurance standard](../../references/development-assurance-standard.md), `$continuity-local`, `.continuity/config.json`, and the project memory index before acting.

## Required assurance

- Commit only sanitized, project-relevant knowledge authorized by an active goal; never promote raw captures, secrets, personal data, or unverifiable claims.
- Require stable IDs, citations, verification state, confidence, unresolved gaps, and supersession history. Mark uncertainty disputed or historical instead of presenting it as current.
- Audit default-search privacy, stale-index rebuilding, duplicate and orphan IDs, contradictions, code/documentation drift, and the exact memory IDs supplied to planning or execution.

## Retrieval

Rebuild the index when needed, then search before planning or execution. Prefer current, verified entries and cite memory IDs, paths, headings, and sources.

```text
.agents/continuity/bin/continuity --project-root "$PWD" memory index
.agents/continuity/bin/continuity --project-root "$PWD" memory search "<query>"
.agents/continuity/bin/continuity --project-root "$PWD" memory similar "<concept or situation>" --scope all
.agents/continuity/bin/continuity --project-root "$PWD" note patterns
.agents/continuity/bin/continuity --project-root "$PWD" memory brief "<goal or topic>"
.agents/continuity/bin/continuity --project-root "$PWD" memory audit
```

Default retrieval excludes raw captures and private ledgers. Use an explicit private/all scope only when the user needs private context. Similarity and pattern results are planning recommendations, never execution authority.

## Curation

Never silently overwrite changed understanding. Supersede the prior entry and preserve provenance. Mutation of committed memory requires an approved documentation or execution goal.

```text
.agents/continuity/bin/continuity --project-root "$PWD" memory promote <note-id> --goal-id <goal-id> ...
.agents/continuity/bin/continuity --project-root "$PWD" memory verify <memory-id> --goal-id <goal-id> --commit <sha>
.agents/continuity/bin/continuity --project-root "$PWD" memory supersede <memory-id> --with <replacement-id> --goal-id <goal-id>
```

Mark unverifiable knowledge disputed, historical, or stale. Report contradictions, missing coverage, duplicate IDs, verification age, and malformed entries.

## Handoff

Run `continuity workflow status` on entry and exit. Pass exact memory IDs, freshness findings, contradictions, and unresolved gaps to `$continuity-roadmap` or `$continuity-plan`; do not convert a memory finding into execution authority.
