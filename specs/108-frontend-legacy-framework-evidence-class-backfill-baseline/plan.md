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
# 执行计划：Frontend Legacy Framework Evidence Class Backfill Baseline

**功能编号**：`108-frontend-legacy-framework-evidence-class-backfill-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`108` 的目标是把 `107` 已经支持的 evidence-class-aware readiness 语义回填到一条直接前序链上：`065-071 / 073 / 093 / 094`。实现方式只限 canonical footer 与 manifest mirror 补齐，不新增 runtime 逻辑，也不伪造 observation artifact。

## 2. 范围

### 2.1 In Scope

- 创建 `108` formal docs 与 execution log
- 在 `program-manifest.yaml` 注册 `108`
- 为 `065-071 / 073 / 093 / 094` 补齐 canonical `frontend_evidence_class: "framework_capability"`
- 同步对应 manifest entry
- 回放 `program status`、`verify constraints`、`program validate`、`close-check`

### 2.2 Out Of Scope

- 修改 `src/` runtime logic 或补测试逻辑
- 伪造 `frontend-contract-observations.json`
- 一次性清理 `063/064` 以及更早历史 frontend 线上的全部 blocker
- 改写目标规格正文或历史结论

## 3. 变更文件面

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md`
- `specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`
- `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`
- `specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- `specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`
- `specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`
- `specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md`
- `specs/073-frontend-p2-provider-style-solution-baseline/spec.md`
- `specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md`
- `specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md`
- `specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/*`

## 4. 实施规则

### 4.1 Metadata only

- `108` 只能修改 target spec 的 terminal footer 与 manifest mirror
- 若目标 spec 已有 footer，只能增补 `frontend_evidence_class`
- 若目标 spec 尚无 footer，只能追加最小 metadata block

### 4.2 Scope discipline

- 当前批次只处理 `065-071 / 073 / 093 / 094`
- `063/064` 以及更早历史 line 保持原状，避免把一次 metadata backfill 扩张成整仓历史清扫
- 不得把任何目标 spec 标成 `consumer_adoption`

### 4.3 Verification discipline

- 先记录当前 `program status` 红灯基线
- 再完成 metadata backfill
- 最后回放 `program status / verify constraints / program validate / close-check / diff hygiene`

## 5. 分批计划

### Batch 1：formal baseline and red baseline capture

- 完成 `108` 的 `spec.md / plan.md / tasks.md / task-execution-log.md`
- 在 `program-manifest.yaml` 注册 `108`
- 记录修改前 `program status` 中目标规格的 `blocked` 状态

### Batch 2：metadata backfill

- 为 `065-071 / 073` 追加 canonical footer
- 为 `093 / 094` 在现有 footer 中补入 `frontend_evidence_class`
- 为同一批条目同步 manifest mirror

### Batch 3：verification and close-out

- 回放 `uv run ai-sdlc program status`
- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program validate`
- 运行 `git diff --check` 与 `uv run ai-sdlc workitem close-check --wi specs/108-frontend-legacy-framework-evidence-class-backfill-baseline`

## 6. 最小验证策略

- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program status`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md specs/066-frontend-p1-experience-stability-planning-baseline/spec.md specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md specs/073-frontend-p2-provider-style-solution-baseline/spec.md specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md specs/108-frontend-legacy-framework-evidence-class-backfill-baseline`

## 7. 回滚原则

- 若任何目标 spec 被错误标记为非 `framework_capability`，必须回退
- 若 metadata backfill 影响到范围外历史条目，必须回退
- 若 `program validate` 或 `verify constraints` 因 manifest/footer drift 失败，`108` 不得宣称完成
