---
related_doc:
  - "specs/028-frontend-program-provider-patch-handoff-baseline/spec.md"
---
# 实施计划：Frontend Program Guarded Patch Apply Baseline

**编号**：`029-frontend-program-guarded-patch-apply-baseline` | **日期**：2026-04-03 | **规格**：specs/029-frontend-program-guarded-patch-apply-baseline/spec.md

## 概述

本计划处理的是 `028` 之后的 frontend program guarded patch apply baseline，而不是继续扩张 `028` 的 readonly patch handoff responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface
- `026`：guarded provider runtime request/result 与显式确认 CLI surface
- `027`：provider runtime artifact writer 与 execute artifact output/report
- `028`：readonly provider patch handoff payload 与 CLI/report surface

但 downstream patch execution 面仍缺少稳定 truth：

- patch handoff 已形成，但 apply 何时允许执行、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进 patch apply，仍缺少统一 guard / result contract
- 若继续直接编码，容易把 patch apply、cross-spec code writeback 与更宽的 code rewrite orchestration 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Guarded Patch Apply Baseline`：

- 先冻结 patch apply 的 truth order、non-goals 与 explicit guard
- 再冻结 apply input contract、apply packaging 与 result reporting boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService guarded patch apply request/result packaging`，随后再进入 CLI execute surface。当前仍不直接进入 cross-spec writeback、registry 或更宽的 code rewrite orchestration。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`028` provider patch handoff payload、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- guarded patch apply 只能消费既有 patch handoff truth，不得另造第二套 patch/apply context
- 当前阶段不默认启用 cross-spec writeback、registry 或更宽的 code rewrite orchestration
- apply 必须显式确认，并诚实回报结果

## 项目结构

```text
specs/029-frontend-program-guarded-patch-apply-baseline/
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
│   └── program_service.py                   # current slice: apply request + result packaging
└── cli/
    └── program_cmd.py                       # next slice: explicit patch apply surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- patch apply 只消费 `028` provider patch handoff truth
- apply 必须显式确认，且结果必须诚实回报
- cross-spec writeback、registry 与更宽的 code rewrite orchestration 仍留在下游 work item
- 当前 baseline 不改写 `028` patch handoff truth 或更上游 truth

未锁定上述决策前，不得进入 `029` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| apply truth | 定义 guarded patch apply 输入、确认边界与结果回报 | 不得改写 `028` patch handoff truth |
| service packaging | 定义 service 如何把 handoff payload 翻译为 patch apply request/result | 不得直接进入 cross-spec writeback orchestration |
| explicit CLI surface | 定义 apply execute/dry-run surface 与确认流程 | 不得偷渡成默认 execute |
| downstream handoff | 定义 future cross-spec writeback child work item 边界 | 不得把 broader writeback engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program guarded patch apply 从 `028` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/029/...` 文档改动。

### Phase 1：Patch apply truth freeze

**目标**：锁定 patch apply 在 `028 -> 029 -> future cross-spec writeback runtime` 主线中的 truth order。  
**产物**：apply truth baseline、non-goals baseline、explicit guard baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Apply contract / result boundary freeze

**目标**：锁定 apply input contract、apply packaging 与 result honesty boundary。  
**产物**：apply request baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream cross-spec writeback handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService guarded patch apply packaging slice

**目标**：在 `ProgramService` 中落下 guarded patch apply request/result packaging。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program guarded patch apply CLI surface slice

**目标**：把 guarded patch apply 暴露到独立 CLI surface，要求显式确认，并输出 apply 结果。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 guarded patch apply request/result packaging
- 再把显式 apply surface 暴露到 CLI
- cross-spec writeback、registry 与更宽的 code rewrite orchestration 仍应作为后续 guarded child work item 单独承接
