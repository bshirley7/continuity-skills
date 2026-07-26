# Motion and feedback

## Generalized principles

- Represent asynchronous work as explicit states—accepted, queued, transferring, validating, processing, partially complete, complete, failed, canceled, or interrupted—so feedback never overstates durable completion.
- Anchor feedback to the affected object and preserve task identity, source context, user input, and return path across transitions, background continuation, interruption, and completion.
- Use determinate progress only when meaningful completion can be measured; otherwise name the current stage, ongoing activity, and expected next state without fabricating precision.
- Separate immediate acknowledgement from durable completion, then resolve success into the actual saved, booked, published, or generated product state rather than a disconnected celebratory endpoint.
- Make failure and interruption actionable by preserving completed work, identifying the failed scope, explaining what remains uncertain, and offering retry, correction, cancellation, or safe exit without duplicate commitment.
- Provide non-motion equivalents for every transition and progress signal through persistent text, icons, state labels, structure, and focus management; reduced motion should remove unnecessary travel and looping without removing information.

## Variation levers

- Use object-anchored inline feedback for routine reversible changes.
- Use staged progress for imports, validation, and multi-step processing.
- Use durable receipts for financial, booking, publication, or access commitments.
- Move long-running work into background status only when task identity and return paths remain clear.
- Use brief transition motion to explain spatial or state continuity, with reduced-motion alternatives.

## Tensions and tradeoffs

- Immediate acknowledgement improves confidence while risking false success.
- Persistent progress reassures while consuming attention.
- Celebratory motion reinforces completion while delaying continued work.
- Background continuation frees the interface while making status easier to lose.
- Detailed failure messages aid recovery while increasing cognitive load.

## Failure modes

- A spinner stands in for an unnamed state.
- Optimistic feedback looks identical to durable completion.
- Progress percentages are fabricated or stall without explanation.
- Success ends at an interstitial with no resulting object.
- Retry can duplicate payment, booking, upload, or publish actions.
- Background work loses task identity or return path.
- Reduced motion removes state information rather than only unnecessary movement.

## Anti-patterns

- Endless spinner.
- Success toast before persistence.
- Fake linear progress bar.
- Confetti for routine saves.
- Blocking animation after completion.
- Error that discards input.
- Retry without idempotency warning.
- Notification with no object link.
- Motion-only change cue.
- Looping skeleton after actionable content exists.

## Acceptance and review questions

- Are asynchronous states named distinctly from durable completion?
- Is feedback anchored to the affected object with task identity, input, context, and return path preserved?
- Is progress determinate only when it is genuinely measurable?
- Does success resolve into the actual resulting product state?
- Can partial failure, interruption, cancellation, and retry preserve completed work and avoid duplicate commitment?
- Does background work remain findable across attention changes?
- Do reduced-motion alternatives preserve every informational and focus-management function?
- Is guidance limited to visible state transitions rather than claiming unobserved processing behavior?
