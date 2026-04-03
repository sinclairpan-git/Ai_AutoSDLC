---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
---
# 实施计划：Frontend Program Execute Runtime Baseline

**编号**：`020-frontend-program-execute-runtime-baseline` | **日期**：2026-04-03 | **规格**：specs/020-frontend-program-execute-runtime-baseline/spec.md

## 概述

本计划处理的是 `019` 之后的 program-level frontend execute runtime baseline，而不是继续扩张 `019` 的 dry-run/status responsibility。当前仓库已经在上游锁定并实现了：

- `014`：runtime attachment helper 与 `run` CLI summary
- `018`：frontend gate summary、verify/gate aggregation 与 CLI summary
- `019`：program-level readiness aggregation、`program status` 与 `program integrate --dry-run` frontend surface
- `program integrate --execute`：close/dependency/dirty-tree gate

但最后一段“program execute 如何消费 frontend readiness truth，并在什么时候阻断 / recheck / 仅给 remediation hint”仍缺少独立 child work item 去冻结：

- execute preflight 还没有 formal baseline 说明它应如何消费 per-spec frontend readiness
- step-level recheck handoff 还没有进入 canonical truth
- remediation hint 与 auto-fix engine 的边界还没有被 program execute 语义冻结
- 若继续直接编码，容易把 execute runtime、recheck、remediation 与 auto-fix 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Execute Runtime Baseline`：

- 先冻结 execute runtime 的 truth order 与 non-goals
- 再冻结 execute preflight、recheck handoff 与 remediation hint 的 responsibility
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前阶段只冻结 formal baseline，不直接进入 `src/` / `tests/` 实现。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`019` frontend program orchestration baseline、`018` gate / recheck baseline、现有 `ProgramService` / `program_cmd.py` execute surface  
**主要约束**：

- execute runtime 只能消费既有 per-spec readiness truth，不得另造 program 私有 execute truth
- 当前阶段不默认启用 scanner/provider 写入、auto-attach、auto-fix、registry 或 cross-spec writeback
- recheck 是 bounded handoff，不是后台 loop
- remediation hint 必须诚实表达，但不等于默认修复

## 项目结构

```text
specs/020-frontend-program-execute-runtime-baseline/
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
│   └── program_service.py                   # current execute gate / future frontend execute preflight
└── cli/
    └── program_cmd.py                       # execute preflight / recheck / remediation surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- program execute 只消费 `019` per-spec readiness truth 与 `018` recheck boundary，不另造 program 私有 execute truth
- execute blocker、recheck_required 与 remediation hint 必须按 spec 粒度暴露
- `program integrate --execute` 可以暴露 frontend preflight / recheck handoff，但不得默认触发 scanner/provider 写入
- auto-fix、registry、writeback 与 remediation runtime 仍留在下游 work item
- 当前 baseline 不改写 manifest 语义，只在既有 execute surface 上冻结 frontend responsibility

未锁定上述决策前，不得进入 `020` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| execute preflight gate | 定义 execute 前如何消费 per-spec frontend readiness truth | 不得改写 `019` readiness truth |
| recheck handoff | 定义 execute step 之后的 frontend recheck 触发与提示边界 | 不得把 recheck 扩张成后台 loop |
| remediation hint | 定义失败/未接线时的最小 remediation guidance | 不得默认触发 auto-fix 或 writeback |
| downstream handoff | 定义推荐文件面、测试矩阵与 future auto-fix child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program execute runtime 从 `019` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/020/...` 文档改动。

### Phase 1：Execute truth freeze

**目标**：锁定 program execute runtime 在 `014 / 018 / 019 -> 020 -> future auto-fix` 主线中的 truth order。  
**产物**：execute truth baseline、non-goals baseline、recheck/remediation baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Execute / recheck / remediation responsibility freeze

**目标**：锁定 execute preflight、step-level recheck handoff 与 remediation hint 的 responsibility 与 honesty 语义。  
**产物**：execute baseline、recheck baseline、remediation hint baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream auto-fix handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Execute truth freeze

**范围**：execute truth order、non-goals、spec-granularity execute gate 与 recheck/remediation boundary。  
**影响范围**：后续 `program --execute` 的 frontend guard surface 与 downstream auto-fix child work item。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Execute / recheck / remediation responsibility freeze

**范围**：execute preflight、step-level recheck handoff、failure honesty 与 remediation hint 规则。  
**影响范围**：后续 `program_service.py`、`program_cmd.py` 与 operator-facing execute runtime surface。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream auto-fix handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 auto-fix runtime 实现。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| execute truth order | 文档交叉引用检查 | 人工审阅 |
| per-spec execute gate granularity | formal wording review | 人工审阅 |
| recheck handoff clarity | contract review | file-map review |
| remediation hint honesty | formal docs review | 人工审阅 |
| downstream auto-fix handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 per-spec frontend execute gate 与 recheck handoff payload
- 再把 execute preflight / remediation hint 暴露到 `program integrate --execute`
- auto-fix engine 与 writeback runtime 仍应作为后续 guarded child work item 单独承接
