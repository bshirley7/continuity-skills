# Offline work, synchronization, and conflict recovery

## Generalized principles

- Define and expose distinct durability states around the exact object or action: unsaved in memory, saved locally, prepared for offline use, queued for transmission, sending, accepted remotely, synchronized across relevant devices, completed by the business process, failed, conflicted or cancelled; use plain language, timestamps and affected scope so a positive local-save signal is never mistaken for remote acceptance or final completion.
- Let people prepare for disconnection deliberately: show which items, dependencies, attachments, permissions and capabilities will remain available; estimate size and freshness; expose download progress, storage location and expiry; support item and collection scopes, pause, resume, remove and refresh; and warn before travel, field work or commitment when required content is not ready.
- Preserve local intent through interruption and reconnection: save drafts and edits durably, keep an inspectable queue with original order and dependencies, assign a stable identity to every mutating action, resume transfers safely, avoid duplicate side effects, and allow retry, cancel, export or copy without forcing the person to reconstruct work from memory.
- Represent freshness, authority and degraded capability explicitly: show last successful synchronization, data origin, local and remote revision, pending collaborator changes and unavailable actions; continue safe read or local work where possible; never present cached values as current for inventory, balance, permission, safety or legal state; and require renewed validation before high-consequence commitment when freshness matters.
- Resolve divergence without silent overwrite: identify the exact fields, blocks, files or actions in conflict; preserve both versions and authorship; compare meaningful differences in context; auto-merge only demonstrably compatible changes; let authorized people keep, combine, duplicate or defer; preview consequences; and retain reversible history with a clear resulting canonical version.
- Close the loop after reconnection: summarize what synchronized, what remains pending, what failed permanently, what was deduplicated and what needs a decision; link each status to evidence and recovery; notify proportionately when background work completes or stalls; retain diagnostic history without exposing sensitive content; and measure lost work, duplicate effects, convergence time, unresolved conflicts and successful recovery.

## Variation levers

- Increase freshness validation, explicit confirmation and human conflict review with financial, legal, safety, permission or inventory consequence.
- Queue low-risk reversible work automatically; require review before transmitting stale, irreversible or context-sensitive intent.
- Use field-level or block-level merging for independently editable structures and version-level preservation when semantic interaction makes automatic merge unsafe.
- Adapt download size, refresh cadence and background transfer to storage, battery, metered network, privacy and user-selected constraints.

## Tensions and tradeoffs

- Optimistic local work preserves momentum while allowing decisions against stale remote state.
- Automatic synchronization reduces effort while obscuring when and why data moved between devices or accounts.
- Last-write-wins converges quickly while silently discarding valid concurrent intent.
- Persistent local copies improve availability while increasing device loss, shared-device and retention exposure.
- Frequent status messaging builds confidence while turning normal background convergence into interruption noise.

## Failure modes

- Saved means only local persistence but visually implies completed submission.
- An offline badge does not identify item freshness, missing dependencies, expiry or restricted capabilities.
- Retry creates duplicate orders, signatures, messages, uploads or payments.
- Reconnection silently replaces local work with a remote version.
- Last-write-wins discards semantically important concurrent edits.
- A spinner has no object, start time, queue position, cancellation or failure path.
- Cached high-consequence data is shown without a last-updated time or validation requirement.
- The user learns that sync failed only after leaving the device or missing a deadline.
- Conflict recovery requires copying content from an inaccessible raw diff.
- Removing an offline copy appears to delete the canonical remote object.

## Anti-patterns

- False completion checkmark.
- Meaningless offline badge.
- Duplicate-on-retry.
- Reconnect overwrite.
- Timestamp decides truth.
- Orphan spinner.
- Fresh-looking stale data.
- Silent background failure.
- Raw-diff recovery.
- Local removal ambiguity.

## Acceptance and review questions

- Can people distinguish local save, offline availability, queued transmission, remote acceptance, cross-device synchronization and final business completion for the exact object or action?
- Before disconnection, can they verify scope, dependencies, freshness, size, progress, expiry and available capabilities?
- Are local changes and queued actions durable, inspectable, safely retryable, cancellable and exportable without duplicate side effects?
- Does stale or degraded state identify origin, last synchronization, missing capabilities and required revalidation for consequential decisions?
- Are conflicts compared at a meaningful grain with both versions preserved, safe merge choices, consequence preview and reversible history?
- After reconnection, can people verify completed, pending, failed, deduplicated and decision-required work and recover every unresolved item?
