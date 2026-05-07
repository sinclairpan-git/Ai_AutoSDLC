#!/usr/bin/env bash
# One-click offline install: run from inside the unpacked bundle directory.
# Usage:
#   ./install_offline.sh              # creates ./.venv and installs ai-sdlc
#   ./install_offline.sh /path/to/venv
#   ./install_offline.sh --upgrade-existing
# Env:
#   PYTHON=/path/to/python3.11  (optional override)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELS="${ROOT}/wheels"
MANIFEST="${ROOT}/bundle-manifest.json"
PYTHON_RUNTIME_ROOT="${ROOT}/python-runtime"
UPGRADE_EXISTING=0
if [[ "${1:-}" == "--upgrade-existing" ]]; then
  UPGRADE_EXISTING=1
  shift
fi

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

fail_install() {
  local message="$1"
  echo "error: ${message}" >&2
  print_status \
    "离线安装失败，请先修复当前阻塞项。" \
    "Offline installation failed. Resolve the current blocker first." \
    "./install_offline.sh" \
    "在修复问题后重新执行离线安装。" \
    "Rerun the offline installer after fixing the issue." >&2
  exit 1
}

if [[ ! -d "${WHEELS}" ]]; then
  fail_install "missing wheels/ next to this script (wrong directory?)"
fi

shopt -s nullglob
MAIN=( "${WHEELS}"/ai_sdlc-*.whl )
shopt -u nullglob

if [[ ${#MAIN[@]} -eq 0 ]]; then
  fail_install "no ai_sdlc-*.whl found under ${WHEELS}"
fi

if [[ ${#MAIN[@]} -gt 1 ]]; then
  fail_install "multiple ai_sdlc wheels found; keep only one version in wheels/"
fi

pick_python() {
  local candidate
  if [[ -n "${PYTHON:-}" ]]; then
    printf '%s' "${PYTHON}"
    return 0
  fi
  if [[ -x "${PYTHON_RUNTIME_ROOT}/bin/python3" ]]; then
    printf '%s' "${PYTHON_RUNTIME_ROOT}/bin/python3"
    return 0
  fi
  if [[ -x "${PYTHON_RUNTIME_ROOT}/bin/python" ]]; then
    printf '%s' "${PYTHON_RUNTIME_ROOT}/bin/python"
    return 0
  fi
  shopt -s nullglob
  for candidate in "${PYTHON_RUNTIME_ROOT}"/bin/python3.* "${PYTHON_RUNTIME_ROOT}"/bin/python*; do
    if [[ -x "${candidate}" && ! -d "${candidate}" ]]; then
      printf '%s' "${candidate}"
      shopt -u nullglob
      return 0
    fi
  done
  shopt -u nullglob
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    printf '%s' "python"
    return 0
  fi
  return 1
}

pick_existing_ai_sdlc_python() {
  local cli_path
  local target
  local dir
  local shebang
  local exec_line
  local interpreter
  if ! cli_path="$(command -v ai-sdlc 2>/dev/null)"; then
    return 1
  fi
  while [[ -L "${cli_path}" ]]; do
    target="$(readlink "${cli_path}")"
    dir="$(cd -P "$(dirname "${cli_path}")" >/dev/null 2>&1 && pwd)"
    if [[ "${target}" == /* ]]; then
      cli_path="${target}"
    else
      cli_path="${dir}/${target}"
    fi
  done
  if [[ ! -f "${cli_path}" ]]; then
    return 1
  fi
  if ! IFS= read -r shebang < "${cli_path}"; then
    return 1
  fi
  shebang="${shebang#\#!}"
  if [[ "${shebang}" == "/bin/sh" || "${shebang}" == "/usr/bin/sh" || "${shebang}" == *"/sh" ]]; then
    exec_line="$(sed -n "2s/^'''exec' //p" "${cli_path}" 2>/dev/null || true)"
    if [[ -z "${exec_line}" ]]; then
      return 1
    fi
    if [[ "${exec_line}" == \"* ]]; then
      interpreter="${exec_line#\"}"
      interpreter="${interpreter%%\"*}"
    else
      interpreter="${exec_line%% *}"
    fi
  else
    if [[ "${shebang}" == /usr/bin/env\ * ]]; then
      shebang="${shebang#/usr/bin/env }"
      if [[ "${shebang}" == -S\ * ]]; then
        shebang="${shebang#-S }"
      fi
    fi
    # shellcheck disable=SC2086
    set -- ${shebang}
    interpreter="${1:-}"
  fi
  if [[ -z "${interpreter}" ]]; then
    return 1
  fi
  if [[ -x "${interpreter}" ]]; then
    printf '%s' "${interpreter}"
    return 0
  fi
  if command -v "${interpreter}" >/dev/null 2>&1; then
    printf '%s' "${interpreter}"
    return 0
  fi
  return 1
}

if [[ "${UPGRADE_EXISTING}" == "1" ]]; then
  if ! PY="$(pick_existing_ai_sdlc_python)"; then
    fail_install "cannot find the Python runtime behind the current ai-sdlc command"
  fi
  echo "Using existing AI-SDLC runtime: ${PY}"
elif ! PY="$(pick_python)"; then
  fail_install "no usable Python runtime found. Bundle a python-runtime/ directory or set PYTHON=..."
elif [[ "${PY}" == "${PYTHON_RUNTIME_ROOT}"/bin/* ]]; then
  echo "Using bundled Python runtime: ${PY}"
else
  echo "Using detected system Python runtime: ${PY}"
fi

if ! "${PY}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  fail_install "need Python >= 3.11 (found ${PY})"
fi

if [[ -f "${MANIFEST}" ]]; then
  if ! "${PY}" - "${MANIFEST}" <<'PY'
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
expected_os = str(payload.get("platform_os", "")).strip().lower()
expected_machine = str(payload.get("platform_machine", "")).strip().lower()
current_os = platform.system().lower()
current_machine = platform.machine().lower()
wheel_python_version = str(payload.get("wheel_python_version", "")).strip()
current_python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

mismatches: list[str] = []
if expected_os and expected_os != current_os:
    mismatches.append(f"os={expected_os} (current={current_os})")
if expected_machine and expected_machine != current_machine:
    mismatches.append(f"machine={expected_machine} (current={current_machine})")
if wheel_python_version and wheel_python_version != current_python_version:
    mismatches.append(
        f"python={wheel_python_version} wheel ABI (selected={current_python_version})"
    )

if mismatches:
    raise SystemExit(
        "error: offline bundle platform mismatch: "
        + "; ".join(mismatches)
        + ". Rebuild the bundle on the target OS/CPU/Python ABI or use a matching archive."
    )
PY
  then
    exit 1
  fi
  echo "Validated offline bundle platform manifest."
else
  echo "warning: bundle-manifest.json missing; skipping platform compatibility check." >&2
fi

if [[ "${UPGRADE_EXISTING}" == "1" ]]; then
  WHEEL_NAME="$(basename "${MAIN[0]}")"
  EXPECTED_VERSION="${WHEEL_NAME#ai_sdlc-}"
  EXPECTED_VERSION="${EXPECTED_VERSION%%-*}"
  echo "Upgrading current ai-sdlc installation from this offline bundle..."
  if ! "${PY}" -m pip install --force-reinstall --no-index --find-links="${WHEELS}" "${MAIN[0]}"; then
    fail_install "failed to upgrade the current ai-sdlc installation"
  fi
  hash -r 2>/dev/null || true
  if ! INSTALLED_VERSION="$("${PY}" -c "from importlib.metadata import version; print(version('ai-sdlc'))" 2>/dev/null)"; then
    fail_install "upgraded runtime could not report the installed ai-sdlc version"
  fi
  if [[ "${INSTALLED_VERSION}" != "${EXPECTED_VERSION}" ]]; then
    fail_install "installed version is ${INSTALLED_VERSION}, expected ${EXPECTED_VERSION}"
  fi
  if ! ai-sdlc self-update install --help >/dev/null 2>&1; then
    fail_install "current PATH still resolves an older ai-sdlc command after installation"
  fi
  echo ""
  print_status \
    "升级完成。安装包已覆盖当前 ai-sdlc 入口对应的运行环境。" \
    "Upgrade completed. The package installer updated the runtime behind the current ai-sdlc command." \
    "ai-sdlc --version && ai-sdlc self-update check" \
    "确认版本；以后更新只执行 self-update check。" \
    "Confirm the version; future updates only need self-update check."
  exit 0
fi

VENV_TARGET="${1:-${ROOT}/.venv}"
echo "Creating venv: ${VENV_TARGET}"
"${PY}" -m venv "${VENV_TARGET}"

# shellcheck disable=SC1090
source "${VENV_TARGET}/bin/activate"

VENV_PYTHON="${VENV_TARGET}/bin/python"
if [[ ! -x "${VENV_PYTHON}" ]]; then
  fail_install "failed to create venv Python at ${VENV_PYTHON}"
fi

"${VENV_PYTHON}" -m pip install -U pip >/dev/null
echo "Installing ai-sdlc (offline)…"
"${VENV_PYTHON}" -m pip install --no-index --find-links="${WHEELS}" "${MAIN[0]}"

echo ""
print_status \
  "离线安装完成。安装脚本已创建运行环境并安装 AI-SDLC。" \
  "Offline installation completed. The installer created the runtime and installed AI-SDLC." \
  "source \"${VENV_TARGET}/bin/activate\" && cd <your-project> && ai-sdlc init ." \
  "进入你的项目后执行初始化；init 会自动完成必要检查和安全预演。" \
  "Enter your project and initialize it; init will automatically run the required checks and safe rehearsal."
