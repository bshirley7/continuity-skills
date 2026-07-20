# Notification centers and inbox triage

## Generalized principles

- Model notification state separately from work state: unread, read, seen, dismissed, archived, snoozed, assigned, resolved, and completed must not collapse into one badge or clearing action.
- Make every notification answer why the person received it, who or what caused it, what object and workspace it concerns, what changed, when it happened, whether action is required, and where to inspect or act.
- Design the inbox for triage by preserving queue context while opening event detail and related work; support meaningful categories, filters, bulk clearing, and return position without treating chronological order as priority.
- Give people durable control over event category, scope, channel, urgency, frequency, digest, quiet time, preview privacy, and complete suppression, and show whether a setting is personal, workspace-derived, or system-controlled.
- Use grouping and aggregation to reduce repetition only when the summary preserves source, count, time span, affected objects, exceptional events, and a route to the underlying items.

## Variation levers

- Use a compact panel for occasional awareness and a persistent split-view inbox when notification volume or required follow-up is substantial.
- Prioritize mentions, assignments, approvals, failures, security events, deadlines, and direct communication differently from passive updates and promotional content.
- Offer immediate delivery for time-sensitive events and digests or passive in-product delivery for lower-urgency awareness.
- Increase privacy controls and reduce preview detail when notifications can appear on shared screens, email, mobile devices, or external channels.

## Tensions and tradeoffs

- Mark-all-read reduces attention debt while potentially hiding items that still require action.
- Chronological ordering supports recency while obscuring consequence and responsibility.
- Aggregation reduces noise while concealing exceptional events or distinct affected objects.
- Fine-grained preferences improve control while becoming difficult to understand and maintain.
- Rich previews accelerate triage while increasing exposure of sensitive content.

## Failure modes

- Clearing unread state implies that underlying work is resolved.
- A notification omits receipt rationale, affected object, workspace scope, action expectation, or deep link.
- Opening an item loses the queue, filters, or return position.
- All events share one urgency, channel, frequency, or global toggle.
- Grouped items cannot be expanded or hide failures and direct mentions.
- Notification preferences do not identify inherited, personal, workspace, or operating-system scope.

## Anti-patterns

- Unread equals unfinished.
- Chronology as priority.
- Mystery notification.
- Inbox dead end.
- One toggle for everything.
- Aggregation without evidence.
- Private data in the preview.

## Acceptance and review questions

- Are unread, read, dismissed, snoozed, assigned, resolved, and completed represented as distinct states?
- Does every notification explain receipt rationale, actor or source, event, object, scope, time, action expectation, and destination?
- Can people inspect detail and related work without losing queue context, filters, or return position?
- Are urgency and ordering based on consequence and responsibility rather than recency alone?
- Can people control event category, scope, channel, frequency, digest, quiet time, preview privacy, and suppression?
- Are personal, workspace-derived, inherited, and operating-system settings clearly distinguished?
- Can grouped notifications expand to exact events, exceptions, affected objects, and underlying actions?
