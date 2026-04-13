# 功能规格：Stage0 093-095 Formal Docs Backfill Baseline

**功能编号**：`114-stage0-093-095-formal-docs-backfill-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../113-frontend-082-092-manifest-mirror-baseline/spec.md`](../113-frontend-082-092-manifest-mirror-baseline/spec.md)

> 口径：`114` 不是新的 Stage 0 / frontend runtime feature，也不是对 `093-095` formal baseline 语义的改写。它只是把 `093`、`094`、`095` 当前缺失的 `tasks.md` 与 `task-execution-log.md` 补齐，让这三条已冻结 baseline 能按现行 close-check 口径诚实收口。

## 问题定义

在 `113` 之后，下一批 close-check blocker 收敛到了 `093-095`：

- `093`、`094`、`095` 都已经有正式 `spec.md`
- `program-manifest.yaml` 已为它们登记 canonical entry 与 `frontend_evidence_class`
- `workitem close-check` 不再报告 manifest drift、docs consistency drift 或 spec footer 问题

当前唯一 blocker 是三者都缺少：

- `tasks.md`
- `task-execution-log.md`

这属于 formal docs package 未补齐，不是 baseline contract 未冻结，也不是 runtime / CLI / onboarding / mainline delivery 行为尚未实现。`114` 的目标是把这组缺口用最小 docs-only carrier 收口。

## 范围

- **覆盖**：
  - 创建 `114` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `114`
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `115`
  - 为 `093`、`094`、`095` 各补齐 `tasks.md`
  - 为 `093`、`094`、`095` 各补齐 `task-execution-log.md`
  - 复跑 `093`、`094`、`095` 与 `114` 的 `workitem close-check`
- **不覆盖**：
  - 修改 `093-095` 的 `spec.md` 语义、任务边界、验收标准或 runtime 代码
  - 回写 `096+` 的 downstream implementable slice 或 close-out 欠账
  - 修改 adapter target / activation 配置
  - 扩大为新的 Stage 0 / frontend mainline 设计工单

## 已锁定决策

- `114` 只补 `093-095` 的缺失 formal docs 组件，不改写已有 baseline 语义
- `114` 采用 docs-only close-out 方式收口，不引入新的实现任务
- `093-095` 当前不新增 `plan.md`；继续保持 `related_plan` 未声明、由 close-check 按现行口径跳过
- `114` 只修改 `project-state`、`program-manifest.yaml`、`093-095` 的 `tasks.md / task-execution-log.md` 与 `114` 自身 carrier 文件

## 用户故事与验收

### US-114-1 — Framework Maintainer 需要 093-095 按现行 close-check 口径收口

作为 **framework maintainer**，我希望 `093-095` 都具备当前 close-check 所需的 formal docs 基本件，这样这组已冻结 baseline 不会继续因为缺失 `tasks.md` / `task-execution-log.md` 被误判为未完成。

**验收**：

1. Given `093-095` 都补齐了 `tasks.md` 与 `task-execution-log.md`，When 运行 `uv run ai-sdlc workitem close-check --wi specs/<093-095...>`，Then `tasks_completion` 与 `execution_log_fields` 不再因缺文件阻塞
2. Given `114` 完成后，When 检查 diff，Then 变更只出现在 docs/state/manifest，不改动任何 runtime 代码或规格正文

### US-114-2 — Operator 需要 formal docs backfill 不伪造新的实现结论

作为 **operator**，我希望 `114` 只补 formal docs package，而不把 `093-095` 重写成新的实现批次或新的 runtime 结论，这样 close-check 绿灯只来自文档诚实修复，而不是历史重述。

**验收**：

1. Given `114` 只做 docs-only close-out backfill，When 检查新增文件，Then 它们只说明 formal docs 组件补齐与验证结果，不宣称新的 CLI / onboarding / frontend delivery 行为实现
2. Given 复跑 `verify constraints / program validate / workitem close-check`，When 检查结果，Then 不会引入新的 blocker 或 drift

## 边界情况

- 若 `093-095` 将来需要补 `plan.md`，应由后续明确工单处理，而不是在 `114` 中顺手引入
- 若 `run --dry-run` 仍受 adapter activation 状态阻塞，`114` 不借机修改 project adapter 选择，只记录当前框架上下文事实
- 若 `096+` 在同次扫描中存在别的 blocker family，`114` 仍不得混修

## 功能需求

| ID | 需求 |
|----|------|
| FR-114-001 | `114` 必须为 `093`、`094`、`095` 各补齐 `tasks.md` |
| FR-114-002 | `114` 必须为 `093`、`094`、`095` 各补齐 `task-execution-log.md` |
| FR-114-003 | `114` 新增文档不得宣称新的 runtime / test 实现，只能描述 formal docs close-out 与验证 |
| FR-114-004 | `114` 必须注册到 `program-manifest.yaml`，并推进 `next_work_item_seq` 到 `115` |
| FR-114-005 | `114` 必须用 fresh close-check 证明 `093-095` 与 `114` 自身的 done gate 能在 clean tree 下通过 |

## 成功标准

- **SC-114-001**：`uv run ai-sdlc workitem close-check --wi specs/093-stage0-installed-runtime-update-advisor-baseline` 通过
- **SC-114-002**：`uv run ai-sdlc workitem close-check --wi specs/094-stage0-init-dual-path-project-onboarding-baseline` 通过
- **SC-114-003**：`uv run ai-sdlc workitem close-check --wi specs/095-frontend-mainline-product-delivery-baseline` 通过
- **SC-114-004**：`uv run ai-sdlc workitem close-check --wi specs/114-stage0-093-095-formal-docs-backfill-baseline` 通过

---
related_doc:
  - "specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/113-frontend-082-092-manifest-mirror-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
