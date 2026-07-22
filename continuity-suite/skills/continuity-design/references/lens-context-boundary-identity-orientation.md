# Context boundary and identity orientation

## Generalized principles

- Represent identity and context as an explicit tuple: authenticated person or workload, credential or session, represented profile, organization or tenant, resource hierarchy, effective role and policy, intended audience and requested action; use immutable identifiers underneath human-readable labels; and never infer resource authority solely from successful authentication, a client-supplied tenant value or a familiar visual identity.
- Maintain continuous orientation at the boundary: expose the current account, represented identity, tenant or workspace and role where they affect content or consequence; identify current state programmatically and with redundant visual and textual cues; preserve predictable navigation; announce material context changes; and avoid revealing unnecessary personal or organizational identifiers on shared or public displays.
- Treat context switching as an atomic security and interaction transition: require deliberate selection, validate access, resolve or bind dirty state and background operations, obtain context-appropriate session or resource scope, clear or partition prior-context caches, re-evaluate role and policy, load the destination, move focus meaningfully and confirm completion; on failure, preserve the prior safe context and explain recovery.
- Enforce the same context boundary across interface and system state: scope every resource query, cache key, storage path, queue, notification, suggestion, search index, analytics event, export, log and background job; label intentionally aggregated views; validate authorization on every request; and test for transient flashes, stale tokens, confused deputies, direct-object access and cross-context action rather than trusting the visible selector.
- Make authority contextual and consequence-sensitive: show that the same person may be owner, administrator, member, guest, child, delegate or viewer in different contexts; apply least privilege and deny by default; distinguish selection from invitation, authentication, consent, delegation and elevation; restate actor, tenant, resource and effect before consequential action; and require fresh verification or independent approval when policy and harm justify it.
- Preserve context-bound continuity without cross-boundary memory leakage: associate drafts, return locations, recent items, preferences, uploads and recovery state with the exact context and authority under which they were created; revalidate on resume after role, membership or policy changes; minimize identity attributes and behavioral linkage across contexts; and give shared-device users reliable local sign-out and data-clearing controls.
- Design lifecycle, loss of access and remedy as first-class states: represent invitation, acceptance, active membership, guest status, restriction, suspension, credential expiry, role change, leaving, removal and deprovisioning; explain changes without leaking protected policy or membership; stop access and background processing promptly; preserve lawful retention, export, handoff, appeal and audit routes; and test offboarding across sessions, devices, caches and derived data.

## Method

- Map person, credential, represented identity, tenant, resource hierarchy, role, policy, audience, data owner, billing owner and action separately.
- Define the persistent orientation cues and accessible current-state semantics for every context-sensitive surface.
- Specify switching as an atomic transition covering dirty state, background work, session and token scope, caches, authorization, focus, loading, completion and rollback.
- Partition every interface and system-derived state by the same context boundary and define any intentional aggregation explicitly.
- Review consequential actions, lifecycle changes, shared-device privacy, loss of access, offboarding, audit and remedy across role and tenant combinations.

## Ethical safeguards

- Do not equate a signed-in person with one stable role, organization, profile or authority.
- Do not make logos, avatars or color the only way to identify a current context.
- Do not apply a context switch on focus, hover or another input that people cannot review and predict.
- Do not expose prior-context content, notifications, suggestions or counts while a new context loads.
- Do not rely on a visible tenant selector as proof that queries, caches, tokens and background jobs are isolated.
- Do not carry drafts, recipients, payment methods, credentials, destructive selections or behavioral profiles across contexts without exact justified scope.
- Do not present switching, invitation acceptance or profile selection as permission elevation.
- Do not reveal private email, child, employer, guest or membership details merely to disambiguate when a less sensitive identifier works.
- Do not let removal from a context silently strand owned work, lawful export, appeal or required handoff.

## Variation levers

- Increase persistent context cues as visual similarity and action consequence increase.
- Use faster switching for clean read-only contexts and stronger review for dirty state, transactions, administration, publishing and physical or external effects.
- Minimize identifiers on shared devices while providing richer role, environment and billing disambiguation in private administrative tools.
- Require fresh authorization and context-specific tokens where tenant, project, environment or resource audience is a security boundary.

## Tensions and tradeoffs

- Seamless switching improves flow while obscuring a real policy and security boundary.
- Persistent context labels improve safety while consuming scarce interface space.
- Unified activity reduces navigation while increasing leakage and cross-context mistakes.
- Remembered context improves continuity while reopening sensitive state after membership or role changes.
- Detailed disambiguation prevents mistaken identity while exposing private account and organizational information.

## Failure modes

- The interface cannot state which person, profile, tenant, role and resource context are active.
- A visual context change occurs without a programmatic current state or announcement.
- A switch completes visually before session, authorization, cache and background state are rebound.
- Failure leaves the interface showing one context while actions target another.
- A unified search or notification action executes in an unlabeled source context.
- Role and policy are assumed to follow the person across tenants.
- A client-controlled identifier or stale token selects another tenant's data.
- Local continuity reopens content after access was removed or a shared-device user changed.
- Offboarding removes access in the main interface but leaves sessions, caches, exports or background jobs active.

## Anti-patterns

- Identity as avatar.
- Unannounced context change.
- Visual switch before security switch.
- Split-brain context.
- Actionable unlabeled aggregation.
- Portable role assumption.
- Client-selected tenant trust.
- Stale continuity after revocation.
- Interface-only offboarding.

## Acceptance and review questions

- Can the design state the authenticated person, represented identity, tenant, resource hierarchy, role, policy, intended audience and action without conflating them?
- Is current context persistently and programmatically identifiable with predictable navigation, announced change and privacy-appropriate disambiguation?
- Does switching atomically protect dirty state, rebind session and resource scope, partition caches, re-evaluate authorization, move focus, confirm completion and preserve a safe rollback?
- Are queries, storage, caches, queues, notifications, search, analytics, logs, exports and background jobs isolated or explicitly aggregated under the same boundary?
- Are role and authority contextual, least-privileged and restated before consequence, with switching kept distinct from invitation, authentication, consent, delegation and elevation?
- Is continuity bound to exact context and revalidated after membership, role or policy change without leaking identity or behavioral state across contexts?
- Are invitation, guest, restriction, suspension, expiry, role change, leaving, removal and deprovisioning represented with prompt access removal, lawful handoff, export, audit, appeal and remedy?
