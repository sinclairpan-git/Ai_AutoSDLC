---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 Page Recipe Expansion Baseline

**编号**：`068-frontend-p1-page-recipe-expansion-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-068-001 ~ FR-068-021 / SC-068-001 ~ SC-068-005）

---

## 分批策略

```text
Batch 1: positioning and truth-order freeze
Batch 2: recipe set and area-constraint freeze
Batch 3: state expectation and downstream handoff freeze
Batch 4: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `068` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `068` 不得反向改写 `067` 已冻结的 `Ui*` 语义组件协议或页面级状态语义。
- `068` 不得扩张 whitelist、token rules、drift diagnostics、同一套 gate matrix 的兼容执行口径相关规则/反馈面或 remediation feedback；这些保留给下游 diagnostics child。
- `068` 不得定义 `Ui* -> provider/runtime` 的具体映射、Vue 组件实现、白名单承接或企业样式包装。
- `068` 不得借 `WizardPage` 顺手引入新的 `UiStepper` 协议，也不得借 `DashboardPage` 顺手引入图表协议或自由 widget contract。
- `068` 不得修改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`。
- `068` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现或已进入 program close。
- `068` 不得改写 `009/015/017/018/065/066/067` 的 formal truth，也不得用 provider/history page skeleton 反向主导 P1 recipe 标准本体。
- 只有在 `068` docs-only 门禁通过且用户明确要求继续时，才允许进入实现批次或继续 formalize 下游 diagnostics child。

---

## Batch 1：positioning and truth-order freeze

### Task 1.1 冻结 `068` 作为 P1 recipe expansion child 的定位

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `068` 是 `066` 下游的 page recipe expansion child work item
  2. `spec.md` 明确 `068` 位于 `067` 之后、下游 diagnostics child 之前
  3. `spec.md` 明确 `068` 不是 semantic component / diagnostics / provider 工单
- **验证**：formal docs review

### Task 1.2 冻结 `068` 的 non-goals 与 truth order

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `068` 继续遵守 `Contract -> Kernel -> Provider/Code -> Gate` 单一真值顺序
  2. `spec.md` 明确 `recipe standard body` 与 `recipe declaration` 分层保持不变
  3. `spec.md` 明确 diagnostics、provider/runtime 与 P2 能力不在本工单内
- **验证**：上游 formal docs 对账

---

## Batch 2：recipe set and area-constraint freeze

### Task 2.1 冻结 P1 新增 page recipe 集合

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结 `DashboardPage / DialogFormPage / SearchListPage / WizardPage`
  2. 每个 recipe 都具备明确的核心场景与结构角色说明
  3. 文档明确这些 recipe 继续保持 Provider 无关性
- **验证**：recipe table review

### Task 2.2 冻结每个 recipe 的 area constraint

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. 每个 recipe 都具备 `required area / optional area / forbidden pattern`
  2. `SearchListPage` 与 MVP `ListPage` 的边界被明确区分
  3. `DialogFormPage`、`WizardPage` 不退化为 provider runtime API 或自由页面片段集合
- **验证**：area constraint review

---

## Batch 3：state expectation and downstream handoff freeze

### Task 3.1 冻结 recipe 级状态期望

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确每个 recipe 的最小状态期望
  2. 文档明确这些状态期望与 `015/067` 状态 baseline 的关系
  3. 文档明确状态期望仍属 recipe baseline，而不是 diagnostics / gate 规则
- **验证**：state expectation review

### Task 3.2 冻结 `068` 与下游 child / 实现触点的 handoff boundary

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`, `specs/068-frontend-p1-page-recipe-expansion-baseline/plan.md`, `specs/068-frontend-p1-page-recipe-expansion-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 文档明确下游 diagnostics child 负责 whitelist / token / drift / coverage expansion
  2. `plan.md` 给出 future recipe 模型/工件的优先文件面
  3. 文档明确这些文件面当前仅为后续实现触点，不构成当前批次改动授权
- **验证**：formal docs review

---

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 execution log 为 docs-only child baseline freeze

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确当前 batch 只记录 child baseline freeze
  2. execution log 不提前伪造 accepted、root sync 或 code implementation 状态
  3. execution log 可在后续批次 append-only 归档
- **验证**：execution log review

### Task 4.2 推进 project-state 序号

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：`.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `next_work_item_seq` 从 `68` 推进到 `69`
  2. 不伪造 root truth sync 或 close 状态
  3. 当前 child work item 编号占位完成
- **验证**：state file review

### Task 4.3 运行 docs-only 门禁

- **任务编号**：T43
- **优先级**：P1
- **依赖**：T42
- **文件**：`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`, `specs/068-frontend-p1-page-recipe-expansion-baseline/plan.md`, `specs/068-frontend-p1-page-recipe-expansion-baseline/tasks.md`, `specs/068-frontend-p1-page-recipe-expansion-baseline/task-execution-log.md`, `.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check` 通过
  3. `068` 当前仍清楚停留在 docs-only formal baseline 状态
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`

---

## 后续进入执行前的前提

- 用户明确要求继续进入 `068` 的实现批次，或继续 formalize 下游 diagnostics child
- `068` formal docs 已通过 docs-only 门禁
- 下游 child 编号以后续 scaffold 当时的 `project-state` 为准，不使用当前文稿中的占位编号作为法定真值
- root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 的更新，必须等至少首批 P1 child baseline 已 formalize 并需要 root sync 时再单独评估
