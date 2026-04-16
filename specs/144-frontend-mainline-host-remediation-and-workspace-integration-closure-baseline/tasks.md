---
related_doc:
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "src/ai_sdlc/models/host_runtime_plan.py"
  - "src/ai_sdlc/models/frontend_managed_delivery.py"
  - "src/ai_sdlc/core/host_runtime_manager.py"
  - "src/ai_sdlc/core/managed_delivery_apply.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "program-manifest.yaml"
---
# 任务分解：Frontend Mainline Host Remediation And Workspace Integration Closure Baseline

**编号**：`144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline` | **日期**：2026-04-14
**来源**：plan.md + spec.md

## Batch 1：Red tests 与 canonical request bridge

### Task 1.1 锁定 request materialization / runtime remediation / workspace integration 红灯

- **任务编号**：T144-11
- **优先级**：P0
- **文件**：`tests/unit/test_program_service.py`, `tests/unit/test_managed_delivery_apply.py`, `tests/integration/test_cli_program.py`
- **验收标准**：
  1. 当前 public/private registry-declared provider 选择能够暴露“尚无 canonical request bridge”红灯
  2. `runtime_remediation` 当前 nominal/no-op 行为被测试锁定
  3. `workspace_integration` 默认关闭、显式选择、越界阻断三类场景被红灯锁定
  4. path normalization 逃逸、symlink traversal、mixed target_class payload 三类 root-level 风险被红灯锁定

## Batch 2：Host remediation 与 managed target prepare

### Task 2.1 落地 runtime remediation payload 与 execute truth

- **任务编号**：T144-21
- **优先级**：P0
- **文件**：`src/ai_sdlc/models/host_runtime_plan.py`, `src/ai_sdlc/models/frontend_managed_delivery.py`, `src/ai_sdlc/core/host_runtime_manager.py`, `src/ai_sdlc/core/managed_delivery_apply.py`
- **验收标准**：
  1. `runtime_remediation` 从 `HostRuntimePlan.remediation_fragment` 自动派生，不再靠手写 executor payload
  2. execute path 只改 framework-managed runtime root，bootstrap-only 缺口继续 fail-closed
  3. ledger 对 `runtime_remediation` 记录真实 before/after state 或真实 blocker

### Task 2.2 落地 managed target prepare 真执行

- **任务编号**：T144-22
- **优先级**：P0
- **文件**：`src/ai_sdlc/models/frontend_managed_delivery.py`, `src/ai_sdlc/core/managed_delivery_apply.py`, `tests/unit/test_managed_delivery_apply.py`
- **验收标准**：
  1. `managed_target_prepare` 真实创建 managed subtree / 最小骨架
  2. 已存在 target、越界 path、will_not_touch 命中时 fail-closed
  3. `managed_target_prepare` 不再以 generic success 冒充已执行

## Batch 3：Bundle-driven dependency install 与 workspace integration

### Task 3.1 从 selected provider/bundle 真值自动生成 dependency install payload

- **任务编号**：T144-31
- **优先级**：P0
- **文件**：`src/ai_sdlc/models/frontend_solution_confirmation.py`, `src/ai_sdlc/models/frontend_managed_delivery.py`, `src/ai_sdlc/core/program_service.py`, `tests/unit/test_program_service.py`
- **验收标准**：
  1. `dependency_install` payload 自动继承 install strategy `package_manager + packages`
  2. `component_library_packages` 与 `adapter_packages` 被同时纳入 canonical install selection
  3. 仅 registry-declared public/private package 集合允许进入 canonical install selection；缺 private registry prerequisite 时 request/preflight 明确阻断

### Task 3.2 落地 bounded workspace integration optional action

- **任务编号**：T144-32
- **优先级**：P0
- **文件**：`src/ai_sdlc/models/frontend_managed_delivery.py`, `src/ai_sdlc/core/managed_delivery_apply.py`, `src/ai_sdlc/core/program_service.py`, `tests/unit/test_managed_delivery_apply.py`, `tests/integration/test_cli_program.py`
- **验收标准**：
  1. `workspace_integration` 只接受 `workspace / lockfile / ci / proxy / route` 五类 root target
  2. action 默认关闭；未选择时 root-level targets 保持 no-touch
  3. 选择后只能修改已声明 approved root targets，越界或 unsupported target class preflight 阻断
  4. 规范化后路径逃逸 repo、symlink 穿透 repo 边界、mixed target_class payload 都必须在任何写入前阻断

## Batch 4：CLI / truth / release evidence

### Task 4.1 提供 canonical surface 并完成 focused verification

- **任务编号**：T144-41
- **优先级**：P1
- **文件**：`src/ai_sdlc/cli/program_cmd.py`, `src/ai_sdlc/core/program_service.py`, `tests/integration/test_cli_program.py`, `program-manifest.yaml`, `task-execution-log.md`
- **验收标准**：
  1. operator 能直接看到 canonical request（既有 canonical path）、blockers、execute result，以及“只支持 registry-declared package set 自动安装”的边界，而不是手写 apply request YAML
  2. `program validate`、`verify constraints`、focused pytest 与 `workitem truth-check` 通过
  3. manifest / closure summary 诚实更新，不再把 096/124/144 混成历史灰区
  4. canonical request artifact 与 apply result/ledger truth 保持职责分离，不发生 schema 混写
