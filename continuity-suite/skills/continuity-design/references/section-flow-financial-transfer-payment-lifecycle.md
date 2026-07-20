# Financial transfer and payment lifecycle

## Generalized principles

- Start with recipient certainty: show the intended person or organization, verified name where available, account or handle type, masked destination, institution or network, country and currency; distinguish saved, recent, contact-derived, scanned and manually entered recipients; disclose match, close-match, no-match or unverifiable results without converting a weak signal into false assurance; and require deliberate review when the destination is new, changed or high consequence.
- Make the transfer route and value reconstructable before commitment: show funding source, available balance or credit implication, amount sent, currency, exchange rate and its validity window, provider and third-party fees, taxes, amount expected by the recipient, rail, speed, availability date, limits and material protections; distinguish estimates from guaranteed values and never describe an instant initiation as guaranteed recipient access.
- Provide one exact, editable review surface before final authorization: repeat recipient identity and destination, amount, source, currency, fees, rate, arrival, schedule, recurrence, memo or reference and protection type; label the final action with amount and consequence; preserve edits without discarding valid data; use authentication to confirm the current actor rather than as a substitute for transaction comprehension; and state when cancellation or reversal ends.
- Represent transfer status as a state machine: drafted, authorized, scheduled, submitted, accepted by provider, processing, compliance review, sent to network, settled, available to recipient, collected, rejected, canceled, expired, returned, reversed or disputed; identify which party owns the next action, what money is reserved or debited, the expected next event and time, and whether the sender can still edit, cancel, recall or only request return.
- Issue a durable receipt tied to the exact transaction: preserve transfer and settlement references, sender and recipient, source and destination, amount, currency, rate, fees, schedule, initiation and completion timestamps, status history and support rights; let people retrieve and share an appropriately redacted proof without exposing full account details; and never let animation, chat acknowledgement or a generic checkmark replace auditable settlement evidence.
- Make limits and review holds specific without exposing evasion detail: name the affected amount or capability, current used and remaining limit where safe, reset period, verification or documentation needed, expected review time, money location, scheduled-transfer effect and support path; preserve entered details; distinguish fraud, sanctions, account, liquidity, recipient and technical causes at a level that enables repair; and do not invite repeated submissions that could create duplicates.
- Design failure and return as recoverable financial outcomes: state whether nothing moved, funds are reserved, sender was debited, network rejected, recipient institution returned, recipient declined, or a refund is pending; show exact amount and fees restored or retained, reason, correction path, retry safety, new rate or fee effects, expected restoration date and dispute route; preserve the original record and use an idempotent retry or explicit new-transfer boundary.
- Connect cancellation, recall, scam report, unauthorized-transfer report and recipient-return request without conflating them: show which remedy applies to current authorization and settlement state, deadlines, evidence, responsible institution, provisional or final credit, and likely limits; transfer existing transaction evidence across parties; support human escalation for livelihood or essential-payment impact; and never imply that a submitted request has reversed a final payment.

## Variation levers

- Increase name-match and new-recipient friction as irreversibility and amount rise.
- Expose rate validity, recipient amount and intermediary uncertainty for cross-border transfers.
- Add role, approval, invoice and reconciliation context for business payments.
- Use explicit collect or accept states when the recipient must claim funds.
- Increase exception, return and dispute detail for instant and final rails.

## Tensions and tradeoffs

- Speed reduces anxiety while shrinking verification and cancellation time.
- Recipient masking protects privacy while weakening identity certainty.
- Fraud warnings protect users while habituation and generic alarms reduce attention.
- Detailed failure reasons aid repair while revealing control logic.
- Saved recipients reduce effort while stale or compromised details create risk.
- Immediate receipts reassure while account debit may precede recipient availability.

## Failure modes

- A contact name is treated as verified account ownership.
- The recipient amount omits fees or exchange uncertainty.
- Authentication occurs without an exact transaction review.
- Sent, settled and received collapse into one success state.
- A receipt has no reference, timing or durable status history.
- A compliance hold gives no money location or expected next step.
- Retrying a failure risks a duplicate transfer.
- A recall request is presented as if funds have already returned.

## Anti-patterns

- Contact-name certainty.
- Recipient-value omission.
- Authenticate instead of review.
- Success-state compression.
- Celebratory receipt evaporation.
- Opaque money hold.
- Duplicate-by-retry.
- Recall-as-refund fiction.

## Acceptance and review questions

- Is recipient identity and destination evidence proportional to risk without false verification?
- Can the sender reconstruct source, amount, rate, fees, recipient value, rail, timing, limits and protection before commitment?
- Does the final review show one exact editable transaction and the actual point of irreversibility?
- Are authorization, processing, settlement, recipient availability, return, reversal and dispute distinct?
- Does the durable receipt preserve references, values, times, status history and safe proof sharing?
- Do limits and holds explain affected scope, money location, repair, timing and duplicate-safe continuation?
- Does failure or return show what moved, what was restored, what changed and whether retry creates a new transfer?
- Are cancellation, recall, scam, unauthorized and recipient-return remedies correctly separated and evidence-linked?
