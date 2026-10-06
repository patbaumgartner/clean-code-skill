# Contributing

Thanks for helping make this skill better. This project is small on purpose: one skill, a few
reference files, and light tooling. Contributions that keep it focused are the most welcome.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions are
licensed under the [MIT License](LICENSE).

## Ways to contribute

- **Fix a wrong or unclear rule, example, or link.** Small pull requests are easy to review.
- **Improve a language guide** or add one for a language that has clear, widely used tooling.
- **Report a skill that does not trigger, triggers too often, or misbehaves** in a specific tool,
  with the tool and version. Use the bug report template.
- **Propose a new rule, workflow, or adapter** by opening an issue first so we can agree on scope.

## Ground rules

1. **Do not reproduce the book.** No verbatim text, code listings, figures, or examples from
   *Clean Code*, and no chapter-by-chapter structure. Restate ideas in your own words and organize
   by topic. Rule codes (`G5`, `F3`) and framework names (SRP, F.I.R.S.T.) are terminology and
   fine to use.
2. **Keep it portable.** `SKILL.md` frontmatter may only use `name`, `description`, `license`,
   `compatibility`, `metadata`, and `allowed-tools`. No tool-specific fields.
3. **Keep it lean.** `SKILL.md` stays under 500 lines (it is much shorter today). Put detail in
   `references/` and link it from `SKILL.md`; every reference file must be linked.
4. **Conventions beat dogma.** Guidance must tell the agent to follow project conventions and
   treat rules as heuristics.
5. **Be concrete and verifiable.** Prefer a symptom plus a remedy over abstract advice. Do not
   cite statistics or research you cannot link to a primary source.
6. **Keep file references relative** and one hop from `SKILL.md`.

## Development workflow

Requirements: Python 3.9+ and Bash. [ShellCheck](https://www.shellcheck.net/) is recommended.

```bash
git clone https://github.com/patbaumgartner/clean-code-skill.git
cd clean-code-skill

python3 scripts/validate.py              # frontmatter, links, catalog, versions, adapters
python3 -m unittest discover -s tests    # unit tests
bash tests/test_install.sh               # installer smoke test
shellcheck scripts/*.sh tests/*.sh       # shell lint
```

If you edit [adapters/digest.md](adapters/digest.md), regenerate the adapters:

```bash
python3 scripts/build_adapters.py
```

Never edit files under `adapters/` other than `digest.md`; CI fails when they drift.

### Testing a change against a real agent

1. Install your working copy by symlink: `./scripts/install.sh --tool <tool> --method symlink --force`.
2. Start a fresh session and ask for something the skill should handle, for example "Review this
   file with the clean-code skill".
3. Confirm it activates, loads the right reference, and cites rule codes. If you changed the
   `description`, also test a prompt that should *not* trigger it.

## Pull requests

- Keep each pull request to one topic.
- Update [CHANGELOG.md](CHANGELOG.md) under `Unreleased`.
- Fill in the pull request template, including which tool(s) you tested with.
- CI must be green. Maintainers may ask for wording changes to keep the skill consistent.

### Commit messages

Use short, imperative subjects (for example `Add Swift language guide`). Conventional Commit
prefixes are welcome but not required.

## Releasing (maintainers)

1. Move `Unreleased` notes under a new version heading in `CHANGELOG.md`.
2. Bump the version in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and
   `metadata.version` in `skills/clean-code/SKILL.md`. `validate.py` fails if they disagree.
3. Run all checks, commit, and tag: `git tag -s vX.Y.Z`; `git push origin main vX.Y.Z`.
4. The release workflow builds the archive and publishes the GitHub release.

Versioning: removing or renaming a rule code or the skill name is major; new rules, guides, or
workflow changes are minor; fixes and wording are patch.
