# Attention and interruption

## Generalized principles

- Treat attention as a user cost: choose interruption level from consequence, required response window, current task, reversibility, and the cost of missing the event, never from the sender's desire for engagement.
- Use the least disruptive channel that still makes the state perceivable: prefer contextual status near the affected work, then persistent banners or inboxes, reserving focus-taking alerts and modal interruption for rare events requiring immediate action.
- Give people durable control to postpone, suppress, group, schedule, digest, mute, or change delivery by meaningful event category and account or workspace scope, while preserving genuinely emergency communication.
- Make status changes accessible without unnecessary focus movement: expose them programmatically, preserve sufficient reading and action time, avoid rapid disappearance and repeated announcements, and never rely on color, sound, motion, badge, or one channel alone.
- Write notifications for recognition and action with concise event, object, consequence, time relevance, and next step; avoid sensitive preview content, duplicate delivery, vague urgency, and actions that merely reopen the product without restoring context.

## Method

- Classify the event by user consequence, response window, reversibility, affected scope, privacy sensitivity, and cost of delayed or missed attention.
- Choose contextual status, inline message, toast, banner, inbox entry, external notification, alert, or modal according to the minimum interruption needed.
- Specify event category, delivery channels, grouping key, persistence, expiry, deduplication, escalation, quiet-period behavior, and user controls.
- Write the message around event, object, consequence, current state, time relevance, and the smallest useful next action, with a safe generic preview when privacy is uncertain.
- Test visual, keyboard, screen-reader, reduced-distraction, background, shared-screen, delayed-reading, duplicate-event, and high-volume scenarios.
- Measure comprehension, successful follow-up, false urgency, dismissal, muting, opt-out, repeated exposure, missed critical events, and interruption burden, not click-through alone.

## Ethical safeguards

- Do not label marketing, engagement, or routine updates as time-sensitive or critical.
- Do not make promotional delivery a condition of receiving operational, safety, security, or account notifications.
- Do not use unread counts, repeated alerts, or escalating visual pressure to manufacture obligation.
- Do not expose sensitive personal, health, financial, employment, or security information in previews by default.
- Do not override quiet periods or suppression except for a narrowly defined and honestly classified emergency.
- Do not optimize notification clicks without monitoring opt-out, muting, regret, task disruption, and missed critical-event rates.

## Variation levers

- Increase interruption only as consequence and response urgency rise, and reduce it as reversibility, redundancy, or passive awareness increase.
- Use immediate delivery for direct communication and time-bounded operational risk; use digests or in-product inboxes for accumulated low-urgency updates.
- Prefer persistent, user-dismissed messages when comprehension or action is required and transient status when the result is routine, low risk, and recoverable.
- Reduce preview specificity as device sharing, lock-screen exposure, workplace sensitivity, or personal-data risk increases.

## Tensions and tradeoffs

- Immediate visibility reduces missed events while fragmenting attention and assistive-technology output.
- Fine-grained controls support autonomy while imposing configuration and maintenance burden.
- Persistent messages preserve access while competing with current content and becoming habituated.
- Aggregation reduces repetition while delaying or obscuring exceptional events.
- Rich previews improve recognition while increasing privacy exposure.

## Failure modes

- Urgency is derived from business value rather than user consequence and response window.
- A focus-taking alert communicates information that could have remained contextual and nonblocking.
- The only control is a global opt-out, or operational and promotional messages are bundled together.
- Transient messages disappear before they can be read or acted on.
- Status changes are visual-only, color-only, sound-only, motion-only, or badge-only.
- Duplicate notifications repeat the same event across channels without state synchronization.
- Success is measured by opens or clicks while muting, opt-out, regret, interruption, and missed critical events are ignored.

## Anti-patterns

- Sender-defined urgency.
- Modal FYI.
- Promotion as operational notice.
- Blink-and-miss status.
- Badge-only importance.
- Cross-channel echo.
- Clicks as notification quality.

## Acceptance and review questions

- What user consequence, response window, reversibility, and missed-event cost justify this interruption level?
- Could the state remain contextual, persistent, or inbox-based instead of taking focus?
- Can people postpone, suppress, group, schedule, digest, mute, and control delivery by meaningful category and scope?
- Are operational, safety, security, direct-communication, and promotional messages separated?
- Can every message be perceived without relying on color, sound, motion, badge, or one delivery channel alone?
- Does the message persist long enough, avoid duplicate announcements, restore context, and protect sensitive preview content?
- Are comprehension, follow-up, false urgency, muting, opt-out, regret, interruption burden, and missed critical events measured?
