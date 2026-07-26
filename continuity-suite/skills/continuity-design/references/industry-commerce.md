# Commerce

## Generalized principles

- Keep product identity, selected variant, seller, stock, fulfillment destination, delivery promise, return condition, and current price together at the purchase action.
- Support comparison through aligned decision fields, stable units, definition help, variant equivalence, and visible differences rather than forcing memory across product pages.
- Make the checkout total reconstructable from items, quantities, discounts, delivery, service charges, regulatory fees, tax, tip, deposits, subscriptions, and temporary authorization.
- Carry material substitution, cancellation, return, refund, delivery, and charge-timing conditions into final review beside the action they govern.
- Treat fulfillment and return as explicit lifecycles with current stage, next expected event, deadline, affected item, amount, payment destination, tracking, support, and safe cancellation.
- Separate transaction success from operational completion so payment, acceptance, picking, shipment, delivery, pickup, return receipt, validation, and refund cannot collapse into one completed label.
- Design merchant operations around exceptions and accountable inventory truth, distinguishing draft, active, archived, unavailable, committed, available, on-hand, damaged, and unsaved state.
- Connect merchant-facing catalog, orders, fulfillment, customer communication, policy, marketing, finance, and channel scope without allowing promotional presentation to obscure operational state.

## Variation levers

- Use comparison tables for specification-heavy goods and variant sheets for bounded visual choices.
- Use itemized checkout for high-fee or variable fulfillment and a compact review for low-variance digital delivery.
- Use stage timelines for returns and shipment and state tables for merchant inventory.
- Use temporary authorization explanations when final totals can change after fulfillment.
- Use direct edit routes for payment, address, quantity, substitution, and fulfillment before commitment.
- Use bulk merchant actions only when selected scope and downstream channel effects remain visible.

## Tensions and tradeoffs

- Rich product detail supports choice while delaying action.
- Aligned comparison improves judgment while flattening qualitative differences.
- Full fee disclosure increases trust while making checkout feel more complex.
- Fast checkout reduces friction while hiding fulfillment consequences.
- Detailed return tracking supports recovery while prolonging uncertainty.
- Dense merchant tables increase control while amplifying bulk-action risk.

## Failure modes

- The purchase action is detached from seller, variant, stock, delivery, or return terms.
- Comparison uses inconsistent fields or units.
- Checkout hides a fee, tip, deposit, subscription, or authorization amount.
- Material fulfillment terms disappear before final commitment.
- Return status lacks deadline, next event, item, amount, or refund destination.
- Payment success is presented as fulfillment completion.
- Merchant inventory collapses committed, available, and on-hand quantities.
- Bulk catalog changes hide affected channels, markets, or variants.

## Anti-patterns

- Comparing products through unrelated marketing cards.
- Changing a variant while silently changing seller or return terms.
- Showing only a final checkout total.
- Disclosing variable charges after order placement.
- Using in progress with no next event or deadline.
- Calling a refund complete before its destination is credited.
- Editing inventory with no unsaved state.
- Publishing merchant changes to every channel by default.

## Acceptance and review questions

- Does purchase review preserve product, variant, seller, stock, destination, delivery, return, and price?
- Are comparable attributes aligned, defined, and expressed in stable units?
- Can the total be reconstructed from every charge, discount, and authorization?
- Are substitution, cancellation, return, refund, and charge terms present at commitment?
- Do fulfillment and return states expose stage, next event, deadline, item, amount, and support?
- Are payment and operational completion distinct?
- Does merchant inventory preserve every quantity and publication state?
- Do bulk actions expose affected variants, channels, markets, and consequences?
