from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SUITE = Path(__file__).resolve().parents[1]
LIB = SUITE / "lib"
sys.path.insert(0, str(LIB))
import runtime  # noqa: E402


def python_process(source: str, *arguments: Path | str) -> subprocess.Popen[str]:
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.Popen(
        [sys.executable, "-c", source, str(LIB), *(str(item) for item in arguments)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )


class RuntimePortabilityTest(unittest.TestCase):
    def test_cli_output_is_utf8_when_host_stdio_requests_a_legacy_encoding(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity-locale-") as directory:
            root = Path(directory) / "données-✓"
            root.mkdir()
            environment = {
                **os.environ,
                "PYTHONUTF8": "0",
                "PYTHONIOENCODING": "cp1252",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            result = subprocess.run(
                [sys.executable, str(SUITE / "bin" / "continuity"), "--project-root", str(root), "--json", "project", "doctor"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            decoded = result.stderr.decode("utf-8")
            self.assertIn(root.name, decoded)

    def test_project_relative_paths_are_posix_and_confined(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            nested = root / "données" / "nested file.json"
            nested.parent.mkdir()
            nested.write_text("{}", encoding="utf-8")
            self.assertEqual(runtime.project_relative_posix(nested, root), "données/nested file.json")
            with self.assertRaises(runtime.RuntimeIntegrityError):
                runtime.project_relative_posix(root.parent, root)

    def test_casefold_collisions_normalize_separators(self) -> None:
        self.assertEqual(
            runtime.casefold_path_collisions(["Docs/Plan.md", "docs\\plan.md", "docs/other.md"]),
            [["Docs/Plan.md", "docs/plan.md"]],
        )

    def test_casefold_collisions_normalize_unicode(self) -> None:
        self.assertEqual(
            runtime.casefold_path_collisions(["docs/caf\u00e9.md", "DOCS/cafe\u0301.md"]),
            [["DOCS/cafe\u0301.md", "docs/caf\u00e9.md"]],
        )
        self.assertEqual(
            runtime.casefold_path_collisions(["docs/caf\u00e9.md", "docs/cafe\u0301.md"]),
            [["docs/cafe\u0301.md", "docs/caf\u00e9.md"]],
        )

    def test_portable_relative_paths_reject_windows_and_unicode_hazards(self) -> None:
        self.assertEqual(runtime.validate_portable_relative_path("docs/ready.txt"), "docs/ready.txt")
        for value in (
            "../escape", "folder\\file", "CON.txt", "CON .txt", "COM¹.txt", "file.txt:stream",
            "trail.", "cafe\u0301.txt", "bidirectional-\u202efile.txt", "/rooted",
        ):
            with self.subTest(value=value), self.assertRaises(runtime.RuntimeIntegrityError):
                runtime.validate_portable_relative_path(value)

    def test_secret_redaction_and_restricted_subprocess_environment(self) -> None:
        secret = "ghp_012345678901234567890123456789012345"
        rendered = runtime.redact_sensitive_text(f"Authorization: Bearer {secret} token={secret} https://nick:{secret}@example.test/repo")
        self.assertNotIn(secret, rendered)
        self.assertGreaterEqual(rendered.count("[REDACTED]"), 3)
        with mock.patch.dict(os.environ, {"PATH": "safe-path", "GH_TOKEN": secret, "CONTINUITY_API_KEY": secret}, clear=True):
            environment = runtime.restricted_subprocess_environment({"PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(environment["PATH"], "safe-path")
        self.assertEqual(environment["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertNotIn("GH_TOKEN", environment)
        self.assertNotIn("CONTINUITY_API_KEY", environment)

    def test_local_filesystem_profile_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile = runtime.validate_project_filesystem(Path(directory))
            self.assertTrue(profile["supported"])
            self.assertFalse(profile["remote_filesystem"])

    @unittest.skipUnless(os.name == "nt", "Windows UNC policy")
    def test_windows_remote_drive_profile_fails_closed(self) -> None:
        with mock.patch.object(runtime, "_windows_drive_type", return_value=4):
            with self.assertRaisesRegex(runtime.RuntimeIntegrityError, "UNC and mapped network-drive"):
                runtime.validate_project_filesystem(Path.cwd())

    @unittest.skipUnless(os.name == "nt", "Windows ACL inspection")
    def test_windows_private_temp_acl_is_not_broadly_writable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory) / ".continuity" / "private"
            private.mkdir(parents=True)
            profile = runtime.windows_acl_profile(private)
            self.assertTrue(profile["applicable"])
            self.assertTrue(profile["healthy"], profile)

    def test_long_unicode_path_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root
            for index in range(8):
                target /= f"segment-{index}-{'x' * 24}"
            target /= "résultat.json"
            runtime.atomic_write_json(target, {"status": "complete", "path_length": len(str(target))})
            self.assertGreater(len(str(target)), 260)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["status"], "complete")

    @unittest.skipUnless(os.name == "nt" and os.environ.get("OneDrive"), "OneDrive workspace smoke test")
    def test_onedrive_workspace_atomic_write_and_ledger(self) -> None:
        one_drive = Path(os.environ["OneDrive"]).resolve()
        self.assertTrue(SUITE.resolve().is_relative_to(one_drive), "the checked-out suite is not under the configured OneDrive root")
        with tempfile.TemporaryDirectory(prefix="continuity onedrive ü-", dir=SUITE.parent) as directory:
            root = Path(directory)
            profile = runtime.project_filesystem_profile(root)
            self.assertTrue(profile["one_drive"])
            state = root / ".continuity" / "private" / "state.json"
            ledger = root / ".continuity" / "private" / "events.jsonl"
            runtime.atomic_write_json(state, {"workspace": "OneDrive", "complete": True})
            runtime.append_integrity_jsonl(ledger, {"event": "onedrive.smoke"})
            self.assertTrue(json.loads(state.read_text(encoding="utf-8"))["complete"])
            self.assertEqual(runtime.verify_jsonl_records(ledger)["records"], 1)

    @unittest.skipUnless(os.name == "nt", "Windows junction containment")
    def test_windows_junction_cannot_escape_project(self) -> None:
        with tempfile.TemporaryDirectory() as project_directory, tempfile.TemporaryDirectory() as outside_directory:
            project = Path(project_directory)
            outside = Path(outside_directory)
            secret = outside / "secret.txt"
            secret.write_text("outside", encoding="utf-8")
            junction = project / "linked-outside"
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            try:
                with self.assertRaises(runtime.RuntimeIntegrityError):
                    runtime.project_relative_posix(junction / "secret.txt", project)
            finally:
                os.rmdir(junction)

    def test_atomic_unicode_write_replaces_complete_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "données" / "state file.json"
            runtime.atomic_write_text(target, "first")
            runtime.atomic_write_text(target, "réplacement ✓")
            self.assertEqual(target.read_text(encoding="utf-8"), "réplacement ✓")
            self.assertEqual(list(target.parent.glob(f".{target.name}.*.tmp")), [])

    @unittest.skipUnless(os.name == "nt", "Windows sharing-violation retry behavior")
    def test_atomic_replace_retries_transient_windows_sharing_violation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            original = os.replace
            calls = 0

            def flaky(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls < 3:
                    error = PermissionError(errno_value := 13, "sharing violation")
                    error.winerror = 32
                    error.errno = errno_value
                    raise error
                original(source, destination)

            with mock.patch.object(runtime.os, "replace", side_effect=flaky):
                runtime.atomic_write_text(target, "complete")
            self.assertEqual(target.read_text(encoding="utf-8"), "complete")
            self.assertEqual(calls, 3)

    def test_lock_excludes_a_second_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "state.lock"
            ready = root / "ready"
            acquired = root / "acquired"
            holder_source = (
                "import sys,time; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                "import runtime; lock=Path(sys.argv[2]); ready=Path(sys.argv[3]); "
                "ctx=runtime.exclusive_file_lock(lock); ctx.__enter__(); "
                "ready.write_text('ready',encoding='utf-8'); time.sleep(2); ctx.__exit__(None,None,None)"
            )
            waiter_source = (
                "import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                "import runtime; lock=Path(sys.argv[2]); acquired=Path(sys.argv[3]); "
                "\nwith runtime.exclusive_file_lock(lock): acquired.write_text('acquired',encoding='utf-8')"
            )
            holder = python_process(holder_source, lock, ready)
            self._wait_for_path(ready, holder)
            waiter = python_process(waiter_source, lock, acquired)
            time.sleep(0.3)
            self.assertFalse(acquired.exists(), "the waiter acquired an already-held process lock")
            holder_stdout, holder_stderr = holder.communicate(timeout=5)
            waiter_stdout, waiter_stderr = waiter.communicate(timeout=5)
            self.assertEqual(holder.returncode, 0, holder_stderr or holder_stdout)
            self.assertEqual(waiter.returncode, 0, waiter_stderr or waiter_stdout)
            self.assertTrue(acquired.exists())

    def test_terminated_process_releases_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "state.lock"
            ready = root / "ready"
            acquired = root / "acquired"
            holder_source = (
                "import sys,time; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                "import runtime; ctx=runtime.exclusive_file_lock(Path(sys.argv[2])); ctx.__enter__(); "
                "Path(sys.argv[3]).write_text('ready',encoding='utf-8'); time.sleep(60)"
            )
            waiter_source = (
                "import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import runtime; "
                "\nwith runtime.exclusive_file_lock(Path(sys.argv[2])): Path(sys.argv[3]).write_text('ok',encoding='utf-8')"
            )
            holder = python_process(holder_source, lock, ready)
            self._wait_for_path(ready, holder)
            holder.terminate()
            holder.communicate(timeout=5)
            waiter = python_process(waiter_source, lock, acquired)
            waiter_stdout, waiter_stderr = waiter.communicate(timeout=5)
            self.assertEqual(waiter.returncode, 0, waiter_stderr or waiter_stdout)
            self.assertEqual(acquired.read_text(encoding="utf-8"), "ok")

    def test_interrupted_atomic_write_preserves_canonical_state_and_recovers_temp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "state.json"
            marker = root / "ready"
            runtime.atomic_write_text(target, "canonical-old")
            source = (
                "import sys,time; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import runtime; "
                "target=Path(sys.argv[2]); marker=Path(sys.argv[3])\n"
                "def pause(source,destination):\n marker.write_text('ready',encoding='utf-8'); time.sleep(60)\n"
                "runtime.os.replace=pause; runtime.atomic_write_text(target,'partial-new')"
            )
            writer = python_process(source, target, marker)
            self._wait_for_path(marker, writer)
            writer.terminate()
            writer.communicate(timeout=5)
            self.assertEqual(target.read_text(encoding="utf-8"), "canonical-old")
            self.assertEqual(len(list(root.glob(f".{target.name}.*.tmp"))), 1)
            runtime.atomic_write_text(target, "canonical-new")
            self.assertEqual(target.read_text(encoding="utf-8"), "canonical-new")
            self.assertEqual(list(root.glob(f".{target.name}.*.tmp")), [])

    def test_timeout_terminates_the_full_child_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            survived = Path(directory) / "grandchild-survived.txt"
            started = Path(directory) / "grandchild-started.txt"
            grandchild = (
                "import sys,time; from pathlib import Path; "
                "Path(sys.argv[1]).write_text('started',encoding='utf-8'); "
                "time.sleep(2); Path(sys.argv[2]).write_text('survived',encoding='utf-8')"
            )
            parent = (
                "import subprocess,sys,time; "
                "subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]]); "
                "time.sleep(30)"
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                runtime.run_process_tree(
                    [sys.executable, "-c", parent, grandchild, str(started), str(survived)],
                    capture_output=True,
                    text=True,
                    timeout=0.75,
                )
            deadline = time.monotonic() + 1
            while time.monotonic() < deadline and not started.exists():
                time.sleep(0.02)
            self.assertTrue(started.exists(), "the grandchild did not start before cancellation")
            time.sleep(2.25)
            self.assertFalse(survived.exists(), "a timed-out validation command left a grandchild running")

    def test_concurrent_processes_append_one_integrity_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / ".continuity" / "private" / "events.jsonl"
            source = (
                "import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import runtime; "
                "ledger=Path(sys.argv[2]); worker=int(sys.argv[3]); "
                "[runtime.append_integrity_jsonl(ledger,{'worker':worker,'item':item}) for item in range(15)]"
            )
            processes = [python_process(source, ledger, str(worker)) for worker in range(4)]
            for process in processes:
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, 0, stderr or stdout)
            status = runtime.verify_jsonl_records(ledger, allow_legacy=False)
            records = runtime.load_jsonl(ledger)
            self.assertEqual(status["records"], 60)
            self.assertEqual({(item["worker"], item["item"]) for item in records}, {(worker, item) for worker in range(4) for item in range(15)})

    def _wait_for_path(self, path: Path, process: subprocess.Popen[str]) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if path.exists():
                return
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.fail(stderr or stdout or "child process exited before signaling readiness")
            time.sleep(0.02)
        process.kill()
        self.fail(f"timed out waiting for child process marker {path}")


if __name__ == "__main__":
    unittest.main()
