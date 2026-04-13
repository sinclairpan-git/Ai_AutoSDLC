# 执行计划：Stage 0 Installed Runtime Update Advisor Baseline

**功能编号**：`093-stage0-installed-runtime-update-advisor-baseline`
**创建日期**：`2026-04-13`
**状态**：docs-only update advisor contract freeze
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`093` 的目标不是实现自升级器或联网刷新 runtime，而是把 installed runtime update advisor 的 contract 先冻结成正式计划输入：

- 冻结 installed runtime 判定、refresh authority 与 notify surface 的边界；
- 冻结 helper machine contract、cache freshness / backoff / dedupe 规则；
- 冻结 CLI、IDE、AI 三类表面对 notice class 的消费方式；
- 保持 update advisor 继续是 advisory-only，不滑成自动升级执行器。

## 2. 范围

### 2.1 In Scope

- 补齐 `093` 的 `plan.md`
- 把 update advisor contract 对齐为 docs-only / contract-freeze 口径
- 记录 `identity / evaluate / ack-notice` 的 plan-level 交付目标
- 为后续实现批次提供明确的边界、验证面与回滚原则

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 GitHub release 检查、helper 命令或缓存写入
- 增加自动升级、自更新或 install channel 改造
- 修改 `094` onboarding truth 或 `095` frontend mainline truth

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/093-stage0-installed-runtime-update-advisor-baseline/plan.md`

## 4. Contract Freeze Rules

### 4.1 Installed runtime boundary

- 只要不是可验证的 installed CLI runtime，就必须 fail-closed
- `uv run`、`python -m ai_sdlc`、editable/source runtime 与宿主内置 runtime 都不得进入在线检查
- fallback version string 不得被当作 installed runtime 证据

### 4.2 Refresh and cache boundary

- 只有 installed CLI runtime 或其 helper 拥有 refresh authority
- freshness、backoff、timeout、dedupe 都必须由 helper 统一裁决
- 检查失败、缓存损坏或网络异常都只能 advisory，不得阻断主流程

### 4.3 Surface boundary

- CLI 可以展示 actionable update notice，但 IDE / AI 只能消费 helper machine output
- IDE / AI 不得直接联网，也不得自行推断 notice eligibility
- `ack-notice` 的状态写回只能经由 helper 完成

## 5. 分阶段计划

### Phase 0：contract reconciliation

- 回读 `spec.md` 中 installed runtime、helper machine contract 与 notice class 约束
- 确认 `093` 仅为 Stage 0 supporting baseline，不越界到安装器或主线执行器

### Phase 1：machine contract freeze

- 明确 `identity / evaluate / ack-notice` 的目标字段面
- 明确 freshness、channel truth、reason code 与 notice eligibility 的计划边界

### Phase 2：verification and archive preparation

- 在执行日志中记录 plan 补齐事实
- 保持 `verify constraints`、`program validate` 与 close-check 无回归

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- specs/093-stage0-installed-runtime-update-advisor-baseline/plan.md`

## 7. 回滚原则

- 如果 `093` 让人误以为 update advisor 已实现自动升级，必须回退
- 如果 `093` 允许 IDE / AI 绕过 installed helper 直接联网，必须回退
- 如果本轮误改 `src/`、`tests/` 或上游 spec，必须回退
