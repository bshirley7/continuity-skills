"""Shared integrity, schema, and atomic persistence helpers for Continuity."""

from __future__ import annotations

import contextlib
import errno
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence, TypeVar

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class RuntimeIntegrityError(RuntimeError):
    pass


_Result = TypeVar("_Result")
_WINDOWS_TRANSIENT_ERRORS = {5, 32, 33}
_WINDOWS_RESERVED_PATH_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "CONIN$",
    "CONOUT$",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
    *(f"COM{index}" for index in "¹²³"),
    *(f"LPT{index}" for index in "¹²³"),
}
_SENSITIVE_ENV_KEY = re.compile(
    r"(?:^|_)(?:ACCESS_KEY|API_KEY|AUTH|BEARER|CREDENTIAL|DATABASE_URL|PASSWORD|PRIVATE_KEY|SECRET|SESSION|TOKEN)(?:$|_)",
    re.IGNORECASE,
)
_SENSITIVE_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [^-\r\n]*PRIVATE KEY-----.*?-----END [^-\r\n]*PRIVATE KEY-----", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bAGE-SECRET-KEY-1[A-Z0-9]+\b", re.IGNORECASE),
    re.compile(r"(?i)\b(authorization\s*:\s*(?:bearer|basic)\s+)[^\s,;]+"),
    re.compile(r"(?i)\b([A-Za-z0-9_.-]*(?:api[_-]?key|access[_-]?key|access[_-]?token|auth[_-]?token|password|private[_-]?key|secret|session|token)[A-Za-z0-9_.-]*\s*[=:]\s*)[^\s,;]+"),
    re.compile(r"\b(?:gh[oprsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}|npm_[A-Za-z0-9_-]{20,}|pypi-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)(https?://[^\s/:@]+:)[^\s/@]+(@)"),
)


def configure_utf8_stdio() -> None:
    """Make CLI pipes and redirected output independent of the host code page."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _create_windows_kill_job(process: subprocess.Popen[Any]) -> int:
    import ctypes
    from ctypes import wintypes

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("read_operations", ctypes.c_ulonglong),
            ("write_operations", ctypes.c_ulonglong),
            ("other_operations", ctypes.c_ulonglong),
            ("read_bytes", ctypes.c_ulonglong),
            ("write_bytes", ctypes.c_ulonglong),
            ("other_bytes", ctypes.c_ulonglong),
        ]

    class BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("per_process_user_time", ctypes.c_longlong),
            ("per_job_user_time", ctypes.c_longlong),
            ("limit_flags", wintypes.DWORD),
            ("minimum_working_set", ctypes.c_size_t),
            ("maximum_working_set", ctypes.c_size_t),
            ("active_process_limit", wintypes.DWORD),
            ("affinity", ctypes.c_size_t),
            ("priority_class", wintypes.DWORD),
            ("scheduling_class", wintypes.DWORD),
        ]

    class ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("basic", BasicLimitInformation),
            ("io", IoCounters),
            ("process_memory_limit", ctypes.c_size_t),
            ("job_memory_limit", ctypes.c_size_t),
            ("peak_process_memory", ctypes.c_size_t),
            ("peak_job_memory", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    information = ExtendedLimitInformation()
    information.basic.limit_flags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel.SetInformationJobObject(job, 9, ctypes.byref(information), ctypes.sizeof(information)):
        error = ctypes.get_last_error()
        kernel.CloseHandle(job)
        raise ctypes.WinError(error)
    if not kernel.AssignProcessToJobObject(job, wintypes.HANDLE(process._handle)):
        error = ctypes.get_last_error()
        kernel.CloseHandle(job)
        raise ctypes.WinError(error)
    return int(job)


def _close_windows_job(job_handle: int | None) -> None:
    if os.name == "nt" and job_handle:
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        kernel.CloseHandle(wintypes.HANDLE(job_handle))


def _terminate_process_tree(process: subprocess.Popen[Any], job_handle: int | None = None) -> None:
    if os.name == "nt" and job_handle:
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.TerminateJobObject(wintypes.HANDLE(job_handle), 1)
        return
    if process.poll() is not None:
        return
    if os.name == "nt":
        process.kill()
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        process.kill()


def run_process_tree(
    argv: Sequence[str | os.PathLike[str]],
    *,
    cwd: str | os.PathLike[str] | None = None,
    input: str | bytes | None = None,
    capture_output: bool = False,
    text: bool = False,
    timeout: float | None = None,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[Any]:
    """Run direct argv and ensure cancellation or timeout kills all descendants."""
    original_argv = [os.fspath(value) for value in argv]
    if not original_argv:
        raise ValueError("argv cannot be empty")
    launch_argv = original_argv
    ready_path: Path | None = None
    if os.name == "nt":
        executable = shutil.which(original_argv[0], path=(env or os.environ).get("PATH"))
        if not executable:
            candidate = Path(original_argv[0])
            if not candidate.is_absolute() and cwd is not None:
                candidate = Path(cwd) / candidate
            if not candidate.is_file():
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), original_argv[0])
            executable = str(candidate.resolve())
        resolved_argv = [executable, *original_argv[1:]]
        descriptor, ready_name = tempfile.mkstemp(prefix="continuity-process-", suffix=".ready")
        os.close(descriptor)
        ready_path = Path(ready_name)
        ready_path.unlink()
        wrapper = (
            "import os,subprocess,sys,time; marker=sys.argv[1]; deadline=time.monotonic()+30; "
            "\nwhile not os.path.exists(marker):"
            "\n if time.monotonic()>=deadline: raise SystemExit(125)"
            "\n time.sleep(0.005)"
            "\nchild=subprocess.Popen(sys.argv[2:],stdin=sys.stdin.buffer,stdout=sys.stdout.buffer,stderr=sys.stderr.buffer)"
            "\nraise SystemExit(child.wait())"
        )
        launch_argv = [sys.executable, "-c", wrapper, str(ready_path), *resolved_argv]
    process = subprocess.Popen(
        launch_argv,
        cwd=cwd,
        stdin=subprocess.PIPE if input is not None else None,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        text=text,
        env=env,
        start_new_session=os.name != "nt",
    )
    job_handle: int | None = None
    try:
        if os.name == "nt":
            job_handle = _create_windows_kill_job(process)
            assert ready_path is not None
            ready_path.touch()
        try:
            stdout, stderr = process.communicate(input=input, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            _terminate_process_tree(process, job_handle)
            stdout, stderr = process.communicate()
            exc.cmd = original_argv
            exc.stdout = stdout
            exc.stderr = stderr
            raise
        except BaseException:
            _terminate_process_tree(process, job_handle)
            process.communicate()
            raise
    finally:
        _close_windows_job(job_handle)
        if ready_path is not None:
            with contextlib.suppress(OSError):
                ready_path.unlink()
    completed = subprocess.CompletedProcess(original_argv, process.returncode, stdout, stderr)
    if check:
        completed.check_returncode()
    return completed


def project_relative_posix(path: Path, root: Path) -> str:
    """Return a stable project-relative path for persisted records and output."""
    resolved_root = root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise RuntimeIntegrityError(f"Path escapes the project root: {path}")
    return resolved.relative_to(resolved_root).as_posix()


def validate_portable_relative_path(value: str, *, label: str = "Path") -> str:
    """Validate an archive or manifest path against portable Windows rules."""
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise RuntimeIntegrityError(f"{label} must be a non-empty relative path of at most 4096 characters")
    if "\\" in value or value.startswith("/") or value.endswith("/") or re.match(r"^[A-Za-z]:", value):
        raise RuntimeIntegrityError(f"{label} is not a portable relative path: {value!r}")
    parts = value.split("/")
    for part in parts:
        if part in {"", ".", ".."}:
            raise RuntimeIntegrityError(f"{label} contains an unsafe path segment: {value!r}")
        if unicodedata.normalize("NFC", part) != part:
            raise RuntimeIntegrityError(f"{label} must use NFC-normalized Unicode: {value!r}")
        if len(part.encode("utf-8")) > 255:
            raise RuntimeIntegrityError(f"{label} contains a path segment longer than 255 UTF-8 bytes: {value!r}")
        if part.endswith((" ", ".")) or any(
            unicodedata.category(character) in {"Cc", "Cf", "Cs"} or character in '<>:"|?*'
            for character in part
        ):
            raise RuntimeIntegrityError(f"{label} contains characters Windows cannot store safely: {value!r}")
        if part.split(".", 1)[0].rstrip(" ").upper() in _WINDOWS_RESERVED_PATH_NAMES:
            raise RuntimeIntegrityError(f"{label} uses a Windows reserved device name: {value!r}")
    return "/".join(parts)


def redact_sensitive_text(value: Any) -> str:
    """Remove common credential forms from persisted diagnostics and CLI errors."""
    redacted = "" if value is None else str(value)
    for pattern in _SENSITIVE_TEXT_PATTERNS:
        if pattern.groups == 2:
            redacted = pattern.sub(r"\1[REDACTED]\2", redacted)
        elif pattern.groups == 1:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def restricted_subprocess_environment(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Copy the process environment while excluding likely credentials."""
    environment = {key: value for key, value in os.environ.items() if not _SENSITIVE_ENV_KEY.search(key)}
    if extra:
        for key, value in extra.items():
            if _SENSITIVE_ENV_KEY.search(key):
                raise RuntimeIntegrityError(f"Refusing to pass sensitive environment variable to a validation command: {key}")
            environment[key] = value
    return environment


def casefold_path_collisions(paths: Sequence[str]) -> list[list[str]]:
    """Find paths that cannot coexist on a case-insensitive filesystem."""
    grouped: dict[str, set[str]] = {}
    for value in paths:
        display = value.replace("\\", "/").strip("/")
        comparison = unicodedata.normalize("NFC", display).casefold()
        grouped.setdefault(comparison, set()).add(display)
    return [sorted(values) for values in grouped.values() if len(values) > 1]


def _windows_drive_type(path: Path) -> int | None:
    if os.name != "nt":
        return None
    import ctypes

    anchor = path.resolve().anchor
    return int(ctypes.windll.kernel32.GetDriveTypeW(anchor)) if anchor else None


def project_filesystem_profile(root: Path) -> dict[str, Any]:
    """Describe platform properties that affect Continuity persistence."""
    resolved = root.resolve()
    drive_type = _windows_drive_type(resolved)
    remote = drive_type == 4  # Win32 DRIVE_REMOTE (UNC or mapped network drive).
    one_drive = False
    if os.name == "nt":
        for name in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
            value = os.environ.get(name)
            if not value:
                continue
            candidate = Path(value).resolve()
            if resolved == candidate or resolved.is_relative_to(candidate):
                one_drive = True
                break
    return {
        "platform": os.name,
        "path_length": len(str(resolved)),
        "windows_drive_type": drive_type,
        "remote_filesystem": remote,
        "one_drive": one_drive,
        "supported": not remote,
        "problem": "UNC and mapped network-drive project roots are unsupported because atomic replacement and locking semantics cannot be guaranteed" if remote else None,
    }


def validate_project_filesystem(root: Path, tracked_paths: Sequence[str] = ()) -> dict[str, Any]:
    profile = project_filesystem_profile(root)
    if not profile["supported"]:
        raise RuntimeIntegrityError(str(profile["problem"]))
    collisions = casefold_path_collisions(tracked_paths)
    if collisions:
        rendered = "; ".join(", ".join(group) for group in collisions)
        raise RuntimeIntegrityError(f"Case-insensitive path collisions are not supported on Windows: {rendered}")
    return {**profile, "case_collisions": collisions}


def windows_acl_profile(path: Path) -> dict[str, Any]:
    """Report whether broad Windows principals can modify a sensitive path."""
    if os.name != "nt":
        return {"applicable": False, "broad_write_principals": [], "healthy": True}
    import ctypes
    from ctypes import wintypes

    class Trustee(ctypes.Structure):
        _fields_ = [
            ("multiple_trustee", ctypes.c_void_p),
            ("multiple_trustee_operation", ctypes.c_int),
            ("trustee_form", ctypes.c_int),
            ("trustee_type", ctypes.c_int),
            ("name", ctypes.c_void_p),
        ]

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    get_security = advapi.GetNamedSecurityInfoW
    get_security.argtypes = [
        wintypes.LPWSTR,
        ctypes.c_int,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    get_security.restype = wintypes.DWORD
    convert_sid = advapi.ConvertStringSidToSidW
    convert_sid.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
    convert_sid.restype = wintypes.BOOL
    effective_rights = advapi.GetEffectiveRightsFromAclW
    effective_rights.argtypes = [ctypes.c_void_p, ctypes.POINTER(Trustee), ctypes.POINTER(wintypes.DWORD)]
    effective_rights.restype = wintypes.DWORD
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p

    dacl = ctypes.c_void_p()
    descriptor = ctypes.c_void_p()
    result = get_security(str(path.resolve()), 1, 0x00000004, None, None, ctypes.byref(dacl), None, ctypes.byref(descriptor))
    if result != 0:
        raise RuntimeIntegrityError(f"Unable to inspect Windows ACL for {path}: Win32 error {result}")
    write_mask = 0x00000002 | 0x00000004 | 0x00000010 | 0x00000100 | 0x00010000 | 0x00040000 | 0x00080000 | 0x10000000 | 0x40000000
    broad: list[str] = []
    try:
        for name, sid_text in (("Everyone", "S-1-1-0"), ("BUILTIN\\Users", "S-1-5-32-545")):
            sid = ctypes.c_void_p()
            if not convert_sid(sid_text, ctypes.byref(sid)):
                raise RuntimeIntegrityError(f"Unable to construct Windows SID {sid_text}")
            try:
                trustee = Trustee(None, 0, 0, 0, sid)
                access = wintypes.DWORD()
                status = effective_rights(dacl, ctypes.byref(trustee), ctypes.byref(access))
                if status != 0:
                    raise RuntimeIntegrityError(f"Unable to evaluate Windows ACL for {name}: Win32 error {status}")
                if access.value & write_mask:
                    broad.append(name)
            finally:
                kernel.LocalFree(sid)
    finally:
        kernel.LocalFree(descriptor)
    return {"applicable": True, "broad_write_principals": broad, "healthy": not broad}


@contextlib.contextmanager
def secure_temporary_directory(*, prefix: str, directory: Path | None = None) -> Iterable[Path]:
    """Create a temporary directory and fail closed on a broad Windows DACL."""
    with tempfile.TemporaryDirectory(prefix=prefix, dir=str(directory) if directory else None) as temporary:
        path = Path(temporary)
        profile = windows_acl_profile(path)
        if not profile["healthy"]:
            raise RuntimeIntegrityError(
                f"Sensitive temporary directory is writable by broad Windows principals: {profile['broad_write_principals']}"
            )
        yield path


def _is_transient_windows_error(exc: OSError) -> bool:
    return os.name == "nt" and (
        getattr(exc, "winerror", None) in _WINDOWS_TRANSIENT_ERRORS
        or exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}
    )


def _retry_windows_file_operation(
    operation: Callable[[], _Result],
    *,
    attempts: int = 20,
    delay_seconds: float = 0.05,
) -> _Result:
    """Retry only transient Windows sharing violations for idempotent file I/O."""
    for attempt in range(attempts):
        try:
            return operation()
        except OSError as exc:
            if not _is_transient_windows_error(exc) or attempt + 1 == attempts:
                raise
            time.sleep(delay_seconds)
    raise AssertionError("unreachable")


def replace_staged_file(source: Path, destination: Path) -> None:
    """Atomically publish a complete staged file with transient Windows retry."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    _retry_windows_file_operation(lambda: os.replace(source, destination))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _private_root(path: Path) -> Path | None:
    resolved = path.resolve()
    parts = resolved.parts
    for index in range(len(parts) - 1):
        if parts[index] == ".continuity" and parts[index + 1] == "private":
            return Path(*parts[: index + 2])
    return None


def mutation_lock_path(path: Path) -> Path:
    private = _private_root(path)
    return (private / ".state.lock") if private else path.parent / ".continuity-write.lock"


@contextlib.contextmanager
def exclusive_file_lock(path: Path) -> Iterable[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use a binary handle because Windows locks byte ranges rather than whole
    # files.  The sentinel byte makes the same one-byte range available to all
    # contenders while the POSIX implementation retains flock semantics.
    with path.open("a+b") as handle:
        if os.name == "nt":
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError as exc:
                    if not _is_transient_windows_error(exc):
                        raise
                    time.sleep(0.05)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _fsync_directory(path: Path) -> None:
    # Windows does not support opening a directory as a file descriptor.
    # os.replace is still atomic there; flushing the temporary file above is
    # the strongest portable durability guarantee available from Python.
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _cleanup_stale_atomic_temps(path: Path) -> None:
    for candidate in path.parent.glob(f".{path.name}.*.tmp"):
        if candidate.is_file() or candidate.is_symlink():
            _retry_windows_file_operation(candidate.unlink)


def atomic_write_bytes(path: Path, value: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(mutation_lock_path(path)):
        _cleanup_stale_atomic_temps(path)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp_path = Path(temporary)
        try:
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, mode)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            _retry_windows_file_operation(lambda: os.replace(temp_path, path))
            _fsync_directory(path.parent)
        finally:
            if temp_path.exists():
                _retry_windows_file_operation(temp_path.unlink)


def atomic_write_text(path: Path, value: str, *, mode: int = 0o600) -> None:
    atomic_write_bytes(path, value.encode("utf-8"), mode=mode)


def atomic_write_json(path: Path, value: Any, *, mode: int = 0o600) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n", mode=mode)


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "_integrity"}


def verify_jsonl_records(path: Path, *, allow_legacy: bool = True) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "records": 0, "integrity_records": 0, "legacy_records": 0, "head_hash": None, "healthy": True}
    previous: str | None = None
    legacy = 0
    integrity = 0
    logical_sequence = 0
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        logical_sequence += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeIntegrityError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(record, dict):
            raise RuntimeIntegrityError(f"JSONL record at {path}:{number} is not an object")
        metadata = record.get("_integrity")
        if not isinstance(metadata, dict):
            legacy += 1
            if not allow_legacy:
                raise RuntimeIntegrityError(f"Unsigned legacy JSONL record at {path}:{number}")
            previous = f"legacy:{sha256_bytes(canonical_json(record).encode())}"
            continue
        integrity += 1
        sequence = metadata.get("sequence")
        if sequence != logical_sequence:
            raise RuntimeIntegrityError(f"JSONL sequence mismatch at {path}:{number}")
        if metadata.get("previous_hash") != previous:
            raise RuntimeIntegrityError(f"JSONL chain mismatch at {path}:{number}")
        material = {
            "sequence": sequence,
            "previous_hash": previous,
            "payload": _record_payload(record),
        }
        expected = sha256_bytes(canonical_json(material).encode())
        if metadata.get("record_hash") != expected:
            raise RuntimeIntegrityError(f"JSONL record hash mismatch at {path}:{number}")
        previous = expected
    return {
        "path": str(path),
        "records": legacy + integrity,
        "integrity_records": integrity,
        "legacy_records": legacy,
        "head_hash": previous,
        "healthy": True,
    }


def jsonl_chain_hash_at(path: Path, record_count: int) -> str | None:
    status = verify_jsonl_records(path)
    if record_count < 0 or record_count > int(status["records"]):
        raise RuntimeIntegrityError(f"JSONL checkpoint count is outside the current ledger: {path}")
    if record_count == 0:
        return None
    logical_sequence = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        logical_sequence += 1
        record = json.loads(line)
        metadata = record.get("_integrity") if isinstance(record, dict) else None
        current = metadata.get("record_hash") if isinstance(metadata, dict) else f"legacy:{sha256_bytes(canonical_json(record).encode())}"
        if logical_sequence == record_count:
            return current
    raise RuntimeIntegrityError(f"JSONL checkpoint count could not be resolved: {path}")


def append_integrity_jsonl(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeIntegrityError("JSONL values must be objects")
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(mutation_lock_path(path)):
        verify_jsonl_records(path)
        existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        nonempty = [line for line in existing if line.strip()]
        previous: str | None = None
        if nonempty:
            try:
                last = json.loads(nonempty[-1])
            except json.JSONDecodeError as exc:
                raise RuntimeIntegrityError(f"Cannot append to invalid JSONL ledger {path}") from exc
            metadata = last.get("_integrity") if isinstance(last, dict) else None
            previous = metadata.get("record_hash") if isinstance(metadata, dict) else f"legacy:{sha256_bytes(canonical_json(last).encode())}"
        sequence = len(nonempty) + 1
        payload = _record_payload(value)
        material = {"sequence": sequence, "previous_hash": previous, "payload": payload}
        record = {
            **payload,
            "_integrity": {
                "algorithm": "sha256-chain-v1",
                "sequence": sequence,
                "previous_hash": previous,
                "record_hash": sha256_bytes(canonical_json(material).encode()),
            },
        }
        encoded = (canonical_json(record) + "\n").encode()
        with path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
        return record


def load_jsonl(path: Path, *, verify: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if verify:
        verify_jsonl_records(path)
    values: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            values.append(json.loads(line))
    return values


def _resolve_schema(schema: dict[str, Any], schema_path: Path) -> tuple[dict[str, Any], Path]:
    reference = schema.get("$ref")
    if not reference:
        return schema, schema_path
    if reference.startswith("#"):
        raise RuntimeIntegrityError(f"Internal schema references are not supported: {reference}")
    target = (schema_path.parent / reference).resolve()
    return json.loads(target.read_text(encoding="utf-8")), target


def validate_schema(value: Any, schema: dict[str, Any], schema_path: Path, label: str = "record") -> None:
    schema, schema_path = _resolve_schema(schema, schema_path)
    if "const" in schema and value != schema["const"]:
        raise RuntimeIntegrityError(f"{label} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise RuntimeIntegrityError(f"{label} is not one of {schema['enum']}")
    expected = schema.get("type")
    type_checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected in type_checks and not type_checks[expected](value):
        raise RuntimeIntegrityError(f"{label} must be a {expected}")
    if isinstance(value, dict):
        if len(value) < int(schema.get("minProperties", 0)):
            raise RuntimeIntegrityError(f"{label} has too few properties")
        if schema.get("maxProperties") is not None and len(value) > int(schema["maxProperties"]):
            raise RuntimeIntegrityError(f"{label} has too many properties")
        required = schema.get("required", [])
        missing = sorted(set(required) - set(value))
        if missing:
            raise RuntimeIntegrityError(f"{label} is missing required fields: {missing}")
        properties = schema.get("properties", {})
        unknown = sorted(set(value) - set(properties))
        additional = schema.get("additionalProperties")
        if additional is False:
            if unknown:
                raise RuntimeIntegrityError(f"{label} has unsupported fields: {unknown}")
        elif isinstance(additional, dict):
            for key in unknown:
                validate_schema(value[key], additional, schema_path, f"{label}.{key}")
        property_names = schema.get("propertyNames")
        if isinstance(property_names, dict):
            for key in value:
                validate_schema(key, property_names, schema_path, f"{label} property name")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, schema_path, f"{label}.{key}")
    if isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            raise RuntimeIntegrityError(f"{label} has too few items")
        if schema.get("uniqueItems") and len({canonical_json(item) for item in value}) != len(value):
            raise RuntimeIntegrityError(f"{label} items must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], schema_path, f"{label}[{index}]")
    if isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            raise RuntimeIntegrityError(f"{label} is too short")
        if schema.get("maxLength") is not None and len(value) > int(schema["maxLength"]):
            raise RuntimeIntegrityError(f"{label} is too long")
        if schema.get("pattern") and not re.fullmatch(schema["pattern"], value):
            raise RuntimeIntegrityError(f"{label} does not match the required format")
    if isinstance(value, int) and not isinstance(value, bool):
        if schema.get("minimum") is not None and value < schema["minimum"]:
            raise RuntimeIntegrityError(f"{label} is below the minimum")
        if schema.get("maximum") is not None and value > schema["maximum"]:
            raise RuntimeIntegrityError(f"{label} is above the maximum")


def validate_schema_file(value: Any, path: Path, label: str = "record") -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    validate_schema(value, schema, path, label)
