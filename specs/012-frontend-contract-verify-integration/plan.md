---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Contract Verify Integration

**编号**：`012-frontend-contract-verify-integration` | **日期**：2026-04-02 | **规格**：specs/012-frontend-contract-verify-integration/spec.md

## 概述

本计划处理的是 `011` 下游的 frontend contract verify integration，而不是继续扩张 `011` 本体。当前仓库已经在 `011` 中锁定并实现了：

- frontend contract models
- contract artifact instantiation
- artifact-vs-observation drift helper
- 最小 `frontend_contract_gate`

但 verify 主链仍缺少一个独立 child work item 去冻结：

- frontend contract verification 如何进入 `verify constraints`
- `VerificationGate / VerifyGate` 如何消费 contract-aware 结果
- CLI `verify` 的 terminal / JSON surface 如何诚实暴露 contract 状态
- scanner / fix-loop / auto-fix 应如何被明确留在下游，而不是混进当前集成工单

因此，本计划的目标是建立统一的 `Frontend Contract Verify Integration` formal baseline：

- 先冻结 verify integration 的 truth order
- 再冻结 verification surface / coverage gap / CLI 口径
- 最后给出后续实现文件面与测试矩阵

当前阶段只冻结 formal baseline，不直接进入 `src/` / `tests/` 级实现。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Pydantic models、Markdown formal docs  
**主要依赖**：`009` 母规格、`011` contract baseline、现有 `verify constraints` / `VerificationGate` / `VerifyGate` / CLI verify 流程  
**现有基础**：

- [`../../src/ai_sdlc/gates/frontend_contract_gate.py`](../../src/ai_sdlc/gates/frontend_contract_gate.py) 已提供最小 contract-aware 只读 gate surface
- [`../../src/ai_sdlc/core/frontend_contract_drift.py`](../../src/ai_sdlc/core/frontend_contract_drift.py) 已提供 artifact-vs-observation drift helper
- [`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py) 已持有 verification source / check object / coverage gap 机制
- [`../../src/ai_sdlc/gates/pipeline_gates.py`](../../src/ai_sdlc/gates/pipeline_gates.py) 已持有 `VerificationGate / VerifyGate`
- [`../../src/ai_sdlc/cli/verify_cmd.py`](../../src/ai_sdlc/cli/verify_cmd.py) 已持有 terminal / JSON verify surface

**目标平台**：AI-SDLC 框架仓库自身，面向 frontend contract verify integration 主链  
**主要约束**：

- verify integration 必须复用现有 `verify constraints -> VerificationGate / VerifyGate -> cli verify`
- `frontend_contract_gate` 只能作为上游 surface，不得扩张成新的平行 gate system
- observation 输入必须保持结构化，不得退回 prompt 文本
- scanner、fix-loop 与 auto-fix 保持在下游 child work item
- 当前阶段只冻结 formal baseline，不直接承诺完整运行时接线

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 verify integration 的最小合同，不扩张到 scanner / fix-loop / auto-fix |
| MUST-2 关键路径可验证 | verification source、check object、coverage gap、CLI 口径和测试矩阵都必须可被文档与后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 verify integration 主线，当前变更仅作用于 `specs/012/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 将 verify integration baseline 落为 canonical truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 verification 合同，不引入前端 runtime 或 scanner 实现 |

## 项目结构

### 文档结构

```text
specs/012-frontend-contract-verify-integration/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── core/
│   └── frontend_contract_drift.py
├── gates/
│   └── frontend_contract_gate.py
├── generators/
│   └── frontend_contract_artifacts.py
└── models/
    └── frontend_contracts.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_verification.py   # contract verify report / context builder
│   └── verify_constraints.py               # verification source / check objects / coverage gaps
├── gates/
│   ├── frontend_contract_gate.py           # existing upstream gate surface
│   └── pipeline_gates.py                   # VerificationGate / VerifyGate aggregation
├── cli/
│   └── verify_cmd.py                       # terminal / json verify surface
└── gates/
    └── registry.py                         # only if attachment strategy truly requires registry touch

tests/
├── unit/test_frontend_contract_verification.py
├── unit/test_verify_constraints.py
├── unit/test_gates.py
└── integration/test_cli_verify_constraints.py
```

## 开始执行前必须锁定的阻断决策

- frontend contract verification 是现有 Verification Gate 的输入面之一，不是新的平行 gate
- `frontend_contract_gate` 只负责 contract-aware 汇总，不直接承担 CLI / telemetry / verify constraints 报告拼装
- observation 输入边界与 scanner 实现必须分离
- 缺失 artifact、缺失 observation 或 drift 未清必须被诚实暴露
- 若无充分理由，不新增新的 registry stage 名称

未锁定上述决策前，不得进入 `012` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| verification source contract | 定义 contract-aware source / check objects / coverage gaps | 不得把 contract 状态继续隐藏在自由文本或 helper 内部 |
| gate aggregation | 定义 `VerificationGate / VerifyGate` 如何消费 contract-aware 结果 | 不得另起新 stage 或复制第二套 verification 规则 |
| CLI surface | 定义 terminal / JSON verify 如何显示 contract 状态 | 不得误报 PASS 或掩盖“无法比较”的真实状态 |
| observation boundary | 定义结构化 observation 输入消费面 | 不得在当前 work item 中顺手实现 scanner |
| downstream remediation handoff | 明确 scanner / fix-loop / auto-fix 的下游边界 | 不得把 remediation 逻辑混入 verify integration |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend contract verify integration 从 `011` 后续建议动作收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/012/...` 文档改动。

### Phase 1：Verify surface truth freeze

**目标**：锁定 `frontend_contract_gate -> verify constraints -> VerificationGate / VerifyGate -> cli verify` 的单一真值顺序。  
**产物**：truth-order baseline、source/check object baseline、coverage-gap baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：CLI and attachment baseline

**目标**：锁定 terminal / JSON verify surface、现有 stage 复用策略与 registry attachment 边界。  
**产物**：CLI baseline、attachment strategy、non-goal freeze。  
**验证方式**：命令语义对账。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and test matrix

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Verify surface contract freeze

**范围**：verification source、check object、coverage gap、honest failure semantics。  
**影响范围**：`verify constraints`、`VerificationGate / VerifyGate` 与后续 telemetry source。  
**验证方式**：对象矩阵与真值顺序审阅。  
**回退方式**：不触发代码实现。

### 工作流 B：CLI and attachment freeze

**范围**：`cli verify` terminal / JSON surface、现有 stage 复用、registry attachment 边界。  
**影响范围**：`verify constraints` 输出、Verification Gate 汇总与 CLI 展示面。  
**验证方式**：命令语义与文件面审阅。  
**回退方式**：不创建新 stage/gate。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与下游 remediation handoff。  
**影响范围**：后续 `core / gates / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 scanner / fix-loop / auto-fix。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| verify truth order | 文档交叉引用检查 | 人工审阅 |
| honest missing/drift semantics | 语义对账 | 测试矩阵回挂 |
| stage reuse vs new stage | attachment strategy review | 人工审阅 |
| CLI surface honesty | 终端 / JSON 口径对账 | 集成测试矩阵 |
| downstream handoff clarity | file-map review | 人工审阅 |

## 已锁定决策

- `012` 是 `011` 下游的 verify integration child work item，不再回到 `011` 混做
- frontend contract verification 必须复用现有 `verify constraints` 与 `VerificationGate / VerifyGate`
- `frontend_contract_gate` 只作为上游输入，不直接冒充最终 verify surface
- scanner / fix-loop / auto-fix 保持在下游 work item
- 当前只冻结 formal baseline，不直接放行 `src/` / `tests/` 实现

## 实施顺序建议

1. 先冻结 `012` formal spec/plan/tasks，确保 verify integration 主线有独立 canonical truth。
2. 再冻结 contract-aware verification source、check object、coverage gap 与 honest-failure 口径。
3. 再冻结 `VerificationGate / VerifyGate`、CLI surface 与 stage attachment 边界。
4. 最后冻结推荐文件面、最小测试矩阵与下游 scanner/fix-loop handoff。
