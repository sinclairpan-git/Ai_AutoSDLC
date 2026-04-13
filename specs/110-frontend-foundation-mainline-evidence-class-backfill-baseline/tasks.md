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
---
# 任务分解：Frontend Foundation Mainline Evidence Class Backfill Baseline

**编号**：`110-frontend-foundation-mainline-evidence-class-backfill-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-110-001` ~ `FR-110-007` / `SC-110-001` ~ `SC-110-004`）

---

## 分批策略

```text
Batch 1: formal baseline and red baseline capture
Batch 2: metadata backfill
Batch 3: verification and close-out
```

---

## 执行护栏

- `110` 只允许做 metadata backfill，不得修改 runtime code
- `110` 只覆盖 `009 + 011-049`
- `110` 不得伪造 observation artifact 或改写范围外旧规格正文
- `110` 必须保持 canonical footer 与 manifest mirror 一致

---

## Batch 1：formal baseline and red baseline capture

### Task 1.1 冻结 110 formal baseline

- [x] 完成 `110` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 注册 `110`

**完成标准**

- `110` 有合法 carrier，且 manifest graph 能引用本 work item

### Task 1.2 记录目标 foundation/mainline 的红灯基线

- [x] 记录 `009 + 011-049` 在修改前的 `program status`
- [x] 明确本批只处理剩余历史 frontend framework/governance blocker

**完成标准**

- execution log 能证明本批处理前目标条目确实处于 `missing_artifact / blocked`

## Batch 2：metadata backfill

### Task 2.1 补齐 canonical footer

- [x] 为 `009 + 011-049` 追加 terminal footer 中的 `frontend_evidence_class: "framework_capability"`
- [x] 保持正文与历史成功标准不变

**完成标准**

- 目标规格具备可被 `107` runtime 识别的 canonical evidence class

### Task 2.2 同步 manifest mirror

- [x] 为 `009 + 011-049` 的 `program-manifest.yaml` entry 同步 mirror 字段
- [x] 为 `110` 自身注册 canonical entry

**完成标准**

- footer 与 manifest mirror 口径一致，且 `110` 自身也已注册

## Batch 3：verification and close-out

### Task 3.1 回放 focused verification

- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`

**完成标准**

- 目标历史主线从 `blocked` 转为 `ready / advisory_only`，且无新的约束失败

### Task 3.2 完成 diff hygiene 与 close-out

- [x] 运行 `git diff --check`
- [x] 更新 `task-execution-log.md`
- [x] 运行 `uv run ai-sdlc workitem close-check --wi specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline`

**完成标准**

- `110` 可以作为 foundation/mainline evidence-class metadata backfill carrier 收口
