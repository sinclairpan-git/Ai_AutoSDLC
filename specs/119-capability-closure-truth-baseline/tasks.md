---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/cli/commands.py"
---
# 任务分解：Capability Closure Truth Baseline

**编号**：`119-capability-closure-truth-baseline` | **日期**：2026-04-13
**来源**：`plan.md` + `spec.md`

---

## 分批策略

```text
Batch 1: formal carrier freeze
Batch 2: status JSON red/green + manifest model
Batch 3: root truth sync and rollout wording alignment
```

---

## Batch 1：formal carrier freeze

### Task 1.1 冻结 capability closure 的 formal truth

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `119` 明确 root-level capability closure truth 的定位
  2. `119` 明确 `formal_only / partial / capability_open` 的定义
  3. `119` 明确 local status 与 capability closure 的拆层
- **验证**：文档对账

## Batch 2：status JSON red/green + manifest model

### Task 2.1 先写 capability closure status JSON 红灯夹具

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：`tests/integration/test_cli_status.py`
- **可并行**：否
- **验收标准**：
  1. `status --json` 缺少 capability closure summary 时测试失败
  2. 夹具只要求 bounded counts + open cluster summary
- **验证**：`uv run pytest tests/integration/test_cli_status.py -q -k capability_closure_summary`

### Task 2.2 实现 manifest model 与 bounded status surface

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`src/ai_sdlc/models/program.py`, `src/ai_sdlc/telemetry/readiness.py`, `src/ai_sdlc/cli/commands.py`
- **可并行**：否
- **验收标准**：
  1. `program-manifest.yaml` 可解析 `capability_closure_audit`
  2. `status --json` 返回 capability closure summary
  3. 文本 `status` 可读到最小 capability closure 提示
- **验证**：`uv run pytest tests/integration/test_cli_status.py -q -k capability_closure_summary`

## Batch 3：root truth sync

### Task 3.1 回写 manifest、rollout wording 与 project-state

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`program-manifest.yaml`, `frontend-program-branch-rollout-plan.md`, `.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. manifest 顶层已有当前 open capability clusters
  2. rollout 文档明确 local status 不等于 capability closure
  3. project-state 推进到下一个 work item seq
- **验证**：文档对账 + YAML 解析

### Task 3.2 完成 focused verification 并归档

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. focused integration test 通过
  2. `verify constraints` 通过
  3. 执行日志完整归档 red/green 与 root truth sync
- **验证**：`uv run pytest tests/integration/test_cli_status.py -q -k capability_closure_summary` + `uv run ai-sdlc verify constraints`
