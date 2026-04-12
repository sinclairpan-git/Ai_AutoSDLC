# 任务分解：Frontend Mainline Browser Gate Recheck Remediation Binding Baseline

**编号**：`104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline` | **日期**：2026-04-13  
**来源**：plan.md + spec.md（`FR-104-001` ~ `FR-104-015` / `SC-104-001` ~ `SC-104-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: result-binding contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `104` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/104/...`
- `104` 不得实现 replay runtime、auto-fix engine、CLI wiring 或 program aggregation
- `104` 不得改写 `102` gate contract、`103` probe runtime 或 `020` execute baseline
- `104` 不得把 advisory 升级为 blocker，或把 bounded replay request 写成后台自动循环
- `104` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 result-binding 承接边界

- [x] 回读 `102` 中 bundle、handoff、failure taxonomy 与 `020` vocabulary 的正式要求
- [x] 回读 `103` 中 runtime evidence lineage、artifact honesty 与 non-goals
- [x] 回读 `020` 中 execute state、recheck handoff 与 remediation hint 的最小输入面
- [x] 确认 `104` 只收结果绑定，不把 runtime replay、auto-fix 或 program aggregation 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `104` 是 `103` 的 result-binding child slice，而不是第三份 browser gate 母规格

## Batch 2：result-binding contract freeze

### Task 2.1 冻结 execute decision、recheck binding 与 remediation binding

- [x] 在 `spec.md` 冻结 `BrowserGateExecuteHandoffDecision`
- [x] 在 `spec.md` 冻结 `ProgramFrontendRecheckBinding`、`ProgramFrontendRemediationBinding` 与 `BrowserGateReplayRequest`
- [x] 在 `spec.md` 固定 `recheck_required / needs_remediation / blocked / ready` 的映射与诚实边界

**完成标准**

- reviewer 能直接判断 browser gate 结果何时该重跑、何时该修复、何时只是 advisory

### Task 2.2 冻结 fail-closed 条件与非目标

- [x] 在 `spec.md` 写清 stale bundle、scope mismatch、source linkage 缺失与 result inconsistency 的 fail-closed 规则
- [x] 在 `spec.md` 写清 bounded replay request 不等于自动重跑 loop
- [x] 在 `spec.md` 写清本切片不实现 auto-fix、runtime replay 或 CLI wiring

**完成标准**

- maintainer 能直接回答为什么 `020` 不需要反向猜测 browser gate 结果可信度

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `104` 能独立说明 result binding、bounded replay 与 diagnostics-first blocked 的边界

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `104` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `104` 推进到 `105`

**完成标准**

- `104` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline`

**完成标准**

- 本轮 diff 保持 docs-only result-binding 边界且 fresh verification 通过
