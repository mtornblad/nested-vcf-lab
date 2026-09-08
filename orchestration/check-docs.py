#!/usr/bin/env python3
"""Validate local Markdown links and fenced code blocks."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


LAB_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^\s*```")
IGNORED_SCHEMES = frozenset({"http", "https", "mailto", "sandbox"})


def markdown_files() -> list[Path]:
    candidates = [LAB_ROOT / "README.md", LAB_ROOT / "artifacts" / "README.md"]
    candidates.extend(sorted((LAB_ROOT / "docs").rglob("*.md")))
    return [path for path in candidates if path.is_file()]


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split(maxsplit=1)[0]
    parsed = urlsplit(target)
    if parsed.scheme in IGNORED_SCHEMES or parsed.netloc or not parsed.path:
        return None
    decoded = unquote(parsed.path)
    if decoded.startswith("/"):
        return LAB_ROOT / decoded.removeprefix("/")
    return source.parent / decoded


def validate_file(path: Path) -> list[str]:
    relative = path.relative_to(LAB_ROOT)
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    fences = sum(1 for line in content.splitlines() if FENCE_PATTERN.match(line))
    if fences % 2:
        errors.append(f"{relative}: unclosed fenced code block")

    for match in LINK_PATTERN.finditer(content):
        raw_target = match.group(1)
        target = local_target(path, raw_target)
        if target is None:
            continue
        try:
            resolved = target.resolve()
            resolved.relative_to(LAB_ROOT)
        except (OSError, ValueError):
            errors.append(f"{relative}: link escapes repository: {raw_target}")
            continue
        if not resolved.exists():
            errors.append(f"{relative}: missing local link target: {raw_target}")

    return errors


def main() -> int:
    files = markdown_files()
    errors = [error for path in files for error in validate_file(path)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Documentation validation failed with {len(errors)} error(s).",
            file=sys.stderr,
        )
        return 1
    print(f"Documentation validation passed for {len(files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
