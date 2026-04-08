# 执行记录：089-frontend-evidence-class-close-check-late-resurfacing-baseline

## Batch 2026-04-09-001 | close-check late resurfacing contract freeze

### 1.1 范围

- **任务来源**：`083` ~ `088` 已冻结 detection、diagnostics、verify/runtime first cut、mirror placement、writeback owner 与 bounded status surfacing，但 `workitem close-check` 对 evidence-class 的 close-stage resurfacing 仍缺独立 contract。
- **目标**：把 future close-check 对 `frontend_evidence_class` 的 role 冻结为 close-stage late resurfacing，明确 table / json 允许暴露的最小粒度、禁止展开的 payload，以及 non-healing / non-adjudication 边界，同时保持当前 runtime truth 不变。
- **本批 touched files**：
  - `specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`
  - `specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/plan.md`
  - `specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/tasks.md`
  - `specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`

### 1.2 预读与 research inputs

- `specs/083-frontend-evidence-class-validator-surface-baseline/spec.md`
- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`
- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`
- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`
- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`
- `specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`
- `docs/USER_GUIDE.zh-CN.md`
- `src/ai_sdlc/cli/workitem_cmd.py`
- `src/ai_sdlc/core/close_check.py`

### 1.3 改动内容

- 新建 `089` formal docs，把 `frontend_evidence_class` 的 future `workitem close-check` surfacing 冻结为独立 late-resurfacing contract baseline
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `88` 推进到 `89`

### 1.4 验证命令

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`

### 1.5 验证结果

- `uv run ai-sdlc verify constraints`：退出码 `0`，输出 `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program status`：退出码 `0`；当前 runtime truth 未发生 retroactive 变化，`067` 继续为 `close`，`068` 继续停留在既有 `decompose_ready` 语义，`069` ~ `071` 仍沿用既有阻塞链，Frontend 列继续显示 `missing_artifact [frontend_contract_observations]`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`：退出码 `0`

### 1.6 结论

- `089` 已将 `frontend_evidence_class` 的 future close-stage late resurfacing role、allowed bounded detail 与 forbidden payload 冻结为独立 formal input
- 该 baseline 明确 close-check 只能重述 upstream blocker truth，不得 first-detect、writeback 或 auto-heal
