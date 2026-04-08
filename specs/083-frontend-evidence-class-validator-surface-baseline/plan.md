# 执行计划：Frontend Evidence Class Validator Surface Baseline

**功能编号**：`083-frontend-evidence-class-validator-surface-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective validator-surface contract

## 1. 目标与定位

`083` 的目标是把 `082` 中已经冻结的 authoring surface，继续推进成一条 future validator/reporting contract：以后如果 `frontend_evidence_class` 写错，哪个命令先发现、哪个命令检查 mirror、一类命令只能展示可见性，都需要在实现前先冻结。

## 2. 范围

### 2.1 In Scope

- 创建 `083` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `83`
- 冻结 `verify constraints` 作为 primary detection surface
- 冻结 `program validate` 作为 future manifest mirror consistency surface
- 冻结 `program status` / `status --json` / `workitem close-check` 的职责边界

### 2.2 Out Of Scope

- 修改任意 `src/` / `tests/` 实现
- 给 `program-manifest.yaml` 或模板新增字段
- retroactively 改义 `068` ~ `071`
- 改写 `082` 的 key/value authoring contract
- 新增 runtime stage 或 CLI 子命令

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/083-frontend-evidence-class-validator-surface-baseline/spec.md`
- `specs/083-frontend-evidence-class-validator-surface-baseline/plan.md`
- `specs/083-frontend-evidence-class-validator-surface-baseline/tasks.md`
- `specs/083-frontend-evidence-class-validator-surface-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Contract Rules

### 4.1 Primary detection

- malformed `frontend_evidence_class` 的首次定责由 `uv run ai-sdlc verify constraints` 承担
- 该命令面代表 future canonical authoring failure truth

### 4.2 Mirror consistency

- future 若引入 manifest mirror，镜像一致性检查由 `uv run ai-sdlc program validate` 承担
- `program validate` 不重新定义 key、allowed values 或 source-of-truth priority

### 4.3 Read-only visibility

- `uv run ai-sdlc program status`
- `uv run ai-sdlc status --json`

以上两类命令只负责 bounded summary / visibility，不负责 first-detection

### 4.4 Late-stage resurfacing

- `uv run ai-sdlc workitem close-check` 可在 close-stage 复现同一 malformed authoring
- 但它只承担晚期复检责任，不是 primary detection surface

## 5. 分阶段计划

### Phase 0：surface mapping

- 回读 `082`
- 回读用户指南与 program 语义文档中现有命令面
- 确认 `verify constraints`、`program validate`、`program status`、`status --json`、`workitem close-check` 的职责边界

### Phase 1：validator surface freeze

- 新建 `083` formal docs
- 写清 primary detection、mirror consistency、late-stage resurfacing 与 bounded visibility 的分工
- 写清多 surface 并存时的 precedence

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变更
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/083-frontend-evidence-class-validator-surface-baseline`

## 7. 回滚原则

- 如果 `083` 让人误以为当前 CLI 已经实现 evidence-class validator surface，必须回退
- 如果 `083` 把 `program status` 或 `status --json` 写成 primary detection surface，必须回退
- 如果 `083` 让 `program validate` 抢走 `082` 的 authoring truth 角色，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
