---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
---
# 任务分解：Frontend P2 Page UI Schema Baseline

**编号**：`147-frontend-p2-page-ui-schema-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-147-001 ~ FR-147-012 / SC-147-001 ~ SC-147-005）

---

## 分批策略

```text
Batch 1: page-ui schema problem statement and structure boundary freeze
Batch 2: implementation order, upstream/downstream dependency, and non-goal freeze
Batch 3: development summary, docs-only validation, and global truth handoff readiness
```

---

## 执行护栏

- `147` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `147` 不得把 `068` page recipe truth 或 `073` provider/style first-phase truth 回写成 page schema 的唯一来源。
- `147` 不得混入 multi-theme/token governance、quality platform、cross-provider consistency、modern provider expansion。
- `147` 必须保持 provider-neutral，不得先站队单一 provider。
- `147` 必须明确它是 `145 Track A` 的 child，而不是新的顶层母级 planning item。

## Batch 1：page-ui schema problem statement and structure boundary freeze

### Task 1.1 冻结 page schema / ui schema scope

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. canonical formal docs 已直接位于 `specs/147-frontend-p2-page-ui-schema-baseline/`
  2. `spec.md` 明确 page schema、ui schema、render slot、section anchor、schema versioning 的边界
  3. `spec.md` 明确 `147` 是 `145 Track A` 的正式承接
- **验证**：related docs 对账 review

### Task 1.2 冻结与 `068/073` 的关系

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `147` 不是重做 `068/073`
  2. `spec.md` 明确 schema truth 与 recipe/provider truth 的关系
  3. reviewer 可以直接从 formal docs 读出三者边界
- **验证**：boundary wording review

## Batch 2：implementation order, upstream/downstream dependency, and non-goal freeze

### Task 2.1 冻结 implementation slice 顺序

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 schema model/serialization、validator/versioning、provider/kernel consumption 的顺序
  2. `plan.md` 明确当前只停留在 formal baseline
  3. `plan.md` 明确后续 Track B/C/D 如何依赖 `147`
- **验证**：plan review

### Task 2.2 冻结 non-goals 与 downstream dependency

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T21
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`, `specs/147-frontend-p2-page-ui-schema-baseline/plan.md`, `specs/147-frontend-p2-page-ui-schema-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 theme/quality/provider expansion 不属于当前 child
  2. downstream tracks 可以把 `147` 作为 schema anchor 引用
  3. tasks 与 plan 不再存在模板占位或 scope 混乱
- **验证**：formal docs consistency review

## Batch 3：development summary, docs-only validation, and global truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`, `specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 记录当前是 docs-only child baseline freeze
  2. development summary 诚实说明 `147` 当前尚未进入 runtime implementation
  3. 两份文档可被 close-check / global truth 消费
- **验证**：execution log / summary review

### Task 3.2 运行 docs-only 门禁并确认 truth handoff readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`, `specs/147-frontend-p2-page-ui-schema-baseline/plan.md`, `specs/147-frontend-p2-page-ui-schema-baseline/tasks.md`, `specs/147-frontend-p2-page-ui-schema-baseline/task-execution-log.md`, `specs/147-frontend-p2-page-ui-schema-baseline/development-summary.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/147-frontend-p2-page-ui-schema-baseline` 通过
  3. `program truth sync` 后 `147` 能进入 global truth mirror
  4. `git diff --check` 通过
- **验证**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/147-frontend-p2-page-ui-schema-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`
