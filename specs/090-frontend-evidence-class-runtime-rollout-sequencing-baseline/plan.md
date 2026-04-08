# 实施计划：Frontend Evidence Class Runtime Rollout Sequencing Baseline

**编号**：`090-frontend-evidence-class-runtime-rollout-sequencing-baseline`  
**日期**：2026-04-09  
**状态**：已冻结（formal baseline）

## 1. 目标

把 `frontend_evidence_class` 的 future runtime rollout 顺序冻结成一条可执行、少返工的 prospective contract：明确 verify first cut、mirror carrier/writeback、validate drift、status surfacing 与 close-stage resurfacing 应按什么依赖顺序落地，同时保持当前 runtime truth 不变。

## 2. 范围与非目标

### 2.1 覆盖范围

- 新建 `090` formal docs：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 推进 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 到 `90`
- 冻结 future runtime rollout 的 phase 顺序与依赖前置
- 冻结 owner-first、writeback-before-drift、summary-last 三条 rollout 护栏

### 2.2 明确不做

- 不修改 `src/`、`tests/`、`program-manifest.yaml`
- 不定义具体实现 PR、工时、负责人、日期
- 不新增 runtime flags、状态字段或 CLI 文案
- 不 retroactively 改写 `068` ~ `071` 或任何历史 item 的现有 truth

## 3. 分批执行

### Phase 1：contract chain reconciliation

- 回读 `082` ~ `089` 已冻结 contract
- 对齐 authoring、mirror、writeback、status、close-check 各自的 owner 与 non-goals
- 提炼最小返工顺序与禁止抢跑规则

### Phase 2：runtime rollout sequence freeze

- 在 `spec.md` 冻结五阶段 rollout order
- 在 `spec.md` 冻结 owner-first、writeback-before-drift、summary-last 护栏
- 在 `plan.md` / `tasks.md` 写清 docs-only 边界与验证命令

### Phase 3：verification and archive

- 运行 `uv run ai-sdlc verify constraints`
- 运行 `uv run ai-sdlc program status`
- 运行 `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline`
- 提交 docs-only baseline，不伪造 runtime 已开始实现

## 4. 验证策略

- **约束验证**：`uv run ai-sdlc verify constraints`
- **程序状态核对**：`uv run ai-sdlc program status`
- **diff 完整性**：`git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline`

## 5. 完成定义

- `090` formal docs 能独立说明 future runtime implementation 的推荐顺序
- reviewer 能据此判断 summary / close-stage surface 是否抢跑
- maintainer 能据此判断 drift enforcement 是否早于 writeback path
- 本轮 diff 保持 docs-only 边界，且 `project-state.yaml` 序号推进到 `90`
