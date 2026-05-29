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
#   AI_SDLC_OFFLINE_PYTHON_VERSIONS=3.11,3.12   optional wheel ABI versions to include
#   AI_SDLC_OFFLINE_TARGET_PLATFORM=win_amd64   optional pip target platform for multi-ABI wheels

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

_py_version_nodot() {
  printf '%s' "$1" | tr -d '.'
}

if [[ -n "${AI_SDLC_OFFLINE_PYTHON_VERSIONS:-}" ]]; then
  IFS=', ' read -r -a SUPPORTED_PYTHON_VERSIONS <<< "${AI_SDLC_OFFLINE_PYTHON_VERSIONS}"
else
  CURRENT_PY_VERSION="$("${PY}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  SUPPORTED_PYTHON_VERSIONS=("${CURRENT_PY_VERSION}")
fi

if [[ "${#SUPPORTED_PYTHON_VERSIONS[@]}" -eq 0 ]]; then
  echo "error: AI_SDLC_OFFLINE_PYTHON_VERSIONS did not contain any Python versions" >&2
  exit 1
fi

for PY_VERSION in "${SUPPORTED_PYTHON_VERSIONS[@]}"; do
  if [[ -z "${PY_VERSION}" ]]; then
    continue
  fi
  PY_VERSION_NODOT="$(_py_version_nodot "${PY_VERSION}")"
  if [[ -n "${AI_SDLC_OFFLINE_TARGET_PLATFORM:-}" ]]; then
    "${PY}" -m pip download \
      --only-binary=:all: \
      --platform "${AI_SDLC_OFFLINE_TARGET_PLATFORM}" \
      --implementation cp \
      --python-version "${PY_VERSION_NODOT}" \
      --abi "cp${PY_VERSION_NODOT}" \
      -d "${OUT}/wheels" \
      "${MAIN_WHEEL}"
  else
    "${PY}" -m pip download -d "${OUT}/wheels" "${MAIN_WHEEL}"
  fi
done

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
  cp -R -L "${AI_SDLC_OFFLINE_PYTHON_RUNTIME}" "${OUT}/python-runtime"
  RUNTIME_BUNDLED="true"
fi

"${PY}" - "${VERSION}" "${MANIFEST}" "${RUNTIME_BUNDLED}" "${SUPPORTED_PYTHON_VERSIONS[@]}" <<'PY'
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

version = sys.argv[1]
manifest_path = Path(sys.argv[2])
runtime_bundled = sys.argv[3].lower() == "true"
supported_versions = [item.strip() for item in sys.argv[4:] if item.strip()]
if not supported_versions:
    supported_versions = [f"{sys.version_info.major}.{sys.version_info.minor}"]
manifest_path.write_text(
    json.dumps(
        {
            "bundle_format_version": 1,
            "package_version": version,
            "platform_os": platform.system().lower(),
            "platform_machine": platform.machine().lower(),
            "python_runtime_bundled": runtime_bundled,
            "wheel_python_version": supported_versions[0],
            "wheel_python_tag": "cp" + supported_versions[0].replace(".", ""),
            "supported_python_versions": supported_versions,
            "supported_wheel_python_tags": [
                "cp" + item.replace(".", "") for item in supported_versions
            ],
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

"${PY}" "${SCRIPT_DIR}/verify_offline_bundle.py" "${OUT}"

mkdir -p "${ROOT}/dist-offline"
rm -f "${ARCHIVE}"
if tar --version 2>/dev/null | grep -qi 'gnu tar'; then
  tar --warning=no-file-changed -czf "${ARCHIVE}" -C "${ROOT}/dist-offline" "$(basename "${OUT}")"
else
  tar -czf "${ARCHIVE}" -C "${ROOT}/dist-offline" "$(basename "${OUT}")"
fi
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
echo "  Windows:     \$BundleName = \"${OUT_BASENAME}\"; \$PackageName = \"\$BundleName.zip\"; \$PackageDir = (Get-Location).Path; \$ExtractRoot = Join-Path \$PackageDir \".ai-sdlc-install\"; New-Item -ItemType Directory -Path \$ExtractRoot -Force | Out-Null; Expand-Archive -LiteralPath (Join-Path \$PackageDir \$PackageName) -DestinationPath \$ExtractRoot -Force; Set-Location (Join-Path \$ExtractRoot \$BundleName); install_offline.bat"
if [[ "${RUNTIME_BUNDLED}" == "true" ]]; then
  echo "  Bundled Python runtime: included"
else
  echo "  Bundled Python runtime: not included (set AI_SDLC_OFFLINE_PYTHON_RUNTIME=... to embed one)"
fi
