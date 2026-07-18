# Content

## Generalized principles

- Give every field, value, state, message, and action a persistent semantic label that names the concept or operation; use supporting text for format, units, scope, evidence, consequence, or examples rather than repeating the label.
- Write actions as a specific verb and target and distinguish draft, preview, save, submit, send, share, publish, approve, pay, retry, cancel, and delete according to the actual resulting state.
- Express state with object, status, scope, source or evidence, observation time, owner when relevant, consequence, and next step; never depend on color, icon, placement, or a bare success-failure word.
- Make validation and errors local, specific, and recovery-oriented: identify the affected field or object, unmet rule or known cause, retained work, resulting state, and safest next action without blaming the user.
- Preserve exact amounts, units, rates, fees, destinations, times, identities, permissions, and irreversible effects from entry through review, confirmation, receipt, history, and failure handling.
- Keep content scannable through concise front-loaded sentences, parallel structures, stable terminology, descriptive headings, bounded lists, and progressive detail while preserving all information required for a safe decision.

## Variation levers

- Use inline help for short local rules and a linked detail view for policy, evidence, or complex examples.
- Use sentence-style labels for familiar concepts and explicit noun phrases for technical or regulated data.
- Use a compact status summary with inspectable evidence and history.
- Use immediate validation only when the user has completed a meaningful input and the system can evaluate it reliably.
- Repeat critical transaction facts at review and confirmation rather than relying on prior screens.

## Tensions and tradeoffs

- Brevity improves scanning while omitting context needed for safe action.
- Friendly language reduces anxiety while obscuring operational precision.
- Immediate validation accelerates correction while interrupting entry.
- Stable terminology improves comprehension while conflicting with familiar industry language.
- Detailed status improves auditability while increasing visual density.
- Specific recovery guidance helps action while requiring accurate system-state knowledge.

## Failure modes

- Placeholder text is the only label.
- The same word names different states or actions.
- A status lacks object, scope, time, evidence, or next step.
- An error states that something went wrong without identifying what or whether work was retained.
- Retry can duplicate a transaction but the content does not warn the user.
- A destructive or irreversible action uses a vague verb.
- Critical instructions are hidden behind hover or detached from the affected control.

## Anti-patterns

- Placeholder-only form.
- Submit for every action.
- Success without naming the result.
- Something went wrong.
- Invalid input.
- Friendly euphemism for destructive action.
- Color-only status.
- Learn more as the only recovery.
- Changing terminology across steps.
- Instruction wall before a simple field.

## Acceptance and review questions

- Does every field, value, state, message, and action have a persistent semantic label?
- Do actions state the actual verb, target, and resulting state?
- Do statuses include object, scope, evidence, time, owner, consequence, and next step where relevant?
- Do validation and errors identify the affected object, rule or cause, retained work, resulting state, and recovery?
- Are amounts, units, rates, fees, destinations, times, identities, permissions, and irreversible effects preserved through the lifecycle?
- Is content concise, front-loaded, parallel, terminologically stable, and progressively detailed without hiding safe-decision information?
- Can the content be understood without relying on placeholder, color, icon, hover, or position?
