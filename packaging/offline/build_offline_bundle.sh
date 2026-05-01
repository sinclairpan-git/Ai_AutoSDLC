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
#   AI_SDLC_OFFLINE_PYTHON_RUNTIME=/path/to/portable/python-runtime   optional runtime copied into python-runtime/
#   AI_SDLC_OFFLINE_ASSET_SUFFIX=-windows-amd64   optional suffix for platform-specific release assets

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT}"

VERSION="$(awk -F'"' '/^version =/ {print $2; exit}' pyproject.toml)"
ASSET_SUFFIX="${AI_SDLC_OFFLINE_ASSET_SUFFIX:-}"
OUT_BASENAME="ai-sdlc-offline-${VERSION}${ASSET_SUFFIX}"
OUT="${ROOT}/dist-offline/${OUT_BASENAME}"
ARCHIVE="${ROOT}/dist-offline/${OUT_BASENAME}.tar.gz"
ZIP_ARCHIVE="${ROOT}/dist-offline/${OUT_BASENAME}.zip"
MANIFEST="${OUT}/bundle-manifest.json"
RUNTIME_BUNDLED="false"

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

if [[ -n "${AI_SDLC_OFFLINE_PYTHON_RUNTIME:-}" ]]; then
  if [[ ! -d "${AI_SDLC_OFFLINE_PYTHON_RUNTIME}" ]]; then
    echo "error: AI_SDLC_OFFLINE_PYTHON_RUNTIME must point to a portable runtime directory" >&2
    exit 1
  fi
  echo "==> Copying bundled Python runtime into offline bundle…"
  cp -R "${AI_SDLC_OFFLINE_PYTHON_RUNTIME}" "${OUT}/python-runtime"
  RUNTIME_BUNDLED="true"
fi

"${PY}" - "${VERSION}" "${MANIFEST}" "${RUNTIME_BUNDLED}" <<'PY'
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

version = sys.argv[1]
manifest_path = Path(sys.argv[2])
runtime_bundled = sys.argv[3].lower() == "true"
manifest_path.write_text(
    json.dumps(
        {
            "bundle_format_version": 1,
            "package_version": version,
            "platform_os": platform.system().lower(),
            "platform_machine": platform.machine().lower(),
            "python_runtime_bundled": runtime_bundled,
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
rm -f "${ZIP_ARCHIVE}"
"${PY}" - "${VERSION}" "${OUT_BASENAME}" <<'PY'
from pathlib import Path
import sys
import zipfile

version = sys.argv[1]
out_basename = sys.argv[2]
root = Path("dist-offline")
src = root / out_basename
dst = root / f"{out_basename}.zip"
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in src.rglob("*"):
        if path.is_file():
            zf.write(path, path.relative_to(root))
PY

echo ""
echo "Done."
echo "  Archive: ${ARCHIVE}"
echo "  Archive: ${ZIP_ARCHIVE}"
echo "  Folder:  ${OUT}"
echo ""
echo "Ship either archive (or the folder) to offline machines."
echo "  Linux/macOS: tar xzf ${OUT_BASENAME}.tar.gz && cd ${OUT_BASENAME} && ./install_offline.sh"
echo "  Windows:     unzip ${OUT_BASENAME}.zip && cd ${OUT_BASENAME} && install_offline.bat"
if [[ "${RUNTIME_BUNDLED}" == "true" ]]; then
  echo "  Bundled Python runtime: included"
else
  echo "  Bundled Python runtime: not included (set AI_SDLC_OFFLINE_PYTHON_RUNTIME=... to embed one)"
fi
