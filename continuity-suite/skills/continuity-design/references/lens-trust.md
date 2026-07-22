# Trust

## Generalized principles

- At the decision boundary, show the exact actor or account, affected object or resource, destination, amount or data scope, permission, and timing needed to verify what will happen.
- State consequences in operational terms, including affected dependencies, irreversibility, cost, duration, eligibility, or resulting state, before the final action is available.
- Separate current state, observed evidence, inferred risk, and recommended action so a health summary does not become a stronger claim than its visible basis supports.
- Attach freshness and provenance to security or system evidence through timestamps, time ranges, actors, sources, coverage, and scan or event scope.
- Match confirmation friction to consequence: use direct review for routine reversible changes, explicit acknowledgment for material loss, and target-specific confirmation for high-impact irreversible actions.
- Keep cancellation or safe exit visible and label the final action with its actual outcome rather than relying on generic confirmation language.
- When an operation fails, identify the failed task, distinguish known facts from possible causes, state what context or work remains, and offer retry, an alternative path, safe exit, or support as appropriate.
- Permission views should expose both capabilities and the people, roles, resources, or locations they govern, while distinguishing system-defined access from editable assignments.
- Mask sensitive values while preserving enough target identity, source context, and resulting state for the user to verify a consequential operation.
- Place warnings, qualifications, and material terms beside the decision they govern; use linked detail as supporting evidence rather than a substitute for decision-critical disclosure.

## Variation levers

- Use a compact summary plus drill-down for recurring permission or status review, and an expanded review when the action changes money, access, ownership, or durable data.
- Lead monitoring views with current risk and evidence freshness when action is required, and with recent changes and actors when accountability is the primary task.
- Use direct confirmation for low-consequence reversible actions, acknowledgment for material consequences, and typed target confirmation only for rare high-impact irreversible actions.
- Show human-readable cause and recovery first, with technical codes or raw service responses available when they materially help diagnosis or support escalation.
- Use an event table for comparison and audit, a chronological feed for investigation, and a concise state card only when scope and freshness remain visible.
- Use permission presets when roles are stable and legible, and a resource or capability matrix when exceptions and exclusions are common.
- On narrow screens, keep a concise commitment summary and final action together; on wide screens, preserve the affected context behind a focused confirmation layer.
- Use persistent warnings for unresolved system consequences, inline warnings for the current decision, and transient feedback only for completed low-risk operations.

## Tensions and tradeoffs

- Specific target detail improves verification while increasing the risk of exposing sensitive account, identity, or resource information.
- Additional confirmation friction reduces accidental harm while delaying legitimate frequent work and encouraging habituated clicking.
- Comprehensive consequence disclosure supports informed decisions while making the final review difficult to scan.
- Exact timestamps and counts improve auditability while creating false confidence if coverage or collection boundaries remain unstated.
- Raw error detail accelerates expert diagnosis while confusing general users or revealing implementation and security information.
- Strong warning treatment attracts attention while repeated low-value warnings teach users to ignore consequential ones.
- Reassuring language reduces anxiety while becoming misleading when evidence, uncertainty, or recovery limits are absent.
- Linked terms and troubleshooting preserve a compact interface while moving decision-critical evidence away from the moment it is needed.

## Failure modes

- The affected account, actor, object, destination, permission, amount, or time scope is ambiguous at the moment of commitment.
- A warning calls an action risky or permanent without naming the concrete downstream effect.
- A favorable status, score, or zero count appears without timestamp, evidence source, coverage, or assessment boundary.
- Material fees, terms, eligibility, or data-loss consequences appear only after the user commits.
- An error states that something went wrong without identifying the failed task, preserved state, retry path, alternative, or safe exit.
- Every change receives the same heavy confirmation friction, making safeguards routine and easy to dismiss.
- An irreversible or high-impact operation uses the same interaction and visual treatment as a routine reversible action.
- The final control says only confirm or continue, leaving the actual operation and consequence implicit.
- Status color or a health label substitutes for counts, denominators, freshness, or evidence.
- A permission name appears without the capabilities and governed people, resources, or locations needed to evaluate it.

## Anti-patterns

- Using a secure label, shield icon, trust badge, or reassuring sentence as a substitute for visible scope, evidence, and safeguards.
- Using red styling or an alert icon without naming the affected object and concrete consequence.
- Burying a fee, minimum term, eligibility rule, or irreversible effect in linked terms while keeping the commitment action prominent.
- Showing a green score or zero-risk state without the last assessment time, covered population, or evidence source.
- Offering contact support as the only recovery path when retry, safe exit, or an alternate method is available.
- Exposing only a raw exception or service code without a plain-language task, uncertainty statement, or recovery action.
- Requiring typed confirmation for ordinary reversible work until users learn to complete it without reading.
- Preselecting a broad privilege or risky toggle without explaining its capabilities and resource scope.
- Masking so much information that the user cannot verify the source, destination, or affected object.
- Presenting audit activity without actor, time, event scope, or a route to inspect supporting detail.

## Acceptance and review questions

- Can the user verify the active actor or account, affected object or resource, destination, scope, permission, amount, and timing before commitment?
- Are irreversible effects, dependencies, costs, terms, eligibility, and resulting state stated in concrete operational language?
- Does the interface distinguish observed evidence from inferred risk, recommendation, and reassurance?
- Do security, audit, or health claims expose freshness, source, coverage, actors, and assessment boundaries?
- Is confirmation friction proportionate to consequence and rare enough to remain meaningful?
- Does the final action name the actual outcome, with cancel, edit, or safe exit available where appropriate?
- If the operation fails, can the user tell what failed, what remains preserved, which causes are known or uncertain, and what recovery paths exist?
- Do permission labels reveal both capabilities and the people, roles, resources, or locations governed?
- Are sensitive values masked without making the target or source impossible to verify?
- Are decision-critical warnings and terms visible beside the governed action rather than delegated entirely to linked detail?
