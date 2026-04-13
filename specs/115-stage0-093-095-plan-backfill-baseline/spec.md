# 功能规格：Stage0 093-095 Plan Backfill Baseline

**功能编号**：`115-stage0-093-095-plan-backfill-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../114-stage0-093-095-formal-docs-backfill-baseline/spec.md`](../114-stage0-093-095-formal-docs-backfill-baseline/spec.md)

> 口径：`115` 不是新的 Stage 0 / frontend runtime feature，也不是对 `093-095` baseline 语义的改写。它只是把 `093`、`094`、`095` 当前缺失的 `plan.md` 补齐，让这三条已冻结 baseline 拥有完整的 formal docs package。

## 问题定义

`114` 已经把 `093-095` 的 `tasks.md` 与 `task-execution-log.md` 补齐，并让三项的 close-check 全部通过。当前仓库中这组三项剩余的共同文档缺口只剩：

- `specs/093-stage0-installed-runtime-update-advisor-baseline/plan.md`
- `specs/094-stage0-init-dual-path-project-onboarding-baseline/plan.md`
- `specs/095-frontend-mainline-product-delivery-baseline/plan.md`

这不是 close-check blocker，也不是 runtime blocker，而是 formal docs package 还未完整。`115` 的目标是用最小 docs-only carrier 把这组三项的 plan 文档补齐，并保持现有真值不变。

## 范围

- **覆盖**：
  - 创建 `115` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `115`
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `116`
  - 为 `093`、`094`、`095` 各补齐 `plan.md`
  - 回放 `verify constraints`、`program validate`、`plan-check`、`close-check`
- **不覆盖**：
  - 修改 `093-095` 的 `spec.md / tasks.md / task-execution-log.md` 语义
  - 修改 `src/` / `tests/`
  - 新增 `related_plan`
  - 扩大到 `096+` downstream implementable slice

## 已锁定决策

- `115` 只补 `093-095` 的本地 `plan.md`，不改写已有 spec / tasks / execution log truth
- `115` 继续保持 docs-only close-out，不引入新的实现任务
- `093-095` 新增的 `plan.md` 只描述 contract freeze、scope、verification 与 rollback 原则，不宣称 runtime 已实现
- `115` 只修改 `project-state`、`program-manifest.yaml`、`093-095` 的 `plan.md` 与 `115` 自身 carrier 文件

## 用户故事与验收

### US-115-1 — Framework Maintainer 需要 093-095 拥有完整 formal docs package

作为 **framework maintainer**，我希望 `093-095` 都补齐 `plan.md`，这样这组三项不仅能通过 close-check，也能在仓库层面保持完整的 spec / plan / tasks / execution-log 结构。

**验收**：

1. Given `093-095` 都补齐了 `plan.md`，When 检查目录结构，Then 三者都拥有 `spec.md + plan.md + tasks.md + task-execution-log.md`
2. Given `115` 完成后，When 检查 diff，Then 变更只出现在 docs/state/manifest，不改动任何 runtime 代码或规格正文

### US-115-2 — Operator 需要 plan backfill 不伪造新的实现结论

作为 **operator**，我希望 `115` 只补 plan 文档，而不把 `093-095` 重写成新的实现批次或新的 runtime 结论，这样 formal docs 的完整性提升不会污染既有 contract truth。

**验收**：

1. Given `115` 只做 plan backfill，When 检查新增 `plan.md`，Then 它们只描述 contract freeze、scope、verification 与 rollback，不宣称新的 CLI / onboarding / mainline delivery 实现
2. Given 复跑 `verify constraints / program validate / close-check`，When 检查结果，Then 不会引入新的 blocker 或 drift

## 边界情况

- 若后续需要外部 `related_plan`，应由独立工单处理；`115` 不追加该声明
- `093-095` 当前 close-check 已绿，`115` 不以“修 blocker”为理由改写既有 execution truth
- 若 `plan-check` 对本地计划文件无额外 blocker，`115` 也不强造外部计划链路

## 功能需求

| ID | 需求 |
|----|------|
| FR-115-001 | `115` 必须为 `093`、`094`、`095` 各补齐 `plan.md` |
| FR-115-002 | `115` 新增计划文档不得宣称新的 runtime / test 实现，只能描述 contract freeze 与验证策略 |
| FR-115-003 | `115` 必须注册到 `program-manifest.yaml`，并推进 `next_work_item_seq` 到 `116` |
| FR-115-004 | `115` 必须用 fresh verification 证明 plan backfill 未引入新的约束或 close-check 漂移 |

## 成功标准

- **SC-115-001**：`specs/093-stage0-installed-runtime-update-advisor-baseline/plan.md` 存在且与 `093/spec.md` 边界一致
- **SC-115-002**：`specs/094-stage0-init-dual-path-project-onboarding-baseline/plan.md` 存在且与 `094/spec.md` 边界一致
- **SC-115-003**：`specs/095-frontend-mainline-product-delivery-baseline/plan.md` 存在且与 `095/spec.md` 边界一致
- **SC-115-004**：`uv run ai-sdlc verify constraints` 通过
- **SC-115-005**：`uv run ai-sdlc program validate` 通过
- **SC-115-006**：`uv run ai-sdlc workitem close-check --wi specs/093-stage0-installed-runtime-update-advisor-baseline`、`094`、`095` 与 `115` 在 post-commit 复核中通过

---
related_doc:
  - "specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/114-stage0-093-095-formal-docs-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
