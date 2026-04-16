---
related_doc:
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "src/ai_sdlc/core/host_runtime_manager.py"
  - "src/ai_sdlc/core/managed_delivery_apply.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/models/host_runtime_plan.py"
  - "src/ai_sdlc/models/frontend_managed_delivery.py"
  - "src/ai_sdlc/models/frontend_solution_confirmation.py"
  - "program-manifest.yaml"
---
# 实施计划：Frontend Mainline Host Remediation And Workspace Integration Closure Baseline

**功能编号**：`144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 先冻结 `144` formal scope，把剩余 blocker 收紧为 `request materialization + runtime remediation + workspace integration`
2. 先写 red tests，锁定“从 selected provider 到 apply request”的桥接和 root integration 默认关闭的 fail-closed 行为
3. 扩展 `frontend_managed_delivery` models、`managed_delivery_apply`、`host_runtime_manager` 与 `ProgramService`
4. 补 CLI / canonical artifact surface、focused verification、对抗评审与 truth 对账

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：现有 `HostRuntimePlan` / `FrontendSolutionSnapshot` / `InstallStrategy` / `managed_delivery_apply` 模型；不新增任意 shell 执行层  
**存储**：`.ai-sdlc/memory/frontend-managed-delivery/` canonical request/apply artifacts；`.ai-sdlc/runtime/` 作为 framework-managed runtime root  
**测试**：`pytest` unit/integration；以 injected installer / artifact writer / runtime executor 保持离线稳定  
**目标平台**：已被 `096` profile 覆盖的平台；source-only / unbound surface 仍然 fail-closed  
**约束**：只补 host remediation、registry-declared package install 与 optional workspace integration；不碰 browser gate、默认 old-root takeover、多浏览器矩阵、任意 root patch，也不支持 operator 手填任意包坐标

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 先文档后实现 | `144` 先冻结 spec/plan/tasks，再进入 red tests 与实现 |
| truth order 不反写上游 | 只消费 `073/096/097/098/099/100`，不重写 solution/posture/registry truth |
| fail-closed 优先 | host 缺口、credential 缺口、workspace 越界、unsupported target class 全部 preflight 阻断 |
| 小白可用 | blocker 必须输出 plain-language 原因、reentry condition 与单一下一步动作 |

## 项目结构

```text
specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
src/ai_sdlc/models/host_runtime_plan.py
src/ai_sdlc/models/frontend_managed_delivery.py
src/ai_sdlc/models/frontend_solution_confirmation.py
src/ai_sdlc/core/host_runtime_manager.py
src/ai_sdlc/core/managed_delivery_apply.py
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_host_runtime_manager.py
tests/unit/test_managed_delivery_apply.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
program-manifest.yaml
```

## 实施路径

### Phase 0：Gap freeze 与 request bridge contract

**目标**：明确 `144` 要补的是 canonical request/materialization 链，不再靠手写 apply request YAML，并冻结 public/private registry-declared package scope  
**产物**：formal docs、request bridge contract、runtime/workspace payload contract  
**验证方式**：docs 对账 + red tests 暴露当前无自动桥接 reality  
**回退方式**：仅回退 `144` formal docs 与新加红灯测试

### Phase 1：Runtime remediation 与 managed target prepare 实装

**目标**：让 `runtime_remediation`、`managed_target_prepare` 从 nominal action 变成真实 execute truth  
**产物**：runtime remediation payload/executor、managed target prepare payload/executor、ledger before/after truth  
**验证方式**：`tests/unit/test_managed_delivery_apply.py`、`tests/unit/test_program_service.py`  
**回退方式**：回退 execute wiring，不改 `096` read-only host plan contract

### Phase 2：Bundle-driven dependency install 与 workspace integration

**目标**：把 registry-declared install strategy 真值与 optional root integration 接入 apply runtime  
**产物**：bundle-driven dependency selection、workspace integration payload/validator/executor、plain-language prerequisite blockers  
**验证方式**：`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`  
**回退方式**：保留 `124` 既有 `dependency_install/artifact_generate` 行为，回退 `workspace_integration` 与 auto request bridge

### Phase 3：CLI / truth / close evidence

**目标**：让 operator 有 canonical surface 能直接看到 request、blockers、execute result，并把 `144` 纳入 truth ledger  
**产物**：CLI/report surface、program manifest truth refs、execution log、focused verification、request schema 与 apply result 的职责分离说明  
**验证方式**：`program validate`、`verify constraints`、focused CLI tests、`workitem truth-check`  
**回退方式**：回退 `144` 的 surface/manifest wiring，不影响 `143` 已落成 browser gate truth

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| selected provider -> canonical apply request | `tests/unit/test_program_service.py` | `tests/integration/test_cli_program.py` |
| host remediation fail-closed / execute truth | `tests/unit/test_host_runtime_manager.py` | `tests/unit/test_managed_delivery_apply.py` |
| dependency install payload derives from install strategy truth | `tests/unit/test_program_service.py` | `tests/unit/test_managed_delivery_apply.py` |
| workspace integration default-off + bounded execution | `tests/unit/test_managed_delivery_apply.py`（含 path normalization / symlink traversal / mixed target_class 阻断） | `tests/integration/test_cli_program.py` |

## 冻结决策

| 决策 | 冻结结果 | 影响阶段 |
|------|----------|----------|
| canonical managed delivery request artifact | 复用既有 canonical 路径 `.ai-sdlc/memory/frontend-managed-delivery/latest.yaml`；显式 request path 仅保留调试/回放入口，不再作为主线必需 | Phase 1 |
| `runtime_remediation` default executor | 仅支持 framework-managed runtime root 与其受控缓存；不复用 offline profile launcher，不向 system/global runtime 升级 | Phase 1 |
| `workspace_integration` v1 mutation_kind | 只允许 `write_new` 与 `overwrite_existing`；append/merge 留待后续 tranche | Phase 2 |
| external component package scope | 仅指已写入 `solution_snapshot/install_strategy/delivery_bundle_entry` 真值的 public/private package 集合；不支持 operator 手填任意 package 坐标 | Phase 0-2 |

## 实施顺序建议

1. 先锁定 request materialization 与 payload schema，再碰执行器
2. 先让 host/runtime/package/managed-target 这四类 required action 真执行，再补 root-level optional integration
3. 最后补 CLI/manifest/truth surface，避免过早宣称 closure
