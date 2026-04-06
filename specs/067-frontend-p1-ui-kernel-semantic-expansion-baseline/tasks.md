---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 UI Kernel Semantic Expansion Baseline

**编号**：`067-frontend-p1-ui-kernel-semantic-expansion-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-067-001 ~ FR-067-019 / SC-067-001 ~ SC-067-005）

---

## 分批策略

```text
Batch 1: positioning and truth-order freeze
Batch 2: semantic component set and state baseline freeze
Batch 3: downstream handoff and implementation-surface freeze
Batch 4: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `067` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `067` 不得定义新的 page recipe 标准本体；`DashboardPage / DialogFormPage / SearchListPage / WizardPage` 保留给下游 `068`。
- `067` 不得扩张 whitelist、token rules、drift diagnostics、同一套 gate matrix 的兼容执行口径相关规则/反馈面或 remediation feedback；这些保留给下游 `069` 或更后续 child。
- `067` 不得定义 `Ui* -> provider/runtime` 的具体映射、Vue 组件实现、白名单承接或企业样式包装。
- `067` 不得修改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`。
- `067` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现或已进入 program close。
- `067` 不得改写 `009/015/017/018/066` 的 formal truth，也不得用 provider/history page skeleton 反向主导 P1 Kernel 组件集。
- 只有在 `067` docs-only 门禁通过且用户明确要求继续时，才允许进入实现批次或 downstream child formalize。

---

## Batch 1：positioning and truth-order freeze

### Task 1.1 冻结 `067` 作为 P1 Kernel expansion child 的定位

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `067` 是 `066` 下游第一条 child work item
  2. `spec.md` 明确 `067` 位于 `015` 之后、`068/069` 之前
  3. `spec.md` 明确 `067` 不是 recipe / diagnostics / provider 工单
- **验证**：formal docs review

### Task 1.2 冻结 `067` 的 non-goals 与 truth order

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `067` 继续遵守 `Contract -> Kernel -> Provider/Code -> Gate` 单一真值顺序
  2. `spec.md` 明确 page recipe、diagnostics、provider/runtime 不在本工单内
  3. `spec.md` 明确 `067` 不偷渡 P2 的 `modern provider / multi-theme / multi-style`
- **验证**：上游 formal docs 对账

---

## Batch 2：semantic component set and state baseline freeze

### Task 2.1 冻结 P1 新增 `Ui*` 语义组件集合

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard`
  2. 每个组件都具备明确的核心角色与边界说明
  3. 文档明确这些组件继续保持 Provider 无关性
- **验证**：component table review

### Task 2.2 冻结 P1 页面级状态语义扩展

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结 `refreshing / submitting / no-results / partial-error / success-feedback`
  2. 文档明确这些状态与 `loading / empty / error / disabled / no-permission` 的关系
  3. 文档明确状态语义仍属 Kernel baseline，而不是 diagnostics/gate 规则
- **验证**：state semantic review

---

## Batch 3：downstream handoff and implementation-surface freeze

### Task 3.1 冻结 `067 -> 068 -> 069` handoff boundary

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`, `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. 文档明确 `068` 负责 page recipe 标准本体扩展
  2. 文档明确 `069` 负责 diagnostics / drift / whitelist / token 扩展
  3. 文档明确 `067` 不提前消费 root program sync
- **验证**：formal docs review

### Task 3.2 冻结未来实现触点与 docs-only honesty

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/plan.md`, `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出 future Kernel 模型/工件的优先文件面
  2. 文档明确这些文件面当前仅为后续实现触点，不构成当前批次改动授权
  3. 文档明确 `067` 当前不生成 `development-summary.md`，也不宣称 close-ready 或已实现
- **验证**：docs consistency review

---

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 execution log 为 docs-only child baseline freeze

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确当前 batch 只记录 child baseline freeze
  2. execution log 不提前伪造 code implementation、root sync 或 accepted 状态
  3. execution log 可在后续批次 append-only 归档
- **验证**：execution log review

### Task 4.2 推进 project-state 序号

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：`.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `next_work_item_seq` 从 `67` 推进到 `68`
  2. 不伪造 root truth sync 或 close 状态
  3. 当前 child work item 编号占位完成
- **验证**：state file review

### Task 4.3 运行 docs-only 门禁

- **任务编号**：T43
- **优先级**：P1
- **依赖**：T42
- **文件**：`specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`, `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/plan.md`, `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/tasks.md`, `specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/task-execution-log.md`, `.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check` 通过
  3. `067` 当前仍清楚停留在 docs-only formal baseline 状态
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`

---

## 后续进入执行前的前提

- 用户明确要求继续进入 `067` 的实现批次，或继续 formalize 下游 `068`
- `067` formal docs 已通过 docs-only 门禁
- `068/069` 的真实编号以后续 scaffold 当时的 `project-state` 为准，不使用当前文稿中的占位编号作为法定真值
- root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 的更新，必须等至少首批 P1 child baseline 已 formalize 并需要 root sync 时再单独评估
