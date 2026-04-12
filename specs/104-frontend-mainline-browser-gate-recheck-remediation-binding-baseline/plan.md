# 执行计划：Frontend Mainline Browser Gate Recheck Remediation Binding Baseline

**功能编号**：`104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline`  
**创建日期**：2026-04-13  
**状态**：docs-only result-binding contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`104` 的目标不是实现 replay runtime、auto-fix 或 `020` CLI wiring，而是把 `102/103` 下游的 browser gate 结果绑定层先冻结成正式合同：

- 冻结 `browser_quality_bundle + FrontendBrowserGateHandoff -> BrowserGateExecuteHandoffDecision`；
- 冻结 `incomplete / blocked / passed_with_advisories / passed` 到 `020` execute vocabulary 的映射；
- 冻结 `ProgramFrontendRecheckBinding`、`ProgramFrontendRemediationBinding` 与 `BrowserGateReplayRequest`；
- 冻结 stale bundle、scope mismatch、source linkage 缺失与 result inconsistency 的 fail-closed 规则；
- 保持 replay orchestration、auto-fix 与 program aggregation 继续在后续切片独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `104` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `105`
- 在 `program-manifest.yaml` 为 `104` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 execute handoff decision、recheck binding、remediation binding 与 replay request
- 冻结 result inconsistency / linkage invalid 的 fail-closed 规则

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 replay runtime、auto-fix engine、CLI wiring 或 program aggregation
- 改写 `102` 的 gate contract、`103` 的 probe runtime 或 `020` 的 execute baseline
- 把 advisory 升级为 blocker，或把 remediation hint 伪装成已执行修复

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`
- `specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/plan.md`
- `specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/tasks.md`
- `specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Binding boundary

- `104` 只能在 `102.browser_quality_bundle` 与 `FrontendBrowserGateHandoff` 之后启动
- `104` 只能把 browser gate 结果绑定到 `020` execute vocabulary，不得重写 `102/103` 上游 truth
- `104` 不得把 bounded replay request 扩张成自动重跑 loop

### 4.2 Honesty boundary

- `evidence_missing` / `transient_run_failure` 必须维持 recheck 语义
- evidence-backed `actual_quality_blocker` 必须维持 remediation 语义
- stale bundle、scope mismatch 与 result inconsistency 必须 fail-closed 为 `blocked`

### 4.3 Scope boundary

- `104` 只 formalize result binding 与 handoff decision
- `104` 不得实现 auto-fix、runtime replay、program aggregation 或 `020` CLI wiring
- `104` 不得修改 `src/`、`tests/` 或声称 binding runtime 已落地

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `102` 对 bundle、handoff 与 failure taxonomy 的正式要求
- 回读 `103` 对 runtime evidence lineage 与 non-goals 的直接约束
- 回读 `020` 对 execute state、recheck handoff 与 remediation hint 的 vocabulary 底线

### Phase 1：formal result-binding freeze

- 在 `spec.md` 冻结 `BrowserGateExecuteHandoffDecision`、`ProgramFrontendRecheckBinding`、`ProgramFrontendRemediationBinding` 与 `BrowserGateReplayRequest`
- 在 `spec.md` 冻结 bundle-status 到 execute-state 的主映射与 fail-closed 条件
- 在 `spec.md` 写清 bounded replay request 与 diagnostics-first blocked 的非目标

### Phase 2：registry sync and verification

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline`

## 7. 回滚原则

- 如果 `104` 让人误以为 auto-fix、后台 replay loop、program aggregation 或 CLI wiring 已在本切片实现，必须回退
- 如果 `104` 把 `recheck_required`、`needs_remediation` 与 fail-closed `blocked` 混成一类状态，必须回退
- 如果 `104` 放宽 stale bundle / scope mismatch / linkage invalid 的 fail-closed 规则，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
