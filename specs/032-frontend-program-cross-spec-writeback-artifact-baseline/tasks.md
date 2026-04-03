---
related_doc:
  - "specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md"
---
# 任务分解：Frontend Program Cross-Spec Writeback Artifact Baseline

**编号**：`032-frontend-program-cross-spec-writeback-artifact-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-032-001 ~ FR-032-009 / SC-032-001 ~ SC-032-005）

---

## 分批策略

```text
Batch 1: cross-spec writeback artifact truth freeze
Batch 2: artifact contract / output boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService cross-spec writeback artifact writer slice
Batch 5: program cross-spec writeback artifact CLI surface slice
```

---

## 执行护栏

- `032` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `032` 不得改写 `031` cross-spec writeback truth 或更上游 truth。
- `032` 不得在当前 child work item 中直接启用 registry orchestration、broader code rewrite orchestration 或默认 auto-fix。
- `032` 不得把 writeback artifact 偷渡成新的默认 execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：cross-spec writeback artifact truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `032` 是 `031` 下游的 cross-spec writeback artifact child work item
  2. `spec.md` 明确 artifact 只消费 `031` cross-spec writeback request/result truth
  3. `spec.md` 不再依赖临时对话才能解释 `032` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 artifact write boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 registry 与 broader code rewrite orchestration 不属于当前 work item
  2. formal docs 明确 artifact 只允许在显式确认后的 execute 路径写出
  3. formal docs 明确 artifact 落盘不等于 registry 或 broader governance 已执行
- **验证**：scope review

### Task 1.3 冻结 artifact 输入与输出字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 artifact 输入至少包括 writeback request linkage、result linkage 与 source artifact linkage
  2. formal docs 明确 artifact 输出至少包括 writeback state、orchestration result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确 `032` 不新增第二套 cross-spec writeback artifact truth
- **验证**：truth-order review

---

## Batch 2：artifact contract / output boundary freeze

### Task 2.1 冻结 artifact writer responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 cross-spec writeback artifact writer 的 responsibility
  2. formal docs 明确 artifact 只组织既有 writeback truth，不默认扩张到 registry orchestration
  3. formal docs 明确与 `031` writeback truth 的关系
- **验证**：responsibility review

### Task 2.2 冻结 result honesty 与 downstream registry 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 artifact 输出必须诚实回报 writeback state、orchestration result 与 remaining blockers
  2. formal docs 明确 artifact 不等于 registry 已执行或页面代码已全面安全改写
  3. formal docs 明确 downstream registry / broader orchestration 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream registry / broader orchestration handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 cross-spec writeback artifact 与 future registry / broader orchestration 的边界
  2. formal docs 明确 registry 与 broader code rewrite orchestration 仍由下游工单承接
  3. formal docs 明确 `032` 与 `031` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `031` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 artifact writer、artifact output/report 与 downstream registry guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 registry / broader orchestration 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/plan.md`, `specs/032-frontend-program-cross-spec-writeback-artifact-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 cross-spec writeback artifact、write boundary 与 downstream boundary 保持单一真值
  3. 当前分支上的 `032` formal docs 可作为后续进入 cross-spec writeback artifact 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService cross-spec writeback artifact writer slice

### Task 4.1 先写 failing tests 固定 cross-spec writeback artifact writer 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 cross-spec writeback artifact 的 canonical path、request/result linkage 与 payload 字段
  2. 单测明确覆盖 dry-run truth 不会隐式写入 artifact
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 artifact writer truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 cross-spec writeback artifact writer

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 cross-spec writeback request/result 生成 canonical artifact 并返回路径
  2. 实现保持 bounded artifact writer，不引入 registry orchestration 或 broader code rewrite orchestration
  3. 实现不改写 `031` cross-spec writeback truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/032-frontend-program-cross-spec-writeback-artifact-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/032-frontend-program-cross-spec-writeback-artifact-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program cross-spec writeback artifact CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI artifact 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 artifact path 输出与 report 落盘
  2. 集成测试明确覆盖 dry-run 不会隐式写出 artifact
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 artifact surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 cross-spec writeback artifact CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能在显式 execute 后回报 artifact path 与 writeback state
  2. 实现保持 artifact output 为独立显式 surface，不挂接到默认 provider-patch-apply 或默认 cross-spec-writeback dry-run
  3. 实现不进入 registry orchestration 或 broader code rewrite
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/032-frontend-program-cross-spec-writeback-artifact-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/032-frontend-program-cross-spec-writeback-artifact-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/032-frontend-program-cross-spec-writeback-artifact-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
