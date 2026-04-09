# 执行记录：091-frontend-evidence-class-close-check-runtime-implementation-baseline

## Batch 2026-04-09-001 | close-check bounded resurfacing runtime cut

### 1.1 范围

- **任务来源**：`089` 已冻结 close-stage late resurfacing contract，但 docs-only baseline 本身不授权 `src/` / `tests/` 写面，需要新的 implementation carrier 承接 runtime cut。
- **目标**：将 `frontend_evidence_class` 的 bounded late resurfacing 落到 `workitem close-check`，并用 integration regression 固定 authoring malformed / mirror drift 两类 close-stage blocker。
- **本批 touched files**：
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/plan.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/tasks.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`
  - `src/ai_sdlc/core/close_check.py`
  - `tests/integration/test_cli_workitem_close_check.py`

### 1.2 根因与实现摘要

- `close_check.py` 新增 `frontend_evidence_class` 的 close-stage summary builder：
  - 优先消费 `verify constraints` 已派生的 authoring malformed blocker
  - 再消费 `program validate` 已派生的 mirror drift summary
  - 仅回传 bounded `problem_family`、`detection_surface` 与 compact token
- integration regression 覆盖：
  - `authoring malformed` 在 `--json` surface 的 bounded resurfacing
  - `mirror drift` 在 table surface 的 bounded resurfacing
- 调试中发现 mirror drift 回归最初失败不是 runtime 逻辑错误，而是测试夹具把 `program-manifest.yaml` 写成了非法 YAML；`close-check` 按 bounded contract 吞掉 manifest 解析异常后返回 `None`，因此表现为未 surfacing。当前已将 fixture writer 改为 `dedent + strip`，把夹具错误与 runtime 语义分离。

### 1.3 验证命令

- `uv run pytest tests/integration/test_cli_workitem_close_check.py::TestCliWorkitemCloseCheck::test_exit_1_when_close_check_late_resurfaces_frontend_evidence_class_mirror_drift -vv -s`
- `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

### 1.4 验证结果

- mirror drift 定向回归：通过，`1 passed in 1.13s`
- `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`：通过，`30 passed in 11.51s`
- `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`：通过，`All checks passed!`
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`
- `git diff --check`：通过，无输出
- 提交前 fresh 重跑：
  - `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`：通过，`30 passed in 12.28s`
  - `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`：通过，`All checks passed!`
  - `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`
  - `git diff --check`：通过，无输出

### 1.5 对账结论

- `091` 已为当前 runtime diff 提供合法写面，消除了“`089` docs-only baseline 却直接改 `src/` / `tests/`”的框架冲突。
- `close_check.py` 当前实现满足 `089` 的 bounded late resurfacing contract：只复报 unresolved blocker，不 first-detect，不 writeback，不泄露 full diagnostics payload。
- integration regression 已固定 table / json 两种 surface，并显式验证不输出 `source_of_truth_path=` 与 `human_remediation_hint=`。

### 1.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`56dc3de`
- 当前 batch 结论：`091` 的首批 close-check runtime cut 已完成实现、fresh verification 与独立提交。
- **下一步动作**：如继续推进 runtime，优先回到 `086/087` 对应的 mirror carrier / `program validate` 路径，补齐 close-check 上游 canonical drift surface。

### Batch 2026-04-09-002 | close-out evidence normalization

#### 1. 准备

- **任务来源**：`close-out gate remediation`
- **目标**：为 `091` 的 latest batch 补齐当前 `workitem close-check` 要求的 canonical close-out markers，并保持 `091` runtime implementation truth 不变。
- **预读范围**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`src/ai_sdlc/core/close_check.py`、`tests/integration/test_cli_workitem_close_check.py`
- **激活的规则**：close-check execution log fields；verification profile truthfulness；fresh verification before commit
- **验证画像**：`docs-only`
- **改动范围**：`specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`

#### 2. 统一验证命令

- **V1（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
- **V2（diff hygiene）**
  - 命令：`git diff --check -- specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`
- **V3（workitem close-check）**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline`

#### 3. 任务记录

##### Task close-out-remediation | 规范 091 latest batch 结构

- **改动范围**：`specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`
- **改动内容**：
  - 追加 latest `### Batch ...` close-out evidence 结构，补齐 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`验证画像` 与 git close-out markers。
  - 保持 `091` 的 close-check bounded resurfacing runtime 行为不变；本批只做 execution evidence normalization。
  - 不新增关联 branch lifecycle truth，因为 `091` 当前没有独立命名的 associated work-item branch 需要归档。
- **新增/调整的测试**：无新增测试；本批仅补 close-out docs，复用治理只读校验、diff hygiene 与 post-commit close-check 复核。
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：
  - `uv run ai-sdlc verify constraints`：将在本批提交前 fresh 复跑。
  - `git diff --check -- specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`：将在本批提交前 fresh 复跑。
  - `uv run ai-sdlc workitem close-check --wi specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline`：将在本批提交后复跑，用于确认 latest close-out evidence 已满足 gate。
- **是否符合任务目标**：符合。latest batch 现已具备 close-check 所需的 mandatory markers，最终完成态以 post-commit close-check 为准。

#### 4. 代码审查（摘要）

- 本批审查重点是 `091` 的 close-stage truth 是否被 latest batch 正确表达，而不是重审 runtime 行为本身。
- 审查结论：`091` 继续保持 bounded late resurfacing contract；本批没有引入新的 detection surface 或 payload，只把 close-out evidence 调整为框架认可的 canonical 形状。

#### 5. 任务/计划同步状态

- `tasks.md` 同步状态：`已对账`
- `plan.md` 同步状态：`已对账`
- `spec.md` 同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`retained（close-out sync only；无 associated work-item branch 需要归档）`

#### 6. 批次结论

- 当前批次只做 `091` close-out evidence normalization，不改写实现与测试范围；fresh verification 与 post-commit close-check 通过后即可作为 formal close-out latest batch。

#### 7. 归档后动作

- **已完成 git 提交**：是（`091` implementation baseline 已提交；latest close-out sync 将在当前归档提交中落盘）
- **提交哈希**：`c82053e`
- 当前批次 branch disposition 状态：`retained`
- 当前批次 worktree disposition 状态：`retained（close-out sync clean worktree；无 associated work-item branch 需要归档）`
