# Adaptive layout

## Generalized principles

- Adapt by semantic priority: preserve current scope, selected object, consequential state, primary action, and safe return first; collapse, move, summarize, or defer secondary navigation, inspectors, metadata, and utilities.
- When simultaneous panes become a compact sequence, preserve selection, title, parent scope, filters, unsaved state, scroll position, and a predictable back path so layout change does not become context loss.
- Define explicit region behavior across width classes, including minimum viable size, reflow order, collapse trigger, replacement control, overlay or drawer use, persistence, and restoration.
- For analytical and operational surfaces, keep the governing question, active filters, key result, exceptions, comparison basis, and drill-down path together even when charts and tables must summarize or serialize.
- Use progressive disclosure to transform breadth into depth on small screens: lead with status and next action, then reveal records, comparison, explanation, and configuration without hiding consequential information.
- Test adaptation with real content and state combinations—including long labels, many panes, wide tables, active filters, keyboard or input surfaces, open menus, errors, loading, selection, and unsaved work—rather than viewport dimensions alone.

## Variation levers

- Use persistent panes when comparison or cross-reference is the primary task.
- Use drawers or overlays for temporary context that should not displace the active object.
- Use list-detail serialization when one object can be acted on independently.
- Summarize charts and tables only when the comparison basis and drill-down remain visible.
- Promote operational exceptions above aggregate reporting on constrained displays.

## Tensions and tradeoffs

- Persistent context consumes working space.
- Serialization improves focus while slowing comparison.
- Dense wide layouts support experts while increasing scan and input burden.
- Drawers preserve place while obscuring underlying content.
- Summary cards improve compactness while hiding variance and denominator context.

## Failure modes

- Every region shrinks proportionally.
- Collapsed panes have no visible replacement control.
- Selection or filters reset during reflow.
- A mobile view loses parent scope or return path.
- Charts collapse without retaining comparison basis or drill-down.
- Primary and secondary actions reorder unpredictably.
- Breakpoint tests omit realistic content and transient states.

## Anti-patterns

- Desktop layout scaled down.
- Breakpoint-only design specification.
- Hamburger menu as a universal adaptation.
- Horizontal scrolling for every dense surface.
- Modal replacement for persistent context.
- Summary metric without baseline.
- Hidden active filters.
- Different navigation vocabulary by device.
- State reset on orientation or width change.

## Acceptance and review questions

- Does adaptation preserve scope, selection, consequential state, primary action, and safe return?
- Are pane collapse, replacement, persistence, and restoration explicitly defined?
- Do serialized layouts preserve filters, unsaved state, scroll position, and parent context?
- Do compact analytics retain question, filters, key result, comparison basis, exceptions, and drill-down?
- Is consequential information protected from progressive disclosure?
- Are realistic content, input, error, loading, selection, and unsaved states tested across layouts?
- Is guidance based on visible adaptive behavior rather than claiming unobserved implementation logic?
