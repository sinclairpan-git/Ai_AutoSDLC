# 功能规格：Frontend Framework-Only Prospective Closure Contract Baseline

**功能编号**：`081-frontend-framework-only-prospective-closure-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../079-frontend-framework-only-closure-policy-baseline/spec.md`](../079-frontend-framework-only-closure-policy-baseline/spec.md)、[`../080-frontend-framework-only-root-policy-sync-baseline/spec.md`](../080-frontend-framework-only-root-policy-sync-baseline/spec.md)、[`../../frontend-program-branch-rollout-plan.md`](../../frontend-program-branch-rollout-plan.md)

> 口径：`081` 冻结的是 prospective-only contract，而不是 runtime 改造批次。它把 `079` 的 policy split 前推成 future machine-gate design target：未来新的 framework-only frontend work item，必须在 authoring 阶段显式声明自己属于 `framework_capability` 还是 `consumer_adoption`，且二者不得继续混写到同一个 close gate。`081` 不 retroactive 改写 `068` ~ `071`，也不修改当前 `ai-sdlc` 实现。

## 问题定义

`079` 和 `080` 已经把两层 truth 说清楚：

- framework-only repository 可以完成 framework capability
- consumer implementation evidence 仍是独立的外部接入事实

但这条 truth 目前仍停留在 policy / wording 层：

- spec author 未来如何建模，还没有 machine-tractable contract
- reviewer 知道应该拆层，但机器还不知道新 spec 该如何被分类
- 如果后续继续按旧模式写 item，仍会把 framework capability 与 consumer adoption evidence 绑回同一个 close 条件

因此 `081` 要冻结的，是一条仅对未来生效的 prospective contract：

- future framework-only frontend item 必须声明自己的 evidence class
- `framework_capability` 与 `consumer_adoption` 必须分项建模
- future machine gate 可以依据该 contract 实现，但本轮不修改任何代码

## 范围

- **覆盖**：
  - 新建 `081` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `81`
  - 冻结 future frontend framework-only item 的 authoring contract
  - 冻结 future machine-gate implementation 应遵守的输入语义
- **不覆盖**：
  - 修改 `program-manifest.yaml`
  - 修改 `src/` / `tests/` 或当前 `ai-sdlc` runtime behavior
  - retroactively 重写 `068` ~ `071` 的 stage、close 条件或 blocker
  - 发明新的 runtime stage 名称
  - 修改根级 rollout wording

## 已锁定决策

- `081` 只对 future work item 生效，不 retroactive 迁移既有 spec
- future frontend framework-only item 必须显式声明 `evidence class`
- 可接受的 class 只有两类：
  - `framework_capability`
  - `consumer_adoption`
- 单个 future work item 不得同时承载两类 evidence 语义；若两者都需要，必须拆成两个 item
- future machine gate 若实现该 contract，`framework_capability` item 的 close 不得再被真实 `frontend_contract_observations` 缺失直接阻塞
- `consumer_adoption` item 若要求真实页面实现证据，仍必须由 canonical `frontend-contract-observations.json` 满足

## Contract Draft

### 1. Evidence Class

未来新的 framework-related frontend spec 在 authoring 阶段必须声明：

- `framework_capability`
  - 表示该 item 交付的是框架能力、规则、CLI、gate、diagnostics、schema、sample self-check 或等价 framework-side deliverable
- `consumer_adoption`
  - 表示该 item 交付的是消费方真实页面实现接入、真实 observation backfill、真实 contract alignment evidence

### 2. Close Semantics

- 对 `framework_capability`：
  - close evidence 应来自 formal docs、框架实现、测试、sample self-check 或等价 framework-side verification
  - 不得要求同一 item 同时持有真实 consumer observation artifact
- 对 `consumer_adoption`：
  - close evidence 必须来自真实实现来源生成的 canonical `frontend-contract-observations.json` 或其后续正式替代物

### 3. Split Rule

- 若一个需求同时涉及 framework capability 与 consumer adoption：
  - 必须拆成至少两个 work item
  - 前者冻结 framework deliverable
  - 后者冻结真实接入 / backfill evidence
- 不允许再创建“框架能力已实现，但因真实 consumer artifact 不在本仓库内而永远不能 close”的单项混合 spec

### 4. Future Machine-Gate Target

未来若 `ai-sdlc` 要支持该 contract，至少应满足：

- 能从 spec / manifest /等价 metadata 中读取 item 的 evidence class
- 对 `framework_capability` 与 `consumer_adoption` 走不同 frontend gating rule
- 对未声明 evidence class 的 future framework-only frontend item，视为 authoring error，而不是静默沿用旧语义

`081` 只冻结这条 target contract，不规定本轮立刻采用哪一个 metadata 字段名，也不要求本轮实现 parser / validator。

## 用户故事与验收

### US-081-1 — Author 需要在写 future spec 时就声明 evidence class

作为 **author**，我希望 future framework-only frontend spec 在编写时就必须声明自己到底交付 framework capability 还是 consumer adoption evidence，这样后续 close 语义不会再靠 reviewer 口头推断。

**验收**：

1. Given 我阅读 `081`，When 我准备写新的 framework-only frontend spec，Then 我能知道必须二选一声明 `framework_capability` 或 `consumer_adoption`
2. Given 我发现一个需求同时需要两类 evidence，When 我按 `081` 设计，Then 我会把它拆成两个 item，而不是继续写成单个混合 close gate

### US-081-2 — Future Runtime Maintainer 需要一个可实现但不立刻落地的 contract

作为 **future runtime maintainer**，我希望有一条已经冻结的 prospective contract，说明未来 machine gate 至少该识别什么、拒绝什么，这样后续修改 `ai-sdlc` 时不是从零定义语义。

**验收**：

1. Given 我阅读 `081`，When 我规划后续 runtime change，Then 我能知道至少要读取 evidence class，并对两类 item 走不同 gating rule
2. Given 当前 runtime 还没改，When 我核对 `081`，Then 我不会误把它理解成已经生效的行为

### US-081-3 — Reviewer 需要确保既有 item 不被偷偷 retroactive 改义

作为 **reviewer**，我希望 `081` 明确自己只对 future item 生效，这样 `068` ~ `071` 不会在没有单独迁移批次的情况下被偷偷改义。

**验收**：

1. Given 我检查 `081` 的范围和决策，When 我比对 `068` ~ `071`，Then 我能确认它们当前 truth 不因 `081` 自动改变

## 功能需求

| ID | 需求 |
|----|------|
| FR-081-001 | `081` 必须明确自己是 prospective-only contract baseline，而不是 runtime implementation batch |
| FR-081-002 | `081` 必须明确 future framework-only frontend item 需要声明 `framework_capability` 或 `consumer_adoption` evidence class |
| FR-081-003 | `081` 必须明确单个 future work item 不得同时承载这两类 evidence 语义 |
| FR-081-004 | `081` 必须明确 `framework_capability` item 的 close evidence 来源于 framework-side artifacts，而非真实 consumer observation |
| FR-081-005 | `081` 必须明确 `consumer_adoption` item 的 close evidence 仍要求 canonical real-implementation artifact |
| FR-081-006 | `081` 必须明确 future machine gate 应把未声明 evidence class 的 framework-only frontend item 视为 authoring error |
| FR-081-007 | `081` 不得 retroactively 改写 `068` ~ `071` 或任何现有 runtime stage |
| FR-081-008 | `081` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `80` 推进到 `81` |

## 成功标准

- **SC-081-001**：future author 能从 `081` 直接知道 framework-only frontend item 必须声明 evidence class
- **SC-081-002**：future runtime change 可以直接复用 `081` 作为 machine-gate contract 输入，而不是重新发明语义
- **SC-081-003**：`081` 不会让 reviewer 误以为 `068` ~ `071` 已被 retroactive 改义
- **SC-081-004**：本轮 diff 仅新增 `081` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md"
  - "frontend-program-branch-rollout-plan.md"
---
