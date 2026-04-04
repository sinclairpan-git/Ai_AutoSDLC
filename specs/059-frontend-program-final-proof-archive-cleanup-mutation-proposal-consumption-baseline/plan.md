---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md"
  - "specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Mutation Proposal Consumption Baseline

**编号**：`059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline` | **日期**：2026-04-04 | **规格**：specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md

## 概述

`059` 是一个 test-first 的 service/CLI consumption work item。它不进入 approval semantics 或 real cleanup mutation，而是把 `058` 已冻结的 `cleanup_mutation_proposal` 正式接入 `ProgramService`、artifact payload 与 CLI output，确保 project cleanup request/result/report 只消费 canonical proposal truth，并继续保持 `deferred` honesty boundary。

## 技术背景

**语言/版本**：Python 3.12  
**主要依赖**：Typer、PyYAML、pytest、ruff  
**存储**：项目内 canonical YAML artifact（`.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`）  
**测试**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints`、`uv run ruff check src tests`  
**目标平台**：本地 CLI 驱动的 framework workflow  
**约束**：
- 只消费 `cleanup_mutation_proposal` truth，不新增旁路 artifact
- 只允许显式 proposal truth，禁止从 targets、eligibility、preview plan 或隐式信号推断
- 不执行真实 cleanup mutation
- 先写 failing tests，再做 service/CLI 最小实现
- 保持 `050/057/058` 的 single-truth-source 与 `deferred` 边界

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一事实源 | 只消费 `050` cleanup artifact 中的 `cleanup_mutation_proposal` sibling truth |
| 诚实边界 | 继续返回 `deferred`，不把 listed proposal 解释成 mutation approval |
| test-first | 先扩展 unit/integration tests，确认红测后再补 service/CLI |
| focused scope | 只修改 `specs/059-.../`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、相关 tests |

## 项目结构

### 文档结构

```text
specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/
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

**目标**：确认 `059` 是 `058` 的 proposal truth consumption，而不是 approval semantics 或 real mutation  
**产物**：`task-execution-log.md` 中的上下文对账记录  
**验证方式**：审阅 `050/057/058` docs 与现有 `ProgramService` / CLI cleanup 流程  
**回退方式**：仅回退 `059` 文档草稿内容

### Phase 1：red tests

**目标**：补齐 proposal truth 缺失、空列表、显式列表与 invalid alignment 的 unit/integration failing tests  
**产物**：更新后的 `tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py -q` 与 `uv run pytest tests/integration/test_cli_program.py -q` 先出现与 proposal truth 相关的失败  
**回退方式**：回退新增 proposal tests

### Phase 2：service/CLI consumption

**目标**：最小改动接通 `cleanup_mutation_proposal` 的 request/result/artifact/CLI 消费  
**产物**：更新后的 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`  
**验证方式**：red tests 转绿，request/result/report 均可观测到 `cleanup_mutation_proposal_state` 与 proposal count  
**回退方式**：按文件局部回退 proposal consumption 逻辑

### Phase 3：focused verification

**目标**：确认 proposal consumption 满足约束，并留下可审计验证证据  
**产物**：更新后的 `task-execution-log.md`  
**验证方式**：`uv run pytest tests/unit/test_program_service.py -q`、`uv run pytest tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration .ai-sdlc/project/config/project-state.yaml`  
**回退方式**：根据失败点只调整 `059` 相关文档、实现或测试

## 工作流计划

### 工作流 A：Proposal truth parser

**范围**：在 `ProgramService` 中解析 `cleanup_mutation_proposal`，校验结构、target 对齐、eligibility、preview alignment 与 action consistency  
**影响范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`  
**验证方式**：单元测试覆盖 `missing`、`empty`、`listed`、invalid structure、unknown target、ineligible target、preview mismatch、action mismatch  
**回退方式**：回退 proposal parser 相关逻辑

### 工作流 B：CLI/report exposure

**范围**：在 dry-run / execute 输出中暴露 proposal truth state/count，并保持 `deferred` honesty boundary  
**影响范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`  
**验证方式**：CLI 集成测试断言 dry-run / execute 输出包含 `cleanup mutation proposal state` 与 proposal 数量  
**回退方式**：回退 CLI/report 相关输出

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `cleanup_mutation_proposal` 被消费为 sibling truth surface | 单元测试断言 request/result/artifact payload 中存在 `cleanup_mutation_proposal_state` 和 proposal list | 审阅 `source_linkage` 与 warnings 是否保持可追踪 |
| invalid proposal truth 不被伪装成 readiness | 单元测试断言 invalid structure / unknown target / ineligible target / preview mismatch / action mismatch 会生成 warning | 检查 execute 结果仍为 `deferred` |
| CLI 暴露 proposal state/count | 集成测试断言 dry-run / execute 输出包含 proposal truth state/count | 审阅 report 输出与 artifact 摘要 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| proposal approval semantics 是否需要单独 truth surface | 已延期到后续 child work item | 不阻塞 `059` |
| future mutation executor 是否需要消费 proposal item 的更多字段 | 当前保持最小字段，不在本项扩张 | 不阻塞 `059` |

## 实施顺序建议

1. 对齐 `050/057/058`，确认 `cleanup_mutation_proposal` 是唯一合法输入面。
2. 先补 unit/integration failing tests，固定 proposal truth 的消费语义。
3. 以最小实现接通 `ProgramService`、artifact payload 与 CLI output。
4. 运行 focused verification，并把证据追加到 `task-execution-log.md`。
