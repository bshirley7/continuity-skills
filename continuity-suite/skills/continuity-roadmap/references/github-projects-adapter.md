# GitHub Projects Adapter

Use this reference when a project configures `planning_patterns.tracker_provider` as `github` and wants a shared operational projection of canonical roadmap records.

## Authority model

- Committed Markdown under `docs/project-roadmap/entities/` remains canonical.
- GitHub Project items are sanitized operational projections. They never authorize roadmap, goal, execution, merge, or completion changes.
- The explicit `connect` command is one durable authorization for creating or attaching the exact Project, configuring its fields, and automatically creating or editing sanitized roadmap and task items. It does not authorize a different account, Project, visibility, capability expansion, or deletion.
- A remote edit is a reconciliation proposal. Inspect it, retrieve current roadmap context, and route any canonical change through an approved goal with structured `roadmap_impact`.

## First-release scope

The adapter bootstraps or attaches a GitHub Project through `gh`, then manages an export-only set of Project draft issues for committed roadmap entries and private goal lifecycle status. It does not create repository issues, alter pull requests, receive webhooks, delete items, or write canonical roadmap files from remote state.

Each managed draft issue carries:

- a stable `<project_id>:<roadmap_id>` roadmap ID or `<project_id>:goal:<goal_id>` task ID;
- title, sanitized summary, canonical source path, and source revision;
- mapped kind, status, health, priority, and delivery-phase fields;
- optional start date, target date, parent IDs, and dependency IDs.

The adapter fails closed on missing fields, missing single-select options, duplicate Continuity IDs, inaccessible Projects, unsupported managed item types, stale plans, or a missing/mismatched durable connection. Legacy plan/apply exports still require their exact plan approval.

## Setup

1. Set `planning_patterns.tracker_provider` to `github` through project configuration.
2. Authenticate `gh` with the `project` scope and access to the intended owner. Continuity reads the active login, stable GitHub account ID, scope list, and selected Project metadata; it never reads or stores the token. Organization automation should use a least-privilege GitHub App with organization Projects read/write access.
3. Run the connection workflow below. Omit `--project-number` to create a private Project or provide it to attach an existing Project.
4. `Continuity ID` is text. Kind, Status, Health, Priority, and Phase are single-select. Date and relationship fields are optional.

## Connection workflow

```text
gh auth login --hostname github.com --web --scopes project
continuity roadmap github-projects connect \
  --owner-type user \
  --owner <authenticated-login> \
  --title "<project title>" \
  --visibility PRIVATE
continuity roadmap github-projects status
```

For an existing Project, add `--project-number <number>`. The command verifies that the user-owned destination matches the authenticated account, verifies stable account and Project IDs, confirms Project read/write access, configures required fields, records read/write/create/edit capabilities with deletion disabled, and performs the first sync.

The ignored private connection record is durable authorization for sanitized synchronization to that destination. It stores no credentials. Renew only for an account, destination, visibility, capability, deletion-policy, or published-data-class change.

## Automatic synchronization

Goal creation, approval, dispatch, execution state changes, controlled rework, review disposition, and approved roadmap mutations trigger a best-effort sync. GitHub receives sanitized titles and lifecycle fields, never captured notes, exact requests, approval text, private evidence, or memory. A remote failure is recorded as an advisory and preserves the successful local transition.

```text
continuity roadmap github-projects sync
```

The command is idempotent. Stable Continuity IDs distinguish roadmap items from goals. Existing managed items are edited in place; no item is deleted or archived.

## Legacy plan/apply workflow

The older bootstrap and export plan/apply commands remain available for separately approved, non-connected exports. New interactive installations should use `connect` so they do not require repeated approval for every status update.

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
