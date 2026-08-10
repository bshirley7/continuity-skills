"""Offline design-direction lifecycle for Continuity."""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import shutil
import struct
import zlib
from pathlib import Path
from typing import Any

import design_slop

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
UNCERTAINTY_DISPOSITIONS = {"open", "assumed", "resolved", "deferred"}
MODALITY_CONFLICT_STATUSES = {"resolved", "not-applicable", "unresolved"}
CONSEQUENCE_LEVELS = {"routine", "moderate", "high"}
INSIGHT_DECISION_STATUSES = {"decided", "provisional", "omitted"}
ARTIFACT_MATURITY = {"directional", "behavioral", "implementation-facing"}
COMPONENT_STRATEGIES = {"reuse", "compose", "extend", "custom", "missing-capability"}
WEB_ARTIFACT_QUALITY_SCENARIOS = {
    "horizontal-overflow", "sticky-action-obstruction", "color-contrast",
    "accessible-names", "semantic-controls", "reduced-motion", "intermediate-viewport",
}
COLLABORATION_PROFILES = {"guided", "collaborative", "creative-peer"}
COLLABORATION_CONTRACTS = {
    "guided": {
        "recommendation_posture": "decisive",
        "explanation_depth": "plain-language",
        "feedback_scope": "three-to-five-numbered-elements",
        "challenge_posture": "translate-design-language",
    },
    "collaborative": {
        "recommendation_posture": "co-creative",
        "explanation_depth": "tradeoff-visible",
        "feedback_scope": "system-and-element-reactions",
        "challenge_posture": "surface-and-test-assumptions",
    },
    "creative-peer": {
        "recommendation_posture": "point-of-view-with-boundary-studies",
        "explanation_depth": "professional-shorthand",
        "feedback_scope": "direction-system-and-craft",
        "challenge_posture": "direct-creative-challenge",
    },
}
DESIGN_SPECIALIZATIONS = {
    "brand-marketing", "product-system", "document-editorial",
    "image-art-direction", "cinematic-experience", "mixed",
}
RESEARCH_MODES = {"adaptive-live", "offline", "user-supplied-only", "declined"}
RESEARCH_STATUSES = {"not-started", "in-progress", "complete", "unavailable", "declined"}
RESEARCH_AXES = {"subject-material", "treatment-light", "graphic-spatial"}
CONCEPT_PRESENTATION_MODES = {"equal-directions", "director-led"}
CONCEPT_ROLES = {"direction", "contrast-study"}
RESEARCH_LINK_DISPOSITIONS = {"adopted", "transformed", "rejected", "reference-only"}
FEEDBACK_REACTIONS = {"keep", "change", "avoid", "uncertain"}
VISUAL_REFERENCE_OWNERSHIP = {"project-owned", "supplied-with-rights", "generated", "third-party"}
GENERATIVE_EXPLORATION_STATUSES = {"complete", "unavailable", "declined", "deliberately-omitted"}
GENERATIVE_EXPLORATION_MODES = {"mixed-media", "generated-media", "code-only", "omitted"}
GENERATIVE_MEDIA = {"image-generation", "image-editing", "svg", "typography", "collage", "motion-frame", "code-sketch"}
GENERATED_IMAGE_MEDIA = {"image-generation", "image-editing"}
ART_DIRECTION_FAMILIES = {
    "photographic", "documentary", "illustrative", "typographic", "material",
    "spatial", "diagrammatic", "cinematic", "interaction-led", "mixed",
}
TYPOGRAPHY_FAMILIES = {
    "serif", "humanist-sans", "grotesk-sans", "neo-grotesk-sans", "condensed-display",
    "monospaced", "vernacular-display", "system-utility", "custom-letterform", "mixed",
}
TYPOGRAPHY_SOURCES = {"system", "project-supplied", "open-licensed", "licensed", "custom-lettering", "code-native"}
COMPOSITION_FAMILIES = {
    "editorial-sequence", "spatial-field", "cinematic-chapters", "typographic-poster",
    "documentary-index", "interactive-instrument", "material-collage", "narrative-scroll", "modular-system",
}
PAGE_GRAMMAR_FAMILIES = {
    "longform-narrative", "single-canvas-instrument", "navigable-artifact", "editorial-issue",
    "cinematic-sequence", "modular-system", "spatial-journey",
}
PAGE_GRAMMAR_REQUIRED_BEHAVIORS = {
    "longform-narrative": {"narrative-progression", "section-rhythm", "returning-carrier"},
    "single-canvas-instrument": {"persistent-canvas", "state-recomposition", "control-continuity"},
    "navigable-artifact": {"artifact-index", "nonlinear-entry", "custody-relationship"},
    "editorial-issue": {"issue-spread-variation", "cross-spread-carrier", "article-sequencing"},
    "cinematic-sequence": {"chapter-transition", "shot-continuity", "static-chapter-fallback"},
    "modular-system": {"module-variation", "system-relationship", "nonuniform-emphasis"},
    "spatial-journey": {"spatial-topology", "path-progression", "node-to-evidence"},
}
INTERACTION_MOTION_MODES = {"static", "native-disclosure", "direct-manipulation", "spatial-transition", "cinematic", "mixed"}
GENERATED_EXTRACTION_DOMAINS = {"typography", "composition", "material", "motion", "code-native", "imagery"}
STYLE_FRAME_METHODS = {"generated", "edited", "code-native", "project-owned"}
IMPACT_STRENGTHS = {"credible", "compelling"}
IMPACT_REVIEWER_TYPES = {"agent-multimodal", "human"}
JOURNEY_STRUCTURE_MODES = {"structural-variety", "persistent-state-variation"}
IMPROVEMENT_PASS_STATUSES = {"planned", "implemented", "validated", "awaiting-human", "accepted", "changes-requested"}
JOURNEY_STAGE_ROLES = {
    "opening", "orientation", "proof", "system-model", "interaction", "quiet-state",
    "edge-state", "trust", "decision", "closure",
}
MEDIA_ASSET_SOURCES = {"generated", "derived", "project-owned", "supplied", "code-native", "deliberately-omitted"}
PRIMARY_CONCEPT_CARRIERS = {"imagery", "interaction", "typography", "material", "spatial-system", "motion", "narrative"}
CREATIVE_DISTANCE_DIMENSIONS = {
    "organizing-idea", "primary-carrier", "emotional-register", "material-system",
    "typography-behavior", "imagery-behavior", "motion-model", "voice", "responsive-transformation",
}
REFERENCE_CONSTRAINT_DIMENSIONS = {
    "composition", "scale", "negative-space", "typography", "media", "material",
    "color", "motion", "interaction", "content-structure", "responsive-transformation",
}
REFERENCE_REQUIRED_DIMENSIONS = {
    "composition", "scale", "negative-space", "typography", "media", "responsive-transformation",
}
REFERENCE_MEDIA_STRATEGIES = {"generated", "project-owned", "supplied-with-rights", "code-native", "mixed"}
REFERENCE_FIDELITY_CHECKS = (
    "reference_mechanics_preserved", "project_identity_distinct", "material_fidelity",
    "template_distance", "declared_visible",
)
REFERENCE_REVIEW_QUESTIONS = (
    "salience_order", "spatial_tension", "typography_role", "media_dominance",
    "mechanic_lineage", "project_distinction", "responsive_fidelity", "variable_contrast",
)
REFERENCE_CLASSES = {"photographic", "diagrammatic", "editorial", "motion-led", "product-object", "mixed"}
REFERENCE_CLASS_THRESHOLDS = {
    "photographic": {"crop-fidelity", "media-transition", "responsive-crop"},
    "diagrammatic": {"information-density", "relationship-topology", "label-hierarchy"},
    "editorial": {"reading-order", "typographic-rhythm", "material-texture"},
    "motion-led": {"timing-model", "state-transition", "static-fallback"},
    "product-object": {"object-salience", "material-detail", "responsive-object-behavior"},
    "mixed": {"dominant-medium", "cross-medium-hierarchy", "responsive-medium-priority"},
}
ADAPTATION_DISTANCE_DIMENSIONS = {
    "composition", "color", "typography", "media-role", "responsive-behavior", "interaction",
}
ADAPTATION_DISTANCE_ROLES = {"close-study", "far-study", "experimental-study"}
PORTFOLIO_FINGERPRINT_DIMENSIONS = {
    "palette-family", "typography-family", "composition-family", "label-style",
    "status-mark-style", "signature-language", "material-system", "section-rhythm",
}
ASSET_RESOLUTION_STATUSES = {"resolved", "deliberately-omitted", "blocked"}
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


def _infer_collaboration_profile(payload: dict[str, Any]) -> str:
    supplied = payload.get("collaboration_profile")
    if supplied is not None:
        if supplied not in COLLABORATION_PROFILES:
            raise DesignError("collaboration_profile must be guided, collaborative, or creative-peer")
        return supplied
    context = " ".join(
        str(value)
        for key in ("intent", "audiences", "workflow_signals", "evidence_inspected")
        for value in ([payload.get(key)] if isinstance(payload.get(key), str) else payload.get(key, []))
    ).lower()
    if any(term in context for term in ("creative director", "design director", "art director", "creative lead", "design lead")):
        return "creative-peer"
    if any(term in context for term in ("co-create", "collaborate", "workshop", "design team")):
        return "collaborative"
    return "guided"


def _collaboration_contract(profile: str) -> dict[str, str]:
    return dict(COLLABORATION_CONTRACTS[profile])


def _infer_specialization(payload: dict[str, Any]) -> str:
    supplied = payload.get("specialization")
    if supplied is not None:
        if supplied not in DESIGN_SPECIALIZATIONS:
            raise DesignError("specialization is not supported")
        return supplied
    targets = set(payload.get("targets", []))
    context = " ".join([payload.get("intent", ""), *payload.get("sections", []), *payload.get("themes", [])]).lower()
    if len(targets) > 1:
        return "mixed"
    if targets == {"document"}:
        return "document-editorial"
    if targets == {"image"}:
        return "image-art-direction"
    if any(term in context for term in ("film", "cinematic", "immersive", "motion experience")):
        return "cinematic-experience"
    if any(term in context for term in ("brand", "campaign", "marketing", "launch", "story")):
        return "brand-marketing"
    return "product-system"


def _validate_reference_decomposition(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DesignError("reference_decomposition must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    dimensions = ("composition", "typography", "density", "imagery", "motion", "voice")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise DesignError(f"reference_decomposition[{index}] must be an object")
        reference_id = _identifier(str(item.get("reference_id", "")), "reference ID")
        if reference_id in seen:
            raise DesignError("Reference decomposition IDs must be unique")
        source = item.get("source")
        appeal = item.get("inferred_appeal")
        transformation = item.get("project_transformation")
        if not all(isinstance(text, str) and text.strip() for text in (source, appeal, transformation)):
            raise DesignError("Reference decomposition requires source, inferred_appeal, and project_transformation")
        breakdown = item.get("dimensions")
        if not isinstance(breakdown, dict) or any(not isinstance(breakdown.get(key), str) or not breakdown[key].strip() for key in dimensions):
            raise DesignError("Reference decomposition requires composition, typography, density, imagery, motion, and voice")
        normalized.append({
            "reference_id": reference_id,
            "source": source.strip(),
            "inferred_appeal": appeal.strip(),
            "project_transformation": transformation.strip(),
            "dimensions": {key: breakdown[key].strip() for key in dimensions},
            "provisional": True,
        })
        seen.add(reference_id)
    return normalized


def _validate_research_record(value: Any, root: Path, *, precision: bool = False) -> dict[str, Any]:
    if value is None:
        return {"mode": "offline", "status": "not-started", "announced": False, "opt_out_offered": False, "moodboard": []}
    if not isinstance(value, dict) or value.get("mode") not in RESEARCH_MODES or value.get("status") not in RESEARCH_STATUSES:
        raise DesignError("research requires a supported mode and status")
    announced = value.get("announced", False)
    opt_out = value.get("opt_out_offered", False)
    if not isinstance(announced, bool) or not isinstance(opt_out, bool):
        raise DesignError("research announcement flags must be booleans")
    if value["mode"] == "adaptive-live" and (not announced or not opt_out):
        raise DesignError("Adaptive live research must be announced and offer an opt-out")
    completed_at = value.get("completed_at")
    if completed_at is not None and (not isinstance(completed_at, str) or not completed_at.strip()):
        raise DesignError("research completed_at must be non-empty text when supplied")
    tiles = value.get("moodboard", [])
    if not isinstance(tiles, list):
        raise DesignError("research moodboard must be an array")
    if value["status"] == "complete" and value["mode"] == "adaptive-live" and not 12 <= len(tiles) <= 20:
        raise DesignError("Completed live-research moodboards require 12 to 20 tiles")
    normalized_tiles: list[dict[str, Any]] = []
    seen: set[int] = set()
    seen_sources: set[str] = set()
    seen_visuals: set[str] = set()
    axes: set[str] = set()
    for index, tile in enumerate(tiles):
        if not isinstance(tile, dict) or not isinstance(tile.get("tile"), int) or tile["tile"] < 1:
            raise DesignError(f"Moodboard tile {index + 1} requires a positive number")
        if tile["tile"] in seen:
            raise DesignError("Moodboard tile numbers must be unique")
        for key in ("source", "captured_at", "intended_lesson", "axis", "project_mechanic"):
            if not isinstance(tile.get(key), str) or not tile[key].strip():
                raise DesignError(f"Moodboard tile {tile['tile']} requires {key}")
        if tile["axis"] not in RESEARCH_AXES:
            raise DesignError(f"Moodboard tile {tile['tile']} requires a supported research axis")
        ownership = tile.get("ownership", "third-party")
        if ownership not in VISUAL_REFERENCE_OWNERSHIP:
            raise DesignError("Moodboard tile ownership is invalid")
        copy_candidates = tile.get("copy_candidates", [])
        shipping_boundary = tile.get("shipping_boundary", "")
        if precision:
            if not isinstance(copy_candidates, list) or not copy_candidates:
                raise DesignError(f"Moodboard tile {tile['tile']} must identify specific details to copy privately and adapt")
            if not isinstance(shipping_boundary, str) or not shipping_boundary.strip():
                raise DesignError(f"Moodboard tile {tile['tile']} requires a shipping boundary")
            if tile.get("shipping_copy_prohibited") is not True:
                raise DesignError(f"Moodboard tile {tile['tile']} must keep source identity and pixels out of shipping work")
        elif tile.get("prohibited_copying") is not True:
            raise DesignError("Legacy moodboard tiles must explicitly prohibit copying")
        normalized_candidates: list[dict[str, str]] = []
        candidate_ids: set[str] = set()
        for candidate in copy_candidates:
            if not isinstance(candidate, dict):
                raise DesignError(f"Moodboard tile {tile['tile']} copy candidates must be objects")
            detail_id = _identifier(str(candidate.get("detail_id", "")), "moodboard copy detail ID")
            fields = ("detail", "source_location", "private_copy_action", "project_adaptation", "shipping_transformation")
            if detail_id in candidate_ids or any(not isinstance(candidate.get(field), str) or not candidate[field].strip() for field in fields):
                raise DesignError(f"Moodboard tile {tile['tile']} copy candidates require unique IDs and a complete adaptation path")
            normalized_candidates.append({"detail_id": detail_id, **{field: candidate[field].strip() for field in fields}})
            candidate_ids.add(detail_id)
        if ownership == "third-party" and tile.get("publishable", False):
            raise DesignError("Third-party moodboard tiles cannot be publishable")
        local_path = str(tile.get("local_path", "")).strip()
        visual_hash = str(tile.get("sha256", "")).strip()
        if value["status"] == "complete":
            relative, path = _artifact_relative_path(root, local_path)
            if not path.is_file() or path.suffix.lower() not in {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}:
                raise DesignError(f"Moodboard tile {tile['tile']} requires a local captured image")
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if visual_hash != actual_hash:
                raise DesignError(f"Moodboard tile {tile['tile']} image changed or is not hash-bound")
            local_path = relative
            if actual_hash in seen_visuals:
                raise DesignError("Completed moodboards cannot repeat the same captured visual")
            seen_visuals.add(actual_hash)
        normalized_tiles.append({
            "tile": tile["tile"], "source": tile["source"].strip(), "captured_at": tile["captured_at"].strip(),
            "intended_lesson": tile["intended_lesson"].strip(), "axis": tile["axis"].strip(),
            "project_mechanic": tile["project_mechanic"].strip(),
            "copy_candidates": normalized_candidates, "shipping_boundary": shipping_boundary.strip(),
            "ownership": ownership, "prohibited_copying": bool(tile.get("prohibited_copying", not precision)),
            "shipping_copy_prohibited": bool(tile.get("shipping_copy_prohibited", precision)), "publishable": bool(tile.get("publishable", False)),
            "local_path": local_path, "sha256": visual_hash,
        })
        seen.add(tile["tile"])
        seen_sources.add(tile["source"].strip())
        axes.add(tile["axis"])
    if value["status"] == "complete" and tiles:
        if len(axes) < 2:
            raise DesignError("Completed moodboards require at least two research axes")
        if len(seen_sources) < min(3, len(tiles)):
            raise DesignError("Completed moodboards require source diversity")
    return {
        "mode": value["mode"], "status": value["status"], "announced": announced,
        "opt_out_offered": opt_out, "completed_at": completed_at, "moodboard": normalized_tiles,
    }


def _validate_generative_exploration(value: Any, root: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError("Creative-director workflow requires an explicit generative_exploration record")
    status = value.get("status")
    mode = value.get("mode")
    required = value.get("required_for_directioning")
    if status not in GENERATIVE_EXPLORATION_STATUSES or mode not in GENERATIVE_EXPLORATION_MODES:
        raise DesignError("generative_exploration requires a supported status and mode")
    if not isinstance(required, bool):
        raise DesignError("generative_exploration required_for_directioning must be boolean")
    omission = value.get("omission_rationale", "")
    if not isinstance(omission, str):
        raise DesignError("generative_exploration omission_rationale must be text")
    lenses = value.get("lenses", [])
    seeds = value.get("seeds", [])
    combinations = value.get("cross_pollinations", [])
    shortlist = value.get("shortlisted_seed_ids", [])
    style_frames = value.get("style_frame_explorations", [])
    range_plan = value.get("range_plan", {})
    if not all(isinstance(items, list) for items in (lenses, seeds, combinations, shortlist, style_frames)):
        raise DesignError("generative_exploration collections must be arrays")
    if status != "complete":
        if mode != "omitted" or required or lenses or seeds or combinations or shortlist or style_frames or range_plan or not omission.strip():
            raise DesignError("Unavailable, declined, or omitted concept laboratories require mode omitted, no generated work, and a rationale")
        return {
            "status": status, "mode": mode, "required_for_directioning": False,
            "lenses": [], "seeds": [], "cross_pollinations": [],
            "shortlisted_seed_ids": [], "style_frame_explorations": [], "range_plan": {}, "omission_rationale": omission.strip(),
            "laboratory_hash": _canonical_hash({"status": status, "mode": mode, "omission_rationale": omission.strip()}),
        }
    if mode == "omitted" or required is not True or omission.strip():
        raise DesignError("A completed concept laboratory must be required for directioning and cannot use omitted mode or rationale")
    if not 4 <= len(lenses) <= 8:
        raise DesignError("Completed concept laboratories require four to eight project-derived lenses")
    if not isinstance(range_plan, dict):
        raise DesignError("Completed concept laboratories require a range_plan object")
    art_families = range_plan.get("art_direction_families")
    typography_hypotheses = range_plan.get("typography_hypotheses")
    composition_families = range_plan.get("composition_families")
    page_depth_roles = range_plan.get("page_depth_roles")
    page_grammar_hypotheses = range_plan.get("page_grammar_hypotheses")
    interaction_motion_hypotheses = range_plan.get("interaction_motion_hypotheses")
    intentional_convergence = range_plan.get("intentional_convergence", "")
    if (
        not isinstance(art_families, list) or len(set(art_families)) < 4
        or any(item not in ART_DIRECTION_FAMILIES for item in art_families)
    ):
        raise DesignError("Completed concept laboratories require at least four distinct art-direction families")
    if (
        not isinstance(composition_families, list) or len(set(composition_families)) < 3
        or any(item not in COMPOSITION_FAMILIES for item in composition_families)
    ):
        raise DesignError("Completed concept laboratories require at least three distinct composition families")
    if (
        not isinstance(page_depth_roles, list) or len(set(page_depth_roles)) < 5
        or any(item not in JOURNEY_STAGE_ROLES for item in page_depth_roles)
        or not {"opening", "proof", "closure"} <= set(page_depth_roles)
        or not set(page_depth_roles).intersection({"quiet-state", "edge-state"})
    ):
        raise DesignError("Completed concept laboratories require opening, proof, quiet or edge, closure, and at least one additional page-depth role")
    if not isinstance(typography_hypotheses, list) or not 3 <= len(typography_hypotheses) <= 6:
        raise DesignError("Completed concept laboratories require three to six typography hypotheses")
    normalized_typography: list[dict[str, Any]] = []
    typography_ids: set[str] = set()
    typography_families: set[str] = set()
    typography_specimen_hashes: set[str] = set()
    non_system_typography_count = 0
    for item in typography_hypotheses:
        if not isinstance(item, dict):
            raise DesignError("Every typography hypothesis must be an object")
        strategy_id = _identifier(str(item.get("strategy_id", "")), "typography strategy ID")
        family = item.get("family")
        if strategy_id in typography_ids or family not in TYPOGRAPHY_FAMILIES:
            raise DesignError("Typography hypotheses require unique IDs and supported families")
        source = item.get("source")
        if source not in TYPOGRAPHY_SOURCES:
            raise DesignError(f"Typography hypothesis {strategy_id} requires a supported source")
        text_fields = ("role_relationship", "responsive_behavior", "anti_default", "customization", "license_evidence")
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in text_fields):
            raise DesignError(f"Typography hypothesis {strategy_id} lacks role, responsive, anti-default, customization, or license evidence")
        specimen = item.get("specimen")
        if not isinstance(specimen, dict):
            raise DesignError(f"Typography hypothesis {strategy_id} requires a rendered specimen")
        specimen_relative, specimen_path = _artifact_relative_path(root, specimen.get("path"))
        specimen_actual = hashlib.sha256(specimen_path.read_bytes()).hexdigest() if specimen_path.is_file() else ""
        if specimen_path.suffix.lower() not in {".html", ".png", ".svg"} or not specimen_actual or specimen.get("sha256") != specimen_actual:
            raise DesignError(f"Typography specimen is missing or changed: {specimen_relative}")
        if specimen_actual in typography_specimen_hashes:
            raise DesignError("Every typography hypothesis requires a distinct specimen")
        behavior_tests = item.get("behavior_tests")
        if not isinstance(behavior_tests, list) or not {"display", "text", "narrow"} <= set(behavior_tests):
            raise DesignError(f"Typography hypothesis {strategy_id} must test display, text, and narrow behavior")
        normalized_typography.append({
            "strategy_id": strategy_id, "family": family, "source": source,
            **{key: item[key].strip() for key in text_fields},
            "behavior_tests": list(dict.fromkeys(behavior_tests)),
            "specimen": {"path": specimen_relative, "sha256": specimen_actual},
        })
        typography_ids.add(strategy_id)
        typography_families.add(family)
        typography_specimen_hashes.add(specimen_actual)
        if source != "system":
            non_system_typography_count += 1
    if len(typography_families) < 3:
        raise DesignError("Completed concept laboratories require at least three typography families")
    if non_system_typography_count < 1:
        raise DesignError("Completed concept laboratories require at least one supplied, licensed, custom-lettered, or code-native typography study")
    if not isinstance(page_grammar_hypotheses, list) or not 4 <= len(page_grammar_hypotheses) <= 7:
        raise DesignError("Completed concept laboratories require four to seven page-grammar hypotheses")
    normalized_page_grammars: list[dict[str, str]] = []
    page_grammar_ids: set[str] = set()
    page_grammar_families: set[str] = set()
    for item in page_grammar_hypotheses:
        if not isinstance(item, dict):
            raise DesignError("Every page-grammar hypothesis must be an object")
        grammar_id = _identifier(str(item.get("grammar_id", "")), "page grammar ID")
        family = item.get("family")
        if grammar_id in page_grammar_ids or family not in PAGE_GRAMMAR_FAMILIES:
            raise DesignError("Page-grammar hypotheses require unique IDs and supported families")
        fields = ("hypothesis", "responsive_behavior", "depth_proof", "risk")
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in fields):
            raise DesignError(f"Page grammar {grammar_id} lacks hypothesis, responsive, depth, or risk evidence")
        normalized_page_grammars.append({"grammar_id": grammar_id, "family": family, **{key: item[key].strip() for key in fields}})
        page_grammar_ids.add(grammar_id)
        page_grammar_families.add(family)
    if len(page_grammar_families) < 4 or page_grammar_families == {"longform-narrative"}:
        raise DesignError("Completed concept laboratories require at least four materially different page grammars")
    if not isinstance(interaction_motion_hypotheses, list) or not 3 <= len(interaction_motion_hypotheses) <= 6:
        raise DesignError("Completed concept laboratories require three to six interaction and motion hypotheses")
    normalized_interactions: list[dict[str, Any]] = []
    interaction_ids: set[str] = set()
    interaction_artifact_hashes: set[str] = set()
    for item in interaction_motion_hypotheses:
        if not isinstance(item, dict):
            raise DesignError("Every interaction and motion hypothesis must be an object")
        strategy_id = _identifier(str(item.get("strategy_id", "")), "interaction and motion strategy ID")
        interaction_mode = item.get("mode")
        if strategy_id in interaction_ids or interaction_mode not in INTERACTION_MOTION_MODES:
            raise DesignError("Interaction and motion hypotheses require unique IDs and supported modes")
        fields = ("semantic_purpose", "reduced_motion", "static_fallback", "risk")
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in fields):
            raise DesignError(f"Interaction and motion hypothesis {strategy_id} lacks semantic, fallback, or risk evidence")
        prototype = item.get("prototype")
        if not isinstance(prototype, dict):
            raise DesignError(f"Interaction and motion hypothesis {strategy_id} requires a prototype artifact")
        prototype_relative, prototype_path = _artifact_relative_path(root, prototype.get("path"))
        prototype_actual = hashlib.sha256(prototype_path.read_bytes()).hexdigest() if prototype_path.is_file() else ""
        if prototype_path.suffix.lower() not in {".html", ".json", ".png", ".svg"} or not prototype_actual or prototype.get("sha256") != prototype_actual:
            raise DesignError(f"Interaction and motion prototype is missing or changed: {prototype_relative}")
        if prototype_actual in interaction_artifact_hashes:
            raise DesignError("Every interaction and motion hypothesis requires a distinct prototype")
        normalized_interactions.append({"strategy_id": strategy_id, "mode": interaction_mode, **{key: item[key].strip() for key in fields}, "prototype": {"path": prototype_relative, "sha256": prototype_actual}})
        interaction_ids.add(strategy_id)
        interaction_artifact_hashes.add(prototype_actual)
    if not isinstance(intentional_convergence, str):
        raise DesignError("Concept-laboratory intentional_convergence must be text")
    normalized_range_plan = {
        "art_direction_families": list(dict.fromkeys(art_families)),
        "typography_hypotheses": normalized_typography,
        "composition_families": list(dict.fromkeys(composition_families)),
        "page_depth_roles": list(dict.fromkeys(page_depth_roles)),
        "page_grammar_hypotheses": normalized_page_grammars,
        "interaction_motion_hypotheses": normalized_interactions,
        "intentional_convergence": intentional_convergence.strip(),
    }
    normalized_lenses: list[dict[str, str]] = []
    lens_ids: set[str] = set()
    for item in lenses:
        if not isinstance(item, dict):
            raise DesignError("Every generative lens must be an object")
        lens_id = _identifier(str(item.get("lens_id", "")), "generative lens ID")
        if lens_id in lens_ids:
            raise DesignError("Generative lens IDs must be unique")
        thesis = item.get("thesis")
        truth = item.get("product_truth")
        if not all(isinstance(text, str) and text.strip() for text in (thesis, truth)):
            raise DesignError("Every generative lens requires a thesis and project-specific product truth")
        normalized_lenses.append({"lens_id": lens_id, "thesis": thesis.strip(), "product_truth": truth.strip()})
        lens_ids.add(lens_id)
    if not 8 <= len(seeds) <= 12:
        raise DesignError("Completed concept laboratories require eight to twelve inexpensive seeds")
    normalized_seeds: list[dict[str, Any]] = []
    seed_ids: set[str] = set()
    artifact_hashes: set[str] = set()
    media: set[str] = set()
    represented_lenses: set[str] = set()
    for item in seeds:
        if not isinstance(item, dict):
            raise DesignError("Every generative seed must be an object")
        seed_id = _identifier(str(item.get("seed_id", "")), "generative seed ID")
        lens_id = _identifier(str(item.get("lens_id", "")), "generative lens ID")
        medium = item.get("medium")
        if seed_id in seed_ids or lens_id not in lens_ids or medium not in GENERATIVE_MEDIA:
            raise DesignError("Generative seeds require unique IDs, known lenses, and supported media")
        art_family = item.get("art_direction_family")
        typography_strategy_id = item.get("typography_strategy_id")
        composition_family = item.get("composition_family")
        depth_roles = item.get("page_depth_roles")
        if art_family not in set(normalized_range_plan["art_direction_families"]):
            raise DesignError(f"Generative seed {seed_id} requires a planned art-direction family")
        if typography_strategy_id not in typography_ids:
            raise DesignError(f"Generative seed {seed_id} requires a planned typography strategy")
        if composition_family not in set(normalized_range_plan["composition_families"]):
            raise DesignError(f"Generative seed {seed_id} requires a planned composition family")
        if not isinstance(depth_roles, list) or not depth_roles or any(role not in set(normalized_range_plan["page_depth_roles"]) for role in depth_roles):
            raise DesignError(f"Generative seed {seed_id} requires planned page-depth roles")
        text_fields = ("hypothesis", "project_specificity", "surprising_quality", "risk")
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in text_fields):
            raise DesignError(f"Generative seed {seed_id} lacks its hypothesis, specificity, surprise, or risk")
        mechanics = item.get("transferable_mechanics")
        if not isinstance(mechanics, list) or not mechanics or any(not isinstance(entry, str) or not entry.strip() for entry in mechanics):
            raise DesignError(f"Generative seed {seed_id} requires transferable mechanics")
        provenance = item.get("provenance")
        if provenance not in {"generated", "project-owned", "supplied-with-rights", "derived-study"}:
            raise DesignError(f"Generative seed {seed_id} requires supported provenance")
        artifact = item.get("artifact")
        if not isinstance(artifact, dict):
            raise DesignError(f"Generative seed {seed_id} requires an artifact")
        relative, path = _artifact_relative_path(root, artifact.get("path"))
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if not actual or artifact.get("sha256") != actual:
            raise DesignError(f"Generative seed artifact is missing or changed: {relative}")
        if actual in artifact_hashes:
            raise DesignError("Every generative seed requires a distinct artifact")
        normalized_seeds.append({
            "seed_id": seed_id, "lens_id": lens_id, "medium": medium,
            "art_direction_family": art_family, "typography_strategy_id": typography_strategy_id,
            "composition_family": composition_family, "page_depth_roles": list(dict.fromkeys(depth_roles)),
            **{key: item[key].strip() for key in text_fields},
            "transferable_mechanics": [entry.strip() for entry in mechanics],
            "provenance": provenance, "artifact": {"path": relative, "sha256": actual},
        })
        seed_ids.add(seed_id)
        artifact_hashes.add(actual)
        media.add(medium)
        represented_lenses.add(lens_id)
    if len(represented_lenses) < 4:
        raise DesignError("Completed concept laboratories must explore at least four lenses")
    if len({item["art_direction_family"] for item in normalized_seeds}) < 4:
        raise DesignError("Completed concept laboratories must realize at least four art-direction families in seed artifacts")
    if len({item["typography_strategy_id"] for item in normalized_seeds}) < 3:
        raise DesignError("Completed concept laboratories must realize at least three typography strategies in seed artifacts")
    if len({item["composition_family"] for item in normalized_seeds}) < 3:
        raise DesignError("Completed concept laboratories must realize at least three composition families in seed artifacts")
    if not set(normalized_range_plan["page_depth_roles"]) <= {role for item in normalized_seeds for role in item["page_depth_roles"]}:
        raise DesignError("Completed concept laboratories must test every planned page-depth role in seed artifacts")
    if mode == "mixed-media" and (len(media) < 3 or not media.intersection(GENERATED_IMAGE_MEDIA)):
        raise DesignError("Mixed-media concept laboratories require at least three media including image generation or editing")
    if mode == "generated-media" and not media.intersection(GENERATED_IMAGE_MEDIA):
        raise DesignError("Generated-media concept laboratories require image generation or editing")
    if mode == "code-only" and not media <= {"svg", "typography", "motion-frame", "code-sketch"}:
        raise DesignError("Code-only concept laboratories cannot claim generated-image media")
    generated_families = {
        item["art_direction_family"] for item in normalized_seeds if item["medium"] in GENERATED_IMAGE_MEDIA
    }
    if not isinstance(style_frames, list) or len(style_frames) < max(2, len(generated_families)):
        raise DesignError("Completed concept laboratories require multi-frame exploration for at least two promising art-direction families")
    normalized_style_frames: list[dict[str, Any]] = []
    style_frame_group_ids: set[str] = set()
    explored_style_families: set[str] = set()
    style_frame_hashes: set[str] = set()
    for group in style_frames:
        if not isinstance(group, dict):
            raise DesignError("Every style-frame exploration must be an object")
        exploration_id = _identifier(str(group.get("exploration_id", "")), "style-frame exploration ID")
        art_family = group.get("art_direction_family")
        if exploration_id in style_frame_group_ids or art_family not in set(normalized_range_plan["art_direction_families"]):
            raise DesignError("Style-frame explorations require unique IDs and planned art-direction families")
        hypothesis = group.get("hypothesis")
        synthesis = group.get("synthesis")
        if not isinstance(hypothesis, str) or not hypothesis.strip() or not isinstance(synthesis, str) or not synthesis.strip():
            raise DesignError(f"Style-frame exploration {exploration_id} requires a hypothesis and synthesis")
        frames = group.get("frames")
        if not isinstance(frames, list) or not 2 <= len(frames) <= 4:
            raise DesignError(f"Style-frame exploration {exploration_id} requires two to four frames")
        normalized_frames: list[dict[str, Any]] = []
        frame_ids: set[str] = set()
        for frame in frames:
            if not isinstance(frame, dict):
                raise DesignError("Every style frame must be an object")
            frame_id = _identifier(str(frame.get("frame_id", "")), "style frame ID")
            method = frame.get("method")
            lesson = frame.get("lesson")
            if frame_id in frame_ids or method not in STYLE_FRAME_METHODS or not isinstance(lesson, str) or not lesson.strip():
                raise DesignError("Style frames require unique IDs, supported methods, and a lesson")
            artifact = frame.get("artifact")
            if not isinstance(artifact, dict):
                raise DesignError(f"Style frame {frame_id} requires an artifact")
            relative, artifact_path = _artifact_relative_path(root, artifact.get("path"))
            actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest() if artifact_path.is_file() else ""
            if artifact_path.suffix.lower() not in {".html", ".jpeg", ".jpg", ".png", ".svg", ".webp"} or not actual or artifact.get("sha256") != actual:
                raise DesignError(f"Style frame is missing or changed: {relative}")
            if actual in style_frame_hashes:
                raise DesignError("Every style frame requires a distinct artifact")
            normalized_frames.append({"frame_id": frame_id, "method": method, "lesson": lesson.strip(), "artifact": {"path": relative, "sha256": actual}})
            frame_ids.add(frame_id)
            style_frame_hashes.add(actual)
        selected = group.get("selected_frame_ids")
        rejected = group.get("rejected_frame_ids")
        mechanics = group.get("system_extractions")
        if (
            not isinstance(selected, list) or not selected or not set(selected) <= frame_ids
            or not isinstance(rejected, list) or not rejected or not set(rejected) <= frame_ids
            or set(selected) & set(rejected)
        ):
            raise DesignError(f"Style-frame exploration {exploration_id} must explicitly select and reject frames")
        if not isinstance(mechanics, list) or len(mechanics) < 3 or any(not isinstance(item, str) or not item.strip() for item in mechanics):
            raise DesignError(f"Style-frame exploration {exploration_id} requires at least three system extractions")
        normalized_style_frames.append({
            "exploration_id": exploration_id, "art_direction_family": art_family,
            "hypothesis": hypothesis.strip(), "frames": normalized_frames,
            "selected_frame_ids": selected, "rejected_frame_ids": rejected,
            "system_extractions": [item.strip() for item in mechanics], "synthesis": synthesis.strip(),
        })
        style_frame_group_ids.add(exploration_id)
        explored_style_families.add(art_family)
    if not generated_families <= explored_style_families:
        raise DesignError("Every generated art-direction family requires a multi-frame exploration before concept commitment")
    if len(combinations) < 2:
        raise DesignError("Completed concept laboratories require at least two cross-pollination experiments")
    normalized_combinations: list[dict[str, Any]] = []
    combination_ids: set[str] = set()
    for item in combinations:
        if not isinstance(item, dict):
            raise DesignError("Every cross-pollination experiment must be an object")
        combination_id = _identifier(str(item.get("combination_id", "")), "cross-pollination ID")
        linked = item.get("seed_ids")
        hypothesis = item.get("hypothesis")
        mechanics = item.get("resulting_mechanics")
        if combination_id in combination_ids or not isinstance(linked, list) or len(set(linked)) < 2 or not set(linked) <= seed_ids:
            raise DesignError("Cross-pollination experiments require unique IDs and at least two known seeds")
        if not isinstance(hypothesis, str) or not hypothesis.strip() or not isinstance(mechanics, list) or not mechanics or any(not isinstance(entry, str) or not entry.strip() for entry in mechanics):
            raise DesignError("Cross-pollination experiments require a hypothesis and resulting mechanics")
        normalized_combinations.append({"combination_id": combination_id, "seed_ids": linked, "hypothesis": hypothesis.strip(), "resulting_mechanics": [entry.strip() for entry in mechanics]})
        combination_ids.add(combination_id)
    if not 3 <= len(shortlist) <= 6 or len(set(shortlist)) != len(shortlist) or not set(shortlist) <= seed_ids:
        raise DesignError("Completed concept laboratories require three to six unique shortlisted seeds")
    normalized = {
        "status": status, "mode": mode, "required_for_directioning": True,
        "lenses": normalized_lenses, "seeds": normalized_seeds,
        "cross_pollinations": normalized_combinations, "shortlisted_seed_ids": shortlist,
        "style_frame_explorations": normalized_style_frames,
        "range_plan": normalized_range_plan,
        "omission_rationale": "",
    }
    normalized["laboratory_hash"] = _canonical_hash(normalized)
    return normalized


def concept_lab_validate(root: Path, config: dict[str, Any], input_path: Path) -> dict[str, Any]:
    _enabled(config)
    laboratory = _validate_generative_exploration(_read_json(input_path), root)
    return {
        "status": laboratory["status"], "mode": laboratory["mode"],
        "lens_count": len(laboratory["lenses"]), "seed_count": len(laboratory["seeds"]),
        "media_count": len({item["medium"] for item in laboratory["seeds"]}),
        "art_direction_family_count": len({item["art_direction_family"] for item in laboratory["seeds"]}) if laboratory["status"] == "complete" else 0,
        "typography_strategy_count": len({item["typography_strategy_id"] for item in laboratory["seeds"]}) if laboratory["status"] == "complete" else 0,
        "typography_family_count": len({item["family"] for item in laboratory.get("range_plan", {}).get("typography_hypotheses", [])}),
        "composition_family_count": len({item["composition_family"] for item in laboratory["seeds"]}) if laboratory["status"] == "complete" else 0,
        "page_depth_role_count": len(laboratory.get("range_plan", {}).get("page_depth_roles", [])),
        "page_grammar_count": len(laboratory.get("range_plan", {}).get("page_grammar_hypotheses", [])),
        "interaction_motion_count": len(laboratory.get("range_plan", {}).get("interaction_motion_hypotheses", [])),
        "style_frame_family_count": len({item["art_direction_family"] for item in laboratory.get("style_frame_explorations", [])}),
        "style_frame_count": sum(len(item["frames"]) for item in laboratory.get("style_frame_explorations", [])),
        "non_system_typography_count": sum(item.get("source") != "system" for item in laboratory.get("range_plan", {}).get("typography_hypotheses", [])),
        "generated_seed_count": sum(item["medium"] in GENERATED_IMAGE_MEDIA for item in laboratory["seeds"]),
        "shortlisted_seed_count": len(laboratory["shortlisted_seed_ids"]),
        "laboratory_hash": laboratory["laboratory_hash"], "execution_authorized": False,
    }


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


def _validate_source_uncertainties(value: Any, open_questions: list[str], working_assumptions: list[str]) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise DesignError("source_uncertainties must be an array of objects")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        question = item.get("question")
        disposition = item.get("disposition")
        response = item.get("response", "")
        source_refs = item.get("source_refs", [])
        if not isinstance(question, str) or not question.strip() or question.strip() in seen:
            raise DesignError("source_uncertainties requires unique non-empty questions")
        if disposition not in UNCERTAINTY_DISPOSITIONS or not isinstance(response, str):
            raise DesignError(f"Source uncertainty {question.strip()} requires a valid disposition and response")
        if not isinstance(source_refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in source_refs):
            raise DesignError(f"Source uncertainty {question.strip()} has invalid source_refs")
        normalized = {"question": question.strip(), "disposition": disposition, "response": response.strip(), "source_refs": list(dict.fromkeys(ref.strip() for ref in source_refs))}
        if disposition in {"open", "deferred"} and normalized["question"] not in open_questions:
            raise DesignError(f"Open source uncertainty must remain in open_questions: {normalized['question']}")
        if disposition == "assumed" and (not normalized["response"] or normalized["response"] not in working_assumptions):
            raise DesignError(f"Assumed source uncertainty must remain in working_assumptions: {normalized['question']}")
        if disposition == "resolved" and (not normalized["response"] or not normalized["source_refs"]):
            raise DesignError(f"Resolved source uncertainty requires a response and source evidence: {normalized['question']}")
        result.append(normalized)
        seen.add(normalized["question"])
    return result


def _validate_modality_assessment(value: Any, targets: list[str], *, required: bool) -> dict[str, Any] | None:
    if value is None:
        if required:
            raise DesignError("Authored directions require modality_assessment")
        return None
    if not isinstance(value, dict):
        raise DesignError("modality_assessment must be an object")
    signals = _string_list(value.get("observed_signals"), "modality_assessment observed_signals", required=True)
    selected = _string_list(value.get("selected_targets"), "modality_assessment selected_targets", required=True)
    if set(selected) != set(targets):
        raise DesignError("modality_assessment selected_targets must exactly match targets")
    rationale = value.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise DesignError("modality_assessment requires rationale")
    conflicts = value.get("conflicts", [])
    if not isinstance(conflicts, list) or any(not isinstance(item, dict) for item in conflicts):
        raise DesignError("modality_assessment conflicts must be an array of objects")
    normalized_conflicts = []
    for item in conflicts:
        conflict = item.get("conflict")
        status = item.get("status")
        resolution = item.get("resolution", "")
        if not isinstance(conflict, str) or not conflict.strip() or status not in MODALITY_CONFLICT_STATUSES or not isinstance(resolution, str):
            raise DesignError("modality_assessment has an invalid conflict")
        if status == "unresolved":
            raise DesignError(f"Modality conflict must be resolved before direction authoring: {conflict.strip()}")
        if status == "resolved" and not resolution.strip():
            raise DesignError(f"Resolved modality conflict requires a resolution: {conflict.strip()}")
        normalized_conflicts.append({"conflict": conflict.strip(), "status": status, "resolution": resolution.strip()})
    return {"observed_signals": signals, "selected_targets": selected, "rationale": rationale.strip(), "conflicts": normalized_conflicts}


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
        normalized["variants"] = _string_list(item.get("variants"), f"component {component_id} variants")
        normalized["invalid_combinations"] = _string_list(item.get("invalid_combinations"), f"component {component_id} invalid_combinations")
        normalized["extension_points"] = _string_list(item.get("extension_points"), f"component {component_id} extension_points")
        for key in ("state_owner", "composition_boundary", "state_interface"):
            text = item.get(key, "")
            if not isinstance(text, str):
                raise DesignError(f"Component {component_id} has invalid {key}")
            normalized[key] = text.strip()
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
        "capability_digest": ["Record inspected tokens, components, assets, fonts, motion, breakpoints, and material missing capabilities before implementation-facing status."],
        "token_strategy": ["Translate approved semantic roles into the actual project token system."],
        "type_constraints": ["Set readable measures, wrapping behavior, fallbacks, and responsive ceilings."],
        "layout_constraints": ["Define spacing rhythm, collision behavior, and narrow-screen transformation."],
        "motion_constraints": ["Preserve content without motion and respect reduced-motion preferences."],
        "component_recipes": ["Use installed primitives for behavior while preserving project-specific expression."],
        "change_impact_checks": ["Before revising a shared token or recipe, identify affected surfaces, states, preservation risks, and required recaptures."],
        "hardening_checks": ["Test long content, overflow, focus, target sizes, contrast, interruption, and recovery."],
    }
    for key, default in implementation_defaults.items():
        items = implementation.get(key, default)
        if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
            raise DesignError(f"distinctive_expression implementation_system requires non-empty {key}")
        result["implementation_system"][key] = list(dict.fromkeys(item.strip() for item in items))
    surface_grammar = implementation.get("surface_grammar", [{
        "surface_role": "primary-content", "parent_role": "application-or-artifact-canvas",
        "fill": "Use the approved primary reading or working field.",
        "border": "Use boundaries only when they communicate grouping, state, or interaction.",
        "elevation": "Keep the primary field on the base plane; reserve elevation for temporary focus or consequential interruption.",
        "radius": "Use the approved radius family consistently rather than library defaults.",
        "density": "Match spacing and information density to the usage scene.",
        "typography": "Apply the approved content hierarchy and readable measure.",
        "state_behavior": "Preserve hierarchy, semantics, and contrast across interactive and system states.",
    }])
    if not isinstance(surface_grammar, list) or not surface_grammar or any(not isinstance(item, dict) for item in surface_grammar):
        raise DesignError("distinctive_expression implementation_system requires surface_grammar")
    result["implementation_system"]["surface_grammar"] = []
    for item in surface_grammar:
        normalized_surface = {}
        for key in ("surface_role", "parent_role", "fill", "border", "elevation", "radius", "density", "typography", "state_behavior"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"distinctive_expression implementation_system surface_grammar requires {key}")
            normalized_surface[key] = text.strip()
        result["implementation_system"]["surface_grammar"].append(normalized_surface)
    responsive_matrix = implementation.get("responsive_delta_matrix", [{
        "element": result["signature_element"],
        "desktop": "Use the full approved composition.",
        "tablet": "Recompose relationships before reducing scale or removing content.",
        "mobile": "Preserve meaning, sequence, state, and recognition in a linear or disclosed form.",
        "invariant": "Preserve the subject-derived relationship, semantic order, and required action.",
    }])
    if not isinstance(responsive_matrix, list) or not responsive_matrix or any(not isinstance(item, dict) for item in responsive_matrix):
        raise DesignError("distinctive_expression implementation_system requires responsive_delta_matrix")
    result["implementation_system"]["responsive_delta_matrix"] = []
    for item in responsive_matrix:
        normalized_delta = {}
        for key in ("element", "desktop", "tablet", "mobile", "invariant"):
            text = item.get(key)
            if not isinstance(text, str) or not text.strip():
                raise DesignError(f"distinctive_expression implementation_system responsive_delta_matrix requires {key}")
            normalized_delta[key] = text.strip()
        result["implementation_system"]["responsive_delta_matrix"].append(normalized_delta)
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
    requested_workflow = payload.get("workflow_version", 1)
    if requested_workflow not in {1, 2, 3}:
        raise DesignError("workflow_version must be 1, 2, or 3")
    creative_director_workflow = requested_workflow >= 2
    reference_translation_workflow = requested_workflow >= 3
    v2_fields = {
        "collaboration_profile", "specialization", "research", "reference_decomposition",
        "generative_exploration", "concept_presentation_mode", "rejected_decisions",
    }
    if not creative_director_workflow and v2_fields.intersection(payload):
        raise DesignError("Creative-director fields require explicit workflow_version 2 or 3")
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
        if payload["implementation_context"].get("react_version"):
            for component in payload["component_map"]:
                missing = [key for key in ("state_owner", "composition_boundary", "state_interface") if not component[key]]
                if missing or not component["variants"]:
                    raise DesignError(f"Complete React component {component['component_id']} requires composition ownership, a state interface, and explicit variants")
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
    payload["collaboration_profile"] = _infer_collaboration_profile(payload)
    payload["specialization"] = _infer_specialization(payload)
    payload["research"] = _validate_research_record(payload.get("research"), root, precision=requested_workflow >= 3)
    payload["reference_decomposition"] = _validate_reference_decomposition(payload.get("reference_decomposition"))
    if creative_director_workflow and "generative_exploration" not in payload:
        raise DesignError("Creative-director workflow requires an explicit generative_exploration record")
    payload["generative_exploration"] = _validate_generative_exploration(payload.get("generative_exploration"), root) if creative_director_workflow else None
    presentation_mode = payload.get("concept_presentation_mode")
    if presentation_mode is not None and presentation_mode not in CONCEPT_PRESENTATION_MODES:
        raise DesignError("concept_presentation_mode must be equal-directions or director-led")
    payload["concept_presentation_mode"] = presentation_mode
    rejected = payload.get("rejected_decisions", [])
    if not isinstance(rejected, list) or any(not isinstance(item, (str, dict)) for item in rejected):
        raise DesignError("rejected_decisions must be an array of text or decision objects")
    payload["rejected_decisions"] = rejected
    consequence_level = payload.get("consequence_level", "moderate")
    if consequence_level not in CONSEQUENCE_LEVELS:
        raise DesignError("consequence_level must be routine, moderate, or high")
    payload["consequence_level"] = consequence_level
    payload["source_uncertainties"] = _validate_source_uncertainties(
        payload.get("source_uncertainties"), payload["open_questions"], payload["working_assumptions"]
    )
    supplied = payload.get("directions")
    payload["modality_assessment"] = _validate_modality_assessment(
        payload.get("modality_assessment"), payload["targets"], required=supplied is not None
    )
    if consequence_level == "high" and payload["prototype_scope"] and payload["prototype_scope"]["fixture_data"] == "present" and not payload["content_provenance"]:
        raise DesignError("High-consequence prototypes with fixture content require content_provenance")
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
    if payload["concept_presentation_mode"] is None:
        payload["concept_presentation_mode"] = "equal-directions" if count > 1 and bool(payload["open_questions"]) else "director-led"
    if creative_director_workflow and supplied is None:
        raise DesignError("Creative-director workflow requires agent-authored project-specific directions")
    if creative_director_workflow and payload["concept_presentation_mode"] == "director-led" and count != 1:
        raise DesignError("Director-led workflow requires one selectable direction; contrast studies belong in concept evidence")
    if creative_director_workflow and payload["concept_presentation_mode"] == "equal-directions" and count < 2:
        raise DesignError("Equal-direction workflow requires two or three selectable directions")
    if supplied is not None and payload["direction_assessment"] is None:
        raise DesignError("Authored directions require direction_assessment")
    if payload["direction_assessment"]:
        unresolved_ambiguities = set(payload["direction_assessment"]["material_ambiguities"]) - set(payload["direction_assessment"]["resolved_by_evidence"])
        required_count = min(3, 1 + len(unresolved_ambiguities))
        if count < required_count:
            raise DesignError(f"At least {required_count} directions are required while material design ambiguities remain unresolved")
    if supplied is not None:
        if not isinstance(supplied, list) or not 1 <= len(supplied) <= 3:
            raise DesignError("Supplied creative work requires one to three directions")
        if len(supplied) != count:
            raise DesignError("Supplied direction count must match direction_count")
        directions = [_validate_direction(item, index, payload["targets"]) for index, item in enumerate(supplied)]
    else:
        directions = [_validate_direction(_generated_direction(payload, index), index, payload["targets"]) for index in range(count)]
    if len({item["direction_id"] for item in directions}) != len(directions):
        raise DesignError("Direction IDs must be unique")
    design_id = _identifier(str(payload.get("design_id") or f"design-{hashlib.sha256((config['project_id'] + payload['title']).encode()).hexdigest()[:10]}"), "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    prior_path = design_dir / "draft.json"
    revision = 1
    carried_feedback: list[dict[str, Any]] = []
    carried_rejections: list[Any] = []
    carried_decisions: list[dict[str, Any]] = []
    if prior_path.exists():
        prior = _read_json(prior_path)
        carried_feedback = list(prior.get("feedback_rounds", []))
        carried_rejections = list(prior.get("rejected_decisions", []))
        carried_decisions = list(prior.get("decision_register", []))
        refining_current_revision = (
            creative_director_workflow
            and prior.get("workflow_version", 1) >= 2
            and prior.get("status") == "refining"
            and isinstance(prior.get("concept_evidence"), dict)
            and prior["concept_evidence"].get("validated") is False
        )
        if refining_current_revision:
            revision = int(prior.get("revision", 1))
        else:
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
    merged_rejections = carried_rejections + payload["rejected_decisions"]
    deduped_rejections: list[Any] = []
    seen_rejections: set[str] = set()
    for item in merged_rejections:
        key = _canonical_hash(item)
        if key not in seen_rejections:
            deduped_rejections.append(item)
            seen_rejections.add(key)
    record = {
        "schema_version": requested_workflow,
        "workflow_version": requested_workflow,
        "design_id": design_id,
        "revision": revision,
        "status": "developing-reference-translations" if reference_translation_workflow else ("developing-concepts" if creative_director_workflow else "awaiting-selection"),
        "title": payload["title"].strip(),
        "intent": payload["intent"].strip(),
        "collaboration_profile": payload["collaboration_profile"],
        "collaboration_contract": _collaboration_contract(payload["collaboration_profile"]),
        "specialization": payload["specialization"],
        "research": payload["research"],
        "reference_decomposition": payload["reference_decomposition"],
        "generative_exploration": payload["generative_exploration"],
        "concept_presentation_mode": payload["concept_presentation_mode"],
        "concept_evidence": None,
        "reference_translation": None,
        "feedback_rounds": carried_feedback,
        "decision_register": carried_decisions,
        "rejected_decisions": deduped_rejections,
        "slop_ruleset_version": design_slop.RULESET_VERSION,
        "slop_ruleset_hash": design_slop.ruleset_hash(),
        "audiences": payload["audiences"],
        "targets": payload["targets"],
        "modality_assessment": payload["modality_assessment"],
        "consequence_level": payload["consequence_level"],
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
        "source_uncertainties": payload["source_uncertainties"],
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
        f"Consequence level: `{draft_record.get('consequence_level', 'moderate')}`  ",
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
    modality_assessment = draft_record.get("modality_assessment")
    lines.extend(["## Modality assessment", ""])
    if modality_assessment:
        lines.extend([
            f"Selected targets: {', '.join(f'`{item}`' for item in modality_assessment['selected_targets'])}", "",
            f"Rationale: {modality_assessment['rationale']}", "",
            "Observed signals:", "", *[f"- {item}" for item in modality_assessment["observed_signals"]], "",
        ])
        if modality_assessment["conflicts"]:
            lines.extend(["Resolved modality conflicts:", "", *[f"- **{item['conflict']} — {item['status']}:** {item['resolution'] or 'Not applicable.'}" for item in modality_assessment["conflicts"]], ""])
    else:
        lines.extend(["- Legacy input supplied no explicit modality assessment; verify targets before implementation-facing work.", ""])
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
    uncertainties = draft_record.get("source_uncertainties", [])
    lines.extend(["## Source uncertainty register", ""])
    if uncertainties:
        for item in uncertainties:
            sources = "; ".join(item["source_refs"]) or "No resolving source recorded."
            lines.append(f"- **{item['question']} — {item['disposition']}:** {item['response'] or 'No answer assumed.'} Sources: {sources}")
    else:
        lines.append("- No structured source uncertainties were supplied; do not infer that the source material was complete.")
    lines.append("")
    laboratory = draft_record.get("generative_exploration")
    if isinstance(laboratory, dict):
        lines.extend(["## Generative concept lineage", "", f"Status: `{laboratory.get('status')}`  ", f"Laboratory hash: `{laboratory.get('laboratory_hash')}`", ""])
        if laboratory.get("status") == "complete":
            lines.extend(["Exploration lenses:", "", *[f"- **{item['lens_id']}:** {item['thesis']} Product truth: {item['product_truth']}" for item in laboratory.get("lenses", [])], ""])
            lines.extend(["Shortlisted seeds:", "", *[f"- `{seed_id}`" for seed_id in laboratory.get("shortlisted_seed_ids", [])], ""])
        else:
            lines.extend([f"- {laboratory.get('omission_rationale') or 'No exploration rationale recorded.'}", ""])
        range_evidence = draft_record.get("concept_evidence", {}).get("creative_range") if isinstance(draft_record.get("concept_evidence"), dict) else None
        if range_evidence:
            lines.extend(["Creative-range disposition:", "", f"- `{range_evidence.get('status')}` — {range_evidence.get('house_tell_review', {}).get('rationale', '')}", ""])
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
        for dimension in ("capability_digest", "token_strategy", "type_constraints", "layout_constraints", "motion_constraints", "component_recipes", "change_impact_checks", "hardening_checks"):
            lines.extend([f"#### {dimension.replace('_', ' ').title()}", "", *[f"- {item}" for item in implementation[dimension]], ""])
        lines.extend([
            "#### Surface Grammar", "",
            "| Surface | Parent | Fill | Border | Elevation | Radius | Density | Typography | State behavior |",
            "|---|---|---|---|---|---|---|---|---|",
        ])
        for surface in implementation["surface_grammar"]:
            lines.append("| " + " | ".join(surface[key].replace("|", "\\|") for key in ("surface_role", "parent_role", "fill", "border", "elevation", "radius", "density", "typography", "state_behavior")) + " |")
        lines.extend([
            "", "#### Responsive Delta Matrix", "",
            "| Element | Desktop | Tablet | Mobile | Invariant |", "|---|---|---|---|---|",
        ])
        for delta in implementation["responsive_delta_matrix"]:
            lines.append("| " + " | ".join(delta[key].replace("|", "\\|") for key in ("element", "desktop", "tablet", "mobile", "invariant")) + " |")
        lines.append("")
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
            if any(item.get("state_owner") for item in draft_record["component_map"]):
                lines.extend(["### React composition contracts", ""])
                for item in draft_record["component_map"]:
                    lines.extend([
                        f"#### {item['component_id']}", "",
                        f"- **State owner:** {item['state_owner'] or 'Not recorded'}",
                        f"- **Composition boundary:** {item['composition_boundary'] or 'Not recorded'}",
                        f"- **State interface:** {item['state_interface'] or 'Not recorded'}",
                        f"- **Explicit variants:** {', '.join(item['variants']) or 'None recorded'}",
                        f"- **Invalid combinations:** {'; '.join(item['invalid_combinations']) or 'None recorded'}",
                        f"- **Extension points:** {', '.join(item['extension_points']) or 'None recorded'}", "",
                    ])
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
    if record.get("workflow_version", 1) >= 2:
        evidence = record.get("concept_evidence")
        concept_ids = {item["direction_id"] for item in evidence.get("concepts", [])} if isinstance(evidence, dict) else set()
        if not evidence or not evidence.get("validated") or not set(requested).issubset(concept_ids):
            raise DesignError("Creative-director selection requires current validated concept and slop evidence")
    markdown = _direction_markdown(record, [by_id[item] for item in requested])
    design_hash = hashlib.sha256(markdown.encode()).hexdigest()
    (design_dir / "design.md").write_bytes(markdown.encode("utf-8"))
    update = {"status": "awaiting-approval", "selected_direction_ids": requested, "selected_by": actor, "selected_at": _now(), "design_hash": design_hash}
    if record.get("workflow_version", 1) >= 2:
        bundle = {
            "design_hash": design_hash,
            "visual_reference_hash": record["concept_evidence"]["visual_reference_hash"],
            "concept_manifest_hash": record["concept_evidence"]["manifest_hash"],
            "selected_slop_report_hashes": [
                concept["slop_report"]["report_hash"]
                for concept in record["concept_evidence"]["concepts"]
                if concept["direction_id"] in requested
            ],
            "slop_ruleset_version": record["slop_ruleset_version"],
            "slop_ruleset_hash": record["slop_ruleset_hash"],
        }
        if record.get("workflow_version", 1) >= 3:
            bundle["reference_translation_hash"] = record["concept_evidence"].get("reference_translation_hash")
            selected_concepts = [
                concept for concept in record["concept_evidence"]["concepts"]
                if concept["direction_id"] in requested
            ]
            bundle["typographic_transfer_hashes"] = [_canonical_hash(concept["typographic_transfer"]) for concept in selected_concepts]
            bundle["composition_asset_plan_hashes"] = [_canonical_hash(concept["composition_asset_plan"]) for concept in selected_concepts]
        update.update({"approval_bundle": bundle, "approval_bundle_hash": _canonical_hash(bundle), "prototype_slop_evidence": None})
    record.update(update)
    _write_json(design_dir / "draft.json", record)
    record["required_authorization_text"] = (
        f"Approve design {design_id} revision {record['revision']} hash {design_hash} bundle {record['approval_bundle_hash']}"
        if record.get("approval_bundle_hash")
        else f"Approve design {design_id} revision {record['revision']} hash {design_hash}"
    )
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
    if record.get("workflow_version", 1) >= 2:
        if _canonical_hash(record.get("approval_bundle")) != record.get("approval_bundle_hash"):
            raise DesignError("Approval bundle changed after selection")
        if not record.get("prototype_slop_evidence"):
            raise DesignError("Exact approval requires a passed slop check for the selected private prototype")
        prototype_slop = _verified_private_report(root, record["prototype_slop_evidence"], stage="prototype")
        _, prototype_report_path = _artifact_relative_path(root, prototype_slop["path"])
        prototype_report = _read_json(prototype_report_path)
        for key, expected in (("design_id", design_id), ("revision", revision), ("design_hash", actual_hash), ("approval_bundle_hash", record["approval_bundle_hash"])):
            if prototype_report.get(key) != expected:
                raise DesignError(f"Prototype AI-slop report {key} is stale")
        for item in prototype_report.get("files", []):
            relative, scanned_path = _artifact_relative_path(root, item.get("path"))
            if not scanned_path.is_file() or hashlib.sha256(scanned_path.read_bytes()).hexdigest() != item.get("sha256"):
                raise DesignError(f"Prototype AI-slop report is stale for: {relative}")
    required = (
        f"Approve design {design_id} revision {revision} hash {actual_hash} bundle {record['approval_bundle_hash']}"
        if record.get("approval_bundle_hash")
        else f"Approve design {design_id} revision {revision} hash {actual_hash}"
    )
    if authorization_text != required:
        raise DesignError("Authorization text must exactly match the design ID, revision, and hash")
    canonical_path = root / "docs" / "design" / "design.md"
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(draft_path, canonical_path)
    approved_references: list[dict[str, Any]] = []
    if record.get("workflow_version", 1) >= 2:
        reference_dir = root / "docs" / "design" / "references"
        reference_dir.mkdir(parents=True, exist_ok=True)
        for item in record.get("concept_evidence", {}).get("publishable_references", []):
            if item["ownership"] not in {"project-owned", "supplied-with-rights", "generated"}:
                raise DesignError("Only owned, rights-supplied, or generated references may be promoted")
            _, source = _artifact_relative_path(root, item["path"])
            if hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
                raise DesignError("Approved visual reference changed after concept validation")
            destination = reference_dir / source.name
            if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() != item["sha256"]:
                raise DesignError(f"Approved visual reference name conflicts with an existing file: {source.name}")
            shutil.copy2(source, destination)
            approved_references.append({"path": f"docs/design/references/{source.name}", "sha256": item["sha256"], "ownership": item["ownership"]})
        if _canonical_hash(record.get("concept_evidence", {}).get("visual_reference_material", [])) != record.get("approval_bundle", {}).get("visual_reference_hash"):
            raise DesignError("Visual-reference bundle changed after selection")
    approval = {
        "schema_version": 2 if record.get("workflow_version", 1) >= 2 else 1,
        "design_id": design_id, "revision": revision, "design_hash": actual_hash,
        "approved_by": approved_by, "approved_at": _now(), "authorization_text": authorization_text,
        "execution_authorized": False,
    }
    if record.get("workflow_version", 1) >= 2:
        approval.update({
            "visual_reference_hash": record["approval_bundle"]["visual_reference_hash"],
            "approval_bundle_hash": record["approval_bundle_hash"],
            "slop_ruleset_version": record["slop_ruleset_version"],
            "slop_ruleset_hash": record["slop_ruleset_hash"],
            "prototype_slop_evidence": record["prototype_slop_evidence"],
        })
        if record.get("workflow_version", 1) >= 3:
            approval["reference_translation_hash"] = record["approval_bundle"].get("reference_translation_hash")
            approval["approval_bundle"] = record["approval_bundle"]
    _write_json(design_dir / "approval.json", approval)
    shared = {key: approval[key] for key in ("schema_version", "design_id", "revision", "design_hash", "approved_by", "approved_at", "execution_authorized")}
    for key in ("visual_reference_hash", "approval_bundle_hash", "reference_translation_hash", "slop_ruleset_version", "slop_ruleset_hash"):
        if key in approval:
            shared[key] = approval[key]
    if "approval_bundle" in approval:
        shared["approval_bundle"] = approval["approval_bundle"]
    selected = [item for item in record["directions"] if item["direction_id"] in record["selected_direction_ids"]]
    alignment_contract = {
        "selected_direction_ids": record["selected_direction_ids"],
        "creative_signatures": [direction["creative_signature"] for direction in selected],
        "distinctive_expression": [direction["distinctive_expression"] for direction in selected],
        "creative_provenance": [item for direction in selected for item in direction["creative_provenance"]],
        "content_provenance": record.get("content_provenance", []),
        "source_uncertainties": record.get("source_uncertainties", []),
        "modality_assessment": record.get("modality_assessment"),
        "consequence_level": record.get("consequence_level", "moderate"),
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
    alignment_contract.update({
        "collaboration_profile": record.get("collaboration_profile"),
        "collaboration_contract": record.get("collaboration_contract"),
        "specialization": record.get("specialization"),
        "reference_decomposition": record.get("reference_decomposition", []),
        "research": record.get("research"),
        "generative_exploration": record.get("generative_exploration"),
        "decision_register": record.get("decision_register", []),
        "rejected_decisions": record.get("rejected_decisions", []),
        "concept_evidence": record.get("concept_evidence"),
        "reference_translation": record.get("reference_translation"),
        "slop_ruleset_version": record.get("slop_ruleset_version"),
    })
    shared.update({"status": "approved", "document_path": "docs/design/design.md", "visual_references": approved_references, "catalog_packs": record["catalog_packs"], "alignment_contract": alignment_contract})
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
    if status == "developing-reference-translations":
        return {"design_id": design_id, "revision": record["revision"], "status": status, "next_skill": "continuity-design", "human_required": False, "allowed_actions": ["rebuild-reference-mechanics", "compile-transfer-constraints", "render-project-adaptations", "validate-reference-translation"], "execution_authorized": False}
    if status == "developing-concepts":
        return {"design_id": design_id, "revision": record["revision"], "status": status, "next_skill": "continuity-design", "human_required": False, "allowed_actions": ["render-visual-evidence", "run-concept-slop-checks", "validate-concept-set"], "execution_authorized": False}
    if status in {"awaiting-feedback", "refining"}:
        return {"design_id": design_id, "revision": record["revision"], "status": status, "next_skill": "continuity-design", "human_required": True, "allowed_actions": ["react-to-numbered-visuals", "record-visual-delta", "mark-ready-for-selection"], "execution_authorized": False}
    if status == "awaiting-selection":
        return {"design_id": design_id, "revision": record["revision"], "status": status, "next_skill": "continuity-design", "human_required": True, "allowed_actions": ["select-or-combine"], "execution_authorized": False}
    if status == "awaiting-approval":
        return {"design_id": design_id, "revision": record["revision"], "design_hash": record["design_hash"], "approval_bundle_hash": record.get("approval_bundle_hash"), "status": status, "next_skill": "continuity-design", "human_required": True, "allowed_actions": ["validate-selected-prototype", "approve-exact-draft", "revise"], "execution_authorized": False}
    return {"design_id": design_id, "revision": record["revision"], "design_hash": record.get("design_hash"), "approval_bundle_hash": record.get("approval_bundle_hash"), "status": status, "next_skill": "continuity-plan", "human_required": False, "allowed_actions": ["plan-with-design-binding", "revise-design"], "execution_authorized": False}


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
    binding = {"design_id": record["design_id"], "revision": record["revision"], "design_hash": record["design_hash"], "catalog_packs": record["catalog_packs"], "alignment_contract": record.get("alignment_contract", {})}
    for key in ("approval_bundle_hash", "visual_reference_hash", "reference_translation_hash", "slop_ruleset_version", "slop_ruleset_hash"):
        if key in record:
            binding[key] = record[key]
    return [binding]


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


def _document_probe_fingerprint(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text
    for name, placeholder in (
        ("continuity-probe-target-sha256", "PROBE_TARGET_FINGERPRINT"),
        ("continuity-probe-source-bundle-sha256", "PROBE_SOURCE_BUNDLE_FINGERPRINT"),
    ):
        normalized = re.sub(
            rf'(<meta\s+name=["\']{name}["\']\s+content=["\'])[^"\']*(["\']\s*/?>)',
            rf"\g<1>{placeholder}\g<2>", normalized, flags=re.IGNORECASE,
        )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


RUNTIME_SOURCE_SUFFIXES = {".html", ".htm", ".css", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
_RUNTIME_DEPENDENCY_PATTERNS = (
    re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'(?:import|export)\s+(?:[^"\']*?\s+from\s+)?["\']([^"\']+)["\']'),
    re.compile(r'import\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'require(?:\.resolve)?\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'new\s+URL\s*\(\s*["\']([^"\']+)["\']\s*,\s*import\.meta\.url\s*\)'),
    re.compile(r'new\s+(?:Shared)?Worker\s*\(\s*["\']([^"\']+)["\']'),
    re.compile(r'import\.meta\.glob(?:Eager)?\s*\(\s*["\']([^"\']+)["\']\s*(?:,|\))'),
    re.compile(r'@import\s+(?:url\(\s*)?["\']?([^"\')\s;]+)', re.IGNORECASE),
)


def _runtime_alias_roots(root: Path, source: Path, reference: str) -> tuple[list[Path], bool]:
    candidates: list[Path] = []
    matched = False
    if reference.startswith("@/"):
        candidates.extend((root / "src" / reference[2:], root / reference[2:]))
        matched = True
    current = source.parent.resolve()
    root_resolved = root.resolve()
    while True:
        for name in ("tsconfig.json", "jsconfig.json"):
            config_path = current / name
            if not config_path.is_file():
                continue
            try:
                config_text = config_path.read_text(encoding="utf-8")
                config_text = re.sub(r"/\*.*?\*/", "", config_text, flags=re.DOTALL)
                config_text = re.sub(r"(^|\s)//.*$", r"\1", config_text, flags=re.MULTILINE)
                config_text = re.sub(r",\s*([}\]])", r"\1", config_text)
                options = json.loads(config_text).get("compilerOptions", {})
            except (OSError, json.JSONDecodeError, AttributeError):
                continue
            base = (current / str(options.get("baseUrl", "."))).resolve()
            paths = options.get("paths", {})
            if not isinstance(paths, dict):
                continue
            for alias, replacements in paths.items():
                if not isinstance(alias, str) or not isinstance(replacements, list):
                    continue
                if "*" in alias:
                    prefix, suffix = alias.split("*", 1)
                    if not reference.startswith(prefix) or (suffix and not reference.endswith(suffix)):
                        continue
                    wildcard = reference[len(prefix):len(reference) - len(suffix) if suffix else None]
                elif reference == alias:
                    wildcard = ""
                else:
                    continue
                matched = True
                for replacement in replacements:
                    if isinstance(replacement, str):
                        candidates.append(base / replacement.replace("*", wildcard))
        if current == root_resolved or root_resolved not in current.parents:
            break
        current = current.parent
    return candidates, matched


def _resolve_runtime_dependency(root: Path, source: Path, reference: str, *, strict: bool) -> Path | None:
    clean = reference.split("?", 1)[0].split("#", 1)[0].strip()
    if not clean or clean.startswith(("data:", "http:", "https:", "//", "#")):
        return None
    alias_candidates, alias_matched = _runtime_alias_roots(root, source, clean)
    raw_candidates = alias_candidates or [
        (root / clean.lstrip("/")) if clean.startswith("/") else (source.parent / clean)
    ]
    candidates: list[Path] = []
    for raw in raw_candidates:
        candidates.append(raw)
        if not raw.suffix:
            candidates.extend(raw.with_suffix(suffix) for suffix in RUNTIME_SOURCE_SUFFIXES)
            candidates.extend(raw / f"index{suffix}" for suffix in RUNTIME_SOURCE_SUFFIXES)
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if resolved.is_file() and resolved.suffix.lower() in RUNTIME_SOURCE_SUFFIXES:
            return resolved
    if (clean.startswith((".", "/")) or alias_matched) and (strict or Path(clean).suffix.lower() in RUNTIME_SOURCE_SUFFIXES or alias_matched):
        raise DesignError(f"Runtime source dependency is missing: {reference}")
    return None


def _runtime_source_closure(root: Path, target_document: Path) -> list[Path]:
    queue = [target_document.resolve()]
    found: set[Path] = set()
    while queue:
        source = queue.pop()
        if source in found:
            continue
        try:
            source.relative_to(root.resolve())
        except ValueError as exc:
            raise DesignError("Runtime source closure escapes the project root") from exc
        if not source.is_file() or source.suffix.lower() not in RUNTIME_SOURCE_SUFFIXES:
            raise DesignError(f"Runtime source is missing or unsupported: {source}")
        found.add(source)
        text = source.read_text(encoding="utf-8", errors="replace")
        for arguments in re.findall(r'importScripts\s*\(([^)]*)\)', text):
            references = re.findall(r'["\']([^"\']+)["\']', arguments)
            if not references:
                raise DesignError("importScripts runtime dependencies must use static local URLs")
            for reference in references:
                dependency = _resolve_runtime_dependency(root, source, reference, strict=True)
                if dependency is not None and dependency not in found:
                    queue.append(dependency)
        for arguments in re.findall(r'import\.meta\.glob(?:Eager)?\s*\(\s*\[([^\]]+)\]', text):
            references = re.findall(r'["\']([^"\']+)["\']', arguments)
            if not references:
                raise DesignError("import.meta.glob runtime dependencies must use static local patterns")
            for reference in references:
                if not reference.startswith((".", "/")):
                    raise DesignError(f"Runtime source glob must be relative or project-rooted: {reference}")
                glob_root = root.resolve() if reference.startswith("/") else source.parent
                matches = [
                    item.resolve() for item in glob_root.glob(reference.lstrip("/"))
                    if item.is_file() and item.suffix.lower() in RUNTIME_SOURCE_SUFFIXES
                ]
                if not matches:
                    raise DesignError(f"Runtime source glob has no supported matches: {reference}")
                queue.extend(item for item in matches if item not in found)
        for pattern_index, pattern in enumerate(_RUNTIME_DEPENDENCY_PATTERNS):
            for reference in pattern.findall(text):
                clean_reference = reference.split("?", 1)[0].split("#", 1)[0]
                if any(character in clean_reference for character in "*?["):
                    if not clean_reference.startswith((".", "/")):
                        raise DesignError(f"Runtime source glob must be relative or project-rooted: {reference}")
                    glob_root = root.resolve() if clean_reference.startswith("/") else source.parent
                    matches = [
                        item.resolve() for item in glob_root.glob(clean_reference.lstrip("/"))
                        if item.is_file() and item.suffix.lower() in RUNTIME_SOURCE_SUFFIXES
                    ]
                    if not matches:
                        raise DesignError(f"Runtime source glob has no supported matches: {reference}")
                    queue.extend(item for item in matches if item not in found)
                    continue
                dependency = _resolve_runtime_dependency(root, source, reference, strict=pattern_index > 0)
                if dependency is not None and dependency not in found:
                    queue.append(dependency)
    return sorted(found, key=lambda item: item.relative_to(root.resolve()).as_posix())


def _verified_runtime_source_bundle(root: Path, target_document: Path, declared: Any, label: str) -> dict[str, Any]:
    if not isinstance(declared, list) or not declared:
        raise DesignError(f"{label} requires hash-bound runtime source files")
    closure = _runtime_source_closure(root, target_document)
    closure_paths = {item.relative_to(root.resolve()).as_posix() for item in closure}
    normalized: list[dict[str, str]] = []
    declared_paths: set[str] = set()
    for item in declared:
        verified = _verified_reference_file(root, item, f"{label} runtime source", RUNTIME_SOURCE_SUFFIXES)
        if verified["path"] in declared_paths:
            raise DesignError(f"{label} runtime source files contain duplicates")
        normalized.append(verified)
        declared_paths.add(verified["path"])
    if declared_paths != closure_paths:
        missing = sorted(closure_paths - declared_paths)
        extra = sorted(declared_paths - closure_paths)
        raise DesignError(f"{label} runtime source closure does not match its declaration; missing={missing}, extra={extra}")
    target_relative = target_document.resolve().relative_to(root.resolve()).as_posix()
    entries = [
        {
            "path": item["path"],
            "sha256": _document_probe_fingerprint(target_document) if item["path"] == target_relative else item["sha256"],
        }
        for item in sorted(normalized, key=lambda value: value["path"])
    ]
    return {
        "target_document_path": target_relative,
        "target_document_sha256": _document_probe_fingerprint(target_document),
        "source_files": normalized,
        "source_bundle_sha256": _canonical_hash({"target_document_path": target_relative, "sources": entries}),
    }


def _set_probe_meta(document: str, name: str, content: str) -> str:
    tag = '<meta name="{}" content="{}">'.format(name, content)
    pattern = re.compile(
        rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\'][^"\']*["\']\s*/?>',
        re.IGNORECASE,
    )
    if pattern.search(document):
        return pattern.sub(tag, document, count=1)
    head_end = re.search(r"</head\s*>", document, re.IGNORECASE)
    if not head_end:
        raise DesignError("Probe preparation requires an HTML document with a head element")
    return document[:head_end.start()] + f"  {tag}\n" + document[head_end.start():]


def probe_prepare(root: Path, config: dict[str, Any], target_path: Path) -> dict[str, Any]:
    """Bind an HTML target and its complete local runtime source closure for browser evidence."""
    _enabled(config)
    target = target_path.resolve()
    try:
        target_relative = target.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise DesignError("Probe target must remain inside the project root") from exc
    if not target.is_file() or target.suffix.lower() not in {".html", ".htm"}:
        raise DesignError("Probe target must be an existing HTML document")
    document = target.read_text(encoding="utf-8")
    document = _set_probe_meta(document, "continuity-probe-target-path", target_relative)
    document = _set_probe_meta(document, "continuity-probe-target-sha256", "pending")
    document = _set_probe_meta(document, "continuity-probe-source-bundle-sha256", "pending")
    target.write_text(document, encoding="utf-8")
    closure = _runtime_source_closure(root, target)
    declared = [
        {"path": item.relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(item.read_bytes()).hexdigest()}
        for item in closure
    ]
    prepared = _verified_runtime_source_bundle(root, target, declared, "Browser probe")
    document = target.read_text(encoding="utf-8")
    document = _set_probe_meta(document, "continuity-probe-target-sha256", prepared["target_document_sha256"])
    document = _set_probe_meta(document, "continuity-probe-source-bundle-sha256", prepared["source_bundle_sha256"])
    target.write_text(document, encoding="utf-8")
    closure = _runtime_source_closure(root, target)
    final_declared = [
        {"path": item.relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(item.read_bytes()).hexdigest()}
        for item in closure
    ]
    final = _verified_runtime_source_bundle(root, target, final_declared, "Browser probe")
    if final["source_bundle_sha256"] != prepared["source_bundle_sha256"]:
        raise DesignError("Probe source-bundle fingerprint did not stabilize")
    return {
        "schema_version": 1,
        "target_document": {"path": target_relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()},
        "target_document_fingerprint": final["target_document_sha256"],
        "source_bundle_sha256": final["source_bundle_sha256"],
        "runtime_source_files": final["source_files"],
        "next_action": "Run artifact-browser-probe.js in the rendered desktop document without editing its output",
        "execution_authorized": False,
    }


VISUAL_REVIEW_QUESTIONS = {
    "signature_identifiable": "Can the signature be identified within five seconds?",
    "identity_specific": "Does the identity remain project-specific when the product name is removed?",
    "not_category_reflex": "Does the result avoid both the category default and its fashionable opposite?",
    "directions_structurally_distinct": "Are concept directions structurally different rather than cosmetically varied?",
    "not_library_default": "Does the implementation avoid retreating to component-library defaults?",
    "signature_survives_states": "Does the signature survive mobile, quiet states, errors, and reduced motion?",
    "reference_transformed": "Does the output adapt a mechanic instead of copying a reference identity?",
    "decoration_has_job": "Is each decorative choice doing work content, hierarchy, or subject material cannot do?",
}
VISUAL_REVIEW_FAILURE_RULES = {
    "signature_identifiable": "CDS-P002",
    "identity_specific": "CDS-D018",
    "not_category_reflex": "CDS-D017",
    "directions_structurally_distinct": "CDS-D019",
    "not_library_default": "CDS-P005",
    "signature_survives_states": "CDS-P002",
    "reference_transformed": "CDS-P003",
    "decoration_has_job": "CDS-D020",
}


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _normalize_visual_review(root: Path, review: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(review, dict) or set(review) != set(VISUAL_REVIEW_QUESTIONS):
        raise DesignError("Slop-check requires structured answers to every visual review question")
    normalized: dict[str, Any] = {}
    failures: list[dict[str, Any]] = []
    for question_id in VISUAL_REVIEW_QUESTIONS:
        item = review.get(question_id)
        if not isinstance(item, dict) or item.get("result") not in {"pass", "fail", "not-applicable"}:
            raise DesignError(f"Visual review {question_id} requires pass, fail, or not-applicable")
        reviewer = item.get("reviewer")
        reviewed_at = item.get("reviewed_at")
        finding = item.get("finding", "")
        rationale = item.get("rationale", "")
        if not isinstance(reviewer, str) or not reviewer.strip() or not isinstance(reviewed_at, str) or not reviewed_at.strip():
            raise DesignError(f"Visual review {question_id} requires reviewer and reviewed_at")
        if not isinstance(finding, str) or not isinstance(rationale, str):
            raise DesignError(f"Visual review {question_id} has invalid finding or rationale")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise DesignError(f"Visual review {question_id} requires hashed screenshot evidence")
        normalized_evidence: list[dict[str, Any]] = []
        for artifact in evidence:
            if not isinstance(artifact, dict):
                raise DesignError(f"Visual review {question_id} evidence must be objects")
            relative, path = _artifact_relative_path(root, artifact.get("path"))
            if path.suffix.lower() != ".png" or not path.is_file():
                raise DesignError(f"Visual review evidence must be a PNG screenshot: {relative}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if artifact.get("sha256") != actual:
                raise DesignError(f"Visual review screenshot changed: {relative}")
            width, height = _png_dimensions(path)
            region = artifact.get("region", "full-frame")
            if not isinstance(region, str) or not region.strip():
                raise DesignError(f"Visual review evidence requires a region: {relative}")
            normalized_evidence.append({"path": relative, "sha256": actual, "region": region.strip(), "width": width, "height": height})
        if item["result"] == "fail" and not finding.strip():
            raise DesignError(f"Failed visual review {question_id} requires a finding")
        if item["result"] == "not-applicable" and not rationale.strip():
            raise DesignError(f"Not-applicable visual review {question_id} requires a rationale")
        normalized[question_id] = {
            "result": item["result"], "finding": finding.strip(), "rationale": rationale.strip(),
            "reviewer": reviewer.strip(), "reviewed_at": reviewed_at.strip(), "evidence": normalized_evidence,
        }
        if item["result"] == "fail":
            first = normalized_evidence[0]
            failures.append({
                "rule_id": VISUAL_REVIEW_FAILURE_RULES[question_id],
                "location": f"{first['path']}#{first['region']}",
                "evidence": finding.strip(),
            })
    return normalized, failures


def visual_atlas(root: Path, config: dict[str, Any], catalog_path: Path, input_path: Path) -> dict[str, Any]:
    """Render a private first-party visual-language atlas without network access."""
    _enabled(config)
    request = _read_json(input_path)
    title = request.get("title", "Visual language atlas")
    if not isinstance(title, str) or not title.strip():
        raise DesignError("Visual atlas requires a title")
    project_copy = request.get("project_copy")
    if not isinstance(project_copy, str) or not project_copy.strip():
        raise DesignError("Visual atlas requires real project_copy shared across every plate")
    contrasts = request.get("contrasts", ["quiet / expressive", "dense / spacious", "flat / material"])
    if not isinstance(contrasts, list) or not 1 <= len(contrasts) <= 6 or any(not isinstance(item, str) or not item.strip() for item in contrasts):
        raise DesignError("Visual atlas contrasts must contain one to six labels")
    catalog = load_catalog(catalog_path)
    systems = [
        {"id": "editorial-asymmetry", "type": "high-contrast editorial roles", "density": "spacious", "surface": "paper-flat", "motion": "none; hierarchy carries the transition", "counter": "a centered headline over a generic card grid", "palette": ("#f2efe8", "#171918", "#a4432c")},
        {"id": "technical-index", "type": "condensed index plus neutral reading face", "density": "compact", "surface": "ruled and exact", "motion": "state-led row continuity", "counter": "terminal styling used as a shortcut for technical credibility", "palette": ("#e4e9e6", "#17211e", "#276b54")},
        {"id": "material-field", "type": "quiet grotesk with material captions", "density": "layered", "surface": "subject-led depth", "motion": "one spatial reveal with a static crop", "counter": "decorative glow pretending to be material or light", "palette": ("#ded8cc", "#231f1a", "#8d6434")},
        {"id": "cinematic-frame", "type": "display scale paired with restrained utility", "density": "episodic", "surface": "edge-to-edge image field", "motion": "chapter transition with reduced-motion stills", "counter": "autoplay spectacle without narrative purpose", "palette": ("#d9dde0", "#12171a", "#a34b3f")},
        {"id": "dense-ledger", "type": "tabular rhythm with emphatic evidence type", "density": "dense", "surface": "ledger and annotation", "motion": "no ambient motion; state changes only", "counter": "uniform rounded cards flattening every relationship", "palette": ("#edf0ec", "#18201e", "#3d6658")},
        {"id": "quiet-utility", "type": "calm humanist hierarchy", "density": "measured", "surface": "minimal utility planes", "motion": "direct state replacement", "counter": "warm cream used as unexplained sophistication", "palette": ("#eef1f2", "#1b2226", "#415f72")},
    ]
    compositions = {
        "editorial-asymmetry": '<div class="study editorial"><b>01</b><h3>{copy}</h3><i></i><p>Evidence remains attached to the claim.</p></div>',
        "technical-index": '<div class="study index-grid"><b>SYS / 02</b><ul><li>{copy}</li><li>Source</li><li>Decision</li></ul><p>STATUS — REVIEW</p></div>',
        "material-field": '<div class="study material"><div></div><h3>{copy}</h3><p>Material carries meaning before decoration.</p></div>',
        "cinematic-frame": '<div class="study cinematic"><span>CHAPTER 04</span><h3>{copy}</h3><p>Still equivalent preserves the same narrative beat.</p></div>',
        "dense-ledger": '<div class="study ledger"><b>{copy}</b><table><tr><td>Source</td><td>Observed</td></tr><tr><td>Decision</td><td>Pending</td></tr><tr><td>Risk</td><td>Bound</td></tr></table></div>',
        "quiet-utility": '<div class="study utility"><small>Primary task</small><h3>{copy}</h3><button type="button">Review evidence</button></div>',
    }
    plate_html: list[str] = []
    for index, contrast in enumerate(contrasts, 1):
        system = systems[(index - 1) % len(systems)]
        surface, ink, accent = system["palette"]
        composition = compositions[system["id"]].format(copy=html.escape(project_copy.strip()))
        plate_html.append(f"""
        <article class="plate" data-system="{system['id']}" style="--surface:{surface};--ink:{ink};--accent:{accent}">
          <div class="plate-copy"><span class="index">{index:02d}</span><h2>{html.escape(contrast)}</h2>
          <p>System: {html.escape(system['id'].replace('-', ' '))}. Compare the same project language through a different organizing idea.</p>
          <div class="type"><strong>{html.escape(system['type'])}</strong><span>{html.escape(project_copy.strip())}</span></div></div>
          {composition}
          <div class="tokens"><i style="background:var(--surface)"></i><i style="background:var(--ink)"></i><i style="background:var(--accent)"></i></div>
          <p class="counter"><b>Counterexample:</b> {html.escape(system['counter'])}.</p>
          <dl><div><dt>Density</dt><dd>{system['density']}</dd></div><div><dt>Surface</dt><dd>{system['surface']}</dd></div><div><dt>Motion</dt><dd>{system['motion']}</dd></div></dl>
        </article>""")
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{html.escape(title)}</title><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#111514;color:#edf0ea;font-family:ui-sans-serif,system-ui,sans-serif}}main{{max-width:1440px;margin:auto;padding:clamp(24px,5vw,72px)}}
    header{{display:grid;grid-template-columns:1fr 2fr;gap:32px;margin-bottom:56px}}h1{{font:600 clamp(38px,7vw,96px)/.9 ui-serif,Georgia,serif;letter-spacing:-.045em;margin:0}}header p{{max-width:58ch;margin:8px 0 0;color:#aeb8b2}}
    .grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.plate{{background:var(--surface);color:var(--ink);padding:clamp(18px,3vw,36px);display:grid;grid-template-columns:.8fr 1.2fr;gap:24px;min-height:510px}}
    .index{{font:600 11px/1 ui-monospace,monospace;letter-spacing:.18em}}h2{{font:600 clamp(28px,4vw,52px)/.94 ui-serif,Georgia,serif;letter-spacing:-.035em;margin:18px 0}}.plate p{{line-height:1.45}}.type{{border-left:3px solid var(--accent);padding:12px;margin-top:28px;display:grid;gap:6px}}.composition{{width:100%;align-self:start}}.tokens{{display:flex;gap:5px}}.tokens i{{width:34px;height:34px;border:1px solid color-mix(in srgb,var(--ink) 25%,transparent)}}.counter{{grid-column:1/-1;border-top:1px solid color-mix(in srgb,var(--ink) 25%,transparent);padding-top:14px}}dl{{grid-column:1/-1;display:flex;gap:22px;margin:0}}dl div{{display:grid;gap:3px}}dt{{font:600 10px/1 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.12em}}dd{{margin:0;font-size:13px}}
    .study{{min-height:270px;align-self:start;position:relative;overflow:hidden}}.study h3,.study p{{margin:0}}.editorial{{display:grid;grid-template-columns:48px 1fr;align-content:start;gap:18px}}.editorial h3{{font:600 44px/.88 Georgia,serif;letter-spacing:-.05em}}.editorial i{{grid-column:2;height:4px;background:var(--accent)}}.editorial p{{grid-column:2;max-width:25ch}}.index-grid{{border:1px solid var(--ink);padding:16px;font:12px/1.3 ui-monospace,monospace}}.index-grid ul{{list-style:none;padding:0;margin:36px 0;display:grid;gap:0}}.index-grid li{{padding:9px;border-top:1px solid var(--ink)}}.material{{background:var(--ink);color:var(--surface);padding:24px;display:grid;align-content:end}}.material div{{position:absolute;inset:20px 20px 42%;background:linear-gradient(135deg,var(--accent),transparent 62%)}}.material h3{{font:500 34px/.95 Georgia,serif;z-index:1}}.material p{{z-index:1}}.cinematic{{background:linear-gradient(155deg,var(--ink) 0 48%,var(--accent) 48% 52%,#6d7475 52%);color:var(--surface);padding:22px;display:flex;flex-direction:column;justify-content:space-between}}.cinematic h3{{font:600 42px/.9 Georgia,serif;max-width:11ch}}.ledger{{font:12px ui-monospace,monospace}}.ledger>b{{display:block;font:600 30px/.95 Georgia,serif;margin-bottom:28px}}.ledger table{{border-collapse:collapse;width:100%}}.ledger td{{border:1px solid var(--ink);padding:12px}}.utility{{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:36px;border-left:1px solid var(--ink)}}.utility h3{{font:500 36px/1.05 system-ui,sans-serif;max-width:14ch;margin:12px 0 34px}}.utility button{{border:0;background:var(--ink);color:var(--surface);padding:12px 18px}}
    @media(max-width:760px){{header,.grid,.plate{{grid-template-columns:1fr}}.plate{{min-height:0}}dl{{flex-wrap:wrap}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
    </style></head><body><main><header><h1>{html.escape(title)}</h1><p>React to numbered contrasts. Each plate demonstrates type, palette, composition, density, surface, motion intent, and an explicit counterexample. Catalog {html.escape(catalog['catalog_version'])}.</p></header><section class="grid">{''.join(plate_html)}</section></main></body></html>"""
    request_hash = _canonical_hash({"request": request, "catalog_version": catalog["catalog_version"]})
    relative = Path(config.get("private_dir", ".continuity/private")) / "design" / "visual-atlas" / f"{request_hash}.html"
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return {"schema_version": 1, "private": True, "network_used": False, "path": relative.as_posix(), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "plate_count": len(contrasts), "catalog_version": catalog["catalog_version"], "required_snapshot_viewports": ["mobile", "tablet", "desktop"]}


def visual_render(root: Path, config: dict[str, Any], input_path: Path) -> dict[str, Any]:
    """Render private moodboard, concept-comparison, or visual-delta evidence."""
    _enabled(config)
    request = _read_json(input_path)
    kind = request.get("kind")
    if kind not in {"moodboard", "concept-comparison", "visual-delta"}:
        raise DesignError("Visual render kind must be moodboard, concept-comparison, or visual-delta")
    title = request.get("title")
    items = request.get("items")
    if not isinstance(title, str) or not title.strip() or not isinstance(items, list) or not items or len(items) > 20:
        raise DesignError("Visual render requires a title and one to twenty items")
    cards: list[str] = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict) or not isinstance(item.get("title"), str) or not item["title"].strip():
            raise DesignError("Each visual render item requires a title")
        def image_markup(field: str, label: str) -> str:
            relative, path = _artifact_relative_path(root, item.get(field))
            if not path.is_file():
                raise DesignError(f"Visual render image is missing: {relative}")
            if path.suffix.lower() not in {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}:
                raise DesignError(f"Visual render {field} must be an image")
            if path.suffix.lower() == ".png":
                _png_dimensions(path)
            alt_text = html.escape(str(item.get(f"{field}_alt", item.get("alt", f"{item['title']} — {label}"))))
            return f'<figure><img src="{html.escape(path.as_uri())}" alt="{alt_text}"><figcaption>{html.escape(label)}</figcaption></figure>'
        if kind == "moodboard":
            visuals = image_markup("image_path", "Reference capture")
        elif kind == "concept-comparison":
            visuals = image_markup("wide_image_path", "Wide composition") + image_markup("narrow_image_path", "Narrow transformation")
        else:
            visuals = image_markup("before_image_path", "Before") + image_markup("after_image_path", "After")
        summary = html.escape(str(item.get("summary", "")))
        lesson = html.escape(str(item.get("lesson", "")))
        source = html.escape(str(item.get("source", "")))
        label = html.escape(str(item.get("number", index)))
        cards.append(f'<article><div class="visual">{visuals}</div><div class="copy"><span>{label}</span><h2>{html.escape(item["title"])}</h2><p>{summary}</p><p class="lesson">{lesson}</p><small>{source}</small></div></article>')
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#f3f3f0;color:#171917;font-family:ui-sans-serif,system-ui,sans-serif}}main{{max-width:1600px;margin:auto;padding:clamp(20px,4vw,64px)}}header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:38px;border-bottom:1px solid #252925;padding-bottom:20px}}h1{{font:600 clamp(34px,6vw,76px)/.94 system-ui,sans-serif;letter-spacing:-.04em;margin:0}}header p{{max-width:48ch;color:#525a53}}section{{display:grid;gap:32px}}article{{background:#fff;color:#18201e;display:grid;grid-template-columns:minmax(0,2fr) minmax(260px,.7fr);border-top:4px solid #18201e}}.visual{{min-height:320px;background:#d9ded9;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));overflow:hidden}}figure{{margin:0;position:relative;min-height:280px;background:#d9ded9}}img{{width:100%;height:100%;position:absolute;inset:0;object-fit:contain}}figcaption{{position:absolute;left:10px;bottom:10px;background:#111;color:#fff;padding:5px 7px;font-size:11px}}.copy{{padding:24px;display:flex;flex-direction:column}}.copy>span{{font:700 11px ui-monospace,monospace;letter-spacing:.16em}}h2{{font:600 clamp(24px,3vw,40px)/.98 system-ui,sans-serif;margin:18px 0}}p{{line-height:1.45}}.lesson{{border-top:1px solid #9ea7a1;padding-top:12px}}small{{margin-top:auto;color:#5c6862;word-break:break-word}}@media(max-width:820px){{header,article{{display:grid;grid-template-columns:1fr}}.visual{{grid-template-columns:1fr}}figure{{min-height:240px}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}</style></head><body><main><header><h1>{html.escape(title)}</h1><p>{html.escape(kind.replace('-', ' ').title())}. Neutral comparison chrome keeps the project visuals—not Continuity styling—in control.</p></header><section>{''.join(cards)}</section></main></body></html>'''
    request_hash = _canonical_hash(request)
    relative = Path(config.get("private_dir", ".continuity/private")) / "design" / "visual-renders" / kind / f"{request_hash}.html"
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return {"schema_version": 1, "kind": kind, "private": True, "network_used": False, "path": relative.as_posix(), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "item_count": len(items), "required_snapshot_viewports": ["mobile", "tablet", "desktop"]}


def slop_check(root: Path, config: dict[str, Any], target_path: Path, manifest_path: Path) -> dict[str, Any]:
    _enabled(config)
    resolved_root = root.resolve()
    resolved_target = target_path.resolve()
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as exc:
        raise DesignError("Slop-check target must remain inside the project root") from exc
    manifest = _read_json(manifest_path)
    if manifest.get("ruleset_version", design_slop.RULESET_VERSION) != design_slop.RULESET_VERSION:
        raise DesignError("Slop-check manifest ruleset version is stale")
    stage = manifest.get("stage")
    if stage not in {"concept", "prototype", "implementation"}:
        raise DesignError("Slop-check manifest requires concept, prototype, or implementation stage")
    design_id = manifest.get("design_id")
    if isinstance(design_id, str) and design_id.strip():
        draft_path = root / config.get("private_dir", ".continuity/private") / "design" / _identifier(design_id, "design ID") / "draft.json"
        if draft_path.is_file() and _read_json(draft_path).get("workflow_version", 1) >= 3:
            fidelity = manifest.get("translation_fidelity")
            required_fidelity = {"editable_depth_preserved", "font_transfer_verified", "approved_layer_plan_present", "approved_typographic_character_present"}
            if not isinstance(fidelity, dict) or any(fidelity.get(key) is not True for key in required_fidelity):
                raise DesignError("Workflow version 3 slop checks require passed editable-depth, font-transfer, layer-plan, and typographic-character evidence")
    review, review_failures = _normalize_visual_review(root, manifest.get("visual_review"))
    manifest["visual_review"] = review
    if review_failures:
        visual_findings = manifest.get("visual_findings", [])
        if not isinstance(visual_findings, list):
            raise DesignError("visual_findings must be an array")
        manifest["visual_findings"] = [*visual_findings, *review_failures]
    if "craft_findings" in manifest and "dispositions" not in manifest:
        dispositions: list[dict[str, Any]] = []
        for item in manifest["craft_findings"]:
            if not isinstance(item, dict):
                raise DesignError("Slop craft findings must be objects")
            dispositions.append({
                "rule_id": item.get("rule_id"), "status": item.get("status"),
                "rationale": item.get("override_rationale", item.get("response", "")),
                "contract_reference": item.get("contract_reference", item.get("artifact_ref", "")),
                "evidence": item.get("evidence", ""),
            })
        manifest["dispositions"] = dispositions
    try:
        report = design_slop.inspect(resolved_target, resolved_root, manifest)
    except (OSError, ValueError) as exc:
        raise DesignError(str(exc)) from exc
    report.update({
        "stage": stage,
        "design_id": manifest.get("design_id"),
        "revision": manifest.get("revision"),
        "design_hash": manifest.get("design_hash"),
        "approval_bundle_hash": manifest.get("approval_bundle_hash"),
        "visual_review_questions": VISUAL_REVIEW_QUESTIONS,
        "checked_at": _now(),
    })
    report.pop("report_hash", None)
    report["report_hash"] = _canonical_hash(report)
    relative = Path(config.get("private_dir", ".continuity/private")) / "design" / "slop" / f"{report['report_hash']}.json"
    _write_json(root / relative, report)
    return {**report, "report_path": relative.as_posix()}


def _verified_private_report(root: Path, value: Any, *, stage: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError("Concept direction requires a slop report reference")
    relative, path = _artifact_relative_path(root, value.get("path"))
    if not path.is_file():
        raise DesignError("Concept slop report is missing")
    report = _read_json(path)
    actual = _canonical_hash({key: item for key, item in report.items() if key != "report_hash"})
    if value.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest() or report.get("report_hash") != actual:
        raise DesignError("Concept slop report hash is invalid")
    if (
        report.get("stage") != stage
        or report.get("status") != "passed"
        or report.get("ruleset_version") != design_slop.RULESET_VERSION
        or report.get("ruleset_hash") != design_slop.ruleset_hash()
    ):
        raise DesignError("Concept slop report is stale or did not pass")
    dispositions_hash = _canonical_hash(report.get("dispositions", []))
    expected_manifest = {
        "report_hash": report["report_hash"], "ruleset_version": report["ruleset_version"],
        "counts_by_severity": report.get("counts_by_severity", {}), "dispositions_hash": dispositions_hash,
        "status": report["status"],
    }
    if any(value.get(key) != expected for key, expected in expected_manifest.items()):
        raise DesignError("Slop report manifest summary does not match the bound report")
    return {"path": relative, "sha256": value["sha256"], **expected_manifest}


def _verified_browser_probe(root: Path, value: Any, viewport: str, screenshot_width: int) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("viewport") != viewport:
        raise DesignError("Browser probe viewport does not match its screenshot")
    relative, path = _artifact_relative_path(root, value.get("path"))
    if not path.is_file() or path.suffix.lower() != ".json":
        raise DesignError(f"Browser probe evidence is missing: {relative}")
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if value.get("sha256") != actual_hash:
        raise DesignError(f"Browser probe evidence changed: {relative}")
    probe = _read_json(path)
    probe_viewport = probe.get("viewport")
    findings = probe.get("craft_findings")
    if (
        probe.get("schema_version") not in {2, 3}
        or probe.get("passed") is not True
        or not isinstance(probe_viewport, dict)
        or probe_viewport.get("width") != screenshot_width
        or probe.get("horizontal_overflow") is not False
        or probe.get("sticky_or_fixed_obstructions") != []
        or not isinstance(findings, list)
        or any(isinstance(item, dict) and item.get("severity") in {"error", "critical"} for item in findings)
    ):
        raise DesignError(f"Browser probe did not supply passing machine evidence: {relative}")
    return {"viewport": viewport, "path": relative, "sha256": actual_hash, "schema_version": probe["schema_version"], "status": "passed"}


def _verified_reference_file(root: Path, value: Any, label: str, suffixes: set[str]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise DesignError(f"{label} requires hash-bound file evidence")
    relative, path = _artifact_relative_path(root, value.get("path"))
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
    if path.suffix.lower() not in suffixes or not actual or value.get("sha256") != actual:
        raise DesignError(f"{label} is missing or changed: {relative}")
    return {"path": relative, "sha256": actual}


def _png_alpha_stats(path: Path) -> dict[str, int | bool]:
    """Return deterministic alpha evidence for an 8-bit, non-interlaced RGBA PNG."""
    data = path.read_bytes()
    if len(data) < 45 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise DesignError(f"Invalid PNG artifact: {path}")
    offset = 8
    width = height = 0
    bit_depth = color_type = interlace = -1
    compressed = bytearray()
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        start = offset + 8
        end = start + length
        crc_end = end + 4
        if crc_end > len(data) or zlib.crc32(kind + data[start:end]) & 0xFFFFFFFF != struct.unpack(">I", data[end:crc_end])[0]:
            raise DesignError(f"Invalid PNG chunk: {path}")
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", data[start:end])
        elif kind == b"IDAT":
            compressed.extend(data[start:end])
        elif kind == b"IEND":
            break
        offset = crc_end
    if bit_depth != 8 or color_type != 6 or interlace != 0 or width < 1 or height < 1:
        raise DesignError(f"Foreground plane must be an 8-bit non-interlaced RGBA PNG: {path}")
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise DesignError(f"Invalid PNG image data: {path}") from exc
    stride = width * 4
    if len(raw) != height * (stride + 1):
        raise DesignError(f"Unexpected PNG scanline data: {path}")
    rows: list[bytearray] = []
    cursor = 0
    previous = bytearray(stride)
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor:cursor + stride]
        cursor += stride
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - 4] if index >= 4 else 0
            up = previous[index]
            up_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                p = left + up - up_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                predictor = left if pa <= pb and pa <= pc else up if pb <= pc else up_left
            else:
                raise DesignError(f"Unsupported PNG filter: {path}")
            row[index] = (value + predictor) & 0xFF
        rows.append(row)
        previous = row
    alphas = [row[index] for row in rows for index in range(3, stride, 4)]
    corner_alphas = (rows[0][3], rows[0][stride - 1], rows[-1][3], rows[-1][stride - 1])
    return {
        "width": width, "height": height,
        "transparent_pixels": sum(alpha == 0 for alpha in alphas),
        "partial_pixels": sum(0 < alpha < 255 for alpha in alphas),
        "opaque_pixels": sum(alpha == 255 for alpha in alphas),
        "transparent_corners": sum(alpha == 0 for alpha in corner_alphas),
    }


def _validate_typographic_transfer(root: Path, concept_id: str, value: Any, prototype_source: str, expected_reference_probe: Any = None, expected_target_document: Any = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError(f"Concept {concept_id} requires executable typographic transfer evidence")
    transfer_id = _identifier(str(value.get("transfer_id", "")), "typographic transfer ID")
    required_text = ("rendered_copy", "font_family", "source", "license_evidence", "source_character", "project_transformation", "narrow_behavior")
    if any(not isinstance(value.get(field), str) or not value[field].strip() for field in required_text):
        raise DesignError(f"Concept {concept_id} typographic transfer lacks source, license, character, transformation, or responsive evidence")
    relation = value.get("type_media_relation")
    if relation not in {"separate", "behind-subject", "interleaved", "foreground-over-type"}:
        raise DesignError(f"Concept {concept_id} requires a supported type-to-media relation")
    reference_probe_ref = _verified_reference_file(root, value.get("reference_render_probe"), f"Concept {concept_id} reference typography browser probe", {".json"})
    if expected_reference_probe is not None and reference_probe_ref != expected_reference_probe:
        raise DesignError(f"Concept {concept_id} reference typography probe is not bound to its validated reference study")
    _, reference_probe_path = _artifact_relative_path(root, reference_probe_ref["path"])
    reference_probe = _read_json(reference_probe_path)
    probe_ref = _verified_reference_file(root, value.get("render_probe"), f"Concept {concept_id} typography render probe", {".json"})
    _, probe_path = _artifact_relative_path(root, probe_ref["path"])
    probe = _read_json(probe_path)
    if expected_target_document is not None and (
        not isinstance(expected_target_document, dict)
        or not isinstance(expected_target_document.get("source_bundle_sha256"), str)
        or len(expected_target_document["source_bundle_sha256"]) != 64
        or probe.get("target_document_path") != expected_target_document.get("path")
        or probe.get("target_document_sha256") != expected_target_document.get("sha256")
        or probe.get("source_bundle_sha256") != expected_target_document.get("source_bundle_sha256")
        or not isinstance(probe.get("document_url"), str)
        or not probe["document_url"].split("?", 1)[0].endswith(expected_target_document.get("path", ""))
    ):
        raise DesignError(f"Concept {concept_id} typography browser probe is stale for its target document")
    transfers = probe.get("typography_transfers")
    if not isinstance(transfers, list):
        raise DesignError(f"Concept {concept_id} typography evidence must come from the rendered browser probe")
    matching = [item for item in transfers if isinstance(item, dict) and item.get("transfer_id") == transfer_id]
    if len(matching) != 1:
        raise DesignError(f"Concept {concept_id} rendered browser probe must locate typographic transfer {transfer_id} exactly once")
    rendered = matching[0]
    metrics = {key: rendered.get(key) for key in ("cap_height_ratio", "word_width_ratio", "line_count")}
    reference_transfers = reference_probe.get("typography_transfers")
    reference_matching = [item for item in reference_transfers if isinstance(item, dict) and item.get("transfer_id") == transfer_id] if isinstance(reference_transfers, list) else []
    reference_rendered = reference_matching[0] if len(reference_matching) == 1 else {}
    reference_metrics = {key: reference_rendered.get(key) for key in ("cap_height_ratio", "word_width_ratio", "line_count")}
    tolerances = value.get("metric_tolerances")
    computed_families = {
        item.strip().strip("'\"").casefold()
        for item in str(rendered.get("computed_family", "")).split(",") if item.strip()
    }
    if (
        probe.get("schema_version") != 3 or probe.get("probe_kind") != "continuity-artifact-browser-probe"
        or probe.get("passed") is not True or probe.get("document_fonts_status") != "loaded"
        or not isinstance(probe.get("viewport"), dict) or probe["viewport"].get("width") != 1440
        or reference_probe.get("schema_version") != 3 or reference_probe.get("probe_kind") != "continuity-artifact-browser-probe"
        or reference_probe.get("passed") is not True or len(reference_matching) != 1
        or value["font_family"].casefold() not in computed_families
        or rendered.get("font_loaded") is not True
        or rendered.get("font_face_status") != "loaded"
        or rendered.get("rendered_copy") != value["rendered_copy"]
        or not isinstance(metrics, dict)
        or any(not isinstance(metrics.get(key), (int, float)) or metrics[key] <= 0 for key in ("cap_height_ratio", "word_width_ratio", "line_count"))
        or not isinstance(reference_metrics, dict)
        or any(not isinstance(reference_metrics.get(key), (int, float)) or reference_metrics[key] <= 0 for key in ("cap_height_ratio", "word_width_ratio", "line_count"))
        or not isinstance(tolerances, dict)
        or not isinstance(tolerances.get("cap_height_ratio"), (int, float)) or not 0 < tolerances["cap_height_ratio"] <= 0.08
        or not isinstance(tolerances.get("word_width_ratio"), (int, float)) or not 0 < tolerances["word_width_ratio"] <= 0.10
        or abs(metrics["cap_height_ratio"] - reference_metrics["cap_height_ratio"]) > tolerances["cap_height_ratio"]
        or abs(metrics["word_width_ratio"] - reference_metrics["word_width_ratio"]) > tolerances["word_width_ratio"]
        or metrics["line_count"] != reference_metrics["line_count"]
    ):
        raise DesignError(f"Concept {concept_id} typography render probe does not prove the declared face and rendered silhouette")
    return {field: value[field].strip() for field in required_text} | {
        "transfer_id": transfer_id, "type_media_relation": relation, "reference_render_probe": reference_probe_ref, "render_probe": probe_ref,
        "metric_tolerances": {key: tolerances[key] for key in ("cap_height_ratio", "word_width_ratio")},
        "metrics": {key: metrics[key] for key in ("cap_height_ratio", "word_width_ratio", "line_count")},
        "reference_metrics": {key: reference_metrics[key] for key in ("cap_height_ratio", "word_width_ratio", "line_count")},
        "tolerances": {key: tolerances[key] for key in ("cap_height_ratio", "word_width_ratio")},
    }


def _validate_composition_asset_plan(root: Path, concept_id: str, value: Any, prototype_source: str, type_media_relation: str, render_probe: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError(f"Concept {concept_id} requires an executable composition asset plan")
    plan_id = _identifier(str(value.get("plan_id", "")), "composition asset plan ID")
    if value.get("type_media_relation") != type_media_relation:
        raise DesignError(f"Concept {concept_id} composition and typography must agree on their type-to-media relation")
    registration_basis = value.get("registration_basis")
    if not isinstance(registration_basis, str) or not registration_basis.strip():
        raise DesignError(f"Concept {concept_id} composition asset plan requires a registration basis")
    planes = value.get("planes")
    if not isinstance(planes, list) or len(planes) < 2:
        raise DesignError(f"Concept {concept_id} composition asset plan requires at least two editable planes")
    normalized: list[dict[str, Any]] = []
    probe_ref = _verified_reference_file(root, render_probe, f"Concept {concept_id} composition browser probe", {".json"})
    _, probe_path = _artifact_relative_path(root, probe_ref["path"])
    probe = _read_json(probe_path)
    rendered_planes = probe.get("composition_planes")
    if probe.get("schema_version") != 3 or probe.get("probe_kind") != "continuity-artifact-browser-probe" or probe.get("passed") is not True or not isinstance(rendered_planes, list):
        raise DesignError(f"Concept {concept_id} composition evidence must come from a passed rendered browser probe")
    ids: set[str] = set()
    z_indexes: set[int] = set()
    roles: dict[str, dict[str, Any]] = {}
    for plane in planes:
        if not isinstance(plane, dict):
            raise DesignError(f"Concept {concept_id} composition planes must be objects")
        plane_id = _identifier(str(plane.get("plane_id", "")), "composition plane ID")
        role = plane.get("role")
        source_kind = plane.get("source_kind")
        z_index = plane.get("z_index")
        if plane_id in ids or role not in {"background", "midground", "live-type", "foreground", "annotation"} or source_kind not in {"raster", "live-html", "svg", "video"} or not isinstance(z_index, int) or z_index in z_indexes:
            raise DesignError(f"Concept {concept_id} composition planes require unique IDs, z-indexes, and supported roles")
        for field in ("crop_anchor", "responsive_behavior"):
            if not isinstance(plane.get(field), str) or not plane[field].strip():
                raise DesignError(f"Concept {concept_id} plane {plane_id} requires crop and responsive behavior")
        item: dict[str, Any] = {"plane_id": plane_id, "role": role, "source_kind": source_kind, "z_index": z_index, "crop_anchor": plane["crop_anchor"].strip(), "responsive_behavior": plane["responsive_behavior"].strip()}
        rendered_matches = [entry for entry in rendered_planes if isinstance(entry, dict) and entry.get("plane_id") == plane_id]
        if len(rendered_matches) != 1 or rendered_matches[0].get("visible") is not True or rendered_matches[0].get("computed_z_index") != z_index:
            raise DesignError(f"Concept {concept_id} browser probe does not render plane {plane_id} once at its declared z-index")
        rendered_plane = rendered_matches[0]
        if source_kind == "live-html":
            selector = plane.get("selector")
            if not isinstance(selector, str) or not selector.strip() or rendered_plane.get("selector") != selector.strip():
                raise DesignError(f"Concept {concept_id} live plane {plane_id} is not consumed by the prototype")
            item["selector"] = selector.strip()
        else:
            asset = _verified_reference_file(root, plane.get("asset"), f"Concept {concept_id} plane {plane_id}", {".png", ".svg", ".webp", ".jpg", ".jpeg", ".mp4", ".webm"})
            asset_url = rendered_plane.get("asset_url")
            if not isinstance(asset_url, str) or not asset_url.split("?", 1)[0].endswith(asset["path"]) or rendered_plane.get("load_complete") is not True:
                raise DesignError(f"Concept {concept_id} prototype does not consume plane asset {asset['path']}")
            item["asset"] = asset
            if Path(asset["path"]).suffix.lower() == ".png":
                _, asset_path = _artifact_relative_path(root, asset["path"])
                item["dimensions"] = dict(zip(("width", "height"), _png_dimensions(asset_path)))
                if role == "foreground":
                    alpha = _png_alpha_stats(asset_path)
                    if alpha["transparent_pixels"] == 0 or alpha["opaque_pixels"] == 0 or alpha["transparent_corners"] < 4:
                        raise DesignError(f"Concept {concept_id} foreground plane {plane_id} must contain usable alpha with four transparent corners")
                    item["alpha"] = alpha
        ids.add(plane_id)
        z_indexes.add(z_index)
        if role in {"background", "live-type", "foreground"} and role in roles:
            raise DesignError(f"Concept {concept_id} composition asset plan can declare only one {role} plane")
        roles[role] = item
        normalized.append(item)
    if type_media_relation in {"behind-subject", "interleaved", "foreground-over-type"}:
        if not {"background", "live-type", "foreground"} <= set(roles):
            raise DesignError(f"Concept {concept_id} layered type-to-media relation requires background, live-type, and alpha foreground planes")
        if not roles["background"].get("dimensions") or not roles["foreground"].get("dimensions") or roles["background"]["dimensions"] != roles["foreground"]["dimensions"]:
            raise DesignError(f"Concept {concept_id} background and foreground planes must share exact crop registration")
        if Path(roles["background"]["asset"]["path"]).suffix.lower() != ".png" or Path(roles["foreground"]["asset"]["path"]).suffix.lower() != ".png":
            raise DesignError(f"Concept {concept_id} registered layered planes must use PNG assets")
        if roles["background"]["crop_anchor"] != roles["foreground"]["crop_anchor"]:
            raise DesignError(f"Concept {concept_id} background and foreground planes must share the same crop anchor")
        if not roles["background"]["z_index"] < roles["live-type"]["z_index"] < roles["foreground"]["z_index"]:
            raise DesignError(f"Concept {concept_id} declared type-to-media depth is not reflected in plane order")
        if roles["background"]["asset"]["sha256"] == roles["foreground"]["asset"]["sha256"]:
            raise DesignError(f"Concept {concept_id} background and foreground must be independently editable assets")
        rendered_by_id = {item["plane_id"]: item for item in rendered_planes if isinstance(item, dict) and item.get("plane_id")}
        background_rect = rendered_by_id[roles["background"]["plane_id"]].get("rect")
        type_rect = rendered_by_id[roles["live-type"]["plane_id"]].get("rect")
        foreground_rect = rendered_by_id[roles["foreground"]["plane_id"]].get("rect")
        if not all(isinstance(rect, dict) and all(isinstance(rect.get(key), (int, float)) for key in ("x", "y", "width", "height")) for rect in (background_rect, type_rect, foreground_rect)):
            raise DesignError(f"Concept {concept_id} browser probe lacks rendered plane geometry")
        if any(abs(background_rect[key] - foreground_rect[key]) > 1 for key in ("x", "y", "width", "height")):
            raise DesignError(f"Concept {concept_id} background and foreground planes are not registered in rendered geometry")
        overlap_width = min(type_rect["x"] + type_rect["width"], foreground_rect["x"] + foreground_rect["width"]) - max(type_rect["x"], foreground_rect["x"])
        overlap_height = min(type_rect["y"] + type_rect["height"], foreground_rect["y"] + foreground_rect["height"]) - max(type_rect["y"], foreground_rect["y"])
        if overlap_width <= 0 or overlap_height <= 0:
            raise DesignError(f"Concept {concept_id} foreground plane does not visibly intersect the live type region")
    return {"plan_id": plan_id, "type_media_relation": type_media_relation, "registration_basis": registration_basis.strip(), "planes": normalized}


def _verified_reference_visual(root: Path, value: Any, label: str, role: str) -> dict[str, Any]:
    result = _verified_reference_file(root, value, label, {".png"})
    _, path = _artifact_relative_path(root, result["path"])
    width, height = _png_dimensions(path)
    if height < 1 or (role == "wide" and width < 1100) or (role == "narrow" and width >= 600):
        raise DesignError(f"{label} has the wrong viewport role: {result['path']}")
    return {**result, "width": width, "height": height}


def portfolio_validate(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    """Validate private prior-output fingerprints used to resist Continuity house-style convergence."""
    _enabled(config)
    manifest = _read_json(manifest_path)
    if manifest.get("schema_version") != 1 or manifest.get("status") != "passed":
        raise DesignError("Design portfolio review requires schema_version 1 with passed status")
    for field in ("portfolio_id", "reviewer", "reviewed_at", "conclusion"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise DesignError(f"Design portfolio review requires {field}")
    generations = manifest.get("generations")
    if not isinstance(generations, list) or len(generations) > 20:
        raise DesignError("Design portfolio review requires zero to twenty prior generations")
    normalized_generations: list[dict[str, Any]] = []
    generation_ids: set[str] = set()
    artifact_hashes: set[str] = set()
    for item in generations:
        if not isinstance(item, dict):
            raise DesignError("Portfolio generations must be objects")
        generation_id = _identifier(str(item.get("generation_id", "")), "portfolio generation ID")
        if generation_id in generation_ids:
            raise DesignError("Portfolio generation IDs must be unique")
        for field in ("reference_identity", "concept_name"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise DesignError(f"Portfolio generation {generation_id} requires {field}")
        impact = item.get("impact_score")
        if not isinstance(impact, (int, float)) or not 0 <= impact <= 5:
            raise DesignError(f"Portfolio generation {generation_id} impact_score must be between zero and five")
        artifact = _verified_reference_visual(root, item.get("artifact"), f"Portfolio generation {generation_id}", "wide")
        if artifact["sha256"] in artifact_hashes:
            raise DesignError("Portfolio generations require distinct visual evidence")
        fingerprint = item.get("fingerprint")
        if not isinstance(fingerprint, dict) or set(fingerprint) != PORTFOLIO_FINGERPRINT_DIMENSIONS:
            raise DesignError(f"Portfolio generation {generation_id} requires every fingerprint dimension")
        if any(not isinstance(value, str) or not value.strip() for value in fingerprint.values()):
            raise DesignError(f"Portfolio generation {generation_id} fingerprint values must be non-empty")
        normalized_generations.append({
            "generation_id": generation_id,
            "reference_identity": item["reference_identity"].strip(),
            "concept_name": item["concept_name"].strip(),
            "impact_score": float(impact),
            "artifact": artifact,
            "fingerprint": {key: fingerprint[key].strip() for key in sorted(PORTFOLIO_FINGERPRINT_DIMENSIONS)},
        })
        generation_ids.add(generation_id)
        artifact_hashes.add(artifact["sha256"])
    audit_window = manifest.get("audit_window")
    if not isinstance(audit_window, dict) or set(audit_window) != {"first_generation_index", "last_generation_index", "runs_since_last_audit"}:
        raise DesignError("Design portfolio review requires an exact audit_window")
    if any(not isinstance(audit_window.get(key), int) or audit_window[key] < 0 for key in audit_window):
        raise DesignError("Design portfolio audit-window values must be non-negative integers")
    if generations and (
        audit_window["first_generation_index"] < 1
        or audit_window["last_generation_index"] < audit_window["first_generation_index"]
        or audit_window["runs_since_last_audit"] < 1
        or audit_window["runs_since_last_audit"] > 4
    ):
        raise DesignError("Portfolio reviews must run at least every four generations")
    recurring = manifest.get("recurring_tells")
    if not isinstance(recurring, list):
        raise DesignError("Design portfolio review recurring_tells must be an array")
    if len(generations) >= 3 and not recurring:
        raise DesignError("Portfolios with three or more generations must identify recurring house tells")
    normalized_tells: list[dict[str, Any]] = []
    tell_ids: set[str] = set()
    for item in recurring:
        if not isinstance(item, dict):
            raise DesignError("Recurring house tells must be objects")
        tell_id = _identifier(str(item.get("tell_id", "")), "house tell ID")
        dimension = item.get("dimension")
        members = item.get("generation_ids")
        if tell_id in tell_ids or dimension not in PORTFOLIO_FINGERPRINT_DIMENSIONS:
            raise DesignError("Recurring house tells require unique IDs and supported dimensions")
        if not isinstance(members, list) or len(set(members)) < 2 or not set(members) <= generation_ids:
            raise DesignError(f"House tell {tell_id} must cite at least two known prior generations")
        for field in ("value", "description", "default_response"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise DesignError(f"House tell {tell_id} requires {field}")
        if any(next(entry for entry in normalized_generations if entry["generation_id"] == member)["fingerprint"][dimension] != item["value"] for member in members):
            raise DesignError(f"House tell {tell_id} does not match the cited generation fingerprints")
        normalized_tells.append({
            "tell_id": tell_id, "dimension": dimension, "value": item["value"].strip(),
            "description": item["description"].strip(), "generation_ids": members,
            "default_response": item["default_response"].strip(),
        })
        tell_ids.add(tell_id)
    strongest = manifest.get("strongest_prior_generation_id")
    if normalized_generations:
        if strongest not in generation_ids:
            raise DesignError("Design portfolio review must identify the strongest prior generation")
        strongest_score = next(item["impact_score"] for item in normalized_generations if item["generation_id"] == strongest)
        if strongest_score != max(item["impact_score"] for item in normalized_generations):
            raise DesignError("The strongest prior generation must have the portfolio's highest impact score")
    elif strongest is not None:
        raise DesignError("An empty portfolio cannot claim a strongest prior generation")
    normalized = {
        "schema_version": 1, "status": "passed", "portfolio_id": manifest["portfolio_id"].strip(),
        "reviewer": manifest["reviewer"].strip(), "reviewed_at": manifest["reviewed_at"].strip(),
        "conclusion": manifest["conclusion"].strip(), "audit_window": audit_window,
        "generations": normalized_generations, "recurring_tells": normalized_tells,
        "strongest_prior_generation_id": strongest, "validated_at": _now(),
    }
    normalized["report_hash"] = _canonical_hash(normalized)
    relative = Path(config.get("private_dir", ".continuity/private")) / "design" / "portfolio" / f"{normalized['report_hash']}.json"
    _write_json(root / relative, normalized)
    return {
        "schema_version": 1, "status": "passed", "portfolio_id": normalized["portfolio_id"],
        "generation_count": len(normalized_generations), "recurring_tell_count": len(normalized_tells),
        "strongest_prior_generation_id": strongest, "portfolio_report_hash": normalized["report_hash"],
        "report_path": relative.as_posix(), "execution_authorized": False,
    }


def _verified_portfolio_report(root: Path, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignError("Concept evidence requires a portfolio report reference")
    relative, path = _artifact_relative_path(root, value.get("path"))
    if not path.is_file():
        raise DesignError("Concept portfolio report is missing")
    report = _read_json(path)
    actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    actual_hash = _canonical_hash({key: item for key, item in report.items() if key != "report_hash"})
    if (
        value.get("sha256") != actual_sha
        or value.get("report_hash") != report.get("report_hash")
        or report.get("report_hash") != actual_hash
        or report.get("status") != "passed"
    ):
        raise DesignError("Concept portfolio report is stale or invalid")
    return {"path": relative, "sha256": actual_sha, "report_hash": actual_hash, "report": report}


def reference_validate(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    """Validate a precision-first reconstruction and controlled project adaptation ladder."""
    _enabled(config)
    manifest = _read_json(manifest_path)
    if manifest.get("schema_version") != 2 or manifest.get("status") != "passed":
        raise DesignError("Reference translation requires precision schema_version 2 with passed status")
    design_id = _identifier(str(manifest.get("design_id", "")), "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    record = _read_json(design_dir / "draft.json")
    if record.get("workflow_version", 1) < 3:
        raise DesignError("Reference reconstruction requires workflow_version 3")
    if manifest.get("revision") != record.get("revision"):
        raise DesignError("Reference translation revision does not match the current draft")
    for field in ("prepared_by", "reviewer", "reviewed_at", "set_conclusion"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise DesignError(f"Reference translation requires {field}")
    if manifest["prepared_by"].strip().casefold() == manifest["reviewer"].strip().casefold():
        raise DesignError("Reference translation requires an independent reviewer distinct from its preparer")
    if manifest.get("reviewer_type") not in IMPACT_REVIEWER_TYPES:
        raise DesignError("Reference translation requires a human or agent-multimodal reviewer")

    research_tiles = {item["tile"] for item in record.get("research", {}).get("moodboard", []) if isinstance(item, dict) and isinstance(item.get("tile"), int)}
    studies = manifest.get("reference_studies")
    if not isinstance(studies, list) or not 1 <= len(studies) <= 3:
        raise DesignError("Reference translation requires one to three reconstructed reference studies")
    normalized_studies: list[dict[str, Any]] = []
    study_ids: set[str] = set()
    constraint_by_id: dict[str, str] = {}
    reconstruction_visual_hashes: set[str] = set()
    for study in studies:
        if not isinstance(study, dict):
            raise DesignError("Reference studies must be objects")
        study_id = _identifier(str(study.get("study_id", "")), "reference study ID")
        if study_id in study_ids:
            raise DesignError("Reference study IDs must be unique")
        tile_ids = study.get("source_tile_ids", [])
        if not isinstance(tile_ids, list) or len(set(tile_ids)) != len(tile_ids) or any(not isinstance(item, int) or item < 1 for item in tile_ids):
            raise DesignError(f"Reference study {study_id} source_tile_ids must be unique positive integers")
        if research_tiles and (not tile_ids or not set(tile_ids) <= research_tiles):
            raise DesignError(f"Reference study {study_id} must link to known moodboard tiles")
        source_identity = study.get("source_identity")
        if not isinstance(source_identity, str) or not source_identity.strip():
            raise DesignError(f"Reference study {study_id} requires one named source identity")
        source_evidence = study.get("source_evidence")
        if not isinstance(source_evidence, list) or len(source_evidence) != 2:
            raise DesignError(f"Reference study {study_id} requires exact wide and narrow captures of one source identity")
        normalized_sources: list[dict[str, Any]] = []
        source_roles: set[str] = set()
        source_ids: set[str] = set()
        for source in source_evidence:
            if not isinstance(source, dict) or source.get("ownership") not in VISUAL_REFERENCE_OWNERSHIP:
                raise DesignError(f"Reference study {study_id} source evidence requires ownership")
            role = source.get("viewport_role")
            source_id = source.get("source_id")
            if role not in {"wide", "narrow"} or not isinstance(source_id, str) or not source_id.strip():
                raise DesignError(f"Reference study {study_id} source evidence requires source_id and wide or narrow viewport_role")
            artifact = _verified_reference_visual(root, source, f"Reference study {study_id} {role} source", role)
            publishable = bool(source.get("publishable", False))
            if source["ownership"] == "third-party" and publishable:
                raise DesignError("Third-party reference evidence must remain private and non-publishable")
            normalized_sources.append({**artifact, "source_id": source_id.strip(), "viewport_role": role, "ownership": source["ownership"], "publishable": publishable})
            source_roles.add(role)
            source_ids.add(source_id.strip())
        if source_roles != {"wide", "narrow"} or len(source_ids) != 1:
            raise DesignError(f"Reference study {study_id} cannot hybridize multiple sources and must capture both target viewports")
        reference_class = study.get("reference_class")
        difficulty_evidence = study.get("difficulty_evidence")
        if reference_class not in REFERENCE_CLASSES or not isinstance(difficulty_evidence, list):
            raise DesignError(f"Reference study {study_id} requires a supported reference_class and difficulty evidence")
        expected_difficulty = set(REFERENCE_CLASS_THRESHOLDS[reference_class])
        if {item.get("threshold") for item in difficulty_evidence if isinstance(item, dict)} != expected_difficulty:
            raise DesignError(f"Reference study {study_id} must pass every {reference_class} difficulty threshold")
        normalized_difficulty: list[dict[str, str]] = []
        for item in difficulty_evidence:
            if (
                item.get("status") != "pass"
                or any(not isinstance(item.get(field), str) or not item[field].strip() for field in ("finding", "evidence_region"))
            ):
                raise DesignError(f"Reference study {study_id} difficulty evidence must be passing and visually located")
            normalized_difficulty.append({
                "threshold": item["threshold"], "status": "pass",
                "finding": item["finding"].strip(), "evidence_region": item["evidence_region"].strip(),
            })
        copy_ledger = study.get("copy_adaptation_ledger")
        if not isinstance(copy_ledger, list) or len(copy_ledger) < 3:
            raise DesignError(f"Reference study {study_id} requires at least three concrete copy-to-adaptation decisions")
        normalized_copy_ledger: list[dict[str, str]] = []
        copied_detail_ids: set[str] = set()
        for item in copy_ledger:
            if not isinstance(item, dict):
                raise DesignError(f"Reference study {study_id} copy ledger entries must be objects")
            detail_id = _identifier(str(item.get("detail_id", "")), "reference copy detail ID")
            fields = ("detail", "source_location", "private_copy_action", "project_adaptation", "shipping_boundary")
            if detail_id in copied_detail_ids or any(not isinstance(item.get(field), str) or not item[field].strip() for field in fields):
                raise DesignError(f"Reference study {study_id} copy ledger requires unique IDs and a complete private-to-shipping path")
            normalized_copy_ledger.append({"detail_id": detail_id, **{field: item[field].strip() for field in fields}})
            copied_detail_ids.add(detail_id)
        reconstruction = study.get("reconstruction")
        if not isinstance(reconstruction, dict):
            raise DesignError(f"Reference study {study_id} requires a responsive HTML reconstruction")
        html_artifact = _verified_reference_file(root, reconstruction.get("html"), f"Reference study {study_id} reconstruction", {".html", ".htm"})
        wide = _verified_reference_visual(root, reconstruction.get("wide"), f"Reference study {study_id} wide reconstruction", "wide")
        narrow = _verified_reference_visual(root, reconstruction.get("narrow"), f"Reference study {study_id} narrow reconstruction", "narrow")
        typography_probe = None
        runtime_source_bundle = None
        if reconstruction.get("typography_render_probe") is not None:
            runtime_source_bundle = _verified_runtime_source_bundle(
                root, root / html_artifact["path"], reconstruction.get("runtime_source_files"),
                f"Reference study {study_id} reconstruction",
            )
            typography_probe = _verified_reference_file(root, reconstruction.get("typography_render_probe"), f"Reference study {study_id} typography browser probe", {".json"})
            _, typography_probe_path = _artifact_relative_path(root, typography_probe["path"])
            typography_probe_value = _read_json(typography_probe_path)
            if (
                typography_probe_value.get("schema_version") != 3
                or typography_probe_value.get("probe_kind") != "continuity-artifact-browser-probe"
                or typography_probe_value.get("passed") is not True
                or not isinstance(typography_probe_value.get("viewport"), dict)
                or typography_probe_value["viewport"].get("width") != 1440
                or not isinstance(typography_probe_value.get("typography_transfers"), list)
                or not typography_probe_value["typography_transfers"]
                or typography_probe_value.get("target_document_path") != html_artifact["path"]
                or typography_probe_value.get("target_document_sha256") != _document_probe_fingerprint(root / html_artifact["path"])
                or typography_probe_value.get("source_bundle_sha256") != runtime_source_bundle["source_bundle_sha256"]
                or not isinstance(typography_probe_value.get("document_url"), str)
                or not typography_probe_value["document_url"].split("?", 1)[0].endswith(html_artifact["path"])
            ):
                raise DesignError(f"Reference study {study_id} typography browser probe is not passed desktop evidence")
        if wide["sha256"] in reconstruction_visual_hashes or narrow["sha256"] in reconstruction_visual_hashes:
            raise DesignError("Every reference reconstruction requires distinct wide and narrow visual evidence")
        reconstruction_visual_hashes.update({wide["sha256"], narrow["sha256"]})
        correction_passes = study.get("correction_passes")
        if not isinstance(correction_passes, list) or len(correction_passes) < 2:
            raise DesignError(f"Reference study {study_id} requires at least two visual-difference correction passes")
        normalized_passes: list[dict[str, Any]] = []
        for index, correction in enumerate(correction_passes, 1):
            expected_status = "passed" if index == len(correction_passes) else "changes-required"
            if not isinstance(correction, dict) or correction.get("pass_number") != index or correction.get("status") != expected_status:
                raise DesignError(f"Reference study {study_id} correction passes must be sequential and end in passed status")
            findings = correction.get("findings")
            changes = correction.get("changes")
            if (
                not isinstance(findings, list) or not findings
                or not isinstance(changes, list) or not changes
                or any(not isinstance(item, dict) or not all(isinstance(item.get(field), str) and item[field].strip() for field in ("dimension", "evidence_region", "finding", "correction")) for item in findings)
                or any(not isinstance(item, str) or not item.strip() for item in changes)
            ):
                raise DesignError(f"Reference study {study_id} correction pass {index} requires located findings and applied changes")
            normalized_passes.append({
                "pass_number": index, "status": expected_status,
                "combined_wide": _verified_reference_visual(root, correction.get("combined_wide"), f"Reference study {study_id} pass {index} wide comparison", "wide"),
                "combined_narrow": _verified_reference_visual(root, correction.get("combined_narrow"), f"Reference study {study_id} pass {index} narrow comparison", "narrow"),
                "findings": [{field: item[field].strip() for field in ("dimension", "evidence_region", "finding", "correction")} for item in findings],
                "changes": [item.strip() for item in changes],
            })
        salience = study.get("salience_order")
        if not isinstance(salience, list) or len(salience) != 3 or {item.get("rank") for item in salience if isinstance(item, dict)} != {1, 2, 3}:
            raise DesignError(f"Reference study {study_id} requires an exact three-element salience comparison")
        normalized_salience: list[dict[str, Any]] = []
        for item in sorted(salience, key=lambda entry: entry["rank"]):
            if item.get("result") != "pass" or any(not isinstance(item.get(field), str) or not item[field].strip() for field in ("source_element", "reconstruction_element", "evidence_region")):
                raise DesignError(f"Reference study {study_id} salience order must visibly match")
            normalized_salience.append({"rank": item["rank"], "result": "pass", **{field: item[field].strip() for field in ("source_element", "reconstruction_element", "evidence_region")}})
        constraints = study.get("constraints")
        if not isinstance(constraints, list) or len(constraints) < 8:
            raise DesignError(f"Reference study {study_id} requires at least eight measured design-grammar constraints")
        normalized_constraints: list[dict[str, Any]] = []
        dimensions: set[str] = set()
        for constraint in constraints:
            if not isinstance(constraint, dict):
                raise DesignError(f"Reference study {study_id} constraints must be objects")
            constraint_id = _identifier(str(constraint.get("constraint_id", "")), "reference constraint ID")
            dimension = constraint.get("dimension")
            if constraint_id in constraint_by_id or dimension not in REFERENCE_CONSTRAINT_DIMENSIONS or dimension in dimensions:
                raise DesignError("Reference constraints require globally unique IDs and distinct supported dimensions per study")
            fields = ("observation", "invariant", "measurable_rule", "project_mapping", "allowed_variance", "prohibited_copying", "source_location", "reconstruction_location")
            if any(not isinstance(constraint.get(field), str) or not constraint[field].strip() for field in fields):
                raise DesignError(f"Reference constraint {constraint_id} requires located source and reconstruction evidence")
            metric = constraint.get("metric")
            if (
                not isinstance(metric, dict)
                or not isinstance(metric.get("name"), str) or not metric["name"].strip()
                or not isinstance(metric.get("unit"), str) or not metric["unit"].strip()
                or any(not isinstance(metric.get(field), (int, float)) for field in ("source_value", "reconstruction_value", "tolerance"))
                or metric["tolerance"] < 0
                or abs(metric["source_value"] - metric["reconstruction_value"]) > metric["tolerance"]
                or metric.get("status") != "pass"
            ):
                raise DesignError(f"Reference constraint {constraint_id} requires a passing numeric source-to-reconstruction measurement")
            normalized_constraints.append({"constraint_id": constraint_id, "dimension": dimension, **{field: constraint[field].strip() for field in fields}, "metric": {"name": metric["name"].strip(), "unit": metric["unit"].strip(), "source_value": metric["source_value"], "reconstruction_value": metric["reconstruction_value"], "tolerance": metric["tolerance"], "status": "pass"}})
            constraint_by_id[constraint_id] = study_id
            dimensions.add(dimension)
        if not REFERENCE_REQUIRED_DIMENSIONS <= dimensions or not ({"interaction", "motion"} & dimensions):
            raise DesignError(f"Reference study {study_id} must measure core spatial, typographic, media, responsive, and motion or interaction grammar")
        normalized_studies.append({
            "study_id": study_id, "source_identity": source_identity.strip(), "source_tile_ids": tile_ids, "source_evidence": normalized_sources,
            "reference_class": reference_class, "difficulty_evidence": normalized_difficulty,
            "reconstruction": {"html": html_artifact, "wide": wide, "narrow": narrow, "typography_render_probe": typography_probe, "runtime_source_files": runtime_source_bundle["source_files"] if runtime_source_bundle else None},
            "copy_adaptation_ledger": normalized_copy_ledger,
            "correction_passes": normalized_passes, "salience_order": normalized_salience, "constraints": normalized_constraints,
        })
        study_ids.add(study_id)

    adaptations = manifest.get("adaptations")
    if not isinstance(adaptations, list) or not 2 <= len(adaptations) <= 3:
        raise DesignError("Reference translation requires two or three Continuity adaptation studies")
    normalized_adaptations: list[dict[str, Any]] = []
    adaptation_ids: set[str] = set()
    adaptation_visual_hashes: set[str] = set()
    adaptation_distance_roles: set[str] = set()
    for adaptation in adaptations:
        if not isinstance(adaptation, dict):
            raise DesignError("Reference adaptations must be objects")
        adaptation_id = _identifier(str(adaptation.get("adaptation_id", "")), "reference adaptation ID")
        if adaptation_id in adaptation_ids:
            raise DesignError("Reference adaptation IDs must be unique")
        linked_studies = adaptation.get("study_ids")
        if not isinstance(linked_studies, list) or len(linked_studies) != 1 or not set(linked_studies) <= study_ids:
            raise DesignError(f"Reference adaptation {adaptation_id} requires one exact primary study; cross-source synthesis belongs after literal substitution")
        html_artifact = _verified_reference_file(root, adaptation.get("html"), f"Reference adaptation {adaptation_id}", {".html", ".htm"})
        wide = _verified_reference_visual(root, adaptation.get("wide"), f"Reference adaptation {adaptation_id} wide evidence", "wide")
        narrow = _verified_reference_visual(root, adaptation.get("narrow"), f"Reference adaptation {adaptation_id} narrow evidence", "narrow")
        if wide["sha256"] in adaptation_visual_hashes or narrow["sha256"] in adaptation_visual_hashes:
            raise DesignError("Every reference adaptation requires distinct wide and narrow visual evidence")
        adaptation_visual_hashes.update({wide["sha256"], narrow["sha256"]})
        expected_constraints = {constraint_id for constraint_id, owner in constraint_by_id.items() if owner in linked_studies}
        literal = adaptation.get("literal_substitution")
        if not isinstance(literal, dict) or literal.get("study_id") not in linked_studies:
            raise DesignError(f"Reference adaptation {adaptation_id} requires a literal substitution baseline from one linked source")
        literal_html = _verified_reference_file(root, literal.get("html"), f"Reference adaptation {adaptation_id} literal substitution", {".html", ".htm"})
        literal_wide = _verified_reference_visual(root, literal.get("wide"), f"Reference adaptation {adaptation_id} literal wide evidence", "wide")
        literal_narrow = _verified_reference_visual(root, literal.get("narrow"), f"Reference adaptation {adaptation_id} literal narrow evidence", "narrow")
        mapping = literal.get("mapping")
        if not isinstance(mapping, list) or {item.get("constraint_id") for item in mapping if isinstance(item, dict)} != expected_constraints:
            raise DesignError(f"Reference adaptation {adaptation_id} literal substitution must map every linked constraint")
        normalized_mapping: list[dict[str, str]] = []
        for item in mapping:
            fields = ("source_role", "project_replacement", "preserved_relationship", "source_location", "artifact_location")
            if any(not isinstance(item.get(field), str) or not item[field].strip() for field in fields):
                raise DesignError(f"Reference adaptation {adaptation_id} literal mappings require located role replacements")
            normalized_mapping.append({"constraint_id": item["constraint_id"], **{field: item[field].strip() for field in fields}})
        divergence = adaptation.get("controlled_divergence")
        if not isinstance(divergence, dict):
            raise DesignError(f"Reference adaptation {adaptation_id} requires a controlled divergence ledger")
        changes = divergence.get("changes")
        if not isinstance(changes, list) or not 1 <= len(changes) <= 4:
            raise DesignError(f"Reference adaptation {adaptation_id} must change one to four dimensions after literal substitution")
        normalized_changes: list[dict[str, Any]] = []
        changed_dimensions: set[str] = set()
        for item in changes:
            dimension = item.get("dimension") if isinstance(item, dict) else None
            preserved = item.get("preserved_constraint_ids") if isinstance(item, dict) else None
            if (
                dimension not in REFERENCE_CONSTRAINT_DIMENSIONS or dimension in changed_dimensions
                or not isinstance(preserved, list) or not preserved or not set(preserved) <= expected_constraints
                or any(not isinstance(item.get(field), str) or not item[field].strip() for field in ("from", "to", "rationale"))
            ):
                raise DesignError(f"Reference adaptation {adaptation_id} divergence changes require unique dimensions and preserved constraints")
            normalized_changes.append({"dimension": dimension, "from": item["from"].strip(), "to": item["to"].strip(), "rationale": item["rationale"].strip(), "preserved_constraint_ids": preserved})
            changed_dimensions.add(dimension)
        results = adaptation.get("constraint_results")
        if not isinstance(results, list) or {item.get("constraint_id") for item in results if isinstance(item, dict)} != expected_constraints:
            raise DesignError(f"Reference adaptation {adaptation_id} must disposition every linked formal constraint")
        normalized_results: list[dict[str, str]] = []
        for result in results:
            if result.get("result") != "pass" or any(not isinstance(result.get(field), str) or not result[field].strip() for field in ("evidence", "artifact_location")):
                raise DesignError(f"Reference adaptation {adaptation_id} constraint results require passing artifact evidence")
            normalized_results.append({"constraint_id": result["constraint_id"], "result": "pass", "evidence": result["evidence"].strip(), "artifact_location": result["artifact_location"].strip()})
        media = adaptation.get("media_strategy")
        if not isinstance(media, dict) or media.get("source") not in REFERENCE_MEDIA_STRATEGIES or media.get("primitive_substitution") is not False:
            raise DesignError(f"Reference adaptation {adaptation_id} cannot replace source-defining media with primitive CSS decoration")
        if media.get("generated_media_disposition") not in {"retained", "translated", "not-applicable"} or not isinstance(media.get("rationale"), str) or not media["rationale"].strip():
            raise DesignError(f"Reference adaptation {adaptation_id} requires a generated-media disposition and rationale")
        distance = adaptation.get("adaptation_distance")
        if not isinstance(distance, dict) or distance.get("role") not in ADAPTATION_DISTANCE_ROLES:
            raise DesignError(f"Reference adaptation {adaptation_id} requires a close, far, or experimental distance role")
        distance_dimensions = distance.get("dimensions")
        if not isinstance(distance_dimensions, list) or {item.get("dimension") for item in distance_dimensions if isinstance(item, dict)} != ADAPTATION_DISTANCE_DIMENSIONS:
            raise DesignError(f"Reference adaptation {adaptation_id} must measure every adaptation-distance dimension")
        normalized_distance_dimensions: list[dict[str, Any]] = []
        for item in distance_dimensions:
            score = item.get("score")
            if not isinstance(score, (int, float)) or not 0 <= score <= 1 or not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
                raise DesignError(f"Reference adaptation {adaptation_id} distance scores require a zero-to-one score and rationale")
            normalized_distance_dimensions.append({"dimension": item["dimension"], "score": float(score), "rationale": item["rationale"].strip()})
        total_score = sum(item["score"] for item in normalized_distance_dimensions) / len(normalized_distance_dimensions)
        if not isinstance(distance.get("total_score"), (int, float)) or abs(distance["total_score"] - total_score) > 0.01:
            raise DesignError(f"Reference adaptation {adaptation_id} distance total does not match its dimensions")
        if distance["role"] == "close-study" and not 0.25 <= total_score <= 0.55:
            raise DesignError(f"Reference adaptation {adaptation_id} close study must remain recognizably near the source")
        if distance["role"] == "far-study" and (total_score < 0.55 or sum(item["score"] >= 0.5 for item in normalized_distance_dimensions) < 4):
            raise DesignError(f"Reference adaptation {adaptation_id} far study must materially diverge in at least four dimensions")
        review = adaptation.get("fidelity_review")
        if not isinstance(review, dict) or review.get("status") != "passed" or any(review.get(check) != "pass" for check in REFERENCE_FIDELITY_CHECKS):
            raise DesignError(f"Reference adaptation {adaptation_id} requires a passed translation-fidelity review")
        for field in ("strongest_transfer", "weakest_loss", "next_action"):
            if not isinstance(review.get(field), str) or not review[field].strip():
                raise DesignError(f"Reference adaptation {adaptation_id} fidelity review requires {field}")
        normalized_adaptations.append({
            "adaptation_id": adaptation_id, "study_ids": linked_studies, "html": html_artifact,
            "wide": wide, "narrow": narrow, "constraint_results": normalized_results,
            "literal_substitution": {"study_id": literal["study_id"], "html": literal_html, "wide": literal_wide, "narrow": literal_narrow, "mapping": normalized_mapping},
            "controlled_divergence": {"changes": normalized_changes},
            "media_strategy": {"source": media["source"], "primitive_substitution": False, "generated_media_disposition": media["generated_media_disposition"], "rationale": media["rationale"].strip()},
            "adaptation_distance": {"role": distance["role"], "total_score": round(total_score, 4), "dimensions": normalized_distance_dimensions},
            "fidelity_review": {"status": "passed", **{check: "pass" for check in REFERENCE_FIDELITY_CHECKS}, **{field: review[field].strip() for field in ("strongest_transfer", "weakest_loss", "next_action")}},
        })
        adaptation_ids.add(adaptation_id)
        adaptation_distance_roles.add(distance["role"])

    if not {"close-study", "far-study"} <= adaptation_distance_roles:
        raise DesignError("Reference adaptation sets require both a close study and a materially far study")

    comparison = manifest.get("comparison")
    if not isinstance(comparison, dict):
        raise DesignError("Reference translation requires a side-by-side comparison artifact")
    normalized_comparison = {
        "html": _verified_reference_file(root, comparison.get("html"), "Reference translation comparison", {".html", ".htm"}),
        "wide": _verified_reference_visual(root, comparison.get("wide"), "Reference translation wide comparison", "wide"),
        "narrow": _verified_reference_visual(root, comparison.get("narrow"), "Reference translation narrow comparison", "narrow"),
    }
    independent = manifest.get("independent_review")
    if (
        not isinstance(independent, dict)
        or independent.get("status") != "passed"
        or independent.get("method") != "combined-visual-comparison"
        or independent.get("reviewer") != manifest["reviewer"]
        or independent.get("reviewer_type") != manifest["reviewer_type"]
        or independent.get("reviewed_at") != manifest["reviewed_at"]
    ):
        raise DesignError("Reference translation requires a passed independent combined-visual-comparison review")
    questions = independent.get("questions")
    if not isinstance(questions, dict) or set(questions) != set(REFERENCE_REVIEW_QUESTIONS):
        raise DesignError("Independent reference review must answer every precision question")
    normalized_questions: dict[str, dict[str, str]] = {}
    for question in REFERENCE_REVIEW_QUESTIONS:
        answer = questions[question]
        if not isinstance(answer, dict) or answer.get("result") != "pass" or any(not isinstance(answer.get(field), str) or not answer[field].strip() for field in ("finding", "evidence_region")):
            raise DesignError(f"Independent reference review question {question} requires passing located evidence")
        normalized_questions[question] = {"result": "pass", "finding": answer["finding"].strip(), "evidence_region": answer["evidence_region"].strip()}
    review_findings = independent.get("findings")
    if not isinstance(review_findings, list) or not review_findings:
        raise DesignError("Independent reference review must record at least one concrete correction finding")
    normalized_review_findings: list[dict[str, str]] = []
    for item in review_findings:
        if (
            not isinstance(item, dict) or item.get("disposition") != "resolved"
            or item.get("severity") not in {"info", "warning", "error", "critical"}
            or any(not isinstance(item.get(field), str) or not item[field].strip() for field in ("finding_id", "description", "evidence_region", "resolution"))
        ):
            raise DesignError("Independent reference review findings must be located and resolved before concept expansion")
        normalized_review_findings.append({field: item[field].strip() for field in ("finding_id", "severity", "description", "evidence_region", "disposition", "resolution")})
    normalized = {
        "schema_version": 2, "status": "passed", "design_id": design_id, "revision": record["revision"],
        "prepared_by": manifest["prepared_by"].strip(),
        "reviewer_type": manifest["reviewer_type"], "reviewer": manifest["reviewer"].strip(),
        "reviewed_at": manifest["reviewed_at"].strip(), "set_conclusion": manifest["set_conclusion"].strip(),
        "reference_studies": normalized_studies, "adaptations": normalized_adaptations,
        "comparison": normalized_comparison,
        "independent_review": {"status": "passed", "method": "combined-visual-comparison", "reviewer_type": manifest["reviewer_type"], "reviewer": manifest["reviewer"].strip(), "reviewed_at": manifest["reviewed_at"].strip(), "questions": normalized_questions, "findings": normalized_review_findings},
        "validated_at": _now(),
    }
    normalized["report_hash"] = _canonical_hash(normalized)
    record.update({"status": "developing-concepts", "reference_translation": normalized, "concept_evidence": None})
    _write_json(design_dir / "draft.json", record)
    return {
        "schema_version": 2, "precision_schema_version": 2,
        "design_id": design_id, "revision": record["revision"], "status": record["status"],
        "reference_study_count": len(normalized_studies), "adaptation_count": len(normalized_adaptations),
        "constraint_count": len(constraint_by_id), "correction_pass_count": sum(len(item["correction_passes"]) for item in normalized_studies),
        "copy_detail_count": sum(len(item["copy_adaptation_ledger"]) for item in normalized_studies),
        "literal_substitution_count": len(normalized_adaptations), "independent_review_status": "passed",
        "reference_classes": sorted({item["reference_class"] for item in normalized_studies}),
        "adaptation_distance_roles": sorted(adaptation_distance_roles),
        "reference_translation_hash": normalized["report_hash"],
        "execution_authorized": False,
    }


def concept_validate(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    _enabled(config)
    manifest = _read_json(manifest_path)
    design_id = _identifier(str(manifest.get("design_id", "")), "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    record = _read_json(design_dir / "draft.json")
    if record.get("workflow_version", 1) < 2:
        raise DesignError("Concept evidence requires a creative-director workflow draft")
    reference_translation = record.get("reference_translation")
    if record.get("workflow_version", 1) >= 3 and (not isinstance(reference_translation, dict) or reference_translation.get("status") != "passed"):
        raise DesignError("Workflow version 3 requires passed reference reconstruction and adaptation evidence before concept validation")
    portfolio = _verified_portfolio_report(root, manifest.get("portfolio_report")) if record.get("workflow_version", 1) >= 3 else None
    portfolio_report = portfolio["report"] if portfolio else {"generations": [], "recurring_tells": [], "strongest_prior_generation_id": None}
    if manifest.get("revision") != record.get("revision"):
        raise DesignError("Concept manifest revision does not match the current draft")
    mode = manifest.get("presentation_mode")
    if mode != record.get("concept_presentation_mode") or mode not in CONCEPT_PRESENTATION_MODES:
        raise DesignError("Concept presentation mode does not match the draft")
    concepts = manifest.get("concepts")
    if not isinstance(concepts, list) or not 2 <= len(concepts) <= 3:
        raise DesignError("Creative-director concept manifests require two or three visual concepts")
    collaboration_delivery = manifest.get("collaboration_delivery")
    expected_collaboration = record.get("collaboration_contract")
    if not isinstance(collaboration_delivery, dict) or collaboration_delivery.get("profile") != record.get("collaboration_profile"):
        raise DesignError("Concept manifest must record the active collaboration profile")
    for key, expected in expected_collaboration.items():
        if collaboration_delivery.get(key) != expected:
            raise DesignError(f"Concept collaboration delivery does not match {key}")
    if not isinstance(collaboration_delivery.get("feedback_prompt"), str) or not collaboration_delivery["feedback_prompt"].strip():
        raise DesignError("Concept collaboration delivery requires a profile-appropriate feedback prompt")
    recommendation_count = sum(item.get("recommended") is True for item in concepts if isinstance(item, dict))
    roles = [item.get("role") for item in concepts if isinstance(item, dict)]
    if mode == "equal-directions" and (len(concepts) != len(record.get("directions", [])) or set(roles) != {"direction"}):
        raise DesignError("Equal-direction concept evidence must cover every selectable direction without studies")
    if mode == "equal-directions" and recommendation_count:
        raise DesignError("Equal-direction concepts cannot preselect a winner")
    if mode == "director-led" and (
        len(record.get("directions", [])) != 1
        or recommendation_count != 1
        or roles.count("direction") != 1
        or roles.count("contrast-study") != len(concepts) - 1
    ):
        raise DesignError("Director-led concepts require one selectable recommendation and one or two contrast studies")
    required_text = ("thesis", "impact_thesis", "emotional_register", "signature_move", "imagery_treatment", "motion_decision", "preservation_promise", "tradeoff", "anti_reference")
    laboratory = record.get("generative_exploration") or {}
    laboratory_seeds = {item["seed_id"]: item for item in laboratory.get("seeds", []) if isinstance(item, dict) and item.get("seed_id")}
    normalized: list[dict[str, Any]] = []
    fidelity: set[str] = set()
    concept_ids: set[str] = set()
    reference_adaptation_ids: set[str] = set()
    known_reference_adaptations = {
        item["adaptation_id"]: item for item in (reference_translation or {}).get("adaptations", [])
        if isinstance(item, dict) and item.get("adaptation_id")
    }
    visual_hashes: set[str] = set()
    report_hashes: list[str] = []
    typography_strategy_ids: set[str] = set()
    typography_family_names: set[str] = set()
    art_direction_family_names: set[str] = set()
    composition_family_names: set[str] = set()
    page_grammar_ids: set[str] = set()
    page_grammar_families: set[str] = set()
    interaction_strategy_ids: set[str] = set()
    interaction_modes: set[str] = set()
    concept_runtime_probe_hashes: set[str] = set()
    comparison_strip_hashes: set[str] = set()
    generated_extraction_passed = True
    concept_forming_media_count = 0
    portfolio_fingerprints: dict[str, dict[str, str]] = {}
    minimum_journey_stage_count = 999
    laboratory_complete = laboratory.get("status") == "complete"
    planned_typography = {
        item["strategy_id"]: item
        for item in laboratory.get("range_plan", {}).get("typography_hypotheses", [])
        if isinstance(item, dict) and item.get("strategy_id")
    }
    planned_art_families = set(laboratory.get("range_plan", {}).get("art_direction_families", []))
    planned_composition_families = set(laboratory.get("range_plan", {}).get("composition_families", []))
    planned_page_grammars = {
        item["grammar_id"]: item
        for item in laboratory.get("range_plan", {}).get("page_grammar_hypotheses", [])
        if isinstance(item, dict) and item.get("grammar_id")
    }
    planned_interactions = {
        item["strategy_id"]: item
        for item in laboratory.get("range_plan", {}).get("interaction_motion_hypotheses", [])
        if isinstance(item, dict) and item.get("strategy_id")
    }
    for index, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            raise DesignError("Each concept must be an object")
        role = concept.get("role")
        if role not in CONCEPT_ROLES:
            raise DesignError("Each concept must be a selectable direction or contrast study")
        if role == "direction":
            concept_id = _identifier(str(concept.get("direction_id", "")), "concept direction ID")
            if concept_id not in {item["direction_id"] for item in record["directions"]}:
                raise DesignError("Selectable concept direction does not belong to the draft")
            tests_uncertainty = ""
        else:
            concept_id = _identifier(str(concept.get("study_id", "")), "contrast study ID")
            tests_uncertainty = concept.get("tests_uncertainty", "")
            if not isinstance(tests_uncertainty, str) or not tests_uncertainty.strip():
                raise DesignError(f"Contrast study {concept_id} must test a named uncertainty")
            if concept.get("recommended") is True:
                raise DesignError("Contrast studies cannot be recommended or selected")
        if concept_id in concept_ids:
            raise DesignError("Concept and study IDs must be unique")
        reference_adaptation_id = concept.get("reference_adaptation_id")
        if record.get("workflow_version", 1) >= 3:
            reference_adaptation_id = _identifier(str(reference_adaptation_id or ""), "reference adaptation ID")
            if reference_adaptation_id not in known_reference_adaptations or reference_adaptation_id in reference_adaptation_ids:
                raise DesignError(f"Concept {concept_id} requires its own validated reference adaptation")
            reference_adaptation_ids.add(reference_adaptation_id)
        if any(not isinstance(concept.get(key), str) or not concept[key].strip() for key in required_text):
            raise DesignError(f"Concept {concept_id} lacks required creative evidence")
        primary_carrier = concept.get("primary_carrier")
        if primary_carrier not in PRIMARY_CONCEPT_CARRIERS:
            raise DesignError(f"Concept {concept_id} requires a supported primary creative carrier")
        lineage = concept.get("seed_lineage")
        if not isinstance(lineage, list) or len(set(lineage)) != len(lineage) or any(item not in laboratory_seeds for item in lineage):
            raise DesignError(f"Concept {concept_id} seed lineage must reference unique known laboratory seeds")
        if laboratory.get("status") == "complete" and not lineage:
            raise DesignError(f"Concept {concept_id} must carry lineage from the completed concept laboratory")
        extractions = concept.get("system_extractions")
        if not isinstance(extractions, list) or any(not isinstance(item, str) or not item.strip() for item in extractions):
            raise DesignError(f"Concept {concept_id} system_extractions must be an array of design decisions")
        if any(laboratory_seeds[item]["medium"] in GENERATED_IMAGE_MEDIA for item in lineage) and len(extractions) < 3:
            raise DesignError(f"Concept {concept_id} must extract at least three non-image system decisions from generated-image lineage")
        palette = concept.get("palette")
        specimen = concept.get("type_specimen")
        level = concept.get("fidelity_level")
        if not isinstance(palette, list) or len(palette) < 3 or any(not isinstance(item, str) or not item.strip() for item in palette):
            raise DesignError(f"Concept {concept_id} requires at least three palette roles")
        if not isinstance(specimen, dict) or not isinstance(specimen.get("copy"), str) or not specimen["copy"].strip():
            raise DesignError(f"Concept {concept_id} requires a real-copy type specimen")
        if not isinstance(level, str) or not level.strip():
            raise DesignError(f"Concept {concept_id} requires a fidelity level")
        typography_system = concept.get("typography_system")
        if not isinstance(typography_system, dict):
            raise DesignError(f"Concept {concept_id} requires a typography system")
        strategy_id = _identifier(str(typography_system.get("strategy_id", "")), "typography strategy ID")
        typography_family = typography_system.get("family")
        typography_text_fields = ("display_behavior", "text_behavior", "responsive_behavior", "rationale")
        if laboratory_complete:
            if strategy_id not in planned_typography or typography_family != planned_typography[strategy_id].get("family"):
                raise DesignError(f"Concept {concept_id} typography must use a planned laboratory strategy and family")
        elif typography_family not in TYPOGRAPHY_FAMILIES:
            raise DesignError(f"Concept {concept_id} typography requires a supported family")
        if any(not isinstance(typography_system.get(key), str) or not typography_system[key].strip() for key in typography_text_fields):
            raise DesignError(f"Concept {concept_id} typography system lacks display, text, responsive, or rationale evidence")
        media_system = concept.get("media_system")
        if not isinstance(media_system, dict):
            raise DesignError(f"Concept {concept_id} requires a media system")
        if laboratory_complete:
            if media_system.get("art_direction_family") not in planned_art_families:
                raise DesignError(f"Concept {concept_id} media system must use a planned art-direction family")
        elif media_system.get("art_direction_family") not in ART_DIRECTION_FAMILIES:
            raise DesignError(f"Concept {concept_id} media system requires a supported art-direction family")
        if any(not isinstance(media_system.get(key), str) or not media_system[key].strip() for key in ("primary_role", "quiet_state", "fallback")):
            raise DesignError(f"Concept {concept_id} media system lacks primary, quiet, or fallback behavior")
        asset_mix = media_system.get("asset_mix")
        if not isinstance(asset_mix, list) or not asset_mix or len(set(asset_mix)) != len(asset_mix) or any(item not in MEDIA_ASSET_SOURCES for item in asset_mix):
            raise DesignError(f"Concept {concept_id} media system requires a supported asset mix")
        concept_role = media_system.get("concept_role", "supporting")
        if record.get("workflow_version", 1) >= 3 and concept_role not in {"concept-forming", "supporting", "omitted"}:
            raise DesignError(f"Concept {concept_id} media system requires an explicit concept role")
        media_effects = {}
        for field in ("thesis_effect", "composition_effect", "interaction_effect"):
            value = media_system.get(field, "Legacy workflow evidence")
            if record.get("workflow_version", 1) >= 3 and (not isinstance(value, str) or not value.strip()):
                raise DesignError(f"Concept {concept_id} media system requires {field}")
            media_effects[field] = str(value).strip()
        if concept_role == "concept-forming":
            if not set(asset_mix).intersection({"generated", "project-owned", "supplied"}):
                raise DesignError(f"Concept {concept_id} concept-forming media must use owned, supplied, or generated material")
            concept_forming_media_count += 1
        composition_family = concept.get("composition_family")
        if laboratory_complete:
            if composition_family not in planned_composition_families:
                raise DesignError(f"Concept {concept_id} must use a planned composition family")
        elif composition_family not in COMPOSITION_FAMILIES:
            raise DesignError(f"Concept {concept_id} requires a supported composition family")
        page_grammar = concept.get("page_grammar")
        if not isinstance(page_grammar, dict):
            raise DesignError(f"Concept {concept_id} requires an explicit page grammar")
        grammar_id = _identifier(str(page_grammar.get("grammar_id", "")), "page grammar ID")
        grammar_family = page_grammar.get("family")
        grammar_fields = ("core_behavior", "responsive_behavior", "depth_proof")
        if laboratory_complete:
            if grammar_id not in planned_page_grammars or grammar_family != planned_page_grammars[grammar_id].get("family"):
                raise DesignError(f"Concept {concept_id} page grammar must use a planned laboratory hypothesis")
        elif grammar_family not in PAGE_GRAMMAR_FAMILIES:
            raise DesignError(f"Concept {concept_id} requires a supported page-grammar family")
        if any(not isinstance(page_grammar.get(key), str) or not page_grammar[key].strip() for key in grammar_fields):
            raise DesignError(f"Concept {concept_id} page grammar lacks core, responsive, or depth behavior")
        interaction_system = concept.get("interaction_motion_system")
        if not isinstance(interaction_system, dict):
            raise DesignError(f"Concept {concept_id} requires an interaction and motion system")
        interaction_strategy_id = _identifier(str(interaction_system.get("strategy_id", "")), "interaction and motion strategy ID")
        interaction_mode = interaction_system.get("mode")
        interaction_fields = ("semantic_purpose", "reduced_motion", "static_fallback")
        if laboratory_complete:
            if interaction_strategy_id not in planned_interactions or interaction_mode != planned_interactions[interaction_strategy_id].get("mode"):
                raise DesignError(f"Concept {concept_id} interaction and motion must use a planned laboratory hypothesis")
        elif interaction_mode not in INTERACTION_MOTION_MODES:
            raise DesignError(f"Concept {concept_id} requires a supported interaction and motion mode")
        if any(not isinstance(interaction_system.get(key), str) or not interaction_system[key].strip() for key in interaction_fields):
            raise DesignError(f"Concept {concept_id} interaction and motion lacks semantic, reduced-motion, or static behavior")
        motion_decision = interaction_system.get("decision", "explicit-no-motion" if interaction_mode == "static" else "purposeful-motion")
        atmosphere_contribution = str(interaction_system.get("atmosphere_contribution", "Legacy workflow evidence")).strip()
        state_transition = str(interaction_system.get("state_transition", "Legacy workflow evidence")).strip()
        if record.get("workflow_version", 1) >= 3:
            if (interaction_mode == "static" and motion_decision != "explicit-no-motion") or (interaction_mode != "static" and motion_decision != "purposeful-motion"):
                raise DesignError(f"Concept {concept_id} interaction decision must match its motion mode")
            if not atmosphere_contribution or not state_transition:
                raise DesignError(f"Concept {concept_id} interaction system requires atmosphere and state-transition evidence")
            motion_storyboard = _verified_reference_file(root, interaction_system.get("storyboard"), f"Concept {concept_id} motion storyboard", {".html", ".htm", ".png", ".svg"})
        else:
            motion_storyboard = None
        journey_stages = concept.get("journey_stages")
        if not isinstance(journey_stages, list) or len(journey_stages) < 5:
            raise DesignError(f"Concept {concept_id} requires at least five journey stages")
        normalized_stages: list[dict[str, str]] = []
        stage_ids: set[str] = set()
        stage_roles: set[str] = set()
        for stage in journey_stages:
            if not isinstance(stage, dict):
                raise DesignError(f"Concept {concept_id} journey stages must be objects")
            stage_id = _identifier(str(stage.get("stage_id", "")), "journey stage ID")
            role_name = stage.get("role")
            if stage_id in stage_ids or role_name not in JOURNEY_STAGE_ROLES:
                raise DesignError(f"Concept {concept_id} journey stages require unique IDs and supported roles")
            if any(not isinstance(stage.get(key), str) or not stage[key].strip() for key in ("purpose", "signature_expression")):
                raise DesignError(f"Concept {concept_id} journey stage {stage_id} lacks purpose or signature evidence")
            normalized_stages.append({"stage_id": stage_id, "role": role_name, "purpose": stage["purpose"].strip(), "signature_expression": stage["signature_expression"].strip()})
            stage_ids.add(stage_id)
            stage_roles.add(role_name)
        if not {"opening", "proof", "closure"} <= stage_roles or not stage_roles.intersection({"quiet-state", "edge-state"}):
            raise DesignError(f"Concept {concept_id} journey must include opening, proof, quiet or edge, and closure stages")
        if record.get("workflow_version", 1) >= 3 and len(stage_roles - {"opening"}) < 4:
            raise DesignError(f"Concept {concept_id} must extend its signature across at least four distinct downstream roles")
        fingerprint = concept.get("portfolio_fingerprint")
        if record.get("workflow_version", 1) >= 3:
            if not isinstance(fingerprint, dict) or set(fingerprint) != PORTFOLIO_FINGERPRINT_DIMENSIONS:
                raise DesignError(f"Concept {concept_id} requires every portfolio fingerprint dimension")
            if any(not isinstance(value, str) or not value.strip() for value in fingerprint.values()):
                raise DesignError(f"Concept {concept_id} portfolio fingerprint values must be non-empty")
            portfolio_fingerprints[concept_id] = {key: fingerprint[key].strip() for key in sorted(PORTFOLIO_FINGERPRINT_DIMENSIONS)}
        else:
            portfolio_fingerprints[concept_id] = {}
        grammar_congruence = concept.get("grammar_congruence")
        if not isinstance(grammar_congruence, dict) or grammar_congruence.get("status") != "passed":
            raise DesignError(f"Concept {concept_id} requires a passed page-grammar congruence review")
        if grammar_congruence.get("reviewer_type") not in IMPACT_REVIEWER_TYPES:
            raise DesignError(f"Concept {concept_id} page-grammar congruence requires a human or agent-multimodal reviewer")
        for field in ("reviewer", "reviewed_at", "strongest_match", "weakest_mismatch"):
            if not isinstance(grammar_congruence.get(field), str) or not grammar_congruence[field].strip():
                raise DesignError(f"Concept {concept_id} page-grammar congruence requires {field}")
        behavior_evidence = grammar_congruence.get("behaviors")
        required_behaviors = PAGE_GRAMMAR_REQUIRED_BEHAVIORS[grammar_family]
        if not isinstance(behavior_evidence, list) or {
            item.get("behavior_id") for item in behavior_evidence if isinstance(item, dict)
        } != required_behaviors:
            raise DesignError(f"Concept {concept_id} page-grammar congruence must evidence every required {grammar_family} behavior")
        normalized_grammar_behaviors: list[dict[str, Any]] = []
        for behavior in behavior_evidence:
            behavior_id = behavior.get("behavior_id")
            visible_stages = behavior.get("journey_stage_ids")
            if (
                not isinstance(visible_stages, list)
                or len(set(visible_stages)) < 2
                or not set(visible_stages) <= stage_ids
                or not isinstance(behavior.get("artifact_note"), str)
                or not behavior["artifact_note"].strip()
            ):
                raise DesignError(f"Concept {concept_id} grammar behavior {behavior_id} requires two journey stages and a concrete artifact note")
            normalized_grammar_behaviors.append({
                "behavior_id": behavior_id,
                "journey_stage_ids": visible_stages,
                "artifact_note": behavior["artifact_note"].strip(),
            })
        comparison_coverage = concept.get("comparison_coverage")
        if not isinstance(comparison_coverage, dict):
            raise DesignError(f"Concept {concept_id} requires full-page comparison coverage")
        chapter_index = comparison_coverage.get("chapter_index")
        if chapter_index != [item["stage_id"] for item in normalized_stages]:
            raise DesignError(f"Concept {concept_id} comparison chapter index must cover the complete journey in order")
        strip = comparison_coverage.get("full_page_strip")
        if not isinstance(strip, dict):
            raise DesignError(f"Concept {concept_id} requires a full-page comparison strip")
        strip_relative, strip_path = _artifact_relative_path(root, strip.get("path"))
        strip_actual = hashlib.sha256(strip_path.read_bytes()).hexdigest() if strip_path.is_file() else ""
        if strip_path.suffix.lower() != ".png" or not strip_actual or strip.get("sha256") != strip_actual:
            raise DesignError(f"Concept comparison strip is missing or changed: {strip_relative}")
        strip_width, strip_height = _png_dimensions(strip_path)
        if strip_height < strip_width * 1.5 or strip_actual in comparison_strip_hashes:
            raise DesignError("Every concept requires a distinct, genuinely full-page comparison strip")
        deep_link = comparison_coverage.get("deep_link")
        if not isinstance(deep_link, dict):
            raise DesignError(f"Concept {concept_id} requires a deep link to its complete prototype")
        deep_relative, deep_path = _artifact_relative_path(root, deep_link.get("path"))
        deep_actual = hashlib.sha256(deep_path.read_bytes()).hexdigest() if deep_path.is_file() else ""
        if deep_path.suffix.lower() != ".html" or not deep_actual or deep_link.get("sha256") != deep_actual:
            raise DesignError(f"Concept comparison deep link is missing or changed: {deep_relative}")
        prototype_source = deep_path.read_text(encoding="utf-8", errors="replace")
        if record.get("workflow_version", 1) >= 3:
            runtime_source_bundle = _verified_runtime_source_bundle(
                root, deep_path, concept.get("runtime_source_files"), f"Concept {concept_id}",
            )
            adaptation_study_id = known_reference_adaptations[reference_adaptation_id]["study_ids"][0]
            linked_reference_study = next(item for item in reference_translation["reference_studies"] if item["study_id"] == adaptation_study_id)
            expected_reference_probe = linked_reference_study["reconstruction"].get("typography_render_probe")
            if not expected_reference_probe:
                raise DesignError(f"Concept {concept_id} requires typography browser evidence in its validated reference study")
            normalized_typographic_transfer = _validate_typographic_transfer(
                root, concept_id, concept.get("typographic_transfer"), prototype_source, expected_reference_probe,
                {"path": deep_relative, "sha256": runtime_source_bundle["target_document_sha256"], "source_bundle_sha256": runtime_source_bundle["source_bundle_sha256"]},
            )
            normalized_composition_asset_plan = _validate_composition_asset_plan(
                root, concept_id, concept.get("composition_asset_plan"), prototype_source,
                normalized_typographic_transfer["type_media_relation"],
                concept.get("typographic_transfer", {}).get("render_probe"),
            )
        else:
            runtime_source_bundle = None
            normalized_typographic_transfer = None
            normalized_composition_asset_plan = None
        for behavior in normalized_grammar_behaviors:
            marker = f'data-continuity-grammar-behavior="{behavior["behavior_id"]}"'
            if marker not in prototype_source:
                raise DesignError(f"Concept {concept_id} prototype does not implement grammar behavior {behavior['behavior_id']}")
            for stage_id in behavior["journey_stage_ids"]:
                if f'data-continuity-stage="{stage_id}"' not in prototype_source:
                    raise DesignError(f"Concept {concept_id} prototype does not expose journey stage {stage_id} for grammar review")
        journey_structure = concept.get("journey_structure_review")
        if not isinstance(journey_structure, dict) or journey_structure.get("status") != "passed":
            raise DesignError(f"Concept {concept_id} requires a passed deep-journey structure review")
        structure_mode = journey_structure.get("mode")
        if structure_mode not in JOURNEY_STRUCTURE_MODES:
            raise DesignError(f"Concept {concept_id} requires a supported deep-journey structure mode")
        if structure_mode == "persistent-state-variation" and grammar_family != "single-canvas-instrument":
            raise DesignError("Persistent state variation is reserved for a single-canvas instrument grammar")
        for field in ("deepest_signature_change", "repeated_pattern_risk"):
            if not isinstance(journey_structure.get(field), str) or not journey_structure[field].strip():
                raise DesignError(f"Concept {concept_id} deep-journey structure review requires {field}")
        assignments = journey_structure.get("assignments")
        if not isinstance(assignments, list) or {item.get("stage_id") for item in assignments if isinstance(item, dict)} != stage_ids:
            raise DesignError(f"Concept {concept_id} deep-journey structure review must cover every stage exactly once")
        normalized_assignments: list[dict[str, str]] = []
        expression_ids: set[str] = set()
        for assignment in assignments:
            expression_id = _identifier(str(assignment.get("expression_id", "")), "journey expression ID")
            if any(not isinstance(assignment.get(field), str) or not assignment[field].strip() for field in ("artifact_note", "responsive_behavior")):
                raise DesignError(f"Concept {concept_id} journey expressions require artifact and responsive behavior notes")
            expression_ids.add(expression_id)
            normalized_assignments.append({
                "stage_id": assignment["stage_id"], "expression_id": expression_id,
                "artifact_note": assignment["artifact_note"].strip(),
                "responsive_behavior": assignment["responsive_behavior"].strip(),
            })
        if len(expression_ids) < 4 or journey_structure.get("distinct_expression_count") != len(expression_ids):
            raise DesignError(f"Concept {concept_id} deep journey requires at least four distinct structural or state expressions")
        if structure_mode == "persistent-state-variation":
            if 'data-continuity-persistent-canvas="true"' not in prototype_source:
                raise DesignError(f"Concept {concept_id} does not implement the claimed persistent canvas")
            marker_name = "data-continuity-instrument-state"
        else:
            marker_name = "data-continuity-journey-structure"
        for expression_id in expression_ids:
            if f'{marker_name}="{expression_id}"' not in prototype_source:
                raise DesignError(f"Concept {concept_id} prototype does not implement journey expression {expression_id}")
        generated_lineage = [item for item in lineage if laboratory_seeds[item]["medium"] in GENERATED_IMAGE_MEDIA]
        generated_disposition = concept.get("generated_media_disposition")
        if not isinstance(generated_disposition, dict):
            raise DesignError(f"Concept {concept_id} requires an explicit generated-media disposition")
        normalized_generated_disposition: dict[str, Any]
        if generated_lineage:
            if generated_disposition.get("status") not in {"extracted", "retained-as-concept-carrier"}:
                raise DesignError(f"Concept {concept_id} must extract generated media or retain it as an approved concept carrier")
            if generated_disposition.get("status") == "extracted" and generated_disposition.get("pixel_promotion") is not False:
                raise DesignError(f"Concept {concept_id} extracted media cannot promote generated pixels")
            if generated_disposition.get("status") == "retained-as-concept-carrier" and generated_disposition.get("pixel_promotion") is not True:
                raise DesignError(f"Concept {concept_id} retained concept media must declare pixel promotion")
            source_seed_ids = generated_disposition.get("source_seed_ids")
            mappings = generated_disposition.get("extractions")
            if not isinstance(source_seed_ids, list) or not set(source_seed_ids) == set(generated_lineage):
                raise DesignError(f"Concept {concept_id} generated-media disposition must cover every generated seed in its lineage")
            if not isinstance(mappings, list) or len(mappings) < 3:
                raise DesignError(f"Concept {concept_id} requires at least three generated-media extraction mappings")
            domains: set[str] = set()
            normalized_mappings: list[dict[str, str]] = []
            for mapping in mappings:
                domain = mapping.get("domain") if isinstance(mapping, dict) else None
                rule = mapping.get("rule") if isinstance(mapping, dict) else None
                if domain not in GENERATED_EXTRACTION_DOMAINS or domain in domains or not isinstance(rule, str) or not rule.strip():
                    raise DesignError(f"Concept {concept_id} generated-media extractions require unique supported domains and concrete rules")
                domains.add(domain)
                normalized_mappings.append({"domain": domain, "rule": rule.strip()})
            derived = generated_disposition.get("derived_artifacts")
            if not isinstance(derived, list) or not derived:
                raise DesignError(f"Concept {concept_id} requires at least one hash-bound artifact derived from generated exploration")
            normalized_derived: list[dict[str, str]] = []
            for artifact in derived:
                relative, artifact_path = _artifact_relative_path(root, artifact.get("path") if isinstance(artifact, dict) else None)
                actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest() if artifact_path.is_file() else ""
                if artifact_path.suffix.lower() not in {".css", ".html", ".png", ".svg"} or not actual or artifact.get("sha256") != actual:
                    raise DesignError(f"Generated-media derived artifact is missing or changed: {relative}")
                normalized_derived.append({"path": relative, "sha256": actual})
            normalized_generated_disposition = {"status": generated_disposition["status"], "source_seed_ids": source_seed_ids, "pixel_promotion": generated_disposition["pixel_promotion"], "extractions": normalized_mappings, "derived_artifacts": normalized_derived}
        else:
            rationale = generated_disposition.get("rationale")
            if generated_disposition.get("status") != "not-applicable" or not isinstance(rationale, str) or not rationale.strip():
                raise DesignError(f"Concept {concept_id} without generated-image lineage must explain why generated-media extraction is not applicable")
            normalized_generated_disposition = {"status": "not-applicable", "rationale": rationale.strip()}
        comparison_strip_hashes.add(strip_actual)
        runtime_probes = concept.get("runtime_probes")
        if not isinstance(runtime_probes, list) or len(runtime_probes) != 3:
            raise DesignError(f"Concept {concept_id} requires mobile, tablet, and desktop runtime probes")
        normalized_runtime_probes: list[dict[str, Any]] = []
        runtime_viewports: set[str] = set()
        expected_widths = {"mobile": 390, "tablet": 768, "desktop": 1440}
        for probe in runtime_probes:
            viewport = probe.get("viewport") if isinstance(probe, dict) else None
            if viewport not in expected_widths or viewport in runtime_viewports:
                raise DesignError(f"Concept {concept_id} runtime probes require unique mobile, tablet, and desktop evidence")
            normalized_probe = _verified_browser_probe(root, probe, viewport, expected_widths[viewport])
            if record.get("workflow_version", 1) >= 3 and normalized_probe["schema_version"] != 3:
                raise DesignError(f"Concept {concept_id} workflow version 3 requires browser probe schema 3 at every viewport")
            if normalized_probe["sha256"] in concept_runtime_probe_hashes:
                raise DesignError("Every concept requires its own runtime probe artifacts")
            concept_runtime_probe_hashes.add(normalized_probe["sha256"])
            normalized_runtime_probes.append(normalized_probe)
            runtime_viewports.add(viewport)
        if record.get("workflow_version", 1) >= 3 and not any(
            item["viewport"] == "desktop"
            and item["path"] == normalized_typographic_transfer["render_probe"]["path"]
            and item["sha256"] == normalized_typographic_transfer["render_probe"]["sha256"]
            for item in normalized_runtime_probes
        ):
            raise DesignError(f"Concept {concept_id} typographic transfer must use one of its three validated runtime probes")
        fidelity.add(level.strip())
        visuals: dict[str, dict[str, str]] = {}
        for visual_role in ("wide_composition", "narrow_transformation"):
            evidence = concept.get(visual_role)
            if not isinstance(evidence, dict):
                raise DesignError(f"Concept {concept_id} requires {visual_role}")
            relative, path = _artifact_relative_path(root, evidence.get("path"))
            if path.suffix.lower() != ".png" or not path.is_file() or evidence.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
                raise DesignError(f"Concept visual evidence is missing or changed: {relative}")
            width, height = _png_dimensions(path)
            if (visual_role == "wide_composition" and width < 1100) or (visual_role == "narrow_transformation" and width >= 600):
                raise DesignError(f"Concept visual evidence has the wrong viewport role: {relative}")
            if evidence["sha256"] in visual_hashes:
                raise DesignError("Every wide and narrow concept visual must be distinct")
            visual_hashes.add(evidence["sha256"])
            visuals[visual_role] = {"path": relative, "sha256": evidence["sha256"], "width": width, "height": height}
        slop = _verified_private_report(root, concept.get("slop_report"), stage="concept")
        _, slop_path = _artifact_relative_path(root, slop["path"])
        slop_report = _read_json(slop_path)
        if record.get("workflow_version", 1) >= 3:
            fidelity_context = slop_report.get("translation_fidelity")
            if not isinstance(fidelity_context, dict) or any(fidelity_context.get(key) is not True for key in ("editable_depth_preserved", "font_transfer_verified", "approved_layer_plan_present", "approved_typographic_character_present")):
                raise DesignError(f"Concept {concept_id} slop report does not carry passed layer and typography fidelity")
        reviewed_visual_hashes = {
            artifact.get("sha256")
            for answer in slop_report.get("visual_review", {}).values()
            if isinstance(answer, dict)
            for artifact in answer.get("evidence", [])
            if isinstance(artifact, dict)
        }
        required_visual_hashes = {visuals["wide_composition"]["sha256"], visuals["narrow_transformation"]["sha256"]}
        if not required_visual_hashes <= reviewed_visual_hashes:
            raise DesignError(f"Concept {concept_id} slop review is not bound to its wide and narrow visuals")
        report_hashes.append(slop["report_hash"])
        normalized.append({
            "concept_id": concept_id, "role": role,
            "direction_id": concept_id if role == "direction" else None,
            "study_id": concept_id if role == "contrast-study" else None,
            "tests_uncertainty": tests_uncertainty.strip(), "recommended": bool(concept.get("recommended", False)),
            **{key: concept[key].strip() for key in required_text}, "primary_carrier": primary_carrier,
            "seed_lineage": lineage, "system_extractions": [item.strip() for item in extractions], "palette": palette,
            "type_specimen": specimen,
            "typography_system": {"strategy_id": strategy_id, "family": typography_family, **{key: typography_system[key].strip() for key in typography_text_fields}},
            "typographic_transfer": normalized_typographic_transfer,
            "runtime_source_files": runtime_source_bundle["source_files"] if runtime_source_bundle else None,
            "media_system": {"art_direction_family": media_system["art_direction_family"], "primary_role": media_system["primary_role"].strip(), "asset_mix": asset_mix, "quiet_state": media_system["quiet_state"].strip(), "fallback": media_system["fallback"].strip(), "concept_role": concept_role, **media_effects},
            "composition_asset_plan": normalized_composition_asset_plan,
            "composition_family": composition_family,
            "page_grammar": {"grammar_id": grammar_id, "family": grammar_family, **{key: page_grammar[key].strip() for key in grammar_fields}},
            "grammar_congruence": {
                "status": "passed", "reviewer_type": grammar_congruence["reviewer_type"],
                "reviewer": grammar_congruence["reviewer"].strip(), "reviewed_at": grammar_congruence["reviewed_at"].strip(),
                "strongest_match": grammar_congruence["strongest_match"].strip(),
                "weakest_mismatch": grammar_congruence["weakest_mismatch"].strip(),
                "behaviors": normalized_grammar_behaviors,
            },
            "journey_structure_review": {
                "status": "passed", "mode": structure_mode,
                "distinct_expression_count": len(expression_ids),
                "deepest_signature_change": journey_structure["deepest_signature_change"].strip(),
                "repeated_pattern_risk": journey_structure["repeated_pattern_risk"].strip(),
                "assignments": normalized_assignments,
            },
            "interaction_motion_system": {"strategy_id": interaction_strategy_id, "mode": interaction_mode, "decision": motion_decision, "storyboard": motion_storyboard, "atmosphere_contribution": atmosphere_contribution, "state_transition": state_transition, **{key: interaction_system[key].strip() for key in interaction_fields}},
            "portfolio_fingerprint": portfolio_fingerprints[concept_id],
            "journey_stages": normalized_stages, "runtime_probes": normalized_runtime_probes,
            "comparison_coverage": {"full_page_strip": {"path": strip_relative, "sha256": strip_actual, "width": strip_width, "height": strip_height}, "chapter_index": chapter_index, "deep_link": {"path": deep_relative, "sha256": deep_actual}},
            "generated_media_disposition": normalized_generated_disposition,
            "reference_adaptation_id": reference_adaptation_id if record.get("workflow_version", 1) >= 3 else None,
            "fidelity_level": level.strip(), **visuals, "slop_report": slop,
        })
        typography_strategy_ids.add(strategy_id)
        typography_family_names.add(typography_family)
        art_direction_family_names.add(media_system["art_direction_family"])
        composition_family_names.add(composition_family)
        page_grammar_ids.add(grammar_id)
        page_grammar_families.add(grammar_family)
        interaction_strategy_ids.add(interaction_strategy_id)
        interaction_modes.add(interaction_mode)
        minimum_journey_stage_count = min(minimum_journey_stage_count, len(normalized_stages))
        concept_ids.add(concept_id)
    if record.get("workflow_version", 1) >= 3 and reference_adaptation_ids != set(known_reference_adaptations):
        raise DesignError("Concept set must consume every validated reference adaptation exactly once")
    if len(fidelity) != 1:
        raise DesignError("Concept directions must have comparable fidelity")
    if len(set(report_hashes)) != len(normalized):
        raise DesignError("Every concept requires its own current AI-slop report")
    if len({(item["thesis"].casefold(), item["signature_move"].casefold()) for item in normalized}) != len(normalized):
        raise DesignError("Concept directions must differ structurally, not only cosmetically")
    if len(typography_strategy_ids) != len(normalized) or len(typography_family_names) < min(2, len(normalized)):
        raise DesignError("Concept range requires a distinct typography strategy per concept and at least two typography families")
    if len(art_direction_family_names) != len(normalized):
        raise DesignError("Concept range requires a distinct art-direction family per concept")
    if len(composition_family_names) != len(normalized):
        raise DesignError("Concept range requires a distinct composition family per concept")
    if len(page_grammar_ids) != len(normalized) or len(page_grammar_families) != len(normalized):
        raise DesignError("Concept range requires a distinct planned page grammar per concept")
    if len(interaction_strategy_ids) != len(normalized):
        raise DesignError("Concept range requires a distinct interaction and motion strategy per concept")
    if len(normalized) > 1 and interaction_modes == {"static"}:
        raise DesignError("Multi-concept UI directioning must test at least one meaningful interaction or motion mode")
    if record.get("workflow_version", 1) >= 3 and concept_forming_media_count < 1:
        raise DesignError("Concept sets require at least one direction whose media forms the idea rather than decorating it")
    creative_range = manifest.get("creative_range")
    if not isinstance(creative_range, dict) or creative_range.get("status") != "passed":
        raise DesignError("Concept selection requires a passed creative-range review separate from AI-slop review")
    for key in ("reviewer", "reviewed_at"):
        if not isinstance(creative_range.get(key), str) or not creative_range[key].strip():
            raise DesignError(f"Creative-range review requires {key}")
    reactions = creative_range.get("five_second_reactions")
    if not isinstance(reactions, list) or {item.get("concept_id") for item in reactions if isinstance(item, dict)} != concept_ids:
        raise DesignError("Creative-range review requires one five-second reaction for every concept")
    reaction_text = []
    for item in reactions:
        if not isinstance(item, dict) or set(item) != {"concept_id", "reaction"} or not isinstance(item.get("reaction"), str) or not item["reaction"].strip():
            raise DesignError("Five-second reactions require only concept_id and reaction")
        reaction_text.append(item["reaction"].strip().casefold())
    if len(set(reaction_text)) != len(reaction_text):
        raise DesignError("Five-second reactions must distinguish the concepts at a glance")
    distances = creative_range.get("pairwise_distances")
    ordered_concept_ids = sorted(concept_ids)
    expected_pairs = {frozenset((left, right)) for index, left in enumerate(ordered_concept_ids) for right in ordered_concept_ids[index + 1:]}
    normalized_pairs: set[frozenset[str]] = set()
    if not isinstance(distances, list):
        raise DesignError("Creative-range review requires pairwise distance evidence")
    for item in distances:
        pair = item.get("concept_ids") if isinstance(item, dict) else None
        dimensions = item.get("differing_dimensions") if isinstance(item, dict) else None
        rationale = item.get("rationale") if isinstance(item, dict) else None
        pair_set = frozenset(pair) if isinstance(pair, list) else frozenset()
        if len(pair_set) != 2 or not pair_set <= concept_ids or pair_set in normalized_pairs:
            raise DesignError("Creative-range pairwise evidence must cover unique known concept pairs")
        if not isinstance(dimensions, list) or len(set(dimensions)) < 3 or not set(dimensions) <= CREATIVE_DISTANCE_DIMENSIONS:
            raise DesignError("Every concept pair must differ across at least three material design dimensions")
        if not isinstance(rationale, str) or not rationale.strip():
            raise DesignError("Creative-range pairwise evidence requires rationale")
        normalized_pairs.add(pair_set)
    if normalized_pairs != expected_pairs:
        raise DesignError("Creative-range review must compare every concept pair")
    house_review = creative_range.get("house_tell_review")
    if not isinstance(house_review, dict) or house_review.get("project_identity_wins") is not True:
        raise DesignError("Creative-range review must show that project identity wins over Continuity house tells")
    if portfolio and house_review.get("portfolio_report_hash") != portfolio["report_hash"]:
        raise DesignError("House-tell review must bind the current portfolio report")
    tells = house_review.get("recurring_tells_checked")
    known_tells = {item["tell_id"]: item for item in portfolio_report.get("recurring_tells", [])}
    if portfolio and (not isinstance(tells, list) or set(tells) != set(known_tells)):
        raise DesignError("House-tell review must check every current portfolio tell with a project-specific rationale")
    if not isinstance(tells, list) or not isinstance(house_review.get("rationale"), str) or not house_review["rationale"].strip():
        raise DesignError("House-tell review must check every current portfolio tell with a project-specific rationale")
    comparisons = house_review.get("concept_comparisons")
    if portfolio and (not isinstance(comparisons, list) or {item.get("concept_id") for item in comparisons if isinstance(item, dict)} != concept_ids):
        raise DesignError("House-tell review requires one derived comparison for every concept")
    for item in comparisons or []:
        concept_id = item["concept_id"]
        derived_matches = {
            tell_id for tell_id, tell in known_tells.items()
            if portfolio_fingerprints[concept_id][tell["dimension"]] == tell["value"]
        }
        if set(item.get("matched_tell_ids", [])) != derived_matches or len(derived_matches) > 2:
            raise DesignError(f"Concept {concept_id} repeats too many portfolio house tells or misstates its overlap")
        changed = item.get("changed_fingerprint_dimensions")
        strongest_id = portfolio_report.get("strongest_prior_generation_id")
        strongest_fingerprint = next(
            (generation["fingerprint"] for generation in portfolio_report.get("generations", []) if generation["generation_id"] == strongest_id),
            None,
        )
        derived_changed = {
            dimension for dimension in PORTFOLIO_FINGERPRINT_DIMENSIONS
            if strongest_fingerprint is None or portfolio_fingerprints[concept_id][dimension] != strongest_fingerprint[dimension]
        }
        if not isinstance(changed, list) or set(changed) != derived_changed or len(derived_changed) < 3:
            raise DesignError(f"Concept {concept_id} must deliberately change at least three portfolio fingerprint dimensions")
        recurrences = item.get("intentional_recurrences")
        if not isinstance(recurrences, list) or {entry.get("tell_id") for entry in recurrences if isinstance(entry, dict)} != derived_matches:
            raise DesignError(f"Concept {concept_id} must disposition every recurring house tell it retains")
        for entry in recurrences:
            if any(not isinstance(entry.get(field), str) or not entry[field].strip() for field in ("rationale", "contract_reference")):
                raise DesignError(f"Concept {concept_id} retained house tells require rationale and contract references")
    adversarial = creative_range.get("adversarial_pass")
    if not isinstance(adversarial, list) or {item.get("concept_id") for item in adversarial if isinstance(item, dict)} != concept_ids:
        raise DesignError("Creative-range review requires an adversarial pass for every concept")
    adversarial_fields = ("genericity_argument", "opposing_hypothesis", "resulting_change", "rejected_choice")
    for item in adversarial:
        if not isinstance(item, dict) or any(not isinstance(item.get(key), str) or not item[key].strip() for key in adversarial_fields):
            raise DesignError("Every adversarial concept pass requires its genericity argument, opposing hypothesis, resulting change, and rejected choice")
    range_audit = creative_range.get("range_audit")
    actual_range_counts = {
        "typography_strategy_count": len(typography_strategy_ids),
        "typography_family_count": len(typography_family_names),
        "art_direction_family_count": len(art_direction_family_names),
        "composition_family_count": len(composition_family_names),
        "page_grammar_count": len(page_grammar_ids),
        "interaction_motion_strategy_count": len(interaction_strategy_ids),
        "minimum_journey_stage_count": minimum_journey_stage_count,
    }
    if record.get("workflow_version", 1) >= 3:
        actual_range_counts["concept_forming_media_count"] = concept_forming_media_count
    if not isinstance(range_audit, dict) or range_audit.get("status") != "passed" or range_audit.get("per_concept_runtime_probes") is not True:
        raise DesignError("Creative-range review requires a passed typography, media, depth, and per-concept runtime audit")
    if range_audit.get("comparison_depth_coverage") is not True or range_audit.get("generated_media_extraction_passed") is not True:
        raise DesignError("Creative-range review requires full-page comparison coverage and generated-media extraction evidence")
    if any(range_audit.get(key) != value for key, value in actual_range_counts.items()):
        raise DesignError("Creative-range audit counts do not match the concept evidence")
    if not isinstance(range_audit.get("rationale"), str) or not range_audit["rationale"].strip():
        raise DesignError("Creative-range audit requires a project-specific rationale")
    normalized_creative_range = {
        "status": "passed", "reviewer": creative_range["reviewer"].strip(), "reviewed_at": creative_range["reviewed_at"].strip(),
        "five_second_reactions": reactions, "pairwise_distances": distances,
        "house_tell_review": house_review, "adversarial_pass": adversarial,
        "range_audit": {"status": "passed", **actual_range_counts, "per_concept_runtime_probes": True, "comparison_depth_coverage": True, "generated_media_extraction_passed": True, "rationale": range_audit["rationale"].strip()},
    }
    impact_review = manifest.get("impact_review")
    if not isinstance(impact_review, dict) or impact_review.get("status") != "passed":
        raise DesignError("Concept selection requires a passed impact review separate from range and AI-slop review")
    reviewer_type = impact_review.get("reviewer_type")
    if reviewer_type not in IMPACT_REVIEWER_TYPES:
        raise DesignError("Impact review requires a human or agent-multimodal reviewer type")
    for key in ("reviewer", "reviewed_at", "set_conclusion"):
        if not isinstance(impact_review.get(key), str) or not impact_review[key].strip():
            raise DesignError(f"Impact review requires {key}")
    impact_concepts = impact_review.get("concepts")
    if not isinstance(impact_concepts, list) or {item.get("concept_id") for item in impact_concepts if isinstance(item, dict)} != concept_ids:
        raise DesignError("Impact review requires one assessment for every concept")
    normalized_impact_concepts: list[dict[str, Any]] = []
    compelling_count = 0
    signature_stage_minimum = 999
    normalized_by_id = {item["concept_id"]: item for item in normalized}
    for assessment in impact_concepts:
        concept_id = assessment.get("concept_id")
        concept = normalized_by_id[concept_id]
        if assessment.get("outcome") != "passed" or assessment.get("strength") not in IMPACT_STRENGTHS:
            raise DesignError(f"Concept {concept_id} impact review must pass with credible or compelling strength")
        signature_stage_ids = assessment.get("signature_stage_ids")
        stage_by_id = {item["stage_id"]: item for item in concept["journey_stages"]}
        if (
            not isinstance(signature_stage_ids, list) or len(set(signature_stage_ids)) < 3
            or not set(signature_stage_ids) <= set(stage_by_id)
            or len({stage_by_id[item]["role"] for item in signature_stage_ids}) < 3
        ):
            raise DesignError(f"Concept {concept_id} signature must materially control at least three different journey roles")
        checks = ("identity_specificity", "emotional_resonance", "craft_coherence")
        if any(assessment.get(key) != "pass" for key in checks):
            raise DesignError(f"Concept {concept_id} impact review must pass identity, resonance, and craft checks")
        fields = ("rationale", "weakest_moment", "refinement_priority")
        if any(not isinstance(assessment.get(key), str) or not assessment[key].strip() for key in fields):
            raise DesignError(f"Concept {concept_id} impact review requires rationale, weakest moment, and refinement priority")
        impact_evidence = assessment.get("evidence")
        if not isinstance(impact_evidence, list) or len(impact_evidence) < 2:
            raise DesignError(f"Concept {concept_id} impact review requires wide and narrow visual evidence")
        normalized_impact_evidence: list[dict[str, str]] = []
        impact_hashes: set[str] = set()
        for artifact in impact_evidence:
            relative, artifact_path = _artifact_relative_path(root, artifact.get("path") if isinstance(artifact, dict) else None)
            actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest() if artifact_path.is_file() else ""
            if artifact_path.suffix.lower() != ".png" or not actual or artifact.get("sha256") != actual:
                raise DesignError(f"Impact-review evidence is missing or changed: {relative}")
            normalized_impact_evidence.append({"path": relative, "sha256": actual})
            impact_hashes.add(actual)
        if not {concept["wide_composition"]["sha256"], concept["narrow_transformation"]["sha256"]} <= impact_hashes:
            raise DesignError(f"Concept {concept_id} impact review is not bound to its wide and narrow visuals")
        if assessment["strength"] == "compelling":
            compelling_count += 1
        signature_stage_minimum = min(signature_stage_minimum, len(set(signature_stage_ids)))
        normalized_impact_concepts.append({
            "concept_id": concept_id, "outcome": "passed", "strength": assessment["strength"],
            "signature_stage_ids": signature_stage_ids, **{key: "pass" for key in checks},
            **{key: assessment[key].strip() for key in fields}, "evidence": normalized_impact_evidence,
        })
    if compelling_count < 1 or impact_review.get("at_least_one_compelling") is not True:
        raise DesignError("A concept set cannot proceed without at least one compelling direction")
    normalized_impact_review = {
        "status": "passed", "reviewer_type": reviewer_type,
        "reviewer": impact_review["reviewer"].strip(), "reviewed_at": impact_review["reviewed_at"].strip(),
        "at_least_one_compelling": True, "set_conclusion": impact_review["set_conclusion"].strip(),
        "signature_stage_coverage_minimum": signature_stage_minimum, "concepts": normalized_impact_concepts,
    }
    prior_challenge = manifest.get("prior_output_challenge")
    strongest_prior = portfolio_report.get("strongest_prior_generation_id")
    if record.get("workflow_version", 1) < 3:
        normalized_prior_challenge = None
    elif strongest_prior:
        if (
            not isinstance(prior_challenge, dict)
            or prior_challenge.get("status") != "passed"
            or prior_challenge.get("portfolio_report_hash") != portfolio["report_hash"]
            or prior_challenge.get("strongest_prior_generation_id") != strongest_prior
            or prior_challenge.get("lineage_preserved") is not True
        ):
            raise DesignError("Concept set must pass a hash-bound counterfactual against the strongest prior generation")
        challenger_id = prior_challenge.get("challenger_concept_id")
        impact_by_id = {item["concept_id"]: item for item in normalized_impact_concepts}
        if challenger_id not in impact_by_id or impact_by_id[challenger_id]["strength"] != "compelling":
            raise DesignError("The strongest-prior challenger must be a compelling current concept")
        for field in ("impact_advantage", "project_specificity_gain", "reviewer", "reviewed_at"):
            if not isinstance(prior_challenge.get(field), str) or not prior_challenge[field].strip():
                raise DesignError(f"Strongest-prior challenge requires {field}")
        challenge_evidence = prior_challenge.get("evidence")
        if not isinstance(challenge_evidence, list) or len(challenge_evidence) < 3:
            raise DesignError("Strongest-prior challenge requires current wide, current narrow, and prior evidence")
        normalized_challenge_evidence = [
            _verified_reference_file(root, item, "Strongest-prior challenge evidence", {".png"}) for item in challenge_evidence
        ]
        challenger = next(item for item in normalized if item["concept_id"] == challenger_id)
        prior_generation = next(item for item in portfolio_report["generations"] if item["generation_id"] == strongest_prior)
        expected_hashes = {challenger["wide_composition"]["sha256"], challenger["narrow_transformation"]["sha256"], prior_generation["artifact"]["sha256"]}
        if not expected_hashes <= {item["sha256"] for item in normalized_challenge_evidence}:
            raise DesignError("Strongest-prior challenge evidence is not bound to the compared generations")
        normalized_prior_challenge = {
            "status": "passed", "portfolio_report_hash": portfolio["report_hash"],
            "strongest_prior_generation_id": strongest_prior, "challenger_concept_id": challenger_id,
            "lineage_preserved": True,
            **{field: prior_challenge[field].strip() for field in ("impact_advantage", "project_specificity_gain", "reviewer", "reviewed_at")},
            "evidence": normalized_challenge_evidence,
        }
    else:
        if not isinstance(prior_challenge, dict) or prior_challenge.get("status") != "not-applicable" or not isinstance(prior_challenge.get("rationale"), str) or not prior_challenge["rationale"].strip():
            raise DesignError("An empty portfolio requires an explicit strongest-prior not-applicable rationale")
        normalized_prior_challenge = {"status": "not-applicable", "rationale": prior_challenge["rationale"].strip()}
    browser_snapshots = manifest.get("browser_snapshots")
    if not isinstance(browser_snapshots, list) or len(browser_snapshots) != 3:
        raise DesignError("Concept comparison requires mobile, tablet, and desktop browser snapshots")
    normalized_snapshots: list[dict[str, Any]] = []
    snapshot_roles: set[str] = set()
    for item in browser_snapshots:
        if not isinstance(item, dict) or item.get("viewport") not in {"mobile", "tablet", "desktop"}:
            raise DesignError("Concept browser snapshot requires a supported viewport")
        relative, path = _artifact_relative_path(root, item.get("path"))
        if path.suffix.lower() != ".png" or not path.is_file() or item.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            raise DesignError(f"Concept browser snapshot is missing or changed: {relative}")
        width, height = _png_dimensions(path)
        role = item["viewport"]
        if role in snapshot_roles or height < 1 or (role == "mobile" and width >= 600) or (role == "tablet" and not 600 <= width < 1100) or (role == "desktop" and width < 1100):
            raise DesignError("Concept browser snapshot dimensions do not match its viewport")
        normalized_snapshots.append({"viewport": role, "path": relative, "sha256": item["sha256"], "width": width, "height": height})
        snapshot_roles.add(role)
    browser_probes = manifest.get("browser_probes")
    if not isinstance(browser_probes, list) or len(browser_probes) != 3:
        raise DesignError("Concept comparison requires a passed browser probe at every required viewport")
    normalized_probes: list[dict[str, Any]] = []
    probe_roles: set[str] = set()
    for item in browser_probes:
        if not isinstance(item, dict) or item.get("viewport") not in snapshot_roles or item["viewport"] in probe_roles:
            raise DesignError("Concept browser probes require unique mobile, tablet, and desktop evidence")
        snapshot = next(snapshot for snapshot in normalized_snapshots if snapshot["viewport"] == item["viewport"])
        normalized_probes.append(_verified_browser_probe(root, item, item["viewport"], snapshot["width"]))
        probe_roles.add(item["viewport"])
    research_tiles = {tile["tile"] for tile in record.get("research", {}).get("moodboard", [])}
    research_links = manifest.get("research_links", [])
    if not isinstance(research_links, list):
        raise DesignError("research_links must be an array")
    normalized_links: list[dict[str, Any]] = []
    linked_tiles: set[int] = set()
    for item in research_links:
        if not isinstance(item, dict) or item.get("tile") not in research_tiles or item.get("disposition") not in RESEARCH_LINK_DISPOSITIONS:
            raise DesignError("Research links must reference a moodboard tile and supported disposition")
        if item["tile"] in linked_tiles:
            raise DesignError("Each moodboard tile requires one concept disposition")
        rationale = item.get("rationale")
        linked_concepts = item.get("concept_ids", [])
        if not isinstance(rationale, str) or not rationale.strip() or not isinstance(linked_concepts, list) or any(value not in concept_ids for value in linked_concepts):
            raise DesignError("Research links require rationale and known concept IDs")
        if item["disposition"] in {"adopted", "transformed"} and not linked_concepts:
            raise DesignError("Adopted or transformed research requires a concept link")
        normalized_links.append({"tile": item["tile"], "disposition": item["disposition"], "rationale": rationale.strip(), "concept_ids": linked_concepts})
        linked_tiles.add(item["tile"])
    if research_tiles != linked_tiles:
        raise DesignError("Every moodboard tile must be adopted, transformed, rejected, or retained as reference-only")
    references = manifest.get("visual_references", [])
    if not isinstance(references, list):
        raise DesignError("visual_references must be an array")
    publishable: list[dict[str, Any]] = []
    normalized_refs: list[dict[str, Any]] = []
    for item in references:
        if not isinstance(item, dict) or item.get("ownership") not in VISUAL_REFERENCE_OWNERSHIP:
            raise DesignError("Visual references require a valid ownership classification")
        relative, path = _artifact_relative_path(root, item.get("path"))
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if not actual or item.get("sha256") != actual:
            raise DesignError(f"Visual reference is missing or changed: {relative}")
        publish = bool(item.get("publishable", False))
        if publish and item["ownership"] == "third-party":
            raise DesignError("Third-party moodboard and screenshot material cannot be promoted")
        normalized_ref = {"path": relative, "sha256": actual, "ownership": item["ownership"], "publishable": publish, "lesson": str(item.get("lesson", "")).strip()}
        normalized_refs.append(normalized_ref)
        if publish:
            publishable.append(normalized_ref)
    visual_reference_material = [
        {"name": Path(item["path"]).name, "sha256": item["sha256"], "ownership": item["ownership"]}
        for item in publishable
    ]
    visual_reference_hash = _canonical_hash(visual_reference_material)
    evidence = {
        "manifest_hash": _canonical_hash(manifest), "presentation_mode": mode, "concepts": normalized,
        "visual_references": normalized_refs, "publishable_references": publishable,
        "visual_reference_material": visual_reference_material,
        "browser_snapshots": normalized_snapshots,
        "browser_probes": normalized_probes,
        "research_links": normalized_links,
        "collaboration_delivery": collaboration_delivery,
        "creative_range": normalized_creative_range,
        "creative_range_status": "passed",
        "impact_review": normalized_impact_review,
        "impact_review_status": "passed",
        "portfolio_report": {key: portfolio[key] for key in ("path", "sha256", "report_hash")} if portfolio else None,
        "prior_output_challenge": normalized_prior_challenge if record.get("workflow_version", 1) >= 3 else None,
        "generative_laboratory_hash": laboratory.get("laboratory_hash"),
        "reference_translation_hash": (reference_translation or {}).get("report_hash"),
        "visual_reference_hash": visual_reference_hash, "slop_report_hashes": report_hashes,
        "ruleset_version": design_slop.RULESET_VERSION, "validated": True, "validated_at": _now(),
    }
    record.update({"status": "awaiting-feedback", "concept_evidence": evidence})
    _write_json(design_dir / "draft.json", record)
    return {"design_id": design_id, "revision": record["revision"], "status": record["status"], "concept_count": len(normalized), "concept_manifest_hash": evidence["manifest_hash"], "visual_reference_hash": visual_reference_hash, "creative_range_status": "passed", "impact_review_status": "passed", "compelling_concept_count": compelling_count, "range_audit_status": "passed", "grammar_congruence_status": "passed", "journey_structure_status": "passed", "typography_family_count": len(typography_family_names), "art_direction_family_count": len(art_direction_family_names), "composition_family_count": len(composition_family_names), "page_grammar_count": len(page_grammar_ids), "interaction_motion_strategy_count": len(interaction_strategy_ids), "minimum_journey_stage_count": minimum_journey_stage_count, "concept_forming_media_count": concept_forming_media_count, "signature_stage_coverage_minimum": signature_stage_minimum, "per_concept_runtime_probes": True, "comparison_depth_coverage": True, "generated_media_extraction_passed": True, "portfolio_report_hash": portfolio["report_hash"] if portfolio else None, "prior_output_challenge_status": normalized_prior_challenge["status"] if normalized_prior_challenge else None, "generative_laboratory_hash": laboratory.get("laboratory_hash"), "reference_translation_hash": (reference_translation or {}).get("report_hash"), "slop_ruleset_version": design_slop.RULESET_VERSION, "execution_authorized": False}


def improvement_cycle(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    """Validate and persist one resumable design-improvement cycle without granting authority."""
    _enabled(config)
    payload = _read_json(manifest_path)
    if payload.get("schema_version") != 1:
        raise DesignError("Design improvement cycles require schema_version 1")
    cycle_id = _identifier(str(payload.get("cycle_id", "")), "design improvement cycle ID")
    design_id = _identifier(str(payload.get("design_id", "")), "design ID")
    mode = payload.get("mode", "artifact-refinement")
    if mode not in {"artifact-refinement", "fresh-design-experiments"}:
        raise DesignError("Design improvement cycles require a supported mode")
    objective = payload.get("objective")
    max_passes = payload.get("max_passes")
    if not isinstance(objective, str) or not objective.strip() or not isinstance(max_passes, int) or not 1 <= max_passes <= 8:
        raise DesignError("Design improvement cycles require an objective and one to eight maximum passes")
    source = payload.get("source")
    if (
        not isinstance(source, dict) or set(source) != {"branch", "commit", "skill_sha256"}
        or not isinstance(source["branch"], str) or not source["branch"].strip()
        or not re.fullmatch(r"[a-f0-9]{40}", str(source["commit"]))
        or not re.fullmatch(r"[a-f0-9]{64}", str(source["skill_sha256"]))
    ):
        raise DesignError("Design improvement cycles require an exact branch, commit, and skill hash")

    def verified_artifact(value: Any, label: str, suffixes: set[str] | None = None) -> dict[str, str]:
        if not isinstance(value, dict):
            raise DesignError(f"{label} requires a hash-bound artifact")
        relative, path = _artifact_relative_path(root, value.get("path"))
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if not actual or value.get("sha256") != actual or (suffixes is not None and path.suffix.lower() not in suffixes):
            raise DesignError(f"{label} is missing or changed: {relative}")
        return {"path": relative, "sha256": actual}

    baseline = payload.get("baseline")
    if not isinstance(baseline, dict):
        raise DesignError("Design improvement cycles require a baseline evaluation and self-assessment")
    baseline_evaluation = verified_artifact(baseline.get("benchmark_evaluation"), "Baseline benchmark evaluation", {".json"})
    baseline_assessment = verified_artifact(baseline.get("self_assessment"), "Baseline self-assessment", {".json", ".md"})
    passes = payload.get("passes")
    if not isinstance(passes, list) or len(passes) > max_passes:
        raise DesignError("Design improvement cycle passes must be an array within max_passes")
    normalized_passes: list[dict[str, Any]] = []
    previous_status: str | None = None
    experiment_hashes: dict[str, set[str]] = {
        key: set() for key in ("brief", "research", "moodboard", "generative_laboratory", "concept_manifest", "comparison")
    }
    experiment_seeds: set[tuple[str, str, str, str]] = set()
    experiment_reference_sets: list[frozenset[str]] = []
    for index, item in enumerate(passes, 1):
        if not isinstance(item, dict) or item.get("pass_number") != index or item.get("status") not in IMPROVEMENT_PASS_STATUSES:
            raise DesignError("Design improvement passes must be sequential and use supported statuses")
        status = item["status"]
        if mode == "artifact-refinement" and previous_status not in {None, "changes-requested"}:
            raise DesignError("A new improvement pass can start only after human-requested changes")
        experiment: dict[str, Any] | None = None
        if mode == "fresh-design-experiments":
            raw_experiment = item.get("experiment")
            if not isinstance(raw_experiment, dict):
                raise DesignError(f"Fresh-design pass {index} requires experiment evidence")
            experiment_id = _identifier(str(raw_experiment.get("experiment_id", "")), "design experiment ID")
            experiment_source = raw_experiment.get("source")
            if (
                not isinstance(experiment_source, dict)
                or set(experiment_source) != {"commit", "skill_sha256"}
                or not re.fullmatch(r"[a-f0-9]{40}", str(experiment_source.get("commit", "")))
                or not re.fullmatch(r"[a-f0-9]{64}", str(experiment_source.get("skill_sha256", "")))
            ):
                raise DesignError(f"Fresh-design pass {index} requires an exact source commit and skill hash")
            artifacts: dict[str, dict[str, str]] = {}
            for key, suffixes in {
                "brief": {".json", ".md"}, "research": {".json"}, "moodboard": {".html"},
                "generative_laboratory": {".json"}, "concept_manifest": {".json"}, "comparison": {".html"},
            }.items():
                artifact = verified_artifact(raw_experiment.get(key), f"Fresh-design pass {index} {key.replace('_', ' ')}", suffixes)
                if artifact["sha256"] in experiment_hashes[key]:
                    raise DesignError(f"Fresh-design pass {index} must use a new {key.replace('_', ' ')}")
                experiment_hashes[key].add(artifact["sha256"])
                artifacts[key] = artifact
            seed = raw_experiment.get("creative_seed")
            seed_keys = ("audience", "posture", "hero_mechanism", "reference_category")
            if not isinstance(seed, dict) or set(seed) != set(seed_keys) or any(not isinstance(seed.get(key), str) or not seed[key].strip() for key in seed_keys):
                raise DesignError(f"Fresh-design pass {index} requires a complete creative seed")
            normalized_seed = {key: seed[key].strip() for key in seed_keys}
            seed_tuple = tuple(normalized_seed[key].lower() for key in seed_keys)
            if seed_tuple in experiment_seeds:
                raise DesignError(f"Fresh-design pass {index} must use a new creative seed")
            experiment_seeds.add(seed_tuple)
            reference_families = raw_experiment.get("reference_families")
            if (
                not isinstance(reference_families, list) or len(reference_families) < 2
                or any(not isinstance(value, str) or not value.strip() for value in reference_families)
            ):
                raise DesignError(f"Fresh-design pass {index} requires at least two reference families")
            normalized_references = [value.strip() for value in reference_families]
            reference_set = frozenset(value.lower() for value in normalized_references)
            if len(reference_set) != len(normalized_references) or reference_set in experiment_reference_sets:
                raise DesignError(f"Fresh-design pass {index} must use a distinct reference-family set")
            experiment_reference_sets.append(reference_set)
            novelty = raw_experiment.get("novelty_review")
            expected_comparisons = list(range(1, index))
            if not isinstance(novelty, dict) or novelty.get("compared_to_passes") != expected_comparisons:
                raise DesignError(f"Fresh-design pass {index} must compare against every prior experiment")
            changed_dimensions = novelty.get("changed_dimensions")
            conclusions = novelty.get("novel_conclusions")
            inherited = novelty.get("inherited_constraints")
            if (
                not isinstance(changed_dimensions, list) or len({str(value).strip().lower() for value in changed_dimensions}) < 5
                or any(not isinstance(value, str) or not value.strip() for value in changed_dimensions)
                or not isinstance(conclusions, list) or not conclusions
                or any(not isinstance(value, str) or not value.strip() for value in conclusions)
                or not isinstance(inherited, list) or not inherited
                or any(not isinstance(value, str) or not value.strip() for value in inherited)
            ):
                raise DesignError(f"Fresh-design pass {index} requires a concrete cross-cycle novelty review")
            moodboard_quality = raw_experiment.get("moodboard_quality")
            concept_mechanics = raw_experiment.get("concept_mechanics")
            normalized_quality: dict[str, Any] | None = None
            normalized_mechanics: list[dict[str, Any]] = []
            if index > 1:
                if not isinstance(moodboard_quality, dict):
                    raise DesignError(f"Fresh-design pass {index} requires moodboard capture-quality evidence")
                tile_count = moodboard_quality.get("tile_count")
                direct_count = moodboard_quality.get("direct_reference_tile_count")
                clear_count = moodboard_quality.get("clear_tile_count")
                focal_crop_count = moodboard_quality.get("focal_crop_count")
                unresolved = moodboard_quality.get("unresolved_weak_tile_ids")
                if (
                    not isinstance(tile_count, int) or tile_count < 8
                    or not isinstance(direct_count, int) or direct_count < 2 or direct_count > tile_count
                    or not isinstance(clear_count, int) or clear_count > tile_count or clear_count / tile_count < 0.8
                    or unresolved != []
                    or not isinstance(moodboard_quality.get("reviewer"), str) or not moodboard_quality["reviewer"].strip()
                    or not isinstance(moodboard_quality.get("reviewed_at"), str) or not moodboard_quality["reviewed_at"].strip()
                ):
                    raise DesignError(f"Fresh-design pass {index} moodboard contains unresolved or unclear captures")
                if index > 2 and (
                    not isinstance(focal_crop_count, int)
                    or focal_crop_count > direct_count
                    or focal_crop_count / direct_count < 0.8
                ):
                    raise DesignError(f"Fresh-design pass {index} moodboard requires strong focal crops for direct references")
                normalized_quality = {
                    "tile_count": tile_count, "direct_reference_tile_count": direct_count,
                    "clear_tile_count": clear_count, "unresolved_weak_tile_ids": [],
                    "focal_crop_count": focal_crop_count if index > 2 else None,
                    "reviewer": moodboard_quality["reviewer"].strip(), "reviewed_at": moodboard_quality["reviewed_at"].strip(),
                }
                if not isinstance(concept_mechanics, list) or len(concept_mechanics) < 3:
                    raise DesignError(f"Fresh-design pass {index} requires unique concept-mechanic evidence")
                mechanic_ids: set[str] = set()
                interaction_ids: set[str] = set()
                for mechanic in concept_mechanics:
                    fields = ("concept_id", "metaphor", "unique_interaction", "product_job")
                    if not isinstance(mechanic, dict) or any(not isinstance(mechanic.get(key), str) or not mechanic[key].strip() for key in fields):
                        raise DesignError(f"Fresh-design pass {index} concept mechanics are incomplete")
                    concept_id = _identifier(mechanic["concept_id"], "fresh-design concept ID")
                    interaction_id = mechanic["unique_interaction"].strip().lower()
                    if concept_id in mechanic_ids or interaction_id in interaction_ids:
                        raise DesignError(f"Fresh-design pass {index} concepts must enable different interactions")
                    mechanic_ids.add(concept_id)
                    interaction_ids.add(interaction_id)
                    journey_roles = mechanic.get("journey_roles", [])
                    if index > 2 and (
                        not isinstance(journey_roles, list)
                        or len({str(value).strip().lower() for value in journey_roles}) < 3
                        or any(not isinstance(value, str) or not value.strip() for value in journey_roles)
                    ):
                        raise DesignError(f"Fresh-design pass {index} concept interactions must survive at least three journey roles")
                    normalized_mechanics.append({
                        "concept_id": concept_id,
                        **{key: mechanic[key].strip() for key in fields[1:]},
                        "journey_roles": [value.strip() for value in journey_roles],
                    })
            house_tell_review: dict[str, Any] | None = None
            category_reflex_review: dict[str, Any] | None = None
            if index > 2:
                required_dimensions = {"typography", "media", "composition", "page grammar", "interaction", "emotional register"}
                actual_dimensions = {str(value).strip().lower() for value in changed_dimensions}
                if not required_dimensions <= actual_dimensions:
                    raise DesignError(f"Fresh-design pass {index} must change the full design system against prior experiments")
                raw_house_tells = raw_experiment.get("house_tell_review")
                if not isinstance(raw_house_tells, dict) or raw_house_tells.get("compared_to_passes") != expected_comparisons:
                    raise DesignError(f"Fresh-design pass {index} requires a house-tell review against every prior experiment")
                avoided_tells = raw_house_tells.get("avoided_tells")
                recurring_tells = raw_house_tells.get("recurring_tells")
                justified = raw_house_tells.get("justified_recurrences")
                if (
                    not isinstance(avoided_tells, list) or not avoided_tells
                    or any(not isinstance(value, str) or not value.strip() for value in avoided_tells)
                    or not isinstance(recurring_tells, list)
                    or any(not isinstance(value, str) or not value.strip() for value in recurring_tells)
                    or not isinstance(justified, list)
                    or any(not isinstance(value, str) or not value.strip() for value in justified)
                    or not isinstance(raw_house_tells.get("reviewer"), str) or not raw_house_tells["reviewer"].strip()
                    or not isinstance(raw_house_tells.get("reviewed_at"), str) or not raw_house_tells["reviewed_at"].strip()
                ):
                    raise DesignError(f"Fresh-design pass {index} house-tell review is incomplete")
                if recurring_tells and not justified:
                    raise DesignError(f"Fresh-design pass {index} must justify every recurring house tell")
                house_tell_review = {
                    "compared_to_passes": expected_comparisons,
                    "avoided_tells": [value.strip() for value in avoided_tells],
                    "recurring_tells": [value.strip() for value in recurring_tells],
                    "justified_recurrences": [value.strip() for value in justified],
                    "reviewer": raw_house_tells["reviewer"].strip(),
                    "reviewed_at": raw_house_tells["reviewed_at"].strip(),
                }
                raw_category_reflexes = raw_experiment.get("category_reflex_review")
                if not isinstance(raw_category_reflexes, dict):
                    raise DesignError(f"Fresh-design pass {index} requires a reference-category reflex review")
                category_defaults = raw_category_reflexes.get("category_defaults")
                avoided_defaults = raw_category_reflexes.get("avoided_defaults")
                intentional_risks = raw_category_reflexes.get("intentional_risks")
                if (
                    not isinstance(category_defaults, list) or len(category_defaults) < 2
                    or any(not isinstance(value, str) or not value.strip() for value in category_defaults)
                    or not isinstance(avoided_defaults, list)
                    or any(not isinstance(value, str) or not value.strip() for value in avoided_defaults)
                    or not isinstance(intentional_risks, list)
                    or not isinstance(raw_category_reflexes.get("reviewer"), str) or not raw_category_reflexes["reviewer"].strip()
                    or not isinstance(raw_category_reflexes.get("reviewed_at"), str) or not raw_category_reflexes["reviewed_at"].strip()
                ):
                    raise DesignError(f"Fresh-design pass {index} reference-category reflex review is incomplete")
                default_ids = {value.strip().lower() for value in category_defaults}
                disposition_ids = {value.strip().lower() for value in avoided_defaults}
                normalized_risks = []
                for risk in intentional_risks:
                    if (
                        not isinstance(risk, dict)
                        or any(not isinstance(risk.get(key), str) or not risk[key].strip() for key in ("pattern", "rationale", "product_job"))
                    ):
                        raise DesignError(f"Fresh-design pass {index} intentional category risks require rationale and product jobs")
                    disposition_ids.add(risk["pattern"].strip().lower())
                    normalized_risks.append({key: risk[key].strip() for key in ("pattern", "rationale", "product_job")})
                if disposition_ids != default_ids:
                    raise DesignError(f"Fresh-design pass {index} must disposition every reference-category default")
                category_reflex_review = {
                    "category_defaults": [value.strip() for value in category_defaults],
                    "avoided_defaults": [value.strip() for value in avoided_defaults],
                    "intentional_risks": normalized_risks,
                    "reviewer": raw_category_reflexes["reviewer"].strip(),
                    "reviewed_at": raw_category_reflexes["reviewed_at"].strip(),
                }
            experiment = {
                "experiment_id": experiment_id,
                "source": experiment_source,
                **artifacts,
                "creative_seed": normalized_seed,
                "reference_families": normalized_references,
                "moodboard_quality": normalized_quality,
                "concept_mechanics": normalized_mechanics,
                "house_tell_review": house_tell_review,
                "category_reflex_review": category_reflex_review,
                "novelty_review": {
                    "compared_to_passes": expected_comparisons,
                    "changed_dimensions": changed_dimensions,
                    "inherited_constraints": inherited,
                    "novel_conclusions": conclusions,
                },
            }
        findings = item.get("findings")
        if not isinstance(findings, list) or not findings:
            raise DesignError(f"Improvement pass {index} requires concrete findings")
        normalized_findings: list[dict[str, str]] = []
        finding_ids: set[str] = set()
        for finding in findings:
            if not isinstance(finding, dict):
                raise DesignError("Improvement findings must be objects")
            finding_id = _identifier(str(finding.get("finding_id", "")), "improvement finding ID")
            fields = ("category", "observation", "action", "success_metric")
            if finding_id in finding_ids or any(not isinstance(finding.get(key), str) or not finding[key].strip() for key in fields):
                raise DesignError("Improvement findings require unique IDs, observations, actions, and success metrics")
            normalized_findings.append({"finding_id": finding_id, **{key: finding[key].strip() for key in fields}})
            finding_ids.add(finding_id)
        changes = item.get("changes", [])
        if status != "planned" and (not isinstance(changes, list) or not changes):
            raise DesignError(f"Improvement pass {index} status {status} requires implemented changes")
        normalized_changes: list[dict[str, Any]] = []
        for change in changes:
            linked = change.get("finding_ids") if isinstance(change, dict) else None
            description = change.get("description") if isinstance(change, dict) else None
            artifacts = change.get("artifacts") if isinstance(change, dict) else None
            if not isinstance(linked, list) or not linked or not set(linked) <= finding_ids or not isinstance(description, str) or not description.strip() or not isinstance(artifacts, list):
                raise DesignError("Improvement changes must bind findings, description, and artifacts")
            normalized_changes.append({"finding_ids": linked, "description": description.strip(), "artifacts": [verified_artifact(artifact, "Improvement change artifact") for artifact in artifacts]})
        validation = item.get("validation")
        normalized_validation: dict[str, Any] | None = None
        if status in {"validated", "awaiting-human", "accepted", "changes-requested"}:
            if not isinstance(validation, dict) or validation.get("passed") is not True:
                raise DesignError(f"Improvement pass {index} requires passed validation before human review")
            evaluation = verified_artifact(validation.get("benchmark_evaluation"), "Improvement benchmark evaluation", {".json"})
            assessment = verified_artifact(validation.get("self_assessment"), "Improvement self-assessment", {".json", ".md"})
            evaluation_value = _read_json(root / evaluation["path"])
            if evaluation_value.get("stage_valid") is not True:
                raise DesignError("Improvement benchmark evaluation must be stage-valid")
            source_tests = validation.get("source_tests")
            if not isinstance(source_tests, list) or not source_tests or any(not isinstance(test, dict) or test.get("status") != "passed" or not isinstance(test.get("name"), str) or not test["name"].strip() for test in source_tests):
                raise DesignError("Improvement validation requires named passing source tests")
            normalized_validation = {"passed": True, "benchmark_evaluation": evaluation, "self_assessment": assessment, "source_tests": source_tests}
        human_gate = item.get("human_gate")
        if not isinstance(human_gate, dict) or human_gate.get("required") is not True or human_gate.get("status") not in {"pending", "accepted", "changes-requested"}:
            raise DesignError("Every improvement pass requires an explicit human gate")
        if status in {"accepted", "changes-requested"}:
            if human_gate.get("status") != status or human_gate.get("actor_type") != "human" or not isinstance(human_gate.get("actor"), str) or not human_gate["actor"].strip():
                raise DesignError("Accepted or changes-requested passes require an identified human disposition")
        elif human_gate.get("status") != "pending":
            raise DesignError("Unfinished improvement passes must keep the human gate pending")
        normalized_passes.append({"pass_number": index, "status": status, "experiment": experiment, "findings": normalized_findings, "changes": normalized_changes, "validation": normalized_validation, "human_gate": human_gate})
        previous_status = status
    if not normalized_passes:
        status = "active"
        next_gate = "diagnose-and-plan-pass-1"
    else:
        last = normalized_passes[-1]
        status = "complete" if last["status"] == "accepted" else "active"
        if mode == "fresh-design-experiments" and last["status"] == "awaiting-human":
            next_gate = "human-cross-cycle-review" if len(normalized_passes) >= max_passes else f"diagnose-and-run-experiment-{len(normalized_passes) + 1}"
        else:
            next_gate = {
                "planned": "implement-pass",
                "implemented": "validate-pass",
                "validated": "human-feedback",
                "awaiting-human": "human-feedback",
                "changes-requested": "cycle-limit-reached" if len(normalized_passes) >= max_passes else f"diagnose-and-plan-pass-{len(normalized_passes) + 1}",
                "accepted": "complete",
            }[last["status"]]
    normalized = {
        "schema_version": 1, "cycle_id": cycle_id, "design_id": design_id,
        "objective": objective.strip(), "max_passes": max_passes, "mode": mode, "source": source,
        "baseline": {"benchmark_evaluation": baseline_evaluation, "self_assessment": baseline_assessment},
        "passes": normalized_passes, "status": status, "next_gate": next_gate,
        "updated_at": _now(), "execution_authorized": False,
    }
    normalized["cycle_hash"] = _canonical_hash(normalized)
    relative = Path(config.get("private_dir", ".continuity/private")) / "design" / "cycles" / cycle_id / "cycle.json"
    _write_json(root / relative, normalized)
    return {"cycle_id": cycle_id, "mode": mode, "status": status, "pass_count": len(normalized_passes), "max_passes": max_passes, "next_gate": next_gate, "cycle_hash": normalized["cycle_hash"], "record_path": relative.as_posix(), "execution_authorized": False}


def feedback_record(root: Path, config: dict[str, Any], design_id: str, input_path: Path) -> dict[str, Any]:
    _enabled(config)
    design_id = _identifier(design_id, "design ID")
    design_dir = root / config.get("private_dir", ".continuity/private") / "design" / design_id
    record = _read_json(design_dir / "draft.json")
    if record.get("status") not in {"awaiting-feedback", "refining", "awaiting-selection", "awaiting-approval", "approved"} or not record.get("concept_evidence"):
        raise DesignError("Design does not have a validated concept set for feedback")
    if not record["concept_evidence"].get("validated"):
        raise DesignError("Feedback requires refreshed concept and slop evidence for the current revision")
    payload = _read_json(input_path)
    reactions = payload.get("reactions")
    if not isinstance(reactions, list) or not reactions:
        raise DesignError("Feedback requires at least one numbered visual reaction")
    normalized: list[dict[str, str]] = []
    for item in reactions:
        if not isinstance(item, dict) or item.get("reaction") not in FEEDBACK_REACTIONS:
            raise DesignError("Each feedback reaction must be keep, change, avoid, or uncertain")
        element_id = item.get("element_id")
        why = item.get("why")
        if not isinstance(element_id, str) or not element_id.strip() or not isinstance(why, str) or not why.strip():
            raise DesignError("Each feedback reaction requires a numbered element_id and why")
        if not re.match(r"^\d+(?:[.:-][A-Za-z0-9._-]+)?$", element_id.strip()):
            raise DesignError("Feedback element_id must begin with its visible number")
        normalized.append({"element_id": element_id.strip(), "reaction": item["reaction"], "why": why.strip(), "user_language": str(item.get("user_language", why)).strip()})
    contract_changed = payload.get("contract_changed", False)
    ready = payload.get("ready_for_selection", False)
    if not isinstance(contract_changed, bool) or not isinstance(ready, bool) or (contract_changed and ready):
        raise DesignError("Feedback readiness and contract_changed flags are invalid")
    requested_change = any(item["reaction"] in {"change", "avoid"} for item in normalized)
    effective_contract_change = contract_changed or requested_change
    if effective_contract_change and ready:
        raise DesignError("Material visual feedback cannot be ready for selection until refreshed evidence passes")
    material_feedback = effective_contract_change
    visual_delta = payload.get("visual_delta", {})
    if material_feedback:
        if not isinstance(visual_delta, dict):
            raise DesignError("Material feedback requires a visual_delta object")
        for key in ("changed", "stayed", "why"):
            values = visual_delta.get(key)
            if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
                raise DesignError(f"Material feedback visual_delta requires {key}")
        relative, delta_path = _artifact_relative_path(root, visual_delta.get("path"))
        if not delta_path.is_file() or visual_delta.get("sha256") != hashlib.sha256(delta_path.read_bytes()).hexdigest():
            raise DesignError("Visual delta evidence is missing or changed")
        visual_delta = {"changed": visual_delta["changed"], "stayed": visual_delta["stayed"], "why": visual_delta["why"], "path": relative, "sha256": visual_delta["sha256"]}
    elif not isinstance(visual_delta, dict):
        raise DesignError("visual_delta must be an object")
    round_record = {
        "round": len(record.get("feedback_rounds", [])) + 1, "recorded_at": _now(),
        "actor": str(payload.get("actor", "user")), "reactions": normalized,
        "visual_delta": visual_delta, "contract_changed": effective_contract_change,
        "contract_change_declared": contract_changed, "ready_for_selection": ready,
    }
    if effective_contract_change:
        previous_revision = record["revision"]
        archive = design_dir / "revisions" / f"v{previous_revision}"
        if archive.exists():
            raise DesignError("Design revision archive already exists")
        archive.mkdir(parents=True)
        shutil.copy2(design_dir / "draft.json", archive / "draft.json")
        for name in ("design.md", "approval.json"):
            path = design_dir / name
            if path.exists():
                shutil.copy2(path, archive / name)
                path.unlink()
        record["revision"] = previous_revision + 1
        record["status"] = "refining"
        record["selected_direction_ids"] = []
        record.pop("design_hash", None)
        record.pop("approval_bundle_hash", None)
        record["concept_evidence"]["validated"] = False
        record["concept_evidence"]["invalidated_by_feedback_round"] = round_record["round"]
    elif ready:
        if not record["concept_evidence"].get("validated"):
            raise DesignError("Stale concept and slop evidence cannot be marked ready for selection")
        record["status"] = "awaiting-selection"
    else:
        record["status"] = "refining"
    record.setdefault("feedback_rounds", []).append(round_record)
    decision_by_element = {
        item.get("element_id"): item
        for item in record.get("decision_register", [])
        if isinstance(item, dict) and isinstance(item.get("element_id"), str)
    }
    for reaction in normalized:
        disposition = {
            "keep": "accepted", "change": "unresolved-change", "avoid": "rejected", "uncertain": "unresolved",
        }[reaction["reaction"]]
        decision_by_element[reaction["element_id"]] = {
            "element_id": reaction["element_id"], "disposition": disposition,
            "reason": reaction["why"], "user_language": reaction["user_language"], "round": round_record["round"],
        }
        if reaction["reaction"] == "avoid":
            record.setdefault("rejected_decisions", []).append({"element_id": reaction["element_id"], "reason": reaction["why"], "round": round_record["round"]})
    record["decision_register"] = list(decision_by_element.values())
    _write_json(design_dir / "draft.json", record)
    return {"design_id": design_id, "revision": record["revision"], "status": record["status"], "feedback_round": round_record["round"], "slop_evidence_valid": bool(record["concept_evidence"].get("validated")), "execution_authorized": False}


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 45 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise DesignError(f"Invalid PNG artifact: {path}")
    offset = 8
    width = height = 0
    saw_ihdr = saw_idat = saw_iend = False
    compressed = bytearray()
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk_start = offset + 8
        chunk_end = chunk_start + length
        crc_end = chunk_end + 4
        if crc_end > len(data):
            raise DesignError(f"Invalid PNG chunk bounds: {path}")
        chunk = data[chunk_start:chunk_end]
        expected_crc = struct.unpack(">I", data[chunk_end:crc_end])[0]
        if zlib.crc32(chunk_type + chunk) & 0xFFFFFFFF != expected_crc:
            raise DesignError(f"Invalid PNG checksum: {path}")
        if chunk_type == b"IHDR":
            if saw_ihdr or offset != 8 or length != 13:
                raise DesignError(f"Invalid PNG header: {path}")
            width, height = struct.unpack(">II", chunk[:8])
            if width < 1 or height < 1:
                raise DesignError(f"Invalid PNG dimensions: {path}")
            saw_ihdr = True
        elif chunk_type == b"IDAT":
            saw_idat = True
            compressed.extend(chunk)
        elif chunk_type == b"IEND":
            if length != 0:
                raise DesignError(f"Invalid PNG end chunk: {path}")
            saw_iend = True
            offset = crc_end
            break
        offset = crc_end
    if not (saw_ihdr and saw_idat and saw_iend) or offset != len(data):
        raise DesignError(f"Incomplete PNG artifact: {path}")
    try:
        if not zlib.decompress(bytes(compressed)):
            raise ValueError("empty image data")
    except zlib.error as exc:
        raise DesignError(f"Invalid PNG image data: {path}") from exc
    return width, height


def _validate_artifact_against_record(root: Path, manifest: dict[str, Any], approved: dict[str, Any], *, candidate: bool) -> dict[str, Any]:
    for key in ("design_id", "revision", "design_hash"):
        if manifest.get(key) != approved.get(key):
            raise DesignError(f"Artifact manifest {key} does not match the approved design")
    approval_bundle = approved.get("approval_bundle", {})
    for key in ("typographic_transfer_hashes", "composition_asset_plan_hashes"):
        if key in approval_bundle and manifest.get(key) != approval_bundle[key]:
            raise DesignError(f"Artifact manifest {key} does not preserve the selected composition and type evidence")
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
    if "typographic_transfer_hashes" in approval_bundle:
        current_probe = _verified_reference_file(root, manifest.get("fidelity_runtime_probe"), "Artifact composition and typography browser probe", {".json"})
        if not any(item["path"] == current_probe["path"] and item["sha256"] == current_probe["sha256"] for item in verified_files):
            raise DesignError("Artifact fidelity runtime probe must be one of the manifest's hash-bound files")
        _, current_probe_path = _artifact_relative_path(root, current_probe["path"])
        current_probe_value = _read_json(current_probe_path)
        target_file = next((
            item
            for item in verified_files
            if item["media_type"] == "text/html"
            and current_probe_value.get("target_document_path") == item["path"]
            and current_probe_value.get("target_document_sha256") == _document_probe_fingerprint(root / item["path"])
        ), None)
        target_document = None
        if target_file is not None:
            closure_paths = {
                item.relative_to(root.resolve()).as_posix()
                for item in _runtime_source_closure(root, root / target_file["path"])
            }
            declared_runtime_sources = [item for item in verified_files if item["path"] in closure_paths]
            runtime_source_bundle = _verified_runtime_source_bundle(
                root, root / target_file["path"], declared_runtime_sources, "Artifact fidelity",
            )
            target_document = {
                "path": target_file["path"],
                "sha256": runtime_source_bundle["target_document_sha256"],
                "source_bundle_sha256": runtime_source_bundle["source_bundle_sha256"],
            }
        if (
            target_document is None
            or current_probe_value.get("source_bundle_sha256") != target_document["source_bundle_sha256"]
            or not isinstance(current_probe_value.get("document_url"), str)
            or not current_probe_value["document_url"].split("?", 1)[0].endswith(target_document["path"])
        ):
            raise DesignError("Artifact fidelity runtime probe is stale for the current HTML artifact")
        contract = approved.get("alignment_contract", {})
        concept_evidence = contract.get("concept_evidence") if isinstance(contract, dict) else None
        selected_ids = contract.get("selected_direction_ids", []) if isinstance(contract, dict) else []
        selected_concepts = [
            item for item in concept_evidence.get("concepts", [])
            if isinstance(item, dict) and item.get("direction_id") in selected_ids
        ] if isinstance(concept_evidence, dict) else []
        if not selected_concepts:
            raise DesignError("Artifact fidelity validation requires the selected concept contract")
        for concept in selected_concepts:
            transfer = dict(concept["typographic_transfer"])
            transfer["render_probe"] = current_probe
            validated_transfer = _validate_typographic_transfer(
                root, concept["concept_id"], transfer, "", concept["typographic_transfer"]["reference_render_probe"], target_document,
            )
            _validate_composition_asset_plan(
                root, concept["concept_id"], concept["composition_asset_plan"], "",
                validated_transfer["type_media_relation"], current_probe,
            )
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
    content_claims = manifest.get("content_claims", [])
    if not isinstance(content_claims, list):
        raise DesignError("Artifact content_claims must be an array")
    provenance = {
        item.get("content_id"): item
        for item in approved.get("alignment_contract", {}).get("content_provenance", [])
        if isinstance(item, dict)
    }
    for claim in content_claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("claim"), str) or not claim["claim"].strip():
            raise DesignError("Artifact content claim is invalid")
        provenance_ids = _string_list(claim.get("provenance_ids"), "artifact content claim provenance_ids", required=True)
        evidence_refs = _string_list(claim.get("evidence_refs"), "artifact content claim evidence_refs", required=True)
        qualification = claim.get("visible_qualification", "")
        if not isinstance(qualification, str):
            raise DesignError("Artifact content claim visible_qualification must be text")
        if set(provenance_ids) - set(provenance):
            raise DesignError("Artifact content claim references unknown provenance IDs")
        for reference in evidence_refs:
            file_ref = reference.split("#", 1)[0]
            if file_ref not in file_paths:
                raise DesignError("Artifact content claim evidence must reference a bound artifact file")
        classifications = {provenance[item]["classification"] for item in provenance_ids}
        if classifications & {"illustrative", "inferred"} and not qualification.strip():
            raise DesignError("Illustrative or inferred artifact claims require a visible qualification")
        if qualification.strip():
            html_evidence = [
                html_texts[file_ref]
                for file_ref in {ref.split("#", 1)[0] for ref in evidence_refs}
                if file_ref in html_texts
            ]
            if html_evidence and not any(qualification.strip() in text for text in html_evidence):
                raise DesignError("Artifact content claim qualification is not visible in its HTML evidence")
        if claim.get("presentation") == "verified" and classifications != {"inspected"}:
            raise DesignError("Verified artifact claims require inspected content provenance")
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
    slop_evidence: dict[str, Any] | None = None
    if manifest.get("schema_version", 1) in {2, 3}:
        contract = approved.get("alignment_contract", {})
        for field, value in (
            ("implementation_context_hash", contract.get("implementation_context")),
            ("component_map_hash", contract.get("component_map", [])),
            ("asset_strategy_hash", contract.get("asset_strategy", [])),
        ):
            expected = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if manifest.get(field) != expected:
                raise DesignError(f"Artifact manifest {field} does not match the design contract")
        if maturity == "implementation-facing" and html_texts:
            missing_quality = WEB_ARTIFACT_QUALITY_SCENARIOS - set(validation_by_scenario)
            failed_quality = sorted(
                scenario for scenario in WEB_ARTIFACT_QUALITY_SCENARIOS
                if validation_by_scenario.get(scenario, {}).get("status") != "passed"
            )
            if missing_quality:
                raise DesignError(f"Implementation-facing web artifacts lack quality results: {sorted(missing_quality)}")
            if failed_quality:
                raise DesignError(f"Implementation-facing web artifact quality checks did not pass: {failed_quality}")
        if maturity == "implementation-facing" and fixture_data != "none" and not content_claims:
            raise DesignError("Implementation-facing fixture content requires artifact content claims bound to provenance")
        required_states = {
            state
            for component in contract.get("component_map", [])
            for state in component.get("required_states", [])
        }
        missing_component_states = sorted(required_states - set(manifest.get("demonstrated_states", [])))
        if maturity == "implementation-facing" and missing_component_states:
            raise DesignError(f"Artifact is missing required component states: {missing_component_states}")
        asset_resolutions = manifest.get("asset_resolutions", [])
        if not isinstance(asset_resolutions, list):
            raise DesignError("Artifact asset_resolutions must be an array")
        resolution_by_id: dict[str, dict[str, Any]] = {}
        for item in asset_resolutions:
            if not isinstance(item, dict) or item.get("status") not in ASSET_RESOLUTION_STATUSES:
                raise DesignError("Artifact asset resolution is invalid")
            asset_id = _identifier(str(item.get("asset_id", "")), "asset resolution ID")
            evidence_refs = _string_list(item.get("evidence_refs"), f"asset resolution {asset_id} evidence_refs")
            if asset_id in resolution_by_id:
                raise DesignError("Artifact asset resolution IDs must be unique")
            for reference in evidence_refs:
                if reference.split("#", 1)[0] not in file_paths:
                    raise DesignError("Asset resolution evidence must reference a bound artifact file")
            if item["status"] == "resolved" and not evidence_refs:
                raise DesignError(f"Resolved asset {asset_id} requires artifact evidence")
            resolution_by_id[asset_id] = {"asset_id": asset_id, "status": item["status"], "evidence_refs": evidence_refs}
        contract_assets = {item.get("asset_id"): item for item in contract.get("asset_strategy", [])}
        if maturity == "implementation-facing":
            if set(contract_assets) != set(resolution_by_id):
                raise DesignError("Implementation-facing artifacts must resolve every design asset")
            if any(item["status"] == "blocked" for item in resolution_by_id.values()):
                raise DesignError("Implementation-facing artifacts cannot retain blocked assets")
            for asset_id, asset in contract_assets.items():
                expected_status = "deliberately-omitted" if asset.get("source") == "deliberately-omitted" else "resolved"
                if resolution_by_id[asset_id]["status"] != expected_status:
                    raise DesignError(f"Artifact asset resolution conflicts with the design strategy: {asset_id}")
        completion = contract.get("completion_contract")
        if maturity == "implementation-facing" and isinstance(completion, dict) and completion.get("artifact_critique_required"):
            if not isinstance(manifest.get("artifact_critique_revision"), int) or manifest["artifact_critique_revision"] < 1:
                raise DesignError("Implementation-facing complete prototypes require an artifact critique revision")
            required_roles = set(completion.get("required_viewports", []))
            if required_roles - screenshot_roles:
                raise DesignError("Artifact is missing completion-contract viewport captures")
            if set(completion.get("required_states", [])) - set(manifest.get("demonstrated_states", [])):
                raise DesignError("Artifact is missing completion-contract states")
    if manifest.get("schema_version", 1) == 3:
        if manifest.get("approval_bundle_hash") != approved.get("approval_bundle_hash"):
            raise DesignError("Artifact approval_bundle_hash does not match the approved design")
        stage = "prototype" if candidate else "implementation"
        slop_evidence = _verified_private_report(root, manifest.get("slop_report"), stage=stage)
        _, report_path = _artifact_relative_path(root, slop_evidence["path"])
        report = _read_json(report_path)
        for item in report.get("files", []):
            relative, scanned_path = _artifact_relative_path(root, item.get("path"))
            if not scanned_path.is_file() or hashlib.sha256(scanned_path.read_bytes()).hexdigest() != item.get("sha256"):
                raise DesignError(f"AI-slop report is stale for artifact file: {relative}")
        for key in ("design_id", "revision", "design_hash", "approval_bundle_hash"):
            if report.get(key) != manifest.get(key):
                raise DesignError(f"AI-slop report {key} does not match the artifact manifest")
        reviewed_visual_hashes = {
            artifact.get("sha256")
            for answer in report.get("visual_review", {}).values()
            if isinstance(answer, dict)
            for artifact in answer.get("evidence", [])
            if isinstance(artifact, dict)
        }
        artifact_screenshot_hashes = {
            item["sha256"] for item in verified_files if item["media_type"] == "image/png"
        }
        if artifact_screenshot_hashes and not artifact_screenshot_hashes <= reviewed_visual_hashes:
            raise DesignError("AI-slop visual review is not bound to every artifact screenshot")
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
        "ai_slop_check": slop_evidence,
        "missing_decided_insights": missing_decided_insights,
        "implementation_ready": maturity == "implementation-facing" and not readiness_problems,
        "candidate": candidate,
        "execution_authorized": False,
    }


def validate_artifact(root: Path, config: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    _enabled(config)
    manifest = _read_json(manifest_path)
    approved = _read_json(root / ".continuity" / "design.json")
    if approved.get("schema_version", 1) >= 2 and manifest.get("schema_version") != 3:
        raise DesignError("Schema v2 design approval requires a schema v3 artifact with AI-slop evidence")
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
        "content_provenance": draft.get("content_provenance", []),
        "implementation_context": draft.get("implementation_context"),
        "component_map": draft.get("component_map", []),
        "asset_strategy": draft.get("asset_strategy", []),
        "completion_contract": draft.get("completion_contract"),
        "selected_direction_ids": draft["selected_direction_ids"],
        "implementation_guidance": [rule for direction in selected for rule in direction["implementation_guidance"]],
    }
    candidate_record = {
        "design_id": draft["design_id"], "revision": draft["revision"], "design_hash": draft["design_hash"],
        "approval_bundle_hash": draft.get("approval_bundle_hash"),
        "approval_bundle": draft.get("approval_bundle", {}),
        "alignment_contract": {**alignment_contract, "concept_evidence": draft.get("concept_evidence")},
    }
    result = _validate_artifact_against_record(root, manifest, candidate_record, candidate=True)
    if draft.get("workflow_version", 1) >= 2:
        if manifest.get("schema_version") != 3 or not result.get("ai_slop_check"):
            raise DesignError("Creative-director prototype validation requires schema v3 AI-slop evidence")
        screenshot_roles = {
            item["role"] for item in result.get("verified_files", []) if item.get("media_type") == "image/png"
        }
        if not {"mobile", "tablet", "desktop"} <= screenshot_roles:
            raise DesignError("Creative-director prototype validation requires mobile, tablet, and desktop screenshots")
        draft["prototype_slop_evidence"] = result["ai_slop_check"]
        _write_json(design_dir / "draft.json", draft)
    return result
