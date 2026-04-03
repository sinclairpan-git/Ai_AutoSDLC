---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Gate Compatibility Baseline

**编号**：`018-frontend-gate-compatibility-baseline` | **日期**：2026-04-03 | **规格**：specs/018-frontend-gate-compatibility-baseline/spec.md

## 概述

本计划处理的是 `009` 下游的 `Gate-Recheck-Auto-fix / Compatibility` formal baseline，而不是直接实现完整前端诊断平台。当前仓库已经在上游锁定并实现了：

- `011 / 012 / 013 / 014`：contract-aware verify 主链、observation provider 与 runtime attachment
- `017`：generation control plane models + artifact

但最后一条 MVP 主线仍缺少独立 child work item 去冻结：

- MVP gate matrix 到底覆盖什么
- Compatibility 如何作为同一套 gate matrix 的执行强度，而不是第二套规则
- 结构化输出与 Recheck / Auto-fix 的边界如何定义
- 后续 `models / reports / gates / tests` 的实现应从哪里开始

因此，本计划的目标是建立统一的 `Frontend Gate Compatibility Baseline`：

- 先冻结 gate / compatibility truth order 与 non-goals
- 再冻结 MVP gate matrix、结构化输出、Recheck 和 Auto-fix 边界
- 最后给出后续 `models / reports / gates / tests` 的推荐文件面与测试矩阵

当前 formal baseline、`gate matrix and report models`、`gate policy artifacts`、`frontend gate verification helper`、`verify constraints attachment` 与 `VerificationGate aggregation` 实现切片已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入下一批实现切片：`verify CLI summary surface`，把 frontend gate summary 正式暴露到 `ai-sdlc verify constraints` 的终端用户面；不同时触碰新的 JSON schema、完整 gate execution runtime 或 auto-fix engine。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`011` / `017` 上游 baseline、现有 `verify_constraints` 与 `pipeline_gates` 框架、冻结设计稿第 12 章  
**主要约束**：

- Compatibility 不能被实现成第二套 gate / 规则系统
- Gate / Recheck / Auto-fix 只能消费上游 truth，不得反向改写 Contract / Kernel / Provider / generation baseline
- 当前阶段只冻结并实现最小 gate matrix / report models，不直接实现完整 auto-fix runtime

## 项目结构

```text
specs/018-frontend-gate-compatibility-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的实现触点

```text
src/ai_sdlc/
├── models/
│   └── frontend_gate_policy.py               # gate matrix / compatibility policy / report models
├── generators/
│   └── frontend_gate_policy_artifacts.py
├── core/
│   ├── frontend_gate_verification.py
│   └── verify_constraints.py
├── cli/
│   └── verify_cmd.py                         # current slice: frontend gate CLI summary surface
└── gates/
    └── pipeline_gates.py

tests/
├── unit/test_frontend_gate_policy_models.py
├── unit/test_frontend_gate_policy_artifacts.py
├── unit/test_frontend_gate_verification.py
├── unit/test_verify_constraints.py
├── unit/test_gates.py
└── integration/test_cli_verify_constraints.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 Gate / Compatibility 主线从 `009` 母规格拆成单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/018/...` 文档改动。

### Phase 1：Gate truth freeze

**目标**：锁定 gate / compatibility 在闭环中的 truth order、scope 与 non-goals。  
**产物**：scope baseline、truth-order baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Matrix / output / recheck / fix boundary freeze

**目标**：锁定 MVP gate matrix、Compatibility 执行口径、结构化输出、Recheck 与 Auto-fix 边界。  
**产物**：gate matrix baseline、compatibility baseline、report baseline、recheck/fix baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Gate matrix and report models slice

**目标**：落下 MVP gate matrix、Compatibility 执行策略与机器可消费 report payload 的共享结构化模型，先稳定 `018` 的 policy/report truth，不直接进入完整 gate runtime。
**产物**：`src/ai_sdlc/models/frontend_gate_policy.py`、`tests/unit/test_frontend_gate_policy_models.py`、`src/ai_sdlc/models/__init__.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `models/`、`tests/` 与 execution log 变更。

### Phase 5：Gate policy artifact slice

**目标**：把共享 gate policy / compatibility policy / report types 物化为 `governance/frontend/gates/**` 的 canonical artifact tree，使后续 verify/gate integration 消费 artifact 而不是直接耦合 Python builder。
**产物**：`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`、可选 `src/ai_sdlc/generators/__init__.py` 导出、`tests/unit/test_frontend_gate_policy_artifacts.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `generators/`、`tests/` 与 execution log 变更。

### Phase 6：Frontend gate verification helper slice

**目标**：提供 work-item-scoped 的 `frontend gate verification` helper，把 gate policy artifact、generation governance artifact 与 contract verification 聚合为 verify 可消费的统一 report/context，而不直接实现完整 gate runtime。
**产物**：`src/ai_sdlc/core/frontend_gate_verification.py`、`tests/unit/test_frontend_gate_verification.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 7：Verify constraints attachment slice

**目标**：将 scoped frontend gate summary 接到 `build_constraint_report()` 与 `build_verification_gate_context()`，让 active `018` 在 verify surface 上具备真实 frontend gate summary。
**产物**：`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 8：VerificationGate aggregation slice

**目标**：将 `frontend_gate_verification` payload 正式并入 `VerificationGate / VerifyGate` 的 gate checks，使 gate layer 能识别 frontend gate summary 的 presence、linkage 与 clear status。
**产物**：`src/ai_sdlc/gates/pipeline_gates.py`、`tests/unit/test_gates.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `gates/`、`tests/` 与 execution log 变更。

### Phase 9：Verify CLI summary surface slice

**目标**：将 scoped frontend gate summary 暴露到 `ai-sdlc verify constraints` 的终端输出，使 operator 在不读取 JSON payload 的前提下也能直接看到 frontend gate verdict 与 coverage gap 摘要。
**产物**：`src/ai_sdlc/cli/verify_cmd.py`、`tests/integration/test_cli_verify_constraints.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| gate truth order | 文档交叉引用检查 | 人工审阅 |
| explicit compatibility wording | formal wording review | 人工审阅 |
| report boundary clarity | contract review | 测试矩阵回挂 |
| downstream handoff clarity | file-map review | 人工审阅 |
| gate matrix model correctness | `uv run pytest tests/unit/test_frontend_gate_policy_models.py -q` | model payload / builder review |
| gate policy artifact correctness | `uv run pytest tests/unit/test_frontend_gate_policy_artifacts.py -q` | artifact file layout / yaml payload review |
| frontend gate verification helper correctness | `uv run pytest tests/unit/test_frontend_gate_verification.py -q` | scoped verify payload review |
| frontend gate verify attachment correctness | `uv run pytest tests/unit/test_verify_constraints.py -q` | active `018` verify surface review |
| frontend gate verification aggregation correctness | `uv run pytest tests/unit/test_gates.py -q` | VerificationGate / VerifyGate payload review |
| frontend gate CLI summary correctness | `uv run pytest tests/integration/test_cli_verify_constraints.py -q -k "018_frontend_gate"` | terminal wording / exit-code review |
