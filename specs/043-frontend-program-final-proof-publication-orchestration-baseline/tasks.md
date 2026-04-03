---
related_doc:
  - "specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Publication Orchestration Baseline

**编号**：`043-frontend-program-final-proof-publication-orchestration-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-043-001 ~ FR-043-009 / SC-043-001 ~ SC-043-005）

---

## 分批策略

```text
Batch 1: final proof publication orchestration truth freeze
Batch 2: orchestration contract / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService final proof publication packaging slice
Batch 5: program final proof publication CLI surface slice
```

---

## 执行护栏

- `043` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `043` 不得改写 `042` persisted write proof artifact truth 或更上游 truth。
- `043` 不得在当前 child work item 中直接启用 publication artifact persistence 或默认 auto-fix。
- `043` 不得把 final proof publication orchestration 偷渡成新的默认 execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/043-frontend-program-final-proof-publication-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/043-frontend-program-final-proof-publication-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：final proof publication orchestration truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `043` 是 `042` 下游的 final proof publication orchestration child work item
  2. `spec.md` 明确 orchestration 只消费 `042` persisted write proof artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `043` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 publication artifact persistence 不属于当前 work item
  2. formal docs 明确 final proof publication orchestration 必须显式确认，不得默认触发
  3. formal docs 明确 final proof publication orchestration 不等于 publication artifact 已完成
- **验证**：scope review

### Task 1.3 冻结 orchestration 输入与结果回报字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 输入至少包括 artifact linkage、proof state、written paths 与 remaining blockers
  2. formal docs 明确 orchestration 结果至少包括 publication result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确 `043` 不新增第二套 final proof publication orchestration truth
- **验证**：truth-order review

---

## Batch 2：orchestration contract / result boundary freeze

### Task 2.1 冻结 final proof publication responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `043` 只负责 final proof publication orchestration
  2. formal docs 明确 orchestration 不默认扩张到 publication artifact persistence
  3. formal docs 明确与 `042` artifact truth 的关系
- **验证**：responsibility review

### Task 2.2 冻结 result honesty 与 downstream publication artifact persistence 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 结果必须诚实回报 publication result、written paths 与 remaining blockers
  2. formal docs 明确 final proof publication orchestration 不等于最终 publication artifact 已完成
  3. formal docs 明确 downstream publication artifact persistence 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream publication artifact persistence handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 final proof publication orchestration 与 future publication artifact persistence 的边界
  2. formal docs 明确 publication artifact persistence 仍由下游工单承接
  3. formal docs 明确 `043` 与 `042` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `042` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 final proof publication request/result、CLI surface 与 downstream publication-artifact-persistence guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 publication artifact persistence 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/plan.md`, `specs/043-frontend-program-final-proof-publication-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 final proof publication orchestration、explicit guard 与 downstream boundary 保持单一真值
  3. 当前分支上的 `043` formal docs 可作为后续进入 final proof publication 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService final proof publication packaging slice

### Task 4.1 先写 failing tests 固定 final proof publication request/result 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 final proof publication request/result 的 artifact linkage、publication state 与 explicit confirmation guard
  2. 单测明确覆盖 publication artifact persistence 不会在当前 baseline 被隐式执行
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 final proof publication truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 final proof publication packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 `042` persisted write proof artifact 生成 final proof publication request/result
  2. 实现保持 final proof publication packaging，不引入 publication artifact persistence
  3. 实现不改写 `042` persisted write proof artifact truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/043-frontend-program-final-proof-publication-orchestration-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/043-frontend-program-final-proof-publication-orchestration-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program final proof publication CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI final proof publication 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 publication result 输出与 report 落盘
  2. 集成测试明确覆盖 dry-run 的 guard / preview 语义
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 final proof publication surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 final proof publication CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 会在显式确认后的 execute 路径输出 canonical publication result
  2. CLI 终端与 report 会诚实显示 publication result 与 remaining blockers
  3. CLI 默认 dry-run 行为保持不变，不默认写出 publication artifact
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/043-frontend-program-final-proof-publication-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run pytest tests/unit/test_program_service.py -q`、`uv run ruff check src tests`、`git diff --check -- specs/043-frontend-program-final-proof-publication-orchestration-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/043-frontend-program-final-proof-publication-orchestration-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`, `uv run ai-sdlc verify constraints`
