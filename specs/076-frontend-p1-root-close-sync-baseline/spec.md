# 功能规格：Frontend P1 Root Close Sync Baseline

**功能编号**：`076-frontend-p1-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md)、[`../075-frontend-p2-root-close-sync-baseline/spec.md`](../075-frontend-p2-root-close-sync-baseline/spec.md)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：本 work item 是 `067-frontend-p1-ui-kernel-semantic-expansion-baseline` 补齐 `development-summary.md` 之后的 root close sync carrier。它只负责把根级 rollout 文案从“P1 planning-only / `067` 未 close”更新为与当前 `program status` 一致的口径，并同步 `068` 已从 `067` 阻塞中释放这一事实；不再修改 `program-manifest.yaml`，不改写 `067/068` formal docs，也不把 `076` 自己写入 root DAG。

## 问题定义

当前 root machine truth 已经发生两点变化：

- `067` 已因 `development-summary.md` 补齐而进入 `close`
- `068` 的 `Blocked By` 已从 `067` 清空，当前成为 P1 链上新的首个未 close 项

但根级 rollout plan 仍保留旧口径：

- P1 支线仍被整体描述为 planning-only / 未 close
- `067` 仍被写成 docs-only child baseline / 未 close
- `068` 仍缺少“已解锁”的人读说明

如果不单独做一次 root close sync，就会留下 root 文档与 machine truth 失配的问题，并让后续 reviewer 继续低估 P1 支线的真实推进位置。

## 范围

- **覆盖**：
  - 创建 `076` canonical docs 与 execution log
  - 更新根级 `frontend-program-branch-rollout-plan.md` 中 P1 支线的总体口径
  - 更新 `067` 在 rollout table 中的状态为与当前 `program status` 一致的 `close`
  - 更新 `068` 在 rollout table / 备注中的状态说明，明确其已解锁但仍未 close
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `75` 推进到 `76`
- **不覆盖**：
  - 修改 `program-manifest.yaml`
  - 回写 `067` 或 `068` 的 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`
  - 进入 `src/` / `tests/` 或任何 runtime / implementation 行为
  - 把 `076` 自己写入 root rollout table 或 root manifest

## 已锁定决策

- `067` 的 close artifact 已存在，本轮只同步 root 人读 truth
- `068` 当前仍未 close，本轮只把“已解锁”同步到 rollout wording，不伪造成 close-ready
- 本轮不再修改 `program-manifest.yaml`
- `076` 仍是 carrier-only docs item，不进入 root DAG

## 用户故事与验收

### US-076-1 — Reviewer 需要根级文档诚实反映 `067 -> 068` 的推进位置

作为 **reviewer**，我希望 rollout plan 中 `067` 和 `068` 的状态描述与当前 `program status` 一致，这样阅读 root 文档时不会继续看到旧的 planning-only 口径。

**验收**：

1. Given 我查看 `frontend-program-branch-rollout-plan.md`，When 我定位 P1 支线，Then 可以读到 `067` 已是 `close`，`068` 已解锁但仍未 close
2. Given 我运行 `uv run ai-sdlc program status`，When 我对比 `067/068`，Then 不会与 rollout plan 冲突

### US-076-2 — Operator 需要本轮仍保持 carrier-only 边界

作为 **operator**，我希望这轮仍只同步 rollout wording 与项目编号，而不是再次进入 manifest、spec 实现或测试。

**验收**：

1. Given 我查看 `076` formal docs，When 我检查文件面，Then 可以确认只涉及 rollout plan 与 `project-state.yaml`
2. Given 我检查本批 diff，When 我查看 root machine truth 文件，Then 不会看到 `program-manifest.yaml` 被修改

## 功能需求

| ID | 需求 |
|----|------|
| FR-076-001 | `076` 必须更新根级 `frontend-program-branch-rollout-plan.md`，把 `067` 从“docs-only child baseline，未 close”改成与当前 `program status` 一致的 close wording |
| FR-076-002 | `076` 必须在 rollout wording 中明确 `068` 已从 `067` 阻塞中释放，但仍未 close |
| FR-076-003 | `076` 必须更新 P1 主线分段与备注，消除“`066 ~ 071` 全部 planning-only / 缺少 `development-summary.md`”的过期表述 |
| FR-076-004 | `076` 不得修改 `program-manifest.yaml` |
| FR-076-005 | `076` 不得回写 `067/068` formal docs 或任何 `src/` / `tests/` |
| FR-076-006 | `076` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `75` 推进到 `76` |
| FR-076-007 | `076` 不得把自己写入根级 rollout table 或 root manifest |
| FR-076-008 | `076` 的验证只允许使用 docs-only / read-only 门禁 |

## 成功标准

- **SC-076-001**：root rollout plan 不再把 `067` 写成未 close
- **SC-076-002**：root rollout plan 能诚实表达 `068` 已解锁但仍未 close
- **SC-076-003**：P1 主线分段与备注不再使用“`066 ~ 071` 全部 planning-only / 缺少 `development-summary.md`”的过期口径
- **SC-076-004**：本轮 diff 不修改 `program-manifest.yaml`、`src/`、`tests/` 或 `067/068` formal docs
- **SC-076-005**：`project-state.yaml` 已前进到 `76`
---
related_doc:
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/development-summary.md"
  - "specs/075-frontend-p2-root-close-sync-baseline/spec.md"
  - "frontend-program-branch-rollout-plan.md"
---
