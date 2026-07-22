# Discovery

## Generalized principles

- Keep the active query, category, location, date, audience, and other material scope visible beside the results, representing applied constraints as removable state so users can explain, narrow, or broaden the set without reconstructing the search.
- Expose the attributes that determine choice at result level, including price basis, availability, eligibility, source, recency, location, scope, or commitment cost, and align comparable fields so users do not have to open every item to judge fit.
- Separate retrieval modes such as recent, saved, popular, editorially curated, sponsored, personalized, and query-matched results, and disclose the rationale closely enough that familiarity, payment, or recommendation does not masquerade as relevance.
- Preserve discovery context when users inspect, save, compare, or make a lightweight commitment by retaining the query, filters, scroll or spatial position, selected item, and a direct route back to the same result set.
- Synchronize alternate result representations such as list, grid, map, room, or canvas views through one selection and filter state, and make view-specific scope changes explicit.
- Treat availability, sold-out state, inventory, eligibility, delivery timing, and service capacity as discovery evidence because these constraints change whether a result can meaningfully enter comparison.
- Provide result counts and clear empty or reduced-set explanations after filters change, including which constraints produced the set and the safest ways to broaden it without discarding the user's intent.
- Use card density and grouping according to decision complexity: keep a stable grammar for comparable items, add detail when material constraints must be judged before opening, and separate collections when they represent different discovery intents.
- Make search results trustworthy through type, owner or provider, source or space, updated time, location, sponsorship, and other provenance needed to distinguish similarly named or visually similar items.
- Support progressive commitment from explore to inspect, save, compare, contact, book, subscribe, or purchase, keeping the consequence and reversible state clear at each transition rather than collapsing discovery directly into the final action.

## Variation levers

- Use query-first retrieval when intent is explicit, category-led browsing when users are learning the space, and recommendation modules when prior behavior or editorial judgment materially improves orientation.
- Use a list for metadata-rich comparison, a grid for visual scanning, a map for location-sensitive choice, and a split view when spatial and descriptive evidence must remain synchronized.
- Use compact cards when one or two attributes dominate choice and expanded rows when price basis, availability, scope, eligibility, or provenance must be compared before detail.
- Use global filters for constraints that redefine the full set and local controls for one collection or representation, labeling any difference in scope.
- Use saved items for known candidates, saved searches for recurring intent, and comparison trays for deliberate side-by-side evaluation.
- Use immediate inline commitment for reversible actions and a detail or review transition when the action creates cost, eligibility, scheduling, or fulfillment consequences.
- Use explicit rationale labels for sponsored, personalized, popular, recently viewed, and editorially selected results.
- Use pagination for stable retrieval, continuous loading for open-ended exploration, and bounded carousels only for clearly named secondary collections.

## Tensions and tradeoffs

- More result-level evidence reduces unnecessary detail visits while increasing card density and scan time.
- Persistent filters make scope legible while consuming scarce space, especially on mobile.
- Personalization can accelerate relevance while narrowing exposure and obscuring why alternatives were excluded.
- Map synchronization supports spatial judgment while marker density and viewport changes can destabilize the result set.
- Inline save, compare, and purchase actions support momentum while increasing accidental activation and card competition.
- Editorial grouping improves orientation while weakening exhaustive retrieval and direct cross-group comparison.
- Recent and popular shortcuts reduce effort while allowing familiarity or volume to displace the current query.
- Preserving exploration context supports return and comparison while complicating navigation, caching, and state restoration.

## Failure modes

- Results appear without the active query, scope, filters, sort, or count that produced them.
- Cards omit a material choice attribute and force every candidate to be opened before comparison.
- Sponsored, personalized, popular, recent, and query-matched results are blended without a visible rationale.
- Opening, saving, comparing, or committing to an item destroys the prior result and filter state.
- List, grid, map, or canvas views show different selections or constraints without declaring the mismatch.
- Unavailable, ineligible, sold-out, out-of-stock, or delayed results look equally actionable.
- A reduced or empty set offers only a generic reset that discards all user intent.
- Card size, metadata, and imagery vary without mapping to a different item type or decision need.
- Enterprise results omit type, owner, source, path, or freshness needed to distinguish similar records.
- A result card jumps directly to a consequential action without a legible inspection or review boundary.

## Anti-patterns

- Hiding every applied constraint inside a filter drawer.
- Using recommendation labels such as for you without explaining the signal or allowing escape.
- Ranking by popularity alone when availability, eligibility, distance, freshness, or fit determines utility.
- Putting promotional collections above the user's explicit query without separating them.
- Resetting scroll position and filters after returning from item detail.
- Letting map movement silently redefine results without a visible search-this-area action.
- Using image-led cards for services or high-consequence choices without scope, provider, and commitment evidence.
- Treating saved items, saved searches, and comparison selection as the same state.
- Showing a result count without explaining that local filters or representation-specific scope changed it.
- Making paid placement visually indistinguishable from relevance-ranked results.

## Acceptance and review questions

- Can users see the active query, scope, constraints, sort, and result count without reopening controls?
- Do result cards expose the material attributes needed to judge fit before detail?
- Are recent, saved, popular, sponsored, personalized, curated, and query-matched modes visibly distinct?
- Does inspecting, saving, comparing, or acting on an item preserve the exact discovery context?
- Do list, grid, map, room, and canvas views share one explicit selection and filter state?
- Are availability, eligibility, inventory, timing, capacity, and sold-out states visible before commitment?
- Can users broaden a reduced or empty set one constraint at a time without losing their intent?
- Does card density and grouping match the complexity and type of decision?
- Do enterprise and service results expose type, source, owner or provider, freshness, and sponsorship where material?
- Is the transition from explore to inspect, save, compare, contact, book, subscribe, or purchase explicit and appropriately reviewable?
