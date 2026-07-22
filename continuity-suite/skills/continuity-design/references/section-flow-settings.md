# Settings

## Generalized principles

- Identify the setting's subject and scope before the control, distinguishing personal, workspace, organization, product, environment, audience, and inherited policy so users know who and what will change.
- Show the current value, source, inheritance, override state, and effective result together, especially when system defaults, administrators, plans, groups, or environments determine behavior.
- Use one explicit change model within a settings region—immediate, autosaved, or save-and-cancel—and expose dirty, saving, saved, failed, and conflicting states instead of mixing silent persistence with batch save.
- Explain the operational consequence beside each material control, including visibility audience, notification event and channel, billing commitment, authentication reach, integration data flow, or accessibility behavior.
- For integrations, expose connected identity, grant authority, personal or shared scope, permissions, data or action direction, assets affected, last successful activity, error state, and reconnect or disconnect consequence.
- For billing and entitlement, connect plan, trial or renewal timing, seats and utilization, usage limits, owner, payment method, invoice history, support, and downgrade or cancellation effects.
- Separate reversible preference changes from consequential security, privacy, ownership, billing, publication, and deletion actions, using stronger review, authorization, and confirmation in proportion to impact.
- For export, deletion, deactivation, or transfer, state the exact data and resources affected, prerequisites, retained information, downstream obligations, processing time, recovery window, identity reuse, delivery method, and irreversible outcome.
- Organize settings by user-recognizable domain and provide search or direct routes for large systems, keeping related dependencies linked without duplicating controls across sections.
- Preserve a recoverable path through cancel, reset to inherited or default, reconnect, undo window, export-before-delete, or documented support, and confirm the effective result after change.

## Variation levers

- Use immediate changes for reversible personal display preferences and explicit save for multi-field identity, policy, or configuration changes.
- Use tabs for a small account surface, hierarchical navigation for organization administration, and search or deep links when settings span many products.
- Use toggles for independent binary effects, radio groups for mutually exclusive behavior, selectors for bounded values, and review dialogs for consequential actions.
- Use inherited values when administrators define policy and explicit overrides only when the user has authority.
- Use one global notification default with event-level exceptions when volume is high, or fully explicit event-channel rows when consequence varies.
- Use separate connected, available, error, and administrator-managed integration states.
- Use typed confirmation only as one layer of destructive review, not as a substitute for explaining impact.
- Use reset to system, organization, or product default according to the source actually governing the value.

## Tensions and tradeoffs

- Immediate persistence feels responsive while increasing accidental change and making multi-field cancellation impossible.
- Deep categorization improves findability for experts while forcing new users to understand the product's internal model.
- Local explanations improve confidence while making settings pages dense and repetitive.
- Administrator control improves consistency while obscuring why a personal control is unavailable.
- Granular notifications reduce noise while creating a large and difficult preference matrix.
- Easy integration connection accelerates setup while hiding data access and long-term ownership.
- Strong deletion friction prevents mistakes while obstructing legitimate privacy rights.
- Reset to default simplifies recovery while becoming ambiguous when several defaults or policies apply.

## Failure modes

- A control does not identify whether it affects the person, workspace, organization, product, environment, or public audience.
- The displayed value hides an inherited policy, administrator source, or pending override.
- Immediate and explicit-save controls are mixed without dirty or saved state.
- A material setting changes without explaining its audience, cost, security, data, or behavior consequence.
- A connected app omits identity, permission, scope, activity, error, or disconnect impact.
- Billing hides renewal timing, utilization, owner, usage limits, or cancellation effects.
- Destructive actions are visually grouped with routine preferences.
- Deletion or export omits affected resources, retention, timing, recovery, or delivery details.
- A large settings surface lacks stable hierarchy, search, or direct routes.
- A failed or conflicting change leaves the displayed control different from effective behavior.

## Anti-patterns

- Using a toggle without naming the resulting behavior or audience.
- Saving some fields immediately and others only through an unlabeled page-level button.
- Showing disabled controls without the governing plan, role, policy, or remediation path.
- Labeling an integration connected without naming the connected account or data scope.
- Using a generic danger zone as the only explanation of destructive impact.
- Requiring typed confirmation while omitting what will be deleted or retained.
- Treating notification preferences as one global on or off switch.
- Duplicating the same setting in personal and organization pages with no precedence rule.
- Resetting to default without identifying which default will apply.
- Confirming save success before the effective policy or remote connection has updated.

## Acceptance and review questions

- Does every setting identify its subject, scope, source, inheritance, and effective result?
- Is the current value and any administrator, plan, environment, or system constraint visible?
- Is the change model consistently immediate, autosaved, or explicit, with dirty, saved, and failed states?
- Are audience, behavior, security, data, cost, and accessibility consequences explained locally?
- Do integrations expose identity, authority, scope, permissions, direction, assets, activity, errors, and disconnect effects?
- Does billing connect plan, timing, seats, usage, owner, payment, invoices, and cancellation effects?
- Are consequential actions separated from reversible preferences and reviewed proportionally?
- Do export, deletion, deactivation, and transfer explain scope, prerequisites, retention, timing, recovery, delivery, and irreversibility?
- Can users find settings through stable domains, search, and direct dependency links?
- Can users cancel, reset, reconnect, recover, or verify the effective result after a change?
