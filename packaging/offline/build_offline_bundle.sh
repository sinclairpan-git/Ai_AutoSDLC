#!/usr/bin/env bash
# Run on a machine WITH internet access (same OS/arch as targets when possible).
# Produces: dist-offline/ai-sdlc-offline-<version>.tar.gz
#
# Usage:
#   ./packaging/offline/build_offline_bundle.sh
# Env:
#   PYTHON=/path/to/python3.11   interpreter used for pip download (default: python3)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT}"

VERSION="$(awk -F'"' '/^version =/ {print $2; exit}' pyproject.toml)"
OUT="${ROOT}/dist-offline/ai-sdlc-offline-${VERSION}"
ARCHIVE="${ROOT}/dist-offline/ai-sdlc-offline-${VERSION}.tar.gz"
PY="${PYTHON:-python3}"

if ! "${PY}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  echo "error: ${PY} must be Python >= 3.11" >&2
  exit 1
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
cp "${SCRIPT_DIR}/README_BUNDLE.txt" "${OUT}/README.txt"
chmod +x "${OUT}/install_offline.sh"

mkdir -p "${ROOT}/dist-offline"
rm -f "${ARCHIVE}"
tar -czf "${ARCHIVE}" -C "${ROOT}/dist-offline" "$(basename "${OUT}")"

echo ""
echo "Done."
echo "  Archive: ${ARCHIVE}"
echo "  Folder:  ${OUT}"
echo ""
echo "Ship the .tar.gz (or the folder) to offline machines, then:"
echo "  tar xzf ai-sdlc-offline-${VERSION}.tar.gz && cd ai-sdlc-offline-${VERSION} && ./install_offline.sh"
