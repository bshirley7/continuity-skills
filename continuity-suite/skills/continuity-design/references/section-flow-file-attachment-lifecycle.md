# File and attachment lifecycle

## Generalized principles

- Frame the file request before presenting a picker: name the purpose, destination or affected record, whether submission is required, who can access the result, acceptable alternatives, supported types, count and size limits, expected processing and retention; ask for a file only when its information is necessary; and avoid a generic attachment icon when the person must infer what evidence, format or disclosure is expected.
- Offer source choices that match the task and minimize access: distinguish capture now, choose specific local or cloud items, select an existing workspace object, paste a link and enter equivalent information manually; preserve the system picker and keyboard-operable file input as dependable paths; make drag-and-drop an enhancement; and request access only to the items the person explicitly chooses rather than an entire library or storage area.
- Stage selection before disclosure: show a recognizable thumbnail or type marker, full usable name, type, size, count, order and destination; expose metadata or sensitive fields that may travel when relevant; let people preview, rename, reorder, replace and remove individual items; distinguish local selection from transfer; and require a separate, accurately labeled submit or send action when recipient, publication, cost or consequence merits review.
- Model each file as an independent stateful object: selected locally, queued, transferring with measurable progress, paused, canceled, uploaded, validating, scanning, processing, converted, ready, partially usable, rejected, failed, stale, replaced, quarantined or removed; communicate state with text and programmatic updates rather than a spinner or color alone; retain completed items when one fails; and provide state-appropriate cancel, retry, resume, inspect or replace actions.
- Validate early without pretending client checks are final: explain restrictions before selection, identify the affected file and exact fix, distinguish type, size, count, empty, corrupt, encrypted, duplicate, template, malware and processing errors, preserve the person's other work, and never label a transfer complete or safe merely because bytes reached the service; if rejection follows processing, keep the reason and a recovery path attached to the durable item.
- Keep uploaded content anchored to ownership and access context: show the containing record, workspace, conversation, audience or recipient; distinguish private draft, shared, published and externally accessible states; preserve uploader, source, time, version and processing provenance when relevant; warn before a file crosses an access boundary; and do not infer that an attachment inherits safe visibility merely because the surrounding screen is familiar.
- Design the post-upload lifecycle: support preview or safe download, replacement and version distinction, access change, correction, withdrawal, retention explanation and removal; clarify whether delete removes a reference, a version, all copies or only the person's access; preserve audit evidence when policy requires it without making content indefinitely available; and ensure interrupted sessions can resume without duplicate uploads or lost state.
- Test the lifecycle across modalities and adverse conditions: keyboard, screen reader, voice, touch and drag input; long and duplicate names, unsupported and deceptive extensions, many and very large files, slow or lost connectivity, backgrounding and refresh, partial success, server rejection, unsafe content, expired sessions and revoked access; keep progress, errors and completion announced; and preserve a simple native-input fallback when enhancements fail.

## Variation levers

- Require a stronger review and confirmation stage as recipient breadth, publication, sensitivity, irreversibility or processing cost increases.
- Use immediate transfer for low-risk reversible drafts; defer transfer until explicit submission when selection itself would disclose sensitive content.
- Prefer one file per request for infrequent public-service tasks; support queues, bulk control and resumability for expert or media workflows.
- Expose more provenance, version and processing detail for evidence, regulated records and collaborative assets than for disposable conversational attachments.
- Provide capture and system-picker shortcuts on mobile while retaining explicit source, selection and destination context.

## Tensions and tradeoffs

- Automatic upload reduces steps while making local selection itself a disclosure event.
- Broad format support improves access while increasing validation, conversion and safety complexity.
- Rich previews improve review while exposing sensitive content on shared screens or unsafe files.
- Background processing reduces waiting while making completion, failure and later retrieval easier to miss.
- Durable version history supports accountability while conflicting with withdrawal, minimization and storage limits.

## Failure modes

- The interface asks for a file without explaining why, where it goes or what alternatives exist.
- The application requests an entire media library when one selected item would suffice.
- Choosing a file immediately sends it to an unseen recipient or public destination.
- One spinner represents transfer, scanning, conversion and availability.
- A failed item clears successful files or destroys surrounding form work.
- The error says invalid file without naming the file, rule or repair.
- An uploaded attachment loses its workspace, audience, owner or version context.
- Delete, replace and remove-access actions have indistinguishable effects.
- A custom drop zone has no keyboard, assistive or native-input fallback.

## Anti-patterns

- Context-free paperclip.
- Whole-library permission for one item.
- Selection equals silent submission.
- Omnibus upload spinner.
- All-or-nothing queue failure.
- Invalid file mystery.
- Orphaned attachment.
- Ambiguous deletion semantics.
- Drag-only upload.

## Acceptance and review questions

- Does the request name purpose, destination, necessity, audience, alternatives, limits, processing and retention before selection?
- Do source choices minimize access while preserving native, keyboard, touch and drag paths?
- Can people inspect, rename, reorder, replace and remove selected items before consequential disclosure?
- Are transfer, validation, scanning, processing, readiness, failure, quarantine and removal modeled as distinct per-file states?
- Do restrictions and errors identify the file, exact problem and recovery without losing successful items or surrounding work?
- Does every attachment retain record, workspace, audience, owner, source, time, version and access context appropriate to its consequence?
- Are replacement, version, download, access change, correction, withdrawal, retention and deletion effects explicit?
- Has the lifecycle been tested across modalities, file extremes, connectivity loss, partial success, unsafe content and enhancement failure?
