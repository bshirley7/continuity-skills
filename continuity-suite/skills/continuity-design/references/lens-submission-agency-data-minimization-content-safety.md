# Submission agency, data minimization, and content safety

## Generalized principles

- Justify the submission at the field and purpose level: ask only for information necessary to deliver the stated outcome, explain why a file is needed and whether another path can satisfy the requirement, avoid collecting whole documents when a smaller attestation or field is adequate, accept interoperable formats where feasible, and periodically review whether the content, metadata and retained copies remain relevant and necessary.
- Preserve selected-item agency: use system or bounded pickers that grant access only to explicitly chosen items when possible, distinguish browsing from granting access and granting access from submitting, show selection order and limits, let people deselect or revoke, expose whether captions, location or other metadata will travel, and do not request broad library or storage permission merely to reduce implementation effort.
- Make disclosure reviewable before consequence: identify the selected item, destination, recipient or audience, purpose, visibility, transformation and retention; provide a safe preview or summary without executing untrusted content; separate local selection, transfer and final submission when risk merits it; allow correction and cancellation; and avoid defaults or automatic upload behavior that makes an exploratory choice an irreversible disclosure.
- Communicate lifecycle state as verifiable facts: distinguish queued, transferred, server-received, validating, scanning, processing, accepted, ready, rejected, quarantined, failed, withdrawn and deleted; announce progress and results programmatically without stealing focus; identify partial success per item; never use a single success mark to imply that content is safe, processed, shared or durably retained; and attach retry, correction and support to the state that actually failed.
- Treat every supplied file as untrusted while keeping security language useful: validate on the service against an allowlist and task semantics, inspect extension, declared type, signature, structure, size, archive expansion and authorization as applicable, isolate storage and processing, scan or reconstruct where risk warrants, avoid exposing system paths or internals, and tell the person whether the issue is format, size, corruption, encryption, duplication, malware, policy or service failure without claiming certainty the controls cannot provide.
- Provide equivalent and resilient interaction: use persistent labels and restriction hints, keyboard-operable native controls, visible focus and adequate targets; make drag-and-drop optional; announce selection, count, progress, errors and completion; preserve a progressive fallback when enhancement fails; account for limited bandwidth and data cost; keep successful items and surrounding work through partial failure; and test with screen readers, voice, touch, keyboard and interrupted connectivity.
- Bind content to access and retention boundaries after submission: show owner, containing record, audience, version and status; authorize every preview, download, replacement and removal rather than only the initial upload; explain reuse on shared or public devices; distinguish deleting a reference, revoking access and erasing retained content; support correction and withdrawal where appropriate; and retain only what policy and purpose require, with accountable review of copies, logs, derivatives and backups.
- Evaluate the complete sociotechnical path, not only the picker: test necessity and comprehension with intended users; threat-model malicious, mistaken and coerced submission; examine sensitive metadata, bystanders and third-party information inside files; review moderation and staff access; define what happens when scanning is unavailable or inconclusive; measure abandonment, correction and false rejection alongside completion; and provide human recourse for consequential decisions based on submitted content.

## Method

- State the exact purpose, minimum information, acceptable alternative, audience, processing and retention for every requested file or media item.
- Map browsing, selected access, local preview, transfer, validation, scanning, processing, acceptance, sharing, withdrawal and deletion as separate states and authority changes.
- Design the smallest-access source picker, pre-submit review, per-item state feedback, recovery and accessible fallback.
- Define service-side validation, isolation and safe-preview boundaries without exposing internals or overclaiming certainty.
- Test accessibility, bandwidth, partial failure, sensitive metadata, malicious content, mistaken recipient, revocation and retention behavior.
- Audit necessity, access, copies, derivatives, error rates, correction, withdrawal and human recourse after release.

## Ethical safeguards

- Do not require a whole document when a smaller data element or nonfile alternative can meet the purpose.
- Do not request an entire photo or storage library when selected-item access is available.
- Do not make file selection itself an undisclosed upload or public submission.
- Do not preview untrusted active content in a way that can execute or expose other data.
- Do not call content safe merely because the transfer, extension check or one scan completed.
- Do not clear successful items or unrelated work because one file fails.
- Do not reveal sensitive server paths, rules or internals in an error message.
- Do not retain originals, metadata, derivatives or backups indefinitely without purpose and policy.
- Do not make automated rejection of consequential evidence final without correction or appropriate human recourse.

## Variation levers

- Increase review, separation of selection and submission, and human recourse with audience breadth, sensitivity, automation and consequence.
- Minimize to selected-item access for media; require broader library access only for explicit ongoing library-management capabilities.
- Use asynchronous queues and resumability for large or many files while keeping per-item state and cancellation visible.
- Increase validation, isolation and safe-preview controls as formats become active, complex, compressed or externally shareable.
- Shorten retention and reduce derived copies when files contain identity, health, financial, child, location or third-party information.

## Tensions and tradeoffs

- Fewer submission steps improve completion while reducing the chance to catch the wrong file or audience.
- Flexible formats improve inclusion while increasing processing and safety surface.
- Detailed errors improve recovery while potentially disclosing validation internals.
- Reusable uploads reduce repeated burden while increasing exposure on shared devices and extending retention.
- Aggressive scanning reduces some threats while creating false confidence, delay and false rejection.

## Failure modes

- A service collects a full document or media library for a narrowly scoped need.
- The picker looks embedded in the app and people cannot tell which items have been granted.
- Selecting an item immediately sends it to a recipient the person has not reviewed.
- Transfer completion is announced as processing, safety and publication completion.
- A generic invalid-file error gives no actionable repair or misstates the risk.
- Drag-and-drop and visual progress have no keyboard or assistive equivalent.
- Later preview, download and deletion paths bypass the access rules applied at upload.
- Originals, metadata and derivatives persist after their purpose or consent ends.
- Automated rejection blocks a consequential claim with no correction or human path.

## Anti-patterns

- Document maximalism.
- Permission for convenience.
- Picker as silent disclosure.
- Success-state compression.
- Security theater error.
- Visual-only transfer state.
- Upload-only authorization.
- Derivative retention shadow.
- Unappealable evidence rejection.

## Acceptance and review questions

- Is every requested file justified by an exact purpose, with minimum information, alternatives and periodic deletion review?
- Does the source flow grant access only to selected items and distinguish browsing, access, transfer and submission?
- Can people review item, metadata, destination, audience, transformation and retention before consequential disclosure?
- Are transfer, receipt, validation, scanning, processing, acceptance, readiness, quarantine, withdrawal and deletion stated separately and accessibly?
- Are untrusted files validated, isolated and previewed safely with precise but nonrevealing recovery language?
- Do labels, hints, focus, targets, keyboard, assistive announcements, fallbacks, bandwidth and partial failure preserve equivalent completion?
- Are owner, record, audience, version, access, reuse, correction, withdrawal, copies, derivatives and retention governed after upload?
- Has the complete path been tested for necessity, coercion, mistakes, sensitive metadata, staff access, false rejection and human recourse?
