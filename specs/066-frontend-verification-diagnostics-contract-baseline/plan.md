---
related_doc:
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/plan.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/plan.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/plan.md"
---
# 实施计划：Frontend Verification Diagnostics Contract Baseline

**编号**：`066-frontend-verification-diagnostics-contract-baseline` | **日期**：2026-04-06 | **规格**：specs/066-frontend-verification-diagnostics-contract-baseline/spec.md

## 概述

本计划处理的是 diagnostics contract baseline，而不是再造一套 verify/gate/runtime 主链。当前仓库已经具备：

- `012` 冻结的 frontend contract verify integration 主线
- `013 / 014` 冻结的 observation provider/export/attachment truth
- `018` 冻结的 gate / compatibility 消费面
- `065` 冻结的 sample-source self-check 输入与 `pass / drift / gap` 演示链

缺少的是一层统一 diagnostics truth，来把以下能力收敛成单一 canonical contract：

- 把 observation artifact/reference 的状态解析为明确的 `diagnostic_status`
- 把 `diagnostic_status` 单向投影成 `policy_projection`
- 让 `verify constraints`、`VerificationGate / VerifyGate`、CLI、runner、`ProgramService` 消费同一 truth，而不是各自从 `[]`、异常字符串或缺失路径重算语义

因此，本计划的目标是：

- 先冻结 `Layer A / Layer B / Layer C` 的单向关系与 truth order
- 再冻结 frontend 首个 source family 的 status resolution、`evidence` 与 `policy_projection`
- 最后为 `core / gates / cli / program / tests` 提供可直接执行的实现切片和验证矩阵

`066` 当前允许推进的是 **diagnostics contract formal baseline + implementation handoff**。后续实现必须继续遵守：`Layer C` 只能消费已有 truth，不得再长出第二套 diagnostics 规则系统。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Pydantic models、Markdown formal docs  
**主要依赖**：`012` verify integration baseline、`013` observation provider baseline、`014` runtime attachment baseline、`018` gate compatibility baseline、`065` sample-source self-check baseline  
**现有基础**：

- `src/ai_sdlc/core/frontend_contract_observation_provider.py`
- `src/ai_sdlc/core/frontend_contract_verification.py`
- `src/ai_sdlc/core/frontend_gate_verification.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/gates/frontend_contract_gate.py`
- `tests/unit/test_frontend_contract_gate.py`
- `tests/unit/test_frontend_contract_verification.py`
- `tests/unit/test_frontend_gate_verification.py`
- `tests/unit/test_program_service.py`
- `tests/unit/test_verify_constraints.py`
- `tests/integration/test_cli_verify_constraints.py`

**目标平台**：AI-SDLC 框架仓库自身，面向 frontend verification diagnostics 的 canonical contract  
**主要约束**：

- `066` 只冻结 diagnostics contract，不改写 `012 / 013 / 014 / 065 / 018` 的既有真值
- frontend 只是首个 source family；字段与规则必须可扩展，但当前不得为“通用化”而额外引入第二套抽象层
- `policy_projection` 只能由 status resolution 单向导出；所有 surface 必须消费投影结果，而不是重算
- `Layer C` 不得通过空列表、异常字符串、路径缺失或局部上下文回推 diagnostics 语义
- remediation / recheck / visual-a11y 只允许作为 downstream consumer 出现在当前计划中，不在 `066` 内落检查本体

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 diagnostics contract 与首个 frontend source family，不扩张到第二个 source family、recheck runtime 或 visual-a11y 检查本体 |
| MUST-2 关键路径可验证 | status resolution、projection、verify/gate/runtime consumer 与 CLI/program surface 都有对应单测/集成测试矩阵 |
| MUST-3 范围声明与回退 | 每个批次都锁定精确文件面；回退时可按 docs、core truth、consumer surface 独立回退 |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 冻结 `066` 的 diagnostics contract truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理 diagnostics truth 与消费边界，不引入新的 runtime provider、平行 gate system 或额外 artifact 格式 |

## 项目结构

### 文档结构

```text
specs/066-frontend-verification-diagnostics-contract-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_observation_provider.py
│   ├── frontend_contract_verification.py
│   ├── frontend_gate_verification.py
│   ├── program_service.py
│   └── verify_constraints.py
├── gates/
│   └── frontend_contract_gate.py
└── cli/
    └── verify_cmd.py

tests/
├── integration/
│   └── test_cli_verify_constraints.py
└── unit/
    ├── test_frontend_contract_gate.py
    ├── test_frontend_contract_verification.py
    ├── test_frontend_gate_verification.py
    ├── test_program_service.py
    └── test_verify_constraints.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_observation_provider.py   # artifact/reference presence、loader、normalization status
│   ├── frontend_contract_verification.py           # Layer B core entity、status resolution、projection helpers
│   ├── frontend_gate_verification.py               # Layer A 与 Layer B 之间的 gate-facing translation
│   ├── program_service.py                          # ProgramService surface adapter；只消费 projection
│   └── verify_constraints.py                       # verification source / coverage / blocker 接入
├── gates/
│   └── frontend_contract_gate.py                   # gate-facing diagnostics summary，只消费 Layer B
└── cli/
    └── verify_cmd.py                              # 仅当 terminal / JSON summary 需要显式字段暴露时触碰

tests/
├── integration/
│   └── test_cli_verify_constraints.py
└── unit/
    ├── test_frontend_contract_gate.py
    ├── test_frontend_contract_verification.py
    ├── test_frontend_gate_verification.py
    ├── test_program_service.py
    └── test_verify_constraints.py
```

## 开始执行前必须锁定的阻断决策

- `diagnostic_status` 必须按 `missing_artifact -> invalid_artifact -> valid_empty -> drift -> clean` 的顺序单向、互斥、短路决议
- `missing_artifact` 只表示 absence；`invalid_artifact` 只表示 presence-but-broken；不得通过宽松 loader 或 surface fallback 折叠两者
- `valid_empty` 必须建立在 canonical normalization 完成之后；不得把 “可解析但未 normalize” 视为 empty
- `drift` 只能建立在 artifact 已提供、合法、canonical normalization 完成且比较已完成的前提上
- `policy_projection` 必须由 status resolution 单向导出；`verify constraints`、gate、CLI、runner、`ProgramService` 都不得覆盖该投影
- downstream consumer 不得跳过 projection，不得直接以 `diagnostic_status` 推导 verdict、severity、report family 或 readiness

未锁定上述决策前，不得进入 `src/` / `tests/` 级实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| diagnostics core contract | 定义 `Layer B` core entity、status resolution、evidence 与 projection contract | 不得把 verdict / gate policy / CLI wording 混入 core entity 本体 |
| frontend source normalizer | 解析 observation artifact/reference 的 presence、validity、normalization 与 drift comparison 前置条件 | 不得偷偷把 `missing` 并到 `invalid`，也不得把 `valid_empty` 并到 `drift` |
| verification / gate consumers | 将 `policy_projection` 投影进 `Layer A` 的 blocker / advisory / gap / readiness | 不得复制第二套 status resolution 规则 |
| surface adapters | CLI、runner、`ProgramService` 的显示、序列化与 operator-facing summary | 不得从空数组、异常字符串、路径缺失等局部信号重算 diagnostics 语义 |
| downstream handoff | recheck、remediation、visual-a11y、未来 source family 对 `Layer B` 的消费方式 | 不得在 `066` 内实现这些检查本体，也不得绕过 projection contract |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 diagnostics contract 从口头设计收敛为 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/066/...` 文档改动。

### Phase 1：Diagnostics core entity and status resolution

**目标**：落下 frontend 首个 source family 的 `Layer B` core entity、status resolution、evidence 与 projection helper。  
**产物**：`src/ai_sdlc/core/frontend_contract_observation_provider.py`、`src/ai_sdlc/core/frontend_contract_verification.py`、对应单测。  
**验证方式**：定向 `pytest` + `git diff --check`。  
**回退方式**：仅回退 core helper 与对应单测。

### Phase 2：Verification / gate consumer convergence

**目标**：让 `verify_constraints`、`frontend_gate_verification`、`frontend_contract_gate` 统一消费 `Layer B` truth，不再各自重算缺失/空/漂移语义。  
**产物**：`src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/gates/frontend_contract_gate.py`、对应单测。  
**验证方式**：定向 `pytest` + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 verification/gate consumer 相关改动。

### Phase 3：Surface adapter convergence

**目标**：让 CLI terminal/JSON、runner、`ProgramService` 只消费已冻结的 `diagnostic_status + policy_projection`，不再通过局部信号补判。  
**产物**：`src/ai_sdlc/core/program_service.py`、必要时 `src/ai_sdlc/cli/verify_cmd.py`、对应 unit/integration tests。  
**验证方式**：定向 `pytest` + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 surface adapter 改动。

### Phase 4：Fresh verification and downstream handoff archive

**目标**：执行 fresh verification，补 execution log，并把 downstream handoff 与 non-goal 边界落为 close-ready baseline。  
**产物**：`task-execution-log.md`。  
**验证方式**：定向 `pytest`、必要的 `ruff`、`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：不引入新的产品行为，只补归档与对账。

## 工作流计划

### 工作流 A：Diagnostics truth freeze

**范围**：`Layer A / B / C` 分层、truth order、status set、projection rules。  
**影响范围**：后续所有 verification、gate、CLI、runner、`ProgramService` surface。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### 工作流 B：Frontend status normalizer

**范围**：presence、reference resolution、loader validity、canonical normalization、empty-vs-drift 前置条件。  
**影响范围**：`frontend_contract_observation_provider.py`、`frontend_contract_verification.py`。  
**验证方式**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`。  
**回退方式**：不触碰 gate 或 surface adapters。

### 工作流 C：Verification / gate consumer convergence

**范围**：`verify_constraints`、`frontend_gate_verification`、`frontend_contract_gate` 的 projection 消费与 blocker/gap 分类。  
**影响范围**：verification source、coverage gap、gate check summary。  
**验证方式**：`uv run pytest tests/unit/test_frontend_contract_gate.py tests/unit/test_frontend_gate_verification.py tests/unit/test_verify_constraints.py -q`。  
**回退方式**：不触碰 CLI/program surface。

### 工作流 D：Surface adapter convergence

**范围**：CLI terminal/JSON、runner、`ProgramService` 对 diagnostics truth 的显示与 readiness 投影。  
**影响范围**：operator-facing summary、JSON surface、program readiness output。  
**验证方式**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_verify_constraints.py -q`。  
**回退方式**：不引入 local inference rule。

### 工作流 E：Downstream handoff freeze

**范围**：recheck、remediation、visual-a11y 与未来 source family 的消费边界。  
**影响范围**：后续 child work item 的接口稳定性。  
**验证方式**：formal docs review + execution-log 对账。  
**回退方式**：不实现下游检查本体。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| status resolution 顺序与互斥性 | `uv run pytest tests/unit/test_frontend_contract_verification.py -q` | diagnostics payload review |
| missing / invalid / valid_empty / drift / clean 边界 | `uv run pytest tests/unit/test_frontend_contract_verification.py tests/unit/test_frontend_contract_gate.py -q` | surface summary review |
| projection 单向导出 | `uv run pytest tests/unit/test_frontend_gate_verification.py tests/unit/test_verify_constraints.py -q` | payload diff review |
| Layer C 不重算语义 | `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_verify_constraints.py -q` | terminal / JSON output review |
| 同一输入跨 surface 的确定性 | 定向 unit + integration regression | 人工对账 |
| downstream consumer 不跳过 projection | formal docs review | 后续 child work item review |

## 已锁定决策

- frontend 是首个 source family，但暂不抽出新的 shared module；如无第二个 source family 的现实需求，不提前做跨域抽象迁移
- `Layer B` core entity 允许在现有 frontend verification helper 中起步，但字段与 contract 必须保持 source-agnostic
- `verify_cmd.py` 只有在当前 generic terminal / JSON surface 无法暴露 diagnostics summary 时才允许触碰
- `ProgramService` 只能消费 `policy_projection` 与 `diagnostic_status` 的既有结果，不能自行推断 gap / readiness / drift
- 任何 future consumer 若需要新 severity 或 blocker class，必须经由 projection contract 扩展，而不是在 surface 上私有 hardcode

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否在第二个 source family 出现前抽出共享 diagnostics model 模块 | 已决策：暂不抽取 | 不阻塞 Phase 1 |

## 实施顺序建议

1. 先冻结 `066` formal docs，确保 status set、projection rules 与 adapter boundary 不再依赖对话记忆
2. 再落 frontend status normalizer，把 `missing / invalid / valid_empty / drift / clean` 的判断收敛进 `Layer B`
3. 然后统一 verification / gate consumer，让 `verify_constraints`、gate surface 共用 projection
4. 最后收紧 CLI / runner / `ProgramService`，证明同一输入在所有 surface 上给出同一 diagnostics truth
