---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
---
# 任务分解：Frontend P2 P3 Deferred Capability Expansion Planning Baseline

**编号**：`145-frontend-p2-p3-deferred-capability-expansion-planning-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-145-001 ~ FR-145-022 / SC-145-001 ~ SC-145-005）

---

## 分批策略

```text
Batch 1: residual capability census and delivered/deferred boundary freeze
Batch 2: child track topology and first carrier freeze
Batch 3: development summary, docs-only validation, truth handoff readiness
```

---

## 执行护栏

- `145` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `145` 不得重做 `073` 第一阶段，也不得把 `071/137/095/143/144` 已承接能力重新包装成“当前缺口”。
- `145` 必须一次性覆盖剩余 later-phase capability family，不得只补单条能力然后继续把其他 deferred 项留在 design 引用层。
- `145` 必须明确下一条优先 child 是 `frontend-p2-page-ui-schema-baseline`。
- `145` 不得开放 React UI 选择面、第二公开 Provider、开放式 style editor 或真实质量平台执行。
- `145` 只允许引用外部 design docs，不得在 `docs/superpowers/*` 新建第二套 canonical docs。
- 只有在 `145` docs-only 门禁通过且用户继续要求推进时，才允许进入 downstream child scaffold / implementation。
- downstream child 继续遵守一工单一分支；在 shared schema / theme truth 未冻结前，不得抢跑 quality platform 或 provider expansion。

## Batch 1：residual capability census and delivered/deferred boundary freeze

### Task 1.1 冻结剩余 deferred capability 集合

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少明确 `page/ui schema`、`multi-theme/token governance`、`quality platform`、`cross-provider consistency`、`modern provider expansion`
  2. `spec.md` 明确这些能力来自顶层设计与已有 non-goals/later-phase 边界，而不是临时会话猜测
  3. 当前 capability set 不再遗漏已在设计中明示的后续前端主线
- **验证**：top-level design / related docs 对账

### Task 1.2 冻结 delivered / deferred boundary honesty

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `073` 第一阶段与 `071/137/095/143/144` 已经承接了哪些能力
  2. `spec.md` 不再把 bounded browser gate、first-phase provider/style truth 误报成当前缺口
  3. delivered 与 deferred 的边界能直接被 reviewer 读取
- **验证**：相关 formal docs 对账 review

## Batch 2：child track topology and first carrier freeze

### Task 2.1 冻结 downstream child track 集合与建议 slug

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结五条 child tracks 与建议 slug
  2. 每条 child 都有目标、边界与上游依赖
  3. child track 不会与当前已完成 workitem scope 重叠
- **验证**：child table review

### Task 2.2 冻结 child DAG、owner boundary 与有限并行窗口

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 `page/ui schema -> multi-theme/token -> quality platform -> cross-provider consistency -> provider expansion` 的推荐顺序
  2. `plan.md` 明确各 child 的 owner boundary 与禁止跨层改写
  3. `plan.md` 明确哪些问题暂时不阻塞 `145`
- **验证**：DAG review

### Task 2.3 冻结下一条优先实现 carrier

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/plan.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. 三件套都明确下一条优先 child 是 `frontend-p2-page-ui-schema-baseline`
  2. `145` 不再停留在“只列出还有很多待办”的模糊状态
  3. 后续执行者可以直接继续 scaffold 该 child
- **验证**：formal docs consistency review

## Batch 3：development summary, docs-only validation, truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/task-execution-log.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确记录本批是 docs-only planning freeze
  2. development summary 诚实声明本次收口的是 planning truth，而不是 runtime code
  3. 两份文档都能被后续 close-check / global truth 消费
- **验证**：execution log / development summary review

### Task 3.2 运行 docs-only 门禁并确认 close-check readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/plan.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/tasks.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/task-execution-log.md`, `specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline` 通过
  3. `git diff --check` 通过
- **验证**：`uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline`、`git diff --check`

### Task 3.3 确认 truth handoff readiness

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`program-manifest.yaml`（如执行 truth sync）、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `145` 已可作为 global truth 中“后续前端优化主线”的 canonical planning input
  2. downstream child 不再需要重新做 capability census
  3. 当前 batch 不伪造任何 runtime implementation complete 结论
- **验证**：program truth refresh / docs review

## 后续进入执行前的前提

- 用户明确要求继续 scaffold `frontend-p2-page-ui-schema-baseline`
- `145` 已通过 docs-only 门禁
- downstream child 编号以后续 scaffold 当时的 `project-state` 为准
- `145` 之后的实现优先级默认遵循 `Track A -> Track B -> Track C -> Track D -> Track E`
