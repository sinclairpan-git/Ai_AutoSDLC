# 执行记录：084-frontend-evidence-class-diagnostic-contract-baseline

## Batch 2026-04-08-001 | evidence class diagnostics contract freeze

### 1.1 范围

- **任务来源**：`083` 已冻结 future detection surface，但尚未冻结 evidence-class 问题该如何被稳定分类、最少应输出哪些 bounded truth、status surface 又该克制到什么程度。
- **目标**：冻结 future evidence-class diagnostics 的问题族群、最低严重级别边界与最小 payload，同时保持当前 runtime truth 不变。
- **本批 touched files**：
  - `specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`
  - `specs/084-frontend-evidence-class-diagnostic-contract-baseline/plan.md`
  - `specs/084-frontend-evidence-class-diagnostic-contract-baseline/tasks.md`
  - `specs/084-frontend-evidence-class-diagnostic-contract-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`

### 1.2 预读与 research inputs

- `specs/083-frontend-evidence-class-validator-surface-baseline/spec.md`
- `docs/framework-defect-backlog.zh-CN.md`
- `docs/USER_GUIDE.zh-CN.md`
- `rg -n "authoring error|diagnostic|BLOCKER|warning|error code|status --json|verify constraints" docs specs src tests -g '*.md' -g '*.py'`

### 1.3 改动内容

- 新建 `084` formal docs，把 future evidence-class diagnostics 的 problem family、severity boundary、minimum payload 与 bounded status exposure 冻结成独立 baseline
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `83` 推进到 `84`

### 1.4 验证命令

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/084-frontend-evidence-class-diagnostic-contract-baseline`

### 1.5 验证结果

- `uv run ai-sdlc verify constraints`：退出码 `0`，输出 `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program status`：退出码 `0`；当前 runtime truth 未发生 retroactive 变化，`068` 继续停留在既有 `decompose_ready` 语义，`069` ~ `071` 仍沿用既有阻塞链，Frontend 列继续显示 `missing_artifact [frontend_contract_observations]`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/084-frontend-evidence-class-diagnostic-contract-baseline`：退出码 `0`

### 1.6 结论

- `084` 已把 future evidence-class diagnostics 冻结为两类稳定问题族群：`frontend_evidence_class_authoring_malformed` 与 `frontend_evidence_class_mirror_drift`，并明确 owning surface 上最低严重级别为 `BLOCKER`
- 该 baseline 同时限制了 `program status` / `status --json` 的 bounded summary 边界，可作为后续 parser / validator diagnostics 实现的 formal input
