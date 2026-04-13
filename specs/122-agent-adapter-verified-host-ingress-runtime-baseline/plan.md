---
related_doc:
  - "program-manifest.yaml"
  - "specs/121-agent-adapter-verified-host-ingress-truth-baseline/spec.md"
  - "src/ai_sdlc/models/project.py"
  - "src/ai_sdlc/integrations/agent_target.py"
  - "src/ai_sdlc/integrations/ide_adapter.py"
  - "src/ai_sdlc/cli/adapter_cmd.py"
  - "src/ai_sdlc/cli/run_cmd.py"
  - "tests/unit/test_ide_adapter.py"
  - "tests/integration/test_cli_adapter.py"
  - "tests/integration/test_cli_init.py"
  - "tests/integration/test_cli_run.py"
---
# 实施计划：Agent Adapter Verified Host Ingress Runtime Baseline

**编号**：`122-agent-adapter-verified-host-ingress-runtime-baseline` | **日期**：2026-04-13 | **规格**：`specs/122-agent-adapter-verified-host-ingress-runtime-baseline/spec.md`

## 概述

`122` 的目标是把 `121` 已冻结的 root truth 变成可执行 runtime。推荐实现分四步：先补 target/path 红灯夹具，再重构 adapter 状态机与 canonical path materialization，再接自动 verify 和 `run` gate，最后收口 `init / adapter / run` 的 integration tests。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：`ProjectConfig` adapter fields、`agent_target` detector、`ide_adapter` materialization、CLI `init/adapter/run` surfaces  
**存储**：`src/ai_sdlc/models/project.py`、`src/ai_sdlc/integrations/*`、`src/ai_sdlc/cli/*`、adapter templates、tests  
**测试**：unit + integration focused adapter/run matrix  
**目标平台**：repo-local host ingress verification baseline  
**约束**：

- 不引入 `TRAE` 单独 target
- 不回退到 `.claude/AI-SDLC.md`、`.codex/AI-SDLC.md`、`.vscode/AI-SDLC.md` 这类旧入口
- 不再把 `adapter activate` 当作主路径 gate
- `generic` 只能诚实降级，不能伪装成 verified

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | runtime 直接承接 `121` 的 target/path/state truth |
| 最小改动面 | 仅改 adapter model/integration/CLI 与对应 tests |
| 流程诚实 | 未 verified 时只允许诚实降级，不误报激活 |

## 项目结构

```text
specs/122-agent-adapter-verified-host-ingress-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

src/ai_sdlc/models/project.py
src/ai_sdlc/integrations/agent_target.py
src/ai_sdlc/integrations/ide_adapter.py
src/ai_sdlc/cli/adapter_cmd.py
src/ai_sdlc/cli/run_cmd.py
src/ai_sdlc/adapters/*
tests/unit/test_ide_adapter.py
tests/integration/test_cli_adapter.py
tests/integration/test_cli_init.py
tests/integration/test_cli_run.py
```

## 阶段计划

### Phase 0：Red fixtures

**目标**：先锁定 canonical path、target set、generic degrade 与 run gate 的红灯夹具  
**产物**：adapter/init/run focused tests  
**验证方式**：targeted pytest  
**回退方式**：仅回退测试夹具

### Phase 1：State + path materialization

**目标**：切 canonical path，并把 ingress truth 升级成 `materialized / verified_loaded / degraded / unsupported`  
**产物**：model + ide_adapter + adapter templates  
**验证方式**：unit + integration focused tests  
**回退方式**：独立回退 adapter model/materialization

### Phase 2：Auto verify + gate

**目标**：把 `init / adapter select` 自动 verify 化，并让 `run` 按 ingress truth 门禁  
**产物**：adapter CLI + run gate + persisted evidence/degrade reason  
**验证方式**：integration focused tests  
**回退方式**：独立回退 CLI gate

### Phase 3：Closeout

**目标**：归档 focused verification 与 user-facing guidance 收敛  
**产物**：execution log + updated help/user guidance strings  
**验证方式**：`git diff --check` + targeted pytest  
**回退方式**：仅回退文案与归档

## 实施顺序建议

1. 先让测试锁死 target/path/state truth
2. 再改 materialization 和 persisted fields
3. 再接 auto verify 与 `run`/managed delivery gate
4. 最后统一 help/status/init 文案
