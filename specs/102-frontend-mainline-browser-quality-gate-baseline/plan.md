# 执行计划：Frontend Mainline Browser Quality Gate Baseline

**功能编号**：`102-frontend-mainline-browser-quality-gate-baseline`  
**创建日期**：2026-04-13  
**状态**：docs-only browser gate contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`102` 的目标不是实现 browser probes，而是把 `101` 下游的真实浏览器质量门禁先冻结成正式合同：

- 冻结 browser gate 的 eligibility、execution context 与 scope binding；
- 冻结四类检查面的最低覆盖与输入真值；
- 冻结 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only` 的诚实分类；
- 冻结 `browser_quality_bundle` 与 `FrontendBrowserGateHandoff`；
- 保持 probe runtime、recheck/remediation replay 与 program aggregation 继续在后续切片独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `102` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `103`
- 在 `program-manifest.yaml` 为 `102` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 browser gate 输入、四类检查、bundle schema 与 `020` handoff
- 冻结 browser gate 的 fail-closed 与 advisory 语义

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 Playwright runner、视觉回归平台、自动修复或自动重跑
- 改写 `101` apply runtime truth、`071` visual/a11y foundation truth 或 `020` execute gate truth
- 直接产出 program 级最终 readiness `ready`
- 放宽 `one bundle == one active spec scope == one managed frontend target` 的绑定规则

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md`
- `specs/102-frontend-mainline-browser-quality-gate-baseline/plan.md`
- `specs/102-frontend-mainline-browser-quality-gate-baseline/tasks.md`
- `specs/102-frontend-mainline-browser-quality-gate-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Gate boundary

- `102` 只能在 `101.apply_succeeded_pending_browser_gate` 之后启动
- browser gate 只能消费 `073` provider/style truth 与 `071` visual/a11y 底线
- `102` 不得回到 apply runtime 补写动作，也不得在 gate 期新增 planner truth

### 4.2 Evidence and verdict boundary

- 四类检查都必须产出结构化结果，不得用自由文本吞并
- `evidence_missing`、`transient_run_failure`、`actual_quality_blocker` 与 `advisory_only` 必须继续分开
- `advisory_only` 不得被误判为 blocked
- `browser_quality_bundle` 必须保持单一 scope/target/source-linkage 绑定

### 4.3 Handoff boundary

- `FrontendBrowserGateHandoff` 只做 `020` consume surface
- `102` 不得直接产出 program 级最终 ready verdict
- `102` 不得把 remediation engine 或 auto-fix 伪装成 gate 的一部分

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `095` 对 browser gate、四类检查、失败分类与 bundle 的原始要求
- 回读 `101` 对 apply result / source linkage / browser gate handoff 的下游约束
- 回读 `071` 的 visual/a11y foundation 与 `020` 的 execute/recheck/remediation vocabulary

### Phase 1：formal browser gate freeze

- 在 `spec.md` 冻结 execution context、check result、bundle 与 handoff
- 在 `spec.md` 冻结四类检查的最低覆盖面与 failure honesty
- 在 `spec.md` 写清 bundle binding 与 `020` handoff 规则

### Phase 2：registry sync and verification

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/102-frontend-mainline-browser-quality-gate-baseline`

## 7. 回滚原则

- 如果 `102` 让人误以为 apply runtime、remediation engine 或 program aggregation 已在本切片实现，必须回退
- 如果 `102` 放宽了 `one bundle == one active spec scope == one managed frontend target`，必须回退
- 如果 `102` 把 advisory、缺证据或瞬时失败压成统一 blocker，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
