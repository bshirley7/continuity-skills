# Risk-Based Test Design

Read this reference when creating the goal quality plan, selecting targeted tests, reviewing security, or explaining missing and residual coverage.

## Applicability matrix

| Change | Required focus |
| --- | --- |
| User-visible behavior | Success, empty, error, boundary, accessibility, and visual/manual evidence when automation is insufficient |
| API or interface | Contract compatibility, validation, authorization, errors, serialization, and consumers |
| Data model or migration | Forward and rollback behavior, integrity, idempotency, partial failure, and representative scale |
| Authentication or permissions | Allowed and denied paths, privilege boundaries, session or token handling, and audit evidence |
| File path or subprocess | Untrusted input, traversal, confinement, argument arrays, exit status, timeout, and secret-safe output |
| Dependency change | Lockfile integrity, compatibility, advisories, provenance, build and runtime behavior |
| Scheduled or background work | Idempotency, retries, concurrency, stale recovery, timeout, observability, and duplicate prevention |
| Configuration | Defaults, invalid values, drift, precedence, migration, and fail-closed behavior |
| Documentation or memory only | Link, schema, factual consistency, privacy, and installer or retrieval behavior as applicable |

## Evidence rules

- Use repository-native checks first.
- Add focused regression tests for the changed behavior when a practical test surface exists.
- Record manual review method and result; “reviewed” alone is not evidence.
- Treat flaky, skipped, unavailable, or not-run checks as findings with impact and follow-up.
- A scanner pass does not replace trust-boundary review.
- Final evidence is valid only for the clean committed source fingerprint and exact command set.

## Good residual-risk statement

“Automated coverage verifies grouping and keyboard behavior. Visual density was reviewed at configured viewports. No automated screen-reader environment is available; semantic roles were inspected and the limitation remains for human review.”

Weak: “Tests pass; accessibility should be fine.”

## Handoff checklist

- Acceptance criteria map to checks or explicit evidence.
- Changed risks map to regression and security review.
- Commands, outputs, exit status, commit, branch, plan, behavior, and source fingerprint are recorded.
- Findings and residual risk are explicit.
- The current passing report is handed to `$continuity-merge`; failures return to execution without weakening scope or gates.
