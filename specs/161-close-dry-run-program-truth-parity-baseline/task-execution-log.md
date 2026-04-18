# 任务执行日志：Close Dry Run Program Truth Parity Baseline

**功能编号**：`161-close-dry-run-program-truth-parity-baseline`
**创建日期**：2026-04-18
**状态**：收口中

## 1. 归档规则

- 本文件记录 `161` 的 dry-run/live close parity 修复过程。
- 每次回填都必须对应真实命令、真实测试与真实 runner 行为。

## 2. 批次记录

### Batch 2026-04-18-001 | T11-T14

#### 2.1 批次范围

- 覆盖任务：`T11`、`T12`、`T13`、`T14`
- 覆盖阶段：dry-run parity root cause -> red/green -> formal sync

#### 2.2 统一验证命令

- `R0`：`python -m ai_sdlc adapter status`
- `R1`：`python -m ai_sdlc run --dry-run`
- `R2`：`python -m ai_sdlc workitem close-check --wi specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline --json`
- `R3`：`uv run pytest tests/unit/test_runner_confirm.py -k "dry_run_includes_program_truth_close_check_fanout" -q`
- `V1`：`uv run pytest tests/unit/test_runner_confirm.py -k "dry_run_includes_program_truth_close_check_fanout or dry_run_skips_program_truth_audit_surface" -q`
- `V2`：`uv run pytest tests/integration/test_cli_run.py -k "stale_program_truth" -q`
- `V3`：`python -m ai_sdlc adapter status`
- `V4`：`python -m ai_sdlc run --dry-run`

#### 2.3 任务记录

- `T11`：将 `test_close_context_dry_run_skips_program_truth_close_check_fanout` 改为必须包含 `include_program_truth=True` 的红灯测试，直接锁定 runner 参数分叉。
- `T12`：新增 CLI 集成测试，通过 monkeypatch 的 close-check blocker 验证 `run --dry-run` 在 close 阶段会输出 `Stage close: RETRY`。
- `T13`：在 `SDLCRunner._enrich_close_context()` 中把 dry-run close-check fanout 改为始终包含 program truth，同时保留 dry-run 不启用独立 audit surface。
- `T14`：回填 `161` formal docs、执行日志与开发总结，记录当前框架入口状态。

#### 2.4 结果回填

- `R0`：`PASS`，观测到 `adapter_ingress_state=verified_loaded` 且 `adapter_canonical_consumption_result=unverified`。
- `R1`：`PASS but incorrect`，修复前输出 `Stage close: PASS` 与 `Pipeline completed. Stage: close`，暴露 dry-run/live close 分叉。
- `R2`：`FAIL as expected`，`close-check` 返回 `BLOCKER: program truth unresolved: truth_snapshot_stale`，证明 live close 已被 program truth 拦截。
- `R3`：`FAIL as expected`，断言 `captured["include_program_truth"] is True` 时得到 `False is True`。
- `V1`：`PASS`，`2 passed, 18 deselected`
- `V2`：`PASS`，`1 passed, 16 deselected`
- `V3`：`PASS`，`adapter_ingress_state=verified_loaded`、`adapter_canonical_consumption_result=unverified`，说明当前仓库仍处在“宿主接入已验证但 canonical consumption proof 未验证”状态。
- `V4`：`PASS`，输出 `Stage close: RETRY` 与 `Dry-run completed with open gates. Last stage: close (RETRY)`，未再出现错误的 `Pipeline completed. Stage: close`。

#### 2.5 代码审查结论

- 宪章/规格对齐：修复只针对 close-check fanout，不改变 host ingress 或 truth rule 本身。
- 代码质量：实现收敛在 runner 一处参数，不引入额外条件分支。
- 测试质量：同时覆盖 `_build_context()` 参数层和 CLI `run --dry-run` 用户可见层。
- 结论：满足本任务的最小闭环。

#### 2.6 任务/计划同步状态

- `tasks.md` 同步状态：已同步
- `related_plan` 同步状态：已同步
- 关联 branch/worktree disposition 计划：待最终收口
- 说明：当前尚未为 `161` 单独提交 commit。

#### 2.7 批次结论

- `161` 已把 close dry-run 与 live close 在 program truth fanout 上的语义拉齐；剩余工作只有最终框架核验与后续提交。

#### 2.8 归档后动作

- 已完成 git 提交：否
- 提交哈希：待提交
- 当前批次 branch disposition 状态：待最终收口
- 当前批次 worktree disposition 状态：待最终收口
- 是否继续下一批：是，进入最终验证
