---
related_doc:
  - "program-manifest.yaml"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
---
# 任务分解：Frontend Mainline Managed Delivery Apply Runtime Implementation Baseline

**编号**：`123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline` | **日期**：2026-04-13
**来源**：`spec.md` + `plan.md`

---

## 分批策略

```text
Batch 1: red fixtures
Batch 2: core executor runtime
Batch 3: thin service/CLI wiring
Batch 4: closeout
```

---

## Batch 1：Red fixtures

### Task 1.1 锁定 fail-closed 与 honest result 红灯夹具

- **任务编号**：T123-11
- **优先级**：P0
- **依赖**：无
- **文件**：`tests/unit/test_managed_delivery_apply.py`, `tests/unit/test_program_service.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 测试锁定 `plan_fingerprint` 不一致时必须 `blocked_before_start`
  2. 测试锁定 selected required unsupported action 不得被绕过
  3. 测试锁定 `before_state` 写入失败时 action 不得执行
  4. 测试锁定成功态只能是 `apply_succeeded_pending_browser_gate`
- **验证**：`uv run pytest tests/unit/test_managed_delivery_apply.py tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`

## Batch 2：Core executor runtime

### Task 2.1 新增 runtime model

- **任务编号**：T123-21
- **优先级**：P0
- **依赖**：T11
- **文件**：`src/ai_sdlc/models/frontend_managed_delivery.py`
- **可并行**：否
- **验收标准**：
  1. model 能表达 execution view、decision receipt、execution session、ledger action truth 与 apply result
  2. action-level status 与 `failure_classification` 分离
  3. `required_unsupported` / `selected_optional_unsupported` / `dependency_blocked_by_unsupported` / `user_deselected_optional` 有稳定枚举
- **验证**：`uv run pytest tests/unit/test_managed_delivery_apply.py -q`

### Task 2.2 落窄版 apply executor

- **任务编号**：T123-22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/managed_delivery_apply.py`, `tests/unit/test_managed_delivery_apply.py`
- **可并行**：否
- **验收标准**：
  1. executor 能完成 decision gate、ledger bootstrap、dependency graph、action execution 与 result finalization
  2. 第一批只真执行 `runtime_remediation` 与 `managed_target_prepare`
  3. rollback/retry/cleanup 只记录 refs，不执行
  4. action 执行后必须写入 `after_state + result_status`
- **验证**：`uv run pytest tests/unit/test_managed_delivery_apply.py -q`

## Batch 3：Thin service/CLI wiring

### Task 3.1 接入 ProgramService apply request/result

- **任务编号**：T123-31
- **优先级**：P0
- **依赖**：T22
- **文件**：`src/ai_sdlc/core/program_service.py`, `tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService` 能构建最小 apply request/result，不重定义 executor truth
  2. host ingress 未达 mutate delivery 阈值时，在 apply 前 fail-closed
  3. `ProgramService` 不把 browser gate 或 installer scope 混入 apply result
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/unit/test_managed_delivery_apply.py -q`

### Task 3.2 接入最小 CLI preview/execute surface

- **任务编号**：T123-32
- **优先级**：P0
- **依赖**：T31
- **文件**：`src/ai_sdlc/cli/program_cmd.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能稳定展示 blocked / partial progress / pending browser gate 语义
  2. CLI 会明确输出未执行 action 与原因
  3. CLI 不把 apply result 渲染成最终 readiness 通过
  4. CLI headline 不得只输出 raw success token，必须明确 `delivery is not complete` 与 `browser gate has not run`
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 4：123-scoped closeout

### Task 4.1 完成 123-scoped focused verification 与归档

- **任务编号**：T123-41
- **优先级**：P1
- **依赖**：T32
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. focused unit/integration tests 通过
  2. `uv run ai-sdlc verify constraints`、`uv run ai-sdlc program validate` 与 `git diff --check` 通过
  3. 执行日志完整归档 fail-closed / pending browser gate / manual recovery boundary
- **验证**：`uv run pytest tests/unit/test_managed_delivery_apply.py tests/unit/test_program_service.py tests/integration/test_cli_program.py -q` + `uv run ai-sdlc verify constraints` + `uv run ai-sdlc program validate` + `git diff --check`
