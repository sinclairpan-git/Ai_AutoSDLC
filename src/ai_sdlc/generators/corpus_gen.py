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
    Default prose is 简体中文 for human readers; paths and identifiers stay as-is.
    """
    sections: list[str] = [
        "# 工程认知基线（Engineering Corpus）\n",
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
    """Generate a concise codebase-summary.md (简体中文)."""
    lang_lines = "\n".join(
        f"- **{lang}**：{count} 个文件"
        for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1])
    )
    deps_by_eco: dict[str, int] = {}
    for d in scan.dependencies:
        deps_by_eco[d.ecosystem] = deps_by_eco.get(d.ecosystem, 0) + 1
    dep_lines = "\n".join(
        f"- {eco}：{count} 个依赖" for eco, count in sorted(deps_by_eco.items())
    )

    return f"""# 代码库摘要

## 统计

- **文件总数**：{scan.total_files}
- **代码行数合计**：{scan.total_lines}
- **语言种类**：{len(scan.languages)}
- **依赖条目**：{len(scan.dependencies)}
- **API 端点**：{len(scan.api_endpoints)}
- **测试文件**：{len(scan.tests)}

## 按语言

{lang_lines or "- 未检测到源码文件"}

## 依赖

{dep_lines or "- 未发现依赖清单文件"}

## 入口

{chr(10).join(f"- `{ep}`" for ep in scan.entry_points) or "- 未检测到入口"}
"""


def generate_project_brief(scan: ScanResult) -> str:
    """Generate a project-brief.md with high-level project info (简体中文)."""
    primary_lang = (
        max(scan.languages, key=scan.languages.get) if scan.languages else "unknown"
    )
    return f"""# 项目概要

## 概览

仓库路径 `{scan.root}` — 以 **{primary_lang}** 为主，共 {scan.total_files} 个文件，涵盖 {len(scan.languages)} 种语言。

## 关键特征

- 主语言：{primary_lang}
- 源码行数合计：{scan.total_lines}
- 依赖条目：{len(scan.dependencies)}
- API 端点：{len(scan.api_endpoints)}
- 测试文件：{len(scan.tests)} 个（已检测）

## 入口

{chr(10).join(f"- `{ep}`" for ep in scan.entry_points) or "- 待补充：识别主入口"}

## 备注

<!-- 在此补充项目背景、团队约定等 -->
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
    return f"""## 1. 一页摘要

以 **{primary}** 为主的项目，共 **{scan.total_files}** 个文件（{scan.total_lines} 行），涉及 {len(scan.languages)} 种语言。
依赖：{len(scan.dependencies)} | API：{len(scan.api_endpoints)} | 测试文件：{len(scan.tests)}
"""


def _section_2_repo_map(scan: ScanResult) -> str:
    dirs: set[str] = set()
    for f in scan.files:
        parts = Path(f.path).parts
        if len(parts) > 1:
            dirs.add(parts[0])
    dir_list = "\n".join(f"- `{d}/`" for d in sorted(dirs))
    return f"""## 2. 仓库地图

### 顶层目录

{dir_list or "- （扁平结构，无子目录）"}

### 按语言分布

{chr(10).join(f"- {lang}：{count}" for lang, count in sorted(scan.languages.items(), key=lambda x: -x[1]))}
"""


def _section_3_module_boundaries(scan: ScanResult) -> str:
    modules: dict[str, list[str]] = {}
    for sym in scan.symbols:
        if sym.kind == "class" and sym.is_public:
            mod = str(Path(sym.source_file).parent)
            modules.setdefault(mod, []).append(sym.name)

    if not modules:
        return "## 3. 模块边界与职责\n\n<!-- TODO：描述模块边界 -->\n"

    lines = []
    for mod, classes in sorted(modules.items()):
        lines.append(f"### `{mod}/`\n")
        lines.append(", ".join(f"`{c}`" for c in classes))
        lines.append("")

    return "## 3. 模块边界与职责\n\n" + "\n".join(lines)


def _section_4_key_files(scan: ScanResult) -> str:
    entries = [f for f in scan.files if f.is_entry_point]
    configs = [f for f in scan.files if f.is_config]
    lines = ["## 4. 关键入口与核心文件\n"]
    if entries:
        lines.append("### 入口\n")
        lines.extend(f"- `{f.path}`（{f.line_count} 行）" for f in entries)
    if configs:
        lines.append("\n### 配置文件\n")
        lines.extend(f"- `{f.path}`" for f in configs[:20])
    if not entries and not configs:
        lines.append("<!-- TODO：识别关键入口与配置文件 -->")
    return "\n".join(lines)


def _section_5_data_models(scan: ScanResult) -> str:
    classes = [s for s in scan.symbols if s.kind == "class" and s.is_public]
    if not classes:
        return "## 5. 核心数据模型 / 领域模型\n\n<!-- TODO：描述关键数据模型 -->\n"
    lines = ["## 5. 核心数据模型 / 领域模型\n"]
    for c in classes[:30]:
        doc = f" — {c.docstring.splitlines()[0]}" if c.docstring else ""
        lines.append(f"- `{c.name}`（`{c.source_file}:{c.line_number}`）{doc}")
    return "\n".join(lines)


def _section_6_architecture_decisions(scan: ScanResult) -> str:
    return "## 6. 架构决策与取舍\n\n<!-- TODO：记录关键架构决策及理由 -->\n"


def _section_7_conventions(scan: ScanResult) -> str:
    return "## 7. 隐式约定与代码规范\n\n<!-- TODO：记录命名习惯、模式等未成文约定 -->\n"


def _section_8_external_integrations(scan: ScanResult) -> str:
    if scan.api_endpoints:
        lines = ["## 8. 外部集成\n", "### 已检测 API 端点\n"]
        for ep in scan.api_endpoints[:20]:
            lines.append(
                f"- `{ep.method} {ep.path}`（{ep.framework}，`{ep.source_file}:{ep.line_number}`）"
            )
        return "\n".join(lines)
    return "## 8. 外部集成\n\n<!-- TODO：记录外部服务与集成方式 -->\n"


def _section_9_risks(scan: ScanResult) -> str:
    if not scan.risks:
        return "## 9. 已知风险与技术债\n\n- 未自动检测到风险项。\n"
    lines = ["## 9. 已知风险与技术债\n"]
    for r in scan.risks:
        lines.append(f"- **{r.category}** [{r.severity}]：`{r.path}` — {r.description}")
    return "\n".join(lines)


def _section_10_open_questions() -> str:
    return "## 10. 待澄清问题\n\n<!-- TODO：列出对代码库仍存疑的问题 -->\n"
