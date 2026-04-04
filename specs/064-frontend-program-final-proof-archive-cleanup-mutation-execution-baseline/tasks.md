---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md"
  - "specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Cleanup Mutation Execution Baseline

**编号**：`064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal docs freeze
Batch 2: failing tests for real cleanup mutation semantics
Batch 3: minimal ProgramService execution implementation
Batch 4: CLI/report alignment
Batch 5: focused verification and log append
```

---

## Batch 1：formal docs freeze

### Task 1.1 冻结 separate execution baseline

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `064` formal docs 明确其是 `063` 之后的 separate execution child work item
  2. 文档明确锁定 baseline action matrix、路径安全约束、aggregate result honesty 与 non-goals
  3. 不再保留脚手架模板占位内容
- **验证**：文档对账 + 后续 `uv run ai-sdlc verify constraints`

## Batch 2：failing tests for real cleanup mutation semantics

### Task 2.1 扩展 ProgramService unit tests

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：tests/unit/test_program_service.py
- **可并行**：否
- **验收标准**：
  1. 覆盖 `thread_archive/archive_thread_report` 与 `spec_dir/remove_spec_dir` 的真实 mutation success 路径
  2. 覆盖 missing target、unsupported action、duplicate target、越界路径、路径类型不匹配、runtime 删除失败与 partial success
  3. 实现前测试先失败，指向当前 execute 仍停留在 `deferred`
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 2.2 扩展 CLI integration tests

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T11
- **文件**：tests/integration/test_cli_program.py
- **可并行**：否
- **验收标准**：
  1. execute 输出与 report 断言包含 aggregate result、per-target outcome 与 written paths
  2. 断言真实 mutation 发生后 CLI 不再把结果显示为 `deferred`
  3. 实现前测试先失败，指向 CLI/report 仍是旧的 deferred baseline
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 3：minimal ProgramService execution implementation

### Task 3.1 实现 canonical target validation

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/program_service.py
- **可并行**：否
- **验收标准**：
  1. listed gating items 会重新校验 target / eligibility / preview / proposal / approval 对齐
  2. duplicate target、unsupported action、越界路径与类型不匹配都会形成显式 non-success outcome
  3. validation 不会引入新的 execution truth 或自动修正 canonical payload
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 3.2 实现 bounded real mutation

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：src/ai_sdlc/core/program_service.py
- **可并行**：否
- **验收标准**：
  1. `archive_thread_report` 只删除 canonical target 文件
  2. `remove_spec_dir` 只递归删除 canonical target 目录
  3. result/artifact payload 记录 per-target outcome、aggregate result、written paths、warnings 与 remaining blockers
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

## Batch 4：CLI/report alignment

### Task 4.1 暴露真实 execution result

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T22, T32
- **文件**：src/ai_sdlc/cli/program_cmd.py
- **可并行**：否
- **验收标准**：
  1. execute 输出与 markdown report 展示 aggregate result、per-target outcome、written paths 与 warnings
  2. 文案不再把真实 mutation 结果表述为 `deferred`
  3. 输出口径与 canonical artifact payload 一致
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

## Batch 5：focused verification and log append

### Task 5.1 完成 focused verification

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T32, T41
- **文件**：task-execution-log.md
- **可并行**：否
- **验收标准**：
  1. `pytest`、`ruff`、`verify constraints` 与 `git diff --check` 结果被追加到 execution log
  2. execution log 保持 append-only，不覆盖已记录事实
  3. verification 结果足以支撑“真实 mutation baseline 已闭环”的结论
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ruff check src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`
