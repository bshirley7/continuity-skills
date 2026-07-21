from __future__ import annotations

import importlib.util
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "lib"))
import design

BOUNDARY_SPEC = importlib.util.spec_from_file_location("validate_design_boundary", SUITE / "scripts" / "validate_design_boundary.py")
BOUNDARY = importlib.util.module_from_spec(BOUNDARY_SPEC)
assert BOUNDARY_SPEC.loader
BOUNDARY_SPEC.loader.exec_module(BOUNDARY)
INSTALL_SPEC = importlib.util.spec_from_file_location("continuity_installer", SUITE / "installer" / "install.py")
INSTALLER = importlib.util.module_from_spec(INSTALL_SPEC)
assert INSTALL_SPEC.loader
INSTALL_SPEC.loader.exec_module(INSTALLER)
EVALUATION_SPEC = importlib.util.spec_from_file_location(
    "evaluate_design_scenarios",
    SUITE / "scripts" / "evaluate_design_scenarios.py",
)
EVALUATION = importlib.util.module_from_spec(EVALUATION_SPEC)
assert EVALUATION_SPEC.loader
EVALUATION_SPEC.loader.exec_module(EVALUATION)
CATALOG = SUITE / "skills" / "continuity-design" / "references" / "catalog.json"
SCENARIOS = SUITE / "skills" / "continuity-design" / "references" / "evaluation-scenarios.json"


def input_value(**overrides):
    value = {
        "design_id": "design-test",
        "title": "Test direction",
        "intent": "Set direction before implementation.",
        "audiences": ["Operators"],
        "targets": ["ui"],
        "industry": "b2b-saas",
        "sections": ["dashboards"],
        "themes": ["calm"],
        "message_structures": ["value-first"],
        "lenses": ["hierarchy", "accessibility", "trust"],
        "constraints": ["Keep keyboard access"],
        "preserve": ["Fast expert path"],
        "open_questions": [],
        "source_note_ids": [],
        "memory_ids": [],
    }
    value.update(overrides)
    return value


class DesignLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = {"project_id": "test-project", "private_dir": ".continuity/private", "collections": ["core", "projects", "design"]}

    def tearDown(self):
        self.temp.cleanup()

    def write_input(self, value):
        path = self.root / "input.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_adaptive_direction_counts(self):
        one = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(design_id="one")))
        self.assertEqual(len(one["directions"]), 1)
        self.assertEqual(set(one["directions"][0]["design_grammar"]), set(design.DESIGN_GRAMMAR_DIMENSIONS))
        self.assertTrue(all(one["directions"][0]["design_grammar"][key] for key in design.DESIGN_GRAMMAR_DIMENSIONS))
        two = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(design_id="two", open_questions=["Density or scanability?"])))
        self.assertEqual(len(two["directions"]), 2)
        three = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(design_id="three", themes=["calm", "technical"], message_structures=["value-first", "proof-first"])))
        self.assertEqual(len(three["directions"]), 3)

    def test_material_direction_count_overrides_question_count(self):
        value = input_value(
            design_id="material-count",
            direction_count=1,
            direction_count_basis="The organizing idea is settled; remaining questions are implementation detail.",
            open_questions=["Which breakpoint needs the compact variant?", "Which empty-state copy is final?"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(len(draft["directions"]), 1)
        self.assertEqual(draft["direction_count_basis"], value["direction_count_basis"])

    def test_current_state_and_alignment_contract_are_durable(self):
        value = input_value(
            design_id="assessed-design",
            evidence_inspected=["docs/product.md", "src/components"],
            current_strengths=["Fast expert navigation"],
            current_gaps=["Inconsistent hierarchy between detail views"],
            design_debt=["Local spacing values bypass shared tokens"],
            preserve=["Fast expert navigation"],
            non_goals=["Do not redesign account administration"],
            validation_criteria=["Expert navigation remains available without an additional step"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        direction = draft["directions"][0]
        self.assertTrue(direction["creative_signature"])
        self.assertTrue(any("fast expert navigation" in item.casefold() for item in direction["experience_principles"]))
        self.assertEqual(direction["validation_criteria"], value["validation_criteria"])
        design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (self.root / ".continuity/private/design/assessed-design/design.md").read_text(encoding="utf-8")
        for heading in (
            "## Decision at a glance", "## Current-state assessment", "## Design thesis", "## Experience principles",
            "## Experience architecture", "## Visual and interaction system",
            "## Component and pattern direction", "## Implementation contract",
            "### Acceptance and drift checks", "### Prohibited patterns",
        ):
            self.assertIn(heading, markdown)
        self.assertIn("Fast expert navigation", markdown)
        self.assertIn("Inconsistent hierarchy between detail views", markdown)
        self.assertIn("**Creative signature:**", markdown)

    def test_distinctive_expression_renders_from_provenance_and_persists(self):
        recovery = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="expression-recovery")),
        )["directions"][0]
        recovery["direction_id"] = "evidence-margin"
        recovery["creative_provenance"] = [
            {
                "provenance_id": "working-papers",
                "classification": "inspected",
                "observation": "Project workshops use annotated working papers.",
                "source_refs": ["docs/research/workshops.md"],
                "design_implication": "Attach evidence annotations to the claims they qualify.",
            },
            {
                "provenance_id": "bounded-risk",
                "classification": "inferred",
                "observation": "One structural interruption can make evidence visible without adding decoration.",
                "source_refs": [],
                "design_implication": "Let one evidence block cross the reading-column boundary.",
            },
        ]
        expression_budget = recovery["distinctive_expression"]["expression_budget"]
        refinement_passes = recovery["distinctive_expression"]["refinement_passes"]
        contextual_reviews = [{
            "review_id": "evidence-comprehension",
            "routing": "inferred",
            "perspective": "Evidence comprehension",
            "why_applicable": "Executive readers must distinguish a recommendation from the evidence and uncertainty that qualify it.",
            "finding": "A detached evidence panel would make qualification look optional.",
            "design_response": "Attach the evidence margin to the claim it qualifies and preserve adjacency on narrow targets.",
            "preserved_behavior": ["Linear reading order", "Direct access to the recommendation"],
            "verification": "In wide and narrow compositions, every qualified claim is immediately associated with its evidence state.",
        }]
        expression_budget.update({
            "target_weight": 0.62,
            "exploration_ceiling": 0.88,
            "mode": "calibrated",
            "source": "inferred",
            "weight_rationale": "The evidence margin can carry a strong authored point of view while the reading field remains quiet.",
            "boundary_being_pushed": "Make the evidence margin the single dominant compositional interruption.",
            "quiet_field": "Keep typography, imagery, motion, and depth quiet around the evidence margin.",
        })
        recovery["distinctive_expression"] = {
            "aesthetic_thesis": "A working brief whose visible annotations make rigor part of the identity.",
            "subject_world": ["Annotated working papers and evidence margins"],
            "signature_element": "A responsive evidence margin attached to each qualified claim.",
            "aesthetic_risk": {
                "move": "Let one proof block cross the primary reading boundary.",
                "rationale": "The interruption makes evidence structurally visible.",
                "boundary": "Preserve linear reading order and a non-motion equivalent.",
            },
            "anti_defaults": ["Reject generic editorial numbering and interchangeable cream-and-red prestige styling."],
            "expression_system": {
                "palette": ["Paper #F2F0EA; Carbon #171816; Signal cobalt #2855D9"],
                "typography": ["Compact grotesk display, readable serif body, tabular mono utility"],
                "composition": ["Recommendation column with attached evidence margin"],
                "material_imagery": ["Use qualified working artifacts rather than generic executive photography"],
                "motion": ["One claim-to-evidence reveal with a reduced-motion equivalent"],
                "voice": ["Direct executive language that distinguishes observation from inference"],
            },
            "expression_budget": expression_budget,
            "refinement_passes": refinement_passes,
            "contextual_reviews": contextual_reviews,
            "reference_compositions": ["Wide evidence margin; narrow inline evidence reveal"],
            "uniqueness_checks": ["Removing the evidence margin removes the identity, not merely decoration"],
            "provenance_ids": ["working-papers", "bounded-risk"],
        }
        value = input_value(design_id="distinctive-expression", directions=[recovery])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        selected = design.select(self.root, self.config, draft["design_id"], ["evidence-margin"], "reviewer")
        markdown = (self.root / ".continuity/private/design/distinctive-expression/design.md").read_text(encoding="utf-8")
        for text in (
            "## Distinctive expression", "### Subject world", "### Aesthetic risk",
            "### Expression budget", "### Multi-pass refinement",
            "### Contextual review outcomes", "#### Evidence comprehension",
            "### Anti-default decisions", "### Expression system", "### Creative provenance",
            "### Brand signature system", "#### Primary carrier", "#### Expression transformation",
            "### Design register", "### Usage scene", "### Color commitment",
            "### Anti-reflex review", "### Implementation system", "#### Hardening Checks",
            "**Aesthetic proposition:**", "**Bounded aesthetic risk:**",
            "**Target weight:** `0.62`", "**Exploration ceiling:** `0.88`",
            "`inspected`", "docs/research/workshops.md", "No direct source; inference is explicitly labeled.",
        ):
            self.assertIn(text, markdown)
        approved = design.approve(
            self.root, self.config, draft["design_id"], draft["revision"], "reviewer", selected["required_authorization_text"]
        )
        contract = approved["alignment_contract"]
        self.assertEqual(contract["distinctive_expression"][0]["aesthetic_risk"]["move"], recovery["distinctive_expression"]["aesthetic_risk"]["move"])
        self.assertEqual(contract["distinctive_expression"][0]["expression_budget"]["primary_dimension"], "composition")
        self.assertEqual(contract["distinctive_expression"][0]["expression_budget"]["target_weight"], 0.62)
        self.assertEqual(contract["distinctive_expression"][0]["expression_budget"]["exploration_ceiling"], 0.88)
        self.assertEqual(contract["distinctive_expression"][0]["brand_signature"]["primary_carrier"]["rule"], recovery["distinctive_expression"]["signature_element"])
        self.assertEqual(len(contract["distinctive_expression"][0]["refinement_passes"]), 7)
        self.assertEqual(contract["distinctive_expression"][0]["contextual_reviews"][0]["review_id"], "evidence-comprehension")
        self.assertEqual(contract["distinctive_expression"][0]["design_register"]["mode"], "mixed")
        self.assertEqual(contract["distinctive_expression"][0]["color_commitment"]["level"], "restrained")
        self.assertEqual(contract["distinctive_expression"][0]["implementation_system"]["status"], "provisional")
        self.assertEqual({item["provenance_id"] for item in contract["creative_provenance"]}, {"working-papers", "bounded-risk"})

    def test_distinctive_expression_rejects_multiple_signature_dimensions(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="bad-budget-recovery")),
        )["directions"][0]
        recovery["distinctive_expression"]["expression_budget"]["intensity"]["typography"] = "signature"
        with self.assertRaisesRegex(design.DesignError, "exactly one signature"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="bad-budget", directions=[recovery])),
            )

    def test_distinctive_expression_rejects_invalid_expression_weights(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="bad-weight-recovery")),
        )["directions"][0]
        recovery["distinctive_expression"]["expression_budget"].update({
            "target_weight": 0.8,
            "exploration_ceiling": 0.6,
        })
        with self.assertRaisesRegex(design.DesignError, "greater than or equal"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="bad-weight", directions=[recovery])),
            )

        recovery["distinctive_expression"]["expression_budget"].update({
            "target_weight": 1.1,
            "exploration_ceiling": 1.0,
        })
        with self.assertRaisesRegex(design.DesignError, "between 0 and 1"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="out-of-range-weight", directions=[recovery])),
            )

    def test_distinctive_expression_rejects_invalid_brand_transformation_weight(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="bad-brand-recovery")),
        )["directions"][0]
        recovery["distinctive_expression"]["brand_signature"]["transformation_matrix"][0]["target_weight"] = 1.2
        with self.assertRaisesRegex(design.DesignError, "transformation weight must be between 0 and 1"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="bad-brand", directions=[recovery])),
            )

    def test_distinctive_expression_rejects_out_of_order_refinement_passes(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="bad-passes-recovery")),
        )["directions"][0]
        passes = recovery["distinctive_expression"]["refinement_passes"]
        passes[0], passes[1] = passes[1], passes[0]
        with self.assertRaisesRegex(design.DesignError, "ordered multi-pass"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="bad-passes", directions=[recovery])),
            )

    def test_completed_contextual_review_requires_evidence_records(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="missing-context-review-recovery")),
        )["directions"][0]
        contextual = next(item for item in recovery["distinctive_expression"]["refinement_passes"] if item["pass_id"] == "contextual-review")
        contextual.update({"status": "completed", "changes": ["Adjusted hierarchy."], "unresolved": []})
        with self.assertRaisesRegex(design.DesignError, "evidence-bearing contextual_reviews"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="missing-context-review", directions=[recovery])),
            )

    def test_contextual_review_requires_verifiable_fields(self):
        recovery = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id="invalid-context-review-recovery")),
        )["directions"][0]
        recovery["distinctive_expression"]["contextual_reviews"] = [{
            "review_id": "trust", "routing": "inferred", "perspective": "Trust",
            "why_applicable": "Consequential claims require qualification.", "finding": "Claims appear certain.",
            "design_response": "Label their evidence state.", "preserved_behavior": ["Direct reading order"],
        }]
        with self.assertRaisesRegex(design.DesignError, "requires verification"):
            design.draft(
                self.root, self.config, CATALOG,
                self.write_input(input_value(design_id="invalid-context-review", directions=[recovery])),
            )

    def test_distinctive_expression_rejects_unknown_provenance(self):
        recovery = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="bad-expression-recovery")),
        )["directions"][0]
        recovery["distinctive_expression"]["provenance_ids"] = ["missing-source"]
        with self.assertRaisesRegex(design.DesignError, "unknown creative provenance"):
            design.draft(
                self.root,
                self.config,
                CATALOG,
                self.write_input(input_value(design_id="bad-expression", directions=[recovery])),
            )

    def test_prototype_integrity_renders_and_persists(self):
        value = input_value(
            design_id="prototype-integrity",
            audiences=["Occasional managers", "Full-time reviewers"],
            content_provenance=[
                {"content_id": "queue-count", "classification": "illustrative", "statement": "18 requests ready", "source_refs": [], "required_qualification": "Illustrative fixture value", "allowed_uses": ["prototype"]},
                {"content_id": "workflow", "classification": "inspected", "statement": "Reviewers retain keyboard navigation", "source_refs": ["src/review"], "required_qualification": "", "allowed_uses": ["design"]},
            ],
            audience_architecture={
                "mode": "differentiated",
                "shared_core": ["Understand decision state"],
                "routes": [
                    {"audience": "Occasional managers", "route": "decision summary", "needs": ["Guided review"]},
                    {"audience": "Full-time reviewers", "route": "evidence workbench", "needs": ["Dense comparison"]},
                ],
                "unresolved_conflicts": [],
            },
            prototype_scope={
                "maturity": "behavioral", "artifact_type": "responsive HTML", "fixture_data": "present",
                "demonstrated_surfaces": ["Review queue"], "demonstrated_states": ["default", "selected"],
                "omitted_surfaces": ["Request creation"], "omitted_states": ["offline", "error"],
            },
            validation_matrix=[
                {"scenario": "keyboard-only", "status": "passed", "evidence": "Manual traversal completed"},
                {"scenario": "localization expansion", "status": "required", "evidence": ""},
            ],
            insight_decisions=[{
                "insight_id": "expert-route",
                "insight": "Full-time reviewers need to retain dense keyboard-supported comparison.",
                "status": "decided",
                "source_refs": ["src/review"],
                "design_response": "Keep a dense evidence workbench as a differentiated reviewer route.",
                "affected_surfaces": ["Review queue", "Evidence detail"],
                "affected_states": ["default", "selected"],
                "observable_evidence": "The reviewer route exposes comparable evidence and complete keyboard traversal.",
            }],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (self.root / ".continuity/private/design/prototype-integrity/design.md").read_text(encoding="utf-8")
        for heading in ("## Content and evidence integrity", "## Audience architecture", "## Demonstrated and not demonstrated", "## Prototype validation matrix", "## Insight-to-design decisions", "## Content rules", "## Audience strategy", "## Prototype boundaries"):
            self.assertIn(heading, markdown)
        self.assertIn("Illustrative fixture value", markdown)
        approved = design.approve(self.root, self.config, draft["design_id"], draft["revision"], "reviewer", selected["required_authorization_text"])
        contract = approved["alignment_contract"]
        self.assertEqual(contract["content_provenance"], draft["content_provenance"])
        self.assertEqual(contract["audience_architecture"]["mode"], "differentiated")
        self.assertEqual(contract["prototype_scope"]["maturity"], "behavioral")
        self.assertEqual(contract["insight_decisions"][0]["insight_id"], "expert-route")
        self.assertTrue(contract["content_rules"])

    def test_prototype_integrity_rejects_invalid_records(self):
        cases = [
            input_value(design_id="bad-classification", content_provenance=[{"content_id": "claim", "classification": "verified", "statement": "A claim"}]),
            input_value(design_id="unqualified-fixture", content_provenance=[{"content_id": "claim", "classification": "illustrative", "statement": "A claim"}]),
            input_value(design_id="thin-audiences", audience_architecture={"mode": "differentiated", "routes": [{"audience": "One", "route": "one", "needs": ["one"]}]}),
            input_value(design_id="unfinished-readiness", prototype_scope={"maturity": "implementation-facing", "artifact_type": "HTML", "demonstrated_surfaces": ["Home"], "demonstrated_states": ["default"], "fixture_data": "none"}, validation_matrix=[{"scenario": "keyboard", "status": "required", "evidence": ""}]),
        ]
        for value in cases:
            with self.subTest(design_id=value["design_id"]), self.assertRaises(design.DesignError):
                design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_legacy_inputs_receive_conservative_integrity_defaults(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(design_id="legacy-integrity")))
        self.assertEqual(draft["content_provenance"], [])
        self.assertIsNone(draft["audience_architecture"])
        self.assertIsNone(draft["prototype_scope"])
        self.assertEqual(draft["validation_matrix"], [])
        self.assertEqual(draft["insight_decisions"], [])
        self.assertTrue(draft["directions"][0]["prototype_boundaries"])

    def test_one_direction_rejects_unresolved_material_ambiguity(self):
        value = input_value(
            design_id="premature-convergence",
            direction_count=1,
            direction_count_basis="A recommendation is available.",
            direction_assessment={"material_ambiguities": ["Shared core or differentiated audience routes"], "resolved_by_evidence": []},
        )
        with self.assertRaisesRegex(design.DesignError, "material design ambiguities"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))
        value["direction_count"] = 2
        self.assertEqual(len(design.draft(self.root, self.config, CATALOG, self.write_input(value))["directions"]), 2)

    def test_artifact_manifest_binds_files_and_reports_audience_coverage(self):
        value = input_value(
            design_id="artifact-design",
            audiences=["Managers", "Reviewers"],
            audience_architecture={
                "mode": "differentiated", "shared_core": ["Decision identity"], "unresolved_conflicts": [],
                "routes": [
                    {"audience": "Managers", "route": "guided decision", "needs": ["Plain-language consequence"]},
                    {"audience": "Reviewers", "route": "evidence workbench", "needs": ["Dense evidence"]},
                ],
            },
            prototype_scope={"maturity": "behavioral", "artifact_type": "HTML", "demonstrated_surfaces": ["Queue"], "demonstrated_states": ["default"], "omitted_surfaces": [], "omitted_states": [], "fixture_data": "present"},
            validation_matrix=[{"scenario": "sticky-action-obstruction", "status": "required", "evidence": ""}],
            insight_decisions=[{
                "insight_id": "manager-guidance", "insight": "Occasional managers need a guided decision route.",
                "status": "decided", "source_refs": [], "design_response": "Provide a plain-language manager decision path.",
                "affected_surfaces": ["Manager route"], "affected_states": ["default"],
                "observable_evidence": "A separate manager route explains consequence and next action.",
            }],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        approved = design.approve(self.root, self.config, draft["design_id"], 1, "reviewer", selected["required_authorization_text"])
        artifact_dir = self.root / "docs/design/artifacts"
        artifact_dir.mkdir(parents=True)
        html = artifact_dir / "queue.html"
        html.write_text(
            "<html><head>"
            f'<meta name="continuity-design-id" content="{approved["design_id"]}">'
            f'<meta name="continuity-design-revision" content="{approved["revision"]}">'
            f'<meta name="continuity-design-hash" content="{approved["design_hash"]}">'
            '<meta name="continuity-prototype-maturity" content="behavioral">'
            '<meta name="continuity-fixture-data" content="present-labeled">'
            '</head><body><section id="reviewer-route">Reviewer workbench</section></body></html>',
            encoding="utf-8",
        )
        manifest = {
            "schema_version": 1, "artifact_id": "queue-v1", "design_id": approved["design_id"],
            "revision": approved["revision"], "design_hash": approved["design_hash"], "maturity": "behavioral",
            "fixture_data": "present-labeled",
            "files": [{"path": "docs/design/artifacts/queue.html", "media_type": "text/html", "role": "prototype", "sha256": design.hashlib.sha256(html.read_bytes()).hexdigest()}],
            "demonstrated_audiences": ["Reviewers"], "demonstrated_surfaces": ["Queue"], "demonstrated_states": ["default"],
            "omitted_surfaces": ["Manager route"], "omitted_states": ["error"],
            "design_claims": [{"design_section": "Audience architecture", "claim": "Reviewer evidence workbench", "coverage": "demonstrated", "evidence_refs": ["docs/design/artifacts/queue.html#reviewer-route"], "insight_ids": []}],
            "validation_results": [], "execution_authorized": False,
        }
        manifest_path = self.root / "artifact.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = design.validate_artifact(self.root, self.config, manifest_path)
        self.assertEqual(result["missing_differentiated_audiences"], ["Managers"])
        self.assertFalse(result["implementation_ready"])
        manifest["maturity"] = "implementation-facing"
        html.write_text(html.read_text().replace('content="behavioral"', 'content="implementation-facing"'), encoding="utf-8")
        manifest["files"][0]["sha256"] = design.hashlib.sha256(html.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "not implementation-facing"):
            design.validate_artifact(self.root, self.config, manifest_path)
        html.write_text(html.read_text().replace("</body>", '<section id="manager-route">Manager decision path</section></body>'), encoding="utf-8")
        for name, width, height, role in (("desktop.png", 1440, 900, "desktop"), ("mobile.png", 390, 844, "mobile")):
            png = artifact_dir / name
            png.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big"))
            manifest["files"].append({"path": f"docs/design/artifacts/{name}", "media_type": "image/png", "role": role, "sha256": design.hashlib.sha256(png.read_bytes()).hexdigest()})
        manifest["files"][0]["sha256"] = design.hashlib.sha256(html.read_bytes()).hexdigest()
        manifest["demonstrated_audiences"] = ["Managers", "Reviewers"]
        manifest["omitted_surfaces"] = []
        manifest["design_claims"].append({"design_section": "Audience architecture", "claim": "Manager guided decision", "coverage": "demonstrated", "evidence_refs": ["docs/design/artifacts/queue.html#manager-route"], "insight_ids": ["manager-guidance"]})
        manifest["validation_results"] = [
            {"scenario": "horizontal-overflow", "status": "passed", "evidence": "Browser probe passed"},
            {"scenario": "sticky-action-obstruction", "status": "passed", "evidence": "Desktop and mobile inspection recorded"},
        ]
        manifest["craft_findings"] = [{
            "rule_id": "content-collision", "severity": "error", "status": "open",
            "artifact_ref": "docs/design/artifacts/mobile.png", "location": "#manager-route",
            "evidence": "Browser probe found overlapping content.", "response": "", "override_rationale": "",
        }]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "craft review"):
            design.validate_artifact(self.root, self.config, manifest_path)
        manifest["craft_findings"][0].update({"status": "resolved", "response": "Reflowed the route and recaptured the mobile viewport."})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        ready = design.validate_artifact(self.root, self.config, manifest_path)
        self.assertTrue(ready["implementation_ready"])
        self.assertEqual(ready["craft_findings"][0]["status"], "resolved")

    def test_artifact_manifest_rejects_hash_drift_and_unsafe_paths(self):
        value = input_value(design_id="artifact-drift")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        approved = design.approve(self.root, self.config, draft["design_id"], 1, "reviewer", selected["required_authorization_text"])
        manifest = {"artifact_id": "bad-artifact", "design_id": approved["design_id"], "revision": 1, "design_hash": approved["design_hash"], "maturity": "directional", "fixture_data": "none", "files": [{"path": "../escape.html", "media_type": "text/html", "role": "prototype", "sha256": "0" * 64}], "demonstrated_audiences": [], "design_claims": [], "validation_results": []}
        manifest_path = self.write_input(manifest)
        with self.assertRaisesRegex(design.DesignError, "project-relative"):
            design.validate_artifact(self.root, self.config, manifest_path)

    def test_complete_react_prototype_validates_before_approval(self):
        value = input_value(
            design_id="complete-react",
            implementation_context={
                "framework": "Next.js", "framework_version": "15", "react_version": "19",
                "styling_systems": ["Tailwind CSS"], "ui_libraries": ["Radix UI"],
                "motion_libraries": ["Motion"], "data_libraries": [], "icon_libraries": ["Lucide"],
                "component_roots": ["src/components"], "token_sources": ["src/styles/tokens.css"],
                "asset_roots": ["public/images"], "storybook_available": False,
                "evidence_refs": ["package.json", "components.json"],
            },
            component_map=[{
                "component_id": "decision-surface", "experience_need": "Review a consequential decision",
                "surface": "Decision review", "existing_capability": "Radix Dialog and project Button",
                "strategy": "compose", "components": ["Dialog", "Button"],
                "required_states": ["default", "loading", "error", "recovery", "complete"],
                "responsive_behavior": "Two-column review becomes a linear evidence-first sequence.",
                "accessibility_contract": "Focus, status, and consequence remain programmatically available.",
                "custom_expression": "A project-specific evidence margin carries the identity.",
            }],
            asset_strategy=[{
                "asset_id": "evidence-material", "purpose": "Ground the review in recognizable project evidence.",
                "source": "deliberately-omitted", "art_direction": "Use structured evidence fragments rather than generic photography.",
                "provenance_status": "Omission is deliberate; no rights-bearing asset is required.", "source_refs": [],
                "required_crops": [], "responsive_treatment": "Evidence fragments reflow without decorative cropping.",
                "accessibility_alternative": "All evidence remains readable text.", "fallback": "Preserve the structured evidence field.",
                "claim_boundary": "Do not imply that illustrative evidence is verified.",
            }],
            completion_contract={
                "mode": "complete-prototype", "required_viewports": ["desktop", "tablet", "mobile"],
                "required_states": ["default", "loading", "error", "recovery", "complete"],
                "content_status": "representative", "artifact_critique_required": True,
            },
            prototype_scope={
                "maturity": "implementation-facing", "artifact_type": "React",
                "demonstrated_surfaces": ["Decision review"],
                "demonstrated_states": ["default", "loading", "error", "recovery", "complete"],
                "omitted_surfaces": [], "omitted_states": [], "fixture_data": "present",
            },
            validation_matrix=[
                {"scenario": "horizontal-overflow", "status": "passed", "evidence": "Browser probe passed."},
                {"scenario": "sticky-action-obstruction", "status": "passed", "evidence": "Viewport captures inspected."},
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        artifact_dir = self.root / ".continuity/private/designs/complete-react/1"
        artifact_dir.mkdir(parents=True)
        html = artifact_dir / "index.html"
        html.write_text(
            "<html><head>"
            f'<meta name="continuity-design-id" content="{selected["design_id"]}">'
            f'<meta name="continuity-design-revision" content="{selected["revision"]}">'
            f'<meta name="continuity-design-hash" content="{selected["design_hash"]}">'
            '<meta name="continuity-prototype-maturity" content="implementation-facing">'
            '<meta name="continuity-fixture-data" content="present-labeled">'
            '</head><body><main id="primary-surface">Decision review</main></body></html>', encoding="utf-8",
        )
        files = [{"path": ".continuity/private/designs/complete-react/1/index.html", "media_type": "text/html", "role": "prototype", "sha256": design.hashlib.sha256(html.read_bytes()).hexdigest()}]
        for name, width in (("desktop", 1440), ("tablet", 768), ("mobile", 390)):
            png = artifact_dir / f"{name}.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + width.to_bytes(4, "big") + (900).to_bytes(4, "big"))
            files.append({"path": f".continuity/private/designs/complete-react/1/{name}.png", "media_type": "image/png", "role": name, "sha256": design.hashlib.sha256(png.read_bytes()).hexdigest()})
        digest = lambda item: design.hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        manifest = {
            "schema_version": 2, "artifact_id": "complete-react-v1", "design_id": selected["design_id"],
            "revision": selected["revision"], "design_hash": selected["design_hash"], "maturity": "implementation-facing",
            "fixture_data": "present-labeled", "implementation_context_hash": digest(value["implementation_context"]),
            "component_map_hash": digest(value["component_map"]), "asset_strategy_hash": digest(value["asset_strategy"]),
            "artifact_critique_revision": 1, "files": files, "demonstrated_audiences": ["Operators"],
            "demonstrated_surfaces": ["Decision review"],
            "demonstrated_states": ["default", "loading", "error", "recovery", "complete"],
            "omitted_surfaces": [], "omitted_states": [],
            "design_claims": [{"design_section": "Component capability map", "claim": "Decision surface is demonstrated", "coverage": "demonstrated", "evidence_refs": [".continuity/private/designs/complete-react/1/index.html#primary-surface"], "insight_ids": []}],
            "validation_results": [
                {"scenario": "horizontal-overflow", "status": "passed", "evidence": "Browser probe passed."},
                {"scenario": "sticky-action-obstruction", "status": "passed", "evidence": "Viewport captures inspected."},
            ], "execution_authorized": False,
        }
        manifest_path = self.write_input(manifest)
        result = design.validate_candidate_artifact(self.root, self.config, manifest_path)
        self.assertTrue(result["candidate"])
        self.assertTrue(result["implementation_ready"])
        markdown = (self.root / ".continuity/private/design/complete-react/design.md").read_text()
        self.assertIn("## React and implementation system", markdown)
        self.assertIn("### Component capability map", markdown)
        self.assertIn("## Asset strategy", markdown)
        self.assertIn("## Prototype completion contract", markdown)

    def test_non_ui_targets_require_only_meaningful_grammar_dimensions(self):
        document = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="document-grammar", targets=["document"])),
        )
        image = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="image-grammar", targets=["image"])),
        )
        self.assertNotIn("motion", document["directions"][0]["design_grammar"])
        self.assertNotIn("surface_depth", document["directions"][0]["design_grammar"])
        self.assertNotIn("motion", image["directions"][0]["design_grammar"])
        self.assertNotIn("state_language", image["directions"][0]["design_grammar"])

    def test_omitted_lenses_apply_explainable_baseline_and_contextual_routing(self):
        value = input_value(
            design_id="auto-lenses",
            title="AI-assisted identity review",
            intent="Help an operator review an automated recommendation and verify identity.",
        )
        value.pop("lenses")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(draft["lens_selection_mode"], "inferred")
        self.assertEqual(
            draft["lenses"][:6],
            ["comprehension", "usability", "accessibility", "trust", "behavioral-ethics", "error-prevention-recovery"],
        )
        self.assertIn("human-agency-calibrated-reliance-automation-boundaries", draft["lenses"])
        self.assertIn("explanation-contestability-decision-support", draft["lenses"])
        self.assertIn("identity-assurance-proportional-verification-exclusion-recovery", draft["lenses"])
        rules = {item["rule_id"]: item for item in draft["lens_routing"]}
        self.assertIn("automation-and-ai", rules)
        self.assertIn("identity-and-delegated-access", rules)
        self.assertIn("automated", rules["automation-and-ai"]["matched_terms"])
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-human-agency-calibrated-reliance-automation-boundaries", packs)
        self.assertIn("lens-identity-assurance-proportional-verification-exclusion-recovery", packs)

    def test_context_signals_infer_all_psychology_packs_with_versioned_rationale(self):
        value = input_value(
            design_id="psychology-context",
            title="Decision workspace",
            intent="Help a novice understand a complex system and make an independent choice.",
            consequences=["Financial consequence and irreversible commitment."],
            workflow_signals=[
                "Multi-step research workflow with survey evidence, saved state, interruption, and resume."
            ],
            interaction_signals=[
                "Dense information requires visual hierarchy, grouping, comparison, async processing, status, and retry."
            ],
            risk_signals=[
                "Progress, deadline, customer review, rating, social proof, scarcity, and vulnerable users."
            ],
        )
        value.pop("lenses")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        expected = {
            "perception-salience-affordance",
            "choice-comparison-decision-integrity",
            "mental-model-comprehension-transfer",
            "research-bias-evidence-validity",
            "motivation-progress-temporal-agency",
            "memory-learning-experience-continuity",
            "feedback-feedforward-temporal-state",
            "social-influence-persuasion-integrity",
        }
        self.assertTrue(expected.issubset(draft["lenses"]))
        self.assertIn("accessibility", draft["lenses"])
        self.assertEqual(draft["consequences"], value["consequences"])
        self.assertEqual(draft["workflow_signals"], value["workflow_signals"])
        self.assertEqual(draft["interaction_signals"], value["interaction_signals"])
        self.assertEqual(draft["risk_signals"], value["risk_signals"])
        rules = {item["rule_id"]: item for item in draft["lens_routing"]}
        for rule_id in (
            "perception-salience-and-affordance",
            "choice-comparison-and-commitment",
            "mental-model-and-transfer",
            "research-and-evidence-validity",
            "motivation-progress-and-temporal-agency",
            "memory-learning-and-resumption",
            "feedback-feedforward-and-temporal-state",
            "social-influence-and-persuasion",
            "high-consequence-psychology-safeguards",
        ):
            with self.subTest(rule_id=rule_id):
                rule = rules[rule_id]
                self.assertTrue(rule["matched_terms"])
                self.assertTrue(rule["matched_context"])
                self.assertTrue(rule["catalog_packs"])
                self.assertTrue(all(pack["version"] == "1.0.0" for pack in rule["catalog_packs"]))
        self.assertIn(
            "risk_signals",
            {context["field"] for context in rules["social-influence-and-persuasion"]["matched_context"]},
        )
        self.assertEqual(
            {pack["pack_id"] for pack in rules["high-consequence-psychology-safeguards"]["catalog_packs"]},
            {
                "lens-choice-comparison-decision-integrity",
                "lens-feedback-feedforward-temporal-state",
                "lens-social-influence-persuasion-integrity",
            },
        )
        self.assertEqual(len(draft["lenses"]), len(set(draft["lenses"])))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (
            self.root
            / ".continuity"
            / "private"
            / "design"
            / draft["design_id"]
            / "design.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("## UX lens selection", markdown)
        self.assertNotIn("social-influence-and-persuasion", markdown)
        self.assertNotIn("lens-social-influence-persuasion-integrity", markdown)
        self.assertEqual(selected["execution_authorized"], False)

    def test_natural_language_input_does_not_require_or_expose_design_taxonomy(self):
        value = {
            "design_id": "natural-brief",
            "title": "A clearer first experience",
            "intent": "Help people reach a useful result quickly and resume unfinished work.",
            "audiences": ["People using the product for the first time"],
            "targets": ["ui"],
            "constraints": ["Keep the existing expert shortcut"],
            "working_assumptions": ["The first useful result matters more than complete feature exposure"],
            "open_questions": ["Which existing shortcut do experienced users rely on most?"],
        }
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(draft["industry"], "")
        self.assertEqual(draft["sections"], [])
        self.assertEqual(draft["themes"], [])
        self.assertEqual(draft["message_structures"], [])
        self.assertEqual(draft["lens_selection_mode"], "inferred")
        self.assertEqual(len(draft["directions"]), 2)
        self.assertEqual(draft["working_assumptions"], value["working_assumptions"])
        packs = {pack["pack_id"] for pack in draft["catalog_packs"]}
        self.assertNotIn("design-industries", packs)
        self.assertNotIn("design-sections-flows", packs)
        self.assertNotIn("design-themes", packs)
        self.assertNotIn("design-message-structures", packs)
        self.assertIn("design-ux-lenses", packs)
        self.assertNotIn("lens", draft["directions"][0]["summary"].casefold())
        self.assertNotIn("theme", draft["directions"][0]["summary"].casefold())
        design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (
            self.root
            / ".continuity"
            / "private"
            / "design"
            / draft["design_id"]
            / "design.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("## UX lens selection", markdown)
        self.assertNotIn("## Explicit design concepts", markdown)
        self.assertIn("## Working assumptions", markdown)
        self.assertIn(value["working_assumptions"][0], markdown)
        self.assertIn("## Open questions", markdown)
        self.assertIn(value["open_questions"][0], markdown)

    def test_non_goals_do_not_trigger_contextual_lenses(self):
        value = {
            "design_id": "negative-routing",
            "title": "A clearer account page",
            "intent": "Help a customer understand current account details.",
            "audiences": ["Customers"],
            "targets": ["ui"],
            "non_goals": ["Do not add AI recommendations or automated decisions"],
        }
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertNotIn("human-agency-calibrated-reliance-automation-boundaries", draft["lenses"])

    def test_supplied_creative_direction_count_is_not_derived_from_taxonomy(self):
        seed = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="creative-seed")),
        )
        value = {
            "design_id": "creative-supplied",
            "title": "Independent creative direction",
            "intent": "Create a memorable and useful experience.",
            "audiences": ["Customers"],
            "targets": ["ui"],
            "open_questions": ["How bold?", "How dense?"],
            "directions": [seed["directions"][0]],
        }
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(len(draft["directions"]), 1)
        self.assertEqual(draft["directions"][0], seed["directions"][0])

    def test_cross_industry_cross_modality_evaluation_is_healthy(self):
        report = EVALUATION.evaluate(CATALOG, SCENARIOS)
        self.assertTrue(report["healthy"], report)
        self.assertEqual(report["metrics"]["scenario_count"], 20)
        self.assertEqual(report["metrics"]["passed_scenario_count"], 20)
        self.assertEqual(report["metrics"]["routing_precision"], 1.0)
        self.assertEqual(report["metrics"]["routing_recall"], 1.0)
        self.assertEqual(report["metrics"]["safeguard_coverage"], 1.0)
        self.assertEqual(report["metrics"]["conflict_resolution_coverage"], 1.0)
        self.assertLessEqual(report["metrics"]["maximum_direction_similarity"], 0.78)
        self.assertGreaterEqual(report["metrics"]["minimum_implementation_usefulness"], 0.9)
        self.assertEqual({item["modality"] for item in report["scenarios"]}, {"ui", "document", "image"})
        self.assertGreaterEqual(len({item["industry_group"] for item in report["scenarios"]}), 10)

    def test_evaluation_fails_closed_on_metric_regressions(self):
        suite = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        by_id = {item["scenario_id"]: item for item in suite["scenarios"]}
        by_id["consumer-onboarding-resumption"]["expected_lenses"].append(
            "authorship-provenance-content-integrity"
        )
        by_id["neutral-contact-page"]["input"]["risk_signals"] = ["Scarcity"]
        by_id["neutral-contact-page"]["required_safeguards"].append(
            "identity-assurance-proportional-verification-exclusion-recovery"
        )
        by_id["creative-ambiguity"]["expected_conflicts"] = [
            "automation-versus-human-authority"
        ]
        path = self.root / "regressed-scenarios.json"
        path.write_text(json.dumps(suite), encoding="utf-8")
        report = EVALUATION.evaluate(CATALOG, path)
        self.assertFalse(report["healthy"])
        self.assertFalse(report["threshold_results"]["routing_precision"])
        self.assertFalse(report["threshold_results"]["routing_recall"])
        self.assertFalse(report["threshold_results"]["safeguard_coverage"])
        self.assertFalse(report["threshold_results"]["conflict_resolution_coverage"])

    def test_direction_metrics_detect_duplicates_and_vague_rules(self):
        draft = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="metric-sensitivity")),
        )
        direction = draft["directions"][0]
        self.assertEqual(EVALUATION._maximum_similarity([direction, direction]), 1.0)
        vague = json.loads(json.dumps(direction))
        for dimension in design.DESIGN_GRAMMAR_DIMENSIONS:
            vague["design_grammar"][dimension] = ["Decorative."]
        self.assertLess(EVALUATION._implementation_usefulness([vague]), 0.9)

    def test_composition_precedence_resolves_active_conflicts_privately(self):
        value = input_value(
            design_id="composition-conflicts",
            intent="Help people scan dense information and use social proof without coercion.",
            interaction_signals=["Visual hierarchy and grouping"],
            risk_signals=["Customer reviews and ratings"],
        )
        value.pop("lenses")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        precedence = draft["composition_resolution"]["precedence"]
        self.assertEqual(
            [item["priority"] for item in precedence],
            sorted((item["priority"] for item in precedence), reverse=True),
        )
        conflicts = {
            item["conflict_id"]: item
            for item in draft["composition_resolution"]["active_conflicts"]
        }
        self.assertIn("density-versus-comprehension", conflicts)
        self.assertIn("persuasion-versus-agency", conflicts)
        self.assertEqual(
            conflicts["persuasion-versus-agency"]["dominant_precedence_id"],
            "safety-accessibility-agency",
        )
        self.assertTrue(all(item["resolution"] for item in conflicts.values()))
        design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (
            self.root
            / ".continuity"
            / "private"
            / "design"
            / draft["design_id"]
            / "design.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("persuasion-versus-agency", markdown)
        self.assertNotIn("safety-accessibility-agency", markdown)

    def test_approved_psychology_catalog_entries_are_offline_and_reviewable(self):
        catalog = design.load_catalog(CATALOG)
        expected = {
            "lens-perception-salience-affordance",
            "lens-choice-comparison-decision-integrity",
            "lens-mental-model-comprehension-transfer",
            "lens-research-bias-evidence-validity",
            "lens-motivation-progress-temporal-agency",
            "lens-memory-learning-experience-continuity",
            "lens-feedback-feedforward-temporal-state",
            "lens-social-influence-persuasion-integrity",
        }
        packs = {pack["pack_id"]: pack for pack in catalog["packs"]}
        self.assertTrue(expected.issubset(packs))
        for pack_id in expected:
            with self.subTest(pack_id=pack_id):
                pack = packs[pack_id]
                self.assertEqual(pack["version"], "1.0.0")
                self.assertEqual(pack["evidence_kind"], "literature")
                self.assertGreaterEqual(pack["evidence_sufficiency"]["sample_count"], 12)
                reference = CATALOG.parent / pack["reference"]
                self.assertTrue(reference.is_file())
                text = reference.read_text(encoding="utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertIn("## Ethical safeguards", text)
                self.assertIn("## Anti-patterns", text)
                self.assertIn("## Acceptance and review questions", text)

    def test_explicit_lenses_preserve_manual_compatibility_mode(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(lenses=["hierarchy", "trust"])))
        self.assertEqual(draft["lens_selection_mode"], "manual")
        self.assertEqual(draft["lens_routing"], [])
        self.assertEqual(draft["lenses"], ["hierarchy", "trust"])

    def test_lens_routing_rejects_unknown_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(CATALOG.parent, root / "references")
            routing_path = root / "references" / "lens-routing.json"
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            routing["baseline"].append("not-a-reviewed-lens")
            routing_path.write_text(json.dumps(routing), encoding="utf-8")
            catalog = design.load_catalog(root / "references" / "catalog.json")
            with self.assertRaisesRegex(design.DesignError, "invalid baseline"):
                design.load_lens_routing(root / "references" / "catalog.json", catalog)

    def test_lens_routing_rejects_invalid_match_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(CATALOG.parent, root / "references")
            routing_path = root / "references" / "lens-routing.json"
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            routing["rules"][0]["minimum_matches"] = 0
            routing_path.write_text(json.dumps(routing), encoding="utf-8")
            catalog = design.load_catalog(root / "references" / "catalog.json")
            with self.assertRaisesRegex(design.DesignError, "incomplete or unknown rule"):
                design.load_lens_routing(root / "references" / "catalog.json", catalog)

    def test_composition_precedence_rejects_unknown_lens(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(CATALOG.parent, root / "references")
            rules_path = root / "references" / "composition-precedence.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["conflicts"][0]["all_lenses"].append("not-a-reviewed-lens")
            rules_path.write_text(json.dumps(rules), encoding="utf-8")
            catalog = design.load_catalog(root / "references" / "catalog.json")
            with self.assertRaisesRegex(design.DesignError, "invalid conflict"):
                design.load_composition_precedence(root / "references" / "catalog.json", catalog)

    def test_supplied_direction_requires_complete_design_grammar(self):
        value = input_value(
            directions=[
                {
                    "direction_id": "incomplete",
                    "name": "Incomplete",
                    "summary": "Missing the implementation-facing grammar.",
                    "creative_signature": "Use one deliberate focal relationship to make the primary task recognizable.",
                    "principles": ["Keep the task clear."],
                    "variation_levers": ["Adjust density."],
                    "tradeoffs": ["Less visible context."],
                }
            ]
        )
        with self.assertRaisesRegex(design.DesignError, "complete design grammar"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_foundation_and_matching_category_packs_are_bound(self):
        value = input_value(industry="finance", sections=["onboarding"], themes=["calm"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(
            [pack["pack_id"] for pack in draft["catalog_packs"]],
            [
                "design-industries",
                "industry-finance",
                "design-sections-flows",
                "section-flow-onboarding",
                "design-themes",
                "theme-calm-clarity",
                "design-message-structures",
                "message-structure-value-first",
                "design-ux-lenses",
                "lens-hierarchy",
                "lens-accessibility",
                "lens-trust",
            ],
        )

    def test_reviewed_section_flow_overlays_are_bound(self):
        value = input_value(sections=["marketing", "conversion", "checkout"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(
            [pack["pack_id"] for pack in draft["catalog_packs"]],
            [
                "design-industries",
                "industry-b2b-saas",
                "design-sections-flows",
                "section-flow-marketing",
                "section-flow-conversion",
                "section-flow-checkout",
                "design-themes",
                "theme-calm-clarity",
                "design-message-structures",
                "message-structure-value-first",
                "design-ux-lenses",
                "lens-hierarchy",
                "lens-accessibility",
                "lens-trust",
            ],
        )

    def test_reviewed_value_first_overlay_is_bound(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value()))
        self.assertEqual(
            [pack["pack_id"] for pack in draft["catalog_packs"]],
            [
                "design-industries",
                "industry-b2b-saas",
                "design-sections-flows",
                "section-flow-dashboards",
                "design-themes",
                "theme-calm-clarity",
                "design-message-structures",
                "message-structure-value-first",
                "design-ux-lenses",
                "lens-hierarchy",
                "lens-accessibility",
                "lens-trust",
            ],
        )

    def test_reviewed_consumer_and_b2b_saas_overlays_are_bound(self):
        consumer = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="consumer", industry="consumer")),
        )
        self.assertEqual(
            [pack["pack_id"] for pack in consumer["catalog_packs"][:2]],
            ["design-industries", "industry-consumer"],
        )
        b2b = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="b2b", industry="b2b-saas")),
        )
        self.assertEqual(
            [pack["pack_id"] for pack in b2b["catalog_packs"][:2]],
            ["design-industries", "industry-b2b-saas"],
        )

    def test_reviewed_industry_depth_overlays_are_bound(self):
        for industry in ["health", "commerce", "media-social", "travel", "education", "developer-ai", "geospatial-operations", "media-production", "enterprise-administration", "security-operations", "developer-tooling", "agentic-ai"]:
            with self.subTest(industry=industry):
                draft = design.draft(
                    self.root,
                    self.config,
                    CATALOG,
                    self.write_input(input_value(design_id=industry, industry=industry)),
                )
                self.assertEqual(
                    [pack["pack_id"] for pack in draft["catalog_packs"][:2]],
                    ["design-industries", f"industry-{industry}"],
                )

    def test_reviewed_dashboard_overlay_is_bound(self):
        value = input_value(sections=["dashboards"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-dashboards", packs)
        self.assertEqual(packs[packs.index("section-flow-dashboards") - 1], "design-sections-flows")

    def test_reviewed_discovery_overlay_is_bound(self):
        value = input_value(sections=["discovery"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-discovery", packs)
        self.assertEqual(packs[packs.index("section-flow-discovery") - 1], "design-sections-flows")

    def test_reviewed_creation_overlay_is_bound(self):
        value = input_value(sections=["creation"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-creation", packs)
        self.assertEqual(packs[packs.index("section-flow-creation") - 1], "design-sections-flows")

    def test_reviewed_collaboration_overlay_is_bound(self):
        value = input_value(sections=["collaboration"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-collaboration", packs)
        self.assertEqual(packs[packs.index("section-flow-collaboration") - 1], "design-sections-flows")

    def test_reviewed_settings_overlay_is_bound(self):
        value = input_value(sections=["settings"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-settings", packs)
        self.assertEqual(packs[packs.index("section-flow-settings") - 1], "design-sections-flows")

    def test_reviewed_permissions_overlay_is_bound(self):
        value = input_value(sections=["permissions"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-permissions", packs)
        self.assertEqual(packs[packs.index("section-flow-permissions") - 1], "design-sections-flows")

    def test_reviewed_high_consequence_decisions_overlay_is_bound(self):
        value = input_value(sections=["high-consequence-decisions"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-high-consequence-decisions", packs)
        self.assertEqual(
            packs[packs.index("section-flow-high-consequence-decisions") - 1],
            "design-sections-flows",
        )

    def test_reviewed_reminders_reengagement_overlay_is_bound(self):
        value = input_value(sections=["reminders-reengagement"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-reminders-reengagement", packs)
        self.assertEqual(
            packs[packs.index("section-flow-reminders-reengagement") - 1],
            "design-sections-flows",
        )

    def test_reviewed_contextual_learning_overlay_is_bound(self):
        value = input_value(sections=["contextual-learning"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-contextual-learning", packs)
        self.assertEqual(packs[packs.index("section-flow-contextual-learning") - 1], "design-sections-flows")

    def test_reviewed_contextual_help_recovery_overlay_is_bound(self):
        value = input_value(sections=["contextual-help-recovery"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-contextual-help-recovery", packs)
        self.assertEqual(packs[packs.index("section-flow-contextual-help-recovery") - 1], "design-sections-flows")

    def test_reviewed_consent_privacy_controls_overlay_is_bound(self):
        value = input_value(sections=["consent-privacy-controls"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-consent-privacy-controls", packs)
        self.assertEqual(
            packs[packs.index("section-flow-consent-privacy-controls") - 1],
            "design-sections-flows",
        )

    def test_reviewed_retention_overlay_is_bound(self):
        value = input_value(sections=["retention"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-retention", packs)
        self.assertEqual(packs[packs.index("section-flow-retention") - 1], "design-sections-flows")

    def test_reviewed_authentication_recovery_overlay_is_bound(self):
        value = input_value(sections=["authentication-recovery"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-authentication-recovery", packs)
        self.assertEqual(
            packs[packs.index("section-flow-authentication-recovery") - 1],
            "design-sections-flows",
        )

    def test_reviewed_data_portability_overlay_is_bound(self):
        value = input_value(sections=["data-portability"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-data-portability", packs)
        self.assertEqual(packs[packs.index("section-flow-data-portability") - 1], "design-sections-flows")

    def test_reviewed_bulk_operations_overlay_is_bound(self):
        value = input_value(sections=["bulk-operations"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-bulk-operations", packs)
        self.assertEqual(packs[packs.index("section-flow-bulk-operations") - 1], "design-sections-flows")

    def test_reviewed_activity_audit_history_overlay_is_bound(self):
        value = input_value(sections=["activity-audit-history"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-activity-audit-history", packs)
        self.assertEqual(packs[packs.index("section-flow-activity-audit-history") - 1], "design-sections-flows")

    def test_reviewed_notification_inbox_overlay_is_bound(self):
        value = input_value(sections=["notification-inbox"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-notification-inbox", packs)
        self.assertEqual(packs[packs.index("section-flow-notification-inbox") - 1], "design-sections-flows")

    def test_reviewed_attention_interruption_overlay_is_bound(self):
        value = input_value(lenses=["attention-interruption"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-attention-interruption", packs)
        self.assertEqual(packs[packs.index("lens-attention-interruption") - 1], "design-ux-lenses")

    def test_reviewed_search_and_information_foraging_overlays_are_bound(self):
        value = input_value(sections=["search-discovery"], lenses=["information-foraging"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-search-discovery", packs)
        self.assertIn("lens-information-foraging", packs)
        self.assertEqual(packs[packs.index("section-flow-search-discovery") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-information-foraging") - 1], "design-ux-lenses")

    def test_reviewed_complex_forms_and_error_prevention_overlays_are_bound(self):
        value = input_value(sections=["complex-forms"], lenses=["error-prevention-recovery"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-complex-forms", packs)
        self.assertIn("lens-error-prevention-recovery", packs)
        self.assertEqual(packs[packs.index("section-flow-complex-forms") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-error-prevention-recovery") - 1], "design-ux-lenses")

    def test_reviewed_analytical_exploration_and_quantitative_evidence_overlays_are_bound(self):
        value = input_value(sections=["analytical-exploration"], lenses=["quantitative-evidence-uncertainty"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-analytical-exploration", packs)
        self.assertIn("lens-quantitative-evidence-uncertainty", packs)
        self.assertEqual(packs[packs.index("section-flow-analytical-exploration") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-quantitative-evidence-uncertainty") - 1], "design-ux-lenses")

    def test_reviewed_support_case_lifecycle_and_procedural_fairness_service_recovery_overlays_are_bound(self):
        value = input_value(sections=["support-case-lifecycle"], lenses=["procedural-fairness-service-recovery"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-support-case-lifecycle", packs)
        self.assertIn("lens-procedural-fairness-service-recovery", packs)
        self.assertEqual(packs[packs.index("section-flow-support-case-lifecycle") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-procedural-fairness-service-recovery") - 1], "design-ux-lenses")

    def test_reviewed_conversation_lifecycle_and_conversation_grounding_turn_taking_repair_overlays_are_bound(self):
        value = input_value(sections=["conversation-lifecycle"], lenses=["conversation-grounding-turn-taking-repair"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-conversation-lifecycle", packs)
        self.assertIn("lens-conversation-grounding-turn-taking-repair", packs)
        self.assertEqual(packs[packs.index("section-flow-conversation-lifecycle") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-conversation-grounding-turn-taking-repair") - 1], "design-ux-lenses")

    def test_reviewed_operational_exception_incident_and_situation_awareness_resilient_control_overlays_are_bound(self):
        value = input_value(sections=["operational-exception-incident"], lenses=["situation-awareness-resilient-control"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-operational-exception-incident", packs)
        self.assertIn("lens-situation-awareness-resilient-control", packs)
        self.assertEqual(packs[packs.index("section-flow-operational-exception-incident") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-situation-awareness-resilient-control") - 1], "design-ux-lenses")

    def test_reviewed_review_approval_and_accountability_overlays_are_bound(self):
        value = input_value(sections=["review-approval-lifecycle"], lenses=["accountability-separation-of-duties-independent-review"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-review-approval-lifecycle", packs)
        self.assertIn("lens-accountability-separation-of-duties-independent-review", packs)
        self.assertEqual(packs[packs.index("section-flow-review-approval-lifecycle") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-accountability-separation-of-duties-independent-review") - 1], "design-ux-lenses")

    def test_reviewed_policy_rule_and_rule_governance_overlays_are_bound(self):
        value = input_value(sections=["policy-rule-administration"], lenses=["rule-legibility-consistency-exception-governance"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-policy-rule-administration", packs)
        self.assertIn("lens-rule-legibility-consistency-exception-governance", packs)
        self.assertEqual(packs[packs.index("section-flow-policy-rule-administration") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-rule-legibility-consistency-exception-governance") - 1], "design-ux-lenses")

    def test_reviewed_ai_memory_and_contextual_integrity_overlays_are_bound(self):
        value = input_value(sections=["ai-memory-context-management"], lenses=["contextual-integrity-meaningful-data-agency"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-ai-memory-context-management", packs)
        self.assertIn("lens-contextual-integrity-meaningful-data-agency", packs)
        self.assertEqual(packs[packs.index("section-flow-ai-memory-context-management") - 1], "design-sections-flows")
        self.assertEqual(packs[packs.index("lens-contextual-integrity-meaningful-data-agency") - 1], "design-ux-lenses")

    def test_reviewed_empty_error_states_overlay_is_bound(self):
        value = input_value(sections=["empty-error-states"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-empty-error-states", packs)
        self.assertEqual(packs[packs.index("section-flow-empty-error-states") - 1], "design-sections-flows")

    def test_reviewed_application_lens_overlays_are_bound(self):
        draft = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(
                input_value(
                    lenses=[
                        "hierarchy",
                        "comprehension",
                        "usability",
                        "accessibility",
                        "interaction",
                        "responsiveness",
                        "trust",
                    ]
                )
            ),
        )
        packs = {pack["pack_id"]: pack for pack in draft["catalog_packs"]}
        self.assertEqual(packs["lens-hierarchy"]["version"], "1.0.0")
        self.assertEqual(packs["lens-comprehension"]["version"], "1.0.0")
        self.assertEqual(packs["lens-usability"]["version"], "1.0.0")
        self.assertEqual(packs["lens-accessibility"]["version"], "1.0.0")
        self.assertEqual(packs["lens-interaction"]["version"], "1.0.0")
        self.assertEqual(packs["lens-responsiveness"]["version"], "1.0.0")
        self.assertEqual(packs["lens-trust"]["version"], "1.0.0")

    def test_reviewed_professional_services_overlay_is_bound(self):
        value = input_value(industry="professional-services")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(packs[:2], ["design-industries", "industry-professional-services"])

    def test_reviewed_corporate_website_overlay_is_bound(self):
        value = input_value(sections=["corporate-website"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-corporate-website", packs)
        self.assertEqual(packs[packs.index("section-flow-corporate-website") - 1], "design-sections-flows")

    def test_reviewed_editorial_overlay_is_bound(self):
        value = input_value(themes=["editorial"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("theme-editorial", packs)
        self.assertEqual(packs[packs.index("theme-editorial") - 1], "design-themes")

    def test_reviewed_premium_overlay_is_bound(self):
        value = input_value(themes=["premium"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("theme-premium", packs)
        self.assertEqual(packs[packs.index("theme-premium") - 1], "design-themes")

    def test_reviewed_application_theme_overlays_are_bound(self):
        for theme in ("minimal", "expressive", "data-dense", "technical", "playful", "cinematic", "utilitarian"):
            with self.subTest(theme=theme):
                draft = design.draft(
                    self.root,
                    self.config,
                    CATALOG,
                    self.write_input(input_value(design_id=theme, themes=[theme])),
                )
                packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
                overlay = f"theme-{theme}"
                self.assertIn(overlay, packs)
                self.assertEqual(packs[packs.index(overlay) - 1], "design-themes")

    def test_reviewed_design_tokens_overlay_is_bound(self):
        value = input_value(lenses=["design-tokens"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-design-tokens", packs)
        self.assertEqual(packs[packs.index("lens-design-tokens") - 1], "design-ux-lenses")

    def test_reviewed_typography_overlay_is_bound(self):
        value = input_value(lenses=["typography"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-typography", packs)
        self.assertEqual(packs[packs.index("lens-typography") - 1], "design-ux-lenses")
        typography = next(pack for pack in draft["catalog_packs"] if pack["pack_id"] == "lens-typography")
        self.assertEqual(typography["version"], "1.1.0")

    def test_reviewed_component_architecture_overlay_is_bound(self):
        value = input_value(lenses=["component-architecture"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-component-architecture", packs)
        self.assertEqual(packs[packs.index("lens-component-architecture") - 1], "design-ux-lenses")

    def test_reviewed_theming_overlay_is_bound(self):
        value = input_value(lenses=["theming"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-theming", packs)
        self.assertEqual(packs[packs.index("lens-theming") - 1], "design-ux-lenses")

    def test_reviewed_system_governance_overlay_is_bound(self):
        value = input_value(lenses=["system-governance"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-system-governance", packs)
        self.assertEqual(packs[packs.index("lens-system-governance") - 1], "design-ux-lenses")

    def test_reviewed_adaptive_layout_overlay_is_bound(self):
        value = input_value(lenses=["adaptive-layout"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-adaptive-layout", packs)
        self.assertEqual(packs[packs.index("lens-adaptive-layout") - 1], "design-ux-lenses")

    def test_reviewed_motion_feedback_overlay_is_bound(self):
        value = input_value(lenses=["motion-feedback"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-motion-feedback", packs)
        self.assertEqual(packs[packs.index("lens-motion-feedback") - 1], "design-ux-lenses")

    def test_reviewed_direct_manipulation_overlay_is_bound(self):
        value = input_value(lenses=["direct-manipulation"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-direct-manipulation", packs)
        self.assertEqual(packs[packs.index("lens-direct-manipulation") - 1], "design-ux-lenses")

    def test_reviewed_keyboard_expert_workflows_overlay_is_bound(self):
        value = input_value(lenses=["keyboard-expert-workflows"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-keyboard-expert-workflows", packs)
        self.assertEqual(packs[packs.index("lens-keyboard-expert-workflows") - 1], "design-ux-lenses")

    def test_reviewed_proof_first_overlay_is_bound(self):
        value = input_value(message_structures=["proof-first"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-proof-first", packs)
        self.assertEqual(packs[packs.index("message-structure-proof-first") - 1], "design-message-structures")

    def test_reviewed_problem_solution_overlay_is_bound(self):
        value = input_value(message_structures=["problem-solution"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-problem-solution", packs)
        self.assertEqual(packs[packs.index("message-structure-problem-solution") - 1], "design-message-structures")

    def test_reviewed_guided_narrative_overlay_is_bound(self):
        value = input_value(message_structures=["guided-narrative"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-guided-narrative", packs)
        self.assertEqual(packs[packs.index("message-structure-guided-narrative") - 1], "design-message-structures")

    def test_reviewed_comparison_overlay_is_bound(self):
        value = input_value(message_structures=["comparison"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-comparison", packs)
        self.assertEqual(packs[packs.index("message-structure-comparison") - 1], "design-message-structures")

    def test_reviewed_progressive_disclosure_overlay_is_bound(self):
        value = input_value(message_structures=["progressive-disclosure"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-progressive-disclosure", packs)
        self.assertEqual(packs[packs.index("message-structure-progressive-disclosure") - 1], "design-message-structures")

    def test_reviewed_personalization_overlay_is_bound(self):
        value = input_value(message_structures=["personalization"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-personalization", packs)
        self.assertEqual(packs[packs.index("message-structure-personalization") - 1], "design-message-structures")

    def test_reviewed_content_overlay_is_bound(self):
        value = input_value(lenses=["content"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-content", packs)
        self.assertEqual(packs[packs.index("lens-content") - 1], "design-ux-lenses")

    def test_reviewed_differentiation_overlay_is_bound(self):
        value = input_value(lenses=["differentiation"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-differentiation", packs)
        self.assertEqual(packs[packs.index("lens-differentiation") - 1], "design-ux-lenses")

    def test_reviewed_color_overlay_is_bound(self):
        value = input_value(lenses=["color"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-color", packs)
        self.assertEqual(packs[packs.index("lens-color") - 1], "design-ux-lenses")

    def test_reviewed_trust_risk_reversal_overlay_is_bound(self):
        value = input_value(message_structures=["trust-risk-reversal"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("message-structure-trust-risk-reversal", packs)
        self.assertEqual(packs[packs.index("message-structure-trust-risk-reversal") - 1], "design-message-structures")

    def test_reviewed_interface_language_overlay_is_bound(self):
        value = input_value(lenses=["interface-language"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-interface-language", packs)
        self.assertEqual(packs[packs.index("lens-interface-language") - 1], "design-ux-lenses")

    def test_reviewed_accessibility_language_overlay_is_bound(self):
        value = input_value(lenses=["accessibility-language"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-accessibility-language", packs)
        self.assertEqual(packs[packs.index("lens-accessibility-language") - 1], "design-ux-lenses")

    def test_reviewed_localization_content_overlay_is_bound(self):
        value = input_value(lenses=["localization-content"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-localization-content", packs)
        self.assertEqual(packs[packs.index("lens-localization-content") - 1], "design-ux-lenses")

    def test_reviewed_design_evaluation_overlay_is_bound(self):
        value = input_value(lenses=["design-evaluation"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-design-evaluation", packs)
        self.assertEqual(packs[packs.index("lens-design-evaluation") - 1], "design-ux-lenses")

    def test_reviewed_behavioral_psychology_overlay_is_bound(self):
        value = input_value(lenses=["behavioral-psychology"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-behavioral-psychology", packs)
        self.assertEqual(packs[packs.index("lens-behavioral-psychology") - 1], "design-ux-lenses")

    def test_reviewed_decision_architecture_overlay_is_bound(self):
        value = input_value(lenses=["decision-architecture"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-decision-architecture", packs)
        self.assertEqual(packs[packs.index("lens-decision-architecture") - 1], "design-ux-lenses")

    def test_reviewed_cognitive_load_learning_overlay_is_bound(self):
        value = input_value(lenses=["cognitive-load-learning"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-cognitive-load-learning", packs)
        self.assertEqual(packs[packs.index("lens-cognitive-load-learning") - 1], "design-ux-lenses")

    def test_reviewed_behavioral_ethics_overlay_is_bound(self):
        value = input_value(lenses=["behavioral-ethics"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("lens-behavioral-ethics", packs)
        self.assertEqual(packs[packs.index("lens-behavioral-ethics") - 1], "design-ux-lenses")

    def test_reviewed_consumer_value_payment_and_fulfillment_overlays_are_bound(self):
        value = input_value(
            sections=[
                "loyalty-rewards-membership-lifecycle",
                "financial-transfer-payment-lifecycle",
                "order-fulfillment-delivery-handoff-lifecycle",
            ],
            lenses=[
                "earned-value-legibility-breakage-loyalty-fairness",
                "transaction-finality-recipient-certainty-recoverable-payment-control",
                "promise-accuracy-custody-transparency-exception-agency",
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        section_foundation = packs.index("design-sections-flows")
        lens_foundation = packs.index("design-ux-lenses")
        for pack_id in [
            "section-flow-loyalty-rewards-membership-lifecycle",
            "section-flow-financial-transfer-payment-lifecycle",
            "section-flow-order-fulfillment-delivery-handoff-lifecycle",
        ]:
            self.assertGreater(packs.index(pack_id), section_foundation)
        for pack_id in [
            "lens-earned-value-legibility-breakage-loyalty-fairness",
            "lens-transaction-finality-recipient-certainty-recoverable-payment-control",
            "lens-promise-accuracy-custody-transparency-exception-agency",
        ]:
            self.assertGreater(packs.index(pack_id), lens_foundation)

    def test_catalog_rejects_competing_category_overlays(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            value = json.loads(CATALOG.read_text(encoding="utf-8"))
            duplicate = dict(next(pack for pack in value["packs"] if pack["pack_id"] == "theme-calm-clarity"))
            duplicate.update({"pack_id": "theme-calm-competing", "reference": "theme-calm-competing.md"})
            value["packs"].append(duplicate)
            for reference in {pack["reference"] for pack in value["packs"] if pack["reference"] != duplicate["reference"]}:
                shutil.copy2(CATALOG.parent / reference, root / reference)
            (root / duplicate["reference"]).write_text("# Competing pack\n", encoding="utf-8")
            path = root / "catalog.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(design.DesignError):
                design.load_catalog(path)

    def test_exact_approval_promotion_and_goal_binding(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value()))
        selected = design.select(self.root, self.config, draft["design_id"], [draft["directions"][0]["direction_id"]], "human")
        private_design = (self.root / ".continuity" / "private" / "design" / draft["design_id"] / "design.md").read_text(encoding="utf-8")
        self.assertIn("#### Design grammar", private_design)
        self.assertIn("##### Responsive Behavior", private_design)
        with self.assertRaises(design.DesignError):
            design.approve(self.root, self.config, draft["design_id"], 1, "human", "approve")
        approved = design.approve(self.root, self.config, draft["design_id"], 1, "human", selected["required_authorization_text"])
        self.assertFalse(approved["execution_authorized"])
        self.assertEqual((self.root / "docs/design/design.md").read_bytes(), (self.root / ".continuity/private/design/design-test/design.md").read_bytes())
        bound = design.bind_approved(self.root, self.config, ["design-test"])
        self.assertEqual(bound[0]["design_hash"], approved["design_hash"])

    def test_revision_does_not_change_canonical_design(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value()))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "human")
        approved = design.approve(self.root, self.config, draft["design_id"], 1, "human", selected["required_authorization_text"])
        canonical = (self.root / "docs/design/design.md").read_bytes()
        revised = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(open_questions=["More density?"])))
        self.assertEqual(revised["revision"], 2)
        self.assertEqual((self.root / "docs/design/design.md").read_bytes(), canonical)
        self.assertEqual(json.loads((self.root / ".continuity/design.json").read_text())["design_hash"], approved["design_hash"])

    def test_non_ui_targets_are_labeled_inferred(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(targets=["document"])))
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "human")
        text = (self.root / ".continuity/private/design/design-test/design.md").read_text()
        self.assertIn("Evidence application: `inferred`", text)
        self.assertNotIn("## Evidence applicability", text)
        self.assertFalse(selected["execution_authorized"])

    def test_direct_document_evidence_is_reported_as_mixed_with_inferred_foundations(self):
        value = input_value(targets=["document"], lenses=["document-design-system"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        application = draft["evidence_application"]["document"]
        self.assertEqual(application["status"], "mixed")
        self.assertIn("lens-document-design-system", application["validated_packs"])
        self.assertIn("design-ux-lenses", application["inferred_packs"])
        design.select(self.root, self.config, draft["design_id"], ["direction-1"], "human")
        text = (self.root / ".continuity/private/design/design-test/design.md").read_text()
        self.assertIn("Evidence application: `mixed`", text)
        self.assertIn("`document-design-system`", text)
        self.assertNotIn("`lens-document-design-system`", text)

    def test_direct_image_evidence_is_reported_as_mixed_with_inferred_foundations(self):
        value = input_value(targets=["image"], lenses=["image-art-direction"])
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        application = draft["evidence_application"]["image"]
        self.assertEqual(application["status"], "mixed")
        self.assertIn("lens-image-art-direction", application["validated_packs"])
        self.assertIn("design-ux-lenses", application["inferred_packs"])

    def test_catalog_accepts_bounded_campaign_and_platform_evidence_contexts(self):
        catalog = design.load_catalog(CATALOG)
        campaign = next(pack for pack in catalog["packs"] if pack["pack_id"] == "lens-campaign-design-system")
        platform = next(pack for pack in catalog["packs"] if pack["pack_id"] == "lens-platform-native-adaptation")
        self.assertEqual(campaign["modalities"]["campaign"], "validated")
        self.assertEqual(platform["modalities"]["platform"], "validated")

    def test_catalog_rejects_unknown_evidence_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            value = json.loads(CATALOG.read_text(encoding="utf-8"))
            value["packs"][0]["modalities"]["unknown-context"] = "validated"
            for reference in {pack["reference"] for pack in value["packs"]}:
                shutil.copy2(CATALOG.parent / reference, root / reference)
            path = root / "catalog.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(design.DesignError):
                design.load_catalog(path)

    def test_goal_hash_changes_with_bound_design_hash(self):
        functions = runpy.run_path(str(SUITE / "bin" / "continuity"))
        directory = self.root / "goal"
        directory.mkdir()
        (directory / "plan.md").write_text("# Plan\n", encoding="utf-8")
        goal = {"design_refs": [{"design_id": "design-test", "revision": 1, "design_hash": "a" * 64, "catalog_packs": []}]}
        first = functions["goal_material_hash"](directory, goal)
        goal["design_refs"][0]["design_hash"] = "b" * 64
        self.assertNotEqual(first, functions["goal_material_hash"](directory, goal))

    def test_reviewed_pregnancy_lifecycle_and_reproductive_autonomy_overlays_are_bound(self):
        value = input_value(
            sections=["pregnancy-prenatal-birth-postpartum-lifecycle"],
            lenses=["reproductive-autonomy-maternal-safety-loss-sensitive-care"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertIn("section-flow-pregnancy-prenatal-birth-postpartum-lifecycle", packs)
        self.assertIn("lens-reproductive-autonomy-maternal-safety-loss-sensitive-care", packs)
        self.assertEqual(
            packs[packs.index("section-flow-pregnancy-prenatal-birth-postpartum-lifecycle") - 1],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[packs.index("lens-reproductive-autonomy-maternal-safety-loss-sensitive-care") - 1],
            "design-ux-lenses",
        )

    def test_reviewed_employment_and_housing_lifecycle_and_fairness_overlays_are_bound(self):
        pairs = (
            (
                "employment-discovery-application-selection-offer-lifecycle",
                "opportunity-fairness-applicant-agency-accountable-selection",
            ),
            (
                "housing-discovery-rental-application-lease-residency-lifecycle",
                "housing-opportunity-tenant-agency-accountable-screening",
            ),
        )
        for section, lens in pairs:
            draft = design.draft(
                self.root,
                self.config,
                CATALOG,
                self.write_input(input_value(sections=[section], lenses=[lens])),
            )
            packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
            section_pack = f"section-flow-{section}"
            lens_pack = f"lens-{lens}"
            self.assertEqual(packs[packs.index(section_pack) - 1], "design-sections-flows")
            self.assertEqual(packs[packs.index(lens_pack) - 1], "design-ux-lenses")

    def test_reviewed_learning_lifecycle_and_learner_agency_overlays_are_bound(self):
        value = input_value(
            sections=["learning-enrollment-assessment-completion-credential-lifecycle"],
            lenses=["learner-agency-assessment-validity-credential-integrity"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[packs.index("section-flow-learning-enrollment-assessment-completion-credential-lifecycle") - 1],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[packs.index("lens-learner-agency-assessment-validity-credential-integrity") - 1],
            "design-ux-lenses",
        )

    def test_reviewed_dietary_food_lifecycle_and_ingredient_integrity_overlays_are_bound(self):
        value = input_value(
            sections=["dietary-safe-food-discovery-customization-order-substitution-handoff-incident-lifecycle"],
            lenses=["ingredient-integrity-dietary-agency-allergen-safety-nutrition-context"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-dietary-safe-food-discovery-customization-order-substitution-handoff-incident-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[packs.index("lens-ingredient-integrity-dietary-agency-allergen-safety-nutrition-context") - 1],
            "design-ux-lenses",
        )


    def test_reviewed_tax_lifecycle_and_taxpayer_agency_overlays_are_bound(self):
        value = input_value(
            sections=["tax-record-classification-calculation-filing-payment-notice-correction-lifecycle"],
            lenses=["taxpayer-agency-calculation-transparency-procedural-rights-compliance-equity"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-tax-record-classification-calculation-filing-payment-notice-correction-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-taxpayer-agency-calculation-transparency-procedural-rights-compliance-equity"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_deposit_account_lifecycle_and_financial_inclusion_overlays_are_bound(self):
        value = input_value(
            sections=["deposit-account-comparison-opening-funding-use-restriction-switching-closure-lifecycle"],
            lenses=["financial-inclusion-account-transparency-funds-access-fair-restriction-resolution"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-deposit-account-comparison-opening-funding-use-restriction-switching-closure-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-financial-inclusion-account-transparency-funds-access-fair-restriction-resolution"
                )
                - 1
            ],
            "design-ux-lenses",
        )


    def test_reviewed_essential_utility_lifecycle_and_access_overlay_are_bound(self):
        value = input_value(
            sections=["essential-utility-service-lifecycle"],
            lenses=["essential-service-access-billing-affordability-continuity-remedy"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[packs.index("section-flow-essential-utility-service-lifecycle") - 1],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-essential-service-access-billing-affordability-continuity-remedy"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_procurement_lifecycle_and_integrity_overlay_are_bound(self):
        value = input_value(
            sections=["organizational-procurement-supplier-purchase-order-invoice-lifecycle"],
            lenses=["procurement-integrity-spend-authority-supplier-access-value-accountability"],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-organizational-procurement-supplier-purchase-order-invoice-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-procurement-integrity-spend-authority-supplier-access-value-accountability"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_contract_lifecycle_and_agreement_overlay_are_bound(self):
        value = input_value(
            sections=[
                "contract-authoring-negotiation-approval-signature-obligation-renewal-termination-lifecycle"
            ],
            lenses=[
                "agreement-comprehension-consent-authority-version-integrity-obligation-remedy"
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-contract-authoring-negotiation-approval-signature-obligation-renewal-termination-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-agreement-comprehension-consent-authority-version-integrity-obligation-remedy"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_project_delivery_lifecycle_and_outcome_overlay_are_bound(self):
        value = input_value(
            sections=[
                "project-planning-task-execution-dependency-delivery-learning-lifecycle"
            ],
            lenses=[
                "outcome-clarity-prioritization-dependency-capacity-accountable-delivery-learning"
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-project-planning-task-execution-dependency-delivery-learning-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-outcome-clarity-prioritization-dependency-capacity-accountable-delivery-learning"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_asset_lifecycle_and_accountability_overlay_are_bound(self):
        value = input_value(
            sections=[
                "inventory-asset-acquisition-catalog-custody-use-maintenance-transfer-retirement-lifecycle"
            ],
            lenses=[
                "asset-identity-custody-availability-maintenance-safety-circularity-accountability"
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-inventory-asset-acquisition-catalog-custody-use-maintenance-transfer-retirement-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-asset-identity-custody-availability-maintenance-safety-circularity-accountability"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_expense_lifecycle_and_worker_agency_overlay_are_bound(self):
        value = input_value(
            sections=[
                "business-expense-capture-substantiation-approval-reimbursement-lifecycle"
            ],
            lenses=[
                "expense-policy-legibility-evidence-proportionality-worker-agency-reimbursement-accountability"
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-business-expense-capture-substantiation-approval-reimbursement-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-expense-policy-legibility-evidence-proportionality-worker-agency-reimbursement-accountability"
                )
                - 1
            ],
            "design-ux-lenses",
        )

    def test_reviewed_sales_lifecycle_and_customer_agency_overlay_are_bound(self):
        value = input_value(
            sections=[
                "customer-lead-qualification-opportunity-proposal-close-handoff-lifecycle"
            ],
            lenses=[
                "customer-agency-consent-fit-evidence-forecast-integrity-accountable-handoff"
            ],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        packs = [pack["pack_id"] for pack in draft["catalog_packs"]]
        self.assertEqual(
            packs[
                packs.index(
                    "section-flow-customer-lead-qualification-opportunity-proposal-close-handoff-lifecycle"
                )
                - 1
            ],
            "design-sections-flows",
        )
        self.assertEqual(
            packs[
                packs.index(
                    "lens-customer-agency-consent-fit-evidence-forecast-integrity-accountable-handoff"
                )
                - 1
            ],
            "design-ux-lenses",
        )


class BoundaryTests(unittest.TestCase):
    def test_shared_suite_passes_boundary_scan(self):
        self.assertEqual(BOUNDARY.validate([SUITE]), [])

    def test_candidate_leak_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "guidance.md"
            path.write_text("source " + "mo" + "bbin" + " https://example.invalid/screen.png", encoding="utf-8")
            self.assertTrue(BOUNDARY.validate([path]))

    def test_maintainer_index_leak_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "guidance.md"
            path.write_text("source https://" + "growth." + "design/psychology", encoding="utf-8")
            self.assertTrue(BOUNDARY.validate([path]))

    def test_optional_collection_filters_skill_install(self):
        manifest = {"files": {"skills/continuity/SKILL.md": "x", "skills/continuity-plan/SKILL.md": "x", "skills/continuity-design/SKILL.md": "x", "bin/continuity": "x"}}
        defaults, default_skills = INSTALLER.resolve_collections(SUITE, [], None)
        self.assertEqual(defaults, ["core", "projects"])
        default_map = INSTALLER.install_file_map(SUITE, manifest, default_skills)
        self.assertNotIn(".agents/skills/continuity-design/SKILL.md", default_map)
        enabled, design_skills = INSTALLER.resolve_collections(SUITE, ["design"], None)
        self.assertEqual(enabled, ["core", "design", "projects"])
        design_map = INSTALLER.install_file_map(SUITE, manifest, design_skills)
        self.assertIn(".agents/skills/continuity-design/SKILL.md", design_map)

    def test_shared_design_runtime_has_no_network_imports(self):
        source = (SUITE / "lib" / "design.py").read_text(encoding="utf-8")
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("import socket", source)

    def test_design_collection_installs_adapts_and_runs_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "tests@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Tests"], check=True)
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "initial"], check=True, capture_output=True)
            installed = json.loads(subprocess.run([
                sys.executable, str(SUITE / "installer" / "install.py"), "--project-root", str(root),
                "--project-id", "design-project", "--integration-branch", "main", "--collection", "design",
                "--ignore-user-defaults",
            ], check=True, capture_output=True, text=True).stdout)
            self.assertEqual(installed["suite_version"], "0.1.0-rc.3")
            self.assertTrue((root / ".agents/skills/continuity-design/SKILL.md").is_file())
            self.assertTrue(
                (
                    root
                    / ".agents/skills/continuity-design/references/lens-social-influence-persuasion-integrity.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    root
                    / ".agents/skills/continuity-design/references/composition-precedence.json"
                ).is_file()
            )
            installed_evaluation = json.loads(
                subprocess.run(
                    [
                        sys.executable,
                        str(root / ".agents/continuity/scripts/evaluate_design_scenarios.py"),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
            )
            self.assertTrue(installed_evaluation["healthy"], installed_evaluation)
            self.assertTrue(installed_evaluation["offline"])
            self.assertTrue((root / ".claude/commands/continuity-design.md").is_file())
            self.assertTrue((root / ".agents/skills/continuity-design/scripts/artifact-browser-probe.js").is_file())
            self.assertTrue((root / ".agents/continuity/schemas/design-artifact-manifest.schema.json").is_file())
            config = json.loads((root / ".continuity/config.json").read_text())
            self.assertEqual(config["collections"], ["core", "design", "projects"])
            cli = root / ".agents/continuity/bin/continuity"
            design_input = root / "design-input.json"
            design_input.write_text(json.dumps(input_value()), encoding="utf-8")

            def call(*args):
                result = subprocess.run([str(cli), "--project-root", str(root), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                return json.loads(result.stdout)

            draft_record = call("design", "draft", "--input", str(design_input))
            selected = call("design", "select", draft_record["design_id"], "--direction", "direction-1", "--actor", "human")
            approved = call("design", "approve", draft_record["design_id"], "--revision", "1", "--approved-by", "human", "--authorization-text", selected["required_authorization_text"])
            self.assertFalse(approved["execution_authorized"])
            workflow = call("workflow", "status", "--design-id", draft_record["design_id"])["design"]
            self.assertEqual(workflow["next_skill"], "continuity-plan")
            goal_input = root / "goal.json"
            goal_input.write_text(json.dumps({"goal_id": "goal-design-bound", "title": "Implement approved design", "scope": "Implement the exact approved direction.", "acceptance_criteria": ["Approved behavior is implemented"], "design_ids": [draft_record["design_id"]]}), encoding="utf-8")
            goal = call("goal", "create", "--goal-file", str(goal_input))
            self.assertEqual(goal["design_refs"][0]["design_hash"], approved["design_hash"])
            doctor = call("project", "doctor")
            self.assertTrue(doctor["design_catalog"]["healthy"])
            self.assertEqual(doctor["design_catalog"]["approved_design"]["design_hash"], approved["design_hash"])


if __name__ == "__main__":
    unittest.main()
