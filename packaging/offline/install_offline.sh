#!/usr/bin/env bash
# One-click offline install: run from inside the unpacked bundle directory.
# Usage:
#   ./install_offline.sh              # creates ./.venv and installs ai-sdlc
#   ./install_offline.sh /path/to/venv
# Env:
#   PYTHON=/path/to/python3.11  (optional override)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELS="${ROOT}/wheels"
MANIFEST="${ROOT}/bundle-manifest.json"
PYTHON_RUNTIME_ROOT="${ROOT}/python-runtime"

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

if ! PY="$(pick_python)"; then
  fail_install "no usable Python runtime found. Bundle a python-runtime/ directory or set PYTHON=..."
fi

if [[ "${PY}" == "${PYTHON_RUNTIME_ROOT}"/bin/* ]]; then
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

mismatches: list[str] = []
if expected_os and expected_os != current_os:
    mismatches.append(f"os={expected_os} (current={current_os})")
if expected_machine and expected_machine != current_machine:
    mismatches.append(f"machine={expected_machine} (current={current_machine})")

if mismatches:
    raise SystemExit(
        "error: offline bundle platform mismatch: "
        + "; ".join(mismatches)
        + ". Rebuild the bundle on the target OS/CPU or use a matching archive."
    )
PY
  then
    exit 1
  fi
  echo "Validated offline bundle platform manifest."
else
  echo "warning: bundle-manifest.json missing; skipping platform compatibility check." >&2
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
echo "OK. Verify:"
print_status \
  "离线安装完成，可以先验证 CLI，再进入项目执行启动预演。" \
  "Offline installation completed. Verify the CLI, then enter your project and run the startup rehearsal." \
  "source \"${VENV_TARGET}/bin/activate\" && ai-sdlc adapter status && ai-sdlc run --dry-run" \
  "激活 venv，检查 adapter 接入真值，再执行安全预演；run --dry-run 只证明 CLI 预演成功，不证明治理已激活。" \
  "Activate the venv, inspect adapter ingress truth, then run the safe rehearsal; run --dry-run only proves the CLI rehearsal succeeded, not governance activation."
