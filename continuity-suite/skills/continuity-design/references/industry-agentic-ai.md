# Agentic AI interfaces

## Generalized principles

- Translate the user's request into an inspectable execution contract: intended outcome, target objects and people, scope, constraints, assumptions, inputs, allowed tools and actions, expected artifacts, approval points, stop conditions, and verifiable completion criteria.
- Separate proposed plan from execution and expose each step's purpose, dependencies, tool, data source, authority, expected change, state, progress evidence, output, cost or usage, and next decision; allow pause, interruption, correction, and bounded resume.
- Request permission at the narrowest consequential boundary with service and account, data read or written, exact operation, targets and recipients, persistence, credential or memory use, expected consequence, reversibility, and whether consent applies once, for this task, or until revoked.
- Keep evidence and epistemic state visible: distinguish source observation, retrieval, model inference, hypothesis, recommendation, forecast, generated artifact, attempted action, tool response, and independently verified result; attach provenance, time, coverage, conflicts, and uncertainty.
- Present consequential output as a reviewable diff or decision package with original state, proposed state, affected scope, rationale, evidence, alternatives, risks, unresolved questions, editable fields, accept or reject granularity, and the exact action approval would authorize.
- Declare completion only from verified external state: identify attempted and successful actions, changed and unchanged targets, partial failures, pending work, notifications, artifacts, evidence, cost, residual risk, and rollback or correction path; retain an immutable task and tool history.

## Variation levers

- Use conversational summaries for orientation and structured plans, diffs, permissions, and receipts for consequential details.
- Allow automatic execution only for bounded, reversible, low-consequence actions within explicit scope and limits.
- Require step approval, action approval, or final-review approval according to consequence, externality, uncertainty, and reversibility.
- Use progressive disclosure for tool traces while keeping current state, authority, scope, evidence, blockers, and next decision visible.
- Offer branching, retry, regenerate, edit, resume, cancel, compensate, and rollback as distinct operations with explicit state effects.

## Tensions and tradeoffs

- Conversational simplicity reduces friction while hiding operational state and authority.
- Detailed plans improve control while becoming stale as tools return new evidence.
- Broad permissions reduce repeated prompts while increasing unintended access and action.
- Autonomous execution improves speed while reducing opportunities to correct mistaken assumptions.
- Verbose traces improve auditability while exposing sensitive data and overwhelming review.
- A confident completion message improves closure while masking partial or unverified results.

## Failure modes

- The agent changes scope without surfacing the revision.
- A plan is displayed as if it were already executing.
- Permission does not name the exact tool, account, data, action, or duration.
- A recommendation is visually indistinguishable from a completed action.
- Sources support only part of a generated claim.
- A review omits the original state or affected targets.
- Cancellation leaves in-flight or completed actions ambiguous.
- A retry duplicates an external action.
- Partial failure is summarized as success.
- Completion is inferred from model output rather than verified state.

## Anti-patterns

- Working on it without current step.
- Approve everything.
- Reasoning theater.
- Tool use hidden behind typing animation.
- Citations as decoration.
- Accept without a diff.
- Cancel without compensation state.
- Retry an external mutation blindly.
- Done because the model said so.
- Human-like agency without accountable authority.

## Acceptance and review questions

- Does the execution contract name outcome, targets, scope, constraints, assumptions, inputs, tools, actions, artifacts, approvals, stops, and completion criteria?
- Are plan and execution distinct, with step purpose, dependency, tool, data, authority, change, state, evidence, output, usage, and next decision?
- Does each permission identify service, account, data, operation, targets, persistence, credential or memory, consequence, reversibility, and consent duration?
- Are observation, retrieval, inference, hypothesis, recommendation, forecast, artifact, attempt, response, and verified result distinct and traceable?
- Do consequential outputs show original, proposed state, scope, rationale, evidence, alternatives, risk, questions, editable fields, granularity, and exact authorization?
- Does completion reflect verified external state, partial failure, pending work, notifications, artifacts, usage, residual risk, and rollback?
- Can users pause, correct, resume, cancel, compensate, and audit the task without losing state?
