from __future__ import annotations

import importlib.util
import json
import runpy
import shutil
import subprocess
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
SUITE_VERSION = (SUITE / "VERSION").read_text(encoding="utf-8").strip()
sys.path.insert(0, str(SUITE / "lib"))
import design
import design_slop

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
OUTPUT_EVALUATION_SPEC = importlib.util.spec_from_file_location(
    "evaluate_design_outputs",
    SUITE / "scripts" / "evaluate_design_outputs.py",
)
OUTPUT_EVALUATION = importlib.util.module_from_spec(OUTPUT_EVALUATION_SPEC)
assert OUTPUT_EVALUATION_SPEC.loader
OUTPUT_EVALUATION_SPEC.loader.exec_module(OUTPUT_EVALUATION)
HOMEPAGE_EVALUATION_SPEC = importlib.util.spec_from_file_location(
    "evaluate_design_homepage",
    SUITE / "scripts" / "evaluate_design_homepage.py",
)
HOMEPAGE_EVALUATION = importlib.util.module_from_spec(HOMEPAGE_EVALUATION_SPEC)
assert HOMEPAGE_EVALUATION_SPEC.loader
HOMEPAGE_EVALUATION_SPEC.loader.exec_module(HOMEPAGE_EVALUATION)
CATALOG = SUITE / "skills" / "continuity-design" / "references" / "catalog.json"
SCENARIOS = SUITE / "skills" / "continuity-design" / "references" / "evaluation-scenarios.json"


def png_bytes(width, height, color=(238, 240, 234, 255)):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    row = b"\x00" + bytes(color) * width
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(row * height)) + chunk(b"IEND", b"")


def input_value(**overrides):
    value = {
        "design_id": "design-test",
        "title": "Test direction",
        "intent": "Set direction before implementation.",
        "audiences": ["Operators"],
        "targets": ["ui"],
        "consequence_level": "moderate",
        "direction_assessment": {"material_ambiguities": [], "resolved_by_evidence": []},
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
    if "modality_assessment" not in overrides:
        target_names = ", ".join(value["targets"])
        value["modality_assessment"] = {
            "observed_signals": [f"The requested output targets {target_names}"],
            "selected_targets": value["targets"],
            "rationale": f"The supplied target evidence identifies {target_names} as the intended modality.",
            "conflicts": [],
        }
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

    def visual_review(self):
        screenshot = self.root / "visual-review.png"
        if not screenshot.exists():
            screenshot.write_bytes(png_bytes(1440, 900))
        return self.visual_review_for([screenshot])

    def visual_review_for(self, screenshots):
        evidence = [
            {"path": path.relative_to(self.root).as_posix(), "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(), "region": "full-frame"}
            for path in screenshots
        ]
        return {
            key: {
                "result": "pass", "finding": "", "rationale": "",
                "reviewer": "test-visual-reviewer", "reviewed_at": "2026-08-08T12:00:00Z",
                "evidence": evidence,
            }
            for key in design.VISUAL_REVIEW_QUESTIONS
        }

    def creative_input(self, **overrides):
        desired_id = overrides.get("design_id", "creative-design")
        seed = design.draft(
            self.root, self.config, CATALOG,
            self.write_input(input_value(design_id=f"{desired_id}-seed")),
        )
        value = input_value(
            workflow_version=2,
            direction_count=1,
            directions=[seed["directions"][0]],
            collaboration_profile="guided",
            concept_presentation_mode="director-led",
            research={"mode": "offline", "status": "not-started", "announced": True, "opt_out_offered": True, "moodboard": []},
            generative_exploration={
                "status": "deliberately-omitted", "mode": "omitted", "required_for_directioning": False,
                "lenses": [], "seeds": [], "cross_pollinations": [], "shortlisted_seed_ids": [],
                "range_plan": {},
                "omission_rationale": "Unit test uses pre-authored directions without expressive media generation.",
            },
        )
        value.update(overrides)
        return value

    def write_slop_manifest(self, stage="concept", **overrides):
        value = {"stage": stage, "ruleset_version": design_slop.RULESET_VERSION, "visual_review": self.visual_review()}
        value.update(overrides)
        path = self.root / f"slop-{stage}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def slop_reference(self, result):
        report_path = self.root / result["report_path"]
        return {
            "path": result["report_path"], "sha256": __import__("hashlib").sha256(report_path.read_bytes()).hexdigest(),
            "report_hash": result["report_hash"], "ruleset_version": result["ruleset_version"],
            "counts_by_severity": result["counts_by_severity"], "dispositions_hash": design._canonical_hash(result["dispositions"]),
            "status": result["status"],
        }

    def test_creative_director_input_infers_profile_and_specialization(self):
        value = self.creative_input(
            design_id="creative-peer", intent="A creative director will co-create a launch system.",
            collaboration_profile="creative-peer", concept_presentation_mode="director-led",
            research={"mode": "declined", "status": "declined", "announced": True, "opt_out_offered": True, "moodboard": []},
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(draft["schema_version"], 2)
        self.assertEqual(draft["collaboration_profile"], "creative-peer")
        self.assertEqual(draft["specialization"], "brand-marketing")
        self.assertEqual(len(draft["directions"]), 1)
        self.assertEqual(draft["slop_ruleset_hash"], design_slop.ruleset_hash())

    def test_creative_director_workflow_is_explicit_and_rejects_generic_recovery(self):
        with self.assertRaisesRegex(design.DesignError, "explicit workflow_version 2"):
            design.draft(self.root, self.config, CATALOG, self.write_input(input_value(collaboration_profile="guided")))
        value = self.creative_input(design_id="missing-authored-direction")
        value.pop("directions")
        with self.assertRaisesRegex(design.DesignError, "agent-authored"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_completed_live_research_requires_numbered_provenance_tiles(self):
        value = self.creative_input(
            design_id="bad-research", collaboration_profile="guided",
            research={"mode": "adaptive-live", "status": "complete", "announced": True, "opt_out_offered": True, "moodboard": []},
        )
        with self.assertRaisesRegex(design.DesignError, "12 to 20"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_completed_live_research_binds_unique_local_captures_axes_and_sources(self):
        moodboard = []
        for index in range(1, 13):
            image = self.root / f"mood-{index}.png"
            image.write_bytes(png_bytes(320, 200, (180 + index, 190, 200, 255)))
            moodboard.append({
                "tile": index,
                "source": f"https://source-{(index % 3) + 1}.example/reference-{index}",
                "captured_at": "2026-08-08T12:00:00Z",
                "intended_lesson": f"Study project-relevant relationship {index}.",
                "axis": "subject-material" if index % 2 else "graphic-spatial",
                "project_mechanic": f"Translate relationship {index} into the project evidence system.",
                "ownership": "third-party", "prohibited_copying": True, "publishable": False,
                "local_path": image.name,
                "sha256": __import__("hashlib").sha256(image.read_bytes()).hexdigest(),
            })
        value = self.creative_input(
            design_id="complete-live-research",
            research={"mode": "adaptive-live", "status": "complete", "announced": True, "opt_out_offered": True, "moodboard": moodboard},
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(len(draft["research"]["moodboard"]), 12)
        self.assertEqual(len({item["sha256"] for item in draft["research"]["moodboard"]}), 12)

        duplicate = json.loads(json.dumps(value))
        duplicate["design_id"] = "duplicate-live-research"
        duplicate["research"]["moodboard"][1]["local_path"] = duplicate["research"]["moodboard"][0]["local_path"]
        duplicate["research"]["moodboard"][1]["sha256"] = duplicate["research"]["moodboard"][0]["sha256"]
        with self.assertRaisesRegex(design.DesignError, "same captured visual"):
            design.draft(self.root, self.config, CATALOG, self.write_input(duplicate))

    def test_third_party_moodboard_tile_cannot_be_marked_publishable(self):
        value = self.creative_input(
            design_id="third-party-promotion", collaboration_profile="guided",
            research={"mode": "offline", "status": "complete", "announced": True, "opt_out_offered": True, "moodboard": [{
                "tile": 1, "source": "https://example.com/reference", "captured_at": "2026-08-08T12:00:00Z",
                "intended_lesson": "Observe the relationship between scale and whitespace.", "axis": "graphic-spatial", "project_mechanic": "Use scale to distinguish source from consequence.",
                "ownership": "third-party", "prohibited_copying": True, "publishable": True,
            }]},
        )
        with self.assertRaisesRegex(design.DesignError, "cannot be publishable"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_generative_concept_laboratory_requires_breadth_and_hash_bound_artifacts(self):
        lenses = [
            {"lens_id": f"lens-{index}", "thesis": f"Explore structural proposition {index}.", "product_truth": f"Project truth {index} must remain visible."}
            for index in range(1, 5)
        ]
        media = ["image-generation", "svg", "typography", "motion-frame", "image-editing", "collage", "code-sketch", "svg"]
        seeds = []
        for index, medium in enumerate(media, 1):
            artifact = self.root / f"seed-{index}.png"
            artifact.write_bytes(png_bytes(320 + index, 200, (180 + index, 190, 200, 255)))
            seeds.append({
                "seed_id": f"seed-{index}", "lens_id": f"lens-{((index - 1) % 4) + 1}", "medium": medium,
                "art_direction_family": ["photographic", "illustrative", "typographic", "spatial"][(index - 1) % 4],
                "typography_strategy_id": ["type-serif", "type-humanist", "type-mono"][(index - 1) % 3],
                "composition_family": ["editorial-sequence", "spatial-field", "typographic-poster"][(index - 1) % 3],
                "page_depth_roles": [["opening"], ["orientation"], ["proof"], ["edge-state"], ["closure"]][(index - 1) % 5],
                "hypothesis": f"Seed {index} tests a different organizing relationship.",
                "project_specificity": f"It makes project truth {((index - 1) % 4) + 1} visible.",
                "surprising_quality": f"It changes the expected reading order {index}.",
                "transferable_mechanics": [f"Carry relationship {index} into hierarchy."],
                "risk": "Could become decorative if detached from product proof.", "provenance": "generated",
                "artifact": {"path": artifact.name, "sha256": __import__("hashlib").sha256(artifact.read_bytes()).hexdigest()},
            })
        typography_hypotheses = []
        for strategy_id, family, source in (("type-serif", "serif", "open-licensed"), ("type-humanist", "humanist-sans", "system"), ("type-mono", "monospaced", "code-native")):
            specimen = self.root / f"{strategy_id}-specimen.svg"
            specimen.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><text x="30" y="120">{strategy_id} display</text><text x="30" y="220">Evidence text at narrow measure.</text></svg>', encoding="utf-8")
            typography_hypotheses.append({
                "strategy_id": strategy_id, "family": family, "source": source,
                "role_relationship": "Display establishes identity while utility text keeps evidence literal.",
                "responsive_behavior": "Display measure narrows before scale reduces and evidence remains readable.",
                "anti_default": "No interchangeable model-default type stack.",
                "customization": "Spacing, measure, and role contrast derive from the tested project relationship.",
                "license_evidence": "Test fixture uses a system, open-licensed, or code-native specimen without distribution rights claims.",
                "behavior_tests": ["display", "text", "narrow"],
                "specimen": {"path": specimen.name, "sha256": __import__("hashlib").sha256(specimen.read_bytes()).hexdigest()},
            })
        interaction_hypotheses = []
        for strategy_id, mode in (("motion-disclosure", "native-disclosure"), ("motion-direct", "direct-manipulation"), ("motion-spatial", "spatial-transition")):
            prototype = self.root / f"{strategy_id}.html"
            prototype.write_text(f"<main><button>{strategy_id}</button><p>Static equivalent remains visible.</p></main>", encoding="utf-8")
            interaction_hypotheses.append({
                "strategy_id": strategy_id, "mode": mode,
                "semantic_purpose": "Reveal one consequential relationship without hiding the default truth.",
                "reduced_motion": "Remove interpolation while preserving the state change and reading order.",
                "static_fallback": "Render every label and outcome in the initial document.",
                "risk": "Could become decorative if the transition is detached from authority.",
                "prototype": {"path": prototype.name, "sha256": __import__("hashlib").sha256(prototype.read_bytes()).hexdigest()},
            })
        style_frame_groups = []
        for group_index, family in enumerate(("photographic", "illustrative"), 1):
            frames = []
            for frame_index in (1, 2):
                frame = self.root / f"style-{group_index}-{frame_index}.png"
                frame.write_bytes(png_bytes(480 + frame_index, 300, (130 + group_index * 20, 150 + frame_index * 10, 180, 255)))
                frames.append({"frame_id": f"style-{group_index}-{frame_index}", "method": "generated" if family == "photographic" else "code-native", "lesson": f"Test {family} relationship {frame_index}.", "artifact": {"path": frame.name, "sha256": __import__("hashlib").sha256(frame.read_bytes()).hexdigest()}})
            style_frame_groups.append({"exploration_id": f"style-group-{group_index}", "art_direction_family": family, "hypothesis": f"Compare two {family} systems before commitment.", "frames": frames, "selected_frame_ids": [frames[0]["frame_id"]], "rejected_frame_ids": [frames[1]["frame_id"]], "system_extractions": ["Extract the composition rule.", "Extract the typography relationship.", "Extract the material or motion behavior."], "synthesis": "The selected frame produced a stronger project-specific system."})
        laboratory = {
            "status": "complete", "mode": "mixed-media", "required_for_directioning": True,
            "range_plan": {
                "art_direction_families": ["photographic", "illustrative", "typographic", "spatial"],
                "typography_hypotheses": typography_hypotheses,
                "composition_families": ["editorial-sequence", "spatial-field", "typographic-poster"],
                "page_depth_roles": ["opening", "orientation", "proof", "edge-state", "closure"],
                "page_grammar_hypotheses": [
                    {"grammar_id": "grammar-long", "family": "longform-narrative", "hypothesis": "A sequential argument can build trust.", "responsive_behavior": "Chapters stack without losing proof adjacency.", "depth_proof": "Opening, proof, edge, and closure use different compositions.", "risk": "Could collapse into a conventional landing page."},
                    {"grammar_id": "grammar-canvas", "family": "single-canvas-instrument", "hypothesis": "One operable canvas can teach the model.", "responsive_behavior": "The canvas becomes a vertical control trace.", "depth_proof": "Interaction, proof, edge, and decision remain addressable.", "risk": "Could hide narrative depth."},
                    {"grammar_id": "grammar-issue", "family": "editorial-issue", "hypothesis": "An issue structure can make time and evidence tangible.", "responsive_behavior": "Spreads become ordered mobile articles.", "depth_proof": "Sections retain different editorial roles.", "risk": "Could become premium editorial styling."},
                    {"grammar_id": "grammar-spatial", "family": "spatial-journey", "hypothesis": "Topology can organize authority.", "responsive_behavior": "Routes become a linear evidence trace.", "depth_proof": "The field includes opening, proof, quiet, and closure nodes.", "risk": "Could become a generic node map."},
                ],
                "interaction_motion_hypotheses": interaction_hypotheses,
                "intentional_convergence": "",
            },
            "lenses": lenses, "seeds": seeds,
            "cross_pollinations": [
                {"combination_id": "cross-a", "seed_ids": ["seed-1", "seed-3"], "hypothesis": "Combine image scale with typographic interruption.", "resulting_mechanics": ["Type interrupts the image boundary."]},
                {"combination_id": "cross-b", "seed_ids": ["seed-2", "seed-4"], "hypothesis": "Combine diagram structure with time.", "resulting_mechanics": ["State changes reshape the spatial diagram."]},
            ],
            "style_frame_explorations": style_frame_groups,
            "shortlisted_seed_ids": ["seed-1", "seed-2", "seed-3", "seed-4"], "omission_rationale": "",
        }
        lab_path = self.root / "laboratory.json"
        lab_path.write_text(json.dumps(laboratory), encoding="utf-8")
        result = design.concept_lab_validate(self.root, self.config, lab_path)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["seed_count"], 8)
        self.assertEqual(result["media_count"], 7)
        value = self.creative_input(design_id="lab-backed", generative_exploration=laboratory)
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(draft["generative_exploration"]["laboratory_hash"], result["laboratory_hash"])

        too_narrow = json.loads(json.dumps(laboratory))
        too_narrow["seeds"] = too_narrow["seeds"][:7]
        with self.assertRaisesRegex(design.DesignError, "eight to twelve"):
            design._validate_generative_exploration(too_narrow, self.root)

        collapsed_range = json.loads(json.dumps(laboratory))
        collapsed_range["range_plan"]["art_direction_families"] = ["photographic", "illustrative", "typographic"]
        with self.assertRaisesRegex(design.DesignError, "four distinct art-direction"):
            design._validate_generative_exploration(collapsed_range, self.root)
        single_frame = json.loads(json.dumps(laboratory))
        single_frame["style_frame_explorations"][0]["frames"] = single_frame["style_frame_explorations"][0]["frames"][:1]
        with self.assertRaisesRegex(design.DesignError, "two to four frames"):
            design._validate_generative_exploration(single_frame, self.root)
        system_only_type = json.loads(json.dumps(laboratory))
        for hypothesis in system_only_type["range_plan"]["typography_hypotheses"]:
            hypothesis["source"] = "system"
        with self.assertRaisesRegex(design.DesignError, "at least one supplied, licensed"):
            design._validate_generative_exploration(system_only_type, self.root)
        collapsed_page_grammar = json.loads(json.dumps(laboratory))
        collapsed_page_grammar["range_plan"]["page_grammar_hypotheses"] = collapsed_page_grammar["range_plan"]["page_grammar_hypotheses"][:3]
        with self.assertRaisesRegex(design.DesignError, "four to seven page-grammar"):
            design._validate_generative_exploration(collapsed_page_grammar, self.root)

    def test_visual_atlas_is_private_self_contained_and_network_free(self):
        request = self.root / "atlas.json"
        request.write_text(json.dumps({"title": "Material contrasts", "project_copy": "Inspect the source before approval.", "contrasts": ["editorial evidence", "technical index"]}), encoding="utf-8")
        result = design.visual_atlas(self.root, self.config, CATALOG, request)
        text = (self.root / result["path"]).read_text(encoding="utf-8")
        self.assertTrue(result["private"])
        self.assertFalse(result["network_used"])
        self.assertEqual(result["plate_count"], 2)
        self.assertIn('data-system="editorial-asymmetry"', text)
        self.assertIn('data-system="technical-index"', text)
        self.assertNotIn("http://", text)
        self.assertNotIn("https://", text)

    def test_design_improvement_cycle_is_resumable_hash_bound_and_human_gated(self):
        baseline_eval = self.root / "baseline-evaluation.json"
        baseline_eval.write_text(json.dumps({"stage_valid": True, "status": "directions"}), encoding="utf-8")
        baseline_assessment = self.root / "baseline-assessment.md"
        baseline_assessment.write_text("The concepts need a stronger impact gate.", encoding="utf-8")
        improved_eval = self.root / "improved-evaluation.json"
        improved_eval.write_text(json.dumps({"stage_valid": True, "status": "directions"}), encoding="utf-8")
        improved_assessment = self.root / "improved-assessment.md"
        improved_assessment.write_text("At least one concept is now compelling.", encoding="utf-8")
        changed = self.root / "changed-schema.json"
        changed.write_text(json.dumps({"impact_review": "required"}), encoding="utf-8")
        ref = lambda path: {"path": path.name, "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}
        cycle = {
            "schema_version": 1, "cycle_id": "cycle-001", "design_id": "benchmark-homepage",
            "objective": "Raise the creative ceiling without weakening evidence gates.", "max_passes": 3,
            "source": {"branch": "feature/design", "commit": "a" * 40, "skill_sha256": "b" * 64},
            "baseline": {"benchmark_evaluation": ref(baseline_eval), "self_assessment": ref(baseline_assessment)},
            "passes": [{
                "pass_number": 1, "status": "awaiting-human",
                "findings": [{"finding_id": "impact-gate", "category": "creative-impact", "observation": "Range validation cannot prove impact.", "action": "Require a separate multimodal impact review.", "success_metric": "At least one concept is compelling and every signature controls three roles."}],
                "changes": [{"finding_ids": ["impact-gate"], "description": "Added impact evidence and validation.", "artifacts": [ref(changed)]}],
                "validation": {"passed": True, "benchmark_evaluation": ref(improved_eval), "self_assessment": ref(improved_assessment), "source_tests": [{"name": "focused design tests", "status": "passed"}]},
                "human_gate": {"required": True, "status": "pending"},
            }],
        }
        cycle_path = self.root / "cycle.json"
        cycle_path.write_text(json.dumps(cycle), encoding="utf-8")
        result = design.improvement_cycle(self.root, self.config, cycle_path)
        self.assertEqual(result["next_gate"], "human-feedback")
        self.assertFalse(result["execution_authorized"])
        persisted = json.loads((self.root / result["record_path"]).read_text(encoding="utf-8"))
        self.assertEqual(persisted["passes"][0]["status"], "awaiting-human")
        invalid = json.loads(json.dumps(cycle))
        invalid["passes"][0]["status"] = "accepted"
        invalid["passes"][0]["human_gate"] = {"required": True, "status": "accepted"}
        invalid_path = self.root / "cycle-invalid.json"
        invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "identified human"):
            design.improvement_cycle(self.root, self.config, invalid_path)

    def test_private_renderer_supports_moodboards_concepts_and_visual_deltas(self):
        wide = self.root / "render-wide.png"
        narrow = self.root / "render-narrow.png"
        changed = self.root / "render-changed.png"
        wide.write_bytes(png_bytes(1200, 800, (238, 240, 234, 255)))
        narrow.write_bytes(png_bytes(390, 800, (219, 226, 221, 255)))
        changed.write_bytes(png_bytes(1200, 800, (225, 231, 235, 255)))
        for kind in ("moodboard", "concept-comparison", "visual-delta"):
            with self.subTest(kind=kind):
                request = self.root / f"{kind}.json"
                item = {"number": 1, "title": "Evidence rail", "summary": "A structural study", "lesson": "Keep proof attached", "source": "project-owned study"}
                if kind == "moodboard":
                    item["image_path"] = wide.name
                elif kind == "concept-comparison":
                    item.update({"wide_image_path": wide.name, "narrow_image_path": narrow.name})
                else:
                    item.update({"before_image_path": wide.name, "after_image_path": changed.name})
                request.write_text(json.dumps({"kind": kind, "title": f"{kind} evidence", "items": [item]}), encoding="utf-8")
                result = design.visual_render(self.root, self.config, request)
                rendered = (self.root / result["path"]).read_text(encoding="utf-8")
                self.assertTrue(result["private"])
                self.assertFalse(result["network_used"])
                self.assertIn("Evidence rail", rendered)
                self.assertIn("Neutral comparison chrome", rendered)

    def test_slop_check_detects_hard_and_default_risks(self):
        source = self.root / "risk.css"
        source.write_text(".hero { transition: all .3s; background: linear-gradient(90deg,#8b5cf6,#3b82f6); }", encoding="utf-8")
        result = design.slop_check(self.root, self.config, source, self.write_slop_manifest())
        self.assertEqual(result["status"], "failed")
        self.assertEqual({item["rule_id"] for item in result["findings"]}, {"CDS-H004", "CDS-D001"})

    def test_static_slop_rules_have_positive_detection_fixtures(self):
        fixtures = {
            "CDS-H001": "<video autoplay src='clip.mp4'></video>",
            "CDS-H002": "const scene = new WebGLRenderer();",
            "CDS-H003": "main { opacity: 0; }",
            "CDS-H004": ".thing { transition: all .2s; }",
            "CDS-H005": "window.addEventListener('scroll', update);",
            "CDS-D001": ".hero{background:linear-gradient(90deg,#8b5cf6,#3b82f6)}",
            "CDS-D002": ".headline{background:linear-gradient(red,blue);background-clip:text}",
            "CDS-D003": ":root{--surface:#faf7f0}",
            "CDS-D004": ".body{font-family:'Space Grotesk',sans-serif}",
            "CDS-D005": ".glass{backdrop-filter:blur(12px);background:rgba(255,255,255,.4)}",
            "CDS-D006": ".a{border-radius:24px}.b{border-radius:24px}.c{border-radius:24px}",
            "CDS-D007": "<div class='bento-grid'></div>",
            "CDS-D008": "<p class='eyebrow'>A</p><p class='eyebrow'>B</p><p class='eyebrow'>C</p>",
            "CDS-D009": "<p>01. One</p><p>02. Two</p><p>03. Three</p>",
            "CDS-D010": ".a{text-align:center}.b{text-align:center}.c{text-align:center}.d{text-align:center}.e{text-align:center}",
            "CDS-D011": "<div class='fade-up'></div><div class='fade-up'></div><div class='fade-up'></div>",
            "CDS-D012": "<section class='hero'><div class='stat'>1</div><div class='metric'>2</div></section>",
            "CDS-D013": ".orb{box-shadow:0 0 40px #8b5cf6}",
            "CDS-D014": "<img src='https://images.unsplash.com/example'>",
            "CDS-D015": "<h1>Revolutionize your work</h1>",
            "CDS-D016": "One — two — three — four — five.",
            "CDS-D017": ".terminal{background:#000;color:#39ff14;font-family:monospace}",
        }
        for rule_id, source in fixtures.items():
            with self.subTest(rule_id=rule_id):
                actual = {item["rule_id"] for item in design_slop._scan_text("fixture", source)}
                self.assertIn(rule_id, actual)

    def test_hero_metric_rule_does_not_treat_station_as_stat(self):
        source = "<section class='hero'><p>One connected station</p><div class='proof'>Current</div></section>"
        self.assertNotIn("CDS-D012", {item["rule_id"] for item in design_slop._scan_text("fixture", source)})

    def test_slop_check_rejects_stale_ruleset_and_unqualified_generated_claim(self):
        source = self.root / "claim.html"
        source.write_text("<main><h1>Illustrative outcome</h1></main>", encoding="utf-8")
        stale = self.write_slop_manifest(ruleset_version="0.9.0")
        with self.assertRaisesRegex(design.DesignError, "stale"):
            design.slop_check(self.root, self.config, source, stale)
        result = design.slop_check(self.root, self.config, source, self.write_slop_manifest(
            generated_claims=[{"location": "claim.html#outcome", "visible_qualification": "", "provenance": ""}]
        ))
        self.assertIn("CDS-H006", {item["rule_id"] for item in result["findings"]})

    def test_slop_report_manifest_summary_is_hash_bound(self):
        source = self.root / "bound.html"
        source.write_text("<main><h1>Bound evidence</h1></main>", encoding="utf-8")
        result = design.slop_check(self.root, self.config, source, self.write_slop_manifest())
        reference = self.slop_reference(result)
        reference["counts_by_severity"] = {**reference["counts_by_severity"], "warning": 1}
        with self.assertRaisesRegex(design.DesignError, "summary"):
            design._verified_private_report(self.root, reference, stage="concept")

    def test_context_slop_layer_detects_contract_reference_rejection_and_house_drift(self):
        source = self.root / "drift.html"
        source.write_text("<main class='unapproved-radius copied-brand generic-proof-grid'>Reference identity</main>", encoding="utf-8")
        manifest = self.write_slop_manifest(project_context={
            "unapproved_markers": ["unapproved-radius"],
            "required_signature_markers": ["approved-evidence-rail"],
            "reference_transformations": [{"reference_identity_marker": "copied-brand", "project_transformation_marker": "project-proof-rail"}],
            "rejected_choices": ["generic-proof-grid"],
            "continuity_house_tells": ["reference identity"],
        })
        result = design.slop_check(self.root, self.config, source, manifest)
        self.assertEqual(
            {item["rule_id"] for item in result["findings"]},
            {"CDS-P001", "CDS-P002", "CDS-P003", "CDS-P004", "CDS-P005"},
        )
        self.assertEqual(result["status"], "failed")

    def test_default_risk_can_be_intentionally_accepted_with_contract_evidence(self):
        source = self.root / "approved.css"
        source.write_text(".signal { background: linear-gradient(90deg,#8b5cf6,#3b82f6); }", encoding="utf-8")
        manifest = self.write_slop_manifest(dispositions=[{
            "rule_id": "CDS-D001", "status": "accepted-intentional",
            "rationale": "The approved spectrograph uses this measured wavelength mapping.",
            "contract_reference": "Design contract / Signature move",
        }])
        result = design.slop_check(self.root, self.config, source, manifest)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["dispositions"][0]["status"], "accepted-intentional")

    def test_hash_bound_craft_finding_shape_can_accept_intentional_default(self):
        source = self.root / "intentional.css"
        source.write_text(".signal { background: linear-gradient(90deg,#8b5cf6,#3b82f6); }", encoding="utf-8")
        manifest = self.write_slop_manifest(craft_findings=[{
            "rule_id": "CDS-D001", "status": "accepted-intentional", "artifact_ref": "Design contract / Signature move",
            "evidence": "Rendered spectrograph wavelength mapping.", "override_rationale": "The approved subject encodes wavelength with this exact range.",
        }])
        result = design.slop_check(self.root, self.config, source, manifest)
        self.assertEqual(result["status"], "passed")

    def test_hard_failure_cannot_be_suppressed_as_intentional(self):
        source = self.root / "unsafe.css"
        source.write_text(".thing { transition: all .3s; }", encoding="utf-8")
        manifest = self.write_slop_manifest(dispositions=[{
            "rule_id": "CDS-H004", "status": "accepted-intentional", "rationale": "Wanted", "contract_reference": "contract",
        }])
        with self.assertRaisesRegex(design.DesignError, "cannot be accepted"):
            design.slop_check(self.root, self.config, source, manifest)

    def test_hard_failure_cannot_be_marked_not_applicable(self):
        source = self.root / "unsafe-not-applicable.css"
        source.write_text(".thing { transition: all .3s; }", encoding="utf-8")
        manifest = self.write_slop_manifest(dispositions=[{
            "rule_id": "CDS-H004", "status": "not-applicable", "rationale": "Claimed false positive", "evidence": "No exception is valid.",
        }])
        with self.assertRaisesRegex(design.DesignError, "cannot be accepted or marked not applicable"):
            design.slop_check(self.root, self.config, source, manifest)

    def test_visual_review_requires_hash_bound_structured_evidence(self):
        source = self.root / "clean-review.html"
        source.write_text("<main><h1>Project-specific evidence</h1></main>", encoding="utf-8")
        manifest = self.write_slop_manifest(visual_review={key: "not actually reviewed" for key in design.VISUAL_REVIEW_QUESTIONS})
        with self.assertRaisesRegex(design.DesignError, "requires pass, fail, or not-applicable"):
            design.slop_check(self.root, self.config, source, manifest)

    def test_failed_visual_review_becomes_a_blocking_finding(self):
        source = self.root / "visual-failure.html"
        source.write_text("<main><h1>Project evidence</h1></main>", encoding="utf-8")
        review = self.visual_review()
        review["directions_structurally_distinct"] = {
            **review["directions_structurally_distinct"],
            "result": "fail",
            "finding": "The alternatives share the same hierarchy and differ only by palette.",
        }
        result = design.slop_check(self.root, self.config, source, self.write_slop_manifest(visual_review=review))
        self.assertEqual(result["status"], "failed")
        self.assertIn("CDS-D019", {item["rule_id"] for item in result["findings"]})

    def test_visual_slop_questions_cover_identity_category_and_decorative_work(self):
        mappings = {
            "identity_specific": "CDS-D018",
            "not_category_reflex": "CDS-D017",
            "directions_structurally_distinct": "CDS-D019",
            "decoration_has_job": "CDS-D020",
        }
        for question, rule_id in mappings.items():
            with self.subTest(question=question):
                source = self.root / f"{question}.html"
                source.write_text("<main><h1>Project evidence</h1></main>", encoding="utf-8")
                review = self.visual_review()
                review[question] = {**review[question], "result": "fail", "finding": f"Failed review question: {question}"}
                result = design.slop_check(self.root, self.config, source, self.write_slop_manifest(visual_review=review))
                self.assertEqual(result["status"], "failed")
                self.assertIn(rule_id, {item["rule_id"] for item in result["findings"]})

    def test_third_party_reference_promotion_is_a_hard_failure(self):
        source = self.root / "clean.html"
        source.write_text("<main><h1>Project evidence</h1></main>", encoding="utf-8")
        manifest = self.write_slop_manifest(promoted_references=[{"path": "refs/example.png", "ownership": "third-party"}])
        result = design.slop_check(self.root, self.config, source, manifest)
        self.assertEqual(result["status"], "failed")
        self.assertIn("CDS-H007", {item["rule_id"] for item in result["findings"]})

    def test_adversarial_slop_fixture_corpus_recall_and_nearby_precision(self):
        fixture_root = SUITE / "skills" / "continuity-design" / "references" / "slop-fixtures"
        expectations = json.loads((fixture_root / "expectations.json").read_text(encoding="utf-8"))
        for name, expected in expectations.items():
            with self.subTest(name=name):
                findings = design_slop._scan_text(name, (fixture_root / name).read_text(encoding="utf-8"))
                self.assertEqual(sorted({item["rule_id"] for item in findings}), sorted(expected))

    def test_concept_feedback_gates_selection_and_invalidates_changed_revision(self):
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(self.creative_input(
            design_id="concept-loop", collaboration_profile="guided", concept_presentation_mode="director-led",
            research={"mode": "offline", "status": "complete", "announced": True, "opt_out_offered": True, "moodboard": []},
        )))
        concept_visuals = {}
        concept_visual_paths = {}
        for name, width, color in (
            ("direction-wide", 1440, (238, 240, 234, 255)),
            ("direction-narrow", 390, (221, 229, 224, 255)),
            ("study-wide", 1440, (231, 226, 216, 255)),
            ("study-narrow", 390, (215, 221, 229, 255)),
        ):
            visual = self.root / f"{name}.png"
            visual.write_bytes(png_bytes(width, 900, color))
            concept_visual_paths[name] = visual
            concept_visuals[name] = {"path": visual.name, "sha256": __import__("hashlib").sha256(visual.read_bytes()).hexdigest()}
        source = self.root / "concept.html"
        source.write_text("<main><h1>Operational evidence</h1><p>A calm direct path.</p></main>", encoding="utf-8")
        slop = design.slop_check(self.root, self.config, source, self.write_slop_manifest(
            design_id=draft["design_id"], revision=draft["revision"],
            visual_review=self.visual_review_for([concept_visual_paths["direction-wide"], concept_visual_paths["direction-narrow"]]),
        ))
        file_hash = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
        contrast = self.root / "contrast.html"
        contrast.write_text("<main><h1>Infrastructure field notes</h1><p>A spatial inspection path.</p></main>", encoding="utf-8")
        contrast_slop = design.slop_check(self.root, self.config, contrast, self.write_slop_manifest(
            design_id=draft["design_id"], revision=draft["revision"],
            visual_review=self.visual_review_for([concept_visual_paths["study-wide"], concept_visual_paths["study-narrow"]]),
        ))
        browser_snapshots = []
        browser_probes = []
        direction_probes = []
        study_probes = []
        for viewport, width in (("mobile", 390), ("tablet", 768), ("desktop", 1440)):
            snapshot = self.root / f"concept-{viewport}.png"
            snapshot.write_bytes(png_bytes(width, 900, (235, 237, 234, 255)))
            browser_snapshots.append({"viewport": viewport, "path": snapshot.name, "sha256": __import__("hashlib").sha256(snapshot.read_bytes()).hexdigest()})
            probe = self.root / f"concept-{viewport}-probe.json"
            probe.write_text(json.dumps({"schema_version": 2, "viewport": {"width": width, "height": 900}, "horizontal_overflow": False, "sticky_or_fixed_obstructions": [], "craft_findings": [], "passed": True}), encoding="utf-8")
            browser_probes.append({"viewport": viewport, "path": probe.name, "sha256": __import__("hashlib").sha256(probe.read_bytes()).hexdigest()})
            for concept_name, probe_collection in (("direction", direction_probes), ("study", study_probes)):
                concept_probe = self.root / f"{concept_name}-{viewport}-probe.json"
                concept_probe.write_text(json.dumps({"schema_version": 2, "concept_id": concept_name, "viewport": {"width": width, "height": 900}, "horizontal_overflow": False, "sticky_or_fixed_obstructions": [], "craft_findings": [], "passed": True}), encoding="utf-8")
                probe_collection.append({"viewport": viewport, "path": concept_probe.name, "sha256": __import__("hashlib").sha256(concept_probe.read_bytes()).hexdigest()})
        direction_journey = [
            {"stage_id": "opening-proof", "role": "opening", "purpose": "State the authority thesis.", "signature_expression": "The proof rail interrupts the opening claim."},
            {"stage_id": "orientation", "role": "orientation", "purpose": "Explain the evidence model.", "signature_expression": "Proof labels establish the reading order."},
            {"stage_id": "project-proof", "role": "proof", "purpose": "Demonstrate accountable evidence.", "signature_expression": "Each claim carries adjacent source material."},
            {"stage_id": "blocked-edge", "role": "edge-state", "purpose": "Show review-ready without completion.", "signature_expression": "The rail stops before authority."},
            {"stage_id": "closure", "role": "closure", "purpose": "Return responsibility to the person.", "signature_expression": "The final proof seam remains visibly human-held."},
        ]
        study_journey = [
            {"stage_id": "opening-field", "role": "opening", "purpose": "Introduce the inspection space.", "signature_expression": "Spatial routes begin at the source boundary."},
            {"stage_id": "orientation-map", "role": "orientation", "purpose": "Teach the topology.", "signature_expression": "Labels define navigable evidence regions."},
            {"stage_id": "inspection-proof", "role": "proof", "purpose": "Trace source to consequence.", "signature_expression": "Material and outcome share a visible seam."},
            {"stage_id": "quiet-route", "role": "quiet-state", "purpose": "Preserve the model without activity.", "signature_expression": "Static topology retains ownership boundaries."},
            {"stage_id": "closure-boundary", "role": "closure", "purpose": "End at exact authority.", "signature_expression": "The final route remains closed until selected."},
        ]
        concept_manifest = self.root / "concept.json"
        concept_manifest.write_text(json.dumps({
            "design_id": draft["design_id"], "revision": draft["revision"], "presentation_mode": "director-led",
            "collaboration_delivery": {"profile": draft["collaboration_profile"], **draft["collaboration_contract"], "feedback_prompt": "React to elements 1 through 5 in plain language."},
            "concepts": [{
                "role": "direction", "direction_id": "direction-1", "recommended": True, "thesis": "Evidence before ornament.",
                "impact_thesis": "Make authority legible before asking for trust.", "primary_carrier": "narrative", "emotional_register": "calm scrutiny", "seed_lineage": [], "system_extractions": [],
                "signature_move": "A proof rail attached to each decision.", "palette": ["paper", "carbon", "signal"],
                "type_specimen": {"copy": "Review the source before approval."}, "wide_composition": concept_visuals["direction-wide"],
                "typography_system": {"strategy_id": "type-proof-serif", "family": "serif", "display_behavior": "Reflective serif claims are interrupted by proof labels.", "text_behavior": "Humanist utility text remains literal and compact.", "responsive_behavior": "Claims narrow before scale reduces and proof follows immediately.", "rationale": "The contrast separates judgment from evidence."},
                "media_system": {"art_direction_family": "documentary", "primary_role": "Owned evidence material proves each claim.", "asset_mix": ["project-owned"], "quiet_state": "Captions and source seams remain without imagery.", "fallback": "Use a qualified no-evidence state."},
                "composition_family": "editorial-sequence",
                "page_grammar": {"grammar_id": "grammar-proof-issue", "family": "editorial-issue", "core_behavior": "Claims and proof form an evidence issue.", "responsive_behavior": "Spreads become ordered mobile evidence articles.", "depth_proof": "Opening, proof, edge, and closure use distinct issue structures."},
                "interaction_motion_system": {"strategy_id": "interaction-proof-disclosure", "mode": "native-disclosure", "semantic_purpose": "Reveal proof without losing its claim.", "reduced_motion": "Use immediate disclosure.", "static_fallback": "All proof remains in document order."},
                "journey_stages": direction_journey,
                "comparison_coverage": {"full_page_strip": concept_visuals["direction-narrow"], "chapter_index": [item["stage_id"] for item in direction_journey], "deep_link": {"path": source.name, "sha256": file_hash}},
                "generated_media_disposition": {"status": "not-applicable", "rationale": "This unit-test direction has no generated-image lineage."},
                "runtime_probes": direction_probes,
                "narrow_transformation": concept_visuals["direction-narrow"], "imagery_treatment": "Owned working evidence only.",
                "motion_decision": "No ambient motion.", "preservation_promise": "Keep the expert path direct.",
                "tradeoff": "Less simultaneous overview.", "anti_reference": "No generic dashboard bento.", "fidelity_level": "board-v1",
                "slop_report": self.slop_reference(slop),
            }, {
                "role": "contrast-study", "study_id": "study-spatial-inspection", "tests_uncertainty": "Whether spatial evidence improves confidence without slowing expert review.",
                "recommended": False, "thesis": "Inspection creates confidence.",
                "impact_thesis": "Turn system relationships into a place the user can inspect.", "primary_carrier": "spatial-system", "emotional_register": "active investigation", "seed_lineage": [], "system_extractions": [],
                "signature_move": "A spatial field-note seam connecting material to consequence.", "palette": ["field", "graphite", "safety"],
                "type_specimen": {"copy": "Inspect the system from source to outcome."}, "wide_composition": concept_visuals["study-wide"],
                "typography_system": {"strategy_id": "type-spatial-mono", "family": "monospaced", "display_behavior": "Monospaced coordinates establish the field.", "text_behavior": "A humanist sans carries explanations.", "responsive_behavior": "Coordinates become a sequential mobile index.", "rationale": "The type acts as navigational evidence rather than a terminal costume."},
                "media_system": {"art_direction_family": "diagrammatic", "primary_role": "Code-native topology explains authority boundaries.", "asset_mix": ["code-native"], "quiet_state": "Static routes preserve every ownership relationship.", "fallback": "Render a labeled linear source-to-outcome path."},
                "composition_family": "spatial-field",
                "page_grammar": {"grammar_id": "grammar-inspection-field", "family": "single-canvas-instrument", "core_behavior": "One field supports inspection and consequence.", "responsive_behavior": "The field becomes a vertical control trace.", "depth_proof": "Opening, proof, quiet state, and closure remain addressable."},
                "interaction_motion_system": {"strategy_id": "interaction-spatial-trace", "mode": "direct-manipulation", "semantic_purpose": "Trace source to consequence.", "reduced_motion": "Update state without interpolation.", "static_fallback": "Render the complete labeled route."},
                "journey_stages": study_journey,
                "comparison_coverage": {"full_page_strip": concept_visuals["study-narrow"], "chapter_index": [item["stage_id"] for item in study_journey], "deep_link": {"path": contrast.name, "sha256": __import__("hashlib").sha256(contrast.read_bytes()).hexdigest()}},
                "generated_media_disposition": {"status": "not-applicable", "rationale": "This unit-test study has no generated-image lineage."},
                "runtime_probes": study_probes,
                "narrow_transformation": concept_visuals["study-narrow"], "imagery_treatment": "Owned infrastructure details with annotated scale.",
                "motion_decision": "One state-led spatial transition with a static equivalent.", "preservation_promise": "Keep the expert path direct.",
                "tradeoff": "More deliberate scanning.", "anti_reference": "No copied aerospace identity.", "fidelity_level": "board-v1",
                "slop_report": self.slop_reference(contrast_slop),
            }],
            "creative_range": {
                "status": "passed", "reviewer": "test-creative-reviewer", "reviewed_at": "2026-08-08T12:00:00Z",
                "five_second_reactions": [
                    {"concept_id": "direction-1", "reaction": "A restrained proof ledger."},
                    {"concept_id": "study-spatial-inspection", "reaction": "An explorable field map."},
                ],
                "pairwise_distances": [{"concept_ids": ["direction-1", "study-spatial-inspection"], "differing_dimensions": ["organizing-idea", "primary-carrier", "responsive-transformation"], "rationale": "One is a linear proof narrative while the other is a spatial inspection model."}],
                "house_tell_review": {"recurring_tells_checked": ["serif-plus-mono", "thin-rules", "quiet-field", "orange-interruption"], "project_identity_wins": True, "rationale": "Authority and inspection determine the systems, not a recurring Continuity palette or type pairing."},
                "adversarial_pass": [
                    {"concept_id": "direction-1", "genericity_argument": "Could resemble editorial enterprise software.", "opposing_hypothesis": "Proof should alter the reading path, not decorate it.", "resulting_change": "Bound evidence to every consequential decision.", "rejected_choice": "Detached credibility logo row."},
                    {"concept_id": "study-spatial-inspection", "genericity_argument": "Could become a generic node map.", "opposing_hypothesis": "The map should expose authority boundaries.", "resulting_change": "Made authorization state change topology.", "rejected_choice": "Decorative network particles."},
                ],
                "range_audit": {"status": "passed", "typography_strategy_count": 2, "typography_family_count": 2, "art_direction_family_count": 2, "composition_family_count": 2, "page_grammar_count": 2, "interaction_motion_strategy_count": 2, "minimum_journey_stage_count": 5, "per_concept_runtime_probes": True, "comparison_depth_coverage": True, "generated_media_extraction_passed": True, "rationale": "The direction and study use different type, media, composition, page grammar, interaction, and full-page journey systems."},
            },
            "impact_review": {
                "status": "passed", "reviewer_type": "agent-multimodal", "reviewer": "test-impact-reviewer", "reviewed_at": "2026-08-08T12:00:00Z", "at_least_one_compelling": True,
                "set_conclusion": "The proof direction is compelling and the spatial study is a credible contrast.",
                "concepts": [
                    {"concept_id": "direction-1", "outcome": "passed", "strength": "compelling", "signature_stage_ids": ["opening-proof", "project-proof", "blocked-edge"], "identity_specificity": "pass", "emotional_resonance": "pass", "craft_coherence": "pass", "rationale": "The proof seam controls three consequential roles.", "weakest_moment": "The orientation could feel familiar.", "refinement_priority": "Make the evidence issue more ownable.", "evidence": [concept_visuals["direction-wide"], concept_visuals["direction-narrow"]]},
                    {"concept_id": "study-spatial-inspection", "outcome": "passed", "strength": "credible", "signature_stage_ids": ["opening-field", "inspection-proof", "quiet-route"], "identity_specificity": "pass", "emotional_resonance": "pass", "craft_coherence": "pass", "rationale": "The topology controls opening, proof, and quiet state.", "weakest_moment": "The field could feel diagrammatic.", "refinement_priority": "Add human consequence.", "evidence": [concept_visuals["study-wide"], concept_visuals["study-narrow"]]},
                ],
            }, "browser_snapshots": browser_snapshots,
            "browser_probes": browser_probes,
            "research_links": [],
            "visual_references": [],
        }), encoding="utf-8")
        duplicate_manifest = self.root / "concept-duplicate-visual.json"
        duplicate_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        duplicate_value["concepts"][1]["narrow_transformation"] = duplicate_value["concepts"][0]["narrow_transformation"]
        duplicate_manifest.write_text(json.dumps(duplicate_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "must be distinct"):
            design.concept_validate(self.root, self.config, duplicate_manifest)
        reused_probe_manifest = self.root / "concept-reused-probe.json"
        reused_probe_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        reused_probe_value["concepts"][1]["runtime_probes"] = reused_probe_value["concepts"][0]["runtime_probes"]
        reused_probe_manifest.write_text(json.dumps(reused_probe_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "own runtime probe"):
            design.concept_validate(self.root, self.config, reused_probe_manifest)
        collapsed_art_manifest = self.root / "concept-collapsed-art.json"
        collapsed_art_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        collapsed_art_value["concepts"][1]["media_system"]["art_direction_family"] = "documentary"
        collapsed_art_value["creative_range"]["range_audit"]["art_direction_family_count"] = 1
        collapsed_art_manifest.write_text(json.dumps(collapsed_art_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "distinct art-direction"):
            design.concept_validate(self.root, self.config, collapsed_art_manifest)
        weak_impact_manifest = self.root / "concept-weak-impact.json"
        weak_impact_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        weak_impact_value["impact_review"]["at_least_one_compelling"] = False
        weak_impact_value["impact_review"]["concepts"][0]["strength"] = "credible"
        weak_impact_manifest.write_text(json.dumps(weak_impact_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "at least one compelling"):
            design.concept_validate(self.root, self.config, weak_impact_manifest)
        shallow_signature_manifest = self.root / "concept-shallow-signature.json"
        shallow_signature_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        shallow_signature_value["impact_review"]["concepts"][0]["signature_stage_ids"] = ["opening-proof", "project-proof"]
        shallow_signature_manifest.write_text(json.dumps(shallow_signature_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "at least three different journey roles"):
            design.concept_validate(self.root, self.config, shallow_signature_manifest)
        collapsed_grammar_manifest = self.root / "concept-collapsed-grammar.json"
        collapsed_grammar_value = json.loads(concept_manifest.read_text(encoding="utf-8"))
        collapsed_grammar_value["concepts"][1]["page_grammar"]["grammar_id"] = collapsed_grammar_value["concepts"][0]["page_grammar"]["grammar_id"]
        collapsed_grammar_value["concepts"][1]["page_grammar"]["family"] = collapsed_grammar_value["concepts"][0]["page_grammar"]["family"]
        collapsed_grammar_value["creative_range"]["range_audit"]["page_grammar_count"] = 1
        collapsed_grammar_manifest.write_text(json.dumps(collapsed_grammar_value), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "distinct planned page grammar"):
            design.concept_validate(self.root, self.config, collapsed_grammar_manifest)
        validated = design.concept_validate(self.root, self.config, concept_manifest)
        self.assertEqual(validated["status"], "awaiting-feedback")
        self.assertEqual(validated["impact_review_status"], "passed")
        self.assertEqual(validated["compelling_concept_count"], 1)
        with self.assertRaisesRegex(design.DesignError, "not selectable"):
            design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        feedback = self.root / "feedback.json"
        feedback.write_text(json.dumps({"actor": "reviewer", "contract_changed": False, "ready_for_selection": True, "reactions": [{"element_id": "1.signature", "reaction": "keep", "why": "It makes evidence structural."}]}), encoding="utf-8")
        ready = design.feedback_record(self.root, self.config, draft["design_id"], feedback)
        self.assertEqual(ready["status"], "awaiting-selection")
        selected = design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        self.assertIn(" bundle ", selected["required_authorization_text"])
        prototype = self.root / "prototype.html"
        prototype.write_text(
            "<html><head>"
            f'<meta name="continuity-design-id" content="{selected["design_id"]}">'
            f'<meta name="continuity-design-revision" content="{selected["revision"]}">'
            f'<meta name="continuity-design-hash" content="{selected["design_hash"]}">'
            '<meta name="continuity-prototype-maturity" content="directional">'
            '<meta name="continuity-fixture-data" content="none">'
            "</head><body><main id=\"direction\"><h1>Operational evidence</h1></main></body></html>", encoding="utf-8",
        )
        prototype_screenshots = []
        prototype_paths = []
        for viewport, width, color in (
            ("mobile", 390, (236, 239, 235, 255)),
            ("tablet", 768, (229, 234, 230, 255)),
            ("desktop", 1440, (221, 228, 223, 255)),
        ):
            screenshot = self.root / f"prototype-{viewport}.png"
            screenshot.write_bytes(png_bytes(width, 900, color))
            prototype_paths.append(screenshot)
            prototype_screenshots.append({"path": screenshot.name, "media_type": "image/png", "role": viewport, "sha256": __import__("hashlib").sha256(screenshot.read_bytes()).hexdigest()})
        prototype_slop = design.slop_check(self.root, self.config, prototype, self.write_slop_manifest(
            stage="prototype", design_id=selected["design_id"], revision=selected["revision"],
            design_hash=selected["design_hash"], approval_bundle_hash=selected["approval_bundle_hash"],
            visual_review=self.visual_review_for(prototype_paths),
        ))
        prototype_manifest = self.root / "prototype-manifest.json"
        prototype_manifest.write_text(json.dumps({
            "schema_version": 3, "artifact_id": "concept-loop-prototype", "design_id": selected["design_id"],
            "revision": selected["revision"], "design_hash": selected["design_hash"], "approval_bundle_hash": selected["approval_bundle_hash"],
            "maturity": "directional", "fixture_data": "none",
            "implementation_context_hash": design._canonical_hash(None), "component_map_hash": design._canonical_hash([]), "asset_strategy_hash": design._canonical_hash([]),
            "files": [{"path": "prototype.html", "media_type": "text/html", "role": "prototype", "sha256": __import__("hashlib").sha256(prototype.read_bytes()).hexdigest()}, *prototype_screenshots],
            "demonstrated_audiences": [], "demonstrated_surfaces": ["Direction"], "demonstrated_states": ["default"],
            "omitted_surfaces": [], "omitted_states": [], "design_claims": [], "validation_results": [],
            "slop_report": self.slop_reference(prototype_slop), "execution_authorized": False,
        }), encoding="utf-8")
        candidate = design.validate_candidate_artifact(self.root, self.config, prototype_manifest)
        self.assertEqual(candidate["ai_slop_check"]["status"], "passed")
        approved = design.approve(self.root, self.config, draft["design_id"], 1, "reviewer", selected["required_authorization_text"])
        self.assertEqual(approved["schema_version"], 2)
        self.assertEqual(approved["approval_bundle_hash"], selected["approval_bundle_hash"])
        implementation_slop = design.slop_check(self.root, self.config, prototype, self.write_slop_manifest(
            stage="implementation", design_id=selected["design_id"], revision=selected["revision"],
            design_hash=selected["design_hash"], approval_bundle_hash=selected["approval_bundle_hash"],
            visual_review=self.visual_review_for(prototype_paths),
        ))
        artifact_value = json.loads(prototype_manifest.read_text(encoding="utf-8"))
        artifact_value["slop_report"] = self.slop_reference(implementation_slop)
        prototype_manifest.write_text(json.dumps(artifact_value), encoding="utf-8")
        approved_artifact = design.validate_artifact(self.root, self.config, prototype_manifest)
        self.assertEqual(approved_artifact["ai_slop_check"]["status"], "passed")
        changed = self.root / "changed.json"
        changed.write_text(json.dumps({
            "actor": "reviewer", "contract_changed": True, "ready_for_selection": False,
            "reactions": [{"element_id": "1.signature", "reaction": "change", "why": "Make the evidence rail quieter."}],
            "visual_delta": {"changed": ["Reduced evidence-rail contrast"], "stayed": ["Evidence remains attached to the decision"], "why": ["Preserve rigor without overpowering content"], "path": "prototype.html", "sha256": __import__("hashlib").sha256(prototype.read_bytes()).hexdigest()},
        }), encoding="utf-8")
        revised = design.feedback_record(self.root, self.config, draft["design_id"], changed)
        self.assertEqual(revised["revision"], 2)
        self.assertEqual(revised["status"], "refining")
        self.assertFalse(revised["slop_evidence_valid"])
        refreshed = design.draft(self.root, self.config, CATALOG, self.write_input(self.creative_input(
            design_id="concept-loop", collaboration_profile="guided", concept_presentation_mode="director-led",
            research={"mode": "offline", "status": "complete", "announced": True, "opt_out_offered": True, "moodboard": []},
        )))
        self.assertEqual(refreshed["revision"], 2)
        self.assertEqual(len(refreshed["feedback_rounds"]), 2)
        self.assertEqual(refreshed["decision_register"][0]["disposition"], "unresolved-change")
        self.assertTrue(refreshed["rejected_decisions"] == [] or isinstance(refreshed["rejected_decisions"], list))

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
            "#### Capability Digest", "#### Surface Grammar", "#### Responsive Delta Matrix", "#### Change Impact Checks",
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
        self.assertTrue(contract["distinctive_expression"][0]["implementation_system"]["surface_grammar"])
        self.assertTrue(contract["distinctive_expression"][0]["implementation_system"]["responsive_delta_matrix"])
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
        with self.assertRaisesRegex(design.DesignError, "At least 2 directions"):
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
            png.write_bytes(png_bytes(width, height))
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
                "state_owner": "DecisionReviewProvider owns asynchronous review state and recovery.",
                "composition_boundary": "DecisionReview composes Evidence, Status, and Actions through shared context.",
                "state_interface": "Expose state, actions, and metadata without binding presentation to the data client.",
                "variants": ["DecisionReview.Default", "DecisionReview.Loading", "DecisionReview.Error", "DecisionReview.Complete"],
                "invalid_combinations": ["Complete and loading cannot be active together."],
                "extension_points": ["Evidence panel", "Policy explanation"],
                "responsive_behavior": "Two-column review becomes a linear evidence-first sequence.",
                "accessibility_contract": "Focus, status, and consequence remain programmatically available.",
                "custom_expression": "A project-specific evidence margin carries the identity.",
            }],
            content_provenance=[{
                "content_id": "fixture-decision", "classification": "illustrative",
                "statement": "The representative decision content is invented for design validation.",
                "source_refs": [], "required_qualification": "Illustrative fixture",
                "allowed_uses": ["Private prototype validation"],
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
            '</head><body><main id="primary-surface">Illustrative fixture — Decision review</main></body></html>', encoding="utf-8",
        )
        files = [{"path": ".continuity/private/designs/complete-react/1/index.html", "media_type": "text/html", "role": "prototype", "sha256": design.hashlib.sha256(html.read_bytes()).hexdigest()}]
        for name, width in (("desktop", 1440), ("tablet", 768), ("mobile", 390)):
            png = artifact_dir / f"{name}.png"
            png.write_bytes(png_bytes(width, 900))
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
            "content_claims": [{"claim": "Representative decision content", "presentation": "illustrative", "provenance_ids": ["fixture-decision"], "evidence_refs": [".continuity/private/designs/complete-react/1/index.html#primary-surface"], "visible_qualification": "Illustrative fixture"}],
            "asset_resolutions": [{"asset_id": "evidence-material", "status": "deliberately-omitted", "evidence_refs": []}],
            "validation_results": [
                {"scenario": scenario, "status": "passed", "evidence": "Required artifact quality evidence passed."}
                for scenario in sorted(design.WEB_ARTIFACT_QUALITY_SCENARIOS)
            ], "execution_authorized": False,
        }
        manifest_path = self.write_input(manifest)
        result = design.validate_candidate_artifact(self.root, self.config, manifest_path)
        self.assertTrue(result["candidate"])
        self.assertTrue(result["implementation_ready"])
        baseline = json.loads(json.dumps(manifest))
        manifest["validation_results"] = [
            item for item in manifest["validation_results"] if item["scenario"] != "color-contrast"
        ]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "lack quality results"):
            design.validate_candidate_artifact(self.root, self.config, manifest_path)
        manifest = json.loads(json.dumps(baseline))
        for item in manifest["validation_results"]:
            if item["scenario"] == "intermediate-viewport":
                item.update({"status": "failed", "evidence": "Mobile action collides with the signature carrier."})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "artifact validation has failures"):
            design.validate_candidate_artifact(self.root, self.config, manifest_path)
        manifest = json.loads(json.dumps(baseline))
        manifest["content_claims"][0]["visible_qualification"] = "Qualification absent from the artifact"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "qualification is not visible"):
            design.validate_candidate_artifact(self.root, self.config, manifest_path)
        manifest = json.loads(json.dumps(baseline))
        manifest["asset_resolutions"][0]["status"] = "blocked"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(design.DesignError, "cannot retain blocked assets"):
            design.validate_candidate_artifact(self.root, self.config, manifest_path)
        manifest_path.write_text(json.dumps(baseline), encoding="utf-8")
        markdown = (self.root / ".continuity/private/design/complete-react/design.md").read_text()
        self.assertIn("## React and implementation system", markdown)
        self.assertIn("### Component capability map", markdown)
        self.assertIn("## Asset strategy", markdown)
        self.assertIn("## Prototype completion contract", markdown)
        self.assertIn("### React composition contracts", markdown)

    def test_complete_react_contract_requires_composition_ownership(self):
        value = input_value(
            design_id="missing-composition-contract",
            implementation_context={
                "framework": "Next.js", "react_version": "19", "evidence_refs": ["package.json"],
            },
            component_map=[{
                "component_id": "review", "experience_need": "Review", "surface": "Review",
                "strategy": "custom", "components": [], "required_states": ["default"],
                "responsive_behavior": "Reflows", "accessibility_contract": "Keyboard operable",
                "custom_expression": "Evidence rail",
            }],
            asset_strategy=[{
                "asset_id": "none", "purpose": "Record omission", "source": "deliberately-omitted",
                "art_direction": "No asset", "provenance_status": "Deliberately omitted", "source_refs": [],
                "required_crops": [], "responsive_treatment": "Not applicable",
                "accessibility_alternative": "No visual content", "fallback": "No asset",
                "claim_boundary": "No visual claim",
            }],
            completion_contract={"mode": "complete-prototype", "required_viewports": ["desktop", "tablet", "mobile"], "required_states": ["default"], "content_status": "representative", "artifact_critique_required": True},
        )
        with self.assertRaisesRegex(design.DesignError, "requires composition ownership"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

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

    def test_cinematic_media_context_routes_loops_motion_and_equivalence_review(self):
        value = input_value(
            design_id="cinematic-loops",
            title="A material-led commercial journey",
            intent="Use a looping macro video in the hero and section loops for page storytelling with a credible final action.",
            interaction_signals=["Full-screen looping hero, section video loops, subtle parallax, and an optional auto tour"],
        )
        value.pop("lenses")
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertIn("motion-art-direction", draft["lenses"])
        self.assertIn("multimodal-equivalence-sensory-agency", draft["lenses"])
        self.assertIn("attention-interruption", draft["lenses"])
        rule = next(item for item in draft["lens_routing"] if item["rule_id"] == "cinematic-media-storytelling")
        self.assertIn("looping hero", rule["matched_terms"])
        self.assertIn("section video", rule["matched_terms"])
        packs = {pack["pack_id"]: pack for pack in draft["catalog_packs"]}
        self.assertEqual(packs["lens-motion-art-direction"]["version"], "1.2.0")

    def test_cinematic_media_method_is_progressively_disclosed(self):
        skill = (CATALOG.parent.parent / "SKILL.md").read_text(encoding="utf-8")
        method = (CATALOG.parent / "cinematic-scroll-experiences.md").read_text(encoding="utf-8")
        self.assertIn("looping-hero, section-loop, scroll-driven", skill)
        self.assertIn("Define the cinematic outcome", method)
        self.assertIn("Choose the playback grammar", method)
        self.assertIn("Looping hero", method)
        self.assertIn("Chapter loops", method)
        self.assertIn("Run a private narrative-spine burst", method)
        self.assertIn("coalesces pending targets", method)
        self.assertIn("Rejected imports", method)

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
            "modality_assessment": {
                "observed_signals": ["Interactive experience"], "selected_targets": ["ui"],
                "rationale": "The requested output is interactive.", "conflicts": [],
            },
            "direction_count": 1,
            "direction_count_basis": "The supplied direction resolves the organizing idea.",
            "direction_assessment": {"material_ambiguities": ["How bold?", "How dense?"], "resolved_by_evidence": ["How bold?", "How dense?"]},
            "open_questions": ["How bold?", "How dense?"],
            "directions": [seed["directions"][0]],
        }
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(len(draft["directions"]), 1)
        self.assertEqual(draft["directions"][0], seed["directions"][0])

    def test_source_uncertainties_remain_visible_until_resolved(self):
        value = input_value(
            design_id="uncertainty-register",
            open_questions=["Are verified silhouettes available?"],
            source_uncertainties=[{
                "question": "Are verified silhouettes available?", "disposition": "open",
                "response": "", "source_refs": ["docs/recalls.md"],
            }],
        )
        draft = design.draft(self.root, self.config, CATALOG, self.write_input(value))
        self.assertEqual(draft["source_uncertainties"][0]["disposition"], "open")
        design.select(self.root, self.config, draft["design_id"], ["direction-1"], "reviewer")
        markdown = (self.root / ".continuity/private/design/uncertainty-register/design.md").read_text()
        self.assertIn("## Source uncertainty register", markdown)
        self.assertIn("Are verified silhouettes available?", markdown)
        value["open_questions"] = []
        with self.assertRaisesRegex(design.DesignError, "must remain in open_questions"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_authored_directions_require_modality_and_matching_assessed_count(self):
        seed = design.draft(self.root, self.config, CATALOG, self.write_input(input_value(design_id="assessment-seed")))
        direction = seed["directions"][0]
        value = input_value(
            design_id="missing-modality", directions=[direction], direction_count=1,
            modality_assessment=None,
        )
        with self.assertRaisesRegex(design.DesignError, "require modality_assessment"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))
        value["modality_assessment"] = input_value()["modality_assessment"]
        value["direction_count"] = 2
        with self.assertRaisesRegex(design.DesignError, "Supplied direction count must match"):
            design.draft(self.root, self.config, CATALOG, self.write_input(value))

    def test_modality_conflicts_and_high_consequence_fixture_claims_fail_closed(self):
        conflict = input_value(
            design_id="modality-conflict",
            modality_assessment={
                "observed_signals": ["A printed notice rendered in HTML"], "selected_targets": ["ui"],
                "rationale": "HTML was selected as the carrier.",
                "conflicts": [{"conflict": "The requested output is a document, not an interface", "status": "unresolved", "resolution": ""}],
            },
        )
        with self.assertRaisesRegex(design.DesignError, "Modality conflict must be resolved"):
            design.draft(self.root, self.config, CATALOG, self.write_input(conflict))
        fixture = input_value(
            design_id="high-consequence-fixture", consequence_level="high",
            prototype_scope={"maturity": "behavioral", "artifact_type": "HTML notice", "fixture_data": "present", "demonstrated_surfaces": ["Recall notice"], "demonstrated_states": ["default"], "omitted_surfaces": [], "omitted_states": []},
        )
        with self.assertRaisesRegex(design.DesignError, "require content_provenance"):
            design.draft(self.root, self.config, CATALOG, self.write_input(fixture))

    def test_cross_industry_cross_modality_evaluation_is_healthy(self):
        report = EVALUATION.evaluate(CATALOG, SCENARIOS)
        self.assertTrue(report["healthy"], report)
        self.assertEqual(report["quality_scope"], "contract-routing-and-regression-only")
        self.assertEqual(report["output_quality_evidence"], "not-measured-run-evaluate-design-outputs")
        self.assertEqual(report["metrics"]["scenario_count"], 21)
        self.assertEqual(report["metrics"]["passed_scenario_count"], 21)
        self.assertEqual(report["metrics"]["routing_precision"], 1.0)
        self.assertEqual(report["metrics"]["routing_recall"], 1.0)
        self.assertEqual(report["metrics"]["safeguard_coverage"], 1.0)
        self.assertEqual(report["metrics"]["conflict_resolution_coverage"], 1.0)
        self.assertLessEqual(report["metrics"]["maximum_direction_similarity"], 0.78)
        self.assertGreaterEqual(report["metrics"]["minimum_implementation_usefulness"], 0.9)
        self.assertEqual({item["modality"] for item in report["scenarios"]}, {"ui", "document", "image"})
        self.assertGreaterEqual(len({item["industry_group"] for item in report["scenarios"]}), 10)

    def test_blinded_output_benchmark_requires_real_artifacts_and_paired_lift(self):
        dimensions = ["project-specificity", "signature-recognition", "structural-diversity", "reference-transformation", "responsive-fidelity", "genericity-resistance"]
        benchmark = {
            "schema_version": 1,
            "dimensions": dimensions,
            "thresholds": {"minimum_cases": 3, "minimum_reviewers_per_case": 2, "minimum_mean_lift": 0.5, "minimum_candidate_win_rate": 1.0, "maximum_dimension_regression": 0},
            "cases": [],
        }
        for index, case_id in enumerate(("vague-operator-brief", "named-reference", "creative-peer"), 1):
            baseline = self.root / f"baseline-{index}.png"
            candidate = self.root / f"candidate-{index}.png"
            baseline.write_bytes(png_bytes(1200, 800, (230 - index, 230, 230, 255)))
            candidate.write_bytes(png_bytes(1200, 800, (210, 222 - index, 216, 255)))
            benchmark["cases"].append({
                "case_id": case_id, "brief_hash": f"{index:x}" * 64,
                "baseline": {"path": baseline.name, "sha256": __import__("hashlib").sha256(baseline.read_bytes()).hexdigest()},
                "candidate": {"path": candidate.name, "sha256": __import__("hashlib").sha256(candidate.read_bytes()).hexdigest()},
                "ratings": [
                    {"reviewer_id": "reviewer-a", "blind": True, "baseline_scores": {dimension: 2 for dimension in dimensions}, "candidate_scores": {dimension: 4 for dimension in dimensions}},
                    {"reviewer_id": "reviewer-b", "blind": True, "baseline_scores": {dimension: 3 for dimension in dimensions}, "candidate_scores": {dimension: 4 for dimension in dimensions}},
                ],
            })
        manifest = self.root / "output-benchmark.json"
        manifest.write_text(json.dumps(benchmark), encoding="utf-8")
        report = OUTPUT_EVALUATION.evaluate(self.root, manifest)
        self.assertTrue(report["healthy"])
        self.assertEqual(report["case_count"], 3)
        self.assertGreater(report["mean_lift"], 0.5)

        benchmark["thresholds"]["minimum_cases"] = 1
        manifest.write_text(json.dumps(benchmark), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "at least three cases"):
            OUTPUT_EVALUATION.evaluate(self.root, manifest)

    def test_homepage_benchmark_preserves_human_gates_and_hash_binding(self):
        definition_path = SUITE / "skills" / "continuity-design" / "references" / "continuity-homepage-benchmark.json"
        definition = json.loads(definition_path.read_text(encoding="utf-8"))
        brief_path = definition_path.parent / definition["brief_path"]
        skill_path = SUITE / "skills" / "continuity-design" / "SKILL.md"

        def artifact(relative, content):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                path.write_bytes(content)
            else:
                path.write_text(content, encoding="utf-8")
            return {"path": relative, "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}

        doctor = artifact("evidence/doctor.json", json.dumps({"healthy": True}))
        concepts = []
        laboratory_hash = "9" * 64
        concept_range = {
            "morning-brief": ("type-reflective-serif", "serif", "photographic", "cinematic-chapters", "editorial-issue", "motion-witness", "compelling"),
            "proof-relay": ("type-humanist-proof", "humanist-sans", "diagrammatic", "editorial-sequence", "navigable-artifact", "interaction-proof", "credible"),
            "local-aperture": ("type-mono-coordinate", "monospaced", "spatial", "spatial-field", "single-canvas-instrument", "spatial-inspection", "credible"),
        }
        for direction_id in ("morning-brief", "proof-relay", "local-aperture"):
            board = artifact(f"concepts/{direction_id}.html", f"<h1>{direction_id}</h1>")
            slop = artifact(
                f"concepts/{direction_id}-slop.json",
                json.dumps({"stage": "concept", "status": "passed"}),
            )
            strategy, family, art_family, composition, grammar, interaction, strength = concept_range[direction_id]
            concepts.append({"direction_id": direction_id, "board": board, "slop_report": slop, "creative_range_status": "passed", "range_audit_status": "passed", "generative_laboratory_hash": laboratory_hash, "typography_strategy_id": strategy, "typography_family": family, "art_direction_family": art_family, "composition_family": composition, "page_grammar_family": grammar, "interaction_motion_strategy_id": interaction, "journey_stage_count": 5, "signature_stage_count": 3, "runtime_probe_count": 3, "impact_review_status": "passed", "impact_strength": strength, "comparison_depth_status": "passed", "generated_media_extraction_status": "passed"})

        checkpoints = []
        for checkpoint_id in ("brief-interpretation", "reference-synthesis", "generative-concept-laboratory", "concept-directions"):
            content = {"checkpoint_id": checkpoint_id}
            if checkpoint_id == "generative-concept-laboratory":
                content.update({"status": "complete", "lens_count": 4, "seed_count": 8, "media_count": 3, "generated_seed_count": 2, "art_direction_family_count": 4, "typography_strategy_count": 3, "typography_family_count": 3, "composition_family_count": 3, "page_depth_role_count": 5, "page_grammar_count": 4, "interaction_motion_count": 3, "style_frame_family_count": 2, "style_frame_count": 4, "non_system_typography_count": 1, "shortlisted_seed_count": 4, "laboratory_hash": laboratory_hash})
            value = artifact(f"checkpoints/{checkpoint_id}.json", json.dumps(content))
            checkpoints.append({"checkpoint_id": checkpoint_id, "created_at": "2026-08-08T12:00:00Z", **value})

        manifest = {
            "schema_version": 1,
            "benchmark_id": definition["benchmark_id"],
            "workflow": "$continuity-design",
            "run_id": "test-homepage",
            "status": "directions",
            "definition_sha256": __import__("hashlib").sha256(definition_path.read_bytes()).hexdigest(),
            "brief_sha256": __import__("hashlib").sha256(brief_path.read_bytes()).hexdigest(),
            "source": {
                "branch": "feature/test",
                "commit": "a" * 40,
                "skill_path": "skills/continuity-design/SKILL.md",
                "skill_sha256": __import__("hashlib").sha256(skill_path.read_bytes()).hexdigest(),
            },
            "seed": {
                "audience": "founder-operator",
                "posture": "calm-authority",
                "hero": "morning-decision-surface",
                "references": ["Linear", "Palantir Foundry"],
                "edge_case": "healthy-but-unauthorized",
            },
            "doctor": doctor,
            "checkpoints": checkpoints,
            "concepts": concepts,
            "selection": None,
            "prototype_validation": None,
            "approval": None,
            "evidence": [],
            "reviews": [],
            "hard_failure_reviews": [],
            "execution_authorized": False,
        }
        manifest_path = self.root / "run.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = HOMEPAGE_EVALUATION.evaluate(SUITE, self.root, definition_path, manifest_path)
        self.assertTrue(report["stage_valid"])
        self.assertFalse(report["benchmark_passed"])
        self.assertFalse(report["merge_eligible"])
        self.assertEqual(report["next_gate"], "human-direction-selection")

        with self.assertRaisesRegex(ValueError, "cannot preselect"):
            manifest["selection"] = {
                "actor_type": "human", "selected_by": "reviewer", "selected_at": "2026-08-08T12:10:00Z", "direction_ids": ["morning-brief"]
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            HOMEPAGE_EVALUATION.evaluate(SUITE, self.root, definition_path, manifest_path)

        manifest["selection"] = None
        manifest["definition_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "definition changed"):
            HOMEPAGE_EVALUATION.evaluate(SUITE, self.root, definition_path, manifest_path)

    def test_homepage_benchmark_passes_only_after_approval_and_human_score(self):
        definition_path = SUITE / "skills" / "continuity-design" / "references" / "continuity-homepage-benchmark.json"
        definition = json.loads(definition_path.read_text(encoding="utf-8"))
        brief_path = definition_path.parent / definition["brief_path"]
        skill_path = SUITE / "skills" / "continuity-design" / "SKILL.md"

        def artifact(relative, content):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
            return {"path": relative, "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}

        checkpoints = []
        laboratory_hash = "9" * 64
        for checkpoint_id in definition["required_checkpoints"]:
            content = {"checkpoint_id": checkpoint_id}
            if checkpoint_id == "generative-concept-laboratory":
                content.update({"status": "complete", "lens_count": 4, "seed_count": 8, "media_count": 3, "generated_seed_count": 2, "art_direction_family_count": 4, "typography_strategy_count": 3, "typography_family_count": 3, "composition_family_count": 3, "page_depth_role_count": 5, "page_grammar_count": 4, "interaction_motion_count": 3, "style_frame_family_count": 2, "style_frame_count": 4, "non_system_typography_count": 1, "shortlisted_seed_count": 4, "laboratory_hash": laboratory_hash})
            value = artifact(f"checkpoints/{checkpoint_id}.json", json.dumps(content))
            checkpoints.append({"checkpoint_id": checkpoint_id, "created_at": "2026-08-08T12:00:00Z", **value})
        board = artifact("concepts/morning-brief.html", "<h1>Morning brief</h1>")
        slop = artifact("concepts/morning-brief-slop.json", json.dumps({"stage": "concept", "status": "passed"}))
        prototype = artifact("evidence/prototype-validation.json", json.dumps({"validated": True, "ai_slop_check": {"status": "passed"}}))
        evidence = []
        media_types = {
            "desktop": "image/png", "tablet": "image/png", "mobile": "image/png",
            "interaction": "application/json", "reduced-motion": "application/json", "accessibility": "text/markdown",
        }
        for role, media_type in media_types.items():
            value = artifact(f"evidence/{role}.bin", role.encode("utf-8"))
            evidence.append({"role": role, "media_type": media_type, **value})
        approval_value = {
            "status": "approved", "execution_authorized": False, "design_id": "homepage", "revision": 1,
            "design_hash": "1" * 64, "visual_reference_hash": "2" * 64, "approval_bundle_hash": "3" * 64,
        }
        approval_record = artifact("evidence/approval.json", json.dumps(approval_value))
        scores = {item["dimension"]: item["weight"] for item in definition["rubric"]}
        manifest = {
            "schema_version": 1, "benchmark_id": definition["benchmark_id"], "workflow": "$continuity-design",
            "run_id": "test-homepage-complete", "status": "scored",
            "definition_sha256": __import__("hashlib").sha256(definition_path.read_bytes()).hexdigest(),
            "brief_sha256": __import__("hashlib").sha256(brief_path.read_bytes()).hexdigest(),
            "source": {"branch": "feature/test", "commit": "b" * 40, "skill_path": "skills/continuity-design/SKILL.md", "skill_sha256": __import__("hashlib").sha256(skill_path.read_bytes()).hexdigest()},
            "seed": {"audience": "founder-operator", "posture": "calm-authority", "hero": "morning-decision-surface", "references": ["Linear", "Palantir Foundry"], "edge_case": "healthy-but-unauthorized"},
            "doctor": artifact("evidence/doctor.json", json.dumps({"healthy": True})),
            "checkpoints": checkpoints,
            "concepts": [{"direction_id": "morning-brief", "board": board, "slop_report": slop, "creative_range_status": "passed", "range_audit_status": "passed", "generative_laboratory_hash": laboratory_hash, "typography_strategy_id": "type-reflective-serif", "typography_family": "serif", "art_direction_family": "photographic", "composition_family": "cinematic-chapters", "page_grammar_family": "editorial-issue", "interaction_motion_strategy_id": "motion-witness", "journey_stage_count": 5, "signature_stage_count": 3, "runtime_probe_count": 3, "impact_review_status": "passed", "impact_strength": "compelling", "comparison_depth_status": "passed", "generated_media_extraction_status": "passed"}],
            "selection": {"actor_type": "human", "selected_by": "reviewer", "selected_at": "2026-08-08T12:10:00Z", "direction_ids": ["morning-brief"]},
            "prototype_validation": prototype,
            "approval": {"actor_type": "human", **{key: approval_value[key] for key in ("design_id", "revision", "design_hash", "visual_reference_hash", "approval_bundle_hash")}, "record": approval_record},
            "evidence": evidence,
            "reviews": [{"actor_type": "human", "reviewer_id": "reviewer-a", "scores": scores, "rationale": "All supplied evidence was inspected against the fixed rubric."}],
            "hard_failure_reviews": [{"rule_id": item["rule_id"], "result": "pass", "rationale": "Verified in the bound evidence."} for item in definition["hard_failures"]],
            "execution_authorized": False,
        }
        manifest_path = self.root / "run-complete.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = HOMEPAGE_EVALUATION.evaluate(SUITE, self.root, definition_path, manifest_path)
        self.assertEqual(report["score"], 100)
        self.assertTrue(report["benchmark_passed"])
        self.assertTrue(report["merge_eligible"])

        manifest["hard_failure_reviews"][0]["result"] = "fail"
        manifest["hard_failure_reviews"][0]["rationale"] = "Healthy was incorrectly shown as authorization."
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = HOMEPAGE_EVALUATION.evaluate(SUITE, self.root, definition_path, manifest_path)
        self.assertEqual(report["score"], definition["passing_score"] - 1)
        self.assertFalse(report["benchmark_passed"])
        self.assertFalse(report["merge_eligible"])

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

    def test_reviewed_cinematic_overlay_uses_media_led_contract(self):
        draft = design.draft(
            self.root,
            self.config,
            CATALOG,
            self.write_input(input_value(design_id="cinematic-media", themes=["cinematic"])),
        )
        pack = next(pack for pack in draft["catalog_packs"] if pack["pack_id"] == "theme-cinematic")
        self.assertEqual(pack["version"], "1.2.0")

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
        guided = next(pack for pack in draft["catalog_packs"] if pack["pack_id"] == "message-structure-guided-narrative")
        self.assertEqual(guided["version"], "1.2.0")

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
            self.assertEqual(installed["suite_version"], SUITE_VERSION)
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
                result = subprocess.run(
                    [sys.executable, str(cli), "--project-root", str(root), *args],
                    capture_output=True,
                    text=True,
                )
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
            self.assertTrue(doctor["design_catalog"]["healthy"], doctor["design_catalog"])
            self.assertEqual(doctor["design_catalog"]["approved_design"]["design_hash"], approved["design_hash"])


if __name__ == "__main__":
    unittest.main()
