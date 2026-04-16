---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
---
# 实施计划：Frontend P3 Target Project Adapter Scaffold Baseline

**编号**：`153-frontend-p3-target-project-adapter-scaffold-baseline` | **日期**：2026-04-16 | **规格**：specs/153-frontend-p3-target-project-adapter-scaffold-baseline/spec.md

## 概述

`153` 是 `152` 后的第一条 runtime tranche。目标是在 Core 仓库中把 target-project adapter scaffold truth、runtime boundary receipt、ProgramService/CLI handoff 与 verify attachment 一次性接通，形成可被后续外部 target project 直接消费的最小 runtime scaffold contract。

## 技术背景

**语言/版本**：Python 3.11 + Pydantic models + YAML artifacts  
**主要依赖**：`151` provider expansion baseline、`frontend solution snapshot`、ProgramService、verify constraints  
**存储**：`src/ai_sdlc/models/frontend_provider_runtime_adapter.py`、`src/ai_sdlc/generators/frontend_provider_runtime_adapter_artifacts.py`、`src/ai_sdlc/core/frontend_provider_runtime_adapter.py`、`governance/frontend/provider-runtime-adapter/`  
**测试**：`uv run pytest` 聚焦 unit/integration suites、`uv run ai-sdlc verify constraints`、`workitem close-check`、`program truth sync/audit`  
**目标平台**：Ai_AutoSDLC Core runtime contract / handoff / verify surfaces  
**约束**：
- 不进入外部 target project 的真实 runtime code
- 不提前实现 `independent-adapter-package` 真实包化
- 不把 scaffold truth 伪造成 delivered truth

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | `153` formal docs 与 runtime contracts 全部归入当前 work item |
| 先 formalize 再实现 | `152` 已冻结 successor truth，`153` 只消费其 runtime tranche 入口 |
| 诚实区分 policy 与 runtime | `153` 只实现 scaffold truth / boundary receipt，不宣称 target project delivered |
| 有界实现 | 范围限制在 Core 的 models/artifacts/handoff/verify，不碰外部项目 runtime |

## 项目结构

### 文档结构

```text
specs/153-frontend-p3-target-project-adapter-scaffold-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 源码结构

```text
src/ai_sdlc/
├── models/frontend_provider_runtime_adapter.py
├── generators/frontend_provider_runtime_adapter_artifacts.py
├── core/frontend_provider_runtime_adapter.py
├── core/program_service.py
├── core/verify_constraints.py
└── cli/program_cmd.py
```

## 阶段计划

### Phase 0：Freeze 153 runtime tranche scope

**目标**：把 `153` 明确限定为 `target-project-adapter-layer scaffold + boundary receipt + handoff + verify`。  
**产物**：`spec.md`、`plan.md`、`tasks.md`  
**验证方式**：`152/151` truth 对账 review  
**回退方式**：回退 `153` formal docs，不影响既有 runtime truth。  

### Phase 1：Implement models / artifacts / validation / handoff

**目标**：落地 runtime adapter scaffold models、artifact materializer、validator、ProgramService handoff 与 CLI handoff。  
**产物**：新增 `models/generators/core` 模块，并修改 `program_service.py`、`program_cmd.py`、`verify_constraints.py`。  
**验证方式**：聚焦 unit/integration pytest。  
**回退方式**：回退 `153` 相关代码与 tests。  

### Phase 2：Close-out and truth refresh

**目标**：补齐 execution log / development summary，刷新 global truth，并确认 `153` 可通过 close-check。  
**产物**：`task-execution-log.md`、`development-summary.md`、`program-manifest.yaml`。  
**验证方式**：`UV_CACHE_DIR=/tmp/uv-cache uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi specs/153-frontend-p3-target-project-adapter-scaffold-baseline`、`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`。  
**回退方式**：回退 `153` formal docs 与 latest truth snapshot。  

## 工作流计划

### 工作流 A：runtime scaffold contract

**范围**：落地 target-project adapter scaffold models 与 YAML artifact contract。  
**影响范围**：`models`、`generators`、对应 unit tests。  
**验证方式**：model / artifact unit tests。  
**回退方式**：回退 `frontend_provider_runtime_adapter` 相关文件。  

### 工作流 B：handoff and verify surfacing

**范围**：落地 ProgramService handoff、CLI handoff 与 verify attachment report。  
**影响范围**：`program_service.py`、`program_cmd.py`、`verify_constraints.py`、对应 tests。  
**验证方式**：program service tests、CLI integration tests、verify tests。  
**回退方式**：回退 handoff/verify 接口，不影响 artifact models。  

### 工作流 C：truth close-out

**范围**：补齐 close-out docs、刷新 truth snapshot、确认 `153` close-check。  
**影响范围**：`specs/153/...`、`program-manifest.yaml`。  
**验证方式**：close-check + truth sync/audit。  
**回退方式**：回退 `153` formal docs 与 snapshot。  

## 实施顺序建议

1. 先落地 models / artifacts，把 `153` 的 target-project scaffold contract 固定下来
2. 再接 `ProgramService / CLI / verify`
3. 最后刷新 `153` formal docs 与 global truth
