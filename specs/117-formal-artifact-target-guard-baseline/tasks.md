---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "cursor/rules/ai-sdlc.md"
  - "src/ai_sdlc/stages/refine.yaml"
  - "USER_GUIDE.zh-CN.md"
---
# 任务分解：Formal Artifact Target Guard Baseline

**编号**：`117-formal-artifact-target-guard-baseline` | **日期**：2026-04-13
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline correction
Batch 2: formal artifact target guard
Batch 3: breach logging atomicity guard and focused verification
```

---

## Batch 1：formal baseline correction

### Task 1.1 冻结 `117` 的真实缺陷边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `117` formal docs 明确承接 `FD-2026-04-07-002`
  2. `117` 不再宣称自己是 direct-formal scaffold work item
  3. `117` 写清 formal artifact target guard 与 breach logging atomicity 两条边界
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：formal artifact target guard

### Task 2.1 先写 artifact target 正反夹具

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`tests/unit/test_artifact_target_guard.py`
- **可并行**：否
- **验收标准**：
  1. formal spec -> `specs/<WI>/spec.md` 为 allow
  2. formal spec -> `docs/superpowers/specs/*.md` 为 block
  3. auxiliary design doc -> `docs/superpowers/*` 不被误阻断
- **验证**：`uv run pytest tests/unit/test_artifact_target_guard.py -q`

### Task 2.2 实现 canonical path guard

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/core/artifact_target_guard.py`, `src/ai_sdlc/core/workitem_scaffold.py`, `src/ai_sdlc/core/verify_constraints.py`, `src/ai_sdlc/telemetry/readiness.py`, `src/ai_sdlc/cli/commands.py`
- **可并行**：否
- **验收标准**：
  1. formal artifact producer 在落盘前会做 canonical target preflight
  2. blocker 具有稳定 reason code
  3. `verify constraints` / `status` 可稳定暴露 misplaced formal artifact
  4. 合法 canonical path 不受影响
- **验证**：`uv run pytest tests/unit/test_artifact_target_guard.py tests/unit/test_workitem_scaffold.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_status.py -q`

## Batch 3：breach logging atomicity guard and focused verification

### Task 3.1 为 breach-detected-but-not-logged 增加 blocker surface

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`src/ai_sdlc/core/backlog_breach_guard.py`, `tests/unit/test_backlog_breach_guard.py`
- **可并行**：否
- **验收标准**：
  1. 已识别 breach 但未同轮补录 backlog 时返回 blocker
  2. 同轮已补录 backlog 时 blocker 消失
  3. 输出保持 bounded
- **验证**：`uv run pytest tests/unit/test_backlog_breach_guard.py -q`

### Task 3.2 完成 focused verification 与归档

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. focused tests 与 code-change verification 已归档
  2. execution log 明确记录 canonical-path guard 与 breach logging guard 的验证结论
  3. latest batch 不再沿用 direct-formal scaffold 语义
- **验证**：`uv run pytest tests/unit/test_artifact_target_guard.py tests/unit/test_backlog_breach_guard.py tests/unit/test_verify_constraints.py tests/unit/test_workitem_scaffold.py tests/integration/test_cli_status.py tests/integration/test_cli_workitem_init.py -q` + `uv run ruff check ...` + `uv run ai-sdlc verify constraints`
