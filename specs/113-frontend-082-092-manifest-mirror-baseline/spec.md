# 功能规格：Frontend 082-092 Manifest Mirror Baseline

**功能编号**：`113-frontend-082-092-manifest-mirror-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`](../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md)、[`../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md`](../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md)、[`../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`](../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md)、[`../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md`](../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md)、[`../112-frontend-072-081-close-check-backfill-baseline/spec.md`](../112-frontend-072-081-close-check-backfill-baseline/spec.md)

> 口径：`113` 不是新的 evidence-class runtime feature，也不是对 `082-092` baseline 语义的改写。它只是把当前 runtime reality 已经要求的一层 manifest mirror registration 正式补到 `program-manifest.yaml`，并顺手为 `082-084` 补齐 latest-batch close-check mandatory fields，让 `082-092` 按现行门禁口径诚实收口。

## 问题定义

`112` 收口 `072-081` 后，下一批 still-blocked frontend work item 集中在 `082-092`。其中：

- `082-084` 的 latest batch 仍沿用早期 execution log 模板，缺少 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`verification profile` 与 `git close-out markers`
- `082-092` 全部已经在 `spec.md` footer 声明 `frontend_evidence_class: "framework_capability"`，但 `program-manifest.yaml` 里没有对应 `specs[] .frontend_evidence_class` mirror，导致 `workitem close-check` 继续以 `frontend_evidence_class_mirror_drift via program load (manifest_unmapped)` 阻塞

这些缺口来自 manifest registration truth 与 close-out schema 演进，而不是 `082-092` 的 docs-only contract 或 `091/092` 已验证 runtime reality 本身未完成。`113` 的目标是用 append-only 的 close-out backfill 加一次性 manifest registration，把这批 blocker 收敛到当前框架口径。

## 范围

- **覆盖**：
  - 创建 `113` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `082-092` 与 `113`
  - 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 推进到 `114`
  - 为 `082-084` 各追加一个 latest-batch close-check backfill 归档段落
  - 复跑 `082-092` 与 `113` 的 `workitem close-check`
- **不覆盖**：
  - 修改 `082-092` 的 spec 语义、任务边界、验收标准或 runtime 代码
  - 回写 `082-092` 的 `spec.md / plan.md / tasks.md`
  - 改写 `085-092` 已存在的 latest batch close-out 叙述
  - 扩大到 `093-100` 的其他 blocker 家族

## 已锁定决策

- `113` 只为 `082-092` 补 manifest mirror registration，不借机扩散到 `093-100`
- `113` 对 `082-084` 采用 append-only 的 latest-batch close-out backfill，不重写旧 batch 文本
- `113` 不改变 `082-092` 已冻结的 source-of-truth / validator ownership / diagnostics family / rollout sequencing 结论
- `program-manifest.yaml` 中新增的 `frontend_evidence_class` 仅作为 mirror，不覆盖各 spec footer metadata

## 用户故事与验收

### US-113-1 — Framework Maintainer 需要 082-092 与当前 manifest reality 对齐

作为 **framework maintainer**，我希望 `082-092` 被正式登记到 `program-manifest.yaml`，这样 `workitem close-check` 不会继续把已经声明好的 `frontend_evidence_class` 误报为 `manifest_unmapped`。

**验收**：

1. Given `082-092` 已完成 manifest registration，When 运行 `uv run ai-sdlc workitem close-check --wi specs/<082-092...>`，Then `frontend_evidence_class` 不再因 `manifest_unmapped` 阻塞
2. Given `113` 完成后，When 检查 `program-manifest.yaml`，Then `082-092` 的 `frontend_evidence_class` 只出现在各自 `specs[]` entry 上，不新增并行 alias 或顶层 map

### US-113-2 — Operator 需要 latest-batch close-out 诚实修复而不重写旧结论

作为 **operator**，我希望 `082-084` 的 latest batch 只补 schema-required close-out 字段，而不借机重写 authoring / validator / diagnostics baseline 本体，这样 close-check 绿灯来自文档诚实修复，而不是历史重述。

**验收**：

1. Given `082-084` 各自追加了 latest-batch close-check backfill 段落，When 检查 diff，Then 变更只出现在 `task-execution-log.md` 末尾追加段落
2. Given `113` 复跑 `verify constraints / program validate / workitem close-check`，When 检查结果，Then 不会引入新的 blocker 或 schema drift

## 边界情况

- 若某个 work item 的 old batch 仍写着更早的 git 状态，只允许保留为历史叙述，不能替代 latest batch 当前 close-out markers
- 若 `082-092` 的 spec footer 与 manifest mirror future 发生冲突，仍以 spec footer metadata 为 canonical source-of-truth
- 若 `093-100` 在同次扫描中出现别的 blocker family，`113` 仍不得顺手混修

## 功能需求

| ID | 需求 |
|----|------|
| FR-113-001 | `113` 必须为 `082-092` 注册 `program-manifest.yaml` mirror entry，并为每个 entry 写入 `frontend_evidence_class: "framework_capability"` |
| FR-113-002 | `113` 必须为 `082-084` 各追加一个 latest-batch close-check backfill 段落 |
| FR-113-003 | 新增段落必须补齐 latest batch 当前 close-check 需要的 mandatory fields，包括 `验证画像`、`统一验证命令`、`代码审查结论（Mandatory）`、`任务/计划同步状态（Mandatory）` 与 `归档后动作` |
| FR-113-004 | `113` 必须注册自身到 `program-manifest.yaml`，并推进 `next_work_item_seq` 到 `114` |
| FR-113-005 | `113` 必须用 fresh close-check 证明 `082-092` 与 `113` 自身的 done gate 能在 clean tree 下通过 |

## 成功标准

- **SC-113-001**：`uv run ai-sdlc workitem close-check --wi specs/082-frontend-evidence-class-authoring-surface-baseline` 通过
- **SC-113-002**：`uv run ai-sdlc workitem close-check --wi specs/083-frontend-evidence-class-validator-surface-baseline` 通过
- **SC-113-003**：`uv run ai-sdlc workitem close-check --wi specs/084-frontend-evidence-class-diagnostic-contract-baseline` 通过
- **SC-113-004**：`uv run ai-sdlc workitem close-check --wi specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline` 通过
- **SC-113-005**：`uv run ai-sdlc workitem close-check --wi specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline` 通过
- **SC-113-006**：`uv run ai-sdlc workitem close-check --wi specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline` 通过
- **SC-113-007**：`uv run ai-sdlc workitem close-check --wi specs/088-frontend-evidence-class-bounded-status-surface-baseline` 通过
- **SC-113-008**：`uv run ai-sdlc workitem close-check --wi specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline` 通过
- **SC-113-009**：`uv run ai-sdlc workitem close-check --wi specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline` 通过
- **SC-113-010**：`uv run ai-sdlc workitem close-check --wi specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline` 通过
- **SC-113-011**：`uv run ai-sdlc workitem close-check --wi specs/092-frontend-evidence-class-runtime-reality-sync-baseline` 通过
- **SC-113-012**：`uv run ai-sdlc workitem close-check --wi specs/113-frontend-082-092-manifest-mirror-baseline` 通过

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/112-frontend-072-081-close-check-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
