# Continuity Provider Adapter Contract

A Codex, Claude Code, Cursor, Windsurf, or external scheduler integration is conformant only when it satisfies this runtime contract. Writing a registration receipt is not sufficient.

1. Run the portfolio supervisor on the configured sweep interval with an authenticated agent identity and a stable provider task ID.
2. Call `portfolio actions` with that task ID, a unique sweep ID, and the exact registered workspace roots. A successful call refreshes the expiring registration heartbeat.
3. Start one isolated project task for each returned `due` or `retry` action. Pass its exact project root, action, idempotency key, claim token, and due goal ID to `scheduler run-start`. Before a code-changing `dispatch`, acquire the project's remote lease with the exact goal ID. A lease conflict or unreachable remote is a non-launch state.
4. Treat `manual-only`, `waiting-for-review`, `capacity-deferred`, `backoff`, `active`, and `stale` as non-launch states. Never manufacture or reuse a claim.
5. Send run heartbeats while a child task is active and always record `scheduler run-finish`. Let `scheduler recover` handle stale runs; do not infer a replacement decision.
6. Keep provider credentials, workspace roots, task IDs, claims, and run ledgers in private local state. Never place them in project commits or portfolio summaries.
7. Demonstrate conformance by allowing `project doctor` to observe at least two successive sweeps, launching a claimed no-op review or report action, rejecting a replayed claim, showing that an expired supervisor becomes `stale`, and proving a second workstation cannot acquire an active execution lease.

For Codex, generate the task definition with `scheduler adapter codex render` and verify observed operation with `scheduler adapter codex verify`. Do not hand-maintain a divergent prompt or schedule when a rendered definition is available.

Provider-native task creation remains the adapter's responsibility because agent surfaces expose different scheduling APIs. Continuity supplies the fail-closed project protocol, liveness lease, capacity reservation, and claim validation shared by every adapter.
