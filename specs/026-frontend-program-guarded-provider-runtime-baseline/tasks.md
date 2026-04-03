---
related_doc:
  - "specs/025-frontend-program-provider-handoff-baseline/spec.md"
---
# 任务分解：Frontend Program Guarded Provider Runtime Baseline

**编号**：`026-frontend-program-guarded-provider-runtime-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-026-001 ~ FR-026-009 / SC-026-001 ~ SC-026-005）

---

## 分批策略

```text
Batch 1: provider runtime truth freeze
Batch 2: runtime contract / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService guarded provider runtime packaging slice
Batch 5: program guarded provider runtime CLI surface slice
```

---

## 执行护栏

- `026` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `026` 不得改写 `025` 已冻结的 provider handoff truth。
- `026` 不得在当前 child work item 中直接启用页面代码改写、cross-spec code writeback、registry 或默认 provider auto execution。
- `026` 不得把 guarded provider runtime 偷渡成新的默认 remediation side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/026-frontend-program-guarded-provider-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/026-frontend-program-guarded-provider-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：provider runtime truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `026` 是 `025` 下游的 guarded provider runtime child work item
  2. `spec.md` 明确 runtime 只消费 `025` provider handoff payload
  3. `spec.md` 不再依赖临时对话才能解释 `026` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确页面代码改写、cross-spec code writeback、registry 与默认 provider auto execution 不属于当前 work item
  2. formal docs 明确 runtime 必须显式确认
  3. formal docs 明确 runtime 不等于代码已改写
- **验证**：scope review

### Task 1.3 冻结 runtime 输入与结果回报字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 runtime 输入至少包括 handoff linkage、per-spec pending inputs、suggested next actions 与 source linkage
  2. formal docs 明确 runtime 结果至少包括 invocation result、patch summary、remaining blockers 与 source linkage
  3. formal docs 明确 `026` 不新增第二套 provider/runtime truth
- **验证**：truth-order review

---

## Batch 2：runtime contract / result boundary freeze

### Task 2.1 冻结 guarded runtime responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 guarded provider runtime 的 responsibility
  2. formal docs 明确 runtime 只组织既有 handoff truth，不默认扩张到 code rewrite engine
  3. formal docs 明确与 `025` provider handoff 的关系
- **验证**：responsibility review

### Task 2.2 冻结 result honesty 与 downstream code-rewrite 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 runtime 结果必须诚实回报 invocation result 与 remaining blockers
  2. formal docs 明确结果不等于 patch 已应用或页面代码已安全改写
  3. formal docs 明确 downstream code rewrite / writeback 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream runtime handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 guarded provider runtime 与 future code rewrite / writeback engine 的边界
  2. formal docs 明确 registry、页面代码改写与 cross-spec code writeback 仍由下游工单承接
  3. formal docs 明确 `026` 与 `025` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `025` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 runtime request、result reporting、CLI surface 与 downstream code-rewrite guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 code rewrite / writeback 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/plan.md`, `specs/026-frontend-program-guarded-provider-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 guarded provider runtime、explicit guard 与 downstream boundary 保持单一真值
  3. 当前分支上的 `026` formal docs 可作为后续进入 guarded provider runtime 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService guarded provider runtime packaging slice

### Task 4.1 先写 failing tests 固定 guarded provider runtime request/result 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 guarded provider runtime request 的 handoff linkage、pending inputs 与 explicit confirmation guard
  2. 单测明确覆盖 runtime result 的 invocation result、patch summary 与 remaining blockers
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 runtime truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 guarded provider runtime packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 provider handoff payload 生成 guarded runtime request/result
  2. 实现保持 explicit guard，不引入页面代码改写、cross-spec code writeback 或默认 provider auto execution
  3. 实现不改写 `025` handoff truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/026-frontend-program-guarded-provider-runtime-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/026-frontend-program-guarded-provider-runtime-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program guarded provider runtime CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI runtime 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 guarded provider runtime 的确认、execute 与结果输出
  2. 集成测试明确覆盖 runtime 结果不会被误表述成页面代码已改写
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 runtime surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 guarded provider runtime CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能暴露 guarded provider runtime 的显式确认与结果回报
  2. 实现保持 explicit execute surface，不挂接到默认 remediation execute
  3. 实现不进入页面代码改写、cross-spec code writeback 或默认 provider auto execution
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/026-frontend-program-guarded-provider-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/026-frontend-program-guarded-provider-runtime-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/026-frontend-program-guarded-provider-runtime-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
