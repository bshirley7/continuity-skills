# Contextual help and recovery

## Generalized principles

- Keep the affected object, user input, workflow position, prior successful state, and surrounding task visible or restorable while explaining what failed and what remains safe, pending, changed, or unknown.
- Offer recovery actions that match verified state: edit invalid input, retry an idempotent operation, choose an alternative, resume preserved work, undo a partial change, or escalate with a diagnostic reference; never present retry when duplicate outcome is uncertain.
- Route help from the current object and task into relevant guidance first, then searchable documentation, examples, peer support, feedback, and human support without replacing the workspace or losing the return path.
- When support needs access or context, identify the information shared, target scope, duration, authority, current access state, and revoke path; separate diagnostic assistance from permission to mutate.

## Variation levers

- Use inline correction for known local errors, a side panel for contextual diagnosis, and a dedicated incident workspace for multi-source investigation.
- Escalate from suggested guidance to search, peer support, and human support according to consequence and uncertainty.
- Use terse recovery for familiar reversible failures and fuller state explanation for financial, destructive, or ambiguous outcomes.

## Tensions and tradeoffs

- Detailed diagnostics aid recovery while overwhelming non-expert users.
- Embedded help preserves context while reducing workspace area.
- Automated diagnosis accelerates investigation while introducing uncertain interpretation.

## Failure modes

- A generic error cannot identify the affected object or whether work was saved.
- Retry is offered when the previous result may still be pending.
- Starting over discards work without disclosure.
- Support opens without current task context and forces the user to reconstruct the problem.

## Anti-patterns

- Something went wrong as the whole diagnosis.
- Blind retry.
- Start over without loss preview.
- Help that replaces the task.
- Support access without scope or expiry.
- AI diagnosis presented as verified cause.

## Acceptance and review questions

- Can users identify the affected object and verified outcome?
- Is preserved, pending, changed, and unknown state explicit?
- Does each recovery action match the operation's actual safety and idempotency?
- Can users reach relevant guidance without losing task context?
- Does escalation carry a useful diagnostic reference?
- Is support access scoped, time-bound, visible, and revocable?
