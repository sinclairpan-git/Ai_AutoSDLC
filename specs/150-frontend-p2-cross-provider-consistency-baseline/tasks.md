---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
  - "specs/149-frontend-p2-quality-platform-baseline/spec.md"
---
# 任务分解：Frontend P2 Cross Provider Consistency Baseline

**编号**：`150-frontend-p2-cross-provider-consistency-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-150-001 ~ FR-150-024 / SC-150-001 ~ SC-150-007）

---

## 分批策略

```text
Batch 1: Track D positioning and upstream boundary freeze
Batch 2: verdict / diff / certification handoff freeze
Batch 3: development summary, docs-only validation, truth handoff readiness
```

---

## 执行护栏

- `150` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `150` 不得重写 `073` provider/style truth、`147` schema truth、`148` theme truth、`149` quality truth。
- `150` 必须一次性冻结 multi-axis state vector、UX equivalence、structured diff、artifact/truth-surfacing contract、consistency certification 与 Track E readiness gate，不得只补一条 diff 语义然后继续把其他 Track D 内容留在设计引用层。
- `150` 不得开放 provider roster expansion、public provider choice surface、React exposure 或开放式 style editor runtime。
- `150` 只允许引用外部 design docs，不得在 `docs/superpowers/*` 新建第二套 canonical docs。
- 只有在 `150` docs-only 门禁通过且用户继续要求推进时，才允许进入 Track D runtime 实现。
- Track E 必须等待 Track D certification truth 冻结后再承接，不得抢跑 provider expansion。

## Batch 1：Track D positioning and upstream boundary freeze

### Task 1.1 冻结 Track D 的独立定位与 capability set

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少明确 `shared verdict`、`structured diff surface`、`consistency certification workflow`、`Track E readiness gate`
  2. `spec.md` 明确 Track D 的能力来自顶层设计与 `145/073/147/148/149` 边界，而不是临时会话猜测
  3. 当前 capability set 不再遗漏设计中明示的 Track D 主线
- **验证**：top-level design / related docs 对账

### Task 1.2 冻结 upstream input 与 delivered/deferred boundary honesty

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `073/147/148/149` 分别提供的上游 truth
  2. `spec.md` 不再把 provider expansion、React exposure、public choice surface 误报成当前工单能力
  3. delivered truth 与 deferred consistency/runtime 的边界能直接被 reviewer 读取
- **验证**：相关 formal docs 对账 review

## Batch 2：verdict / diff / certification handoff freeze

### Task 2.1 冻结 consistency verdict 与 structured diff surface

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结 `final_verdict`、`comparability_state`、`blocking_state`、`evidence_state` 四个维度或等价分层
  2. `spec.md` 明确 diff surface 至少覆盖关键用户旅程、schema slot、theme token、quality dimension、severity、evidence refs 与 remediation hint
  3. verdict 与 diff surface 不会越界重写 `149` 的 quality 标准
- **验证**：consistency model review

### Task 2.2 冻结 certification handoff 与 Track E readiness gate

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 与 `plan.md` 明确 Track E 只消费 Track D certification truth
  2. `spec.md` 与 `plan.md` 明确 `ready / conditional / blocked` 的 gate 裁决矩阵
  3. `plan.md` 明确 future runtime slices：`models -> artifact/certification materialization -> validator/rules -> ProgramService/CLI/verify handoff`
  4. 文档不再停留在“以后再比较 provider”的模糊状态
- **验证**：formal docs consistency review

### Task 2.3 冻结 owner boundary 与有限并行窗口

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确 Track D 不扩 provider roster，Track E 不重建 consistency baseline
  2. `plan.md` 固定 canonical artifact root 与 truth surfacing contract
  3. `tasks.md` 与 `plan.md` 对下一步 Track E 的承接边界表达一致
  4. downstream 执行者可直接依据 `150` 进入 Track D runtime 或继续 formalize Track E
- **验证**：DAG / owner boundary review

## Batch 3：development summary, docs-only validation, truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/task-execution-log.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确记录本批是 docs-only Track D planning freeze
  2. development summary 诚实声明本次收口的是 Track D baseline，而不是 runtime code
  3. 两份文档都能被后续 close-check / global truth 消费
- **验证**：execution log / development summary review

### Task 3.2 运行 docs-only 门禁并确认 close-check readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/tasks.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/task-execution-log.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/150-frontend-p2-cross-provider-consistency-baseline` 通过
  3. `git diff --check` 通过
  4. UX / AI-Native 专家评审结论已吸收进 formal docs
- **验证**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/150-frontend-p2-cross-provider-consistency-baseline`、`git diff --check`

### Task 3.3 确认 truth handoff readiness

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`program-manifest.yaml`（如执行 truth sync）、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `150` 已可作为 global truth 中 Track D 的 canonical planning input
  2. Track E 不再需要重新做 consistency capability census
  3. `program truth sync --execute --yes` 与 `program truth audit` 已作为强制 close-out 门禁执行并记录到 execution log
  4. 当前 batch 不伪造任何 consistency runtime complete 结论
- **验证**：`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、docs review

## 后续进入执行前的前提

- 用户明确要求继续进入 Track D runtime 或 formalize `frontend-p3-modern-provider-expansion-baseline`
- `150` 已通过 docs-only 门禁
- downstream child 编号以后续 scaffold 当时的 `project-state` 为准
- `150` 之后的实现优先级默认遵循 `Track D runtime -> Track E`
