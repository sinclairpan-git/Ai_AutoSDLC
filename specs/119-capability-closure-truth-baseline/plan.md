---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/cli/commands.py"
---
# 实施计划：Capability Closure Truth Baseline

**编号**：`119-capability-closure-truth-baseline` | **日期**：2026-04-13 | **规格**：`specs/119-capability-closure-truth-baseline/spec.md`

## 概述

`119` 的目标是把“能力闭环状态”回写成仓库真值，而不是继续停留在口头审计。推荐实现分三步：先冻结 formal carrier，再在 `program-manifest.yaml` 增加 `capability_closure_audit`，最后把该真值以 bounded 方式接到 `status --json` / `status` 并同步 frontend rollout 文档。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：现有 `ProgramManifest` model、`ProgramService` manifest loader、`status` bounded telemetry surface  
**存储**：`program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`、`specs/119-capability-closure-truth-baseline/*`  
**测试**：`pytest` integration focused check  
**目标平台**：root truth + bounded status surface  
**约束**：
- 不新增平行 manifest；继续复用根级 `program-manifest.yaml`
- 不自动推导所有 cluster 状态；当前先手工冻结审计结果
- 不把 capability closure audit 升级为新的 hard blocker

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | capability closure 只认 manifest 顶层 audit |
| 最小改动面 | 仅改 model、status surface、root docs/config |
| 流程诚实 | 明确拆开 work item local status 与 capability closure |

## 项目结构

```text
specs/119-capability-closure-truth-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

src/ai_sdlc/models/program.py
src/ai_sdlc/telemetry/readiness.py
src/ai_sdlc/cli/commands.py
tests/integration/test_cli_status.py
program-manifest.yaml
frontend-program-branch-rollout-plan.md
.ai-sdlc/project/config/project-state.yaml
```

## 阶段计划

### Phase 0：Formal carrier freeze

**目标**：把 `119` 的 capability closure 口径冻结成 formal truth  
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`  
**验证方式**：文档对账  
**回退方式**：仅回退 `119` carrier

### Phase 1：Root truth sync

**目标**：在 `program-manifest.yaml` 增加 `capability_closure_audit` 并回写当前 open clusters  
**产物**：manifest 新字段 + frontend rollout wording 同步  
**验证方式**：YAML 解析 + 文档对账  
**回退方式**：独立回退 root truth 变更

### Phase 2：Bounded status surfacing

**目标**：让 `status --json` / `status` 可稳定读出 capability closure summary  
**产物**：model + readiness + CLI status + regression test  
**验证方式**：integration focused test + repo constraints  
**回退方式**：独立回退 status surface，不影响 manifest truth

## 实施顺序建议

1. 先写 status JSON 红灯夹具
2. 再补 manifest model 与 capability closure surface
3. 回写 root manifest / rollout plan / project-state / 119 formal carrier
4. 跑 focused verification 与 repo constraints
