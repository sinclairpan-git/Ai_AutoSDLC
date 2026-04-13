# 功能规格：Frontend Cleanup Archive Evidence Class Backfill Baseline

**功能编号**：`109-frontend-cleanup-archive-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`](../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md)、[`../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`](../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md)、[`../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md`](../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md)、[`../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`](../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md)、[`../055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md`](../055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md)、[`../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md`](../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md)、[`../057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md`](../057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md)、[`../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md`](../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md)、[`../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md`](../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md)、[`../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md`](../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md)、[`../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md`](../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md)、[`../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md`](../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md)、[`../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md`](../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md)、[`../064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md`](../064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md)、[`../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`](../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md)、[`../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md`](../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md)

> 口径：`109` 不是新的 final-proof-archive cleanup runtime 行为工单，而是 `107` 落地后对历史 cleanup 主线 `050-064` 的第二批 metadata 回填。它只补 canonical `frontend_evidence_class: framework_capability`，让这条 cleanup line 不再因为缺失真实 `frontend_contract_observations` 而继续被误报为 blocked，同时不改变 cleanup mutation、approval、gating 或 execution 的既有语义。

## 问题定义

`107` 已将 evidence-class-aware readiness gate 接入 runtime，`108` 进一步把 `065-071 / 073 / 093 / 094` 这条直接前序链回填为 canonical `framework_capability`。但更早的 final-proof-archive cleanup 主线 `050-064` 仍停留在旧口径：

- `050-064` 的 `spec.md` 文件末尾尚未声明 canonical `frontend_evidence_class`
- `program-manifest.yaml` 对应 entry 也未镜像该字段
- 因此 `uv run ai-sdlc program status` 仍将这组 cleanup / planning / runtime baseline 显示为 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`

这条 work item line 的内容本身都是 framework-governed cleanup contract、truth consumption 或 bounded execution baseline，不属于 `consumer_adoption`。`109` 的目标是在不伪造 observation artifact、不改写 cleanup runtime semantics、不改变 consumer adoption truth 的前提下，补齐 `050-064` 这条历史 cleanup 主线的 canonical evidence class truth。

## 范围

- **覆盖**：
  - 创建 `109` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `109`
  - 为 `050-064` 补齐 canonical `frontend_evidence_class: "framework_capability"`
  - 同步上述规格在 `program-manifest.yaml` 中的 mirror 字段
  - 回放 `program status / verify constraints / program validate / close-check`
- **不覆盖**：
  - 修改 `050-064` 既有 cleanup runtime 逻辑、approval/gating 语义或 execution result contract
  - 修改 `107` runtime gate 逻辑
  - 伪造任何 `frontend-contract-observations.json`
  - 把任何条目改写为 `consumer_adoption`
  - 一次性处理 `009-049` 或其他范围外历史 frontend 条目
  - 改写目标规格正文、需求语义或历史结论

## 已锁定决策

- `109` 只补 metadata，不改动 runtime code、测试逻辑或 close contract
- 目标 evidence class 固定为 `framework_capability`，不得引入新枚举值
- canonical truth 仍以 `spec.md` terminal footer 为准；manifest mirror 只作同步镜像
- 本批只处理 final-proof-archive cleanup 主线 `050-064`
- `109` 不得借 metadata backfill 重新解释 cleanup action matrix、approval truth、execution gating 或 execution semantics

## 用户故事与验收

### US-109-1 — Framework Maintainer 需要 cleanup 主线不再被 observation artifact 假性阻塞

作为 **framework maintainer**，我希望 `050-064` 这条 final-proof-archive cleanup 主线补齐 canonical `frontend_evidence_class`，这样 `program status` 就能按 `107` 的 runtime 口径把它们识别为 framework capability，而不是继续误报真实 observation 缺口。

**验收**：

1. Given `050-064` 的 canonical footer 声明 `frontend_evidence_class: "framework_capability"`，When 运行 `uv run ai-sdlc program status`，Then 这些规格不再显示 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`
2. Given 上述规格的 manifest entry 同步了同名字段，When 运行 `uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc program validate`，Then 不会因 footer / manifest drift 产生新的 blocker

### US-109-2 — Operator 需要 cleanup 语义保持诚实边界

作为 **operator**，我希望 `109` 只修正 evidence-class metadata，而不是篡改 cleanup runtime 语义或伪造 observation artifact，这样 `050-064` 的 readiness 改善只来自 `107` 已存在的 evidence-class-aware gate，而不是文档层面的假绿灯。

**验收**：

1. Given `109` 完成后，When 检查目标规格 diff，Then 改动只出现在 terminal footer / manifest mirror / `109` formal docs
2. Given `050-064` 中已有的 planning、proposal、approval、gating 与 execution 基线，When 运行相同命令，Then 它们的 cleanup contract 不会被本批静默改写

## 边界情况

- 若某个目标规格已有 terminal footer，`109` 只能增补 `frontend_evidence_class`，不得破坏其既有 metadata key
- 若某个目标规格尚无 footer，`109` 追加的 footer 必须位于文件末尾，且语义仅限 metadata backfill
- `109` 不负责证明所有历史 frontend blocker 都已收敛；`009-049` 继续保持原状

## 功能需求

| ID | 需求 |
|----|------|
| FR-109-001 | `109` 必须为 `050-064` 的 canonical `spec.md` footer 补齐 `frontend_evidence_class: "framework_capability"` |
| FR-109-002 | `109` 必须为同一批目标条目的 `program-manifest.yaml` entry 同步 mirror 字段 |
| FR-109-003 | `109` 不得修改 `050-064` 的 runtime semantics、`107` runtime code 或补造 `frontend_contract_observations` artifact |
| FR-109-004 | `109` 不得把范围外历史 frontend 条目静默纳入本批 |
| FR-109-005 | `109` 必须在 `program-manifest.yaml` 注册自身 canonical entry |
| FR-109-006 | `109` 必须用 fresh verification 证明目标条目从 `blocked` 转为 `ready / advisory_only` |
| FR-109-007 | `109` 必须保持 footer 与 manifest mirror 的口径一致，避免引入 metadata drift |

## 成功标准

- **SC-109-001**：`uv run ai-sdlc program status` 显示 `050-064` 全部为 `ready / advisory_only`
- **SC-109-002**：`uv run ai-sdlc verify constraints` 输出 `verify constraints: no BLOCKERs.`
- **SC-109-003**：`uv run ai-sdlc program validate` 成功通过
- **SC-109-004**：`git diff --check` 通过，且目标规格 diff 仅包含 metadata backfill 与 `109` formal carrier

---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
  - "specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md"
  - "specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md"
  - "specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md"
  - "specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md"
  - "specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md"
  - "specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md"
  - "specs/061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md"
  - "specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md"
  - "specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md"
  - "specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
