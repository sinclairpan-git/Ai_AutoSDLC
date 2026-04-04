---
related_doc:
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Program Final Proof Archive Project Cleanup Baseline

**编号**：`050-frontend-program-final-proof-archive-project-cleanup-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md（FR-050-001 ~ FR-050-010 / SC-050-001 ~ SC-050-005）

---

## 分批策略

```text
Batch 1: final proof archive project cleanup truth freeze
Batch 2: cleanup service / artifact boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService final proof archive project cleanup slice
Batch 5: program final proof archive project cleanup output slice
```

---

## 执行护栏

- `050` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `050` 不得改写 `049` thread archive truth 或更上游 truth。
- `050` 不得把 final proof archive project cleanup 偷渡成新的默认 execute side effect。
- `050` 不得扩张成任意 workspace mutation engine，不得执行未定义删除或未声明的 cleanup 行为。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：final proof archive project cleanup truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `050` 是 `049` 下游的 final proof archive project cleanup child work item
  2. `spec.md` 明确 cleanup 只消费 `049` thread archive execute truth
  3. `spec.md` 不再依赖临时对话才能解释 `050` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 cleanup execute boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确任意 workspace mutation 不属于当前 work item
  2. formal docs 明确 final proof archive project cleanup 必须显式确认后执行，不得默认触发
  3. formal docs 明确当前 baseline 的 cleanup 结果必须诚实回报 deferred / blocked / skipped
- **验证**：scope review

### Task 1.3 冻结 cleanup 输入、输出与 artifact 字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 cleanup 输入至少包括 thread archive source linkage、thread archive result、written paths、remaining blockers 与 warnings
  2. formal docs 明确 cleanup 输出至少包括 cleanup state、cleanup result、written paths、remaining blockers 与 source linkage
  3. formal docs 明确 execute 后允许写入 canonical cleanup artifact，但不新增第二套 truth
- **验证**：truth-order review

---

## Batch 2：cleanup service / artifact boundary freeze

### Task 2.1 冻结 final proof archive project cleanup service responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `050` 只负责 bounded project cleanup materialization
  2. formal docs 明确 cleanup 不默认扩张到 thread archive 之外的 mutation
  3. formal docs 明确与 `049` thread archive truth 的关系
- **验证**：responsibility review

### Task 2.2 冻结 bounded mutation 语义、artifact strategy 与 result honesty 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 cleanup 输出必须诚实回报 cleanup state、cleanup result 与 remaining blockers
  2. formal docs 明确 bounded mutation 语义与 readonly upstream truth order
  3. formal docs 明确 cleanup artifact 只记录 canonical cleanup truth，不伪造额外 side effect
- **验证**：语义对账

### Task 2.3 冻结 terminal side-effect guard 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 terminal side effect 止于 bounded cleanup baseline
  2. formal docs 明确未定义删除、工作树清理或其他 mutation 仍不由当前工单承接
  3. formal docs 明确 `050` 与 `049` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `049` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 cleanup service、cleanup artifact、cleanup output/report 与 terminal side-effect guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行任意 workspace mutation
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/plan.md`, `specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 final proof archive project cleanup、execute boundary、artifact strategy 与 terminal side-effect guard 保持单一真值
  3. 当前分支上的 `050` formal docs 可作为后续进入 final proof archive project cleanup 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService final proof archive project cleanup slice

### Task 4.1 先写 failing tests 固定 final proof archive project cleanup service 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 final proof archive project cleanup service 的 input linkage、result 字段、artifact writer 与 readonly upstream truth
  2. 单测明确覆盖 execute result 不会在当前 baseline 伪造未定义 cleanup action
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 cleanup truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 final proof archive project cleanup service

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 `049` thread archive truth 生成 bounded cleanup request / result / artifact
  2. 实现保持 cleanup materialization，不引入未定义 workspace mutation
  3. 实现不改写 `049` thread archive truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/050-frontend-program-final-proof-archive-project-cleanup-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/050-frontend-program-final-proof-archive-project-cleanup-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program final proof archive project cleanup output slice

### Task 5.1 先写 failing tests 固定 CLI cleanup 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 execute 成功后的 cleanup result 输出、cleanup artifact 落盘与 report 落盘
  2. 集成测试明确覆盖 dry-run 的 guard / preview 语义
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 cleanup output surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 final proof archive project cleanup CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 会在显式确认后的 execute 路径执行 bounded cleanup 并写入 cleanup artifact
  2. CLI 终端与 report 会诚实显示 cleanup result、remaining blockers 与 cleanup artifact
  3. CLI 默认 dry-run 行为保持不变，不默认进入任意 workspace mutation
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run pytest tests/unit/test_program_service.py -q`、`uv run ruff check src tests`、`git diff --check -- specs/050-frontend-program-final-proof-archive-project-cleanup-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/050-frontend-program-final-proof-archive-project-cleanup-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`, `uv run ai-sdlc verify constraints`
