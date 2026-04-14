# 功能规格：Frontend Mainline Delivery Close-Check Closure Baseline

**功能编号**：`142-frontend-mainline-delivery-close-check-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 起草中（待两轮对抗评审）
**输入**：[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../098-frontend-mainline-posture-detector-baseline/spec.md`](../098-frontend-mainline-posture-detector-baseline/spec.md)、[`../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`](../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)、[`../102-frontend-mainline-browser-quality-gate-baseline/spec.md`](../102-frontend-mainline-browser-quality-gate-baseline/spec.md)、[`../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`](../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md)、[`../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`](../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md)、[`../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`](../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md)、[`../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md`](../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md)、[`../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md`](../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md)、[`../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md`](../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md)、[`../126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md`](../126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md)、[`../140-program-truth-ledger-release-audit-baseline/spec.md`](../140-program-truth-ledger-release-audit-baseline/spec.md)、[`../141-program-manifest-root-census-backfill-baseline/spec.md`](../141-program-manifest-root-census-backfill-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)

> 口径：`141` 已经清掉 root census 噪音，`142` 因而可以专注处理 `frontend-mainline-delivery` 的真实 blocker。这里的 blocker universe 不能靠本 spec 手写冻结，必须始终以“执行时重新获取的最新 `program truth audit` + `program-manifest.yaml` 中 `required_evidence.close_check_refs`”为唯一入口。`142` 的职责是把这批 blocker 当成单一 release capability closure 问题来处理，而不是再新增一层“解释性文档”或把 formal wording 当成完成证明。

## 问题定义

在 `141` 完成后，根级 truth ledger 已从 `migration_pending` 收敛到纯 `blocked`。按当前基线观测，`frontend-mainline-delivery` 的阻断项为：

- `capability_closure_audit:capability_open`
- `close_check:specs/095-frontend-mainline-product-delivery-baseline`
- `close_check:specs/096-frontend-mainline-host-runtime-manager-baseline`
- `close_check:specs/098-frontend-mainline-posture-detector-baseline`
- `close_check:specs/099-frontend-mainline-delivery-registry-resolver-baseline`
- `close_check:specs/100-frontend-mainline-action-plan-binding-baseline`
- `close_check:specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline`
- `close_check:specs/102-frontend-mainline-browser-quality-gate-baseline`
- `close_check:specs/103-frontend-mainline-browser-gate-probe-runtime-baseline`
- `close_check:specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline`
- `close_check:specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`
- `close_check:specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline`
- `close_check:specs/124-frontend-mainline-delivery-materialization-runtime-baseline`
- `close_check:specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline`
- `close_check:specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`

这说明现在的发布阻断已经很纯粹：

- 不再是“历史 spec 未纳管”
- 不再是“宿主 ingress 证据未识别”
- 不再是“状态面没有 program-level truth”
- 而是 `frontend-mainline-delivery` 这条能力链本身还没有通过 close-check / closure audit

上述列表只是 `142` 启动时的基线观测，不是静态真值。`142` 必须在每个执行批次开始前重新拉取最新 truth audit，并把最新 blocker surface 与既有 `required_evidence.close_check_refs` 对齐。然后再把对应 spec blocker 作为一个 capability closure tranche 处理：按能力链重新分组、锁定依赖顺序和最小交付闭环，再进入逐批实现，而不是对每个 spec 独立零散修补。

## 范围

- **覆盖**：
  - 冻结 `frontend-mainline-delivery` blocker closure 的统一口径
  - 以 capability 为中心重组 `095/096/098/099/100/101/102/103/104/105/123/124/125/126`
  - 明确 close-check blocker、closure audit blocker 与 runtime reality 之间的映射关系
  - 定义 machine-readable `blocker-execution-map.yaml`
  - 为每个 blocker_ref 建立 operator-grade 执行矩阵：`blocker_ref -> carrier spec -> batch -> verification command/surface -> expected evidence`
  - 定义该能力链的子批次顺序、验证面与最终 release-close 口径
  - 以 `program truth audit` 的 blocker surface 作为唯一 machine-readable 入口
- **不覆盖**：
  - 不回退 `141` 已清掉的 root census backfill 工作
  - 不新增第二条发布能力链或第二套 release ledger
  - 不用 docs-only 话术替代 runtime closure
  - 不把 `142` 自身加入 release target membership；release blocker 仍由既有 `095/096/.../126` 承载

## 已锁定决策

- `142` 是一个 capability closure tranche，不是新的 release-required capability
- blocker 清单以执行时重新获取的 `program truth audit` / `release_capabilities[].blocking_refs` 与既有 `required_evidence.close_check_refs` 为准，不接受人工另列一套“理解版 blocker list”
- `142` 必须按能力链分组推进，至少拆成：
  - 产品交付/宿主管理/姿态与 registry 链：`095 -> 096 -> 098 -> 099 -> 100 -> 101 -> 123 -> 124`
  - browser gate / recheck remediation 链：`102 -> 103 -> 104 -> 105 -> 125 -> 126`，其中 `125` 还依赖第一条子链中的 `124`
- `142` 的 spec 目录下必须维护一份 machine-readable `blocker-execution-map.yaml`，plan/tasks 只能消费该映射而不能各写一套
- `blocker-execution-map.yaml` 中每一行必须逐项列出：
  - `blocker_ref`
  - `carrier_spec`
  - `execution_batch`
  - `verification_command_or_surface`
  - `expected_close_evidence`
- `verification_command_or_surface` 只能引用仓库中已存在、可机器验证的 surface（如 `program truth audit`、`workitem close-check`、`workitem truth-check`、`verify constraints` 或已冻结的 evidence artifact path），不得写成自由文本操作步骤
- `capability_closure_audit:capability_open` 不能靠更新 wording 消失，必须由 machine-verifiable close-check/closure evidence 共同消解
- `142` 自身不是 release carrier；它的 close 条件是“所协调的 child work 全部落地后，最新 `program truth audit` 显示 `frontend-mainline-delivery.audit_state=ready`”。在此之前，`142` 不得宣称完成

## 功能需求

| ID | 需求 |
|----|------|
| FR-142-001 | `142` 的 blocker universe 必须始终来自执行时重新获取的 `program truth audit` 与 `program-manifest.yaml` 中 `required_evidence.close_check_refs`，不得人工维护第二份静态列表 |
| FR-142-002 | `142` 必须将 `095/096/098/099/100/101/123/124` 与 `102/103/104/105/125/126` 至少拆为两个 capability 子链，并为每个子链定义显式执行顺序 |
| FR-142-003 | `142` 必须提供 machine-readable `blocker-execution-map.yaml`，逐项将每个 blocker_ref 绑定到具体 `carrier_spec`、`execution_batch`、`verification_command_or_surface` 与 `expected_close_evidence`；其中 `verification_command_or_surface` 只能引用现有 machine-verifiable surface |
| FR-142-004 | `capability_closure_audit:capability_open` 的消解必须与 blocker 消除同步验证，不得单独以人工 closure wording 覆盖 |
| FR-142-005 | `142` 自身不得加入 `frontend-mainline-delivery` 的 `spec_refs`、`roles` 或 `capability_refs`，避免把 orchestrator spec 误当 release carrier |
| FR-142-006 | `142` 只有在所协调的 child work 全部落地，且最新 `program truth audit` 对 `frontend-mainline-delivery` 给出 `audit_state=ready` 时才可关闭；若仍有任何 blocker，则继续 fail-closed |

## Exit Criteria

- **SC-142-001**：`frontend-mainline-delivery` 的 blocker universe 已被正式绑定到“最新 truth audit + `required_evidence.close_check_refs`”，不再由对话临时解释
- **SC-142-002**：第二 tranche 的执行顺序能够直接映射到 blocker execution matrix 中的各个 blocker_ref
- **SC-142-003**：`142` 的最终完成标准明确要求 `program truth audit` 将 `frontend-mainline-delivery` 收敛为 `ready`

---
related_doc:
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md"
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "specs/141-program-manifest-root-census-backfill-baseline/spec.md"
  - "program-manifest.yaml"
frontend_evidence_class: "framework_capability"
---
