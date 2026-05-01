# 实施计划：Release 0.7.1 Offline Smoke And Artifact Verification

**编号**：`184-release-0-7-1-offline-smoke-and-artifact-verification` | **日期**：2026-05-01 | **规格**：`specs/184-release-0-7-1-offline-smoke-and-artifact-verification/spec.md`

## 概述

本切片将当前发布线推进到 `0.7.1`，重点修复 offline smoke workflow 的旧 artifact action runtime warning，并补齐从 GitHub Release 下载正式发布资产后安装冒烟的证据路径。

## 技术背景

**语言/版本**：Python 3.11；GitHub Actions workflow YAML  
**主要依赖**：`actions/upload-artifact@v7`、GitHub CLI、现有 offline installer  
**存储**：release docs、workflow evidence artifact、`program-manifest.yaml` 真值账本  
**测试**：pytest、ruff、`ai-sdlc verify constraints`  
**目标平台**：Windows offline smoke；Linux POSIX tar smoke；release entry docs  
**约束**：先执行 `ai-sdlc run --dry-run`；release docs / install docs / tests / 约束 gate 必须同步；不得把 `run --dry-run` 误称为治理激活证明。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 入口预演 | 本批已先执行 `uv run ai-sdlc run --dry-run`，结果 PASS。 |
| 真值一致 | 同步 README、release notes、offline README、USER_GUIDE、PR checklist 与 verify constraints gate。 |
| 可验证证据 | 用 pytest 覆盖 workflow 静态合同；发布后由 release workflow 产出真实资产安装证据。 |

## 项目结构

### 文档结构

```text
specs/184-release-0-7-1-offline-smoke-and-artifact-verification/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
.github/workflows/windows-offline-smoke.yml
.github/workflows/release-artifact-smoke.yml
src/ai_sdlc/core/verify_constraints.py
src/ai_sdlc/__init__.py
tests/integration/test_github_workflows.py
tests/unit/test_verify_constraints.py
tests/unit/test_packaging_backend.py
```

## 工作流计划

### 工作流 A：CI action warning 收口

**范围**：升级 `windows-offline-smoke.yml` 的 artifact 上传 action 到 `v7`。  
**影响范围**：GitHub Actions runtime warning；smoke evidence 上传。  
**验证方式**：`uv run pytest tests/integration/test_github_workflows.py -q`。  
**回退方式**：若 GitHub hosted runner 暂不支持，回退到官方支持的最近版本并在 release notes 记录边界。

### 工作流 B：release artifact smoke

**范围**：新增 `release-artifact-smoke.yml`，通过 `workflow_dispatch` 或 release published 触发。  
**影响范围**：发布后证据，不参与发布资产构建。  
**验证方式**：静态 workflow 测试；发布后人工/CI 触发 tag `v0.7.1`。  
**回退方式**：保留当前 Windows offline smoke，release artifact smoke 标记为发布后阻断项。

### 工作流 C：0.7.1 入口真值

**范围**：版本号、release docs、offline docs、用户手册、约束测试。  
**影响范围**：用户安装入口与 release docs consistency gate。  
**验证方式**：`uv run ai-sdlc verify constraints`、相关 pytest。  
**回退方式**：恢复 `0.7.0` 入口并取消 `0.7.1` 发布。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| workflow contract | `uv run pytest tests/integration/test_github_workflows.py -q` | GitHub Actions 实际运行 |
| version/doc consistency | `uv run pytest tests/unit/test_verify_constraints.py -q` | `uv run ai-sdlc verify constraints` |
| packaging version | `uv run pytest tests/unit/test_packaging_backend.py -q` | `uv build` / offline bundle build |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| GitHub Release 是否已上传 `v0.7.1` 资产 | 发布后执行 | release artifact smoke |
| 企业私有源 managed delivery 证据 | 外部凭证边界 | 不阻塞本 patch release |

## 实施顺序建议

1. 更新 workflow 和版本真值。
2. 同步 release docs 与约束测试。
3. 运行本地 pytest / ruff / verify constraints。
4. PR 合并后创建 tag、上传资产、运行 release artifact smoke。
