# 任务分解：Frontend Framework-Only Prospective Closure Contract Baseline

**编号**：`081-frontend-framework-only-prospective-closure-contract-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-081-001 ~ FR-081-008 / SC-081-001 ~ SC-081-004）

---

## 分批策略

```text
Batch 1: truth alignment
Batch 2: prospective contract freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `081` 只允许修改 `specs/081/...` 与本地 `project-state.yaml`
- `081` 不得回写 `079`、`080` formal docs
- `081` 不得修改 `frontend-program-branch-rollout-plan.md`
- `081` 不得进入 `src/` / `tests/`
- `081` 不得伪造当前 runtime 已识别 evidence class

---

## Batch 1：truth alignment

### Task 1.1 对齐 prospective-only 边界

- [x] 回读 `079`、`080`
- [x] 确认当前缺口在 future machine-gate contract，而不是 root wording
- [x] 明确本轮不得 retroactively 改义 `068` ~ `071`

**完成标准**

- 能用单一 wording 解释为什么 `081` 只冻结 future contract

## Batch 2：prospective contract freeze

### Task 2.1 新建 `081` formal docs

- [x] 在 `spec.md` 明确 `081` 是 prospective-only contract baseline
- [x] 在 `plan.md` 冻结 evidence class / split rule / future runtime target
- [x] 在 `spec.md` 明确不规定本轮 metadata 字段名或 runtime 实现

**完成标准**

- reviewer 能直接读出 future item 需要声明 evidence class

### Task 2.2 冻结 future machine-gate input semantics

- [x] 明确 `framework_capability` 与 `consumer_adoption` 的 close semantics
- [x] 明确 mixed requirement 必须拆 item
- [x] 明确未声明 evidence class 的 future framework-only item 属于 authoring error

**完成标准**

- future runtime maintainer 能直接拿 `081` 作为后续实现 contract

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `081` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `081` 能独立说明 prospective closure contract 的边界

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `80` 推进到 `81`
- [x] 不伪造当前 runtime truth 已改变

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
