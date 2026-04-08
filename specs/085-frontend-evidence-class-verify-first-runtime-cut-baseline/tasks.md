# 任务分解：Frontend Evidence Class Verify First Runtime Cut Baseline

**编号**：`085-frontend-evidence-class-verify-first-runtime-cut-baseline` | **日期**：2026-04-08  
**来源**：plan.md + spec.md（FR-085-001 ~ FR-085-010 / SC-085-001 ~ SC-085-004）

---

## 分批策略

```text
Batch 1: design reconciliation
Batch 2: first runtime cut baseline freeze
Batch 3: verification, project-state update, archive
```

---

## 执行护栏

- `085` 只允许修改 `specs/085/...` 与本地 `project-state.yaml`
- `085` 不得实现 helper、parser、validator 或任一 CLI 输出
- `085` 不得把 `program validate`、manifest mirror、status projection 或 close-stage resurfacing 提前并入同一轮
- `085` 不得改写 `081` ~ `084` 已冻结的 prospective contract
- `085` 不得 retroactively 改义 `068` ~ `071`
- `085` 不得修改 `src/`、`tests/`、`program-manifest.yaml`

---

## Batch 1：design reconciliation

### Task 1.1 对齐 frozen design 与已有 contract

- [x] 回读 `081`、`082`、`083`、`084`
- [x] 回读 `docs/superpowers/specs/2026-04-08-frontend-evidence-class-verify-first-runtime-cut-design.md`
- [x] 确认 first runtime cut 只属于 `verify constraints`

**完成标准**

- 能用单一 wording 解释为什么 first runtime cut 必须先和 mirror / status / observation gate 脱钩

## Batch 2：first runtime cut baseline freeze

### Task 2.1 新建 `085` formal docs

- [x] 在 `spec.md` 冻结 owning surface、canonical source 与 reader placement
- [x] 在 `spec.md` 冻结 separation from frontend contract gate
- [x] 在 `plan.md` 写清 docs-only 边界与验证命令

**完成标准**

- reviewer 能直接判断未来 first runtime cut 应落在哪个命令面和哪个代码入口附近

### Task 2.2 冻结 diagnostics 边界与 non-goals

- [x] 在 `spec.md` 冻结 allowed `error_kind`
- [x] 在 `spec.md` 冻结 minimum payload / severity boundary 的承接关系
- [x] 在 `tasks.md` 明确 mirror、status、close-stage 与 retroactive migration 不属于本轮

**完成标准**

- future runtime maintainer 能直接用 `085` 作为 first implementation cut 的 bounded target

## Batch 3：verification, project-state update, archive

### Task 3.1 初始化 `085` canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `085` 能独立说明 first runtime cut 的入点、出点与非目标

### Task 3.2 推进 project-state 序号

- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `84` 推进到 `85`
- [x] 不伪造当前 runtime truth 已变化

**完成标准**

- work item 序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program status`
- [x] 运行 `git diff --check`

**完成标准**

- 本轮 diff 保持 docs-only 边界且 verification fresh
