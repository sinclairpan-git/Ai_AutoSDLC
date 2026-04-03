---
related_doc:
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
---
# 实施计划：Frontend Program Remediation Runtime Baseline

**编号**：`021-frontend-program-remediation-runtime-baseline` | **日期**：2026-04-03 | **规格**：specs/021-frontend-program-remediation-runtime-baseline/spec.md

## 概述

本计划处理的是 `020` 之后的 program-level frontend remediation runtime baseline，而不是继续扩张 `020` 的 execute/recheck responsibility。当前仓库已经在上游锁定并实现了：

- `018`：frontend gate / recheck / fix-input boundary baseline
- `019`：program-level readiness aggregation、status / dry-run frontend surface
- `020`：program execute preflight、recheck handoff 与 execute CLI/report surface

但最后一段“program 如何消费 remediation hint / fix input，并在什么边界内组织 bounded remediation runtime”仍缺少独立 child work item 去冻结：

- remediation input 还没有 formal baseline 说明它应如何承接 `020` 的 handoff
- fix-input packaging 与 operator-facing remediation handoff 还没有进入 canonical truth
- bounded remediation runtime 与完整 auto-fix engine 的边界还没有被 program orchestration 语义冻结

因此，本计划的目标是建立统一的 `Frontend Program Remediation Runtime Baseline`：

- 先冻结 remediation runtime 的 truth order 与 non-goals
- 再冻结 remediation input、fix input packaging 与 handoff responsibility
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入首批实现切片：`program remediation input packaging`，先在 `ProgramService` 中落 per-spec remediation input / fix-input packaging；随后再进入 execute CLI / report 的 remediation handoff surface。当前仍不直接进入 auto-fix engine 或 writeback runtime。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`018` gate / fix-input baseline、`020` execute/recheck baseline、现有 `ProgramService` / `program_cmd.py` surface  
**主要约束**：

- remediation runtime 只能消费既有 execute/recheck truth，不得另造 program 私有 remediation truth
- 当前阶段不默认启用 scanner/provider 写入、auto-fix、registry 或 cross-spec writeback
- remediation input / handoff 必须按 spec 粒度暴露
- bounded remediation runtime 不等于完整 auto-fix engine

## 项目结构

```text
specs/021-frontend-program-remediation-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── cli/
│   └── program_cmd.py
├── core/
│   └── program_service.py
└── gates/
    └── pipeline_gates.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py                   # current slice: remediation input packaging
└── cli/
    └── program_cmd.py                       # next slice: remediation handoff / operator surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- program remediation runtime 只消费 `020` execute/recheck truth 与 `018` fix-input boundary，不另造 program 私有 remediation truth
- remediation state、fix input 与 suggested actions 必须按 spec 粒度暴露
- bounded remediation runtime 可以暴露 remediation handoff，但不得默认触发 scanner/provider 写入
- auto-fix engine、registry、writeback 与 provider runtime 仍留在下游 work item
- 当前 baseline 不改写 manifest 或 execute truth，只在既有 surface 上冻结 remediation responsibility

未锁定上述决策前，不得进入 `021` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| remediation input packaging | 定义 remediation input / fix input 的最小 truth 与 packaging | 不得改写 `018` / `020` 上游 truth |
| remediation handoff surface | 定义哪些 CLI/report surface 负责展示 remediation input 与 suggested actions | 不得默认触发 runtime side effect |
| bounded remediation runtime | 定义 bounded remediation 与完整 auto-fix engine 的边界 | 不得把 remediation path 偷渡成默认写入入口 |
| downstream handoff | 定义推荐文件面、测试矩阵与 future auto-fix child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program remediation runtime 从 `020` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/021/...` 文档改动。

### Phase 1：Remediation truth freeze

**目标**：锁定 program remediation runtime 在 `018 / 020 -> 021 -> future auto-fix` 主线中的 truth order。  
**产物**：remediation truth baseline、non-goals baseline、fix-input handoff baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Remediation input / handoff responsibility freeze

**目标**：锁定 remediation input、fix input packaging 与 remediation handoff 的 responsibility 与 honesty 语义。  
**产物**：input baseline、packaging baseline、handoff baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream auto-fix handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Program remediation input packaging slice

**目标**：在 `ProgramService` 中为 frontend-not-ready integration steps 落下 remediation input / fix-input packaging truth，统一消费 `020` readiness / handoff truth，并保持只读 packaging。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program execute CLI/report remediation handoff surface slice

**目标**：把 remediation input / suggested actions 暴露到 `program integrate --execute` 的终端输出和 report 中，让 operator 能直接看到 bounded remediation handoff，而不进入 auto-fix engine。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Remediation truth freeze

**范围**：remediation truth order、non-goals、spec-granularity remediation input 与 fix-input boundary。  
**影响范围**：后续 program remediation child work item 与 downstream auto-fix orchestration。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Remediation input / handoff responsibility freeze

**范围**：remediation input、fix input packaging、failure honesty 与 operator-facing handoff 规则。  
**影响范围**：后续 `program_service.py`、`program_cmd.py` 与 remediation operator surface。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream auto-fix handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 auto-fix runtime 实现。

### 工作流 D：Program remediation input packaging slice

**范围**：per-spec remediation input、fix-input packaging、suggested actions 与 source linkage reuse。
**影响范围**：后续 execute CLI / report remediation handoff 的 data source。
**验证方式**：`tests/unit/test_program_service.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不改 execute gate / recheck truth。

### 工作流 E：Program execute CLI/report remediation handoff surface slice

**范围**：`program integrate --execute` 的 remediation handoff 输出与 report surface。
**影响范围**：operator-facing remediation guidance，可见性提升但不新增 runtime side effect。
**验证方式**：`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不进入 auto-fix / writeback runtime。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| remediation truth order | 文档交叉引用检查 | 人工审阅 |
| per-spec remediation granularity | formal wording review | 人工审阅 |
| fix-input packaging clarity | contract review | file-map review |
| remediation honesty | formal docs review | 人工审阅 |
| downstream auto-fix handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |
| program remediation input packaging correctness | `uv run pytest tests/unit/test_program_service.py -q` | remediation payload / source linkage review |
| program execute CLI/report remediation surface correctness | `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / report review |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 per-spec remediation input / fix-input packaging
- 再把 remediation handoff 暴露到 CLI / report surface
- auto-fix engine 与 writeback runtime 仍应作为后续 guarded child work item 单独承接
- auto-fix engine 与 writeback runtime 仍应作为后续 guarded child work item 单独承接
