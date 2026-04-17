# 功能规格：Frontend P1 Experience Stability Closure Audit Reconciliation Baseline

**功能编号**：`156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline`
**创建日期**：2026-04-17
**状态**：已实现（truth-only closure carrier）
**输入**：承接 `120/155`，在 root `capability_closure_audit` 口径下，对 `frontend-p1-experience-stability` 的 open cluster 做一次 fresh closure reconciliation；只允许消费 `066-072`、`076` 的 current close-check / truth evidence，目标是在不伪造新 runtime 的前提下，把已经过时的 P1 open cluster 从 root truth 中移除。参考：`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/155-frontend-program-automation-chain-closure-audit-reconciliation-baseline/spec.md`、`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`、`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`、`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`、`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`、`specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`、`specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md`、`specs/072-frontend-p1-root-rollout-sync-baseline/spec.md`、`specs/076-frontend-p1-root-close-sync-baseline/spec.md`

> 口径：`156` 不是再做 P1 runtime implementation，也不是把 `072/076` 提升为 capability delivery。它只处理 root truth reconciliation：若 `066-072`、`076` 的 fresh close evidence 已足以证明当前 root `frontend-p1-experience-stability` wording 过时，就移除该 open cluster；若 evidence 仍存在 material residual gap，则把 root wording 收缩为单一、诚实且有界的剩余阻塞，而不是继续沿用旧的“`067-069` 有实现、`070-071` docs-only”描述。

## 问题定义

`120` 曾将 `frontend-p1-experience-stability` 标成 `S5` open capability cluster，并给出以下旧口径：

- `067-069` 有局部 implementation slice
- `070-071` 仍 docs-only
- `066/072/076` 的 sync / wording carrier 不能等同 capability delivery

当前仓库中的真实情况已经进一步演化：

- `066-072`、`076` 在 fresh truth 下均可通过 current `workitem close-check`
- `072/076` 的角色已经固定为 root sync / honesty carrier，而不是 capability delivery proof
- `frontend-program-branch-rollout-plan.md` 中关于 `missing_artifact [frontend_contract_observations]` 的说明，已被 `079` 的 framework-only policy split 约束为 consumer implementation evidence 缺口，不应再反推为框架侧 P1 capability 仍然 open
- root `program-manifest.yaml` 仍保留 `frontend-p1-experience-stability=capability_open`，且 summary 继续使用旧 tranche wording，已经与 fresh close evidence 不一致

因此，`156` 的职责是把 P1 cluster 的 root truth 收束为一条 capability closure reconciliation 问题：以 `066-072`、`076` 的 fresh close evidence 为唯一依据，明确 child carrier、sync carrier 与外部 consumer evidence 之间的边界，并决定 root `open_clusters` 是否继续保留 `frontend-p1-experience-stability`。

## 范围

- **覆盖**：
  - 冻结 `frontend-p1-experience-stability` 的 closure universe 为 `066-072`、`076`
  - 对 `066-072`、`076` 执行 fresh close-check sweep，并记录 child carrier 与 sync carrier 的分类
  - 将常驻对抗专家的评估固化为显式约束：不得把 `072/076` 当成 capability delivery proof，不得把 `frontend_contract_observations` 缺口伪造成框架内已补齐
  - 回写 root `program-manifest.yaml`，移除已过时的 `frontend-p1-experience-stability` open cluster
  - 执行 `program truth sync --execute --yes` 与 `program truth audit`，刷新 root truth
- **不覆盖**：
  - 不新增 `src/` / `tests/` runtime 实现
  - 不修改 `066-072`、`076` 的 formal scope 或历史结论
  - 不修改 `frontend-program-branch-rollout-plan.md`；该 advisory 汇总文档的对齐由后续 docs-only carrier 处理
  - 不顺带关闭 `agent-adapter-verified-host-ingress`、`project-meta-foundations`、`frontend-evidence-class-lifecycle`
  - 不把 `072/076` 写成 implementation carrier
  - 不伪造 `frontend_contract_observations` 已在仓库内被真实 consumer 项目回填

## 已锁定决策

- `frontend-p1-experience-stability` 的 cluster close 只能基于 fresh machine-verifiable evidence，不接受旧 backlog wording 直接推断
- `072/076` 只提供 root sync / honesty evidence，不提供 capability delivery proof
- `frontend_contract_observations` 若仍作为 active spec 外部输入缺口存在，只能被解释为 consumer evidence 层残余，不得继续作为框架侧 P1 capability_open 的直接依据
- 本工单只消费以下 machine surfaces：
  - `python -m ai_sdlc workitem close-check --wi ...`
  - `uv run ai-sdlc verify constraints`
  - `python -m ai_sdlc program truth sync --execute --yes`
  - `python -m ai_sdlc program truth audit`
- 若 `066-072`、`076` 任一 ref 在 current grammar 下无法形成 fresh close evidence，`156` 必须 fail-closed

## 用户场景与测试

### US-156-1 — Maintainer 需要 root truth 不再保留过时的 P1 open cluster

作为**框架维护者**，我希望 root truth 只保留真正未收口的 cluster，而不是继续把已经完成 reconciliation 的 `frontend-p1-experience-stability` 维持为 open。

**优先级说明**：P0。只要该 cluster 仍挂在 root `open_clusters` 中，global truth 就会继续误报框架侧 P1 capability 仍未闭环。

**独立测试**：完成 `156` 后，`program-manifest.yaml` 中不再存在 `frontend-p1-experience-stability` 的 open cluster 条目。

**验收场景**：

1. **Given** `066-072`、`076` 均已有 fresh close evidence，**When** 我执行 `156`，**Then** root `open_clusters` 中不再保留 `frontend-p1-experience-stability`
2. **Given** root truth 已刷新，**When** 我查看 bounded capability closure surface，**Then** 我不会再看到过时的 `frontend-p1-experience-stability=capability_open`

### US-156-2 — Reviewer 需要 child carrier、sync carrier 与外部 consumer evidence 被诚实区分

作为**reviewer**，我希望 `067-071` 的 child evidence、`072/076` 的 sync 角色，以及 `frontend_contract_observations` 的外部输入缺口被分层说明，这样不会把不同 truth layer 混成同一条未闭环理由。

**优先级说明**：P0。若继续混淆这些层次，root capability audit 就会重复暴露已经过时的 blocker。

**独立测试**：`156/spec.md`、`task-execution-log.md` 与 root truth 更新后，均明确说明 `072/076` 不属于 capability delivery，`frontend_contract_observations` 也不再被当成框架侧 P1 capability 未闭环的直接证明。

**验收场景**：

1. **Given** 我检查 `156` formal docs，**When** 我查看锁定决策，**Then** 能看到 `072/076` 只是 sync carrier
2. **Given** 我查看 root truth 与 `156` 的收口记录，**When** 我对照 `079` 的 policy split，**Then** 不会再把 consumer evidence gap 误读为 framework capability gap

### US-156-3 — Operator 需要 `156` 的收口记录显式停留在 truth-only 边界

作为**operator**，我希望 `156` 在关闭 root P1 cluster 后，不再顺手改写人读 rollout 汇总，而是把“下一条 frontend 主线”留给后续独立 docs-only / planning carrier 处理。

**优先级说明**：P1。若在 truth-only carrier 中混入额外的人读排序调整，会破坏 close-check 对验证画像的约束。

**独立测试**：`156/spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md` 都明确把 `frontend-program-branch-rollout-plan.md` 排除在本批改动之外。

**验收场景**：

1. **Given** 我查看 `156` 的 formal docs，**When** 我关注 truth-only 边界，**Then** 会看到 rollout 汇总被显式排除在本批之外
2. **Given** root P1 cluster 已被移除，**When** 我继续做 frontend 排序决策，**Then** 我需要基于最新 root truth 或独立 planning carrier，而不是把 `156` 误解为已完成全部人读汇总同步

### 边界情况

- 即使 `072/076` close-check 通过，也不能把它们当成 capability delivery proof；它们只证明 sync / honesty carrier 自身已闭环
- 即使 `frontend_contract_observations` 仍在部分人读文案中出现，也只能被解释为 consumer evidence gap，不足以单独维持 framework P1 cluster=open
- `156` 不能因为关闭了 P1 cluster，就顺带宣称 `frontend-evidence-class-lifecycle` 或其他 cluster 已关闭

## 需求

### 功能需求

- **FR-156-001**：系统必须把 `frontend-p1-experience-stability` 的 closure reconciliation 作为独立 truth-only carrier 处理，而不是直接手改 manifest
- **FR-156-002**：系统必须将 cluster close evidence 的 closure universe 固定为 `066-072`、`076`
- **FR-156-003**：系统必须以 `066-072`、`076` 的 fresh close-check 作为 root reconciliation 的唯一 machine evidence
- **FR-156-004**：系统必须显式记录常驻对抗专家评估带来的三条约束：不得用 `072/076` 冒充 capability delivery、不得用 `frontend_contract_observations` 伪造 closure、不得把 `156` 扩成多 cluster 清理
- **FR-156-005**：根级 `capability_closure_audit` 对 `frontend-p1-experience-stability` 的关闭必须通过移除 `open_clusters` 条目表达
- **FR-156-006**：系统必须在 `156` 的 formal close-out docs 中显式记录：`frontend-program-branch-rollout-plan.md` 不属于本批 truth-only 变更范围
- **FR-156-007**：`156` 必须在 root cluster removal 后刷新 `truth_snapshot`
- **FR-156-008**：若 close-check sweep 或 truth refresh 暴露 material residual blocker，`156` 必须 fail-closed

### 关键实体

- **P1 Close Sweep**：对 `066-072`、`076` 执行的 fresh close-check 证据汇总
- **Carrier Classification**：将 `067-071` 归类为 child capability/close evidence，将 `072/076` 归类为 root sync/honesty carrier
- **Adversarial Guardrail Set**：常驻对抗专家对 `156` 给出的三条 fail-closed 约束
- **Open Cluster Removal**：把 `frontend-p1-experience-stability` 从 root `open_clusters` 中移除的动作
- **Truth Refresh Snapshot**：在 cluster removal 后重新 materialize 的 root truth snapshot

## 成功标准

- **SC-156-001**：`066-072`、`076` 的 fresh close-check sweep 全部通过
- **SC-156-002**：`frontend-p1-experience-stability` 从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除
- **SC-156-003**：`program truth sync --execute --yes` 后，root truth 保持 fresh，且 `program truth audit` 不再暴露 `frontend-p1-experience-stability`
- **SC-156-004**：`156` 的 formal close-out docs 不再把 rollout 汇总同步误记为本批已完成动作，并显式保留 truth-only 边界
- **SC-156-005**：`156` 的收口语义诚实停留在 capability closure reconciliation，不伪造新的 runtime 实现

---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/155-frontend-program-automation-chain-closure-audit-reconciliation-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/072-frontend-p1-root-rollout-sync-baseline/spec.md"
  - "specs/076-frontend-p1-root-close-sync-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
