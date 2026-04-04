---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Cleanup Eligibility Consumption Baseline

**编号**：`055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline` | **日期**：2026-04-04
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline freeze
Batch 2: failing tests for eligibility truth consumption
Batch 3: service/CLI implementation and focused verification
```

---

## Batch 1：formal baseline freeze

### Task 1.1 冻结 `055` 的 canonical 边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `055` formal docs 明确约束 `cleanup_target_eligibility` 的消费边界与 non-goals
  2. 文档明确 `eligible` 不等于 real cleanup 放行
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

## Batch 2：failing tests for eligibility truth consumption

### Task 2.1 固定 service payload 语义

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：tests/unit/test_program_service.py
- **可并行**：否
- **验收标准**：
  1. 单元测试覆盖 `cleanup_target_eligibility` 的 `missing`、`empty`、`listed` 与 invalid mapping
  2. 实现前测试必须因缺少 eligibility 字段/输出而失败
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 2.2 固定 CLI observability 语义

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T11
- **文件**：tests/integration/test_cli_program.py
- **可并行**：否
- **验收标准**：
  1. 集成测试覆盖 dry-run / execute 输出中的 eligibility state/count
  2. 实现前测试必须因 CLI 未暴露 eligibility truth 而失败
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 3：service/CLI implementation and focused verification

### Task 3.1 接入 `ProgramService` eligibility truth 消费

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/program_service.py
- **可并行**：否
- **验收标准**：
  1. request/result/artifact/source_linkage 暴露 `cleanup_target_eligibility_state` 与 `cleanup_target_eligibility`
  2. invalid eligibility truth 产出 warning，但不突破 `deferred` 边界
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 3.2 接入 CLI guard / report 输出

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T22, T31
- **文件**：src/ai_sdlc/cli/program_cmd.py
- **可并行**：否
- **验收标准**：
  1. dry-run / execute guard 输出 eligibility state/count
  2. report 文本与 terminal output 保持一致
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 3.3 完成 focused verification 并记录证据

- **任务编号**：T33
- **优先级**：P0
- **依赖**：T31, T32
- **文件**：task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. focused verification 命令全部通过
  2. `task-execution-log.md` 记录脚手架、red-green 和最终验证结果
- **验证**：
  - `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
  - `uv run ruff check src tests`
  - `uv run ai-sdlc verify constraints`
  - `git diff --check -- specs/055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
