---
related_doc:
  - "program-manifest.yaml"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "src/ai_sdlc/models/frontend_managed_delivery.py"
  - "src/ai_sdlc/core/managed_delivery_apply.py"
  - "src/ai_sdlc/core/program_service.py"
  - "tests/unit/test_managed_delivery_apply.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
---
# 任务分解：Frontend Mainline Delivery Materialization Runtime Baseline

**编号**：`124-frontend-mainline-delivery-materialization-runtime-baseline` | **日期**：2026-04-14
**来源**：`spec.md` + `plan.md`

## Batch 1：Formal carrier 与 red tests

### Task 1.1 锁定 materialization red fixtures

- **任务编号**：T124-11
- **优先级**：P0
- **文件**：`tests/unit/test_managed_delivery_apply.py`, `tests/unit/test_program_service.py`, `tests/integration/test_cli_program.py`
- **验收标准**：
  1. `dependency_install` 只能消费结构化 payload
  2. `artifact_generate` 越界时必须 fail-closed
  3. CLI execute 能在 managed target 内 materialize 文件

## Batch 2：Runtime materialization

### Task 2.1 扩 executor payload 与 boundary 校验

- **任务编号**：T124-21
- **优先级**：P0
- **文件**：`src/ai_sdlc/models/frontend_managed_delivery.py`, `src/ai_sdlc/core/managed_delivery_apply.py`
- **验收标准**：
  1. 引入 `managed_target_path`
  2. `dependency_install` / `artifact_generate` 支持 preflight 校验
  3. `will_not_touch` 命中时阻断

### Task 2.2 接入 ProgramService execute/preflight 分流

- **任务编号**：T124-22
- **优先级**：P0
- **文件**：`src/ai_sdlc/core/program_service.py`, `tests/unit/test_program_service.py`
- **验收标准**：
  1. build request 仅做 preflight
  2. execute path 才进行 materialization

## Batch 3：Closeout

### Task 3.1 focused verification 与归档

- **任务编号**：T124-31
- **优先级**：P1
- **文件**：`task-execution-log.md`
- **验收标准**：
  1. focused tests 通过
  2. 记录 payload/boundary/preflight 分流的收口证据
