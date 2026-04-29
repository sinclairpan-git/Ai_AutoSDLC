"""Source checkout shim that resolves ``ai_sdlc`` imports into ``src/``."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "ai_sdlc"

# In a source checkout, make submodule imports resolve to ``src/ai_sdlc`` even
# when the current interpreter also has a globally installed ``ai_sdlc``.
__path__ = [str(_SRC_PACKAGE)]

try:
    __version__ = version("ai-sdlc")
except PackageNotFoundError:  # pragma: no cover - source checkout fallback
    __version__ = "0.7.0"
