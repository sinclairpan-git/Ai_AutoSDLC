"""AI-SDLC: AI-native SDLC automation framework."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ai-sdlc")
except PackageNotFoundError:  # pragma: no cover — editable/src-only runs
    __version__ = "0.2.4"
