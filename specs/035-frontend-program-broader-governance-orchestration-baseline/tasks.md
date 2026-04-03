---
related_doc:
  - "specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Broader Governance Orchestration Baseline

**编号**：`035-frontend-program-broader-governance-orchestration-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-035-001 ~ FR-035-009 / SC-035-001 ~ SC-035-005）

---

## 分批策略

```text
Batch 1: broader governance orchestration truth freeze
Batch 2: orchestration contract / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService broader governance packaging slice
Batch 5: program broader governance CLI surface slice
```

---

## 执行护栏

- `035` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `035` 不得改写 `034` guarded registry artifact truth 或更上游 truth。
- `035` 不得在当前 child work item 中直接启用 final code rewrite / governance execution 或默认 auto-fix。
- `035` 不得把 broader governance orchestration 偷渡成新的默认 execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/035-frontend-program-broader-governance-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/035-frontend-program-broader-governance-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：broader governance orchestration truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `035` 是 `034` 下游的 broader governance orchestration child work item
  2. `spec.md` 明确 orchestration 只消费 `034` guarded registry artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `035` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 final code rewrite / governance execution 不属于当前 work item
  2. formal docs 明确 broader governance orchestration 必须显式确认，不得默认触发
  3. formal docs 明确 broader governance orchestration 不等于 final governance 已执行
- **验证**：scope review

### Task 1.3 冻结 orchestration 输入与结果回报字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 输入至少包括 artifact linkage、registry state、written paths 与 remaining blockers
  2. formal docs 明确 orchestration 结果至少包括 orchestration result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确 `035` 不新增第二套 broader governance orchestration truth
- **验证**：truth-order review

---

## Batch 2：orchestration contract / result boundary freeze

### Task 2.1 冻结 broader governance responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `035` 只负责 broader governance orchestration
  2. formal docs 明确 orchestration 不默认扩张到 final governance engine
  3. formal docs 明确与 `034` artifact truth 的关系
- **验证**：responsibility review

### Task 2.2 冻结 result honesty 与 downstream final governance 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 结果必须诚实回报 orchestration result、written paths 与 remaining blockers
  2. formal docs 明确 broader governance orchestration 不等于 final governance 已执行或页面代码已全面安全改写
  3. formal docs 明确 downstream final governance 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream final governance handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 broader governance orchestration 与 future final governance 的边界
  2. formal docs 明确 final code rewrite / governance execution 仍由下游工单承接
  3. formal docs 明确 `035` 与 `034` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `034` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 broader governance request/result、CLI surface 与 downstream final-governance guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 final governance 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/plan.md`, `specs/035-frontend-program-broader-governance-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 broader governance orchestration、explicit guard 与 downstream boundary 保持单一真值
  3. 当前分支上的 `035` formal docs 可作为后续进入 broader governance 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService broader governance packaging slice

### Task 4.1 先写 failing tests 固定 broader governance request/result 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 broader governance request/result 的 artifact linkage、orchestration state 与 explicit confirmation guard
  2. 单测明确覆盖 final governance 不会在当前 baseline 被隐式执行
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 broader governance truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 broader governance packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 `034` registry artifact 生成 broader governance request/result
  2. 实现保持 broader governance packaging，不引入 final code rewrite / governance execution
  3. 实现不改写 `034` registry artifact truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/035-frontend-program-broader-governance-orchestration-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/035-frontend-program-broader-governance-orchestration-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program broader governance CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI broader governance 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 orchestration result 输出与 report 落盘
  2. 集成测试明确覆盖 dry-run 的 guard / preview 语义
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 broader governance surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 broader governance CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能在显式 execute 下回报 orchestration result 与 remaining blockers
  2. 实现保持 broader governance output 为独立显式 surface，不挂接到默认 guarded-registry execute
  3. 实现不进入 final code rewrite / governance execution
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/035-frontend-program-broader-governance-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/035-frontend-program-broader-governance-orchestration-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/035-frontend-program-broader-governance-orchestration-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
