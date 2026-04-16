---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
---
# 实施计划：Frontend P2 Page UI Schema Baseline

**编号**：`147-frontend-p2-page-ui-schema-baseline` | **日期**：2026-04-16 | **规格**：specs/147-frontend-p2-page-ui-schema-baseline/spec.md

## 概述

`147` 的目标是把前端后续主线的第一条 child 物化成 provider-neutral schema runtime baseline。顺序保持为：先 formalize schema layer contract，再进入 schema model / serialization，随后落实 validator / versioning，最后接 provider/kernel consumption handoff 与下游 theme/quality/consistency 引用。

## 技术背景

**语言/版本**：Python 3.11
**主要依赖**：frontend contract/kernel docs、page recipe truth、provider/style solution baseline、schema models/validators/artifacts
**存储**：`specs/147-frontend-p2-page-ui-schema-baseline/*`
**测试**：formal docs review + 后续 focused unit/integration regression
**目标平台**：frontend schema truth / provider-neutral page-ui structure
**约束**：

- 不重写 `068`、`073` 的既有 truth；
- 不提前混入 theme governance、quality platform、cross-provider certification；
- schema truth 必须保持 provider-neutral。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值顺序 | 先冻结并物化 schema truth，再让 theme/quality/provider consumption 继续往下走 |
| 最小改动面 | 只实现 page/ui schema baseline 自身，不实现新的 provider/theme/quality runtime |
| 范围诚实 | 明确 `147` 是结构层，不是 recipe/style 第一阶段重做 |
| 后续可执行性 | 给出 implementation slice 顺序，避免下游 child 再重做 capability census |

## 项目结构

### 文档结构

```text
specs/147-frontend-p2-page-ui-schema-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
src/ai_sdlc/models/
src/ai_sdlc/generators/
src/ai_sdlc/core/
src/ai_sdlc/cli/
tests/unit/
tests/integration/
```

## 阶段计划

### Phase 0：研究与决策冻结

**目标**：冻结 `147` 的 schema layer scope、与 `068/073/145` 的关系、下游依赖位置
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`development-summary.md`
**验证方式**：formal docs review + `verify constraints` + `close-check`
**回退方式**：仅回退 `specs/147/...` 与对应 manifest authoring 变更

### Phase 1：schema model / serialization implementation slice

**目标**：建立 page schema / ui schema 的模型、序列化与最小结构实例
**产物**：`frontend_page_ui_schema.py` models、baseline builders、focused unit tests
**验证方式**：schema structure unit tests + red/green TDD record
**回退方式**：回退 schema model/serialization 文件

### Phase 2：validator / versioning / anchor contract

**目标**：补 schema versioning、anchor/slot validation 与 drift diagnostics
**产物**：artifact materialization、validator layer、versioning contract、diagnostic tests
**验证方式**：unit + integration focused checks
**回退方式**：回退 validator/versioning 增量

### Phase 3：provider/kernel consumption handoff

**目标**：让 provider/style solution 与 kernel surface 开始消费上游 schema truth
**产物**：provider-neutral consumption contract、ProgramService handoff、CLI surfaced diagnostics
**验证方式**：integration tests against existing solution surfaces
**回退方式**：回退 provider/kernel consumption，不回退 schema core

## 工作流计划

### 工作流 A：schema truth formalization

**范围**：page schema、ui schema、versioning、render slot、section anchor
**影响范围**：后续前端 Track A 的 canonical truth
**验证方式**：formal docs consistency + downstream dependency review
**回退方式**：回退 `147` formal docs 与 manifest entry

### 工作流 B：schema runtime materialization

**范围**：page schema / ui schema models、artifact materialization、validator/versioning
**影响范围**：Track A 的 machine-verifiable runtime truth
**验证方式**：focused unit tests + artifact root review
**回退方式**：回退 models/generators/core 增量

### 工作流 C：downstream consumption preparation

**范围**：theme/quality/consistency 后续 child 的 schema anchor 输入
**影响范围**：Track B/C/D 的上游结构真值
**验证方式**：ProgramService/CLI handoff review + integration tests
**回退方式**：回退 handoff/CLI wording 与 orchestration surface

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `145 -> 147` child handoff | docs consistency review | program truth mirror review |
| schema layer boundary | model + validator unit tests | compare against `068/073` |
| implementation slice order | `147/plan.md` review | downstream dependency table review |
| artifact materialization | artifact unit tests | `git diff --check` |
| provider/kernel handoff | ProgramService + CLI integration tests | `verify constraints` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| page schema 与 ui schema 的最终字段粒度 | 以 provider-neutral page/slot/anchor/block 最小集合实现 | 已决议 |
| versioning 是否采用显式 schema version 字段还是 capability-level compatibility matrix | 采用显式 versioning contract + compatible version list | 已决议 |
| provider/kernel consumption 的第一条 runtime slice 应先接 solution snapshot 还是独立 validator CLI | 先接 ProgramService + CLI handoff，再供后续 Track B/C/D 消费 | 已决议 |

## 实施顺序建议

1. 先 formalize `147`，固定 schema truth 与 upstream/downstream boundary
2. 再进入 schema model / serialization 首切片
3. 然后实现 artifact materialization 与 validator / versioning / anchor diagnostics
4. 最后再接 provider/kernel consumption，并作为 Track B/C/D 的输入
