# 功能规格：Frontend P1 Child Close Check Backfill Baseline

**功能编号**：`111-frontend-p1-child-close-check-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md`](../110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md)

> 口径：`111` 不是新的 P1 child runtime / gate / provider 工单，而是对 `068-071` 的 latest-batch execution log 做 close-check 口径回填。它只补当前门禁要求的 `统一验证命令 / 代码审查 / 任务/计划同步状态 / git close-out markers / verification profile` 字段，使这些历史 P1 child baseline 能按现行 close-out 规则诚实收口；不改写既有 spec 语义，不追加新的实现功能。

## 问题定义

`110` 完成后，frontend readiness blocker 已全部清空，但 `068-071` 的 latest batch 仍沿用更早的 execution log 模板，导致 `uv run ai-sdlc workitem close-check` 对这些 work item 输出一致 blocker：

- 缺少 `统一验证命令`
- 缺少 `代码审查`
- 缺少 `任务/计划同步状态`
- 缺少 latest batch 的 `git close-out markers`
- `068-070` 还缺少 latest batch review evidence

这些缺口是 close-out 文档 schema 演进造成的历史债，不是新的实现断层。`111` 的目标是通过 append-only 的 latest-batch backfill，让 `068-071` 的最新归档段落切到当前 close-check 口径，同时保持各自的 P1 child 边界与已完成结论不变。

## 范围

- **覆盖**：
  - 创建 `111` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `111`
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `112`
  - 为 `068-071` 各追加一个 latest-batch close-check backfill 归档段落
  - 复跑 `068-071` 与 `111` 的 `workitem close-check`
- **不覆盖**：
  - 修改 `068-071` 的 spec 语义、任务边界、验收标准或 runtime 代码
  - 新增 diagnostics / recheck / visual-a11y / provider-runtime 行为
  - 回写或篡改旧 batch 的历史叙述
  - 变更 `frontend_evidence_class`、program gating 逻辑或 observation artifact

## 已锁定决策

- `111` 采用 append-only 方式回填 latest batch，不重写旧 batch 文本
- `111` 只修改 `068-071` 的 `task-execution-log.md`，不改 `spec.md / plan.md / tasks.md`
- 所有新增归档段落统一使用当前 close-check 口径的 mandatory fields
- `111` 不改变 `068-071` 当前 formal/accepted 状态，只修 close-out honesty 与 schema drift

## 用户故事与验收

### US-111-1 — Framework Maintainer 需要 P1 child baseline 通过现行 close-check

作为 **framework maintainer**，我希望 `068-071` 的 latest batch execution log 补齐现行 close-check 需要的 mandatory fields，这样这些历史 P1 child baseline 在不重写旧实现的前提下，也能按当前门禁口径被诚实验证。

**验收**：

1. Given `068-071` 各自追加了 latest-batch close-check backfill 段落，When 运行 `uv run ai-sdlc workitem close-check --wi specs/<068-071...>`，Then `execution_log_fields / review_gate / verification_profile / git_closure` 不再因缺字段而阻塞
2. Given `111` 完成后，When 检查 `068-071` 的 diff，Then 变更只出现在 `task-execution-log.md` 的末尾追加段落，不改既有 runtime 或 spec truth

### US-111-2 — Operator 需要 close-out 回填不伪造新的实现结论

作为 **operator**，我希望 `111` 只补 schema-required close-out 字段，而不借机把 `068-071` 改写成新的实现批次或新的阶段结论，这样 close-check 绿灯只来自文档诚实修复，而不是历史重述。

**验收**：

1. Given `111` 只做 latest-batch backfill，When 检查新增归档段落，Then 它们只说明 close-check schema 回填与文档/提交状态对齐，不宣称新的行为实现
2. Given 复跑 `verify constraints / program validate / workitem close-check`，When 检查结果，Then 不会引入新的 blocker 或 drift

## 边界情况

- 若旧日志中存在历史叙述里的 `已完成 git 提交：否` 引用，只允许保留为过去时说明，不能作为 latest batch 当前状态字段
- 若目标 work item 已有 review evidence，只补缺失的 latest-batch mandatory fields，不重复制造新的实现结论
- 若 latest batch 仅为 docs-only honesty backfill，验证命令与结果必须据实写为 docs-only close-out，不伪造运行时代码测试

## 功能需求

| ID | 需求 |
|----|------|
| FR-111-001 | `111` 必须为 `068-071` 各追加一个 latest-batch close-check backfill 段落 |
| FR-111-002 | 新增段落必须包含 `统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作` |
| FR-111-003 | 新增段落不得宣称新的 runtime / test 实现，只能描述 close-check schema 回填 |
| FR-111-004 | `111` 必须注册到 `program-manifest.yaml`，并推进 `next_work_item_seq` 到 `112` |
| FR-111-005 | `111` 必须用 fresh close-check 证明 `068-071` 与 `111` 自身的 done gate 能在 clean tree 下通过 |

## 成功标准

- **SC-111-001**：`uv run ai-sdlc workitem close-check --wi specs/068-frontend-p1-page-recipe-expansion-baseline` 通过
- **SC-111-002**：`uv run ai-sdlc workitem close-check --wi specs/069-frontend-p1-governance-diagnostics-drift-baseline` 通过
- **SC-111-003**：`uv run ai-sdlc workitem close-check --wi specs/070-frontend-p1-recheck-remediation-feedback-baseline` 通过
- **SC-111-004**：`uv run ai-sdlc workitem close-check --wi specs/071-frontend-p1-visual-a11y-foundation-baseline` 通过
- **SC-111-005**：`uv run ai-sdlc workitem close-check --wi specs/111-frontend-p1-child-close-check-backfill-baseline` 通过

---
related_doc:
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
