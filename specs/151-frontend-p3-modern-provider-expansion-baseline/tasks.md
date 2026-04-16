---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md"
---
# 任务分解：Frontend P3 Modern Provider Expansion Baseline

**编号**：`151-frontend-p3-modern-provider-expansion-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-151-001 ~ FR-151-025 / SC-151-001 ~ SC-151-006）

---

## 分批策略

```text
Batch 1: Track E positioning and upstream gate freeze
Batch 2: provider admission / choice-surface / react boundary freeze
Batch 3: development summary, docs-only validation, truth handoff readiness
```

---

## 执行护栏

- `151` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `151` 不得重写 `073` provider/style truth、`150` consistency gate truth。
- `151` 必须一次性冻结 provider admission、provider-level certification aggregation、choice-surface visibility、React stack/binding boundary、artifact/truth-surfacing contract，不得只补单条 provider 状态然后继续把其他 Track E 内容留在设计引用层。
- `151` 不得伪造 modern provider roster、public choice surface、React exposure 已真实落地。
- `151` 只允许引用外部 design docs，不得在 `docs/superpowers/*` 新建第二套 canonical docs。
- 只有在 `151` docs-only 门禁通过且用户继续要求推进时，才允许进入 Track E runtime 实现。
- 真实 provider runtime / adapter 扩张必须等待 Track E policy truth 冻结后再承接。

## Batch 1：Track E positioning and upstream gate freeze

### Task 1.1 冻结 Track E 的独立定位与 capability set

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少明确 `provider admission policy`、`public choice surface expansion policy`、`React exposure boundary`
  2. `spec.md` 明确 Track E 的能力来自顶层设计与 `145/073/150` 边界，而不是临时会话猜测
  3. 当前 capability set 不再遗漏设计中明示的 Track E 主线
- **验证**：top-level design / related docs 对账

### Task 1.2 冻结 upstream gate 与 delivered/deferred boundary honesty

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `073/150` 分别提供的上游 truth
  2. `spec.md` 不再把真实 provider runtime、public-ready React、adapter 落地误报成当前工单能力
  3. delivered truth 与 deferred expansion/runtime 的边界能直接被 reviewer 读取
- **验证**：相关 formal docs 对账 review

## Batch 2：provider admission / choice-surface / react boundary freeze

### Task 2.1 冻结 provider aggregation、admission states 与 choice-surface matrix

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 至少冻结 `certification_gate`、`roster_admission_state`、`choice_surface_visibility` 三个独立状态轴
  2. `spec.md` 明确 pair-level `150` certification 如何聚合为 provider-level admission truth
  3. `spec.md` 明确 simple mode、advanced mode、public choice surface 与 internal modeling 的准入矩阵与展示规则
  4. choice-surface policy 不会绕过 `150` gate 与 `073` requested/effective 边界
- **验证**：policy model review

### Task 2.2 冻结 React exposure boundary 与 Track E handoff

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 与 `plan.md` 明确 `react` 的 current-state honesty，以及 stack visibility / provider binding visibility 的升级路径
  2. `plan.md` 明确 future runtime slices：`admission models -> roster/choice-surface artifacts -> validator/policy -> ProgramService/CLI/verify/global truth handoff`
  3. 文档不再停留在“以后再开放 React/provider”的模糊状态
- **验证**：formal docs consistency review

### Task 2.3 冻结 artifact root、truth surfacing 与 owner boundary

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/plan.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 固定 canonical artifact root、truth surfacing contract 与最小 consumer contract
  2. `plan.md` 明确 Track E 输出在 global truth 中的语义层级与 consumer position
  3. `plan.md` 明确真实 runtime / adapter 扩张不属于当前工单
  4. `tasks.md` 与 `plan.md` 对下一步 Track E runtime 的承接边界表达一致
  5. downstream 执行者可直接依据 `151` 进入 Track E runtime
- **验证**：artifact / owner boundary review

## Batch 3：development summary, docs-only validation, truth handoff readiness

### Task 3.1 初始化 execution log 与 development summary

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/task-execution-log.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. execution log 明确记录本批是 docs-only Track E planning freeze
  2. development summary 诚实声明本次收口的是 Track E baseline，而不是 runtime code
  3. 两份文档都能被后续 close-check / global truth 消费
- **验证**：execution log / development summary review

### Task 3.2 运行 docs-only 门禁并确认 close-check readiness

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/plan.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/tasks.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/task-execution-log.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints` 通过
  2. `python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline` 通过
  3. `git diff --check` 通过
  4. UX / AI-Native 专家评审结论已吸收进 formal docs
- **验证**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/151-frontend-p3-modern-provider-expansion-baseline`、`git diff --check`

### Task 3.3 确认 truth handoff readiness

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`program-manifest.yaml`（如执行 truth sync）、`specs/151-frontend-p3-modern-provider-expansion-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `151` 已可作为 global truth 中 Track E 的 canonical planning input
  2. 后续 Track E runtime 不再需要重新做 provider-expansion capability census
  3. `program truth sync --execute --yes` 与 `program truth audit` 已作为强制 close-out 门禁执行并记录到 execution log
  4. 当前 batch 不伪造任何 provider expansion runtime complete 结论
- **验证**：`python -m ai_sdlc program truth sync --dry-run`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、docs review

## 后续进入执行前的前提

- 用户明确要求继续进入 Track E runtime
- `151` 已通过 docs-only 门禁
- downstream runtime 切片仍遵循一工单一分支
- `151` 之后才允许进入真实 modern provider runtime / adapter 扩张
