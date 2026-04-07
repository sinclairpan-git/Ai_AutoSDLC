#!/usr/bin/env bash
# Run on a machine WITH internet access (same OS/arch as targets when possible).
# Produces:
#   - dist-offline/ai-sdlc-offline-<version>.tar.gz
#   - dist-offline/ai-sdlc-offline-<version>.zip
#
# Usage:
#   ./packaging/offline/build_offline_bundle.sh
# Env:
#   PYTHON=/path/to/python3.11   interpreter used for pip download (default: try python3.11, then python3)
#   OFFLINE_BUNDLE_ZIP=0         skip creating the .zip archive (default: create both .tar.gz and .zip)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT}"

VERSION="$(awk -F'"' '/^version =/ {print $2; exit}' pyproject.toml)"
OUT="${ROOT}/dist-offline/ai-sdlc-offline-${VERSION}"
ARCHIVE="${ROOT}/dist-offline/ai-sdlc-offline-${VERSION}.tar.gz"
ZIP_ARCHIVE="${ROOT}/dist-offline/ai-sdlc-offline-${VERSION}.zip"
MANIFEST="${OUT}/bundle-manifest.json"
BUILD_ZIP="${OFFLINE_BUNDLE_ZIP:-1}"

_pick_py() {
  local c
  for c in "$@"; do
    if "${c}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null \
      && "${c}" -m pip --version >/dev/null 2>&1; then
      printf '%s' "${c}"
      return 0
    fi
  done
  return 1
}

if [[ -n "${PYTHON:-}" ]]; then
  if ! PY="$(_pick_py "${PYTHON}")"; then
    echo "error: PYTHON=${PYTHON} must be Python >= 3.11 with pip (for pip download step)" >&2
    exit 1
  fi
else
  if ! PY="$(_pick_py python3.11 python3)"; then
    echo "error: need Python >= 3.11 with pip on PATH (try: brew install python@3.11, or set PYTHON=...)" >&2
    exit 1
  fi
fi

rm -rf "${OUT}"
mkdir -p "${OUT}/wheels"

echo "==> Building wheel into dist/"
if command -v uv >/dev/null 2>&1; then
  uv build
else
  "${PY}" -m pip install -q build
  "${PY}" -m build --wheel -o dist
fi

MAIN_WHEEL=""
for w in "${ROOT}/dist/ai_sdlc-${VERSION}-py3-none-any.whl" "${ROOT}/dist"/ai_sdlc-*.whl; do
  if [[ -f "${w}" ]]; then
    MAIN_WHEEL="${w}"
    break
  fi
done

if [[ -z "${MAIN_WHEEL}" ]]; then
  echo "error: no ai_sdlc-*.whl found in dist/ after build" >&2
  exit 1
fi

echo "==> Downloading dependency wheels into bundle (needs network)…"
"${PY}" -m pip download -d "${OUT}/wheels" "${MAIN_WHEEL}"

cp "${SCRIPT_DIR}/install_offline.sh" "${OUT}/"
cp "${SCRIPT_DIR}/install_offline.ps1" "${OUT}/"
cp "${SCRIPT_DIR}/install_offline.bat" "${OUT}/"
cp "${SCRIPT_DIR}/README_BUNDLE.txt" "${OUT}/README.txt"
chmod +x "${OUT}/install_offline.sh"

"${PY}" - "${VERSION}" "${MANIFEST}" <<'PY'
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

version = sys.argv[1]
manifest_path = Path(sys.argv[2])
manifest_path.write_text(
    json.dumps(
        {
            "bundle_format_version": 1,
            "package_version": version,
            "platform_os": platform.system().lower(),
            "platform_machine": platform.machine().lower(),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

mkdir -p "${ROOT}/dist-offline"
rm -f "${ARCHIVE}"
tar -czf "${ARCHIVE}" -C "${ROOT}/dist-offline" "$(basename "${OUT}")"
if [[ "${BUILD_ZIP}" != "0" ]]; then
  rm -f "${ZIP_ARCHIVE}"
  "${PY}" - <<PY
from pathlib import Path
import zipfile

root = Path(r"${ROOT}/dist-offline")
src = root / Path(r"${OUT}").name
dst = Path(r"${ZIP_ARCHIVE}")
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in src.rglob("*"):
        if path.is_file():
            zf.write(path, path.relative_to(root))
PY
fi

echo ""
echo "Done."
echo "  Archive: ${ARCHIVE}"
if [[ "${BUILD_ZIP}" != "0" ]]; then
  echo "  Archive: ${ZIP_ARCHIVE}"
fi
echo "  Folder:  ${OUT}"
echo ""
echo "Ship either archive (or the folder) to offline machines."
echo "  Linux/macOS: tar xzf ai-sdlc-offline-${VERSION}.tar.gz && cd ai-sdlc-offline-${VERSION} && ./install_offline.sh"
if [[ "${BUILD_ZIP}" != "0" ]]; then
  echo "  Windows:     unzip ai-sdlc-offline-${VERSION}.zip && cd ai-sdlc-offline-${VERSION} && install_offline.bat"
fi
