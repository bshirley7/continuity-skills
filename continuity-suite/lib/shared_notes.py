"""Explicit, hash-bound, non-authorizing shared-note packet transport."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import runtime as runtime_lib


SECRET_PATTERNS = [
    re.compile(r"(?i)\b(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*\S+"),
    re.compile(r"\b(?:ghp|github_pat|sk-[A-Za-z0-9_-]{8,})[A-Za-z0-9_-]*\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+\S+"),
    re.compile(r"://[^/\s:@]+:[^/\s@]+@"),
]
NOTE_KINDS = {
    "context", "insight", "decision", "question", "documentation-candidate",
    "backlog-candidate", "execution-candidate", "explicit-instruction",
}


class SharedNoteError(RuntimeError):
    pass


def _dump(path: Path, value: Any) -> None:
    runtime_lib.atomic_write_json(path, value)


def _load(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _private(root: Path, config: dict[str, Any]) -> Path:
    value = Path(config.get("private_dir", ".continuity/private"))
    if value.is_absolute() or not (root / value).resolve().is_relative_to(root.resolve()):
        raise SharedNoteError("private_dir escapes the project root")
    return (root / value).resolve()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _find_note(root: Path, config: dict[str, Any], note_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    found = []
    for path in (_private(root, config) / "captures").glob("**/*.json"):
        capture = _load(path, {})
        for item in capture.get("items", []):
            if item.get("item_id") == note_id:
                found.append((capture, item))
    if len(found) != 1:
        raise SharedNoteError(f"Expected one private note {note_id}; found {len(found)}")
    return found[0]


def _sanitize(text: str) -> str:
    normalized = "".join(character for character in text.strip() if character in "\n\t" or ord(character) >= 32)
    if len(normalized) > 12000:
        raise SharedNoteError("Shared note item exceeds the 12,000 character limit")
    for pattern in SECRET_PATTERNS:
        if pattern.search(normalized):
            raise SharedNoteError("Potential secret found; revise the private note or prepare a separately sanitized item")
    return normalized


def _clean_metadata(value: Any, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip() or len(value) > 500 or any(character in value for character in "\r\n\x00"):
        raise SharedNoteError(f"{label} must be a non-empty, single-line string of at most 500 characters")
    return _sanitize(value)


def _payload(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key not in {"content_hash", "approval", "publication", "private_path"}}


def _approval_bytes(approval: dict[str, Any]) -> bytes:
    return (json.dumps(approval, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _allowed_signers(root: Path, config: dict[str, Any]) -> Path:
    relative = Path(config.get("approval_allowed_signers", ".continuity/trusted-approvers"))
    resolved = (root / relative).resolve()
    if relative.is_absolute() or not resolved.is_relative_to(root.resolve()):
        raise SharedNoteError("approval_allowed_signers escapes the project root")
    return resolved


def _sign_approval(root: Path, config: dict[str, Any], path: Path, approval: dict[str, Any], signing_key: str) -> None:
    ssh_keygen = shutil.which("ssh-keygen")
    if not ssh_keygen:
        raise SharedNoteError("ssh-keygen is required for signed packet approvals")
    with tempfile.TemporaryDirectory(prefix="continuity-packet-approval-") as temporary:
        receipt = Path(temporary) / "receipt.json"
        receipt.write_bytes(_approval_bytes(approval))
        result = subprocess.run(
            [ssh_keygen, "-Y", "sign", "-f", str(Path(signing_key).expanduser().resolve()), "-n", "continuity-packet-approval", str(receipt)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        generated = receipt.with_suffix(receipt.suffix + ".sig")
        if result.returncode != 0 or not generated.is_file():
            raise SharedNoteError(f"Unable to sign packet approval: {result.stderr.strip() or result.stdout.strip()}")
        runtime_lib.atomic_write_bytes(path.parent / "approval.sig", generated.read_bytes())
    _verify_approval(root, config, path, approval)


def _verify_approval(root: Path, config: dict[str, Any], path: Path, approval: dict[str, Any]) -> None:
    try:
        runtime_lib.validate_schema_file(approval, Path(__file__).resolve().parents[1] / "schemas" / "packet-approval.schema.json", "packet approval receipt")
    except runtime_lib.RuntimeIntegrityError as exc:
        raise SharedNoteError(str(exc)) from exc
    ssh_keygen = shutil.which("ssh-keygen")
    signature = path.parent / "approval.sig"
    allowed = _allowed_signers(root, config)
    if not ssh_keygen or not signature.is_file() or not allowed.is_file():
        raise SharedNoteError("Signed packet approval is missing its signature or trusted approver allowlist")
    result = subprocess.run(
        [ssh_keygen, "-Y", "verify", "-f", str(allowed), "-I", str(approval.get("approved_by", "")), "-n", "continuity-packet-approval", "-s", str(signature)],
        input=_approval_bytes(approval), capture_output=True, timeout=60, check=False,
    )
    if result.returncode != 0:
        raise SharedNoteError("Packet approval signature is invalid or untrusted")


def _packet_path(root: Path, config: dict[str, Any], packet_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", packet_id):
        raise SharedNoteError("Invalid packet ID")
    return _private(root, config) / "shared-notes" / "outbox" / packet_id / "packet.json"


def prepare(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if not args.note_ids:
        raise SharedNoteError("Prepare requires at least one private note ID")
    if args.target_project != config["project_id"]:
        raise SharedNoteError("V1 packets must target the current project inbox")
    selected = []
    sources = []
    classifications = set()
    for note_id in args.note_ids:
        capture, item = _find_note(root, config, note_id)
        selected.append({"item_id": note_id, "classification": item.get("kind", "context"), "content": _sanitize(str(item.get("text", ""))), "execution_authorized": False})
        sources.append({"capture_id": capture.get("capture_id"), "source_type": capture.get("source_type"), "source_ref_hash": _canonical_hash(str(capture.get("source_ref", "private")))})
        classifications.add(item.get("kind", "context"))
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    seed = _canonical_hash({"project": config["project_id"], "notes": sorted(args.note_ids), "items": selected})[:12]
    packet_id = args.packet_id or f"packet-{seed}"
    path = _packet_path(root, config, packet_id)
    previous = _load(path, {})
    version = int(previous.get("version", 0)) + 1
    if previous:
        archive = path.parent / "versions" / f"v{previous.get('version', version - 1)}.json"
        if not archive.exists():
            _dump(archive, previous)
    sender = _clean_metadata(args.sender, "sender")
    source_pr = _clean_metadata(args.source_pr, "source_pr", optional=True)
    if source_pr and not re.fullmatch(r"https://github\.com/[^/\s]+/[^/\s]+/pull/\d+", source_pr):
        raise SharedNoteError("source_pr must be a canonical GitHub pull-request URL")
    for roadmap_id in args.roadmap_id or []:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", roadmap_id):
            raise SharedNoteError(f"Invalid roadmap ID: {roadmap_id}")
    commit_result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    git_commit = commit_result.stdout.strip()
    if commit_result.returncode != 0 or not re.fullmatch(r"[a-f0-9]{40,64}", git_commit):
        raise SharedNoteError("A valid source Git commit is required before preparing a packet")
    packet = {
        "schema_version": 1,
        "assurance_standard_version": 2,
        "packet_id": packet_id,
        "version": version,
        "source_project_id": config["project_id"],
        "target_project_id": args.target_project,
        "intended_project_inbox": config["project_id"],
        "sender": sender,
        "created_at": stamp,
        "source_commit": git_commit,
        "source_pr": source_pr,
        "classifications": sorted(classifications),
        "items": selected,
        "roadmap_ids": sorted(set(args.roadmap_id or [])),
        "roadmap_relation": args.relation,
        "provenance": sources,
        "deduplication_key": _canonical_hash({"target": args.target_project, "items": selected}),
        "execution_authorized": False,
    }
    packet["content_hash"] = _canonical_hash(_payload(packet))
    _dump(path, packet)
    return {**packet, "private_path": str(path.relative_to(root)), "approved": False}


def approve(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    path = _packet_path(root, config, args.packet_id)
    packet = _load(path, {})
    if not packet or int(args.version) != packet.get("version"):
        raise SharedNoteError("Packet version is missing or stale")
    expected = re.compile(rf"\b{re.escape(args.packet_id)}\b.*\bversion\s+{args.version}\b.*\b{re.escape(packet['target_project_id'])}\b", re.IGNORECASE)
    if not expected.search(args.authorization_text):
        raise SharedNoteError("Approval text must name packet ID, version, and target project")
    current_hash = _canonical_hash(_payload(packet))
    if current_hash != packet.get("content_hash"):
        raise SharedNoteError("Packet content hash is invalid")
    packet["approval"] = {"approved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "approved_by": args.approved_by, "authorization_text": args.authorization_text, "content_hash": current_hash, "version": args.version, "target_project_id": packet["target_project_id"], "packet_id": packet["packet_id"], "nonce": secrets.token_hex(16), "signature_format": "openssh-sshsig-v1" if args.signing_key else "legacy-unsigned"}
    try:
        runtime_lib.validate_schema_file(packet["approval"], Path(__file__).resolve().parents[1] / "schemas" / "packet-approval.schema.json", "packet approval receipt")
    except runtime_lib.RuntimeIntegrityError as exc:
        raise SharedNoteError(str(exc)) from exc
    if config.get("require_signed_approvals", False) and not args.signing_key:
        raise SharedNoteError("This project requires --signing-key for shared packet approval")
    if args.signing_key:
        _sign_approval(root, config, path, packet["approval"], args.signing_key)
    _dump(path, packet)
    return packet["approval"]


def render_packet(packet: dict[str, Any]) -> str:
    metadata = {key: packet[key] for key in ("packet_id", "version", "source_project_id", "target_project_id", "intended_project_inbox", "sender", "created_at", "source_commit", "source_pr", "classifications", "roadmap_ids", "roadmap_relation", "deduplication_key", "content_hash", "execution_authorized")}
    metadata["packet_payload"] = _payload(packet)
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) or value is None or isinstance(value, bool) else value}")
    lines.extend(["---", "", f"# Shared note packet {packet['packet_id']} v{packet['version']}", "", "> This sanitized packet is context only. It does not authorize roadmap, memory, goal, code, or system changes.", "", "## Atomic items", ""])
    for item in packet["items"]:
        lines.extend([f"### {item['item_id']} — {item['classification']}", "", item["content"], ""])
    lines.extend(["## Provenance", "", f"- Source commit: `{packet['source_commit']}`", f"- Source PR: {packet.get('source_pr') or 'none'}", f"- Content hash: `{packet['content_hash']}`", "- Execution authorized: `false`", ""])
    return "\n".join(lines)


def _run(root: Path, *args: str, timeout: int = 60) -> str:
    result = subprocess.run([*args], cwd=root, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise SharedNoteError(result.stderr.strip() or result.stdout.strip() or f"Command failed: {' '.join(args)}")
    return result.stdout.strip()


def publish(root: Path, config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    packet_path = _packet_path(root, config, args.packet_id)
    packet = _load(packet_path, {})
    approval = packet.get("approval")
    if not approval or approval.get("content_hash") != packet.get("content_hash") or approval.get("version") != packet.get("version"):
        raise SharedNoteError("Publish requires an exact current packet approval")
    if config.get("require_signed_approvals", False) or approval.get("signature_format") == "openssh-sshsig-v1":
        _verify_approval(root, config, packet_path, approval)
    if packet.get("target_project_id") != config["project_id"] or packet.get("execution_authorized") is not False:
        raise SharedNoteError("Packet target or authorization boundary is invalid")
    rendered = render_packet(packet)
    _sanitize(rendered)
    date = dt.date.today().isoformat()
    branch = f"continuity-notes/{date}/{packet['packet_id']}"
    relative = Path(".continuity/shared-notes/packets") / date[:4] / f"{packet['packet_id']}-v{packet['version']}.md"
    if args.dry_run:
        return {"dry_run": True, "branch": branch, "path": str(relative), "content_hash": packet["content_hash"], "execution_authorized": False}
    if subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=False).stdout.strip():
        raise SharedNoteError("Source checkout must be clean before publishing a shared-note packet")
    _run(root, "git", "fetch", "origin", config["integration_branch"])
    _run(root, "gh", "auth", "status")
    temp = Path(tempfile.mkdtemp(prefix="continuity-note-"))
    worktree = temp / "worktree"
    _run(root, "git", "worktree", "add", "-b", branch, str(worktree), f"origin/{config['integration_branch']}")
    try:
        target = worktree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        _run(worktree, "git", "diff", "--check")
        _run(worktree, "git", "add", str(relative))
        _run(worktree, "git", "commit", "-m", f"Share note packet {packet['packet_id']} v{packet['version']}")
        _run(worktree, "git", "push", "-u", "origin", branch)
        pr_url = _run(worktree, "gh", "pr", "create", "--base", config["integration_branch"], "--head", branch, "--title", f"Shared note packet: {packet['packet_id']} v{packet['version']}", "--body", "Sanitized project-context packet. Execution is not authorized; human review and merge are required.")
    except Exception as exc:
        raise SharedNoteError(f"Publish stopped; inspect retained worktree {worktree}: {exc}") from exc
    _run(root, "git", "worktree", "remove", str(worktree))
    temp.rmdir()
    publication = {
        "published_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "branch": branch,
        "path": str(relative),
        "pr_url": pr_url,
        "version": packet["version"],
        "content_hash": packet["content_hash"],
    }
    packet["publication"] = publication
    _dump(packet_path, packet)
    return {"published": True, **publication, "execution_authorized": False}


def status(root: Path, config: dict[str, Any], packet_id: str) -> dict[str, Any]:
    packet = _load(_packet_path(root, config, packet_id), {})
    if not packet:
        raise SharedNoteError(f"Unknown packet {packet_id}")
    current_hash = _canonical_hash(_payload(packet))
    approval = packet.get("approval") if isinstance(packet.get("approval"), dict) else {}
    approval_current = bool(
        approval
        and approval.get("content_hash") == packet.get("content_hash") == current_hash
        and approval.get("version") == packet.get("version")
    )
    blockers = []
    if approval_current and (config.get("require_signed_approvals", False) or approval.get("signature_format") == "openssh-sshsig-v1"):
        try:
            _verify_approval(root, config, _packet_path(root, config, packet_id), approval)
        except SharedNoteError as exc:
            approval_current = False
            blockers.append(str(exc))
    publication = packet.get("publication") if isinstance(packet.get("publication"), dict) else None
    publication_current = bool(
        publication
        and publication.get("content_hash") == packet.get("content_hash")
        and publication.get("version") == packet.get("version")
    )
    committed_paths = sorted(
        str(path.relative_to(root))
        for path in (root / ".continuity" / "shared-notes" / "packets").glob(f"**/{packet_id}-v{packet.get('version')}.md")
    )
    imports: list[dict[str, Any]] = []
    inbox = _private(root, config) / "queues" / "shared-notes.jsonl"
    if inbox.is_file():
        for line in inbox.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("content_hash") == packet.get("content_hash"):
                imports.append(record)
    state = "prepared"
    if approval_current:
        state = "approved"
    if publication_current:
        state = "published"
    if committed_paths:
        state = "merged"
    if imports:
        state = "imported"
    if packet.get("content_hash") != current_hash:
        blockers.append("packet content hash is stale")
    return {
        "packet_id": packet_id,
        "version": packet.get("version"),
        "target_project_id": packet.get("target_project_id"),
        "content_hash": packet.get("content_hash"),
        "note_ids": [str(item.get("item_id")) for item in packet.get("items", []) if isinstance(item, dict)],
        "state": state,
        "approval_current": approval_current,
        "publication": publication if publication_current else None,
        "committed_paths": committed_paths,
        "imports": imports,
        "blockers": blockers,
        "execution_authorized": False,
    }


def _metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise SharedNoteError(f"Packet lacks frontmatter: {path}")
    end = text.find("\n---\n", 4)
    result: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, raw = line.split(":", 1)
            raw = raw.strip()
            try:
                result[key] = json.loads(raw)
            except json.JSONDecodeError:
                result[key] = raw
    return result


def import_packets(root: Path, config: dict[str, Any], _args: argparse.Namespace) -> dict[str, Any]:
    ledger_path = _private(root, config) / "shared-notes" / "imported.json"
    ledger = _load(ledger_path, {"hashes": []})
    known = set(ledger.get("hashes", []))
    imported = []
    rejected = []
    for path in sorted((root / ".continuity" / "shared-notes" / "packets").glob("**/*.md")):
        if path.stat().st_size > 1_000_000:
            rejected.append({"path": str(path.relative_to(root)), "reason": "packet exceeds one megabyte"})
            continue
        metadata = _metadata(path)
        if metadata.get("target_project_id") != config["project_id"] or metadata.get("execution_authorized") is not False:
            rejected.append({"path": str(path.relative_to(root)), "reason": "target or authorization boundary"})
            continue
        content_hash = str(metadata.get("content_hash", ""))
        if not re.fullmatch(r"[a-f0-9]{64}", content_hash):
            rejected.append({"path": str(path.relative_to(root)), "reason": "invalid content hash"})
            continue
        payload = metadata.get("packet_payload")
        if not isinstance(payload, dict) or _canonical_hash(payload) != content_hash:
            rejected.append({"path": str(path.relative_to(root)), "reason": "packet content hash mismatch"})
            continue
        if payload.get("target_project_id") != config["project_id"] or payload.get("execution_authorized") is not False:
            rejected.append({"path": str(path.relative_to(root)), "reason": "payload target or authorization boundary"})
            continue
        if content_hash in known:
            continue
        imported_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        packet_id = str(metadata.get("packet_id"))
        capture_id = f"capture-shared-{content_hash[:20]}"
        capture_path = _private(root, config) / "captures" / imported_at[:10] / f"{capture_id}.json"
        note_items = []
        for index, packet_item in enumerate(payload.get("items", []), 1):
            if not isinstance(packet_item, dict) or not str(packet_item.get("content", "")).strip():
                raise SharedNoteError(f"Packet {packet_id} contains an invalid atomic item")
            kind = str(packet_item.get("classification", "context"))
            if kind not in NOTE_KINDS:
                kind = "context"
            note_items.append(
                {
                    "item_id": f"note-shared-{content_hash[:16]}-{index}",
                    "source_item_id": packet_item.get("item_id"),
                    "kind": kind,
                    "text": str(packet_item["content"]).strip(),
                    "created_at": imported_at,
                    "updated_at": imported_at,
                    "occurred_at": imported_at,
                    "occurred_at_confidence": "capture-time",
                    "perspective": "external",
                    "sentiment": "unknown",
                    "occurrence_type": "observation",
                    "impact": "unknown",
                    "confidence": "medium",
                    "actionability": "context",
                    "stakeholders": [str(payload.get("sender", "shared-contributor"))],
                    "themes": ["shared-note", packet_id],
                    "routing_status": "captured",
                    "work_status": "open",
                    "execution_authorized": False,
                }
            )
        capture = {
            "schema_version": 1,
            "capture_id": capture_id,
            "captured_at": imported_at,
            "project_id": config["project_id"],
            "repository": str(root),
            "source_type": "shared-packet",
            "source_ref": str(path.relative_to(root)),
            "source_timestamp": metadata.get("created_at"),
            "dedupe_key": content_hash,
            "execution_authorized": False,
            "items": note_items,
        }
        if not capture_path.exists():
            _dump(capture_path, capture)
        record = {
            "imported_at": imported_at,
            "packet_id": packet_id,
            "version": metadata.get("version"),
            "content_hash": content_hash,
            "source_path": str(path.relative_to(root)),
            "capture_id": capture_id,
            "item_ids": [item["item_id"] for item in note_items],
            "execution_authorized": False,
        }
        imported.append(record)
        known.add(content_hash)
    inbox = _private(root, config) / "queues" / "shared-notes.jsonl"
    inbox.parent.mkdir(parents=True, exist_ok=True)
    for record in imported:
        runtime_lib.append_integrity_jsonl(inbox, record)
    _dump(ledger_path, {"hashes": sorted(known)})
    return {"imported": imported, "deduplicated": len(known) - len(imported), "rejected": rejected, "execution_authorized": False}
