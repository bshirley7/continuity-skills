"""Offline design-direction lifecycle for Continuity."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import struct
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
CATALOG_MODALITIES = TARGETS | {"campaign", "platform"}
EVIDENCE_STATUSES = {"validated", "inferred", "not-applicable"}
CONTENT_CLASSIFICATIONS = {"inspected", "supplied", "inferred", "illustrative"}
CREATIVE_PROVENANCE_CLASSIFICATIONS = {"inspected", "supplied", "inferred"}
EXPRESSION_INTENSITIES = {"quiet", "present", "signature"}
EXPRESSION_DIMENSIONS = ("composition", "typography", "color", "motion", "imagery", "surface_depth", "voice")
EXPRESSION_MODES = {"calibrated", "boundary-study"}
EXPRESSION_SOURCES = {"inferred", "user-supplied"}
DESIGN_REGISTERS = {"brand", "product", "mixed"}
COLOR_COMMITMENTS = {"restrained", "committed", "full-palette", "drenched"}
REFINEMENT_PASS_STATUSES = {"completed", "pending", "not-applicable"}
REFINEMENT_PASS_IDS = (
    "provenance-grounding", "divergent-exploration", "boundary-push",
    "contextual-review", "restraint-edit", "responsive-transformation", "artifact-critique",
)
AUDIENCE_MODES = {"shared-core", "differentiated", "unresolved"}
PROTOTYPE_MATURITY = {"directional", "behavioral", "implementation-facing"}
VALIDATION_STATUSES = {"required", "passed", "not-applicable"}
INSIGHT_DECISION_STATUSES = {"decided", "provisional", "omitted"}
ARTIFACT_MATURITY = {"directional", "behavioral", "implementation-facing"}
COMPONENT_STRATEGIES = {"reuse", "compose", "extend", "custom", "missing-capability"}
ASSET_SOURCES = {"existing", "supplied", "generated", "derived", "deliberately-omitted"}
ARTIFACT_MEDIA_TYPES = {
    "text/html", "image/png", "text/css", "text/javascript", "application/javascript",
    "application/typescript", "application/json", "image/svg+xml",
}
DESIGN_GRAMMAR_DIMENSIONS = (
    "composition",
    "spacing_density",
    "typography",
    "color",
    "shape_form",
    "surface_depth",
    "imagery",
    "iconography",
    "motion",
    "voice",
    "state_language",
    "responsive_behavior",
)
TARGET_GRAMMAR_DIMENSIONS = {
    "ui": DESIGN_GRAMMAR_DIMENSIONS,
    "document": (
        "composition", "spacing_density", "typography", "color", "shape_form",
        "imagery", "iconography", "voice", "state_language", "responsive_behavior",
    ),
    "image": (
        "composition", "spacing_density", "typography", "color", "shape_form",
        "surface_depth", "imagery", "iconography", "voice", "responsive_behavior",
    ),
}
INFERENCE_CONTEXT_FIELDS = (
    "title",
    "intent",
    "audiences",
    "targets",
    "industry",
    "sections",
    "themes",
    "message_structures",
    "constraints",
    "preserve",
    "current_strengths",
    "current_gaps",
    "design_debt",
    "open_questions",
    "consequences",
    "workflow_signals",
    "interaction_signals",
    "risk_signals",
)
DIRECTION_STRATEGIES = (
    {
        "name": "Direct path",
        "summary": "Concentrate the experience on the shortest credible path to the primary outcome, revealing secondary capability only when it becomes relevant.",
        "principle": "Prioritize one obvious next action and preserve a direct route back to the current task.",
        "grammar": {
            "composition": "Use a strong primary region, one supporting context region, and a stable recovery route; suppress unrelated destinations at the decision point.",
            "spacing_density": "Use generous separation around the primary task and compact spacing only within tightly related supporting details.",
            "typography": "Use a restrained hierarchy with one dominant task heading, concise operational labels, and readable supporting explanation.",
            "color": "Reserve the strongest color for current action and consequential state; keep surrounding surfaces quiet and semantically neutral.",
            "shape_form": "Use a small set of familiar control and container forms so the primary path is recognized without interpretation.",
            "surface_depth": "Keep most content on one plane and introduce elevation only for temporary focus, confirmation, or recovery.",
            "imagery": "Use imagery only when it clarifies the outcome or object; remove decorative media that competes with the primary task.",
            "iconography": "Pair a limited set of familiar symbols with direct labels, especially for state, exit, and recovery.",
            "motion": "Use brief transitions to preserve continuity along the primary path and avoid ambient or attention-seeking motion.",
            "voice": "Use concise, direct language that names the next action, consequence, and available recovery without promotional framing.",
            "state_language": "Keep current, pending, complete, blocked, and recoverable states adjacent to the primary object and action.",
            "responsive_behavior": "Preserve the primary action, current state, and recovery route before secondary context as space becomes constrained."
        }
    },
    {
        "name": "Guided confidence",
        "summary": "Organize the experience as a supported sequence that explains unfamiliar choices at the moment they become relevant.",
        "principle": "Build confidence through progressive context, visible progress, examples, and reversible checkpoints.",
        "grammar": {
            "composition": "Use a staged sequence with visible orientation, current-step focus, contextual help, and a persistent summary of prior commitments.",
            "spacing_density": "Use moderate density within each step and larger breaks between stages so progress and responsibility remain legible.",
            "typography": "Combine instructional headings, plain-language explanations, examples, and compact summaries of completed decisions.",
            "color": "Use a calm semantic progression for current, complete, attention, and blocked states without turning progress into pressure.",
            "shape_form": "Differentiate instruction, user input, evidence, checkpoint, and support through consistent but clearly distinct forms.",
            "surface_depth": "Use bounded panels to separate the current step from prior decisions and optional help while keeping the sequence connected.",
            "imagery": "Use annotated examples or diagrams where they reduce unfamiliarity, with equivalent text and no decorative claim inflation.",
            "iconography": "Use labeled status and orientation symbols consistently across steps, with redundant text for consequential meaning.",
            "motion": "Use transitions to explain advancement, return, validation, and changed state while respecting reduced-motion preferences.",
            "voice": "Use reassuring but precise guidance that explains why information is needed and never treats questions as user failure.",
            "state_language": "Distinguish not started, in progress, needs attention, ready for review, submitted, and safely resumable states.",
            "responsive_behavior": "Collapse the sequence without hiding orientation, prior commitments, help, or the ability to move backward safely."
        }
    },
    {
        "name": "Explorable system",
        "summary": "Expose a coherent overview with several meaningful entry paths so people can inspect relationships and choose where to begin.",
        "principle": "Support comparison and self-directed exploration while keeping scope, state, and commitment boundaries explicit.",
        "grammar": {
            "composition": "Use an overview, stable navigation, comparable object regions, and a focused detail surface that preserves broader context.",
            "spacing_density": "Use structured density for scanning and comparison, with alignment and grouping doing more work than empty space.",
            "typography": "Use a broad but disciplined hierarchy for overview metrics, object identity, comparison labels, detail, and evidence.",
            "color": "Use a differentiated palette for categories and state with redundant labels, stable mappings, and accessible contrast.",
            "shape_form": "Create recognizable forms for collections, comparable objects, filters, evidence, actions, and focused detail.",
            "surface_depth": "Use layering to distinguish overview, selected detail, transient controls, and modal commitment without excessive nesting.",
            "imagery": "Use imagery as navigable evidence, category signal, or object identity with inspectable source and graceful absence states.",
            "iconography": "Use a systematic symbol language for navigation, filtering, comparison, state, and view changes with labels where ambiguity remains.",
            "motion": "Use spatial transitions to preserve object identity between overview and detail without making animation carry state alone.",
            "voice": "Use descriptive labels and concise comparative language that supports inspection before asking for commitment.",
            "state_language": "Expose selection, filtering, freshness, comparison scope, pending changes, and commitment as distinct states.",
            "responsive_behavior": "Transform overview and detail into a reversible sequence while preserving filters, selection, comparison context, and return position."
        }
    }
)


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
        if (
            not TARGETS.issubset(modalities)
            or not set(modalities).issubset(CATALOG_MODALITIES)
            or any(value not in EVIDENCE_STATUSES for value in modalities.values())
        ):
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
            evidence_kind = pack.get("evidence_kind", "ui-observation")
            ui_evidence = (
                evidence_kind == "ui-observation"
                and isinstance(evidence, dict)
                and set(evidence) == {"sample_count", "product_count", "industry_count"}
                and all(isinstance(value, int) for value in evidence.values())
                and evidence["sample_count"] >= 12
                and evidence["product_count"] >= 6
                and evidence["industry_count"] >= 1
            )
            literature_evidence = (
                evidence_kind == "literature"
                and isinstance(evidence, dict)
                and set(evidence) == {"sample_count", "publisher_count", "evidence_family_count"}
                and all(isinstance(value, int) for value in evidence.values())
                and evidence["sample_count"] >= 12
                and evidence["publisher_count"] >= 3
                and evidence["evidence_family_count"] >= 3
            )
            if not (ui_evidence or literature_evidence):
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


def load_lens_routing(catalog_path: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    routing_path = catalog_path.parent / "lens-routing.json"
    routing = _read_json(routing_path)
    if routing.get("schema_version") != 1 or not isinstance(routing.get("baseline"), list) or not isinstance(routing.get("rules"), list):
        raise DesignError("Installed UX lens routing is invalid")
    lens_foundation = next(pack for pack in catalog["packs"] if pack["axis"] == "lens" and pack["role"] == "foundation")
    available = set(lens_foundation["categories"])
    baseline = routing["baseline"]
    if not baseline or len(set(baseline)) != len(baseline) or any(not isinstance(item, str) or item not in available for item in baseline):
        raise DesignError("Installed UX lens routing has an invalid baseline")
    seen_rules: set[str] = set()
    for rule in routing["rules"]:
        if not isinstance(rule, dict):
            raise DesignError("Installed UX lens routing has an invalid rule")
        rule_id = rule.get("rule_id")
        reason = rule.get("reason")
        terms = rule.get("terms")
        lenses = rule.get("lenses")
        minimum_matches = rule.get("minimum_matches", 1)
        if (
            not isinstance(rule_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]+", rule_id)
            or rule_id in seen_rules
            or not isinstance(reason, str)
            or not reason.strip()
            or not isinstance(terms, list)
            or not terms
            or any(not isinstance(item, str) or not item.strip() for item in terms)
            or not isinstance(minimum_matches, int)
            or minimum_matches < 1
            or minimum_matches > len(terms)
            or not isinstance(lenses, list)
            or not lenses
            or any(not isinstance(item, str) or item not in available for item in lenses)
        ):
            raise DesignError("Installed UX lens routing has an incomplete or unknown rule")
        seen_rules.add(rule_id)
    return routing


def load_composition_precedence(catalog_path: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    path = catalog_path.parent / "composition-precedence.json"
    value = _read_json(path)
    precedence = value.get("precedence")
    conflicts = value.get("conflicts")
    if value.get("schema_version") != 1 or not isinstance(precedence, list) or not precedence or not isinstance(conflicts, list):
        raise DesignError("Installed design composition precedence is invalid")
    precedence_ids: set[str] = set()
    priorities: set[int] = set()
    for item in precedence:
        precedence_id = item.get("precedence_id")
        priority = item.get("priority")
        rule = item.get("rule")
        if (
            not isinstance(precedence_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]+", precedence_id)
            or precedence_id in precedence_ids
            or not isinstance(priority, int)
            or priority in priorities
            or not isinstance(rule, str)
            or not rule.strip()
        ):
            raise DesignError("Installed design composition precedence has an invalid rule")
        precedence_ids.add(precedence_id)
        priorities.add(priority)
    available_lenses = set(
        next(pack for pack in catalog["packs"] if pack["axis"] == "lens" and pack["role"] == "foundation")["categories"]
    )
    seen_conflicts: set[str] = set()
    for conflict in conflicts:
        conflict_id = conflict.get("conflict_id")
        all_lenses = conflict.get("all_lenses", [])
        any_lenses = conflict.get("any_lenses", [])
        any_input_fields = conflict.get("any_input_fields", [])
        if (
            not isinstance(conflict_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9-]+", conflict_id)
            or conflict_id in seen_conflicts
            or not all(isinstance(values, list) for values in (all_lenses, any_lenses, any_input_fields))
            or not all_lenses + any_lenses + any_input_fields
            or any(lens not in available_lenses for lens in all_lenses + any_lenses)
            or any(field not in INFERENCE_CONTEXT_FIELDS for field in any_input_fields)
            or conflict.get("dominant_precedence_id") not in precedence_ids
            or not isinstance(conflict.get("resolution"), str)
            or not conflict["resolution"].strip()
        ):
            raise DesignError("Installed design composition precedence has an invalid conflict")
        seen_conflicts.add(conflict_id)
    return value


def _resolve_composition(payload: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    selected_lenses = set(payload["lenses"])
    active_conflicts: list[dict[str, Any]] = []
    for conflict in rules["conflicts"]:
        all_lenses = set(conflict.get("all_lenses", []))
        any_lenses = set(conflict.get("any_lenses", []))
        input_fields = conflict.get("any_input_fields", [])
        if not all_lenses.issubset(selected_lenses):
            continue
        if any_lenses and not any_lenses.intersection(selected_lenses):
            continue
        if input_fields and not any(payload.get(field) for field in input_fields):
            continue
        active_conflicts.append(
            {
                "conflict_id": conflict["conflict_id"],
                "dominant_precedence_id": conflict["dominant_precedence_id"],
                "resolution": conflict["resolution"],
            }
        )
    precedence = sorted(rules["precedence"], key=lambda item: item["priority"], reverse=True)
    return {
        "precedence": [
            {
                "precedence_id": item["precedence_id"],
                "priority": item["priority"],
                "rule": item["rule"],
            }
            for item in precedence
        ],
        "active_conflicts": active_conflicts,
    }


def _inference_context(payload: dict[str, Any]) -> dict[str, str]:
    context: dict[str, str] = {}
    for key in INFERENCE_CONTEXT_FIELDS:
        value = payload.get(key)
        values = value if isinstance(value, list) else [value] if isinstance(value, str) else []
        if values:
            context[key] = " ".join(values).casefold().replace("-", " ")
    return context


def _term_matches(text: str, term: str) -> bool:
    normalized = term.casefold().replace("-", " ").strip()
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text) is not None


def _infer_lenses(payload: dict[str, Any], routing: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    selected = list(routing["baseline"])
    rationale: list[dict[str, Any]] = [
        {
            "rule_id": "universal-baseline",
            "reason": "Applied to every automatically routed design.",
            "lenses": list(routing["baseline"]),
            "matched_terms": [],
            "matched_context": [],
        }
    ]
    context = _inference_context(payload)
    for rule in routing["rules"]:
        matched_context = []
        matched_terms: list[str] = []
        for field, text in context.items():
            field_terms = [term for term in rule["terms"] if _term_matches(text, term)]
            if field_terms:
                matched_context.append({"field": field, "matched_terms": field_terms})
                matched_terms.extend(term for term in field_terms if term not in matched_terms)
        if len(matched_terms) < rule.get("minimum_matches", 1):
            continue
        lenses = list(rule["lenses"])
        selected.extend(lens for lens in lenses if lens not in selected)
        rationale.append(
            {
                "rule_id": rule["rule_id"],
                "reason": rule["reason"],
                "lenses": lenses,
                "matched_terms": matched_terms,
                "matched_context": matched_context,
            }
        )
    return selected, rationale


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
        if input_key == "industry":
            values = [payload[input_key]] if payload[input_key] else []
        else:
            values = payload[input_key]
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


def _bind_lens_routing(
    rationale: list[dict[str, Any]],
    catalog: dict[str, Any],
    selected_packs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    lens_packs = [pack for pack in catalog["packs"] if pack["axis"] == "lens"]
    foundation = next(pack for pack in lens_packs if pack["role"] == "foundation")
    overlays = {
        pack["categories"][0]: pack
        for pack in lens_packs
        if pack["role"] == "category"
    }
    selected_ids = {pack["pack_id"] for pack in selected_packs}
    for item in rationale:
        bound: list[dict[str, str]] = []
        seen: set[str] = set()
        for lens in item["lenses"]:
            pack = overlays.get(lens, foundation)
            if pack["pack_id"] not in selected_ids:
                raise DesignError("Inferred UX lens is not bound to a selected catalog pack")
            if pack["pack_id"] not in seen:
                bound.append({"pack_id": pack["pack_id"], "version": pack["version"]})
                seen.add(pack["pack_id"])
        item["catalog_packs"] = bound
    return rationale


def _direction_count(payload: dict[str, Any]) -> int:
    explicit = payload.get("direction_count")
    if explicit is not None:
        if not isinstance(explicit, int) or isinstance(explicit, bool) or explicit not in {1, 2, 3}:
            raise DesignError("direction_count must be 1, 2, or 3 when supplied")
        return explicit
    ambiguities = len(payload["open_questions"])
    varied_axes = sum(len(payload[key]) > 1 for key in ("themes", "message_structures", "sections"))
    if ambiguities == 0 and varied_axes == 0:
        return 1
    if ambiguities + varied_axes <= 1:
        return 2
    return 3


def _required_grammar_dimensions(targets: list[str]) -> tuple[str, ...]:
    return tuple(
        dimension
        for dimension in DESIGN_GRAMMAR_DIMENSIONS
        if any(dimension in TARGET_GRAMMAR_DIMENSIONS[target] for target in targets)
    )


def _validate_content_provenance(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("content_provenance must be an array")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise DesignError("Each content provenance record must be an object")
        content_id = _identifier(str(item.get("content_id", "")), "content ID")
        classification = item.get("classification")
        statement = item.get("statement")
        qualification = item.get("required_qualification", "")
        if content_id in seen:
            raise DesignError("Content provenance IDs must be unique")
        if classification not in CONTENT_CLASSIFICATIONS:
            raise DesignError(f"Unknown content classification: {classification}")
        if not isinstance(statement, str) or not statement.strip():
            raise DesignError(f"Content provenance {content_id} requires statement")
        if classification in {"inferred", "illustrative"} and (not isinstance(qualification, str) or not qualification.strip()):
            raise DesignError(f"Content provenance {content_id} requires qualification")
        source_refs = item.get("source_refs", [])
        allowed_uses = item.get("allowed_uses", [])
        for key, strings in (("source_refs", source_refs), ("allowed_uses", allowed_uses)):
            if not isinstance(strings, list) or any(not isinstance(entry, str) or not entry.strip() for entry in strings):
                raise DesignError(f"Content provenance {content_id} has invalid {key}")
        if classification == "inspected" and not source_refs:
            raise DesignError(f"Inspected content provenance {content_id} requires source_refs")
        records.append({
            "content_id": content_id,
            "classification": classification,
            "statement": statement.strip(),
            "source_refs": source_refs,
            "required_qualification": qualification.strip() if isinstance(qualification, str) else "",
            "allowed_uses": allowed_uses,
        })
        seen.add(content_id)
    return records


def _validate_audience_architecture(value: Any, audiences: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("mode") not in AUDIENCE_MODES:
        raise DesignError("audience_architecture requires a valid mode")
    mode = value["mode"]
    shared_core = value.get("shared_core", [])
    unresolved = value.get("unresolved_conflicts", [])
    for key, strings in (("shared_core", shared_core), ("unresolved_conflicts", unresolved)):
        if not isinstance(strings, list) or any(not isinstance(entry, str) or not entry.strip() for entry in strings):
            raise DesignError(f"audience_architecture has invalid {key}")
    routes = value.get("routes", [])
    if not isinstance(routes, list):
        raise DesignError("audience_architecture routes must be an array")
    normalized_routes: list[dict[str, Any]] = []
    for route in routes:
        if not isinstance(route, dict):
            raise DesignError("Each audience route must be an object")
        audience = route.get("audience")
        route_name = route.get("route")
        needs = route.get("needs", [])
        if not isinstance(audience, str) or not audience.strip() or not isinstance(route_name, str) or not route_name.strip():
            raise DesignError("Each audience route requires audience and route")
        if not isinstance(needs, list) or not needs or any(not isinstance(entry, str) or not entry.strip() for entry in needs):
            raise DesignError("Each audience route requires non-empty needs")
        normalized_routes.append({"audience": audience.strip(), "route": route_name.strip(), "needs": needs})
    if mode == "shared-core" and not shared_core:
        raise DesignError("shared-core audience architecture requires shared_core")
    if mode == "differentiated" and len(normalized_routes) < 2:
        raise DesignError("differentiated audience architecture requires at least two routes")
    if mode == "unresolved" and not unresolved:
        raise DesignError("unresolved audience architecture requires unresolved_conflicts")
    return {"mode": mode, "shared_core": shared_core, "routes": normalized_routes, "unresolved_conflicts": unresolved}


def _validate_prototype_scope(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("maturity") not in PROTOTYPE_MATURITY:
        raise DesignError("prototype_scope requires a valid maturity")
    artifact_type = value.get("artifact_type")
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        raise DesignError("prototype_scope requires artifact_type")
    result = {"maturity": value["maturity"], "artifact_type": artifact_type.strip()}
    for key in ("demonstrated_surfaces", "demonstrated_states", "omitted_surfaces", "omitted_states"):
        strings = value.get(key, [])
        if not isinstance(strings, list) or any(not isinstance(entry, str) or not entry.strip() for entry in strings):
            raise DesignError(f"prototype_scope has invalid {key}")
        result[key] = strings
    fixture_data = value.get("fixture_data", "none")
    if fixture_data not in {"none", "present"}:
        raise DesignError("prototype_scope fixture_data must be none or present")
    result["fixture_data"] = fixture_data
    if result["maturity"] == "implementation-facing" and (not result["demonstrated_surfaces"] or not result["demonstrated_states"]):
        raise DesignError("implementation-facing prototype scope requires demonstrated surfaces and states")
    return result


def _validate_validation_matrix(value: Any, prototype_scope: dict[str, Any] | None) -> list[dict[str, str]]:
    if value is None:
        value = []
    if not isinstance(value, list):
        raise DesignError("validation_matrix must be an array")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("scenario"), str) or not item["scenario"].strip():
            raise DesignError("Each validation entry requires scenario")
        scenario = item["scenario"].strip()
        status = item.get("status")
        evidence = item.get("evidence", "")
        if scenario in seen or status not in VALIDATION_STATUSES or not isinstance(evidence, str):
            raise DesignError(f"Invalid validation entry: {scenario}")
        if status in {"passed", "not-applicable"} and not evidence.strip():
            raise DesignError(f"Validation entry {scenario} requires evidence or rationale")
        result.append({"scenario": scenario, "status": status, "evidence": evidence.strip()})
        seen.add(scenario)
    if prototype_scope and prototype_scope["maturity"] == "implementation-facing":
        if not result or any(item["status"] == "required" for item in result):
            raise DesignError("implementation-facing prototypes require completed validation evidence")
    return result


def _validate_direction_assessment(value: Any) -> dict[str, list[str]] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise DesignError("direction_assessment must be an object")
    result: dict[str, list[str]] = {}
    for key in ("material_ambiguities", "resolved_by_evidence"):
        items = value.get(key, [])
        if not isinstance(items, list) or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"direction_assessment has invalid {key}")
        result[key] = list(dict.fromkeys(item.strip() for item in items))
    if set(result["resolved_by_evidence"]) - set(result["material_ambiguities"]):
        raise DesignError("resolved_by_evidence must name material ambiguities")
    return result


def _validate_insight_decisions(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("insight_decisions must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise DesignError("Each insight decision must be an object")
        insight_id = _identifier(str(item.get("insight_id", "")), "insight ID")
        if insight_id in seen:
            raise DesignError("Insight decision IDs must be unique")
        status = item.get("status")
        if status not in INSIGHT_DECISION_STATUSES:
            raise DesignError(f"Insight decision {insight_id} requires a valid status")
        normalized: dict[str, Any] = {"insight_id": insight_id, "status": status}
        for key in ("insight", "design_response", "observable_evidence"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Insight decision {insight_id} requires {key}")
            normalized[key] = text.strip()
        for key in ("source_refs", "affected_surfaces", "affected_states"):
            strings = item.get(key, [])
            if not isinstance(strings, list) or any(not isinstance(entry, str) or not entry.strip() for entry in strings):
                raise DesignError(f"Insight decision {insight_id} has invalid {key}")
            normalized[key] = list(dict.fromkeys(entry.strip() for entry in strings))
        if status == "decided" and not normalized["affected_surfaces"]:
            raise DesignError(f"Decided insight {insight_id} requires affected_surfaces")
        result.append(normalized)
        seen.add(insight_id)
    return result


def _string_list(value: Any, label: str, *, required: bool = False) -> list[str]:
    if value is None:
        value = []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise DesignError(f"{label} must be an array of non-empty strings")
    result = list(dict.fromkeys(item.strip() for item in value))
    if required and not result:
        raise DesignError(f"{label} must not be empty")
    return result


def _validate_implementation_context(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("framework"), str) or not value["framework"].strip():
        raise DesignError("implementation_context requires framework")
    result: dict[str, Any] = {
        "framework": value["framework"].strip(),
        "framework_version": str(value.get("framework_version", "")).strip(),
        "react_version": str(value.get("react_version", "")).strip(),
        "storybook_available": value.get("storybook_available", False),
    }
    if not isinstance(result["storybook_available"], bool):
        raise DesignError("implementation_context storybook_available must be boolean")
    for key in (
        "styling_systems", "ui_libraries", "motion_libraries", "data_libraries", "icon_libraries",
        "component_roots", "token_sources", "asset_roots",
    ):
        result[key] = _string_list(value.get(key), f"implementation_context {key}")
    result["evidence_refs"] = _string_list(value.get("evidence_refs"), "implementation_context evidence_refs", required=True)
    return result


def _validate_component_map(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("component_map must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise DesignError("Each component map entry must be an object")
        component_id = _identifier(str(item.get("component_id", "")), "component ID")
        if component_id in seen or item.get("strategy") not in COMPONENT_STRATEGIES:
            raise DesignError(f"Invalid or duplicate component map entry: {component_id}")
        normalized: dict[str, Any] = {"component_id": component_id, "strategy": item["strategy"]}
        for key in ("experience_need", "surface", "responsive_behavior", "accessibility_contract", "custom_expression"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Component {component_id} requires {key}")
            normalized[key] = text.strip()
        normalized["existing_capability"] = str(item.get("existing_capability", "")).strip()
        normalized["components"] = _string_list(item.get("components"), f"component {component_id} components")
        normalized["required_states"] = _string_list(item.get("required_states"), f"component {component_id} required_states", required=True)
        if normalized["strategy"] in {"reuse", "compose", "extend"} and not normalized["components"]:
            raise DesignError(f"Component {component_id} strategy {normalized['strategy']} requires existing components")
        result.append(normalized)
        seen.add(component_id)
    return result


def _validate_asset_strategy(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("asset_strategy must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise DesignError("Each asset strategy entry must be an object")
        asset_id = _identifier(str(item.get("asset_id", "")), "asset ID")
        if asset_id in seen or item.get("source") not in ASSET_SOURCES:
            raise DesignError(f"Invalid or duplicate asset strategy entry: {asset_id}")
        normalized: dict[str, Any] = {"asset_id": asset_id, "source": item["source"]}
        for key in (
            "purpose", "art_direction", "provenance_status", "responsive_treatment",
            "accessibility_alternative", "fallback", "claim_boundary",
        ):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Asset {asset_id} requires {key}")
            normalized[key] = text.strip()
        normalized["source_refs"] = _string_list(item.get("source_refs"), f"asset {asset_id} source_refs")
        normalized["required_crops"] = _string_list(item.get("required_crops"), f"asset {asset_id} required_crops")
        if normalized["source"] in {"existing", "supplied", "derived"} and not normalized["source_refs"]:
            raise DesignError(f"Asset {asset_id} source {normalized['source']} requires source_refs")
        result.append(normalized)
        seen.add(asset_id)
    return result


def _validate_completion_contract(value: Any, targets: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("mode") not in {"exploration", "complete-prototype"}:
        raise DesignError("completion_contract requires a valid mode")
    viewports = _string_list(value.get("required_viewports"), "completion_contract required_viewports")
    if set(viewports) - {"desktop", "tablet", "mobile"}:
        raise DesignError("completion_contract has an unknown viewport")
    required_states = _string_list(value.get("required_states"), "completion_contract required_states")
    content_status = value.get("content_status")
    if content_status not in {"representative", "production", "mixed"}:
        raise DesignError("completion_contract requires content_status")
    critique = value.get("artifact_critique_required")
    if not isinstance(critique, bool):
        raise DesignError("completion_contract artifact_critique_required must be boolean")
    if value["mode"] == "complete-prototype" and "ui" in targets:
        if set(viewports) != {"desktop", "tablet", "mobile"} or not required_states or not critique:
            raise DesignError("Complete UI prototypes require desktop, tablet, mobile, relevant states, and artifact critique")
    return {
        "mode": value["mode"], "required_viewports": viewports, "required_states": required_states,
        "content_status": content_status, "artifact_critique_required": critique,
    }


def _validate_creative_provenance(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("creative_provenance must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise DesignError("Each creative provenance record must be an object")
        provenance_id = _identifier(str(item.get("provenance_id", "")), "creative provenance ID")
        if provenance_id in seen:
            raise DesignError("Creative provenance IDs must be unique within a direction")
        classification = item.get("classification")
        if classification not in CREATIVE_PROVENANCE_CLASSIFICATIONS:
            raise DesignError(f"Creative provenance {provenance_id} requires a valid classification")
        normalized = {"provenance_id": provenance_id, "classification": classification}
        for key in ("observation", "design_implication"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Creative provenance {provenance_id} requires {key}")
            normalized[key] = text.strip()
        source_refs = item.get("source_refs", [])
        if not isinstance(source_refs, list) or any(not isinstance(entry, str) or not entry.strip() for entry in source_refs):
            raise DesignError(f"Creative provenance {provenance_id} has invalid source_refs")
        normalized["source_refs"] = list(dict.fromkeys(entry.strip() for entry in source_refs))
        if classification in {"inspected", "supplied"} and not normalized["source_refs"]:
            raise DesignError(f"Creative provenance {provenance_id} requires source_refs for {classification} material")
        result.append(normalized)
        seen.add(provenance_id)
    return result


def _validate_distinctive_expression(value: Any, provenance_ids: set[str], creative_signature: str) -> dict[str, Any]:
    if value is None:
        return {
            "aesthetic_thesis": creative_signature,
            "subject_world": ["Derive visual language from the recorded project intent and inspected product context before implementation."],
            "signature_element": creative_signature,
            "aesthetic_risk": {
                "move": "No additional aesthetic risk was authored in this legacy direction.",
                "rationale": "Preserve backward compatibility while making the missing creative decision visible.",
                "boundary": "Do not invent novelty that weakens comprehension, accessibility, or favorable behavior.",
            },
            "anti_defaults": ["Do not substitute an interchangeable category or model-generated aesthetic for subject-specific expression."],
            "expression_system": {
                "palette": ["Derive named color roles from the subject and selected direction before artifact generation."],
                "typography": ["Choose deliberate display, body, and utility roles appropriate to the subject before artifact generation."],
                "composition": ["Create a target-native reference composition that makes the signature visible."],
                "material_imagery": ["Use only materials and imagery supported by project context or clearly labeled inference."],
                "motion": ["Use one orchestrated motion idea only when it reinforces meaning and the target supports motion."],
                "voice": ["Use audience-native language rather than reusable design-copy formulas."],
            },
            "reference_compositions": ["A representative composition is still required before implementation-facing status."],
            "uniqueness_checks": ["Confirm the expression could not be transferred unchanged to an unrelated project."],
            "expression_budget": {
                "target_weight": 0.35,
                "exploration_ceiling": 0.55,
                "mode": "calibrated",
                "source": "inferred",
                "weight_rationale": "Use restrained project-specific expression until stronger project evidence or an explicit user preference is available.",
                "boundary_being_pushed": "No authored boundary was recorded for this legacy direction.",
                "primary_dimension": "composition",
                "supporting_dimensions": ["voice"],
                "restrained_dimensions": ["typography", "color", "motion", "imagery", "surface_depth"],
                "intensity": {dimension: ("signature" if dimension == "composition" else "quiet") for dimension in EXPRESSION_DIMENSIONS},
                "quiet_field": "Keep surrounding content and controls conventional until a project-specific expression budget is authored.",
                "containment_boundary": "Do not weaken comprehension, accessibility, recovery, or favorable behavior.",
                "removal_order": ["ornamental effects", "secondary motion", "secondary color"],
            },
            "design_register": {
                "mode": "mixed",
                "source": "inferred",
                "rationale": "Balance identity-building moments with clear, familiar routine use until the project evidence supports a narrower register.",
                "brand_behavior": "Use the signature where orientation, recognition, or narrative matters.",
                "product_behavior": "Keep repeated, dense, consequential, and recovery surfaces task-led and quiet.",
            },
            "usage_scene": {
                "people": "The recorded primary audience",
                "setting": "The documented or reasonably inferred use environment",
                "ambient_conditions": "Unknown; avoid relying on fragile contrast, motion, or ideal viewing conditions.",
                "frequency_and_consequence": "Unknown; preserve comprehension and recovery while the context is refined.",
                "design_effect": "Use the scene as a provisional calibration aid rather than a verified user fact.",
            },
            "color_commitment": {
                "level": "restrained",
                "source": "inferred",
                "rationale": "Keep color subordinate until project-specific semantic and brand roles are authored.",
                "role_distribution": "Reserve stronger chroma for identity or consequential state and keep routine fields quiet.",
                "contrast_method": "Verify text and control contrast in rendered artifacts; never rely on color alone.",
            },
            "anti_reflex_review": {
                "category_default": "No project-specific category reflex was recorded for this legacy direction.",
                "anti_default_default": "Do not replace an obvious category default with an equally interchangeable anti-default aesthetic.",
                "revision": "Re-derive palette, typography, composition, imagery, and voice from the subject before implementation-facing status.",
            },
            "implementation_system": {
                "status": "provisional",
                "token_strategy": ["Translate approved semantic roles into the actual project token system."],
                "type_constraints": ["Set readable measures, wrapping behavior, fallbacks, and responsive ceilings before implementation-facing status."],
                "layout_constraints": ["Define spacing rhythm, collision behavior, and narrow-screen transformation in the target stack."],
                "motion_constraints": ["Preserve content without motion and respect reduced-motion preferences."],
                "component_recipes": ["Use installed primitives for behavior while keeping the project-specific carrier visible."],
                "hardening_checks": ["Test long content, overflow, focus, target sizes, contrast, interruption, and recovery."],
            },
            "brand_signature": {
                "identity_premise": creative_signature,
                "primary_carrier": {"role": "Make the direction recognizable.", "rule": creative_signature, "quiet_variant": "Preserve the same relationship with reduced scale and contrast."},
                "recurring_carriers": [{"carrier_id": "project-language", "role": "Carry identity through routine content.", "rule": "Use subject-specific nouns and actions consistently."}],
                "utility_expression": "Keep routine controls conventional while preserving the signature relationship in labels, hierarchy, or state treatment.",
                "quiet_mode": "Reduce intensity on dense, consequential, error, permission, and recovery surfaces without removing identity.",
                "campaign_mode": "Expand the primary carrier only when the target supports expressive orientation or storytelling.",
                "subject_tokens": [{"token_id": "signature-rule", "role": "Encode the primary carrier as a reusable semantic rule.", "visual_rule": creative_signature}],
                "transformation_matrix": [{"context": "routine utility", "target_weight": 0.25, "behavior": "Use the quiet variant and preserve familiar controls."}],
                "prohibited_substitutions": ["Do not replace the project-specific carrier with a generic category treatment."],
                "recognition_tests": ["Confirm the design remains recognizable without its logo or primary accent color."],
            },
            "refinement_passes": [
                {"pass_id": pass_id, "status": "pending", "purpose": "Legacy direction requires an explicit refinement pass.", "changes": [], "preserved": [], "unresolved": ["Refinement evidence not yet recorded."]}
                for pass_id in REFINEMENT_PASS_IDS
            ],
            "contextual_reviews": [],
            "provenance_ids": sorted(provenance_ids),
        }
    if not isinstance(value, dict):
        raise DesignError("distinctive_expression must be an object")
    result: dict[str, Any] = {}
    for key in ("aesthetic_thesis", "signature_element"):
        text = value.get(key)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression requires {key}")
        result[key] = text.strip()
    for key in ("subject_world", "anti_defaults", "reference_compositions", "uniqueness_checks"):
        items = value.get(key)
        if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"distinctive_expression requires non-empty {key}")
        result[key] = list(dict.fromkeys(item.strip() for item in items))
    risk = value.get("aesthetic_risk")
    if not isinstance(risk, dict):
        raise DesignError("distinctive_expression requires aesthetic_risk")
    result["aesthetic_risk"] = {}
    for key in ("move", "rationale", "boundary"):
        text = risk.get(key)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression aesthetic_risk requires {key}")
        result["aesthetic_risk"][key] = text.strip()
    system = value.get("expression_system")
    dimensions = ("palette", "typography", "composition", "material_imagery", "motion", "voice")
    if not isinstance(system, dict) or set(system) != set(dimensions):
        raise DesignError("distinctive_expression requires the complete expression_system")
    result["expression_system"] = {}
    for dimension in dimensions:
        items = system[dimension]
        if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"distinctive_expression requires non-empty expression_system {dimension}")
        result["expression_system"][dimension] = list(dict.fromkeys(item.strip() for item in items))
    budget = value.get("expression_budget")
    if not isinstance(budget, dict):
        raise DesignError("distinctive_expression requires expression_budget")
    result["expression_budget"] = {}
    target_weight = budget.get("target_weight", 0.5)
    exploration_ceiling = budget.get("exploration_ceiling", max(0.7, target_weight) if isinstance(target_weight, (int, float)) and not isinstance(target_weight, bool) else 0.7)
    if not isinstance(target_weight, (int, float)) or isinstance(target_weight, bool) or not 0 <= target_weight <= 1:
        raise DesignError("distinctive_expression expression_budget target_weight must be between 0 and 1")
    if not isinstance(exploration_ceiling, (int, float)) or isinstance(exploration_ceiling, bool) or not 0 <= exploration_ceiling <= 1:
        raise DesignError("distinctive_expression expression_budget exploration_ceiling must be between 0 and 1")
    if exploration_ceiling < target_weight:
        raise DesignError("distinctive_expression expression_budget exploration_ceiling must be greater than or equal to target_weight")
    mode = budget.get("mode", "calibrated")
    source = budget.get("source", "inferred")
    if mode not in EXPRESSION_MODES:
        raise DesignError("distinctive_expression expression_budget requires a valid mode")
    if source not in EXPRESSION_SOURCES:
        raise DesignError("distinctive_expression expression_budget requires a valid source")
    rationale = budget.get("weight_rationale", "Balance subject-specific expression with the recorded project constraints and consequence level.")
    if not isinstance(rationale, str) or not rationale.strip():
        raise DesignError("distinctive_expression expression_budget requires weight_rationale")
    result["expression_budget"].update({
        "target_weight": float(target_weight),
        "exploration_ceiling": float(exploration_ceiling),
        "mode": mode,
        "source": source,
        "weight_rationale": rationale.strip(),
    })
    for key in ("boundary_being_pushed", "quiet_field", "containment_boundary"):
        text = budget.get(key)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression expression_budget requires {key}")
        result["expression_budget"][key] = text.strip()
    primary = budget.get("primary_dimension")
    if primary not in EXPRESSION_DIMENSIONS:
        raise DesignError("distinctive_expression expression_budget requires a valid primary_dimension")
    result["expression_budget"]["primary_dimension"] = primary
    for key in ("supporting_dimensions", "restrained_dimensions"):
        items = budget.get(key)
        if not isinstance(items, list) or not items or any(item not in EXPRESSION_DIMENSIONS for item in items):
            raise DesignError(f"distinctive_expression expression_budget has invalid {key}")
        result["expression_budget"][key] = list(dict.fromkeys(items))
    if set(result["expression_budget"]["supporting_dimensions"]) & set(result["expression_budget"]["restrained_dimensions"]):
        raise DesignError("distinctive_expression expression_budget dimensions must not conflict")
    intensity = budget.get("intensity")
    if not isinstance(intensity, dict) or set(intensity) != set(EXPRESSION_DIMENSIONS) or any(level not in EXPRESSION_INTENSITIES for level in intensity.values()):
        raise DesignError("distinctive_expression expression_budget requires a complete intensity map")
    if [dimension for dimension, level in intensity.items() if level == "signature"] != [primary]:
        raise DesignError("distinctive_expression expression_budget requires exactly one signature intensity matching primary_dimension")
    if sum(level == "quiet" for level in intensity.values()) < 2:
        raise DesignError("distinctive_expression expression_budget requires at least two quiet dimensions")
    result["expression_budget"]["intensity"] = dict(intensity)
    removal = budget.get("removal_order")
    if not isinstance(removal, list) or not removal or any(not isinstance(item, str) or not item.strip() for item in removal):
        raise DesignError("distinctive_expression expression_budget requires removal_order")
    result["expression_budget"]["removal_order"] = list(dict.fromkeys(item.strip() for item in removal))
    register = value.get("design_register", {})
    if not isinstance(register, dict):
        raise DesignError("distinctive_expression design_register must be an object")
    register_mode = register.get("mode", "mixed")
    register_source = register.get("source", "inferred")
    if register_mode not in DESIGN_REGISTERS or register_source not in EXPRESSION_SOURCES:
        raise DesignError("distinctive_expression design_register requires a valid mode and source")
    result["design_register"] = {"mode": register_mode, "source": register_source}
    register_defaults = {
        "rationale": "Balance identity-building moments with clear, familiar routine use.",
        "brand_behavior": "Use the signature where orientation, recognition, or narrative matters.",
        "product_behavior": "Keep repeated, dense, consequential, and recovery surfaces task-led and quiet.",
    }
    for key, default in register_defaults.items():
        text = register.get(key, default)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression design_register requires {key}")
        result["design_register"][key] = text.strip()
    scene = value.get("usage_scene", {})
    if not isinstance(scene, dict):
        raise DesignError("distinctive_expression usage_scene must be an object")
    scene_defaults = {
        "people": "The recorded primary audience",
        "setting": "The documented or reasonably inferred use environment",
        "ambient_conditions": "Unknown; avoid relying on ideal viewing conditions.",
        "frequency_and_consequence": "Unknown; preserve comprehension and recovery while refining context.",
        "design_effect": "Use the scene as a provisional calibration aid rather than a verified user fact.",
    }
    result["usage_scene"] = {}
    for key, default in scene_defaults.items():
        text = scene.get(key, default)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression usage_scene requires {key}")
        result["usage_scene"][key] = text.strip()
    color_commitment = value.get("color_commitment", {})
    if not isinstance(color_commitment, dict):
        raise DesignError("distinctive_expression color_commitment must be an object")
    color_level = color_commitment.get("level", "restrained")
    color_source = color_commitment.get("source", "inferred")
    if color_level not in COLOR_COMMITMENTS or color_source not in EXPRESSION_SOURCES:
        raise DesignError("distinctive_expression color_commitment requires a valid level and source")
    result["color_commitment"] = {"level": color_level, "source": color_source}
    color_defaults = {
        "rationale": "Keep color subordinate until project-specific semantic and brand roles are authored.",
        "role_distribution": "Reserve stronger chroma for identity or consequential state and keep routine fields quiet.",
        "contrast_method": "Verify text and control contrast in rendered artifacts; never rely on color alone.",
    }
    for key, default in color_defaults.items():
        text = color_commitment.get(key, default)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression color_commitment requires {key}")
        result["color_commitment"][key] = text.strip()
    anti_reflex = value.get("anti_reflex_review", {})
    if not isinstance(anti_reflex, dict):
        raise DesignError("distinctive_expression anti_reflex_review must be an object")
    anti_reflex_defaults = {
        "category_default": "Identify the most likely category reflex before implementation.",
        "anti_default_default": "Identify the fashionable counter-default that could replace it without becoming more specific.",
        "revision": "Revise any interchangeable choice from subject evidence before implementation-facing status.",
    }
    result["anti_reflex_review"] = {}
    for key, default in anti_reflex_defaults.items():
        text = anti_reflex.get(key, default)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression anti_reflex_review requires {key}")
        result["anti_reflex_review"][key] = text.strip()
    implementation = value.get("implementation_system", {})
    if not isinstance(implementation, dict):
        raise DesignError("distinctive_expression implementation_system must be an object")
    implementation_status = implementation.get("status", "provisional")
    if implementation_status not in {"provisional", "stack-grounded"}:
        raise DesignError("distinctive_expression implementation_system requires a valid status")
    result["implementation_system"] = {"status": implementation_status}
    implementation_defaults = {
        "token_strategy": ["Translate approved semantic roles into the actual project token system."],
        "type_constraints": ["Set readable measures, wrapping behavior, fallbacks, and responsive ceilings."],
        "layout_constraints": ["Define spacing rhythm, collision behavior, and narrow-screen transformation."],
        "motion_constraints": ["Preserve content without motion and respect reduced-motion preferences."],
        "component_recipes": ["Use installed primitives for behavior while preserving project-specific expression."],
        "hardening_checks": ["Test long content, overflow, focus, target sizes, contrast, interruption, and recovery."],
    }
    for key, default in implementation_defaults.items():
        items = implementation.get(key, default)
        if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"distinctive_expression implementation_system requires non-empty {key}")
        result["implementation_system"][key] = list(dict.fromkeys(item.strip() for item in items))
    brand = value.get("brand_signature")
    if brand is None:
        brand = {
            "identity_premise": result["aesthetic_thesis"],
            "primary_carrier": {"role": "Carry the selected direction's identity.", "rule": result["signature_element"], "quiet_variant": "Preserve the same relationship with reduced expressive intensity."},
            "recurring_carriers": [{"carrier_id": "signature-language", "role": "Repeat the identity in routine surfaces.", "rule": result["signature_element"]}],
            "utility_expression": "Apply the signature through hierarchy and language without changing conventional control semantics.",
            "quiet_mode": "Reduce scale, contrast, motion, imagery, and depth while preserving the primary relationship.",
            "campaign_mode": "Expand the primary carrier within the expression ceiling without introducing a competing signature.",
            "subject_tokens": [{"token_id": "primary-signature", "role": "Encode the selected signature.", "visual_rule": result["signature_element"]}],
            "transformation_matrix": [{"context": "routine utility", "target_weight": min(result["expression_budget"]["target_weight"], 0.4), "behavior": "Use the quiet variant and preserve familiar controls."}],
            "prohibited_substitutions": ["Do not replace the subject-derived signature with an interchangeable library or category default."],
            "recognition_tests": ["Confirm the artifact remains recognizable without its logo, primary color, imagery, or motion."],
        }
    if not isinstance(brand, dict):
        raise DesignError("distinctive_expression brand_signature must be an object")
    normalized_brand: dict[str, Any] = {}
    for key in ("identity_premise", "utility_expression", "quiet_mode", "campaign_mode"):
        text = brand.get(key)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression brand_signature requires {key}")
        normalized_brand[key] = text.strip()
    primary_carrier = brand.get("primary_carrier")
    if not isinstance(primary_carrier, dict):
        raise DesignError("distinctive_expression brand_signature requires primary_carrier")
    normalized_brand["primary_carrier"] = {}
    for key in ("role", "rule", "quiet_variant"):
        text = primary_carrier.get(key)
        if not isinstance(text, str) or not text.strip():
            raise DesignError(f"distinctive_expression brand_signature primary_carrier requires {key}")
        normalized_brand["primary_carrier"][key] = text.strip()
    for key in ("recurring_carriers", "subject_tokens"):
        items = brand.get(key)
        if not isinstance(items, list) or not items or any(not isinstance(item, dict) for item in items):
            raise DesignError(f"distinctive_expression brand_signature requires {key}")
        normalized_brand[key] = []
        id_key = "carrier_id" if key == "recurring_carriers" else "token_id"
        for item in items:
            normalized = {id_key: _identifier(str(item.get(id_key, "")), f"brand {id_key}")}
            for field in ("role", "rule" if key == "recurring_carriers" else "visual_rule"):
                text = item.get(field)
                if not isinstance(text, str) or not text.strip():
                    raise DesignError(f"distinctive_expression brand_signature {key} requires {field}")
                normalized[field] = text.strip()
            normalized_brand[key].append(normalized)
    matrix = brand.get("transformation_matrix")
    if not isinstance(matrix, list) or not matrix or any(not isinstance(item, dict) for item in matrix):
        raise DesignError("distinctive_expression brand_signature requires transformation_matrix")
    normalized_brand["transformation_matrix"] = []
    for item in matrix:
        context = item.get("context")
        behavior = item.get("behavior")
        weight = item.get("target_weight")
        if not isinstance(context, str) or not context.strip() or not isinstance(behavior, str) or not behavior.strip():
            raise DesignError("distinctive_expression brand_signature transformation_matrix requires context and behavior")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or not 0 <= weight <= 1:
            raise DesignError("distinctive_expression brand_signature transformation weight must be between 0 and 1")
        normalized_brand["transformation_matrix"].append({"context": context.strip(), "target_weight": float(weight), "behavior": behavior.strip()})
    for key in ("prohibited_substitutions", "recognition_tests"):
        items = brand.get(key)
        if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"distinctive_expression brand_signature requires {key}")
        normalized_brand[key] = list(dict.fromkeys(item.strip() for item in items))
    result["brand_signature"] = normalized_brand
    passes = value.get("refinement_passes")
    if not isinstance(passes, list) or [item.get("pass_id") for item in passes if isinstance(item, dict)] != list(REFINEMENT_PASS_IDS):
        raise DesignError("distinctive_expression requires the ordered multi-pass refinement record")
    result["refinement_passes"] = []
    for item in passes:
        status = item.get("status")
        if status not in REFINEMENT_PASS_STATUSES:
            raise DesignError(f"Refinement pass {item.get('pass_id')} requires a valid status")
        normalized = {"pass_id": item["pass_id"], "status": status}
        purpose = item.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            raise DesignError(f"Refinement pass {item['pass_id']} requires purpose")
        normalized["purpose"] = purpose.strip()
        for key in ("changes", "preserved", "unresolved"):
            items_value = item.get(key, [])
            if not isinstance(items_value, list) or any(not isinstance(entry, str) or not entry.strip() for entry in items_value):
                raise DesignError(f"Refinement pass {item['pass_id']} has invalid {key}")
            normalized[key] = list(dict.fromkeys(entry.strip() for entry in items_value))
        if status == "completed" and not (normalized["changes"] or normalized["preserved"]):
            raise DesignError(f"Completed refinement pass {item['pass_id']} requires a recorded outcome")
        result["refinement_passes"].append(normalized)
    reviews = value.get("contextual_reviews", [])
    if not isinstance(reviews, list) or any(not isinstance(item, dict) for item in reviews):
        raise DesignError("distinctive_expression contextual_reviews must be a list of objects")
    result["contextual_reviews"] = []
    seen_review_ids: set[str] = set()
    for item in reviews:
        review_id = _identifier(str(item.get("review_id") or ""), "contextual review ID")
        if review_id in seen_review_ids:
            raise DesignError(f"Duplicate contextual review ID: {review_id}")
        routing = item.get("routing")
        if routing not in {"explicit", "inferred"}:
            raise DesignError(f"Contextual review {review_id} requires explicit or inferred routing")
        normalized_review = {"review_id": review_id, "routing": routing}
        for key in ("perspective", "why_applicable", "finding", "design_response", "verification"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Contextual review {review_id} requires {key}")
            normalized_review[key] = text.strip()
        preserved = item.get("preserved_behavior")
        if not isinstance(preserved, list) or not preserved or any(not isinstance(entry, str) or not entry.strip() for entry in preserved):
            raise DesignError(f"Contextual review {review_id} requires preserved_behavior")
        normalized_review["preserved_behavior"] = list(dict.fromkeys(entry.strip() for entry in preserved))
        result["contextual_reviews"].append(normalized_review)
        seen_review_ids.add(review_id)
    contextual_pass = next(item for item in result["refinement_passes"] if item["pass_id"] == "contextual-review")
    if contextual_pass["status"] == "completed" and not result["contextual_reviews"]:
        raise DesignError("A completed contextual-review pass requires evidence-bearing contextual_reviews")
    linked = value.get("provenance_ids", [])
    if not isinstance(linked, list) or any(not isinstance(item, str) or not item.strip() for item in linked):
        raise DesignError("distinctive_expression has invalid provenance_ids")
    result["provenance_ids"] = list(dict.fromkeys(item.strip() for item in linked))
    if set(result["provenance_ids"]) - provenance_ids:
        raise DesignError("distinctive_expression references unknown creative provenance IDs")
    if provenance_ids and not result["provenance_ids"]:
        raise DesignError("distinctive_expression must link its creative provenance")
    return result


def _generated_direction(payload: dict[str, Any], index: int) -> dict[str, Any]:
    strategy = DIRECTION_STRATEGIES[index]
    theme = payload["themes"][index % len(payload["themes"])] if payload["themes"] else ""
    message = payload["message_structures"][index % len(payload["message_structures"])] if payload["message_structures"] else ""
    scope = ", ".join(payload["sections"]) if payload["sections"] else "the experience"
    name = strategy["name"]
    summary = strategy["summary"].replace("the experience", scope)
    if theme:
        summary += f" Honor the explicitly requested {theme} character."
    if message:
        summary += f" Use the explicitly requested {message} narrative structure."
    principles = [
        payload["intent"],
        strategy["principle"],
        "Make consequential choices understandable, reversible where possible, and accessible.",
    ]
    principles.extend(payload["constraints"][:2])
    required_dimensions = _required_grammar_dimensions(payload["targets"])
    preservation = payload["preserve"] or payload["current_strengths"]
    creative_signature = f"Use {strategy['name'].casefold()} as a recognizable organizing move across the relevant visual and interaction dimensions, with project-specific expression supplied during revision."
    return {
        "direction_id": f"direction-{index + 1}",
        "name": name,
        "summary": summary,
        "creative_signature": creative_signature,
        "creative_provenance": [{
            "provenance_id": "project-intent",
            "classification": "inferred",
            "observation": payload["intent"],
            "source_refs": [],
            "design_implication": f"Use the {strategy['name'].casefold()} strategy only as a provisional recovery direction until subject-specific expression is authored.",
        }],
        "distinctive_expression": {
            "aesthetic_thesis": creative_signature,
            "subject_world": [f"Infer initial visual language from the project intent, audience, and the subject matter of {scope}; verify it against inspected artifacts before approval."],
            "signature_element": creative_signature,
            "aesthetic_risk": {
                "move": f"Make the {strategy['name'].casefold()} organization visually unmistakable without relying on a generic category template.",
                "rationale": "A bounded expressive move gives the recovery direction enough character to evaluate.",
                "boundary": "Preserve familiar semantics, accessibility, recovery, and favorable behavior.",
            },
            "anti_defaults": ["Reject interchangeable card grids, editorial styling, or fashionable palettes unless the subject and inspected evidence justify them."],
            "expression_system": {
                "palette": ["Name four to six subject-derived color roles and concrete values during revision; do not inherit a model-default palette."],
                "typography": ["Define distinct display, body, and utility roles whose character follows the subject rather than a reusable pairing."],
                "composition": [strategy["grammar"]["composition"]],
                "material_imagery": ["Derive material and image treatment from inspected subject artifacts or label it inferred."],
                "motion": [strategy["grammar"].get("motion", "Use no motion for static targets.")],
                "voice": [strategy["grammar"]["voice"]],
            },
            "expression_budget": {
                "boundary_being_pushed": f"Make {strategy['name'].casefold()} the single dominant organizing move.",
                "primary_dimension": "composition",
                "supporting_dimensions": ["voice"],
                "restrained_dimensions": ["typography", "color", "motion", "imagery", "surface_depth"],
                "intensity": {
                    "composition": "signature",
                    "typography": "quiet",
                    "color": "quiet",
                    "motion": "quiet",
                    "imagery": "quiet",
                    "surface_depth": "quiet",
                    "voice": "present",
                },
                "quiet_field": "Keep type, color, motion, imagery, and surface treatment calm until subject-specific evidence supports a different allocation.",
                "containment_boundary": "The organizing move must not compromise reading order, accessibility, recovery, or narrow-screen comprehension.",
                "removal_order": ["Remove incidental decoration", "Reduce supporting emphasis", "Simplify the signature before compromising comprehension"],
            },
            "refinement_passes": [
                {
                    "pass_id": pass_id,
                    "status": "pending",
                    "purpose": purpose,
                    "changes": [],
                    "preserved": [],
                    "unresolved": ["Recovery direction requires an authored, evidence-based refinement pass."],
                }
                for pass_id, purpose in (
                    ("provenance-grounding", "Ground the direction in inspected or supplied subject evidence."),
                    ("divergent-exploration", "Test materially different organizing ideas before convergence."),
                    ("boundary-push", "Strengthen the most subject-specific expressive move."),
                    ("contextual-review", "Review the concept through the contextually relevant usability and consequence perspectives."),
                    ("restraint-edit", "Protect legibility and rhythm by quieting competing expression."),
                    ("responsive-transformation", "Make the concept transform coherently across target sizes and modalities."),
                    ("artifact-critique", "Compare rendered artifacts with the approved design and correct visible drift."),
                )
            ],
            "contextual_reviews": [],
            "reference_compositions": ["Create one wide and one narrow target-native composition before treating this recovery direction as implementation-facing."],
            "uniqueness_checks": ["Confirm the composition, type, palette, and signature would change materially if the subject changed."],
            "provenance_ids": ["project-intent"],
        },
        "content_rules": ["Label illustrative or inferred content where it appears; do not present fixture values or unverified claims as observed fact."],
        "audience_strategy": ["Use a shared core for common intent and make materially different audience routes explicit rather than averaging their needs."],
        "prototype_boundaries": ["Treat demonstrated surfaces and states as bounded evidence; do not imply omitted workflows are designed or implementation-ready."],
        "principles": principles,
        "design_grammar": {dimension: [strategy["grammar"][dimension]] for dimension in required_dimensions},
        "experience_principles": [
            strategy["principle"],
            *[f"Preserve {item.rstrip('.').casefold()}." for item in preservation],
        ],
        "experience_architecture": [
            f"Organize {scope} around the primary outcome and make entry, continuation, completion, interruption, and recovery explicit.",
        ],
        "component_patterns": [
            "Reuse established product patterns where they remain coherent; introduce a new pattern only for a distinct semantic need.",
        ],
        "implementation_guidance": [
            "Translate these decisions into project tokens and reusable components before applying local exceptions.",
        ],
        "validation_criteria": payload["validation_criteria"] or [
            "The primary audience can identify the next meaningful action and its current state.",
            *[f"The implementation preserves: {item}" for item in preservation],
        ],
        "prohibited_patterns": payload["non_goals"] or [
            "Do not add visual novelty that weakens established behavior, accessibility, or recovery.",
        ],
        "variation_levers": [
            "Adjust information density without changing task priority.",
            f"Increase or reduce the {strategy['name'].casefold()} emphasis without weakening accessibility or recovery.",
        ],
        "tradeoffs": payload["open_questions"] or ["Greater focus reduces simultaneous exposure of secondary capabilities."],
    }


def _validate_direction(value: Any, index: int, targets: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError("Each direction must be an object")
    result = dict(value)
    result["direction_id"] = _identifier(str(result.get("direction_id") or f"direction-{index + 1}"), "direction ID")
    for key in ("name", "summary", "creative_signature"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise DesignError(f"Direction {result['direction_id']} requires {key}")
    result["creative_provenance"] = _validate_creative_provenance(result.get("creative_provenance"))
    result["distinctive_expression"] = _validate_distinctive_expression(
        result.get("distinctive_expression"),
        {item["provenance_id"] for item in result["creative_provenance"]},
        result["creative_signature"],
    )
    grammar = result.get("design_grammar")
    required_dimensions = _required_grammar_dimensions(targets)
    if not isinstance(grammar, dict) or set(grammar) != set(required_dimensions):
        raise DesignError(f"Direction {result['direction_id']} requires the complete design grammar appropriate to its targets")
    for dimension in required_dimensions:
        rules = grammar[dimension]
        if not isinstance(rules, list) or not rules or any(not isinstance(item, str) or not item.strip() for item in rules):
            raise DesignError(f"Direction {result['direction_id']} requires non-empty design grammar dimension {dimension}")
    for key in (
        "principles", "experience_principles", "experience_architecture",
        "component_patterns", "implementation_guidance", "validation_criteria",
        "prohibited_patterns", "variation_levers", "tradeoffs",
    ):
        if not isinstance(result.get(key), list) or not result[key] or any(not isinstance(item, str) or not item.strip() for item in result[key]):
            raise DesignError(f"Direction {result['direction_id']} requires non-empty {key}")
    defaults = {
        "content_rules": ["Distinguish inspected, supplied, inferred, and illustrative content; qualify anything not evidenced."],
        "audience_strategy": ["Preserve shared needs while making material audience differences explicit."],
        "prototype_boundaries": ["Do not present unshown surfaces, states, or workflows as demonstrated or implementation-ready."],
    }
    for key, fallback in defaults.items():
        candidate = result.get(key, fallback)
        if not isinstance(candidate, list) or not candidate or any(not isinstance(item, str) or not item.strip() for item in candidate):
            raise DesignError(f"Direction {result['direction_id']} requires non-empty {key}")
        result[key] = candidate
    return result


def draft(root: Path, config: dict[str, Any], catalog_path: Path, input_path: Path) -> dict[str, Any]:
    _enabled(config)
    payload = _read_json(input_path)
    for key in ("title", "intent"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise DesignError(f"Design input requires {key}")
    if "direction_count_basis" in payload and (
        not isinstance(payload["direction_count_basis"], str) or not payload["direction_count_basis"].strip()
    ):
        raise DesignError("direction_count_basis must be a non-empty string when supplied")
    industry = payload.get("industry", "")
    if not isinstance(industry, str):
        raise DesignError("industry must be a string when supplied")
    payload["industry"] = industry.strip()
    manual_lenses = "lenses" in payload
    for key in ("audiences", "targets"):
        payload[key] = _validate_strings(payload, key, required=True)
    payload["content_provenance"] = _validate_content_provenance(payload.get("content_provenance"))
    payload["audience_architecture"] = _validate_audience_architecture(payload.get("audience_architecture"), payload["audiences"])
    payload["prototype_scope"] = _validate_prototype_scope(payload.get("prototype_scope"))
    payload["validation_matrix"] = _validate_validation_matrix(payload.get("validation_matrix"), payload["prototype_scope"])
    payload["direction_assessment"] = _validate_direction_assessment(payload.get("direction_assessment"))
    payload["insight_decisions"] = _validate_insight_decisions(payload.get("insight_decisions"))
    payload["implementation_context"] = _validate_implementation_context(payload.get("implementation_context"))
    payload["component_map"] = _validate_component_map(payload.get("component_map"))
    payload["asset_strategy"] = _validate_asset_strategy(payload.get("asset_strategy"))
    payload["completion_contract"] = _validate_completion_contract(payload.get("completion_contract"), payload["targets"])
    if payload["completion_contract"] and payload["completion_contract"]["mode"] == "complete-prototype" and "ui" in payload["targets"]:
        if not payload["implementation_context"] or not payload["component_map"] or not payload["asset_strategy"]:
            raise DesignError("Complete UI prototypes require implementation_context, component_map, and asset_strategy")
    for key in ("sections", "themes", "message_structures"):
        payload[key] = _validate_strings(payload, key)
    if manual_lenses:
        payload["lenses"] = _validate_strings(payload, "lenses", required=True)
    for key in (
        "constraints",
        "preserve",
        "open_questions",
        "working_assumptions",
        "evidence_inspected",
        "current_strengths",
        "current_gaps",
        "design_debt",
        "non_goals",
        "validation_criteria",
        "consequences",
        "workflow_signals",
        "interaction_signals",
        "risk_signals",
        "source_note_ids",
        "memory_ids",
    ):
        payload[key] = _validate_strings(payload, key)
    if not set(payload["targets"]).issubset(TARGETS):
        raise DesignError(f"Unknown targets: {sorted(set(payload['targets']) - TARGETS)}")
    catalog = load_catalog(catalog_path)
    lens_routing: list[dict[str, Any]] = []
    if not manual_lenses:
        payload["lenses"], lens_routing = _infer_lenses(payload, load_lens_routing(catalog_path, catalog))
    catalog_packs = _selected_packs(payload, catalog)
    if lens_routing:
        lens_routing = _bind_lens_routing(lens_routing, catalog, catalog_packs)
    composition_resolution = _resolve_composition(payload, load_composition_precedence(catalog_path, catalog))
    selected_pack_ids = {pack["pack_id"] for pack in catalog_packs}
    selected_catalog_packs = [pack for pack in catalog["packs"] if pack["pack_id"] in selected_pack_ids]
    evidence_application: dict[str, dict[str, Any]] = {}
    for target in payload["targets"]:
        groups = {
            "validated_packs": [pack["pack_id"] for pack in selected_catalog_packs if pack["modalities"][target] == "validated"],
            "inferred_packs": [pack["pack_id"] for pack in selected_catalog_packs if pack["modalities"][target] == "inferred"],
            "not_applicable_packs": [pack["pack_id"] for pack in selected_catalog_packs if pack["modalities"][target] == "not-applicable"],
        }
        active = {status for status, key in (("validated", "validated_packs"), ("inferred", "inferred_packs")) if groups[key]}
        status = "mixed" if len(active) > 1 else next(iter(active), "not-applicable")
        evidence_application[target] = {"status": status, **groups}
    count = _direction_count(payload)
    if payload["direction_assessment"]:
        unresolved_ambiguities = set(payload["direction_assessment"]["material_ambiguities"]) - set(payload["direction_assessment"]["resolved_by_evidence"])
        if count == 1 and unresolved_ambiguities:
            raise DesignError("One direction is not allowed while material design ambiguities remain unresolved")
    supplied = payload.get("directions")
    if supplied is not None:
        if not isinstance(supplied, list) or not 1 <= len(supplied) <= 3:
            raise DesignError("Supplied creative work requires one to three directions")
        directions = [_validate_direction(item, index, payload["targets"]) for index, item in enumerate(supplied)]
    else:
        directions = [_validate_direction(_generated_direction(payload, index), index, payload["targets"]) for index in range(count)]
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
        "lens_selection_mode": "manual" if manual_lenses else "inferred",
        "lens_routing": lens_routing,
        "composition_resolution": composition_resolution,
        "constraints": payload["constraints"],
        "preserve": payload["preserve"],
        "open_questions": payload["open_questions"],
        "working_assumptions": payload["working_assumptions"],
        "evidence_inspected": payload["evidence_inspected"],
        "current_strengths": payload["current_strengths"],
        "current_gaps": payload["current_gaps"],
        "design_debt": payload["design_debt"],
        "non_goals": payload["non_goals"],
        "validation_criteria": payload["validation_criteria"],
        "consequences": payload["consequences"],
        "workflow_signals": payload["workflow_signals"],
        "interaction_signals": payload["interaction_signals"],
        "risk_signals": payload["risk_signals"],
        "source_note_ids": payload["source_note_ids"],
        "memory_ids": payload["memory_ids"],
        "content_provenance": payload["content_provenance"],
        "audience_architecture": payload["audience_architecture"],
        "prototype_scope": payload["prototype_scope"],
        "implementation_context": payload["implementation_context"],
        "component_map": payload["component_map"],
        "asset_strategy": payload["asset_strategy"],
        "completion_contract": payload["completion_contract"],
        "validation_matrix": payload["validation_matrix"],
        "direction_assessment": payload["direction_assessment"],
        "insight_decisions": payload["insight_decisions"],
        "directions": directions,
        "direction_count_basis": payload.get("direction_count_basis", "legacy heuristic" if payload.get("direction_count") is None else "agent assessed material ambiguity"),
        "catalog_packs": catalog_packs,
        "evidence_application": evidence_application,
        "catalog_version": catalog["catalog_version"],
        "created_at": _now(),
        "execution_authorized": False,
    }
    _write_json(prior_path, record)
    return record


def _direction_markdown(draft_record: dict[str, Any], selected: list[dict[str, Any]]) -> str:
    targets = ", ".join(draft_record["targets"])
    evidence = draft_record["evidence_application"]
    statuses = {evidence[target]["status"] for target in draft_record["targets"]}
    modality = next(iter(statuses)) if len(statuses) == 1 else "mixed"
    lines = [
        f"# {draft_record['title']}", "",
        f"Design ID: `{draft_record['design_id']}`  ",
        f"Revision: `{draft_record['revision']}`  ",
        f"Targets: `{targets}`  ",
        f"Evidence application: `{modality}`", "",
        f"Direction count basis: {draft_record['direction_count_basis']}", "",
        "## Decision at a glance", "",
        f"**Intent:** {draft_record['intent']}", "",
        f"**Audience:** {'; '.join(draft_record['audiences'])}", "",
        "**Selected direction:**", "",
        *[f"- **{direction['name']}:** {direction['summary']}" for direction in selected], "",
        "**Creative signature:**", "",
        *[f"- {direction['creative_signature']}" for direction in selected], "",
        "**Aesthetic proposition:**", "",
        *[f"- {direction['distinctive_expression']['aesthetic_thesis']}" for direction in selected], "",
        "**Bounded aesthetic risk:**", "",
        *[f"- {direction['distinctive_expression']['aesthetic_risk']['move']} — Boundary: {direction['distinctive_expression']['aesthetic_risk']['boundary']}" for direction in selected], "",
        "**Principal tradeoff:**", "",
        *[f"- {item}" for direction in selected for item in direction["tradeoffs"][:1]], "",
        "**Preservation promise:**", "",
        *([f"- {item}" for item in (draft_record["preserve"] or draft_record["current_strengths"])] or ["- No favorable behavior was evidenced for preservation."]), "",
        "**Material unknowns:**", "",
        *([f"- {item}" for item in draft_record["open_questions"][:2]] or ["- None currently material."]), "",
        "## Product and experience context", "", draft_record["intent"], "",
        "Audiences:", "",
        *[f"- {item}" for item in draft_record["audiences"]], "",
    ]
    if draft_record["lens_selection_mode"] == "manual":
        lines.extend([
            "## Explicit design concepts",
            "",
            "The following concepts were explicitly supplied for this bounded design.",
            "",
            f"- Lenses: {', '.join(f'`{value}`' for value in draft_record['lenses'])}",
            "",
        ])
    lines.extend(["## Current-state assessment", ""])
    for heading, key in (
        ("Evidence inspected", "evidence_inspected"),
        ("Existing strengths", "current_strengths"),
        ("Gaps and inconsistencies", "current_gaps"),
        ("Design debt", "design_debt"),
    ):
        lines.extend([f"### {heading}", "", *([f"- {item}" for item in draft_record[key]] or ["- None recorded."]), ""])
    provenance = draft_record.get("content_provenance", [])
    lines.extend(["## Content and evidence integrity", ""])
    if provenance:
        for item in provenance:
            detail = f"- **{item['content_id']} ({item['classification']}):** {item['statement']}"
            if item["required_qualification"]:
                detail += f" Qualification: {item['required_qualification']}"
            lines.append(detail)
    else:
        lines.append("- No content provenance records were supplied; do not treat illustrative copy, fixture values, or inferred claims as verified evidence.")
    lines.append("")
    architecture = draft_record.get("audience_architecture")
    lines.extend(["## Audience architecture", ""])
    if architecture:
        lines.extend([f"Mode: `{architecture['mode']}`", ""])
        lines.extend(["Shared core:", "", *([f"- {item}" for item in architecture["shared_core"]] or ["- None recorded."]), ""])
        for route in architecture["routes"]:
            lines.extend([f"### {route['audience']}: {route['route']}", "", *[f"- {item}" for item in route["needs"]], ""])
        if architecture["unresolved_conflicts"]:
            lines.extend(["Unresolved audience conflicts:", "", *[f"- {item}" for item in architecture["unresolved_conflicts"]], ""])
    else:
        lines.extend(["- No explicit audience architecture was recorded. Use the listed audiences as provisional context and do not silently average conflicting needs.", ""])
    scope = draft_record.get("prototype_scope")
    lines.extend(["## Demonstrated and not demonstrated", ""])
    if scope:
        lines.extend([
            f"Artifact: `{scope['artifact_type']}`  ",
            f"Maturity: `{scope['maturity']}`  ",
            f"Fixture data: `{scope['fixture_data']}`", "",
        ])
        for heading, key in (
            ("Demonstrated surfaces", "demonstrated_surfaces"),
            ("Demonstrated states", "demonstrated_states"),
            ("Omitted surfaces", "omitted_surfaces"),
            ("Omitted states", "omitted_states"),
        ):
            lines.extend([f"### {heading}", "", *([f"- {item}" for item in scope[key]] or ["- None recorded."]), ""])
    else:
        lines.extend(["- No prototype scope was recorded. The design document demonstrates direction, not workflow completeness or implementation readiness.", ""])
    matrix = draft_record.get("validation_matrix", [])
    lines.extend(["## Prototype validation matrix", ""])
    lines.extend(
        [f"- **{item['scenario']} — {item['status']}:** {item['evidence'] or 'Evidence still required.'}" for item in matrix]
        or ["- No validation evidence was recorded; implementation readiness is not claimed."]
    )
    lines.append("")
    insight_decisions = draft_record.get("insight_decisions", [])
    lines.extend(["## Insight-to-design decisions", ""])
    if insight_decisions:
        for item in insight_decisions:
            lines.extend([
                f"### {item['insight_id']}", "",
                f"**Insight:** {item['insight']}  ",
                f"**Status:** `{item['status']}`  ",
                f"**Design response:** {item['design_response']}  ",
                f"**Affected surfaces:** {'; '.join(item['affected_surfaces']) or 'None'}  ",
                f"**Affected states:** {'; '.join(item['affected_states']) or 'None'}  ",
                f"**Observable evidence:** {item['observable_evidence']}", "",
            ])
    else:
        lines.extend(["- No material insight-to-design decisions were recorded.", ""])
    lines.extend(["## Design thesis", ""])
    for direction in selected:
        lines.extend([f"### {direction['name']}", "", direction["summary"], "", "Creative signature:", "", direction["creative_signature"], "", "Principles:", ""])
        lines.extend(f"- {item}" for item in direction["principles"])
        expression = direction["distinctive_expression"]
        lines.extend([
            "", "## Distinctive expression", "",
            "### Aesthetic thesis", "", expression["aesthetic_thesis"], "",
            "### Subject world", "", *[f"- {item}" for item in expression["subject_world"]], "",
            "### Signature element", "", expression["signature_element"], "",
            "### Aesthetic risk", "",
            f"- **Move:** {expression['aesthetic_risk']['move']}",
            f"- **Why it fits:** {expression['aesthetic_risk']['rationale']}",
            f"- **Boundary:** {expression['aesthetic_risk']['boundary']}", "",
            "### Expression budget", "",
            f"- **Target weight:** `{expression['expression_budget']['target_weight']:.2f}`",
            f"- **Exploration ceiling:** `{expression['expression_budget']['exploration_ceiling']:.2f}`",
            f"- **Mode:** `{expression['expression_budget']['mode']}`",
            f"- **Source:** `{expression['expression_budget']['source']}`",
            f"- **Calibration rationale:** {expression['expression_budget']['weight_rationale']}",
            f"- **Boundary being pushed:** {expression['expression_budget']['boundary_being_pushed']}",
            f"- **Signature dimension:** `{expression['expression_budget']['primary_dimension']}`",
            f"- **Supporting dimensions:** {', '.join(expression['expression_budget']['supporting_dimensions'])}",
            f"- **Restrained dimensions:** {', '.join(expression['expression_budget']['restrained_dimensions'])}",
            f"- **Quiet field:** {expression['expression_budget']['quiet_field']}",
            f"- **Containment boundary:** {expression['expression_budget']['containment_boundary']}",
            "- **Intensity:** " + "; ".join(f"{dimension}={level}" for dimension, level in expression["expression_budget"]["intensity"].items()),
            "- **Removal order:** " + " → ".join(expression["expression_budget"]["removal_order"]), "",
            "### Design register", "",
            f"- **Mode:** `{expression['design_register']['mode']}`",
            f"- **Source:** `{expression['design_register']['source']}`",
            f"- **Rationale:** {expression['design_register']['rationale']}",
            f"- **Brand behavior:** {expression['design_register']['brand_behavior']}",
            f"- **Product behavior:** {expression['design_register']['product_behavior']}", "",
            "### Usage scene", "",
            f"- **People:** {expression['usage_scene']['people']}",
            f"- **Setting:** {expression['usage_scene']['setting']}",
            f"- **Ambient conditions:** {expression['usage_scene']['ambient_conditions']}",
            f"- **Frequency and consequence:** {expression['usage_scene']['frequency_and_consequence']}",
            f"- **Design effect:** {expression['usage_scene']['design_effect']}", "",
            "### Color commitment", "",
            f"- **Level:** `{expression['color_commitment']['level']}`",
            f"- **Source:** `{expression['color_commitment']['source']}`",
            f"- **Rationale:** {expression['color_commitment']['rationale']}",
            f"- **Role distribution:** {expression['color_commitment']['role_distribution']}",
            f"- **Contrast method:** {expression['color_commitment']['contrast_method']}", "",
            "### Anti-reflex review", "",
            f"- **Category default:** {expression['anti_reflex_review']['category_default']}",
            f"- **Counter-default risk:** {expression['anti_reflex_review']['anti_default_default']}",
            f"- **Revision:** {expression['anti_reflex_review']['revision']}", "",
            "### Anti-default decisions", "", *[f"- {item}" for item in expression["anti_defaults"]], "",
            "### Expression system", "",
        ])
        for dimension, rules in expression["expression_system"].items():
            lines.extend([f"#### {dimension.replace('_', ' ').title()}", "", *[f"- {item}" for item in rules], ""])
        implementation = expression["implementation_system"]
        lines.extend(["### Implementation system", "", f"- **Status:** `{implementation['status']}`", ""])
        for dimension in ("token_strategy", "type_constraints", "layout_constraints", "motion_constraints", "component_recipes", "hardening_checks"):
            lines.extend([f"#### {dimension.replace('_', ' ').title()}", "", *[f"- {item}" for item in implementation[dimension]], ""])
        brand = expression["brand_signature"]
        lines.extend([
            "### Brand signature system", "",
            f"**Identity premise:** {brand['identity_premise']}", "",
            "#### Primary carrier", "",
            f"- **Role:** {brand['primary_carrier']['role']}",
            f"- **Rule:** {brand['primary_carrier']['rule']}",
            f"- **Quiet variant:** {brand['primary_carrier']['quiet_variant']}", "",
            "#### Carrier modes", "",
            f"- **Utility expression:** {brand['utility_expression']}",
            f"- **Quiet mode:** {brand['quiet_mode']}",
            f"- **Campaign mode:** {brand['campaign_mode']}", "",
            "#### Recurring carriers", "",
            *[f"- **{item['carrier_id']}:** {item['role']} Rule: {item['rule']}" for item in brand["recurring_carriers"]], "",
            "#### Subject-derived tokens", "",
            *[f"- **{item['token_id']}:** {item['role']} Visual rule: {item['visual_rule']}" for item in brand["subject_tokens"]], "",
            "#### Expression transformation", "",
            *[f"- **{item['context']} (`{item['target_weight']:.2f}`):** {item['behavior']}" for item in brand["transformation_matrix"]], "",
            "#### Prohibited substitutions", "", *[f"- {item}" for item in brand["prohibited_substitutions"]], "",
            "#### Recognition tests", "", *[f"- {item}" for item in brand["recognition_tests"]], "",
        ])
        lines.extend(["### Multi-pass refinement", ""])
        for refinement in expression["refinement_passes"]:
            lines.extend([
                f"#### {refinement['pass_id'].replace('-', ' ').title()}", "",
                f"- **Status:** `{refinement['status']}`",
                f"- **Purpose:** {refinement['purpose']}",
                f"- **Changed:** {'; '.join(refinement['changes']) or 'Nothing recorded.'}",
                f"- **Preserved:** {'; '.join(refinement['preserved']) or 'Nothing recorded.'}",
                f"- **Unresolved:** {'; '.join(refinement['unresolved']) or 'None.'}", "",
            ])
        lines.extend(["### Contextual review outcomes", ""])
        if expression["contextual_reviews"]:
            for review in expression["contextual_reviews"]:
                lines.extend([
                    f"#### {review['perspective']}", "",
                    f"- **Routing:** `{review['routing']}`",
                    f"- **Why it applies:** {review['why_applicable']}",
                    f"- **Finding:** {review['finding']}",
                    f"- **Design response:** {review['design_response']}",
                    f"- **Preserved behavior:** {'; '.join(review['preserved_behavior'])}",
                    f"- **Verification:** {review['verification']}", "",
                ])
        else:
            lines.extend(["- No evidence-bearing contextual review has been completed; treat that refinement pass as pending.", ""])
        lines.extend([
            "### Reference compositions", "", *[f"- {item}" for item in expression["reference_compositions"]], "",
            "### Uniqueness checks", "", *[f"- {item}" for item in expression["uniqueness_checks"]], "",
            "### Creative provenance", "",
        ])
        provenance_by_id = {item["provenance_id"]: item for item in direction["creative_provenance"]}
        if expression["provenance_ids"]:
            for provenance_id in expression["provenance_ids"]:
                item = provenance_by_id[provenance_id]
                source_text = "; ".join(item["source_refs"]) or "No direct source; inference is explicitly labeled."
                lines.extend([
                    f"#### {provenance_id}", "",
                    f"- **Classification:** `{item['classification']}`",
                    f"- **Observation:** {item['observation']}",
                    f"- **Sources:** {source_text}",
                    f"- **Design implication:** {item['design_implication']}", "",
                ])
        else:
            lines.extend(["- No creative provenance was authored. Treat the expression as provisional until its subject basis is recorded.", ""])
        lines.extend(["", "## Experience principles", "", *[f"- {item}" for item in direction["experience_principles"]], ""])
        lines.extend(["## Experience architecture", "", *[f"- {item}" for item in direction["experience_architecture"]], ""])
        lines.extend(["## Visual and interaction system", "", "#### Design grammar", ""])
        for dimension in _required_grammar_dimensions(draft_record["targets"]):
            lines.extend([f"##### {dimension.replace('_', ' ').title()}", "", *[f"- {item}" for item in direction["design_grammar"][dimension]], ""])
        lines.extend(["## Component and pattern direction", "", *[f"- {item}" for item in direction["component_patterns"]], ""])
        implementation_context = draft_record.get("implementation_context")
        if implementation_context:
            lines.extend([
                "## React and implementation system", "",
                f"- **Framework:** {implementation_context['framework']} {implementation_context['framework_version'] or ''}".rstrip(),
                f"- **React:** {implementation_context['react_version'] or 'Not independently verified'}",
                f"- **Styling:** {', '.join(implementation_context['styling_systems']) or 'No configured styling system recorded'}",
                f"- **UI libraries:** {', '.join(implementation_context['ui_libraries']) or 'No installed UI library recorded'}",
                f"- **Motion:** {', '.join(implementation_context['motion_libraries']) or 'No installed motion library recorded'}",
                f"- **Data presentation:** {', '.join(implementation_context['data_libraries']) or 'No installed data library recorded'}",
                f"- **Icons:** {', '.join(implementation_context['icon_libraries']) or 'No installed icon library recorded'}",
                f"- **Component roots:** {', '.join(implementation_context['component_roots']) or 'None recorded'}",
                f"- **Token sources:** {', '.join(implementation_context['token_sources']) or 'None recorded'}",
                f"- **Evidence:** {', '.join(implementation_context['evidence_refs'])}", "",
            ])
        if draft_record.get("component_map"):
            lines.extend(["### Component capability map", "", "| Need | Surface | Strategy | Capability | Required states | Custom expression |", "|---|---|---|---|---|---|"])
            for item in draft_record["component_map"]:
                capability = item["existing_capability"] or ", ".join(item["components"]) or "No existing capability"
                lines.append(f"| {item['experience_need']} | {item['surface']} | `{item['strategy']}` | {capability} | {', '.join(item['required_states'])} | {item['custom_expression']} |")
            lines.append("")
        if draft_record.get("asset_strategy"):
            lines.extend(["## Asset strategy", ""])
            for item in draft_record["asset_strategy"]:
                lines.extend([
                    f"### {item['asset_id']}", "",
                    f"- **Purpose:** {item['purpose']}",
                    f"- **Source:** `{item['source']}`",
                    f"- **Art direction:** {item['art_direction']}",
                    f"- **Provenance:** {item['provenance_status']}",
                    f"- **Crops:** {', '.join(item['required_crops']) or 'No crop variants required'}",
                    f"- **Responsive treatment:** {item['responsive_treatment']}",
                    f"- **Alternative:** {item['accessibility_alternative']}",
                    f"- **Fallback:** {item['fallback']}",
                    f"- **Claim boundary:** {item['claim_boundary']}", "",
                ])
        if draft_record.get("completion_contract"):
            contract = draft_record["completion_contract"]
            lines.extend([
                "## Prototype completion contract", "",
                f"- **Mode:** `{contract['mode']}`",
                f"- **Required viewports:** {', '.join(contract['required_viewports']) or 'None'}",
                f"- **Required states:** {', '.join(contract['required_states']) or 'None'}",
                f"- **Content status:** `{contract['content_status']}`",
                f"- **Artifact critique required:** {'yes' if contract['artifact_critique_required'] else 'no'}", "",
            ])
        lines.extend(["## Content rules", "", *[f"- {item}" for item in direction["content_rules"]], ""])
        lines.extend(["## Audience strategy", "", *[f"- {item}" for item in direction["audience_strategy"]], ""])
        lines.extend(["## Prototype boundaries", "", *[f"- {item}" for item in direction["prototype_boundaries"]], ""])
        lines.extend(["## Implementation contract", "", *[f"- {item}" for item in direction["implementation_guidance"]], ""])
        lines.extend(["### Acceptance and drift checks", "", *[f"- {item}" for item in direction["validation_criteria"]], ""])
        lines.extend(["### Prohibited patterns", "", *[f"- {item}" for item in direction["prohibited_patterns"]], ""])
        lines.extend(["### Bounded variation", "", *[f"- {item}" for item in direction["variation_levers"]], ""])
        lines.extend(["### Tradeoffs", "", *[f"- {item}" for item in direction["tradeoffs"]], ""])
    for heading, key in (
        ("Working assumptions", "working_assumptions"),
        ("Constraints", "constraints"),
        ("Behavior to preserve", "preserve"),
        ("Non-goals", "non_goals"),
        ("Open questions", "open_questions"),
    ):
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
    selected = [item for item in record["directions"] if item["direction_id"] in record["selected_direction_ids"]]
    alignment_contract = {
        "selected_direction_ids": record["selected_direction_ids"],
        "creative_signatures": [direction["creative_signature"] for direction in selected],
        "distinctive_expression": [direction["distinctive_expression"] for direction in selected],
        "creative_provenance": [item for direction in selected for item in direction["creative_provenance"]],
        "content_provenance": record.get("content_provenance", []),
        "audience_architecture": record.get("audience_architecture"),
        "prototype_scope": record.get("prototype_scope"),
        "implementation_context": record.get("implementation_context"),
        "component_map": record.get("component_map", []),
        "asset_strategy": record.get("asset_strategy", []),
        "completion_contract": record.get("completion_contract"),
        "validation_matrix": record.get("validation_matrix", []),
        "insight_decisions": record.get("insight_decisions", []),
        "content_rules": [rule for direction in selected for rule in direction["content_rules"]],
        "audience_strategy": [rule for direction in selected for rule in direction["audience_strategy"]],
        "prototype_boundaries": [rule for direction in selected for rule in direction["prototype_boundaries"]],
        "preserve": record["preserve"],
        "non_goals": record["non_goals"],
        "implementation_guidance": [rule for direction in selected for rule in direction["implementation_guidance"]],
        "validation_criteria": [rule for direction in selected for rule in direction["validation_criteria"]],
        "prohibited_patterns": [rule for direction in selected for rule in direction["prohibited_patterns"]],
    }
    shared.update({"status": "approved", "document_path": "docs/design/design.md", "catalog_packs": record["catalog_packs"], "alignment_contract": alignment_contract})
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
    return [{"design_id": record["design_id"], "revision": record["revision"], "design_hash": record["design_hash"], "catalog_packs": record["catalog_packs"], "alignment_contract": record.get("alignment_contract", {})}]


def _artifact_relative_path(root: Path, value: Any) -> tuple[str, Path]:
    if not isinstance(value, str) or not value.strip():
        raise DesignError("Artifact file requires a project-relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise DesignError("Artifact paths must be project-relative and cannot traverse parents")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise DesignError("Artifact path escapes the project root") from exc
    return candidate.as_posix(), resolved


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise DesignError(f"Invalid PNG artifact: {path}")
    return struct.unpack(">II", data[16:24])


def _validate_artifact_against_record(root: Path, manifest: dict[str, Any], approved: dict[str, Any], *, candidate: bool) -> dict[str, Any]:
    for key in ("design_id", "revision", "design_hash"):
        if manifest.get(key) != approved.get(key):
            raise DesignError(f"Artifact manifest {key} does not match the approved design")
    artifact_id = _identifier(str(manifest.get("artifact_id", "")), "artifact ID")
    maturity = manifest.get("maturity")
    if maturity not in ARTIFACT_MATURITY:
        raise DesignError("Artifact manifest requires a valid maturity")
    fixture_data = manifest.get("fixture_data")
    if fixture_data not in {"none", "present-labeled", "present-unlabeled"}:
        raise DesignError("Artifact manifest requires a valid fixture_data status")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise DesignError("Artifact manifest requires files")
    file_paths: set[str] = set()
    html_texts: dict[str, str] = {}
    screenshot_roles: set[str] = set()
    verified_files: list[dict[str, Any]] = []
    for item in files:
        if not isinstance(item, dict) or item.get("media_type") not in ARTIFACT_MEDIA_TYPES:
            raise DesignError("Artifact files require supported media types")
        relative, path = _artifact_relative_path(root, item.get("path"))
        if relative in file_paths or not path.is_file():
            raise DesignError(f"Artifact file is missing or duplicated: {relative}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get("sha256") != actual_hash:
            raise DesignError(f"Artifact file hash mismatch: {relative}")
        role = item.get("role")
        if not isinstance(role, str) or not role.strip():
            raise DesignError(f"Artifact file requires role: {relative}")
        verified: dict[str, Any] = {"path": relative, "media_type": item["media_type"], "role": role, "sha256": actual_hash}
        if item["media_type"] == "text/html":
            text = path.read_text(encoding="utf-8")
            for name, content in {
                "continuity-design-id": manifest["design_id"],
                "continuity-design-revision": str(manifest["revision"]),
                "continuity-design-hash": manifest["design_hash"],
                "continuity-prototype-maturity": maturity,
                "continuity-fixture-data": fixture_data,
            }.items():
                pattern = rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']{re.escape(content)}["\']\s*/?>'
                if not re.search(pattern, text, re.IGNORECASE):
                    raise DesignError(f"HTML artifact is missing bound metadata {name}: {relative}")
            html_texts[relative] = text
        elif item["media_type"] == "image/png":
            width, height = _png_dimensions(path)
            verified.update({"width": width, "height": height})
            screenshot_roles.add(role)
        verified_files.append(verified)
        file_paths.add(relative)
    validations = manifest.get("validation_results", [])
    if not isinstance(validations, list):
        raise DesignError("Artifact validation_results must be an array")
    validation_by_scenario: dict[str, dict[str, Any]] = {}
    for item in validations:
        if not isinstance(item, dict) or not isinstance(item.get("scenario"), str) or item.get("status") not in {"passed", "not-applicable", "failed"}:
            raise DesignError("Artifact validation result is invalid")
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip() or item["scenario"] in validation_by_scenario:
            raise DesignError("Artifact validation results require unique scenarios and evidence")
        validation_by_scenario[item["scenario"]] = item
    craft_findings = manifest.get("craft_findings", [])
    if not isinstance(craft_findings, list):
        raise DesignError("Artifact craft_findings must be an array")
    normalized_findings: list[dict[str, Any]] = []
    for item in craft_findings:
        if not isinstance(item, dict):
            raise DesignError("Artifact craft finding is invalid")
        rule_id = _identifier(str(item.get("rule_id", "")), "craft finding rule ID")
        if item.get("severity") not in {"info", "warning", "error", "critical"} or item.get("status") not in {"open", "resolved", "accepted-intentional", "not-applicable"}:
            raise DesignError(f"Artifact craft finding {rule_id} has invalid severity or status")
        normalized = {"rule_id": rule_id, "severity": item["severity"], "status": item["status"]}
        for key in ("artifact_ref", "location", "evidence"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"Artifact craft finding {rule_id} requires {key}")
            normalized[key] = text.strip()
        for key in ("response", "override_rationale"):
            text = item.get(key, "")
            if not isinstance(text, str):
                raise DesignError(f"Artifact craft finding {rule_id} has invalid {key}")
            normalized[key] = text.strip()
        if normalized["status"] == "resolved" and not normalized["response"]:
            raise DesignError(f"Resolved craft finding {rule_id} requires a response")
        if normalized["status"] == "accepted-intentional" and not normalized["override_rationale"]:
            raise DesignError(f"Intentional craft finding {rule_id} requires an override rationale")
        normalized_findings.append(normalized)
    claims = manifest.get("design_claims", [])
    if not isinstance(claims, list):
        raise DesignError("Artifact design_claims must be an array")
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("coverage") not in {"demonstrated", "omitted"}:
            raise DesignError("Artifact design claim is invalid")
        if not all(isinstance(claim.get(key), str) and claim[key].strip() for key in ("design_section", "claim")):
            raise DesignError("Artifact design claims require section and claim")
        evidence_refs = claim.get("evidence_refs", [])
        insight_ids = claim.get("insight_ids", [])
        if not isinstance(insight_ids, list) or any(not isinstance(item, str) or not item.strip() for item in insight_ids):
            raise DesignError("Artifact design claim insight_ids must be an array of IDs")
        if claim["coverage"] == "demonstrated" and (not isinstance(evidence_refs, list) or not evidence_refs):
            raise DesignError("Demonstrated design claims require artifact evidence")
        for reference in evidence_refs:
            if not isinstance(reference, str) or reference.split("#", 1)[0] not in file_paths:
                raise DesignError("Design claim evidence must reference a bound artifact file")
            if "#" in reference:
                file_ref, anchor = reference.split("#", 1)
                if file_ref not in html_texts or not re.search(rf'id=["\']{re.escape(anchor)}["\']', html_texts[file_ref], re.IGNORECASE):
                    raise DesignError("Design claim evidence anchor is missing")
    decided_insights = {
        item["insight_id"]
        for item in approved.get("alignment_contract", {}).get("insight_decisions", [])
        if item.get("status") == "decided"
    }
    demonstrated_insights = {
        insight_id
        for claim in claims
        if claim.get("coverage") == "demonstrated"
        for insight_id in claim.get("insight_ids", [])
    }
    if demonstrated_insights - decided_insights:
        raise DesignError("Artifact claims reference unknown decided insight IDs")
    missing_decided_insights = sorted(decided_insights - demonstrated_insights)
    demonstrated_audiences = manifest.get("demonstrated_audiences", [])
    if not isinstance(demonstrated_audiences, list) or any(not isinstance(item, str) or not item.strip() for item in demonstrated_audiences):
        raise DesignError("Artifact demonstrated_audiences is invalid")
    architecture = approved.get("alignment_contract", {}).get("audience_architecture")
    missing_audiences: list[str] = []
    if isinstance(architecture, dict) and architecture.get("mode") == "differentiated":
        expected = {route["audience"] for route in architecture.get("routes", [])}
        missing_audiences = sorted(expected - set(demonstrated_audiences))
    failures = sorted(item["scenario"] for item in validations if item["status"] == "failed")
    readiness_problems: list[str] = []
    if maturity == "implementation-facing":
        if fixture_data == "present-unlabeled":
            readiness_problems.append("fixture content is not locally labeled")
        if missing_audiences:
            readiness_problems.append("differentiated audience routes are not all demonstrated")
        if failures:
            readiness_problems.append("artifact validation has failures")
        blocking_findings = [item for item in normalized_findings if item["status"] == "open" and item["severity"] in {"error", "critical"}]
        if blocking_findings:
            readiness_problems.append("artifact craft review has unresolved error or critical findings")
        if not claims or any(claim["coverage"] != "demonstrated" for claim in claims):
            readiness_problems.append("design claims are missing demonstrated evidence")
        if missing_decided_insights:
            readiness_problems.append("decided insights lack demonstrated artifact evidence")
        required = {item["scenario"] for item in approved.get("alignment_contract", {}).get("validation_matrix", []) if item.get("status") == "required"}
        if required - set(validation_by_scenario):
            readiness_problems.append("approved validation requirements lack artifact results")
        if html_texts and not {"desktop", "mobile"} <= screenshot_roles:
            readiness_problems.append("responsive HTML requires desktop and mobile screenshots")
        if html_texts and {"horizontal-overflow", "sticky-action-obstruction"} - set(validation_by_scenario):
            readiness_problems.append("responsive HTML requires overflow and sticky-obstruction probe results")
        if readiness_problems:
            raise DesignError("Artifact is not implementation-facing: " + "; ".join(readiness_problems))
    if manifest.get("schema_version", 1) == 2:
        contract = approved.get("alignment_contract", {})
        for field, value in (
            ("implementation_context_hash", contract.get("implementation_context")),
            ("component_map_hash", contract.get("component_map", [])),
            ("asset_strategy_hash", contract.get("asset_strategy", [])),
        ):
            expected = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if manifest.get(field) != expected:
                raise DesignError(f"Artifact manifest {field} does not match the design contract")
        completion = contract.get("completion_contract")
        if maturity == "implementation-facing" and isinstance(completion, dict) and completion.get("artifact_critique_required"):
            if not isinstance(manifest.get("artifact_critique_revision"), int) or manifest["artifact_critique_revision"] < 1:
                raise DesignError("Implementation-facing complete prototypes require an artifact critique revision")
            required_roles = set(completion.get("required_viewports", []))
            if required_roles - screenshot_roles:
                raise DesignError("Artifact is missing completion-contract viewport captures")
            if set(completion.get("required_states", [])) - set(manifest.get("demonstrated_states", [])):
                raise DesignError("Artifact is missing completion-contract states")
    return {
        "schema_version": manifest.get("schema_version", 1),
        "artifact_id": artifact_id,
        "design_id": manifest["design_id"],
        "revision": manifest["revision"],
        "design_hash": manifest["design_hash"],
        "maturity": maturity,
        "verified_files": verified_files,
        "missing_differentiated_audiences": missing_audiences,
        "failed_validations": failures,
        "craft_findings": normalized_findings,
        "missing_decided_insights": missing_decided_insights,
        "implementation_ready": maturity == "implementation-facing" and not readiness_problems,
        "candidate": candidate,
        "execution_authorized": False,
    }


def validate_artifact(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    _enabled(config)
    manifest = _read_json(manifest_path)
    approved = _read_json(root / ".continuity" / "design.json")
    return _validate_artifact_against_record(root, manifest, approved, candidate=False)


def validate_candidate_artifact(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    _enabled(config)
    manifest = _read_json(manifest_path)
    design_id = _identifier(str(manifest.get("design_id", "")), "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    draft = _read_json(design_dir / "draft.json")
    if draft.get("status") != "awaiting-approval" or not draft.get("selected_direction_ids") or not draft.get("design_hash"):
        raise DesignError("Candidate artifact requires a selected private design awaiting approval")
    selected = [item for item in draft["directions"] if item["direction_id"] in draft["selected_direction_ids"]]
    alignment_contract = {
        "audience_architecture": draft.get("audience_architecture"),
        "validation_matrix": draft.get("validation_matrix", []),
        "insight_decisions": draft.get("insight_decisions", []),
        "implementation_context": draft.get("implementation_context"),
        "component_map": draft.get("component_map", []),
        "asset_strategy": draft.get("asset_strategy", []),
        "completion_contract": draft.get("completion_contract"),
        "selected_direction_ids": draft["selected_direction_ids"],
        "implementation_guidance": [rule for direction in selected for rule in direction["implementation_guidance"]],
    }
    candidate_record = {
        "design_id": draft["design_id"], "revision": draft["revision"], "design_hash": draft["design_hash"],
        "alignment_contract": alignment_contract,
    }
    return _validate_artifact_against_record(root, manifest, candidate_record, candidate=True)
