# Search, filtering, and discovery

## Generalized principles

- Keep the search contract visible: identify scope, searchable object types, query, active filters, sort, result count, freshness or source limits, and whether matching is exact, semantic, personalized, or permission-bounded.
- Make each result provide enough information scent to predict the destination through title, type, source, hierarchy, matched context, relevant attributes, state, date, provenance, and available action without opening every item.
- Treat filters as an inspectable query model: align facets with result attributes, show active criteria and counts, preserve query and sort, support individual and clear-all removal, and prevent hidden or impossible combinations.
- Preserve discovery state across view changes, result inspection, back navigation, and downstream action, including query, filters, sort, scroll or selection position, and the reason a result was shown.
- Design zero and weak results as diagnosis and recovery: retain the query, explain scope and constraints, identify spelling or interpretation changes, expose removable filters, and offer broader categories, alternate terms, or another route without fabricating matches.

## Variation levers

- Use direct suggestions and compact results for known-item lookup; use facets, comparison evidence, saved state, and multiple result views for exploratory discovery.
- Apply filters immediately for fast local data and batch them with explicit apply, pending state, and counts when queries are costly or criteria interdependent.
- Increase provenance, permission, freshness, and matching explanations for enterprise, regulated, AI-mediated, or heterogeneous-source search.
- Prioritize visual attributes in commerce and media, structural and ownership attributes in work systems, and source and method attributes in research or AI search.

## Tensions and tradeoffs

- More result evidence improves prediction while reducing scan density.
- Autocomplete reduces query effort while steering language and potentially narrowing exploration.
- Many facets increase precision while making the query model harder to understand.
- Personalization can improve relevance while obscuring why results differ across people.
- Semantic broadening improves recall while making exact intent and omissions less predictable.

## Failure modes

- Search scope, object types, permission boundaries, or matching behavior are implicit.
- Results show titles without matched context, source, hierarchy, state, or differentiating attributes.
- Applied filters are hidden inside closed controls or cannot be removed individually.
- Opening a result destroys query, filters, sort, view, or return position.
- A zero-result page erases the query, blames the user, or offers only a generic reset.
- AI or semantic search presents confident relevance without provenance, interpretation, or uncertainty.

## Anti-patterns

- Search everywhere, scope nowhere.
- Title-only results.
- Invisible query model.
- Back means restart.
- Zero results, zero help.
- Relevance without a reason.
- Autocomplete as destiny.

## Acceptance and review questions

- Are scope, object types, query, filters, sort, count, source limits, and matching behavior visible?
- Can users predict each destination from matched context, type, source, hierarchy, attributes, state, and provenance?
- Do facets correspond to result attributes and expose active criteria, counts, removal, and clear-all?
- Are query, filters, sort, view, selection, and return position preserved across inspection and action?
- Do zero and weak results diagnose scope and constraints while offering honest reformulation and broadening?
- Are semantic, personalized, permission-bounded, or AI-mediated results explained with appropriate uncertainty?
