---
related_doc:
  - "specs/037-frontend-program-final-governance-orchestration-baseline/spec.md"
---
# 实施计划：Frontend Program Final Governance Artifact Baseline

**编号**：`038-frontend-program-final-governance-artifact-baseline` | **日期**：2026-04-03 | **规格**：specs/038-frontend-program-final-governance-artifact-baseline/spec.md

## 概述

本计划处理的是 `037` 之后的 frontend program final governance artifact baseline，而不是继续扩张 `037` 的 execute responsibility。当前仓库已经在上游锁定并实现了：

- `024` 到 `034`：remediation / provider / patch / writeback / registry 的 orchestration 与 artifact 链路
- `035`：broader governance request/result 与显式确认 CLI surface
- `036`：broader governance artifact writer 与 execute artifact output/report
- `037`：final governance request/result 与显式确认 CLI surface

但 downstream persistence 仍缺少稳定 truth：

- final governance result 已形成，但如何持久化成 downstream 可消费的 artifact 还没有 canonical baseline
- operator 和 automation 若继续推进真实代码改写，仍缺少统一 artifact truth
- 若继续直接编码，容易把 final governance artifact 与真实代码改写 / persistence 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Final Governance Artifact Baseline`：

- 先冻结 final governance artifact 的 truth order、non-goals 与 write boundary
- 再冻结 artifact input contract、payload 与 result honesty boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService final governance artifact writer`，随后再进入 CLI artifact output surface。当前仍不直接进入 code rewrite persistence / writeback artifact。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`037` final governance request/result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- final governance artifact 只能消费既有 final governance truth，不得另造第二套 artifact context
- 当前阶段不默认启用真实代码改写 / writeback persistence
- artifact 必须诚实回报结果

## 项目结构

```text
specs/038-frontend-program-final-governance-artifact-baseline/
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
│   └── program_service.py                   # current slice: final governance artifact writer
└── cli/
    └── program_cmd.py                       # next slice: explicit final governance artifact surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- final governance artifact 只消费 `037` final governance request/result truth
- artifact 只能发生在显式确认后的 execute 路径
- 真实代码改写 / writeback persistence 仍留在下游 work item
- 当前 baseline 不改写 `037` final governance truth 或更上游 truth

未锁定上述决策前，不得进入 `038` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| artifact truth | 定义 final governance artifact 输入、输出与写边界 | 不得改写 `037` final governance truth |
| service writer | 定义 service 如何把 request/result 翻译为 canonical artifact | 不得直接进入真实代码改写 / persistence |
| explicit CLI surface | 定义 artifact output/report surface | 不得偷渡成默认 execute |
| downstream handoff | 定义 future writeback persistence child work item 边界 | 不得把 persistence engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program final governance artifact 从 `037` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/038/...` 文档改动。

### Phase 1：Final governance artifact truth freeze

**目标**：锁定 final governance artifact 在 `037 -> 038 -> future writeback persistence` 主线中的 truth order。  
**产物**：artifact truth baseline、non-goals baseline、write boundary baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact contract / output boundary freeze

**目标**：锁定 artifact input contract、payload 与 result honesty boundary。  
**产物**：artifact input baseline、payload baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream writeback persistence handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService final governance artifact writer slice

**目标**：在 `ProgramService` 中落下 final governance artifact writer。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program final governance artifact CLI surface slice

**目标**：把 final governance artifact 暴露到独立 CLI surface，并输出 artifact path / report。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 final governance artifact writer
- 再把 execute artifact surface 暴露到 CLI
- 真实代码改写 / writeback persistence 仍应作为后续 guarded child work item 单独承接
