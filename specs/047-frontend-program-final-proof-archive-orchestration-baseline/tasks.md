---
related_doc:
  - "specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Final Proof Archive Orchestration Baseline

**编号**：`047-frontend-program-final-proof-archive-orchestration-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md（FR-047-001 ~ FR-047-009 / SC-047-001 ~ SC-047-005）

---

## 分批策略

```text
Batch 1: final proof archive orchestration truth freeze
Batch 2: orchestration contract / result boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService final proof archive packaging slice
Batch 5: program final proof archive CLI surface slice
```

---

## 执行护栏

- `047` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `047` 不得改写 `046` final proof closure artifact truth 或更上游 truth。
- `047` 不得在当前 child work item 中直接启用 archive artifact persistence 或默认 auto-fix。
- `047` 不得把 final proof archive orchestration 偷渡成新的默认 execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/047-frontend-program-final-proof-archive-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/047-frontend-program-final-proof-archive-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：final proof archive orchestration truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `047` 是 `046` 下游的 final proof archive orchestration child work item
  2. `spec.md` 明确 orchestration 只消费 `046` final proof closure artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `047` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 archive artifact persistence 不属于当前 work item
  2. formal docs 明确 final proof archive orchestration 必须显式确认，不得默认触发
  3. formal docs 明确 final proof archive orchestration 不等于 archive artifact 已完成
- **验证**：scope review

### Task 1.3 冻结 orchestration 输入与结果回报字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 最小输入包含 closure artifact linkage、closure state、written paths、remaining blockers 与 source linkage
  2. formal docs 明确最小结果回报包含 archive state、archive result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确结果诚实边界，不得把 orchestration result 伪装成 archive artifact 已落盘
- **验证**：文档对账

---

## Batch 2：orchestration contract / result boundary freeze

### Task 2.1 冻结 final proof archive request responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 request 只读消费 `046` closure artifact truth
  2. formal docs 明确 request 不承担 archive artifact writer responsibility
  3. formal docs 明确 request contract 可直接为 `ProgramService` 实现服务
- **验证**：contract review

### Task 2.2 冻结 result honesty 与 downstream archive artifact 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 orchestration 输出必须诚实回报 archive state、archive result、written paths 与 remaining blockers
  2. formal docs 明确 CLI/report 只展示当前 orchestration truth，不偷渡 future archive artifact
  3. formal docs 明确 dry-run 保持 preview-only
- **验证**：文档对账

### Task 2.3 冻结 downstream archive artifact handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 future archive artifact persistence 仍需单独 child work item 承接
  2. formal docs 明确当前实现优先级是 orchestration guard / packaging / result reporting
  3. reviewer 能从 tasks 直接读出 downstream handoff
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T23
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `core / cli / tests` 的推荐触点
  2. formal docs 明确 Batch 4 与 Batch 5 的 ownership 不重叠
  3. implementation 进入前已有清晰 touched-files baseline
- **验证**：plan/tasks review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 unit tests 覆盖 request/result packaging、guard、remaining blockers honesty
  2. formal docs 明确 integration tests 覆盖 CLI dry-run preview 与 execute confirmation surface
  3. formal docs 明确进入实现前必须先运行 `uv run ai-sdlc verify constraints`
- **验证**：文档对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P0
- **依赖**：T32
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/plan.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/tasks.md`, `specs/047-frontend-program-final-proof-archive-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md / plan.md / tasks.md` 相互引用一致
  2. `uv run ai-sdlc verify constraints` 无 blocker
  3. `task-execution-log.md` 追加 baseline freeze 记录
- **验证**：`uv run ai-sdlc verify constraints`

---

## Batch 4：ProgramService final proof archive packaging slice

### Task 4.1 先写 failing tests 固定 request/result 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单元测试明确覆盖 final proof archive request 只读消费 closure artifact truth
  2. 单元测试明确覆盖 execute 路径的显式确认 guard 与 remaining blockers honesty
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 archive orchestration surface
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 final proof archive request/result packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService` 提供 final proof archive request/result surface
  2. execute 路径保持显式确认，不默认写 archive artifact
  3. 结果对象诚实回报 archive state、archive result、written paths 与 remaining blockers
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/047-frontend-program-final-proof-archive-orchestration-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/047-frontend-program-final-proof-archive-orchestration-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program final proof archive CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI final proof archive 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 archive result 输出与 report 落盘
  2. 集成测试明确覆盖 dry-run 的 guard / preview 语义
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 final proof archive surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 final proof archive CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 会在显式确认后的 execute 路径输出 canonical archive result
  2. CLI 终端与 report 会诚实显示 archive result 与 remaining blockers
  3. CLI 默认 dry-run 行为保持不变，不默认写出 archive artifact
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/047-frontend-program-final-proof-archive-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run pytest tests/unit/test_program_service.py -q`、`uv run ruff check src tests`、`git diff --check -- specs/047-frontend-program-final-proof-archive-orchestration-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/047-frontend-program-final-proof-archive-orchestration-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`, `uv run ai-sdlc verify constraints`
