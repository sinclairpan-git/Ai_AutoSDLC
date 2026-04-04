---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md"
  - "specs/061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md"
  - "specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Cleanup Mutation Execution Gating Consumption Baseline

**编号**：`063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal docs alignment
Batch 2: failing tests for execution gating truth consumption
Batch 3: minimal ProgramService/CLI implementation
Batch 4: focused verification and log append
```

---

## Batch 1：formal docs alignment

### Task 1.1 冻结 execution gating consumption 边界

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `063` formal docs 明确 `cleanup_mutation_execution_gating` 的消费范围、non-goals 与 `deferred` 边界
  2. 文档口径与 `050/060/061/062` 对齐，不再保留脚手架模板占位内容
- **验证**：文档对账 + 后续 `uv run ai-sdlc verify constraints`

## Batch 2：failing tests for execution gating truth consumption

### Task 2.1 扩展 ProgramService unit tests

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：tests/unit/test_program_service.py
- **可并行**：否
- **验收标准**：
  1. 覆盖 `cleanup_mutation_execution_gating` 的 `missing`、`empty`、`listed`
  2. 覆盖 invalid structure、missing keys、unknown target、ineligible target、preview mismatch、proposal mismatch、approval mismatch、action mismatch 警告
  3. 实现前测试先失败，指向 execution gating truth 未接通
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 2.2 扩展 CLI integration tests

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T11
- **文件**：tests/integration/test_cli_program.py
- **可并行**：否
- **验收标准**：
  1. dry-run / execute 输出断言包含 `cleanup mutation execution gating state`
  2. dry-run / execute 输出与 report 断言包含 execution gating 数量
  3. 实现前测试先失败，指向 CLI 未暴露 execution gating truth
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 3：minimal ProgramService/CLI implementation

### Task 3.1 接通 ProgramService execution gating truth 消费

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/program_service.py
- **可并行**：否
- **验收标准**：
  1. request/result/artifact payload 暴露 `cleanup_mutation_execution_gating_state` 与 execution gating list
  2. `source_linkage` 与 warnings 保留 execution gating truth 的 state/path 和结构性问题
  3. execute 结果继续保持 `deferred`
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 3.2 接通 CLI execution gating truth 输出

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T22, T31
- **文件**：src/ai_sdlc/cli/program_cmd.py
- **可并行**：否
- **验收标准**：
  1. dry-run / execute 输出与 report 显示 execution gating truth state/count
  2. 输出口径与 targets/eligibility/preview/proposal/approval state 保持一致
  3. 不新增 mutation-ready 误导性文案
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 4：focused verification and log append

### Task 4.1 完成 focused verification

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T31, T32
- **文件**：task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `pytest`、`ruff`、`verify constraints` 与 `git diff --check` 结果被追加到 execution log
  2. execution log 保持 append-only，不覆盖已记录事实
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`、`uv run pytest tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration .ai-sdlc/project/config/project-state.yaml`
