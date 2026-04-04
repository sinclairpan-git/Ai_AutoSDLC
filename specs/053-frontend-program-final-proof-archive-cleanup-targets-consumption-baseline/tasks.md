---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Program Final Proof Archive Cleanup Targets Consumption Baseline

**编号**：`053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline` | **日期**：2026-04-04
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal boundary freeze
Batch 2: unit red-green for cleanup_targets consumption
Batch 3: CLI truth visibility and focused verification
```

---

## Batch 1：formal boundary freeze

### Task 1.1 冻结 053 scope 与 honesty boundary

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. 文档明确 053 只覆盖 `cleanup_targets` consumption baseline
  2. 文档明确不执行真实 cleanup mutation，保留 `deferred` 边界
  3. 文档明确禁止通过隐式信号推断 cleanup targets
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：unit red-green for cleanup_targets consumption

### Task 2.1 先补三态与 invalid 结构的 failing tests

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：tests/unit/test_program_service.py
- **可并行**：否
- **验收标准**：
  1. 测试覆盖 `missing`、`empty`、`listed`
  2. 测试覆盖 invalid `cleanup_targets` 结构或 entry 缺失必填键
  3. 新测在实现前失败
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 2.2 最小实现 ProgramService 的 target truth 消费

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/program_service.py
- **可并行**：否
- **验收标准**：
  1. request/result/artifact payload 暴露 `cleanup_targets_state`
  2. 显式 target 列表按 artifact 原样透传
  3. invalid truth 产出 warning，但不退化为隐式推断
  4. execute 仍返回 `deferred`
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

## Batch 3：CLI truth visibility and focused verification

### Task 3.1 为 CLI 输出补齐 cleanup target truth 可观测性

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：tests/integration/test_cli_program.py, src/ai_sdlc/cli/program_cmd.py
- **可并行**：否
- **验收标准**：
  1. dry-run 输出包含 `cleanup_targets_state`
  2. execute 输出包含 state 与 target 数量
  3. `missing` 与 `empty` 不会在 terminal output 中混淆
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 3.2 完成 focused verification 与执行记录

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. focused verification 命令全部通过
  2. `task-execution-log.md` 记录 red-green 与验证结论
- **验证**：
  - `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
  - `uv run ruff check src tests`
  - `uv run ai-sdlc verify constraints`
  - `git diff --check -- specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`
