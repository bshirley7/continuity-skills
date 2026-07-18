# Typography

## Generalized principles

- Define typography by semantic role—display, heading, body, label, action, metadata, caption, code, numeric data, status, and assistance—then map family, size, weight, line height, spacing, and contrast consistently to each role.
- Create hierarchy through coordinated differences in role, scale, weight, measure, spacing, placement, and contrast rather than oversized headings or weight alone.
- Protect sustained reading with bounded line length, adequate line height, paragraph rhythm, distinguishable links, stable alignment, and user-respectful zoom or text scaling.
- For dense data, align values by type, preserve tabular comparison where needed, distinguish labels from values and statuses, and make truncation, expansion, selection, and disabled state explicit.
- Specify responsive type behavior by content role and available measure, including wrap, reflow, truncation, minimum readable size, heading balance, and preservation of action and data hierarchy.
- Design for localization and accessibility by testing longer strings, varied scripts, diacritics, numeric and date formats, bidirectional text, user font scaling, contrast, and non-color emphasis without assuming one language or font metric.

## Variation levers

- Use an expressive display family only for bounded roles and a durable reading family for body and interface text.
- Use fluid scale within tested minimum and maximum bounds for marketing layouts.
- Use compact density by reducing whitespace and redundant labels before reducing readable text.
- Use tabular numerals for repeated comparison and proportional numerals for prose.
- Use monospace for code or structurally aligned technical values, not as a generic technical aesthetic.

## Tensions and tradeoffs

- Brand distinctiveness can reduce reading familiarity.
- Large display type creates impact while consuming responsive space.
- Compact density improves scanning while stressing legibility.
- Strict role consistency improves predictability while limiting editorial variation.
- User text scaling protects access while disrupting fixed layouts.

## Failure modes

- Every heading is oversized.
- Body measure becomes too wide or cramped.
- Weight is the only hierarchy signal.
- Metadata and disabled text fall below readable contrast.
- Numbers do not align for comparison.
- Truncation hides consequential content with no expansion.
- Responsive type shrinks proportionally instead of reflowing.
- Localized strings break controls or hierarchy.

## Anti-patterns

- Display font for body copy.
- All caps for long labels.
- Gray-on-gray metadata.
- Font size below readable minimum to preserve layout.
- Manual line breaks that fail responsively.
- Icon-only replacement for overflowed text.
- Monospace as technical decoration.
- Truncated amount, status, warning, or action.
- Typography tokens named by appearance instead of role.

## Acceptance and review questions

- Are display, heading, body, label, action, metadata, caption, code, numeric, status, and assistance roles explicit?
- Does hierarchy use coordinated role, scale, weight, measure, spacing, placement, and contrast?
- Are reading measure, line height, paragraph rhythm, links, zoom, and text scaling protected?
- Do dense data and settings preserve alignment, comparison, truncation, expansion, selection, disabled state, and consequence?
- Is responsive behavior specified by role with tested minimums, wrapping, reflow, and hierarchy?
- Are longer strings, varied scripts, formats, bidirectionality, font scaling, contrast, and non-color emphasis tested?
- Is guidance based on visible typography behavior rather than claiming unobserved font implementation?
