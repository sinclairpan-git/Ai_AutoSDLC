# 任务分解：Frontend Mainline Browser Gate Probe Runtime Baseline

**编号**：`103-frontend-mainline-browser-gate-probe-runtime-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-103-001` ~ `FR-103-015` / `SC-103-001` ~ `SC-103-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: probe-runtime contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `103` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/103/...`
- `103` 不得实现 Playwright runner、artifact store、视觉回归平台或多浏览器矩阵
- `103` 不得绑定 `020` handoff、recheck/remediation replay 或 program aggregation
- `103` 不得回写 `102` gate contract、`101` apply runtime truth、`071` a11y foundation truth 或 `073` provider/style truth
- `103` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 probe runtime 承接边界

- [x] 回读 `102` 中 execution context、四类检查、失败分类与 bundle materialization 的正式要求
- [x] 回读 `101` 中 apply result、source linkage 与 browser gate 下游约束
- [x] 回读 `071` 的 visual/a11y foundation 与 `073` 的 provider/style truth
- [x] 确认 `103` 只收 probe runtime，不把 `020` handoff binding 或 remediation replay 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `103` 是 `102` 的 probe-runtime child slice，而不是第二份 browser gate 母规格

## Batch 2：probe-runtime contract freeze

### Task 2.1 冻结 runtime session、artifact record 与 execution receipt

- [x] 在 `spec.md` 冻结 `BrowserGateProbeRuntimeSession`、`BrowserProbeArtifactRecord` 与 `BrowserProbeExecutionReceipt`
- [x] 在 `spec.md` 冻结 shared browser bootstrap、artifact namespace 与四类检查的 runtime execution order
- [x] 在 `spec.md` 固定 `evidence_missing / transient_run_failure` 的 runtime-level 诚实边界

**完成标准**

- reviewer 能直接判断 probe runtime 如何 materialize artifacts，以及它绝不会在 runtime 层偷做 `020` binding

### Task 2.2 冻结 bundle materialization input 与非目标

- [x] 在 `spec.md` 冻结 `BrowserQualityBundleMaterializationInput`
- [x] 在 `spec.md` 写清 `one gate_run_id == one runtime session == one artifact namespace`
- [x] 在 `spec.md` 写清本切片不实现 runner、artifact store、recheck/remediation binding 或多浏览器矩阵

**完成标准**

- maintainer 能直接回答为什么 `browser_quality_bundle` 只能消费当前 gate run artifacts

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `103` 能独立说明 probe runtime、artifact materialization、evidence honesty 与 bundle input 边界

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `103` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `103` 推进到 `104`

**完成标准**

- `103` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/103-frontend-mainline-browser-gate-probe-runtime-baseline`

**完成标准**

- 本轮 diff 保持 docs-only probe-runtime 边界且 fresh verification 通过
