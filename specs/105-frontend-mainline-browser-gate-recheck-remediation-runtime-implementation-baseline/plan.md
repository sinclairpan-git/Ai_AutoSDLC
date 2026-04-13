# 执行计划：Frontend Mainline Browser Gate Recheck Remediation Runtime Implementation Baseline

**功能编号**：`105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`  
**创建日期**：2026-04-13  
**状态**：runtime implementation baseline 已落地；governance reconciliation 进行中  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`105` 的目标不是再写一份 browser gate contract，而是把 `104` 已冻结的 result-binding truth 落到当前仓库实际可用的 execute gate runtime surface：

- 在 `frontend_gate_verification.py` 固定 `ready / blocked / recheck_required / needs_remediation` 的映射；
- 在 `program_service.py` 固定 recheck handoff 与 remediation runbook 的分流；
- 在 `program_cmd.py` 固定 CLI status / execute 对上述 truth 的呈现；
- 用 unit / integration regression 锁死 `recheck_required`、fail-closed `blocked` 与 remediation runbook 的行为边界；
- 把已经完成的实现对账到新的合法 implementation carrier 中。

## 2. 范围

### 2.1 In Scope

- 创建 `105` formal docs 与 execution log
- 在 `frontend_gate_verification.py` 实现 `104` 的 execute decision mapping
- 在 `program_service.py` 实现 frontend recheck/remediation handoff 分流
- 在 `program_cmd.py` 呈现 frontend execute gate state 与 handoff truth
- 在 unit / integration tests 中补充针对性回归
- 在 `program-manifest.yaml` 增加 `105` canonical entry
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `105` 推进到 `106`

### 2.2 Out Of Scope

- 修改 `104` 的 docs-only result-binding truth
- 实现 browser gate replay scheduler、后台 loop、auto-fix engine 或 bundle 自愈
- 修改 `102` 的 bundle schema、`103` 的 probe runtime 或 `020` 的 execute vocabulary
- 扩张当前实现到 program-wide aggregation 或新的 CLI 子命令

## 3. 变更文件面

`105` 允许改动的文件面如下：

- `src/ai_sdlc/core/frontend_gate_verification.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/cli/program_cmd.py`
- `tests/unit/test_frontend_gate_verification.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`
- `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/plan.md`
- `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/tasks.md`
- `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/task-execution-log.md`

## 4. 实施规则

### 4.1 Mapping honesty

- 只有纯 recheck 场景才允许输出 `recheck_required`
- evidence-backed blocker 必须保持 `needs_remediation`
- source/linkage 不可信与结果不自洽必须 fail-closed 为 `blocked`

### 4.2 Handoff separation

- `ProgramFrontendRecheckBinding` 与 remediation runbook 不能同时 materialize 为同一语义
- CLI 不得把 fail-closed `blocked` 包装成“只需重跑”
- remediation runbook 必须保留 policy artifact gaps 等非 replay 问题

### 4.3 Scope discipline

- `105` 只承接当前已落地的最小实现面
- 不新增 replay orchestrator、background scheduler、auto-fix engine
- 不把 `ProgramService` 变成新的 browser gate truth source

## 5. 分批计划

### Batch 1：execute decision runtime cut

- 收敛 `frontend_gate_verification.py` 的 decision mapping
- 将 recheck 与 remediation 的状态/原因分开
- 为 fail-closed `blocked` 写入定向 unit regression

### Batch 2：ProgramService / CLI handoff propagation

- 在 `program_service.py` 中 materialize recheck handoff 与 remediation runbook
- 在 `program_cmd.py` 中呈现 frontend execute gate state
- 通过 integration regression 锁定 status / execute surface

### Batch 3：runbook regression and governance reconciliation

- 补 `tests/unit/test_program_service.py` 的 remediation runbook 回归
- 为已完成实现创建 `105` implementation carrier docs
- 同步 `program-manifest.yaml` 与 `project-state.yaml`

## 6. 最小验证策略

- `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'missing_visual_a11y_evidence_to_recheck_required or blocks_missing_visual_a11y_policy_artifacts or maps_visual_a11y_issue_to_needs_remediation' -q`
- `uv run pytest tests/unit/test_program_service.py -k 'frontend_readiness_gap_when_071_visual_a11y_evidence_missing or frontend_blocked_when_visual_a11y_policy_artifacts_missing or frontend_needs_remediation_when_visual_a11y_issue_detected or frontend_recheck_handoff or visual_a11y_policy_artifact_remediation_input_when_missing or keeps_visual_a11y_policy_artifact_gaps_in_remediation' -q`
- `uv run pytest tests/integration/test_cli_program.py -k 'program_status_exposes_frontend_execute_gate_recheck_required or frontend_execute_gate_blocked_for_policy_artifact_gap or frontend_execute_gate_needs_remediation or visual_a11y_policy_artifact_remediation_hint or frontend_recheck_handoff' -q`
- `uv run ruff check src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc verify constraints`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`

## 7. 回滚原则

- 如果 `105` 把 docs-only `104` 与 runtime implementation 的边界重新混淆，必须回退
- 如果 `105` 让 policy artifact gap 错误进入 recheck 路径，必须回退
- 如果 `105` 让 fail-closed `blocked` 丢失诊断语义，必须回退
- 如果 `105` 扩张到 replay runtime、auto-fix 或新的 aggregation surface，必须回退
