---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend UI Kernel Standard Baseline

**编号**：`015-frontend-ui-kernel-standard-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-015-001 ~ FR-015-016 / SC-015-001 ~ SC-015-005）

---

## 分批策略

```text
Batch 1: kernel truth freeze
Batch 2: recipe/state/theme boundary freeze
Batch 3: implementation handoff and verification freeze
Batch 4: kernel models slice
Batch 5: kernel artifact slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `015` 不得重新定义 `011` 已冻结的 Contract truth 或 `recipe declaration` shape。
- `015` 不得在当前 child work item 中直接进入 Provider mapping、企业组件库包装、generation runtime、gate diagnostics 或 Vue 组件实现。
- `Batch 4` 只允许写入 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`specs/015-frontend-ui-kernel-standard-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`、`src/ai_sdlc/generators/__init__.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`、`specs/015-frontend-ui-kernel-standard-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 Kernel 模型/标准体，不放行 Provider runtime、Gate、generation 或 Vue 组件实现。
- 当前第二批实现只放行 Kernel artifact instantiation，不放行 Provider runtime、Gate、generation runtime 或 Vue 组件实现。
- `015` 只冻结 UI Kernel baseline，不默认决定任何 `src/` / `tests/` runtime side effect。
- 只有在用户明确要求进入实现，且 `015` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：kernel truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `015` 是 `009` 下游的 UI Kernel child work item
  2. `spec.md` 明确 UI Kernel 位于 Contract 与 Provider/generation/gate 之间
  3. `spec.md` 不再依赖临时对话或设计稿才能解释 `015` 的边界
- **验证**：文档对账

### Task 1.2 冻结 Kernel 与 Provider / 组件库边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `Kernel != Provider != 公司组件库`
  2. formal docs 明确 `Ui*` 协议不是底层 API 透传
  3. 不再出现 Provider 可反向定义 Kernel 的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`, `specs/015-frontend-ui-kernel-standard-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Provider、generation、gate 与 runtime 组件实现不属于当前 work item
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 Kernel 模型/标准体，而不是先写 Provider wrapper
- **验证**：scope review

---

## Batch 2：recipe/state/theme boundary freeze

### Task 2.1 冻结 page recipe 标准本体

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `ListPage / FormPage / DetailPage` 是 MVP 首批 recipe 标准本体
  2. formal docs 明确 `required area / optional area / forbidden pattern` 的区域约束模型
  3. formal docs 明确 `recipe standard body != recipe declaration`
- **验证**：recipe contract review

### Task 2.2 冻结状态、交互与 Theme/Token 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 MVP 页面级最小状态集合与交互底线
  2. formal docs 明确最小可访问性底线与 Theme/Token 边界属于 Kernel 层
  3. formal docs 明确这些边界将在下游 Gate 工程化，而不是在当前工单中直接实现
- **验证**：语义对账

### Task 2.3 冻结 Provider 无关性与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`, `specs/015-frontend-ui-kernel-standard-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Kernel 为 Provider 提供上游标准体，但不被 Provider 反向主导
  2. formal docs 明确公司组件库与 Legacy Adapter 仍在下游工单承接
  3. formal docs 明确 UI Kernel baseline 与 `011` Contract baseline 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `models / provider / gates / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/plan.md`, `specs/015-frontend-ui-kernel-standard-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 `Ui*` 协议边界、recipe 区域约束、状态/交互底线与 Provider 无关性
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 Provider/runtime/gate 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/spec.md`, `specs/015-frontend-ui-kernel-standard-baseline/plan.md`, `specs/015-frontend-ui-kernel-standard-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 UI Kernel truth、recipe boundary、state/theme baseline 与 handoff 保持单一真值
  3. 当前分支上的 `015` formal docs 可作为后续进入 Kernel 模型实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：kernel models slice

### Task 4.1 先写 failing tests 固定 Kernel models / MVP builder 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_ui_kernel_models.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 MVP `Ui*` 协议集合、三个 page recipe 标准本体、状态底线与交互底线
  2. 单测明确覆盖 recipe 区域重叠与重复 component/recipe id 的失败语义
  3. 首次运行定向测试时必须出现预期失败，证明 Kernel models 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_models.py -q`

### Task 4.2 实现最小 Kernel models / MVP builder

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/models/frontend_ui_kernel.py`, `src/ai_sdlc/models/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 模型明确承载 `Ui*` 协议、page recipe 标准本体、状态底线与交互底线
  2. 提供 MVP baseline builder，并落实 `ListPage / FormPage / DetailPage` 与 MVP 首批 `Ui*` 协议集合
  3. 实现只停留在结构化模型层，不引入 Provider/Gate/generation/runtime 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_models.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_ui_kernel_models.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/015-frontend-ui-kernel-standard-baseline src/ai_sdlc/models tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_models.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/015-frontend-ui-kernel-standard-baseline src/ai_sdlc/models tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：kernel artifact slice

### Task 5.1 先写 failing tests 固定 Kernel artifact file set 与 payload 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_ui_kernel_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 `kernel/frontend/**` 的最小 artifact 文件集合
  2. 单测明确覆盖语义组件、page recipe、状态 baseline 与交互 baseline 的 artifact payload
  3. 首次运行定向测试时必须出现预期失败，证明 Kernel artifact instantiation 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_artifacts.py -q`

### Task 5.2 实现最小 Kernel artifact instantiation

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`, `src/ai_sdlc/generators/__init__.py`
- **可并行**：否
- **验收标准**：
  1. 提供 UI Kernel artifact root 与 materialize helper，并把 `FrontendUiKernelSet` 物化为 canonical artifact tree
  2. artifact file set 至少覆盖 semantic components、page recipes、state baseline 与 interaction baseline
  3. 实现只停留在 artifact instantiation 层，不引入 Provider/Gate/runtime 逻辑
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_artifacts.py -q`

### Task 5.3 Fresh verify 并追加 artifact batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/015-frontend-ui-kernel-standard-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_ui_kernel_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/015-frontend-ui-kernel-standard-baseline src/ai_sdlc/generators tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 artifact batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_ui_kernel_artifacts.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/015-frontend-ui-kernel-standard-baseline src/ai_sdlc/generators tests/unit`, `uv run ai-sdlc verify constraints`
