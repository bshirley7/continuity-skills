# Continuity Portfolio Supervisor

Run at the registered sweep interval using the developer-local workspace roots recorded with the scheduler task. Make one call with every root, repeating the flag: `continuity --json portfolio actions --root <root-one> --root <root-two>`. The CLI applies the smallest project concurrency cap across the returned runnable set and marks excess work `capacity-deferred`.

For every `due` or `retry` action, start a separate task in that repository. Do not start `capacity-deferred` work during that sweep. Before project work, record `scheduler run-start <action>` with the supplied idempotency key and provider task ID. Run `project doctor`, apply `$continuity-local`, and follow the matching installed action prompt. Send `scheduler run-heartbeat` during long work and finish with `scheduler run-finish --status succeeded|failed|blocked` plus a concise evidence summary. The CLI rejects a successful dispatch finish until its goal is `review-ready`.

When an action reports `recovery-required`, run project-local `scheduler recover` before retrying. Recovery may block a matching stale execution and release only its matching project lock. Never start duplicate idempotency keys, exceed retry or concurrency limits, infer approval, centralize private state, or continue after a failed doctor.

Review and dispatch run only on nights preceding configured business days. Reports run on configured business-day mornings. The supervisor owns triggering only; every project's instructions, notes, approvals, locks, evidence, and run ledger remain authoritative inside that project.
