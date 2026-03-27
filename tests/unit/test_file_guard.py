"""Unit tests for FileGuard."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.branch.file_guard import FileGuard, ProtectedFileError


class TestFileGuard:
    def test_protect_marks_path_protected(self) -> None:
        fg = FileGuard()
        fg.protect("/tmp/spec.md")
        assert fg.is_protected("/tmp/spec.md") is True

    def test_guard_write_protected_raises(self) -> None:
        fg = FileGuard()
        fg.protect("/x/y.md")
        with pytest.raises(ProtectedFileError, match="protected file"):
            fg.guard_write("/x/y.md")

    def test_guard_write_unprotected_ok(self) -> None:
        fg = FileGuard()
        fg.guard_write("/not/protected.txt")

    def test_unprotect_removes_protection(self) -> None:
        fg = FileGuard()
        fg.protect("/a/b.md")
        fg.unprotect("/a/b.md")
        assert fg.is_protected("/a/b.md") is False
        fg.guard_write("/a/b.md")

    def test_protected_paths_is_frozenset(self) -> None:
        fg = FileGuard()
        fg.protect("p1")
        fg.protect("p2")
        paths = fg.protected_paths
        assert isinstance(paths, frozenset)
        assert paths == frozenset({"p1", "p2"})

    def test_path_normalization_collapses_dotdot(self) -> None:
        fg = FileGuard()
        fg.protect("/tmp/project/spec.md")
        assert fg.is_protected("/tmp/project/../project/spec.md") is True
        with pytest.raises(ProtectedFileError, match="protected file"):
            fg.guard_write("/tmp/project/../project/spec.md")

    def test_path_traversal_normalization(self) -> None:
        guard = FileGuard()
        guard.protect("/project/specs/WI-001/spec.md")
        assert guard.is_protected("/project/specs/../specs/WI-001/spec.md")

    def test_write_text_protected_raises_and_does_not_write(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "spec.md"
        guard.protect(str(target))
        with pytest.raises(ProtectedFileError, match="protected file"):
            guard.write_text(target, "# blocked\n")
        assert not target.exists()

    def test_write_text_unprotected_persists_content(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "plan.md"
        guard.write_text(target, "# ok\n")
        assert target.read_text(encoding="utf-8") == "# ok\n"

    def test_path_write_text_protected_raises(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "spec.md"
        guard.protect(str(target))

        with pytest.raises(ProtectedFileError, match="protected file"):
            target.write_text("# blocked\n", encoding="utf-8")

    def test_path_write_bytes_protected_raises(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "spec.md"
        guard.protect(str(target))

        with pytest.raises(ProtectedFileError, match="protected file"):
            target.write_bytes(b"# blocked\n")

    def test_open_write_protected_raises(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "spec.md"
        guard.protect(str(target))

        with (
            pytest.raises(ProtectedFileError, match="protected file"),
            open(target, "w", encoding="utf-8"),
        ):
            pass

    def test_replace_into_protected_target_raises(self, tmp_path: Path) -> None:
        guard = FileGuard()
        target = tmp_path / "spec.md"
        source = tmp_path / "tmp.md"
        source.write_text("# tmp\n", encoding="utf-8")
        guard.protect(str(target))

        with pytest.raises(ProtectedFileError, match="protected file"):
            source.replace(target)
