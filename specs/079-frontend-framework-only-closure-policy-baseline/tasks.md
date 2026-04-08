# 任务分解：Frontend Framework-Only Closure Policy Baseline

**编号**：`079-frontend-framework-only-closure-policy-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-079-001 ~ FR-079-008 / SC-079-001 ~ SC-079-004）

---

## 分批策略

```text
Batch 1: truth alignment
Batch 2: docs-only policy freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `079` 只允许修改 `specs/079/...` 与本地 `project-state.yaml`
- `079` 不得回写 `065`、`076`、`077`、`078` 或 `frontend-program-branch-rollout-plan.md`
- `079` 不得进入 `src/` / `tests/`
- `079` 不得伪造任何现有 active spec 已获得真实 consumer implementation evidence

---

## Batch 1：truth alignment

### Task 1.1 对齐 framework-only repo 边界

- [x] 回读 `065`、`076`、`077`、`078`
- [x] 确认现有仓库没有已冻结的替代 runtime status 术语
- [x] 明确 policy baseline 只能冻结职责分层，不能直接改 root truth

**完成标准**

- 能用单一 wording 解释当前为什么会出现“框架能力完成但 consumer evidence 仍缺”的张力

## Batch 2：docs-only policy freeze

### Task 2.1 新建 `079` formal docs

- [x] 在 `spec.md` 明确 `079` 是 policy baseline，而不是 close-sync carrier
- [x] 在 `plan.md` 冻结 framework-only repository 的 evidence split
- [x] 在 `spec.md` / `plan.md` 明确 future work item 的拆分原则

**完成标准**

- reviewer 能直接读出 framework capability evidence 与 consumer implementation evidence 的边界

### Task 2.2 冻结 honesty guardrails

- [x] 在 `spec.md` 明确 sample self-check 不能冒充 consumer artifact
- [x] 在 `plan.md` 明确本轮不发明新的 runtime status code
- [x] 在 `spec.md` 明确当前 root machine truth 不会自动改变

**完成标准**

- operator 不会把 `079` 误解为已解决 `068` ~ `071` 的当前 blocker

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `079` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `079` 能独立说明 framework-only closure policy

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `78` 推进到 `79`
- [x] 不伪造 close、merge 或 root blocker 已解除 truth

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
