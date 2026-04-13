---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "src/ai_sdlc/rules/pipeline.md"
  - "src/ai_sdlc/core/workitem_truth.py"
---
# 任务分解：Execute Authorization Preflight Guard Baseline

**编号**：`116-execute-authorization-preflight-guard-baseline` | **日期**：2026-04-13
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline correction
Batch 2: execute authorization preflight core
Batch 3: status surface integration and focused verification
```

---

## Batch 1：formal baseline correction

### Task 1.1 冻结 `116` 的真实缺陷边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `116` formal docs 明确承接 `FD-2026-04-07-003`
  2. `116` 不再宣称自己是 direct-formal scaffold work item
  3. `116` 写清 `tasks.md` 缺失 blocker 与 `current_stage` blocker 的区别
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：execute authorization preflight core

### Task 2.1 先写红灯测试覆盖 blocker / ready 语义

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`tests/unit/test_execute_authorization.py`, `tests/integration/test_cli_status.py`
- **可并行**：否
- **验收标准**：
  1. 测试先覆盖“缺少 `tasks.md`” blocker
  2. 测试覆盖“`tasks.md` 已存在但 checkpoint 未进 execute” blocker
  3. 测试覆盖 ready 场景
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q`

### Task 2.2 实现 execute authorization preflight helper

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/execute_authorization.py`
- **可并行**：否
- **验收标准**：
  1. helper 输出 bounded 结构化结果
  2. helper 复用 `checkpoint.current_stage` 与 `run_truth_check`
  3. helper 提供稳定 reason codes，至少覆盖 `tasks_truth_missing` 与 `explicit_execute_authorization_missing`
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py -q`

## Batch 3：status surface integration and focused verification

### Task 3.1 接入 `status --json` 与 `status` 文本输出

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`src/ai_sdlc/telemetry/readiness.py`, `src/ai_sdlc/cli/commands.py`, `tests/integration/test_cli_status.py`
- **可并行**：否
- **验收标准**：
  1. `status --json` 包含 `execute_authorization`
  2. `status` 文本输出显式显示 execute authorization 状态与 detail
  3. 不引入 unbounded remediation prose
- **验证**：`uv run pytest tests/integration/test_cli_status.py -q`

### Task 3.2 完成 focused verification 与执行归档

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. focused unit/integration tests 结果已归档
  2. `task-execution-log.md` 明确记录 blocker / ready 语义与验证命令
  3. 本批结论不再使用“plan freeze 可直接进入实现”的表述
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q`
