---
related_doc:
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/021-frontend-program-remediation-runtime-baseline/spec.md"
---
# 实施计划：Frontend Governance Materialization Runtime Baseline

**编号**：`022-frontend-governance-materialization-runtime-baseline` | **日期**：2026-04-03 | **规格**：specs/022-frontend-governance-materialization-runtime-baseline/spec.md

## 概述

本计划处理的是 `021` 之后的 frontend governance materialization runtime baseline，而不是继续扩张 `021` 的 remediation handoff responsibility。当前仓库已经在上游锁定并实现了：

- `017`：frontend generation governance models / artifacts baseline
- `018`：frontend gate policy artifacts / verification baseline
- `021`：program remediation input packaging、execute remediation handoff surface

但 remediation handoff 到真实命令面之间仍缺少独立 child work item 去冻结：

- `021` 会输出 “materialize frontend gate policy artifacts / generation governance artifacts”，但还没有正式 CLI command surface
- operator 还不能从 canonical docs 中直接读出 governance artifact materialization 的 bounded runtime 入口
- remediation handoff 还不能稳定输出 machine-consumable command binding
- 若继续直接编码，容易把 materialization runtime、program remediation、auto-fix 与 writeback 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Governance Materialization Runtime Baseline`：

- 先冻结 materialization runtime 的 truth order 与 non-goals
- 再冻结 command surface、artifact group 与 remediation runbook binding
- 最后给出后续 `cli / core / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入首批实现切片：`rules CLI frontend governance materialization command`，先给 operator 一个正式 CLI 入口 materialize canonical governance artifacts；随后再进入 `ProgramService / program_cmd.py` 的 remediation runbook command binding。当前仍不直接进入完整 auto-fix engine、writeback runtime 或 provider orchestration。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`017`/`018` artifact builders、`021` remediation handoff、现有 `rules_app` / `ProgramService` / `program_cmd.py`  
**主要约束**：

- materialization runtime 只能消费既有 builder truth，不得另造第二套 governance artifact truth
- 当前阶段不默认启用 provider runtime、registry、cross-spec writeback 或页面代码改写
- remediation runbook command binding 必须按 spec 粒度暴露
- bounded materialization runtime 不等于完整 auto-fix engine

## 项目结构

```text
specs/022-frontend-governance-materialization-runtime-baseline/
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
├── generators/
│   ├── frontend_gate_policy_artifacts.py
│   └── frontend_generation_constraint_artifacts.py
└── models/
    ├── frontend_gate_policy.py
    └── frontend_generation_constraints.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── cli/
│   └── sub_apps.py                          # current slice: rules CLI materialization command
└── core/
    └── program_service.py                   # next slice: remediation runbook command binding

tests/
├── integration/test_cli_rules.py
├── integration/test_cli_program.py
└── unit/test_program_service.py
```

## 开始执行前必须锁定的阻断决策

- frontend governance materialization runtime 只消费 `017` / `018` builders 与 `021` remediation truth，不另造第二套 artifact contract
- CLI command 负责 materialize canonical governance roots，但 remediation runbook 仍按 spec 粒度引用
- bounded materialization runtime 可以暴露并执行 governance artifact 写入，但不得默认触发页面代码改写或 cross-spec writeback
- auto-fix engine、registry、provider runtime 与 writeback 仍留在下游 work item
- 当前 baseline 不改写 execute truth，只在既有 remediation surface 上补正式命令面

未锁定上述决策前，不得进入 `022` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| materialization truth | 定义 frontend governance materialization command 的最小真值与 side-effect 边界 | 不得改写 `017` / `018` artifact truth |
| CLI command surface | 定义哪个正式命令负责 materialize canonical governance artifacts | 不得偷渡 auto-fix / writeback |
| remediation runbook binding | 定义 `021` remediation payload 如何引用真实命令 | 不得重写 `021` remediation input truth |
| downstream handoff | 定义推荐文件面、测试矩阵与 future auto-fix child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend governance materialization runtime 从 `021` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/022/...` 文档改动。

### Phase 1：Materialization truth freeze

**目标**：锁定 materialization runtime 在 `017 / 018 / 021 -> 022 -> future auto-fix` 主线中的 truth order。  
**产物**：materialization truth baseline、non-goals baseline、runbook binding baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Command surface / runbook binding freeze

**目标**：锁定 CLI materialization command、artifact groups 与 remediation runbook binding 的 responsibility 与 honesty 语义。  
**产物**：command baseline、artifact group baseline、runbook binding baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream auto-fix handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Rules CLI frontend governance materialization command slice

**目标**：在 `rules_app` 中落下正式 frontend governance materialization command，让 operator 能直接 materialize canonical gate / generation artifacts。
**产物**：`src/ai_sdlc/cli/sub_apps.py`、`tests/integration/test_cli_rules.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

### Phase 5：Program remediation runbook command binding slice

**目标**：把正式 materialization command 绑定到 `ProgramService / program_cmd.py` 的 remediation payload 与 execute failure handoff 中，让 operator 看到真实命令而不只是动作文本。
**产物**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Materialization truth freeze

**范围**：truth order、non-goals、artifact group 与 command surface boundary。  
**影响范围**：后续 CLI materialization command 与 remediation runbook binding。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Command surface / runbook binding freeze

**范围**：CLI command、artifact groups、failure honesty 与 remediation runbook 引用规则。  
**影响范围**：后续 `sub_apps.py`、`program_service.py`、`program_cmd.py`。  
**验证方式**：contract review。  
**回退方式**：不创建 auto-fix side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream auto-fix handoff。  
**影响范围**：后续 `cli / core / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 auto-fix runtime 实现。

### 工作流 D：Rules CLI frontend governance materialization command slice

**范围**：frontend governance canonical artifact materialization command。
**影响范围**：operator-facing command surface，为 remediation runbook 提供真实命令入口。
**验证方式**：`tests/integration/test_cli_rules.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不进入 program execute side effect。

### 工作流 E：Program remediation runbook command binding slice

**范围**：`ProgramService` remediation payload command binding 与 `program integrate --execute` remediation output/report 命令渲染。
**影响范围**：operator-facing remediation handoff 从动作文本升级为真实命令，可见性提升但不新增 auto-fix/writeback。
**验证方式**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不进入 auto-fix / writeback runtime。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| materialization truth order | 文档交叉引用检查 | 人工审阅 |
| command surface clarity | formal wording review | 人工审阅 |
| artifact group honesty | contract review | file-map review |
| remediation runbook command binding | tests + report review | 人工审阅 |
| downstream auto-fix handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |
| rules CLI materialization command correctness | `uv run pytest tests/integration/test_cli_rules.py -q` | materialized file set review |
| program remediation command binding correctness | `uv run pytest tests/unit/test_program_service.py -q` + `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / report review |

## 当前建议的下游实现起点

- 先在 `sub_apps.py` 暴露 `rules` 下的正式 frontend governance materialization command
- 再把该命令绑定到 `program_service.py` / `program_cmd.py` 的 remediation runbook
- auto-fix engine、writeback 与 provider runtime 仍应作为后续 guarded child work item 单独承接
