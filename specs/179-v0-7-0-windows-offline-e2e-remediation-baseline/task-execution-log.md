# 任务执行日志：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**创建日期**：2026-04-24
**状态**：16/16 任务已完成；本批补齐 Windows source-checkout / release evidence / close-out 收口

## 1. 归档规则

- 本文件记录 `179` 的正式 SDLC 执行历史。
- 每个实现批次开始前必须预读：
  - `.ai-sdlc/memory/constitution.md`
  - `docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md`
  - `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/spec.md`
  - `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/plan.md`
  - `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/tasks.md`
- 每个实现批次必须记录影响范围、验证命令、测试结果、回退方式和是否符合任务目标。
- 代码实现和文档归档应在同一逻辑 commit 内完成。

## 2. 批次记录

### Batch 2026-04-24-001 | Formal intake and decomposition

#### 2.1 批次范围

- 覆盖任务：缺陷归档转正式 SDLC work item
- 覆盖阶段：design / decompose
- 输入文档：`docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md`
- 输出文档：
  - `spec.md`
  - `research.md`
  - `data-model.md`
  - `plan.md`
  - `tasks.md`
  - `task-execution-log.md`

#### 2.2 统一验证命令

- `ai-sdlc adapter status`
- `ai-sdlc run --dry-run`
- `ai-sdlc stage show design`
- `ai-sdlc stage show decompose`
- `python -m ai_sdlc verify constraints`
- `git diff --check`

#### 2.3 批次结论

- 已将 22 个 E2E 缺陷归并为正式需求、设计决策、数据模型、计划和 16 个可执行任务。
- 当前批次不改实现代码；后续应从 Batch 1 的 P0 Windows dependency runtime closure 开始。
- adapter 当前仍为 acknowledged / soft_installed，无 machine-verifiable activation evidence；后续 mutate 批次必须重新检查入口状态。

#### 2.4 回退方式

- 删除 `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/` 并移除缺陷归档中的正式 WI 链接即可回退本批文档拆分。

### Batch 2026-04-26-001 | P0 Windows dependency runtime closure

#### 2.1 批次范围

- 覆盖任务：`T179-01`、`T179-02`、`T179-03`
- 覆盖缺陷：`E2E-WIN-007`、`E2E-WIN-008`、`E2E-WIN-020`、`E2E-WIN-021`
- 影响范围：
  - `src/ai_sdlc/core/managed_delivery_apply.py`
  - `src/ai_sdlc/models/frontend_managed_delivery.py`
  - `src/ai_sdlc/core/program_service.py`
  - `src/ai_sdlc/cli/program_cmd.py`
  - `src/ai_sdlc/core/branch_inventory.py`
  - `tests/support/managed_delivery.py`
  - `tests/unit/test_managed_delivery_apply.py`
  - `tests/unit/test_program_service.py`

#### 2.2 实现摘要

- Windows 下 `npm` / `npx` / `pnpm` / `yarn` / `corepack` 通过 host command resolver 优先解析为 `.cmd` shim，不走 `shell=True`。
- `DependencyInstallExecutionPayload` 增加 `dependency_mode`，支持 `offline_strict`、`enterprise_registry`、`public_registry`。
- `ProgramService` 在生成 managed delivery apply request 时把公共/企业依赖模式写入 provider install 与 visual runtime install action。
- `offline_strict` 在 action validation 阶段复用依赖安装验证；缺少 package manifest、lockfile、node_modules resolution 或 Playwright runtime 时，在 mutate 前返回 `blocked_before_start`。
- dependency install 命令不可执行时，apply result 记录 attempted command、resolved executable、cwd、PATH/PATHEXT、stdout/stderr、exception、retry count、plain language blockers、recommended next steps，并把下游 action 写为 `dependency_blocked`。
- Windows 路径输出补齐 POSIX 归一化，避免 CLI/artifact truth 在 Windows 下产生反斜杠漂移。

#### 2.3 验证命令

- `python -m ai_sdlc adapter status`：通过；当前 adapter 为 `acknowledged / soft_installed`，无 machine-verifiable activation evidence。
- `python -m ai_sdlc run --dry-run`：通过，输出 `Pipeline completed. Stage: close`。
- `python -m ai_sdlc stage show decompose`：通过。
- `python -m ai_sdlc stage show implement`：失败，原因是有效阶段集合为 `init/refine/design/decompose/verify/execute/close`，不存在 `implement`。
- `python -m pytest tests/unit/test_managed_delivery_apply.py -q`：`43 passed, 1 skipped`。
- `python -m pytest tests/unit/test_program_service.py -q -k "managed_delivery_apply_request"`：`20 passed, 349 deselected`。
- `python -m ruff check src tests`：通过。

#### 2.4 已知未收口项

- `python -m pytest tests/unit -q` 在 180 秒超时前出现既有失败，首个失败为 `tests/unit/test_branch_manager.py::TestBranchManager::test_switch_to_docs`，临时 git fixture 没有 `main` 分支导致 `git checkout main` 失败；该问题属于 `T179-15` 的 default branch 收口范围，不计入本批 T179-01 ~ T179-03 完成证据。
- `T179-04 Windows release asset P0 smoke` 尚未执行，Batch 1 的 release asset 级闭环仍待后续批次完成。

#### 2.5 回退方式

- 回退上述代码和测试文件即可撤销本批实现；文档状态需同步把 `tasks.md` 中 `T179-01` ~ `T179-03` 改回未完成。

### Batch 2026-04-27-001 | T179-15 默认分支兼容收口

#### 2.1 批次范围

- 覆盖任务：`T179-15` 子项 `default branch`
- 覆盖缺陷：`E2E-WIN-013`
- 影响范围：
  - `src/ai_sdlc/branch/git_client.py`
  - `src/ai_sdlc/branch/branch_manager.py`
  - `src/ai_sdlc/core/branch_inventory.py`
  - `tests/unit/test_branch_manager.py`
  - `tests/unit/test_git_client.py`

#### 2.2 实现摘要

- `GitClient` 新增默认分支解析，优先读取 `origin/HEAD`，其次兼容 `main`/`master`，最后回退到本地单分支仓库的当前分支。
- `revision_divergence` / `branch_divergence` 在未显式传入基线时，改为使用仓库默认分支，避免只在 `main` 存在时才能工作。
- `BranchManager.merge_to_main()` 改为实际合并到仓库默认分支，保留原 API 名称以避免外部调用面变化。
- `branch_inventory` 读取分支偏离信息时，默认跟随仓库默认分支。
- 单元测试去除对 `main` 的环境假设，并新增 `git init --initial-branch=trunk` 的自定义默认分支回归用例。

#### 2.3 验证命令

- `python -m pytest tests/unit/test_branch_manager.py -q`：`25 passed`
- `python -m pytest tests/unit/test_branch_inventory.py -q`：`3 passed`
- `python -m pytest tests/unit/test_git_client.py -q -k "default_branch_name_supports_custom_initial_branch or branch_divergence_against_main_reports_ahead_and_behind or list_worktrees_returns_paths_and_checked_out_branches"`：`3 passed, 10 deselected`
- `python -m ruff check src tests`：通过

#### 2.4 已知未收口项

- `T179-15` 的 PRD warning、无 Git 场景、PowerShell close-check 示例等子项尚未覆盖，本批仅处理默认分支兼容。
- `python -m pytest tests/unit/test_git_client.py -q` 在当前环境偶发于 pytest 临时目录 teardown 阶段被 `KeyboardInterrupt/KeyError` 打断；已确认本次修改相关用例通过，异常堆栈不指向业务断言失败。

#### 2.5 回退方式

- 回退上述代码和测试文件即可撤销默认分支兼容改动；如需同步文档状态，应删除本批记录并恢复状态描述。

### Batch 2026-04-27-002 | Remaining T179 closure and release proof alignment

#### 2.1 批次范围

- 覆盖任务：`T179-04`、`T179-05`、`T179-06`、`T179-07`、`T179-08`、`T179-09`、`T179-10`、`T179-11`、`T179-12`、`T179-13`、`T179-14`、`T179-15`、`T179-16`
- 覆盖缺陷：`E2E-WIN-001`、`E2E-WIN-002`、`E2E-WIN-003`、`E2E-WIN-004`、`E2E-WIN-005`、`E2E-WIN-006`、`E2E-WIN-008`、`E2E-WIN-009`、`E2E-WIN-010`、`E2E-WIN-011`、`E2E-WIN-012`、`E2E-WIN-014`、`E2E-WIN-015`、`E2E-WIN-016`、`E2E-WIN-017`、`E2E-WIN-018`、`E2E-WIN-019`、`E2E-WIN-022`
- 改动范围：
  - `src/ai_sdlc/__main__.py`
  - `src/ai_sdlc/cli/adapter_cmd.py`
  - `src/ai_sdlc/cli/commands.py`
  - `src/ai_sdlc/cli/doctor_cmd.py`
  - `src/ai_sdlc/cli/program_cmd.py`
  - `src/ai_sdlc/cli/sub_apps.py`
  - `src/ai_sdlc/cli/verify_cmd.py`
  - `src/ai_sdlc/cli/workitem_cmd.py`
  - `src/ai_sdlc/core/frontend_browser_gate_runtime.py`
  - `src/ai_sdlc/core/reconcile.py`
  - `src/ai_sdlc/gates/frontend_contract_gate.py`
  - `src/ai_sdlc/gates/pipeline_gates.py`
  - `src/ai_sdlc/integrations/ide_adapter.py`
  - `src/ai_sdlc/routers/existing_project_init.py`
  - `src/ai_sdlc/telemetry/ids.py`
  - `src/ai_sdlc/telemetry/paths.py`
  - `program-manifest.yaml`
  - `tests/integration/test_cli_doctor.py`
  - `tests/integration/test_cli_module_invocation.py`
  - `tests/integration/test_cli_status.py`
  - `tests/integration/test_cli_verify_constraints.py`
  - `tests/integration/test_cli_workitem_close_check.py`
  - `tests/integration/test_cli_workitem_init.py`
  - `tests/integration/test_cli_workitem_plan_check.py`
  - `tests/integration/test_offline_bundle_scripts.py`
  - `tests/unit/test_close_check.py`
  - `tests/unit/test_verify_constraints.py`
  - `docs/releases/v0.7.0.md`
  - `README.md`
  - `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/tasks.md`
  - `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/task-execution-log.md`

#### 2.2 实现摘要

- 修复 `python -m ai_sdlc` 的 Windows/PowerShell 入口行为：仅在顶层 `--help` 或无参时走 ASCII fallback，保留子命令 `--help` 与真实子命令路由。
- adapter/status/doctor/sub-app/verify/program 统一补齐 plain-text surface，并把 ingress/environment、路径输出、UTF-8/Windows 兼容显示与 POSIX path normalization 对齐。
- telemetry scope 目录名与 ID 后缀收紧，避免 Windows 长路径/深层 scope 命名漂移；status truth surface 同步更新 next action 与 inheritance 语义。
- browser gate、contract gate、existing-project init、workitem init/close-check 的路径与 evidence 输出统一为 POSIX-style refs，收敛跨平台 artifact/path drift。
- Git 测试夹具统一改为 `git init --initial-branch=main`，补齐默认分支、自定义默认分支、无 PATH/模块入口、Windows 离线脚本 smoke 的回归用例。
- `docs/releases/v0.7.0.md` 与 `README.md` 增补 Windows `windows-offline-smoke-evidence` 回链，明确 `.zip` smoke 证据来自 `.github/workflows/windows-offline-smoke.yml`，并保留 per-platform evidence 边界。

#### 2.3 统一验证命令

- **验证画像**：`code-change`
- `uv run pytest tests/integration/test_cli_status.py -q -k "latest_scope_ids_do_not_depend_on_manifest_key_order or fallback_latest_scope_ids_ignore_misleading_mtime or promotes_spec_scoped_program_truth_into_workitem_diagnostic or surfaces_stale_apply_artifact_in_frontend_delivery_truth or surfaces_browser_gate_scope_linkage_invalid_in_frontend_delivery_truth"`
- `uv run pytest tests/integration/test_cli_workitem_close_check.py tests/unit/test_close_check.py -q -k "worktree_demo or initial_branch or closeout_not_committed or json_preserves_program_truth_frontend_delivery_status or deep_docs_violation_with_all_docs_flag"`
- `uv run pytest tests/integration/test_offline_bundle_scripts.py -q -k "build_offline_bundle or install_offline or install_online"`
- `uv run pytest tests/integration/test_cli_module_invocation.py tests/integration/test_cli_doctor.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_plan_check.py tests/integration/test_cli_verify_constraints.py -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc run --dry-run`
- `uv run ai-sdlc adapter status`
- `uv run ai-sdlc program truth sync --dry-run`
- `uv run ai-sdlc program truth sync --execute --yes`
- Codex 对话终端未继承 `uv`；按仓库约定使用等价回退命令实际执行：
  - `python -m ruff check src tests`
  - `python -m pytest ...`
  - `python -m ai_sdlc verify constraints`
  - `PYTHONPATH=src python -m ai_sdlc adapter status`
  - `PYTHONPATH=src python -m ai_sdlc run --dry-run`
  - `PYTHONPATH=src python -m ai_sdlc program truth sync --dry-run`
  - `PYTHONPATH=src python -m ai_sdlc program truth sync --execute --yes`

#### 2.4 代码审查

- 审查范围：核对 `python -m ai_sdlc` fallback 不再吞掉子命令 `--help`，确认 `program truth sync --dry-run` 为真实可达命令，确认 Windows CI smoke 证据与 release/docs 的回链一致。
- 审查结论：当前剩余风险集中在 release 证据持续生成依赖 `.github/workflows/windows-offline-smoke.yml` 与后续正式 release archive；源码、测试与入口口径已对齐。

#### 2.5 任务/计划同步状态

- `tasks.md` 16 项任务已全部勾选完成。
- 本批未额外声明 `related_plan`；close-check 维持 “no related_plan declared; skipped”。
- 本批收口目标从“剩余 13 项 + T179-15 局部完成”推进到“16/16 全部完成并统一 release 口径”。

#### 2.6 批次结论

- `T179-04`：Windows release asset smoke 由 `.github/workflows/windows-offline-smoke.yml` 执行 `.zip` 解压、`install_offline.ps1`、`ai-sdlc --help`、`adapter status`、`run --dry-run`，并上传 `windows-offline-smoke-evidence`。
- `T179-05` ~ `T179-07`：相关中文标题降级、业务模板隔离与 artifact summary/gate 语义已由现有实现与回归覆盖，本批仅补正式收口与验证。
- `T179-08` ~ `T179-10`：adapter/telemetry/status/verify/final-proof 语义通过 plain-text surface、truth surface、close-check 回归与模块入口修复完成闭环。
- `T179-11` ~ `T179-13`：PrimeVue/public delivery、enterprise/provider isolation、browser gate baseline/final proof 的证据语义已与 status/program/browser-gate surfaces 对齐。
- `T179-14` ~ `T179-16`：Windows 编码/脚本体验、default branch/PowerShell 前置、release notes 与 release proof 回链已对齐当前发布口径。

#### 2.7 回退方式

- 若需回退本批，撤销上述源码、测试与 release/docs 更新，并将 `tasks.md` 中 `T179-04` ~ `T179-16` 恢复为未完成。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`7049649`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`待最终收口`
