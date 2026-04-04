---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Targets Consumption Baseline

**编号**：`053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline` | **日期**：2026-04-04 | **规格**：specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md

## 概述

本 work item 将 `052` 冻结的 `cleanup_targets` formal truth 接入现有 `050` project cleanup baseline。实现重点不是执行 mutation，而是让 `ProgramService` 与 CLI 在 request/result/artifact/output 中稳定消费 `cleanup_targets`，并将 `missing`、`empty`、`listed` 三态暴露为可验证行为。

## 技术背景

**语言/版本**：Python 3.13
**主要依赖**：Typer CLI、PyYAML、pytest、ruff
**存储**：`.ai-sdlc/artifacts/**` YAML artifact 链
**测试**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`
**目标平台**：本地 CLI / framework orchestration
**约束**：
- 必须保持 `046 -> 047 -> 048 -> 049 -> 050 -> 053` 的 artifact truth 链。
- 不执行真实 workspace cleanup mutation。
- 不从隐式信号推断 cleanup targets。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 先冻结 formal truth，再进实现 | 先重写 053 spec/plan/tasks/log，再写红测，最后最小实现 |
| 单一 truth source，不做隐式推断 | 仅消费 `050` artifact 的 `cleanup_targets` 字段 |
| honesty boundary 不后退 | 即使 target 已列出，execute 仍返回 `deferred` |

## 项目结构

### 文档结构

```text
specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：formal boundary freeze

**目标**：将 053 的真实范围冻结为 `cleanup_targets` consumption baseline
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`
**回退方式**：仅回退 053 文档，不影响已有 `050/052` 实现

### Phase 1：ProgramService red-green

**目标**：用 failing unit tests 驱动 `cleanup_targets` 三态消费逻辑
**产物**：单元测试、`ProgramService` 最小实现
**验证方式**：`uv run pytest tests/unit/test_program_service.py -q`
**回退方式**：回退 `program_service.py` 与新增单测

### Phase 2：CLI surface alignment

**目标**：将 `cleanup_targets_state` 和 target 数量暴露到 CLI 输出
**产物**：CLI 集成测试、`program_cmd.py` 最小输出补齐
**验证方式**：`uv run pytest tests/integration/test_cli_program.py -q`
**回退方式**：回退 CLI 输出相关变更

### Phase 3：focused verification

**目标**：确认 053 在框架约束内闭环
**产物**：通过的测试与 execution log
**验证方式**：
- `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`
- `git diff --check -- specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`
**回退方式**：定位失败项，保持文档 truth 不回退

## 工作流计划

### 工作流 A：cleanup target truth ingestion

**范围**：从 `050` artifact 读取 `cleanup_targets`，归一化成可消费的 state + entries
**影响范围**：`ProgramService` request/result/artifact payload
**验证方式**：单元测试覆盖 `missing` / `empty` / `listed` / invalid
**回退方式**：退回到 `050` baseline，不影响现有 deferred 行为

### 工作流 B：CLI truth visibility

**范围**：在 dry-run / execute 输出中补齐 cleanup target truth state
**影响范围**：`program final-proof-archive-project-cleanup`
**验证方式**：CLI 集成测试断言输出
**回退方式**：保留 service truth，不暴露额外 CLI 字段

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `cleanup_targets` 三态识别 | unit tests | artifact payload 断言 |
| CLI truth surface | integration tests | 手工 dry-run 输出检查 |
| 不执行真实 mutation | execute result assertions | warnings / status assertions |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| invalid `cleanup_targets` 应落 `warning` 还是 `blocked` | 本次按 warning + non-mutation 基线处理 | Phase 1 |
| target entry 是否需要额外排序 | 本次按 artifact 原始顺序透传 | 不阻塞 |

## 实施顺序建议

1. 重写 053 文档，确保 scope 与 052 一致。
2. 先写 unit red tests，锁定三态 truth 语义。
3. 在 `ProgramService` 中最小接通 state + entries。
4. 写 CLI integration red tests，再补最小 terminal output。
5. 跑 focused verification 并更新 execution log。
