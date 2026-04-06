---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 Recheck Remediation Feedback Baseline

**编号**：`070-frontend-p1-recheck-remediation-feedback-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-070-001 ~ FR-070-021 / SC-070-001 ~ SC-070-005）

---

## 分批策略

```text
Batch 1: positioning and truth-order freeze
Batch 2: recheck and remediation object boundary freeze
Batch 3: runbook/writeback/handoff honesty freeze
Batch 4: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `070` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `070` 不得改写 `069` 已冻结的 diagnostics coverage matrix、gap / empty / drift classification 或 compatibility feedback boundary。
- `070` 不得扩张 `071` visual / a11y、截图比对、a11y 平台或任何视觉质量基线。
- `070` 不得把 bounded remediation feedback 膨胀成完整 auto-fix engine、任意脚本执行器、整页重写或 provider/runtime 代码生成。
- `070` 不得默认发现 `<frontend-source-root>`，也不得把 sample fixture 或当前仓库根写成隐式 remediation source。
- `070` 不得修改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`。
- `070` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现或已进入 program close。
- `070` 不得改写 `009/017/018/065/066/067/068/069` 的 formal truth，也不得用 author feedback 反向放宽上游 diagnostics / gate / generation 基线。
- 只有在 `070` docs-only 门禁通过且用户明确要求继续时，才允许进入实现批次或 formalize 下游 `071`。

---

## Batch 1：positioning and truth-order freeze

### Task 1.1 冻结 `070` 作为 P1 recheck/remediation child 的定位

- [x] 在 `spec.md` 明确 `070` 是 `066` 下游第四条 child work item
- [x] 在 `spec.md` 明确 `070` 位于 `069` 之后，并与 `071` 并列而非互相吞并
- [x] 在 `spec.md` 明确 `070` 不是 diagnostics / visual-a11y / provider/runtime 工单

**完成标准**

- `spec.md` 能独立表达 `070 != 069 != 071`

### Task 1.2 冻结 `070` 的 non-goals 与 truth order

- [x] 在 `spec.md` 明确 `070` 只能消费 `069 + 018 + 017 + 065 + 067 + 068`
- [x] 在 `plan.md` 明确 remediation / recheck 不得反向重写 diagnostics / gate / generation / kernel / recipe baseline
- [x] 在 `tasks.md` 明确当前工单禁止跨层写入

**完成标准**

- reviewer 可直接从 formal docs 读出 `Contract -> Kernel -> Provider/Code -> Gate -> Recheck/Remediation Feedback` 顺序未变化

## Batch 2：recheck and remediation object boundary freeze

### Task 2.1 冻结 `frontend_recheck_handoff`

- [x] 在 `spec.md` 给出 `frontend_recheck_handoff` 的最小字段边界
- [x] 在 `spec.md` 明确 readiness `READY` 与 recheck handoff 的关系
- [x] 在 `spec.md` 明确 recheck handoff 继续复用 `018` 的 verify / report truth

**完成标准**

- 文档明确 recheck handoff 是 post-execute verify 提示，而不是第二套 gate

### Task 2.2 冻结 `frontend_remediation_input`

- [x] 在 `spec.md` 给出 `frontend_remediation_input` 的最小字段边界
- [x] 在 `spec.md` 明确 remediation input 继续消费 `069` 的分类 truth
- [x] 在 `spec.md` 明确 observation remediation 必须要求显式 `<frontend-source-root>`

**完成标准**

- 文档明确 remediation input 是 bounded author feedback，而不是开放式修复策略引擎

## Batch 3：runbook/writeback/handoff honesty freeze

### Task 3.1 冻结 bounded remediation runbook

- [x] 在 `spec.md` 明确 bounded remediation runbook 的最小职责
- [x] 在 `spec.md` 明确 remediation command 集必须保持 bounded / reviewable
- [x] 在 `plan.md` 明确未来实现触点与未知命令显式失败的预期

**完成标准**

- 文档明确 remediation execute 不能升级成任意命令执行器

### Task 3.2 冻结 writeback artifact / provider handoff / downstream boundary

- [x] 在 `spec.md` 明确 remediation writeback artifact 的最小角色
- [x] 在 `spec.md` 明确 provider handoff payload 只消费摘要与审计信息
- [x] 在 `spec.md` 明确 `071` 继续承接 visual / a11y，不得在当前工单混入

**完成标准**

- 文档明确 `070` 之后的 handoff 边界，不误吞 `071` 或 provider/runtime 主线

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 写入当前边界、批次范围与 accepted 状态
- [x] 在 `project-state.yaml` 将 `next_work_item_seq` 从 `70` 推进到 `71`

**完成标准**

- 目录结构完整，且当前状态诚实表达为 docs-only formal freeze 初始化

### Task 4.2 运行 docs-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check`
- [x] 在 `task-execution-log.md` 记录 touched files、命令与结果

**完成标准**

- `verify constraints` 无 blocker
- `git diff --check` 无输出

## 完成定义

- `070` formal docs 可独立表达 recheck handoff、bounded remediation feedback、runbook / writeback / provider handoff 的 scope 与 truth-order
- `070` 不被误读成 diagnostics / visual-a11y / provider-runtime / auto-fix engine 工单
- docs-only 门禁通过，且状态诚实表达为“formal freeze 已完成并 accepted（accepted child baseline）”
- 文中出现的下游 `071` 编号仅作当前 planning 占位；真实编号以后续 scaffold 时的 `project-state` 为准
