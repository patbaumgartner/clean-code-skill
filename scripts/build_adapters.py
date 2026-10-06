#!/usr/bin/env python3
"""Generate tool-specific rule files from adapters/digest.md.

Skill-aware agents should install the skill itself. These adapters cover tools that only read
rule or instruction files (AGENTS.md, Copilot instructions, Cursor, Windsurf, Cline, Aider).

Usage:
    python3 scripts/build_adapters.py          # write the generated files
    python3 scripts/build_adapters.py --check  # fail if they are out of date
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "adapters" / "digest.md"
DESCRIPTION = "Clean Code rules: naming, functions, comments, errors, structure, tests."

HEADER = "<!-- Generated from adapters/digest.md by scripts/build_adapters.py. Do not edit. -->"


def _plain(body: str) -> str:
    return f"{HEADER}\n\n{body}"


def _with_frontmatter(frontmatter: str, body: str) -> str:
    return f"---\n{frontmatter}\n---\n{HEADER}\n\n{body}"


def targets(body: str) -> dict[Path, str]:
    adapters = ROOT / "adapters"
    return {
        adapters / "agents-md" / "AGENTS.md": _plain(body),
        adapters / "github-copilot" / "clean-code.instructions.md": _with_frontmatter(
            'applyTo: "**"', body
        ),
        adapters / "cursor" / "clean-code.mdc": _with_frontmatter(
            f"description: {DESCRIPTION}\nglobs:\nalwaysApply: true", body
        ),
        adapters / "windsurf" / "clean-code.md": _with_frontmatter("trigger: always_on", body),
        adapters / "cline" / "clean-code.md": _plain(body),
        adapters / "aider" / "CONVENTIONS.md": _plain(body),
    }


def stale_targets(body: str) -> dict[Path, str]:
    return {
        path: content
        for path, content in targets(body).items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()

    body = SOURCE.read_text(encoding="utf-8").rstrip() + "\n"
    stale = stale_targets(body)

    if args.check:
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}", file=sys.stderr)
        if stale:
            print("run: python3 scripts/build_adapters.py", file=sys.stderr)
            return 1
        print("adapters are up to date")
        return 0

    for path, content in stale.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
