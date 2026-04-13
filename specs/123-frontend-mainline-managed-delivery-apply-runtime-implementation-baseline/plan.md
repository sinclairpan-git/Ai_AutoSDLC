---
related_doc:
  - "program-manifest.yaml"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
---
# 实施计划：Frontend Mainline Managed Delivery Apply Runtime Implementation Baseline

**编号**：`123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline` | **日期**：2026-04-13 | **规格**：`specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md`

## 概述

`123` 的目标是把 `101` 的 docs-only apply runtime contract 变成第一批真实 executor runtime。推荐实现分四步：先补 fail-closed 红灯夹具，再新增 model + core executor，再接薄的 ProgramService/CLI wiring，最后完成 focused verification 与归档。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：`101` formal contract、`ProgramService` 现有 request/result 模式、program CLI execute surface  
**存储**：`src/ai_sdlc/models/frontend_managed_delivery.py`、`src/ai_sdlc/core/managed_delivery_apply.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、focused tests  
**测试**：unit + integration focused apply executor matrix  
**目标平台**：frontend mainline managed delivery 的第一批 executor runtime  
**约束**：

- 不把 `dependency_install`、file writer、browser gate 混进 `123`
- 不回到 planner 重写 confirmed `frontend_action_plan`
- 不让 `apply` 成功伪装成 browser gate 或 readiness 成功
- rollback/retry/cleanup 只记录 refs，不做自动执行
- host ingress gate 只消费既有 truth，不在 executor 内重新发明状态机

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | runtime 直接承接 `101` 与 `120/T11`，不新建 planner truth |
| 最小改动面 | 优先新增专用 model/core 文件，只做薄的 ProgramService/CLI 接线 |
| 流程诚实 | unsupported action、partial progress、pending browser gate 都保持 fail-closed/honest wording |

## 项目结构

```text
specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

src/ai_sdlc/models/frontend_managed_delivery.py
src/ai_sdlc/core/managed_delivery_apply.py
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_managed_delivery_apply.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：Red fixtures

**目标**：先锁定 plan fingerprint、required unsupported、dependency blocker、before-state failure 与 pending browser gate 的红灯夹具  
**产物**：focused unit tests  
**验证方式**：targeted pytest  
**回退方式**：仅回退测试夹具

### Phase 1：Core executor runtime

**目标**：新增 runtime model 与窄版 apply executor  
**产物**：`frontend_managed_delivery.py`、`managed_delivery_apply.py`  
**验证方式**：unit focused tests  
**回退方式**：独立回退 executor/model

### Phase 2：Thin service/CLI wiring

**目标**：把 apply request/result 接到 `ProgramService` 与 `program_cmd.py`  
**产物**：thin request/result surface + integration coverage  
**验证方式**：unit + integration focused tests  
**回退方式**：独立回退 ProgramService/CLI 接线

### Phase 3：123-scoped closeout

**目标**：完成 `123` scoped focused verification、docs closeout 与 registry/project-state sync  
**产物**：execution log、`program-manifest.yaml`、`project-state.yaml`  
**验证方式**：`uv run ai-sdlc verify constraints`、`uv run ai-sdlc program validate`、`git diff --check`  
**回退方式**：仅回退 closeout/docs 同步

## 实施顺序建议

1. 先让测试锁死 fail-closed 与 honest result semantics
2. 再新增 executor 专用 model/core 文件
3. 再接 ProgramService/CLI 的最小 request/result surface
4. 最后统一 closeout 文档与验证记录
