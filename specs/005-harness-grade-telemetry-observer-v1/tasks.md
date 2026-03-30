# 任务分解：Harness-Grade Telemetry & Observer V1

**编号**：`005-harness-grade-telemetry-observer-v1` | **日期**：2026-03-30  
**来源**：plan.md + spec.md（FR-005-001 ~ FR-005-018 / SC-005-001 ~ SC-005-006）

---

## 分批策略

```text
Batch 1: formal work item freeze + shared kernel contracts
Batch 2: profile/mode binding + source-closure / hard-fail baseline
Batch 3: deterministic collector baseline
Batch 4: async observer baseline
Batch 5: governance consumption at verify/close/release
Batch 6: bounded surfaces + compatibility smoke
```

---

## Batch 1：formal work item freeze + shared kernel contracts

### Task 1.1 冻结 V1 must-before-v1 决策并回写正式真值

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md, docs/superpowers/plans/2026-03-30-harness-grade-telemetry-observer-v1.md, specs/005-harness-grade-telemetry-observer-v1/spec.md, specs/005-harness-grade-telemetry-observer-v1/plan.md, specs/005-harness-grade-telemetry-observer-v1/tasks.md
- **可并行**：否
- **验收标准**：
  1. V1 manual telemetry surface 明确锁定为最小 CLI。
  2. `incident report` 在 V1 明确锁定为 `contract-preserved deferred artifact`。
  3. 正式 work item 文档与 superpowers design/plan 对齐，不再存在 design/plan 漂移。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 1.2 冻结 shared kernel contracts 与 project-config 默认值

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/models/project.py, src/ai_sdlc/templates/project-config.yaml.j2, src/ai_sdlc/telemetry/enums.py, src/ai_sdlc/telemetry/contracts.py, tests/unit/test_project_config.py, tests/unit/test_telemetry_contracts.py
- **可并行**：否
- **验收标准**：
  1. `profile`、`mode`、`confidence`、`trigger_point_type`、`source_closure_status`、`governance_review_status` 等枚举形成单一来源。
  2. `TraceContext`、mode change record、gate payload 最小合同落盘。
  3. `ProjectConfig` 持久化 `telemetry_profile` / `telemetry_mode` 默认值。
- **验证**：`uv run pytest tests/unit/test_project_config.py tests/unit/test_telemetry_contracts.py -q`

---

## Batch 2：profile/mode binding + source-closure / hard-fail baseline

### Task 2.1 绑定 profile / mode / trace context 到运行时

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：src/ai_sdlc/telemetry/policy.py, src/ai_sdlc/telemetry/runtime.py, src/ai_sdlc/core/runner.py, src/ai_sdlc/core/dispatcher.py, tests/unit/test_telemetry_policy.py, tests/unit/test_runner_confirm.py, tests/integration/test_cli_run.py
- **可并行**：否
- **验收标准**：
  1. `self_hosting` / `mode` 在 `session/run` 启动时显式绑定。
  2. mode 切换记录最少包含 `old_mode`、`new_mode`、`changed_at`、`changed_by`、`reason`、`applicable_scope`。
  3. observer trigger point 与 gate consumption point 在运行时元数据上可区分。
- **验证**：`uv run pytest tests/unit/test_telemetry_policy.py tests/unit/test_runner_confirm.py tests/integration/test_cli_run.py -q`

### Task 2.2 强化 source closure 与 hard-fail 分类

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/telemetry/store.py, src/ai_sdlc/telemetry/resolver.py, src/ai_sdlc/telemetry/writer.py, src/ai_sdlc/telemetry/governance_publisher.py, tests/unit/test_telemetry_store.py, tests/unit/test_telemetry_publisher.py, tests/unit/test_telemetry_governance.py
- **可并行**：否
- **验收标准**：
  1. `source_closure_status` 能稳定表达 `unknown / incomplete / closed`。
  2. `hard-fail default` 与 `policy-overridable hard-fail candidate` 各至少有 1 个正测和 1 个负测。
  3. 代表场景至少覆盖 `raw trace` 根不可写、主键链缺失、`source closure` 判定器损坏。
  4. governance lifecycle 变化不改写来源引用。
- **验证**：`uv run pytest tests/unit/test_telemetry_store.py tests/unit/test_telemetry_publisher.py tests/unit/test_telemetry_governance.py -q`

---

## Batch 3：deterministic collector baseline

### Task 3.1 落地 traced wrappers 与 deterministic collectors

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/telemetry/collectors.py, src/ai_sdlc/cli/trace_cmd.py, src/ai_sdlc/cli/main.py, src/ai_sdlc/telemetry/runtime.py, tests/unit/test_telemetry_collectors.py, tests/integration/test_cli_trace.py
- **可并行**：否
- **验收标准**：
  1. `command execution`、`test result`、`patch apply` 三类 traced wrapper 能落成 canonical facts。
  2. collector 不产生 observer/gate 语义。
  3. `trace context propagation` 可通过 CLI traced wrapper 证明。
- **验证**：`uv run pytest tests/unit/test_telemetry_collectors.py tests/integration/test_cli_trace.py -q`

### Task 3.2 把 execute / parallel / native 边界接入 collector baseline

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：src/ai_sdlc/core/executor.py, src/ai_sdlc/parallel/engine.py, src/ai_sdlc/backends/native.py, tests/unit/test_executor.py, tests/unit/test_parallel.py
- **可并行**：否
- **验收标准**：
  1. execute 阶段只写 tool / collector facts，不写 workflow-owned 事件。
  2. `worker lifecycle` 与 `worker_id` 能稳定进入事实层。
  3. Native backend 的“实际执行交给外部 agent”边界被显式记录，而不是被误当成已观测完成。
- **验证**：`uv run pytest tests/unit/test_executor.py tests/unit/test_parallel.py -q`

---

## Batch 4：async observer baseline

### Task 4.1 引入可再生 observer pipeline

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：src/ai_sdlc/telemetry/observer.py, src/ai_sdlc/telemetry/evaluators.py, src/ai_sdlc/telemetry/runtime.py, tests/unit/test_telemetry_observer.py
- **可并行**：否
- **验收标准**：
  1. observer 在 `step / batch end` 后异步触发，不先于 raw trace append。
  2. 同一事实层 + 同一 `observer_version / policy / profile / mode` 下结果可重复计算。
  3. `coverage evaluation`、`constraint / mismatch finding`、`unknown / unobserved / coverage_gap` 均有正式对象。
- **验证**：`uv run pytest tests/unit/test_telemetry_observer.py -q`

### Task 4.2 把 observer 结果接成最小 governance outputs

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：src/ai_sdlc/telemetry/detectors.py, src/ai_sdlc/telemetry/generators.py, tests/unit/test_telemetry_governance.py
- **可并行**：否
- **验收标准**：
  1. V1 至少产出 `violation`、`audit summary`、`gate decision payload`。
  2. `evaluation summary` 与 `incident report` 保持 contract-preserved，但不强制作为 V1 正式输出启用。
  3. 解释层与治理层不回写事实层。
- **验证**：`uv run pytest tests/unit/test_telemetry_governance.py -q`

---

## Batch 5：verify / close / release consumption

### Task 5.1 把 verify 接到高置信治理消费

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T42
- **文件**：src/ai_sdlc/core/verify_constraints.py, src/ai_sdlc/cli/verify_cmd.py, tests/unit/test_verify_constraints.py, tests/integration/test_cli_verify_constraints.py
- **可并行**：否
- **验收标准**：
  1. verify 只消费带 `confidence`、`evidence refs`、`source closure`、observer 条件的治理对象。
  2. observer / closure 不足时退化为 advisory 或明确缺口，而不是直接 blocker。
  3. gate 不直接扫 raw trace。
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`

### Task 5.2 把 close / release 接到相同治理口径

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：src/ai_sdlc/core/close_check.py, src/ai_sdlc/core/release_gate.py, tests/unit/test_close_check.py, tests/unit/test_gates.py, tests/integration/test_cli_workitem_close_check.py
- **可并行**：否
- **验收标准**：
  1. `close / release` 与 verify 使用同一套 gate-capable payload 最小条件。
  2. `execute` 默认仍 advisory-only。
  3. `source closure` 不成立时只能停留在 `reviewed / draft / blocked` 等状态，不得伪装成已 published。
  4. 至少有 1 条 integration smoke 证明 release 面复用相同最小条件，且不会直接扫描 raw trace。
- **验证**：`uv run pytest tests/unit/test_close_check.py tests/unit/test_gates.py tests/integration/test_cli_workitem_close_check.py -q`

---

## Batch 6：bounded surfaces + compatibility smoke

### Task 6.1 收束 manual telemetry surface 与 bounded read-only surfaces（对应 FR-005-015 / FR-005-016）

- **任务编号**：T61
- **优先级**：P1
- **依赖**：T52
- **文件**：src/ai_sdlc/cli/telemetry_cmd.py, src/ai_sdlc/telemetry/readiness.py, src/ai_sdlc/cli/doctor_cmd.py, src/ai_sdlc/cli/commands.py, tests/integration/test_cli_telemetry.py, tests/integration/test_cli_status.py, tests/integration/test_cli_doctor.py
- **可并行**：否
- **验收标准**：
  1. manual telemetry CLI 与已锁定的最小 V1 surface 完全一致。
  2. `status --json` / `doctor` 仍 bounded、read-only、无 implicit rebuild / init / deep scan。
  3. 只读 surface 不引入新的隐式写副作用。
  4. 未冻结到 V1 的 `note/comment` 类扩展命令不得默认出现，并有负测覆盖。
- **验证**：`uv run pytest tests/integration/test_cli_telemetry.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`

### Task 6.2 补齐 paired positive / negative smoke 与仓库级回归

- **任务编号**：T62
- **优先级**：P1
- **依赖**：T61
- **文件**：tests/unit/test_telemetry_contracts.py, tests/unit/test_telemetry_store.py, tests/unit/test_telemetry_observer.py, tests/unit/test_verify_constraints.py, tests/unit/test_close_check.py, docs/USER_GUIDE.zh-CN.md
- **可并行**：否
- **验收标准**：
  1. `source closure`、`gate consumption`、`mode/profile drift`、`collector boundary` 四类关键能力都有 paired positive / negative smoke。
  2. full regression、lint、`verify constraints` 都通过。
  3. deferred 能力没有偷偷侵入默认 `self_hosting` 路径。
- **验证**：`uv run pytest -q`, `uv run ruff check src tests`, `uv run ai-sdlc verify constraints`

> **Batch 6 收口（2026-03-31）**：Task `6.1` / `6.2` 已完成。bounded `status --json` / `doctor` / manual telemetry surface 的主线实现与 smoke 锁定已由提交 `a64d956`、`b0d0a19`、`8437c55` 对齐；paired smoke 与仓库级回归 fresh evidence 为 `uv run pytest tests/unit/test_runner_confirm.py tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_store.py tests/unit/test_telemetry_observer.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_telemetry_collectors.py tests/unit/test_parallel.py tests/integration/test_cli_trace.py tests/integration/test_cli_telemetry.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q` **208 passed**、`uv run pytest -q` **913 passed**、`uv run ruff check src tests` **All checks passed!**、`uv run ai-sdlc verify constraints` **no BLOCKERs**。正式归档见 [`task-execution-log.md`](task-execution-log.md) Batch `2026-03-31-001` ~ `2026-03-31-003`。
