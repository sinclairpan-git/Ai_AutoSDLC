# 执行记录：082-frontend-evidence-class-authoring-surface-baseline

## Batch 2026-04-08-001 | evidence class authoring surface freeze

### 1.1 范围

- **任务来源**：`081` 已冻结 future framework-only frontend item 必须声明 evidence class，但尚未冻结 declaration location、canonical key 与 authoring error 语义。
- **目标**：冻结 `frontend_evidence_class` 的 canonical authoring surface，明确它写在 `spec.md` footer metadata，且 manifest 未来只能是 mirror，同时保持当前 runtime truth 不变。
- **本批 touched files**：
  - `specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md`
  - `specs/082-frontend-evidence-class-authoring-surface-baseline/plan.md`
  - `specs/082-frontend-evidence-class-authoring-surface-baseline/tasks.md`
  - `specs/082-frontend-evidence-class-authoring-surface-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`

### 1.2 预读与 research inputs

- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`
- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/plan.md`
- `program-manifest.yaml`
- `templates/program-manifest.example.yaml`
- `rg -n "program-manifest|manifest|evidence class|framework_capability|consumer_adoption" specs .ai-sdlc docs -g '*.md' -g '*.yaml' -g '*.yml'`

### 1.3 改动内容

- 新建 `082` formal docs，把 evidence class 的 canonical key、declaration location、allowed values、invalid authoring cases 与 source-of-truth priority 冻结成独立 baseline
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `81` 推进到 `82`

### 1.4 验证命令

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/082-frontend-evidence-class-authoring-surface-baseline`

### 1.5 验证结果

- `uv run ai-sdlc verify constraints`：退出码 `0`，输出 `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program status`：退出码 `0`；当前 runtime truth 未发生 retroactive 变化，`068` 仍为 `decompose_ready`，`069` ~ `071` 仍沿用既有阻塞链，Frontend 列继续显示 `missing_artifact [frontend_contract_observations]`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/082-frontend-evidence-class-authoring-surface-baseline`：退出码 `0`

### 1.6 结论

- `082` 已把 future frontend item 的 evidence class canonical authoring surface 冻结为 `spec.md` footer metadata 中的 `frontend_evidence_class`，同时保持 manifest、runtime 与既有 spec 状态不变
- 该 baseline 满足 prospective-only、docs-only、spec-footer-is-source-of-truth 的边界，可作为后续 parser / validator / manifest mirror 设计的 formal input
