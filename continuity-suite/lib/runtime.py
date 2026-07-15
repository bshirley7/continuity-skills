"""Shared integrity, schema, and atomic persistence helpers for Continuity."""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable


class RuntimeIntegrityError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _private_root(path: Path) -> Path | None:
    resolved = path.resolve()
    parts = resolved.parts
    for index in range(len(parts) - 1):
        if parts[index] == ".continuity" and parts[index + 1] == "private":
            return Path(*parts[: index + 2])
    return None


def mutation_lock_path(path: Path) -> Path:
    private = _private_root(path)
    return (private / ".state.lock") if private else path.parent / ".continuity-write.lock"


@contextlib.contextmanager
def exclusive_file_lock(path: Path) -> Iterable[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write_bytes(path: Path, value: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(mutation_lock_path(path)):
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp_path = Path(temporary)
        try:
            os.fchmod(descriptor, mode)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
            _fsync_directory(path.parent)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def atomic_write_text(path: Path, value: str, *, mode: int = 0o600) -> None:
    atomic_write_bytes(path, value.encode("utf-8"), mode=mode)


def atomic_write_json(path: Path, value: Any, *, mode: int = 0o600) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n", mode=mode)


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "_integrity"}


def verify_jsonl_records(path: Path, *, allow_legacy: bool = True) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "records": 0, "integrity_records": 0, "legacy_records": 0, "healthy": True}
    previous: str | None = None
    legacy = 0
    integrity = 0
    logical_sequence = 0
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        logical_sequence += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeIntegrityError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(record, dict):
            raise RuntimeIntegrityError(f"JSONL record at {path}:{number} is not an object")
        metadata = record.get("_integrity")
        if not isinstance(metadata, dict):
            legacy += 1
            if not allow_legacy:
                raise RuntimeIntegrityError(f"Unsigned legacy JSONL record at {path}:{number}")
            previous = f"legacy:{sha256_bytes(canonical_json(record).encode())}"
            continue
        integrity += 1
        sequence = metadata.get("sequence")
        if sequence != logical_sequence:
            raise RuntimeIntegrityError(f"JSONL sequence mismatch at {path}:{number}")
        if metadata.get("previous_hash") != previous:
            raise RuntimeIntegrityError(f"JSONL chain mismatch at {path}:{number}")
        material = {
            "sequence": sequence,
            "previous_hash": previous,
            "payload": _record_payload(record),
        }
        expected = sha256_bytes(canonical_json(material).encode())
        if metadata.get("record_hash") != expected:
            raise RuntimeIntegrityError(f"JSONL record hash mismatch at {path}:{number}")
        previous = expected
    return {
        "path": str(path),
        "records": legacy + integrity,
        "integrity_records": integrity,
        "legacy_records": legacy,
        "healthy": True,
    }


def append_integrity_jsonl(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeIntegrityError("JSONL values must be objects")
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(mutation_lock_path(path)):
        verify_jsonl_records(path)
        existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        nonempty = [line for line in existing if line.strip()]
        previous: str | None = None
        if nonempty:
            try:
                last = json.loads(nonempty[-1])
            except json.JSONDecodeError as exc:
                raise RuntimeIntegrityError(f"Cannot append to invalid JSONL ledger {path}") from exc
            metadata = last.get("_integrity") if isinstance(last, dict) else None
            previous = metadata.get("record_hash") if isinstance(metadata, dict) else f"legacy:{sha256_bytes(canonical_json(last).encode())}"
        sequence = len(nonempty) + 1
        payload = _record_payload(value)
        material = {"sequence": sequence, "previous_hash": previous, "payload": payload}
        record = {
            **payload,
            "_integrity": {
                "algorithm": "sha256-chain-v1",
                "sequence": sequence,
                "previous_hash": previous,
                "record_hash": sha256_bytes(canonical_json(material).encode()),
            },
        }
        encoded = (canonical_json(record) + "\n").encode()
        with path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
        return record


def load_jsonl(path: Path, *, verify: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if verify:
        verify_jsonl_records(path)
    values: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            values.append(json.loads(line))
    return values


def _resolve_schema(schema: dict[str, Any], schema_path: Path) -> tuple[dict[str, Any], Path]:
    reference = schema.get("$ref")
    if not reference:
        return schema, schema_path
    if reference.startswith("#"):
        raise RuntimeIntegrityError(f"Internal schema references are not supported: {reference}")
    target = (schema_path.parent / reference).resolve()
    return json.loads(target.read_text(encoding="utf-8")), target


def validate_schema(value: Any, schema: dict[str, Any], schema_path: Path, label: str = "record") -> None:
    schema, schema_path = _resolve_schema(schema, schema_path)
    if "const" in schema and value != schema["const"]:
        raise RuntimeIntegrityError(f"{label} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise RuntimeIntegrityError(f"{label} is not one of {schema['enum']}")
    expected = schema.get("type")
    type_checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected in type_checks and not type_checks[expected](value):
        raise RuntimeIntegrityError(f"{label} must be a {expected}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = sorted(set(required) - set(value))
        if missing:
            raise RuntimeIntegrityError(f"{label} is missing required fields: {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise RuntimeIntegrityError(f"{label} has unsupported fields: {unknown}")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, schema_path, f"{label}.{key}")
    if isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            raise RuntimeIntegrityError(f"{label} has too few items")
        if schema.get("uniqueItems") and len({canonical_json(item) for item in value}) != len(value):
            raise RuntimeIntegrityError(f"{label} items must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], schema_path, f"{label}[{index}]")
    if isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            raise RuntimeIntegrityError(f"{label} is too short")
        if schema.get("maxLength") is not None and len(value) > int(schema["maxLength"]):
            raise RuntimeIntegrityError(f"{label} is too long")
        if schema.get("pattern") and not re.fullmatch(schema["pattern"], value):
            raise RuntimeIntegrityError(f"{label} does not match the required format")
    if isinstance(value, int) and not isinstance(value, bool):
        if schema.get("minimum") is not None and value < schema["minimum"]:
            raise RuntimeIntegrityError(f"{label} is below the minimum")
        if schema.get("maximum") is not None and value > schema["maximum"]:
            raise RuntimeIntegrityError(f"{label} is above the maximum")


def validate_schema_file(value: Any, path: Path, label: str = "record") -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    validate_schema(value, schema, path, label)
