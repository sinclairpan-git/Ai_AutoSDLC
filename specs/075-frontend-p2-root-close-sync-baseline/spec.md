# 功能规格：Frontend P2 Root Close Sync Baseline

**功能编号**：`075-frontend-p2-root-close-sync-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../073-frontend-p2-provider-style-solution-baseline/development-summary.md`](../073-frontend-p2-provider-style-solution-baseline/development-summary.md)、[`../074-frontend-p2-root-rollout-sync-baseline/spec.md`](../074-frontend-p2-root-rollout-sync-baseline/spec.md)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：本 work item 是 `073-frontend-p2-provider-style-solution-baseline` 在补齐 `development-summary.md` 之后的 root close sync carrier。它只负责把根级 rollout 文案从“已纳入 program、仍待 summary”更新为与当前 `program status` 一致的 `close` / close-ready 口径，同时推进下一个可用编号；不改写 `073` formal docs，不再回写 `program-manifest.yaml`，也不把 `075` 自己写入 root DAG。

## 问题定义

`074` 已经把 `073` 同步进根级 `program-manifest.yaml` 与 rollout plan，但当时保留的是“已纳入 program、root close 仍待 `development-summary.md`”的诚实口径。随后 `073` 已补齐 `development-summary.md`，根级 `program status` 也已经把它提升为 `close`。当前不一致只剩一层：

- root machine truth 已经把 `073` 视为 `close`
- 根级人读 rollout plan 仍停留在 “summary 缺失 / 未 close” 的旧状态

如果不再单独做一次 close sync，就会留下两种失真：

- 人读 rollout 文档继续低估 `073` 的当前 program 阶段
- 后续 reviewer 无法区分 `074` 的“纳入 root truth”和 `075` 的“同步 close 文案”这两个不同 carrier 批次

因此，`075` 只处理 root close wording 的补齐，不再重造 DAG、不再修改 manifest，也不伪装成新的 frontend implementation item。

## 范围

- **覆盖**：
  - 创建 `075` canonical docs 与 execution log
  - 更新根级 `frontend-program-branch-rollout-plan.md` 中 `073` 的状态口径
  - 明确 `073` 已具备 `development-summary.md`，`program status` 当前为 `close`
  - 明确 `075` 是 close sync carrier，不进入 root DAG
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `74` 推进到 `75`
- **不覆盖**：
  - 改写 `073` 的 `spec.md / plan.md / tasks.md / task-execution-log.md / development-summary.md`
  - 再次改写根级 `program-manifest.yaml`
  - 进入 `src/` / `tests/` 或任何 runtime / implementation 行为
  - 把 `075` 自己写入 root manifest / rollout table

## 已锁定决策

- `073` 的 root DAG 位置与直接依赖已经由 `074` 固定，本轮不再修改 `program-manifest.yaml`
- `075` 只同步 `073` 的 close wording，不改写实现 truth
- rollout plan 对 `073` 的表述必须与当前 `program status` 对齐，即可被人读为 `close` / close-ready，而不是仍待 `development-summary.md`
- `075` 自身仍是 carrier-only docs item，不进入 root DAG，不伪造成新的 frontend branch

## 用户故事与验收

### US-075-1 — Reviewer 需要 root 人读文档与 machine truth 一致

作为 **reviewer**，我希望 rollout plan 中 `073` 的状态口径与当前 `program status` 一致，这样我读根级文档时不会看到过期的“summary 缺失”描述。

**验收**：

1. Given 我查看 `frontend-program-branch-rollout-plan.md`，When 我定位 `073`，Then 能读到它已经进入 `close` / close-ready 口径
2. Given 我运行 `uv run ai-sdlc program status`，When 我对比 `073` 的当前阶段，Then 不会与 rollout plan 冲突

### US-075-2 — Operator 需要本轮 close sync 不再碰 manifest

作为 **operator**，我希望这轮收口只修改 rollout wording 和项目编号，而不再重复改写 root DAG。

**验收**：

1. Given 我查看 `075` formal docs，When 我检查范围与文件面，Then 能确认 `program-manifest.yaml` 不在本轮修改范围
2. Given 我检查本批 diff，When 我查看 root 机器真值文件，Then 只会看到 rollout plan 与 `project-state.yaml` 被改动

## 功能需求

| ID | 需求 |
|----|------|
| FR-075-001 | `075` 必须更新根级 `frontend-program-branch-rollout-plan.md`，把 `073` 从“summary 缺失 / 未 close”改成与当前 `program status` 一致的 close wording |
| FR-075-002 | `075` 必须在 rollout plan 备注中明确：`073` 的 `development-summary.md` 已补齐，当前 root machine truth 已视为 `close` |
| FR-075-003 | `075` 必须明确区分 `074` 的 root inclusion sync 与 `075` 的 root close sync |
| FR-075-004 | `075` 不得再次修改 `program-manifest.yaml` |
| FR-075-005 | `075` 不得回写 `073` formal docs 或任何 `src/` / `tests/` |
| FR-075-006 | `075` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `74` 推进到 `75` |
| FR-075-007 | `075` 不得把自己写入根级 rollout table 或 root manifest |
| FR-075-008 | `075` 的验证只允许使用 docs-only / read-only 门禁 |

## 关键实体

- **Root Close Synced 073**：已经被根级 `program status` 识别为 `close` 的 `073`
- **Rollout Close Wording**：root rollout plan 中反映 `073` 当前 close 阶段的人读表述
- **Close Sync Carrier Spec**：`075` 自身的角色，只负责 root close 文案同步

## 成功标准

- **SC-075-001**：root rollout plan 不再把 `073` 写成“仍待 `development-summary.md`”
- **SC-075-002**：root rollout plan 能诚实表达 `073` 已具备 `development-summary.md`，当前 `program status` 为 `close`
- **SC-075-003**：本轮 diff 不修改 `program-manifest.yaml`、`src/`、`tests/` 或 `073` formal docs
- **SC-075-004**：`project-state.yaml` 已前进到 `75`
- **SC-075-005**：`075` formal docs 能独立解释本轮只做 close sync、不再做 DAG sync 的原因
---
related_doc:
  - "specs/073-frontend-p2-provider-style-solution-baseline/development-summary.md"
  - "specs/074-frontend-p2-root-rollout-sync-baseline/spec.md"
  - "frontend-program-branch-rollout-plan.md"
---
