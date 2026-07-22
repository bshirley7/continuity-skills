# Analytical exploration

## Generalized principles

- Begin with an explicit analytical contract: state the question, decision or hypothesis, population or object scope, measure definition, dimensions, time and timezone basis, comparison or baseline, denominator, source, freshness, exclusions, and whether the work is exploratory, monitoring, or confirmatory.
- Make the query continuously inspectable and reversible through selected measures, dimensions, event or cohort definitions, filters with operators and values, segment logic, date and comparison ranges, grouping, sort, missing-value treatment, result count, and reset or prior-state recovery.
- Coordinate summary, chart, path, and record evidence through one scope and selection model: use visualization for pattern, table or detail for exact values, direct or legend labels for series, drill-down for contributing records, and a predictable return path that preserves the analytical state.
- Keep interpretation proportional to evidence by exposing numerator and denominator, absolute and relative values, baseline, sample or coverage, missing and suppressed data, uncertainty or estimation, source changes, freshness, and noncomparable periods; distinguish observed pattern, generated summary, hypothesis, and validated conclusion.
- Treat a saved analysis as a reproducible governed object with name, owner, purpose, query definition, metric versions, source and freshness, visualization and table state, annotations, access, last run, schedule, and revision history; exports must retain scope, definitions, provenance, generated time, and material limitations.

## Variation levers

- Use guided questions and defined metrics for broad audiences, and composable measures, dimensions, expressions, and query detail for expert analysts.
- Use trends for temporal change, distributions for variation, funnels for ordered conversion, paths for sequence, cohorts for shared start conditions, and tables for exact evidence.
- Increase uncertainty, sample, provenance, privacy, and methodological detail as estimation, consequence, segmentation, or external sharing rises.
- Save a personal view for recurring local exploration and a governed shared report when definitions, schedules, access, or decisions must remain consistent.

## Tensions and tradeoffs

- Flexible exploration supports discovery while increasing selection bias, multiple comparisons, and irreproducible findings.
- Interactive charts accelerate pattern recognition while hiding exact values, missing data, and inaccessible interactions.
- Automatic summaries reduce scan effort while overstating causal or statistical conclusions.
- Saved views preserve work while becoming stale when source schemas and metric definitions change.
- Exports increase portability while severing live freshness, filters, definitions, access controls, and correction history.

## Failure modes

- A chart appears without a question, measure definition, population, period, denominator, source, or freshness.
- Filters are active but hidden, ambiguous, non-removable, or applied inconsistently across panels.
- Drill-down changes scope or loses date range, comparison, selection, and return context.
- Percent change appears without prior value, absolute magnitude, denominator, and comparable period.
- A generated insight presents correlation, forecast, or selected segment as a validated causal conclusion.
- A saved report or export omits query definition, metric version, provenance, generated time, or limitations.

## Anti-patterns

- Chart before question.
- Hidden query.
- Drill-down amnesia.
- Percent without magnitude.
- Average hides distribution.
- Exploration becomes proof.
- Saved view, stale definition.
- Export without provenance.

## Acceptance and review questions

- Does the analysis identify question, use, scope, measure, dimensions, time, comparison, denominator, source, freshness, exclusions, and analytical mode?
- Are measures, filters, segment logic, dates, grouping, missing-value treatment, count, and reset continuously inspectable?
- Do summaries, charts, paths, tables, and records share scope, selection, labels, drill-down, and return state?
- Are absolute and relative values, sample, coverage, uncertainty, missingness, source changes, and comparability visible where material?
- Are observation, generated interpretation, hypothesis, forecast, and validated conclusion clearly distinct?
- Do saved analyses and exports preserve query, definitions, provenance, time, limitations, ownership, access, and revision?
