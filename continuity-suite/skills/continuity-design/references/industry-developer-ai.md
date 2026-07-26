# Developer and AI

## Generalized principles

- Define activation as a scoped verified first run: name project and environment, create the least-privileged credential, explain one-time secret handling, provide runnable code, expose expected response, and confirm telemetry.
- Keep credentials bound to project, environment, owner, permission, creation time, last use, rotation, revocation, and secure-storage guidance without redisplaying secrets.
- Make observability reconstructable from environment, version, time window, request or trace identity, model or service, latency, cost, usage, errors, tool calls, feedback, and raw drilldown.
- Separate availability, performance, quality, safety, cost, and user-feedback signals so one healthy aggregate cannot conceal failure in another dimension.
- Treat prompts and agent configuration as versioned artifacts binding model, instructions, variables, tools, parameters, datasets, evaluators, sharing scope, and deployment state.
- Require comparison and evaluation at the same dataset and scoring grain before changing a default, publishing a preset, or deploying a new model, prompt, tool, or agent version.
- Before agent or automation rollout, expose audience, trigger, tools, data scope, permissions, unresolved-case behavior, expected affected population, human review, go-live state, and rollback route.
- Keep draft, configured, tested, evaluated, approved, deployed, paused, failed, and retired states distinct, with accountable owner, run history, version lineage, and audit evidence.

## Variation levers

- Use guided first-call setup for new users and direct credential management for experts.
- Use dashboards for monitoring and trace or log detail for diagnosis.
- Use side-by-side evaluation for model changes and version history for restoration.
- Use presets for reusable bounded configuration and experiments for measured change.
- Use audience previews for customer-facing agents and repository or resource previews for developer automation.
- Use human approval for consequential tools and automatic execution only for bounded reversible work.

## Tensions and tradeoffs

- Fast credential setup accelerates activation while increasing secret-handling risk.
- Dense telemetry improves diagnosis while obscuring the primary failure.
- Aggregate quality metrics simplify review while hiding distribution and sample limits.
- Configurable prompts increase control while weakening reproducibility without versioning.
- Agent autonomy increases throughput while expanding permission and rollback risk.
- Rich audit history improves governance while increasing operational burden.

## Failure modes

- Onboarding ends at credential creation without a verified request.
- A secret is shown repeatedly or lacks rotation and revocation context.
- Monitoring omits environment, version, time, trace, cost, or raw evidence.
- One health score conflates quality, availability, safety, and cost.
- Prompt or agent changes overwrite configuration without version lineage.
- A default changes without matched evaluation evidence.
- Agent rollout hides audience, tools, permissions, fallback, or rollback.
- Deployment state lacks owner, run history, evaluation, and audit.

## Anti-patterns

- Copy this key and continue with no storage warning.
- Calling account creation developer activation.
- Showing a metric wall with no trace drilldown.
- Treating low latency as product quality.
- Editing production prompts in place.
- Promoting the best anecdotal output.
- Deploying an agent from a generic chat command.
- Listing automations without scope or approval state.

## Acceptance and review questions

- Does activation include scoped credential, secure handling, runnable request, expected response, and telemetry?
- Are credential owner, environment, permission, use, rotation, and revocation visible?
- Can monitoring be traced by environment, version, time, request, model, latency, cost, errors, tools, and feedback?
- Are availability, performance, quality, safety, cost, and feedback distinct?
- Are prompts and agents versioned with model, instructions, variables, tools, data, evaluator, and sharing scope?
- Are default and deployment changes supported by matched comparison evidence?
- Does rollout expose audience, trigger, tools, permissions, fallback, review, and rollback?
- Are lifecycle state, owner, run history, version lineage, and audit evidence complete?
