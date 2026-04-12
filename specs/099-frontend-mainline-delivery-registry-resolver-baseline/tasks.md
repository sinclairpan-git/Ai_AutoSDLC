# 任务分解：Frontend Mainline Delivery Registry Resolver Baseline

**编号**：`099-frontend-mainline-delivery-registry-resolver-baseline` | **日期**：2026-04-12  
**来源**：plan.md + spec.md（`FR-099-001` ~ `FR-099-025` / `SC-099-001` ~ `SC-099-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: resolver contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `099` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/099/...`
- `099` 不得实现 resolver runtime、registry writer、action planner、installer 或 rollback executor
- `099` 不得生成第二份 provider/style compatibility truth
- `099` 不得新增第三条 built-in delivery entry
- `099` 不得改写 `073`、`096`、`097`、`098` 已冻结 truth
- `099` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 resolver 上游 truth 与拆分边界

- [x] 回读 `097` 中 registry / delivery bundle 的 formal freeze 与拆分建议
- [x] 回读 `098` 中 detector 的 handoff boundary
- [x] 确认 `099` 只收 resolver，不把 runtime materialization 或 planner 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `099` 需要单独冻结 built-in artifacts join、entry selection、single-ref 与 drift fail-closed

## Batch 2：resolver contract freeze

### Task 2.1 冻结 built-in registry source 与 join 规则

- [x] 在 `spec.md` 冻结 provider artifacts、solution catalog artifacts 与 selection context
- [x] 在 `spec.md` 写清 `component_library_packages`、`adapter_packages`、`runtime_requirements` 的来源
- [x] 在 `spec.md` 固定 v1 registry matrix 只有两条 built-in entry

**完成标准**

- reviewer 能直接判断 entry truth 来自哪里，以及 resolver 如何把 provider/style/install strategy 归并成单一条目

### Task 2.2 冻结 single-ref 与 drift semantics

- [x] 在 `spec.md` 固定 `provider_manifest_ref` / `resolved_style_support_ref` 的单向引用规则
- [x] 在 `spec.md` 冻结 fail-closed drift 条件
- [x] 在 `spec.md` 写清 resolver 不得静默 fallback 到默认 provider/style

**完成标准**

- maintainer 能直接回答 resolver 在 manifest/style/install strategy 漂移时为什么必须阻断，而不是伪造次优 entry

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `099` 能独立说明 resolver input、join order、v1 entry、single-ref 与 drift boundary

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `099` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `99` 推进到 `100`

**完成标准**

- `099` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/099-frontend-mainline-delivery-registry-resolver-baseline`

**完成标准**

- 本轮 diff 保持 docs-only resolver 边界且 fresh verification 通过
