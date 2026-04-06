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
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend P1 Visual A11y Foundation Baseline

**编号**：`071-frontend-p1-visual-a11y-foundation-baseline` | **日期**：2026-04-06  
**来源**：plan.md + spec.md（FR-071-001 ~ FR-071-023 / SC-071-001 ~ SC-071-006）

---

## 分批策略

```text
Batch 1: positioning and truth-order freeze
Batch 2: visual foundation coverage freeze
Batch 3: a11y foundation and feedback honesty freeze
Batch 4: execution log init, project-state update, docs-only validation
```

---

## 执行护栏

- `071` 当前只允许 docs-only formal baseline freeze，不得进入 `src/` / `tests/`。
- `071` 不得改写 `067` 已冻结的 `Ui*` / 页面级状态语义、`068` 的 page recipe truth、`069` 的 diagnostics coverage matrix 或 drift classification。
- `071` 不得扩张 sibling recheck / remediation feedback、bounded remediation runbook、writeback artifact、provider handoff payload 或完整 auto-fix engine。
- `071` 不得把 visual / a11y foundation 膨胀成完整 visual regression 平台、完整 a11y/WCAG 平台、interaction quality platform 或跨 provider 一致性平台。
- `071` 不得默认发现任何 visual / a11y evidence source，也不得把 sample fixture 或当前仓库根写成隐式 evidence input。
- `071` 不得修改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`。
- `071` 不得生成 `development-summary.md`，也不得宣称 close-ready、已实现或已进入 program close。
- `071` 不得改写 `009/017/018/065/066/067/068/069` 的 formal truth，也不得用质量反馈反向放宽上游 diagnostics / gate / generation baseline。
- 只有在 `071` docs-only 门禁通过且用户明确要求继续时，才允许进入实现批次或 root sync 讨论。

---

## Batch 1：positioning and truth-order freeze

### Task 1.1 冻结 `071` 作为 P1 visual/a11y child 的定位

- [x] 在 `spec.md` 明确 `071` 是 `066` 下游第五条 child work item
- [x] 在 `spec.md` 明确 `071` 位于 `067 + 068 + 069` 之后，并与 sibling recheck/remediation child 并列
- [x] 在 `spec.md` 明确 `071` 不是 diagnostics / recheck-remediation / provider-runtime 工单

**完成标准**

- `spec.md` 能独立表达 `071 != 069 != sibling recheck/remediation != provider/runtime`

### Task 1.2 冻结 `071` 的 non-goals 与 truth order

- [x] 在 `spec.md` 明确 `071` 只能消费 `067 + 068 + 069 + 018 + 065`
- [x] 在 `plan.md` 明确 visual / a11y foundation 不得反向重写 diagnostics / gate / generation / kernel / recipe baseline
- [x] 在 `tasks.md` 明确当前工单禁止跨层写入

**完成标准**

- reviewer 可直接从 formal docs 读出 `Contract -> Kernel -> Provider/Code -> Gate` 顺序未变化

## Batch 2：visual foundation coverage freeze

### Task 2.1 冻结 P1 visual foundation coverage matrix

- [x] 在 `spec.md` 给出 `state visual presence` 的最小覆盖对象与边界
- [x] 在 `spec.md` 给出 `required-area visual presence` 的最小覆盖对象与边界
- [x] 在 `spec.md` 给出 `controlled-container visual continuity` 的最小覆盖对象与边界

**完成标准**

- 文档明确 visual foundation 只承接“最小可感知质量面”，不是像素级平台

### Task 2.2 冻结 visual evidence 与 visual feedback 边界

- [x] 在 `spec.md` 明确 visual evidence 必须为显式输入
- [x] 在 `spec.md` 明确 visual findings 继续复用 `018` report family
- [x] 在 `plan.md` 明确未来 visual evidence fixture 的推荐触点

**完成标准**

- 文档明确 `sample fixture != implicit visual evidence source`

## Batch 3：a11y foundation and feedback honesty freeze

### Task 3.1 冻结 P1 a11y foundation coverage matrix

- [x] 在 `spec.md` 给出 `error/status perceivability` 的最小覆盖对象与边界
- [x] 在 `spec.md` 给出 `accessible naming / semantics`、`keyboard reachability`、`focus continuity` 的最小覆盖对象与边界
- [x] 在 `spec.md` 明确当前工单不扩张为完整 WCAG/a11y 平台

**完成标准**

- 文档明确 a11y foundation 是底线检查，不是完整平台

### Task 3.2 冻结 evidence honesty 与 sibling handoff boundary

- [x] 在 `spec.md` 明确 `input gap / stable empty / actual issue` 的区分
- [x] 在 `spec.md` 明确 sibling recheck/remediation 继续承接作者体验闭环
- [x] 在 `plan.md` 明确未来实现不应直接生成 remediation runbook 或 provider/runtime 代码

**完成标准**

- 文档明确 `071` 只冻结检查面与最小反馈边界，不误吞 sibling remediation 主线

## Batch 4：execution log init, project-state update, docs-only validation

### Task 4.1 初始化 canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 写入当前边界、批次范围与 accepted/frozen 状态
- [x] 在 `project-state.yaml` 将 `next_work_item_seq` 从 worktree 基线的 `70` 推进到 `72`

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

- `071` formal docs 可独立表达 visual foundation、a11y foundation、evidence boundary 与 feedback honesty 的 scope 与 truth-order
- `071` 不被误读成 diagnostics / recheck-remediation / provider-runtime / 完整质量平台工单
- docs-only 门禁通过，且状态诚实表达为“accepted child baseline”
