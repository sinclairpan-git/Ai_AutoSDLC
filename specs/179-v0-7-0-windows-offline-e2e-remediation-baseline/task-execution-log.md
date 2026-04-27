# 任务执行日志：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**创建日期**：2026-04-24
**状态**：Batch 1 已收口，T179-15 默认分支兼容子项已补齐，仍待其余批次继续完成

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
