---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend enterprise-vue2 Provider Baseline

**编号**：`016-frontend-enterprise-vue2-provider-baseline` | **日期**：2026-04-03 | **规格**：specs/016-frontend-enterprise-vue2-provider-baseline/spec.md

## 概述

本计划处理的是 `009` 下游的 `enterprise-vue2 Provider` formal baseline，而不是直接实现完整 Vue2 runtime 包。当前仓库已经在上游锁定并实现了：

- `011`：frontend contract models、artifacts、drift helper 与 verify/gate 主链
- `013 / 014`：observation provider、export 与 runtime attachment 主链
- `015`：UI Kernel standard body、Kernel models 与 `kernel/frontend/**` artifact instantiation

但 `009` 的另一条 MVP 主线“enterprise-vue2 Provider profile”仍缺少独立 child work item 去冻结：

- Provider 到底承载什么，哪些属于公司组件库能力来源而不是标准内核
- `Ui* -> 企业实现` 映射原则、首批映射建议与白名单包装范围如何定义
- 危险能力隔离、`禁止全量 Vue.use` 与 Legacy Adapter 边界如何正式落盘
- 后续 Provider profile / wrapper contract / compatibility handoff 应从哪里开始

因此，本计划的目标是建立统一的 `Frontend enterprise-vue2 Provider Baseline`：

- 先冻结 Provider truth order 与 non-goals
- 再冻结映射原则、白名单包装、危险能力隔离与 Legacy Adapter 边界
- 最后给出后续 `models / runtime profile / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入第一批实现切片：`Provider profile models`，把 `Ui* -> 企业实现` 映射、白名单包装范围、危险能力隔离与 Legacy Adapter 边界收敛到共享 `models/`；不同时触碰业务项目 runtime 包、generation 约束或 gate diagnostics。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`009` 母规格、`015` UI Kernel baseline、冻结设计稿第 10 章  
**现有基础**：

- [`../../specs/009-frontend-governance-ui-kernel/spec.md`](../../specs/009-frontend-governance-ui-kernel/spec.md) 已明确 Provider 是五条主线之一
- [`../../specs/015-frontend-ui-kernel-standard-baseline/spec.md`](../../specs/015-frontend-ui-kernel-standard-baseline/spec.md) 已锁定 `Ui*` 协议、page recipe 标准本体与 `kernel/frontend/**` artifact
- 冻结设计稿第 10 章已给出 Provider 定位、映射原则、白名单包装、危险能力隔离与 Legacy Adapter 章节

**目标平台**：AI-SDLC 框架仓库自身，面向后续 enterprise-vue2 Provider profile baseline  
**主要约束**：

- `Provider != UI Kernel != 公司组件库`
- Provider 只能承接 UI Kernel，不得反向改写 `Ui*` 协议或 recipe 标准本体
- 当前阶段只冻结 Provider profile truth，不直接进入业务项目运行时代码
- Legacy Adapter 必须是受控桥接层，不得变成长期默认入口
- 默认入口不得以全量 `Vue.use` 公司组件库暴露给 AI 链路

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 MVP 必需的 Provider profile 主线，不扩张到 modern provider、完整 runtime 包或公司组件库内部治理 |
| MUST-2 关键路径可验证 | 映射原则、白名单包装、危险能力隔离与 Legacy Adapter 边界都必须可被文档和后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 Provider 主线，当前变更仅作用于 `specs/016/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 将 Provider baseline 落为 canonical truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 formal docs 与后续文件面，不引入业务项目 runtime 代码 |

## 项目结构

### 文档结构

```text
specs/016-frontend-enterprise-vue2-provider-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的实现触点

```text
src/ai_sdlc/
├── models/
│   └── frontend_provider_profile.py           # Ui* -> 企业实现映射 / whitelist / isolation / legacy adapter profile
└── generators/
    └── ...                                    # downstream only

tests/
└── unit/test_frontend_provider_profile_models.py
```

## 开始执行前必须锁定的阻断决策

- Provider 是运行时适配层，不是统一内核
- 公司组件库只能作为 Provider 能力来源，不能直接成为 AI 默认入口
- `Ui* -> 企业实现` 映射必须由 UI Kernel 协议主导
- 白名单包装必须同时做 API、能力和依赖收口
- 危险能力默认关闭，例外只能走结构化声明和下游 checker / gate
- Legacy Adapter 只是过渡桥，不是长期默认入口
- 默认接入方式禁止全量 `Vue.use` 公司组件库

未锁定上述决策前，不得进入 `016` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| provider truth baseline | 定义 Provider 定位、truth order、non-goals | 不得回写 UI Kernel 标准本体或 Contract truth |
| mapping profile baseline | 定义 `Ui* -> 企业实现` 映射与首批包装对象 | 不得把底层组件库 API 直接提升为 Kernel 协议 |
| isolation / legacy baseline | 定义危险能力隔离、Legacy Adapter 与 `no full Vue.use` 边界 | 不得把兼容桥写成长期默认入口 |
| implementation handoff | 为后续 models / runtime profile / tests 提供 file-map 与测试矩阵 | 不得直接进入 business project runtime 包或 gate implementation |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 `enterprise-vue2 Provider` 主线从 `009` 母规格拆成单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/016/...` 文档改动。

### Phase 1：Provider truth freeze

**目标**：锁定 Provider 在 `UI Kernel -> Provider -> generation / gate / runtime` 主线中的 truth order、scope 与 non-goals。  
**产物**：scope baseline、truth-order baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Mapping / whitelist / isolation freeze

**目标**：锁定 `Ui* -> 企业实现` 映射原则、首批白名单包装对象、危险能力隔离与 Legacy Adapter 边界。  
**产物**：mapping baseline、whitelist baseline、isolation baseline、legacy bridge baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Provider profile models slice

**目标**：落下 enterprise-vue2 Provider 的最小结构化模型与 MVP builder，先稳定 `Ui* -> 企业实现` 映射、白名单包装范围、危险能力隔离与 Legacy Adapter 边界。
**产物**：`src/ai_sdlc/models/frontend_provider_profile.py`、`tests/unit/test_frontend_provider_profile_models.py`、`src/ai_sdlc/models/__init__.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `models/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Provider truth freeze

**范围**：Provider truth order、scope、non-goals、`Provider != UI Kernel != 公司组件库`。  
**影响范围**：后续 Provider profile、generation governance 与 gate compatibility。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Mapping / whitelist / isolation freeze

**范围**：`Ui* -> 企业实现` 映射原则、白名单包装、危险能力隔离、Legacy Adapter、`no full Vue.use`。  
**影响范围**：后续 Provider profile、runtime wrapper、generation whitelist 与 gate 规则。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime 代码。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream handoff。  
**影响范围**：后续 `models / runtime profile / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 Provider runtime / gate / generation 实现。

### 工作流 D：Provider profile models slice

**范围**：`Ui* -> 企业实现` 映射模型、白名单包装对象、危险能力隔离与 Legacy Adapter policy。
**影响范围**：后续 Provider artifact、runtime wrapper、generation whitelist 与 compatibility gate 的上游真值。
**验证方式**：`tests/unit/test_frontend_provider_profile_models.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 runtime wrapper、generation 或 gate 实现。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| provider truth order | 文档交叉引用检查 | 人工审阅 |
| kernel/provider/library separation | formal wording review | 人工审阅 |
| mapping and whitelist clarity | contract review | 测试矩阵回挂 |
| isolation and legacy boundary clarity | scope review | 术语对账 |
| downstream handoff clarity | file-map review | 人工审阅 |
| provider profile model correctness | `uv run pytest tests/unit/test_frontend_provider_profile_models.py -q` | model payload / builder review |
