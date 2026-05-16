#!/usr/bin/env bash
# Online installer for AI-SDLC.
# Usage:
#   ./packaging/install_online.sh
#   ./packaging/install_online.sh /path/to/venv
#   ./packaging/install_online.sh --add-to-path
# Env:
#   AI_SDLC_PACKAGE_SPEC=ai-sdlc==0.7.16   optional package spec for pip install
#   PYTHON=/path/to/python3.11            optional interpreter override

set -euo pipefail

PACKAGE_SPEC="${AI_SDLC_PACKAGE_SPEC:-ai-sdlc}"
ADD_TO_PATH=0
POSITIONAL_VENV_TARGET=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --add-to-path)
      ADD_TO_PATH=1
      shift
      ;;
    *)
      if [[ -z "${POSITIONAL_VENV_TARGET}" ]]; then
        POSITIONAL_VENV_TARGET="$1"
      fi
      shift
      ;;
  esac
done
VENV_TARGET="${POSITIONAL_VENV_TARGET:-.venv}"

print_status() {
  local status_zh="$1"
  local status_en="$2"
  local command="$3"
  local purpose_zh="$4"
  local purpose_en="$5"
  echo "当前结果 / Result"
  echo "  ${status_zh}"
  echo "  ${status_en}"
  echo ""
  echo "下一步 / Next"
  echo "  ${command}"
  echo "  ${purpose_zh}"
  echo "  ${purpose_en}"
}

run_privileged() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    return 1
  fi
}

append_path_export_if_needed() {
  local bin_dir="$1"
  local shell_name
  local rc_file
  shell_name="${SHELL##*/}"
  case "${shell_name}" in
    zsh) rc_file="${HOME}/.zshrc" ;;
    bash) rc_file="${HOME}/.bashrc" ;;
    *) rc_file="${HOME}/.profile" ;;
  esac
  local export_line="export PATH=\"${bin_dir}:\$PATH\""
  if [[ -f "${rc_file}" ]]; then
    while IFS= read -r line; do
      if [[ "${line}" == *"${bin_dir}"* ]]; then
        return 0
      fi
    done < "${rc_file}"
  fi
  printf '\n# AI-SDLC CLI entrypoint\n%s\n' "${export_line}" >> "${rc_file}"
}

create_user_cli_link() {
  local user_bin="$1"
  local cli_path="$2"
  "${PYTHON_BIN}" - "${user_bin}" "${cli_path}" <<'PY'
from pathlib import Path
import os
import sys

user_bin = Path(os.path.expanduser(sys.argv[1]))
cli_path = Path(sys.argv[2]).resolve()
user_bin.mkdir(parents=True, exist_ok=True)
link = user_bin / "ai-sdlc"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(cli_path)
PY
}

pick_python() {
  if [[ -n "${PYTHON:-}" ]] && "${PYTHON}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    printf '%s' "${PYTHON}"
    return 0
  fi
  local candidate
  for candidate in python3.11 python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1 \
      && "${candidate}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
      printf '%s' "${candidate}"
      return 0
    fi
  done
  return 1
}

install_python() {
  local os_name
  os_name="$(uname -s)"
  case "${os_name}" in
    Darwin)
      if ! command -v brew >/dev/null 2>&1; then
        return 1
      fi
      brew install python@3.11
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        run_privileged apt-get update
        run_privileged apt-get install -y python3.11 python3.11-venv python3-pip
      elif command -v dnf >/dev/null 2>&1; then
        run_privileged dnf install -y python3.11 python3.11-pip
      elif command -v yum >/dev/null 2>&1; then
        run_privileged yum install -y python3.11 python3.11-pip
      else
        return 1
      fi
      ;;
    *)
      return 1
      ;;
  esac
}

if ! PYTHON_BIN="$(pick_python)"; then
  echo "No Python 3.11+ detected. Attempting online installation…"
  if ! install_python; then
    print_status \
      "当前主机未检测到 Python 3.11+，且无法自动完成在线安装。" \
      "Python 3.11+ was not detected, and online auto-install could not be completed on this host." \
      "./packaging/install_online.sh" \
      "在具备 Homebrew、apt、dnf 或 yum 权限的环境中重新执行此脚本。" \
      "Rerun this script on a host with Homebrew, apt, dnf, or yum privileges available."
    exit 1
  fi
  if ! PYTHON_BIN="$(pick_python)"; then
    print_status \
      "当前主机未检测到 Python 3.11+，且无法自动完成在线安装。" \
      "Python 3.11+ was not detected, and online auto-install could not be completed on this host." \
      "./packaging/install_online.sh" \
      "自动安装已执行，但当前 shell 还未发现可用的 Python 3.11+；请刷新环境后重试此脚本。" \
      "Automatic installation ran, but the current shell still cannot discover Python 3.11+; refresh the environment and rerun this script."
    exit 1
  fi
fi

echo "Using Python runtime: ${PYTHON_BIN}"
echo "Creating venv: ${VENV_TARGET}"
"${PYTHON_BIN}" -m venv "${VENV_TARGET}"
VENV_PYTHON="${VENV_TARGET}/bin/python"
"${VENV_PYTHON}" -m pip install -U pip >/dev/null
"${VENV_PYTHON}" -m pip install "${PACKAGE_SPEC}"

CLI_PATH="${VENV_TARGET}/bin/ai-sdlc"
VENV_PYTHON_DIR="${VENV_PYTHON%/*}"
VENV_PYTHON_BASE="${VENV_PYTHON##*/}"
RESOLVED_VENV_PYTHON="$(cd "${VENV_PYTHON_DIR}" && pwd)/${VENV_PYTHON_BASE}"
NEXT_COMMAND="cd <your-project> && \"${RESOLVED_VENV_PYTHON}\" -m ai_sdlc init ."
if [[ "${ADD_TO_PATH}" == "1" ]]; then
  USER_BIN="${HOME}/.local/bin"
  create_user_cli_link "${USER_BIN}" "${CLI_PATH}"
  append_path_export_if_needed "${USER_BIN}"
  export PATH="${USER_BIN}:${PATH}"
  NEXT_COMMAND="cd <your-project> && ai-sdlc init ."
fi

echo ""
print_status \
  "在线安装完成。安装脚本已创建运行环境并安装 AI-SDLC。" \
  "Online installation completed. The installer created the runtime and installed AI-SDLC." \
  "${NEXT_COMMAND}" \
  "进入你的项目后执行初始化；init 会自动完成必要检查和安全预演。" \
  "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."

if [[ "${ADD_TO_PATH}" == "1" ]]; then
  echo ""
  echo "PATH entry added: ${HOME}/.local/bin"
else
  echo ""
  echo "PATH was not changed. Rerun with --add-to-path to enable bare ai-sdlc commands."
fi
