"""Frontend contract scanner candidate based on structured source annotations."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FrontendContractObservationArtifact,
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.scanners.file_scanner import IGNORED_DIRS

FRONTEND_CONTRACT_OBSERVATION_MARKER = "ai-sdlc:frontend-contract-observation"
FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND = "scanner"
FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME = "frontend_contract_scanner"
FRONTEND_CONTRACT_SCANNER_FILE_SUFFIXES = (
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".mjs",
    ".cjs",
)

_BLOCK_PATTERNS = (
    re.compile(
        r"/\*\s*ai-sdlc:frontend-contract-observation(?P<payload>.*?)\*/",
        re.DOTALL,
    ),
    re.compile(
        r"<!--\s*ai-sdlc:frontend-contract-observation(?P<payload>.*?)-->",
        re.DOTALL,
    ),
)


@dataclass(frozen=True, slots=True)
class FrontendContractScannerResult:
    """Structured result of scanning source annotations for contract observations."""

    observations: tuple[PageImplementationObservation, ...]
    matched_files: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "observations",
            tuple(_dedupe_observation_items(self.observations)),
        )
        object.__setattr__(
            self,
            "matched_files",
            tuple(_dedupe_text_items(self.matched_files)),
        )


def scan_frontend_contract_observations(root: Path) -> FrontendContractScannerResult:
    """Scan source files for structured frontend contract observation annotations."""

    observations: list[PageImplementationObservation] = []
    matched_files: list[str] = []
    seen_page_ids: dict[str, str] = {}

    if not root.is_dir():
        return FrontendContractScannerResult(observations=(), matched_files=())

    for path in _iter_candidate_files(root):
        rel_path = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8", errors="ignore")
        blocks = _extract_annotation_blocks(source)
        if not blocks:
            continue

        matched_files.append(rel_path)
        for index, payload in enumerate(blocks):
            observation = _parse_observation_block(payload, rel_path, index)
            existing = seen_page_ids.get(observation.page_id)
            if existing is not None:
                raise ValueError(
                    f"duplicate page_id {observation.page_id!r} in {existing} and {rel_path}"
                )
            seen_page_ids[observation.page_id] = rel_path
            observations.append(observation)

    observations.sort(key=lambda item: item.page_id)
    return FrontendContractScannerResult(
        observations=tuple(observations),
        matched_files=tuple(matched_files),
    )


def build_frontend_contract_scanner_artifact(
    source_root: Path,
    *,
    generated_at: str,
    source_revision: str | None = None,
    provider_version: str | None = None,
) -> FrontendContractObservationArtifact:
    """Build a canonical observation artifact from scanner findings."""

    result = scan_frontend_contract_observations(source_root)
    return build_frontend_contract_observation_artifact(
        observations=list(result.observations),
        provider_kind=FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND,
        provider_name=FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME,
        provider_version=provider_version,
        generated_at=generated_at,
        source_ref=str(source_root),
        source_digest=_source_digest(source_root, result.matched_files),
        source_revision=source_revision,
    )


def write_frontend_contract_scanner_artifact(
    source_root: Path,
    spec_dir: Path,
    *,
    generated_at: str,
    source_revision: str | None = None,
    provider_version: str | None = None,
) -> Path:
    """Scan source annotations and materialize the canonical observation artifact."""

    artifact = build_frontend_contract_scanner_artifact(
        source_root,
        generated_at=generated_at,
        source_revision=source_revision,
        provider_version=provider_version,
    )
    return write_frontend_contract_observation_artifact(spec_dir, artifact)


def _iter_candidate_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if _should_ignore(rel_path):
            continue
        if path.suffix.lower() not in FRONTEND_CONTRACT_SCANNER_FILE_SUFFIXES:
            continue
        candidates.append(path)
    return candidates


def _should_ignore(rel_path: Path) -> bool:
    return any(
        part in IGNORED_DIRS or part.endswith(".egg-info") for part in rel_path.parts
    )


def _extract_annotation_blocks(source: str) -> list[str]:
    blocks: list[str] = []
    for pattern in _BLOCK_PATTERNS:
        blocks.extend(match.group("payload").strip() for match in pattern.finditer(source))
    return blocks


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or ():
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_observation_items(
    values: object,
) -> list[PageImplementationObservation]:
    deduped: list[PageImplementationObservation] = []
    seen: set[str] = set()
    for value in values or ():
        if not isinstance(value, PageImplementationObservation):
            continue
        key = json.dumps(
            {
                "page_id": value.page_id,
                "recipe_id": value.recipe_id,
                "i18n_keys": value.i18n_keys,
                "validation_fields": value.validation_fields,
                "new_legacy_usages": value.new_legacy_usages,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def _parse_observation_block(
    payload: str,
    rel_path: str,
    index: int,
) -> PageImplementationObservation:
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{rel_path} observation block {index} invalid JSON ({exc.msg})"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(f"{rel_path} observation block {index} must decode to an object")
    try:
        return PageImplementationObservation(**raw)
    except TypeError as exc:
        raise ValueError(f"{rel_path} observation block {index} invalid: {exc}") from exc


def _source_digest(source_root: Path, matched_files: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for rel_path in matched_files:
        path = source_root / rel_path
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


__all__ = [
    "FRONTEND_CONTRACT_OBSERVATION_MARKER",
    "FRONTEND_CONTRACT_SCANNER_FILE_SUFFIXES",
    "FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND",
    "FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME",
    "FrontendContractScannerResult",
    "build_frontend_contract_scanner_artifact",
    "scan_frontend_contract_observations",
    "write_frontend_contract_scanner_artifact",
]
