#!/usr/bin/env python3
"""Validate Continuity skill metadata and local reference links."""

from __future__ import annotations

import re
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    for directory in sorted(path for path in (root / "skills").iterdir() if path.is_dir()):
        skill = directory / "SKILL.md"
        if not skill.is_file():
            failures.append(f"{directory.name}: missing SKILL.md")
            continue
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\nname:" not in text or "\ndescription:" not in text:
            failures.append(f"{directory.name}: invalid frontmatter")
        if len(text.splitlines()) > 500:
            failures.append(f"{directory.name}: SKILL.md exceeds 500 lines")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (directory / target.split("#", 1)[0]).resolve()
            if not resolved.is_file():
                failures.append(f"{directory.name}: broken reference {target}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Validated {sum(1 for path in (root / 'skills').iterdir() if path.is_dir())} Continuity skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
