# 功能规格：Frontend P1 Root Close Sync Baseline

**功能编号**：`076-frontend-p1-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md`](../068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/task-execution-log.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/task-execution-log.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md`](../071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：本 work item 最初用于把 `067 close / 068 unlocked` 同步到根级 rollout wording。随着 `068` ~ `071` 的 carrier closeout 已分别完成并归档，本轮继续承担 honesty sync：明确“carrier 已 formal closeout”与“root program status 仍未 close”是两层不同 truth。`076` 仍只更新根级 rollout 文案，不修改 `program-manifest.yaml`，不回写 `067` ~ `071` formal docs，也不把 `076` 自己写入 root DAG。

## 问题定义

当前 root machine truth 已经进一步发生了两层变化：

- `067` 已因 `development-summary.md` 补齐而进入 `close`
- `068` 的 `Blocked By` 已从 `067` 清空，`068` ~ `071` 各自的 docs-only carrier closeout 也已经完成并归档

但根级 rollout plan 仍保留旧口径：

- P1 支线只同步到了“`067 close / 068 unlocked`”这一层
- `068` ~ `071` 仍被统写成“docs-only child baseline，未 close”，没有区分 carrier closeout 已归档与 root `program status` 仍未进入 `close`
- 当前对全部 frontend spec 生效的 `missing_artifact [frontend_contract_observations]` 外部输入缺口，尚未在 P1 备注中与 `068` ~ `071` 的 root 非 close 状态联动说明

如果不继续做这次 root honesty sync，就会把“carrier 已 formal closeout”和“root machine truth 仍未 close”混在一起，让后续 reviewer 既可能低估已完成的 closeout，也可能误判 root 已经收口。

## 范围

- **覆盖**：
  - 继续使用 `076` 的 canonical docs 与 execution log 归档第二轮 honesty sync
  - 更新根级 `frontend-program-branch-rollout-plan.md` 中 P1 支线的总体口径
  - 保留 `067` 在 rollout wording 中的 `close` 口径
  - 更新 `068` ~ `071` 在 rollout table / 备注中的状态说明，明确其 carrier closeout 已归档，但 root `program status` 仍未进入 `close`
  - 明确 `missing_artifact [frontend_contract_observations]` 仍是外部输入缺口，本轮不伪造成仓库内可直接消除
- **不覆盖**：
  - 修改 `program-manifest.yaml`
  - 再次推进 `.ai-sdlc/project/config/project-state.yaml` 编号
  - 回写 `067` ~ `071` 的 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`
  - 进入 `src/` / `tests/` 或任何 runtime / implementation 行为
  - 把 `076` 自己写入 root rollout table 或 root manifest

## 已锁定决策

- `067` 的 close artifact 已存在，本轮只保留其 root 人读 truth
- `068` ~ `071` 的 carrier closeout 已归档，但这不等于 root `program status` 已经 `close`
- `missing_artifact [frontend_contract_observations]` 仍是 active spec 的外部输入缺口，本轮不伪造成仓库内已补齐
- 本轮不再修改 `program-manifest.yaml`
- `076` 仍是 carrier-only docs item，不进入 root DAG

## 用户故事与验收

### US-076-1 — Reviewer 需要根级文档诚实区分 archived closeout 与 root stage

作为 **reviewer**，我希望 rollout plan 中 `067` ~ `071` 的状态描述能同时反映 archived carrier closeout 与当前 root `program status`，这样阅读 root 文档时不会把 branch closeout 误读成 root 已 close，也不会把已完成的 closeout 误读成尚未 formalize。

**验收**：

1. Given 我查看 `frontend-program-branch-rollout-plan.md`，When 我定位 P1 支线，Then 可以读到 `067` 已是 `close`，`068` ~ `071` 的 carrier closeout 已归档但 root 仍未 close
2. Given 我运行 `uv run ai-sdlc program status`，When 我对比 `068` ~ `071`，Then 不会与 rollout plan 冲突，且能看到 `missing_artifact [frontend_contract_observations]` 仍未被伪造成已解决

### US-076-2 — Operator 需要本轮仍保持 carrier-only 边界

作为 **operator**，我希望这轮仍只同步 rollout wording，而不是再次进入 manifest、formal docs、项目编号或测试实现。

**验收**：

1. Given 我查看 `076` formal docs，When 我检查文件面，Then 可以确认只涉及 `076` docs 与根级 rollout wording
2. Given 我检查本批 diff，When 我查看 root machine truth 文件，Then 不会看到 `program-manifest.yaml` 被修改

## 功能需求

| ID | 需求 |
|----|------|
| FR-076-001 | `076` 必须更新根级 `frontend-program-branch-rollout-plan.md`，保留 `067` 与当前 `program status` 一致的 `close` wording |
| FR-076-002 | `076` 必须在 rollout wording 中明确 `068` ~ `071` 的 carrier closeout 已归档，但 root `program status` 仍未进入 `close` |
| FR-076-003 | `076` 必须保留 `068 -> 069 -> (070 || 071)` 的 DAG 口径，不得把 archived closeout 写成依赖已解除或 root 已收口 |
| FR-076-004 | `076` 必须在 P1 主线分段与备注中明确 `missing_artifact [frontend_contract_observations]` 仍是 active spec 的外部输入缺口 |
| FR-076-005 | `076` 不得修改 `program-manifest.yaml` |
| FR-076-006 | `076` 不得回写 `067` ~ `071` formal docs 或任何 `src/` / `tests/` |
| FR-076-007 | `076` 不得再次推进 `.ai-sdlc/project/config/project-state.yaml` 编号 |
| FR-076-008 | `076` 不得把自己写入根级 rollout table 或 root manifest |
| FR-076-009 | `076` 的验证只允许使用 docs-only / read-only 门禁 |

## 成功标准

- **SC-076-001**：root rollout plan 继续把 `067` 保持为 `close`
- **SC-076-002**：root rollout plan 能诚实表达 `068` ~ `071` 的 carrier closeout 已归档，但 root 仍未 close
- **SC-076-003**：P1 主线分段与备注明确保留 `missing_artifact [frontend_contract_observations]` 的外部输入缺口
- **SC-076-004**：本轮 diff 不修改 `program-manifest.yaml`、`project-state.yaml`、`src/`、`tests/` 或 `067` ~ `071` formal docs
- **SC-076-005**：`068 -> 069 -> (070 || 071)` 的 root DAG 口径未被 archived closeout wording 破坏
- **SC-076-006**：`076` 仍只作为 root honesty sync carrier 存在
---
related_doc:
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/task-execution-log.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md"
  - "frontend-program-branch-rollout-plan.md"
---
