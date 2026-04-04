---
related_doc:
  - "specs/048-frontend-program-final-proof-archive-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Thread Archive Baseline

**编号**：`049-frontend-program-final-proof-archive-thread-archive-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md（FR-049-001 ~ FR-049-010 / SC-049-001 ~ SC-049-005）

---

## 分批策略

```text
Batch 1: final proof archive thread archive truth freeze
Batch 2: thread archive service / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService final proof archive thread archive slice
Batch 5: program final proof archive thread archive output slice
```

---

## 执行护栏

- `049` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `049` 不得改写 `048` final proof archive artifact truth 或更上游 truth。
- `049` 不得在当前 child work item 中直接启用 project cleanup 或其他额外 side effect。
- `049` 不得把 final proof archive thread archive 偷渡成新的默认 execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：final proof archive thread archive truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `049` 是 `048` 下游的 final proof archive thread archive child work item
  2. `spec.md` 明确 thread archive 只消费 `048` final proof archive artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `049` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 thread archive execute boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 project cleanup 不属于当前 work item
  2. formal docs 明确 final proof archive thread archive 必须显式确认后执行，不得默认触发
  3. formal docs 明确 thread archive 只代表 bounded archive action，不代表更宽 side effect 已完成
- **验证**：scope review

### Task 1.3 冻结 thread archive 输入与输出字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 thread archive 输入至少包括 artifact linkage、archive state、written paths、remaining blockers 与 source linkage
  2. formal docs 明确 thread archive 输出至少包括 archive state、archive result、remaining blockers 与 source linkage
  3. formal docs 明确 `049` 不新增第二套 final proof archive thread archive truth
- **验证**：truth-order review

---

## Batch 2：thread archive service / result boundary freeze

### Task 2.1 冻结 final proof archive thread archive service responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `049` 只负责 final proof archive thread archive materialization
  2. formal docs 明确 thread archive 不默认扩张到 project cleanup
  3. formal docs 明确与 `048` archive artifact truth 的关系
- **验证**：responsibility review

### Task 2.2 冻结 bounded mutation 语义与 result honesty 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 thread archive 输出必须诚实回报 archive state、archive result 与 remaining blockers
  2. formal docs 明确 bounded mutation 语义与 readonly upstream truth order
  3. formal docs 明确 result reporting 不得伪造额外 side effect
- **验证**：语义对账

### Task 2.3 冻结 terminal side-effect guard 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 terminal side effect 止于 thread archive
  2. formal docs 明确 project cleanup 仍不由当前工单承接
  3. formal docs 明确 `049` 与 `048` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `048` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 final proof archive thread archive service、thread archive output/report 与 terminal side-effect guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 project cleanup 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/plan.md`, `specs/049-frontend-program-final-proof-archive-thread-archive-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 final proof archive thread archive、execute boundary 与 terminal side-effect guard 保持单一真值
  3. 当前分支上的 `049` formal docs 可作为后续进入 final proof archive thread archive 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService final proof archive thread archive slice

### Task 4.1 先写 failing tests 固定 final proof archive thread archive service 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 final proof archive thread archive service 的 input linkage、result 字段与 readonly upstream truth
  2. 单测明确覆盖 execute result 不会在当前 baseline 隐式进入 project cleanup
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 thread archive truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 final proof archive thread archive service

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 `048` final proof archive artifact 生成 bounded thread archive result
  2. 实现保持 thread archive materialization，不引入 project cleanup
  3. 实现不改写 `048` final proof archive artifact truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/049-frontend-program-final-proof-archive-thread-archive-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/049-frontend-program-final-proof-archive-thread-archive-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program final proof archive thread archive output slice

### Task 5.1 先写 failing tests 固定 CLI thread archive 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 thread archive result 输出与 report 落盘
  2. 集成测试明确覆盖 dry-run 的 guard / preview 语义
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 thread archive output surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 final proof archive thread archive CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 会在显式确认后的 execute 路径执行 bounded thread archive
  2. CLI 终端与 report 会诚实显示 thread archive result 与 remaining blockers
  3. CLI 默认 dry-run 行为保持不变，不默认进入 project cleanup
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/049-frontend-program-final-proof-archive-thread-archive-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run pytest tests/unit/test_program_service.py -q`、`uv run ruff check src tests`、`git diff --check -- specs/049-frontend-program-final-proof-archive-thread-archive-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/049-frontend-program-final-proof-archive-thread-archive-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`, `uv run ai-sdlc verify constraints`
