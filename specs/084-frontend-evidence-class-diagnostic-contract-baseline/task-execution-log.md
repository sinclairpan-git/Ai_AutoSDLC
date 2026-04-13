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
- `USER_GUIDE.zh-CN.md`
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

### Batch 2026-04-13-002 | latest batch close-check backfill and manifest mirror registration

#### 2.1 批次范围

- **任务编号**：latest-batch close-out backfill（无新增实现任务编号）
- **目标**：补齐 `084` latest batch 的现行 close-check mandatory fields，并在同一 close-out carrier 中把 `082-092` 注册到 `program-manifest.yaml`，消除 `manifest_unmapped` 漂移。
- **执行分支**：`codex/113-frontend-082-092-manifest-mirror-baseline`
- **激活的规则**：close-check execution log fields；review gate evidence；verification profile truthfulness；git close-out markers truthfulness；frontend evidence class manifest mirror honesty。
- **验证画像**：`docs-only`
- **改动范围**：`specs/084-frontend-evidence-class-diagnostic-contract-baseline/task-execution-log.md`

#### 2.2 统一验证命令

- 命令：
  - `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc program validate`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc workitem close-check --wi specs/084-frontend-evidence-class-diagnostic-contract-baseline`
  - `git diff --check -- specs/084-frontend-evidence-class-diagnostic-contract-baseline/task-execution-log.md`
- 结果：
  - `verify constraints`：`verify constraints: no BLOCKERs.`
  - `program validate`：`program validate: PASS`
  - `workitem close-check`：latest batch 的 mandatory markers、review evidence、verification profile 与 manifest mapping 已在当前 carrier 中补齐；fresh rerun 只剩 `git working tree has uncommitted changes` 这一项，待 `113` close-out commit 落盘后消除
  - `git diff --check`：fresh rerun 无输出，通过

#### 2.3 任务记录

- 本批只追加 `084/task-execution-log.md` 的 latest-batch close-check backfill 段落
- `084/spec.md / plan.md / tasks.md` 未改写
- `program-manifest.yaml` 中新增 `082-092` 的 canonical `frontend_evidence_class` mirror registration，但不改 `084` 已冻结的 diagnostics family / severity boundary

#### 2.4 代码审查结论（Mandatory）

- docs-only 审查结果：未发现新的 diagnostics contract 语义漂移或 runtime 风险
- `084` 仍保持 `frontend_evidence_class_authoring_malformed` 与 `frontend_evidence_class_mirror_drift` 两类问题族群，以及 owning surface 至少为 `BLOCKER` 的边界

#### 2.5 任务/计划同步状态（Mandatory）

- `084` 的既有 `spec.md / plan.md / tasks.md` 与当前状态保持一致
- 本批只修 latest-batch close-out schema 与 manifest mirror honesty，不新增 feature task 或实现任务

#### 2.6 自动决策记录（如有）

- 选择把 `082-092` manifest registration 与 `082-084` 的 latest-batch close-out backfill 放进同一 `113` carrier；这样 `084` 已定义的 `frontend_evidence_class_mirror_drift` 能与当前 manifest reality 对齐，而不是继续停留在未映射状态。

#### 2.7 批次结论

- `084` 的 latest batch 现已补齐现行 close-check 所需的 mandatory fields
- `084` 的 manifest mirror 已按当前 runtime reality 注册到 `program-manifest.yaml`
- 本批不宣称新的 diagnostics / status / close-check 实现，只修 close-out honesty 与 mirror registration truth

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：由 `113` close-out commit 统一承载；以当前分支 `HEAD` 为准
- 当前批次 branch disposition 状态：retained
- 当前批次 worktree disposition 状态：retained
- 是否继续下一批：是；可由 `113` carrier 继续统一收口其余目标
