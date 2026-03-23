"""Corpus generator — produce engineering-corpus.md, codebase-summary.md, and project-brief.md."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.models.scanner import ScanResult
from ai_sdlc.utils.helpers import AI_SDLC_DIR

logger = logging.getLogger(__name__)


def generate_engineering_corpus(root: Path, scan: ScanResult) -> str:
    """Generate engineering-corpus.md content from scan results.

    The document contains 10 mandatory sections as defined by PRD 8.2.
    Sections that can be auto-filled get content; others get structured placeholders.
    """
    sections: list[str] = [
        "# Engineering Corpus\n",
        _section_1_summary(scan),
        _section_2_repo_map(scan),
        _section_3_module_boundaries(scan),
        _section_4_key_files(scan),
        _section_5_data_models(scan),
        _section_6_architecture_decisions(scan),
        _section_7_conventions(scan),
        _section_8_external_integrations(scan),
        _section_9_risks(scan),
        _section_10_open_questions(),
    ]
    return "\n---\n\n".join(sections)


def generate_codebase_summary(scan: ScanResult) -> str:
    """Generate a concise codebase-summary.md."""
    lang_lines = "\n".join(
        f"- **{lang}**: {count} files"
        for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1])
    )
    deps_by_eco: dict[str, int] = {}
    for d in scan.dependencies:
        deps_by_eco[d.ecosystem] = deps_by_eco.get(d.ecosystem, 0) + 1
    dep_lines = "\n".join(
        f"- {eco}: {count} dependencies" for eco, count in sorted(deps_by_eco.items())
    )

    return f"""# Codebase Summary

## Stats

- **Total files**: {scan.total_files}
- **Total lines**: {scan.total_lines}
- **Languages**: {len(scan.languages)}
- **Dependencies**: {len(scan.dependencies)}
- **API endpoints**: {len(scan.api_endpoints)}
- **Test files**: {len(scan.tests)}

## Languages

{lang_lines or "- No source files detected"}

## Dependencies

{dep_lines or "- No dependency manifests found"}

## Entry Points

{chr(10).join(f"- `{ep}`" for ep in scan.entry_points) or "- None detected"}
"""


def generate_project_brief(scan: ScanResult) -> str:
    """Generate a project-brief.md with high-level project info."""
    primary_lang = (
        max(scan.languages, key=scan.languages.get) if scan.languages else "unknown"
    )
    return f"""# Project Brief

## Overview

Project at `{scan.root}` — a **{primary_lang}**-based project with {scan.total_files} files across {len(scan.languages)} languages.

## Key Characteristics

- Primary language: {primary_lang}
- Total source lines: {scan.total_lines}
- Dependencies: {len(scan.dependencies)}
- API endpoints: {len(scan.api_endpoints)}
- Test coverage: {len(scan.tests)} test files detected

## Entry Points

{chr(10).join(f"- `{ep}`" for ep in scan.entry_points) or "- TODO: Identify main entry points"}

## Notes

<!-- Add project-specific notes, context, and team conventions here -->
"""


def save_corpus_files(root: Path, scan: ScanResult) -> list[str]:
    """Generate and save all corpus files. Returns list of saved file paths."""
    memory_dir = root / AI_SDLC_DIR / "project" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    saved: list[str] = []

    corpus_path = memory_dir / "engineering-corpus.md"
    corpus_path.write_text(generate_engineering_corpus(root, scan), encoding="utf-8")
    saved.append(str(corpus_path.relative_to(root)))

    summary_path = memory_dir / "codebase-summary.md"
    summary_path.write_text(generate_codebase_summary(scan), encoding="utf-8")
    saved.append(str(summary_path.relative_to(root)))

    brief_path = memory_dir / "project-brief.md"
    brief_path.write_text(generate_project_brief(scan), encoding="utf-8")
    saved.append(str(brief_path.relative_to(root)))

    return saved


# --- Section generators ---


def _section_1_summary(scan: ScanResult) -> str:
    primary = (
        max(scan.languages, key=scan.languages.get) if scan.languages else "unknown"
    )
    return f"""## 1. One-Page Summary

A {primary}-based project with **{scan.total_files} files** ({scan.total_lines} lines) across {len(scan.languages)} language(s).
Dependencies: {len(scan.dependencies)} | API Endpoints: {len(scan.api_endpoints)} | Test Files: {len(scan.tests)}
"""


def _section_2_repo_map(scan: ScanResult) -> str:
    dirs: set[str] = set()
    for f in scan.files:
        parts = Path(f.path).parts
        if len(parts) > 1:
            dirs.add(parts[0])
    dir_list = "\n".join(f"- `{d}/`" for d in sorted(dirs))
    return f"""## 2. Repository Map

### Top-Level Directories

{dir_list or "- (flat project structure)"}

### File Distribution by Language

{chr(10).join(f"- {lang}: {count}" for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1]))}
"""


def _section_3_module_boundaries(scan: ScanResult) -> str:
    modules: dict[str, list[str]] = {}
    for sym in scan.symbols:
        if sym.kind == "class" and sym.is_public:
            mod = str(Path(sym.source_file).parent)
            modules.setdefault(mod, []).append(sym.name)

    if not modules:
        return "## 3. Module Boundaries & Responsibilities\n\n<!-- TODO: Describe module boundaries -->\n"

    lines = []
    for mod, classes in sorted(modules.items()):
        lines.append(f"### `{mod}/`\n")
        lines.append(", ".join(f"`{c}`" for c in classes))
        lines.append("")

    return "## 3. Module Boundaries & Responsibilities\n\n" + "\n".join(lines)


def _section_4_key_files(scan: ScanResult) -> str:
    entries = [f for f in scan.files if f.is_entry_point]
    configs = [f for f in scan.files if f.is_config]
    lines = ["## 4. Key Entry Points & Critical Files\n"]
    if entries:
        lines.append("### Entry Points\n")
        lines.extend(f"- `{f.path}` ({f.line_count} lines)" for f in entries)
    if configs:
        lines.append("\n### Configuration Files\n")
        lines.extend(f"- `{f.path}`" for f in configs[:20])
    if not entries and not configs:
        lines.append("<!-- TODO: Identify key entry points and configuration files -->")
    return "\n".join(lines)


def _section_5_data_models(scan: ScanResult) -> str:
    classes = [s for s in scan.symbols if s.kind == "class" and s.is_public]
    if not classes:
        return "## 5. Core Data Models / Domain Models\n\n<!-- TODO: Describe key data models -->\n"
    lines = ["## 5. Core Data Models / Domain Models\n"]
    for c in classes[:30]:
        doc = f" — {c.docstring.splitlines()[0]}" if c.docstring else ""
        lines.append(f"- `{c.name}` (`{c.source_file}:{c.line_number}`){doc}")
    return "\n".join(lines)


def _section_6_architecture_decisions(scan: ScanResult) -> str:
    return "## 6. Architecture Decisions & Rationale\n\n<!-- TODO: Document key architecture decisions and their rationale -->\n"


def _section_7_conventions(scan: ScanResult) -> str:
    return "## 7. Implicit Conventions / Code Standards\n\n<!-- TODO: Document unwritten conventions, naming rules, patterns -->\n"


def _section_8_external_integrations(scan: ScanResult) -> str:
    if scan.api_endpoints:
        lines = ["## 8. External Integrations\n", "### Detected API Endpoints\n"]
        for ep in scan.api_endpoints[:20]:
            lines.append(
                f"- `{ep.method} {ep.path}` ({ep.framework}, `{ep.source_file}:{ep.line_number}`)"
            )
        return "\n".join(lines)
    return "## 8. External Integrations\n\n<!-- TODO: Document external service integrations -->\n"


def _section_9_risks(scan: ScanResult) -> str:
    if not scan.risks:
        return "## 9. Known Risks & Technical Debt\n\n- No automated risks detected.\n"
    lines = ["## 9. Known Risks & Technical Debt\n"]
    for r in scan.risks:
        lines.append(f"- **{r.category}** [{r.severity}]: `{r.path}` — {r.description}")
    return "\n".join(lines)


def _section_10_open_questions() -> str:
    return "## 10. Open Questions\n\n<!-- TODO: List any open questions about the codebase -->\n"
