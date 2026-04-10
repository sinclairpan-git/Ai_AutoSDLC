# 执行计划：Frontend Evidence Class Program Validate Mirror Contract Baseline

**功能编号**：`086-frontend-evidence-class-program-validate-mirror-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective mirror contract

## 1. 目标与定位

`086` 的目标是把 `frontend_evidence_class` 的 future manifest mirror follow-up 正式冻结成 baseline：明确 mirror 在 `program-manifest.yaml` 中的唯一 placement、允许值、source-of-truth precedence，以及 `program validate` 上的 drift semantics。它不实现 mirror，不改 manifest，不定义 writeback，也不推进 status surface。

## 2. 范围

### 2.1 In Scope

- 创建 `086` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `86`
- 冻结 mirror 的 canonical placement 与 key/value shape
- 冻结 `program validate` 的 drift problem family 与 `error_kind` 语义
- 冻结 non-goals，防止 generation / writeback / status / close-check 抢跑

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 真正给 `program-manifest.yaml` 加字段
- 设计 mirror 自动生成、回写责任或同步时机
- 修改 `program status`、`status --json`、`workitem close-check`
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`
- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/plan.md`
- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/tasks.md`
- `specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Mirror Contract Rules

### 4.1 Canonical placement

- mirror 唯一宿主是 `program-manifest.yaml` 的 `specs[]` 节点
- canonical 键名固定为 `frontend_evidence_class`
- future model 扩展优先落在 `ProgramSpecRef`

### 4.2 Value and precedence

- mirror value 只允许 `framework_capability` / `consumer_adoption`
- correctness source 仍然只认 `spec.md` footer
- manifest mirror 只是 `program validate` 消费的 derived mirror

### 4.3 Drift semantics

- `mirror_missing`：spec footer 有值，manifest canonical mirror 缺失
- `mirror_invalid_value`：manifest canonical mirror 值为空或非法
- `mirror_stale`：manifest canonical mirror 值合法，但与 spec footer 当前值不一致
- `mirror_value_conflict`：manifest 出现并行 alias / competing mirror truth

### 4.4 Non-goals

- 不冻结 mirror 生成命令
- 不冻结 writeback 时机
- 不冻结 status summary
- 不冻结 close-stage resurfacing

## 5. 分阶段计划

### Phase 0：contract reconciliation

- 回读 `082` ~ `085`
- 回读当前 `program-manifest.yaml` 与 `ProgramSpecRef`
- 确认本轮只是在 formal baseline 中冻结 placement + drift semantics

### Phase 1：mirror contract baseline freeze

- 新建 `086` formal docs
- 写清 placement、key/value shape、source precedence
- 写清 drift `error_kind` 语义与 non-goals

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline`

## 7. 回滚原则

- 如果 `086` 让人误以为 manifest mirror 已经实现，必须回退
- 如果 `086` 允许顶层 mirror map 或 manifest-only alias，必须回退
- 如果 `086` 把 generation/writeback/status/close-check 偷带进同一轮，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
