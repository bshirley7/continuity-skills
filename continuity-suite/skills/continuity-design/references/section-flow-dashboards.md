# Dashboards

## Generalized principles

- Organize the dashboard around current state, unresolved consequence, and the next meaningful decision, placing urgent eligibility, incident, risk, overdue, or failed-work signals above descriptive totals and secondary exploration.
- Prioritize exceptions through severity, impact, age, lifecycle state, affected scope, and ownership so counts lead to the work that needs attention instead of becoming isolated alarm numbers.
- Declare scope and freshness through date range, comparison period, timezone where material, data-as-of or last-updated time, and scan or refresh state; do not make the reader infer whether widgets share the same evidence window.
- Attach each headline measure to its comparison basis, target, denominator, composition, or trend so the value communicates direction and significance rather than a context-free snapshot.
- Connect summaries to inspectable records, owners, entities, or reports and keep the drill-down within the same scope so users can investigate and act without reconstructing the dashboard query.
- Use stable visual regions for state, exceptions, trends, evidence, and action, varying emphasis only when semantic priority or consequence differs rather than giving every metric an equal card.
- Distinguish healthy zero, empty result, missing data, stale data, excluded scope, not configured, and no recent activity; each state should explain what is known and the most useful next step.
- Keep filter scope legible and separate global dashboard controls from local widget controls, showing when a card uses a different period, segment, comparison, or denominator.
- For project and operational work, preserve the relationship among goal, status, owner, scope, milestone, recent activity, and due state instead of reducing health to completion percentage.
- Use generated narrative summaries only as an attention layer grounded in visible source measures, with refresh time and a route to the underlying work; never let generated interpretation replace status evidence.

## Variation levers

- Use a response queue or lifecycle board when unresolved items drive action, a trend-and-breakdown view when change diagnosis matters, and a goal-context view when alignment and ownership matter.
- Use one dominant exception block for a material blocker, a ranked list for several actionable issues, and a compact severity distribution for posture scanning.
- Use absolute values with composition for inventory or money, rates with denominators for conversion or risk, and deltas with explicit comparison periods for change.
- Use a global time and segment scope when widgets must remain comparable, and allow local overrides only when clearly labeled and operationally necessary.
- Use inline records for a short actionable exception set and a linked result table when the set is large, preserving count and filter context across the transition.
- Use freshness at dashboard level when all widgets update together and per-widget timestamps when sources or refresh schedules differ.
- Use an explicit healthy state when zero is meaningful, an instructional empty state when setup is incomplete, and an unavailable state when evidence cannot be trusted.
- Use generated summaries for orientation across many signals and deterministic alerts for consequences that require precise, auditable conditions.

## Tensions and tradeoffs

- A strong exception focus supports action while making healthy trends and strategic context less visible.
- Uniform cards support scanning while flattening the difference between primary outcomes, diagnostics, exceptions, and empty states.
- Dense operational context supports investigation while overwhelming users who need only the next decision.
- Global filters improve comparability while preventing local metrics from using the most meaningful scope or cadence.
- Frequent refresh improves immediacy while creating unstable numbers, unclear comparison windows, and false precision.
- Generated summaries reduce scanning effort while introducing interpretation that may not be traceable to a rule or source record.
- Severity colors accelerate recognition while losing meaning when every category uses saturated emphasis or color alone.
- Drill-down links preserve overview simplicity while forcing users to leave the context needed to understand the selected record.

## Failure modes

- The dashboard begins with greetings, generic recommendations, or equal KPI cards while urgent unresolved work appears lower or elsewhere.
- An alert count omits severity, impact, age, affected scope, lifecycle state, or owner.
- A measure appears without period, comparison basis, target, denominator, composition, or trend.
- Widgets use different evidence windows or filters without declaring the mismatch.
- A zero or blank chart does not distinguish healthy state, no results, missing source, stale evidence, or incomplete configuration.
- A summary metric has no route to the records, entities, owner, or report that explain it.
- A drill-down loses the dashboard's selected date, segment, comparison, or exception scope.
- Color, card size, and chart type vary without mapping to priority, consequence, or evidence type.
- Project health is reduced to completion while goal, owner, status, milestone, activity, and due state remain disconnected.
- A generated summary states an interpretation without visible source measures, refresh time, or inspectable supporting work.

## Anti-patterns

- Giving every metric the same card size and visual weight because the grid is easier to implement.
- Using a large total as the headline when a smaller failed, overdue, blocked, or high-severity subset determines the next action.
- Displaying a percentage change without the previous value, period, denominator, or business significance.
- Relying on an auto-refresh indicator without showing when the displayed evidence was actually updated.
- Treating an empty chart as self-explanatory.
- Using a doughnut or pie chart for status categories when a ranked actionable list is the real task.
- Making dashboard filters visually subtle even though they redefine every number on the page.
- Sending every card to a generic report rather than the scoped records behind the selected measure.
- Using ownerless progress and overdue counts as a substitute for a work queue.
- Presenting generated prose as a source of truth instead of a summary of visible deterministic evidence.

## Acceptance and review questions

- Does the dashboard lead with current state, unresolved consequence, and the next meaningful decision?
- Can each exception be judged through severity, impact, age, lifecycle state, affected scope, and ownership?
- Are date range, comparison period, timezone where material, data-as-of time, and refresh or scan state visible?
- Does every headline measure expose the comparison, target, denominator, composition, or trend needed to interpret it?
- Can users reach the scoped records, entities, owners, or reports behind each summary without reconstructing filters?
- Do visual regions and emphasis distinguish state, exceptions, trends, evidence, and action rather than flattening all metrics?
- Are healthy zero, empty result, missing data, stale data, excluded scope, not configured, and no recent activity visibly distinct?
- Are global and local filters clearly identified, including any widget that uses a different evidence window or denominator?
- Do project and operational views preserve goal, status, owner, scope, milestone, recent activity, and due state?
- Are generated summaries grounded in visible source measures with refresh time and a route to the underlying work?
