#!/usr/bin/env python3
"""Cross-platform compile, documentation, dependency, and manifest checks."""

from __future__ import annotations

import json
import py_compile
import re
import sys
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "scripts"))
import runtime  # noqa: E402
from build_release_manifest import build_manifest  # noqa: E402
from validate_skills import main as validate_skills  # noqa: E402


def compile_python() -> int:
    sources = [ROOT / "bin" / "continuity", ROOT / "installer" / "install.py"]
    for directory in (ROOT / "lib", ROOT / "scripts"):
        sources.extend(sorted(directory.glob("*.py")))
    for source in sources:
        py_compile.compile(str(source), doraise=True)
    return len(sources)


def validate_markdown_links() -> int:
    failures: list[str] = []
    checked = 0
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for document in sorted(ROOT.rglob("*.md")):
        if "__pycache__" in document.parts:
            continue
        for raw_target in pattern.findall(document.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("#", "/")) or urllib.parse.urlsplit(target).scheme:
                continue
            checked += 1
            resolved = (document.parent / urllib.parse.unquote(target)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                failures.append(f"{document.relative_to(ROOT).as_posix()}: broken or escaping link {raw_target}")
    if failures:
        raise RuntimeError("\n".join(failures))
    return checked


def validate_requirements() -> int:
    lines = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    logical: list[str] = []
    pending = ""
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        pending = f"{pending} {line}".strip()
        if pending.endswith("\\"):
            pending = pending[:-1].rstrip()
            continue
        logical.append(pending)
        pending = ""
    if pending:
        raise RuntimeError("requirements.txt ends with an incomplete continuation")
    for requirement in logical:
        package = requirement.split()[0]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s]+", package):
            raise RuntimeError(f"Dependency is not exactly pinned: {package}")
        hashes = re.findall(r"--hash=sha256:([a-f0-9]{64})(?:\s|$)", requirement)
        if not hashes or len(hashes) != len(set(hashes)):
            raise RuntimeError(f"Dependency must have unique SHA-256 hashes: {package}")
    return len(logical)


def validate_manifest() -> int:
    recorded = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    expected = build_manifest(ROOT)
    if recorded != expected:
        raise RuntimeError("release-manifest.json is stale; run scripts/build_release_manifest.py")
    paths = list(recorded.get("files", {}))
    for relative in paths:
        runtime.validate_portable_relative_path(relative, label="Release manifest path")
    collisions = runtime.casefold_path_collisions(paths)
    if collisions:
        raise RuntimeError(f"Release manifest contains portable path collisions: {collisions}")
    return len(paths)


def main() -> int:
    compiled = compile_python()
    validate_skills()
    links = validate_markdown_links()
    dependencies = validate_requirements()
    files = validate_manifest()
    print(
        f"Validated distribution: {compiled} Python sources, {links} local Markdown links, "
        f"{dependencies} hashed dependencies, {files} release files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
