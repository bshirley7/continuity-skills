# Responsiveness

## Generalized principles

- Adapt by semantic priority rather than proportional shrinking: preserve current scope, selected object, essential state, primary action, and safe return first, then collapse, move, or defer secondary navigation, inspectors, metadata, and utilities.
- Use wide viewports to place stable navigation, collection, work canvas, and selected-object detail in distinct regions, but make secondary panes independently collapsible so content never becomes a set of unusably narrow columns.
- Maintain continuity when a multi-pane workspace becomes a compact sequence by preserving selection, title, project or collection, filters, scroll position, unsaved state, and a predictable back path between list and detail.
- Separate destination navigation, primary creation or commit, and contextual object actions into stable regions; use compact rails, bottom navigation, floating actions, sticky actions, and anchored menus according to frequency and consequence.
- For dense data, preserve report identity, time and comparison scope, essential measures, status, and qualifications before optional annotations, query builders, secondary columns, export controls, and advanced configuration.
- Transform data structures deliberately across widths through prioritized columns, horizontal overflow with visible cues, summary cards, row detail, or alternate chart and table views; never silently remove the values needed for the decision.
- Let forms and editors reflow into sectioned single-column tasks with persistent labels, full-width controls, keyboard-safe spacing, progressive disclosure, and a commit action that stays reachable without obscuring the active field.
- Keep overlays and contextual menus anchored to the selected object when space permits, then promote them to sheets or dedicated screens when a popover would clip, obscure, or produce targets too small to operate.
- Preserve state boundaries across devices: distinguish edit, saved, running, published, and closed state, and do not turn a desktop secondary utility into a persistent mobile obstruction when it is not active.
- Test responsive behavior as content and state combinations, including long labels, many panes, wide tables, keyboard visible, empty and error states, selected rows, open menus, active inspectors, and unsaved work—not only at nominal viewport widths.

## Variation levers

- Use simultaneous panes when comparison and rapid switching matter; use sequential list-to-detail navigation when content needs full width.
- Use a compact rail for high-frequency destinations, an expanded sidebar when labels matter, and bottom navigation for a small mobile destination set.
- Use a side inspector for supporting detail, a bottom or full-height sheet on compact screens, and a dedicated page for consequential review.
- Use prioritized columns and horizontal overflow for expert tables, summary cards for monitoring, and row detail for complete inspection.
- Use sticky commit actions for long forms, inline actions for local changes, and floating creation only when it does not compete with navigation or content.
- Use anchored popovers when target and context fit together and full-width sheets when keyboard, long content, or large targets require more space.
- Use breakpoint changes for structural transitions and intrinsic wrapping or scrolling for local content adaptation.
- Use preserved draft and return context across device transitions when the same task can legitimately resume elsewhere.

## Tensions and tradeoffs

- Simultaneous panes accelerate comparison while reducing usable width and increasing cognitive load.
- Collapsing navigation gives content more space while hiding destinations and orientation.
- Horizontal table scrolling preserves columns while weakening comparison and discoverability.
- Sticky and floating actions remain reachable while covering content or keyboard-safe space.
- Bottom navigation supports touch reach while limiting the number of destinations.
- Sheets preserve underlying context while creating constrained nested scrolling.
- Progressive disclosure reduces compact-screen density while hiding advanced state and controls.
- Cross-device continuity improves flexibility while increasing synchronization and conflict complexity.

## Failure modes

- The layout shrinks every region equally instead of preserving semantic priority.
- A multi-pane workspace cannot collapse secondary panes before content becomes too narrow.
- List-to-detail transitions lose selection, scope, filters, scroll, unsaved state, or safe return.
- Navigation, creation, commit, and contextual actions compete in the same region.
- Dense data drops identity, time scope, essential measures, status, or qualifications at narrow widths.
- Columns disappear silently with no overflow cue, summary, or detail route.
- The keyboard or sticky action obscures fields, errors, or the current editing target.
- A popover clips or creates targets too small for the available viewport.
- A secondary utility remains persistently visible on compact screens when inactive.
- Responsive testing covers viewport width but not real content, state, overlays, and keyboard conditions.

## Anti-patterns

- Scaling a desktop workspace down without changing structure.
- Keeping four narrow panes open because the viewport technically fits them.
- Returning users to the top of a list after closing detail.
- Hiding the primary action inside the same overflow menu as rare utilities.
- Removing table columns with no indication that data is missing.
- Using a chart-only mobile view when exact values are required.
- Letting a sticky button cover the last form fields.
- Opening a desktop-sized popover under the mobile keyboard.
- Keeping an inactive assistant bar over mobile content.
- Testing only empty mockups at standard breakpoints.

## Acceptance and review questions

- Does each layout preserve scope, selection, essential state, primary action, and safe return before secondary regions?
- Can secondary panes collapse independently before the work canvas becomes unusable?
- Do list and detail transitions preserve selection, filters, scroll, unsaved state, and return position?
- Are destination navigation, primary creation or commit, and contextual actions distinct and reachable?
- Do dense data views preserve identity, time and comparison scope, essential measures, status, and qualifications?
- Are removed or overflowing columns discoverable through cues, summaries, or detail routes?
- Do forms and editors remain usable with the keyboard visible and sticky actions present?
- Do popovers become sheets or pages before clipping, obscuring context, or shrinking targets?
- Are edit, saved, running, published, and closed states preserved across compact and wide layouts?
- Have long labels, many panes, wide tables, open overlays, errors, selections, keyboards, and drafts been tested?
