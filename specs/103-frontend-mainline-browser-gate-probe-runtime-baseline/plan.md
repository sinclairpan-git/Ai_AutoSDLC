# 执行计划：Frontend Mainline Browser Gate Probe Runtime Baseline

**功能编号**：`103-frontend-mainline-browser-gate-probe-runtime-baseline`  
**创建日期**：2026-04-13  
**状态**：docs-only probe runtime contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`103` 的目标不是实现 Playwright runner，也不是绑定 `020` handoff，而是把 `102` 下游的 probe runtime 先冻结成正式合同：

- 冻结 `BrowserQualityGateExecutionContext -> BrowserGateProbeRuntimeSession`；
- 冻结 shared browser bootstrap、artifact namespace 与 trace/screenshot materialization；
- 冻结四类检查的 runtime execution order、evidence capture 与结果写出；
- 冻结 `browser_quality_bundle` 的 runtime materialization input；
- 保持 recheck/remediation binding、多浏览器矩阵与更宽质量平台继续在后续切片独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `103` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `104`
- 在 `program-manifest.yaml` 为 `103` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 probe runtime session、artifact record、execution receipt 与 bundle materialization input
- 冻结 `evidence_missing` / `transient_run_failure` 在 runtime 层的最小诚实边界

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 Playwright runner、artifact store、视觉回归平台或多浏览器矩阵
- 绑定 `020` handoff、recheck/remediation replay 或 program aggregation
- 改写 `102` gate contract、`101` apply result truth、`071` a11y foundation truth 或 `073` provider/style truth

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`
- `specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/plan.md`
- `specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/tasks.md`
- `specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Runtime boundary

- `103` 只能在 `102.BrowserQualityGateExecutionContext` 之后启动
- probe runtime 只能消费 `101` apply truth、`073` provider/style truth 与 `071` visual/a11y foundation
- `103` 不得回到 `102` 改 eligibility，也不得顺手绑定 `020` handoff

### 4.2 Artifact boundary

- 一个 `gate_run_id` 只允许一个 runtime session 与一个 artifact namespace
- shared trace / screenshot 必须来自当前 gate run，不得借用历史 run
- blocker / advisory 必须绑定当前 gate run 的 artifact、anchor 与 requirement linkage

### 4.3 Scope boundary

- `103` 只负责 probe execution 与 bundle materialization input
- `103` 不得实现 auto-fix、auto-recheck、多浏览器矩阵或 program-level ready
- `103` 不得修改 `src/`、`tests/` 或声称 runner 已落地

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `102` 对 execution context、check result、bundle 与失败分类的正式要求
- 回读 `101` 对 apply result/source linkage 的下游约束
- 回读 `071` 与 `073` 对 a11y foundation、provider/style truth 的直接输入边界

### Phase 1：formal probe runtime freeze

- 在 `spec.md` 冻结 runtime session、artifact record、execution receipt 与 bundle materialization input
- 在 `spec.md` 冻结 shared bootstrap、四类检查 execution order 与 evidence honesty
- 在 `spec.md` 写清当前切片不绑定 `020` handoff/recheck/remediation

### Phase 2：registry sync and verification

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/103-frontend-mainline-browser-gate-probe-runtime-baseline`

## 7. 回滚原则

- 如果 `103` 让人误以为 `020` handoff binding、recheck/remediation replay 或多浏览器矩阵已在本切片实现，必须回退
- 如果 `103` 放宽了 `one gate_run_id == one runtime session == one artifact namespace`，必须回退
- 如果 `103` 把 `evidence_missing` 与 `transient_run_failure` 压成统一失败态，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
