---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
---
# 任务分解：Frontend Program Orchestration Baseline

**编号**：`019-frontend-program-orchestration-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-019-001 ~ FR-019-012 / SC-019-001 ~ SC-019-005）

---

## 分批策略

```text
Batch 1: program frontend baseline freeze
Batch 2: readiness / status / integrate boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: program frontend readiness aggregation slice
Batch 5: program CLI frontend readiness surface slice
```

---

## 执行护栏

- `019` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `019` 不得改写 `014` 已冻结的 runtime attachment truth。
- `019` 不得改写 `018` 已冻结的 frontend gate summary truth。
- `019` 不得在当前 child work item 中直接启用 program auto-scan、program auto-attach、program auto-fix、registry 或 cross-spec writeback。
- `019` 不得默认扩张 `program --execute` 为新的前端自动编排入口。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 `ProgramService` 的 per-spec frontend readiness aggregation，不放行 CLI execute runtime 或 writeback。
- 当前第二批实现只放行 `program status / integrate --dry-run` 的 frontend readiness surface，不放行 execute runtime、registry 或 auto-fix。

---

## Batch 1：program frontend baseline freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `019` 是 `014 / 018` 下游的 frontend program orchestration child work item
  2. `spec.md` 明确 program-level frontend orchestration 只消费既有 per-spec truth
  3. `spec.md` 不再依赖临时对话才能解释 `019` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 execute guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 auto-scan、auto-attach、auto-fix、registry 与 cross-spec writeback 不属于当前 work item
  2. formal docs 明确 `program --execute` 的前端 runtime 仍是下游 guarded 能力
  3. 不再出现 program-level frontend orchestration 被表述成默认 side effect 的表述
- **验证**：scope review

### Task 1.3 冻结 readiness truth 的来源链接

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`, `specs/019-frontend-program-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 runtime attachment 与 frontend gate summary 分别来自 `014` 与 `018`
  2. formal docs 明确 `019` 不新增第二套 program 私有 frontend truth
  3. formal docs 明确 readiness 以 spec 粒度暴露，而不是伪全局 verdict
- **验证**：truth-order review

---

## Batch 2：readiness / status / integrate boundary freeze

### Task 2.1 冻结 program status / plan / integrate 的 frontend responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `program status` 的 frontend readiness 展示责任
  2. formal docs 明确 `program plan` 与 `program integrate --dry-run` 的 frontend hint / guard 责任
  3. formal docs 明确这些 surface 只做只读聚合，不默认触发写入
- **验证**：responsibility review

### Task 2.2 冻结 honesty / gap surfacing 规则

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确缺口、未接线、来源不明与 invalid summary 必须诚实暴露
  2. formal docs 明确不能把 readiness 缺口静默吞成 program PASS
  3. formal docs 明确最小暴露面包括 readiness state、coverage gaps、blockers 与 source linkage
- **验证**：语义对账

### Task 2.3 冻结 downstream handoff 与推荐实现起点

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`, `specs/019-frontend-program-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确实现起点优先是 `program_service.py` readiness aggregation 与 `program_cmd.py` dry-run/status surface
  2. formal docs 明确更重的 execute runtime 仍由下游工单承接
  3. formal docs 明确 `019` 与 `014 / 018` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/019-frontend-program-orchestration-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `014` / `018` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/019-frontend-program-orchestration-baseline/plan.md`, `specs/019-frontend-program-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 readiness aggregation、status surface、integrate dry-run hints 与 execute guard
  2. `tasks.md` 明确当前 docs baseline 完成后仍不直接放行 execute runtime / auto-fix
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/019-frontend-program-orchestration-baseline/spec.md`, `specs/019-frontend-program-orchestration-baseline/plan.md`, `specs/019-frontend-program-orchestration-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 program-level frontend orchestration truth、honesty 与 handoff 保持单一真值
  3. 当前分支上的 `019` formal docs 可作为后续进入 program readiness aggregation 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：program frontend readiness aggregation slice

### Task 4.1 先写 failing tests 固定 per-spec frontend readiness aggregation 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_program_service.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 frontend-ready spec 的 per-spec readiness 聚合
  2. 单测明确覆盖 frontend artifact 缺失时的缺口与 blocker 聚合
  3. 首次运行定向测试时必须出现预期失败，证明 `program_service.py` 尚未聚合 frontend readiness
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.2 实现最小 program frontend readiness aggregation

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/program_service.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService` 能按 spec 粒度聚合 frontend readiness，并消费 `014` / `018` 既有 truth
  2. readiness payload 至少暴露 state、coverage gaps、blockers 与 source linkage
  3. 实现保持只读聚合，不引入 program execute runtime 或 writeback
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_program_service.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_program_service.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：program CLI frontend readiness surface slice

### Task 5.1 先写 failing tests 固定 program CLI 的 frontend readiness 输出语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/integration/test_cli_program.py`
- **可并行**：否
- **验收标准**：
  1. 集成测试明确覆盖 `program status` 的 frontend readiness 输出
  2. 集成测试明确覆盖 `program integrate --dry-run` 的 frontend hint 输出
  3. 首次运行定向测试时必须出现预期失败，证明 `program_cmd.py` 尚未渲染 frontend readiness
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.2 实现最小 program CLI frontend readiness surface

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/cli/program_cmd.py`
- **可并行**：否
- **验收标准**：
  1. `program status` 能暴露 per-spec frontend readiness
  2. `program integrate --dry-run` 能暴露最小 frontend hint，而不进入 execute runtime
  3. 实现保持 scoped user-facing surface，不改写 manifest 语义或 execute gate
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`

### Task 5.3 Fresh verify 并追加 CLI batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/integration/test_cli_program.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/cli tests/integration` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 CLI batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/integration/test_cli_program.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/cli tests/integration`, `uv run ai-sdlc verify constraints`
