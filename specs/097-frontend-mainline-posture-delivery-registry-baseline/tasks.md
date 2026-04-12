# 任务分解：Frontend Mainline Posture Delivery Registry Baseline

**编号**：`097-frontend-mainline-posture-delivery-registry-baseline` | **日期**：2026-04-12  
**来源**：plan.md + spec.md（`FR-097-001` ~ `FR-097-030` / `SC-097-001` ~ `SC-097-006`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: posture + delivery registry formal freeze
Batch 3: scaffold, project-state update, verification
```

---

## 执行护栏

- `097` 只允许修改 `specs/097/...` 与本地 `project-state.yaml`
- `097` 不得实现 posture detector、registry materializer、action planner、installer 或 rollback runtime
- `097` 不得允许 arbitrary npm URL / git repo / private registry source 进入主流程
- `097` 不得默认 takeover unsupported existing frontend
- `097` 不得改写 `014`、`016`、`073`、`094`、`095`、`096` 已冻结 truth
- `097` 不得新建第二份 provider/style compatibility matrix
- `097` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 upstream truth 与仓库 reality

- [x] 回读 `014`、`016`、`073`、`094`、`095`、`096`
- [x] 回读 provider artifact reality 与相关 tests
- [x] 确认仓库当前已有 `enterprise-vue2` / `public-primevue` reality，但缺少独立冻结的 `frontend_posture_assessment` contract

**完成标准**

- 能用单一 wording 解释为什么 `097` 必须先冻结 brownfield posture + controlled registry，而不是直接假装 action engine 已经存在

## Batch 2：posture + delivery registry formal freeze

### Task 2.1 冻结 posture / sidecar / no-touch truth

- [x] 在 `spec.md` 冻结 `frontend_posture_assessment` 的状态、证据与 next-step boundary
- [x] 在 `spec.md` 冻结 `sidecar_root_recommendation` 与 `will_not_touch_defaults`
- [x] 在 `spec.md` 写清 unsupported / ambiguous / managed-attached 的诚实语义

**完成标准**

- reviewer 能直接判断 existing frontend 遇到 `React`、unknown 或已有托管前端时，系统是否会保持 fail-closed honesty

### Task 2.2 冻结 controlled registry / delivery bundle truth

- [x] 在 `spec.md` 冻结 `frontend_delivery_registry` / `delivery_bundle_entry` 的字段面
- [x] 在 `spec.md` 写清 `enterprise-vue2` 与 `public-primevue` 是 v1 正式条目
- [x] 在 `spec.md` 冻结 `provider_manifest_ref` / `resolved_style_support_ref` 的单向引用规则

**完成标准**

- maintainer 能直接回答 delivery bundle 引用哪一份 provider/style truth，且不会再维护第二份 registry matrix

## Batch 3：scaffold, project-state update, verification

### Task 3.1 初始化 canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `097` 能独立说明 posture、sidecar、registry、delivery bundle 与 downstream handoff 的边界

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `97` 推进到 `98`
- [x] 不伪造当前 runtime truth 已实现

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/097-frontend-mainline-posture-delivery-registry-baseline`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
