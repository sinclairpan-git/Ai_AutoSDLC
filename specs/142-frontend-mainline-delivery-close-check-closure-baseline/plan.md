# 实施计划：Frontend Mainline Delivery Close-Check Closure Baseline

**功能编号**：`142-frontend-mainline-delivery-close-check-closure-baseline`
**日期**：2026-04-14
**规格**：`specs/142-frontend-mainline-delivery-close-check-closure-baseline/spec.md`

## 概述

`142` 的起点是一个已经被 root truth 清洗过的 blocker 面：`frontend-mainline-delivery` 当前是纯 `blocked`，不再混杂 root manifest 漏项。这个 tranche 的目标不是再解释 blocker，而是把 blocker universe、执行顺序、验证面和最终 close 口径全部固定下来，并以此驱动后续实现。

推荐实现顺序是：先刷新 truth audit 并固化 `blocker-execution-map.yaml`，再按两条子链推进 child work，最后用同一条 `program truth audit` 验证 release capability 是否真的收敛为 `ready`。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：`program-manifest.yaml`、`program truth audit`、`workitem close-check`、`workitem truth-check`、`verify constraints`、既有 `095/096/.../126` specs、`specs/142-frontend-mainline-delivery-close-check-closure-baseline/blocker-execution-map.yaml`  
**测试**：focused close-check / truth-audit / integration verification  
**目标平台**：`frontend-mainline-delivery` release capability  
**约束**：

- `142` 自身不是新的 release carrier
- blocker universe 只能来自执行时重新获取的 `program truth audit` 与 `required_evidence.close_check_refs`
- `blocker-execution-map.yaml` 的 canonical 路径固定为 `specs/142-frontend-mainline-delivery-close-check-closure-baseline/blocker-execution-map.yaml`
- `blocker-execution-map.yaml` 必须 machine-readable，且每行只能引用现有 machine-verifiable surface
- 不允许用 docs-only wording 覆盖 `capability_closure_audit:capability_open`

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值 | blocker universe 只认最新 truth audit + root manifest 的 close_check_refs |
| 最小改动面 | 先冻结 blocker map 与执行顺序，再分批处理 child specs |
| 流程诚实 | `142` 只有在 `frontend-mainline-delivery.audit_state=ready` 时才能关闭 |
| 小白可执行 | 对每个 blocker_ref 提供可机读的 carrier / command / evidence 映射 |

## 实施批次

### Phase 0：Formal freeze 与对抗评审

1. 起草 `spec.md`
2. 用 Avicenna 与 Russell 做两轮对抗评审
3. 收口 blocker universe、machine-readable map、子链顺序与 close 条件
4. 再进入 `plan -> tasks -> execute`

### Phase 1：Refresh truth audit and freeze blocker universe

1. 重新运行 `uv run ai-sdlc program truth audit`
2. 从 `release_capabilities[].blocking_refs` 与 `required_evidence.close_check_refs` 提取当前 blocker universe
3. 在 `specs/142-frontend-mainline-delivery-close-check-closure-baseline/blocker-execution-map.yaml` 生成 blocker map
4. 对 universe 做三类校验：
   - 是否与最新 truth audit 对齐
   - 是否覆盖所有 release close_check refs
   - 是否每行都绑定到现有 machine-verifiable surface
5. 固定最小 schema：
   - `blocker_ref: str`
   - `carrier_spec: str`
   - `execution_batch: str`
   - `verification_command_or_surface: list[str]`
   - `expected_close_evidence: list[str]`
   - `prerequisites: list[str]`
6. 为该 map 增加对应 pytest 校验，至少断言：
   - 每个 `blocker_ref` 都存在于最新 `release_capabilities[].blocking_refs` 或 `required_evidence.close_check_refs`
   - 每个 `carrier_spec` 都存在于根 manifest / `specs/*`
   - 每个 `verification_command_or_surface` 都属于允许的验证面集合
   - 不存在 orphan blocker、重复 blocker、空 evidence
7. 该 pytest 必须进入默认 pytest 收集路径，并作为 `142` 与后续 child batch 的最终 tests evidence

### Phase 2：Product/host/registry/apply chain

1. 先处理 `095 -> 096 -> 098 -> 099 -> 100 -> 101 -> 123 -> 124`
2. 每清掉一个或一组 blocker，都要回跑对应 `workitem close-check` / `truth-check`
3. 对 `124` 达成后，作为 browser gate 子链的跨链 prerequisite
4. 任何批次结束时，都要回看最新 `program truth audit` 是否仍保留同一 blocker ref

### Phase 3：Browser gate / recheck remediation chain

1. 按 `102 -> 103 -> 104 -> 105 -> 125 -> 126` 推进
2. 将 `124` 作为 `125` 的跨链 prerequisite 明确纳入 blocker map
3. browser gate 子链的每步都要绑定可机器验证的 close evidence
4. 不得用人工 closure wording 代替 browser gate runtime close

### Phase 4：Capability closure audit reconciliation

1. 在两条子链的 close_check blockers 清零后，复核 `capability_closure_audit:capability_open`
2. 用 machine-verifiable evidence 驱动 capability closure audit 收敛
3. 重新运行 `program truth audit`
4. 仅当 `frontend-mainline-delivery.audit_state=ready` 时，才允许 `142` 关闭

## 风险与回退

- **风险 1：blocker map 变成手写清单**
  - 回避：使用固定路径的 machine-readable `blocker-execution-map.yaml`，并要求每行都引用现有验证面
- **风险 2：按 spec 名字修补，但 truth audit blocker 不动**
  - 回避：每个批次结束都回跑最新 truth audit，对 blocker ref 是否消失做验证
- **风险 3：子链顺序过粗，导致跨链前置条件遗漏**
  - 回避：在 blocker map 中显式标出 `124 -> 125` 这类跨链 prerequisite
- **风险 4：`capability_closure_audit` 被 wording 假关闭**
  - 回避：将 closure audit reconciliation 放到最后，并要求它由 machine evidence 驱动

## 验证策略

最小验收命令集：

- `uv run ai-sdlc program truth audit`
- `uv run pytest <blocker-execution-map validation test> -q`
- `uv run ai-sdlc workitem truth-check --wi specs/<carrier-spec>`
- `uv run ai-sdlc workitem close-check --wi specs/<carrier-spec>`
- `uv run ai-sdlc verify constraints`
- `uv run pytest <targeted close-check / frontend-mainline suites>`

上述验证不是参考项，而是 `142` 的强制 close evidence；缺任一项，`142` 不得宣称完成。
其中 `blocker-execution-map` pytest 还必须进入默认 pytest 收集路径，避免被 CI / 最终测试面绕过。

## 退出条件

1. `142` 的 spec/plan 完成两轮对抗评审并收敛
2. `blocker-execution-map.yaml` 已建立并与最新 truth audit / close_check_refs 对齐
3. 两条子链及跨链 prerequisite 已有明确 tasks
4. `142` 的关闭条件被正式固定为：`frontend-mainline-delivery.audit_state=ready`
