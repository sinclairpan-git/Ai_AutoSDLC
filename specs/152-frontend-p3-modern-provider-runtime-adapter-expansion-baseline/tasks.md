---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
---
# 任务分解：Frontend P3 Modern Provider Runtime Adapter Expansion Baseline

**编号**：`152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-152-001 ~ FR-152-022 / SC-152-001 ~ SC-152-005）

---

## 分批策略

```text
Batch 1: successor positioning and core-vs-runtime boundary freeze
Batch 2: carrier topology / handoff / evidence-return freeze
Batch 3: development summary, docs-only validation, truth handoff readiness
```

---

## 执行护栏

- `152` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `152` 不得重写 `073/150/151` 已冻结 truth，不得把 policy truth 与 runtime delivered truth 混写。
- `152` 不得在 Ai_AutoSDLC Core 仓库中直接实现真实 modern provider runtime / adapter 源码。
- `152` 必须一次性覆盖 successor scope、carrier mode、handoff contract 与 evidence-return contract，不得只补一条 rollout 语义后继续把其他后继项留在 design 引用层。
- `152` 不得伪造 React public runtime、第二 public provider 或独立适配包已真实交付。
- `152` 只允许引用外部 design docs，不得在 `docs/superpowers/*` 新建第二套 canonical docs。
- 只有在 `152` docs-only 门禁通过且用户继续要求推进时，才允许进入后续 target-project adapter/runtime implementation。

## Batch 1：successor positioning and core-vs-runtime boundary freeze

### Task 1.1 冻结 `151` 之后的真实 successor scope

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `152` 承接 `151` 之后的真实 runtime successor，而不是继续扩写 policy truth
  2. `spec.md` 明确当前覆盖 provider runtime / adapter expansion、handoff 与 evidence-return，不直接进入 runtime code
  3. 当前 successor scope 不再依赖会话记忆推断
- **验证**：`009/145/151` formal docs 对账

### Task 1.2 冻结 Core 与真实 runtime carrier 的边界诚实

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 Ai_AutoSDLC Core 不直接承载 provider 运行时代码
  2. `spec.md` 明确目标业务前端项目 / 独立适配包分别负责什么
  3. 文档不再把 runtime delivered truth 与 policy truth 混写
- **验证**：design/source review

## Batch 2：carrier topology / handoff / evidence-return freeze

### Task 2.1 冻结 carrier mode 与升级门槛

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `target-project-adapter-layer` 与 `independent-adapter-package`
  2. `spec.md` 明确默认优先 target project carrier
  3. `spec.md` 明确 `2+ 项目` 稳定复用后才允许考虑独立适配包
- **验证**：carrier topology review

### Task 2.2 冻结 scaffold / handoff / evidence-return / program surfacing contract

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 与 `plan.md` 明确 Adapter Scaffold Contract、Runtime Boundary Receipt、Evidence Return Contract、Program Surfacing Contract
  2. `plan.md` 明确 future runtime implementation 顺序：scaffold truth -> delivery handoff -> evidence ingestion -> program truth surfacing
  3. 文档不再停留在“以后再做 runtime”这种模糊口径
- **验证**：formal docs consistency review

### Task 2.3 冻结后续 runtime implementation 入口

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/plan.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 与 `tasks.md` 明确下一步是 target-project adapter/runtime implementation，而不是继续改 `151`
  2. 后续执行者可以直接根据 `152` 进入真实 runtime 承接
  3. owner boundary 与 future runtime slice 入口表达一致
- **验证**：DAG / owner boundary review

## Batch 3：development summary, docs-only validation, truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/task-execution-log.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确记录本批是 docs-only successor baseline freeze
  2. development summary 诚实声明本次收口的是 planning truth，不是 runtime code
  3. 两份文档都能被后续 close-check / global truth 消费
- **验证**：execution log / development summary review

### Task 3.2 运行 docs-only 门禁并确认 close-check readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/plan.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/tasks.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/task-execution-log.md`、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline` 通过
  3. `git diff --check` 通过
- **验证**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline`、`git diff --check`

### Task 3.3 确认 truth handoff readiness

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`program-manifest.yaml`（如执行 truth sync）、`specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `152` 已可作为 global truth 中真实 runtime successor 的 canonical planning input
  2. 后续执行者不再需要重新做 runtime carrier census
  3. 当前 batch 不伪造任何 modern provider runtime complete 结论
- **验证**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、docs review

## 后续进入执行前的前提

- 用户明确要求继续进入真实 target-project adapter/runtime implementation
- `152` 已通过 docs-only 门禁
- runtime implementation 继续遵守一工单一分支与 clean-tree close-out 纪律
- `152` 之后的实现优先级默认遵循 `target-project adapter layer -> evidence ingestion -> independent package consideration`
