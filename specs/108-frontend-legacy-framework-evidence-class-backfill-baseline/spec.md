# 功能规格：Frontend Legacy Framework Evidence Class Backfill Baseline

**功能编号**：`108-frontend-legacy-framework-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`](../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md)

> 口径：`108` 不是新的 frontend runtime 行为工单，而是 `107` 落地后的历史 metadata 回填批次。它只补 `065-071 / 073 / 093 / 094` 这条当前 mainline 与 stage0 前序链上的 canonical `frontend_evidence_class: framework_capability`，让这些规格不再因为缺失真实 `frontend_contract_observations` 而继续被误报为 blocked。

## 问题定义

`107` 已把 evidence-class-aware readiness gate 接入 runtime，但它只会信任 canonical `spec.md` footer 的 `frontend_evidence_class`。当前仍有一组直接前序规格停留在旧口径：

- `065-071 / 073 / 093 / 094` 的 `spec.md` footer 尚未声明 canonical `frontend_evidence_class`
- `program-manifest.yaml` 对应 entry 也未镜像该字段
- 因此 `uv run ai-sdlc program status` 仍将这些规格显示为 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`

这些 work item 的内容本身都是 framework / planning / stage0 baseline，并不属于 `consumer_adoption`。`108` 的目标是在不伪造 observation artifact、不改写既有 runtime 逻辑的前提下，补齐这组历史前序规格的 canonical evidence class truth。

## 范围

- **覆盖**：
  - 创建 `108` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `108`
  - 为 `065-071 / 073 / 093 / 094` 补齐 canonical `frontend_evidence_class: framework_capability`
  - 同步上述规格在 `program-manifest.yaml` 中的 mirror 字段
  - 回放 `program status / verify constraints / program validate / close-check`
- **不覆盖**：
  - 修改 `107` 的 runtime gate 逻辑
  - 伪造任何 `frontend-contract-observations.json`
  - 把任何条目改写为 `consumer_adoption`
  - 一次性处理 `063/064` 以及更早历史 frontend 线上的所有遗留 blocker
  - 修改目标规格的业务正文、需求语义或历史结论

## 已锁定决策

- `108` 只补 metadata，不改动 runtime code、测试逻辑或 close contract
- 目标 evidence class 固定为 `framework_capability`，不得引入新枚举值
- canonical truth 仍以 `spec.md` terminal footer 为准；manifest mirror 只作同步镜像
- 本批只处理直接前序链 `065-071 / 073 / 093 / 094`，不借机扩张为全量历史清扫

## 用户故事与验收

### US-108-1 — Framework Maintainer 需要直接前序链不再被 observation artifact 假性阻塞

作为 **framework maintainer**，我希望 `065-071 / 073 / 093 / 094` 这组 framework/stage0 前序规格补齐 canonical `frontend_evidence_class`，这样 `program status` 就能按 `107` 的 runtime 口径把它们识别为 framework capability，而不是继续误报真实 observation 缺口。

**验收**：

1. Given `065-071 / 073 / 093 / 094` 的 canonical footer 声明 `frontend_evidence_class: "framework_capability"`，When 运行 `uv run ai-sdlc program status`，Then 这些规格不再显示 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`
2. Given 上述规格的 manifest entry 同步了同名字段，When 运行 `uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc program validate`，Then 不会因 footer / manifest drift 产生新的 blocker

### US-108-2 — Operator 需要 metadata 回填保持诚实边界

作为 **operator**，我希望 `108` 只修正 evidence-class metadata，而不是伪造 observation artifact 或篡改旧规格正文，这样 `ready / advisory_only` 仍然来自 `107` 的既有 runtime 语义，而不是文档层面的假绿灯。

**验收**：

1. Given `108` 完成后，When 检查目标规格 diff，Then 改动只出现在 terminal footer / manifest mirror / `108` formal docs
2. Given 不在 `108` 范围内的历史 frontend 条目，When 运行相同命令，Then 它们的 readiness 结果不会被本批静默改写

## 边界情况

- 若某个目标规格已有 terminal footer，`108` 只能增补 `frontend_evidence_class`，不得破坏其既有 metadata key
- 若某个目标规格尚无 footer，`108` 追加的 footer 必须位于文件末尾，且语义仅限 metadata backfill
- `108` 不负责证明所有历史 frontend blocker 都已收敛；范围外条目继续保持原状

## 功能需求

| ID | 需求 |
|----|------|
| FR-108-001 | `108` 必须为 `065-071 / 073 / 093 / 094` 的 canonical `spec.md` footer 补齐 `frontend_evidence_class: "framework_capability"` |
| FR-108-002 | `108` 必须为同一批目标条目的 `program-manifest.yaml` entry 同步 mirror 字段 |
| FR-108-003 | `108` 不得修改 `107` runtime code 或补造 `frontend_contract_observations` artifact |
| FR-108-004 | `108` 不得把范围外历史 frontend 条目静默纳入本批 |
| FR-108-005 | `108` 必须在 `program-manifest.yaml` 注册自身 canonical entry |
| FR-108-006 | `108` 必须用 fresh verification 证明目标条目从 `blocked` 转为 `ready / advisory_only` |
| FR-108-007 | `108` 必须保持 footer 与 manifest mirror 的口径一致，避免引入 metadata drift |

## 成功标准

- **SC-108-001**：`uv run ai-sdlc program status` 显示 `065-071 / 073 / 093 / 094` 全部为 `ready / advisory_only`
- **SC-108-002**：`uv run ai-sdlc verify constraints` 输出 `verify constraints: no BLOCKERs.`
- **SC-108-003**：`uv run ai-sdlc program validate` 成功通过
- **SC-108-004**：`git diff --check` 通过，且目标规格 diff 仅包含 metadata backfill 与 `108` formal carrier

---
related_doc:
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
