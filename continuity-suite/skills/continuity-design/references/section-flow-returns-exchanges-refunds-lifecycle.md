# Returns, exchanges, and refunds lifecycle

## Generalized principles

- Start remedy from the durable transaction record: identify order, item or service, quantity, variant, seller or provider, fulfillment, payment allocation, delivery or service date, current status and policy source; show the remedy window and whether it is based on purchase, shipment, delivery, activation or discovery of a problem; distinguish statutory, warranty, protection-plan and discretionary rights; and never make people reconstruct a purchase the system already knows.
- Offer remedies that fit the problem and preserve choice: distinguish cancellation, return, repair, replacement, same-item or alternate exchange, partial refund, original-payment refund, credit, dispute and safety report; explain eligibility and tradeoffs before selection; allow item and quantity granularity; use reasons to route help and evidence rather than silently remove valid remedies; and do not foreground faster credit or exchange while hiding an available monetary refund.
- Calculate value restoration transparently: show item amount, quantity, discounts, promotions, tax, original and return shipping, service or restocking charges, used benefits, partial fulfillment, prior credits and remaining installment balance; identify the exact refund destination and expected amount and timing; distinguish estimated from final value pending inspection; explain rounding and allocation across mixed tenders; and never describe store credit as equivalent to cash without explicit choice.
- Request only evidence proportionate to the claim: state what condition, defect, non-delivery, mismatch or damage information is needed and why; support concise text, accessible media and existing order or tracking evidence; preserve privacy and bystander data; allow correction; distinguish optional evidence from required proof; never require impossible documentation for a transient failure; and do not execute or publicly expose supplied content during review.
- Turn approval into workable logistics: offer eligible store, carrier, locker, pickup, mail or no-return methods with cost, distance, accessibility, packaging, hazardous or sensitive-item rules, label or code format, deadline and assistance; provide a durable label, QR code or instructions that can be retrieved and printed or used without printing; record handoff and tracking; and account for people who lack transport, packaging, printers, smartphones or nearby locations.
- Model remedy as a multi-party state machine: requested, awaiting evidence, approved, label or pickup ready, handed off, in transit, received, inspecting, accepted, partially accepted, rejected, replacement reserved, replacement shipped, refund instructed, payment credited, completed, expired, canceled or appealed; identify who owns the next action and deadline; separate merchant approval from carrier custody, platform decision and payment settlement; and announce changes without treating request submission as completion.
- Treat exchange and replacement as new inventory commitments linked to the original remedy: identify exact variant, price difference, hold, shipment, service date and fallback if unavailable; preserve the return timeline while replacement capacity is checked; avoid charging twice without clear authorization and reversal; distinguish advance replacement from replacement after receipt; and allow conversion to refund when the replacement cannot be fulfilled.
- Make rejection, partial outcomes and appeal specific and repairable: identify the item, evidence, policy version, condition finding, amount and responsible decision-maker; show what was accepted and what remains disputed; provide a bounded correction, additional-evidence, seller response, platform review or payment-dispute path as appropriate; pause avoidable collections on genuinely disputed value; preserve communications and custody evidence; and never close the only support route because an automated or first-line decision rejected the claim.

## Variation levers

- Reduce evidence and logistics burden when the business caused non-delivery, cancellation, wrong-item fulfillment or a known defect.
- Use no-return refunds for low-value, unsafe, perishable or operationally wasteful items when fraud and environmental costs support it.
- Increase custody, inspection and condition detail for high-value, serialized, hazardous or authenticated goods.
- Offer advance replacement only with clear authorization, temporary charge and automatic release behavior.
- Coordinate payment pauses and credits explicitly when a lender, wallet, gift balance or mixed tender sits between merchant and customer.

## Tensions and tradeoffs

- Low-friction remedies reduce burden while increasing abuse and reverse-logistics cost.
- Detailed evidence improves adjudication while collecting sensitive content and delaying relief.
- Fast store credit restores spending power while locking value to the same merchant.
- Inspection protects against condition disputes while extending uncertainty after the person relinquishes the item.
- Advance replacement reduces downtime while risking duplicate charges and inventory scarcity.
- Automated decisions increase speed while making unusual but valid claims harder to explain.

## Failure modes

- The person must search policy pages and re-enter order facts the service already holds.
- Selecting a reason silently removes refund and leaves only credit or exchange.
- A refund amount omits discounts, tax, fees, shipping, mixed tender or installment effects.
- The flow requires media evidence without explaining necessity, privacy or alternatives.
- A return method assumes a printer, car, smartphone or accessible carrier location.
- Requested, approved, received, refunded and credited collapse into one completed state.
- A replacement becomes unavailable after the original remedy deadline expires.
- A partial rejection gives no item-level reason, calculation or appeal.
- The platform, seller, carrier and lender each send the person to another party.

## Anti-patterns

- Receipt reconstruction tax.
- Reason-based remedy disappearance.
- Black-box refund math.
- Proof maximalism.
- Logistics by privilege.
- Refund-state compression.
- Exchange deadline trap.
- Opaque partial denial.
- Multi-party support carousel.

## Acceptance and review questions

- Does remedy start from the exact transaction, item, fulfillment, payment, policy and deadline context already known?
- Are cancellation, repair, replacement, exchange, monetary refund, credit, dispute and safety paths visible without reason-based steering?
- Is item-level value restoration traceable across discounts, tax, fees, shipping, installments, mixed tenders and timing?
- Is requested evidence necessary, explained, accessible, privacy-preserving, correctable and proportionate?
- Are method cost, distance, accessibility, packaging, label, deadline, handoff and tracking workable without assumed equipment?
- Are request, approval, custody, inspection, replacement, refund instruction, payment credit, rejection and appeal distinct states?
- Does exchange preserve the original remedy while exact replacement inventory, price, authorization and fallback are resolved?
- Do partial or rejected outcomes provide item-level reasons, calculations, evidence, correction, appeal and responsible support?
