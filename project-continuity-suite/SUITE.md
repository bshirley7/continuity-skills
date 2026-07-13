# Project Continuity Suite

This suite turns project conversations and notes into searchable knowledge, reviewable goals, safely sequenced execution, and evidence-backed reports.

## Operating boundary

Notes are knowledge first. Capture and triage never authorize documentation or code changes. An executable goal requires a decision-complete plan, exact version approval, a valid plan hash, successful preflight, and explicit dispatch.

## Installed layout

```text
.agents/skills/                         project-level skills
.agents/project-continuity/             CLI, schemas, templates, contract
.agents/references/continuity-contract.md
.continuity/project.json                committed enrollment and schedule intent
.continuity/config.json                 committed project configuration
.continuity/private/                    ignored captures, queues, goals, locks, indexes
docs/project-memory/                    canonical searchable project memory
```

The installed control directory also includes project-neutral recurring-action prompt assets. The Codex app owns each developer's actual schedules. A developer-local scheduler discovers enrolled repositories from configured workspace roots, then invokes the skills and CLI installed inside each project. No project paths, notes, memory, or registry are stored in this distribution.

Installation creates a minimal project-memory index and leaves product-code execution disabled unless `--enable-execution` is explicitly supplied. An optional `--seed` may point to project-specific memory data outside this distribution.

## Installation

```text
python3 project-continuity-suite/installer/install.py \
  --project-root <repository> \
  --project-id <stable-project-id> \
  --integration-branch <branch> \
  --validation <project-validation-command>
```

Run the installer again to update an existing installation; managed `AGENTS.md` and `.gitignore` blocks are idempotent. Then run the installed `continuity --project-root <repository> --json project doctor`. Keep developer workspace roots and Codex automation records in developer-local configuration, never in this repository.

## Typical cycle

1. Invoke `$capture-project-note` in the active project conversation.
2. Invoke `$triage-project-notes`, or allow the nightly review to classify and route items.
3. Use `$manage-project-memory` to retrieve a cited context brief.
4. Use `$plan-project-goals` only for selected candidates.
5. Approve an exact goal version; it queues for 10:00 PM America/Chicago.
6. Use `$dispatch-project-goals` to start an approved goal earlier when needed.
7. Use `$execute-project-goal` in the assigned isolated worktree.
8. Use `$report-project-progress` for completion and morning reporting.

```mermaid
flowchart LR
    A["Captured notes"] --> B["Atomic classification"]
    B --> C["Private project knowledge"]
    B --> D["Questions and deferred items"]
    B --> E["Planning candidates"]
    C --> F["Approved memory promotion"]
    F --> G["Trusted searchable memory"]
    E --> H["Versioned plan"]
    G --> H
    H --> I{"Explicit plan approval"}
    I -->|"No"| J["Feedback or hold"]
    I -->|"Yes"| K["10 PM queue or manual start"]
    K --> L["Isolated project worktree"]
    L --> M["Review, validation, security, and merge-safety gates"]
    M --> N["Human-review PR"]
    N --> O["Morning and completion reports"]
```

## Responsible development compliance

Every goal has a `compliance.json` ledger. The CLI blocks approval until memory retrieval and plan review are evidenced, blocks dispatch on failed preflight, and blocks completion until implementation, code review, validation, security review, merge safety, documentation, memory impact, and final alignment are passed or explicitly not applicable with evidence.

## Local validation

```text
python3 -m unittest discover -s project-continuity-suite/tests -v
python3 -m py_compile project-continuity-suite/bin/continuity project-continuity-suite/installer/install.py
```

Validate each skill with the `skill-creator` `quick_validate.py` utility. The validator requires PyYAML in its Python environment.

## Future adapters

The capture schema reserves `notion` and `linear` source types. An adapter must provide stable source references, timestamps, deduplication keys, provenance, and raw snapshot references. It must enter through the same classification and authorization gates; integrations may not dispatch work directly.
