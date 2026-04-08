# 执行记录：088-frontend-evidence-class-bounded-status-surface-baseline

## Batch 2026-04-09-001 | bounded status surface contract freeze

### 1.1 范围

- **任务来源**：`083` ~ `087` 已冻结 detection、diagnostics、mirror placement、writeback owner 与 drift contract，但 status surfacing 仍缺 program-scoped 与 active-work-item scoped 的明确边界。
- **目标**：把 future evidence-class status surfacing 冻结为独立 formal input，明确 `program status` 与 `status --json` 的摘要粒度、可暴露字段、禁止暴露的 payload，以及 non-adjudication 边界，同时保持当前 runtime truth 不变。
- **本批 touched files**：
  - `specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`
  - `specs/088-frontend-evidence-class-bounded-status-surface-baseline/plan.md`
  - `specs/088-frontend-evidence-class-bounded-status-surface-baseline/tasks.md`
  - `specs/088-frontend-evidence-class-bounded-status-surface-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`

### 1.2 预读与 research inputs

- `specs/083-frontend-evidence-class-validator-surface-baseline/spec.md`
- `specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`
- `specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`
- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`
- `specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`
- `docs/USER_GUIDE.zh-CN.md`
- `src/ai_sdlc/cli/program_cmd.py`
- `src/ai_sdlc/cli/commands.py`
- `src/ai_sdlc/telemetry/readiness.py`

### 1.3 改动内容

- 新建 `088` formal docs，把 `frontend_evidence_class` 的 future bounded status surfacing 冻结为独立 status-surface contract baseline
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `87` 推进到 `88`

### 1.4 验证命令

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/088-frontend-evidence-class-bounded-status-surface-baseline`

### 1.5 验证结果

- `uv run ai-sdlc verify constraints`：退出码 `0`，输出 `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program status`：退出码 `0`；当前 runtime truth 未发生 retroactive 变化，`067` 继续为 `close`，`068` 继续停留在既有 `decompose_ready` 语义，`069` ~ `071` 仍沿用既有阻塞链，Frontend 列继续显示 `missing_artifact [frontend_contract_observations]`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/088-frontend-evidence-class-bounded-status-surface-baseline`：退出码 `0`

### 1.6 结论

- `088` 已将 `frontend_evidence_class` 的 future `program status` / `status --json` 粒度边界、允许暴露的最小字段与禁止暴露的 full payload 冻结为独立 formal input
- 该 baseline 明确 status surface 只能重述 upstream truth，不得重新解析 canonical source 或替代 owning diagnostics
