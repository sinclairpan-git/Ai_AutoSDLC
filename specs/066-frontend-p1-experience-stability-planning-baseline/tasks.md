---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 Experience Stability Planning Baseline

**编号**：`066-frontend-p1-experience-stability-planning-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-066-001 ~ FR-066-023 / SC-066-001 ~ SC-066-005）

---

## 分批策略

```text
Batch 1: p1 scope and non-goals freeze
Batch 2: child track topology and dag freeze
Batch 3: rollout policy and root sync timing freeze
Batch 4: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `066` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `066` 不得 scaffold downstream child work item；所有 `067+` 仅作为推荐占位，不构成当前批次承诺。
- `066` 不得修改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`。
- `066` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现或已进入 program close。
- `066` 不得改写 `009/015/017/018/065` 的 formal truth，也不得建立第二套 Contract / Kernel / Gate 体系。
- P1 规划不得偷渡 P2 的 `modern provider / multi-theme / multi-style`、完整 visual regression 平台或完整 a11y 平台。
- 只有在 `066` docs-only 门禁通过且用户明确要求继续时，才允许进入 downstream child scaffold。
- downstream child 仍应遵守一工单一分支与 formalize 先行；在 kernel / recipe / diagnostics truth 未冻结前，不得抢跑并行实现。

---

## Batch 1：P1 scope and non-goals freeze

### Task 1.1 冻结 P1 的阶段目标与非目标

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 P1 目标是“从正确性止血走向体验稳定”
  2. `spec.md` 明确 P1 不包含 `modern provider / multi-theme / multi-style`
  3. `spec.md` 明确 `066` 是 planning baseline，而不是实现工单
- **验证**：formal docs review

### Task 1.2 冻结 P1 与 MVP / P2 的 truth boundary

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 P1 不得建立第二套 Contract / Kernel / Gate 体系
  2. `spec.md` 明确 P1 继续复用 `009` 的单一真值顺序
  3. P1 / P2 边界不再依赖 design 总览临时推断
- **验证**：上游 formal docs 对账

---

## Batch 2：child track topology and DAG freeze

### Task 2.1 冻结推荐 child track 集合与建议 slug

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结五条 P1 child tracks
  2. 每条 track 都有建议 slug 与上游依赖
  3. child track 不会与 `015/017/018/065` 已冻结真值冲突
- **验证**：track table review

### Task 2.2 冻结 child DAG、有限并行窗口与 owner boundary

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 `Kernel -> Recipe -> Diagnostics -> (Recheck || Visual/A11y)` 的推荐顺序
  2. `plan.md` 明确 diagnostics 之前不建议并行扩张
  3. `plan.md` 明确各 child 的 owner boundary 与禁止跨层改写
- **验证**：DAG review

---

## Batch 3：rollout policy and root sync timing freeze

### Task 3.1 冻结 branch rollout policy

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/plan.md`, `specs/066-frontend-p1-experience-stability-planning-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 文档明确 downstream child 继续遵守一工单一分支
  2. 文档明确有限并行窗口只出现在 diagnostics truth 冻结之后
  3. 文档明确当前批次不 scaffold child
- **验证**：formal docs review

### Task 3.2 冻结 root truth sync 时机与 planning-only honesty

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`, `specs/066-frontend-p1-experience-stability-planning-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 文档明确 root `program-manifest.yaml` 与 rollout plan 的更新时机晚于 child baseline formalize
  2. 文档明确 `066` 当前不生成 `development-summary.md`
  3. 文档明确 `066` 不宣称 close-ready 或已实现
- **验证**：docs consistency review

---

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 execution log 为 docs-only formal freeze

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确当前 batch 只记录 planning freeze
  2. execution log 不提前伪造 child scaffold、root sync 或实现完成状态
  3. execution log 可在后续批次 append-only 归档
- **验证**：execution log review

### Task 4.2 推进 project-state 序号

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：`.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `next_work_item_seq` 从 `66` 推进到 `67`
  2. 不伪造 root truth sync 或 close 状态
  3. 当前 work item 编号占位完成
- **验证**：state file review

### Task 4.3 运行 docs-only 门禁

- **任务编号**：T43
- **优先级**：P1
- **依赖**：T42
- **文件**：`specs/066-frontend-p1-experience-stability-planning-baseline/spec.md`, `specs/066-frontend-p1-experience-stability-planning-baseline/plan.md`, `specs/066-frontend-p1-experience-stability-planning-baseline/tasks.md`, `specs/066-frontend-p1-experience-stability-planning-baseline/task-execution-log.md`, `.ai-sdlc/project/config/project-state.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check` 通过
  3. `066` 当前仍清楚停留在 docs-only formal baseline 状态
- **验证**：`uv run ai-sdlc verify constraints`、`git diff --check`

---

## 后续进入执行前的前提

- 用户明确要求继续 scaffold downstream child work item
- `066` formal docs 已通过 docs-only 门禁
- child 编号以后续 scaffold 当时的 `project-state` 为准，不使用 `066` 文稿中的占位编号作为法定真值
- root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 的更新，必须等至少首批 child baseline 已 formalize 后再单独评估
