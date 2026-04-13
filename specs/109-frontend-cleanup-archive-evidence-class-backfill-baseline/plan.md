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
---
# 执行计划：Frontend Cleanup Archive Evidence Class Backfill Baseline

**功能编号**：`109-frontend-cleanup-archive-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`109` 的目标是把 `107` 已经支持的 evidence-class-aware readiness 语义继续回填到更早的 final-proof-archive cleanup 主线：`050-064`。实现方式只限 canonical footer 与 manifest mirror 补齐，不新增 runtime 逻辑，也不改写 cleanup mutation / approval / gating / execution 的既有语义。

## 2. 范围

### 2.1 In Scope

- 创建 `109` formal docs 与 execution log
- 在 `program-manifest.yaml` 注册 `109`
- 为 `050-064` 补齐 canonical `frontend_evidence_class: "framework_capability"`
- 同步对应 manifest entry
- 回放 `program status`、`verify constraints`、`program validate`、`close-check`

### 2.2 Out Of Scope

- 修改 `src/` runtime logic 或补测试逻辑
- 伪造 `frontend-contract-observations.json`
- 改写 `050-064` 已冻结的 cleanup runtime、proposal、approval、gating 或 execution semantics
- 一次性清理 `009-049` 或更早历史 frontend 线上的全部 blocker
- 改写目标规格正文或历史结论

## 3. 变更文件面

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`
- `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`
- `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`
- `specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md`
- `specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`
- `specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md`
- `specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md`
- `specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md`
- `specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md`
- `specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md`
- `specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md`
- `specs/061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md`
- `specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md`
- `specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md`
- `specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md`
- `specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/*`

## 4. 实施规则

### 4.1 Metadata only

- `109` 只能修改 target spec 的 terminal footer 与 manifest mirror
- 若目标 spec 已有 footer，只能增补 `frontend_evidence_class`
- 若目标 spec 尚无 footer，只能追加最小 metadata block

### 4.2 Scope discipline

- 当前批次只处理 `050-064`
- `009-049` 以及更早历史 line 保持原状，避免把一次 metadata backfill 扩张成整仓历史清扫
- 不得把任何目标 spec 标成 `consumer_adoption`

### 4.3 Verification discipline

- 先记录当前 `program status` 红灯基线
- 再完成 metadata backfill
- 最后回放 `program status / verify constraints / program validate / close-check / diff hygiene`

## 5. 分批计划

### Batch 1：formal baseline and red baseline capture

- 完成 `109` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- 在 `program-manifest.yaml` 注册 `109`
- 记录修改前 `program status` 中目标规格的 `blocked` 状态

### Batch 2：metadata backfill

- 为 `050-064` 追加 canonical footer
- 为同一批条目同步 manifest mirror

### Batch 3：verification and close-out

- 回放 `uv run ai-sdlc program status`
- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program validate`
- 运行 `git diff --check` 与 `uv run ai-sdlc workitem close-check --wi specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline`

## 6. 最小验证策略

- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program status`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md specs/061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline`

## 7. 回滚原则

- 若任何目标 spec 被错误标记为非 `framework_capability`，必须回退
- 若 metadata backfill 影响到范围外历史条目，必须回退
- 若 `program validate` 或 `verify constraints` 因 manifest/footer drift 失败，`109` 不得宣称完成
