# Data-dense

## Generalized principles

- Establish shared scope before detail by making object, owner, project, environment, scenario, time range, live state, and filters visible and persistent across summaries, charts, and rows.
- Layer dense work from current health or outcome to trends, exceptions, contributing dimensions, and raw evidence so users can scan first and drill down without losing context.
- Make tables decision-ready through stable row identity, a bounded set of meaningful columns, visible units and state, sorting and filtering, user-controlled columns, and persistent selection feedback.
- Separate inputs, assumptions, calculations, outputs, and comparisons visually and semantically; never rely on position or color alone to communicate data role.
- Keep filters and query construction inspectable, composable, removable, and saveable when they define the result; show their effect in counts, charts, or samples.
- Use compact density for comparison, not compression alone: preserve labels, definitions, units, timestamps, severity, and consequence wherever a number or status can drive action.

## Variation levers

- Use overview cards for health and tables for action queues.
- Use histograms for distribution, line charts for change, and tables for exact evidence.
- Use saved views for recurring work and ad hoc query tokens for investigation.
- Use fixed columns for identity and horizontal scrolling for time or secondary dimensions.
- Use dark themes for sustained monitoring only when semantic contrast remains strong.

## Tensions and tradeoffs

- More visible dimensions improve comparison while increasing scan cost.
- Persistent scope prevents mistakes while consuming header space.
- User-configurable columns support experts while weakening shared defaults.
- Color accelerates exception detection while creating accessibility and overencoding risk.
- Live telemetry improves awareness while destabilizing reading and selection.

## Failure modes

- Charts and rows use different hidden scopes.
- Tables expose many fields without decision hierarchy.
- Numbers omit units, time windows, definitions, or denominators.
- Filters are applied but not visible or removable.
- Bulk actions lose selection count or scope.
- Inputs and calculated outputs are visually indistinguishable.
- Zero states remove the operational dimensions needed during incidents.

## Anti-patterns

- Dashboard mosaics with no question hierarchy.
- Truncated labels as the default density strategy.
- Color-only severity.
- Hidden filters.
- Unlabeled sparklines.
- Bulk action without persistent selection.
- Spreadsheet grids with ambiguous units.
- Live updates that reorder rows during inspection.

## Acceptance and review questions

- Are scope, owner, environment, scenario, time, live state, and filters explicit?
- Can users move from outcome to trend, exception, dimension, and raw evidence?
- Are row identity, columns, units, state, sorting, filtering, and selection clear?
- Are inputs, assumptions, calculations, outputs, and comparisons distinct?
- Can filters be inspected, changed, saved, and tied to visible results?
- Does every actionable value retain label, definition, unit, timestamp, severity, and consequence?
