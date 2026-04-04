---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md"
  - "specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Preview Plan Consumption Baseline

**编号**：`057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline` | **日期**：2026-04-04 | **规格**：specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md

## 概述

`057` 是一个 test-first 的 service/CLI consumption work item。它不进入 real cleanup mutation，而是把 `056` 已冻结的 `cleanup_preview_plan` 正式接入 `ProgramService`、artifact payload 与 CLI output，确保 project cleanup request/result/report 只消费 canonical preview truth，并继续保持 `deferred` honesty boundary。

## 技术背景

**语言/版本**：Python 3.12  
**主要依赖**：Typer、PyYAML、pytest、ruff  
**存储**：项目内 canonical YAML artifact（`.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`）  
**测试**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints`、`uv run ruff check src tests`  
**目标平台**：本地 CLI 驱动的 framework workflow  
**约束**：
- 只消费 `cleanup_preview_plan` truth，不新增旁路 artifact
- 只允许显式 preview plan truth，禁止从 `cleanup_targets` / `cleanup_target_eligibility` 推断
- 不执行真实 cleanup mutation
- 先写 failing tests，再做 service/CLI 最小实现
- 保持 `050/055/056` 的 single-truth-source 与 `deferred` 边界

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一事实源 | 只消费 `050` cleanup artifact 中的 `cleanup_preview_plan` sibling truth |
| 诚实边界 | 继续返回 `deferred`，不把 listed preview 解释成 mutation approval |
| test-first | 先扩展 unit/integration tests，确认红测后再补 service/CLI |
| focused scope | 只修改 `specs/057-.../`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、相关 tests |

## 项目结构

### 文档结构

```text
specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/
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

### Phase 0：context alignment

**目标**：确认 `057` 是 `056` 的 preview truth consumption，而不是 preview truth freeze 或 real mutation  
**产物**：`task-execution-log.md` 中的上下文对账记录  
**验证方式**：审阅 `050/055/056` docs 与现有 `ProgramService` / CLI cleanup 流程  
**回退方式**：仅回退 `057` 文档草稿内容

### Phase 1：red tests

**目标**：补齐 preview truth 缺失、空列表、显式列表与 invalid mapping 的 unit/integration failing tests  
**产物**：更新后的 `tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q` 先出现与 preview truth 相关的失败  
**回退方式**：回退新增 preview tests

### Phase 2：service/CLI consumption

**目标**：最小改动接通 `cleanup_preview_plan` 的 request/result/artifact/CLI 消费  
**产物**：更新后的 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`  
**验证方式**：red tests 转绿，request/result/report 均可观测到 `cleanup_preview_plan_state` 与 preview count  
**回退方式**：按文件局部回退 preview plan consumption 逻辑

### Phase 3：focused verification

**目标**：确认 preview consumption 满足约束，并留下可审计验证证据  
**产物**：更新后的 `task-execution-log.md`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`  
**回退方式**：根据失败点只调整 `057` 相关文档、实现或测试

## 工作流计划

### 工作流 A：Preview truth parser

**范围**：在 `ProgramService` 中解析 `cleanup_preview_plan`，校验结构、target 对齐、eligibility 与 action consistency  
**影响范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`  
**验证方式**：单元测试覆盖 `missing`、`empty`、`listed`、invalid structure、blocked target、action mismatch  
**回退方式**：回退 preview parser 相关逻辑

### 工作流 B：CLI/report exposure

**范围**：在 dry-run / execute 输出中暴露 preview truth state/count，并保持 `deferred` honesty boundary  
**影响范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`  
**验证方式**：CLI 集成测试断言输出包含 `cleanup preview plan state` 与 preview item 数量  
**回退方式**：回退 CLI/report 相关输出

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `cleanup_preview_plan` 被消费为 sibling truth surface | 单元测试断言 request/result/artifact payload 中存在 `cleanup_preview_plan_state` 和 preview list | 审阅 `source_linkage` 与 warnings 是否保持可追踪 |
| invalid preview truth 不被伪装成 readiness | 单元测试断言 invalid structure / blocked target / action mismatch 会生成 warning | 检查 execute 结果仍为 `deferred` |
| CLI 暴露 preview state/count | 集成测试断言 dry-run / execute 输出包含 preview truth state/count | 审阅 report 输出与 artifact 摘要 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| preview item 是否需要更多 operator-facing 文本字段 | 当前保持最小字段，不在本项扩张 | 不阻塞 `057` |
| future mutation proposal 如何消费 listed preview | 已延期到后续 child work item | 不阻塞 `057` |

## 实施顺序建议

1. 对齐 `050/055/056`，确认 `cleanup_preview_plan` 是唯一合法输入面。
2. 先补 unit/integration failing tests，固定 preview truth 的消费语义。
3. 以最小实现接通 `ProgramService`、artifact payload 与 CLI output。
4. 运行 focused verification，并把证据追加到 `task-execution-log.md`。
