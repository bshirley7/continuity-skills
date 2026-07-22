# Booking, reservation, and availability lifecycle

## Generalized principles

- Define the bookable resource and constraints before showing availability: keep service or inventory type, provider, location, duration, capacity, participants, eligibility, accessibility features, dependencies and time zone attached to every slot; distinguish an exact resource from a category guarantee; and do not present a time as interchangeable when room, equipment, staff, fare, accessibility or preparation requirements differ.
- Represent availability as a scoped and time-sensitive fact: show the search criteria and freshness, distinguish available, limited, unavailable, tentative, requestable, held and sold states, explain material eligibility or dependency checks, offer nearby dates, times, locations, providers or equivalent resources, and avoid implying that viewing or selecting a slot guarantees inventory until the system has actually reserved it.
- Separate selection, hold, request and confirmation: state when capacity is temporarily held, for whom, for how long and what preserves or releases it; use truthful countdowns only for real expiring holds; distinguish a submitted request or pending participant acceptance from a confirmed reservation; survive payment or network retry without duplicate bookings; and tell people when availability changed before asking them to choose again.
- Make scarce-capacity alternatives and waitlists actionable: state whether joining reserves nothing, the selection or priority rule, what position or wait estimate means and does not mean, how offers are delivered, how long they remain open, whether accepting replaces an existing booking and how to leave; preserve non-digital or assisted paths where access matters; and do not use a waitlist as a misleading substitute for unavailable service or as an undisclosed marketing list.
- Review the complete commitment in one coherent step: identify resource, provider, location, local date and time with zone, duration, participants, accessibility arrangements, itemized total, deposit or authorization, cancellation and no-show policy, refund or credit conditions, included and excluded services and final action effect; preserve edit links without clearing valid choices; and avoid introducing mandatory fees or stricter terms after scarcity pressure has begun.
- Create a durable reservation object after commitment: provide an unambiguous status such as requested, pending, held, confirmed, changed, canceled, completed or missed; show confirmation identifier, source of truth, itinerary or appointment details, preparation, arrival and accessibility instructions, contact route and calendar export; send notifications through chosen channels; and never use payment success alone as proof that capacity is confirmed.
- Make change, cancellation and provider disruption first-class: expose self-service reschedule and cancel where allowed, calculate fee, refund, credit, capacity and dependent-item effects before confirmation, distinguish person-initiated cancellation from provider cancellation or significant change, preserve the original details and notice history, offer equivalent alternatives without hiding a refund path, and restore released capacity or waitlist opportunity consistently.
- Test the lifecycle as an allocation system: verify keyboard, screen-reader, voice and touch access to calendars and slots; time zones, daylight-saving changes and overnight spans; simultaneous demand, stale inventory, duplicate actions, hold expiry, partial payment and reconnect; accessible-resource guarantees; waitlist ordering, offer expiry and digital exclusion; provider changes, overbooking and no-shows; and audit who receives which inventory, price, priority and recovery rather than measuring conversion alone.

## Variation levers

- Increase exact-resource guarantees and accessibility detail when substituting a nominally similar resource could make the reservation unusable.
- Use immediate confirmation for deterministic inventory; use explicit request and participant-acceptance states when fulfillment depends on people or later qualification.
- Use a short truthful hold for high-contention paid inventory; avoid holds when they create unnecessary scarcity or block equitable access.
- Use first-come ordering only when access speed is a reasonable allocation rule; consider batches, priority classes or lotteries when bots and unequal connectivity dominate.
- Increase refund, alternative and human-support prominence as provider disruption, health, travel dependency or financial consequence increases.

## Tensions and tradeoffs

- Real-time availability improves agency while becoming stale under simultaneous demand.
- Temporary holds protect checkout while withholding capacity from others.
- First-come booking is simple while rewarding automation, connectivity and constant attention.
- Waitlists improve utilization while creating opaque hope and repeated interruption.
- Strict cancellation policies protect provider capacity while shifting disruption risk to people.
- Automated substitution restores service while violating exact accessibility, location, provider or itinerary needs.

## Failure modes

- A slot is shown without the service, resource, provider, location, duration or time zone it represents.
- Selecting a slot appears confirmed even though qualification or participant acceptance remains pending.
- A countdown resets or describes general sales pressure rather than a real personal hold.
- A waitlist hides its ordering, offer window, replacement effect or lack of guarantee.
- Mandatory fees or cancellation terms appear only after urgency and effort have accumulated.
- Payment succeeds but no durable confirmation or source-of-truth status exists.
- Provider cancellation foregrounds credit or substitution and obscures refund or support.
- An accessible resource is replaced by a nominally similar but unusable one.
- Allocation success is measured without examining bots, digital access, protected needs or group disparities.

## Anti-patterns

- Context-free time slot.
- Selection-confirmation blur.
- Resetting scarcity clock.
- Opaque hope queue.
- Late commitment terms.
- Receipt as reservation.
- Refund-obscuring recovery.
- Accessibility by category label.
- Conversion-only allocation.

## Acceptance and review questions

- Does every slot retain resource, service, provider, location, duration, capacity, eligibility, accessibility and time-zone context?
- Are availability scope, freshness, qualification and tentative, held, requestable and confirmed states truthful?
- Are selection, personal hold, submitted request, participant acceptance, payment and confirmation distinct and resilient?
- Do alternatives and waitlists explain ordering, estimates, notification, expiry, replacement, exit and non-guarantee?
- Does final review expose all details, accessibility arrangements, total price, deposits, terms, exclusions and action effect?
- Does the durable reservation show exact status, identifier, details, preparation, arrival, contact, calendar and notification state?
- Do change, cancellation, disruption, alternatives, refunds and released-capacity effects remain understandable and recoverable?
- Has allocation been tested for accessibility, time, concurrency, holds, overbooking, bots, digital exclusion and outcome disparities?
