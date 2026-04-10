# 任务分解：Frontend Evidence Class Manifest Mirror Writeback Contract Baseline

**编号**：`087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-087-001 ~ FR-087-011 / SC-087-001 ~ SC-087-004）

---

## 分批策略

```text
Batch 1: contract reconciliation
Batch 2: writeback contract baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `087` 只允许修改 `specs/087/...` 与本地 `project-state.yaml`
- `087` 不得实现 mirror writer、validator、status surfacing 或 close-stage resurfacing
- `087` 不得修改 `program-manifest.yaml`
- `087` 不得冻结具体 CLI 子命令名或 flags
- `087` 不得改写 `082` ~ `086` 已冻结的 prospective contract
- `087` 不得 retroactively 改义 `068` ~ `071`
- `087` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：contract reconciliation

### Task 1.1 对齐 authoring / validator / mirror / read-only surface 边界

- [x] 回读 `082`、`083`、`084`、`085`、`086`
- [x] 回读 `USER_GUIDE.zh-CN.md` 中 `program validate`、`status --json`、`workitem close-check` 的边界
- [x] 回读 `src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/workitem_cmd.py`、`src/ai_sdlc/core/program_service.py`

**完成标准**

- 能用单一 wording 解释为什么 `087` 必须冻结 owner family + write intent，而不先冻结具体子命令名

## Batch 2：writeback contract baseline freeze

### Task 2.1 新建 `087` formal docs

- [x] 在 `spec.md` 冻结 writer owner family、write intent 与 preconditions
- [x] 在 `spec.md` 冻结 allowed write modes 与 mutation scope
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- runtime maintainer 能直接回答 mirror 由谁写、写前要满足什么、能写 manifest 哪一块

### Task 2.2 冻结 refresh timing 与 forbidden write surfaces

- [x] 在 `spec.md` 冻结 stale / missing mirror 的 refresh timing
- [x] 在 `spec.md` 冻结 no-op / overwrite semantics
- [x] 在 `tasks.md` 明确 read-only surfaces 不得 opportunistic write

**完成标准**

- reviewer 能直接判断某个实现是否在 validate/status/close-check 路径偷写 manifest

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `087` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `087` 能独立说明 mirror writeback 的 owner、前置条件、写范围与禁止入口

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `86` 推进到 `87`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
