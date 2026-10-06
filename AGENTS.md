# AGENTS.md

Guidance for AI coding agents (and humans) working on this repository. For the contribution
workflow see [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repo is

The `clean-code` Agent Skill (`skills/clean-code/`), its Claude Code plugin manifests
(`.claude-plugin/`), generated rule-file adapters (`adapters/`), and the tooling that validates
and installs them (`scripts/`, `tests/`).

## Hard rules

- **Never reproduce the book.** No verbatim text, code, examples, figures, or chapter structure
  from *Clean Code*. Original wording, organized by topic. Rule codes and framework names are fine.
- **Keep the disclaimer** in `skills/clean-code/SKILL.md`, `README.md`, and `NOTICE.md` accurate.
- **Frontmatter portability.** `SKILL.md` frontmatter may use only `name`, `description`,
  `license`, `compatibility`, `metadata`, `allowed-tools`. The `name` must equal the directory name
  (`clean-code`). Keep the `description` under 1024 characters and rich in trigger words.
- **Every file in `skills/clean-code/references/` must be linked from `SKILL.md`.** Links are
  relative. `SKILL.md` stays under 500 lines.
- **Do not hand-edit generated files.** Edit `adapters/digest.md`, then run
  `python3 scripts/build_adapters.py`.
- **Keep versions in sync:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `metadata.version` in `SKILL.md`, and the top entry in `CHANGELOG.md`.
- **Catalog completeness.** `references/catalog.md` must keep a row for every code in C1-C5,
  E1-E2, F1-F4, G1-G36, N1-N7, and T1-T9.

## Commands

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
bash tests/test_install.sh
shellcheck scripts/*.sh tests/*.sh
```

Run all four before finishing a change. Update `CHANGELOG.md` under `Unreleased`.

## Style

- Markdown: ATX headings, one sentence per idea, tables for catalogs, fenced code with a language.
- Shell: Bash with `set -euo pipefail`, quoted expansions, ShellCheck clean.
- Python: standard library only, type hints, Python 3.9+.
