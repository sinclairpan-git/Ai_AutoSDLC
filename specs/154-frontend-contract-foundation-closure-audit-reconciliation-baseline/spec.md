# 功能规格：Frontend Contract Foundation Closure Audit Reconciliation Baseline

**功能编号**：`154-frontend-contract-foundation-closure-audit-reconciliation-baseline`
**创建日期**：2026-04-16
**状态**：已实现（truth-only closure carrier）
**输入**：承接 `119/120/127/128`，在非 release cluster 口径下，将 `frontend-contract-foundation` 的 close-check / runtime closure 证据重新汇总为单一 capability closure carrier；目标是在不伪造新 runtime 的前提下，移除 root truth 中已过时的 open cluster 条目。参考：`specs/119-capability-closure-truth-baseline/spec.md`、`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/127-frontend-contract-observation-producer-runtime-closure-baseline/spec.md`、`specs/128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline/spec.md`

> 口径：`154` 不是新的 runtime tranche，也不是手工“把 manifest 改绿”。它只做一件事：把 `frontend-contract-foundation` 这条 cluster 的最新 machine-verifiable close evidence 重新对齐到根级 `capability_closure_audit`。只有在 `009-018`、`065`、`077-078` 与其现有 runtime carriers 的 close-check sweep 已经成立时，`154` 才允许把该 cluster 从 `open_clusters` 中移除。

## 问题定义

`119` 已把 root-level capability closure truth 正式定义在 `program-manifest.yaml > capability_closure_audit.open_clusters`，`120` 又把 `frontend-contract-foundation` 展开成 `T21/T22` 两条 tranche，并分别派生为：

- `127-frontend-contract-observation-producer-runtime-closure-baseline`
- `128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`

此后，`127/128` 以及上游 `009-018`、`065`、`077-078` 的 formal/runtime truth 已基本落成；但 root truth 仍继续把 `frontend-contract-foundation` 保留为 open cluster。当前的真实缺口不再是“scanner / attachment / gate 主链还没做”，而是：

- root `capability_closure_audit` 仍停留在旧的 `partial` 口径；
- `127/128` 的历史 execution log 没有完全升级到当前 `close-check` grammar，导致 cluster close evidence 不能直接被最新门禁消费；
- operator 继续会在 bounded readiness surface 中看到一个已经过时的 open cluster，误以为 `frontend-contract-foundation` 仍缺核心 runtime。

因此，`154` 的职责是把 `frontend-contract-foundation` 当成一条 capability closure reconciliation 问题来处理：先完成该 cluster 的 close-check sweep 与 latest batch normalization，再用 fresh truth refresh 正式移除过时的 root open cluster 条目。

## 范围

- **覆盖**：
  - 冻结 `frontend-contract-foundation` 的 capability closure 证据边界
  - 对 `127/128` 的 latest batch execution log 做 current close-check grammar normalization
  - 以 `009-018`、`065`、`077-078` 与 `127/128` 的 fresh close-check 作为 `S2` closure evidence
  - 回写根级 `program-manifest.yaml`，移除已过时的 `frontend-contract-foundation` open cluster
  - 执行 `program truth sync --execute --yes` 与 `program truth audit`，刷新 root truth
- **不覆盖**：
  - 不新增 `frontend-contract-foundation` 的 runtime 代码
  - 不扩展 `127/128` 的行为边界
  - 不创建新的 capability taxonomy、第二份 root audit，或平行 cluster ledger
  - 不顺带关闭 `frontend-program-automation-chain`、`project-meta-foundations` 或其他 open clusters

## 已锁定决策

- `frontend-contract-foundation` 的 cluster close 只能基于 fresh machine-verifiable evidence，不接受人工“已经差不多完成”的口头判断；
- `154` 只能消费当前已存在的 evidence surface：
  - `workitem close-check`
  - `uv run ai-sdlc verify constraints`
  - `program truth sync`
  - `program truth audit`
- `154` 不把 `127/128` 重新定义成新的父能力；它们仍只是 `120/T21/T22` 的 implementation carriers；
- 对 non-release cluster，`closed` 的表达方式不是把 cluster 改成另一种 open 状态，而是将其从 `capability_closure_audit.open_clusters` 中移除；
- 若 close-check sweep 仍发现未收口 work item，`154` 必须继续 fail-closed，而不是提前删 root cluster。

## 用户场景与测试

### US-154-1 — Maintainer 需要 root truth 只保留真实 open cluster

作为**框架维护者**，我希望根级 open cluster 只反映仍未闭环的能力，而不是继续挂着已经通过 close-check sweep 的旧条目。

**优先级说明**：P0。只要 root truth 保留过时 open cluster，全局真值就仍然会误报 capability 缺口。

**独立测试**：完成 `154` 后，`program-manifest.yaml` 中不再存在 `frontend-contract-foundation` 的 open cluster 条目，且 `program truth audit` 仍保持 fresh。

**验收场景**：

1. **Given** `127/128` 与 `009-018/065/077-078` 已具备 fresh close evidence，**When** 我执行 `154`，**Then** root `open_clusters` 中不再保留 `frontend-contract-foundation`
2. **Given** root truth 已刷新，**When** 我查看 bounded capability closure surface，**Then** 我不会再看到过时的 `frontend-contract-foundation=partial`

### US-154-2 — Reviewer 需要 capability close 证据能被当前 close-check grammar 消费

作为**reviewer**，我希望 `127/128` 的 latest batch 已经升级到当前 close-check grammar，这样它们才能成为 `frontend-contract-foundation` cluster close 的正式证据。

**优先级说明**：P0。若 latest batch 仍使用旧 execution-log 结构，cluster close 只是人肉判断，不是 machine-verifiable 证据。

**独立测试**：`workitem close-check --wi specs/127-...` 与 `--wi specs/128-...` 在 clean tree + fresh truth 下均通过。

**验收场景**：

1. **Given** `127/128` 曾使用旧 execution-log 结构，**When** 我执行 `154`，**Then** 它们的 latest batch 已补齐 `统一验证命令`、`代码审查`、`任务/计划同步状态`、verification profile 与 git close-out markers
2. **Given** current close-check grammar 生效，**When** 我对 `127/128` 重跑 close-check，**Then** 它们可被直接作为 cluster close evidence 消费

### US-154-3 — Operator 需要区分“过时 root summary”与“真实 capability 缺口”

作为**operator**，我希望 root truth 不再把已经闭环的 contract foundation 继续显示为 open，这样我能把注意力放到真正还没收口的 cluster。

**优先级说明**：P1。global truth 的价值就在于帮助 operator 把注意力聚焦到真实剩余问题。

**独立测试**：`program truth audit` 与 bounded readiness summary 不再重复暴露 `frontend-contract-foundation`。

**验收场景**：

1. **Given** 我查看新的 root truth，**When** 我关注剩余 open clusters，**Then** `frontend-contract-foundation` 已从列表中移除
2. **Given** 我继续推进下一条主线，**When** 我使用 root truth 选题，**Then** 不会再被 `frontend-contract-foundation` 误导

### 边界情况

- `127/128` 的 runtime 已存在，但若 latest batch 没有 current close-check evidence，仍不得删除 root cluster
- 某些上游 formal specs 可能没有新增 runtime；只要它们的 latest close-check 已通过，仍可作为 cluster close 证据的一部分
- `154` 不能因为 `frontend-contract-foundation` 关闭，就顺带宣称 `frontend-program-automation-chain` 也已关闭

## 需求

### 功能需求

- **FR-154-001**：系统必须把 `frontend-contract-foundation` 的 closure reconciliation 作为独立 truth-only carrier 处理，而不是直接手工改 manifest
- **FR-154-002**：系统必须使用 `009-018`、`065`、`077-078` 与 `127/128` 的 fresh close-check evidence 作为 `frontend-contract-foundation` cluster close 的唯一依据
- **FR-154-003**：系统必须先将 `127/128` 的 latest batch 升级到当前 close-check grammar，再允许它们参与 cluster close evidence
- **FR-154-004**：根级 `capability_closure_audit` 对 non-release cluster 的“关闭”必须通过移除 `open_clusters` 条目表达，不得新增伪状态
- **FR-154-005**：`154` 必须在移除 root cluster 后刷新 `truth_snapshot`，避免 manifest authoring 已更新但 snapshot 仍 stale
- **FR-154-006**：若 close-check sweep 发现 `frontend-contract-foundation` 任一关键 ref 仍未收口，`154` 必须保持 fail-closed

### 关键实体

- **S2 Closure Evidence Sweep**：对 `frontend-contract-foundation` 引用范围执行的 fresh close-check 证据汇总
- **Latest Batch Normalization**：将旧 execution-log 追加为当前 close-check grammar 可消费的 latest batch
- **Open Cluster Removal**：把已闭环 cluster 从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除的动作
- **Truth Refresh Snapshot**：在 cluster removal 后重新 materialize 的 root truth snapshot

## 成功标准

- **SC-154-001**：`127/128` 的 latest batch 已被 current close-check grammar 消费
- **SC-154-002**：`frontend-contract-foundation` 从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除
- **SC-154-003**：`program truth sync --execute --yes` 后，root truth 保持 fresh，且 `program truth audit` 不再暴露 `frontend-contract-foundation`
- **SC-154-004**：`154` 的收口语义诚实停留在 capability closure reconciliation，不伪造新的 runtime 实现

---
related_doc:
  - "specs/119-capability-closure-truth-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/127-frontend-contract-observation-producer-runtime-closure-baseline/spec.md"
  - "specs/128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
