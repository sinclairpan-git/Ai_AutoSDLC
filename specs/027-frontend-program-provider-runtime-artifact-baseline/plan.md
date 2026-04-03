---
related_doc:
  - "specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md"
---
# 实施计划：Frontend Program Provider Runtime Artifact Baseline

**编号**：`027-frontend-program-provider-runtime-artifact-baseline` | **日期**：2026-04-03 | **规格**：specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md

## 概述

本计划处理的是 `026` 之后的 frontend program provider runtime artifact baseline，而不是继续扩张 `026` 的 guarded runtime responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface
- `026`：guarded provider runtime request/result 与显式确认 CLI surface

但 downstream patch handoff/apply 仍缺少稳定 truth：

- guarded provider runtime result 目前只存在于内存对象和临时终端/report 输出中
- patch handoff 若继续推进，将缺少稳定的 provider runtime artifact 可供复用
- 若继续直接编码，容易把 runtime artifact、patch handoff、patch apply 与 code rewrite 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Provider Runtime Artifact Baseline`：

- 先冻结 runtime artifact 的 truth order、non-goals 与 write boundary
- 再冻结 artifact payload contract、source linkage 与 honest output boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService provider runtime artifact writer`，随后再进入 CLI execute/write surface。当前仍不直接进入 provider patch handoff、patch apply、页面代码改写或 cross-spec code writeback。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`026` provider runtime request/result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- runtime artifact 只能消费既有 guarded provider runtime truth，不得另造第二套 provider result context
- 当前阶段不默认启用 provider patch handoff、patch apply、registry、页面代码改写或 cross-spec code writeback
- artifact 只能在显式确认后的 execute 路径写出，并诚实回报状态

## 项目结构

```text
specs/027-frontend-program-provider-runtime-artifact-baseline/
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
│   └── program_service.py                   # current slice: runtime artifact writer + loader boundary
└── cli/
    └── program_cmd.py                       # next slice: execute surface artifact output/report

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- runtime artifact 只消费 `026` provider runtime request/result truth
- artifact 只能在显式确认后的 execute 路径写出，dry-run 不得默认落盘
- provider patch handoff、patch apply、registry、页面代码改写与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 不改写 `024` remediation writeback truth、`025` provider handoff truth 或 `026` runtime truth

未锁定上述决策前，不得进入 `027` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| runtime artifact truth | 定义 artifact path、payload contract 与 write boundary | 不得改写 `026` runtime truth |
| service writer | 定义 service 如何把 request/result materialize 为 artifact | 不得直接进入 patch handoff/apply |
| explicit CLI surface | 定义 execute 成功后 artifact output/report surface | 不得偷渡成默认 execute |
| downstream handoff | 定义 future patch handoff/apply child work item 边界 | 不得把 patch apply engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program provider runtime artifact 从 downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/027/...` 文档改动。

### Phase 1：Runtime artifact truth freeze

**目标**：锁定 provider runtime artifact 在 `026 -> 027 -> future patch-handoff/apply runtime` 主线中的 truth order。  
**产物**：artifact truth baseline、non-goals baseline、write boundary baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact contract / output boundary freeze

**目标**：锁定 artifact payload contract、source linkage 与 honest output boundary。  
**产物**：artifact payload baseline、CLI/report output baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream patch handoff/apply handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService provider runtime artifact writer slice

**目标**：在 `ProgramService` 中落下 canonical provider runtime artifact writer。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program provider runtime artifact CLI surface slice

**目标**：把 runtime artifact path/report 暴露到独立 CLI surface，并保持只在显式 execute 后写出。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 provider runtime artifact writer / payload
- 再把 artifact output surface 暴露到 CLI
- provider patch handoff、patch apply、页面代码改写与 cross-spec code writeback 仍应作为后续 guarded child work item 单独承接
