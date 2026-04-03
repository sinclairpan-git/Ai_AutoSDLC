---
related_doc:
  - "specs/029-frontend-program-guarded-patch-apply-baseline/spec.md"
---
# 实施计划：Frontend Program Provider Patch Apply Artifact Baseline

**编号**：`030-frontend-program-provider-patch-apply-artifact-baseline` | **日期**：2026-04-03 | **规格**：specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md

## 概述

本计划处理的是 `029` 之后的 frontend program provider patch apply artifact baseline，而不是继续扩张 `029` 的 guarded patch apply responsibility。当前仓库已经在上游锁定并实现了：

- `024`：canonical remediation writeback artifact
- `025`：provider handoff payload 与 read-only CLI/report surface
- `026`：guarded provider runtime request/result 与显式确认 CLI surface
- `027`：provider runtime artifact writer 与 execute artifact output/report
- `028`：readonly provider patch handoff payload 与 CLI/report surface
- `029`：guarded patch apply request/result 与显式确认 CLI surface

但 downstream writeback orchestration 仍缺少稳定 truth：

- guarded patch apply result 目前只存在于内存对象和临时终端/report 输出中
- writeback orchestration 若继续推进，将缺少稳定的 apply artifact 可供复用
- 若继续直接编码，容易把 apply artifact、writeback orchestration 与 broader code rewrite 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Provider Patch Apply Artifact Baseline`：

- 先冻结 apply artifact 的 truth order、non-goals 与 write boundary
- 再冻结 artifact payload contract、source linkage 与 honest output boundary
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。下一步允许进入首批实现切片：`ProgramService patch apply artifact writer`，随后再进入 CLI execute/write surface。当前仍不直接进入 cross-spec writeback、registry 或 broader code rewrite orchestration。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`029` patch apply request/result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- apply artifact 只能消费既有 guarded patch apply truth，不得另造第二套 apply result context
- 当前阶段不默认启用 cross-spec writeback、registry 或 broader code rewrite orchestration
- artifact 只能在显式确认后的 execute 路径写出，并诚实回报状态

## 项目结构

```text
specs/030-frontend-program-provider-patch-apply-artifact-baseline/
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
│   └── program_service.py                   # current slice: apply artifact writer + loader boundary
└── cli/
    └── program_cmd.py                       # next slice: execute surface artifact output/report

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- apply artifact 只消费 `029` patch apply request/result truth
- artifact 只能在显式确认后的 execute 路径写出，dry-run 不得默认落盘
- cross-spec writeback、registry 与 broader code rewrite orchestration 仍留在下游 work item
- 当前 baseline 不改写 `029` patch apply truth 或更上游 truth

未锁定上述决策前，不得进入 `030` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| apply artifact truth | 定义 artifact path、payload contract 与 write boundary | 不得改写 `029` patch apply truth |
| service writer | 定义 service 如何把 request/result materialize 为 artifact | 不得直接进入 writeback orchestration |
| explicit CLI surface | 定义 execute 成功后 artifact output/report surface | 不得偷渡成默认 execute |
| downstream handoff | 定义 future writeback orchestration child work item 边界 | 不得把 broader orchestration engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program provider patch apply artifact 从 downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/030/...` 文档改动。

### Phase 1：Patch apply artifact truth freeze

**目标**：锁定 patch apply artifact 在 `029 -> 030 -> future writeback orchestration runtime` 主线中的 truth order。  
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
**产物**：implementation touchpoints、tests matrix、downstream writeback orchestration handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService patch apply artifact writer slice

**目标**：在 `ProgramService` 中落下 canonical patch apply artifact writer。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program patch apply artifact CLI surface slice

**目标**：把 patch apply artifact path/report 暴露到独立 CLI surface，并保持只在显式 execute 后写出。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 patch apply artifact writer / payload
- 再把 artifact output surface 暴露到 CLI
- cross-spec writeback、registry 与 broader code rewrite orchestration 仍应作为后续 guarded child work item 单独承接
