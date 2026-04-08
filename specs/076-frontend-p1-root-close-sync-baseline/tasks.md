# 任务分解：Frontend P1 Root Close Sync Baseline

**编号**：`076-frontend-p1-root-close-sync-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-076-001 ~ FR-076-009 / SC-076-001 ~ SC-076-006）

---

## 分批策略

```text
Batch 1: close sync semantics freeze
Batch 2: rollout wording sync
Batch 3: execution log, project-state update, docs-only validation
Batch 4: archived closeout honesty sync
```

---

## 执行护栏

- `076` 只允许修改 `specs/076/...` 与根级 `frontend-program-branch-rollout-plan.md`
- `076` 不得修改 `program-manifest.yaml`
- `076` 不得回写 `067` ~ `071` formal docs，也不得进入 `src/` / `tests/`
- `076` 不得把自己写入 root rollout table 或 root manifest
- `076` 所有表述都必须显式区分 `067 close`、`068` ~ `071` archived carrier closeout 与 `068` ~ `071` root not closed

---

## Batch 1：close sync semantics freeze

### Task 1.1 冻结 `076` 的 carrier 边界

- [x] 在 `spec.md` 明确 `076` 只做 P1 root close wording sync
- [x] 在 `plan.md` 明确本轮不再修改 `program-manifest.yaml`
- [x] 在 `spec.md` / `plan.md` 明确 `076` 不进入 root DAG

**完成标准**

- reviewer 可直接读出 `076` 的 close sync carrier 角色

### Task 1.2 冻结 `067` / `068` 的新状态口径

- [x] 在 `spec.md` 明确 `067` 当前是 `close`
- [x] 在 `spec.md` 明确 `068` 当前已解锁但仍未 close
- [x] 在 rollout plan 备注中保留该职责边界

**完成标准**

- root 文档不会把 `067` 与 `068` 的当前 program 阶段写错

## Batch 2：rollout wording sync

### Task 2.1 同步 P1 主线与排序表

- [x] 更新主线分段中的 P1 描述
- [x] 更新排序总表中的 `067` 状态口径
- [x] 更新排序总表中的 `068` 状态口径

**完成标准**

- root rollout plan 与当前 `program status` 对齐

### Task 2.2 保持 root DAG 不变

- [x] 不修改 `program-manifest.yaml`
- [x] 不改写 `067/068` direct dependency set
- [x] 不把 `076` 写入 root rollout table

**完成标准**

- 本轮 diff 仅限 rollout wording 与本地 project state

## Batch 3：execution log, project-state update, docs-only validation

### Task 3.1 初始化 `076` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 归档 touched files、命令与结果

**完成标准**

- `076` formal docs 可独立说明本轮 close sync 的目标、边界与验证口径

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `75` 推进到 `76`
- [x] 不伪造 close、merge 或 implementation truth

**完成标准**

- 下一个可用编号被诚实前进到 `76`

### Task 3.3 运行 docs-only / read-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- `067` / `068` 的 root close wording 与 machine truth 对齐
- 本轮改动保持 docs-only / read-only 边界

## Batch 4：archived closeout honesty sync

### Task 4.1 冻结 archived closeout 与 root stage 的区分

- [x] 在 `spec.md` 明确 `068` ~ `071` 的 carrier closeout 已归档，但 root `program status` 仍未 close
- [x] 在 `plan.md` 明确 `missing_artifact [frontend_contract_observations]` 仍是外部输入缺口
- [x] 保持 `076` 仍为 root honesty sync carrier，不新开 DAG 项

**完成标准**

- reviewer 能直接分辨 branch closeout truth 与 root machine truth

### Task 4.2 更新 P1 根级 rollout wording

- [x] 更新 P1 主线分段中的 `068` ~ `071` 当前口径
- [x] 更新排序总表中的 `068` ~ `071` 状态说明
- [x] 更新备注中的 `066` ~ `071`、`076` 与外部 artifact gap 说明

**完成标准**

- 根级 rollout wording 不再把 archived closeout 和 root `close` 混写

### Task 4.3 归档执行记录并重跑只读门禁

- [x] 在 `task-execution-log.md` 追加 latest honesty sync batch
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `uv run ai-sdlc program integrate --dry-run`
- [x] 运行 `git diff --check`

**完成标准**

- latest execution log 含 fresh command evidence
- 本轮改动保持 docs-only / read-only 边界
