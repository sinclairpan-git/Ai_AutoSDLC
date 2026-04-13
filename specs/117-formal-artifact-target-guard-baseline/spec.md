# 功能规格：Formal Artifact Target Guard Baseline

**功能编号**：`117-formal-artifact-target-guard-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：Remediate `FD-2026-04-07-002` by freezing a canonical guard that prevents formal `spec.md / plan.md / tasks.md` from being written into `docs/superpowers/*` and requires same-turn backlog logging once a breach is identified. 参考：`docs/framework-defect-backlog.zh-CN.md`、`cursor/rules/ai-sdlc.md`、`src/ai_sdlc/stages/refine.yaml`、`USER_GUIDE.zh-CN.md`

> 口径：`117` 不是新的 direct-formal scaffold 能力，也不是重写 `073` 的 formal docs。它承接的是 `FD-2026-04-07-002` 暴露出的两类高优先回归：formal artifact 落点误写，以及识别违约后没有在同轮立即补录 backlog。

## 问题定义

当前仓库已经明确区分了两类文档：

- `specs/<WI>/spec.md|plan.md|tasks.md`：formal canonical truth
- `docs/superpowers/*`：design input / auxiliary reference

但 `FD-2026-04-07-002` 说明，这个边界仍没有被真正收敛成硬门。执行侧仍可能在 formal spec 生成时误把 `docs/superpowers/specs/*` 当成落点；而当违约已经被识别时，也还可能先停在口头承认或解释层，没有把登记 `docs/framework-defect-backlog.zh-CN.md` 作为同轮原子动作完成。

如果这两个约束继续只存在于文档说明而没有 preflight / guard，formal artifact 与 breach logging 的可信度仍会反复回归。

## 范围

- **覆盖**：
  - 纠正 `117` formal docs，使其与 `FD-2026-04-07-002` 的真实目标一致
  - 为 formal artifact target 增加 canonical-path guard
  - 阻断 formal spec/plan/tasks 写入 `docs/superpowers/*`
  - 为 breach-detected-but-not-logged 增加可测试的 blocker / check surface
  - 为以上 guard 补自动化回归
- **不覆盖**：
  - 重写 `brainstorming` / `writing-plans` 宿主 skill 本身
  - 扩展到 execute authorization 语义（该问题已由 `116` 承接）
  - 追溯修复所有历史 superpowers design docs
  - 把所有非 formal artifact 都纳入同一写保护系统

## 已锁定决策

- formal `spec.md / plan.md / tasks.md` 的唯一合法 canonical target 是 `specs/<WI>/`
- `docs/superpowers/*` 只能作为 `related_doc` / 设计输入，不再是 formal artifact 候选落点
- 一旦已识别出流程违约，“登记 framework-defect-backlog”必须成为同轮动作，不能被解释或迁移动作打断
- guard 必须是可测试、可复用的仓库内真值，不依赖聊天记忆

## 用户故事与验收

### US-117-1 — Framework Maintainer 需要 formal artifact 只能写到 canonical 路径

作为 **framework maintainer**，我希望当产物类型属于 formal spec/plan/tasks 时，框架只能接受 `specs/<WI>/` 作为写入目标，这样不会再把 formal truth 写到 `docs/superpowers/*`。

**验收**：

1. Given 目标路径位于 `specs/<WI>/spec.md`，When 进行 formal artifact preflight，Then guard 允许继续
2. Given 目标路径位于 `docs/superpowers/specs/*.md` 且 artifact 类型为 formal spec，When 进行 formal artifact preflight，Then guard 必须阻断并返回稳定 reason code

### US-117-2 — Operator 需要 breach logging 与违约识别保持同轮原子性

作为 **operator**，我希望当执行侧已经识别出“这是违约”时，系统必须同步要求补录 backlog，而不是继续停在解释层，这样流程台账不会再次假绿。

**验收**：

1. Given 某次流程已明确识别 breach，但同轮未记录 backlog，When 运行相应 guard / check，Then 结果必须是 blocked
2. Given breach 已识别且 backlog 已落盘，When 再运行 guard / check，Then blocker 消失

## 边界情况

- formal artifact target 未绑定 concrete work item 时，guard 应返回 blocked 或 unavailable，而不是猜测落点
- `docs/superpowers/*` 中的普通设计稿、辅助研究文档不应被误判成 formal artifact
- 历史已有 backlog 条目但本轮 breach 尚未补录时，仍应以“本轮未原子补录”为 blocker，而不是简单复用旧条目遮蔽问题

## 功能需求

| ID | 需求 |
|----|------|
| FR-117-001 | 系统必须为 formal artifact target 提供 canonical-path preflight |
| FR-117-002 | 当 artifact 类型属于 formal `spec.md / plan.md / tasks.md` 且目标位于 `docs/superpowers/*` 时，preflight 必须阻断 |
| FR-117-003 | 系统必须提供 breach-detected-but-not-logged 的 blocker / check surface |
| FR-117-004 | `117` 必须补自动化回归，覆盖 formal artifact target 正反夹具与 breach logging 原子性夹具 |
| FR-117-005 | `117` 的 status / close / review surface 不得再把 formal 与 auxiliary artifact 视为可互换类型 |

## 成功标准

- **SC-117-001**：formal spec 写入 `docs/superpowers/specs/*` 的尝试会被稳定阻断
- **SC-117-002**：formal `specs/<WI>/spec.md` 的合法写入路径仍被允许
- **SC-117-003**：已识别 breach 但未同轮记账时，guard / check 返回 blocker
- **SC-117-004**：对应 unit/integration focused tests 全部通过

---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "cursor/rules/ai-sdlc.md"
  - "src/ai_sdlc/stages/refine.yaml"
  - "USER_GUIDE.zh-CN.md"
frontend_evidence_class: "framework_capability"
