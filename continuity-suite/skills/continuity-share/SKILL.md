---
name: continuity-share
description: Prepare, approve, publish, and import sanitized project note packets through isolated Git branches and human-reviewed PRs. Use when one developer intentionally shares selected local insights with the current project inbox.
---

# Continuity Share

Read `.agents/references/continuity-contract.md`, `.agents/references/development-assurance-standard.md`, and `$continuity-local` before acting.

Read [workflow handoffs](../../references/workflow-handoffs.md), [output quality rubrics](../../references/output-quality-rubrics.md), and [sanitization and import](references/sanitization-and-import.md) before preparing, reviewing, publishing, or importing a packet. Apply the privacy, provenance, and recipient-need sections of [decision lenses](../../references/decision-lenses.md).

## Workflow

1. Select private atomic note IDs; never select an entire raw capture by implication.
2. Run `continuity note share prepare <note-id>... --target-project <current-project> --sender <name>`. Review the sanitized packet, provenance, classifications, roadmap links, and content hash.
3. Obtain explicit approval naming the packet ID, exact version, and target project. In a signed-approval project, the named human records it with `continuity note share approve ... --signing-key <ssh-private-key>` using a key already trusted by `continuity approval trust add`. Never select a private key for the human or infer approval.
4. Run `continuity note share publish <packet-id>`. It must use an isolated `continuity-notes/<date>/<packet>` branch, privacy and secret checks, a commit, push, and human-reviewed PR.
5. After merge, each developer runs `continuity note share import`. Import deduplicates packets into the private triage inbox.
6. Triage imported content normally. Promote documentation, roadmap, memory, goals, or code only through their independent approval paths.

## Guardrails

- Packets contain sanitized atomic content only. Raw snapshots and private ledgers never travel through Git.
- V1 packets target the current project inbox; named-recipient and cross-project routing are not implemented.
- Packet versions are immutable after approval. Any edit produces a new version and invalidates prior approval.
- Signed packet approval binds the packet ID, exact version, target project, content hash, approver identity, approval text, time, and nonce. `publish` re-verifies that receipt against the project allowlist and fails closed on a missing, stale, modified, or untrusted signature.
- Every packet sets `execution_authorized: false`; packets never update another developer's private state or authorize code, systems, goals, roadmap truth, or memory.
- Never force-push, auto-merge, embed credentials, publish from a dirty checkout, or bypass remote, authentication, privacy, or security checks.

Imported packet items become private atomic captures with stable packet provenance and `execution_authorized: false`; they enter the same `note triage`, search, pattern, memory, and planning flow as local captures.

## Handoff

Run project-level `continuity workflow status` before selection, `continuity workflow status --packet-id <packet-id>` after preparation or publication, and `continuity workflow status --note-id <imported-note-id>` after import. Imported notes begin a new private dated lifecycle and must pass normal triage and relationship confirmation. A prepared or published packet remains a sharing workflow and cannot advance a product goal.
