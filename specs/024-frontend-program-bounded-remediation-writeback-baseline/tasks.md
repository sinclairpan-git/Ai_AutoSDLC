---
related_doc:
  - "specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md"
---
# 任务分解：Frontend Program Bounded Remediation Writeback Baseline

**编号**：`024-frontend-program-bounded-remediation-writeback-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-024-001 ~ FR-024-009 / SC-024-001 ~ SC-024-005）

---

## 分批策略

```text
Batch 1: writeback truth freeze
Batch 2: artifact / explicit boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService canonical remediation writeback slice
Batch 5: program remediate writeback CLI surface slice
```

---

## 执行护栏

- `024` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `024` 不得改写 `023` 已冻结的 remediation runbook / execute truth。
- `024` 不得在当前 child work item 中直接启用 provider runtime、registry、cross-spec code writeback 或页面代码改写。
- `024` 不得把 writeback 偷渡成新的默认 `program integrate --execute` side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/024-frontend-program-bounded-remediation-writeback-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/024-frontend-program-bounded-remediation-writeback-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 `ProgramService` 的 canonical remediation writeback artifact emission，不放行页面代码改写。
- 当前第二批实现只放行独立 `program remediate` execute surface 的 writeback 输出，不放行 provider runtime 或 cross-spec code writeback。

---

## Batch 1：writeback truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `024` 是 `023` 下游的 frontend program bounded remediation writeback child work item
  2. `spec.md` 明确 writeback 只消费 `023` remediation runbook 与 execute result
  3. `spec.md` 不再依赖临时对话才能解释 `024` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit write boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider runtime、registry、页面代码改写与 cross-spec code writeback 不属于当前 work item
  2. formal docs 明确 bounded remediation writeback 不等于完整 auto-fix engine
  3. formal docs 明确它独立于默认 `program integrate --execute`
- **验证**：scope review

### Task 1.3 冻结 artifact 字段、默认路径与 source linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 canonical artifact 至少包括 generated_at、passed、per-spec steps、executed commands、written paths、remaining blockers 与 source linkage
  2. formal docs 明确 canonical artifact 有稳定默认路径
  3. formal docs 明确 `024` 不新增第二套 remediation truth
- **验证**：truth-order review

---

## Batch 2：artifact / explicit boundary freeze

### Task 2.1 冻结 canonical artifact responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 canonical writeback artifact 的 responsibility
  2. formal docs 明确 artifact 只组织既有 remediation execute truth，不默认扩张 execute contract
  3. formal docs 明确与 `023` remediation execute 的关系
- **验证**：responsibility review

### Task 2.2 冻结 writeback timing 与 execute honesty

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 writeback 只在显式 remediation execute 后发生
  2. formal docs 明确 artifact 必须诚实回报写入结果与 remaining blockers
  3. formal docs 明确 writeback 不会被表述成页面代码 auto-fix 已执行
- **验证**：语义对账

### Task 2.3 冻结 downstream auto-fix/provider 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 bounded writeback 与 future auto-fix / provider runtime 的边界
  2. formal docs 明确 code rewrite / registry / provider runtime 仍由下游工单承接
  3. formal docs 明确 `024` 与 `023` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `023` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 canonical artifact、service emission、CLI writeback surface 与 downstream auto-fix guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 provider runtime / code rewrite 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/plan.md`, `specs/024-frontend-program-bounded-remediation-writeback-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 writeback artifact、writeback timing 与 downstream boundary 保持单一真值
  3. 当前分支上的 `024` formal docs 可作为后续进入 bounded remediation writeback 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService canonical remediation writeback slice

### Task 4.1 先写 failing tests 固定 canonical writeback artifact 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 canonical writeback artifact 的默认路径与最小字段
  2. 单测明确覆盖 execute result 被 writeback artifact 复用，而不是重新执行命令
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 writeback truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 canonical remediation writeback artifact emission

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从既有 remediation runbook 与 execute result 生成 canonical writeback payload
  2. service 能把 canonical payload 稳定写入默认 artifact 路径
  3. 实现保持 bounded writeback，不引入 provider runtime、页面代码改写或 cross-spec code writeback
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/024-frontend-program-bounded-remediation-writeback-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/024-frontend-program-bounded-remediation-writeback-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program remediate writeback CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI writeback 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 `program remediate --execute --yes` 的 writeback path 输出
  2. 集成测试明确覆盖 canonical writeback artifact 的默认落盘
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 writeback surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 program remediate writeback CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. `program remediate --execute --yes` 能输出 canonical writeback path
  2. execute 后会稳定落盘 canonical writeback artifact
  3. 实现保持 explicit execute surface，不挂接到默认 `program integrate --execute`
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/024-frontend-program-bounded-remediation-writeback-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/024-frontend-program-bounded-remediation-writeback-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/024-frontend-program-bounded-remediation-writeback-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
