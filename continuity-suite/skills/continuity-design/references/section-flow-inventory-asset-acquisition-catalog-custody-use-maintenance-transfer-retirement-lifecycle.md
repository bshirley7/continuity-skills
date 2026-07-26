# Inventory and asset acquisition, catalog, custody, use, maintenance, transfer, and retirement lifecycle

## Generalized principles

- Preserve one lifecycle identity while distinguishing item definition from physical instance: identify organization and owner, item type, model and variant, exact asset or lot, manufacturer and supplier, SKU and barcode, serial or tag, acquisition source and date, location, custodian, condition, serviceability, financial class, current state and revision; bind receipt, count, assignment, maintenance, incident, transfer and end-of-life evidence to it; and never let a product name, SKU, employee, bin or accounting line become the asset by itself.
- Separate catalog readiness from operational availability: distinguish draft, active, orderable and sellable definitions from received, inspected, accepted, put away, on hand, available, reserved, committed, in transit, quarantined, damaged, missing and disposed quantities or assets; expose governing location and effective time; and never infer usable supply from active status, price, purchase or a nonzero total.
- Treat receipt as source-linked verification: compare ordered, shipped and received identity and quantity; capture supplier, destination, receiver, time, unit and cost, lot or serial, condition, inspection, discrepancy, rejection and evidence; separate acceptance and putaway from arrival; preserve partial receipt and later correction; and never let scan success, parsed paperwork or a delivered carrier state create available stock automatically.
- Make quantity truth reconstructable: define units and conversions; show expected, counted, variance and financial or service effect; require reason, actor, time, source and review for adjustments; preserve prior values, unmatched and excluded items, recount and correction; scope every count to exact location, item and cutoff; and never overwrite history with a set quantity or present a successful save as verified inventory.
- Represent location, possession, custody and accountability as different relationships: show where an asset is expected, who physically holds it, who may use it, who accepts responsibility, transfer route and current evidence; require explicit handoff and receipt for assignment, loan, shipment, storage, return and transfer; preserve due date and condition; and never infer custody from address, assignee selection, shipping label or organizational ownership.
- Keep condition, availability, serviceability and safety distinct: let people report defects and damage, isolate or quarantine affected items, identify consequence and related assets or lots, prevent unsafe allocation, preserve inspection and repair decisions, and require competent return-to-service evidence where consequence warrants it; never let an in-stock, in-use, repaired or green state prove fitness.
- Make maintenance and inspection an exact-asset work lifecycle: identify trigger, risk, required competence, procedure, isolation, parts, planned and actual downtime, findings, work performed, test, attachments, approver, next interval and residual restriction; connect prior history and affected operations; separate work complete from verified safe return; and never use a reminder, checklist completion or public maintenance status as serviceability evidence.
- Handle loss, theft, damage, recall and quarantine as accountable exceptions: capture reporter, time, last verified custody and location, affected identifiers and related stock, risk, containment, notifications, search or investigation, replacement, remedy, authority and closure evidence; block inappropriate use without erasing the asset; and never convert an unresolved exception directly into zero stock, write-off or archive.
- Treat retirement as a decision tree rather than an archive action: distinguish excess declaration, transfer, repair, redeployment, donation, resale, parts recovery, write-off, data sanitization, recycling, hazardous handling and destruction; preserve title, authority, condition, residual value, recipient or processor, chain of custody and completion evidence; and never let depreciation, end-of-life date or archive reason prove safe and lawful disposition.
- Measure lifecycle value and burden, not only stock and book value: combine availability, fulfillment, utilization, downtime, overdue inspection, repair recurrence, loss, unsafe or inaccessible use, worker effort, assignment inequity, useful-life extension, reuse, recovery and disposal evidence; segment by asset class, location and affected population; and never optimize maximum utilization or low inventory by hiding resilience, safety, accessibility or maintenance debt.

## Variation levers

- Increase lot, expiry, temperature, recall and chain-of-custody controls for regulated or perishable inventory.
- Increase serialized identity, assignment, warranty, security and sanitization for workforce technology.
- Increase inspection competence, isolation, calibration and return-to-service controls for safety-critical equipment.
- Increase location, reservation, transfer, replenishment and cycle-count controls for distributed warehouses.
- Increase residual value, depreciation, title, reuse and disposal authority for capital and public assets.

## Tensions and tradeoffs

- Fast catalog creation versus complete operational identity.
- Editable stock versus evidence-backed reconciliation.
- Visible custody versus worker privacy and surveillance.
- High utilization versus resilience, maintenance and safety.
- Rapid return to service versus competent verification.
- Simple archive versus secure, safe and circular end of life.

## Failure modes

- A product definition is mistaken for a physical asset.
- Active or purchased state is presented as available stock.
- A set-quantity action erases count provenance.
- Assignment or address is mistaken for accepted custody.
- In-stock or repaired status hides unsafe condition.
- Maintenance completion lacks test and return authority.
- Loss or recall disappears into adjustment or archive.
- End-of-life omits reuse, sanitization and disposal evidence.

## Anti-patterns

- SKU as asset.
- Active means available.
- Magic stock total.
- Assignee as custody.
- Green means safe.
- Checked means maintained.
- Exception write-off.
- Archive as disposal.

## Acceptance and review questions

- Can people distinguish item type, variant, lot and unique asset while preserving one lifecycle identity?
- Are catalog, receipt, inspection, acceptance, putaway, allocation, condition and availability represented separately?
- Can each receipt be reconstructed against order, shipment, destination, quantity, condition and discrepancy evidence?
- Do counts and adjustments retain unit, scope, expected, counted, variance, reason, actor, review and correction?
- Are location, possession, permitted use, custody, responsibility and accepted handoff distinct?
- Can unsafe, damaged, recalled, quarantined and unavailable items be contained without disappearing?
- Does maintenance bind exact asset, competence, procedure, work, test, downtime and return-to-service authority?
- Do loss, theft, recall and damage preserve containment, investigation, remedy and closure evidence?
- Does retirement evaluate reuse, repair, transfer, sanitization, recycling and disposal before archive?
- Do metrics expose safety, accessibility, burden, resilience, maintenance debt and circularity alongside value?
