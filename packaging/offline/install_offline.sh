#!/usr/bin/env bash
# One-click offline install: run from inside the unpacked bundle directory.
# Usage:
#   ./install_offline.sh              # creates ./.venv and installs ai-sdlc
#   ./install_offline.sh /path/to/venv
# Env:
#   PYTHON=/path/to/python3.11  (optional; default: python3)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELS="${ROOT}/wheels"
MANIFEST="${ROOT}/bundle-manifest.json"

if [[ ! -d "${WHEELS}" ]]; then
  echo "error: missing wheels/ next to this script (wrong directory?)" >&2
  exit 1
fi

shopt -s nullglob
MAIN=( "${WHEELS}"/ai_sdlc-*.whl )
shopt -u nullglob

if [[ ${#MAIN[@]} -eq 0 ]]; then
  echo "error: no ai_sdlc-*.whl found under ${WHEELS}" >&2
  exit 1
fi

if [[ ${#MAIN[@]} -gt 1 ]]; then
  echo "error: multiple ai_sdlc wheels found; keep only one version in wheels/" >&2
  exit 1
fi

PY="${PYTHON:-python3}"
if ! command -v "${PY}" >/dev/null 2>&1; then
  echo "error: ${PY} not found. Install Python 3.11+ or set PYTHON=..." >&2
  exit 1
fi

if ! "${PY}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  echo "error: need Python >= 3.11 (found ${PY})" >&2
  exit 1
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

python -m pip install -U pip >/dev/null
echo "Installing ai-sdlc (offline)…"
pip install --no-index --find-links="${WHEELS}" "${MAIN[0]}"

echo ""
echo "OK. Verify:"
echo "  source \"${VENV_TARGET}/bin/activate\""
echo "  ai-sdlc --help"
echo "  cd /your/project && ai-sdlc init ."
