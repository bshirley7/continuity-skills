---
name: share-project-notes
description: Prepare, approve, publish, and import sanitized project note packets through isolated Git branches and human-reviewed PRs. Use when one developer intentionally shares selected local insights with the current project inbox.
---

# Share Project Notes

Read `.agents/references/continuity-contract.md`, `.agents/references/development-assurance-standard.md`, and `$project-continuity-local` before acting.

## Workflow

1. Select private atomic note IDs; never select an entire raw capture by implication.
2. Run `continuity note share prepare <note-id>... --target-project <current-project> --sender <name>`. Review the sanitized packet, provenance, classifications, roadmap links, and content hash.
3. Obtain explicit approval naming the packet ID, exact version, and target project. Record it with `continuity note share approve`.
4. Run `continuity note share publish <packet-id>`. It must use an isolated `continuity-notes/<date>/<packet>` branch, privacy and secret checks, a commit, push, and human-reviewed PR.
5. After merge, each developer runs `continuity note share import`. Import deduplicates packets into the private triage inbox.
6. Triage imported content normally. Promote documentation, roadmap, memory, goals, or code only through their independent approval paths.

## Guardrails

- Packets contain sanitized atomic content only. Raw snapshots and private ledgers never travel through Git.
- V1 packets target the current project inbox; named-recipient and cross-project routing are not implemented.
- Packet versions are immutable after approval. Any edit produces a new version and invalidates prior approval.
- Every packet sets `execution_authorized: false`; packets never update another developer's private state or authorize code, systems, goals, roadmap truth, or memory.
- Never force-push, auto-merge, embed credentials, publish from a dirty checkout, or bypass remote, authentication, privacy, or security checks.
