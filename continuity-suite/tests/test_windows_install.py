from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SUITE = Path(__file__).resolve().parents[1]
INSTALLER = SUITE / "installer" / "install.py"


@unittest.skipUnless(os.name == "nt", "native Windows installer acceptance")
class WindowsInstallTest(unittest.TestCase):
    def test_onedrive_path_with_spaces_installs_and_cmd_launcher_runs_doctor(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity install unicode ", dir=SUITE.parent) as directory:
            root = self._install_project(Path(directory))
            interpreter = root / ".continuity" / "private" / "python-interpreter.txt"
            self.assertEqual(Path(interpreter.read_text(encoding="utf-8").strip()).resolve(), Path(sys.executable).resolve())
            launcher = root / ".agents" / "continuity" / "bin" / "continuity.cmd"
            doctor = subprocess.run(
                [str(launcher), "--project-root", str(root), "--json", "project", "doctor"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr or doctor.stdout)
            health = json.loads(doctor.stdout)
            self.assertTrue(health["healthy"], health)
            self.assertEqual(health["platform"]["name"], "win32")
            self.assertTrue(health["filesystem"]["one_drive"])
            self.assertTrue(health["dependencies"]["python"]["configured_path_exists"])
            invalid = subprocess.run(
                [str(launcher), "--project-root", str(root), "not-a-command"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(invalid.returncode, 0)
            powershell_launcher = root / ".agents" / "continuity" / "bin" / "continuity.ps1"
            powershell_doctor = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(powershell_launcher),
                    "--project-root",
                    str(root),
                    "--json",
                    "project",
                    "doctor",
                ],
                cwd=SUITE,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(powershell_doctor.returncode, 0, powershell_doctor.stderr or powershell_doctor.stdout)
            self.assertTrue(json.loads(powershell_doctor.stdout)["healthy"])
            powershell_invalid = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(powershell_launcher),
                    "--project-root",
                    str(root),
                    "not-a-command",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(powershell_invalid.returncode, invalid.returncode)

    def test_reinstall_rebinds_a_posix_project_to_windows_without_state_loss(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity migrated project ", dir=SUITE.parent) as directory:
            root = self._install_project(Path(directory))
            private_note = root / ".continuity" / "private" / "notes" / "from-posix.json"
            private_note.parent.mkdir(parents=True, exist_ok=True)
            private_note.write_text('{"origin":"posix","path":"docs/project-memory/INDEX.md"}\n', encoding="utf-8")
            interpreter = root / ".continuity" / "private" / "python-interpreter.txt"
            interpreter.write_text("/usr/bin/python3\n", encoding="utf-8")

            reinstalled = self._run_installer(root)
            self.assertEqual(reinstalled.returncode, 0, reinstalled.stderr or reinstalled.stdout)
            self.assertTrue(private_note.is_file())
            self.assertEqual(Path(interpreter.read_text(encoding="utf-8").strip()).resolve(), Path(sys.executable).resolve())
            install_manifest = json.loads((root / ".continuity" / "install-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(all("\\" not in path for path in install_manifest["installed_files"]))
            cli = root / ".agents" / "continuity" / "bin" / "continuity"
            doctor = subprocess.run(
                [sys.executable, str(cli), "--project-root", str(root), "--json", "project", "doctor"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr or doctor.stdout)
            self.assertTrue(json.loads(doctor.stdout)["healthy"])

    def test_codex_and_claude_share_canonical_handoff_without_private_context(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity agent handoff ", dir=SUITE.parent) as directory:
            root = self._install_project(Path(directory))
            cli = root / ".agents" / "continuity" / "bin" / "continuity"
            answers = root / "agent-surfaces.json"
            answers.write_text(
                json.dumps({"agent_surfaces": {"primary": "codex", "enabled": ["codex", "claude-code"]}}),
                encoding="utf-8",
            )
            configured = subprocess.run(
                [
                    sys.executable,
                    str(cli),
                    "--project-root",
                    str(root),
                    "--json",
                    "project",
                    "configure",
                    "--answers-file",
                    str(answers),
                    "--actor",
                    "windows-acceptance",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(configured.returncode, 0, configured.stderr or configured.stdout)

            canonical_names = {
                path.name
                for path in (root / ".agents" / "skills").glob("continuity*")
                if path.is_dir()
            }
            expected_names = {
                path.name for path in (SUITE / "skills").iterdir() if path.is_dir()
            } | {"continuity-local"}
            self.assertEqual(canonical_names, expected_names)
            self.assertEqual(
                {path.name for path in (root / ".claude" / "skills").iterdir() if path.is_dir()},
                expected_names,
            )
            self.assertEqual(
                {path.stem for path in (root / ".claude" / "commands").glob("continuity*.md")},
                expected_names,
            )
            self.assertRegex(
                (root / "CLAUDE.md").read_text(encoding="utf-8"),
                r"(?m)^@AGENTS\.md$",
            )

            for canonical in sorted((root / ".agents" / "skills").glob("continuity*")):
                if not canonical.is_dir():
                    continue
                adapter = root / ".claude" / "skills" / canonical.name
                canonical_files = {
                    path.relative_to(canonical).as_posix(): path.read_bytes()
                    for path in canonical.rglob("*")
                    if path.is_file()
                }
                adapter_files = {
                    path.relative_to(adapter).as_posix(): path.read_bytes()
                    for path in adapter.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(adapter_files, canonical_files, canonical.name)
                skill_text = (canonical / "SKILL.md").read_text(encoding="utf-8")
                frontmatter = re.match(r"^---\n(?P<body>.*?)\n---\n", skill_text, re.DOTALL)
                self.assertIsNotNone(frontmatter, canonical.name)
                fields = {
                    key.strip(): value.strip()
                    for line in frontmatter.group("body").splitlines()
                    if ":" in line
                    for key, value in [line.split(":", 1)]
                }
                self.assertEqual(fields.get("name"), canonical.name)
                self.assertTrue(fields.get("description"), canonical.name)
                command = root / ".claude" / "commands" / f"{canonical.name}.md"
                command_text = command.read_text(encoding="utf-8")
                self.assertIn(f"/{canonical.name}", command_text)
                self.assertIn(f".agents/skills/{canonical.name}/SKILL.md", command_text)
                self.assertIn(".agents/skills/continuity-local/SKILL.md", command_text)

            sentinel = "CONTINUITY_PRIVATE_SENTINEL_9f723f01"
            private = root / ".continuity" / "private" / "captures" / "sentinel.txt"
            private.parent.mkdir(parents=True, exist_ok=True)
            private.write_text(sentinel, encoding="utf-8")
            ignored = subprocess.run(
                ["git", "-C", str(root), "check-ignore", "--quiet", str(private)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(ignored.returncode, 0)
            automatic_context = [root / "AGENTS.md", root / "CLAUDE.md"]
            for context_root in (root / ".agents" / "skills", root / ".claude" / "skills", root / ".claude" / "commands"):
                automatic_context.extend(path for path in context_root.rglob("*") if path.is_file())
            for path in automatic_context:
                if path.is_file():
                    self.assertNotIn(sentinel, path.read_text(encoding="utf-8"), str(path))

            nested = root / "packages" / "feature with spaces" / "src"
            nested.mkdir(parents=True)
            child_environment = {
                key: value
                for key, value in os.environ.items()
                if key != "CONTINUITY_PROJECT_ROOT"
            }
            nested_cmd_status = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity.cmd"),
                    "--json",
                    "workflow",
                    "status",
                ],
                cwd=nested,
                env=child_environment,
                capture_output=True,
                text=True,
                check=False,
            )
            nested_ps_status = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(root / ".agents" / "continuity" / "bin" / "continuity.ps1"),
                    "--json",
                    "workflow",
                    "status",
                ],
                cwd=nested,
                env=child_environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(nested_cmd_status.returncode, 0, nested_cmd_status.stderr)
            self.assertEqual(nested_ps_status.returncode, 0, nested_ps_status.stderr)
            nested_cmd = json.loads(nested_cmd_status.stdout)
            nested_ps = json.loads(nested_ps_status.stdout)
            nested_cmd.pop("generated_at", None)
            nested_ps.pop("generated_at", None)
            self.assertEqual(nested_cmd, nested_ps)

            other_workspace_root = root.parent / "Other Workspace Root"
            other_workspace_root.mkdir()
            explicit_root_status = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity.cmd"),
                    "--project-root",
                    str(root),
                    "--json",
                    "workflow",
                    "status",
                ],
                cwd=other_workspace_root,
                env=child_environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(explicit_root_status.returncode, 0, explicit_root_status.stderr)
            self.assertEqual(json.loads(explicit_root_status.stdout)["project_id"], "windows-fixture")

            cmd_capture = subprocess.Popen(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity.cmd"),
                    "--project-root",
                    str(root),
                    "--json",
                    "note",
                    "capture",
                    "--text",
                    "Codex-side simultaneous mutation fixture",
                ],
                cwd=other_workspace_root,
                env=child_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            ps_capture = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(root / ".agents" / "continuity" / "bin" / "continuity.ps1"),
                    "--project-root",
                    str(root),
                    "--json",
                    "note",
                    "capture",
                    "--text",
                    "Claude-side simultaneous mutation fixture",
                ],
                cwd=other_workspace_root,
                env=child_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            cmd_capture_out, cmd_capture_err = cmd_capture.communicate(timeout=30)
            ps_capture_out, ps_capture_err = ps_capture.communicate(timeout=30)
            self.assertEqual(cmd_capture.returncode, 0, cmd_capture_err or cmd_capture_out)
            self.assertEqual(ps_capture.returncode, 0, ps_capture_err or ps_capture_out)
            captures = [json.loads(cmd_capture_out), json.loads(ps_capture_out)]
            self.assertEqual(len({capture["capture_id"] for capture in captures}), 2)

            cmd_status = subprocess.run(
                [
                    str(root / ".agents" / "continuity" / "bin" / "continuity.cmd"),
                    "--project-root",
                    str(root),
                    "--json",
                    "workflow",
                    "status",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            ps_status = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(root / ".agents" / "continuity" / "bin" / "continuity.ps1"),
                    "--project-root",
                    str(root),
                    "--json",
                    "workflow",
                    "status",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(cmd_status.returncode, 0, cmd_status.stderr or cmd_status.stdout)
            self.assertEqual(ps_status.returncode, 0, ps_status.stderr or ps_status.stdout)
            cmd_handoff = json.loads(cmd_status.stdout)
            ps_handoff = json.loads(ps_status.stdout)
            cmd_handoff.pop("generated_at", None)
            ps_handoff.pop("generated_at", None)
            self.assertEqual(cmd_handoff, ps_handoff)
            self.assertFalse(cmd_handoff["handoff"]["authorization"]["execution_authorized"])

    def test_uninstall_is_dry_run_by_default_and_preserves_user_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity uninstall ", dir=SUITE.parent) as directory:
            root = self._install_project(Path(directory))
            private_note = root / ".continuity" / "private" / "notes" / "preserve.json"
            private_note.parent.mkdir(parents=True, exist_ok=True)
            private_note.write_text('{"preserve":true}\n', encoding="utf-8")
            custom_skill = root / ".agents" / "skills" / "custom-user-skill" / "SKILL.md"
            custom_skill.parent.mkdir(parents=True)
            custom_skill.write_text("user owned\n", encoding="utf-8")
            cli = root / ".agents" / "continuity" / "bin" / "continuity"

            preview = subprocess.run(
                [sys.executable, str(cli), "--project-root", str(root), "--json", "suite", "uninstall"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(preview.returncode, 0, preview.stderr or preview.stdout)
            self.assertFalse(json.loads(preview.stdout)["apply"])
            self.assertTrue(cli.exists())

            applied = subprocess.run(
                [sys.executable, str(cli), "--project-root", str(root), "--json", "suite", "uninstall", "--apply"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr or applied.stdout)
            self.assertTrue(json.loads(applied.stdout)["uninstalled"])
            self.assertFalse((root / ".agents" / "continuity").exists())
            self.assertFalse((root / ".continuity" / "install-manifest.json").exists())
            self.assertTrue(private_note.is_file())
            self.assertTrue(custom_skill.is_file())
            manifest = json.loads((root / ".continuity" / "project.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["continuity_enabled"])
            self.assertFalse(manifest["execution_enabled"])
            self.assertNotIn("<!-- continuity:start -->", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def _install_project(self, directory: Path) -> Path:
        root = directory / "Project With Spaces"
        root.mkdir()
        self._git(root, "init", "-b", "main")
        self._git(root, "config", "user.email", "windows-tests@example.invalid")
        self._git(root, "config", "user.name", "Windows Tests")
        (root / "README.md").write_text("# Windows fixture\n", encoding="utf-8")
        self._git(root, "add", ".")
        self._git(root, "commit", "-m", "initial")
        installed = self._run_installer(root)
        self.assertEqual(installed.returncode, 0, installed.stderr or installed.stdout)
        self.assertTrue(json.loads(installed.stdout)["installed"])
        return root

    def _run_installer(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                "--project-root",
                str(root),
                "--project-id",
                "windows-fixture",
                "--integration-branch",
                "main",
                "--ignore-user-defaults",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _git(self, root: Path, *arguments: str) -> None:
        result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
