---
name: triage-project-notes
description: Classify, split, deduplicate, relate, defer, archive, reclassify, or promote captured project notes. Use during scheduled review or whenever the user wants to distinguish project context from questions, documentation candidates, backlog, and possible execution work.
---

# Triage Project Notes

Route knowledge conservatively. Classification or promotion never authorizes documentation or execution.

Read [the continuity contract](../../references/continuity-contract.md) and `.continuity/config.json` before changing state.

## Classification

Assign one primary kind per atomic item: `context`, `insight`, `decision`, `question`, `documentation-candidate`, `backlog-candidate`, `execution-candidate`, or `explicit-instruction`.

Split mixed items first. Preserve source relationships. When intent is ambiguous, use context, question, or a held candidate; never upgrade ambiguity to an instruction.

## Routing

- Route context, insights, and decisions to private knowledge.
- Route questions to the open-question queue.
- Route documentation candidates to the promotion queue.
- Route backlog with optional priority and review date.
- Route execution candidates and explicit instructions to planning.
- Archive duplicates or superseded items with provenance instead of deleting history.

Use:

```text
.agents/project-continuity/bin/continuity --project-root "$PWD" note list
.agents/project-continuity/bin/continuity --project-root "$PWD" note triage <capture-id> <item-id> --kind <kind> --action <route|defer|archive|promote>
```

Report classifications, ambiguities, duplicates, and items needing judgment. A valid review may propose no work.
