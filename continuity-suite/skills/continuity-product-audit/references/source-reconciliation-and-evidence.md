# Source reconciliation and evidence

## Authority is contextual

Use the approved goal as the authority for current delivery scope. A project
intent document or PRD is canonical context, but its applicability still
depends on revision and the approved goal. Canonical documentation and current
project memory explain existing decisions and constraints. Roadmap material
describes time horizon; future work is not a current defect. Insights and
observed code or product behavior are evidence, not permission.

When sources conflict, record the conflict. Do not silently choose the source
that makes the product appear compliant. A current approved decision may
supersede older documentation; otherwise use `contradicted` or `unverifiable`
and route the ambiguity back to planning.

## Evidence quality

Prefer evidence that identifies the target, observation time, journey,
viewport or environment, and source version. Use project-relative sanitized
files when evidence belongs in the candidate commit. Use a reference plus
SHA-256 when the tool produces an external but stable artifact. Never persist
credentials, cookies, access tokens, raw private captures, personal data, or
unredacted production records.

Screenshots establish visible state but not hidden behavior. Pair them with
interaction, DOM, accessibility, command, code, or document evidence when the
claim depends on those layers. A browser adapter may collect evidence, but the
Continuity plan, record, hashes, and finding lifecycle remain portable.

## Finding decisions

| Observed relationship | Status | Typical scope | Gate impact |
| --- | --- | --- | --- |
| Requirement is demonstrably satisfied | aligned | current-goal | none |
| Requirement is only partly satisfied | partial | current-goal or later | blocking or advisory |
| Required behavior is absent | missing | current-goal or later | blocking or advisory |
| Product conflicts with applicable intent | contradicted | current-goal | blocking |
| Previously aligned behavior degraded | regressed | current-goal | blocking |
| Evidence cannot establish the answer | unverifiable | current-goal or context-only | blocking or advisory |
| Source explicitly belongs to a later horizon | future-roadmap | later | advisory |
| Source or observation is outside the approved objective | out-of-scope | out-of-scope | none |

Severity describes consequence. Confidence describes strength of the
conclusion. Scope and time horizon decide whether the finding belongs in the
current goal. Gate impact follows from those fields; it must not be used to
pull later work into the active delivery.

