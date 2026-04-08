# 任务分解：Frontend Framework-Only Root Policy Sync Baseline

**编号**：`080-frontend-framework-only-root-policy-sync-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-080-001 ~ FR-080-008 / SC-080-001 ~ SC-080-004）

---

## 分批策略

```text
Batch 1: truth alignment
Batch 2: root wording sync
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `080` 只允许修改 `specs/080/...`、`frontend-program-branch-rollout-plan.md` 与本地 `project-state.yaml`
- `080` 不得回写 `076`、`077`、`078`、`079` formal docs
- `080` 不得进入 `src/` / `tests/`
- `080` 不得伪造 `068` ~ `071` 已获得真实 consumer implementation evidence

---

## Batch 1：truth alignment

### Task 1.1 对齐 framework-only root wording 输入

- [x] 回读 `076`、`077`、`078`、`079`
- [x] 确认 root 文档现状已区分 archived closeout 与 root non-close，但尚未同步 policy split
- [x] 明确本轮只能改 wording，不改 machine truth

**完成标准**

- 能用单一 wording 解释 `068` ~ `071` 当前为什么仍非 `close`

## Batch 2：root wording sync

### Task 2.1 新建 `080` formal docs

- [x] 在 `spec.md` 明确 `080` 是 root honesty-sync carrier
- [x] 在 `plan.md` 冻结 root wording sync 规则
- [x] 在 `spec.md` / `plan.md` 明确 `077` ~ `079` 的输入角色

**完成标准**

- reviewer 能直接理解 `080` 为什么只同步 wording 而不改状态

### Task 2.2 收紧 P1 rollout wording

- [x] 更新主线分段里 `068` ~ `071` 的描述
- [x] 更新 `068` ~ `071` 表项，明确 blocker 是 consumer implementation evidence 缺口
- [x] 在备注中同步 `077`、`078`、`079` 的职责边界

**完成标准**

- root 文档不会再把当前 blocker 读成框架 capability 尚未存在

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `080` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `080` 能独立说明本轮 root wording sync 的边界

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `79` 推进到 `80`
- [x] 不伪造 `068` ~ `071` 当前 root blocker 已解除

**完成标准**

- work item 序号与本轮新建 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
