# 执行计划：Stage 0 Init Dual-Path Project Onboarding Baseline

**功能编号**：`094-stage0-init-dual-path-project-onboarding-baseline`
**创建日期**：`2026-04-13`
**状态**：docs-only onboarding contract freeze
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`094` 的目标不是实现新的 init executor，而是把 Stage 0 dual-path onboarding 的正式计划输入补齐：

- 冻结 `greenfield / existing` 双路径的入口判定与 truth order；
- 冻结 Stage 0 operator surface、项目基线产物与 next-step handoff；
- 冻结 unsupported / ambiguous / no-frontend 等场景在 onboarding 层的边界；
- 保持 `094` 只定义 onboarding truth，不提前吞并 `095` 的 frontend mainline 主线。

## 2. 范围

### 2.1 In Scope

- 补齐 `094` 的 `plan.md`
- 把 dual-path onboarding contract 对齐为 docs-only / contract-freeze 口径
- 记录 Stage 0 输入、输出、handoff 与 no-touch 边界
- 为后续实现批次提供明确的变更面与验证面

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现实际 init 交互、项目脚手架写入或自动接管既有前端
- 改写 `093` update advisor truth
- 改写 `095` frontend mainline product delivery truth

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/094-stage0-init-dual-path-project-onboarding-baseline/plan.md`

## 4. Contract Freeze Rules

### 4.1 Dual-path boundary

- `greenfield` 与 `existing` 必须在 Stage 0 明确分流
- onboarding 只建立 baseline 与 handoff，不直接接管旧前端或进入写入型 delivery
- ambiguous 或 unsupported existing frontend 只能诚实保留，并交给后续主线显式处理

### 4.2 Surface and output boundary

- `094` 只冻结 Stage 0 operator surface 与产物，不定义后续 mutate 权
- onboarding 结果必须可被 `095` 与其下游 implementable slice 单向消费
- 不允许在 onboarding 阶段偷带 provider / package / scaffold 写入

### 4.3 No-touch boundary

- 对 existing project 的旧 frontend、manifest、lockfile 与 root 级联动必须保持显式 no-touch / opt-in 语义
- 不得把 sidecar、新托管前端或 root integration 伪装成默认 happy path

## 5. 分阶段计划

### Phase 0：contract reconciliation

- 回读 `spec.md` 中 dual-path、existing posture 与 downstream handoff 约束
- 确认 `094` 继续只作为 Stage 0 baseline，不越界到 frontend mainline 执行

### Phase 1：onboarding boundary freeze

- 明确 dual-path 入口、产物与 handoff 面
- 明确 existing project no-touch、sidecar option 与 ambiguous fail-closed 边界

### Phase 2：verification and archive preparation

- 在执行日志中记录 plan 补齐事实
- 保持 `verify constraints`、`program validate` 与 close-check 无回归

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- specs/094-stage0-init-dual-path-project-onboarding-baseline/plan.md`

## 7. 回滚原则

- 如果 `094` 让人误以为 Stage 0 已默认接管 existing frontend，必须回退
- 如果 `094` 把 onboarding 扩成写入型 delivery 或 provider install，必须回退
- 如果本轮误改 `src/`、`tests/` 或上游 spec，必须回退
