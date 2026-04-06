---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend P1 Experience Stability Planning Baseline

**编号**：`066-frontend-p1-experience-stability-planning-baseline` | **日期**：2026-04-06 | **规格**：specs/066-frontend-p1-experience-stability-planning-baseline/spec.md

## 概述

本计划处理的是“在 frontend MVP 已冻结并落地主线之后，如何正式进入 P1”的母级 planning baseline，而不是新的产品实现工单。当前已经存在的前置真值包括：

- `009`：前端治理与 UI Kernel 的母规格
- `015`：UI Kernel 标准本体
- `017`：前端生成治理基线
- `018`：Compatibility 口径下的 gate 基线
- `065`：sample source self-check 的自包含路径

在这些 MVP truths 已经落稳的前提下，`066` 的目标只有四件事：

- 冻结 P1 的 scope 与 non-goals
- 冻结推荐 child tracks 与依赖 DAG
- 冻结 branch rollout policy 与 root truth sync 时机
- 为后续 child work item 的 formalize 提供单一 planning truth

当前批次只允许 **docs-only freeze**。`066` 不进入 `src/` / `tests/`，不创建 downstream child，不写入 root `program-manifest.yaml`，也不生成 `development-summary.md`。

## 技术背景

**语言/版本**：Markdown formal docs、YAML project state、Python 3.11+ 框架上下文  
**主要依赖**：`009` 母规格、`015` UI Kernel、`017` governance、`018` gate compatibility、`065` sample self-check、frontend design 总览  
**存储**：

- 当前母级 planning baseline：`specs/066-frontend-p1-experience-stability-planning-baseline/`
- 当前项目编号真值：`.ai-sdlc/project/config/project-state.yaml`

**测试**：`uv run ai-sdlc verify constraints`、`git diff --check`  
**目标平台**：Ai_AutoSDLC 框架仓库的 formal planning 层  
**主要约束**：

- P1 必须保持在 MVP 单一真值顺序之下演进，不改写 `009` truth order
- P1 不得偷渡 P2 的 `modern provider / multi-theme / multi-style`
- `066` 当前只冻结 planning truth，不得提前落根级 program sync
- downstream child work item 仍遵守一工单一分支与 formalize 先行的框架纪律

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | `066` 不扩张实现，只在 MVP 真值已稳的前提下冻结 P1 planning 边界 |
| MUST-2 关键路径可验证 | child track DAG、rollout policy 与 root sync 时机都写成 formal docs，可通过只读门禁核验 |
| MUST-3 范围声明与回退 | 当前批次只改 `specs/066/...` 与 `project-state.yaml`，回退边界清晰 |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 冻结 planning truth，并追加执行归档 |
| MUST-5 产品代码与开发框架隔离 | `066` 不写产品实现、不改 `src/` / `tests/`，保持 planning 与 runtime 隔离 |

## 项目结构

### 文档结构

```text
specs/066-frontend-p1-experience-stability-planning-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已冻结的 MVP truths

```text
specs/
├── 009-frontend-governance-ui-kernel/
├── 015-frontend-ui-kernel-standard-baseline/
├── 017-frontend-generation-governance-baseline/
├── 018-frontend-gate-compatibility-baseline/
└── 065-frontend-contract-sample-source-selfcheck-baseline/
```

### 推荐的后续 child track 文件面

```text
specs/
├── 067-frontend-p1-ui-kernel-semantic-expansion-baseline/
├── 068-frontend-p1-page-recipe-expansion-baseline/
├── 069-frontend-p1-governance-diagnostics-drift-baseline/
├── 070-frontend-p1-recheck-remediation-feedback-baseline/
└── 071-frontend-p1-visual-a11y-foundation-baseline/
```

上面的编号仅作为 rollout 占位建议，不构成当前批次必须立即 scaffold 的承诺；真实编号以后续创建时的 `project-state` 为准。

## 开始执行前必须锁定的阻断决策

- P1 只承接体验稳定层，不允许引入 P2 的 `modern provider / multi-theme / multi-style`
- child track DAG 必须先冻结 kernel / recipe truth，再扩 diagnostics / recheck / visual-a11y
- `066` 当前只做 docs-only freeze，不得顺手写 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`
- `066` 不得生成 `development-summary.md`，也不得宣称 close-ready
- child work item 创建前，不得假定固定编号已经保留；真实编号以后续 scaffold 当时的 `project-state` 为准

未锁定上述决策前，不得进入 child scaffold 或 root truth sync。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| P1 母级 planning baseline | 冻结 P1 scope、non-goals、child DAG 与 rollout policy | 不得直接写 `src/` / `tests/` 实现 |
| Kernel expansion child | 扩展 `Ui*` 语义组件集与页面状态语义 | 不得跳过 `015` 直接改 recipe/gate truth |
| Recipe expansion child | 扩展 page recipe 标准本体与声明约束 | 不得绕开 expanded kernel 自行定义新标准本体 |
| Diagnostics / drift child | 扩展 whitelist / token / 状态覆盖与 drift 反馈面 | 不得抢跑 visual/a11y 平台化或改写 program root truth |
| Recheck / remediation child | 扩 bounded feedback、recheck 策略与作者体验闭环 | 不得在 diagnostics truth 未冻结前单独扩张 |
| Visual / a11y child | 承接基础 visual / a11y 检查能力 | 不得膨胀为完整 visual regression 或完整 a11y 平台 |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 P1 阶段边界、child track 与 rollout policy 冻结成独立 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`.ai-sdlc/project/config/project-state.yaml`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints` + `git diff --check`。  
**回退方式**：仅回退 `specs/066/...` 与 `project-state.yaml`。

### Phase 1：P1 scope / non-goals freeze

**目标**：把 P1 与 MVP/P2 的边界正式写死。  
**产物**：`spec.md` 中的 scope、non-goals、FR 与 success criteria。  
**验证方式**：formal docs review。  
**回退方式**：不触发任何 runtime 变更。

### Phase 2：Child track topology freeze

**目标**：冻结五条推荐 child tracks、依赖 DAG 与有限并行窗口。  
**产物**：`spec.md` 的 child track 表、`plan.md` 的 DAG 与 owner boundary。  
**验证方式**：文档对账。  
**回退方式**：不 scaffold 实际 child work item。

### Phase 3：Rollout policy and root sync policy freeze

**目标**：冻结 branch rollout、program sync 时机与 root truth honesty 边界。  
**产物**：`plan.md`、`tasks.md`。  
**验证方式**：formal docs review。  
**回退方式**：不改 root `program-manifest.yaml` 或 rollout plan。

### Phase 4：Fresh verification and execution handoff

**目标**：通过只读门禁验证 `066` 的 planning truth，并把本批归档为 docs-only formal freeze。  
**产物**：`task-execution-log.md`。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：仅更新文档归档，不引入新实现。

## 工作流计划

### 工作流 A：P1 stage boundary freeze

**范围**：P1 的目标、non-goals、与 MVP/P2 的边界。  
**影响范围**：后续所有 frontend P1 child work item。  
**验证方式**：`spec.md` review。  
**回退方式**：不影响已冻结 MVP truths。

### 工作流 B：Child track DAG freeze

**范围**：五条 child tracks 的命名、职责、依赖顺序与有限并行窗口。  
**影响范围**：后续 child formalize 的排序与 branch 设计。  
**验证方式**：`spec.md` / `plan.md` 对账。  
**回退方式**：不创建实际 child scaffold。

### 工作流 C：Branch rollout and program sync honesty

**范围**：一工单一分支、root sync 时机、不得提前 close-ready。  
**影响范围**：root `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md` 的后续更新纪律。  
**验证方式**：`tasks.md` review。  
**回退方式**：保持 root truth 不变。

### 工作流 D：Docs-only validation and handoff

**范围**：`verify constraints`、`git diff --check`、execution log append-only 归档。  
**影响范围**：`066` 当前 formal baseline 的可审计性。  
**验证方式**：命令结果 + execution log。  
**回退方式**：仅回退 docs 改动。

## 推荐 DAG 与并行窗口

```text
Track A: Kernel Expansion
  -> Track B: Page Recipe Expansion
    -> Track C: Governance Diagnostics / Drift
      -> Track D: Recheck / Remediation Feedback
      -> Track E: Visual / A11y Foundation
```

规则说明：

- Track A 必须先行，因为 P1 recipe、diagnostics、visual/a11y 都不能绕开 expanded kernel truth
- Track B 依赖 Track A，先冻结新增 recipe 标准本体
- Track C 依赖 Track A + B，并继续消费 `017/018/065` 已有基线
- Track D 与 Track E 都依赖 Track C；两者是当前设计下唯一建议并行的窗口
- 在 Track C 之前，不建议并行创建多个 child implementation branch

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| P1 scope / non-goals 冻结 | formal docs review | 上游 `009` / design 总览对账 |
| child track DAG 冻结 | `spec.md` / `plan.md` 对账 | 人工审阅 |
| rollout honesty | `tasks.md` review | root truth 未改动核对 |
| docs-only 状态诚实性 | `task-execution-log.md` review | `git status --short` |
| planning truth 可读性 | `uv run ai-sdlc verify constraints` | `git diff --check` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 推荐 child track 的最终编号是否严格使用 `067-071` | 开放，但不阻塞 | 不阻塞 Phase 0；以后续 scaffold 时的 `project-state` 为准 |
| 是否需要在 child 全部 formalize 后再单开一个 root rollout sync work item | 待后续确认 | 不阻塞 `066` 当前 freeze |

## 实施顺序建议

1. 先冻结 `066` formal docs，确保 P1 scope、non-goals、DAG 与 rollout policy 脱离对话记忆
2. 再按 `Kernel -> Recipe -> Diagnostics` 的顺序 formalize downstream child work item
3. 在 diagnostics truth 冻结后，再并行推进 `Recheck / Remediation Feedback` 与 `Visual / A11y Foundation`
4. 只有在 child baseline 已 formalize 且需要 program-level sync 时，再更新 root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md`
