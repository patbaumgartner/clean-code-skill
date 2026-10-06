# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions apply to the skill content and tooling. Changes to rule wording, workflows, or the
frontmatter `description` (which affects activation) count as minor or patch releases; removing
or renaming a rule code or the skill name is a major release.

## [Unreleased]

## [1.0.0] - 2026-10-06

### Added

- `clean-code` skill following the Agent Skills specification, with a core checklist, operating
  rules, and mode routing for writing, reviewing, refactoring, and explaining code.
- Reference library: smell and heuristic catalog (C, E, F, G, N, T), principles, patterns,
  glossary, review workflow, refactoring workflow, and AI-assisted coding guardrails.
- Language guides for Python, TypeScript/JavaScript, Java, Kotlin, Go, Rust, and C#.
- Claude Code plugin and marketplace manifests.
- Generated rule-file adapters for `AGENTS.md`, GitHub Copilot instructions, Cursor, Windsurf,
  Cline, and Aider.
- Installer script for Claude Code, GitHub Copilot, OpenCode, Codex, Gemini CLI, Cursor,
  Windsurf, and Amp, with copy and symlink modes.
- Validation script, unit tests, installer smoke test, and CI and release workflows.

[Unreleased]: https://github.com/patbaumgartner/clean-code-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/patbaumgartner/clean-code-skill/releases/tag/v1.0.0
