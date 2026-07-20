# Information foraging and findability

## Generalized principles

- Support both known-item lookup and exploratory foraging: preserve a simple direct query path while offering visible scopes, categories, facets, related concepts, and alternate routes for people who cannot name the destination precisely.
- Strengthen information scent by making labels, result summaries, matched terms, hierarchy, source, attributes, and destination cues correspond to the language and evidence people use to judge relevance.
- Externalize the evolving query model through retained terms, result counts, applied-filter overviews, facet values, sort, scope, and individual or global removal; do not require people to remember why the set changed.
- Make query assistance accessible and noncoercive: label the search purpose, preserve keyboard and assistive-technology control, distinguish suggestions from entered text, allow arbitrary input where valid, and never silently replace intent.
- Treat poor results as system feedback rather than user failure: retain and explain the interpreted query and scope, support spelling and terminology variation, reveal constraints, and provide reversible broadening or alternate navigation.

## Method

- Identify known-item, category, attribute, problem, exploratory, and comparison search intents plus the vocabulary users actually bring.
- Define searchable scope, object types, permissions, freshness, matching logic, ranking inputs, source coverage, and uncertainty before styling results.
- Design query entry, suggestions, results, facets, sorting, empty and weak results, inspection, back navigation, and saved or shared search as one stateful journey.
- Annotate keyboard, screen-reader, voice-input, focus, announcement, touch-target, localization, and reduced-cognitive-load behavior.
- Test misspellings, synonyms, ambiguous terms, long queries, mixed object types, overconstrained filters, no permission, stale content, slow results, and return from detail.
- Measure successful finding, reformulation, filter correction, backtracking, abandonment, result confidence, false-positive cost, and time to recover, not query submission alone.

## Ethical safeguards

- Do not disguise sponsored, promoted, or organizationally preferred results as relevance.
- Do not silently broaden, personalize, rewrite, or omit query terms without an inspectable explanation and correction path.
- Do not expose inaccessible or unauthorized result existence through counts, suggestions, snippets, or facets.
- Do not use autocomplete to steer toward higher-value choices while suppressing valid user language.
- Do not claim completeness when source coverage, indexing, permissions, freshness, or retrieval limits are material.
- Do not present AI-generated answers as a substitute for source inspection when consequence or uncertainty is high.

## Variation levers

- Favor speed and direct matching for known-item retrieval; favor breadth, facets, comparison, and saved state for exploratory work.
- Increase matching and provenance explanation as semantic inference, personalization, heterogeneity, or consequence rises.
- Use immediate filtering for fast local sets and explicit apply for costly, remote, or interdependent queries.
- Tune result density to the evidence needed for selection rather than maximizing items per viewport.

## Tensions and tradeoffs

- More guidance reduces query effort while increasing steering and visual complexity.
- Broader recall helps exploration while increasing false positives and evaluation cost.
- Dense results speed scanning while weakening information scent and accessibility.
- Personalization can improve ranking while reducing comparability and explainability.
- Persistent state supports orientation while making it harder to recognize stale filters or scope.

## Failure modes

- Search assumes users know the product taxonomy or exact object name.
- Suggestions are inaccessible, replace intent, or cannot be controlled by keyboard.
- Result relevance cannot be judged without opening each destination.
- Applied filters, scope, sort, or query interpretation are hidden.
- Zero results offer blame, generic advice, or indiscriminate broadening.
- Ranking, personalization, source coverage, permissions, and uncertainty are materially opaque.

## Anti-patterns

- Recall the taxonomy.
- Suggestion takeover.
- Click to discover relevance.
- Invisible query state.
- No results, try again.
- Opaque relevance.
- Answer without sources.

## Acceptance and review questions

- Does the design support both direct lookup and exploratory discovery without requiring exact taxonomy?
- Can people judge relevance from matched context, source, hierarchy, attributes, and destination cues?
- Are terms, scope, counts, filters, sort, and query interpretation continuously inspectable and reversible?
- Are suggestions labeled, keyboard-operable, assistive-technology compatible, and subordinate to user intent?
- Do weak and zero results explain constraints and offer honest, reversible recovery?
- Are promotion, personalization, semantic rewriting, permissions, source coverage, freshness, and uncertainty disclosed where material?
