# 执行记录：Branch Lifecycle Direct Formal Runtime Closure Baseline

**功能编号**：`139-branch-lifecycle-direct-formal-runtime-closure-baseline`
**日期**：2026-04-14
**状态**：runtime closure 已完成；focused verification 已通过

## Batch 2026-04-14-001 | Carrier derivation and runtime audit

- 核对 `007/008` formal truth 与当前 `branch inventory/traceability/close-check/branch-check/readiness`、`direct-formal scaffold/workitem init`、相关 unit/integration tests，确认 branch lifecycle/direct-formal runtime 已在仓库中形成真实闭环
- 确认 `120/T44` 的关键缺口是 implementation carrier 缺失，而不是 branch lifecycle truth、direct-formal entry 或 CLI surfaces 仍然不存在
- 新建 `139` formal carrier，固定 `T44` 的问题定义、实现边界、非目标与下游分界
- 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `139` 推进到 `140`

## Batch 2026-04-14-002 | Focused verification and backlog honesty sync

- 运行 fresh focused verification，覆盖 branch lifecycle inventory/disposition、direct-formal scaffold、CLI init/close-check/branch-check 与 bounded governance/readiness surfaces
- 本批不新增 production 代码；fresh verification 结果用于证明 `007/008` 的 runtime closure 在当前工作区依然成立
- `uv run pytest tests/unit/test_branch_inventory.py tests/unit/test_workitem_scaffold.py tests/unit/test_command_names.py tests/unit/test_verify_constraints.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_plan_check.py tests/integration/test_cli_workitem_link.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_init.py -q`
  - `224 passed in 55.45s`
- `uv run ai-sdlc verify constraints`
  - `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program validate`
  - `program validate: PASS`
- `git diff --check`
  - `clean`

## Batch 2026-04-14-003 | Installed-wheel smoke de-network remediation

- 将 `pyproject.toml` 的 build backend 从外部 `hatchling` 收敛为仓库内 `packaging_backend.py`，消除 `uv build` 对 `pypi.org` 的硬依赖
- 新增 `tests/unit/test_packaging_backend.py`，锁定 wheel 中的 `entry_points.txt` 与 `workitem init` 所需模板映射
- 将 installed-wheel smoke 的依赖注入 helper 收紧为第三方依赖 overlay，不再把当前开发环境里的 `ai_sdlc` 包暴露给临时 venv
- `uv run pytest tests/integration/test_cli_workitem_init.py::TestCliWorkitemInit::test_workitem_init_succeeds_from_installed_wheel_runtime tests/unit/test_packaging_config.py tests/unit/test_packaging_backend.py -q`
  - `4 passed in 10.92s`
- `uv run pytest tests/unit/test_workitem_scaffold.py tests/unit/test_packaging_config.py tests/unit/test_packaging_backend.py tests/integration/test_cli_workitem_init.py tests/integration/test_offline_bundle_scripts.py -q`
  - `18 passed in 10.75s`
- `uv build --wheel --out-dir /tmp/ai-sdlc-build-check`
  - `Successfully built /tmp/ai-sdlc-build-check/ai_sdlc-0.6.0-py3-none-any.whl`

## 本批结论

- `139` 已把 `007/008` 的 branch lifecycle/direct-formal runtime 正式收束为 `T44` implementation carrier
- `120/T44` 不再需要继续以 `formal_only` 假设 “repo mutation/entry runtime 尚未落地”
- 当前边界仍然保持 branch lifecycle read-only truth 与 direct-formal single canonical entry，不扩张为自动 branch mutation 或双轨文档体系
- installed-wheel smoke 已不再依赖外部 `hatchling` 下载，当前环境可直接完成真实 wheel build + 安装态 smoke
- `120/T44` 当前继续保留 `partial`，仅表示 tranche/root closure 维持保守态，不表示 `139` 仍缺实现 carrier

## Batch 2026-04-18-004 | Current close-check grammar normalization

### 2.1 批次范围

- 覆盖任务：`latest-batch grammar normalization`
- 覆盖阶段：historical carrier close-out evidence regularization
- 预读范围：`spec.md`、`plan.md`、`tasks.md`、`specs/164-*`、当前 `program truth audit`
- 当前结论：`139` 的 runtime closure 事实未变；需要补齐 latest batch 让 current close-check 直接消费

### 2.2 统一验证命令

- **验证画像**：`truth-only`
- **改动范围**：`specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline/task-execution-log.md`
- `V1`：`python -m ai_sdlc workitem close-check --wi specs/139-branch-lifecycle-direct-formal-runtime-closure-baseline --json`
- `V2`：`python -m ai_sdlc program truth sync --dry-run`
- `V3`：`python -m ai_sdlc program truth audit`
- `V4`：`git diff --check`

### 2.3 任务记录

- 改动范围：`task-execution-log.md`
- 改动内容：
  - 追加 current close-check grammar 所需字段，保留 `2026-04-14` runtime verification 与 installed-wheel smoke 结论不变
  - 记录 fresh `close-check` 暴露的 blocker 已从“旧版 latest batch 缺字段 + stale truth snapshot”收敛为“latest batch 尚未 git close-out”
- 新增/调整的测试：无
- 执行的命令：`V1`、`V2`、`V3`、`V4`
- 测试结果：
  - `V2`：`ready`
  - `V3`：`state=ready / snapshot state=fresh`
  - `V4`：`clean`
  - `V1`：当前仅剩 `git close-out verification failed: latest batch is not marked as git committed`
- 是否符合任务目标：是；已把 blocker 从“格式缺失”显式化

### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：本批只正规化 historical carrier 的 close-out grammar，不改写 branch lifecycle/direct-formal runtime 边界
- 代码质量：无 production 代码变更
- 测试质量：使用 `close-check + truth audit + diff hygiene` 复核 latest batch 可消费性
- 结论：latest batch 已满足 current grammar 与 fresh truth 要求，剩余 blocker 只与本批提交状态相关

### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：无需变更；历史任务分解仍然成立
- `related_plan` 同步状态：无需变更；本批只补 close-out evidence
- 关联 branch/worktree disposition 计划：沿用当前 branch/worktree，和 `164` 同批收口
- 说明：`139` 本批作为 `164` 的 supporting carrier，不派生新的 implementation scope

### 2.6 批次结论

- `139` 的当前 blocker 已从“runtime 是否存在”收敛为“本批尚未完成 git close-out”

### 2.7 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：`retained`
- 当前批次 worktree disposition 状态：`retained`
- 是否继续下一批：否；等待 `164` 同批 close-out
