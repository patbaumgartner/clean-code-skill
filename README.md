# clean-code-skill

[![CI](https://github.com/patbaumgartner/clean-code-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/patbaumgartner/clean-code-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-6f42c1.svg)](https://agentskills.io/specification)

One [Agent Skill](https://agentskills.io/specification) that teaches your AI coding agent to
write, review, and refactor code the clean-code way. Install it once and use it in Claude Code,
GitHub Copilot, OpenCode, Codex, Gemini CLI, Cursor, Windsurf, Amp, and any other tool that
supports the open skill format. Tools that only read rule files get a ready-made adapter.

AI writes code fast, and it is just as fast at producing duplication, vague names, swallowed
errors, and weakened tests. This skill gives the agent a shared vocabulary (`G5`, `F3`, `N1`)
and a disciplined workflow so changes stay small, honest, and reviewable.

## What you get

- **Core checklist** the agent applies while writing code, with project conventions and
  linters always winning over generic rules.
- **Named smell catalog**: C1-C5, E1-E2, F1-F4, G1-G36, N1-N7, T1-T9, with symptom and remedy.
- **Review workflow** that produces a prioritized report (Blocker, Major, Minor, Nit) citing rule
  codes and `path:line` locations.
- **Refactoring workflow**: small, test-protected steps, one smell at a time.
- **Language guides** for Python, TypeScript/JavaScript, Java, Kotlin, Go, Rust, and C#, covering
  tooling and where idioms override the generic rules.
- **AI-assisted coding guardrails** against re-implementing helpers, sweeping diffs, invented
  APIs, and muted checks.
- **Progressive disclosure**: a short `SKILL.md` loads on activation; the catalog, patterns, and
  language guides load only when needed.

## Install

Pick the route that fits your setup. All routes install the same `clean-code` skill.

### Any tool: `npx skills`

```bash
npx skills add patbaumgartner/clean-code-skill
```

The [`skills`](https://github.com/vercel-labs/skills) CLI detects the agents on your machine and
installs into the right directories. Add `-g` for a global install.

### Installer script

```bash
git clone https://github.com/patbaumgartner/clean-code-skill.git
cd clean-code-skill

# user-wide, for specific tools
./scripts/install.sh --tool claude,copilot,opencode

# user-wide, every supported tool
./scripts/install.sh --tool all

# into the current project (commit it to share with your team)
./scripts/install.sh --tool agents,claude,copilot --scope project

# symlink instead of copy, so `git pull` updates it
./scripts/install.sh --tool all --method symlink

./scripts/install.sh --list        # show every location
./scripts/install.sh --uninstall --tool all
```

The script runs on Linux, macOS, and Windows through WSL or Git Bash. It never overwrites a
directory that is not this skill, and `--dry-run` previews every action.

### Claude Code plugin

```text
/plugin marketplace add patbaumgartner/clean-code-skill
/plugin install clean-code@clean-code-skill
```

### Gemini CLI

```bash
gemini skills install https://github.com/patbaumgartner/clean-code-skill.git --path skills/clean-code
```

### Manual copy

Copy `skills/clean-code/` into the skills directory of your tool, so that the result is
`<skills-dir>/clean-code/SKILL.md`.

| Tool | Project scope | User scope |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| GitHub Copilot (VS Code, CLI, cloud agent) | `.github/skills/` (also `.claude/skills/`, `.agents/skills/`) | `~/.copilot/skills/` (also `~/.claude/skills/`, `~/.agents/skills/`) |
| OpenCode | `.opencode/skills/` (also `.claude/skills/`, `.agents/skills/`) | `~/.config/opencode/skills/` (also `~/.claude/skills/`, `~/.agents/skills/`) |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` |
| Cursor | `.cursor/skills/` or `.agents/skills/` | `~/.cursor/skills/` or `~/.agents/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Amp | `.agents/skills/` | `~/.config/agents/skills/` |

`.agents/skills/` is the most portable choice: Copilot, OpenCode, Codex, Gemini CLI, Cursor, and
Amp all read it. Claude Code reads `.claude/skills/`, which most other tools also accept. Tool
vendors change locations from time to time; check your tool's documentation if a skill does not
show up.

### Tools without skill support

Some tools only read rule files. Copy the matching generated adapter into your project:

| Tool | Adapter | Destination |
| --- | --- | --- |
| Codex, OpenCode, Amp, Copilot, Cursor, and others that read `AGENTS.md` | [adapters/agents-md/AGENTS.md](adapters/agents-md/AGENTS.md) | `AGENTS.md` (append if one exists) |
| GitHub Copilot instructions | [adapters/github-copilot/clean-code.instructions.md](adapters/github-copilot/clean-code.instructions.md) | `.github/instructions/` |
| Cursor rules | [adapters/cursor/clean-code.mdc](adapters/cursor/clean-code.mdc) | `.cursor/rules/` |
| Windsurf rules | [adapters/windsurf/clean-code.md](adapters/windsurf/clean-code.md) | `.windsurf/rules/` |
| Cline | [adapters/cline/clean-code.md](adapters/cline/clean-code.md) | `.clinerules/` |
| Aider | [adapters/aider/CONVENTIONS.md](adapters/aider/CONVENTIONS.md) | project root, then `aider --read CONVENTIONS.md` |

Adapters carry only the condensed rules. The skill adds the catalog, language guides, and the
review and refactor workflows, so prefer the skill wherever it is supported.

## Use it

The skill activates on its own when you write, review, or refactor code. You can also invoke it
explicitly:

| Tool | Explicit invocation |
| --- | --- |
| Claude Code, GitHub Copilot, Cursor | `/clean-code review src/billing` |
| OpenAI Codex | `$clean-code review src/billing` |
| OpenCode, Gemini CLI, others | Ask in plain language: "Use the clean-code skill to review src/billing" |

Example prompts:

- "Review this diff with the clean-code skill. Blockers and Majors only."
- "Refactor `OrderService` for G30 and G14. Do not change behavior; run the tests."
- "Explain smell G36 with an example in Go."
- "Do a Boy Scout pass on the files you just edited."

Sample output of a review:

```markdown
## Clean-code review: src/billing

**Verdict:** ship after fixes

### Blocker
- **G4 - muted test** - `tests/test_billing.py:42`: `@skip` hides a failing rounding case.
  Fix the cause or delete the test with a reason.

### Major
- **G5 - duplication** - `invoice.py:18-31` and `credit_note.py:22-35` compute tax identically.
  Extract `apply_tax(amount, region)`.

### Done well
- The payment gateway adapter keeps vendor types out of the domain.
```

## How it works

```text
skills/clean-code/
├── SKILL.md                      # activation: rules, modes, checklist (loads first)
└── references/                   # loaded on demand
    ├── catalog.md                # every smell and heuristic code
    ├── principles.md             # the underlying frameworks
    ├── patterns.md               # when / how / trade-offs for common techniques
    ├── glossary.md
    ├── review.md                 # review workflow and report format
    ├── refactor.md               # safe refactoring workflow
    ├── ai-assisted-coding.md     # guardrails for agent-written code
    └── languages/                # python, typescript, java, kotlin, go, rust, csharp
```

The skill follows the Agent Skills open standard: frontmatter limited to `name`, `description`,
`license`, `compatibility`, and `metadata`, so it loads in strict validators and in every
compatible tool. Skill-specific extras such as Claude Code's `disable-model-invocation` are
deliberately omitted to stay portable.

## Customize

- **Your team's rules:** add a short `references/team-standards.md`, link it from `SKILL.md`, and
  say when to read it. Keep your conventions out of the generic catalog.
- **Only the parts you want:** the language guides are independent. Delete the ones you do not
  use and remove their rows from the `SKILL.md` table.
- **Always-on rules:** if you want the rules in every prompt rather than on demand, use an adapter
  from the table above in addition to the skill.

## FAQ

**Why one skill instead of many small ones?** Many tools share one skill namespace and a
description budget. One focused skill with progressive disclosure costs less context and cannot
conflict with itself.

**Does it reproduce the book?** No. It restates named principles and heuristic codes in original,
condensed wording and is organized by topic. See [NOTICE.md](NOTICE.md).

**What if my project's style disagrees with a rule?** The project wins. The skill tells the agent
to match existing conventions and to explain deliberate exceptions in one line.

**Will it rewrite my whole codebase?** No. The scope rule limits cleanup to code the task touches,
and the refactor workflow works in small, verified steps.

## Development

```bash
python3 scripts/validate.py                # frontmatter, links, catalog, versions, adapters
python3 -m unittest discover -s tests      # unit tests
bash tests/test_install.sh                 # installer smoke test
python3 scripts/build_adapters.py          # regenerate adapters after editing adapters/digest.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and
[CHANGELOG.md](CHANGELOG.md) for release notes.

## License

[MIT](LICENSE) © 2026 Patrick Baumgartner
