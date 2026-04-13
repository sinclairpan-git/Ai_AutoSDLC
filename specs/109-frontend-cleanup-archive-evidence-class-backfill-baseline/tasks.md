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
# 任务分解：Frontend Cleanup Archive Evidence Class Backfill Baseline

**编号**：`109-frontend-cleanup-archive-evidence-class-backfill-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-109-001` ~ `FR-109-007` / `SC-109-001` ~ `SC-109-004`）

---

## 分批策略

```text
Batch 1: formal baseline and red baseline capture
Batch 2: metadata backfill
Batch 3: verification and close-out
```

---

## 执行护栏

- `109` 只允许做 metadata backfill，不得修改 runtime code
- `109` 只覆盖 `050-064`
- `109` 不得伪造 observation artifact 或改写范围外旧规格正文
- `109` 必须保持 canonical footer 与 manifest mirror 一致

---

## Batch 1：formal baseline and red baseline capture

### Task 1.1 冻结 109 formal baseline

- [x] 完成 `109` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 注册 `109`

**完成标准**

- `109` 有合法 carrier，且 manifest graph 能引用本 work item

### Task 1.2 记录目标 cleanup 主线的红灯基线

- [x] 记录 `050-064` 在修改前的 `program status`
- [x] 明确本批不扩张到 `009-049` 及更早历史线

**完成标准**

- execution log 能证明本批处理前目标条目确实处于 `missing_artifact / blocked`

## Batch 2：metadata backfill

### Task 2.1 补齐 canonical footer

- [x] 为 `050-064` 追加 terminal footer 中的 `frontend_evidence_class: "framework_capability"`
- [x] 保持正文与历史成功标准不变

**完成标准**

- 目标规格具备可被 `107` runtime 识别的 canonical evidence class

### Task 2.2 同步 manifest mirror

- [x] 为 `050-064` 的 `program-manifest.yaml` entry 同步 mirror 字段
- [x] 为 `109` 自身注册 canonical entry

**完成标准**

- footer 与 manifest mirror 口径一致，且 `109` 自身也已注册

## Batch 3：verification and close-out

### Task 3.1 回放 focused verification

- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`

**完成标准**

- 目标 cleanup 主线从 `blocked` 转为 `ready / advisory_only`，且无新的约束失败

### Task 3.2 完成 diff hygiene 与 close-out

- [x] 运行 `git diff --check`
- [x] 更新 `task-execution-log.md`
- [x] 运行 `uv run ai-sdlc workitem close-check --wi specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline`

**完成标准**

- `109` 可以作为 cleanup archive evidence-class metadata backfill carrier 收口
