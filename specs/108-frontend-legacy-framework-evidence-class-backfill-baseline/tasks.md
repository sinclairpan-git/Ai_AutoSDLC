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
---
# 任务分解：Frontend Legacy Framework Evidence Class Backfill Baseline

**编号**：`108-frontend-legacy-framework-evidence-class-backfill-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-108-001` ~ `FR-108-007` / `SC-108-001` ~ `SC-108-004`）

---

## 分批策略

```text
Batch 1: formal baseline and red baseline capture
Batch 2: metadata backfill
Batch 3: verification and close-out
```

---

## 执行护栏

- `108` 只允许做 metadata backfill，不得修改 runtime code
- `108` 只覆盖 `065-071 / 073 / 093 / 094`
- `108` 不得伪造 observation artifact 或改写范围外旧规格正文
- `108` 必须保持 canonical footer 与 manifest mirror 一致

---

## Batch 1：formal baseline and red baseline capture

### Task 1.1 冻结 108 formal baseline

- [x] 完成 `108` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `program-manifest.yaml` 注册 `108`

**完成标准**

- `108` 有合法 carrier，且 manifest graph 能引用本 work item

### Task 1.2 记录目标前序链的红灯基线

- [x] 记录 `065-071 / 073 / 093 / 094` 在修改前的 `program status`
- [x] 明确本批不扩张到 `063/064` 及更早历史线

**完成标准**

- execution log 能证明本批处理前目标条目确实处于 `missing_artifact / blocked`

## Batch 2：metadata backfill

### Task 2.1 补齐 canonical footer

- [x] 为 `065-071 / 073` 追加 terminal footer 中的 `frontend_evidence_class: "framework_capability"`
- [x] 保持正文与历史成功标准不变

**完成标准**

- 目标规格具备可被 `107` runtime 识别的 canonical evidence class

### Task 2.2 同步 manifest mirror 与现有 footer

- [x] 为 `093 / 094` 的现有 footer 增补 `frontend_evidence_class: "framework_capability"`
- [x] 为 `065-071 / 073 / 093 / 094` 的 `program-manifest.yaml` entry 同步 mirror 字段

**完成标准**

- footer 与 manifest mirror 口径一致，且 `108` 自身也已注册

## Batch 3：verification and close-out

### Task 3.1 回放 focused verification

- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`

**完成标准**

- 目标前序链从 `blocked` 转为 `ready / advisory_only`，且无新的约束失败

### Task 3.2 完成 diff hygiene 与 close-out

- [x] 运行 `git diff --check`
- [x] 更新 `task-execution-log.md`
- [x] 运行 `uv run ai-sdlc workitem close-check --wi specs/108-frontend-legacy-framework-evidence-class-backfill-baseline`

**完成标准**

- `108` 可以作为 legacy framework evidence-class metadata backfill carrier 收口
