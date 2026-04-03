---
related_doc:
  - "specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md"
---
# 任务分解：Frontend Program Provider Patch Handoff Baseline

**编号**：`028-frontend-program-provider-patch-handoff-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-028-001 ~ FR-028-009 / SC-028-001 ~ SC-028-005）

---

## 分批策略

```text
Batch 1: patch handoff truth freeze
Batch 2: handoff contract / output boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: ProgramService provider patch handoff packaging slice
Batch 5: program provider patch handoff CLI surface slice
```

---

## 执行护栏

- `028` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `028` 不得改写 `027` runtime artifact truth 或更上游 truth。
- `028` 不得在当前 child work item 中直接启用 patch apply、registry、页面代码改写或 cross-spec code writeback。
- `028` 不得把 patch handoff 偷渡成新的默认 apply side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/028-frontend-program-provider-patch-handoff-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/028-frontend-program-provider-patch-handoff-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。

---

## Batch 1：patch handoff truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `028` 是 `027` 下游的 provider patch handoff child work item
  2. `spec.md` 明确 handoff 只消费 `027` provider runtime artifact truth
  3. `spec.md` 不再依赖临时对话才能解释 `028` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 readonly boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 patch apply、registry、页面代码改写与 cross-spec code writeback 不属于当前 work item
  2. formal docs 明确 patch handoff 保持只读
  3. formal docs 明确 handoff 不等于 patch 已应用
- **验证**：scope review

### Task 1.3 冻结 handoff 输入与输出字段

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 handoff 输入至少包括 runtime artifact linkage、patch availability、per-spec pending inputs 与 source linkage
  2. formal docs 明确 handoff 输出至少包括 patch availability state、remaining blockers、warnings 与 source linkage
  3. formal docs 明确 `028` 不新增第二套 provider patch handoff truth
- **验证**：truth-order review

---

## Batch 2：handoff contract / output boundary freeze

### Task 2.1 冻结 patch handoff responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider patch handoff 的 responsibility
  2. formal docs 明确 handoff 只组织既有 runtime artifact truth，不默认扩张到 patch apply engine
  3. formal docs 明确与 `027` runtime artifact 的关系
- **验证**：responsibility review

### Task 2.2 冻结 output honesty 与 downstream patch apply 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 handoff 输出必须诚实回报 patch availability 与 remaining blockers
  2. formal docs 明确输出不等于 patch 已应用或页面代码已安全改写
  3. formal docs 明确 downstream patch apply 仍需单独工单承接
- **验证**：语义对账

### Task 2.3 冻结 downstream patch-apply handoff 边界

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 provider patch handoff 与 future patch apply / writeback engine 的边界
  2. formal docs 明确 registry、页面代码改写与 cross-spec code writeback 仍由下游工单承接
  3. formal docs 明确 `028` 与 `027` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `027` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 handoff payload/build、readonly CLI surface 与 downstream patch-apply guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 patch apply 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/spec.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/plan.md`, `specs/028-frontend-program-provider-patch-handoff-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 patch handoff、readonly boundary 与 downstream boundary 保持单一真值
  3. 当前分支上的 `028` formal docs 可作为后续进入 provider patch handoff 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：ProgramService provider patch handoff packaging slice

### Task 4.1 先写 failing tests 固定 provider patch handoff payload 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 handoff 的 runtime artifact linkage、patch availability、pending inputs 与 remaining blockers
  2. 单测明确覆盖 handoff 保持只读，不隐式进入 patch apply
  3. 首次运行定向测试时必须出现预期失败，证明 service 尚未暴露该 handoff truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 provider patch handoff packaging

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. service 能从 provider runtime artifact 生成 readonly patch handoff payload
  2. 实现保持只读，不引入 patch apply、页面代码改写或 cross-spec code writeback
  3. 实现不改写 `027` runtime artifact truth
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/028-frontend-program-provider-patch-handoff-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/028-frontend-program-provider-patch-handoff-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program provider patch handoff CLI surface slice

### Task 5.1 先写 failing tests 固定 CLI patch handoff 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 readonly patch handoff 的输出与 report 语义
  2. 集成测试明确覆盖 handoff 不会被误表述成 patch 已应用
  3. 首次运行定向测试时必须出现预期失败，证明 CLI 尚未暴露该 handoff surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 provider patch handoff CLI surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. CLI 能暴露 readonly provider patch handoff 的 patch availability 与 blockers
  2. 实现保持显式 readonly surface，不挂接到默认 apply side effect
  3. 实现不进入 patch apply、页面代码改写或 cross-spec code writeback
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/028-frontend-program-provider-patch-handoff-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/028-frontend-program-provider-patch-handoff-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/028-frontend-program-provider-patch-handoff-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
