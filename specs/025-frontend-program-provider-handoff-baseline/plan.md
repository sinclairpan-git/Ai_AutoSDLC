---
related_doc:
  - "specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md"
---
# 实施计划：Frontend Program Provider Handoff Baseline

**编号**：`025-frontend-program-provider-handoff-baseline` | **日期**：2026-04-03 | **规格**：specs/025-frontend-program-provider-handoff-baseline/spec.md

## 概述

本计划处理的是 `024` 之后的 frontend program provider handoff baseline，而不是继续扩张 `024` 的 writeback responsibility。当前仓库已经在上游锁定并实现了：

- `023`：program remediation runbook、bounded command dispatch 与独立 `program remediate`
- `024`：canonical remediation writeback artifact 与 explicit execute writeback surface

但 downstream provider 面仍缺少稳定 truth：

- remediation execute 完成后虽然有 canonical writeback artifact，但 provider/runtime 还没有稳定 handoff payload
- operator 和 automation 若继续推进 provider 处理，仍需要重新拼装 pending inputs、steps 和 next actions
- 若继续直接编码，容易把 provider handoff、provider runtime、页面代码改写与 registry 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Provider Handoff Baseline`：

- 先冻结 provider handoff runtime 的 truth order 与 non-goals
- 再冻结 handoff payload、writeback linkage 与 explicit human approval boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService provider handoff packaging`，先在 service 层落下 handoff payload/build；随后再进入 CLI/report surface。当前仍不直接进入 provider invocation、registry 或页面代码改写 runtime。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`024` remediation writeback artifact、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- provider handoff payload 只能消费既有 writeback truth，不得另造第二套 remediation context
- 当前阶段不默认启用 provider runtime、registry、cross-spec code writeback 或页面代码改写
- provider handoff 只能是只读 payload，不得伪装成 provider 已执行

## 项目结构

```text
specs/025-frontend-program-provider-handoff-baseline/
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
│   └── program_service.py                   # current slice: provider handoff payload packaging
└── cli/
    └── program_cmd.py                       # next slice: provider handoff CLI/report surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- provider handoff runtime 只消费 `024` canonical writeback artifact 与既有 remediation steps
- handoff payload 必须是只读、可复用、machine-consumable 的单一真值
- provider runtime、registry、页面代码改写与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 不改写 `023` execute truth 或 `024` writeback truth

未锁定上述决策前，不得进入 `025` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| handoff truth | 定义 provider handoff payload 字段、writeback linkage 与 source linkage | 不得改写 `024` writeback truth |
| service packaging | 定义 service 如何把 writeback artifact 翻译为 provider-friendly payload | 不得调用 provider/runtime 或代码改写 |
| explicit CLI surface | 定义 `program remediate` 或独立 surface 如何暴露 provider handoff | 不得偷渡成 provider 已执行 |
| downstream handoff | 定义 future provider/runtime/code-rewrite child work item 边界 | 不得把 provider invocation 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program provider handoff 从 `024` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/025/...` 文档改动。

### Phase 1：Provider handoff truth freeze

**目标**：锁定 provider handoff runtime 在 `024 -> 025 -> future provider runtime` 主线中的 truth order。  
**产物**：handoff truth baseline、non-goals baseline、writeback linkage baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Payload / explicit boundary freeze

**目标**：锁定 handoff payload、source linkage 与 explicit human approval boundary。  
**产物**：payload baseline、readonly boundary baseline、report boundary baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream provider runtime handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService provider handoff packaging slice

**目标**：在 `ProgramService` 中落下 provider handoff payload/build。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program provider handoff CLI surface slice

**目标**：把 provider handoff payload 暴露到 CLI/report surface，保持只读与显式交接。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 provider handoff payload、writeback linkage 与 source linkage
- 再把 handoff payload 暴露到 CLI/report surface
- provider runtime、registry、页面代码改写与 cross-spec code writeback 仍应作为后续 guarded child work item 单独承接
