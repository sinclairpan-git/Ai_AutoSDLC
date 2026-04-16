# 功能规格：Frontend Program Automation Chain Closure Audit Reconciliation Baseline

**功能编号**：`155-frontend-program-automation-chain-closure-audit-reconciliation-baseline`
**创建日期**：2026-04-16
**状态**：已实现（truth-only closure carrier）
**输入**：承接 `119/120/131/132/133/134/135`，在非 release cluster 口径下，将 `frontend-program-automation-chain` 的 close-check / runtime closure 证据重新汇总为单一 capability closure carrier；目标是在不伪造新 runtime 的前提下，清理 root truth 中已过时的 open cluster 条目。参考：`specs/119-capability-closure-truth-baseline/spec.md`、`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/131-frontend-program-execute-remediation-materialization-runtime-closure-baseline/spec.md`、`specs/132-frontend-program-provider-patch-writeback-runtime-closure-baseline/spec.md`、`specs/133-frontend-program-registry-governance-persistence-runtime-closure-baseline/spec.md`、`specs/134-frontend-program-final-proof-publication-archive-runtime-closure-baseline/spec.md`、`specs/135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline/spec.md`

> 口径：`155` 不是再实现 program automation runtime，而是把 `019-064` 已经被 `131-135` 收束的 runtime closure 正式对齐到根级 `capability_closure_audit`。只有在 cluster 的 formal anchors 与 `131-135` latest close evidence 都可被 current close-check grammar 消费时，`155` 才允许把 `frontend-program-automation-chain` 从 root `open_clusters` 中移除。

## 问题定义

`120` 已将 `frontend-program-automation-chain` 明确拆成两段：

- `S3`：`019-040`
- `S4`：`041-064`

并分别派生为以下 runtime closure carriers：

- `131-frontend-program-execute-remediation-materialization-runtime-closure-baseline`
- `132-frontend-program-provider-patch-writeback-runtime-closure-baseline`
- `133-frontend-program-registry-governance-persistence-runtime-closure-baseline`
- `134-frontend-program-final-proof-publication-archive-runtime-closure-baseline`
- `135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline`

当前仓库中的真实情况已经不是“program automation 主线还没进入 runtime”，而是：

- `131-135` 已经把 execute/remediation/writeback/archive/cleanup 的关键 runtime 主线收束成 implementation carriers；
- root `capability_closure_audit` 仍继续把 `frontend-program-automation-chain` 保留为 open cluster；
- `131-135` 的历史 execution log 还没有全部升级到 current close-check grammar，导致 cluster-level close evidence 不能直接被当前门禁消费。

因此，`155` 的职责是将 `frontend-program-automation-chain` 收束为一条 capability closure reconciliation 问题：先完成 `131-135` latest batch normalization，再用 fresh close-check sweep 与 truth refresh 将这条 root cluster 从 `open_clusters` 中移除。

## 范围

- **覆盖**：
  - 冻结 `frontend-program-automation-chain` 的 capability closure 证据边界
  - 对 `131-135` 的 latest batch execution log 做 current close-check grammar normalization
  - 以 `019/025/032/041/050` 等 formal anchors 与 `131-135` 的 fresh close-check 作为 cluster close evidence
  - 回写根级 `program-manifest.yaml`，移除已过时的 `frontend-program-automation-chain` open cluster
  - 执行 `program truth sync --execute --yes` 与 `program truth audit`，刷新 root truth
- **不覆盖**：
  - 不新增 `frontend-program-automation-chain` 的 runtime 代码
  - 不重写 `131-135` 的 runtime scope
  - 不顺带关闭 `frontend-p1-experience-stability` 或其他 open clusters
  - 不创建第二份 capability closure ledger

## 已锁定决策

- `frontend-program-automation-chain` 的 cluster close 只能基于 fresh machine-verifiable evidence，不接受旧 backlog wording 直接推断；
- `155` 只消费已存在的 machine surfaces：
  - `workitem close-check`
  - `uv run ai-sdlc verify constraints`
  - `program truth sync`
  - `program truth audit`
- `131-135` 仍是 `120/T31-T35` 的 implementation carriers，不升级成新的 root capability；
- 对 non-release cluster，关闭的表达方式仍然是从 `open_clusters` 中移除，而不是新增 `closed` 字面值；
- 若 `131-135` 任一 latest batch 仍不满足 current close-check grammar，`155` 必须继续 fail-closed。

## 用户场景与测试

### US-155-1 — Maintainer 需要 root truth 不再重复暴露已闭环的 automation cluster

作为**框架维护者**，我希望 root truth 只保留真正未闭环的 cluster，而不是继续把 `frontend-program-automation-chain` 挂成过时 open 条目。

**优先级说明**：P0。只要这条旧 cluster 还在，global truth 就会继续误报 program automation 仍缺主链 runtime。

**独立测试**：完成 `155` 后，`program-manifest.yaml` 中不再存在 `frontend-program-automation-chain` 的 open cluster 条目。

**验收场景**：

1. **Given** `131-135` 与 formal anchors 已有 fresh close evidence，**When** 我执行 `155`，**Then** root `open_clusters` 中不再保留 `frontend-program-automation-chain`
2. **Given** root truth 已刷新，**When** 我查看 bounded capability closure surface，**Then** 我不会再看到过时的 `frontend-program-automation-chain=capability_open`

### US-155-2 — Reviewer 需要 `131-135` 的 latest batch 能被当前门禁直接消费

作为**reviewer**，我希望 `131-135` 的 latest batch 已升级到 current close-check grammar，这样 program automation cluster close 不再依赖人肉解释。

**优先级说明**：P0。没有 latest close evidence normalization，cluster close 仍然不是 machine-verifiable。

**独立测试**：`workitem close-check --wi specs/131-...` 到 `--wi specs/135-...` 在 clean tree + fresh truth 下均通过。

**验收场景**：

1. **Given** `131-135` 使用了旧 execution-log 结构，**When** 我执行 `155`，**Then** 它们的 latest batch 已补齐 current close-check grammar 所需字段
2. **Given** current close-check grammar 生效，**When** 我对 `131-135` 重跑 close-check，**Then** 它们可直接作为 cluster close evidence 被消费

### US-155-3 — Operator 需要把注意力从 program automation 旧缺口转移到真实剩余 cluster

作为**operator**，我希望 root truth 不再把已经闭环的 program automation cluster 继续显示为 open，这样我能继续追真正剩余的 cluster。

**优先级说明**：P1。capability truth 的价值在于减少噪音，聚焦剩余问题。

**独立测试**：`program truth audit` 与 bounded readiness summary 不再暴露 `frontend-program-automation-chain`。

**验收场景**：

1. **Given** 我查看新的 root truth，**When** 我关注 open clusters，**Then** `frontend-program-automation-chain` 已被移除
2. **Given** 我继续推进后续 cluster，**When** 我依赖 root truth 选题，**Then** 不会再被 program automation 旧口径误导

### 边界情况

- `131-135` 的 runtime 已存在，但若 latest batch 未通过 current close-check grammar，仍不得删除 root cluster
- formal anchors 只提供 segment 边界，不替代 implementation carriers
- `155` 不能因为 program automation cluster 关闭，就顺带宣称 `frontend-p1-experience-stability` 已关闭

## 需求

### 功能需求

- **FR-155-001**：系统必须把 `frontend-program-automation-chain` 的 closure reconciliation 作为独立 truth-only carrier 处理，而不是直接手改 manifest
- **FR-155-002**：系统必须使用 formal anchors 与 `131-135` 的 fresh close-check evidence 作为 cluster close 的唯一依据
- **FR-155-003**：系统必须先将 `131-135` 的 latest batch 升级到当前 close-check grammar，再允许它们参与 cluster close evidence
- **FR-155-004**：根级 `capability_closure_audit` 对 non-release cluster 的关闭必须通过移除 `open_clusters` 条目表达
- **FR-155-005**：`155` 必须在移除 root cluster 后刷新 `truth_snapshot`
- **FR-155-006**：若 close-check sweep 发现关键 ref 仍未收口，`155` 必须保持 fail-closed

### 关键实体

- **Automation Chain Close Sweep**：对 `frontend-program-automation-chain` 引用范围执行的 fresh close-check 证据汇总
- **Latest Batch Normalization**：将 `131-135` 旧 execution-log 追加为 current close-check grammar 可消费的 latest batch
- **Open Cluster Removal**：把 `frontend-program-automation-chain` 从 root `open_clusters` 中移除的动作
- **Truth Refresh Snapshot**：在 cluster removal 后重新 materialize 的 root truth snapshot

## 成功标准

- **SC-155-001**：`131-135` 的 latest batch 已被 current close-check grammar 消费
- **SC-155-002**：`frontend-program-automation-chain` 从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除
- **SC-155-003**：`program truth sync --execute --yes` 后，root truth 保持 fresh，且 `program truth audit` 不再暴露 `frontend-program-automation-chain`
- **SC-155-004**：`155` 的收口语义诚实停留在 capability closure reconciliation，不伪造新的 runtime 实现

---
related_doc:
  - "specs/119-capability-closure-truth-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/131-frontend-program-execute-remediation-materialization-runtime-closure-baseline/spec.md"
  - "specs/132-frontend-program-provider-patch-writeback-runtime-closure-baseline/spec.md"
  - "specs/133-frontend-program-registry-governance-persistence-runtime-closure-baseline/spec.md"
  - "specs/134-frontend-program-final-proof-publication-archive-runtime-closure-baseline/spec.md"
  - "specs/135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
