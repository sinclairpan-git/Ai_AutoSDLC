# 任务分解：Frontend Mainline Posture Detector Baseline

**编号**：`098-frontend-mainline-posture-detector-baseline` | **日期**：2026-04-12  
**来源**：plan.md + spec.md（`FR-098-001` ~ `FR-098-022` / `SC-098-001` ~ `SC-098-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: detector contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `098` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/098/...`
- `098` 不得实现 detector runtime、resolver、action planner、installer 或 sidecar scaffold writer
- `098` 不得让 component-library clue 单独决定 supported verdict
- `098` 不得默认 takeover unsupported existing frontend
- `098` 不得改写 `014`、`073`、`094`、`095`、`096`、`097` 已冻结 truth
- `098` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 detector 上游 truth 与拆分边界

- [x] 回读 `095` 中 `frontend_posture_assessment` 的原始字段面
- [x] 回读 `097` 中 posture / registry 的 formal freeze 与拆分建议
- [x] 确认 `098` 只收 detector，不把 registry resolver 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `098` 需要单独冻结 evidence source、优先级、五类状态与 sidecar 边界

## Batch 2：detector contract freeze

### Task 2.1 冻结 evidence source 与优先级

- [x] 在 `spec.md` 冻结 attachment truth、repo signal、component-library clue 的 evidence class
- [x] 在 `spec.md` 写清 dominant evidence 与 conflict downgrade 规则
- [x] 在 `spec.md` 固定 attachment truth 优先级最高

**完成标准**

- reviewer 能直接判断 detector 如何在 attached / repo signal / weak clue 冲突时给出诚实 verdict

### Task 2.2 冻结五类状态与 sidecar recommendation boundary

- [x] 在 `spec.md` 固定五类 `support_status` 的成立条件
- [x] 在 `spec.md` 冻结 `sidecar_root_recommendation` 的 detector-only 输出边界
- [x] 在 `spec.md` 写清 detector 不得决定 provider/style/install/root integration

**完成标准**

- maintainer 能直接回答 detector 在 unsupported / ambiguous / no frontend 时最多允许给出什么建议

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `098` 能独立说明 detector evidence、状态语义、sidecar 边界与 downstream handoff

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `098` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `98` 推进到 `99`

**完成标准**

- `098` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/098-frontend-mainline-posture-detector-baseline`

**完成标准**

- 本轮 diff 保持 docs-only detector 边界且 fresh verification 通过
