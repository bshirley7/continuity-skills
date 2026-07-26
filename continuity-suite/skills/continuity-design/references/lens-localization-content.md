# Localization and content resilience

## Generalized principles

- Model language, region, market, currency, units, time zone, calendar, and content availability as separate preferences or states whenever they can produce different behavior; show the source, scope, precedence, and effect of each.
- Design containers, controls, navigation, tables, and responsive states for translated expansion, contraction, wrapping, reordered grammar, and bidirectional flow; preserve semantic order and action priority instead of relying on fixed text widths or physical left-right labels.
- Accept names, addresses, telephone numbers, postal identifiers, and identity structures according to the selected jurisdiction and task; request only necessary components and do not force one culture's ordering, character set, or family-name model.
- Format dates, times, numbers, currencies, and units for the active locale while retaining unambiguous semantic data; show time zone, currency code, unit, calendar, or an explicit example wherever conversion or misreading changes a decision.
- Make translation and localization coverage inspectable: distinguish interface language, authored content, user-generated content, automated translation, legal text, support availability, and market inventory, including fallback behavior when coverage differs.
- Treat culturally dependent icons, colors, metaphors, examples, address conventions, consent language, and legal claims as reviewable content rather than universal meaning; retain a plain semantic label and jurisdiction-aware validation.

## Variation levers

- Use automatic locale detection as a reversible starting point, not a hidden permanent decision.
- Offer one combined regional panel when effects are closely coupled and separate controls when language, market, currency, or units can vary independently.
- Prefer flexible wrapping and intrinsic sizing; use truncation only when the full value remains immediately available.
- Mirror directional layout relationships in right-to-left contexts while preserving non-directional data conventions, media meaning, and task sequence.
- Show both localized display and canonical code or unit in high-consequence review states.

## Tensions and tradeoffs

- Automatic detection reduces setup while producing incorrect or opaque assumptions.
- Localized formatting improves familiarity while making cross-region comparison harder.
- One regional selector is compact while conflating language, market, currency, and availability.
- Flexible text preserves meaning while changing density, alignment, and scan paths.
- Translated content expands reach while uneven coverage can imply false completeness.
- Jurisdiction-specific forms improve validity while increasing maintenance and testing complexity.

## Failure modes

- A flag is used as the only language label.
- Language selection silently changes market, currency, or inventory.
- Fixed-width controls clip or obscure translated actions.
- Physical left and right instructions break in bidirectional layouts.
- A form requires one country's name, address, or telephone structure.
- Dates or times omit order or time-zone context.
- A currency symbol appears without enough context to disambiguate it.
- Machine-translated, untranslated, and legally authoritative content are not distinguished.

## Anti-patterns

- One locale equals one user identity.
- Flag-only language picker.
- First name and last name as universal identity.
- MM/DD/YYYY without an example or locale context.
- Dollar sign without currency code in cross-market decisions.
- Text baked into images.
- Hard-coded string concatenation.
- Left means previous.
- Ellipsis as the only response to language expansion.
- Translated interface implies translated support.

## Acceptance and review questions

- Are language, region, market, currency, units, time zone, calendar, and content availability separated wherever their effects differ?
- Can every layout survive expansion, contraction, wrapping, reordered grammar, and bidirectional flow without losing meaning or action priority?
- Do forms accept jurisdiction-appropriate names, addresses, telephone numbers, identifiers, and character sets without unnecessary decomposition?
- Are dates, times, numbers, currencies, and units localized while remaining unambiguous at consequential decisions?
- Is translation coverage explicit across interface, authored, generated, legal, support, and market content with defined fallbacks?
- Are culturally dependent symbols, metaphors, examples, and legal claims reviewed with plain semantic alternatives?
- Can users inspect and override automatically detected locale behavior?
