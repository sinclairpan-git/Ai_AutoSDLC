---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Eligibility Consumption Baseline

**编号**：`055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline` | **日期**：2026-04-04 | **规格**：specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md

## 概述

`055` 将 `054` 冻结的 `cleanup_target_eligibility` truth surface 接入现有 `050 -> 053` project cleanup 链路。实现范围限定在 `ProgramService`、CLI、单元测试和集成测试，目标是让 request/result/artifact/terminal output 都能消费并暴露 eligibility truth，同时继续保持 `050` 的 `deferred` honesty boundary。

## 技术背景

**语言/版本**：Python 3.12  
**主要依赖**：Typer、PyYAML、pytest、ruff  
**存储**：项目内 canonical YAML artifact（`.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`）  
**测试**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**目标平台**：本地 CLI 工作流  
**约束**：
- 只消费 `050` cleanup artifact 中显式 `cleanup_target_eligibility`
- 不执行真实 cleanup mutation
- 先写 failing tests，再做最小实现
- 不通过隐式信号推断 eligibility

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一事实源 | 只从 `050` cleanup artifact 读取 `cleanup_target_eligibility`，不新增旁路 artifact |
| 诚实边界 | 即使 eligibility 为 `listed`，执行结果仍保持 `deferred`，不越权到 real cleanup |
| 先测后改 | 先补 unit/integration failing tests，再修改 service/CLI |
| focused verification | 完成后运行定向 pytest、ruff、constraints 与 diff-check |

## 项目结构

### 文档结构

```text
specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/
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

### Phase 0：formal freeze

**目标**：将 `055` 的消费边界、non-goals、测试目标与验证策略冻结到 canonical docs  
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `specs/055-.../` 文档改动

### Phase 1：TDD red

**目标**：用 failing tests 固定 eligibility truth 的 request/result/artifact/CLI 消费语义  
**产物**：更新后的 `tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**验证方式**：定向 pytest 先失败且失败原因指向缺失的 eligibility consumption 字段/输出  
**回退方式**：回退本次新增测试块

### Phase 2：Service / CLI green

**目标**：在最小变更下接入 eligibility truth，补齐 request/result/artifact/source_linkage/CLI guard/report  
**产物**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`  
**验证方式**：定向 pytest 通过  
**回退方式**：回退 service/CLI 相关最小 patch

### Phase 3：Focused verification

**目标**：确认实现未破坏现有链路并记录验证证据  
**产物**：更新后的 `task-execution-log.md`  
**验证方式**：`pytest`、`ruff`、`verify constraints`、`git diff --check`  
**回退方式**：根据失败点仅调整对应源码/测试

## 工作流计划

### 工作流 A：Eligibility truth consumption

**范围**：从 seed cleanup artifact 读取 `cleanup_target_eligibility`，解析 state/list，透传到 request/result/artifact/source_linkage  
**影响范围**：`ProgramService` dataclass、解析 helper、artifact payload builder  
**验证方式**：单元测试覆盖 `missing`、`empty`、`listed`、invalid structure  
**回退方式**：保持 `cleanup_targets` 消费逻辑不变，仅去掉 eligibility 接线

### 工作流 B：CLI observability

**范围**：在 dry-run / execute guard、结果输出与 report 中暴露 eligibility state/count  
**影响范围**：`program final-proof-archive-project-cleanup` 命令与渲染函数  
**验证方式**：集成测试断言 output/report 文本  
**回退方式**：仅回退 CLI 展示变更，不动 service truth

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| request/result/artifact 能消费 eligibility truth | `uv run pytest tests/unit/test_program_service.py -q` | YAML payload 对账 |
| CLI guard/report 暴露 eligibility state/count | `uv run pytest tests/integration/test_cli_program.py -q` | 手工检查 report 文本 |
| `deferred` honesty boundary 未被破坏 | 单元测试断言 `project_cleanup_result == deferred` | `uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `eligible` 是否授权 real cleanup | 已由 `054` 冻结为否 | 无 |
| invalid eligibility truth 是否需要 hard-block | 当前基线只要求 warning + `deferred`，未来子项再细化 | 不阻塞 |

## 实施顺序建议

1. 冻结 `055` docs 与 execution log。
2. 编写 unit/integration failing tests 固定 eligibility consumption。
3. 修改 `ProgramService` request/result/helper/artifact payload。
4. 修改 CLI guard/result/report 输出。
5. 运行 focused verification 并把证据追加到 `task-execution-log.md`。
