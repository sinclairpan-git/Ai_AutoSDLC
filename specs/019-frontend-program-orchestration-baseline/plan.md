---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/plan.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/plan.md"
---
# 实施计划：Frontend Program Orchestration Baseline

**编号**：`019-frontend-program-orchestration-baseline` | **日期**：2026-04-03 | **规格**：specs/019-frontend-program-orchestration-baseline/spec.md

## 概述

本计划处理的是 `014` runtime attachment 与 `018` frontend gate summary 之后的 program-level frontend orchestration baseline，而不是继续扩张 `014` 或 `018` 本体。当前仓库已经在上游锁定并实现了：

- `014`：runtime attachment helper、runner verify-context、`run` CLI summary
- `018`：frontend gate policy / artifact、verify attachment、gate aggregation、`verify constraints` CLI summary
- `program_cmd.py` / `ProgramService`：多 spec 的 validate / status / plan / integrate surface

但最后一段“program 如何消费 per-spec frontend readiness truth”仍缺少独立 child work item 去冻结：

- `program` surface 还没有 formal baseline 说明它应消费哪些 frontend readiness 输入
- 多 spec frontend readiness 的暴露粒度、诚实缺口和 execute guard 还没有进入 canonical truth
- 若继续直接编码，容易把 runtime attachment、gate summary、program orchestration、execute runtime 与 auto-fix 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Orchestration Baseline`：

- 先冻结 program-level frontend orchestration 的 truth order 与 non-goals
- 再冻结 readiness input、status/plan/integrate responsibility 与 execute guard
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前阶段只完成 canonical formal baseline，不直接进入 `src/` / `tests/` 实现。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`014` runtime attachment baseline、`018` frontend gate compatibility baseline、现有 `ProgramService` / `program_cmd.py` surface  
**主要约束**：

- program-level frontend orchestration 只能消费既有 per-spec truth，不得另造 program 私有 frontend truth
- 当前阶段不默认启用 auto-scan、auto-attach、auto-fix、registry 或 cross-spec writeback
- `program --execute` 的更重前端 runtime 仍属于 guarded downstream 能力，不在当前 baseline 默认启用
- readiness 必须按 spec 粒度暴露，缺口必须诚实表达

## 项目结构

```text
specs/019-frontend-program-orchestration-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── cli/
│   ├── run_cmd.py
│   └── program_cmd.py
├── core/
│   ├── frontend_contract_runtime_attachment.py
│   ├── frontend_gate_verification.py
│   └── program_service.py
└── gates/
    └── pipeline_gates.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py                   # per-spec frontend readiness aggregation
└── cli/
    └── program_cmd.py                       # status / integrate dry-run frontend readiness surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- program-level frontend orchestration 只消费 `014` runtime attachment 与 `018` frontend gate summary，不另造 program 私有 frontend truth
- readiness 必须按 spec 粒度暴露，不得压成伪全局 verdict
- `program status / plan / integrate --dry-run` 可以暴露 frontend readiness / guard，但不得默认触发 scanner/provider 写入
- execute runtime、registry、auto-fix 与 remediation 仍留在下游 work item
- 当前 baseline 不改写 program manifest 主体语义，只在既有 surface 上冻结 frontend responsibility

未锁定上述决策前，不得进入 `019` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| program readiness aggregation | 定义 program-level frontend readiness 输入、粒度与 honesty 规则 | 不得改写 `014` / `018` 上游 truth |
| status / plan / integrate surface | 定义哪些 program CLI surface 负责展示 frontend readiness 与 guard | 不得默认触发 runtime side effect |
| execute guard | 定义 program execute 与 frontend runtime 的边界 | 不得把 execute path 偷渡成默认 auto-attach / auto-fix |
| downstream handoff | 定义推荐文件面、测试矩阵与 future runtime child work item 边界 | 不得把 registry / remediation 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program orchestration 从 `014` / `018` 的 downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/019/...` 文档改动。

### Phase 1：Program frontend truth freeze

**目标**：锁定 program-level frontend orchestration 在 `014 / 018 -> 019 -> future execute runtime` 主线中的 truth order。  
**产物**：readiness truth baseline、non-goals baseline、execute guard baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Status / plan / integrate responsibility freeze

**目标**：锁定 program-level frontend readiness 输入、按 spec 粒度暴露规则、status/plan/integrate 的 responsibility 与 honesty 语义。  
**产物**：status baseline、integrate dry-run baseline、readiness honesty baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Program frontend truth freeze

**范围**：program-level frontend truth order、readiness input、non-goals、execute guard。  
**影响范围**：后续 program orchestration child work item 与 `014` / `018` 下游消费边界。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Status / plan / integrate responsibility freeze

**范围**：`program status / plan / integrate` 的 frontend responsibility、spec-granularity readiness 与 honesty 规则。  
**影响范围**：后续 `program_service.py`、`program_cmd.py` 与 operator-facing orchestration surface。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream runtime / auto-fix handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 execute runtime 实现。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| program frontend truth order | 文档交叉引用检查 | 人工审阅 |
| per-spec readiness granularity | formal wording review | 人工审阅 |
| status / integrate responsibility clarity | contract review | file-map review |
| execute guard clarity | formal docs review | 人工审阅 |
| downstream handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 per-spec frontend readiness aggregation
- 再把 readiness 暴露到 `program status` 与 `program integrate --dry-run`
- `program --execute` 的更重前端 runtime 仍应作为后续 guarded child work item 单独承接
