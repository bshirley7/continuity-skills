#!/usr/bin/env python3
"""Build the deterministic Continuity release file manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INCLUDED_ROOTS = ("automation", "bin", "docs", "installer", "lib", "references", "roadmap-ui", "schemas", "scripts", "skills", "templates")
INCLUDED_FILES = ("CONTRIBUTING.md", "README.md", "SUITE.md", "VERSION", "requirements.txt")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(root: Path, release_commit: str | None = None) -> dict[str, object]:
    root = root.resolve()
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    files = {}
    for name in INCLUDED_FILES:
        path = root / name
        files[name] = digest(path)
    for directory in INCLUDED_ROOTS:
        for path in sorted((root / directory).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith(".pyc"):
                files[path.relative_to(root).as_posix()] = digest(path)
    manifest = {
        "schema_version": 1,
        "suite": "Continuity",
        "version": version,
        "canonical_repository": "https://github.com/bshirley7/continuity-skills",
        "supported_platforms": ["darwin", "linux", "win32"],
        "state_schema_versions": [1],
        "assurance_standard_versions": [2],
        "files": files,
    }
    if release_commit:
        manifest["release_commit"] = release_commit
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--output", default="release-manifest.json")
    parser.add_argument("--release-commit", help="Immutable source commit embedded only in a published artifact")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = build_manifest(root, args.release_commit)
    output = root / args.output
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
