#!/usr/bin/env bash
# Online installer for AI-SDLC.
# Usage:
#   ./packaging/install_online.sh
#   ./packaging/install_online.sh /path/to/venv
# Env:
#   AI_SDLC_PACKAGE_SPEC=ai-sdlc==0.6.0   optional package spec for pip install
#   PYTHON=/path/to/python3.11            optional interpreter override

set -euo pipefail

VENV_TARGET="${1:-.venv}"
PACKAGE_SPEC="${AI_SDLC_PACKAGE_SPEC:-ai-sdlc}"

print_status() {
  local status_zh="$1"
  local status_en="$2"
  local command="$3"
  local purpose_zh="$4"
  local purpose_en="$5"
  echo "当前状态 / Current status"
  echo "  ${status_zh}"
  echo "  ${status_en}"
  echo ""
  echo "下一步命令 / Next command"
  echo "  ${command}"
  echo ""
  echo "命令作用 / What this command does"
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
  PYTHON_BIN="$(pick_python)"
fi

echo "Using Python runtime: ${PYTHON_BIN}"
echo "Creating venv: ${VENV_TARGET}"
"${PYTHON_BIN}" -m venv "${VENV_TARGET}"
VENV_PYTHON="${VENV_TARGET}/bin/python"
"${VENV_PYTHON}" -m pip install -U pip >/dev/null
"${VENV_PYTHON}" -m pip install "${PACKAGE_SPEC}"

echo ""
print_status \
  "在线安装完成，可以进入项目检查 adapter 接入真值并执行安全预演。" \
  "Online installation completed. Enter your project, inspect adapter ingress truth, and run the safe rehearsal." \
  "source \"${VENV_TARGET}/bin/activate\" && ai-sdlc adapter status && ai-sdlc run --dry-run" \
  "激活 venv，检查 adapter 接入真值，再执行安全预演；run --dry-run 只证明 CLI 预演成功，不证明治理已激活。" \
  "Activate the venv, inspect adapter ingress truth, then run the safe rehearsal; run --dry-run only proves the CLI rehearsal succeeded, not governance activation."

