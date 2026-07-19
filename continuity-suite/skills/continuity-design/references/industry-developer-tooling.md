# Developer tooling

## Generalized principles

- Keep source and runtime lineage continuous: repository, branch or tag, immutable revision, author and review state, configuration fingerprint, build or artifact identity, target environment, deployment, active version, and rollback ancestor.
- Make environment and scope persistent across project, workspace, account, region, service, resource, branch, preview, staging, and production contexts; distinguish navigation context, read source, mutation target, and runtime destination.
- Model runs with explicit lifecycle and causality: trigger, initiator, inputs, revision, configuration, dependencies, queue, steps, current state, duration, logs, artifacts, output, failure cause, cancellation, retry semantics, and resulting runtime state.
- Treat logs, metrics, traces, errors, profiles, deploy events, and user reports as distinct evidence types connected by time, environment, release, service, request or correlation identifier, region, and query window; preserve filtering and sampling context.
- Separate completed, deployed, ready, healthy, verified, promoted, and customer-visible states; show rollout coverage, checks, warnings, regional or instance variance, active traffic, and the evidence required before promotion or rollback.
- Preview consequential developer actions with exact source and target, environment, configuration diff, affected services and dependencies, credentials or data touched, expected downtime or behavior, authorization, verification, partial failure, rollback, and audit record.

## Variation levers

- Use code-first, pipeline-first, service-first, or incident-first navigation according to the primary operating model while preserving cross-links among all four.
- Use compact status summaries for scanning and expandable evidence for diagnosis; never hide environment, revision, active state, or failure cause.
- Stream live output for active runs while preserving a stable retained record with explicit truncation and retention.
- Offer rerun, retry-failed, rebuild, redeploy, promote, rollback, and revert as distinct operations with explicit input reuse.
- Require stronger preview and approval as environment criticality, data access, privilege, cost, or blast radius increases.

## Tensions and tradeoffs

- Dense operational context accelerates experts while overwhelming occasional contributors.
- Live output improves feedback while changing beneath inspection and complicating stable references.
- Automatic deployment shortens feedback loops while obscuring authority and production consequence.
- One project abstraction simplifies navigation while flattening repositories, services, resources, and environments.
- Secret masking reduces exposure while making identity, source, and drift harder to inspect.
- Aggressive log retention supports diagnosis while increasing cost and sensitive-data risk.

## Failure modes

- The active environment or mutation target is ambiguous.
- A deployment cannot be traced to immutable source and configuration.
- Success conflates completion, health, verification, and promotion.
- Retry semantics do not state which inputs or artifacts are reused.
- Live logs lack time zone, source, retention, or query context.
- An error lacks affected release, environment, frequency, or owner.
- A configuration change hides consumers or redeploy requirements.
- Rollback target and retained data are not named.
- Partial rollout or regional failure appears globally successful.

## Anti-patterns

- Latest as a version.
- Production inferred from color.
- Deploy without source revision.
- Retry means try something unspecified.
- Green means healthy everywhere.
- Logs without query context.
- Secret value as configuration identity.
- Rollback to previous.
- Build success equals release success.
- One generic run status.

## Acceptance and review questions

- Can every runtime state be traced through repository, revision, configuration, artifact, environment, deployment, active version, and rollback ancestor?
- Are navigation context, read source, mutation target, and runtime destination explicit across all scopes?
- Does each run expose trigger, initiator, inputs, revision, configuration, dependencies, steps, state, logs, artifacts, outcome, retry, and resulting runtime?
- Are logs, metrics, traces, errors, profiles, deploy events, and reports distinct but correlated with preserved query context?
- Are completion, deployment, readiness, health, verification, promotion, and customer visibility distinct?
- Do consequential actions preview exact source, target, diff, dependencies, credentials or data, downtime, authority, verification, failure, rollback, and audit?
- Are partial rollouts, regional variance, warnings, and retained state visible?
