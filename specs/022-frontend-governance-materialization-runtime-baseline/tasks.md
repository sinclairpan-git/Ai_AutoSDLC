---
related_doc:
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/021-frontend-program-remediation-runtime-baseline/spec.md"
---
# 任务分解：Frontend Governance Materialization Runtime Baseline

**编号**：`022-frontend-governance-materialization-runtime-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-022-001 ~ FR-022-009 / SC-022-001 ~ SC-022-005）

---

## 分批策略

```text
Batch 1: materialization runtime truth freeze
Batch 2: command surface / runbook binding freeze
Batch 3: implementation handoff and verification freeze
Batch 4: rules CLI frontend governance materialization command slice
Batch 5: program remediation runbook command binding slice
```

---

## 执行护栏

- `022` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `022` 不得改写 `017` / `018` 已冻结的 governance artifact truth。
- `022` 不得改写 `021` 已冻结的 remediation input truth。
- `022` 不得在当前 child work item 中直接启用 auto-fix、registry、cross-spec writeback、provider runtime 或页面代码改写。
- `022` 不得把 materialization runtime 扩张成新的默认 program execute side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/cli/sub_apps.py`、`tests/integration/test_cli_rules.py`、`specs/022-frontend-governance-materialization-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`、`specs/022-frontend-governance-materialization-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 `rules` CLI 的 frontend governance materialization command，不放行 auto-fix、writeback 或 provider runtime。
- 当前第二批实现只放行 remediation runbook 的真实命令绑定与渲染，不放行自动执行或 cross-spec writeback。

---

## Batch 1：materialization runtime truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `022` 是 `021` 下游的 frontend governance materialization runtime child work item
  2. `spec.md` 明确 materialization runtime 只消费 `017` / `018` builders 与 `021` remediation truth
  3. `spec.md` 不再依赖临时对话才能解释 `022` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 auto-fix、registry、cross-spec writeback、provider runtime 与页面代码改写不属于当前 work item
  2. formal docs 明确 bounded materialization runtime 不等于完整 auto-fix engine
  3. 不再出现 materialization runtime 被表述成默认修复器的表述
- **验证**：scope review

### Task 1.3 冻结 materialization 命令真值与 source linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`, `specs/022-frontend-governance-materialization-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 materialization command 的最小暴露面至少包括 command id、artifact groups、写入根目录与 source linkage
  2. formal docs 明确 remediation runbook 只引用正式命令，不伪造 auto-fix 完成状态
  3. formal docs 明确 `022` 不新增第二套 governance artifact truth
- **验证**：truth-order review

---

## Batch 2：command surface / runbook binding freeze

### Task 2.1 冻结 frontend governance materialization command responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 materialization command 的 responsibility
  2. formal docs 明确 command 只做 canonical governance artifact 写入，不默认写产品代码
  3. formal docs 明确与 `017` / `018` builders 的关系
- **验证**：responsibility review

### Task 2.2 冻结 remediation runbook command binding 与 operator surface

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation runbook command binding 的最小输入/输出与提示边界
  2. formal docs 明确 operator-facing command surface 何时只显示命令、何时仍需人工确认
  3. formal docs 明确 command binding 不会被表述成 auto-fix 已执行
- **验证**：语义对账

### Task 2.3 冻结 downstream handoff 与 future auto-fix boundary

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`, `specs/022-frontend-governance-materialization-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 materialization runtime 与 future auto-fix engine 的边界
  2. formal docs 明确 writeback / registry / provider runtime 仍由下游工单承接
  3. formal docs 明确 `022` 与 `017 / 018 / 021` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `cli / core / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `017` / `018` / `021` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/plan.md`, `specs/022-frontend-governance-materialization-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 CLI command、runbook command binding 与 downstream auto-fix guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 auto-fix / writeback 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/spec.md`, `specs/022-frontend-governance-materialization-runtime-baseline/plan.md`, `specs/022-frontend-governance-materialization-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 materialization runtime、command surface 与 runbook binding 保持单一真值
  3. 当前分支上的 `022` formal docs 可作为后续进入 materialization command 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：rules CLI frontend governance materialization command slice

### Task 4.1 先写 failing tests 固定 frontend governance materialization command 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/integration/test_cli_rules.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 `rules materialize-frontend-mvp` 的成功写入结果
  2. 集成测试明确覆盖 canonical gate / generation artifact roots
  3. 首次运行定向测试时必须出现预期失败，证明正式 CLI command 尚未存在
- **验证**：`uv run pytest tests/integration/test_cli_rules.py -q`

### Task 4.2 实现最小 frontend governance materialization command

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/cli/sub_apps.py`
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc rules materialize-frontend-mvp` 能 materialize canonical gate / generation artifact roots
  2. 输出能诚实暴露 materialized file count 或关键路径
  3. 实现保持 bounded command surface，不进入 auto-fix、writeback 或 provider runtime
- **验证**：`uv run pytest tests/integration/test_cli_rules.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_rules.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/022-frontend-governance-materialization-runtime-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_rules.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/022-frontend-governance-materialization-runtime-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program remediation runbook command binding slice

### Task 5.1 先写 failing tests 固定 remediation runbook command binding 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_program_service.py`, `tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 remediation payload 对真实命令的绑定
  2. 集成测试明确覆盖 execute failure output/report 中的 remediation commands
  3. 首次运行定向测试时必须出现预期失败，证明 remediation handoff 尚未渲染真实命令
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 program remediation runbook command binding

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/core/program_service.py`, `src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. remediation payload 能暴露 machine-consumable recommended commands
  2. execute failure output/report 能渲染 remediation commands
  3. 实现保持 command-binding only，不自动执行或写产品代码
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI/core batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/022-frontend-governance-materialization-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 与 `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/022-frontend-governance-materialization-runtime-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/022-frontend-governance-materialization-runtime-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration`, `uv run ai-sdlc verify constraints`
