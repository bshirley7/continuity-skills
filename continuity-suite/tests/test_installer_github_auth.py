from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "lib"))
SPEC = importlib.util.spec_from_file_location("continuity_installer", SUITE / "installer" / "install.py")
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import machinery guard
    raise RuntimeError("Unable to load Continuity installer")
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


def auth_status(*, login: str = "octocat", scopes: list[str] | None = None, healthy: bool = True) -> subprocess.CompletedProcess[str]:
    payload = {
        "hosts": {
            "github.com": [
                {
                    "active": True,
                    "login": login,
                    "scopes": scopes or [],
                    "state": "success" if healthy else "failure",
                }
            ]
        }
    }
    return subprocess.CompletedProcess(["gh", "auth", "status"], 0 if healthy else 1, json.dumps(payload), "")


class InstallerGitHubAuthenticationTests(unittest.TestCase):
    def test_existing_project_scope_passes_without_prompt(self) -> None:
        with (
            mock.patch.object(INSTALLER.shutil, "which", return_value="/usr/local/bin/gh"),
            mock.patch.object(INSTALLER.subprocess, "run", return_value=auth_status(scopes=["repo", "project"])) as run,
            mock.patch.object(INSTALLER, "run_github_auth_interactive") as interactive,
        ):
            result = INSTALLER.ensure_github_cli_authentication()

        self.assertEqual(result["status"], "authenticated")
        self.assertEqual(result["login"], "octocat")
        self.assertFalse(result["prompted"])
        self.assertEqual(run.call_count, 1)
        interactive.assert_not_called()

    def test_missing_project_scope_launches_refresh_and_verifies(self) -> None:
        with (
            mock.patch.object(INSTALLER.shutil, "which", return_value="/usr/local/bin/gh"),
            mock.patch.object(
                INSTALLER.subprocess,
                "run",
                side_effect=[auth_status(scopes=["repo"]), auth_status(scopes=["repo", "project"])],
            ),
            mock.patch.object(INSTALLER, "interactive_terminal_available", return_value=True),
            mock.patch.object(
                INSTALLER,
                "run_github_auth_interactive",
                return_value=subprocess.CompletedProcess(["gh", "auth", "refresh"], 0, "", ""),
            ) as interactive,
        ):
            result = INSTALLER.ensure_github_cli_authentication()

        self.assertEqual(result["status"], "authenticated")
        self.assertTrue(result["prompted"])
        command = interactive.call_args.args[0]
        self.assertEqual(command[:4], ["/usr/local/bin/gh", "auth", "refresh", "--hostname"])
        self.assertIn("project", command)

    def test_missing_account_launches_browser_login(self) -> None:
        with (
            mock.patch.object(INSTALLER.shutil, "which", return_value="/usr/local/bin/gh"),
            mock.patch.object(
                INSTALLER.subprocess,
                "run",
                side_effect=[auth_status(healthy=False), auth_status(scopes=["project"])],
            ),
            mock.patch.object(INSTALLER, "interactive_terminal_available", return_value=True),
            mock.patch.object(
                INSTALLER,
                "run_github_auth_interactive",
                return_value=subprocess.CompletedProcess(["gh", "auth", "login"], 0, "", ""),
            ) as interactive,
        ):
            result = INSTALLER.ensure_github_cli_authentication()

        self.assertTrue(result["authenticated"])
        command = interactive.call_args.args[0]
        self.assertEqual(command[:4], ["/usr/local/bin/gh", "auth", "login", "--hostname"])
        self.assertIn("--web", command)
        self.assertIn("project", command)

    def test_unattended_install_returns_exact_command_without_hanging(self) -> None:
        with (
            mock.patch.object(INSTALLER.shutil, "which", return_value="/usr/local/bin/gh"),
            mock.patch.object(INSTALLER.subprocess, "run", return_value=auth_status(healthy=False)),
            mock.patch.object(INSTALLER, "interactive_terminal_available", return_value=False),
            mock.patch.object(INSTALLER, "run_github_auth_interactive") as interactive,
        ):
            result = INSTALLER.ensure_github_cli_authentication()

        self.assertEqual(result["status"], "authentication-required")
        self.assertEqual(
            result["next_command"],
            "gh auth login --hostname github.com --web --scopes project",
        )
        interactive.assert_not_called()

    def test_missing_cli_is_reported_without_installing_software(self) -> None:
        with mock.patch.object(INSTALLER.shutil, "which", return_value=None):
            result = INSTALLER.ensure_github_cli_authentication()

        self.assertEqual(result["status"], "cli-missing")
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["credential_storage"], "GitHub CLI")


if __name__ == "__main__":
    unittest.main()
