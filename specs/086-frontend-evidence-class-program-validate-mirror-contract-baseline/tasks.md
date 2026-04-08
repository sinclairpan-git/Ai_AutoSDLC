# 任务分解：Frontend Evidence Class Program Validate Mirror Contract Baseline

**编号**：`086-frontend-evidence-class-program-validate-mirror-contract-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-086-001 ~ FR-086-012 / SC-086-001 ~ SC-086-004）

---

## 分批策略

```text
Batch 1: contract reconciliation
Batch 2: mirror contract baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `086` 只允许修改 `specs/086/...` 与本地 `project-state.yaml`
- `086` 不得实现 manifest mirror、validator、writeback 或任一 CLI 输出
- `086` 不得给 `program-manifest.yaml` 实际加字段
- `086` 不得把 generation、writeback、status projection 或 close-stage resurfacing 并入同一轮
- `086` 不得改写 `082` ~ `085` 已冻结的 prospective contract
- `086` 不得 retroactively 改义 `068` ~ `071`
- `086` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：contract reconciliation

### Task 1.1 对齐 authoring / validator / diagnostics / first-cut contract

- [x] 回读 `082`、`083`、`084`、`085`
- [x] 回读当前 `program-manifest.yaml` 结构
- [x] 回读 `src/ai_sdlc/models/program.py` 与 `ProgramService.validate_manifest()`

**完成标准**

- 能用单一 wording 解释为什么 `086` 必须同时冻结 placement 与 drift semantics，但仍不提前实现 mirror

## Batch 2：mirror contract baseline freeze

### Task 2.1 新建 `086` formal docs

- [x] 在 `spec.md` 冻结 mirror 的唯一宿主、键名与 value shape
- [x] 在 `spec.md` 冻结 source-of-truth precedence
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- reviewer 能直接判断 future manifest mirror 应放在哪、叫什么、值是否复用 `frontend_evidence_class`

### Task 2.2 冻结 drift semantics 与 non-goals

- [x] 在 `spec.md` 冻结 `mirror_missing`、`mirror_invalid_value`、`mirror_stale`、`mirror_value_conflict`
- [x] 在 `spec.md` 写清 `mirror_stale` 与 `mirror_value_conflict` 的边界
- [x] 在 `tasks.md` 明确 generation、writeback、status、close-check 不属于本轮

**完成标准**

- future runtime maintainer 能直接用 `086` 作为 `program validate` mirror follow-up 的 bounded target

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `086` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `086` 能独立说明 mirror contract 的 placement、drift 语义与非目标

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `85` 推进到 `86`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
