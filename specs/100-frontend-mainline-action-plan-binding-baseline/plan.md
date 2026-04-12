# 执行计划：Frontend Mainline Action Plan Binding Baseline

**功能编号**：`100-frontend-mainline-action-plan-binding-baseline`  
**创建日期**：2026-04-12  
**状态**：docs-only managed action engine contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`100` 的目标不是实现 apply runtime，而是把 `095` 里的 `Managed Action Engine` 先拆出第一层正式合同：

- 冻结 `frontend_action_plan` 的 binding inputs、truth order 与动作分类；
- 冻结 `required / optional`、`will_* / will_not_touch` 与 sidecar/no-touch 规则；
- 冻结 `delivery_execution_confirmation_surface` 的最小展示面与二次确认边界；
- 冻结 `delivery_action_ledger` 的 action-id continuity、rollback、retry 与 partial-progress 语义；
- 保持真实执行器与 browser quality gate 继续在后续切片独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `100` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `101`
- 在 `program-manifest.yaml` 为 `100` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 activation/solution/runtime/posture/bundle/local evidence 到 action plan 的绑定顺序
- 冻结确认页、风险项、二次确认、ledger continuity 与 fail-closed blocked 规则

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 apply runtime、installer、writer、rollback executor 或 browser gate
- 改写 `073`、`096`、`098`、`099` 已冻结 truth
- 新增 takeover old frontend 的默认路径
- 新增 provider/style/registry/browser probe

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/100-frontend-mainline-action-plan-binding-baseline/spec.md`
- `specs/100-frontend-mainline-action-plan-binding-baseline/plan.md`
- `specs/100-frontend-mainline-action-plan-binding-baseline/tasks.md`
- `specs/100-frontend-mainline-action-plan-binding-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Truth order

- `100` 只能消费 `010`、`014`、`073`、`094`、`095`、`096`、`098`、`099`
- `100` 不得回写 activation truth、solution truth、runtime truth、posture truth 或 registry truth
- downstream executor 与 browser gate 只能消费 `100` 输出，不得反向改写 action plan

### 4.2 Plan boundary

- `frontend_action_plan` 只能在 `solution_snapshot confirmed` 之后生成
- `required / optional` 与 `will_* / will_not_touch` 必须是 planning 阶段显式产物，不能留给执行期猜测
- `workspace/lockfile/CI/proxy/route` 集成必须保持独立 optional action
- `unsupported_existing_frontend_sidecar_only` 与 v1 `supported_existing_candidate` 都必须保持旧工程 no-touch

### 4.3 Confirmation and ledger boundary

- 没有 `delivery_execution_confirmation_surface` 就不得开始 mutate
- `delivery_action_ledger` 只记录真实执行动作，不得在 planning 阶段预填成功结果
- 含 `non_rollbackable_effect` 或 `manual_recovery_required` 的 action 必须要求二次确认
- `100` 不得声称 apply runtime 或 browser gate 已在本切片实现

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `095` 中 `Managed Action Engine` 的原始要求与建议模型
- 回读 `096 / 098 / 099` 的 handoff 边界，确认不重复定义 runtime、posture、bundle truth
- 对齐 manifest 末段与 project-state 当前序号

### Phase 1：formal action-plan-binding freeze

- 在 `spec.md` 冻结 ActionBindingContext、LocalDetectionEvidence、FrontendActionPlan、ConfirmationSurface、Ledger
- 在 `spec.md` 冻结 truth order、requiredness policy、will-surface 与 blocked semantics
- 在 `spec.md` 写清 executor/browser gate 的下游边界

### Phase 2：registry sync and verification

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/100-frontend-mainline-action-plan-binding-baseline`

## 7. 回滚原则

- 如果 `100` 让人误以为 apply runtime、rollback executor 或 browser gate 已经实现，必须回退
- 如果 `100` 重新发明第二份 runtime/package/provider truth，必须回退
- 如果 `100` 允许 old frontend takeover 在没有单独 formal slice 的情况下默认发生，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
