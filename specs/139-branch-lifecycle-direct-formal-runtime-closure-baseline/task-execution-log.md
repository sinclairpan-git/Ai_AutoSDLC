# 执行记录：Branch Lifecycle Direct Formal Runtime Closure Baseline

**功能编号**：`139-branch-lifecycle-direct-formal-runtime-closure-baseline`
**日期**：2026-04-14
**状态**：runtime closure 已完成；bounded focused verification 已通过；installed-wheel smoke 受网络限制待补跑

## Batch 2026-04-14-001 | Carrier derivation and runtime audit

- 核对 `007/008` formal truth 与当前 `branch inventory/traceability/close-check/branch-check/readiness`、`direct-formal scaffold/workitem init`、相关 unit/integration tests，确认 branch lifecycle/direct-formal runtime 已在仓库中形成真实闭环
- 确认 `120/T44` 的关键缺口是 implementation carrier 缺失，而不是 branch lifecycle truth、direct-formal entry 或 CLI surfaces 仍然不存在
- 新建 `139` formal carrier，固定 `T44` 的问题定义、实现边界、非目标与下游分界
- 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `139` 推进到 `140`

## Batch 2026-04-14-002 | Focused verification and backlog honesty sync

- 运行 fresh focused verification，覆盖 branch lifecycle inventory/disposition、direct-formal scaffold、CLI init/close-check/branch-check 与 bounded governance/readiness surfaces
- 本批不新增 production 代码；closure 主证据采用排除 network-limited installed-wheel smoke 的 bounded suite，fresh verification 结果用于证明 `007/008` 的 runtime closure 在当前工作区依然成立
- `uv run pytest tests/unit/test_branch_inventory.py tests/unit/test_workitem_scaffold.py tests/unit/test_command_names.py tests/unit/test_verify_constraints.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_plan_check.py tests/integration/test_cli_workitem_link.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_init.py -q`
  - `1 failed, 223 passed in 51.37s`
  - 失败点：`tests/integration/test_cli_workitem_init.py::TestCliWorkitemInit::test_workitem_init_succeeds_from_installed_wheel_runtime`
  - 原因：当前环境无法连接 `https://pypi.org/simple/hatchling/`，installed-wheel smoke 无法完成 build dependency 拉取
- `uv run pytest tests/unit/test_branch_inventory.py tests/unit/test_workitem_scaffold.py tests/unit/test_command_names.py tests/unit/test_verify_constraints.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_plan_check.py tests/integration/test_cli_workitem_link.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_init.py -q -k 'not installed_wheel_runtime'`
  - `223 passed, 1 deselected in 47.40s`
  - 该命令作为 `T44` 当前批次的 bounded closure verification 主证据
- `uv run ai-sdlc verify constraints`
  - `verify constraints: no BLOCKERs.`
- `uv run ai-sdlc program validate`
  - `program validate: PASS`
- `git diff --check`
  - `clean`

## 本批结论

- `139` 已把 `007/008` 的 branch lifecycle/direct-formal runtime 正式收束为 `T44` implementation carrier
- `120/T44` 不再需要继续以 `formal_only` 假设 “repo mutation/entry runtime 尚未落地”
- 当前边界仍然保持 branch lifecycle read-only truth 与 direct-formal single canonical entry，不扩张为自动 branch mutation 或双轨文档体系
- 当前环境仍未满足 installed-wheel smoke 所需的外网依赖拉取条件；该限制已显式记录，不影响本批对 `T44` 主链 runtime closure 的 focused 证据
- `120/T44` 当前继续保留 `partial`，仅表示 tranche/root closure 维持保守态，不表示 `139` 仍缺实现 carrier
