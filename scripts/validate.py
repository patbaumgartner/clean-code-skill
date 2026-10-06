#!/usr/bin/env python3
"""Validate the skill, plugin manifests, adapters, links, and version consistency.

Usage:
    python3 scripts/validate.py

Exits with status 1 and prints every problem when validation fails. Uses only the standard
library so it runs anywhere Python 3.9+ is installed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import build_adapters

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CHANGELOG_VERSION_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)
MAX_BODY_LINES = 500

REQUIRED_CODES = (
    [f"C{i}" for i in range(1, 6)]
    + [f"E{i}" for i in range(1, 3)]
    + [f"F{i}" for i in range(1, 5)]
    + [f"G{i}" for i in range(1, 37)]
    + [f"N{i}" for i in range(1, 8)]
    + [f"T{i}" for i in range(1, 10)]
)


def parse_frontmatter(text: str) -> tuple[dict, str, list[str]]:
    """Parse the small YAML subset used by SKILL.md: scalars and one nested string map."""
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["SKILL.md must start with a '---' frontmatter line"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, text, ["frontmatter is not closed with '---'"]

    data: dict = {}
    current_map: str | None = None
    for number, raw in enumerate(lines[1:end], start=2):
        if not raw.strip():
            continue
        indented = raw.startswith("  ")
        if indented and current_map is not None:
            key, sep, value = raw.strip().partition(":")
            if not sep:
                errors.append(f"frontmatter line {number}: expected 'key: value'")
                continue
            data[current_map][key.strip()] = _unquote(value.strip())
            continue
        key, sep, value = raw.partition(":")
        if not sep or indented:
            errors.append(f"frontmatter line {number}: expected 'key: value'")
            continue
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = {}
            current_map = key
        else:
            data[key] = _unquote(value)
            current_map = None
    body = "\n".join(lines[end + 1 :])
    return data, body, errors


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]

    data, body, parse_errors = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    errors += [f"{skill_file}: {e}" for e in parse_errors]
    errors += check_frontmatter(skill_dir, data)

    body_lines = len(body.splitlines())
    if body_lines > MAX_BODY_LINES:
        errors.append(f"{skill_file}: body has {body_lines} lines (limit {MAX_BODY_LINES})")

    errors += check_references_linked(skill_dir, body)
    errors += check_catalog(skill_dir)
    return errors


def check_frontmatter(skill_dir: Path, data: dict) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"

    unknown = set(data) - ALLOWED_KEYS
    if unknown:
        errors.append(f"{skill_file}: unsupported frontmatter keys {sorted(unknown)}")

    name = data.get("name", "")
    if not isinstance(name, str) or not name:
        errors.append(f"{skill_file}: 'name' is required")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            errors.append(f"{skill_file}: invalid name {name!r}")
        if name != skill_dir.name:
            errors.append(f"{skill_file}: name {name!r} must match directory {skill_dir.name!r}")

    description = data.get("description", "")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append(f"{skill_file}: description must be 1-1024 characters")

    compatibility = data.get("compatibility", "")
    if isinstance(compatibility, str) and len(compatibility) > 500:
        errors.append(f"{skill_file}: compatibility must be at most 500 characters")

    if not isinstance(data.get("metadata", {}), dict):
        errors.append(f"{skill_file}: metadata must be a map of strings")
    return errors


def check_references_linked(skill_dir: Path, body: str) -> list[str]:
    """Every file under references/ must be a link target in SKILL.md."""
    references = skill_dir / "references"
    if not references.is_dir():
        return []
    linked = {_link_path(target) for target in LINK_RE.findall(body)}
    return [
        f"{skill_dir / 'SKILL.md'}: does not link {relative}"
        for path in sorted(references.rglob("*"))
        if path.is_file()
        and (relative := path.relative_to(skill_dir).as_posix()) not in linked
    ]


def _link_path(target: str) -> str:
    path = target.split("#", 1)[0].split("?", 1)[0]
    return path.removeprefix("./")


def check_catalog(skill_dir: Path) -> list[str]:
    catalog = skill_dir / "references" / "catalog.md"
    if not catalog.is_file():
        return [f"{catalog}: missing"]
    text = catalog.read_text(encoding="utf-8")
    present = set(re.findall(r"^\| ([A-Z]\d+) \|", text, flags=re.MULTILINE))
    return [f"{catalog}: missing rule {code}" for code in REQUIRED_CODES if code not in present]


def iter_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        yield path


def check_links(root: Path) -> list[str]:
    """Verify relative Markdown links resolve to existing files."""
    errors: list[str] = []
    for path in iter_markdown(root):
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith("```") or line.lstrip().startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK_RE.findall(re.sub(r"`[^`]*`", "", line)):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                file_part = _link_path(target)
                if file_part and not (path.parent / file_part).resolve().exists():
                    errors.append(f"{path.relative_to(root)}:{number}: broken link {target}")
    return errors


def load_json(root: Path, path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(root)}: {exc}")
        return {}


def check_versions(root: Path) -> list[str]:
    """plugin.json, marketplace.json, SKILL.md metadata, and CHANGELOG must agree."""
    errors: list[str] = []
    versions: dict[str, str] = {}

    plugin = load_json(root, root / ".claude-plugin" / "plugin.json", errors)
    versions["plugin.json"] = plugin.get("version", "")

    marketplace = load_json(root, root / ".claude-plugin" / "marketplace.json", errors)
    plugins = marketplace.get("plugins", [])
    versions["marketplace.json"] = plugins[0].get("version", "") if plugins else ""

    skill_file = root / "skills" / "clean-code" / "SKILL.md"
    data, _, _ = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    metadata = data.get("metadata", {})
    versions["SKILL.md metadata.version"] = (
        metadata.get("version", "") if isinstance(metadata, dict) else ""
    )

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = CHANGELOG_VERSION_RE.search(changelog)
    versions["CHANGELOG.md"] = match.group(1) if match else ""

    if len(set(versions.values())) != 1 or "" in versions.values():
        details = ", ".join(f"{k}={v or '?'}" for k, v in versions.items())
        errors.append(f"version mismatch: {details}")
    return errors


def check_adapters(root: Path) -> list[str]:
    body = build_adapters.SOURCE.read_text(encoding="utf-8").rstrip() + "\n"
    return [
        f"{path.relative_to(root)}: out of date (run scripts/build_adapters.py)"
        for path in build_adapters.stale_targets(body)
    ]


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    skill_dirs = sorted(p for p in (root / "skills").iterdir() if p.is_dir())
    if not skill_dirs:
        errors.append("skills/: no skills found")
    for skill_dir in skill_dirs:
        errors += validate_skill(skill_dir)
    errors += check_links(root)
    errors += check_versions(root)
    errors += check_adapters(root)
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found", file=sys.stderr)
        return 1
    print("ok: skill, manifests, links, versions, and adapters are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
