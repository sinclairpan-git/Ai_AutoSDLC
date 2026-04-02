---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Contract Authoring Baseline

**编号**：`011-frontend-contract-authoring-baseline` | **日期**：2026-04-02 | **规格**：specs/011-frontend-contract-authoring-baseline/spec.md

## 概述

本计划处理的是 `009` 下游 `Contract` 主线的 formal baseline，而不是直接实现前端 runtime。当前仓库已经在 `009` 中锁定“`PRD/spec -> Contract -> code` 才是前端真值顺序”，但还缺少一个单独 child work item 去冻结：

- Contract 到底承载什么
- Contract 如何进入现有 stage / gate / artifact 链路
- legacy 扩展字段如何在 MVP 阶段受控落位
- 后续模型、实例化、drift 检查与测试应从哪里开始

因此，本计划的目标是建立统一的 `Frontend Contract Authoring Baseline`：

- 先冻结 Contract 的对象边界
- 再冻结 Contract 在现有 artifact 链路中的位置
- 再冻结 legacy 扩展字段和 drift 处理口径
- 最后给出实现前的最小文件面与验证基线

该计划当前先停在 formal baseline 与 implementation handoff，不直接进入 `src/` / `tests/` 代码实现。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs、后续实现预计使用 Pydantic models  
**主要依赖**：`009` 母规格、现有 `ai-sdlc` stage/gate 流程、`src/ai_sdlc/rules/pipeline.md` 的 artifact 约束  
**现有基础**：

- [`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md) 已锁定 `Contract` 为五条主线之一
- 设计冻结稿在 [`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md) 中明确了 Contract 的对象边界、artifact 链路和 drift 口径
- [`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md) 已要求 `decompose` 阶段消费 `contracts/`

**目标平台**：AI-SDLC 框架仓库自身，面向后续 Contract 模型、实例化、验证与 drift 控制实现  
**主要约束**：

- `Contract != UI Kernel != Provider != Gate`
- `recipe declaration` 只能在 Contract 层，不能写回 UI Kernel 标准本体
- Contract 必须进入现有 artifact 链路，不得另起独立前端流水线
- legacy 信息必须优先作为 `page/module contract` 扩展字段承载
- 当前阶段只冻结 formal baseline，不直接承诺完整 schema/runtime 实现

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 MVP 必需的 Contract 对象和链路，不扩张到 Kernel / Provider / Gate 全实现 |
| MUST-2 关键路径可验证 | Contract 边界、artifact 链路、legacy 扩展字段与 drift 口径都必须可被文档和后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 Contract 主线，所有当前变更仅作用于 `specs/011/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md` 将 Contract baseline 落为 canonical truth，避免继续依赖散落设计段落 |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 formal docs 与后续文件面，不引入前端 runtime 或业务项目代码 |

## 项目结构

### 文档结构

```text
specs/011-frontend-contract-authoring-baseline/
├── spec.md
├── plan.md
└── tasks.md
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── models/
│   └── frontend_contracts.py        # Contract models / legacy extension fields
├── generators/
│   └── frontend_contract_artifacts.py
│                                     # refine/design -> contract artifact instantiation
├── core/
│   └── frontend_contract_drift.py    # contract-vs-code drift helpers
├── gates/
│   └── frontend_contract_gate.py     # later contract-aware verify/gate surface
└── rules/
    └── pipeline.md                   # contract artifact consumption wording

tests/
├── unit/test_frontend_contract_models.py
├── unit/test_frontend_contract_artifacts.py
├── unit/test_frontend_contract_drift.py
└── integration/test_frontend_contract_stage_flow.py
```

### 推荐的后续 artifact 面

```text
contracts/
└── frontend/
    ├── page-contract.schema.yaml
    └── module-contract.schema.yaml
```

## 开始执行前必须锁定的阻断决策

- Contract 是实例化 artifact，不是解释性附录
- `page recipe standard body != recipe declaration`
- `Contract` 同时服务于生成、检查与修复
- legacy 信息优先走 `page/module contract` 扩展字段
- Contract 漂移必须在 `回写 Contract` 与 `修正实现代码` 之间二选一
- Contract 接入现有 stage / gate / artifact 链路，不得另起平行系统

未锁定上述决策前，不得进入 `011` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| contract object model | 定义 `page/module contract`、规则集合与 legacy 扩展字段 | 不得写入 UI Kernel 标准本体或 Provider 映射 |
| artifact instantiation | 定义 refine/design 如何产出 Contract artifact | 不得把 Contract 降级成 prompt 注释或临时 Markdown |
| drift control | 定义 Contract 与实现不一致时的回写/修正口径 | 不得接受长期漂移或“先写代码后补 Contract” |
| downstream verification | 定义后续模型、序列化、stage integration 的最小验证面 | 不得跳过 Contract 直接只看代码或 prompt |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 `Contract` 主线从 `009` 母规格拆成单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/011/...` 文档改动。

### Phase 1：Contract object model freeze

**目标**：锁定 Contract 对象边界、MVP 承载对象和与 UI Kernel 的关系。  
**产物**：Contract object matrix、MVP object coverage、boundary truth。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact chain and drift baseline

**目标**：锁定 Contract 在 `refine / design / decompose / verify / execute / close` 中的落位，以及 drift 处理口径。  
**产物**：artifact-chain baseline、drift policy、stage integration contract。  
**验证方式**：stage relationship review。  
**回退方式**：不写入代码。

### Phase 3：Legacy extension and implementation handoff

**目标**：锁定 legacy 扩展字段、推荐文件面和后续最小验证矩阵。  
**产物**：legacy extension baseline、implementation touchpoints、tests matrix。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Contract object authoring baseline

**范围**：`page/module contract`、`recipe declaration`、规则对象、例外字段。  
**影响范围**：后续 `models/`、`generators/` 与 Contract artifact 设计。  
**验证方式**：对象矩阵与边界审阅。  
**回退方式**：不进入实现。

### 工作流 B：Artifact chain and drift control freeze

**范围**：stage integration、Contract drift、contract-vs-code truth order。  
**影响范围**：后续 `decompose / verify / execute / close` 的 Contract 消费面。  
**验证方式**：关系图与语义对账。  
**回退方式**：不触发 Gate 实现。

### 工作流 C：Legacy extension and implementation handoff

**范围**：`compatibility_profile / migration_level / legacy_boundary_ref / migration_scope`、推荐代码面、测试矩阵。  
**影响范围**：后续 Contract 模型和兼容治理实现。  
**验证方式**：legacy 术语一致性与 file-map 审阅。  
**回退方式**：不写入任何 runtime 代码。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Contract / Kernel 边界 | 文档交叉引用检查 | 人工审阅 |
| MVP Contract 对象覆盖 | object matrix 对账 | 设计稿回挂复核 |
| artifact chain 一致性 | stage 关系检查 | 术语搜索 |
| legacy 扩展字段收敛 | 全文术语检查 | 人工审阅 |
| next-step readiness | `uv run ai-sdlc verify constraints` | `git status --short` |

## 已锁定决策

- `011` 是 `009` 的 child work item，不再回到母规格层混做 Contract 细节
- Contract 当前先冻结 formal baseline，再进入模型/实例化实现
- `recipe declaration` 必须归 Contract，不得在后续实现中混入 UI Kernel
- Contract 模型、artifact 实例化、drift 检查和 stage integration 是后续实现的主路径
- legacy 扩展字段优先留在 Contract 层，而不是单独拉出迁移专用 artifact

## 实施顺序建议

1. 先冻结 `011` formal spec/plan/tasks，确保 Contract 主线有独立 canonical truth。
2. 再冻结 `page/module contract`、规则对象与 `recipe declaration` 的对象边界。
3. 再冻结 Contract 的 artifact 链路、drift 口径和 legacy 扩展字段。
4. 完成 formal baseline 校验后，再决定是否在 `011` 内继续进入模型/实例化实现。
