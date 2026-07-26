# Order fulfillment, delivery, and handoff lifecycle

## Generalized principles

- Preserve one durable fulfillment record from commitment through handoff: identify order, item, quantity, variant, seller, fulfillment method, destination or pickup site, payment state and original promise; split status by package, item or service unit when custody diverges; link replacements and remedies without overwriting the original history; and never make people infer which item a carrier event affects.
- Model fulfillment as accountable stages rather than a decorative progress bar: confirmed, allocated, preparing, substituted, backordered, packed, label created, handed to carrier, in network, customs or authentication review, out for delivery, ready for pickup, attempted, delivered, collected, partially completed, delayed, lost, damaged, canceled or returned; identify actor, source event, timestamp, next expected event and available control at every stage.
- Treat time as a revisable promise with provenance: show the original date or window, current estimate, confidence or range where material, last update, reason for change, dependency and next reassessment; distinguish ship-by, carrier acceptance, arrival, out-for-delivery, pickup readiness and hold deadline; notify meaningful slippage before the promise expires; and offer reschedule, consent-to-delay, cancellation or remedy according to the actual contract.
- Make custody and responsibility explicit across merchant, seller, preparer, authenticator, warehouse, carrier, courier, pickup site, delegate and recipient: show who physically or operationally controls the item now, who owns the next action and which party can correct the issue; distinguish electronic label creation from possession, route proximity from committed arrival and platform aggregation from source-of-record status.
- Provide safe, accessible handoff controls: let people review and, while feasible, change address, safe place, access note, contact method, delivery window, signature, identity, pickup person or collection site; state lock times and consequences; avoid exposing sensitive goods or full personal details in notifications and proof; offer non-map, non-audio and assisted alternatives; and protect courier and recipient location beyond the active operational need.
- Treat pickup as its own state contract: distinguish preparing, ready, checked in, waiting, handed off, collected, expired and returned; show exact site, hours, collection window, item scope, code or identification, delegate rules, accessibility, storage or temperature conditions and assistance; do not send arrival prompts before readiness; and retain recovery when the merchant cannot locate a supposedly ready order.
- Bind completion claims to proportionate evidence: identify whether delivered means carrier scan, geofence, photo, signature, access-code exchange, locker deposit, merchant handoff or recipient confirmation; show time and sufficiently precise location without exposing unnecessary private data; allow the recipient to report not received, wrong place, missing item, damage or unsafe condition; and never treat weak automated evidence as conclusive against a timely challenge.
- Turn exceptions into item-specific agency: state what changed, affected item or package, money and authorization state, current custody, revised expectation and cause at a useful level; offer safe address correction, redelivery, pickup, substitution approval, cancellation, refund, replacement, missing-item report or escalation as applicable; preserve prior messages and proof; and avoid a merchant-carrier-platform support carousel.

## Variation levers

- Increase identity, privacy and safe-handoff controls for health, alcohol, regulated and high-value goods.
- Increase temperature and expiration detail for prepared food, groceries and medicine.
- Increase package-level splitting for marketplaces and multi-origin orders.
- Increase delegate, vehicle, loading and site detail for bulky pickup.
- Reduce live-location precision and retention once operational coordination ends.

## Tensions and tradeoffs

- Precise ETA reduces uncertainty while creating false certainty and pressure on workers.
- Live location supports coordination while exposing courier and recipient privacy.
- Detailed stages improve orientation while amplifying anxiety and notification volume.
- Safe-place delivery increases convenience while weakening proof and security.
- Strong identity checks protect goods while creating accessibility and delegation burdens.
- Centralized tracking simplifies access while obscuring source disagreements.

## Failure modes

- One order status hides divergent package or item states.
- A label-created event appears as carrier possession.
- The ETA changes without preserving the original promise or reason.
- A map implies precise progress despite stale or modeled location.
- Pickup reminders arrive before the order is ready.
- Delivered is based on an unexplained scan and treated as unchallengeable.
- A missing item closes the whole order or requires full-order reconstruction.
- Merchant, carrier and platform each redirect the person.

## Anti-patterns

- Order-level state flattening.
- Label-equals-shipped.
- Promise history erasure.
- Map-marker certainty theater.
- Premature pickup summons.
- Scan-as-proof absolutism.
- Partial exception collapse.
- Fulfillment support carousel.

## Acceptance and review questions

- Does one durable record preserve item-level identity, payment, method, destination, promise and history?
- Are operational stages source-linked, timestamped, accountable and tied to the next event and available control?
- Are original and revised promises, uncertainty, change reasons and consent or remedy options visible?
- Can people distinguish custody, responsibility and source-of-record across every party?
- Are handoff controls accessible, time-bounded, privacy-preserving and safe for recipient and worker?
- Does pickup expose readiness, site, window, item scope, verification, delegation, storage and recovery?
- Is every completion claim labeled by its actual evidence and open to proportionate challenge?
- Do exceptions preserve item, custody, money, history and a direct corrective path without support redirection?
