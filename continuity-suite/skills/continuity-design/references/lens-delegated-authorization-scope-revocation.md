# Delegated authorization, scope, and revocation

## Generalized principles

- Make the delegation model explicit before asking for agreement: identify the resource owner or authorizing administrator, requesting client, authorization service, protected resource and tenant, acting identity, intended audience, beneficiary, purpose, requested duration, and whether the client will read data, change data, trigger actions, act unattended, or delegate further; never collapse authentication, authorization, installation, data processing, and automation into one consent.
- Request and present the least authority needed for the current purpose: bind access to specific resources, tenants, objects, fields, actions, environments, subjects, value or consequence limits, and time; translate protocol scopes into concrete user-visible capabilities and exclusions; avoid broad defaults, hidden implied scopes, bundled unrelated purposes, and future-use access; request additional authority only when the user invokes the dependent capability.
- Make authorization an informed, attributable decision: show verified client and provider identity, selected account, requested versus previously granted versus newly added access, who can authorize for whom, policy restrictions, material risks and downstream processing, refusal and partial-choice options, effective and expiry time, and a durable receipt; preserve a clear distinction between a person’s choice, administrator policy, pre-established trust, and system-issued credentials.
- Expose delegated authority as a living state rather than a one-time screen: let authorized people inspect client, account, issuer, audience, scopes and resources, active sessions or credentials, last use, refresh and expiry, dependent workflows, data sharing, administrator constraints, and material changes; require fresh authorization when purpose, client, account, resource, scope, audience, risk, or acting behavior expands.
- Design revocation as verifiable containment: offer an accessible route to withdraw or administratively terminate authority, distinguish local disconnect, token revocation, session logout, application uninstall, credential rotation, data deletion, and workflow shutdown, explain cascading and non-cascading effects, stop new use promptly, surface failures or residual access, preserve necessary accountability evidence, and tell the person what retained data or independent provider action remains.

## Method

- Map resource owner, administrator, user, client, authorization service, identity provider, protected resources, tenants, audiences, downstream processors, credentials, sessions, and automated actors.
- Inventory every requested resource, scope, object, field, action, environment, subject, consequence limit, duration, refresh path, and implied or bundled capability.
- Translate technical grants into purpose-linked capabilities, exclusions, risks, acting behavior, and concrete examples understandable at the decision point.
- Design refusal, granular choice, incremental authorization, administrator policy, receipt, inspection, expiry, reauthorization, and material-change handling.
- Map local disconnect, token and grant revocation, logout, uninstall, webhook and subscription termination, workflow shutdown, retained data, and provider-side control.
- Test wrong-account binding, confused authority, scope expansion, audience mismatch, stale consent, shared administration, unattended action, revocation failure, residual tokens, and misleading deletion claims.

## Ethical safeguards

- Do not use sign-in familiarity, provider branding, urgency, default selection, or a single allow action to disguise broad delegated authority.
- Do not require unrelated access, future-use permissions, promotional processing, or broad organizational reach as a condition of one bounded capability.
- Do not imply that a person can authorize organizational, shared, third-party, or administrator-controlled resources when they lack that authority.
- Do not silently broaden scope, change the connected account, re-enable an expired grant, or preserve unattended action during reconnection.
- Do not describe local disconnection, logout, uninstall, or hidden listing removal as full revocation when credentials or provider-side access survive.
- Do not make withdrawal harder than authorization or punish refusal and revocation with avoidable loss of unrelated service, work, or data.

## Variation levers

- Use runtime user authorization for personal resources and a separate administrator installation path for organization-wide resources and policy.
- Use incremental authorization for optional capabilities and stronger reauthentication or independent approval for high-value, destructive, or unattended actions.
- Use short-lived, audience-restricted authority for high-risk access and visible periodic review for long-lived integrations.
- Offer local pause for reversible operational control and full grant revocation for privacy, compromise, ownership change, or relationship termination.

## Tensions and tradeoffs

- Granular scopes improve control while overwhelming users when capability labels are technical, numerous, or disconnected from purpose.
- Long-lived access improves continuity while making stale authority and unnoticed compromise more consequential.
- Administrator installation supports shared workflows while reducing individual choice and obscuring who authorized access.
- Single sign-on reduces credential burden while users may mistake authentication for permission to process data or act.
- Cascading revocation contains risk while abruptly breaking dependent workflows and shared services.

## Failure modes

- The screen identifies an app but not the authorizing actor, selected account, tenant, protected resource, audience, beneficiary, or acting behavior.
- Technical scope names or vague phrases hide concrete data, actions, exclusions, duration, and downstream processing.
- Authentication or administrator policy is presented as the person’s voluntary consent.
- Previously granted, newly requested, denied, expired, and active authority are visually indistinguishable.
- A reconnect flow silently changes account, audience, scope, duration, or unattended capability.
- Revocation terminates one token or local session while refresh credentials, grants, webhooks, workflows, or provider access survive.
- The interface claims data deletion or complete disconnection without evidence about retained copies and independent systems.

## Anti-patterns

- Sign in means consent.
- Allow everything.
- Scope by jargon.
- Admin chose for everyone.
- Forever by default.
- Reconnect and expand.
- Disconnect equals revoke.
- Logout means deletion.

## Acceptance and review questions

- Are resource owner or administrator, client, authorization service, protected resource and tenant, acting identity, audience, beneficiary, purpose, duration, and acting behavior explicit?
- Are requested resources, scopes, objects, fields, actions, environments, subjects, limits, exclusions, implied capabilities, and future-use access concrete and purpose-bound?
- Can people distinguish authentication, authorization, installation, consent, administrator policy, data processing, automation, session, and credential state?
- Are requested, previously granted, newly added, denied, active, refreshed, expired, revoked, and compromised authority visibly distinct and inspectable?
- Does material expansion of purpose, client, account, resource, scope, audience, risk, duration, or unattended behavior require fresh authorization?
- Can users verify local disconnect, grant and token revocation, logout, uninstall, workflow shutdown, residual access, retained data, and provider-side actions without losing unrelated service?
