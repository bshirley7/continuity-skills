# Interface language

## Generalized principles

- Define canonical names for objects, actors, scopes, states, and operations; use one term for one concept and introduce a different term only when lifecycle, authority, or user meaning genuinely differs.
- Write actions as literal verb-and-object operations that predict the resulting state; distinguish create, add, connect, assign, invite, save, submit, send, publish, approve, resolve, archive, revoke, and delete.
- Make scope and precedence explicit across personal, team, app, project, workspace, environment, organization, and external-system contexts, including inherited, overridden, and policy-controlled state.
- Structure activity and notification language around actor, action, object, scope, time, resulting state, urgency, and available response; distinguish information, request, assignment, warning, approval, failure, and completion.
- Use domain terms where they match the user's operating model, but define unfamiliar, overloaded, technical, regulated, or metaphorical language at the point where it affects a decision or action.
- Let tone adapt to context while keeping state, cause, evidence, consequence, retained work, and recovery literal; do not use warmth, humor, confidence, or apology to blur operational truth.

## Variation levers

- Use familiar plain-language nouns for common tasks and domain-specific nouns for genuine specialist objects.
- Use concise labels with contextual definitions rather than expanding every label into instruction text.
- Use neutral operational tone for dense and high-consequence work and more expressive tone for onboarding or low-risk empty states.
- Use active voice when the actor is known and explicit system language when responsibility belongs to the product.
- Maintain a terminology registry with canonical term, definition, scope, lifecycle, prohibited synonyms, and localization notes.

## Tensions and tradeoffs

- Domain vocabulary improves precision while excluding newcomers.
- Plain language improves approachability while flattening meaningful distinctions.
- Concise labels improve scanning while requiring contextual help.
- A consistent term improves learning while inherited industry language may vary.
- Conversational tone improves warmth while weakening operational clarity.
- Human-like system language improves flow while obscuring agency and accountability.

## Failure modes

- The same concept has different names across navigation, forms, activity, and help.
- One term names objects with different scope or lifecycle.
- An action label does not predict the resulting state.
- Notifications omit actor, object, time, or required response.
- Activity is described as completion or approval without the corresponding state change.
- AI metaphors hide input, output, uncertainty, review, or automation behavior.
- Friendly tone replaces a literal explanation of failure or consequence.

## Anti-patterns

- Synonym roulette.
- Submit for every action.
- Smart as a behavior description.
- Activity equals completion.
- Success without an object.
- Human-like system agency.
- Marketing copy in settings.
- Scope hidden in a tooltip.
- Cute destructive language.
- Jargon glossary detached from the decision.

## Acceptance and review questions

- Are canonical object, actor, scope, state, and operation names defined and used consistently?
- Does every action label predict its actual resulting state?
- Are personal, team, app, project, workspace, environment, organization, and external scopes explicit with precedence?
- Do activity and notifications identify actor, action, object, scope, time, resulting state, urgency, and response?
- Are unfamiliar, overloaded, technical, regulated, and metaphorical terms defined where they affect decisions?
- Does tone preserve literal state, cause, evidence, consequence, retained work, and recovery?
- Can terminology be localized without collapsing distinct concepts or embedding grammar in reusable labels?
