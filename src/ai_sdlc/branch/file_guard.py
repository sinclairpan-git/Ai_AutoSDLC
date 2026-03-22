"""File-level write protection for governance enforcement."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class ProtectedFileError(Exception):
    """Raised when a write to a protected file is attempted."""


class FileGuard:
    """Track and enforce file-level write protection.

    Used to enforce BR-012 (constitution immutable after freeze)
    and BR-022 (spec.md/plan.md immutable on dev branch).
    """

    def __init__(self) -> None:
        self._protected: set[str] = set()

    def protect(self, path: str) -> None:
        """Mark a file path as protected (write-forbidden).

        Args:
            path: Absolute or relative path to protect.
        """
        normalized = os.path.normpath(path)
        self._protected.add(normalized)
        logger.info("File protected: %s", normalized)

    def unprotect(self, path: str) -> None:
        """Remove write protection from a file path.

        Args:
            path: Path to unprotect.
        """
        normalized = os.path.normpath(path)
        self._protected.discard(normalized)

    def is_protected(self, path: str) -> bool:
        """Check if a file path is protected.

        Args:
            path: Path to check.

        Returns:
            True if the path is write-protected.
        """
        normalized = os.path.normpath(path)
        return normalized in self._protected

    def guard_write(self, path: str) -> None:
        """Raise ProtectedFileError if path is protected.

        Args:
            path: Path to validate before writing.

        Raises:
            ProtectedFileError: If the file is write-protected.
        """
        if self.is_protected(path):
            raise ProtectedFileError(f"Cannot write to protected file: {path}")

    @property
    def protected_paths(self) -> frozenset[str]:
        """Return all currently protected paths."""
        return frozenset(self._protected)
