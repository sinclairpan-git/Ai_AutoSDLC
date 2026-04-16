---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "specs/141-program-manifest-root-census-backfill-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
---
# 实施计划：Program Truth Pipeline Injection Baseline

**编号**：`146-program-truth-pipeline-injection-baseline` | **日期**：2026-04-16 | **规格**：specs/146-program-truth-pipeline-injection-baseline/spec.md

## 概述

`146` 的目标不是再次扩 program truth schema，而是把 `140/141/145` 已建立的根级真值真正注入 AI-SDLC 流水线。推荐顺序是：先冻结 handoff contract 与诊断语义，再实现 manifest mapping / freshness remediation surfaces，最后把 `close-check / status / run-stage` 接到统一的 truth injection gate 上。

## 技术背景

**语言/版本**：Python 3.11
**主要依赖**：`ProgramService`、`workitem init` scaffolder、`workitem close-check`、`program status`、`program truth sync`、runner/stage gate surfaces
**存储**：根级 `program-manifest.yaml`、`specs/146-program-truth-pipeline-injection-baseline/*`
**测试**：focused unit + integration + docs-only governance verification
**目标平台**：program truth pipeline injection / diagnostic surfaces
**约束**：

- 不新增第二份 truth ledger 或平行 dashboard；
- 不让 read-only surfaces 偷写 `truth_snapshot`；
- 先收口 pipeline truth injection contract，再进入具体代码改造；
- 当前 formal baseline 不得越界到前端业务 capability 实现；
- stale / unmapped / blocked 必须保持诊断语义分离。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值 | 继续只使用根 `program-manifest.yaml` + `truth_snapshot`，不引入第二 program truth |
| 流程诚实 | 明确区分 `manifest_unmapped`、`truth_snapshot_stale` 与业务 capability blocker |
| 最小改动面 | 先冻结 contract / diagnostics / verification profile，再进入实现切片 |
| 阶段注入 | 把 global truth 从审计层推进为 pipeline surface 必须消费的治理前提 |

## 项目结构

### 文档结构

```text
specs/146-program-truth-pipeline-injection-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/core/close_check.py
src/ai_sdlc/core/workitem_scaffold.py
src/ai_sdlc/cli/program_cmd.py
src/ai_sdlc/cli/workitem_cmd.py
src/ai_sdlc/core/runner.py
src/ai_sdlc/gates/pipeline_gates.py
tests/unit/test_program_service.py
tests/unit/test_close_check.py
tests/integration/test_cli_program.py
tests/integration/test_cli_workitem_close_check.py
```

## 阶段计划

### Phase 0：研究与决策冻结

**目标**：冻结 `146` 的 scope、handoff contract 与 diagnostic semantics  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`development-summary.md`  
**验证方式**：formal docs review + `verify constraints` + `close-check`  
**回退方式**：仅回退 `specs/146/...` 与本次 manifest authoring 变更

### Phase 1：manifest mapping 与 truth sync handoff contract

**目标**：定义 `workitem init` 之后如何显式进入 global truth  
**产物**：manifest entry materialization policy、truth sync required-state policy、operator next-action contract  
**验证方式**：unit + integration fixtures 覆盖 unmapped / stale / fresh  
**回退方式**：回退 handoff diagnostics 与对应 tests

### Phase 2：diagnostic surfaces 与 gating integration

**目标**：让 `close-check / status / run-stage` 消费 truth freshness  
**产物**：diagnostic surface contract、stale surfaced policy、read-only boundary guard  
**验证方式**：CLI integration + stage-gate regression  
**回退方式**：回退 close/status/stage wiring，不回退 ledger authoring schema

### Phase 3：truth-only verification profile 与收口

**目标**：为 manifest/snapshot-only 变更建立诚实验证口径  
**产物**：verification profile contract、docs/rules alignment、close wording update  
**验证方式**：focused verification profile regression + `program status/truth sync` refresh  
**回退方式**：回退 profile/rules 变更并保留原 close diagnostics

## 工作流计划

### 工作流 A：new formal workitem truth handoff

**范围**：`workitem init`、manifest mapping、truth sync required-state  
**影响范围**：新 formal workitem 的纳管路径  
**验证方式**：新工单创建后能明确得到 unmapped/fresh/remediation 诊断  
**回退方式**：回退 handoff guidance 和 manifest materialization policy

### 工作流 B：diagnostic and gate surfacing

**范围**：`workitem close-check`、`program status`、`run/stage`  
**影响范围**：truth freshness 如何进入关键 operator surface  
**验证方式**：stale/unmapped/blocked 语义分离 regression  
**回退方式**：回退 status/close/stage 集成，保留 ledger 只读 contract

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `workitem init -> manifest mapping` | targeted CLI regression | source inventory / truth audit review |
| `manifest mapped -> truth sync required` | `program truth sync --dry-run/--execute` | `program status` freshness check |
| `close-check / status diagnostics` | focused unit + integration tests | docs consistency review |
| truth-only verification profile | `verify constraints` + profile-specific checks | `git diff --check` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| manifest mapping 是在 `workitem init` 自动 materialize，还是以 hard guidance 方式显式交棒 | 待实现阶段决定 | Phase 1 |
| `run --dry-run` 对 stale truth 采取 advisory 还是 gated surfaced 语义 | 待实现阶段决定 | Phase 2 |
| truth-only verification profile 的命名与落盘位置 | 待实现阶段决定 | Phase 3 |

## 实施顺序建议

1. 先冻结 `146` formal baseline，明确 handoff / diagnostics / verification truth
2. 再实现 manifest mapping 与 truth sync required-state contract
3. 然后接 `close-check / status / run-stage` diagnostics
4. 最后补 verification profile、docs/rules alignment 与 focused regression
