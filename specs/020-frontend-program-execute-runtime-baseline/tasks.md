---
related_doc:
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
---
# 任务分解：Frontend Program Execute Runtime Baseline

**编号**：`020-frontend-program-execute-runtime-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-020-001 ~ FR-020-012 / SC-020-001 ~ SC-020-005）

---

## 分批策略

```text
Batch 1: execute runtime truth freeze
Batch 2: execute / recheck / remediation boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: program frontend execute preflight slice
Batch 5: program execute CLI frontend gate surface slice
```

---

## 执行护栏

- `020` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `020` 不得改写 `014` 已冻结的 runtime attachment truth。
- `020` 不得改写 `018` 已冻结的 gate / recheck boundary truth。
- `020` 不得改写 `019` 已冻结的 per-spec readiness truth。
- `020` 不得在当前 child work item 中直接启用 scanner/provider 写入、auto-attach、auto-fix、registry 或 cross-spec writeback。
- `020` 不得把 `program --execute` 扩张成新的默认前端自动编排入口。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 `ProgramService` 的 frontend execute preflight，不放行 recheck loop runtime 或 auto-fix。
- 当前第二批实现只放行 `program integrate --execute` 的 frontend gate / remediation hint surface，不放行 auto-fix、writeback 或 recheck loop。

---

## Batch 1：execute runtime truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `020` 是 `019` 下游的 frontend program execute runtime child work item
  2. `spec.md` 明确 execute runtime 只消费 `019` per-spec readiness truth 与 `018` recheck boundary
  3. `spec.md` 不再依赖临时对话才能解释 `020` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 scanner/provider 写入、auto-attach、auto-fix、registry 与 cross-spec writeback 不属于当前 work item
  2. formal docs 明确 recheck 是 bounded handoff，不是后台 loop
  3. 不再出现 execute runtime 被表述成默认修复器的表述
- **验证**：scope review

### Task 1.3 冻结 execute 输入真值与 source linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 execute gate 的输入至少包括 readiness state、blockers、recheck_required、remediation hint 与 source linkage
  2. formal docs 明确这些输入按 spec 粒度暴露，而不是伪全局 verdict
  3. formal docs 明确 `020` 不新增 program 私有 execute truth
- **验证**：truth-order review

---

## Batch 2：execute / recheck / remediation boundary freeze

### Task 2.1 冻结 execute preflight responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `program integrate --execute` 的 frontend preflight 阻断责任
  2. formal docs 明确 close/dependency/dirty-tree gate 与 frontend execute gate 的关系
  3. formal docs 明确 execute preflight 只做只读决策，不默认触发写入
- **验证**：responsibility review

### Task 2.2 冻结 step-level recheck handoff

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 execute step 后何时需要 frontend recheck
  2. formal docs 明确 recheck 的最小输入/输出与提示边界
  3. formal docs 明确 recheck 不会被实现成无限 loop 或默认 auto-fix 入口
- **验证**：语义对账

### Task 2.3 冻结 remediation hint 与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation hint 只做诊断 handoff，不默认触发 auto-fix
  2. formal docs 明确未来 auto-fix engine 仍由下游工单承接
  3. formal docs 明确 `020` 与 `014 / 018 / 019` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `019` / `018` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 execute preflight、recheck handoff、remediation hint 与 downstream auto-fix guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 auto-fix / writeback 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 execute runtime、recheck 与 remediation hint 保持单一真值
  3. 当前分支上的 `020` formal docs 可作为后续进入 execute preflight 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：program frontend execute preflight slice

### Task 4.1 先写 failing tests 固定 frontend execute preflight 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 spec 已 close 但 frontend readiness 不 clear 时的 execute 阻断
  2. 单测明确覆盖 spec 已 close 且 frontend readiness ready 时的 execute 放行
  3. 首次运行定向测试时必须出现预期失败，证明 `evaluate_execute_gates()` 尚未消费 frontend readiness
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 frontend execute preflight

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService.evaluate_execute_gates()` 能按 spec 粒度消费 frontend readiness truth
  2. execute gate 至少能诚实暴露 frontend execute blockers 与最小 remediation hint
  3. 实现保持只读 preflight，不引入 recheck loop、auto-fix 或 writeback
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program execute CLI frontend gate surface slice

### Task 5.1 先写 failing tests 固定 execute CLI frontend gate 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 `program integrate --execute` 的 frontend execute gate 阻断输出
  2. 集成测试明确覆盖 ready frontend execute preflight 的通过输出
  3. 首次运行定向测试时必须出现预期失败，证明 execute CLI 尚未渲染 frontend gate surface
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 execute CLI frontend gate surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. `program integrate --execute` 能暴露 frontend execute gate 的阻断或通过信息
  2. 失败时能暴露最小 remediation hint，而不触发 auto-fix 或 recheck loop
  3. 实现保持 scoped user-facing surface，不改写 dry-run/status truth
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
