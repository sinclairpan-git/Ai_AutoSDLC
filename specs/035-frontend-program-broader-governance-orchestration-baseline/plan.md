---
related_doc:
  - "specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md"
---
# 实施计划：Frontend Program Broader Governance Orchestration Baseline

**编号**：`035-frontend-program-broader-governance-orchestration-baseline` | **日期**：2026-04-03 | **规格**：specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md

## 概述

本计划处理的是 `034` 之后的 frontend program broader governance orchestration baseline，而不是继续扩张 `034` 的 registry artifact responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface
- `026`：guarded provider runtime request/result 与显式确认 CLI surface
- `027`：provider runtime artifact writer 与 execute artifact output/report
- `028`：readonly provider patch handoff payload 与 CLI/report surface
- `029`：guarded patch apply request/result 与显式确认 CLI surface
- `030`：patch apply artifact writer 与 execute artifact output/report
- `031`：guarded cross-spec writeback request/result 与显式确认 CLI surface
- `032`：cross-spec writeback artifact writer 与 execute artifact output/report
- `033`：guarded registry request/result 与显式确认 CLI surface
- `034`：guarded registry artifact writer 与 execute artifact output/report

但 downstream final governance execution 仍缺少稳定 truth：

- registry artifact 已形成，但 broader governance orchestration 何时允许执行、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进更宽的治理编排，仍缺少统一 guard / result contract
- 若继续直接编码，容易把 broader governance orchestration 与 final code rewrite / governance execution 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Broader Governance Orchestration Baseline`：

- 先冻结 broader governance orchestration 的 truth order、non-goals 与 explicit guard
- 再冻结 orchestration input contract、packaging 与 result reporting boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService broader governance request/result packaging`，随后再进入 CLI execute surface。当前仍不直接进入 final code rewrite / governance execution。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`034` guarded registry artifact、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- broader governance orchestration 只能消费既有 registry artifact truth，不得另造第二套 orchestration context
- 当前阶段不默认启用 final code rewrite / governance execution
- orchestration 必须显式确认，并诚实回报结果

## 项目结构

```text
specs/035-frontend-program-broader-governance-orchestration-baseline/
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
│   └── program_service.py                   # current slice: broader governance request + result packaging
└── cli/
    └── program_cmd.py                       # next slice: explicit broader governance surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- broader governance orchestration 只消费 `034` guarded registry artifact truth
- orchestration 必须显式确认，且结果必须诚实回报
- final code rewrite / governance execution 仍留在下游 work item
- 当前 baseline 不改写 `034` registry artifact truth 或更上游 truth

未锁定上述决策前，不得进入 `035` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| orchestration truth | 定义 broader governance 输入、确认边界与结果回报 | 不得改写 `034` registry artifact truth |
| service packaging | 定义 service 如何把 artifact 翻译为 broader governance request/result | 不得直接进入 final governance execution |
| explicit CLI surface | 定义 broader governance execute/dry-run surface 与确认流程 | 不得偷渡成默认 execute |
| downstream handoff | 定义 future final governance child work item 边界 | 不得把 final governance engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program broader governance orchestration 从 `034` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/035/...` 文档改动。

### Phase 1：Broader governance orchestration truth freeze

**目标**：锁定 broader governance orchestration 在 `034 -> 035 -> future final governance execution` 主线中的 truth order。  
**产物**：orchestration truth baseline、non-goals baseline、explicit guard baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Orchestration contract / result boundary freeze

**目标**：锁定 orchestration input contract、packaging 与 result honesty boundary。  
**产物**：broader governance request baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream final governance handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService broader governance packaging slice

**目标**：在 `ProgramService` 中落下 broader governance request/result packaging。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program broader governance CLI surface slice

**目标**：把 broader governance 暴露到独立 CLI surface，要求显式确认，并输出 orchestration 结果。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 broader governance request/result packaging
- 再把显式 broader governance surface 暴露到 CLI
- final code rewrite / governance execution 仍应作为后续 guarded child work item 单独承接
