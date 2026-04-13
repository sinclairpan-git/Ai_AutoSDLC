---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "README.md"
  - "packaging/offline/README.md"
  - "docs/releases/v0.6.0.md"
  - "docs/pull-request-checklist.zh.md"
---
# 任务分解：Release Docs And Execute Handoff Guard Baseline

**编号**：`118-release-docs-and-execute-handoff-guard-baseline` | **日期**：2026-04-13
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: execute handoff guard
Batch 3: release docs consistency sweep and backlog backfill
```

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 `118` 的真实缺陷边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `118` formal docs 明确承接 `FD-2026-04-07-001/002/003`
  2. `118` 不再宣称自己是 direct-formal scaffold work item
  3. `118` 写清 execute handoff guard、release sweep、002 backlog backfill 三条边界
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：execute handoff guard

### Task 2.1 先写 execute handoff 红灯夹具

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`tests/unit/test_execute_authorization.py`, `tests/integration/test_cli_status.py`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 缺失时返回 blocked + docs-only / review 口径
  2. `tasks.md` 存在但阶段未进入 execute 时返回 blocked
  3. `status --json` / `status` 可读到稳定 detail
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q`

### Task 2.2 实现 execute handoff guard

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/execute_authorization.py`, `src/ai_sdlc/telemetry/readiness.py`, `src/ai_sdlc/cli/commands.py`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 缺失时不会再被解读为可直接进入实现
  2. 未进入 execute 时 bounded detail 明确为 review-to-decompose / not authorized
  3. 已进入 execute 的 ready 行为不回归
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py -q`

## Batch 3：release docs consistency sweep and backlog backfill

### Task 3.1 先写 release docs consistency 红灯夹具

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`tests/unit/test_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 任一 release 入口文档缺失 `v0.6.0` 或资产口径时返回 blocker
  2. 六个入口文件一致时 blocker 消失
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`

### Task 3.2 实现 sweep、回填 backlog，并完成 focused verification

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`src/ai_sdlc/core/verify_constraints.py`, `README.md`, `docs/框架自迭代开发与发布约定.md`, `docs/pull-request-checklist.zh.md`, `docs/framework-defect-backlog.zh-CN.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. release docs consistency sweep 已进入 `verify constraints`
  2. `FD-2026-04-07-002` 条目与 backlog 顶部摘要已回填 closed
  3. focused verification 已归档
- **验证**：`uv run pytest tests/unit/test_execute_authorization.py tests/unit/test_verify_constraints.py tests/integration/test_cli_status.py -q` + `uv run ai-sdlc verify constraints`
