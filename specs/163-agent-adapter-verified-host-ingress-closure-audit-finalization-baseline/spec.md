# 功能规格：Agent Adapter Verified Host Ingress Closure Audit Finalization Baseline

**功能编号**：`163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline`
**创建日期**：2026-04-18
**状态**：草稿
**输入**：`specs/121-agent-adapter-verified-host-ingress-truth-baseline/spec.md`、`specs/122-agent-adapter-verified-host-ingress-runtime-baseline/spec.md`、`specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md`、`specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline/spec.md`、`specs/160-agent-adapter-canonical-consumption-release-gate-baseline/spec.md`、`specs/161-agent-adapter-dry-run-program-truth-parity-baseline/spec.md`、`specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/spec.md`、`program-manifest.yaml`

> 口径：`163` 不是继续实现 adapter runtime，而是把 `121/122/158/159/160/161/162` 已经产生的 fresh machine-verifiable evidence 正式收束到 root `capability_closure_audit`。只有当当前 close-check grammar、truth sync 与 release capability ledger 一致证明 `agent-adapter-verified-host-ingress` 已闭合时，`163` 才允许从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除该 cluster。

## 问题定义

当前仓库的 program truth 已收敛到单一 blocker：

- `capability_closure_audit:partial`

fresh `program truth audit` 显示：

- `frontend-mainline-delivery` 已是 `closure=closed / audit=ready`
- `agent-adapter-verified-host-ingress` 仍是 `closure=partial / audit=blocked`

但 `partial` 已不再代表 runtime 缺失，而只代表 root audit 仍保留一条过时 open cluster。与此同时，仓库已经具备以下新事实：

1. `adapter status --json` 与 `adapter exec -- ...` 已能区分 verified ingress、canonical consumption proof 与 child-process proof carrier。
2. `159/160/161/162` 已将 canonical proof 字段、release/program gate、dry-run truth parity 与正式 proof carrier 命令收束为 machine-verifiable surface。
3. `162` 的 close-check 已通过，说明 canonical proof carrier 本身已完成 close-ready 收口。

因此，当前缺口不再是“还没有 capability”，而是“root closure audit 尚未消费最新 close evidence”。若继续保留旧 cluster 摘要，program truth 会持续误报 agent-adapter release capability 仍处于部分闭合状态；若未经 fresh evidence sweep 就直接删除 open cluster，则会把 truth-only reconciliation 变成手工消音。

## 范围

- **覆盖**：
  - 冻结 `agent-adapter-verified-host-ingress` 的 cluster close evidence universe
  - 重新审计 `121/122/158/159/160/161/162` 是否都满足 current close-check grammar
  - 核对 `release_capabilities[].spec_refs / required_evidence / capability_closure_audit` 是否仍与当前事实一致
  - 在证据完备时，从 root `open_clusters` 中移除 `agent-adapter-verified-host-ingress`
  - 刷新 `program truth sync --execute --yes` 与 `program truth audit`
- **不覆盖**：
  - 不新增 adapter runtime、proof carrier 或 release gate 逻辑
  - 不伪造新的 host ingress / canonical consumption evidence
  - 不顺带关闭 `project-meta-foundations` 或其他 cluster
  - 不创建第二份 closure ledger

## 已锁定决策

- `163` 是 root closure audit finalization carrier，不是新的 release runtime carrier；
- cluster close 的唯一依据是 fresh machine-verifiable evidence，不接受“162 已完成所以应该可以关了”的人工推断；
- release capability 关闭后，root audit 的表达方式仍然是从 `open_clusters` 中移除该条目，而不是写入新的 `closed` cluster 行；
- 若 fresh close sweep 中任一关键 work item 不满足当前 grammar，`163` 必须继续 fail-closed；
- 若 capability ledger 仍缺 `161/162` 等当前实际 carrier 的 provenance，必须在同一真值面内诚实补齐或明确维持现状的理由。

## 用户场景与测试

### US-163-1 — Maintainer 需要 root truth 只暴露真实未闭合能力

作为**框架维护者**，我希望在 agent-adapter capability 真实闭合后，root `capability_closure_audit` 不再继续保留这条过时 open cluster。

**优先级说明**：P0。当前 program truth 的唯一 blocker 就是这条 stale cluster。

**独立测试**：完成 `163` 后，`program-manifest.yaml` 中不再存在 `agent-adapter-verified-host-ingress` 的 open cluster 条目。

**验收场景**：

1. **Given** `121/122/158/159/160/161/162` 都已有 fresh close evidence，**When** 我执行 `163`，**Then** root `open_clusters` 中移除 `agent-adapter-verified-host-ingress`
2. **Given** root truth 已刷新，**When** 我运行 `program truth audit`，**Then** 不再出现 `capability_closure_audit:partial`

### US-163-2 — Reviewer 需要 cluster close 只消费 current grammar 可读的证据

作为**reviewer**，我希望 cluster removal 之前先完成一次 fresh close sweep，而不是靠历史完成印象直接关账。

**优先级说明**：P0。root audit finalization 只能建立在 current close-check grammar 可消费的 evidence 上。

**独立测试**：`workitem close-check` 对 `121/122/158/159/160/161/162` 的当前状态可被 `163` 直接引用。

**验收场景**：

1. **Given** 任一关键 work item 的 latest batch 不满足 current grammar，**When** 我执行 `163`，**Then** cluster 继续保留，truth 不被伪关闭
2. **Given** 关键 work item 全部通过，**When** 我执行 `163`，**Then** manifest 改写与 truth refresh 在同一批次完成

### US-163-3 — Operator 需要 release capability truth 与 dry-run 结论一致

作为**operator**，我希望 root truth、release capability state 与 `run --dry-run` 的 close 结论互相一致，而不是一个地方 ready、另一个地方还挂着旧 blocker。

**优先级说明**：P1。program truth 的价值在于让启动入口与 release gate 保持同一套现实。

**独立测试**：完成 `163` 后，`program truth audit` 将 `agent-adapter-verified-host-ingress` 收敛到 `audit=ready`，且 `run --dry-run` 不再因 `capability_closure_audit:partial` 保持 open gate。

**验收场景**：

1. **Given** cluster 已从 root audit 移除，**When** 我运行 `program truth audit`，**Then** release capability 不再被 closure audit 阻断
2. **Given** close gate 重新计算，**When** 我运行 `python -m ai_sdlc run --dry-run`，**Then** 不再看到由该 cluster 导致的 open gates

### 边界情况

- `162` 已 close-ready 不等于 root audit 必然可关；仍需 fresh consume 当前 close-check 结果
- 若 manifest provenance 需要补充 `161/162` 才能诚实描述 capability lineage，该补充必须与 cluster removal 同步决议
- `163` 不能通过修改 summary wording 来假装完成；要么移除 open cluster，要么保留并明确 blocker

## 需求

### 功能需求

- **FR-163-001**：系统必须先冻结 `agent-adapter-verified-host-ingress` 的 cluster close evidence universe，再执行任何 root audit 改写
- **FR-163-002**：系统必须使用 fresh `workitem close-check` / `program truth audit` / `program truth sync` 作为 cluster close 的唯一 machine-verifiable surface
- **FR-163-003**：若 `121/122/158/159/160/161/162` 中任一关键 work item 不能被当前 grammar 消费，系统必须保持 `partial`
- **FR-163-004**：当且仅当 cluster close evidence 完整时，系统必须从 `program-manifest.yaml > capability_closure_audit.open_clusters` 中移除 `agent-adapter-verified-host-ingress`
- **FR-163-005**：manifest writeback 后，系统必须立即刷新 truth snapshot，并验证 release capability 不再暴露 `capability_closure_audit:partial`
- **FR-163-006**：系统不得借 `163` 发明新的 runtime claims；所有 ready 结论都必须回指现有 verified evidence

### 关键实体

- **Agent Adapter Close Sweep**：对 `121/122/158/159/160/161/162` 的 fresh close-check 证据汇总
- **Root Cluster Removal**：从 `capability_closure_audit.open_clusters` 中移除 `agent-adapter-verified-host-ingress` 的真值动作
- **Capability Provenance Ledger**：`release_capabilities[].spec_refs / required_evidence / source_refs` 的单一 provenance 面
- **Truth Refresh Snapshot**：在 root audit 改写后重新 materialize 的 truth snapshot

## 成功标准

- **SC-163-001**：`program-manifest.yaml` 中不再保留 `agent-adapter-verified-host-ingress` 的 open cluster 条目
- **SC-163-002**：`program truth audit` 对 `agent-adapter-verified-host-ingress` 输出 `closure=closed / audit=ready`
- **SC-163-003**：`program truth audit` 与 `run --dry-run` 不再暴露 `capability_closure_audit:partial`
- **SC-163-004**：`163` 的完成语义停留在 closure audit finalization，不伪装为新的 adapter runtime work

---
related_doc:
  - "specs/121-agent-adapter-verified-host-ingress-truth-baseline/spec.md"
  - "specs/122-agent-adapter-verified-host-ingress-runtime-baseline/spec.md"
  - "specs/158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline/spec.md"
  - "specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline/spec.md"
  - "specs/160-agent-adapter-canonical-consumption-release-gate-baseline/spec.md"
  - "specs/161-agent-adapter-dry-run-program-truth-parity-baseline/spec.md"
  - "specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/spec.md"
  - "program-manifest.yaml"
frontend_evidence_class: "framework_capability"
