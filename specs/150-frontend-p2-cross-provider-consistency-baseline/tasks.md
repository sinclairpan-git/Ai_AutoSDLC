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
Batch 4: pair-centric runtime slice 1 (models + artifact materializer)
Batch 5: pair-centric runtime slice 2 (validator + rules)
Batch 6: pair-centric runtime slice 3 (ProgramService / CLI / rules / verify handoff)
```

---

## 执行护栏

- `150` formal baseline 已完成；当前批次只允许进入 runtime slice 1：`models + artifact materializer skeleton`，不得提前进入 validator、ProgramService / CLI / verify。
- 当前已完成 runtime slices 1-2；本批次只允许进入 runtime slice 3：`ProgramService / CLI / rules / verify handoff`，不得提前把 global truth refresh proof、close-out 或 Track E consumption 误报为已完成。
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

## Batch 4：pair-centric runtime slice 1

### Task 4.1 实现独立的 150 consistency models

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`src/ai_sdlc/models/frontend_cross_provider_consistency.py`、`tests/unit/test_frontend_cross_provider_consistency_models.py`
- **可并行**：否
- **验收标准**：
  1. `150` 具有独立的 pair-centric models，不复用 `149` quality verdict 或 `151` admission truth
  2. 明确落地 `final_verdict / comparability_state / blocking_state / evidence_state`
  3. readiness gate 能从四轴状态派生 `ready / conditional / blocked`
- **验证**：focused pytest

### Task 4.2 实现 canonical artifact materializer skeleton

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/generators/frontend_cross_provider_consistency_artifacts.py`、`tests/unit/test_frontend_cross_provider_consistency_artifacts.py`
- **可并行**：否
- **验收标准**：
  1. canonical root 固定为 `governance/frontend/cross-provider-consistency/`
  2. 至少落地 `consistency.manifest.yaml`、`handoff.schema.yaml`、`truth-surfacing.yaml`、`readiness-gate.yaml` 与 `provider-pairs/<pair_id>/...`
  3. pair-level diff/certification/evidence-index 能保留四轴状态与 UX contract refs
- **验证**：focused pytest

### Task 4.3 同步 runtime slice 1 task memory

- **任务编号**：T43
- **优先级**：P1
- **依赖**：T42
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/tasks.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/task-execution-log.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `150` 的任务记忆从 docs-only baseline 刷新为 runtime slice 1
  2. 文档诚实声明当前尚未落地 validator、ProgramService / CLI / verify
  3. 后续主线明确收敛到 `validator/rules -> handoff surfaces`
- **验证**：docs review、`git diff --check`

## Batch 5：pair-centric runtime slice 2

### Task 5.1 实现独立的 150 validator

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`src/ai_sdlc/core/frontend_cross_provider_consistency.py`、`tests/unit/test_frontend_cross_provider_consistency.py`
- **可并行**：否
- **验收标准**：
  1. validator 校验对象必须是 pair bundle，而不是单 provider snapshot
  2. validator 至少覆盖 page schema/style pack 对齐、coverage gap contract、truth surfacing layers 与 diff evidence refs
  3. validator 不把 `coverage-gap / not-comparable / upstream-blocked` 折叠成单一 `ready/blocked`
- **验证**：focused pytest

### Task 5.2 同步 runtime slice 2 task memory

- **任务编号**：T52
- **优先级**：P1
- **依赖**：T51
- **文件**：`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/tasks.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/task-execution-log.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `150` 的任务记忆从 runtime slice 1 刷新为 runtime slices 1-2
  2. 文档诚实声明当前尚未落地 ProgramService / CLI / verify
  3. 后续主线明确收敛到 `ProgramService / CLI / verify handoff`
- **验证**：docs review、`git diff --check`

## Batch 6：pair-centric runtime slice 3

### Task 6.1 实现 ProgramService / CLI / rules surfacing

- **任务编号**：T61
- **优先级**：P0
- **依赖**：T52
- **文件**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/sub_apps.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`、`tests/integration/test_cli_rules.py`
- **可并行**：否
- **验收标准**：
  1. `ProgramService` 能输出 `150` 的 pair-level handoff，而不是只暴露 isolated validator
  2. CLI 能直接显示 `ready / conditional / blocked` pair truth
  3. `rules materialize-frontend-cross-provider-consistency` 能写出 canonical artifacts
- **验证**：focused pytest

### Task 6.2 实现 verify attachment 与 runtime slice 3 task memory

- **任务编号**：T62
- **优先级**：P0
- **依赖**：T61
- **文件**：`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/plan.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/tasks.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/task-execution-log.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/development-summary.md`
- **可并行**：否
- **验收标准**：
  1. `verify constraints` 能把 `150` artifacts 与 pair gate readiness 纳入 verification context
  2. `150` 的任务记忆从 runtime slices 1-2 刷新为 runtime slices 1-3
  3. 文档诚实声明当前尚未落地 global truth refresh proof、close-out 或 Track E consumption
- **验证**：focused pytest、focused ruff、`git diff --check`
