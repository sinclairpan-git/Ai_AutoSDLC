"""File-level write protection for governance enforcement."""

from __future__ import annotations

import builtins
import logging
import os
from pathlib import Path
from typing import Any
from weakref import WeakSet

logger = logging.getLogger(__name__)


class ProtectedFileError(Exception):
    """Raised when a write to a protected file is attempted."""


class FileGuard:
    """Track and enforce file-level write protection.

    Used to enforce BR-012 (constitution immutable after freeze)
    and BR-022 (spec.md/plan.md immutable on dev branch).
    """

    _active_guards: WeakSet[FileGuard] = WeakSet()
    _hooks_installed = False
    _original_open = builtins.open
    _original_path_open = Path.open
    _original_write_text = Path.write_text
    _original_write_bytes = Path.write_bytes
    _original_replace = Path.replace
    _original_rename = Path.rename

    def __init__(self) -> None:
        self._protected: set[str] = set()
        self.__class__._active_guards.add(self)
        self.__class__._install_hooks()

    def protect(self, path: str) -> None:
        """Mark a file path as protected (write-forbidden).

        Args:
            path: Absolute or relative path to protect.
        """
        normalized = self._normalize(path)
        self._protected.add(normalized)
        logger.info("File protected: %s", normalized)

    def unprotect(self, path: str) -> None:
        """Remove write protection from a file path.

        Args:
            path: Path to unprotect.
        """
        normalized = self._normalize(path)
        self._protected.discard(normalized)

    def is_protected(self, path: str) -> bool:
        """Check if a file path is protected.

        Args:
            path: Path to check.

        Returns:
            True if the path is write-protected.
        """
        normalized = self._normalize(path)
        return normalized in self._protected

    def guard_write(self, path: str) -> None:
        """Raise ProtectedFileError if path is protected.

        Args:
            path: Path to validate before writing.

        Raises:
            ProtectedFileError: If the file is write-protected.
        """
        if self._is_any_protected(path):
            raise ProtectedFileError(f"Cannot write to protected file: {path}")

    def write_text(self, path: str | Path, content: str, *, encoding: str = "utf-8") -> None:
        """Guard and write text to disk through a single checked path."""
        target = Path(path)
        self.guard_write(str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=encoding)

    @property
    def protected_paths(self) -> frozenset[str]:
        """Return all currently protected paths."""
        return frozenset(self._protected)

    @staticmethod
    def _normalize(path: str | os.PathLike[str]) -> str:
        return os.path.normpath(os.fspath(path))

    @classmethod
    def _is_any_protected(cls, path: str | os.PathLike[str] | Any) -> bool:
        try:
            normalized = cls._normalize(path)
        except TypeError:
            return False
        return any(normalized in guard._protected for guard in list(cls._active_guards))

    @classmethod
    def _guard_any_protected(cls, path: str | os.PathLike[str] | Any) -> None:
        if cls._is_any_protected(path):
            raise ProtectedFileError(f"Cannot write to protected file: {path}")

    @staticmethod
    def _mode_is_write(mode: str) -> bool:
        return any(flag in mode for flag in ("w", "a", "x", "+"))

    @classmethod
    def _install_hooks(cls) -> None:
        if cls._hooks_installed:
            return

        def guarded_open(
            file: Any,
            mode: str = "r",
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            if cls._mode_is_write(mode):
                cls._guard_any_protected(file)
            return cls._original_open(file, mode, *args, **kwargs)

        def guarded_path_open(
            self: Path,
            mode: str = "r",
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            if cls._mode_is_write(mode):
                cls._guard_any_protected(self)
            return cls._original_path_open(self, mode, *args, **kwargs)

        def guarded_write_text(
            self: Path,
            data: str,
            *args: Any,
            **kwargs: Any,
        ) -> int:
            cls._guard_any_protected(self)
            return cls._original_write_text(self, data, *args, **kwargs)

        def guarded_write_bytes(self: Path, data: bytes) -> int:
            cls._guard_any_protected(self)
            return cls._original_write_bytes(self, data)

        def guarded_replace(self: Path, target: str | os.PathLike[str]) -> Path:
            cls._guard_any_protected(self)
            cls._guard_any_protected(target)
            return cls._original_replace(self, target)

        def guarded_rename(self: Path, target: str | os.PathLike[str]) -> Path:
            cls._guard_any_protected(self)
            cls._guard_any_protected(target)
            return cls._original_rename(self, target)

        builtins.open = guarded_open
        Path.open = guarded_path_open
        Path.write_text = guarded_write_text
        Path.write_bytes = guarded_write_bytes
        Path.replace = guarded_replace
        Path.rename = guarded_rename
        cls._hooks_installed = True
