# 任务分解：Frontend Evidence Class Runtime Reality Sync Baseline

**编号**：`092-frontend-evidence-class-runtime-reality-sync-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-092-001 ~ FR-092-006 / SC-092-001 ~ SC-092-004）

---

## 分批策略

```text
Batch 1: runtime reality reconciliation
Batch 2: fresh verification and archive
```

---

## 执行护栏

- `092` 只允许修改 `specs/092/...` 与本地 `project-state.yaml`
- `092` 不得新增 runtime behavior、diagnostics family 或 CLI surface
- `092` 不得修改 `src/`、`tests/`、`program-manifest.yaml`
- `092` 不得把 honesty sync 伪装成 implementation baseline
- `092` 不得 retroactively 改义 `068` ~ `071`

---

## Batch 1：runtime reality reconciliation

### Task 1.1 对齐 contract 与当前 runtime 主链

- [x] 回读 `085`、`086`、`087`、`088`、`089`、`090`、`091`
- [x] 回读 `src/ai_sdlc/core/verify_constraints.py`
- [x] 回读 `src/ai_sdlc/core/program_service.py`
- [x] 回读 `src/ai_sdlc/cli/program_cmd.py`
- [x] 回读 `src/ai_sdlc/core/close_check.py`

**完成标准**

- 能用单一 wording 解释 verify / validate / sync / status / close-check 哪些已经是 current reality

### Task 1.2 新建 `092` honesty-sync docs

- [x] 在 `spec.md` 记录当前 runtime reality 已覆盖的五类 surface
- [x] 在 `spec.md` 写清 `086`、`087`、`088`、`090` 的 historical docs-only 身份
- [x] 在 `plan.md` 与 `tasks.md` 锁定 docs-only 写面

**完成标准**

- reviewer 能直接判断后续工作是补实现还是补 truth sync

## Batch 2：fresh verification and archive

### Task 2.1 初始化 execution log 与 project-state

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `91` 推进到 `92`

**完成标准**

- work item 序号与 `092` 对齐，execution log 能独立说明本轮目标

### Task 2.2 运行定向验证

- [x] 运行 `uv run pytest tests/unit/test_verify_constraints.py -q`
- [x] 运行 `uv run pytest tests/integration/test_cli_program.py -q`
- [x] 运行 `uv run pytest tests/integration/test_cli_status.py -q`
- [x] 运行 `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check`

**完成标准**

- fresh verification 证明当前 runtime 主链仍然可执行
