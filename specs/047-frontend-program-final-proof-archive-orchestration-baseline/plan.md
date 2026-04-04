---
related_doc:
  - "specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Orchestration Baseline

**编号**：`047-frontend-program-final-proof-archive-orchestration-baseline` | **日期**：2026-04-04 | **规格**：specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md

## 概述

本计划处理的是 `046` 之后的 frontend program final proof archive orchestration baseline，而不是继续扩张 `046` 的 closure artifact responsibility。当前仓库已经在上游锁定并实现了：

- `024` 到 `034`：remediation / provider / patch / writeback / registry 的 orchestration 与 artifact 链路
- `035`：broader governance request/result 与显式确认 CLI surface
- `036`：broader governance artifact writer 与 execute artifact output/report
- `037`：final governance request/result 与显式确认 CLI surface
- `038`：final governance artifact writer 与 execute artifact output/report
- `039`：writeback persistence request/result 与显式确认 CLI surface
- `040`：writeback persistence artifact writer 与 execute artifact output/report
- `041`：persisted write proof request/result 与显式确认 CLI surface
- `042`：persisted write proof artifact writer 与 execute artifact output/report
- `043`：final proof publication request/result 与显式确认 CLI surface
- `044`：final proof publication artifact writer 与 execute artifact output/report
- `045`：final proof closure request/result 与显式确认 CLI surface
- `046`：final proof closure artifact writer 与 execute artifact output/report

但 downstream archive artifact persistence 仍缺少稳定 truth：

- final proof closure artifact 已形成，但 final proof archive orchestration 何时允许执行、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进最终 archive，仍缺少统一 guard / result contract
- 若继续直接编码，容易把 final proof archive orchestration 与最终 archive artifact persistence 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Final Proof Archive Orchestration Baseline`：

- 先冻结 final proof archive orchestration 的 truth order、non-goals 与 explicit guard
- 再冻结 orchestration input contract、packaging 与 result reporting boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService final proof archive request/result packaging`，随后再进入 CLI execute surface。当前仍不直接进入 archive artifact persistence。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`046` final proof closure artifact、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- final proof archive orchestration 只能消费已落盘的 canonical final proof closure artifact truth
- execute 路径必须保留显式确认，不得把 archive orchestration 变成默认 side effect
- 当前 child work item 只定义 orchestration request/result 与 CLI result surface，不写 archive artifact
- 不得改写 `046` final proof closure artifact 或更上游 artifact truth

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Formal docs must be canonical before implementation | 先冻结 `047` 的 spec/plan/tasks，再进入代码 |
| Single-source-of-truth downstream handoff | 明确 `046` closure artifact 是唯一上游真值 |
| Explicit confirmation on operator-facing orchestration | archive orchestration 仅允许显式确认后 execute |
| No hidden persistence in orchestration baseline | 当前 work item 明确排除 archive artifact persistence |

## 项目结构

### 文档结构

```text
specs/047-frontend-program-final-proof-archive-orchestration-baseline/
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

### Phase 0：Formal baseline freeze

**目标**：将 frontend program final proof archive orchestration 从 `046` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/047/...` 文档改动。

### Phase 1：Final proof archive orchestration truth freeze

**目标**：锁定 final proof archive orchestration 在 `046 -> 047 -> future archive artifact persistence` 主线中的 truth order。  
**产物**：orchestration truth baseline、non-goals baseline、explicit guard baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Orchestration contract / result boundary freeze

**目标**：锁定 orchestration input contract、packaging 与 result honesty boundary。  
**产物**：archive request baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream archive artifact persistence handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService final proof archive packaging slice

**目标**：在 `ProgramService` 中落下 final proof archive request/result packaging。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program final proof archive CLI surface slice

**目标**：把 final proof archive 暴露到独立 CLI surface，要求显式确认，并输出 orchestration 结果。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 final proof archive request/result packaging
- 再把显式 final proof archive surface 暴露到 CLI
- archive artifact persistence 仍应作为后续 guarded child work item 单独承接
