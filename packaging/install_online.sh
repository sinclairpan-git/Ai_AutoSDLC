#!/usr/bin/env bash
# Online installer for AI-SDLC.
# Usage:
#   ./packaging/install_online.sh
#   ./packaging/install_online.sh /path/to/venv
# Env:
#   AI_SDLC_PACKAGE_SPEC=ai-sdlc==0.7.6   optional package spec for pip install
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

echo ""
print_status \
  "在线安装完成。安装脚本已创建运行环境并安装 AI-SDLC。" \
  "Online installation completed. The installer created the runtime and installed AI-SDLC." \
  "source \"${VENV_TARGET}/bin/activate\" && cd <your-project> && ai-sdlc init ." \
  "进入你的项目后执行初始化；init 会自动完成必要检查和安全预演。" \
  "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
