---
related_doc:
  - "specs/025-frontend-program-provider-handoff-baseline/spec.md"
---
# 实施计划：Frontend Program Guarded Provider Runtime Baseline

**编号**：`026-frontend-program-guarded-provider-runtime-baseline` | **日期**：2026-04-03 | **规格**：specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md

## 概述

本计划处理的是 `025` 之后的 frontend program guarded provider runtime baseline，而不是继续扩张 `025` 的 provider handoff responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface

但 downstream provider execute 面仍缺少稳定 truth：

- provider handoff 已形成，但 runtime 何时允许执行、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进 provider 处理，仍缺少统一 guard / result contract
- 若继续直接编码，容易把 provider runtime、页面代码改写、cross-spec code writeback 与 registry 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Guarded Provider Runtime Baseline`：

- 先冻结 provider runtime 的 truth order、non-goals 与 explicit guard
- 再冻结 runtime input contract、provider invocation packaging 与 result reporting boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService guarded provider runtime request packaging`，随后再进入 CLI execute surface。当前仍不直接进入页面代码改写、patch application 或 cross-spec writeback。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`025` provider handoff payload、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- guarded provider runtime 只能消费既有 provider handoff truth，不得另造第二套 provider context
- 当前阶段不默认启用页面代码改写、registry、cross-spec code writeback 或默认 provider auto execution
- runtime 必须显式确认，并诚实回报结果

## 项目结构

```text
specs/026-frontend-program-guarded-provider-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py
└── cli/
    └── program_cmd.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py                   # current slice: runtime request + result packaging
└── cli/
    └── program_cmd.py                       # next slice: explicit provider runtime surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- provider runtime 只消费 `025` provider handoff payload
- runtime 必须显式确认，且结果必须诚实回报
- 页面代码改写、patch application、registry 与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 不改写 `024` writeback truth 或 `025` handoff truth

未锁定上述决策前，不得进入 `026` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| runtime truth | 定义 guarded provider runtime 输入、确认边界与结果回报 | 不得改写 `025` provider handoff truth |
| service packaging | 定义 service 如何把 handoff payload 翻译为 provider runtime request/result | 不得直接改写页面代码 |
| explicit CLI surface | 定义 runtime execute/dry-run surface 与确认流程 | 不得偷渡成默认 execute |
| downstream handoff | 定义 future code-rewrite/writeback child work item 边界 | 不得把 code rewrite engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program guarded provider runtime 从 `025` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/026/...` 文档改动。

### Phase 1：Provider runtime truth freeze

**目标**：锁定 provider runtime 在 `025 -> 026 -> future code-rewrite runtime` 主线中的 truth order。  
**产物**：runtime truth baseline、non-goals baseline、explicit guard baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Runtime contract / result boundary freeze

**目标**：锁定 runtime input contract、provider invocation packaging 与 result honesty boundary。  
**产物**：runtime request baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream code-rewrite runtime handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService guarded provider runtime packaging slice

**目标**：在 `ProgramService` 中落下 guarded provider runtime request/result packaging。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program guarded provider runtime CLI surface slice

**目标**：把 guarded provider runtime 暴露到独立 CLI surface，要求显式确认，并输出 provider runtime 结果。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 guarded provider runtime request/result packaging
- 再把显式 runtime surface 暴露到 CLI
- 页面代码改写、patch application 与 cross-spec code writeback 仍应作为后续 guarded child work item 单独承接
