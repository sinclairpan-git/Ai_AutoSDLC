"""Backend registry — manage and resolve SDLC execution backends."""

from __future__ import annotations

import logging

from ai_sdlc.backends.native import NativeBackend
from ai_sdlc.backends.protocol import BackendProtocol

logger = logging.getLogger(__name__)

_DEFAULT_NAME = "native"


class BackendNotFoundError(Exception):
    """Raised when a requested backend is not registered."""


class BackendRegistry:
    """Registry for SDLC execution backends.

    The native backend is always registered by default.
    Plugin backends can be registered to override or extend it.
    """

    def __init__(self) -> None:
        self._backends: dict[str, BackendProtocol] = {}
        self._default = _DEFAULT_NAME
        self.register(_DEFAULT_NAME, NativeBackend())

    def register(self, name: str, backend: BackendProtocol) -> None:
        """Register a backend by name.

        Args:
            name: Unique backend identifier.
            backend: Backend instance conforming to BackendProtocol.
        """
        self._backends[name] = backend
        logger.info("Backend registered: %s", name)

    def get(self, name: str) -> BackendProtocol:
        """Retrieve a backend by name.

        Args:
            name: Backend identifier.

        Returns:
            The registered backend.

        Raises:
            BackendNotFoundError: If the backend is not registered.
        """
        if name not in self._backends:
            raise BackendNotFoundError(f"Backend not found: {name}")
        return self._backends[name]

    def get_default(self) -> BackendProtocol:
        """Return the default backend (native unless overridden).

        Returns:
            The default backend instance.
        """
        return self._backends[self._default]

    def set_default(self, name: str) -> None:
        """Set the default backend.

        Args:
            name: Name of a registered backend.

        Raises:
            BackendNotFoundError: If the backend is not registered.
        """
        if name not in self._backends:
            raise BackendNotFoundError(f"Cannot set default to unregistered: {name}")
        self._default = name

    @property
    def available(self) -> list[str]:
        """Return sorted list of registered backend names."""
        return sorted(self._backends)
