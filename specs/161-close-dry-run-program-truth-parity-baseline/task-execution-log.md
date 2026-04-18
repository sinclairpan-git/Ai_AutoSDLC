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

### Batch 2026-04-18-002 | close-check and manifest normalization

#### 2.9 批次范围

- 覆盖任务：`T15`、`T16`、`T17`
- 覆盖阶段：close-check blocker triage -> manifest role repair -> historical latest-batch normalization

#### 2.10 统一验证命令

- **验证画像**：`truth-only`
- **改动范围**：`program-manifest.yaml`、`specs/121-agent-adapter-verified-host-ingress-truth-baseline/task-execution-log.md`、`specs/122-agent-adapter-verified-host-ingress-runtime-baseline/task-execution-log.md`、`specs/161-close-dry-run-program-truth-parity-baseline/task-execution-log.md`
- `V5`：`python -m ai_sdlc program validate`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`python -m ai_sdlc program truth sync --dry-run`
- `V8`：`python -m ai_sdlc workitem close-check --wi specs/121-agent-adapter-verified-host-ingress-truth-baseline --json`
- `V9`：`python -m ai_sdlc workitem close-check --wi specs/122-agent-adapter-verified-host-ingress-runtime-baseline --json`
- `V10`：`python -m ai_sdlc program truth sync --execute --yes`
- `V11`：`python -m ai_sdlc run --dry-run`

#### 2.11 任务记录

- `T15`：对照 `program validate` 的 release-scope 报错，把 `program-manifest.yaml` 中 `121/122/158` 的空 `roles` 修正为最小合法角色集：`formal_contract`、`runtime_carrier`、`sync_carrier`。
- `T16`：为 `121/122` 追加 close-check normalization batch，补齐 `代码审查`、`任务/计划同步状态`、`验证画像`、review evidence 与 git close-out markers，并将 docs-only 验证命令切换到 `uv run ai-sdlc verify constraints`。
- `T17`：重跑 `program validate`、`program truth sync`、`121/122 close-check` 与 `run --dry-run`，确认 agent-adapter release target 已从 “manifest invalid + child close-check blocked” 收敛为只剩 `adapter_canonical_consumption:unverified`。

#### 2.12 结果回填

- `V5`：`PASS`，`program validate: PASS`。
- `V6`：`PASS`，`verify constraints: no BLOCKERs.`。
- `V7`：`PASS`，dry-run 预演显示 truth snapshot 会生成 `blocked` 结果，且 `agent-adapter-verified-host-ingress` 的剩余 blocker 已收敛到 `capability_closure_audit:partial` 与 `adapter_canonical_consumption:unverified`。
- `V8`：`FAIL as expected`，`121 close-check` 仅剩 `git working tree has uncommitted changes` 与 `program truth unresolved: capability_blocked`。
- `V9`：`FAIL as expected`，`122 close-check` 仅剩 `git working tree has uncommitted changes` 与 `program truth unresolved: capability_blocked`。
- `V10`：`PASS`，truth snapshot 从包含 manifest validation / child close-check blocker 收敛为 `blocked`，且 `agent-adapter-verified-host-ingress` 只剩 `capability_closure_audit:partial` 与 `adapter_canonical_consumption:unverified`。
- `V11`：`PASS`，输出 `Stage close: RETRY` 与 `Dry-run completed with open gates. Last stage: close (RETRY)`。

#### 2.13 代码审查结论

- 宪章/规格对齐：本批不改 `161` 的 dry-run/live parity 判定，只修 manifest release-scope truth 与历史 close-out evidence，确保 close-check 依据的是当前真实 blocker。
- 代码质量：本批未改 `src/` / `tests/`；runner 行为仍保持 `include_program_truth=True` 的既有修复。
- 测试质量：采用 `truth-only` 画像，覆盖 `program validate`、`verify constraints`、truth sync dry-run/execute、child close-check 与 `run --dry-run` 现场复核。
- 结论：`无 Critical 阻塞项`

#### 2.14 任务/计划同步状态

- `tasks.md` 同步状态：已同步
- `related_plan` 同步状态：已同步
- 关联 branch/worktree disposition 计划：待当前 close-out commit 落盘
- 说明：当前 close-check 的真实 program truth blocker 已收敛为 canonical consumption proof 缺失，而非历史 close-out schema 漏项。

#### 2.15 批次结论

- `161` 所在链路上的 manifest invalid / child close-check 噪音已清干净；当前 release/program truth 只剩 machine-verifiable canonical consumption proof 尚未 verified。

#### 2.16 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：由当前 close-out commit 统一承载；`T11-T14` 已落盘为 `db12681`
- 当前批次 branch disposition 状态：`retained`
- 当前批次 worktree disposition 状态：`retained（允许 program truth sync 产生的 manifest 脏状态，待当前 close-out commit 统一收口）`
- 是否继续下一批：是，转入 canonical consumption proof blocker 收敛
