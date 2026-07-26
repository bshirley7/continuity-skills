# Geospatial operations

## Generalized principles

- Keep spatial state explicit through scale, orientation, extent, current location, selected object, active layer, legend, filters, and a reliable reset or recenter path.
- Bind every time-varying mark to observation, update, forecast, or validity time and distinguish current, predicted, delayed, stale, and unknown states.
- Preserve provenance and uncertainty through source, update cadence, units, confidence or forecast status, coverage limits, and non-color cues beside the mapped decision.
- Synchronize selection across map mark, layer, list, route, alert, and detail while preserving the overview and a reversible return path.
- Treat alerts as spatial-temporal decisions with severity, affected area, valid time, source, consequence, and recommended action—not merely colored polygons or markers.
- For route and location commitments, expose origin, destination or selected point, alternatives, distance, duration, constraints, and correction before confirmation.

## Variation levers

- Use clustering at overview scales and stable object detail after selection.
- Separate operational layers from contextual basemaps.
- Use timelines when marks change materially over time.
- Use list-map coordination for dense or inaccessible spatial populations.
- Use alert prioritization that combines severity, proximity, time, and user relevance.

## Tensions and tradeoffs

- More layers increase context while obscuring priority.
- Clustering reduces clutter while hiding individual exceptions.
- Live updates improve awareness while creating instability.
- Animation explains time while making exact comparison harder.
- Simplified basemaps improve focus while removing orientation landmarks.

## Failure modes

- Scale, time, source, or units are absent.
- Color is the only alert or layer distinction.
- Selection is lost when detail opens.
- Stale position looks current.
- Filters change the population without visible scope.
- Route alternatives lack a consistent comparison baseline.
- Recenter unexpectedly changes zoom or task context.

## Anti-patterns

- Unlabeled heatmap.
- Timeless radar animation.
- Marker soup.
- Alert color with no severity text.
- Map-only data access.
- Hidden active layers.
- Current-location dot with no freshness.
- Selection that vanishes on zoom.
- Route line without origin or destination.
- Provenance buried outside the decision surface.

## Acceptance and review questions

- Are scale, orientation, extent, selection, layers, legend, filters, and recentering explicit?
- Do time-varying marks identify observation, update, forecast, validity, staleness, and unknown states?
- Are source, units, cadence, uncertainty, and coverage limits visible?
- Does selection remain synchronized across map, list, layer, alert, route, and detail?
- Do alerts expose severity, area, time, source, consequence, and action?
- Do route or location commitments expose points, alternatives, metrics, constraints, and correction?
- Is guidance limited to visible geospatial behavior rather than claiming hidden data quality?
