#!/usr/bin/env bash
# Smoke-test scripts/install.sh against a throwaway HOME and project directory.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="${ROOT}/scripts/install.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

export HOME="${WORK}/home"
PROJECT="${WORK}/project"
mkdir -p "${HOME}" "${PROJECT}"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_file() { [[ -f "$1" ]] || fail "expected file $1"; }
assert_missing() { [[ ! -e "$1" && ! -L "$1" ]] || fail "expected $1 to be absent"; }

# user scope, every target
"${INSTALL}" --tool all --scope user >/dev/null
for dir in .agents/skills .claude/skills .copilot/skills .config/opencode/skills \
  .gemini/skills .cursor/skills .codeium/windsurf/skills .config/agents/skills; do
  assert_file "${HOME}/${dir}/clean-code/SKILL.md"
  assert_file "${HOME}/${dir}/clean-code/references/catalog.md"
done

# second run skips, --force replaces
"${INSTALL}" --tool claude --scope user | grep -q '^skip:' || fail "expected skip on reinstall"
"${INSTALL}" --tool claude --scope user --force | grep -q '^installed:' || fail "force failed"

# uninstall
"${INSTALL}" --tool all --scope user --uninstall >/dev/null
assert_missing "${HOME}/.claude/skills/clean-code"
assert_missing "${HOME}/.agents/skills/clean-code"

# project scope with symlink
"${INSTALL}" --tool copilot,claude --scope project --project-dir "${PROJECT}" --method symlink >/dev/null
[[ -L "${PROJECT}/.github/skills/clean-code" ]] || fail "expected symlink in .github/skills"
assert_file "${PROJECT}/.claude/skills/clean-code/SKILL.md"

# refuses to touch a foreign directory
mkdir -p "${PROJECT}/other/clean-code"
echo "not ours" >"${PROJECT}/other/clean-code/SKILL.md"
if "${INSTALL}" --dest "${PROJECT}/other" --force >/dev/null 2>&1; then
  fail "overwrote a foreign skill"
fi
assert_file "${PROJECT}/other/clean-code/SKILL.md"

# dry run changes nothing
"${INSTALL}" --dest "${WORK}/dry" --dry-run >/dev/null
assert_missing "${WORK}/dry"

# bad input is rejected
if "${INSTALL}" --tool nope >/dev/null 2>&1; then fail "accepted unknown tool"; fi

printf 'install.sh: all checks passed\n'
