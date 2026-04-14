"""In-tree PEP 517 backend for offline-friendly wheel and sdist builds."""

from __future__ import annotations

import base64
import hashlib
import io
import os
import re
import tarfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "ai_sdlc"
_EXCLUDED_NAMES = {"__pycache__", ".DS_Store", ".gitkeep"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, object] | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Build a pure-Python wheel without external build dependencies."""
    del config_settings, metadata_directory

    metadata = _load_metadata()
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)

    dist_name = _distribution_filename(metadata["name"])
    wheel_name = f"{dist_name}-{metadata['version']}-py3-none-any.whl"
    wheel_path = wheel_dir / wheel_name
    dist_info_dir = f"{dist_name}-{metadata['version']}.dist-info"

    record_rows: list[str] = []
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for destination, source in _iter_wheel_sources():
            data = source.read_bytes()
            _write_wheel_file(archive, record_rows, destination.as_posix(), data)

        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/METADATA",
            _render_metadata(metadata).encode("utf-8"),
        )
        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/WHEEL",
            _render_wheel_file().encode("utf-8"),
        )
        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/entry_points.txt",
            _render_entry_points(metadata).encode("utf-8"),
        )

        record_path = f"{dist_info_dir}/RECORD"
        record_body = "".join(record_rows) + f"{record_path},,\n"
        archive.writestr(record_path, record_body)

    return wheel_name


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    """Build a source distribution containing the package and packaging backend."""
    del config_settings

    metadata = _load_metadata()
    sdist_dir = Path(sdist_directory)
    sdist_dir.mkdir(parents=True, exist_ok=True)

    dist_name = _distribution_filename(metadata["name"])
    base_name = f"{dist_name}-{metadata['version']}"
    archive_name = f"{base_name}.tar.gz"
    archive_path = sdist_dir / archive_name

    with tarfile.open(archive_path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for relative_path in _iter_sdist_sources():
            source = ROOT / relative_path
            archive.add(source, arcname=f"{base_name}/{relative_path.as_posix()}", recursive=False)

        pkg_info = _render_metadata(metadata).encode("utf-8")
        info = tarfile.TarInfo(name=f"{base_name}/PKG-INFO")
        info.size = len(pkg_info)
        info.mtime = int(os.stat(ROOT / "pyproject.toml").st_mtime)
        archive.addfile(info, io.BytesIO(pkg_info))

    return archive_name


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, object] | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Build an editable wheel that points site-packages at ``src/``."""
    del config_settings, metadata_directory

    metadata = _load_metadata()
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)

    dist_name = _distribution_filename(metadata["name"])
    wheel_name = f"{dist_name}-{metadata['version']}-py3-none-any.whl"
    wheel_path = wheel_dir / wheel_name
    dist_info_dir = f"{dist_name}-{metadata['version']}.dist-info"
    pth_name = f"{dist_name}-editable.pth"

    record_rows: list[str] = []
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_wheel_file(
            archive,
            record_rows,
            pth_name,
            f"{SRC_ROOT}\n".encode(),
        )
        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/METADATA",
            _render_metadata(metadata).encode("utf-8"),
        )
        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/WHEEL",
            _render_wheel_file().encode("utf-8"),
        )
        _write_wheel_file(
            archive,
            record_rows,
            f"{dist_info_dir}/entry_points.txt",
            _render_entry_points(metadata).encode("utf-8"),
        )

        record_path = f"{dist_info_dir}/RECORD"
        record_body = "".join(record_rows) + f"{record_path},,\n"
        archive.writestr(record_path, record_body)

    return wheel_name


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    """Prepare dist-info metadata for frontends that request it."""
    del config_settings

    metadata = _load_metadata()
    dist_name = _distribution_filename(metadata["name"])
    dist_info_dir = Path(metadata_directory) / f"{dist_name}-{metadata['version']}.dist-info"
    dist_info_dir.mkdir(parents=True, exist_ok=True)
    (dist_info_dir / "METADATA").write_text(_render_metadata(metadata), encoding="utf-8")
    (dist_info_dir / "WHEEL").write_text(_render_wheel_file(), encoding="utf-8")
    (dist_info_dir / "entry_points.txt").write_text(
        _render_entry_points(metadata),
        encoding="utf-8",
    )
    return dist_info_dir.name


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    """Editable metadata matches the regular wheel metadata."""
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def get_requires_for_build_wheel(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    del config_settings
    return []


def get_requires_for_build_editable(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    del config_settings
    return []


def get_requires_for_build_sdist(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    del config_settings
    return []


def _load_metadata() -> dict[str, object]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    return {
        "name": project["name"],
        "version": project["version"],
        "description": project.get("description", ""),
        "readme": project.get("readme"),
        "requires_python": project.get("requires-python"),
        "license": (project.get("license") or {}).get("text", ""),
        "dependencies": list(project.get("dependencies", [])),
        "scripts": dict(project.get("scripts", {})),
        "force_include": dict(
            pyproject.get("tool", {})
            .get("ai_sdlc", {})
            .get("packaging", {})
            .get("force-include", {})
        ),
    }


def _distribution_filename(name: str) -> str:
    return re.sub(r"[-_.]+", "_", name)


def _iter_wheel_sources() -> list[tuple[PurePosixPath, Path]]:
    sources: list[tuple[PurePosixPath, Path]] = []
    for source in sorted(PACKAGE_ROOT.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(SRC_ROOT)
        if not _should_include(relative):
            continue
        sources.append((PurePosixPath(relative.as_posix()), source))

    metadata = _load_metadata()
    for source_name, destination_name in sorted(metadata["force_include"].items()):
        source = ROOT / source_name
        destination = PurePosixPath(destination_name)
        sources.append((destination, source))

    return sources


def _iter_sdist_sources() -> list[Path]:
    sources = [
        Path("pyproject.toml"),
        Path("README.md"),
        Path("packaging_backend.py"),
    ]

    for root in (Path("src"), Path("templates")):
        source_root = ROOT / root
        for source in sorted(source_root.rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(ROOT)
            if not _should_include(relative):
                continue
            sources.append(relative)

    deduped: list[Path] = []
    for source in sources:
        if source not in deduped:
            deduped.append(source)
    return deduped


def _should_include(relative_path: Path) -> bool:
    for part in relative_path.parts:
        if part in _EXCLUDED_NAMES:
            return False
        if part.startswith("."):
            return False
    return relative_path.suffix not in _EXCLUDED_SUFFIXES


def _render_metadata(metadata: dict[str, object]) -> str:
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {metadata['name']}",
        f"Version: {metadata['version']}",
    ]
    description = str(metadata["description"]).strip()
    if description:
        lines.append(f"Summary: {description}")
    license_text = str(metadata["license"]).strip()
    if license_text:
        lines.append(f"License: {license_text}")
    requires_python = str(metadata["requires_python"] or "").strip()
    if requires_python:
        lines.append(f"Requires-Python: {requires_python}")
    for dependency in metadata["dependencies"]:
        lines.append(f"Requires-Dist: {dependency}")

    readme_path = metadata["readme"]
    if readme_path:
        lines.append("Description-Content-Type: text/markdown")
        body = (ROOT / str(readme_path)).read_text(encoding="utf-8")
        return "\n".join(lines) + "\n\n" + body
    return "\n".join(lines) + "\n"


def _render_wheel_file() -> str:
    return "\n".join(
        (
            "Wheel-Version: 1.0",
            "Generator: packaging_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        )
    )


def _render_entry_points(metadata: dict[str, object]) -> str:
    scripts: dict[str, str] = metadata["scripts"]  # type: ignore[assignment]
    lines = ["[console_scripts]"]
    for name, target in sorted(scripts.items()):
        lines.append(f"{name} = {target}")
    lines.append("")
    return "\n".join(lines)


def _write_wheel_file(
    archive: zipfile.ZipFile,
    record_rows: list[str],
    destination: str,
    data: bytes,
) -> None:
    archive.writestr(destination, data)
    digest = hashlib.sha256(data).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    record_rows.append(f"{destination},sha256={encoded},{len(data)}\n")
