# 功能规格：Frontend Foundation Mainline Evidence Class Backfill Baseline

**功能编号**：`110-frontend-foundation-mainline-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../019-frontend-program-orchestration-baseline/spec.md`](../019-frontend-program-orchestration-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../021-frontend-program-remediation-runtime-baseline/spec.md`](../021-frontend-program-remediation-runtime-baseline/spec.md)、[`../022-frontend-governance-materialization-runtime-baseline/spec.md`](../022-frontend-governance-materialization-runtime-baseline/spec.md)、[`../023-frontend-program-bounded-remediation-execute-baseline/spec.md`](../023-frontend-program-bounded-remediation-execute-baseline/spec.md)、[`../024-frontend-program-bounded-remediation-writeback-baseline/spec.md`](../024-frontend-program-bounded-remediation-writeback-baseline/spec.md)、[`../025-frontend-program-provider-handoff-baseline/spec.md`](../025-frontend-program-provider-handoff-baseline/spec.md)、[`../026-frontend-program-guarded-provider-runtime-baseline/spec.md`](../026-frontend-program-guarded-provider-runtime-baseline/spec.md)、[`../027-frontend-program-provider-runtime-artifact-baseline/spec.md`](../027-frontend-program-provider-runtime-artifact-baseline/spec.md)、[`../028-frontend-program-provider-patch-handoff-baseline/spec.md`](../028-frontend-program-provider-patch-handoff-baseline/spec.md)、[`../029-frontend-program-guarded-patch-apply-baseline/spec.md`](../029-frontend-program-guarded-patch-apply-baseline/spec.md)、[`../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md`](../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md)、[`../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`](../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md)、[`../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`](../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md)、[`../033-frontend-program-guarded-registry-orchestration-baseline/spec.md`](../033-frontend-program-guarded-registry-orchestration-baseline/spec.md)、[`../034-frontend-program-guarded-registry-artifact-baseline/spec.md`](../034-frontend-program-guarded-registry-artifact-baseline/spec.md)、[`../035-frontend-program-broader-governance-orchestration-baseline/spec.md`](../035-frontend-program-broader-governance-orchestration-baseline/spec.md)、[`../036-frontend-program-broader-governance-artifact-baseline/spec.md`](../036-frontend-program-broader-governance-artifact-baseline/spec.md)、[`../037-frontend-program-final-governance-orchestration-baseline/spec.md`](../037-frontend-program-final-governance-orchestration-baseline/spec.md)、[`../038-frontend-program-final-governance-artifact-baseline/spec.md`](../038-frontend-program-final-governance-artifact-baseline/spec.md)、[`../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md`](../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md)、[`../040-frontend-program-writeback-persistence-artifact-baseline/spec.md`](../040-frontend-program-writeback-persistence-artifact-baseline/spec.md)、[`../041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md`](../041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md)、[`../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md`](../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md)、[`../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`](../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md)、[`../044-frontend-program-final-proof-publication-artifact-baseline/spec.md`](../044-frontend-program-final-proof-publication-artifact-baseline/spec.md)、[`../045-frontend-program-final-proof-closure-orchestration-baseline/spec.md`](../045-frontend-program-final-proof-closure-orchestration-baseline/spec.md)、[`../046-frontend-program-final-proof-closure-artifact-baseline/spec.md`](../046-frontend-program-final-proof-closure-artifact-baseline/spec.md)、[`../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`](../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md)、[`../048-frontend-program-final-proof-archive-artifact-baseline/spec.md`](../048-frontend-program-final-proof-archive-artifact-baseline/spec.md)、[`../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`](../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md)、[`../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`](../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md)、[`../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md`](../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md)、[`../109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md`](../109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md)

> 口径：`110` 不是新的 frontend foundation / program runtime 行为工单，而是沿着 `107 -> 108 -> 109` 的 metadata 回填链，把剩余的历史 framework/governance 主线 `009 + 011-049` 补齐 canonical `frontend_evidence_class: framework_capability`。它只修正 readiness truth 的 metadata 缺口，不伪造 observation artifact，也不改写 contract、governance、program orchestration、final-proof archive 的既有语义。

## 问题定义

`107` 已经把 evidence-class-aware readiness gate 接入 runtime，`108` 解决了直接前序链 `065-071 / 073 / 093 / 094`，`109` 又解决了 cleanup archive 主线 `050-064`。但更早的 foundation / governance / program / final-proof archive 主线 `009 + 011-049` 仍保留旧口径：

- canonical `spec.md` 末尾没有 `frontend_evidence_class`
- `program-manifest.yaml` 对应 entry 也未镜像该字段
- 因此 `uv run ai-sdlc program status` 仍把这些条目判为 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`

这 40 条历史规格都属于 framework-governed contract、kernel、compatibility、orchestration、artifact、archive truth，不是 `consumer_adoption`。`110` 的目标是在不补造真实 observation 的前提下，补齐它们的 canonical evidence class truth，让 runtime gate 按既有规则诚实放行。

## 范围

- **覆盖**：
  - 创建 `110` formal docs 与 execution log
  - 在 `program-manifest.yaml` 注册 `110`
  - 为 `009 + 011-049` 补齐 canonical `frontend_evidence_class: "framework_capability"`
  - 同步上述条目的 manifest mirror 字段
  - 回放 `program status / verify constraints / program validate / close-check`
- **不覆盖**：
  - 修改 runtime code、测试逻辑或 gate 算法
  - 伪造任何 `frontend-contract-observations.json`
  - 把任何历史条目改写为 `consumer_adoption`
  - 改写 `009 + 011-049` 的正文语义、成功标准或历史结论
  - 变更 `107/108/109` 已落地的行为边界

## 已锁定决策

- `110` 只做 metadata backfill，不触碰 runtime semantics
- 目标 evidence class 固定为 `framework_capability`
- canonical truth 仍以 `spec.md` terminal footer 为准；manifest mirror 只做同步镜像
- 本批覆盖所有剩余历史 frontend framework/governance blocker：`009 + 011-049`
- `110` 不得借 metadata 回填重新解释 contract、governance、orchestration、archive 的业务边界

## 用户故事与验收

### US-110-1 — Framework Maintainer 需要历史主线不再被 observation artifact 假性阻塞

作为 **framework maintainer**，我希望 `009 + 011-049` 这条历史 frontend 主线补齐 canonical `frontend_evidence_class`，这样 `program status` 就能按 `107` 的 runtime 口径把它们识别为 framework capability，而不是继续误报 observation 缺口。

**验收**：

1. Given `009 + 011-049` 的 canonical footer 声明 `frontend_evidence_class: "framework_capability"`，When 运行 `uv run ai-sdlc program status`，Then 这些规格不再显示 `missing_artifact / blocked [scope_or_linkage_invalid; frontend_contract_observations]`
2. Given 同一批目标条目的 manifest entry 同步了 mirror 字段，When 运行 `uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc program validate`，Then 不会因 footer / manifest drift 引入新的 blocker

### US-110-2 — Operator 需要 foundation / program 语义边界保持诚实

作为 **operator**，我希望 `110` 只修正 evidence-class metadata，而不是篡改 foundation、contract、governance、program orchestration 或 final-proof archive semantics，这样 readiness 改善只来自 `107` 已存在的 runtime gate，而不是文档层面的假绿灯。

**验收**：

1. Given `110` 完成后，When 检查目标规格 diff，Then 改动只出现在 terminal footer / manifest mirror / `110` formal docs
2. Given `009 + 011-049` 中已有的对象模型、治理边界、orchestration、archive 语义，When 运行同样的验证命令，Then 这些语义不会被本批静默改写

## 边界情况

- 若目标规格已有 terminal footer，`110` 只能增补 `frontend_evidence_class`
- 若目标规格尚无 footer，`110` 只能在文件末尾追加最小 metadata block
- `110` 不负责处理未来新增 spec；它只关闭当前仍残留的历史 frontend framework blocker

## 功能需求

| ID | 需求 |
|----|------|
| FR-110-001 | `110` 必须为 `009 + 011-049` 的 canonical `spec.md` footer 补齐 `frontend_evidence_class: "framework_capability"` |
| FR-110-002 | `110` 必须为同一批目标条目的 `program-manifest.yaml` entry 同步 mirror 字段 |
| FR-110-003 | `110` 不得修改 runtime code、`107` gate 逻辑或补造 `frontend_contract_observations` artifact |
| FR-110-004 | `110` 不得把目标条目改写为 `consumer_adoption`，也不得扩展到范围外新工单 |
| FR-110-005 | `110` 必须在 `program-manifest.yaml` 注册自身 canonical entry |
| FR-110-006 | `110` 必须用 fresh verification 证明目标条目从 `blocked` 转为 `ready / advisory_only` |
| FR-110-007 | `110` 必须保持 canonical footer 与 manifest mirror 口径一致，避免引入 metadata drift |

## 成功标准

- **SC-110-001**：`uv run ai-sdlc program status` 显示 `009 + 011-049` 全部为 `ready / advisory_only`
- **SC-110-002**：`uv run ai-sdlc verify constraints` 输出 `verify constraints: no BLOCKERs.`
- **SC-110-003**：`uv run ai-sdlc program validate` 成功通过
- **SC-110-004**：`git diff --check` 通过，且目标规格 diff 仅包含 metadata backfill 与 `110` formal carrier

---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
  - "specs/021-frontend-program-remediation-runtime-baseline/spec.md"
  - "specs/022-frontend-governance-materialization-runtime-baseline/spec.md"
  - "specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md"
  - "specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md"
  - "specs/025-frontend-program-provider-handoff-baseline/spec.md"
  - "specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md"
  - "specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md"
  - "specs/028-frontend-program-provider-patch-handoff-baseline/spec.md"
  - "specs/029-frontend-program-guarded-patch-apply-baseline/spec.md"
  - "specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md"
  - "specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md"
  - "specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md"
  - "specs/033-frontend-program-guarded-registry-orchestration-baseline/spec.md"
  - "specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md"
  - "specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md"
  - "specs/036-frontend-program-broader-governance-artifact-baseline/spec.md"
  - "specs/037-frontend-program-final-governance-orchestration-baseline/spec.md"
  - "specs/038-frontend-program-final-governance-artifact-baseline/spec.md"
  - "specs/039-frontend-program-writeback-persistence-orchestration-baseline/spec.md"
  - "specs/040-frontend-program-writeback-persistence-artifact-baseline/spec.md"
  - "specs/041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md"
  - "specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md"
  - "specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md"
  - "specs/044-frontend-program-final-proof-publication-artifact-baseline/spec.md"
  - "specs/045-frontend-program-final-proof-closure-orchestration-baseline/spec.md"
  - "specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md"
  - "specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md"
  - "specs/048-frontend-program-final-proof-archive-artifact-baseline/spec.md"
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
