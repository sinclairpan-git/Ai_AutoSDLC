# 执行计划：Frontend Evidence Class Verify First Runtime Cut Baseline

**功能编号**：`085-frontend-evidence-class-verify-first-runtime-cut-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective runtime-cut contract

## 1. 目标与定位

`085` 的目标是把 `frontend_evidence_class` 的 first runtime cut 正式冻结成 baseline：未来 runtime 第一刀只落在 `verify constraints`，只读取 `spec.md` footer metadata，只产出 authoring malformed diagnostics，不连带定义 manifest mirror、status projection 或 close-stage resurfacing。

## 2. 范围

### 2.1 In Scope

- 创建 `085` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `85`
- 冻结 first runtime cut 的 owning surface、source-of-truth 与 reader placement
- 冻结 allowed `error_kind`、minimum payload 与 severity boundary 的承接方式
- 冻结 non-goals，防止 mirror / status / close-stage 抢跑

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 helper、parser 或任一 CLI 诊断输出
- 引入 manifest mirror 或 drift 逻辑
- 改写 `program status`、`status --json`、`workitem close-check`
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`
- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/plan.md`
- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/tasks.md`
- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Runtime-Cut Rules

### 4.1 Owning surface

- first runtime cut 只属于 `verify constraints`
- 不提前把 `program validate` 纳入同一轮

### 4.2 Canonical source

- 只认 future work item `spec.md` footer metadata
- 不把 manifest、status 或 observation artifact 升格为 correctness source

### 4.3 Reader placement

- future helper 落在 `src/ai_sdlc/core/verify_constraints.py` 的治理读路径附近
- 不落在 `frontend_contract_verification.py`

### 4.4 Diagnostics boundary

- 只允许 `frontend_evidence_class_authoring_malformed`
- 只允许 `missing_footer_key`、`empty_value`、`invalid_value`、`duplicate_key`、`body_footer_conflict`
- minimum payload 与 severity boundary 承接 `084`

## 5. 分阶段计划

### Phase 0：design reconciliation

- 回读 `081` ~ `084`
- 回读 frozen design doc
- 确认本轮只是在 formal baseline 中重述已批准设计，不新增 runtime 语义

### Phase 1：first runtime cut baseline freeze

- 新建 `085` formal docs
- 写清 owning surface、canonical source、reader placement、separation boundary
- 写清 bounded diagnostics 与 non-goals

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline`

## 7. 回滚原则

- 如果 `085` 让人误以为 runtime helper 已经实现，必须回退
- 如果 `085` 把 manifest mirror / `program validate` 偷带进 first runtime cut，必须回退
- 如果 `085` 让 status surface 越权承担 full diagnostics，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
