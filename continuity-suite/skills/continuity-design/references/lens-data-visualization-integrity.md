# Data visualization design and integrity

## Generalized principles

- Define the analytical contract before choosing a chart: name the question, decision, population, measure, unit, denominator, time window, comparison, aggregation, exclusions, freshness, source, uncertainty, and route to underlying records; do not let a visually compelling chart create a question or conclusion after the fact.
- Choose visual form and encoding by task and data relationship: use position and aligned length for precise comparison, preserve time order and interval, distinguish part-to-whole from change and distribution, limit simultaneous encodings, and prefer a labeled value, table, or small multiple when a chart adds interpretation cost without analytical benefit.
- Keep scope and comparison visible with the result: show active filters, segmentation, period, baseline, target or threshold, series identity, units, missing data, and material definition changes; bind summary values to the visualization and detail that explain them.
- Preserve evidence and drill-down: connect every aggregate, anomaly, alert, or recommendation to inspectable categories, records, events, accounts, evaluations, or measurements; carry filters and selected context into detail and make export or sharing retain the governing definitions.
- Represent uncertainty, absence, and operational state honestly: distinguish zero from missing, delayed, estimated, partial, forecast, threshold, normal range, incident, recovery, and stale data; avoid fabricated continuity, unsupported precision, diagnostic implication, or confident styling that exceeds the evidence.
- Make visualization accessible and resilient through direct labels, redundant shape or pattern, sufficient contrast, keyboard and assistive exploration, meaningful text summaries, data tables where useful, zoom and localization support, and responsive transformations that preserve the question and comparison rather than merely shrinking marks.
- Constrain brand expression to preserve evidence: use palette, typography, annotation, spacing, and restrained motion consistently, but do not distort scales, suppress baselines, overemphasize favorable values, use decorative area as quantity, or assign semantic colors inconsistently across charts and states.

## Variation levers

- Use compact summaries with immediate drill-down for frequent operational monitoring.
- Use richer annotation and explanatory text for infrequent or consequential interpretation.
- Prefer tables for exact lookup and charts for pattern, relationship, distribution, or change.
- Use small multiples when shared scales make group comparison more reliable than many overlapping series.
- Increase uncertainty and provenance detail as consequence, model dependence, or measurement ambiguity increases.
- Reduce decorative encoding and interaction when exported, printed, localized, or consumed through assistive technology.

## Tensions and tradeoffs

- More context improves validity while increasing cognitive and visual load.
- Summary metrics accelerate scanning while hiding distribution, denominator, and composition.
- Interactive exploration supports discovery while making conclusions difficult to reproduce or share.
- Dense dashboards preserve breadth while weakening the governing question.
- Brand styling improves cohesion while biasing salience or reducing semantic consistency.
- Responsive simplification improves fit while removing comparison and uncertainty context.

## Failure modes

- A chart is selected before the question, measure, denominator, and comparison are defined.
- A headline metric has no visible baseline, period, population, or route to detail.
- Filters and segmentation are hidden after results render.
- Zero, missing, stale, estimated, forecast, and partial data look equivalent.
- Color alone identifies series, severity, direction, or threshold.
- A truncated or inconsistent scale exaggerates favorable change.
- Exported or shared views omit definitions and active scope.
- Mobile transformation removes the comparison basis or drill-down.
- Health, finance, or model metrics imply certainty beyond their evidence.

## Anti-patterns

- Chart before question.
- Dashboard of available metrics.
- Headline number without denominator.
- Invisible filter state.
- Rainbow series encoding.
- Zero equals missing.
- Decorative area as quantity.
- Responsive chart squeeze.
- Export without analytical context.
- Polish as certainty.

## Acceptance and review questions

- Are question, decision, population, measure, unit, denominator, period, comparison, exclusions, freshness, source, uncertainty, and drill-down explicit?
- Does the selected visual form match the actual comparison, change, distribution, relationship, composition, or lookup task?
- Are filters, segmentation, baseline, target, series identity, missing data, and definition changes visible with the result?
- Can every aggregate, anomaly, alert, or recommendation be traced to inspectable records or measurements without losing context?
- Are zero, missing, delayed, estimated, partial, forecast, stale, threshold, incident, and recovery states distinct?
- Are direct labels, redundant encoding, contrast, keyboard access, summaries, tables, zoom, localization, and responsive transformation adequate?
- Does brand treatment preserve scale integrity, semantic color, evidence hierarchy, and uncertainty?
