# 任务分解：Frontend Evidence Class Authoring Surface Baseline

**编号**：`082-frontend-evidence-class-authoring-surface-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-082-001 ~ FR-082-008 / SC-082-001 ~ SC-082-004）

---

## 分批策略

```text
Batch 1: truth alignment
Batch 2: authoring surface freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `082` 只允许修改 `specs/082/...` 与本地 `project-state.yaml`
- `082` 不得修改 `program-manifest.yaml` 或模板
- `082` 不得回写 `081` formal docs
- `082` 不得进入 `src/` / `tests/`
- `082` 不得伪造当前 runtime 已识别 `frontend_evidence_class`

---

## Batch 1：truth alignment

### Task 1.1 对齐 authoring surface 缺口

- [x] 回读 `081`
- [x] 只读检查 `program-manifest.yaml` 与模板中是否已有可复用字段
- [x] 确认本轮应冻结 spec-local footer metadata，而不是先改 manifest

**完成标准**

- 能用单一 wording 解释为什么 `082` 先冻结 `spec.md` footer 作为 canonical surface

## Batch 2：authoring surface freeze

### Task 2.1 新建 `082` formal docs

- [x] 在 `spec.md` 明确 canonical key 为 `frontend_evidence_class`
- [x] 在 `spec.md` 明确 declaration location 为 `spec.md` footer metadata
- [x] 在 `plan.md` 明确 manifest 未来仅可作为 mirror

**完成标准**

- reviewer 能直接读出 future author 应该把 evidence class 写在哪里

### Task 2.2 冻结 allowed values 与 authoring error 语义

- [x] 明确合法值仅为 `framework_capability` 与 `consumer_adoption`
- [x] 明确缺失、空值、非法值、重复键与冲突声明属于 authoring error
- [x] 明确不 retroactively 要求既有 spec 回填该键

**完成标准**

- future parser / validator maintainer 能直接复用 `082` 的 authoring input contract

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `082` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `082` 能独立说明 evidence class 的 authoring surface

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `81` 推进到 `82`
- [x] 不伪造当前 runtime truth 已改变

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
