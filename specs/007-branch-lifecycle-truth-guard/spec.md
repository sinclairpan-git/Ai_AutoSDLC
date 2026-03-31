# 功能规格：Branch Lifecycle Truth Guard

**功能编号**：`007-branch-lifecycle-truth-guard`  
**创建日期**：2026-03-31  
**状态**：已冻结（formal work item baseline）  
**输入**：[`../../docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md`](../../docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-31-002`、[`../../src/ai_sdlc/rules/git-branch.md`](../../src/ai_sdlc/rules/git-branch.md)、[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)

> 口径：本 work item 不是新增 Git 能力本身，而是把 branch/worktree lifecycle 从“人工纪律”升级成仓库可审计、可检查、可收口的正式真值面。

## 范围

- **覆盖**：
  - 本地 branch/worktree inventory 的只读读取、分类与相对 `main` 偏离计算
  - `design / feature / scratch / archive / unmanaged` 生命周期分类
  - work item 关联分支的 disposition 真值：`merged / archived / deleted`
  - `workitem close-check` / `workitem branch-check` 对未处置分支的 close-out 判断
  - `verify constraints` 的 branch lifecycle governance surface
  - `status --json` / `doctor` 的 bounded branch lifecycle read surface
  - `git-branch.md`、`pipeline.md`、execution-log 模板与用户文档的 branch close-out 约束
- **不覆盖**：
  - 自动 merge / 自动 delete / 自动 prune / 自动 archive
  - 远端 fetch、network 对账、跨仓库分支治理
  - execute 阶段的默认 blocker
  - 基于聊天结论或会话备注推断“已 merged”

## 已锁定决策

- 分支 inventory 默认保持 **read-only**
- `scratch` 分支允许存在，但只作为临时执行容器；close 前必须有 disposition
- `archived` 是正式 disposition，且与 `merged` 不同
- 历史无关分支最多形成 warning，不得默认阻断当前 work item close
- 只有与当前 work item 明确关联且未处置的分支/worktree，才能进入 close truth blocker

## 用户故事与验收

### US-007-1 — Framework Maintainer 需要看见真实分支库存

作为**框架维护者**，我希望仓库能只读暴露 branch/worktree inventory 与相对 `main` 的偏离，以便不再靠人工巡检才发现遗留 scratch 分支。

**验收**：

1. Given 仓库存在多个本地分支和 worktree，When 读取 branch inventory，Then 系统返回稳定排序的 branch/worktree、upstream、worktree 绑定和 divergence 摘要
2. Given 某分支仅存在于本地 scratch/worktree，When 读取 inventory，Then 系统不会把它误当成主线已兑现

### US-007-2 — Close Reviewer 需要显式 branch disposition 真值

作为**close reviewer**，我希望当前 work item 关联的分支在收口前明确标记为 `merged / archived / deleted`，以便“分支已实现”和“主线已兑现”不再混淆。

**验收**：

1. Given 当前 work item 仍有关联 scratch 分支比 `main` 多提交，When 运行 close-check，Then 系统返回明确 blocker 或 warning，而不是静默通过
2. Given 关联分支已明确处置为 `merged / archived / deleted`，When 运行 close-check，Then branch lifecycle 缺口不再阻断收口

### US-007-3 — Operator 需要 bounded read-only 分支健康面

作为**operator**，我希望 `status --json` 与 `doctor` 能以 bounded、read-only 的方式暴露 branch lifecycle 健康摘要，以便日常判断是否存在未处置分支漂移。

**验收**：

1. Given 仓库存在未处置 branch/worktree，When 执行 `status --json` 与 `doctor`，Then 可以看到 branch lifecycle 摘要或 readiness finding
2. Given 只读 surface 被调用，When 命令结束，Then 不得触发 fetch、prune、cleanup 或其他隐式写副作用

## 功能需求

### Inventory And Classification

| ID | 需求 |
|----|------|
| FR-007-001 | 系统必须提供 branch/worktree inventory 的只读读取面，至少包含 branch 名称、upstream、worktree 绑定、当前 commit 和相对 `main` 的 ahead/behind |
| FR-007-002 | 系统必须把 branch 生命周期至少分类为 `design`、`feature`、`scratch`、`archive`、`unmanaged` |
| FR-007-003 | branch inventory 输出必须稳定排序，适合 snapshot tests 与 machine-readable 消费 |
| FR-007-004 | `scratch` / `codex/*` / backup / worktree 分支不得被默认视为主线已兑现事实 |

### Disposition Truth And Close-Out

| ID | 需求 |
|----|------|
| FR-007-005 | 当前 work item 关联分支在 close 前必须显式处置为 `merged`、`archived` 或 `deleted` |
| FR-007-006 | `archived` 必须是正式 disposition，且不得被等同为 `merged` |
| FR-007-007 | close-check 必须对“关联分支仍比 `main` 多提交且未处置”给出明确 blocker 或 warning |
| FR-007-008 | execution-log close-out 模板必须为 branch disposition 留出正式字段，不能继续只保留“删除已合并分支（可选）”语义 |

### Governance And Bounded Read Surfaces

| ID | 需求 |
|----|------|
| FR-007-009 | `verify constraints` 必须增加 branch lifecycle governance surface，用于发现当前 work item 的 unresolved branch/worktree truth |
| FR-007-010 | `status --json` 与 `doctor` 必须以 bounded、read-only 方式暴露 branch lifecycle 摘要，不得触发 fetch/prune/rebuild/cleanup |
| FR-007-011 | 历史无关分支最多形成 warning，不得默认阻断当前 work item close |
| FR-007-012 | 系统必须提供 work-item-scoped 的只读 `branch-check` surface，回答“这个 work item 还有哪些未处置 branch/worktree” |

### Explicit Non-Goals

| ID | 需求 |
|----|------|
| FR-007-013 | Phase 1 不得自动 merge / delete / prune / archive 任意 branch 或 worktree |
| FR-007-014 | Phase 1 不得把 branch lifecycle 直接接入 execute blocker；branch lifecycle 的阻断面应停留在 close/governance |

## 成功标准

- **SC-007-001**：branch/worktree inventory 能稳定返回分类、绑定关系和相对 `main` 的 divergence，且输出顺序可快照验证
- **SC-007-002**：当当前 work item 关联 scratch/worktree 分支仍未处置时，`close-check` 或 `branch-check` 能显式发现
- **SC-007-003**：`verify constraints`、`status --json`、`doctor` 至少有一个 bounded read surface 能持续暴露 branch lifecycle 缺口
- **SC-007-004**：历史无关分支不会被错误升级成当前 work item close blocker
- **SC-007-005**：整套 branch lifecycle surface 在默认路径上保持 read-only，不引入新的隐式 Git 写副作用
