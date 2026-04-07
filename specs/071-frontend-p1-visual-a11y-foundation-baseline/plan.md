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
# 执行计划：Frontend P1 Visual A11y Foundation Baseline

**功能编号**：`071-frontend-p1-visual-a11y-foundation-baseline`  
**创建日期**：2026-04-06  
**状态**：docs-only formal freeze  

## 1. 目标与定位

`071` 是 `066` 下游的第五条 child work item，用于把 P1 visual / a11y foundation 冻结成单一 formal truth。它位于 `067 + 068 + 069` 之后，与 sibling recheck / remediation feedback child 并列，不承接 diagnostics truth、不承接 bounded remediation runbook，也不承接 provider/runtime 实现。

当前批次只做 docs-only formal freeze，目标是回答 4 个问题：

- P1 级“基础 visual / a11y 检查”到底只到哪里
- 这些检查如何继续消费 `067 + 068 + 069 + 018 + 065` 的组合 truth
- 最小 evidence boundary 与 feedback honesty 应如何冻结
- 哪些内容必须继续留给 sibling recheck/remediation、provider/runtime 与 P2 质量平台

## 2. 范围

### 2.1 In Scope

- 冻结 P1 visual foundation coverage matrix
- 冻结 P1 a11y foundation coverage matrix
- 冻结 visual / a11y evidence boundary 与 input gap / stable empty 语义
- 冻结 visual / a11y feedback 继续服从 `018` report family 的边界
- 冻结与 sibling recheck/remediation、provider/runtime、P2 完整质量平台的 handoff

### 2.2 Out Of Scope

- 实现截图采集、视觉比对、axe 集成、浏览器自动化或完整 a11y runtime
- 扩张 diagnostics / drift 分类、compatibility 执行强度、recheck 计划、remediation runbook 或 auto-fix engine
- 建设完整 visual regression 平台、跨浏览器/跨设备矩阵、完整 WCAG 平台、interaction quality gate
- 编写 provider/runtime 映射、视觉样式实现、Vue 组件代码或企业样式规范
- 修改 root `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md` 或生成 `development-summary.md`

## 3. 未来实现触点

当前批次不改代码，但 future implementation 预计主要落在以下文件面：

- `src/ai_sdlc/core/frontend_gate_verification.py`
- `src/ai_sdlc/gates/frontend_contract_gate.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/models/frontend_gate_policy.py`
- `tests/unit/test_verify_constraints.py`
- `tests/integration/test_cli_verify_constraints.py`
- `tests/fixtures/frontend-visual-a11y-*`

这些触点仅用于表达未来实现归属，不授权当前批次直接改动。

## 4. 分阶段计划

### Phase 0：positioning and truth-order freeze

- 明确 `071` 是 `066` 下游的 visual / a11y foundation child
- 明确 `071` 位于 `067 + 068 + 069` 之后，与 sibling recheck/remediation 并列
- 明确 `071` 不重写 diagnostics、recheck/remediation 或 provider/runtime baseline

### Phase 1：visual foundation coverage freeze

- 冻结 `state visual presence`
- 冻结 `required-area visual presence`
- 冻结 `controlled-container visual continuity`
- 明确 visual foundation 只承接“最小可感知质量面”，不进入像素级平台

### Phase 2：a11y foundation coverage freeze

- 冻结 `error/status perceivability`
- 冻结 `accessible naming / semantics`
- 冻结 `keyboard reachability`
- 冻结 `focus continuity`

### Phase 3：evidence boundary and feedback honesty freeze

- 冻结显式 evidence source 边界
- 冻结 `input gap / stable empty / actual issue` 的诚实区分
- 冻结 visual / a11y feedback 继续复用 `018` report family 的边界
- 冻结与 sibling recheck/remediation 的 handoff

### Phase 4：execution log init, project-state update, docs-only validation

- 创建 canonical docs 与 execution log
- 将 `project-state.yaml` 的 `next_work_item_seq` 从 worktree 基线的 `70` 推进到 `72`
- 运行 docs-only 门禁并归档结果

## 5. Owner Boundary

- `071` 只拥有 P1 visual / a11y foundation 的 planning truth
- `069` 继续拥有 diagnostics / drift coverage matrix 与分类 truth
- sibling recheck/remediation child 继续拥有作者反馈、runbook、writeback 与 remediation execution 边界
- provider/runtime 主线继续拥有实际组件/样式/交互实现
- P2 主线继续拥有完整 visual regression、完整 a11y 平台、interaction quality 与跨 provider 一致性

## 6. 最小验证策略

当前批次只允许 docs-only / read-only 门禁：

- `uv run ai-sdlc verify constraints`
- `git diff --check`

未来实现阶段的最小测试矩阵应至少覆盖：

- visual foundation 对 `refreshing / submitting / no-results / partial-error / success-feedback` 的 evidence 与反馈分类
- a11y foundation 对表单错误、主操作、分页、搜索/筛选、对话/向导焦点连续性的检查
- evidence 缺失与 stable empty 的诚实区分
- visual / a11y findings 继续复用 `018` report family，而不是第二套 schema

## 7. 执行前提与回滚

执行前提：

- `067`、`068`、`069` 已作为 docs-only baseline formalize
- 当前批次保持 docs-only，不进入实现
- `.worktrees/` 继续作为隔离工作目录，且不触碰 root truth

回滚原则：

- 如发现 `071` 抢跑 diagnostics、recheck/remediation、provider/runtime 或完整质量平台语义，应在 formal docs 中回退到 P1 foundation 边界
- 如发现 visual / a11y evidence boundary 与 `065/018` 冲突，应优先保持显式输入与同一套 report family 的单一真值
