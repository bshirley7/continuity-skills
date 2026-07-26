# Tracker Provider Contract

Use this contract when adding a remote roadmap surface. GitHub Projects is the first implementation; future Notion, Trello, Jira, or other providers must use the same lifecycle and privacy boundaries.

## Connection lifecycle

Every provider must expose equivalent operations for:

1. `connect`: verify the current human identity, select or create one exact destination, prove required capabilities, and record one durable connection authorization;
2. `status`: re-verify the current identity and destination access without returning credentials;
3. `sync`: read current remote state and create or edit sanitized projections under the durable connection envelope;
4. `inspect`: return remote differences as non-authorizing reconciliation proposals.

Connection records belong in ignored private Continuity state. Store stable provider account and destination IDs, display names, URLs, capabilities, sync policy, and authorization renewal conditions. Never store access tokens, session cookies, device codes, refresh tokens, or private keys.

## Required capabilities

The first supported capability vocabulary is:

- `read`
- `write`
- `create_project`
- `edit_project`
- `create_item`
- `edit_item`
- `delete_item`

Continuity connections enable the first six and keep `delete_item: false`. A provider that cannot distinguish these capabilities must fail closed during connection instead of claiming support.

## Projection contract

- Canonical roadmap Markdown and private goal state remain authoritative.
- Publish only sanitized roadmap records and goal lifecycle status. Do not publish raw captured notes, request text, approval text, credentials, private evidence, or private memory.
- Use stable Continuity IDs so create and edit operations are idempotent.
- Automatic sync is advisory to the originating local transition: record remote failure, preserve canonical state, and retry later.
- Remote edits are proposals only. They never approve execution, expand scope, mark local work complete, or overwrite canonical records.
- Do not delete or archive remote items through the first provider contract. A later deletion capability requires a separate consequential authorization design.

## Authorization renewal

The explicit `connect` invocation authorizes ongoing sanitized synchronization to the bound destination. Do not ask for approval on every task or status update. Renew only when the authenticated account, destination, visibility, capability set, deletion policy, or published data class changes.

## Provider implementation boundary

Keep provider-specific authentication, capability probes, field mapping, API calls, and schemas inside the provider adapter. Keep capture, triage, roadmap modeling, goal lifecycle, privacy classification, and canonical reconciliation provider-neutral. Adding a provider must not add a new planning or authorization workflow.
