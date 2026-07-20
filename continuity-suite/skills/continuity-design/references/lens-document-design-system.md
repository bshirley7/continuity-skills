# Document design systems

## Generalized principles

- Begin with reader tasks and a semantic document model rather than pages: define the title, purpose, audience, status, summary, section hierarchy, navigation, figures, tables, notes, references, appendices, and metadata as structured content whose meaning survives restyling, reflow, export, assistive technology, and print.
- Make reading order singular and intentional: ensure the visual sequence, source order, tag tree, keyboard order, headings, lists, captions, notes, and cross-references tell the same story; treat multi-column layouts, sidebars, floating objects, repeated furniture, and inserted pages as risks that require explicit verification.
- Use a bounded page and spacing system that serves comprehension: define measure, margins, columns, baseline and spacing rhythm, heading intervals, paragraph treatment, list indentation, figure and table placement, and controlled exceptions; preserve hierarchy without relying on position, scale, weight, color, or decorative geometry alone.
- Design navigation for both scanning and precise return: provide descriptive titles and headings in a logical hierarchy, a table of contents for longer works, bookmarks or landmarks where supported, meaningful links and cross-references, figure and table identification, stable section identifiers, and compatible print-digital location cues when editions must coordinate.
- Treat figures and tables as evidence-bearing document components: state the question or takeaway, identify what is measured and its scope, use captions and headers, keep data structures simple enough to navigate, provide equivalent text or accessible data, cite the specific source and freshness, and separate interpretation from the underlying values.
- Choose format from use rather than convention: prefer reflowable, searchable, selectable, responsive, and structurally accessible delivery for reading; retain fixed pages only when page geometry is materially required, provide an equivalent accessible form when needed, and preserve an editable accessible source rather than making remediation the primary workflow.
- Build accessibility and resilience into templates and conversion: encode named styles, language, heading levels, list and table semantics, alternative text, link meaning, color and contrast, text spacing, page numbers, metadata, and export settings; test zoom, reflow, mobile reading, print, search, selection, assistive navigation, and lossless conversion with representative content.
- Make document authority and revision state visible: identify owner, status, version or date, applicable scope, source references, approval state, superseded editions, change history, and canonical location; keep these signals in machine-readable metadata and perceivable content where consequential, and verify that exports do not detach them from the work.
- Validate the delivered artifact, not only the source or visual proof: combine automated checks with manual inspection of structure, sequence, headings, tables, figures, links, metadata, language, reflow, keyboard and assistive navigation, print output, and representative reader tasks after every conversion or assembly step.

## Method

- Define the document's readers, decisions, tasks, authority, lifecycle, formats, and accessibility obligations.
- Outline the semantic content model and navigation before designing pages.
- Specify the document grammar: page architecture, measure, spacing, typography, hierarchy, components, figures, tables, citations, notes, and metadata.
- Create accessible source templates with named styles, semantic structures, controlled variants, and safe export settings.
- Prototype representative dense, sparse, tabular, illustrated, long, translated, and revised pages rather than an ideal cover and one body page.
- Produce reflowable and fixed outputs only where their reader tasks justify them.
- Test the final artifacts with automated checkers, manual structure inspection, keyboard and assistive navigation, zoom, reflow, mobile, print, search, selection, and data access.
- Record ownership, approval, revision, canonical location, source data, and supersession before release.

## Ethical safeguards

- Do not use layout, typography, footnotes, or appendices to conceal material limitations, risks, conditions, or dissent.
- Do not present decorative precision, branding, or publication polish as evidence of authority or correctness.
- Do not publish image-only, scanned, untagged, or fixed-layout content without an accessible equivalent when the information can be structured.
- Do not omit data sources, dates, definitions, uncertainty, or exclusions needed to interpret figures and claims.
- Do not let templates silently preserve obsolete owners, dates, approvals, classifications, or confidentiality markings.
- Do not claim accessibility from an automated checker alone.

## Variation levers

- Use a single reflowable column for task guidance and broad accessibility; introduce columns only when comparison, density, or print economy materially benefits.
- Increase navigational aids, summaries, running context, and stable identifiers as length, complexity, reference use, or edition coordination grows.
- Increase typographic and compositional expression for editorial or brand publications while preserving the semantic model and reading sequence.
- Reduce decorative furniture and page-dependent references for mobile-first and assistive reading.
- Use fixed layout for forms, legal exhibits, art books, or print-critical artifacts only with an accessible source and equivalent path.
- Provide richer source, method, uncertainty, and downloadable-data support as analytical consequence increases.

## Tensions and tradeoffs

- Fixed page composition supports print control while resisting reflow, zoom, and small-screen reading.
- Dense reference layouts speed expert lookup while increasing sequence and navigation complexity.
- Strong visual differentiation aids scanning while semantic structure must remain complete without styling.
- Reusable templates improve consistency while carrying stale metadata and encouraging content to fit the template.
- Concise summaries improve access while oversimplifying evidence or dissent.
- Automated generation improves repeatability while conversion can detach tags, reading order, links, and provenance.

## Failure modes

- Pages are designed before the document outline, reader tasks, and semantic structure.
- Visual order differs from source, tag, keyboard, or assistive reading order.
- Hierarchy depends on bold, size, color, indentation, or position instead of named structure.
- Tables and charts appear without captions, accessible equivalents, specific sources, or interpretive context.
- A fixed PDF is the only deliverable even though reading does not require fixed geometry.
- Styles and accessibility are repaired separately in every output instead of encoded in the source template.
- Version, owner, approval, and supersession are hidden, stale, or detached during export.
- The source passes a checker but the converted, merged, or published artifact is not manually verified.

## Anti-patterns

- Page-first authoring.
- Four competing reading orders.
- Formatting masquerading as structure.
- Orphan evidence graphics.
- PDF by reflex.
- Remediation as production.
- Invisible authority state.
- Source-only accessibility testing.

## Acceptance and review questions

- Does the semantic model preserve title, purpose, hierarchy, navigation, components, references, and metadata across styling and formats?
- Do visual, source, tag, keyboard, and assistive reading orders agree for every representative page?
- Does the page and spacing system support readable measure, hierarchy, grouping, scanning, and controlled exceptions without single-channel meaning?
- Can readers scan, navigate, link, cite, and return precisely in both digital and print contexts?
- Do figures and tables communicate scope, structure, source, freshness, uncertainty, interpretation, and accessible equivalents?
- Is each delivery format justified by the reader task, with reflowable or equivalent access where fixed layout is retained?
- Are accessibility, metadata, responsive behavior, and conversion rules encoded in reusable source templates and tested with representative content?
- Are owner, status, version, approval, scope, canonical location, history, and supersession visible and preserved?
- Has the final delivered artifact passed automated and manual structural, visual, assistive, reflow, mobile, print, and task validation?
