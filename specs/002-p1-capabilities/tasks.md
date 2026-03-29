# 任务分解：AI-SDLC P1 能力扩展缺口收敛

**编号**：`002-p1-capabilities` | **日期**：2026-03-28  
**来源**：plan.md + spec.md（RG-010 ~ RG-015 / FR-P1-017 ~ FR-P1-041）

---

## 分批策略

```text
Batch 1: P1 contract models                   (resume-point / execution-path / coordination artifact)
Batch 2: Change / Maintenance runtime         (suspended + execution-path persistence)
Batch 3: Parallel orchestration runtime       (assignment freeze + worker lifecycle + merge verify)
Batch 4: Close path integration               (knowledge refresh + incident postmortem gate)
Batch 5: Surface / traceability finalization  (status / recover / report / close-check)
```

---

## Batch 1：P1 contract models

### Task 1.1 — 补齐 Change / Maintenance / Parallel 的结构化 artifact 模型

- **优先级**：P1
- **依赖**：无
- **输入**：[`spec.md`](spec.md)、[`src/ai_sdlc/models/work.py`](../../src/ai_sdlc/models/work.py)、[`src/ai_sdlc/models/state.py`](../../src/ai_sdlc/models/state.py)
- **产物**：
  - `resume-point` 的可消费结构化合同
  - Maintenance `execution-path` 的对象层真值
  - parallel coordination artifact / assignment freeze / merge verify 所需模型
- **验收标准**：
  1. 对象字段足以支持 `recover/run/status/report` 消费。
  2. 不再只依赖自由文本字段表达暂停点或执行顺序。
  3. 模型默认值与向后兼容策略明确。
- **验证**：`uv run pytest tests/unit/test_p1_models.py tests/unit/test_studios.py -v`

### Task 1.2 — 为新增 artifact 模型补单测与序列化回归

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`tests/unit/test_p1_models.py`](../../tests/unit/test_p1_models.py)
- **验收标准**：
  1. 新模型支持 `model_dump()` / `model_validate()` 往返。
  2. 旧 payload 缺省字段时仍能安全加载或返回明确错误。
- **验证**：`uv run pytest tests/unit/test_p1_models.py -v`

---

## Batch 2：Change / Maintenance runtime

### Task 2.1 — 把 ChangeStudio 的 freeze snapshot / resume-point 接入运行态暂停主链

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/studios/change_studio.py`](../../src/ai_sdlc/studios/change_studio.py)、[`src/ai_sdlc/core/state_machine.py`](../../src/ai_sdlc/core/state_machine.py)、[`tests/unit/test_studios.py`](../../tests/unit/test_studios.py)
- **验收标准**：
  1. 活跃 work item 遇到 `change_request` 后进入 `suspended`。
  2. freeze snapshot 与 `resume-point` 同步落盘。
  3. `resume-point` 不是只给人读，而是后续 `recover/run` 可消费。
- **验证**：`uv run pytest tests/unit/test_studios.py tests/unit/test_state_machine.py -v`

### Task 2.2 — 给 MaintenanceStudio 增加显式 execution path 与持久化

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/studios/maintenance_studio.py`](../../src/ai_sdlc/studios/maintenance_studio.py)、[`tests/unit/test_studios.py`](../../tests/unit/test_studios.py)
- **验收标准**：
  1. Maintenance 输出除 `task_graph` 外还存在 `execution-path`。
  2. 文档层与对象层都能读到一致的执行顺序真值。
  3. 轻量路径仍保持 <= 10 tasks 的约束。
- **验证**：`uv run pytest tests/unit/test_studios.py -v`

### Task 2.3 — Change / Maintenance flow 回归

- **优先级**：P1
- **依赖**：Task 2.1, Task 2.2
- **输入**：新增/扩展 `tests/flow/test_incident_flow.py`、`tests/flow/test_execution_flow.py`、必要的 recover/status 夹具
- **验收标准**：
  1. change pause 后能从 `resume-point` 恢复。
  2. maintenance execution path 能贯穿到执行入口或 status/report surface。
- **验证**：定向 flow tests

---

## Batch 3：Parallel orchestration runtime

### Task 3.1 — 把 parallel 从 simulation 推进到 assignment freeze artifact

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/parallel/engine.py`](../../src/ai_sdlc/parallel/engine.py)、[`src/ai_sdlc/models/state.py`](../../src/ai_sdlc/models/state.py)、[`tests/unit/test_parallel.py`](../../tests/unit/test_parallel.py)
- **验收标准**：
  1. group、worker、allowed/forbidden paths、merge order、contract freeze 结果有正式 artifact。
  2. worker branch 命名与 merge order 可被读取，不再只存在于内存对象。
- **验证**：`uv run pytest tests/unit/test_parallel.py -v`

### Task 3.2 — 接入 ParallelGate / runner orchestration / integration verify

- **优先级**：P1
- **依赖**：Task 3.1
- **输入**：[`src/ai_sdlc/gates/extra_gates.py`](../../src/ai_sdlc/gates/extra_gates.py)、[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py)、[`tests/unit/test_gates.py`](../../tests/unit/test_gates.py)
- **验收标准**：
  1. parallel execution 前必须经过 overlap / contract freeze / merge verify。
  2. runner 能消费 assignment freeze 结果，而不是只停留在 planning helper。
- **验证**：`uv run pytest tests/unit/test_gates.py tests/unit/test_parallel.py -v`

### Task 3.3 — Parallel flow 回归

- **优先级**：P1
- **依赖**：Task 3.2
- **输入**：[`tests/flow/test_parallel_flow.py`](../../tests/flow/test_parallel_flow.py)
- **验收标准**：
  1. parallelizable 任务集合能产出 assignment freeze 与 integration verify 证据。
  2. 冲突存在时，close 前返回 BLOCKER。
- **验证**：`uv run pytest tests/flow/test_parallel_flow.py -v`

---

## Batch 4：Close path integration

### Task 4.1 — 把 Knowledge Refresh 正式接入 Done / Close 主链

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/knowledge/engine.py`](../../src/ai_sdlc/knowledge/engine.py)、[`src/ai_sdlc/gates/extra_gates.py`](../../src/ai_sdlc/gates/extra_gates.py)、[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py)
- **验收标准**：
  1. Level 0 可直接 completed。
  2. Level 1+ 未 refresh 前不得 completed。
  3. refresh 完成后 close 主链能读取 evidence / log。
- **验证**：`uv run pytest tests/unit/test_gates.py tests/flow/test_knowledge_refresh_flow.py -v`

### Task 4.2 — 把 Incident Postmortem Gate 接入 close path

- **优先级**：P1
- **依赖**：Task 4.1
- **输入**：[`src/ai_sdlc/studios/incident_studio.py`](../../src/ai_sdlc/studios/incident_studio.py)、[`src/ai_sdlc/gates/extra_gates.py`](../../src/ai_sdlc/gates/extra_gates.py)、[`tests/unit/test_gates.py`](../../tests/unit/test_gates.py)、[`tests/flow/test_incident_flow.py`](../../tests/flow/test_incident_flow.py)
- **验收标准**：
  1. completed 前必须通过 Postmortem Gate。
  2. 缺章节时返回明确 BLOCKER 与缺失原因。
- **验证**：定向 unit + flow tests

### Task 4.3 — Refresh / Incident close 主链回归

- **优先级**：P1
- **依赖**：Task 4.1, Task 4.2
- **验收标准**：
  1. refresh 与 incident close 不再是旁路动作。
  2. flow tests 覆盖通过与阻断两类结果。
- **验证**：`uv run pytest tests/flow/test_knowledge_refresh_flow.py tests/flow/test_incident_flow.py -v`

---

## Batch 5：Surface / traceability finalization

### Task 5.1 — status / recover / report surface 消费新增 P1 artifact

- **优先级**：P1
- **依赖**：Task 2.3, Task 3.3, Task 4.3
- **输入**：`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/core/runner.py`、相关 integration tests
- **验收标准**：
  1. `resume-point`、parallel assignment、refresh evidence 在 surface 上可见。
  2. surface 不要求人工回忆上下文。
- **验证**：定向 integration tests

### Task 5.2 — 002 traceability / plan/tasks / close-check 对账收口

- **优先级**：P1
- **依赖**：Task 5.1
- **验收标准**：
  1. `spec.md`、`plan.md`、`tasks.md` 三者映射完整。
  2. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：全量 `pytest` + `ruff`

> **Task 5.2 完成（2026-03-30）**：已补 `002` final close-truth refresh。基于当前仓库状态重新执行 `uv run pytest tests/unit/test_p1_artifacts.py tests/unit/test_p1_models.py tests/unit/test_studios.py tests/unit/test_parallel.py tests/unit/test_gates.py tests/unit/test_runner_confirm.py tests/flow/test_incident_flow.py tests/flow/test_parallel_flow.py tests/flow/test_knowledge_refresh_flow.py tests/integration/test_cli_status.py tests/integration/test_cli_run.py -q`、`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem close-check --wi specs/002-p1-capabilities --all-docs`，确认 P1 artifact/runtime contracts 仍与 `spec.md` / `plan.md` / `tasks.md` 对齐，`002` 已具备正式 close 条件。
