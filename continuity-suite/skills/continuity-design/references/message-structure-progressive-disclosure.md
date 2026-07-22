# Progressive disclosure

## Generalized principles

- Reveal information according to the current task, user intent, decision consequence, and need for inspection; do not equate infrequent, advanced, or complex content with safe-to-hide content.
- Make every disclosure control predict its destination through a specific label, current-value summary, scope, state, and visual relationship to the content it governs.
- Keep active hidden state visible beside the result or action it affects, including filters, overrides, selections, scope, freshness, changed values, and unresolved errors.
- Let deeper layers add definitions, evidence, exceptions, controls, or audit detail while preserving the parent context, user work, focus, reading position, and a clear route back.
- Keep price, renewal, eligibility, risk, irreversible effects, permissions, destructive consequences, and other material terms visible before the decision they govern, regardless of the disclosure pattern.
- Design disclosure for keyboard, screen reader, zoom, narrow-screen, and reduced-motion use with programmatic expanded state, logical reading order, visible focus, adequate targets, and no hover-only access.

## Variation levers

- Use inline expansion for short local detail and a dedicated view for complex editing or evidence.
- Use summary-first dashboards when scope, time, freshness, and active filters remain visible.
- Expose expert controls persistently for frequent expert workflows and progressively for occasional configuration.
- Use editable review summaries in sequential transactions.
- Allow users or organizations to preserve preferred density when the task recurs.

## Tensions and tradeoffs

- Reduced initial complexity improves approachability while weakening discoverability.
- A compact summary speeds scanning while hiding assumptions or exceptions.
- Dedicated detail views create space while increasing context switching.
- Remembered expansion improves efficiency while producing inconsistent shared views.
- Disclosure based on frequency protects focus while potentially hiding consequential rare events.
- Animation clarifies spatial change while adding motion and performance risk.

## Failure modes

- A vague more or advanced control gives no preview of what it reveals.
- Hidden filters or overrides change a visible result without a summary.
- Expansion loses focus, scroll position, entered values, or parent context.
- The deeper layer repeats the summary without adding evidence or control.
- Material terms are deferred until after commitment.
- Collapsed content contains the only error, warning, or required field.
- Disclosure works only through hover, animation, or precise pointer input.

## Anti-patterns

- Advanced as a junk drawer.
- More without a content label.
- Hover-only detail.
- Accordion inside accordion.
- Hidden active filter.
- Collapsed validation error.
- Terms revealed after action.
- Drawer with no stable return path.
- Animation required for comprehension.
- Automatic collapse that discards user work.

## Acceptance and review questions

- Is each item layered according to task, intent, consequence, and inspection need rather than complexity alone?
- Does every disclosure control state what it reveals and summarize current value, scope, or state?
- Are hidden filters, overrides, selections, freshness, changes, and errors visible where they affect results?
- Does the deeper layer add evidence or control while preserving context, work, focus, position, and return?
- Are price, renewal, eligibility, risk, permissions, and irreversible effects visible before action?
- Does disclosure work with keyboard, screen readers, zoom, narrow screens, reduced motion, and non-pointer input?
- Can users recover from expansion, collapse, navigation, interruption, and validation without losing work?
