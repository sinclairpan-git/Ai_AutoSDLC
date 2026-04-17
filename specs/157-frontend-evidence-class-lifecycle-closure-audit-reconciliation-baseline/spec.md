# 功能规格：Frontend Evidence Class Lifecycle Closure Audit Reconciliation Baseline

**功能编号**：`157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline`
**创建日期**：2026-04-17
**状态**：已实现（truth-only closure carrier）
**输入**：承接 `120` 与 `079-092`、`107-113`，在 root `capability_closure_audit` 口径下，对 `frontend-evidence-class-lifecycle` 的 open cluster 做一次 fresh closure reconciliation；只允许消费 current close-check / truth evidence，目标是在不伪造新 runtime 的前提下，判断该 cluster 是否仍应保留在 root truth 中。参考：`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/079-frontend-framework-only-closure-policy-baseline/spec.md`、`specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md`、`specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`、`specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md`、`specs/083-frontend-evidence-class-validator-surface-baseline/spec.md`、`specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`、`specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`、`specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`、`specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`、`specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`、`specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`、`specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md`、`specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`、`specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md`、`specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`、`specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md`、`specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md`、`specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md`、`specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md`、`specs/112-frontend-072-081-close-check-backfill-baseline/spec.md`、`specs/113-frontend-082-092-manifest-mirror-baseline/spec.md`

> 口径：`157` 不是新的 `frontend_evidence_class` runtime implementation，也不是把 `079/081/092/108-113` 提升为 capability delivery。它只处理 root truth reconciliation：若 `079-092` 与 `107-113` 的 fresh composite evidence 已足以证明当前 root `frontend-evidence-class-lifecycle` wording 过时，就移除该 open cluster；若 evidence 仍存在 material residual gap，则必须 fail-closed，而不是继续沿用“`083-090` 仍 formal/prospective、`091` 仍 implementation 中”的旧描述。

## 问题定义

`120` 曾将 `frontend-evidence-class-lifecycle` 标成 open capability cluster，并留下以下旧口径：

- `107-113` 已补部分 runtime / backfill
- `083-090` 仍 prospective / formal-only
- `091` 仍首批 implementation slice 进行中

当前仓库中的真实情况已经进一步演化：

- `079/081` 已冻结 framework-only policy split 与 future contract：formal / prospective carrier 不必逐项转成 runtime 才能参与 cluster close
- `091` 的 runtime cut 已完成并在 latest close-out 中被规范化；`107` 已将 readiness gate runtime 正式落地
- `092` 已明确当前 runtime reality 已覆盖 verify / validate / sync / status / close-check 五类 surface；它是 honesty-sync carrier，不是新增实现
- `108-113` 已将 legacy metadata、manifest mirror 与 close-check grammar drift 回填到当前门禁口径
- root `program-manifest.yaml` 仍保留 `frontend-evidence-class-lifecycle=capability_open`，且 summary 继续使用旧 wording，已经与 fresh composite evidence 不一致

因此，`157` 的职责是把 evidence-class cluster 的 root truth 收束为一条 capability closure reconciliation 问题：以 `079-092`、`107-113` 的 fresh close evidence 为依据，明确 policy carrier、runtime carrier、honesty/backfill carrier 之间的边界，并决定 root `open_clusters` 是否继续保留 `frontend-evidence-class-lifecycle`。

## 范围

- **覆盖**：
  - 冻结 `frontend-evidence-class-lifecycle` 的 closure universe 为 `079-092`、`107-113`
  - 对 `079-092`、`107-113` 执行 fresh close-check sweep，并记录 formal/prospective、runtime、honesty/backfill 三类 carrier 的分类
  - 将常驻对抗专家的评估固化为显式约束：不得把 `079/081/092/108-113` 当成 capability delivery proof，不得要求 `083-090` 逐项变成 runtime 才允许 cluster close
  - 回写 root `program-manifest.yaml`，移除已过时的 `frontend-evidence-class-lifecycle` open cluster
  - 执行 `program truth sync --execute --yes` 与 `program truth audit`，刷新 root truth
- **不覆盖**：
  - 不新增 `src/` / `tests/` runtime 实现
  - 不修改 `079-113` 的 formal scope 或历史结论
  - 不修改 `frontend-program-branch-rollout-plan.md`；该 advisory 汇总文档的对齐由后续 docs-only carrier 处理
  - 不顺带关闭 `agent-adapter-verified-host-ingress`、`project-meta-foundations`
  - 不把 `091/107` 单独写成整个 cluster 的 closure proof
  - 不伪造 `frontend_contract_observations` 已在仓库内被真实 consumer 项目回填

## 已锁定决策

- `frontend-evidence-class-lifecycle` 的 cluster close 只能基于 fresh machine-verifiable composite evidence，不接受旧 backlog wording 直接推断
- `079/081` 只提供 policy / prospective contract，`092` 只提供 honesty-sync，`108-113` 只提供 metadata / mirror / close-check honesty；它们均不属于 capability delivery proof
- `091/107` 提供 runtime surface 已落地的证据，但不足以单独关闭整个 cluster
- `083-090` 可继续保持 formal / prospective 身份；cluster close 的判断标准是 composite chain 是否已无 unresolved delivery gap，而不是要求每个 formal baseline 单独变成 runtime
- 本工单只消费以下 machine surfaces：
  - `python -m ai_sdlc workitem close-check --wi ...`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
  - `python -m ai_sdlc program truth sync --execute --yes`
  - `python -m ai_sdlc program truth audit`
- 若 `079-092`、`107-113` 任一 ref 在 current grammar 下无法形成 fresh close evidence，`157` 必须 fail-closed

## 用户场景与测试

### US-157-1 — Maintainer 需要 root truth 不再保留过时的 evidence-class open cluster

作为**框架维护者**，我希望 root truth 只保留真正未收口的 cluster，而不是继续把已经完成 reconciliation 的 `frontend-evidence-class-lifecycle` 维持为 open。

**优先级说明**：P0。只要该 cluster 仍挂在 root `open_clusters` 中，global truth 就会继续误报 evidence-class lifecycle 仍未闭环。

**独立测试**：完成 `157` 后，`program-manifest.yaml` 中不再存在 `frontend-evidence-class-lifecycle` 的 open cluster 条目。

**验收场景**：

1. **Given** `079-092`、`107-113` 已形成 fresh composite close evidence，**When** 我执行 `157`，**Then** root `open_clusters` 中不再保留 `frontend-evidence-class-lifecycle`
2. **Given** root truth 已刷新，**When** 我查看 bounded capability closure surface，**Then** 我不会再看到过时的 `frontend-evidence-class-lifecycle=capability_open`

### US-157-2 — Reviewer 需要 formal、runtime 与 honesty/backfill carrier 被诚实区分

作为**reviewer**，我希望 `079/081` 的 policy role、`083-090` 的 formal/prospective role、`091/107` 的 runtime role，以及 `092/108-113` 的 honesty/backfill role 被分层说明，这样不会把不同 truth layer 混成同一条未闭环理由。

**优先级说明**：P0。若继续混淆这些层次，root capability audit 就会重复暴露已经过时的 blocker。

**独立测试**：`157/spec.md`、`task-execution-log.md` 与 root truth 更新后，均明确说明 formal carrier 不等于 runtime debt、honesty/backfill 不等于 capability delivery。

**验收场景**：

1. **Given** 我检查 `157` formal docs，**When** 我查看锁定决策，**Then** 能看到 `079/081/092/108-113` 的非 delivery 边界
2. **Given** 我查看 root truth 与 `157` 的收口记录，**When** 我对照 `091/107`，**Then** 我不会把单个 runtime slice 误读为整个 cluster 的单点 closure proof

### US-157-3 — Operator 需要 `157` 的收口记录显式停留在 truth-only 边界

作为**operator**，我希望 `157` 在关闭 root evidence-class cluster 后，不再顺手改写人读 rollout 汇总，而是把“下一条 frontend 主线”的 advisory 对齐留给后续独立 carrier 处理。

**优先级说明**：P1。若在 truth-only carrier 中混入额外的人读排序调整，会破坏 close-check 对验证画像的约束。

**独立测试**：`157/spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md` 都明确把 `frontend-program-branch-rollout-plan.md` 排除在本批改动之外。

**验收场景**：

1. **Given** 我查看 `157` 的 formal docs，**When** 我关注 truth-only 边界，**Then** 会看到 rollout 汇总被显式排除在本批之外
2. **Given** root evidence-class cluster 已被移除，**When** 我继续做 frontend 排序决策，**Then** 我需要基于最新 root truth 或独立 planning carrier，而不是把 `157` 误解为已完成全部人读汇总同步

### 边界情况

- 即使 `079/081/092/108-113` close-check 通过，也不能把它们当成 capability delivery proof；它们只证明 policy / sync / backfill / honesty carrier 自身已闭环
- 即使 `091/107` 提供 runtime proof，也只能说明 runtime surface 已落地，不能单独支撑整个 cluster close
- `157` 不能因为关闭了 evidence-class cluster，就顺带宣称 `agent-adapter-verified-host-ingress` 或 `project-meta-foundations` 已关闭

## 需求

### 功能需求

- **FR-157-001**：系统必须把 `frontend-evidence-class-lifecycle` 的 closure reconciliation 作为独立 truth-only carrier 处理，而不是直接手改 manifest
- **FR-157-002**：系统必须将 cluster close evidence 的 closure universe 固定为 `079-092`、`107-113`
- **FR-157-003**：系统必须以 `079-092`、`107-113` 的 fresh close-check 作为 root reconciliation 的唯一 machine evidence
- **FR-157-004**：系统必须显式记录常驻对抗专家评估带来的四条约束：`079/081/092/108-113` 不得冒充 capability delivery、`091/107` 不得单点关闭 cluster、`083-090` 不需逐项转 runtime、`157` 不得扩成多 cluster 清理
- **FR-157-005**：根级 `capability_closure_audit` 对 `frontend-evidence-class-lifecycle` 的关闭必须通过移除 `open_clusters` 条目表达
- **FR-157-006**：系统必须在 `157` 的 formal close-out docs 中显式记录：`frontend-program-branch-rollout-plan.md` 不属于本批 truth-only 变更范围
- **FR-157-007**：`157` 必须在 root cluster removal 后刷新 `truth_snapshot`
- **FR-157-008**：若 close-check sweep 或 truth refresh 暴露 material residual blocker，`157` 必须 fail-closed

### 关键实体

- **Evidence-Class Close Sweep**：对 `079-092`、`107-113` 执行的 fresh close-check 证据汇总
- **Carrier Classification**：将 `079/081/083-090` 归类为 policy/formal/prospective evidence，将 `091/107` 归类为 runtime evidence，将 `092/108-113` 归类为 honesty/backfill evidence
- **Adversarial Guardrail Set**：常驻对抗专家对 `157` 给出的四条 fail-closed 约束
- **Open Cluster Removal**：把 `frontend-evidence-class-lifecycle` 从 root `open_clusters` 中移除的动作
- **Truth Refresh Snapshot**：在 cluster removal 后重新 materialize 的 root truth snapshot

## 成功标准

- **SC-157-001**：`079-092`、`107-113` 的 fresh close-check sweep 全部通过
- **SC-157-002**：`frontend-evidence-class-lifecycle` 从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除
- **SC-157-003**：`program truth sync --execute --yes` 后，root truth 保持 fresh，且 `program truth audit` 不再暴露 `frontend-evidence-class-lifecycle`
- **SC-157-004**：`157` 的 formal close-out docs 不再把 rollout 汇总同步误记为本批已完成动作，并显式保留 truth-only 边界
- **SC-157-005**：`157` 的收口语义诚实停留在 capability closure reconciliation，不伪造新的 runtime 实现

---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md"
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
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
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
  - "specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md"
  - "specs/112-frontend-072-081-close-check-backfill-baseline/spec.md"
  - "specs/113-frontend-082-092-manifest-mirror-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
