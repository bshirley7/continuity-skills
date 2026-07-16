"""Offline design-direction lifecycle for Continuity."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

AXES = {
    "industry": "industry",
    "sections": "section-flow",
    "themes": "theme",
    "message_structures": "message-structure",
    "lenses": "lens",
}
TARGETS = {"ui", "document", "image"}


class DesignError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DesignError(f"Expected a JSON object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise DesignError(f"Invalid {label}")
    return value


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _enabled(config: dict[str, Any]) -> None:
    if "design" not in config.get("collections", []):
        raise DesignError("The design collection is not enabled for this project")


def load_catalog(catalog_path: Path) -> dict[str, Any]:
    catalog = _read_json(catalog_path)
    if (
        catalog.get("schema_version") != 1
        or not re.fullmatch(r"\d+\.\d+\.\d+", str(catalog.get("catalog_version", "")))
        or not isinstance(catalog.get("packs"), list)
    ):
        raise DesignError("Installed design catalog is invalid")
    axes = set(AXES.values())
    seen_pack_ids: set[str] = set()
    foundations: dict[str, dict[str, Any]] = {}
    category_packs: list[dict[str, Any]] = []
    for pack in catalog["packs"]:
        pack_id = str(pack.get("pack_id", ""))
        axis = str(pack.get("axis", ""))
        role = str(pack.get("role", ""))
        if (
            pack_id in seen_pack_ids
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]+", pack_id)
            or axis not in axes
            or role not in {"foundation", "category"}
            or not re.fullmatch(r"\d+\.\d+\.\d+", str(pack.get("version", "")))
            or not isinstance(pack.get("categories"), list)
            or not pack["categories"]
        ):
            raise DesignError("Installed design catalog has duplicate or incomplete packs")
        if len(set(pack["categories"])) != len(pack["categories"]):
            raise DesignError("Installed design catalog has duplicate category IDs")
        applicability = pack.get("applicability")
        if not isinstance(applicability, list) or not applicability or any(not isinstance(item, str) or not item.strip() for item in applicability):
            raise DesignError("Installed design catalog must identify pack applicability")
        modalities = pack.get("modalities", {})
        if set(modalities) != TARGETS or any(value not in {"validated", "inferred", "not-applicable"} for value in modalities.values()):
            raise DesignError("Installed design catalog has invalid modality applicability")
        transferable = pack.get("modality_independent_principles")
        if not isinstance(transferable, list) or any(not isinstance(item, str) or not item.strip() for item in transferable):
            raise DesignError("Installed design catalog has invalid modality-independent principles")
        if role == "foundation":
            if axis in foundations:
                raise DesignError(f"Installed design catalog has multiple {axis} foundation packs")
            foundations[axis] = pack
        else:
            if len(pack["categories"]) != 1:
                raise DesignError("Category design packs must cover exactly one bounded category")
            evidence = pack.get("evidence_sufficiency")
            if (
                not isinstance(evidence, dict)
                or set(evidence) != {"sample_count", "product_count", "industry_count"}
                or not all(isinstance(value, int) for value in evidence.values())
                or evidence["sample_count"] < 12
                or evidence["product_count"] < 6
                or evidence["industry_count"] < 1
            ):
                raise DesignError("Category design packs require sufficient aggregate evidence")
            category_packs.append(pack)
        seen_pack_ids.add(pack_id)
        reference = catalog_path.parent / str(pack.get("reference", ""))
        if not reference.is_file() or reference.parent != catalog_path.parent:
            raise DesignError(f"Installed design reference is missing or unsafe: {pack.get('reference')}")
    missing_foundations = sorted(axes - set(foundations))
    if missing_foundations:
        raise DesignError(f"Installed design catalog is missing foundation packs: {missing_foundations}")
    claims: set[tuple[str, str]] = set()
    for pack in category_packs:
        category = pack["categories"][0]
        key = (pack["axis"], category)
        if category not in foundations[pack["axis"]]["categories"]:
            raise DesignError(f"Category design pack is outside its foundation taxonomy: {key}")
        if key in claims:
            raise DesignError(f"Installed design catalog has competing category packs: {key}")
        claims.add(key)
    return catalog


def catalog_summary(config: dict[str, Any], catalog_path: Path, axis: str | None = None) -> dict[str, Any]:
    _enabled(config)
    catalog = load_catalog(catalog_path)
    packs = [pack for pack in catalog["packs"] if axis is None or pack["axis"] == axis]
    return {"catalog_version": catalog["catalog_version"], "packs": packs, "offline": True}


def _validate_strings(payload: dict[str, Any], key: str, required: bool = False) -> list[str]:
    value = payload.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise DesignError(f"{key} must be an array of non-empty strings")
    if required and not value:
        raise DesignError(f"{key} requires at least one value")
    return [item.strip() for item in value]


def _selected_packs(payload: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for input_key, axis in AXES.items():
        values = [payload[input_key]] if input_key == "industry" else payload[input_key]
        axis_packs = [pack for pack in catalog["packs"] if pack["axis"] == axis]
        foundation = next(pack for pack in axis_packs if pack["role"] == "foundation")
        unknown = sorted(set(values) - set(foundation["categories"]))
        if unknown:
            raise DesignError(f"Unknown {axis} catalog values: {unknown}")
        if values:
            selected.append({"pack_id": foundation["pack_id"], "version": foundation["version"]})
            overlays = {pack["categories"][0]: pack for pack in axis_packs if pack["role"] == "category"}
            for value in values:
                if value in overlays:
                    pack = overlays[value]
                    selected.append({"pack_id": pack["pack_id"], "version": pack["version"]})
    return selected


def _direction_count(payload: dict[str, Any]) -> int:
    ambiguities = len(payload["open_questions"])
    varied_axes = sum(len(payload[key]) > 1 for key in ("themes", "message_structures", "sections"))
    if ambiguities == 0 and varied_axes == 0 and len(payload["themes"]) == 1 and len(payload["message_structures"]) == 1:
        return 1
    if ambiguities + varied_axes <= 1:
        return 2
    return 3


def _generated_direction(payload: dict[str, Any], index: int) -> dict[str, Any]:
    labels = ("Focused", "Balanced", "Distinctive")
    theme = payload["themes"][index % len(payload["themes"])]
    message = payload["message_structures"][index % len(payload["message_structures"])]
    lenses = payload["lenses"]
    return {
        "direction_id": f"direction-{index + 1}",
        "name": f"{labels[index]} {theme}",
        "summary": f"Apply a {theme} theme with a {message} message structure across {', '.join(payload['sections'])}.",
        "principles": [f"Use the {lens} lens at each material decision point." for lens in lenses[:4]],
        "variation_levers": ["Adjust information density without changing task priority.", "Adjust expressive emphasis without weakening accessibility."],
        "tradeoffs": payload["open_questions"] or ["Greater focus reduces simultaneous exposure of secondary capabilities."],
    }


def _validate_direction(value: Any, index: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError("Each direction must be an object")
    result = dict(value)
    result["direction_id"] = _identifier(str(result.get("direction_id") or f"direction-{index + 1}"), "direction ID")
    for key in ("name", "summary"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise DesignError(f"Direction {result['direction_id']} requires {key}")
    for key in ("principles", "variation_levers", "tradeoffs"):
        if not isinstance(result.get(key), list) or not result[key] or any(not isinstance(item, str) or not item.strip() for item in result[key]):
            raise DesignError(f"Direction {result['direction_id']} requires non-empty {key}")
    return result


def draft(root: Path, config: dict[str, Any], catalog_path: Path, input_path: Path) -> dict[str, Any]:
    _enabled(config)
    payload = _read_json(input_path)
    for key in ("title", "intent", "industry"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise DesignError(f"Design input requires {key}")
    for key in ("audiences", "targets", "sections", "themes", "message_structures", "lenses"):
        payload[key] = _validate_strings(payload, key, required=True)
    for key in ("constraints", "preserve", "open_questions", "source_note_ids", "memory_ids"):
        payload[key] = _validate_strings(payload, key)
    if not set(payload["targets"]).issubset(TARGETS):
        raise DesignError(f"Unknown targets: {sorted(set(payload['targets']) - TARGETS)}")
    catalog = load_catalog(catalog_path)
    catalog_packs = _selected_packs(payload, catalog)
    count = _direction_count(payload)
    supplied = payload.get("directions")
    if supplied is not None:
        if not isinstance(supplied, list) or len(supplied) != count:
            raise DesignError(f"Adaptive context requires exactly {count} directions")
        directions = [_validate_direction(item, index) for index, item in enumerate(supplied)]
    else:
        directions = [_validate_direction(_generated_direction(payload, index), index) for index in range(count)]
    if len({item["direction_id"] for item in directions}) != len(directions):
        raise DesignError("Direction IDs must be unique")
    design_id = _identifier(str(payload.get("design_id") or f"design-{hashlib.sha256((config['project_id'] + payload['title']).encode()).hexdigest()[:10]}"), "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    prior_path = design_dir / "draft.json"
    revision = 1
    if prior_path.exists():
        prior = _read_json(prior_path)
        revision = int(prior.get("revision", 0)) + 1
        archive = design_dir / "revisions" / f"v{prior.get('revision', 1)}"
        if archive.exists():
            raise DesignError("Design revision archive already exists")
        archive.mkdir(parents=True)
        for name in ("draft.json", "design.md", "approval.json"):
            path = design_dir / name
            if path.exists():
                shutil.copy2(path, archive / name)
        (design_dir / "design.md").unlink(missing_ok=True)
        (design_dir / "approval.json").unlink(missing_ok=True)
    record = {
        "schema_version": 1,
        "design_id": design_id,
        "revision": revision,
        "status": "awaiting-selection",
        "title": payload["title"].strip(),
        "intent": payload["intent"].strip(),
        "audiences": payload["audiences"],
        "targets": payload["targets"],
        "industry": payload["industry"].strip(),
        "sections": payload["sections"],
        "themes": payload["themes"],
        "message_structures": payload["message_structures"],
        "lenses": payload["lenses"],
        "constraints": payload["constraints"],
        "preserve": payload["preserve"],
        "open_questions": payload["open_questions"],
        "source_note_ids": payload["source_note_ids"],
        "memory_ids": payload["memory_ids"],
        "directions": directions,
        "catalog_packs": catalog_packs,
        "catalog_version": catalog["catalog_version"],
        "created_at": _now(),
        "execution_authorized": False,
    }
    _write_json(prior_path, record)
    return record


def _direction_markdown(draft_record: dict[str, Any], selected: list[dict[str, Any]]) -> str:
    targets = ", ".join(draft_record["targets"])
    modality = "validated" if draft_record["targets"] == ["ui"] else "inferred"
    lines = [
        f"# {draft_record['title']}", "",
        f"Design ID: `{draft_record['design_id']}`  ",
        f"Revision: `{draft_record['revision']}`  ",
        f"Targets: `{targets}`  ",
        f"Evidence application: `{modality}`", "",
        "## Intent", "", draft_record["intent"], "",
        "## Selected direction", "",
    ]
    for direction in selected:
        lines.extend([f"### {direction['name']}", "", direction["summary"], "", "Principles:", ""])
        lines.extend(f"- {item}" for item in direction["principles"])
        lines.extend(["", "Variation levers:", "", *[f"- {item}" for item in direction["variation_levers"]], "", "Tradeoffs:", "", *[f"- {item}" for item in direction["tradeoffs"]], ""])
    for heading, key in (("Constraints", "constraints"), ("Behavior to preserve", "preserve"), ("Open questions", "open_questions")):
        values = draft_record[key]
        lines.extend([f"## {heading}", "", *([f"- {item}" for item in values] or ["- None recorded."]), ""])
    lines.extend(["## Implementation boundary", "", "Approval of this document authorizes publication of this exact design document only. It does not authorize implementation or modify an existing goal.", ""])
    return "\n".join(lines)


def select(root: Path, config: dict[str, Any], design_id: str, direction_ids: list[str], actor: str) -> dict[str, Any]:
    _enabled(config)
    design_id = _identifier(design_id, "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    record = _read_json(design_dir / "draft.json")
    if record.get("status") not in {"awaiting-selection", "awaiting-approval"}:
        raise DesignError("Design is not selectable")
    requested = list(dict.fromkeys(direction_ids))
    by_id = {item["direction_id"]: item for item in record["directions"]}
    if not requested or not set(requested).issubset(by_id):
        raise DesignError("Select one or more known direction IDs")
    markdown = _direction_markdown(record, [by_id[item] for item in requested])
    design_hash = hashlib.sha256(markdown.encode()).hexdigest()
    (design_dir / "design.md").write_text(markdown, encoding="utf-8")
    record.update({"status": "awaiting-approval", "selected_direction_ids": requested, "selected_by": actor, "selected_at": _now(), "design_hash": design_hash})
    _write_json(design_dir / "draft.json", record)
    record["required_authorization_text"] = f"Approve design {design_id} revision {record['revision']} hash {design_hash}"
    return record


def approve(root: Path, config: dict[str, Any], design_id: str, revision: int, approved_by: str, authorization_text: str) -> dict[str, Any]:
    _enabled(config)
    design_id = _identifier(design_id, "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    record = _read_json(design_dir / "draft.json")
    draft_path = design_dir / "design.md"
    if record.get("status") != "awaiting-approval" or not draft_path.is_file():
        raise DesignError("Design has no exact draft awaiting approval")
    if revision != record.get("revision"):
        raise DesignError("Design revision does not match the exact draft")
    actual_hash = hashlib.sha256(draft_path.read_bytes()).hexdigest()
    if actual_hash != record.get("design_hash"):
        raise DesignError("Private design draft changed after selection")
    required = f"Approve design {design_id} revision {revision} hash {actual_hash}"
    if authorization_text != required:
        raise DesignError("Authorization text must exactly match the design ID, revision, and hash")
    canonical_path = root / "docs" / "design" / "design.md"
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(draft_path, canonical_path)
    approval = {"schema_version": 1, "design_id": design_id, "revision": revision, "design_hash": actual_hash, "approved_by": approved_by, "approved_at": _now(), "authorization_text": authorization_text, "execution_authorized": False}
    _write_json(design_dir / "approval.json", approval)
    shared = {key: approval[key] for key in ("schema_version", "design_id", "revision", "design_hash", "approved_by", "approved_at", "execution_authorized")}
    shared.update({"status": "approved", "document_path": "docs/design/design.md", "catalog_packs": record["catalog_packs"]})
    _write_json(root / ".continuity" / "design.json", shared)
    record["status"] = "approved"
    _write_json(design_dir / "draft.json", record)
    return shared


def show(root: Path, config: dict[str, Any], design_id: str | None = None) -> dict[str, Any]:
    _enabled(config)
    if design_id:
        path = root / config.get("private_dir", ".continuity/private") / "design" / _identifier(design_id, "design ID") / "draft.json"
    else:
        path = root / ".continuity" / "design.json"
    if not path.is_file():
        raise DesignError("Design record was not found")
    return _read_json(path)


def workflow(root: Path, config: dict[str, Any], design_id: str) -> dict[str, Any]:
    record = show(root, config, design_id)
    status = record.get("status")
    if status == "awaiting-selection":
        return {"design_id": design_id, "revision": record["revision"], "status": status, "next_skill": "continuity-design", "human_required": True, "allowed_actions": ["select-or-combine"], "execution_authorized": False}
    if status == "awaiting-approval":
        return {"design_id": design_id, "revision": record["revision"], "design_hash": record["design_hash"], "status": status, "next_skill": "continuity-design", "human_required": True, "allowed_actions": ["approve-exact-draft", "revise"], "execution_authorized": False}
    return {"design_id": design_id, "revision": record["revision"], "design_hash": record.get("design_hash"), "status": status, "next_skill": "continuity-plan", "human_required": False, "allowed_actions": ["plan-with-design-binding", "revise-design"], "execution_authorized": False}


def bind_approved(root: Path, config: dict[str, Any], design_ids: list[str]) -> list[dict[str, Any]]:
    if not design_ids:
        return []
    _enabled(config)
    if len(design_ids) != 1:
        raise DesignError("The current design contract supports one canonical approved design")
    record = show(root, config)
    if record.get("status") != "approved" or record.get("design_id") != design_ids[0]:
        raise DesignError("Goal design_ids must name the current approved design")
    document = root / record["document_path"]
    if not document.is_file() or hashlib.sha256(document.read_bytes()).hexdigest() != record["design_hash"]:
        raise DesignError("Approved design document does not match its recorded hash")
    return [{"design_id": record["design_id"], "revision": record["revision"], "design_hash": record["design_hash"], "catalog_packs": record["catalog_packs"]}]
