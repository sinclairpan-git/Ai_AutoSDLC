# 执行记录：105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline

## Batch 2026-04-13-001 | execute gate handoff runtime cut

### 1.1 范围

- **任务来源**：`104` 已冻结 browser gate result-binding contract，但 docs-only baseline 不允许直接修改 `src/` / `tests/`。
- **目标**：把 `104` 的 execute decision truth 落到当前 runtime surface，并用回归测试锁定 recheck、remediation 与 fail-closed `blocked` 的边界。
- **本批 touched files**：
  - `src/ai_sdlc/core/frontend_gate_verification.py`
  - `src/ai_sdlc/core/program_service.py`
  - `src/ai_sdlc/cli/program_cmd.py`
  - `tests/unit/test_frontend_gate_verification.py`
  - `tests/unit/test_program_service.py`
  - `tests/integration/test_cli_program.py`

### 1.2 实现摘要

- `frontend_gate_verification.py` 细化 `build_frontend_gate_execute_decision()`：
  - 纯 visual/a11y evidence 缺口进入 `recheck_required`
  - policy artifact 缺失与不自洽结果保持 fail-closed `blocked`
  - evidence-backed 真实质量问题进入 `needs_remediation`
- `program_service.py` 与 `program_cmd.py` 对齐 frontend execute gate truth：
  - `recheck_required` 只 materialize recheck handoff
  - `blocked` / `needs_remediation` 进入 remediation runbook / remediation input
  - CLI status / execute surface 可区分 recheck 与 remediation
- regression 覆盖：
  - `recheck_required`
  - policy artifact fail-closed `blocked`
  - evidence-backed remediation
  - frontend recheck handoff
  - remediation input / hint

### 1.3 验证命令与结果

- `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'missing_visual_a11y_evidence_to_recheck_required or blocks_missing_visual_a11y_policy_artifacts or maps_visual_a11y_issue_to_needs_remediation' -q`
  - 结果：通过，`3 passed, 12 deselected`
- `uv run pytest tests/unit/test_program_service.py -k 'frontend_readiness_gap_when_071_visual_a11y_evidence_missing or frontend_blocked_when_visual_a11y_policy_artifacts_missing or frontend_needs_remediation_when_visual_a11y_issue_detected or frontend_recheck_handoff or visual_a11y_policy_artifact_remediation_input_when_missing' -q`
  - 结果：通过，`6 passed, 164 deselected`
- `uv run pytest tests/integration/test_cli_program.py -k 'program_status_exposes_frontend_execute_gate_recheck_required or frontend_execute_gate_blocked_for_policy_artifact_gap or frontend_execute_gate_needs_remediation or visual_a11y_policy_artifact_remediation_hint or frontend_recheck_handoff' -q`
  - 结果：通过，`5 passed, 117 deselected`
- `uv run ruff check src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
  - 结果：通过，`All checks passed!`
- `uv run ai-sdlc program validate`
  - 结果：通过，`program validate: PASS`
- `uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `uv run pytest tests/integration/test_cli_program.py -k 'program_integrate_execute_surfaces or program_integrate_execute_success or program_integrate_dry_run' -q`
  - 结果：通过，`10 passed, 111 deselected`

### 1.4 结论

- `104` 的 result-binding truth 已经落到最小 runtime surface，但该 diff 仍缺少独立 implementation carrier 与治理挂载点。
- **已完成 git 提交**：是
- **提交哈希**：`a10344d`

## Batch 2026-04-13-002 | remediation runbook regression backfill

### 2.1 范围

- **任务来源**：首批 runtime cut 已完成，但 remediation runbook 仍需补一条针对 policy artifact gap 的定向回归，防止后续把非 replay 问题误丢到 recheck 路径。
- **目标**：补齐 `tests/unit/test_program_service.py` 中的 remediation runbook 回归，锁死 `frontend_visual_a11y_policy_artifacts` 的保留行为。
- **本批 touched files**：
  - `tests/unit/test_program_service.py`

### 2.2 实现摘要

- 新增 `test_build_frontend_remediation_runbook_keeps_visual_a11y_policy_artifact_gaps_in_remediation`
- 固定 `frontend_visual_a11y_policy_artifacts` 继续进入 remediation runbook，而不是被吸入 replay / recheck 逻辑

### 2.3 验证命令与结果

- `uv run pytest tests/unit/test_program_service.py -q -k 'keeps_visual_a11y_policy_artifact_gaps_in_remediation'`
  - 结果：通过，`1 passed, 170 deselected`
- `uv run pytest tests/unit/test_program_service.py -q -k 'collects_action_commands_and_follow_up_verify or keeps_visual_a11y_policy_artifact_gaps_in_remediation or surfaces_visual_a11y_policy_artifact_remediation_input_when_missing'`
  - 结果：通过，`3 passed, 168 deselected`
- `uv run ruff check tests/unit/test_program_service.py`
  - 结果：通过，`All checks passed!`

### 2.4 结论

- remediation runbook 对 policy artifact gap 的保留行为已被单独锁定，后续不会轻易回归成 replay 语义。
- **已完成 git 提交**：是
- **提交哈希**：`60856ae`

## Batch 2026-04-13-003 | implementation carrier legalization and registry sync

### 3.1 范围

- **任务来源**：代码实现已经提交，但仓库还缺少 `105` canonical spec，且 `project-state.next_work_item_seq` 停在 `105`。
- **目标**：为 `a10344d` 与 `60856ae` 提供合法 implementation carrier，补齐 `spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`，并同步 program registry / project-state。
- **本批 touched files**：
  - `program-manifest.yaml`
  - `.ai-sdlc/project/config/project-state.yaml`
  - `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`
  - `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/plan.md`
  - `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/tasks.md`
  - `specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/task-execution-log.md`

### 3.2 治理对账摘要

- 复核 `104`：其护栏明确禁止修改 `src/` / `tests/`，因此不能反向把已完成实现归入 `104`
- 复核同类模式 `091`：docs-only contract 与 runtime implementation 需要分离到新的 implementation carrier
- 因此新增 `105`，把当前实现对账为 `104` 的首个 runtime implementation carrier，并将下一工作项推进到 `106`

### 3.3 本批验证命令

- `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'missing_visual_a11y_evidence_to_recheck_required or blocks_missing_visual_a11y_policy_artifacts or maps_visual_a11y_issue_to_needs_remediation' -q`
- `uv run pytest tests/unit/test_program_service.py -k 'frontend_readiness_gap_when_071_visual_a11y_evidence_missing or frontend_blocked_when_visual_a11y_policy_artifacts_missing or frontend_needs_remediation_when_visual_a11y_issue_detected or frontend_recheck_handoff or visual_a11y_policy_artifact_remediation_input_when_missing or keeps_visual_a11y_policy_artifact_gaps_in_remediation' -q`
- `uv run pytest tests/integration/test_cli_program.py -k 'program_status_exposes_frontend_execute_gate_recheck_required or frontend_execute_gate_blocked_for_policy_artifact_gap or frontend_execute_gate_needs_remediation or visual_a11y_policy_artifact_remediation_hint or frontend_recheck_handoff' -q`
- `uv run ruff check src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc verify constraints`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`

### 3.4 本批验证结果

- `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'missing_visual_a11y_evidence_to_recheck_required or blocks_missing_visual_a11y_policy_artifacts or maps_visual_a11y_issue_to_needs_remediation' -q`
  - 结果：通过，`3 passed, 12 deselected in 0.48s`
- `uv run pytest tests/unit/test_program_service.py -k 'frontend_readiness_gap_when_071_visual_a11y_evidence_missing or frontend_blocked_when_visual_a11y_policy_artifacts_missing or frontend_needs_remediation_when_visual_a11y_issue_detected or frontend_recheck_handoff or visual_a11y_policy_artifact_remediation_input_when_missing or keeps_visual_a11y_policy_artifact_gaps_in_remediation' -q`
  - 结果：通过，`7 passed, 164 deselected in 0.81s`
- `uv run pytest tests/integration/test_cli_program.py -k 'program_status_exposes_frontend_execute_gate_recheck_required or frontend_execute_gate_blocked_for_policy_artifact_gap or frontend_execute_gate_needs_remediation or visual_a11y_policy_artifact_remediation_hint or frontend_recheck_handoff' -q`
  - 结果：通过，`5 passed, 117 deselected in 0.96s`
- `uv run ruff check src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
  - 结果：通过，`All checks passed!`
- `uv run ai-sdlc program validate`
  - 结果：通过，`program validate: PASS`
- `uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`
  - 结果：通过，无输出

### 3.5 结论

- 当前批次只做 implementation carrier legalization 与 registry sync，不改变既有 runtime 行为。
- fresh verification 已全部通过，`105` 可作为当前实现的合法 canonical work item。
