# Enterprise administration

## Generalized principles

- Keep the active organization, workspace, environment, legal entity, resource, and affected population persistently visible; distinguish navigation context from the scope where a change will apply.
- Explain effective authority as a traceable composition of direct assignments, group membership, role capabilities, inherited policy, temporary grants, external identity sources, and explicit exceptions; show precedence and the path to change each source.
- Separate personal preference, workspace default, organization policy, enforced control, integration-owned value, and entitlement; for every setting show current value, origin, override state, affected population, rollout timing, and available exception or request path.
- Preview high-impact and bulk changes as a concrete diff: selected targets, included and excluded objects, before and after state, dependencies, downstream effects, notification behavior, reversibility, retained data, and recovery procedure.
- Make entitlements inspectable across purchased capacity, enabled capability, assigned access, policy eligibility, actual use, limits, renewal or expiry, and billing consequence; do not use availability as proof of authorization or adoption.
- Record administrative change as immutable evidence with actor and authority, action, target, scope, before and after state, time, source channel, request or correlation identifier, outcome, and recovery event; support filtering and bounded export without altering the record.

## Variation levers

- Use hierarchy navigation when administrators routinely cross scopes; use a locked scope selector for high-consequence tasks.
- Offer role templates for common assignments while exposing effective capabilities and differences before application.
- Use staged rollout, dry run, or sampled preview when a policy affects many identities or resources.
- Require stronger confirmation or dual control according to blast radius, irreversibility, regulated consequence, and privilege escalation.
- Provide bulk operations only with explicit selection summaries, partial-failure handling, idempotency, and downloadable results.

## Tensions and tradeoffs

- A unified administration console improves discovery while increasing wrong-scope risk.
- Role abstraction simplifies assignment while hiding effective permissions.
- Central enforcement improves consistency while restricting legitimate local variation.
- Dense tables support expert scanning while obscuring inherited relationships and consequence.
- Bulk operations improve efficiency while increasing blast radius and partial-failure complexity.
- Detailed audit history improves accountability while increasing privacy and retention obligations.

## Failure modes

- The visible navigation scope differs from the mutation scope.
- A role name is shown without its effective capabilities.
- Inherited and direct access are visually indistinguishable.
- An enforced policy looks like an editable preference.
- An entitlement is treated as assigned access or actual use.
- Bulk selection changes after filtering or pagination.
- A high-impact confirmation repeats the action without previewing consequences.
- An audit event omits before state, authority, or source.
- A partial failure leaves target state ambiguous.

## Anti-patterns

- Global toggle without scope.
- Admin means every permission.
- Role name as the only access explanation.
- Inherited somewhere else.
- Licensed equals enabled.
- Select all without population count.
- Are you sure without a diff.
- Audit log as editable activity feed.
- Success despite partial failure.
- Delete organization without dependency inventory.

## Acceptance and review questions

- Are active context and mutation scope both persistent and unambiguous?
- Can administrators trace effective authority to every direct, grouped, inherited, temporary, external, and exceptional source?
- Does each setting identify preference, default, policy, enforcement, integration ownership, entitlement, origin, override, population, and rollout?
- Do high-impact and bulk changes preview targets, exclusions, diff, dependencies, downstream effects, notifications, reversibility, retained data, and recovery?
- Are purchased, enabled, assigned, eligible, used, limited, expiring, and billable entitlement states distinct?
- Does audit evidence preserve actor, authority, action, target, scope, before and after state, time, source, correlation, outcome, and recovery?
- Are partial failures, retries, and final target states explicit?
