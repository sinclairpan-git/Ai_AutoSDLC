# 功能规格：Release Docs And Execute Handoff Guard Baseline

**功能编号**：`118-release-docs-and-execute-handoff-guard-baseline`
**创建日期**：2026-04-13
**状态**：已完成
**输入**：Close `FD-2026-04-07-001` and `FD-2026-04-07-003` in one bounded guard slice, and backfill `FD-2026-04-07-002` as closed now that formal artifact target guard and breach logging guard have landed. 参考：`docs/framework-defect-backlog.zh-CN.md`、`docs/框架自迭代开发与发布约定.md`、`USER_GUIDE.zh-CN.md`、`README.md`、`packaging/offline/README.md`、`docs/releases/v0.6.0.md`、`docs/pull-request-checklist.zh.md`

> 口径：`118` 不是新的安装器 work item，也不是新的会话语义理解器。它只补两类 bounded hard guard：其一是 `plan/spec freeze != 可直接进入实现` 的 repo-truth guard；其二是 `v0.6.0` release 入口文档一致性 sweep。与此同时，它负责把已由 `117` 落地的 `FD-2026-04-07-002` 正式回填为已收口。

## 问题定义

当前 backlog 中仍有两类已明确识别、但尚未沉淀成硬 guard 的缺口：

- `FD-2026-04-07-003`：当 formal `spec.md / plan.md` 已落成但 `tasks.md` 仍不存在，执行侧容易把“下一步”自然推进成实现，而不是停在 docs-only / review-to-decompose。该问题本质上不是聊天文案优化，而是 execute authorization 的硬边界没有被持续暴露成稳定 surface。
- `FD-2026-04-07-001`：`v0.6.0` 的 release notes、README、offline README、用户手册、发布约定与 PR checklist 虽然已有局部修正，但还没有一条 repo 内 sweep 会去核对“版本号 + 平台资产分工 + release 入口”是否一致，因此仍可能出现入口文档假绿。

另外，`FD-2026-04-07-002` 在 `117` 已经具备实质实现：formal artifact canonical target guard 与 breach logging guard 已落地并经过 focused verification。当前剩下的只是 backlog 真值回填，避免 backlog 顶部摘要与条目状态继续滞后。

## 范围

- **覆盖**：
  - 为 `tasks.md` 缺失 / 未进入 execute 的场景增加更明确的 execute handoff guard surface
  - 将上述 guard 接到现有 `status` / `status --json` / `verify constraints` 或等价 bounded surface
  - 增加 `v0.6.0` release docs consistency sweep，并让 `verify constraints` 能稳定阻断入口文档漂移
  - 回填 `FD-2026-04-07-002` 的 backlog 状态与 backlog 顶部摘要
  - 补 focused unit/integration tests
- **不覆盖**：
  - 不引入会话语义分类器，也不尝试判断用户“是否真想编码”的自然语言意图
  - 不扩张到新的 release automation、tagging、打包脚本或 GitHub release 发布器
  - 不重写 `096` host runtime manager 线
  - 不改动 `117` 已完成的 formal artifact target guard 行为边界

## 已锁定决策

- execute handoff guard 以 repo truth 为准，最小判断面仍是 `tasks.md` 存在性 + 当前阶段是否进入 `execute/close`
- `status` 系列 surface 必须给出稳定、bounded 的 detail；不输出长篇 remediation 建议
- release docs consistency sweep 只核对 repo 内固定入口文件，不扫描全仓 Markdown
- `FD-2026-04-07-002` 的回填必须和本次实现一起完成，避免 backlog 自身继续滞后

## 用户故事与验收

### US-118-1 — Framework Maintainer 需要 `tasks.md` 缺失时稳定停在 docs-only / review

作为 **framework maintainer**，我希望当 active work item 只有 `spec.md / plan.md`、没有 `tasks.md` 或尚未进入 execute 时，bounded surface 只能返回 docs-only / review-to-decompose 口径，这样就不会再把 plan freeze 误当成编码授权。

**验收**：

1. Given active work item 缺少 `tasks.md`，When 运行 execute handoff guard，Then 返回 blocked，reason code 稳定，detail 明确停在 docs-only / review
2. Given active work item 已有 `tasks.md` 但阶段仍是 `verify/review`，When 运行 execute handoff guard，Then 仍为 blocked，且 detail 明确未进入 execute
3. Given active work item 已有 `tasks.md` 且阶段已进入 `execute/close`，When 运行 guard，Then 返回 ready

### US-118-2 — Release Maintainer 需要入口文档一致性有固定 sweep

作为 **release maintainer**，我希望当仓库宣称当前版本为 `v0.6.0` 时，README、release notes、offline README、用户手册、发布约定与 PR checklist 能被同一 sweep 核对，这样不会出现 release 已更新但入口文档仍假绿。

**验收**：

1. Given 某个入口文档缺少 `v0.6.0` 或缺少平台资产分工，When 运行 release docs consistency sweep，Then 返回 blocker
2. Given 六个固定入口文件版本与资产口径一致，When 运行 sweep，Then 无 blocker

### US-118-3 — Backlog Maintainer 需要 `FD-2026-04-07-002` 真值回填

作为 **backlog maintainer**，我希望 `FD-2026-04-07-002` 在 `117` 落地后被正式标记为 closed，并同步更新 backlog 顶部摘要，这样 backlog 真值不会继续落后于仓库实现。

**验收**：

1. Given `117` 已提供 formal artifact target guard 与 backlog breach guard，When 回填 `FD-2026-04-07-002`，Then 条目状态与顶部摘要都与当前事实一致

## 边界情况

- `tasks.md` 缺失时，guard 可以引用 docs-only / review-to-decompose，但不能推断任何会话级用户意图
- release sweep 必须允许固定版本字符串只出现于目标入口文件，而不是要求整个仓库全文统一
- release sweep 只核对当前 backlog 钉住的 `v0.6.0`，不把旧版 release notes 当 blocker

## 功能需求

| ID | 需求 |
|----|------|
| FR-118-001 | 系统必须为 active work item 暴露 execute handoff guard，明确 `tasks.md` 缺失或阶段未进入 execute 时不得视为可直接进入实现 |
| FR-118-002 | execute handoff guard 必须输出稳定 reason code 与 bounded detail，并接入现有 `status` / `status --json` 或等价 surface |
| FR-118-003 | 系统必须提供 `v0.6.0` release docs consistency sweep，固定核对 `README.md`、`docs/releases/v0.6.0.md`、`USER_GUIDE.zh-CN.md`、`packaging/offline/README.md`、`docs/框架自迭代开发与发布约定.md`、`docs/pull-request-checklist.zh.md` |
| FR-118-004 | 当 release 入口文档缺失版本号或平台资产分工口径时，`verify constraints` 必须返回 blocker |
| FR-118-005 | `FD-2026-04-07-002` 的 backlog 条目与 backlog 顶部摘要必须在本次 work item 中回填为与仓库事实一致 |

## 成功标准

- **SC-118-001**：`tasks.md` 缺失时，bounded guard 稳定返回 blocked，detail 明确为 docs-only / review-to-decompose
- **SC-118-002**：阶段未进入 execute 时，不再出现“plan freeze 已可直接进入实现”的 bounded status 口径
- **SC-118-003**：release docs consistency sweep 能稳定识别入口文档缺口
- **SC-118-004**：`FD-2026-04-07-002` 已正式回填为 closed，且 backlog 顶部摘要不再将其列为待修

---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "README.md"
  - "packaging/offline/README.md"
  - "docs/releases/v0.6.0.md"
  - "docs/pull-request-checklist.zh.md"
frontend_evidence_class: "framework_capability"
