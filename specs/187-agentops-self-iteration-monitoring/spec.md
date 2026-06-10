# 功能规格：AgentOps self-iteration monitoring

**功能编号**：`187-agentops-self-iteration-monitoring`
**创建日期**：2026-05-27
**状态**：草稿
**输入**：将 Ai_AutoSDLC 自迭代运行过程上报到本地 AgentOps，AgentOps 只作为旁路观测与质量分析 sink，不替代 Ai_AutoSDLC 自身治理。参考：`docs/engineering/ai-sdlc-agentops-e2e-smoke.md`

**范围**：本工作项覆盖 Ai_AutoSDLC runtime reporter 对本地 AgentOps Gateway 的自迭代上报字段补齐、真实 run 上报验收、receipt/trace/evidence/console 双边对账，以及由 Ops 观测结果反推框架约束优化建议。

**明确不覆盖**：不让 AgentOps 决定 stage/gate/task guard 放行；不发送或伪造 `X-AgentOps-*` 生产身份头；不把 Gateway token 写入 JSON payload、outbox、receipt、diagnostic 或 handoff。

## 用户场景与测试

### 用户故事 1 - 旁路上报自迭代运行事实（优先级：P0）

作为 Ai_AutoSDLC 维护者，我希望 `ai-sdlc run` 在遵守自身治理的同时，把 stage/gate/task guard/outbox receipt 摘要上报到本地 AgentOps，以便分析框架自迭代质量。

**独立测试**：focused integration test 验证 run reporter 生成的 AgentOps batch 包含 gate payload、task guard 观测字段、可选 producer identity env，且 dry-run 不产生外部 POST。

**验收场景**：

1. **Given** 配置了本地 Gateway endpoint 和 Bearer token，**When** 执行真实 `uv run ai-sdlc run`，**Then** SDLC 自身 close gate 仍按原规则通过或阻断，AgentOps 仅收到旁路 runtime event。
2. **Given** run 被 close gate 阻断，**When** AgentOps 接收 batch，**Then** receipt summary 必须显示 delivered 或等价成功，且 rejected/stale/dlq 不得静默吞掉。

### 用户故事 2 - 支持 Ops 观测质量分析字段（优先级：P0）

作为 Ops 分析者，我希望每个 SDLC gate event 带上 run/trace/span、stage、workitem、executable task、task guard、路径范围、blocking reason 和 rule results，以便定位哪些框架约束需要优化。

**独立测试**：`tests/integration/test_cli_run.py` 捕获 batch，断言 payload 包含 `task_title`、`changed_paths`、`allowed_paths`、`forbidden_paths`、`guard_result`、`blocking_reason`。

**验收场景**：

1. **Given** run reporter 构造 gate fact，**When** 发送到 AgentOps，**Then** payload 支持 `run_id / trace_id / span_id / parent_span_id / stage_name / status / workitem / executable_task_id / task_guard_state / rule_results`。
2. **Given** 本地设置 `AGENTOPS_PRODUCER_ID` 等身份 env，**When** 构造 event envelope，**Then** envelope 使用这些 producer identity 字段，但 token 仍只存在于 Authorization header。

### 用户故事 3 - 从 Ops readback 总结框架优化方向（优先级：P1）

作为框架维护者，我希望每轮自迭代后能从 AgentOps trace/evidence/console/readiness 中总结失败 stage、证据缺口、outbox 状态和 guard 质量问题。

**独立测试**：人工 live smoke 对账本地 AgentOps API、PostgreSQL receipt、Gateway audit 和 Console workbench。

**验收场景**：

1. **Given** AgentOps 返回 evidence summary，**When** summary 显示 `missing_dimensions`，**Then** 本工作项输出对应的 evidence readiness 优化建议。
2. **Given** close gate 反复 retry，**When** Ops trace 可读，**Then** 输出应说明失败 rule、blocking reason 和建议的 SDLC 框架改进。

## 需求

- **FR-187-001**：`ai-sdlc agentops doctor --json` 必须只输出 token 是否存在，不输出 token 值。
- **FR-187-002**：真实 `ai-sdlc run` 必须保留 AI-SDLC 自身 stage/gate/task guard 语义；AgentOps 不得成为放行来源。
- **FR-187-003**：run reporter 必须持久化 outbox 和 receipt summary，并在 non-dry-run 时尝试发送到配置的 Gateway。
- **FR-187-004**：gate payload 必须支持 task title、changed paths、allowed paths、forbidden paths、guard result、blocking reason 和 rule results。
- **FR-187-005**：run reporter 必须允许通过 `AGENTOPS_PRODUCER_ID`、`AGENTOPS_RUNTIME_ID`、`AGENTOPS_CREDENTIAL_ID`、`AGENTOPS_KEY_ID` 配置 envelope identity 字段。
- **FR-187-006**：发送 HTTP 请求时不得直接发送或伪造 `X-AgentOps-*` 生产身份头。
- **FR-187-007**：如 receipt 出现 rejected/stale/dlq，CLI 和 diagnostic 必须暴露 error_code、诊断摘要和 retry guidance。
- **FR-187-008**：交付总结必须包含 doctor/status/receipt/trace/evidence/console readback，以及 SDLC 框架自迭代质量建议。
- **FR-187-009**：每个 AgentOps span 必须稳定包含 run_id、trace_id、span_id、parent_span_id、stage_name、span_kind、operation_name、status/status_code、workitem、executable_task_id、task_title、时间、retryable、error_code、blocking/failure reason 和 next_action。
- **FR-187-010**：failed/error/blocked span 必须补齐 failed_conditions、open_gates、failed_command、expected_result、actual_result_summary、blocking_reason、retry_guidance、diagnostic_ref 和 evidence_ref。
- **FR-187-011**：`ai-sdlc run` 必须按 stage 产出 stage-level event，并把 verify 映射为 test 观测阶段；后续 merge/release 通过 report_type 与工程指标继续接入。
- **FR-187-012**：task guard 上报必须是 summary-only，不上传 raw path list，只上传 allowed/forbidden/changed/blocked counts、hash、blocked_paths_summary、guard_policy_version、missing_executable_task 和 candidate_fix_summary。
- **FR-187-013**：runtime report 必须标记 report_type，取值限定为 real_run、dry_run_retry、readiness_fixture、live_smoke。
- **FR-187-014**：工程效果指标应包含 test/failed_test、CI、review finding、retry、duration、token/cost summary、commit_sha、branch、pr_number。
- **FR-187-015**：`verified_loaded` 只能作为 adapter_diagnostic_state，不得作为代码修改授权、L5 eligibility 或 outbox delivered 主门禁。

## 成功标准

- **SC-187-001**：focused pytest 与 ruff 通过。
- **SC-187-002**：真实 `uv run ai-sdlc run` 产生新的 AgentOps outbox，并经本地 Gateway delivered。
- **SC-187-003**：AgentOps Postgres、trace、evidence summary、Gateway audit 和 Console workbench 能按同一 batch/run 对账。
- **SC-187-004**：token 值不出现在 `.ai-sdlc/agentops`、handoff 或 CLI JSON 输出中。
- **SC-187-005**：真实 `ai-sdlc run` 的最新 outbox 包含 stage-level span；若 close gate failed，AgentOps 能读取 failed_conditions、blocking_reason 和 next_action。
- **SC-187-006**：task guard blocked 时，AgentOps 能读取 missing_executable_task 或 blocked_paths_summary；receipt 继续保留 accepted/deduplicated/rejected/dlq/stale 语义，且 rejected/stale/dlq 不静默吞掉。
