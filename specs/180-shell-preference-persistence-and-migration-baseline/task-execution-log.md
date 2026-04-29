# 任务执行日志：跨平台 Shell 偏好持久化与迁移基线

**功能编号**：`180-shell-preference-persistence-and-migration-baseline`  
**创建日期**：2026-04-27  
**状态**：草案

## 1. 归档规则

- 本文件是 `180-shell-preference-persistence-and-migration-baseline` 的固定执行归档文件。
- 后续每完成一批任务，都在本文末尾追加一个新的批次章节。
- 每批开始前必须完成固定预读：`spec.md`、`plan.md`、`tasks.md`、宪章与相关 adapter/shell 配置代码。
- 每批结束后必须按顺序完成：实现、验证、归档、更新 `tasks.md` 勾选状态，再执行单次提交。

## 2. 初始批次记录

### Batch 2026-04-27-001 | Stage-1 formalization

#### 2.1 批次范围

- 覆盖任务：Stage-1 formal docs freeze
- 覆盖阶段：spec / plan / tasks / task-execution-log 初始化
- 预读范围：workitem init baseline、adapter shell feedback、相关 project-config / adapter 代码

#### 2.2 统一验证命令

- `V1`
  - 命令：`python -m ai_sdlc run --dry-run`
  - 结果：PASS；当前 adapter 仍为 `materialized (unverified)`，但允许继续预演
- `V2`
  - 命令：`python -m ai_sdlc workitem init --help`
  - 结果：PASS；确认 canonical Stage-1 docs 入口和分支约束

#### 2.3 本批结果

- 已完成 `specs/180-shell-preference-persistence-and-migration-baseline/` canonical docs 物化
- 已冻结首版范围：配置持久化、init 选择、老项目迁移提示、独立重选命令、adapter 文案物化、状态面补齐
- 已明确后续 next action：`python -m ai_sdlc program truth sync --execute --yes`

#### 2.4 待后续批次补充

- 代码实现记录：待后续批次追加
- 测试结果：待实现批次追加
- 提交哈希：待正式提交后追加

### Batch 2026-04-27-002 | Shell preference persistence + migration rollout

#### Scope
- Implemented project-level preferred shell persistence and normalization.
- Added interactive init shell selection plus non-interactive recommended defaults.
- Added standalone `ai-sdlc adapter shell-select` for already-initialized projects.
- Rendered adapter instructions with managed shell guidance and safe managed rewrites.
- Surfaced missing-shell migration hints through adapter governance, status surfaces, and doctor summaries.

#### Verification
- `python -m pytest tests\\unit\\test_models.py::TestProjectModels::test_project_config_defaults tests\\unit\\test_models.py::TestProjectModels::test_preferred_shell_values tests\\unit\\test_project_config.py::test_load_project_config_missing_file_returns_defaults tests\\unit\\test_project_config.py::test_save_project_config_creates_file tests\\unit\\test_shell_preference.py::test_recommended_shell_for_windows tests\\unit\\test_shell_preference.py::test_recommended_shell_for_macos tests\\unit\\test_shell_preference.py::test_recommended_shell_for_linux tests\\unit\\test_shell_preference.py::test_recommended_shell_for_unknown_platform_falls_back_to_auto tests\\unit\\test_ide_adapter.py::TestApplyAdapter::test_all_ide_templates_point_to_status_then_safe_start tests\\unit\\test_ide_adapter.py::TestApplyAdapter::test_adapter_template_includes_selected_shell_guidance tests\\integration\\test_cli_init.py::TestCliInit::test_init_empty_dir tests\\integration\\test_cli_init.py::TestCliInit::test_init_with_codex_marker_prefers_codex_target tests\\integration\\test_cli_init.py::TestCliInit::test_init_interactive_shell_selector_persists_user_choice tests\\integration\\test_cli_adapter.py::TestCliAdapter::test_adapter_shell_select_with_explicit_shell_persists_and_rewrites_adapter_doc tests\\integration\\test_cli_adapter.py::TestCliAdapter::test_adapter_shell_select_without_flag_uses_interactive_selector tests\\integration\\test_cli_adapter.py::TestCliAdapter::test_adapter_status_json_exposes_target_and_ingress_truth tests\\integration\\test_cli_adapter.py::TestCliAdapter::test_adapter_status_json_reports_shell_selection_migration_hint_for_legacy_project tests\\integration\\test_cli_doctor.py::test_doctor_surfaces_shell_selection_migration_hint_in_status_surface -q` -> PASS (18 passed)
- `python -m ruff check src\\ai_sdlc\\integrations\\agent_target.py src\\ai_sdlc\\integrations\\ide_adapter.py src\\ai_sdlc\\cli\\adapter_cmd.py src\\ai_sdlc\\cli\\commands.py src\\ai_sdlc\\telemetry\\display.py tests\\unit\\test_ide_adapter.py tests\\integration\\test_cli_adapter.py tests\\integration\\test_cli_doctor.py` -> PASS

#### Notes
- Stage-1 docs remain intact; this batch appends implementation evidence only.
- T180-06 remains open for broader doc sweep and close-out regression scope.

### Batch 2026-04-27-003 | Independent review findings archive

#### Findings captured before remediation
- `program-manifest.yaml` was stale relative to `HEAD`, which would force program-truth-gated flows into `truth_snapshot_stale` until another `python -m ai_sdlc program truth sync --execute --yes` ran.
- `src/ai_sdlc/branch/git_client.py` default-branch fallback could silently collapse to the current feature branch when neither `origin/HEAD` nor local `main`/`master` existed, corrupting divergence and merge targeting.
- `src/ai_sdlc/routers/bootstrap.py` persisted `preferred_shell` after adapter materialization, so fresh init could emit `AGENTS.md` with “not configured yet” shell guidance despite config already containing the selected shell.

#### Remediation plan
- Re-run program truth sync after fixes so committed manifest state matches the repaired code path.
- Tighten default-branch detection to require an actual default-branch signal instead of falling back to the current feature branch.
- Persist preferred shell before adapter materialization and add a regression test that checks the first generated adapter document.

### Batch 2026-04-28-001 | Follow-up review findings archive

#### Additional findings captured before remediation
- `offline_strict` preflight was incorrectly calling post-install verification and treating missing installed output as “offline cache missing”.
- telemetry close-session open-run detection still scanned unhashed `sessions/<goal_session_id>` paths even though long session IDs are materialized under hashed scope directories.
- `ai-sdlc init` had no `--shell` override, so TTY-driven scripted flows could block on the raw-key selector even when callers already knew the shell choice.

#### Remediation summary
- Removed the offline-strict preflight that depended on post-install artifacts and added a regression test that proves clean workspaces are no longer rejected before execution.
- Updated runtime open-run detection to resolve session directories through `session_root(...)` and added a hashed-session regression test.
- Added `ai-sdlc init --shell <value>` and regression coverage for explicit shell persistence, first-render adapter guidance, and skipping the interactive selector when a shell is supplied.

### Batch 2026-04-29-001 | Close-gate convergence

#### Scope
- Resolved the Windows-only `GitClient._pid_is_active` regression that used POSIX-style `os.kill(pid, 0)` probing and could interrupt the current Python process on Windows.
- Replaced the fragile threaded write-guard unit test with deterministic lock contention coverage.
- Reconciled checkpoint state from WI-178/close to WI-180/execute and refreshed program truth metadata.
- Closed T180-06 in `tasks.md` and added this final close-out evidence batch.

#### 统一验证命令
- `uv run pytest tests/unit/test_git_client.py -q` -> not runnable in this Codex shell because `uv` is not on PATH.
- `python -m pytest tests/unit/test_git_client.py -q --basetemp pytest-tmp\test_git_client_py -p no:cacheprovider` -> PASS (`16 passed in 9.51s`).
- `uv run ruff check src/ai_sdlc/branch/git_client.py tests/unit/test_git_client.py` -> not runnable in this Codex shell because `uv` is not on PATH.
- `python -m ruff check src\ai_sdlc\branch\git_client.py tests\unit\test_git_client.py` -> PASS (`All checks passed!`).
- `uv run ai-sdlc verify constraints` -> not runnable in this Codex shell because `uv` is not on PATH.
- `python -m ai_sdlc verify constraints` -> initially blocked by unresolved branch lifecycle disposition; this batch records the disposition as `archived`.
- `python -m ai_sdlc program truth sync --execute --yes` -> PASS; refreshed `program-manifest.yaml`.
- `python -m ai_sdlc run --dry-run` -> advanced past checkpoint mismatch and stale truth snapshot; remaining close gates addressed by this batch.

#### 代码审查
- Review focus: Windows PID probing behavior, write-guard regression coverage, and AI-SDLC close-gate evidence surfaces.
- Result: no additional code findings after replacing Windows process probing with Win32 process query and rerunning focused pytest/ruff.

#### 任务/计划同步状态
- `tasks.md` checklist updated to mark T180-01 through T180-06 complete.
- `development-summary.md` added for the WI-180 close gate.
- Program truth metadata refreshed after code/docs/state updates.

#### Close-out markers
- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/branch/git_client.py`, `tests/unit/test_git_client.py`, `specs/180-shell-preference-persistence-and-migration-baseline/tasks.md`, `specs/180-shell-preference-persistence-and-migration-baseline/task-execution-log.md`, `specs/180-shell-preference-persistence-and-migration-baseline/development-summary.md`, `.ai-sdlc/state/checkpoint.yml`, `.ai-sdlc/state/resume-pack.yaml`, `program-manifest.yaml`
- 关联 branch/worktree disposition 计划：archived
- 当前批次 branch disposition 状态：archived
- 当前批次 worktree disposition 状态：retained（current workspace remains active for this Codex thread）
- **已完成 git 提交**：是
- **提交哈希**：随本次收口提交落地
- 是否继续下一批：否，进入 close gate 复验
