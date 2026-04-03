---
related_doc:
  - "specs/021-frontend-program-remediation-runtime-baseline/spec.md"
  - "specs/022-frontend-governance-materialization-runtime-baseline/spec.md"
---
# 实施计划：Frontend Program Bounded Remediation Execute Baseline

**编号**：`023-frontend-program-bounded-remediation-execute-baseline` | **日期**：2026-04-03 | **规格**：specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md

## 概述

本计划处理的是 `022` 之后的 frontend program bounded remediation execute baseline，而不是继续扩张 `022` 的 command binding responsibility。当前仓库已经在上游锁定并实现了：

- `021`：program remediation input packaging 与 handoff surface
- `022`：governance materialization command surface 与 remediation command binding

但 operator-facing bounded execute 仍缺少独立 child work item 去冻结：

- operator 只能手动复制 remediation commands，program 还没有显式确认下的 bounded remediation execute 入口
- `program integrate --execute` 仍只负责 gate / handoff，不负责 remediation commands 的受控 dispatch
- remediation execute 还没有 formal baseline 说明哪些 commands 允许被 runtime 调度、如何汇总结果
- 若继续直接编码，容易把 remediation execute、auto-fix、writeback 与 program execute side effect 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Bounded Remediation Execute Baseline`：

- 先冻结 remediation execute runtime 的 truth order 与 non-goals
- 再冻结 runbook、bounded command dispatch 与结果回报责任
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入首批实现切片：`ProgramService remediation runbook and bounded dispatch`，先在 service 层落下 runbook 聚合与已知命令 dispatch；随后再进入 `program remediate` CLI surface。当前仍不直接进入完整 auto-fix engine、writeback runtime 或 provider orchestration。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`021` remediation payload、`022` command surface、现有 `ProgramService` / `program_cmd.py` / scanner + governance builders  
**主要约束**：

- remediation execute runtime 只能消费既有 remediation truth，不得另造第二套 runbook truth
- 当前阶段不默认启用 provider runtime、registry、cross-spec writeback 或页面代码改写
- remediation execute 必须显式确认
- bounded remediation execute 不等于完整 auto-fix engine

## 项目结构

```text
specs/023-frontend-program-bounded-remediation-execute-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── cli/
│   ├── program_cmd.py
│   └── sub_apps.py
├── core/
│   └── program_service.py
├── scanners/
│   └── frontend_contract_scanner.py
└── generators/
    ├── frontend_gate_policy_artifacts.py
    └── frontend_generation_constraint_artifacts.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py                   # current slice: remediation runbook + bounded dispatch
└── cli/
    └── program_cmd.py                       # next slice: explicit program remediate surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- remediation execute runtime 只消费 `021` remediation payload 与 `022` recommended commands，不另造第二套 command truth
- 首批 runtime 只允许调度已知 bounded commands：frontend contract scanner export、frontend governance materialization、verify constraints
- bounded remediation execute 必须独立于 `program integrate --execute`
- auto-fix engine、registry、provider runtime 与 writeback 仍留在下游 work item
- 当前 baseline 不改写 `020` execute gate truth，只在既有 remediation surface 上补显式 execute 入口

未锁定上述决策前，不得进入 `023` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| remediation runbook truth | 定义 per-spec remediation execute runbook 与 shared follow-up commands | 不得改写 `021` remediation payload truth |
| bounded command dispatch | 定义哪些 known commands 允许被 runtime 调度、如何执行与回报 | 不得透传任意 shell command |
| explicit CLI surface | 定义 `program remediate` 的确认、dry-run、execute 与输出边界 | 不得偷渡到 `program integrate --execute` |
| downstream handoff | 定义推荐文件面、测试矩阵与 future auto-fix child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program bounded remediation execute 从 `022` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/023/...` 文档改动。

### Phase 1：Remediation execute truth freeze

**目标**：锁定 remediation execute runtime 在 `021 / 022 -> 023 -> future auto-fix` 主线中的 truth order。  
**产物**：execute truth baseline、non-goals baseline、bounded command set baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Runbook / bounded dispatch responsibility freeze

**目标**：锁定 remediation runbook、bounded command dispatch 与 execute honesty 语义。  
**产物**：runbook baseline、dispatch baseline、result reporting baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream auto-fix handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService remediation runbook and bounded dispatch slice

**目标**：在 `ProgramService` 中落下 remediation runbook 聚合、known command dispatch 与 execute result reporting。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program remediate explicit CLI surface slice

**目标**：把 remediation runbook 与 bounded execute 暴露为独立 `program remediate` CLI surface，要求显式确认，并输出 dry-run / execute 结果。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Remediation execute truth freeze

**范围**：truth order、non-goals、known command set 与 explicit confirmation boundary。  
**影响范围**：后续 runbook、bounded dispatch 与 CLI execute surface。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Runbook / bounded dispatch responsibility freeze

**范围**：runbook、known command dispatch、result reporting 与 execute honesty。  
**影响范围**：后续 `program_service.py` 与 `program_cmd.py`。  
**验证方式**：contract review。  
**回退方式**：不创建 auto-fix side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream auto-fix handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 auto-fix runtime 实现。

### 工作流 D：ProgramService remediation runbook and bounded dispatch slice

**范围**：per-spec remediation runbook、known command dispatch、execute result reporting。
**影响范围**：为 CLI `program remediate` 提供统一 data source 与 bounded execution backend。
**验证方式**：`tests/unit/test_program_service.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不引入任意 shell dispatch。

### 工作流 E：Program remediate explicit CLI surface slice

**范围**：`program remediate` dry-run / execute / confirm / report surface。
**影响范围**：operator-facing remediation execute，可见性与 automation 提升但不新增默认 auto-fix/writeback。
**验证方式**：`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不挂接到默认 `program integrate --execute`。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| remediation execute truth order | 文档交叉引用检查 | 人工审阅 |
| runbook clarity | formal wording review | 人工审阅 |
| bounded command dispatch honesty | contract review | file-map review |
| explicit confirmation boundary | tests + CLI review | 人工审阅 |
| downstream auto-fix handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |
| ProgramService runbook/dispatch correctness | `uv run pytest tests/unit/test_program_service.py -q` | written paths / blocker review |
| program remediate CLI correctness | `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / artifact review |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 remediation runbook、known command dispatch 与 execute result
- 再把 `program remediate` 暴露到 CLI，并要求 `--yes` 显式确认
- auto-fix engine、writeback 与 provider runtime 仍应作为后续 guarded child work item 单独承接
