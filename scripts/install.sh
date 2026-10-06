#!/usr/bin/env bash
# Install the clean-code skill into the skills directory of one or more AI coding tools.
#
#   scripts/install.sh --tool claude,copilot --scope user
#   scripts/install.sh --tool agents --scope project
#   scripts/install.sh --dest ~/my-skills
#
# Run scripts/install.sh --help for all options.

set -euo pipefail

SKILL_NAME="clean-code"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/../skills/${SKILL_NAME}" && pwd)"

TOOLS="agents"
SCOPE="user"
METHOD="copy"
DEST=""
PROJECT_DIR="${PWD}"
ACTION="install"
FORCE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: install.sh [options]

Options:
  -t, --tool <list>      Comma-separated targets (default: agents)
                           agents    universal .agents/skills (Copilot, OpenCode, Codex,
                                     Gemini CLI, Cursor, Amp)
                           claude    Claude Code
                           copilot   GitHub Copilot (VS Code, CLI, cloud agent)
                           opencode  OpenCode
                           codex     OpenAI Codex
                           gemini    Gemini CLI
                           cursor    Cursor
                           windsurf  Windsurf
                           amp       Amp
                           all       every target above
  -s, --scope <scope>    user (default) or project
  -p, --project-dir <d>  Project root for --scope project (default: current directory)
  -d, --dest <dir>       Install into <dir>/clean-code, ignoring --tool and --scope
  -m, --method <method>  copy (default) or symlink (updates with git pull)
  -f, --force            Replace an existing installation
  -u, --uninstall        Remove the skill instead of installing it
  -n, --dry-run          Print what would happen without changing anything
  -l, --list             Show the install location of every target and exit
  -h, --help             Show this help
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

skills_dir() {
  local tool="$1" scope="$2"
  case "${scope}:${tool}" in
    user:agents | user:codex) printf '%s\n' "${HOME}/.agents/skills" ;;
    user:claude) printf '%s\n' "${HOME}/.claude/skills" ;;
    user:copilot) printf '%s\n' "${HOME}/.copilot/skills" ;;
    user:opencode) printf '%s\n' "${HOME}/.config/opencode/skills" ;;
    user:gemini) printf '%s\n' "${HOME}/.gemini/skills" ;;
    user:cursor) printf '%s\n' "${HOME}/.cursor/skills" ;;
    user:windsurf) printf '%s\n' "${HOME}/.codeium/windsurf/skills" ;;
    user:amp) printf '%s\n' "${HOME}/.config/agents/skills" ;;
    project:agents | project:codex | project:amp) printf '%s\n' "${PROJECT_DIR}/.agents/skills" ;;
    project:claude) printf '%s\n' "${PROJECT_DIR}/.claude/skills" ;;
    project:copilot) printf '%s\n' "${PROJECT_DIR}/.github/skills" ;;
    project:opencode) printf '%s\n' "${PROJECT_DIR}/.opencode/skills" ;;
    project:gemini) printf '%s\n' "${PROJECT_DIR}/.gemini/skills" ;;
    project:cursor) printf '%s\n' "${PROJECT_DIR}/.cursor/skills" ;;
    project:windsurf) printf '%s\n' "${PROJECT_DIR}/.windsurf/skills" ;;
    *) return 1 ;;
  esac
}

ALL_TOOLS="agents claude copilot opencode codex gemini cursor windsurf amp"

is_ours() {
  local dir="$1"
  [[ -f "${dir}/SKILL.md" ]] && grep -q "^name: ${SKILL_NAME}\$" "${dir}/SKILL.md"
}

run() {
  if ((DRY_RUN)); then
    printf '[dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

install_into() {
  local base="$1" target="${1}/${SKILL_NAME}"
  if [[ -e "${target}" || -L "${target}" ]]; then
    if ((FORCE)); then
      if [[ -L "${target}" ]] || is_ours "${target}"; then
        run rm -rf "${target}"
      else
        die "${target} exists and is not this skill; refusing to overwrite"
      fi
    else
      printf 'skip: %s already exists (use --force to replace)\n' "${target}"
      return 0
    fi
  fi
  run mkdir -p "${base}"
  if [[ "${METHOD}" == "symlink" ]]; then
    run ln -s "${SOURCE_DIR}" "${target}"
  else
    run cp -R "${SOURCE_DIR}" "${target}"
  fi
  printf 'installed: %s (%s)\n' "${target}" "${METHOD}"
}

uninstall_from() {
  local target="${1}/${SKILL_NAME}"
  if [[ ! -e "${target}" && ! -L "${target}" ]]; then
    printf 'skip: nothing at %s\n' "${target}"
    return 0
  fi
  if [[ -L "${target}" ]] || is_ours "${target}"; then
    run rm -rf "${target}"
    printf 'removed: %s\n' "${target}"
  else
    die "${target} is not this skill; refusing to delete"
  fi
}

list_targets() {
  local tool
  printf '%-10s %-45s %s\n' "TARGET" "USER SCOPE" "PROJECT SCOPE"
  for tool in ${ALL_TOOLS}; do
    printf '%-10s %-45s %s\n' "${tool}" "$(skills_dir "${tool}" user)" "$(skills_dir "${tool}" project)"
  done
}

while (($#)); do
  case "$1" in
    -t | --tool) TOOLS="${2:?--tool needs a value}"; shift 2 ;;
    -s | --scope) SCOPE="${2:?--scope needs a value}"; shift 2 ;;
    -p | --project-dir) PROJECT_DIR="${2:?--project-dir needs a value}"; shift 2 ;;
    -d | --dest) DEST="${2:?--dest needs a value}"; shift 2 ;;
    -m | --method) METHOD="${2:?--method needs a value}"; shift 2 ;;
    -f | --force) FORCE=1; shift ;;
    -u | --uninstall) ACTION="uninstall"; shift ;;
    -n | --dry-run) DRY_RUN=1; shift ;;
    -l | --list) list_targets; exit 0 ;;
    -h | --help) usage; exit 0 ;;
    *) usage >&2; die "unknown option: $1" ;;
  esac
done

[[ "${SCOPE}" == "user" || "${SCOPE}" == "project" ]] || die "--scope must be user or project"
[[ "${METHOD}" == "copy" || "${METHOD}" == "symlink" ]] || die "--method must be copy or symlink"
[[ -f "${SOURCE_DIR}/SKILL.md" ]] || die "cannot find ${SOURCE_DIR}/SKILL.md"

declare -a bases=()
add_base() {
  local candidate="$1" existing
  if ((${#bases[@]})); then
    for existing in "${bases[@]}"; do
      [[ "${existing}" == "${candidate}" ]] && return 0
    done
  fi
  bases+=("${candidate}")
}

if [[ -n "${DEST}" ]]; then
  add_base "${DEST}"
else
  [[ "${TOOLS}" == "all" ]] && TOOLS="${ALL_TOOLS// /,}"
  IFS=',' read -r -a requested <<<"${TOOLS}"
  for tool in "${requested[@]}"; do
    base="$(skills_dir "${tool}" "${SCOPE}")" || die "unknown tool: ${tool}"
    add_base "${base}"
  done
fi

for base in "${bases[@]}"; do
  if [[ "${ACTION}" == "install" ]]; then
    install_into "${base}"
  else
    uninstall_from "${base}"
  fi
done
