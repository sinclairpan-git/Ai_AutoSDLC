---
related_doc:
  - "specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md"
---
# 实施计划：Frontend Program Provider Patch Handoff Baseline

**编号**：`028-frontend-program-provider-patch-handoff-baseline` | **日期**：2026-04-03 | **规格**：specs/028-frontend-program-provider-patch-handoff-baseline/spec.md

## 概述

本计划处理的是 `027` 之后的 frontend program provider patch handoff baseline，而不是继续扩张 `027` 的 runtime artifact responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface
- `026`：guarded provider runtime request/result 与显式确认 CLI surface
- `027`：provider runtime artifact writer 与 execute artifact output/report

但 downstream patch-review/apply 仍缺少稳定 handoff truth：

- provider runtime artifact 已存在，但缺少面向 patch-review/apply 的只读 handoff contract
- future patch apply 若继续推进，将缺少稳定的 patch handoff payload 可复用
- 若继续直接编码，容易把 runtime artifact、patch handoff、patch apply 与 code writeback 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Provider Patch Handoff Baseline`：

- 先冻结 patch handoff 的 truth order、non-goals 与 readonly boundary
- 再冻结 handoff payload contract、patch availability state 与 honest output boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService provider patch handoff packaging`，随后再进入 CLI readonly handoff surface。当前仍不直接进入 patch apply、页面代码改写或 cross-spec code writeback。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`027` provider runtime artifact、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- patch handoff 只能消费既有 provider runtime artifact truth，不得另造第二套 patch context
- 当前阶段不默认启用 patch apply、registry、页面代码改写或 cross-spec code writeback
- handoff 必须保持只读，并诚实回报 patch availability 与 blockers

## 项目结构

```text
specs/028-frontend-program-provider-patch-handoff-baseline/
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
│   └── program_service.py                   # current slice: patch handoff payload/build
└── cli/
    └── program_cmd.py                       # next slice: readonly patch handoff surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- patch handoff 只消费 `027` provider runtime artifact truth
- handoff 保持只读，不得默认触发 patch apply、页面代码改写或 cross-spec code writeback
- patch apply、registry、页面代码改写与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 不改写 `027` runtime artifact truth 或更上游 truth

未锁定上述决策前，不得进入 `028` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| patch handoff truth | 定义 handoff payload、patch availability state 与 readonly boundary | 不得改写 `027` runtime artifact truth |
| service packaging | 定义 service 如何把 runtime artifact 翻译为 patch handoff | 不得直接进入 patch apply |
| explicit CLI surface | 定义 readonly handoff 展示与 report surface | 不得偷渡成默认 apply surface |
| downstream handoff | 定义 future patch apply/writeback child work item 边界 | 不得把 apply engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program provider patch handoff 从 downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/028/...` 文档改动。

### Phase 1：Patch handoff truth freeze

**目标**：锁定 provider patch handoff 在 `027 -> 028 -> future patch-apply runtime` 主线中的 truth order。  
**产物**：handoff truth baseline、non-goals baseline、readonly boundary baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Handoff contract / output boundary freeze

**目标**：锁定 handoff payload contract、patch availability state 与 honest output boundary。  
**产物**：handoff payload baseline、CLI/report output baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream patch apply handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService provider patch handoff packaging slice

**目标**：在 `ProgramService` 中落下 readonly provider patch handoff payload/build。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program provider patch handoff CLI surface slice

**目标**：把 readonly provider patch handoff 暴露到独立 CLI surface 与 report，不进入 apply side effect。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 readonly provider patch handoff payload/build
- 再把 handoff output surface 暴露到 CLI
- patch apply、页面代码改写与 cross-spec code writeback 仍应作为后续 guarded child work item 单独承接
