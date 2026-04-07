---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P1 Governance Diagnostics Drift Baseline

**编号**：`069-frontend-p1-governance-diagnostics-drift-baseline` | **日期**：2026-04-06 | **规格**：specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md

## 概述

本计划处理的是 `066` 下游的第三条 P1 child baseline：`Frontend P1 Governance Diagnostics Drift Baseline`。formal baseline 已完成，当前允许继续执行唯一的 Batch 5 implementation slice，把 `spec.md` 已冻结的 diagnostics coverage matrix、drift classification 与 compatibility feedback boundary 落到 gate policy model / artifact truth。

当前仓库已经在上游锁定了：

- `017`：generation governance 的 whitelist / hard rules / token rules / exceptions truth
- `018`：同一套 gate matrix、Compatibility 执行口径、结构化 report family 与 gate policy artifacts
- `065`：sample source self-check 只作为显式 observation 输入源
- `067`：P1 semantic component set 与页面级状态语义扩展
- `068`：P1 page recipe set、area constraint 与 recipe 级状态期望

`069` Batch 5 的目标不是进入 verify / gate runtime，而是先建立统一的 diagnostics truth surface：

- 让 gate policy model 能结构化表达 P1 diagnostics coverage matrix
- 让 drift / gap classification 先以 artifact truth 形式落盘
- 让 compatibility feedback boundary 被写成 machine-consumable payload，而不是散落在文案里
- 继续把 `frontend_gate_verification.py`、`verify_constraints.py`、`frontend_contract_gate.py` 留给后续 child / 后续实现批次

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`017` generation governance、`018` gate compatibility、`065` observation self-check、`067/068` P1 kernel / recipe truths
**主要约束**：

- diagnostics 只能消费上游 truth，不得反向改写 Contract / Kernel / generation / gate baseline
- Compatibility 不能被实现成第二套 gate / 规则系统
- observation 输入必须显式 materialize；不得因为仓库内存在 sample fixture 而隐式生成 artifact
- 当前 Batch 5 只放行 gate policy model / artifact truth，不放行 verify / gate runtime

## 当前实现触点

```text
specs/069-frontend-p1-governance-diagnostics-drift-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

src/ai_sdlc/
├── models/
│   ├── frontend_generation_constraints.py
│   ├── frontend_gate_policy.py
│   ├── frontend_ui_kernel.py
│   └── __init__.py
└── generators/
    └── frontend_gate_policy_artifacts.py

tests/unit/
├── test_frontend_gate_policy_models.py
└── test_frontend_gate_policy_artifacts.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 P1 diagnostics / drift 主线从 `066` 的母级 planning baseline 中拆成独立 canonical formal docs。  
**状态**：已完成。
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。

### Phase 1：Diagnostics truth order freeze

**目标**：锁定 `069` 在 `067 / 068 / 017 / 018 / 065` 之后、`070 / 071` 之前的 truth order、scope 与 non-goals。  
**状态**：已完成。
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。

### Phase 2：Coverage matrix freeze

**目标**：锁定 P1 diagnostics 在 semantic component / recipe / state / whitelist / token 五类 coverage 面上的最小扩张边界。  
**状态**：已完成。
**验证方式**：formal docs review。

### Phase 3：Drift / gap / compatibility feedback freeze

**目标**：锁定 `input gap / stable empty observation / drift` 分类、report family 复用边界，以及 shared gate matrix 的 compatibility feedback boundary。
**状态**：已完成。
**验证方式**：formal docs review。

### Phase 4：Implementation handoff freeze

**目标**：锁定未来 diagnostics / gate / verify 文件面、最小测试矩阵、docs-only honesty 与进入实现前提。  
**状态**：已完成。
**验证方式**：formal docs review + docs-only 门禁。

### Phase 5：Diagnostics truth materialization slice

**目标**：把 `069` 已冻结的 diagnostics coverage matrix、drift classification 与 compatibility feedback boundary 落到 `frontend_gate_policy` model / artifact，并用定向 unit tests 证明它们与 `018` shared gate truth 保持一致。
**产物**：`src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`、`tests/unit/test_frontend_gate_policy_models.py`、`tests/unit/test_frontend_gate_policy_artifacts.py`、`task-execution-log.md`。
**验证方式**：RED/GREEN `pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/069-frontend-p1-governance-diagnostics-drift-baseline src/ai_sdlc/models src/ai_sdlc/generators tests/unit`。
**回退方式**：仅回退当前 work item docs、gate policy model / artifact 与对应 tests。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| `069` diagnostics / drift baseline | 冻结并 materialize P1 coverage matrix、drift classification、compatibility feedback boundary | 不得重写 `067/068` kernel / recipe truth，不得抢跑 `070/071` |
| `070` recheck / remediation child | 扩 bounded remediation feedback、recheck 策略与作者体验闭环 | 不得在 diagnostics truth 未 materialize 前单独扩张 |
| `071` visual / a11y child | 承接基础 visual / a11y 检查能力 | 不得膨胀为完整 visual regression 或完整 a11y 平台 |
| verify / gate runtime surfaces | 承接具体 diagnostics 聚合、终端输出与 gate aggregation | 不得反向定义 diagnostics truth |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| diagnostics truth-order 未漂移 | `spec.md / plan.md / tasks.md` 对账 | 人工审阅 |
| RED 证明 `069` builder 为真实增量 | 在 `710638f` 上应用测试补丁后执行定向 `pytest` | 失败形态归档到 execution log |
| diagnostics matrix / drift classification 可构造 | `uv run pytest tests/unit/test_frontend_gate_policy_models.py tests/unit/test_frontend_gate_policy_artifacts.py -q` | payload review |
| compatibility feedback honesty | model 断言 + artifact payload review | formal docs review |
| runtime 面未被越界修改 | `git diff --stat` + `git diff --check` 定向范围检查 | 人工审阅 |

## 最小测试矩阵

| 主题 | 主验证方式 | 说明 |
|------|------------|------|
| diagnostics coverage matrix builder truth | `uv run pytest tests/unit/test_frontend_gate_policy_models.py -q` | 验证 `067/068/017/018/065` 消费边界与结构化字段 |
| drift classification / compatibility feedback boundary | `uv run pytest tests/unit/test_frontend_gate_policy_models.py -q` | 验证 report family 复用与 shared mode honesty |
| gate policy artifact payload | `uv run pytest tests/unit/test_frontend_gate_policy_artifacts.py -q` | 验证新增 YAML file set 与 payload |
| lint / constraint hygiene | `uv run ruff check src tests`、`uv run ai-sdlc verify constraints` | 验证实现未破坏仓库门禁 |

## 执行前提与回退

- 只有在 `069` docs-only 门禁已通过且用户明确要求继续时，才允许进入 Batch 5 diagnostics truth materialization slice
- 当前 Batch 5 不得修改 `src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/gates/frontend_contract_gate.py`、integration tests、root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`
- 当前 Batch 5 不得生成 `development-summary.md`，也不得宣称 close-ready 或 program sync
- 若本批次需要回退，只回退 `specs/069/...`、`src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py` 与对应 tests
