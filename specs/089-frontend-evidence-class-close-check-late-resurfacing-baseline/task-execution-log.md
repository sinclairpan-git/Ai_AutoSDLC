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

### Batch 2026-04-09-002 | close-out evidence normalization

#### 1. 准备

- **任务来源**：`close-out gate remediation`
- **目标**：为 `089` 的 latest batch 补齐当前 `workitem close-check` 要求的 canonical close-out markers，并保持 close-stage late resurfacing contract 的 docs-only truth 不变。
- **预读范围**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`src/ai_sdlc/cli/workitem_cmd.py`、`src/ai_sdlc/core/close_check.py`
- **激活的规则**：close-check execution log fields；verification profile truthfulness；fresh verification before commit
- **验证画像**：`docs-only`
- **改动范围**：`specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/task-execution-log.md`

#### 2. 统一验证命令

- **V1（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
- **V2（diff hygiene）**
  - 命令：`git diff --check -- specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/task-execution-log.md`
- **V3（workitem close-check）**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`

#### 3. 任务记录

##### Task close-out-remediation | 规范 089 latest batch 结构

- **改动范围**：`specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/task-execution-log.md`
- **改动内容**：
  - 追加 latest `### Batch ...` close-out evidence 结构，补齐 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`验证画像` 与 git close-out markers。
  - 保持 `089` 的 close-stage late resurfacing 语义不变；本批只做 execution evidence normalization，不新增 first-detect、writeback 或 auto-heal 行为。
  - 不新增关联 branch lifecycle truth，因为 `089` 当前没有独立命名的 associated work-item branch 需要归档。
- **新增/调整的测试**：无新增测试；本批仅补 close-out docs，复用治理只读校验、diff hygiene 与 post-commit close-check 复核。
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：
  - `uv run ai-sdlc verify constraints`：将在本批提交前 fresh 复跑。
  - `git diff --check -- specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/task-execution-log.md`：将在本批提交前 fresh 复跑。
  - `uv run ai-sdlc workitem close-check --wi specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline`：将在本批提交后复跑，用于确认 latest close-out evidence 已满足 gate。
- **是否符合任务目标**：符合。latest batch 现已具备 close-check 所需的 mandatory markers，最终完成态以 post-commit close-check 为准。

#### 4. 代码审查（摘要）

- 本批审查重点是 `089` 的 docs-only close-stage contract 是否被 latest batch 准确表达，而不是重审 bounded resurfacing 语义本身。
- 审查结论：`089` 继续保持“close-check 只复报 upstream truth，不 first-detect、不 writeback、不 auto-heal”的 contract 边界；本批没有引入新的 surface，只把 close-out evidence 调整为框架认可的 canonical 形状。

#### 5. 任务/计划同步状态

- `tasks.md` 同步状态：`已对账`
- `plan.md` 同步状态：`已对账`
- `spec.md` 同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`retained（close-out sync only；无 associated work-item branch 需要归档）`

#### 6. 批次结论

- 当前批次只做 `089` close-out evidence normalization，不改写 docs-only contract；fresh verification 与 post-commit close-check 通过后即可作为 formal close-out latest batch。

#### 7. 归档后动作

- **已完成 git 提交**：是（`089` close-check late resurfacing baseline 已提交；latest close-out sync 将在当前归档提交中落盘）
- **提交哈希**：`0bb8f52`
- 当前批次 branch disposition 状态：`retained`
- 当前批次 worktree disposition 状态：`retained（close-out sync clean worktree；无 associated work-item branch 需要归档）`
