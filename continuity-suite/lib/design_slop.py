"""Deterministic, network-free AI-slop inspection for design artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

RULESET_VERSION = "1.7.0"
SEVERITIES = {"info", "warning", "error", "critical"}
DISPOSITIONS = {"open", "resolved", "not-applicable", "accepted-intentional"}
SCANNABLE_SUFFIXES = {
    ".astro", ".css", ".html", ".htm", ".js", ".jsx", ".md", ".mjs",
    ".scss", ".svelte", ".ts", ".tsx", ".vue",
}
IGNORED_PARTS = {".git", ".next", "build", "coverage", "dist", "node_modules", "out", "vendor"}


RULES: dict[str, dict[str, str]] = {
    "CDS-H001": {"class": "hard-failure", "severity": "critical", "title": "Audible autoplay", "remediation": "Remove autoplay or make media muted and user-controlled."},
    "CDS-H002": {"class": "hard-failure", "severity": "error", "title": "Motion without fallback", "remediation": "Add reduced-motion and static fallbacks for motion-heavy output."},
    "CDS-H003": {"class": "hard-failure", "severity": "error", "title": "Content hidden pending JavaScript", "remediation": "Render primary content visibly before JavaScript or animation succeeds."},
    "CDS-H004": {"class": "hard-failure", "severity": "error", "title": "Unbounded transition", "remediation": "Transition only named properties with bounded duration."},
    "CDS-H005": {"class": "hard-failure", "severity": "error", "title": "Unbounded raw scroll work", "remediation": "Use passive bounded observation, requestAnimationFrame, or IntersectionObserver."},
    "CDS-H006": {"class": "hard-failure", "severity": "error", "title": "Unqualified illustrative claim", "remediation": "Add visible qualification and provenance for generated or illustrative claims."},
    "CDS-H007": {"class": "hard-failure", "severity": "critical", "title": "Third-party reference promoted", "remediation": "Keep third-party references private and replace the shipping asset with owned or licensed material."},
    "CDS-H008": {"class": "hard-failure", "severity": "error", "title": "Presentation claims lack provenance", "remediation": "Remove invented metrics or bind every factual, testimonial, customer, traction, and performance claim to current evidence with visible qualification."},
    "CDS-H009": {"class": "hard-failure", "severity": "error", "title": "Presentation capture evidence is invalid", "remediation": "Recapture every required viewport and slide, verify the encoded media type and dimensions, and rebuild the contact sheet from the verified individual frames."},
    "CDS-H010": {"class": "hard-failure", "severity": "error", "title": "Presentation copy or data is unreadable", "remediation": "Shorten the copy or change the composition so every title, body line, label, value, source, and qualification is visible, unclipped, sufficiently large, and contrast-safe on every slide and required viewport."},
    "CDS-D001": {"class": "default-risk", "severity": "warning", "title": "Reflexive purple-blue gradient", "remediation": "Explain the project-specific role or replace it with a palette derived from the approved identity."},
    "CDS-D002": {"class": "default-risk", "severity": "warning", "title": "Gradient headline text", "remediation": "Use hierarchy, language, or material treatment instead of default gradient display type."},
    "CDS-D003": {"class": "default-risk", "severity": "warning", "title": "Reflexive warm cream", "remediation": "Record why the warm neutral is specific to this project or choose an evidenced surface color."},
    "CDS-D004": {"class": "default-risk", "severity": "warning", "title": "Common model-default typeface", "remediation": "Record a project-specific typography rationale or select a more characteristic type system."},
    "CDS-D005": {"class": "default-risk", "severity": "warning", "title": "Decorative glass surface", "remediation": "Make the surface treatment communicate hierarchy or material, or remove it."},
    "CDS-D006": {"class": "default-risk", "severity": "warning", "title": "Uniform rounded containers", "remediation": "Use containers only where grouping is meaningful and vary structure by content role."},
    "CDS-D007": {"class": "default-risk", "severity": "warning", "title": "Generic bento grid", "remediation": "Derive the composition from information relationships rather than a fashionable template."},
    "CDS-D008": {"class": "default-risk", "severity": "warning", "title": "Repeated eyebrow labels", "remediation": "Remove redundant micro-labels or give them a real navigational or semantic function."},
    "CDS-D009": {"class": "default-risk", "severity": "warning", "title": "Meaningless numbered section", "remediation": "Use numbering only when sequence or reference has meaning."},
    "CDS-D010": {"class": "default-risk", "severity": "warning", "title": "Excessive centered composition", "remediation": "Use alignment that expresses the content structure and reading path."},
    "CDS-D011": {"class": "default-risk", "severity": "warning", "title": "Repeated fade-up reveal", "remediation": "Reserve motion for state or spatial continuity instead of applying one reveal everywhere."},
    "CDS-D012": {"class": "default-risk", "severity": "warning", "title": "Generic hero metrics", "remediation": "Show metrics only when they are decision-relevant, sourced, and structurally integrated."},
    "CDS-D013": {"class": "default-risk", "severity": "warning", "title": "Decorative glow", "remediation": "Use real material, light logic, or subject imagery instead of an ambient technology glow."},
    "CDS-D014": {"class": "default-risk", "severity": "warning", "title": "Interchangeable stock imagery", "remediation": "Use project-specific subject matter, owned imagery, or an explicit art-direction brief."},
    "CDS-D015": {"class": "default-risk", "severity": "warning", "title": "Generic promotional copy", "remediation": "Replace generic benefit language with concrete actions, evidence, and consequences."},
    "CDS-D016": {"class": "default-risk", "severity": "warning", "title": "Model-like em-dash cadence", "remediation": "Vary sentence structure and use punctuation that fits the project voice."},
    "CDS-D017": {"class": "default-risk", "severity": "warning", "title": "Fashionable counter-default", "remediation": "Demonstrate that the dark terminal or neon treatment belongs to this project rather than serving as an anti-SaaS reflex."},
    "CDS-D018": {"class": "default-risk", "severity": "warning", "title": "Interchangeable category identity", "remediation": "Derive the identity from project-specific subject matter, behavior, language, and evidence rather than a category template."},
    "CDS-D019": {"class": "default-risk", "severity": "warning", "title": "Cosmetic concept variation", "remediation": "Change the organizing idea, hierarchy, composition, interaction, or material system rather than only palette, type, or decoration."},
    "CDS-D020": {"class": "default-risk", "severity": "warning", "title": "Decoration without a job", "remediation": "Remove the decoration or identify the content, hierarchy, state, or subject relationship it communicates."},
    "CDS-D021": {"class": "default-risk", "severity": "warning", "title": "Primitive media substitution", "remediation": "Retain source-defining media or rebuild its material behavior; do not replace it with generic CSS shapes."},
    "CDS-D022": {"class": "default-risk", "severity": "warning", "title": "Reference energy loss", "remediation": "Restore the reference's defining scale, material, density, crop, or spatial relationship before styling details."},
    "CDS-D023": {"class": "default-risk", "severity": "warning", "title": "Template convergence", "remediation": "Rebuild the composition around the transferred constraints instead of a familiar hero-and-sections template."},
    "CDS-D024": {"class": "default-risk", "severity": "warning", "title": "Declared mechanic is not visible", "remediation": "Demonstrate the claimed mechanic in the rendered artifact or remove the unsupported claim."},
    "CDS-D025": {"class": "default-risk", "severity": "warning", "title": "Generated study discarded", "remediation": "Retain the useful generated media or translate its defining relationships into equally capable first-party execution."},
    "CDS-D026": {"class": "default-risk", "severity": "warning", "title": "Primary material demoted to backdrop", "remediation": "Restore the material or subject as the organizing element instead of laying generic display copy over it."},
    "CDS-D027": {"class": "default-risk", "severity": "warning", "title": "Typographic grammar substitution", "remediation": "Preserve the reference type's role, scale relationships, density, and anchoring before changing its identity."},
    "CDS-D028": {"class": "default-risk", "severity": "warning", "title": "Hybrid reference lacks exact baseline", "remediation": "Reconstruct each source separately before synthesizing shared mechanics."},
    "CDS-D029": {"class": "default-risk", "severity": "warning", "title": "Fidelity is self-certified", "remediation": "Use a reviewer distinct from the preparer and bind findings to the combined visual comparison."},
    "CDS-D030": {"class": "default-risk", "severity": "warning", "title": "Mobile comparison is incomplete", "remediation": "Show source, reconstruction, literal substitution, and adaptation together at the narrow viewport."},
    "CDS-D031": {"class": "default-risk", "severity": "warning", "title": "Reference lineage is weak", "remediation": "Restore the source role mapping and make the preserved relationship visible within five seconds."},
    "CDS-D032": {"class": "default-risk", "severity": "warning", "title": "Variable image contrast is unresolved", "remediation": "Move, contain, or protect overlaid type so contrast remains dependable across the actual image range."},
    "CDS-D033": {"class": "default-risk", "severity": "warning", "title": "Compositional depth flattened", "remediation": "Separate the scene into registered background, live-content, and alpha-bearing foreground planes so the intended occlusion remains editable."},
    "CDS-D034": {"class": "default-risk", "severity": "warning", "title": "Typographic character approximated", "remediation": "Use the intended licensed face or a measured project-specific transformation and prove the loaded family and rendered silhouette with real copy."},
    "CDS-D035": {"class": "default-risk", "severity": "warning", "title": "Repeated title-and-body slide template", "remediation": "Define distinct slide roles and vary composition according to narrative purpose rather than repeating one title-and-body shell."},
    "CDS-D036": {"class": "default-risk", "severity": "warning", "title": "Slide-role range is too narrow", "remediation": "Demonstrate at least four structural roles such as opening, interruption, proof, system explanation, quiet or rest, comparison, and closure."},
    "CDS-D037": {"class": "default-risk", "severity": "warning", "title": "Presentation lacks a narrative peak", "remediation": "Give one consequential idea a visibly stronger rhetorical and compositional moment instead of keeping every slide at the same intensity."},
    "CDS-D038": {"class": "default-risk", "severity": "warning", "title": "Presentation lacks a quiet or rest state", "remediation": "Add a deliberate quiet, evidence, or transition role so pacing is not uniformly loud or dense."},
    "CDS-D039": {"class": "default-risk", "severity": "warning", "title": "Projected and read-ahead modes are collapsed", "remediation": "Review live projection and independent reading separately; preserve the same truth while allowing each mode to use an appropriate density and sequence."},
    "CDS-D040": {"class": "default-risk", "severity": "warning", "title": "Generated-media background integration is unverified", "remediation": "Verify the actual alpha channel and background pixels, then use a native frame, verified alpha asset, or provenance-preserving background edit with bound before-and-after evidence."},
    "CDS-D041": {"class": "default-risk", "severity": "warning", "title": "Media treatment suppresses material contrast", "remediation": "Remove or revise blend, filter, crop, or overlay treatment that erases the color, depth, texture, or scale that made the selected media concept-forming."},
    "CDS-P001": {"class": "project-drift", "severity": "error", "title": "Unapproved design token", "remediation": "Return to the approved font, color, spacing, radius, motion, or opening-pattern family."},
    "CDS-P002": {"class": "project-drift", "severity": "error", "title": "Signature absent beyond hero", "remediation": "Carry the approved signature into body, mobile, quiet, error, and reduced-motion states."},
    "CDS-P003": {"class": "project-drift", "severity": "error", "title": "Reference imitation", "remediation": "Adapt the recorded mechanic through the project-specific transformation instead of copying identity."},
    "CDS-P004": {"class": "project-drift", "severity": "error", "title": "Rejected choice reintroduced", "remediation": "Remove the rejected choice or create and approve a new design revision."},
    "CDS-P005": {"class": "project-drift", "severity": "error", "title": "Continuity house tell dominates", "remediation": "Strengthen the approved project identity and remove recurring generator mannerisms."},
    "CDS-P006": {"class": "project-drift", "severity": "error", "title": "Approved reference mechanic lost", "remediation": "Restore the validated reconstruction constraints and rerun the side-by-side fidelity review."},
    "CDS-P007": {"class": "project-drift", "severity": "error", "title": "Portfolio review stale", "remediation": "Review the current output against the last three or four generations and bind the resulting report."},
    "CDS-P008": {"class": "project-drift", "severity": "error", "title": "House-style overlap too high", "remediation": "Change at least three fingerprint dimensions and disposition every intentionally retained tell."},
    "CDS-P009": {"class": "project-drift", "severity": "error", "title": "Strongest prior output unchallenged", "remediation": "Run a visual counterfactual against the strongest prior generation while preserving project lineage."},
    "CDS-P010": {"class": "project-drift", "severity": "error", "title": "Media is merely supporting", "remediation": "Use owned, supplied, or generated media to form at least one concept's thesis, composition, and behavior."},
    "CDS-P011": {"class": "project-drift", "severity": "error", "title": "Adaptation distance collapsed", "remediation": "Produce and measure both a recognizably close study and a materially far study."},
    "CDS-P012": {"class": "project-drift", "severity": "error", "title": "Reference difficulty unresolved", "remediation": "Pass the evidence thresholds for the reference's photographic, diagrammatic, editorial, motion, or product-object class."},
    "CDS-P013": {"class": "project-drift", "severity": "error", "title": "Journey evidence is hero-only", "remediation": "Carry the signature through downstream proof, quiet or edge, closure, responsive, and motion or explicit no-motion states."},
    "CDS-P014": {"class": "project-drift", "severity": "error", "title": "Approved composition planes collapsed", "remediation": "Restore the approved registered asset planes and their DOM order; a flattened composite cannot stand in for editable depth."},
    "CDS-P015": {"class": "project-drift", "severity": "error", "title": "Approved typographic character lost", "remediation": "Restore the approved face, rendered proportions, line breaks, and type-to-media relationship, then rerun the font probe."},
    "CDS-P016": {"class": "project-drift", "severity": "error", "title": "Selected concept-forming media downgraded", "remediation": "Restore the selected media or a provenance-preserving edit at equal or greater visual capability; a simplified SVG or primitive reconstruction cannot replace its defining material impact."},
}


def ruleset_hash() -> str:
    engine_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload = json.dumps({"version": RULESET_VERSION, "rules": RULES, "engine_hash": engine_hash}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _iter_files(target: Path) -> Iterable[Path]:
    if target.is_file():
        if target.suffix.lower() in SCANNABLE_SUFFIXES:
            yield target
        return
    for path in sorted(target.rglob("*")):
        if path.is_file() and path.suffix.lower() in SCANNABLE_SUFFIXES and not IGNORED_PARTS.intersection(path.parts):
            yield path


def _finding(rule_id: str, location: str, line: int, evidence: str, *, source: str = "static") -> dict[str, Any]:
    rule = RULES[rule_id]
    return {
        "finding_id": f"{rule_id}:{location}:{line}",
        "rule_id": rule_id,
        "rule_class": rule["class"],
        "severity": rule["severity"],
        "title": rule["title"],
        "location": location,
        "line": line,
        "evidence": evidence[:300],
        "remediation": rule["remediation"],
        "source": source,
    }


def _line_number(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def _match_once(findings: list[dict[str, Any]], rule_id: str, location: str, text: str, pattern: str, evidence: str, flags: int = re.IGNORECASE | re.DOTALL) -> None:
    match = re.search(pattern, text, flags)
    if match:
        findings.append(_finding(rule_id, location, _line_number(text, match.start()), evidence))


def _scan_text(location: str, text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    _match_once(findings, "CDS-H001", location, text, r"<(?:audio|video)\b(?=[^>]*\bautoplay\b)(?![^>]*\bmuted\b)[^>]*>", "autoplay media is not muted")
    motion_heavy = re.search(r"\b(?:WebGLRenderer|requestAnimationFrame|three(?:\.min)?\.js|@keyframes)\b", text, re.I)
    if motion_heavy and not re.search(r"prefers-reduced-motion|matchMedia\s*\([^)]*reduced-motion", text, re.I):
        findings.append(_finding("CDS-H002", location, _line_number(text, motion_heavy.start()), "motion-heavy code has no reduced-motion fallback"))
    _match_once(findings, "CDS-H003", location, text, r"(?:body|main|#app|#root)\s*\{[^}]*\b(?:opacity\s*:\s*0|visibility\s*:\s*hidden|display\s*:\s*none)", "primary content is initially hidden")
    _match_once(findings, "CDS-H004", location, text, r"\btransition\s*:\s*all\b", "transition: all")
    _match_once(findings, "CDS-H005", location, text, r"addEventListener\s*\(\s*['\"]scroll['\"]\s*,(?![^)]*(?:passive|requestAnimationFrame))", "raw scroll listener has no visible passive or frame bound")
    _match_once(findings, "CDS-D001", location, text, r"(?:linear|radial)-gradient\([^)]*(?:#(?:7c3aed|8b5cf6|9333ea|a855f7)|\bpurple\b)[^)]*(?:#(?:2563eb|3b82f6|0ea5e9)|\bblue\b)", "purple-to-blue gradient")
    if re.search(r"background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text", text, re.I) and re.search(r"gradient\(", text, re.I):
        match = re.search(r"background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text", text, re.I)
        findings.append(_finding("CDS-D002", location, _line_number(text, match.start()), "gradient combined with text background clipping"))
    _match_once(findings, "CDS-D003", location, text, r"(?:background(?:-color)?|--(?:background|surface|cream))\s*:\s*(?:#(?:f5f0e6|f7f3ea|faf7f0|fffaf0|f5f5dc)|\b(?:cream|ivory)\b)", "warm cream surface token")
    _match_once(findings, "CDS-D004", location, text, r"font-family\s*:[^;}]*(?:['\"]?Inter['\"]?|['\"]?Space Grotesk['\"]?)", "common model-default font family")
    if re.search(r"backdrop-filter\s*:\s*blur", text, re.I) and re.search(r"background[^;}]*(?:rgba|hsla)\([^;}]*(?:0?\.[0-7]|/[ ]?[0-7]?\d%)", text, re.I):
        match = re.search(r"backdrop-filter\s*:\s*blur", text, re.I)
        findings.append(_finding("CDS-D005", location, _line_number(text, match.start()), "translucent blurred decorative surface"))
    if len(re.findall(r"border-radius\s*:\s*(?:1[6-9]|[2-9]\d)px", text, re.I)) >= 3:
        match = re.search(r"border-radius\s*:\s*(?:1[6-9]|[2-9]\d)px", text, re.I)
        findings.append(_finding("CDS-D006", location, _line_number(text, match.start()), "large rounded radius repeated across containers"))
    _match_once(findings, "CDS-D007", location, text, r"(?:class|className)\s*=\s*['\"][^'\"]*\bbento(?:-grid)?\b", "bento grid naming indicates a template reflex")
    if len(re.findall(r"(?:class|className)\s*=\s*['\"][^'\"]*\beyebrow\b", text, re.I)) >= 3:
        match = re.search(r"\beyebrow\b", text, re.I)
        findings.append(_finding("CDS-D008", location, _line_number(text, match.start()), "eyebrow label repeated three or more times"))
    if len(re.findall(r">\s*0?\d{1,2}[\s.:/-]+[^<]{1,60}<", text)) >= 3:
        match = re.search(r">\s*0?\d{1,2}[\s.:/-]+[^<]{1,60}<", text)
        findings.append(_finding("CDS-D009", location, _line_number(text, match.start()), "three or more display-numbered sections"))
    if len(re.findall(r"text-align\s*:\s*center|\btext-center\b|\bitems-center\b", text, re.I)) >= 5:
        match = re.search(r"text-align\s*:\s*center|\btext-center\b|\bitems-center\b", text, re.I)
        findings.append(_finding("CDS-D010", location, _line_number(text, match.start()), "centered composition repeated five or more times"))
    if len(re.findall(r"\bfade[-_ ]?up\b|translateY\([^)]*\).*opacity", text, re.I | re.S)) >= 3:
        match = re.search(r"\bfade[-_ ]?up\b|translateY\([^)]*\).*opacity", text, re.I | re.S)
        findings.append(_finding("CDS-D011", location, _line_number(text, match.start()), "fade-up reveal repeated across elements"))
    _match_once(findings, "CDS-D012", location, text, r"(?:hero|masthead)[\s\S]{0,1800}\b(?:metric|stat)\b[\s\S]{0,400}\b(?:metric|stat)\b", "multiple metric/stat elements inside a hero")
    _match_once(findings, "CDS-D013", location, text, r"(?:box-shadow|filter)\s*:[^;}]*\b(?:drop-shadow|0\s+0)\b[^;}]*(?:#(?:7c3aed|8b5cf6|2563eb|3b82f6)|rgba?\([^)]*(?:128|139|37|59))", "decorative purple or blue glow")
    _match_once(findings, "CDS-D014", location, text, r"(?:unsplash\.com|pexels\.com|pixabay\.com|images\.ctfassets\.net/[^\s'\"]*stock)", "interchangeable stock-image source")
    _match_once(findings, "CDS-D015", location, text, r"\b(?:seamless|seamlessly|revolutionize|effortless|effortlessly|elevate)\b", "generic promotional word")
    if text.count("—") >= 4:
        findings.append(_finding("CDS-D016", location, _line_number(text, text.find("—")), "four or more em dashes in one source file"))
    if re.search(r"(?:#00ff|#39ff|neon|lime).{0,300}(?:terminal|monospace|font-family\s*:\s*mono)", text, re.I | re.S) and re.search(r"(?:#000|#050505|background[^;]*black)", text, re.I):
        match = re.search(r"(?:#00ff|#39ff|neon|lime)", text, re.I)
        findings.append(_finding("CDS-D017", location, _line_number(text, match.start()), "black, neon, and terminal styling appear together"))
    return findings


def _external_findings(manifest: dict[str, Any], key: str, source: str) -> list[dict[str, Any]]:
    values = manifest.get(key, [])
    if not isinstance(values, list):
        raise ValueError(f"{key} must be an array")
    findings: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        if not isinstance(value, dict) or value.get("rule_id") not in RULES:
            raise ValueError(f"{key}[{index}] requires a known rule_id")
        location = value.get("location", source)
        evidence = value.get("evidence")
        if not isinstance(location, str) or not location.strip() or not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f"{key}[{index}] requires location and evidence")
        findings.append(_finding(value["rule_id"], location, int(value.get("line", 0)), evidence, source=source))
    return findings


def inspect(target: Path, project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if not target.exists():
        raise ValueError("Slop-check target does not exist")
    files: list[dict[str, str]] = []
    findings: list[dict[str, Any]] = []
    source_texts: list[tuple[str, str]] = []
    for path in _iter_files(target):
        relative = path.resolve().relative_to(project_root.resolve()).as_posix()
        data = path.read_bytes()
        files.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest()})
        decoded = data.decode("utf-8", errors="replace")
        source_texts.append((relative, decoded))
        findings.extend(_scan_text(relative, decoded))
    if not files:
        raise ValueError("Slop-check target has no supported source files")
    findings.extend(_external_findings(manifest, "visual_findings", "visual"))
    findings.extend(_external_findings(manifest, "context_findings", "context"))
    context = manifest.get("project_context", {})
    if not isinstance(context, dict):
        raise ValueError("project_context must be an object")
    marker_groups: dict[str, list[str]] = {}
    for key in ("unapproved_markers", "required_signature_markers", "rejected_choices", "continuity_house_tells"):
        value = context.get(key, [])
        if not isinstance(value, list) or any(not isinstance(marker, str) or not marker.strip() for marker in value):
            raise ValueError(f"project_context.{key} must be an array of non-empty strings")
        marker_groups[key] = value
    combined = "\n".join(text.casefold() for _, text in source_texts)
    first_location = source_texts[0][0]
    for marker in marker_groups["unapproved_markers"]:
        if isinstance(marker, str) and marker.strip() and marker.casefold() in combined:
            findings.append(_finding("CDS-P001", first_location, 0, f"unapproved contract marker is present: {marker}", source="context"))
    required_markers = marker_groups["required_signature_markers"]
    if isinstance(required_markers, list) and required_markers and not all(isinstance(marker, str) and marker.strip() and marker.casefold() in combined for marker in required_markers):
        findings.append(_finding("CDS-P002", first_location, 0, "one or more approved signature markers are absent", source="context"))
    reference_transformations = context.get("reference_transformations", [])
    if not isinstance(reference_transformations, list):
        raise ValueError("project_context.reference_transformations must be an array")
    for item in reference_transformations:
        if not isinstance(item, dict):
            raise ValueError("reference_transformations entries must be objects")
        identity = item.get("reference_identity_marker")
        transformation = item.get("project_transformation_marker")
        if not isinstance(identity, str) or not identity.strip() or not isinstance(transformation, str) or not transformation.strip():
            raise ValueError("reference_transformations entries require identity and project transformation markers")
        if identity.casefold() in combined and transformation.casefold() not in combined:
            findings.append(_finding("CDS-P003", first_location, 0, f"reference marker {identity!r} appears without project transformation {transformation!r}", source="context"))
    for marker in marker_groups["rejected_choices"]:
        if isinstance(marker, str) and marker.strip() and marker.casefold() in combined:
            findings.append(_finding("CDS-P004", first_location, 0, f"previously rejected choice is present: {marker}", source="context"))
    for marker in marker_groups["continuity_house_tells"]:
        if isinstance(marker, str) and marker.strip() and marker.casefold() in combined:
            findings.append(_finding("CDS-P005", first_location, 0, f"Continuity house tell is more visible than the approved identity: {marker}", source="context"))
    translation = manifest.get("translation_fidelity", {})
    if not isinstance(translation, dict):
        raise ValueError("translation_fidelity must be an object")
    translation_checks = (
        ("primitive_media_substitution", True, "CDS-D021", "source-defining media was replaced with primitive decoration"),
        ("material_energy_preserved", False, "CDS-D022", "the adaptation lost the reference's defining visual energy"),
        ("template_convergence", True, "CDS-D023", "the adaptation converged on a familiar generator template"),
        ("declared_mechanics_visible", False, "CDS-D024", "one or more declared mechanics are not visible in the rendered artifact"),
        ("generated_study_retained_or_translated", False, "CDS-D025", "generated exploration was discarded without an equivalent translation"),
        ("approved_constraints_present", False, "CDS-P006", "validated reference constraints are absent from the current artifact"),
        ("primary_material_organizes", False, "CDS-D026", "the primary material has been demoted to a backdrop"),
        ("typographic_grammar_preserved", False, "CDS-D027", "the adaptation substituted a different typographic role or scale system"),
        ("exact_single_source_baseline", False, "CDS-D028", "multiple sources were hybridized without separate exact baselines"),
        ("independent_review", False, "CDS-D029", "the adaptation fidelity was self-certified"),
        ("mobile_comparison_complete", False, "CDS-D030", "the narrow comparison does not show the full translation ladder"),
        ("reference_lineage_visible", False, "CDS-D031", "the preserved reference mechanic is not visibly traceable"),
        ("variable_contrast_resolved", False, "CDS-D032", "display content crosses variable imagery without dependable contrast"),
        ("editable_depth_preserved", False, "CDS-D033", "the intended subject and type relationship was flattened into one image or generic overlay"),
        ("font_transfer_verified", False, "CDS-D034", "the declared display character was approximated without loaded-font and silhouette evidence"),
        ("approved_layer_plan_present", False, "CDS-P014", "the approved background, live-content, and foreground plane plan is absent"),
        ("approved_typographic_character_present", False, "CDS-P015", "the approved typographic character or type-to-media relationship is absent"),
        ("selected_media_fidelity_preserved", False, "CDS-P016", "selected concept-forming media was replaced by a lower-capability derivative"),
        ("background_integration_verified", False, "CDS-D040", "the asset's actual alpha or background behavior was not verified before integration"),
        ("material_contrast_preserved", False, "CDS-D041", "blend, filter, crop, or overlay treatment suppressed the selected media's defining material contrast"),
    )
    for key, failing_value, rule_id, evidence in translation_checks:
        if key in translation and translation.get(key) is failing_value:
            findings.append(_finding(rule_id, first_location, 0, evidence, source="context"))
    portfolio_diversity = manifest.get("portfolio_diversity", {})
    if not isinstance(portfolio_diversity, dict):
        raise ValueError("portfolio_diversity must be an object")
    portfolio_checks = (
        ("portfolio_audit_current", "CDS-P007", "portfolio review is missing or older than four generations"),
        ("house_overlap_within_limit", "CDS-P008", "current output repeats too many prior Continuity fingerprints"),
        ("strongest_prior_challenged", "CDS-P009", "the strongest prior generation was not challenged"),
        ("concept_forming_media_present", "CDS-P010", "no direction uses media to form the concept"),
        ("close_far_distance_present", "CDS-P011", "adaptation studies do not prove both close and far transfer"),
        ("reference_difficulty_passed", "CDS-P012", "reference-class fidelity thresholds remain unresolved"),
        ("journey_state_depth_passed", "CDS-P013", "the signature is not evidenced beyond the hero and happy path"),
    )
    for key, rule_id, evidence in portfolio_checks:
        if key in portfolio_diversity and portfolio_diversity.get(key) is False:
            findings.append(_finding(rule_id, first_location, 0, evidence, source="context"))
    presentation = manifest.get("presentation_fidelity", {})
    if not isinstance(presentation, dict):
        raise ValueError("presentation_fidelity must be an object")
    slide_role_count = presentation.get("slide_role_count")
    if slide_role_count is not None:
        if not isinstance(slide_role_count, int) or isinstance(slide_role_count, bool) or slide_role_count < 0:
            raise ValueError("presentation_fidelity.slide_role_count must be a non-negative integer")
        if slide_role_count < 4:
            findings.append(_finding("CDS-D036", first_location, 0, f"only {slide_role_count} structural slide roles were demonstrated", source="context"))
    repeated_template_ratio = presentation.get("repeated_template_ratio")
    if repeated_template_ratio is not None:
        if not isinstance(repeated_template_ratio, (int, float)) or isinstance(repeated_template_ratio, bool) or not 0 <= repeated_template_ratio <= 1:
            raise ValueError("presentation_fidelity.repeated_template_ratio must be between 0 and 1")
        if repeated_template_ratio > 0.5:
            findings.append(_finding("CDS-D035", first_location, 0, f"{repeated_template_ratio:.0%} of slides repeat one structural template", source="context"))
    presentation_checks = (
        ("narrative_peak_present", "CDS-D037", "the sequence has no visibly dominant narrative peak"),
        ("quiet_or_rest_present", "CDS-D038", "the sequence has no deliberate quiet or rest state"),
    )
    for key, rule_id, evidence in presentation_checks:
        if key in presentation and presentation.get(key) is False:
            findings.append(_finding(rule_id, first_location, 0, evidence, source="context"))
    if (
        presentation.get("live_presentation_review_complete") is False
        or presentation.get("read_ahead_review_complete") is False
    ):
        findings.append(_finding("CDS-D039", first_location, 0, "live projection and read-ahead behavior were not both reviewed", source="context"))
    if presentation.get("claims_provenance_complete") is False:
        findings.append(_finding("CDS-H008", first_location, 0, "one or more presentation claims lack current source evidence or visible qualification", source="context"))
    if presentation.get("capture_integrity_verified") is False:
        findings.append(_finding("CDS-H009", first_location, 0, "one or more required captures have an unverified media type, dimension, viewport, or frame identity", source="context"))
    if presentation.get("copy_readability_verified") is False or presentation.get("data_readability_verified") is False:
        findings.append(_finding("CDS-H010", first_location, 0, "one or more slides contain copy or data that is hidden, clipped, too small, low-contrast, or otherwise unreadable", source="context"))
    for item in manifest.get("generated_claims", []):
        if isinstance(item, dict) and (not item.get("visible_qualification") or not item.get("provenance")):
            findings.append(_finding("CDS-H006", str(item.get("location", "manifest")), 0, "generated or illustrative claim lacks visible qualification or provenance", source="context"))
    for item in manifest.get("promoted_references", []):
        if isinstance(item, dict) and item.get("ownership") == "third-party":
            findings.append(_finding("CDS-H007", str(item.get("path", "manifest")), 0, "third-party moodboard or screenshot marked for promotion", source="context"))
    dispositions = manifest.get("dispositions", [])
    if not isinstance(dispositions, list):
        raise ValueError("dispositions must be an array")
    by_finding: dict[str, dict[str, Any]] = {}
    by_rule: dict[str, dict[str, Any]] = {}
    for item in dispositions:
        if not isinstance(item, dict) or item.get("status") not in DISPOSITIONS:
            raise ValueError("Each disposition requires a supported status")
        key = item.get("finding_id")
        rule_id = item.get("rule_id")
        if isinstance(key, str):
            by_finding[key] = item
        elif isinstance(rule_id, str):
            by_rule[rule_id] = item
        else:
            raise ValueError("Each disposition requires finding_id or rule_id")
    unresolved: list[str] = []
    normalized_dispositions: list[dict[str, Any]] = []
    for finding in findings:
        disposition = by_finding.get(finding["finding_id"]) or by_rule.get(finding["rule_id"])
        if disposition:
            status = disposition["status"]
            if finding["rule_class"] != "default-risk" and status in {"accepted-intentional", "not-applicable"}:
                raise ValueError("Hard failures and project drift cannot be accepted or marked not applicable")
            if status == "accepted-intentional" and (
                not isinstance(disposition.get("rationale"), str) or not disposition["rationale"].strip()
                or not isinstance(disposition.get("contract_reference"), str) or not disposition["contract_reference"].strip()
            ):
                raise ValueError("Intentional acceptance requires a project rationale and design-contract reference")
            if status == "not-applicable" and (
                not isinstance(disposition.get("rationale"), str) or not disposition["rationale"].strip()
                or not isinstance(disposition.get("evidence"), str) or not disposition["evidence"].strip()
            ):
                raise ValueError("Not-applicable default risks require a rationale and evidence")
            normalized_dispositions.append({
                "finding_id": finding["finding_id"], "rule_id": finding["rule_id"], "status": status,
                "rationale": disposition.get("rationale", ""), "contract_reference": disposition.get("contract_reference", ""),
                "evidence": disposition.get("evidence", ""),
            })
            if status == "open":
                unresolved.append(finding["finding_id"])
            elif status == "resolved" and (
                not disposition.get("evidence")
                or finding["source"] == "static"
                or finding["rule_class"] in {"hard-failure", "project-drift"}
            ):
                unresolved.append(finding["finding_id"])
        else:
            normalized_dispositions.append({"finding_id": finding["finding_id"], "rule_id": finding["rule_id"], "status": "open", "rationale": "", "contract_reference": "", "evidence": ""})
            unresolved.append(finding["finding_id"])
    counts = {severity: sum(1 for item in findings if item["severity"] == severity) for severity in sorted(SEVERITIES)}
    source_bundle_hash = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    report = {
        "schema_version": 1,
        "ruleset_version": RULESET_VERSION,
        "ruleset_hash": ruleset_hash(),
        "target": target.resolve().relative_to(project_root.resolve()).as_posix(),
        "source_bundle_hash": source_bundle_hash,
        "files": files,
        "counts_by_severity": counts,
        "findings": findings,
        "dispositions": normalized_dispositions,
        "status": "passed" if not unresolved else "failed",
        "unresolved_finding_ids": unresolved,
        "visual_review": manifest.get("visual_review", {}),
        "translation_fidelity": translation,
        "presentation_fidelity": presentation,
    }
    report["report_hash"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return report
