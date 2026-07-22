# Data import, export, and migration

## Generalized principles

- Before transfer, identify the source, destination, data objects, selected scope, format, account, access permission, transformation, overwrite or duplication behavior, limits, and whether the operation copies, moves, continuously synchronizes, or deletes anything.
- Make transformation inspectable before commitment through representative preview, field or schema mapping, required values, excluded columns, encoding and format assumptions, destination structure, record counts, and explicit treatment of existing data.
- Represent transfer as durable operational state: queued, checking, blocked, running, partially complete, complete, expired, or failed, with destination, timing, delivery route, retry, support, history, and safe navigation away from background work.
- Close the loop with a verifiable result that separates created, updated, skipped, duplicated, associated, missing, and failed items; provide error evidence, correction or rollback options, retained-source state, and a direct route to inspect the destination.

## Variation levers

- Use direct preview and mapping for bounded files, compatibility analysis and staged copying for databases, and persistent status plus access controls for connected synchronization.
- Offer granular scope and format for portability requests, while providing a safe complete export when category-level selection would create misleading omissions.
- Scale rollback, checkpointing, approval, and dry-run requirements with data volume, overwrite risk, relational complexity, and operational consequence.

## Tensions and tradeoffs

- Automatic mapping reduces effort while increasing silent transformation risk.
- Granular export scope improves control while making completeness harder to judge.
- Background processing preserves productivity while weakening visibility and perceived control.
- Continuous synchronization improves freshness while creating persistent access, provenance, and deletion obligations.

## Failure modes

- The interface accepts a file or connection before explaining destination, overwrite, transformation, or access scope.
- A preview shows rows but hides type inference, excluded fields, invalid values, duplicates, or relational consequences.
- Progress is reported as a spinner without durable status, safe exit, timing, retry, or history.
- Completion reports success without separating created, updated, skipped, failed, or missing data.
- Disconnecting a source leaves unclear whether copied data, derived data, credentials, or ongoing synchronization remain.

## Anti-patterns

- Upload and hope.
- Magic mapping.
- Spinner migration.
- Success without accounting.
- Export with unknown scope.
- Sync without provenance.
- Disconnect without aftermath.

## Acceptance and review questions

- Are source, destination, account, scope, format, access, transformation, overwrite, limits, and operation type explicit?
- Can people inspect representative data, mapping, exclusions, invalid values, duplicates, and destination structure before commitment?
- Does background work have durable status, timing, safe exit, history, retry, and support?
- Does completion distinguish created, updated, skipped, duplicated, associated, missing, and failed items?
- Can people inspect the destination and correct, retry, or roll back affected data?
- For connected sources, are ongoing access, provenance, refresh state, disconnect behavior, and retained data clear?
