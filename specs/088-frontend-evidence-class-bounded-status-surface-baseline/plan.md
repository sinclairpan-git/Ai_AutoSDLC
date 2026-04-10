# 执行计划：Frontend Evidence Class Bounded Status Surface Baseline

**功能编号**：`088-frontend-evidence-class-bounded-status-surface-baseline`  
**创建日期**：2026-04-09  
**状态**：docs-only prospective status-surface contract

## 1. 目标与定位

`088` 的目标是把 `frontend_evidence_class` 的 future status surfacing 压到 bounded summary 面：明确 `program status` 只负责 program-scoped compact summary，`status --json` 只负责 active-work-item bounded summary，二者都不得代替 `verify constraints` / `program validate` 的 owning diagnostics。

## 2. 范围

### 2.1 In Scope

- 创建 `088` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `88`
- 冻结 `program status` 与 `status --json` 各自的 summary 粒度
- 冻结 status surface 可暴露的最小字段与禁止暴露的内容
- 冻结 status surface 的 non-adjudication 边界

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 冻结具体 JSON key 名、table column 名或 CLI 文案
- 修改 `verify constraints` / `program validate` / `workitem close-check`
- 让 `status --json` 变成 cross-program diagnostics API
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`
- `specs/088-frontend-evidence-class-bounded-status-surface-baseline/plan.md`
- `specs/088-frontend-evidence-class-bounded-status-surface-baseline/tasks.md`
- `specs/088-frontend-evidence-class-bounded-status-surface-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Status Surface Rules

### 4.1 `program status`

- 只做 program-scoped compact summary
- 最多暴露 spec 级 blocker presence、problem family、单条 bounded hint
- 不得输出 full diagnostic payload

### 4.2 `status --json`

- 只做 active-work-item bounded summary
- 最多暴露 blocker presence、problem family、owning surface
- 不得输出 cross-program spec 列表或 per-spec diagnostics 数组

### 4.3 Source and non-adjudication

- status surface 只能消费 upstream derived truth
- status surface 不得重新解析 canonical source
- status surface 不得重裁 severity、不得 auto-heal mirror

## 5. 分阶段计划

### Phase 0：surface reconciliation

- 回读 `083` ~ `087`
- 回读 `USER_GUIDE.zh-CN.md` 中 `status --json` / `program status` 的只读边界
- 回读 `src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/cli/commands.py` 与 `telemetry/readiness.py`

### Phase 1：status contract baseline freeze

- 新建 `088` formal docs
- 写清两类 status surface 的粒度边界
- 写清 allowed bounded fields 与 forbidden payload

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 仍未变化
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/088-frontend-evidence-class-bounded-status-surface-baseline`

## 7. 回滚原则

- 如果 `088` 让人误以为 status surface 可以替代 owning diagnostics，必须回退
- 如果 `088` 允许 `status --json` 膨胀成 cross-program diagnostics dump，必须回退
- 如果 `088` 允许 status surface 暴露 full payload 或 remediation narrative，必须回退
- 如果本轮误改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec，必须回退
