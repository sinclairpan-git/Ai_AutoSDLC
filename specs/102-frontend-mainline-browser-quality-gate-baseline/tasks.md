# 任务分解：Frontend Mainline Browser Quality Gate Baseline

**编号**：`102-frontend-mainline-browser-quality-gate-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-102-001` ~ `FR-102-019` / `SC-102-001` ~ `SC-102-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: browser-gate contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `102` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/102/...`
- `102` 不得实现 Playwright runner、视觉回归平台、自动修复或自动重跑
- `102` 不得回写 `101` apply runtime truth、`071` a11y foundation truth 或 `020` execute gate truth
- `102` 不得放宽 `one bundle == one active spec scope == one managed frontend target`
- `102` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 browser gate 承接边界

- [x] 回读 `095` 中 browser gate、四类检查、失败分类与 bundle 的原始要求
- [x] 回读 `101` 中 apply result、source linkage 与 browser gate handoff 的下游约束
- [x] 回读 `071` 的 visual/a11y foundation 与 `020` 的 execute/recheck/remediation vocabulary
- [x] 确认 `102` 只收 browser quality gate，不把 apply runtime、remediation engine 或 program aggregation 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `102` 是 `101` 的 browser-gate child slice，而不是新的 program 母规格

## Batch 2：browser-gate contract freeze

### Task 2.1 冻结 execution context、check result 与 bundle

- [x] 在 `spec.md` 冻结 `BrowserQualityGateExecutionContext`、`BrowserQualityCheckResult` 与 `browser_quality_bundle`
- [x] 在 `spec.md` 冻结四类检查的最低覆盖面与输入真值
- [x] 在 `spec.md` 固定 eligibility -> context freeze -> probe execution -> failure classification -> bundle -> handoff 的顺序

**完成标准**

- reviewer 能直接判断 browser gate 何时允许启动，以及它绝不会在 gate 期改写 apply/solution truth

### Task 2.2 冻结 failure honesty 与 020 handoff

- [x] 在 `spec.md` 固定 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only` 的分类边界
- [x] 在 `spec.md` 冻结 `FrontendBrowserGateHandoff` 与 `020` consume surface
- [x] 在 `spec.md` 写清单一 bundle scope/target/source-linkage 绑定规则

**完成标准**

- maintainer 能直接回答为什么 browser gate 只产出 spec 级 handoff，而不是 program 级最终 ready verdict

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `102` 能独立说明 browser gate、bundle、failure honesty 与 `020` handoff 边界

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `102` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `102` 推进到 `103`

**完成标准**

- `102` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/102-frontend-mainline-browser-quality-gate-baseline`

**完成标准**

- 本轮 diff 保持 docs-only browser-gate 边界且 fresh verification 通过
