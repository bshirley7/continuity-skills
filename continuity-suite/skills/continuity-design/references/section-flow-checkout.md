# Checkout

## Generalized principles

- Maintain a concise commitment summary across checkout steps, including the selected item or service, fulfillment or attendance context, current total, and chosen payment state.
- Present the full cost as a reconstructable equation that updates when taxes, fees, discounts, tips, add-ons, quantities, or fulfillment choices change.
- Place the final commitment action beside the exact payable amount and use a verb that distinguishes ordering, booking, paying, or reserving.
- Keep correction and recovery local to the affected detail so users can change items, fulfillment, identity, payment, or promotions without rebuilding valid checkout state.
- Distinguish editable review, payment processing, confirmed, failed, and fulfilled states while preserving enough context to prevent duplicate action and support recovery.
- Carry material fulfillment, eligibility, cancellation, and refund consequences into final review instead of leaving them only at discovery.
- Explain optional additions and communication preferences before inclusion, and keep them visually separate from required purchase inputs.
- Use urgency only for a real expiring condition such as an inventory hold, and keep its basis visible without obscuring cost, correction, or exit.
- Turn confirmation into a durable handoff with an order or booking record, current status, next steps, retrieval or tracking, and support access.

## Variation levers

- Use a compact single review when fulfillment and identity are already known, and a stepped sequence when addresses, travelers, attendees, or policy acknowledgements must be collected.
- Keep the summary persistently visible on wide layouts and provide a stable expandable summary near the action on narrow layouts.
- Show delivery, pickup, digital access, reservation, or attendance details according to the actual fulfillment model.
- Use inline editing for small corrections and a focused substep for sensitive payment, identity, or eligibility changes.
- Offer native wallets for speed while preserving the same total, terms, fulfillment, and confirmation clarity as manual payment.
- Use a processing interstitial when authorization is not immediate, retaining the amount and order identity while disabling duplicate submission.
- Provide tracking for physical or delivery orders, retrieval for digital tickets, itinerary records for travel, and calendar or access details for scheduled services.

## Tensions and tradeoffs

- A persistent summary improves orientation while reducing space for complex forms on small screens.
- Detailed fee and policy disclosure increases trust while making checkout feel longer and more demanding.
- A dedicated review step catches mistakes while adding friction after users believe they have already completed the form.
- Fast wallet payment reduces input effort while risking a weaker review of fulfillment and terms.
- Optional add-ons can improve fit while interrupting the primary purchase and obscuring the base commitment.
- Inventory timers explain real availability while also increasing pressure and reducing careful review.
- Post-purchase recommendations may be commercially useful while competing with receipt, status, recovery, and support needs.

## Failure modes

- The final action is separated from the exact total, fulfillment choice, or selected payment method.
- Taxes, service charges, delivery costs, tips, or add-ons appear only after the user has invested substantial effort.
- Changing fulfillment, quantity, or an optional extra does not visibly update the payable total.
- A correction forces the user to restart or silently clears otherwise valid information.
- The processing state removes item, merchant, amount, or payment context and leaves duplicate submission ambiguous.
- Confirmation celebrates completion without providing an identifier, access, tracking, cancellation, or support path.
- Refund, cancellation, fare, seat, delivery, or attendance conditions disappear before commitment.
- Optional tips, protection, marketing, donations, or memberships are visually indistinguishable from required inputs.
- A countdown remains prominent without explaining what expires or what happens when it reaches zero.

## Anti-patterns

- Using a generic continue label for the final irreversible commitment.
- Displaying only a grand total when material fees or add-ons cannot be inspected.
- Preselecting optional protection, tips, marketing, donations, or memberships without clear consent.
- Introducing a new cost, restriction, or fulfillment condition inside the payment sheet or after authorization begins.
- Combining several scarcity labels, countdowns, and comparative claims around the final action.
- Clearing the basket or form after a recoverable payment, promotion, or validation error.
- Allowing repeated taps to create uncertain duplicate orders while payment is processing.
- Replacing the operational confirmation with advertisements or recommendations before receipt and recovery actions are clear.

## Acceptance and review questions

- Can the user identify what they are buying, how it will be fulfilled, what payment will be used, and the exact total from the final decision region?
- Can every material component of the total be reconstructed and can the user see it update after a relevant choice?
- Does the final action name the commitment rather than merely advancing the interface?
- Can the user correct an item, address, participant, fulfillment choice, payment method, or promotion without losing unrelated valid state?
- Are review, processing, confirmed, failed, and fulfilled states visually and behaviorally distinct?
- Are cancellation, refund, eligibility, timing, seat, or delivery consequences repeated before commitment?
- Are optional additions and communication preferences clearly optional and separately consented?
- If urgency is shown, can the user identify the exact expiring condition and continue to inspect cost and terms?
- Does confirmation provide a durable record, next step, retrieval or tracking path, and support or recovery access?
