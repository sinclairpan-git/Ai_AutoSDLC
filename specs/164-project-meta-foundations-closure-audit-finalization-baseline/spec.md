---
related_doc:
  - "specs/005-harness-grade-telemetry-observer-v1/spec.md"
  - "specs/006-provenance-trace-phase-1/spec.md"
  - "specs/007-branch-lifecycle-truth-guard/spec.md"
  - "specs/008-direct-formal-workitem-entry/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/138-harness-telemetry-provenance-runtime-closure-baseline/spec.md"
  - "specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline/spec.md"
  - "program-manifest.yaml"
frontend_evidence_class: "framework_capability"
---
# 功能规格：Project Meta Foundations Closure Audit Finalization Baseline

**功能编号**：`164-project-meta-foundations-closure-audit-finalization-baseline`  
**创建日期**：2026-04-18  
**状态**：进行中  
**输入**：`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/138-harness-telemetry-provenance-runtime-closure-baseline/spec.md`、`specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline/spec.md`、`program-manifest.yaml`

> 口径：`164` 不是继续实现 telemetry、provenance、branch lifecycle 或 direct-formal runtime，而是把 `138/139` 已经形成的 fresh machine-verifiable evidence 正式收束到 root `capability_closure_audit`。只有当 current close-check grammar、truth sync 与 manifest truth 一致证明 `005-008` 已不再停留在 `formal_only` 时，`164` 才允许移除 `project-meta-foundations` 这条过时 open cluster。

## 问题定义

当前仓库的 capability truth 已收敛到：

- `frontend-mainline-delivery`：`closure=closed / audit=ready`
- `agent-adapter-verified-host-ingress`：`closure=closed / audit=ready`

`program truth sync --dry-run` 的 recompute 也已经显示 release capability ledger 是 ready，但 root `program-manifest.yaml > capability_closure_audit.open_clusters` 仍保留：

- `project-meta-foundations`
- `closure_state=formal_only`
- `summary=005-008 仍是 formal baseline；仓库尚未提供对应 runtime / guard / surface 的实现闭环`

这条 cluster summary 已与仓库当前事实不一致，因为：

1. `138` 已把 `005/006` 的 telemetry/provenance runtime 收束为 formal implementation carrier。
2. `139` 已把 `007/008` 的 branch lifecycle/direct-formal runtime 收束为 formal implementation carrier。
3. 对 `138/139` 的 fresh `workitem close-check` 复跑表明，当前剩余阻断集中在 latest batch grammar、stale truth snapshot 与 git close-out markers，而不是 runtime 本身缺失。

因此，当前缺口不再是“005-008 还没有实现闭环”，而是“root closure audit 仍在消费过时叙述”。如果不做 finalization，program truth 会继续保守地把 project-meta tranche 误报为 `formal_only`；如果未经 fresh evidence sweep 直接删 cluster，又会把 truth-only reconciliation 退化成人工消音。

## 范围

- **覆盖**：
  - 冻结 `project-meta-foundations` 的 close evidence universe
  - 复核 `138/139` 是否满足 current close-check grammar，并把 latest batch 归档补齐到当前规范
  - 核对 `120` 与 `005-008` 在 root audit 中的 provenance 边界，确认它们作为 historical source 而不是新的 runtime blocker
  - 在证据完备时，从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除 `project-meta-foundations`
  - 刷新 truth snapshot，并验证 `program truth audit` / `run --dry-run` 不再把该 cluster 当作 open gate
- **不覆盖**：
  - 不新增 telemetry、provenance、branch lifecycle 或 direct-formal production 代码
  - 不重写 `005-008` 的历史 formal baseline 文本
  - 不创建第二份 capability closure ledger
  - 不顺带改写 `frontend-mainline-delivery`、`agent-adapter-verified-host-ingress` 等已闭合 capability 的 truth

## 已锁定决策

- `164` 是 root closure audit finalization carrier，不是新的 runtime carrier；
- cluster close 的唯一依据是 fresh machine-verifiable evidence，不接受“138/139 已经看起来完成了”的人工推断；
- `120` 在本 work item 中只作为 tranche provenance 来源，不再被重新解释为 runtime 事实面；
- 对 `138/139` 的处理仅限 latest batch grammar normalization，不伪造历史 clean tree，也不篡改其原始实现批次；
- root audit 完成后的表达方式仍然是移除 `open_clusters` 条目，而不是新增一条“closed cluster”记录。

## 用户场景与测试

### US-164-1 — Maintainer 需要 root truth 只暴露真实未闭合能力

作为**框架维护者**，我希望当 `005-008` 已经由 `138/139` 提供 fresh implementation evidence 后，root `capability_closure_audit` 不再继续保留 `project-meta-foundations` 这条过时 open cluster。

**优先级说明**：P0。当前 cluster summary 与仓库事实冲突，会持续误导后续 closure judgment。

**独立测试**：完成 `164` 后，`program-manifest.yaml` 中不再存在 `project-meta-foundations` 条目。

**验收场景**：

1. **Given** `138/139` 都能提供 current grammar 可消费的 close evidence，**When** 我执行 `164`，**Then** root `open_clusters` 中移除 `project-meta-foundations`
2. **Given** root truth 已刷新，**When** 我运行 `program truth audit`，**Then** 不再出现由该 cluster 导致的 `formal_only` 误报

### US-164-2 — Reviewer 需要 cluster removal 只消费 current grammar 可读的证据

作为**reviewer**，我希望 `project-meta-foundations` 的关闭建立在 fresh close sweep 上，而不是只靠旧结论或口头记忆。

**优先级说明**：P0。root audit finalization 必须与当前 close-check grammar 对齐。

**独立测试**：`python -m ai_sdlc workitem close-check --wi specs/138-harness-telemetry-provenance-runtime-closure-baseline --json` 与对 `139` 的同类命令，能被 `164` 直接引用为 close decision 输入。

**验收场景**：

1. **Given** 任一关键 carrier 的 latest batch 仍缺 current grammar 字段，**When** 我执行 `164`，**Then** cluster 继续保留，truth 维持 fail-closed
2. **Given** grammar 与 truth snapshot 都已 fresh，**When** 我执行 `164`，**Then** manifest 改写与 truth refresh 在同一批次完成

### US-164-3 — Operator 需要启动入口与 root truth 结论一致

作为**operator**，我希望 `program truth audit` 与 `run --dry-run` 不再因为 `project-meta-foundations` 的过时描述给出额外噪音。

**优先级说明**：P1。启动入口的 close-stage 诊断应该反映真实剩余 gate，而不是历史 stale cluster。

**独立测试**：完成 `164` 后，fresh `program truth audit` 与 `python -m ai_sdlc run --dry-run` 都不再把 `project-meta-foundations` 视为 open gate。

**验收场景**：

1. **Given** root cluster 已移除，**When** 我运行 `program truth audit`，**Then** root closure audit 不再暴露 `project-meta-foundations`
2. **Given** dry-run 重新计算 close-stage，**When** 我运行 `python -m ai_sdlc run --dry-run`，**Then** 如果仍有 open gate，执行日志必须明确其与本 cluster 无关

### 边界情况

- `138/139` 的 runtime closure 已成立，不等于它们的 latest batch grammar 自动满足 current close-check；仍需 fresh normalization
- `program truth sync --dry-run` ready 不等于 persisted snapshot 已 fresh；在 `sync --execute --yes` 之前，`program truth audit` 仍可能报告 stale
- `164` 不能通过改写 cluster summary wording 来“软关闭”问题；要么移除 cluster，要么明确保留 blocker
- 若 `run --dry-run` 最终仍在 close-stage `RETRY`，必须区分这是 `164` 自身尚未 close-ready，还是存在其他无关 gate

## 需求

### 功能需求

- **FR-164-001**：系统必须先冻结 `project-meta-foundations` 的 close evidence universe，再执行任何 root audit 改写
- **FR-164-002**：系统必须使用 fresh `workitem close-check`、`program truth sync` 与 `program truth audit` 作为 cluster close 的唯一 machine-verifiable surface
- **FR-164-003**：若 `138/139` 任一 carrier 仍不能被 current grammar 消费，系统必须保持 fail-closed
- **FR-164-004**：当且仅当 close evidence 完整时，系统必须从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除 `project-meta-foundations`
- **FR-164-005**：manifest writeback 后，系统必须立即刷新 truth snapshot，并验证 root audit 不再暴露该 cluster
- **FR-164-006**：系统不得借 `164` 发明新的 runtime claims；所有 ready 结论都必须回指 `138/139` 与现有 machine-verifiable evidence

### 关键实体

- **Project Meta Close Sweep**：对 `138/139` latest batch grammar、fresh close-check 与 truth blocker 的复核结果
- **Historical Carrier Normalization**：仅为让 current close-check 消费 `138/139` latest batch 所做的 execution-log grammar 补齐
- **Root Cluster Removal**：从 `capability_closure_audit.open_clusters` 中移除 `project-meta-foundations` 的真值动作
- **Truth Refresh Snapshot**：在 root audit 改写后重新 materialize 的 persisted program truth snapshot

## 成功标准

- **SC-164-001**：`program-manifest.yaml` 中不再保留 `project-meta-foundations` 的 open cluster 条目
- **SC-164-002**：`python -m ai_sdlc program truth audit` 不再把 `project-meta-foundations` 视为当前 open cluster
- **SC-164-003**：`138/139` 的 latest batch 可被 current close-check grammar 消费，且阻断原因不再包含“缺统一验证命令/代码审查/任务计划同步字段”
- **SC-164-004**：`164` 的完成语义停留在 closure audit finalization，不伪装为新的 telemetry/branch runtime 实现
