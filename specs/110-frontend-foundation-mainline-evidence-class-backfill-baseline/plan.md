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
# 执行计划：Frontend Foundation Mainline Evidence Class Backfill Baseline

**功能编号**：`110-frontend-foundation-mainline-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`110` 的目标是把 `107` 已经支持的 evidence-class-aware readiness 语义继续回填到剩余历史 frontend 主线 `009 + 011-049`。实现方式只限 canonical footer 与 manifest mirror 补齐，不新增 runtime 逻辑，也不改写 contract、governance、orchestration 或 final-proof archive 的既有语义。

## 2. 范围

### 2.1 In Scope

- 创建 `110` formal docs 与 execution log
- 在 `program-manifest.yaml` 注册 `110`
- 为 `009 + 011-049` 补齐 canonical `frontend_evidence_class: "framework_capability"`
- 同步对应 manifest entry
- 回放 `program status`、`verify constraints`、`program validate`、`close-check`

### 2.2 Out Of Scope

- 修改 `src/` runtime logic 或补测试逻辑
- 伪造 `frontend-contract-observations.json`
- 改写 `009 + 011-049` 已冻结的正文、治理边界或 archive semantics
- 修改 `107/108/109` 的既有行为边界

## 3. 变更文件面

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/009-frontend-governance-ui-kernel/spec.md`
- `specs/011-frontend-contract-authoring-baseline/spec.md`
- `specs/012-frontend-contract-verify-integration/spec.md`
- `specs/013-frontend-contract-observation-provider-baseline/spec.md`
- `specs/014-frontend-contract-runtime-attachment-baseline/spec.md`
- `specs/015-frontend-ui-kernel-standard-baseline/spec.md`
- `specs/016-frontend-enterprise-vue2-provider-baseline/spec.md`
- `specs/017-frontend-generation-governance-baseline/spec.md`
- `specs/018-frontend-gate-compatibility-baseline/spec.md`
- `specs/019-frontend-program-orchestration-baseline/spec.md`
- `specs/020-frontend-program-execute-runtime-baseline/spec.md`
- `specs/021-frontend-program-remediation-runtime-baseline/spec.md`
- `specs/022-frontend-governance-materialization-runtime-baseline/spec.md`
- `specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md`
- `specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`
- `specs/025-frontend-program-provider-handoff-baseline/spec.md`
- `specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`
- `specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md`
- `specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`
- `specs/029-frontend-program-guarded-patch-apply-baseline/spec.md`
- `specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md`
- `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`
- `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`
- `specs/033-frontend-program-guarded-registry-orchestration-baseline/spec.md`
- `specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md`
- `specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`
- `specs/036-frontend-program-broader-governance-artifact-baseline/spec.md`
- `specs/037-frontend-program-final-governance-orchestration-baseline/spec.md`
- `specs/038-frontend-program-final-governance-artifact-baseline/spec.md`
- `specs/039-frontend-program-writeback-persistence-orchestration-baseline/spec.md`
- `specs/040-frontend-program-writeback-persistence-artifact-baseline/spec.md`
- `specs/041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md`
- `specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md`
- `specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`
- `specs/044-frontend-program-final-proof-publication-artifact-baseline/spec.md`
- `specs/045-frontend-program-final-proof-closure-orchestration-baseline/spec.md`
- `specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md`
- `specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`
- `specs/048-frontend-program-final-proof-archive-artifact-baseline/spec.md`
- `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`
- `specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/*`

## 4. 实施规则

### 4.1 Metadata only

- `110` 只能修改 target spec 的 terminal footer 与 manifest mirror
- 若目标 spec 已有 footer，只能增补 `frontend_evidence_class`
- 若目标 spec 尚无 footer，只能追加最小 metadata block

### 4.2 Scope discipline

- 当前批次只处理 `009 + 011-049`
- 范围外已回填链保持原状，避免重复漂移
- 不得把任何目标 spec 标成 `consumer_adoption`

### 4.3 Verification discipline

- 先记录当前 `program status` 红灯基线
- 再完成 metadata backfill
- 最后回放 `program status / verify constraints / program validate / close-check / diff hygiene`

## 5. 分批计划

### Batch 1：formal baseline and red baseline capture

- 完成 `110` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- 在 `program-manifest.yaml` 注册 `110`
- 记录修改前 `program status` 中目标规格的 `blocked` 状态

### Batch 2：metadata backfill

- 为 `009 + 011-049` 追加 canonical footer
- 为同一批条目同步 manifest mirror

### Batch 3：verification and close-out

- 回放 `uv run ai-sdlc program status`
- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program validate`
- 运行 `git diff --check` 与 `uv run ai-sdlc workitem close-check --wi specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline`

## 6. 最小验证策略

- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program status`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml program-manifest.yaml specs/009-frontend-governance-ui-kernel/spec.md specs/011-frontend-contract-authoring-baseline/spec.md specs/012-frontend-contract-verify-integration/spec.md specs/013-frontend-contract-observation-provider-baseline/spec.md specs/014-frontend-contract-runtime-attachment-baseline/spec.md specs/015-frontend-ui-kernel-standard-baseline/spec.md specs/016-frontend-enterprise-vue2-provider-baseline/spec.md specs/017-frontend-generation-governance-baseline/spec.md specs/018-frontend-gate-compatibility-baseline/spec.md specs/019-frontend-program-orchestration-baseline/spec.md specs/020-frontend-program-execute-runtime-baseline/spec.md specs/021-frontend-program-remediation-runtime-baseline/spec.md specs/022-frontend-governance-materialization-runtime-baseline/spec.md specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md specs/025-frontend-program-provider-handoff-baseline/spec.md specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md specs/028-frontend-program-provider-patch-handoff-baseline/spec.md specs/029-frontend-program-guarded-patch-apply-baseline/spec.md specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md specs/033-frontend-program-guarded-registry-orchestration-baseline/spec.md specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md specs/036-frontend-program-broader-governance-artifact-baseline/spec.md specs/037-frontend-program-final-governance-orchestration-baseline/spec.md specs/038-frontend-program-final-governance-artifact-baseline/spec.md specs/039-frontend-program-writeback-persistence-orchestration-baseline/spec.md specs/040-frontend-program-writeback-persistence-artifact-baseline/spec.md specs/041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md specs/044-frontend-program-final-proof-publication-artifact-baseline/spec.md specs/045-frontend-program-final-proof-closure-orchestration-baseline/spec.md specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md specs/048-frontend-program-final-proof-archive-artifact-baseline/spec.md specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/plan.md specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/tasks.md specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/task-execution-log.md`

## 7. 回滚原则

- 若任何目标 spec 被错误标记为非 `framework_capability`，必须回退
- 若 metadata backfill 影响到范围外条目，必须回退
- 若 `program validate` 或 `verify constraints` 因 manifest/footer drift 失败，`110` 不得宣称完成
