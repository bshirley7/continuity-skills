from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
SUITE = REPOSITORY / "continuity-suite"
BUILDER = SUITE / "scripts" / "build_release_manifest.py"


class ReleasePortabilityTest(unittest.TestCase):
    def test_gitattributes_enforces_lf_for_managed_text(self) -> None:
        attributes = (REPOSITORY / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes)
        for path in ("continuity-suite/bin/continuity", "continuity-suite/bin/continuity.cmd", "continuity-suite/README.md"):
            result = subprocess.run(
                ["git", "-C", str(REPOSITORY), "check-attr", "eol", "--", path],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(result.stdout.rstrip().endswith(": lf"), result.stdout)

    def test_release_manifest_is_deterministic_and_platform_neutral(self) -> None:
        manifest_path = SUITE / "release-manifest.json"
        first = self._build(manifest_path)
        second = self._build(manifest_path)
        self.assertEqual(first, second)
        manifest = json.loads(second)
        self.assertIn("win32", manifest["supported_platforms"])
        self.assertTrue(manifest["files"])
        self.assertTrue(all("\\" not in path for path in manifest["files"]))

    def test_release_hashes_are_stable_across_autocrlf_modes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity-autocrlf-") as directory:
            fixture = Path(directory) / "fixture"
            fixture.mkdir()
            shutil.copy2(REPOSITORY / ".gitattributes", fixture / ".gitattributes")
            shutil.copytree(
                SUITE,
                fixture / "continuity-suite",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            self._git(fixture, "init")
            self._git(fixture, "config", "user.email", "tests@example.invalid")
            self._git(fixture, "config", "user.name", "Continuity Tests")
            self._git(fixture, "add", ".gitattributes", "continuity-suite")
            manifests = []
            for mode in ("true", "false", "input"):
                exported = Path(directory) / f"autocrlf-{mode}"
                exported.mkdir()
                self._git(
                    fixture,
                    "-c",
                    f"core.autocrlf={mode}",
                    "checkout-index",
                    "--all",
                    "--force",
                    f"--prefix={exported.as_posix()}/",
                )
                builder = exported / "continuity-suite" / "scripts" / "build_release_manifest.py"
                result = subprocess.run(
                    [sys.executable, str(builder)],
                    cwd=exported,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                manifests.append((exported / "continuity-suite" / "release-manifest.json").read_bytes())
            self.assertEqual(manifests[0], manifests[1])
            self.assertEqual(manifests[1], manifests[2])

    def _build(self, manifest_path: Path) -> bytes:
        result = subprocess.run([sys.executable, str(BUILDER)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return manifest_path.read_bytes()

    def _git(self, root: Path, *arguments: str) -> None:
        result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
