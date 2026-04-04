---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Mutation Eligibility Baseline

**编号**：`054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline` | **日期**：2026-04-04 | **规格**：specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md

## 概述

本次 work item 只做 docs-only 的 truth freeze：把 `cleanup_target_eligibility` 正式定义为 `050` final proof archive project cleanup artifact 内、与 `cleanup_targets` 并列的 canonical sibling truth surface。`054` 不进入 `ProgramService`、CLI、tests，也不引入 preview plan 或真实 cleanup mutation；它的交付目标是为后续 child work item 固定唯一资格真值、边界语义和接力顺序。

## 技术背景

**语言/版本**：Markdown 文档，沿用 canonical formal spec 模板  
**主要依赖**：`050/051/052/053` final proof archive cleanup truth chain  
**存储**：`specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/`  
**测试**：`uv run ai-sdlc verify constraints`、`git diff --check -- specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline .ai-sdlc/project/config/project-state.yaml`  
**目标平台**：Ai_AutoSDLC governance docs  
**约束**：不修改 `src/`、不修改 `tests/`、不新增 side artifact、不允许 inferred eligibility、不把 `eligible` 误写成真实 cleanup 已执行  

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Single truth chain | 只把 eligibility 定义为 `050` cleanup artifact 的 sibling truth，不新增第二套 artifact |
| Boundary honesty | `eligible` 只授权未来 child work item 进入 test-first / planning truth，不越界到 real mutation |
| Minimal change surface | 仅改 `specs/054-.../` 文档，加上脚手架自动推进的 `project-state.yaml` |

## 项目结构

### 文档结构

```text
specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### 源码结构

```text
docs-only work item
no src changes
no test changes
```

## 阶段计划

### Phase 0：研究与范围选择

**目标**：确认 `054` 不能直接跳到 preview plan 或 real mutation，并把范围锁定为 eligibility truth freeze  
**产物**：范围结论、用户确认、脚手架初始化结果  
**验证方式**：对账 `051/052/053` 已冻结链路与用户确认口径  
**回退方式**：若发现 truth chain 仍有未定义输入，则停留在 docs-only formal freeze，不进入实现  

### Phase 1：Formal Docs Rewrite

**目标**：把脚手架占位文档重写为 `cleanup_target_eligibility` baseline  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：文档对账，确认状态语义、字段约束、non-goals 与未来接力顺序一致  
**回退方式**：若文档之间口径不一致，以 `spec.md` 为准重新对齐其它文档  

### Phase 2：Focused Verification

**目标**：确认 docs-only 变更满足框架约束且无格式错误  
**产物**：通过的 constraints 校验与 diff-check 结果  
**验证方式**：运行约束校验与 diff 格式检查  
**回退方式**：根据校验输出修正文档或 project state 差异，再次验证  

## 工作流计划

### 工作流 A：Eligibility Truth Freeze

**范围**：定义 `cleanup_target_eligibility` truth surface、总体状态和单 target 状态语义  
**影响范围**：仅 `specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/` 与脚手架自动更新的 `.ai-sdlc/project/config/project-state.yaml`  
**验证方式**：文档对账 + focused verification  
**回退方式**：保留 docs-only formal freeze，不向 `src/` 或 `tests/` 扩张  

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| sibling truth source 已固定 | 审阅 `spec.md` 中 eligibility 定位与字段定义 | 对账 `plan.md` / `tasks.md` 是否保持同一口径 |
| `eligible` 未越界成 mutation 放行 | 审阅 `spec.md` 成功标准与已锁定决策 | 对账 `task-execution-log.md` 是否明确 future child item 才能进入 test-first / planning truth |
| docs-only 变更满足约束 | `uv run ai-sdlc verify constraints` | `git diff --check -- specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline .ai-sdlc/project/config/project-state.yaml` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 后续 child item 应先把 eligibility truth 接入 service/CLI，还是先定义 preview plan truth | 已延期，非阻塞 | 后续新 work item |

## 实施顺序建议

1. 脚手架创建 `054` 并推进 `project-state.yaml`
2. 重写 `spec.md` 冻结 eligibility truth
3. 对齐 `plan.md`、`tasks.md`、`task-execution-log.md`
4. 运行 focused verification 并记录结果
