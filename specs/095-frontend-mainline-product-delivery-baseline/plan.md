# 执行计划：Frontend Mainline Product Delivery Baseline

**功能编号**：`095-frontend-mainline-product-delivery-baseline`
**创建日期**：`2026-04-13`
**状态**：docs-only mainline contract freeze
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`095` 的目标不是立即实现整条前端主线，而是把 frontend mainline product delivery 的母规格计划面补齐：

- 冻结七层主线的职责顺序与 truth order；
- 冻结 observe / plan / mutate 三相位边界；
- 冻结 host runtime self-healing、posture assessment、solution freeze、action planning、apply runtime 与 browser quality gate 的 handoff 关系；
- 保持 `095` 继续作为总线母规格，不把 `096+` implementable slice 重新吞回本工单。

## 2. 范围

### 2.1 In Scope

- 补齐 `095` 的 `plan.md`
- 把 frontend mainline contract 对齐为 docs-only / contract-freeze 口径
- 记录七层主线、关键边界、支持矩阵与验证策略
- 为 `096+` implementable slice 提供明确的上游计划输入

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 host runtime manager、posture detector、delivery registry、action plan、apply runtime 或 browser gate
- 改写 `073` solution truth、`094` onboarding truth、`020` execute gate truth
- 放宽受控支持矩阵或引入 React runtime 接管

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/095-frontend-mainline-product-delivery-baseline/plan.md`

## 4. Contract Freeze Rules

### 4.1 Mainline layering

- 七层主线必须保持 `Host Readiness -> Stage 0 Onboarding -> Frontend Posture Assessment -> Solution Freeze -> Managed Delivery Planning -> Managed Delivery Apply -> Browser Quality Gate`
- 顺序不可逆，不得先写代码后补确认，也不得先安装后解释
- `095` 只串联上游 truth，不重写 `094`、`073`、`014`、`020`

### 4.2 Phase boundary

- `observe` 只允许识别与评估
- `plan` 只允许生成推荐与 action plan
- `mutate` 只允许发生在 `delivery_execution_confirmation_surface` 之后
- 所有自动动作都必须可审计、可回滚或可清理、可重试

### 4.3 Scope and support matrix

- v1 支持矩阵固定为 `vue2 + enterprise-vue2` 与 `vue3 + public-primevue`
- unsupported existing frontend 默认保持 no-touch，并只提供 sidecar / continue-without-managed-frontend 路径
- browser quality gate 继续作为 mandatory downstream gate，不被降级成可选检查

## 5. 分阶段计划

### Phase 0：mainline reconciliation

- 回读 `spec.md` 中主线七层、主线顺序、受控支持矩阵与 browser gate 约束
- 确认 `095` 继续作为母规格，不越界到 `096+` 的实现切片

### Phase 1：contract freeze

- 明确七层主线职责、phase boundary 与 user-facing confirmation surface 分工
- 明确 no-touch、sidecar、activation gate、rollback/retry 与 browser evidence handoff 边界

### Phase 2：verification and archive preparation

- 在执行日志中记录 plan 补齐事实
- 保持 `verify constraints`、`program validate` 与 close-check 无回归

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- specs/095-frontend-mainline-product-delivery-baseline/plan.md`

## 7. 回滚原则

- 如果 `095` 让人误以为七层主线已在本工单全部实现，必须回退
- 如果 `095` 把 unsupported existing frontend 默认接管或隐式迁移，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
