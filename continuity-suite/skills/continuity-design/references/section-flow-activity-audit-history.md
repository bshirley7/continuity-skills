# Activity, audit, and version history

## Generalized principles

- Choose the history model before choosing the layout: collaborative activity should optimize orientation and follow-up, administrative audit logs should optimize exact evidence and filtering, and object version history should optimize comparison and recovery.
- Give every event a legible evidence sentence built from actor or agent, action, affected object, scope or location, outcome, and exact time; expose source, device, network, or system attributes in progressive detail when the domain requires them.
- Keep history connected to present context through stable object identity, deep links, previews, current-state labels, and explicit before-and-after or selected-revision comparison; never imply that an event log is itself the current state.
- Support investigation with time range, actor, action or event type, object, scope, and outcome filters plus search, durable detail views, and export where evidence must leave the interface; preserve the active query when drilling in and returning.
- Treat restore, revert, or rollback as a consequential action distinct from browsing: identify the selected revision, summarize what will change, disclose downstream effects and recovery, require confirmation proportional to risk, and record the new event.

## Variation levers

- Use a narrative stream for team awareness, a dense table for high-volume administration, and a split revision-list plus preview or comparison canvas for object recovery.
- Group low-risk repetitive events for comprehension while preserving expansion to exact raw events, counts, actors, and timestamps.
- Show relative time for casual orientation but pair it with exact date, time, and timezone in detail, export, or regulated contexts.
- Increase evidence density, retention cues, export, and source attributes as security, compliance, financial, health, or privileged-administration risk rises.

## Tensions and tradeoffs

- Readable event summaries improve orientation while potentially hiding evidence needed for investigation.
- Dense audit tables improve scanning and exportability while weakening narrative comprehension.
- Grouping repetitive activity reduces noise while risking concealed anomalies or misleading counts.
- Easy restore reduces recovery friction while making consequential rollback feel deceptively routine.
- Relative timestamps are friendly for recent activity while becoming ambiguous across timezones, long retention windows, and exported evidence.

## Failure modes

- A single feed is expected to serve social awareness, forensic audit, and version recovery equally well.
- Events omit actor, object, outcome, exact time, source, or system-agent identity.
- History shows that something changed but offers no link, preview, prior value, selected revision, or current-state distinction.
- Filters reset after inspecting an event, forcing investigators to reconstruct scope repeatedly.
- Grouped activity cannot be expanded to exact underlying events.
- Restore acts immediately or without revision identity, change preview, downstream impact, recovery, and a recorded follow-up event.

## Anti-patterns

- One feed for every history job.
- Something changed.
- Relative time as evidence.
- Current state by implication.
- Unexpandable event bundles.
- Filter amnesia.
- Browse-to-rollback.

## Acceptance and review questions

- Is the surface clearly optimized for collaborative orientation, administrative evidence, or object comparison and recovery?
- Can each event answer who or what acted, what happened, to which object and scope, with what outcome, and exactly when?
- Are system agents, source, device, network, timezone, and other risk-relevant attributes available where needed?
- Can people move from history to the related object, preview or compare changes, and distinguish the selected event or revision from current state?
- Do filters cover time, actor, event type, object, scope, and outcome, and do they survive drill-in and return?
- Can grouped activity expand to exact events and can evidence be exported when required?
- Does restore or rollback identify the revision, preview consequences, disclose recovery, require proportional confirmation, and create a new history event?
