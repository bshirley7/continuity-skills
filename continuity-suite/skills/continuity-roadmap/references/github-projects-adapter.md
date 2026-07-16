# GitHub Projects Adapter

Use this reference when a project configures `planning_patterns.tracker_provider` as `github` and wants a shared operational projection of canonical roadmap records.

## Authority model

- Committed Markdown under `docs/project-roadmap/entities/` remains canonical.
- GitHub Project items are sanitized operational projections. They never authorize roadmap, goal, execution, merge, or completion changes.
- Creating a Project, configuring its fields, or modifying its items is an external side effect. Prepare a deterministic plan, review its exact destination and mutations, and record the exact human approval before applying it.
- A remote edit is a reconciliation proposal. Inspect it, retrieve current roadmap context, and route any canonical change through an approved goal with structured `roadmap_impact`.

## First-release scope

The adapter bootstraps a GitHub Project through `gh`, then manages an export-only set of Project draft issues. It does not create repository issues, alter pull requests, receive webhooks, or write canonical roadmap files from remote state.

Each managed draft issue carries:

- a stable `<project_id>:<roadmap_id>` Continuity ID;
- title, sanitized summary, canonical source path, and source revision;
- mapped kind, status, health, priority, and delivery-phase fields;
- optional start date, target date, parent IDs, and dependency IDs.

The adapter fails closed on missing fields, missing single-select options, duplicate Continuity IDs, inaccessible Projects, unsupported managed item types, stale plans, or missing approval.

## Setup

1. Set `planning_patterns.tracker_provider` to `github` through project configuration.
2. Authenticate `gh` with the `project` scope and access to the intended owner. Organization automation should use a least-privilege GitHub App with organization Projects read/write access.
3. Either run the bootstrap workflow below or copy `.agents/continuity/templates/github-projects-settings.json` to `.continuity/github-projects.json` and configure an existing Project manually.
4. `Continuity ID` is text. Kind, Status, Health, Priority, and Phase are single-select. Date and relationship fields are optional.

## Bootstrap workflow

Bootstrap creates the Project with GitHub CLI, explicitly sets its visibility, configures the required fields, saves the returned Project number to `.continuity/github-projects.json`, and prepares the first export plan. It updates GitHub's default `Status` field rather than creating a duplicate.

```text
continuity roadmap github-projects bootstrap plan \
  --owner-type organization \
  --owner <github-owner> \
  --title "<project title>" \
  --visibility PRIVATE
continuity roadmap github-projects bootstrap approve <bootstrap-plan-hash> \
  --approved-by <identity> \
  --authorization-text "<exact text returned by bootstrap plan>"
continuity roadmap github-projects bootstrap apply <bootstrap-plan-hash>
```

Bootstrap application is resumable after a partial remote failure. Its private checkpoint records the created Project before field setup continues, preventing a normal retry from creating another Project. The result returns an `export_plan_hash` and exact `export_authorization_text`; publishing roadmap items still requires the separate export approval below.

## Export workflow

```text
continuity roadmap github-projects plan --settings .continuity/github-projects.json
continuity roadmap github-projects inspect <plan-hash>
continuity roadmap github-projects approve <plan-hash> \
  --approved-by <identity> \
  --authorization-text "<exact text returned by plan>"
continuity roadmap github-projects apply <plan-hash>
```

Projects requiring signed approvals must also pass `--signing-key` to `approve`. Application re-derives the plan from current canonical Markdown and settings; any drift invalidates approval.

Reapplying an unchanged plan is idempotent: existing managed draft issues and matching fields are left unchanged. Application results are recorded privately under `.continuity/private/integrations/github-projects/`.

## Reconciliation and future webhooks

`inspect` reads the Project and returns differences without writing either side. A future organization-level webhook receiver or local poller may invoke the same inspection path, but it must:

- validate webhook signatures and deduplicate delivery IDs;
- fetch fresh Project state instead of treating the payload as complete truth;
- ignore or coalesce the adapter's own updates to prevent loops;
- preserve the last-synced plan hash and source revision;
- route material remote changes into capture, triage, and roadmap reconciliation;
- never map a dragged card or closed issue directly to Continuity approval, execution, or completion.

For user-owned Projects, prefer authenticated polling because GitHub Projects item webhooks are organization-level and preview-dependent.
