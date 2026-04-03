---
related_doc:
  - "specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md"
---
# 任务分解：Frontend Program Provider Handoff Baseline

**编号**：`025-frontend-program-provider-handoff-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-025-001 ~ FR-025-009 / SC-025-001 ~ SC-025-005）

---

## 分批策略

```text
Batch 1: provider handoff truth freeze
Batch 2: payload / explicit boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService provider handoff packaging slice
Batch 5: program provider handoff CLI surface slice
```

---

## 执行护栏

- `025` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `025` 不得改写 `024` 已冻结的 remediation writeback truth。
- `025` 不得在当前 child work item 中直接启用 provider runtime、registry、cross-spec code writeback 或页面代码改写。
- `025` 不得把 provider handoff 偷渡成新的默认 remediation side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/025-frontend-program-provider-handoff-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/025-frontend-program-provider-handoff-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：provider handoff truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `025` 是 `024` 下游的 frontend provider handoff child work item
  2. `spec.md` 明确 handoff 只消费 `024` writeback artifact 与既有 remediation step truth
  3. `spec.md` 不再依赖临时对话才能解释 `025` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit readonly boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider runtime、registry、页面代码改写与 cross-spec code writeback 不属于当前 work item
  2. formal docs 明确 provider handoff 不等于 provider 已执行
  3. formal docs 明确 handoff 是只读 payload
- **验证**：scope review

### Task 1.3 冻结 handoff 字段与 writeback linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`, `specs/025-frontend-program-provider-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 handoff payload 至少包括 writeback artifact linkage、per-spec pending inputs、suggested next actions 与 source linkage
  2. formal docs 明确 `025` 不新增第二套 remediation truth
  3. formal docs 明确 handoff 不取代 writeback artifact 本身
- **验证**：truth-order review

---

## Batch 2：payload / explicit boundary freeze

### Task 2.1 冻结 provider handoff responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider handoff payload 的 responsibility
  2. formal docs 明确 handoff 只组织既有 writeback truth，不默认扩张 execute/writeback contract
  3. formal docs 明确与 `024` writeback artifact 的关系
- **验证**：responsibility review

### Task 2.2 冻结 handoff honesty 与 explicit approval boundary

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 handoff 只表示可交接输入，不代表 provider 已执行
  2. formal docs 明确后续 provider runtime 仍需显式审批/单独工单承接
  3. formal docs 明确 handoff 不会被表述成代码已改写
- **验证**：语义对账

### Task 2.3 冻结 downstream provider/runtime 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`, `specs/025-frontend-program-provider-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider handoff 与 future provider runtime / code rewrite 的边界
  2. formal docs 明确 registry、页面代码改写与 cross-spec code writeback 仍由下游工单承接
  3. formal docs 明确 `025` 与 `024` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `024` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/plan.md`, `specs/025-frontend-program-provider-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 provider handoff payload、service packaging、CLI handoff surface 与 downstream provider guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 provider runtime / code rewrite 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/spec.md`, `specs/025-frontend-program-provider-handoff-baseline/plan.md`, `specs/025-frontend-program-provider-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 provider handoff、writeback linkage 与 downstream boundary 保持单一真值
  3. 当前分支上的 `025` formal docs 可作为后续进入 provider handoff 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService provider handoff packaging slice

### Task 4.1 先写 failing tests 固定 provider handoff payload 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 provider handoff payload 的 writeback linkage、per-spec pending inputs 与 source linkage
  2. 单测明确覆盖 handoff 不会伪装成 provider 已执行
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 handoff truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 provider handoff payload packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 writeback artifact 与 remediation step truth 生成 provider handoff payload
  2. payload 保持只读，不引入 provider runtime、页面代码改写或 cross-spec code writeback
  3. 实现不改写 `024` writeback truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/025-frontend-program-provider-handoff-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/025-frontend-program-provider-handoff-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program provider handoff CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI handoff 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 provider handoff payload 的 CLI/report 输出
  2. 集成测试明确覆盖 handoff 只读与 source linkage
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 handoff surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 provider handoff CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能暴露 provider handoff payload 的关键信息
  2. 实现保持只读 handoff，不挂接到 provider runtime
  3. 实现不修改默认 `program integrate --execute` 或 `program remediate --execute` 真值
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/025-frontend-program-provider-handoff-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/025-frontend-program-provider-handoff-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/025-frontend-program-provider-handoff-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
