---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Generation Governance Baseline

**编号**：`017-frontend-generation-governance-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-017-001 ~ FR-017-014 / SC-017-001 ~ SC-017-005）

---

## 分批策略

```text
Batch 1: generation truth freeze
Batch 2: constraint object and ordering freeze
Batch 3: implementation handoff and verification freeze
Batch 4: generation constraint models slice
Batch 5: generation constraint artifact slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `017` 不得重新定义 `011` Contract truth、`015` UI Kernel truth 或 `016` Provider truth。
- `017` 不得在当前 child work item 中直接进入完整生成 runtime、gate diagnostics、recheck / auto-fix 或 business project 代码生成实现。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_generation_constraints.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_generation_constraints.py`、`specs/017-frontend-generation-governance-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/generators/frontend_generation_constraint_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`tests/unit/test_frontend_generation_constraint_artifacts.py`、`specs/017-frontend-generation-governance-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `017` 只冻结 generation governance baseline，不默认决定任何 `src/` / `tests/` runtime side effect。
- 当前首批实现只放行 generation constraint 模型/标准体，不放行完整生成 runtime、gate 或 auto-fix 实现。
- 当前第二批实现只放行 generation constraint artifact instantiation，不放行完整生成 runtime、gate verdict 或 auto-fix 实现。
- 只有在用户明确要求进入实现，且 `017` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：generation truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `017` 是 `009` 下游的 generation governance child work item
  2. `spec.md` 明确 generation governance 位于 Contract、Kernel、Provider 与 code generation 之间
  3. `spec.md` 不再依赖临时对话或设计稿才能解释 `017` 的边界
- **验证**：文档对账

### Task 1.2 冻结 generation governance 与上游 / 下游边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 generation governance 不回写 Contract / Kernel / Provider truth
  2. formal docs 明确完整生成 runtime、gate 与 recheck / auto-fix 不属于当前 work item
  3. 不再出现 prompt-only 或隐式默认值可以替代结构化约束集合的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`, `specs/017-frontend-generation-governance-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确完整生成 runtime、gate 与 auto-fix 留在下游工单
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 generation constraint models / artifacts，而不是直接写生成 runtime
- **验证**：scope review

---

## Batch 2：constraint object and ordering freeze

### Task 2.1 冻结 recipe / whitelist / hard rules / token rules / exceptions 对象

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确五类约束对象及其 MVP 边界
  2. formal docs 明确 page recipe 约束、whitelist 与 Hard Rules 的作用差异
  3. formal docs 明确例外不能反向重写 UI Kernel 或不可豁免 Hard Rules
- **验证**：constraint-object review

### Task 2.2 冻结显式引用要求与执行顺序

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确页面生成阶段至少可解析 `recipe declaration / whitelist ref / token rules ref / hard rules set`
  2. formal docs 明确执行顺序为 `Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions`
  3. formal docs 明确不得依赖不可追踪的隐式全局默认值
- **验证**：语义对账

### Task 2.3 冻结异常边界与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`, `specs/017-frontend-generation-governance-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确结构化例外的基本原则、可作用对象与禁止项
  2. formal docs 明确 legacy 例外不能把局部 legacy 用法扩展为默认模式
  3. formal docs 明确 generation governance baseline 与 `011` / `015` / `016` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/017-frontend-generation-governance-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `models / artifacts / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/017-frontend-generation-governance-baseline/plan.md`, `specs/017-frontend-generation-governance-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 recipe 约束、whitelist、hard rules、token rules 与 exceptions 场景
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行完整生成 runtime / gate / auto-fix 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/017-frontend-generation-governance-baseline/spec.md`, `specs/017-frontend-generation-governance-baseline/plan.md`, `specs/017-frontend-generation-governance-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 generation truth、constraint object、ordering 与 handoff 保持单一真值
  3. 当前分支上的 `017` formal docs 可作为后续进入 generation constraint 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：generation constraint models slice

### Task 4.1 先写 failing tests 固定 generation constraint / MVP builder 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_generation_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 MVP recipe 范围、whitelist 组件集合、Hard Rules、token rules 与 exceptions 边界
  2. 单测明确覆盖重复 Hard Rule id 的失败语义
  3. 首次运行定向测试时必须出现预期失败，证明 generation constraint models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraints.py -q`

### Task 4.2 实现最小 generation constraint models / MVP builder

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_generation_constraints.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型明确承载 recipe、whitelist、hard rules、token rules 与 exceptions 的上游控制面
  2. 提供 MVP baseline builder，并落实 `Contract -> Kernel -> Whitelist -> Hard Rules -> Token Rules -> Exceptions` 顺序
  3. 实现只停留在结构化模型层，不引入完整生成 runtime、gate 或 auto-fix 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraints.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/017-frontend-generation-governance-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_generation_constraints.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/017-frontend-generation-governance-baseline src/ai_sdlc/models tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraints.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/017-frontend-generation-governance-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：generation constraint artifact slice

### Task 5.1 先写 failing tests 固定 generation artifact file set 与 payload 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_generation_constraint_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `governance/frontend/generation/**` 的最小 artifact 文件集合
  2. 单测明确覆盖 recipe、whitelist、hard rules、token rules 与 exceptions 的 artifact payload
  3. 首次运行定向测试时必须出现预期失败，证明 generation constraint artifact instantiation 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraint_artifacts.py -q`

### Task 5.2 实现最小 generation artifact instantiation

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/generators/frontend_generation_constraint_artifacts.py`, `src/ai_sdlc/generators/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 提供 generation artifact root 与 materialize helper，并把 `FrontendGenerationConstraintSet` 物化为 canonical artifact tree
  2. artifact file set 至少覆盖 manifest、recipe、whitelist、hard rules、token rules 与 exceptions
  3. 实现只停留在 artifact instantiation 层，不引入完整生成 runtime、gate verdict 或 auto-fix 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraint_artifacts.py -q`

### Task 5.3 Fresh verify 并追加 artifact batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/017-frontend-generation-governance-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_generation_constraint_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/017-frontend-generation-governance-baseline src/ai_sdlc/generators tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 artifact batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_generation_constraint_artifacts.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/017-frontend-generation-governance-baseline src/ai_sdlc/generators tests/unit`, `uv run ai-sdlc verify constraints`
