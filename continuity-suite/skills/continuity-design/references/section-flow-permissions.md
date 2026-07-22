# Permissions

## Generalized principles

- Name the requester, granting identity, resource owner, and destination before asking for access, distinguishing a person, application, service, group, administrator, and external party.
- Describe permissions as concrete data reads, writes, actions, exports, downloads, comments, edits, administration, billing, or impersonation capabilities, separating independently optional scopes to support least privilege.
- Expose resource and audience scope together with role, including account, workspace, project, folder, document, field, environment, device resource, organization, or public reach, and label inherited access and its source.
- State duration and lifecycle explicitly through one-time, while-in-use, ongoing, pending, expiring, deactivated, or revoked status, and provide the later review and revocation path at grant time.
- Request access just in time for a user-initiated capability, explain why it is needed now, offer the narrowest useful scope, and preserve a functional alternative or honest limitation after denial when possible.
- Keep requested, granted, denied, inherited, effective, pending, expired, and revoked states distinct; an enabled app control or sent invitation must not imply that underlying access is active.
- Explain roles through capability boundaries and pair role changes with resource scope, seat or billing effects, data restrictions, ownership transfer, and removal consequences before saving.
- Separate internal membership, guest access, public links, publication, embedding, and exports, showing capability, expiration, protection, resharing, and external-domain consequences for each boundary.
- Make effective access inspectable through owner, groups, policy source, authentication posture, creation and last-use time, expiration, status, and attributable audit history, with direct rotate, revoke, remove, or terminate actions.
- Use proportionate confirmation for grants and removals with high consequence, showing the exact access delta and preserving evidence of who approved, changed, or revoked it.

## Variation levers

- Use a scoped consent checklist for independent application permissions, a role selector for bundled team capabilities, and a policy matrix or graph for many subjects and resources.
- Use one-time or selected-item access for a bounded task, while-in-use access for an active feature, and expiring access for temporary collaboration or support.
- Use direct assignment for named people, groups for managed inheritance, guests for bounded external collaboration, and public links only for intentional broad reach.
- Use capability presets for common roles and advanced overrides only when field, environment, or resource restrictions materially differ.
- Use inline purpose before the system prompt on devices and detailed scope review inside the platform for connected applications.
- Use a pending state for invitations and approvals, an active state only after acceptance and grant, and an expired or revoked state that remains auditable.
- Use tables for account review, relationship views for inherited policy, and audit timelines for reconstructing changes.
- Use immediate revocation for active security incidents and staged review for ordinary role, ownership, or seat changes.

## Tensions and tradeoffs

- Granular scopes support least privilege while increasing consent complexity and setup failures.
- Bundled roles improve consistency while granting capabilities that some members do not need.
- Inherited group access simplifies administration while obscuring why a person can reach a resource.
- Just-in-time prompts preserve context while interrupting the user's current task.
- Denial alternatives preserve autonomy while limiting features that genuinely depend on the permission.
- Public links reduce collaboration friction while weakening identity, expiration, and resharing controls.
- Detailed audit evidence improves accountability while exposing sensitive user and security activity.
- Strong confirmation reduces accidental grants while slowing urgent support and incident response.

## Failure modes

- The requester, granting identity, owner, or destination is ambiguous.
- A permission uses a broad access label without naming concrete read, write, action, export, or administration capabilities.
- Role is shown without the resources, audiences, environments, or inherited source it affects.
- Ongoing or elevated access has no duration, status, review date, or revocation path.
- A permission is requested before a relevant user action or falsely described as required.
- Requested, pending, granted, effective, expired, and revoked states are conflated.
- A role change hides seat cost, data restrictions, ownership, or removal consequences.
- Internal, guest, link, public, publication, embed, and export boundaries are mixed.
- An access review omits owner, group, policy, authentication, age, usage, or history.
- A high-impact grant or removal does not show the exact delta or approver evidence.

## Anti-patterns

- Selecting every application scope by default.
- Using allow as the only path to continue when the capability is optional.
- Displaying an app-level enabled switch before the operating-system grant is effective.
- Naming roles without explaining capabilities.
- Treating a pending invitation as active membership.
- Hiding inherited access behind an undifferentiated viewer or editor label.
- Using anyone-with-link without expiration, protection, or resharing context.
- Granting permanent support access for a temporary troubleshooting need.
- Showing an access graph without effective-resource detail or change preview.
- Removing access without recording actor, time, subject, scope, and prior state.

## Acceptance and review questions

- Are requester, granting identity, resource owner, and destination explicit?
- Are concrete read, write, action, export, edit, billing, and administration capabilities separable where possible?
- Are role, resource, audience, environment, and inheritance source shown together?
- Are duration, pending or active status, expiration, review, and revocation paths visible?
- Is the request just in time, purpose-specific, least-privilege, and honest about denial?
- Are requested, granted, denied, inherited, effective, pending, expired, and revoked states distinct?
- Do role changes disclose capability, scope, seat, billing, data, ownership, and removal effects?
- Are internal, guest, link, public, publication, embed, and export boundaries separately reviewable?
- Can administrators inspect owner, groups, policy, authentication, age, usage, status, and audit history?
- Do high-impact grants and removals show the exact access delta and preserve approver evidence?
