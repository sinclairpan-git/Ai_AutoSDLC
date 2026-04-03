---
related_doc:
  - "specs/041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md"
---
# 实施计划：Frontend Program Persisted Write Proof Artifact Baseline

**编号**：`042-frontend-program-persisted-write-proof-artifact-baseline` | **日期**：2026-04-03 | **规格**：specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md

## 概述

本计划处理的是 `041` 之后的 frontend program persisted write proof artifact baseline，而不是继续扩张 `041` 的 orchestration responsibility。当前仓库已经在上游锁定并实现了：

- `024` 到 `034`：remediation / provider / patch / writeback / registry 的 orchestration 与 artifact 链路
- `035`：broader governance request/result 与显式确认 CLI surface
- `036`：broader governance artifact writer 与 execute artifact output/report
- `037`：final governance request/result 与显式确认 CLI surface
- `038`：final governance artifact writer 与 execute artifact output/report
- `039`：writeback persistence request/result 与显式确认 CLI surface
- `040`：writeback persistence artifact writer 与 execute artifact output/report
- `041`：persisted write proof request/result 与显式确认 CLI surface

但 downstream final proof publication / closure 仍缺少稳定 truth：

- persisted write proof result 已形成，但 persisted write proof artifact 何时允许写出、如何确认、如何回报结果还没有 canonical baseline
- operator 和 automation 若继续推进 final proof，仍缺少统一 artifact contract
- 若继续直接编码，容易把 persisted write proof orchestration、artifact 与最终 proof publication 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Persisted Write Proof Artifact Baseline`：

- 先冻结 persisted write proof artifact 的 truth order、non-goals 与 write boundary
- 再冻结 artifact input contract、writer boundary 与 result reporting
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService persisted write proof artifact writer`，随后再进入 CLI artifact output surface。当前仍不直接进入 final proof publication / closure。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`041` persisted write proof request/result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- persisted write proof artifact 只能消费既有 persisted write proof request/result truth，不得另造第二套 artifact context
- 当前阶段不默认启用 final proof publication / closure
- artifact 必须显式确认后写出，并诚实回报结果

## 项目结构

```text
specs/042-frontend-program-persisted-write-proof-artifact-baseline/
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
│   └── program_service.py                   # current slice: persisted write proof artifact writer
└── cli/
    └── program_cmd.py                       # next slice: explicit persisted write proof artifact surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- persisted write proof artifact 只消费 `041` persisted write proof request/result truth
- artifact 只允许来自显式确认后的 execute 路径，且结果必须诚实回报
- final proof publication / closure 仍留在下游 work item
- 当前 baseline 不改写 `041` persisted write proof truth 或更上游 truth

未锁定上述决策前，不得进入 `042` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| artifact truth | 定义 persisted write proof artifact 输入、写边界与结果回报 | 不得改写 `041` persisted write proof truth |
| service writer | 定义 service 如何把 request/result 翻译为 artifact payload | 不得直接进入 final proof publication / closure |
| explicit CLI surface | 定义 persisted write proof artifact output/report 与确认流程 | 不得偷渡成默认 execute |
| downstream handoff | 定义 future final proof publication / closure child work item 边界 | 不得把 final proof engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program persisted write proof artifact 从 `041` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/042/...` 文档改动。

### Phase 1：Persisted write proof artifact truth freeze

**目标**：锁定 persisted write proof artifact 在 `041 -> 042 -> future final proof publication` 主线中的 truth order。  
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
**产物**：implementation touchpoints、tests matrix、downstream final proof publication handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService persisted write proof artifact writer slice

**目标**：在 `ProgramService` 中落下 persisted write proof artifact writer。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program persisted write proof artifact output slice

**目标**：把 persisted write proof artifact 暴露到独立 CLI surface，要求显式确认，并输出 artifact path / result。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 persisted write proof artifact writer
- 再把显式 persisted write proof artifact surface 暴露到 CLI
- final proof publication / closure 仍应作为后续 guarded child work item 单独承接
