# 功能规格：Frontend Evidence Class Writeback Close-Check Runtime Closure Baseline

**功能编号**：`130-frontend-evidence-class-writeback-close-check-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已由现有实现满足并完成 focused verification
**输入**：[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`](../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md)、[`../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md`](../090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md)、[`../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`](../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md)、[`../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md`](../092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md)、[`../109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md`](../109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md)、[`../110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md`](../110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md)、[`../111-frontend-p1-child-close-check-backfill-baseline/spec.md`](../111-frontend-p1-child-close-check-backfill-baseline/spec.md)、[`../112-frontend-072-081-close-check-backfill-baseline/spec.md`](../112-frontend-072-081-close-check-backfill-baseline/spec.md)、[`../113-frontend-082-092-manifest-mirror-baseline/spec.md`](../113-frontend-082-092-manifest-mirror-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)

> 口径：`130` 是 `120/T24` 的 implementation carrier。它不再引入新的 evidence-class 生命周期语义，而是把已经分散落地在 explicit mirror sync、close-check late resurfacing、runtime reality sync 与 `109-113` backfill closeout 上的现有 runtime 收成同一条 closure slice，明确 `T24` 所要求的 writeback/close-check/backfill 主线已经进入真实运行面。

## 问题定义

`087`、`089`、`090` 只冻结了 prospective writeback、late resurfacing 与 rollout sequencing；`091`、`092`、`109-113` 则把 close-check implementation、explicit sync、manifest registration 与历史 closeout 回填逐步落到了代码和 formal 载体上。当前缺的不是再写一套新逻辑，而是缺少一个总 carrier 去回答：

- explicit program-level mirror write surface 是否已经成为当前唯一合法 writer
- close-check late resurfacing 是否已经从 `091` 的“首批 implementation slice 进行中”推进到完整 closure
- runtime rollout sequencing 与历史 backfill closeout 是否已经把 evidence-class lifecycle 接成 authoring/validate/status/close-check/writeback 的单链

如果这层继续空缺，`120/T24` 会一直停留在抽象 implementation carrier 占位，reviewer 也无法从 formal 载体直接判断哪些能力已经是现行 machine truth，哪些只是 historical prospective contract。

## 范围

- **覆盖**：
  - 将现有 explicit sync、close-check resurfacing、runtime reality sync 与 backfill closeout 收束为 `120/T24` 的正式 implementation carrier
  - 明确 `program frontend-evidence-class-sync` 是当前 explicit program-level mirror write surface
  - 明确 `workitem close-check` 的 evidence-class resurfacing 已形成完整 bounded closure
  - 明确 `109-113` 的 metadata/closeout backfill 已进入当前 lifecycle 主链
  - 回链 `120/T24`、推进 `project-state.yaml` 的下一个工单序号
  - 用 focused verification 证明当前 writeback/close-check runtime 一致
- **不覆盖**：
  - 新增新的 writeback mode、close-check check family 或 diagnostics family
  - 改写 `087/089/090` 的 historical docs-only wording
  - 扩张到 `T25` 之后的 program automation 主线

## 已锁定决策

- `program frontend-evidence-class-sync` 继续是当前 explicit mirror writer，不允许 validator/status/close-check opportunistic write
- `workitem close-check` 继续只做 bounded late resurfacing，不承担 first-detection 或 auto-heal
- `092` 的 runtime reality sync 与 `109-113` 的 metadata/closeout backfill 一并视为 `T24` 已吸收的现有 closure 组成部分
- `130` 只把现有 passing runtime 写实为 closure slice；若后续要扩写 lifecycle，应落到 `T25` 及更后继任务

## 功能需求

| ID | 需求 |
|----|------|
| FR-130-001 | `130` 必须明确 `program frontend-evidence-class-sync` 已满足 `087` 所要求的 explicit program-level mirror write surface |
| FR-130-002 | `130` 必须明确 `workitem close-check` 已满足 `089/091` 所要求的 bounded late resurfacing closure |
| FR-130-003 | `130` 必须明确 `092` 的 runtime reality sync 已将 writeback/status/close-check 现状写实到当前 framework truth |
| FR-130-004 | `130` 必须明确 `109-113` 的 metadata 与 closeout backfill 已把历史 evidence-class lifecycle 接回当前主链 |
| FR-130-005 | `130` 必须回链 `120/T24`，让抽象 implementation carrier 升级为正式工单 |
| FR-130-006 | `130` 必须用 focused verification 证明 close-check / explicit sync / backfill 相关 runtime 当前一致 |

## Exit Criteria

- **SC-130-001**：reviewer 可以从 `130` 直接读出 evidence-class 从 authoring/validate/status/close-check 到 explicit writeback 的单链 closure
- **SC-130-002**：`120/T24` 不再停留在抽象 implementation carrier 占位
- **SC-130-003**：focused verification 能证明 `T24` 当前缺口主要是 formal carrier 缺失，而非新的 runtime 语义未实现

---
related_doc:
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
  - "specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md"
  - "specs/112-frontend-072-081-close-check-backfill-baseline/spec.md"
  - "specs/113-frontend-082-092-manifest-mirror-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/core/close_check.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/workitem_cmd.py"
frontend_evidence_class: "framework_capability"
---
