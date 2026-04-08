# 任务分解：Frontend Evidence Class Runtime Rollout Sequencing Baseline

**编号**：`090-frontend-evidence-class-runtime-rollout-sequencing-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-090-001 ~ FR-090-010 / SC-090-001 ~ SC-090-004）

---

## 分批策略

```text
Batch 1: contract chain reconciliation
Batch 2: rollout sequencing baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `090` 只允许修改 `specs/090/...` 与本地 `project-state.yaml`
- `090` 不得实现 verify/validate/writeback/status/close-check runtime
- `090` 不得修改 `program-manifest.yaml`
- `090` 不得冻结具体 PR 切分、工时、负责人或实现日期
- `090` 不得改写 `082` ~ `089` 已冻结的 prospective contract
- `090` 不得 retroactively 改义 `068` ~ `071`
- `090` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：contract chain reconciliation

### Task 1.1 对齐 authoring / mirror / writeback / status / close-stage 依赖链

- [x] 回读 `082`、`083`、`084`、`085`、`086`、`087`、`088`、`089`
- [x] 回读 `src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/close_check.py` 的现有边界
- [x] 提炼最小返工顺序与禁止抢跑规则

**完成标准**

- 能用单一 wording 解释为什么 runtime rollout 必须 owner-first、summary-last

## Batch 2：rollout sequencing baseline freeze

### Task 2.1 新建 `090` formal docs

- [x] 在 `spec.md` 冻结五阶段 rollout order
- [x] 在 `spec.md` 冻结 owner-first、writeback-before-drift、summary-last 护栏
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- maintainer 能直接回答 evidence-class 的 future runtime 应该先做什么、后做什么

### Task 2.2 冻结禁止抢跑规则

- [x] 在 `spec.md` 明确 `status` / `status --json` / `close-check` 不得早于 owner 落地
- [x] 在 `tasks.md` 明确 `program validate` drift 不得早于 mirror writeback path

**完成标准**

- reviewer 能直接判断某个 implementation cut 是否会导致后续返工

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `090` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `090` 能独立说明未来 runtime rollout 的顺序与依赖

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `89` 推进到 `90`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
