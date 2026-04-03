---
related_doc:
  - "specs/045-frontend-program-final-proof-closure-orchestration-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Closure Artifact Baseline

**编号**：`046-frontend-program-final-proof-closure-artifact-baseline` | **日期**：2026-04-03 | **规格**：specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md

## 概述

本计划处理的是 `045` 之后的 frontend program final proof closure artifact baseline，而不是继续扩张 `045` 的 orchestration responsibility。当前仓库已经在上游锁定并实现了：

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

但 downstream archive proof 仍缺少稳定 truth：

- final proof closure result 已形成，但 final proof closure artifact 何时允许写出、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进 archive proof，仍缺少统一 artifact contract
- 若继续直接编码，容易把 final proof closure orchestration、artifact 与 archive proof 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Final Proof Closure Artifact Baseline`：

- 先冻结 final proof closure artifact 的 truth order、non-goals 与 write boundary
- 再冻结 artifact input contract、writer boundary 与 result reporting
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService final proof closure artifact writer`，随后再进入 CLI artifact output surface。当前仍不直接进入 archive proof。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`045` final proof closure request/result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- final proof closure artifact 只能消费既有 final proof closure request/result truth，不得另造第二套 artifact context
- 当前阶段不默认启用 archive proof
- artifact 必须显式确认后写出，并诚实回报结果

## 项目结构

```text
specs/046-frontend-program-final-proof-closure-artifact-baseline/
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
│   └── program_service.py                   # current slice: final proof closure artifact writer
└── cli/
    └── program_cmd.py                       # next slice: explicit final proof closure artifact surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- final proof closure artifact 只消费 `045` final proof closure request/result truth
- artifact 只允许来自显式确认后的 execute 路径，且结果必须诚实回报
- archive proof 仍留在下游 work item
- 当前 baseline 不改写 `045` final proof closure truth 或更上游 truth

未锁定上述决策前，不得进入 `046` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| artifact truth | 定义 final proof closure artifact 输入、写边界与结果回报 | 不得改写 `045` final proof closure truth |
| service writer | 定义 service 如何把 request/result 翻译为 artifact payload | 不得直接进入 archive proof |
| explicit CLI surface | 定义 final proof closure artifact output/report 与确认流程 | 不得偷渡成默认 execute |
| downstream handoff | 定义 future archive proof child work item 边界 | 不得把 archive proof engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program final proof closure artifact 从 `045` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/046/...` 文档改动。

### Phase 1：Final proof closure artifact truth freeze

**目标**：锁定 final proof closure artifact 在 `045 -> 046 -> future archive proof` 主线中的 truth order。  
**产物**：artifact truth baseline、non-goals baseline、write boundary baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact writer / result boundary freeze

**目标**：锁定 artifact input contract、writer boundary 与 result honesty boundary。  
**产物**：artifact payload baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream archive proof handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService final proof closure artifact writer slice

**目标**：在 `ProgramService` 中落下 final proof closure artifact writer。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program final proof closure artifact output slice

**目标**：把 final proof closure artifact 暴露到独立 CLI surface，要求显式确认，并输出 artifact path / result。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 final proof closure artifact writer
- 再把显式 final proof closure artifact surface 暴露到 CLI
- archive proof 仍应作为后续 guarded child work item 单独承接
