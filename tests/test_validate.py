"""Tests for scripts/validate.py and scripts/build_adapters.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_adapters  # noqa: E402
import validate  # noqa: E402

VALID = """---
name: demo
description: Does a thing. Use when asked.
license: MIT
metadata:
  version: "1.0.0"
---

# Demo
"""


def make_skill(root: Path, name: str, text: str) -> Path:
    skill_dir = root / name
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
    return skill_dir


class FrontmatterTests(unittest.TestCase):
    def test_parses_scalars_and_nested_map(self) -> None:
        data, body, errors = validate.parse_frontmatter(VALID)
        self.assertEqual(errors, [])
        self.assertEqual(data["name"], "demo")
        self.assertEqual(data["metadata"], {"version": "1.0.0"})
        self.assertIn("# Demo", body)

    def test_requires_opening_marker(self) -> None:
        _, _, errors = validate.parse_frontmatter("name: demo\n")
        self.assertTrue(errors)

    def test_requires_closing_marker(self) -> None:
        _, _, errors = validate.parse_frontmatter("---\nname: demo\n")
        self.assertTrue(errors)


class SkillValidationTests(unittest.TestCase):
    def validate_text(self, name: str, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp), name, text)
            return [e for e in validate.validate_skill(skill_dir) if "catalog" not in e]

    def test_valid_skill_has_no_frontmatter_errors(self) -> None:
        self.assertEqual(self.validate_text("demo", VALID), [])

    def test_name_must_match_directory(self) -> None:
        errors = self.validate_text("other", VALID)
        self.assertTrue(any("must match directory" in e for e in errors))

    def test_rejects_uppercase_and_double_hyphen_names(self) -> None:
        for bad in ("Demo", "de--mo", "-demo"):
            errors = self.validate_text(bad, VALID.replace("name: demo", f"name: {bad}"))
            self.assertTrue(any("invalid name" in e for e in errors), bad)

    def test_description_length_limit(self) -> None:
        text = VALID.replace("Does a thing. Use when asked.", "x" * 1025)
        errors = self.validate_text("demo", text)
        self.assertTrue(any("description" in e for e in errors))

    def test_unknown_key_is_rejected(self) -> None:
        text = VALID.replace("license: MIT", "license: MIT\nargument-hint: foo")
        errors = self.validate_text("demo", text)
        self.assertTrue(any("unsupported frontmatter keys" in e for e in errors))

    def test_unlinked_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp), "demo", VALID)
            (skill_dir / "references" / "extra.md").write_text("x", encoding="utf-8")
            errors = validate.check_references_linked(skill_dir, "# Demo")
            self.assertTrue(any("references/extra.md" in e for e in errors))

    def test_prose_mention_does_not_count_as_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp), "demo", VALID)
            (skill_dir / "references" / "extra.md").write_text("x", encoding="utf-8")
            self.assertTrue(validate.check_references_linked(skill_dir, "see references/extra.md"))
            self.assertEqual(
                validate.check_references_linked(skill_dir, "[x](references/extra.md#a)"), []
            )


class LinkTests(unittest.TestCase):
    def test_detects_broken_relative_link_and_ignores_code_fences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok.md").write_text("hi", encoding="utf-8")
            (root / "index.md").write_text(
                "[ok](ok.md) [web](https://example.com) [anchor](#top)\n"
                "[missing](nope.md)\n"
                "```\n[ignored](also-missing.md)\n```\n",
                encoding="utf-8",
            )
            errors = validate.check_links(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("nope.md", errors[0])


class RepositoryTests(unittest.TestCase):
    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate.validate_repository(), [])

    def test_catalog_covers_every_required_code(self) -> None:
        self.assertEqual(validate.check_catalog(ROOT / "skills" / "clean-code"), [])

    def test_adapter_targets_are_generated_from_digest(self) -> None:
        body = build_adapters.SOURCE.read_text(encoding="utf-8").rstrip() + "\n"
        targets = build_adapters.targets(body)
        self.assertGreaterEqual(len(targets), 5)
        for content in targets.values():
            self.assertIn(body, content)


if __name__ == "__main__":
    unittest.main()
