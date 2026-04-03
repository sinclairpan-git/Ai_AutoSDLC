---
related_doc:
  - "specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md"
---
# 实施计划：Frontend Program Bounded Remediation Writeback Baseline

**编号**：`024-frontend-program-bounded-remediation-writeback-baseline` | **日期**：2026-04-03 | **规格**：specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md

## 概述

本计划处理的是 `023` 之后的 frontend program bounded remediation writeback baseline，而不是继续扩张 `023` 的 execute responsibility。当前仓库已经在上游锁定并实现了：

- `021`：program remediation input packaging 与 handoff surface
- `022`：governance materialization command surface 与 remediation command binding
- `023`：program remediation runbook、bounded command dispatch 与独立 `program remediate`

但 remediation execute 结束后仍缺少稳定 writeback truth：

- operator 只能依赖终端输出和可选 Markdown report，automation 没有 canonical artifact 可消费
- `program remediate --execute` 还没有 formal baseline 说明默认写回路径、字段结构与写回条件
- remediation execute 与 writeback truth 仍混在 CLI 文案里，没有 machine-consumable baseline
- 若继续直接编码，容易把 writeback、auto-fix、provider runtime、registry 与页面代码改写混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Bounded Remediation Writeback Baseline`：

- 先冻结 remediation writeback runtime 的 truth order 与 non-goals
- 再冻结 canonical artifact path、payload shape 与 writeback honesty 语义
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进后，当前允许继续进入首批实现切片：`ProgramService canonical remediation writeback emission`，先在 service 层落下 writeback payload/build + artifact persist；随后再进入 CLI surface。当前仍不直接进入 provider runtime、code rewrite engine 或 cross-spec code writeback。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`023` remediation runbook + execute result、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- writeback artifact 只能消费既有 remediation execute truth，不得另造第二套 runbook system
- 当前阶段不默认启用 provider runtime、registry、cross-spec code writeback 或页面代码改写
- canonical writeback 只能发生在显式 remediation execute 之后
- bounded remediation writeback 不等于完整 auto-fix engine

## 项目结构

```text
specs/024-frontend-program-bounded-remediation-writeback-baseline/
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
│   └── program_service.py                   # current slice: writeback payload + artifact emission
└── cli/
    └── program_cmd.py                       # next slice: CLI writeback surface/output

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- remediation writeback runtime 只消费 `023` remediation runbook 与 execute result，不另造第二套 truth
- canonical artifact 必须有稳定默认路径，并可被 downstream automation 直接消费
- bounded writeback 必须独立于默认 `program integrate --execute`
- provider runtime、registry、页面代码改写与 cross-spec code writeback 仍留在下游 work item
- 当前 baseline 不改写 `023` execute truth，只在既有 remediation execute surface 上补 canonical writeback

未锁定上述决策前，不得进入 `024` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| writeback truth | 定义 canonical writeback artifact 的字段、默认路径与 source linkage | 不得改写 `023` remediation execute truth |
| service emission | 定义 service 如何从既有 execute result 构建并落盘 writeback artifact | 不得引入任意代码改写或 provider runtime |
| explicit CLI surface | 定义 `program remediate` 在 execute 后如何输出 writeback path 与结果 | 不得偷渡到默认 `program integrate --execute` |
| downstream handoff | 定义 future automation / provider / code rewrite child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program bounded remediation writeback 从 `023` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/024/...` 文档改动。

### Phase 1：Writeback truth freeze

**目标**：锁定 remediation writeback runtime 在 `023 -> 024 -> future auto-fix/provider` 主线中的 truth order。  
**产物**：artifact truth baseline、non-goals baseline、default path baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact / explicit boundary freeze

**目标**：锁定 canonical artifact payload、writeback honesty 与 explicit execute boundary。  
**产物**：artifact payload baseline、writeback timing baseline、report boundary baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream provider/code-rewrite handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService canonical remediation writeback slice

**目标**：在 `ProgramService` 中落下 canonical remediation writeback payload/build 与 artifact persist。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program remediate writeback CLI surface slice

**目标**：把 canonical remediation writeback path / artifact result 暴露到独立 `program remediate` execute surface，并保持 dry-run 只读。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Writeback truth freeze

**范围**：truth order、non-goals、default path 与 canonical payload。  
**影响范围**：后续 service emission、CLI execute surface 与 automation handoff。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Artifact / explicit boundary freeze

**范围**：writeback artifact、writeback honesty、report boundary 与 explicit execute timing。  
**影响范围**：后续 `program_service.py` 与 `program_cmd.py`。  
**验证方式**：contract review。  
**回退方式**：不创建 provider/code rewrite side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream provider/code-rewrite handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 provider runtime 或 code writeback 实现。

### 工作流 D：ProgramService canonical remediation writeback slice

**范围**：writeback payload、canonical artifact persist、execute result reuse。
**影响范围**：为 CLI execute 提供统一 machine-consumable writeback truth。
**验证方式**：`tests/unit/test_program_service.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不引入页面代码改写、provider runtime 或任意 shell execute。

### 工作流 E：Program remediate writeback CLI surface slice

**范围**：`program remediate` execute 后的 writeback path 输出、artifact surface 与 report coordination。
**影响范围**：operator-facing remediation writeback，可见性与 automation 提升但不新增默认 auto-fix/code writeback。
**验证方式**：`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不挂接到默认 `program integrate --execute`。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| writeback truth order | 文档交叉引用检查 | 人工审阅 |
| canonical artifact clarity | formal wording review | 人工审阅 |
| explicit execute boundary | contract review | file-map review |
| service writeback correctness | `uv run pytest tests/unit/test_program_service.py -q` | artifact payload review |
| CLI writeback correctness | `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / artifact review |
| downstream provider/code-rewrite handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 canonical remediation writeback payload、默认路径与 artifact emission
- 再把 writeback path / artifact result 暴露到 `program remediate --execute --yes`
- provider runtime、页面代码改写与 cross-spec code writeback 仍应作为后续 guarded child work item 单独承接
