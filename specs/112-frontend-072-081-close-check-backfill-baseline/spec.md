# 功能规格：Frontend 072-081 Close Check Backfill Baseline

**功能编号**：`112-frontend-072-081-close-check-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../072-frontend-p1-root-rollout-sync-baseline/spec.md`](../072-frontend-p1-root-rollout-sync-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../074-frontend-p2-root-rollout-sync-baseline/spec.md`](../074-frontend-p2-root-rollout-sync-baseline/spec.md)、[`../075-frontend-p2-root-close-sync-baseline/spec.md`](../075-frontend-p2-root-close-sync-baseline/spec.md)、[`../076-frontend-p1-root-close-sync-baseline/spec.md`](../076-frontend-p1-root-close-sync-baseline/spec.md)、[`../077-frontend-contract-observation-backfill-playbook-baseline/spec.md`](../077-frontend-contract-observation-backfill-playbook-baseline/spec.md)、[`../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`](../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md)、[`../079-frontend-framework-only-closure-policy-baseline/spec.md`](../079-frontend-framework-only-closure-policy-baseline/spec.md)、[`../080-frontend-framework-only-root-policy-sync-baseline/spec.md`](../080-frontend-framework-only-root-policy-sync-baseline/spec.md)、[`../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`](../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md)、[`../111-frontend-p1-child-close-check-backfill-baseline/spec.md`](../111-frontend-p1-child-close-check-backfill-baseline/spec.md)

> 口径：`112` 不是新的 root sync / provider style / framework policy 实现工单，而是对 `072-081` 的 latest-batch execution log 做第二波 close-check 口径回填。它只补当前门禁要求的 `统一验证命令 / 代码审查 / 任务/计划同步状态 / git close-out markers / verification profile` 字段，使这些历史 frontend formal baseline 能按现行 close-out 规则诚实收口；不改写既有 spec 语义，不追加新的实现功能。

## 问题定义

`111` 收口 `068-071` 之后，下一批 still-blocked work item 集中落在 `072-081`。其中：

- `072`、`074-081` 的 latest batch 仍沿用较早的 execution log 模板，缺少 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`verification profile` 与 `git close-out markers`
- `073` 的 latest batch 已有 review / task-plan sync，但仍缺 `verification profile` 与 `git close-out markers`

这些缺口来自 close-out 文档 schema 演进，而不是 root sync、policy freeze、provider style solution 或 observation playbook 本身未完成。`112` 的目标是通过 append-only 的 latest-batch backfill，让 `072-081` 的最新归档段落切到当前 close-check 口径，同时保持各自 baseline 的结论、边界与 runtime truth 不变。

## 范围

- **覆盖**：
  - 创建 `112` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `112`
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `113`
  - 为 `072-081` 各追加一个 latest-batch close-check backfill 归档段落
  - 复跑 `072-081` 与 `112` 的 `workitem close-check`
- **不覆盖**：
  - 修改 `072-081` 的 spec 语义、任务边界、验收标准或 runtime 代码
  - 变更 root machine truth、provider solution contract、framework-only policy contract 或 observation artifact 语义
  - 回写或篡改旧 batch 的历史叙述
  - 变更 `frontend_evidence_class`、program gating 逻辑或 diagnostics / verify 行为

## 已锁定决策

- `112` 采用 append-only 方式回填 latest batch，不重写旧 batch 文本
- `112` 只修改 `072-081` 的 `task-execution-log.md`，不改这些 work item 的 `spec.md / plan.md / tasks.md`
- 所有新增归档段落统一使用当前 close-check 口径的 mandatory fields
- `112` 不改变 `072-081` 当前 formal/accepted/close 状态，只修 close-out honesty 与 schema drift

## 用户故事与验收

### US-112-1 — Framework Maintainer 需要历史 frontend baseline 通过现行 close-check

作为 **framework maintainer**，我希望 `072-081` 的 latest batch execution log 补齐现行 close-check 所需的字段，这样这些历史 frontend formal baseline 在不重写旧实现的前提下，也能按当前门禁口径被诚实验证。

**验收**：

1. Given `072-081` 各自追加了 latest-batch close-check backfill 段落，When 运行 `uv run ai-sdlc workitem close-check --wi specs/<072-081...>`，Then `execution_log_fields / review_gate / verification_profile / git_closure` 不再因缺字段而阻塞
2. Given `112` 完成后，When 检查 `072-081` 的 diff，Then 变更只出现在 `task-execution-log.md` 的末尾追加段落，不改既有 runtime 或 spec truth

### US-112-2 — Operator 需要 close-out 回填不伪造新的实现结论

作为 **operator**，我希望 `112` 只补 schema-required close-out 字段，而不借机把 `072-081` 改写成新的实现批次或新的阶段结论，这样 close-check 绿灯只来自文档诚实修复，而不是历史重述。

**验收**：

1. Given `112` 只做 latest-batch backfill，When 检查新增归档段落，Then 它们只说明 close-check schema 回填与文档/提交状态对齐，不宣称新的行为实现
2. Given 复跑 `verify constraints / program validate / workitem close-check`，When 检查结果，Then 不会引入新的 blocker 或 drift

## 边界情况

- 若旧日志里已有 `已完成 git 提交：否` 之类状态字段，只允许保留为过去时说明，不能作为 latest batch 当前状态字段
- 若目标 work item 已有 review evidence，只补缺失的 latest-batch mandatory fields，不重复制造新的实现结论
- 若 latest batch 仅为 docs-only honesty backfill，验证命令与结果必须据实写为 docs-only close-out，不伪造运行时代码测试

## 功能需求

| ID | 需求 |
|----|------|
| FR-112-001 | `112` 必须为 `072-081` 各追加一个 latest-batch close-check backfill 段落 |
| FR-112-002 | 新增段落必须补齐 latest batch 当前 close-check 需要的 mandatory fields，包括 `验证画像`、`统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作` |
| FR-112-003 | 新增段落不得宣称新的 runtime / test 实现，只能描述 close-check schema 回填 |
| FR-112-004 | `112` 必须注册到 `program-manifest.yaml`，并推进 `next_work_item_seq` 到 `113` |
| FR-112-005 | `112` 必须用 fresh close-check 证明 `072-081` 与 `112` 自身的 done gate 能在 clean tree 下通过 |

## 成功标准

- **SC-112-001**：`uv run ai-sdlc workitem close-check --wi specs/072-frontend-p1-root-rollout-sync-baseline` 通过
- **SC-112-002**：`uv run ai-sdlc workitem close-check --wi specs/073-frontend-p2-provider-style-solution-baseline` 通过
- **SC-112-003**：`uv run ai-sdlc workitem close-check --wi specs/074-frontend-p2-root-rollout-sync-baseline` 通过
- **SC-112-004**：`uv run ai-sdlc workitem close-check --wi specs/075-frontend-p2-root-close-sync-baseline` 通过
- **SC-112-005**：`uv run ai-sdlc workitem close-check --wi specs/076-frontend-p1-root-close-sync-baseline` 通过
- **SC-112-006**：`uv run ai-sdlc workitem close-check --wi specs/077-frontend-contract-observation-backfill-playbook-baseline` 通过
- **SC-112-007**：`uv run ai-sdlc workitem close-check --wi specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline` 通过
- **SC-112-008**：`uv run ai-sdlc workitem close-check --wi specs/079-frontend-framework-only-closure-policy-baseline` 通过
- **SC-112-009**：`uv run ai-sdlc workitem close-check --wi specs/080-frontend-framework-only-root-policy-sync-baseline` 通过
- **SC-112-010**：`uv run ai-sdlc workitem close-check --wi specs/081-frontend-framework-only-prospective-closure-contract-baseline` 通过
- **SC-112-011**：`uv run ai-sdlc workitem close-check --wi specs/112-frontend-072-081-close-check-backfill-baseline` 通过

---
related_doc:
  - "specs/072-frontend-p1-root-rollout-sync-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/074-frontend-p2-root-rollout-sync-baseline/spec.md"
  - "specs/075-frontend-p2-root-close-sync-baseline/spec.md"
  - "specs/076-frontend-p1-root-close-sync-baseline/spec.md"
  - "specs/077-frontend-contract-observation-backfill-playbook-baseline/spec.md"
  - "specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md"
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md"
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
