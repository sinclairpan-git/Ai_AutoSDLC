---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "specs/141-program-manifest-root-census-backfill-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
---
# 任务分解：Program Truth Pipeline Injection Baseline

**编号**：`146-program-truth-pipeline-injection-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-146-001 ~ FR-146-012 / SC-146-001 ~ SC-146-005）

---

## 分批策略

```text
Batch 1: truth injection problem statement and contract freeze
Batch 2: diagnostic surfaces, verification profile, and implementation order freeze
Batch 3: development summary, docs-only validation, and global truth handoff readiness
```

---

## 执行护栏

- `146` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/` 实现。
- `146` 不得新增第二份 program truth、第二个 manifest 或平行 dashboard。
- `146` 不得把 stale truth 继续表述成“只是多跑一个命令即可”的经验问题；必须冻结为 pipeline injection 缺口。
- `146` 必须明确 read-only surface 不得暗写 snapshot。
- `146` 必须为后续 `145/147` 一类 planning workitem 提供 truth handoff contract，而不是继续留给 operator 手工兜底。

## Batch 1：truth injection problem statement and contract freeze

### Task 1.1 冻结问题定义与 handoff contract

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. canonical formal docs 已直接位于 `specs/146-program-truth-pipeline-injection-baseline/`
  2. `spec.md` 明确指出 `140/141/145` 后仍存在的 pipeline injection 缺口
  3. `spec.md` 冻结 `workitem init -> manifest mapping -> truth sync -> close/status` 的最小 handoff 顺序
- **验证**：related docs / current status 对账

### Task 1.2 冻结 diagnostic semantics

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 区分 `manifest_unmapped`、`truth_snapshot_stale`、`capability_blocked`
  2. `spec.md` 明确 `program status` 与 `close-check` 必须给出 next required truth action
  3. `spec.md` 不再把治理注入缺口和业务 capability blocker 混写
- **验证**：diagnostic wording review

## Batch 2：diagnostic surfaces, verification profile, and implementation order freeze

### Task 2.1 冻结实现切片顺序与影响面

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 Phase 1-3 的实现顺序
  2. `plan.md` 明确 manifest mapping、truth sync handoff、diagnostic surfaces、verification profile 的边界
  3. `plan.md` 不越界到前端业务 capability
- **验证**：plan review

### Task 2.2 冻结 truth-only verification profile 与执行护栏

- **任务编号**：T22
- **优先级**：P1
- **依赖**：T21
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/spec.md`, `specs/146-program-truth-pipeline-injection-baseline/plan.md`, `specs/146-program-truth-pipeline-injection-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 truth-only / manifest-only 变更需要单独 verification 口径
  2. tasks 明确当前 batch 仍是 docs-only baseline
  3. downstream implementation 不再需要重新解释为什么 `146` 存在
- **验证**：formal docs consistency review

## Batch 3：development summary, docs-only validation, and global truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/task-execution-log.md`, `specs/146-program-truth-pipeline-injection-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 诚实记录本批只完成 formal baseline freeze
  2. development summary 说明 `146` 当前收口的是 pipeline injection planning truth，而不是 runtime integration
  3. 两份文档可被 close-check / global truth 消费
- **验证**：execution log / summary review

### Task 3.2 运行 docs-only 门禁并确认 truth handoff readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/146-program-truth-pipeline-injection-baseline/spec.md`, `specs/146-program-truth-pipeline-injection-baseline/plan.md`, `specs/146-program-truth-pipeline-injection-baseline/tasks.md`, `specs/146-program-truth-pipeline-injection-baseline/task-execution-log.md`, `specs/146-program-truth-pipeline-injection-baseline/development-summary.md`, `program-manifest.yaml`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/146-program-truth-pipeline-injection-baseline` 通过
  3. `program truth sync` 后 `146` 能进入 global truth mirror
  4. `git diff --check` 通过
- **验证**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/146-program-truth-pipeline-injection-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`git diff --check`
