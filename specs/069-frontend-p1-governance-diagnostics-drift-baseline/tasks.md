---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 Governance Diagnostics Drift Baseline

**编号**：`069-frontend-p1-governance-diagnostics-drift-baseline` | **日期**：2026-04-06
**来源**：plan.md + spec.md（FR-069-001 ~ FR-069-024 / SC-069-001 ~ SC-069-006）

---

## 分批策略

```text
Batch 1: positioning and truth-order freeze
Batch 2: diagnostics coverage matrix freeze
Batch 3: drift classification and compatibility feedback freeze
Batch 4: execution log init, project-state update, docs-only validation
Batch 5: diagnostics truth materialization slice
```

---

## 执行护栏

- `069` formal baseline 已完成；当前只允许在 Batch 5 进入首批实现切片。
- `069` 不得反向改写 `017` 的 generation truth、`018` 的 shared gate truth、`067` 的 semantic component truth 或 `068` 的 page recipe truth。
- `069` 不得把 Compatibility 改写成第二套 gate、第二套 report schema 或新的执行模式。
- `069` 不得把 sample source self-check 写成隐式 observation fallback；diagnostics 仍要求显式 observation artifact 输入。
- `069` 不得抢跑 `070` recheck / remediation feedback、`071` visual / a11y、provider/runtime 实现、integration tests 或 root sync。
- `069` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现完成或已进入 program close。
- Batch 5 只允许写入 `src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`、`tests/unit/test_frontend_gate_policy_models.py`、`tests/unit/test_frontend_gate_policy_artifacts.py`、`specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- 当前首批实现只放行 diagnostics truth model / artifact materialization，不放行 verify / gate runtime、CLI summary surface 或 root truth sync。

---

## Batch 1：positioning and truth-order freeze

### Task 1.1 冻结 `069` 作为 P1 diagnostics / drift child 的定位

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `069` 是 `066` 下游的 governance diagnostics / drift child work item
  2. `spec.md` 明确 `069` 位于 `067/068` 之后、`070/071` 之前
  3. `spec.md` 明确 `069` 不是 recheck / remediation、visual / a11y、provider/runtime 工单
- **验证**：formal docs review

### Task 1.2 冻结 `069` 的 truth-order 与 non-goals

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `069` 只能消费 `067 + 068 + 017 + 018 + 065`
  2. `plan.md` 明确 diagnostics 不得反向重写 kernel / recipe / generation / gate baseline
  3. 文档明确当前工单不进入 verify / gate runtime
- **验证**：上游 formal docs 对账

---

## Batch 2：diagnostics coverage matrix freeze

### Task 2.1 冻结 semantic component / recipe / state coverage

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 给出 semantic component coverage 的最小覆盖对象
  2. `spec.md` 给出 recipe coverage 与 state coverage 的消费边界
  3. 文档明确这些 coverage 直接消费 `067/068`
- **验证**：coverage matrix review

### Task 2.2 冻结 whitelist / token coverage 扩张边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 whitelist coverage 仍服从 `017` whitelist truth
  2. `spec.md` 明确 token coverage 仍服从 `017` minimal token / naked-value truth
  3. 文档明确 P1 扩张的是覆盖面，不是 generation schema 重写
- **验证**：coverage boundary review

---

## Batch 3：drift classification and compatibility feedback freeze

### Task 3.1 冻结 gap / empty / drift 分类

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `input gap / stable empty observation / drift` 的区分
  2. `spec.md` 明确 `recipe structure drift / state expectation drift / whitelist leakage / token leakage` 的最小分类
  3. 文档明确 `065` sample self-check 只作为显式输入源
- **验证**：classification review

### Task 3.2 冻结 compatibility feedback honesty

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 compatibility 仍是同一套 gate matrix 的兼容执行口径
  2. `spec.md` 明确 diagnostics 复用 `018` 的 report family，不新增第二套 report schema
  3. `plan.md` 明确当前工单不新增执行模式或第二套规则系统
- **验证**：formal docs review

### Task 3.3 冻结 downstream handoff

- **任务编号**：T33
- **优先级**：P0
- **依赖**：T32
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/plan.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 文档明确 `070` 承接 recheck / remediation feedback
  2. 文档明确 `071` 承接 visual / a11y foundation
  3. 文档明确当前批次只冻结 diagnostics baseline，不进入下游 formalize
- **验证**：handoff review

---

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 execution log 为 docs-only child baseline freeze

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T33
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确当前 batch 只记录 child baseline freeze
  2. execution log 不提前伪造 runtime implementation 状态
  3. execution log 可在后续批次 append-only 归档
- **验证**：execution log review

### Task 4.2 推进 project-state 序号

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：`.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `next_work_item_seq` 从 `69` 推进到 `70`
  2. 不伪造 root truth sync 或 close 状态
  3. 当前 child work item 编号占位完成
- **验证**：state file review

### Task 4.3 运行 docs-only 门禁

- **任务编号**：T43
- **优先级**：P1
- **依赖**：T42
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/plan.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/tasks.md`, `specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`, `.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check` 通过
  3. `069` 当前清楚停留在 docs-only accepted child baseline 状态
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`

---

## Batch 5：diagnostics truth materialization slice

### Task 5.1 先写 failing tests 固定 P1 diagnostics truth

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_frontend_gate_policy_models.py`, `tests/unit/test_frontend_gate_policy_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 diagnostics coverage matrix、drift classification 与 compatibility feedback boundary 的 builder truth
  2. 单测明确覆盖新增 artifact file set 与 payload
  3. 首次 RED 校验必须证明 `710638f` 尚未暴露 `build_p1_frontend_gate_policy_diagnostics_drift_expansion()` 或等价 truth
- **验证**：`uv run pytest tests/unit/test_frontend_gate_policy_models.py tests/unit/test_frontend_gate_policy_artifacts.py -q`

### Task 5.2 实现最小 diagnostics truth model / artifact

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/models/frontend_gate_policy.py`, `src/ai_sdlc/models/__init__.py`, `src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. `FrontendGatePolicySet` 新增 `069` 对应的 builder，并在 `018` shared gate truth 之上扩展 diagnostics coverage matrix、drift classification 与 compatibility feedback boundary
  2. model 能显式校验 diagnostics governed targets、report family 引用与 shared gate modes 引用边界
  3. artifact generator 能在不破坏 `018` canonical file set 的前提下，条件化写出 `069` 的新增 diagnostics payload
- **验证**：`uv run pytest tests/unit/test_frontend_gate_policy_models.py tests/unit/test_frontend_gate_policy_artifacts.py -q`

### Task 5.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/069-frontend-p1-governance-diagnostics-drift-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_gate_policy_models.py tests/unit/test_frontend_gate_policy_artifacts.py -q` 通过
  2. `uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`git diff --check -- specs/069-frontend-p1-governance-diagnostics-drift-baseline src/ai_sdlc/models src/ai_sdlc/generators tests/unit` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、RED/GREEN 证据、验证命令与对账结论
- **验证**：`uv run pytest tests/unit/test_frontend_gate_policy_models.py tests/unit/test_frontend_gate_policy_artifacts.py -q`, `uv run ruff check src tests`, `uv run ai-sdlc verify constraints`, `git diff --check -- specs/069-frontend-p1-governance-diagnostics-drift-baseline src/ai_sdlc/models src/ai_sdlc/generators tests/unit`

---

## 后续进入执行前的前提

- `069` formal docs 已通过 docs-only 门禁，且 Batch 5 的实现切片已完成 fresh verification
- 如需继续下游 `070` 或更宽的 `069` implementation slice，必须重新声明允许写面与验证矩阵
- 下游 child 编号以后续 scaffold 当时的 `project-state` 为准，不使用当前文稿中的占位编号作为法定真值
- root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 的更新，必须等至少首批 P1 child baseline 已 formalize 并需要 root sync 时再单独评估
