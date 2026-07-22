# Spatial context and location agency

## Generalized principles

- Model location as contextual evidence rather than a coordinate: preserve subject or device, purpose, source, place meaning, precision, accuracy, timestamp, route or boundary, recipient, inference, retention and uncertainty; distinguish observed position from address, saved place, predicted destination, visited place and claimed identity; and never let a precise-looking map erase the limits of the underlying evidence.
- Apply least privilege across precision, duration and operating state: request access only when the person invokes a location-dependent task; prefer approximate, one-time and foreground access; escalate to precise or background access only with a demonstrated need and contextual explanation; preserve manual and non-location alternatives; show active use; and make later narrowing or revocation easy and effective.
- Communicate spatial uncertainty in the representation and the language: expose accuracy, freshness, source, coverage and last update where consequence depends on them; use ranges, areas or confidence rather than a false exact point; distinguish stale, cached, unavailable, paused, offline and permission-denied states; provide an accessible non-map description and correction path; and test indoors, underground, in dense cities, rural areas and constrained networks.
- Make spatial commitment explicit: before dispatch, booking, delivery, navigation, sharing, geofencing or physical automation, present the exact operational place or boundary, entrance or meeting detail, recipient, route or radius, precision, duration and consequence; keep exploration distinct from application; require confirmation proportionate to harm; and preserve a source-bound correction and recovery route.
- Design sharing for safety under unequal power: verify audience and scope, expose forwarding and shared-device risks, limit precision and duration, keep a visible active state and end receipt, support discreet pause or stop where coercion or stalking is plausible, avoid revealing protective actions through unsafe channels, and offer trusted human or emergency support without promising safety that the product cannot guarantee.
- Protect contextual integrity and secondary inference: treat home, work, health, worship, political activity, relationships and routines inferred from movement as sensitive even when individual points appear ordinary; bind collection and use to the stated context; minimize access, linkage, analytics, advertising, brokerage and retransmission; disclose recipients and retention; and provide access, correction, objection, export and deletion with propagation limits explained.
- Evaluate the complete location lifecycle by downstream harm and remedy: test permission comprehension, manual alternatives, accuracy and correction, route and boundary mistakes, stale tracking, battery and connectivity loss, unauthorized recipients, link forwarding, shared-device exposure, revocation, stopping, history deletion and inferred-place misuse across affected groups; preserve audit and contestability without turning location controls into surveillance.

## Method

- Map the person, device, place, route, boundary, purpose, recipient, precision, update cadence, duration, retention, inference and downstream action for every location flow.
- Separate sensed position, searched address, saved place, operational entrance, route position, shared position, inferred place and identity claim.
- Choose the least-privileged access and provide manual or non-location alternatives before designing the system permission request.
- Represent uncertainty, stale and offline state, correction, spatial commitment, sharing lifecycle, safe stop, history and deletion explicitly.
- Evaluate privacy, accessibility, coercion, safety, false precision, secondary inference and remedy across real environments and affected groups.

## Ethical safeguards

- Do not request precise or background location merely for personalization, analytics, advertising or speculative future value.
- Do not make sensor permission a hidden requirement when address, place, area or non-location input can complete the task.
- Do not present a current-position dot, inferred place or predicted route as exact, fresh or identity-verifying evidence.
- Do not let map exploration silently commit a destination, pickup, boundary, recipient or automation.
- Do not share continuously without a named or inspectable audience, bounded duration, visible state and reliable stop control.
- Do not expose a coercion-sensitive stop, support action or safety plan through an unsafe shared-device notification.
- Do not infer or monetize sensitive visits, routines or relationships beyond the context in which location was provided.
- Do not imply that stopping future collection deletes prior records, recipient copies or downstream inferences when it does not.
- Do not use detailed location history as a substitute for proportional authentication, authorization or proof.

## Variation levers

- Reduce precision from point to area as the task moves from pickup, navigation or emergency response toward discovery, content relevance or analytics.
- Increase contextual explanation, recurring indication, recipient control, safe stopping and retention limits from one-time foreground lookup toward continuous background sharing.
- Increase confirmation and human recovery as a wrong point, route, boundary or recipient could cause financial, safety, health, legal or physical harm.
- Prefer local processing and short retention for geofences and connected mobility when the service can operate without transmitting raw movement.

## Tensions and tradeoffs

- Exact location improves coordination while enabling sensitive-place inference and surveillance.
- Persistent sharing may support safety while increasing coercion, stalking and shared-device exposure.
- Visible accuracy and uncertainty improve honesty while complicating a familiar map presentation.
- Location history supports receipts, return and dispute resolution while increasing breach and secondary-use harm.
- Auditability supports contestability while excessive tracking can become the very privacy harm under review.

## Failure modes

- The permission request omits purpose, precision, duration, background behavior or a manual alternative.
- A precise map marker hides an old timestamp, wide accuracy radius or inferred source.
- Location is used as proof of identity, presence or intent without a justified evidence chain.
- A changed route or boundary applies before the person reviews its consequence.
- Recipients, link forwarding, duration or background updates are unclear during live sharing.
- Stopping is hard to find, unsafe on a shared device or lacks confirmation that access ended.
- Sensitive-place and routine inferences are reused for an unrelated purpose.
- Revocation stops the interface indicator but not collection, retention or downstream sharing.
- The only alternative to inaccurate sensing is repeated retry rather than correction or manual entry.

## Anti-patterns

- Coordinate without context.
- Always and precise by default.
- Perfect pin theater.
- Location as identity proof.
- Explore and apply.
- Unbounded live share.
- Unsafe visible stop.
- Sensitive-place repurposing.
- Revocation theater.

## Acceptance and review questions

- Does the design represent subject, purpose, source, place meaning, precision, accuracy, timestamp, boundary, recipient, inference, retention and uncertainty rather than only a coordinate?
- Is access least-privileged across approximate or precise, one-time or persistent, foreground or background, with contextual explanation, manual alternatives, active indication and effective revocation?
- Are accuracy, freshness, stale, cached, offline, paused and denied states communicated accessibly without false exactness, with correction across relevant environments?
- Before a location-dependent commitment, can people review the exact place, boundary, route, recipient, precision, duration and consequence and recover from a mistake?
- Does sharing account for audience, forwarding, unequal power, shared devices, discreet stopping, end confirmation and realistic support without overpromising safety?
- Are sensitive-place and routine inferences minimized, context-bound, protected from unrelated use, and subject to access, correction, objection, export and deletion?
- Has the full lifecycle been evaluated for downstream harm, affected groups, false precision, stale tracking, recipient misuse, revocation failure and meaningful remedy?
