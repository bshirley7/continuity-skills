"""Deterministic, network-free AI-slop inspection for design artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

RULESET_VERSION = "1.0.0"
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
    "CDS-P001": {"class": "project-drift", "severity": "error", "title": "Unapproved design token", "remediation": "Return to the approved font, color, spacing, radius, motion, or opening-pattern family."},
    "CDS-P002": {"class": "project-drift", "severity": "error", "title": "Signature absent beyond hero", "remediation": "Carry the approved signature into body, mobile, quiet, error, and reduced-motion states."},
    "CDS-P003": {"class": "project-drift", "severity": "error", "title": "Reference imitation", "remediation": "Adapt the recorded mechanic through the project-specific transformation instead of copying identity."},
    "CDS-P004": {"class": "project-drift", "severity": "error", "title": "Rejected choice reintroduced", "remediation": "Remove the rejected choice or create and approve a new design revision."},
    "CDS-P005": {"class": "project-drift", "severity": "error", "title": "Continuity house tell dominates", "remediation": "Strengthen the approved project identity and remove recurring generator mannerisms."},
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
    _match_once(findings, "CDS-D012", location, text, r"(?:hero|masthead)[\s\S]{0,1800}(?:metric|stat)[\s\S]{0,400}(?:metric|stat)", "multiple metric/stat elements inside a hero")
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
            if finding["rule_class"] != "default-risk" and status == "accepted-intentional":
                raise ValueError("Hard failures and project drift cannot be accepted as intentional")
            if status == "accepted-intentional" and (
                not isinstance(disposition.get("rationale"), str) or not disposition["rationale"].strip()
                or not isinstance(disposition.get("contract_reference"), str) or not disposition["contract_reference"].strip()
            ):
                raise ValueError("Intentional acceptance requires a project rationale and design-contract reference")
            normalized_dispositions.append({
                "finding_id": finding["finding_id"], "rule_id": finding["rule_id"], "status": status,
                "rationale": disposition.get("rationale", ""), "contract_reference": disposition.get("contract_reference", ""),
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
            normalized_dispositions.append({"finding_id": finding["finding_id"], "rule_id": finding["rule_id"], "status": "open", "rationale": "", "contract_reference": ""})
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
    }
    report["report_hash"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return report
