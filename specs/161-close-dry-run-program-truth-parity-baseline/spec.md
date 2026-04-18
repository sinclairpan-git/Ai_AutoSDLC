# 功能规格：Close Dry Run Program Truth Parity Baseline

**功能编号**：`161-close-dry-run-program-truth-parity-baseline`
**创建日期**：2026-04-18
**状态**：收口中
**输入**：`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/cli/run_cmd.py`、`tests/unit/test_runner_confirm.py`、`tests/integration/test_cli_run.py`

## 问题定义

`160` 已把 canonical consumption proof 接入 release/program truth，但随后验证发现 close dry-run 与 live close 仍然存在一个语义分叉：

- `python -m ai_sdlc adapter status` 已能给出 `adapter_canonical_consumption_result=unverified`
- live `workitem close-check` 会因为 `truth_snapshot_stale` 阻塞 close
- 但 `SDLCRunner._enrich_close_context()` 在 dry-run 下把 `include_program_truth` 关闭，导致 close-check 不消费 program truth fanout

这会产生错误信号：dry-run 可能报告 `Stage close: PASS`，而 live close 仍被 machine-verifiable program truth blocker 拦住。`161` 的目标就是把这条分叉拉回同一条 close 语义。

## 范围

- **覆盖**：
  - 让 dry-run 下的 `run_close_check()` 仍消费 `include_program_truth`
  - 保持 CLI `run --dry-run` 对 stale program truth blocker 的 close 结果与 live close 一致
  - 以单测和 CLI 集成测试锁定该语义
  - 回填 `161` formal docs 与执行证据
- **不覆盖**：
  - 在 dry-run 中启用独立 `_program_truth_gate_surface()` 审计面
  - 修改 adapter ingress / `verified_loaded` 规则
  - 对 stale truth 自动执行 `program truth sync`

## 用户故事与验收

### US-161-1 — Maintainer 需要 dry-run 不再跳过 close truth blocker

作为 **maintainer**，我希望 `ai-sdlc run --dry-run` 在 close 阶段也消费 program truth fanout，这样 dry-run 和 live close 对 unresolved truth 的判定不会再分叉。

**验收**：

1. **Given** close dry-run 调用 `run_close_check()`，**When** `_build_context("close", dry_run=True)` 构建上下文，**Then** `include_program_truth` 必须为 `True`
2. **Given** CLI dry-run 经过 close 阶段，**When** close-check 因 program truth blocker 返回失败，**Then** CLI 必须输出 `Stage close: RETRY` 而不是 `Pipeline completed`

### US-161-2 — Reviewer 需要 dry-run 只补齐 close-check fanout，不扩大审计面

作为 **reviewer**，我希望本次修复只恢复 dry-run 对 close-check 的 program truth 消费，而不顺手把更重的独立审计面也带进 dry-run。

**验收**：

1. **Given** dry-run close，**When** runner 构建 close context，**Then** `_program_truth_gate_surface()` 仍不应作为 dry-run 阶段检查项出现
2. **Given** live close，**When** 非 dry-run 运行，**Then** 既有 program truth audit surface 语义保持不变

## 功能需求

- **FR-161-001**：`SDLCRunner._enrich_close_context()` 在 dry-run 下调用 `run_close_check()` 时必须传入 `include_program_truth=True`
- **FR-161-002**：dry-run close 的 verdict 必须能反映 close-check 返回的 program truth blocker
- **FR-161-003**：dry-run 不得因此自动启用独立 `program_truth_audit_required` surface
- **FR-161-004**：CLI 路径必须有针对该行为的集成测试，避免再次回退到“dry-run PASS / live blocked”分叉

## 成功标准

- **SC-161-001**：`tests/unit/test_runner_confirm.py` 中的 dry-run close fanout 测试通过
- **SC-161-002**：`tests/integration/test_cli_run.py` 中的 dry-run stale program truth CLI 测试通过
- **SC-161-003**：`python -m ai_sdlc run --dry-run` 在当前仓库不再绕过 close truth blocker，并输出 open gates 结果
