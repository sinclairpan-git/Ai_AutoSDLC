# 执行计划：Frontend Framework-Only Prospective Closure Contract Baseline

**功能编号**：`081-frontend-framework-only-prospective-closure-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only prospective contract

## 1. 目标与定位

`081` 的目标是把 `079` 的 policy split 继续前推成 future machine-gate contract，但保持 prospective-only。它冻结 future item 的 authoring semantics，不改变当前 runtime。

## 2. 范围

### 2.1 In Scope

- 创建 `081` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `81`
- 冻结 future framework-only frontend item 的 evidence class contract
- 冻结 future machine-gate 至少应识别的 authoring rule

### 2.2 Out Of Scope

- 修改 `program-manifest.yaml`
- 修改 `frontend-program-branch-rollout-plan.md`
- 修改 `src/` / `tests/` 或当前 `ai-sdlc` 输出
- retroactively 改义 `068` ~ `071`

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`
- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/plan.md`
- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/tasks.md`
- `specs/081-frontend-framework-only-prospective-closure-contract-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Contract Rules

### 4.1 Required declaration

future framework-only frontend item 必须声明 evidence class：

- `framework_capability`
- `consumer_adoption`

### 4.2 Split requirement

- 若一个 future requirement 同时需要 framework capability 与 consumer adoption evidence，必须拆成不同 work item
- 不允许继续使用单个 mixed item 承载两套 close semantics

### 4.3 Future runtime target

- future machine gate 需要识别 evidence class
- 未声明 evidence class 的 future framework-only frontend item 应被视为 authoring error
- `framework_capability` 与 `consumer_adoption` 必须走不同 gating path

### 4.4 Must not do

- 不规定本轮具体 metadata 字段名
- 不要求本轮实现 parser、validator 或 status migration
- 不改变任何既有 spec 的当前解释

## 5. 分阶段计划

### Phase 0：truth alignment

- 回读 `079`、`080`
- 确认当前矛盾已从 wording 层收敛到 future machine-gate contract 缺口

### Phase 1：prospective contract freeze

- 新建 `081` formal docs
- 写清 evidence class、close semantics、split rule 与 future machine-gate target

### Phase 2：verification and archive

- 运行 docs-only / read-only 验证
- 记录当前 runtime truth 保持不变
- 归档 commit

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program status`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/081-frontend-framework-only-prospective-closure-contract-baseline`

## 7. 回滚原则

- 如果 `081` 让人误以为当前 runtime 已识别 evidence class，必须回退
- 如果 `081` 让 `068` ~ `071` 看起来已被 retroactive 改义，必须回退
- 如果本轮误改 `frontend-program-branch-rollout-plan.md`、`program-manifest.yaml`、`src/` 或 `tests/`，必须回退
