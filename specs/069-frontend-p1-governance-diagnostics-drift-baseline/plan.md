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

本计划处理的是 `066` 下游的第三条 P1 child baseline：`Frontend P1 Governance Diagnostics Drift Baseline`。它不是 recheck / remediation child，不是 visual / a11y child，也不是 provider/runtime 实现切片。当前仓库已经在上游锁定了：

- `017`：generation governance 的 recipe / whitelist / hard rules / token rules / exceptions truth
- `018`：同一套 gate matrix、Compatibility 执行口径、结构化 report family 与 verify surface
- `065`：sample source self-check 只作为显式 observation 输入源
- `067`：P1 semantic component set 与页面级状态语义扩展
- `068`：P1 page recipe set、area constraint 与 recipe 级状态期望

但 P1 “体验稳定层”仍缺少一份独立 canonical baseline 去冻结：

- diagnostics / drift 到底要消费哪些 P1 上游 truths
- whitelist / token / recipe / state coverage 的扩张边界是什么
- gap / empty / drift 如何在同一套 report family 下保持诚实区分
- 与 `070` recheck / remediation feedback、`071` visual / a11y foundation 的 handoff boundary 在哪里

因此，本计划的目标是建立统一的 `Frontend P1 Governance Diagnostics Drift Baseline`：

- 先冻结 diagnostics truth order、scope 与 non-goals
- 再冻结 coverage matrix、drift classification 与 compatibility feedback boundary
- 最后给出未来 diagnostics / gate / verify 文件面的推荐触点、测试矩阵与进入实现前提

当前批次只做 docs-only formal freeze，不进入 `src/` / `tests/` 实现。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`017` generation governance、`018` gate compatibility、`065` observation self-check、`067/068` P1 kernel / recipe truths、冻结设计稿第 7.6 / 7.8 / 11 / 12 章  
**主要约束**：

- diagnostics 只能消费上游 truth，不得反向改写 Contract / Kernel / generation / gate baseline
- Compatibility 不能被实现成第二套 gate / 规则系统
- observation 输入必须显式 materialize；不得因为仓库内存在 sample fixture 而隐式生成 artifact
- 当前阶段只冻结 diagnostics / drift baseline，不直接实现 recheck / remediation feedback、visual / a11y 或 provider/runtime

## 项目结构

```text
specs/069-frontend-p1-governance-diagnostics-drift-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的未来实现触点

```text
src/ai_sdlc/
├── models/
│   ├── frontend_generation_constraints.py    # whitelist / token / exception truth consumed by diagnostics
│   └── frontend_gate_policy.py               # gate matrix / compatibility policy / report family
├── core/
│   ├── frontend_gate_verification.py         # diagnostics aggregation candidate
│   ├── verify_constraints.py                 # verify surface attachment candidate
│   └── frontend_contract_observation_provider.py
├── gates/
│   └── frontend_contract_gate.py             # frontend diagnostics / gate aggregation candidate
└── generators/
    ├── frontend_generation_constraint_artifacts.py
    └── frontend_gate_policy_artifacts.py

tests/
├── unit/test_frontend_generation_constraints.py
├── unit/test_frontend_gate_policy_models.py
├── unit/test_frontend_gate_verification.py
├── unit/test_frontend_contract_gate.py
├── unit/test_verify_constraints.py
└── integration/test_cli_verify_constraints.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 P1 diagnostics / drift 主线从 `066` 的母级 planning baseline 中拆成独立 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`.ai-sdlc/project/config/project-state.yaml`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 `specs/069/...` 与 `project-state.yaml`。

### Phase 1：Diagnostics truth order freeze

**目标**：锁定 `069` 在 `067 / 068 / 017 / 018 / 065` 之后、`070 / 071` 之前的 truth order、scope 与 non-goals。  
**产物**：positioning baseline、truth-order baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Coverage matrix freeze

**目标**：锁定 P1 diagnostics 在 semantic component / recipe / state / whitelist / token 五类 coverage 面上的最小扩张边界。  
**产物**：coverage matrix baseline、consumption boundary baseline。  
**验证方式**：formal docs review。  
**回退方式**：不写入代码。

### Phase 3：Drift / gap / compatibility feedback freeze

**目标**：锁定 `input gap / stable empty observation / drift` 分类、report family 复用边界，以及同一套 gate matrix 的兼容执行口径相关反馈面。  
**产物**：drift classification baseline、compatibility feedback baseline、observation input boundary。  
**验证方式**：formal docs review。  
**回退方式**：不写入代码。

### Phase 4：Implementation handoff and validation freeze

**目标**：锁定未来 diagnostics / gate / verify 文件面、最小测试矩阵、docs-only honesty 与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execution handoff baseline。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check`、formal docs review。  
**回退方式**：仅回退 planning baseline。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| `069` diagnostics / drift baseline | 冻结 P1 coverage matrix、drift classification、compatibility feedback boundary | 不得重写 `067/068` kernel / recipe truth，不得抢跑 `070/071` |
| `070` recheck / remediation child | 扩 bounded remediation feedback、recheck 策略与作者体验闭环 | 不得在 diagnostics truth 未冻结前单独扩张 |
| `071` visual / a11y child | 承接基础 visual / a11y 检查能力 | 不得膨胀为完整 visual regression 或完整 a11y 平台 |
| provider/runtime implementation | 承接具体组件映射、执行逻辑与项目接入 | 不得反向定义 diagnostics truth |

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| diagnostics truth order | 文档交叉引用检查 | 人工审阅 |
| compatibility wording honesty | formal wording review | 人工审阅 |
| gap / empty / drift distinction | classification review | 人工审阅 |
| coverage matrix clarity | contract review | 测试矩阵回挂 |
| downstream handoff clarity | file-map review | 人工审阅 |

## 最小测试矩阵

| 主题 | 未来主验证方式 | 说明 |
|------|----------------|------|
| semantic component coverage diagnostics | `uv run pytest tests/unit/test_frontend_gate_verification.py -q` | 验证 `067` 新增 `Ui*` 的 diagnostics 聚合语义 |
| recipe coverage diagnostics | `uv run pytest tests/unit/test_frontend_contract_gate.py -q` | 验证 `068` recipe / area constraint 消费口径 |
| whitelist / token diagnostics | `uv run pytest tests/unit/test_frontend_generation_constraints.py -q` | 验证 `017` truth 在 P1 扩张场景中的消费 |
| gap / empty / drift verify surface | `uv run pytest tests/unit/test_verify_constraints.py -q` | 验证三类输入/结果分类不混淆 |
| CLI diagnostics summary wording | `uv run pytest tests/integration/test_cli_verify_constraints.py -q` | 验证 operator 可见反馈面 |

## 执行前提与回退

- 只有在 `069` docs-only 门禁通过且用户明确要求继续时，才允许进入 diagnostics 相关实现批次或 formalize `070/071`
- 当前批次不得修改 `src/`、`tests/`、root `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`
- 当前批次不得生成 `development-summary.md`，也不得宣称 close-ready 或 program sync
- 若本批次需要回退，只回退 `specs/069/...` 与 `.ai-sdlc/project/config/project-state.yaml`
