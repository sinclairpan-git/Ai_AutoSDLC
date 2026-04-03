---
related_doc:
  - "specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Cross-Spec Writeback Orchestration Baseline

**编号**：`031-frontend-program-cross-spec-writeback-orchestration-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-031-001 ~ FR-031-009 / SC-031-001 ~ SC-031-005）

---

## 分批策略

```text
Batch 1: writeback orchestration truth freeze
Batch 2: orchestration contract / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService cross-spec writeback packaging slice
Batch 5: program cross-spec writeback CLI surface slice
```

---

## 执行护栏

- `031` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `031` 不得改写 `030` 已冻结的 patch apply artifact truth。
- `031` 不得在当前 child work item 中直接启用 registry 或 broader code rewrite orchestration。
- `031` 不得把 cross-spec writeback 偷渡成新的默认 remediation/provider side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：writeback orchestration truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `031` 是 `030` 下游的 cross-spec writeback orchestration child work item
  2. `spec.md` 明确 orchestration 只消费 `030` patch apply artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `031` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 registry 与 broader code rewrite orchestration 不属于当前 work item
  2. formal docs 明确 cross-spec writeback 必须显式确认
  3. formal docs 明确 orchestration 不等于 broader governance 已完成
- **验证**：scope review

### Task 1.3 冻结 orchestration 输入与结果回报字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 输入至少包括 artifact linkage、apply state、written paths 与 source linkage
  2. formal docs 明确 orchestration 结果至少包括 orchestration result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确 `031` 不新增第二套 writeback orchestration truth
- **验证**：truth-order review

---

## Batch 2：orchestration contract / result boundary freeze

### Task 2.1 冻结 guarded writeback responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 guarded writeback 的 responsibility
  2. formal docs 明确 orchestration 只组织既有 artifact truth，不默认扩张到 registry/broader orchestration
  3. formal docs 明确与 `030` patch apply artifact 的关系
- **验证**：responsibility review

### Task 2.2 冻结 result honesty 与 downstream registry/broader orchestration 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 结果必须诚实回报 written paths 与 remaining blockers
  2. formal docs 明确结果不等于 registry 或 broader orchestration 已完成
  3. formal docs 明确 downstream broader orchestration 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream broader orchestration handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 cross-spec writeback 与 future registry/broader orchestration 的边界
  2. formal docs 明确 registry 与 broader code rewrite orchestration 仍由下游工单承接
  3. formal docs 明确 `031` 与 `030` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `030` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 writeback request、result reporting、CLI surface 与 downstream broader-orchestration guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 registry/broader orchestration 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/plan.md`, `specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 guarded writeback、explicit guard 与 downstream boundary 保持单一真值
  3. 当前分支上的 `031` formal docs 可作为后续进入 guarded writeback 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService cross-spec writeback packaging slice

### Task 4.1 先写 failing tests 固定 guarded writeback request/result 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 guarded writeback request 的 artifact linkage、written paths 与 explicit confirmation guard
  2. 单测明确覆盖 orchestration result 的 orchestration result、written paths 与 remaining blockers
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 runtime truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 guarded writeback packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 patch apply artifact 生成 guarded writeback request/result
  2. 实现保持 explicit guard，不引入 registry 或 broader code rewrite orchestration
  3. 实现不改写 `030` artifact truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/031-frontend-program-cross-spec-writeback-orchestration-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/031-frontend-program-cross-spec-writeback-orchestration-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program cross-spec writeback CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI orchestration 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 guarded writeback 的确认、execute 与结果输出
  2. 集成测试明确覆盖 orchestration 结果不会被误表述成 registry/broader orchestration 已完成
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 guarded writeback CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能暴露 guarded writeback 的显式确认与结果回报
  2. 实现保持 explicit execute surface，不挂接到默认 remediation/provider execute
  3. 实现不进入 registry 或 broader code rewrite orchestration
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/031-frontend-program-cross-spec-writeback-orchestration-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/031-frontend-program-cross-spec-writeback-orchestration-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
