#!/usr/bin/env python3
"""Reject source-specific maintenance material at the shared repository boundary."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".py", ""}
BLOCKED = (
    "mo" + "bbin",
    "docs." + "mo" + "bbin.com",
    "growth." + "design",
    "continuity-design-" + "research",
    "research-" + "ledger",
    "data:" + "image",
    "base" + "64,",
)
PATTERNS = (
    re.compile(r"https?://[^\s\"')]+\.(?:png|jpe?g|gif|webp|avif|svg)(?:\?[^\s\"')]*)?", re.I),
    re.compile(r"(?:(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret)\s*[:=]\s*\S+|authorization:\s*bearer\s+\S+)", re.I),
)


def validate(paths: list[Path]) -> list[dict[str, str]]:
    problems: list[dict[str, str]] = []
    for root in paths:
        files = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in files:
            if "tests" in path.parts:
                continue
            if path.suffix.casefold() not in TEXT_SUFFIXES or path.name == "release-manifest.json":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            lowered = text.casefold()
            for token in BLOCKED:
                if token.casefold() in lowered:
                    problems.append({"path": str(path), "rule": "private-maintenance-boundary"})
                    break
            else:
                if any(pattern.search(text) for pattern in PATTERNS):
                    problems.append({"path": str(path), "rule": "private-or-image-reference"})
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    problems = validate([path.resolve() for path in args.paths])
    print(json.dumps({"healthy": not problems, "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
