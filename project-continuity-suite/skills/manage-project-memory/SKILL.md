---
name: manage-project-memory
description: Index, search, brief, audit, verify, curate, promote, and supersede searchable project memory stored as canonical Markdown. Use when trustworthy project context is needed, project documentation should be curated, or memory freshness and contradictions must be audited.
---

# Manage Project Memory

Treat committed Markdown under `docs/project-memory/` as canonical. Treat the ignored SQLite FTS5 database as a rebuildable search index.

Read [the continuity contract](../../references/continuity-contract.md), `.continuity/config.json`, and the project memory index before acting.

## Retrieval

Rebuild the index when needed, then search before planning or execution. Prefer current, verified entries and cite memory IDs, paths, headings, and sources.

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" memory index
.agents/project-continuity/bin/continuity --project-root "$PWD" memory search "<query>"
.agents/project-continuity/bin/continuity --project-root "$PWD" memory brief "<goal or topic>"
.agents/project-continuity/bin/continuity --project-root "$PWD" memory audit
```

Default retrieval excludes raw captures and private ledgers. Use an explicit private scope only when the user needs private context.

## Curation

Never silently overwrite changed understanding. Supersede the prior entry and preserve provenance. Mutation of committed memory requires an approved documentation or execution goal.

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" memory promote <note-id> --goal-id <goal-id> ...
.agents/project-continuity/bin/continuity --project-root "$PWD" memory verify <memory-id> --goal-id <goal-id> --commit <sha>
.agents/project-continuity/bin/continuity --project-root "$PWD" memory supersede <memory-id> --with <replacement-id> --goal-id <goal-id>
```

Mark unverifiable knowledge disputed, historical, or stale. Report contradictions, missing coverage, duplicate IDs, verification age, and malformed entries.
