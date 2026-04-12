# 执行计划：Frontend Mainline Posture Delivery Registry Baseline

**功能编号**：`097-frontend-mainline-posture-delivery-registry-baseline`  
**创建日期**：2026-04-12  
**状态**：docs-only posture / registry contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`097` 的目标不是实现旧工程扫描器、依赖安装器或 sidecar scaffold writer，而是把 `095` 七层前端主线在 `096.Host Readiness` 之后最自然缺失的一块正式合同单独冻结出来：

- 冻结 `frontend_posture_assessment` 的 authority、状态语义与 next-step boundary；
- 冻结 `sidecar_root_recommendation`、`will_not_touch` 与 root 级联动默认关闭的规则；
- 冻结 framework-controlled `frontend_delivery_registry` / `delivery_bundle_entry` 的 machine contract；
- 冻结 `enterprise-vue2` 与 `public-primevue` 作为 v1 官方 delivery entries 的正式口径；
- 保持 provider/style truth 继续单向引用既有 artifact reality，而不是复制出第二份 registry truth。

`097` 只负责 observe / plan 前的 truth freeze，不授权 mutate；任何安装、下载、写入、rollback、confirmation surface 仍属于 `095` 下游 action engine。

## 2. 范围

### 2.1 In Scope

- 创建 `097` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `98`
- 冻结 existing project `frontend_posture_assessment` 的 support status、evidence、reason code 与 no-touch 语义
- 冻结 `sidecar_root_recommendation` 的默认边界
- 冻结 `frontend_delivery_registry` 与 `delivery_bundle_entry` 的字段面
- 冻结 `provider_manifest_ref` / `resolved_style_support_ref` 的单一引用规则
- 冻结 `097` 与 `014 / 016 / 073 / 094 / 095 / 096` 的 truth order 与 downstream handoff

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 posture detector、registry materializer、action planner、installer、rollback runtime
- 自动 takeover unsupported existing frontend
- 冻结 arbitrary npm URL / git repo / private registry source
- 改写 `014` attachment truth、`073` solution truth、`094` onboarding truth 或 `096` host readiness truth
- 新增第二份 provider/style compatibility matrix

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md`
- `specs/097-frontend-mainline-posture-delivery-registry-baseline/plan.md`
- `specs/097-frontend-mainline-posture-delivery-registry-baseline/tasks.md`
- `specs/097-frontend-mainline-posture-delivery-registry-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Contract Freeze Rules

### 4.1 Truth order

- `097` 只能消费 `014`、`016`、`073`、`094`、`095`、`096` 与当前 provider artifact reality
- `097` 不得回写或重定义这些上游 truth
- downstream 只能消费 `frontend_posture_assessment`、`host_runtime_plan` 与 `delivery_bundle_entry`，不得再造 posture/registry truth

### 4.2 Posture and no-touch boundary

- `supported_existing_candidate` 只表示可以进入后续受控判断，不等于默认 takeover
- `unsupported_existing_frontend` 默认语义必须保持旧 frontend 不动
- `ambiguous_existing_frontend` 必须保留 evidence 不足语义
- `managed_frontend_already_attached` 必须继续服从 `014`
- `sidecar_root` 只能指向新建的受控子树；workspace、lockfile、CI、proxy、route integration 必须作为单独 action、默认关闭

### 4.3 Controlled registry boundary

- registry v1 只正式承认 `enterprise-vue2` 与 `public-primevue`
- 每个 `delivery_bundle_entry` 都必须绑定 runtime requirements、package sets、adapter sets、verification probes
- provider/style truth 只允许通过 `provider_manifest_ref` / `resolved_style_support_ref` 单向引用既有 artifacts
- `097` 不得伪装成“现已可执行安装”

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `014`、`016`、`073`、`094`、`095`、`096`
- 回读 `src/ai_sdlc/models/frontend_provider_profile.py`
- 回读 `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`
- 回读 `src/ai_sdlc/models/frontend_solution_confirmation.py`
- 回读相关 unit / integration tests，确认仓库 reality 已有哪些 provider/style/support truth，哪些 formal contract 仍缺席

### Phase 1：formal baseline freeze

- 在 `spec.md` 冻结 posture、sidecar、registry、delivery bundle 与 downstream handoff truth
- 在 `plan.md` 写清 docs-only 边界、truth order 与验证命令
- 在 `tasks.md` 把 research、formal freeze、project-state update 与 verification 固化成可审查 checklist

### Phase 2：verification and archive preparation

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- 确认本轮没有伪造 runtime 已实现

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/097-frontend-mainline-posture-delivery-registry-baseline`

## 7. 回滚原则

- 如果 `097` 让人误以为 posture detector / action engine 已经实现，必须回退
- 如果 `097` 允许 unsupported existing frontend 被默认 takeover，必须回退
- 如果 `097` 复制出第二份 provider/style compatibility truth，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
