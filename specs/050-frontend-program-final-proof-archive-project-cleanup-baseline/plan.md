---
related_doc:
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Program Final Proof Archive Project Cleanup Baseline

**编号**：`050-frontend-program-final-proof-archive-project-cleanup-baseline` | **日期**：2026-04-04 | **规格**：specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md

## 概述

本计划处理的是 `049` 之后的 frontend program final proof archive project cleanup baseline，而不是把 `049` 的 thread archive responsibility 再复制一遍，也不是把 cleanup 扩张成无边界 workspace mutation engine。当前仓库已经在上游锁定并实现了：

- `024` 到 `034`：remediation / provider / patch / writeback / registry 的 orchestration 与 artifact 链路
- `035`：broader governance request/result 与显式确认 CLI surface
- `036`：broader governance artifact writer 与 execute artifact output/report
- `037`：final governance request/result 与显式确认 CLI surface
- `038`：final governance artifact writer 与 execute artifact output/report
- `039`：writeback persistence request/result 与显式确认 CLI surface
- `040`：writeback persistence artifact writer 与 execute artifact output/report
- `041`：persisted write proof request/result 与显式确认 CLI surface
- `042`：persisted write proof artifact writer 与 execute artifact output/report
- `043`：final proof publication request/result 与显式确认 CLI surface
- `044`：final proof publication artifact writer 与 execute artifact output/report
- `045`：final proof closure request/result 与显式确认 CLI surface
- `046`：final proof closure artifact writer 与 execute artifact output/report
- `047`：final proof archive request/result packaging 与显式确认 CLI surface
- `048`：final proof archive artifact writer 与 execute artifact output/report
- `049`：final proof archive thread archive request/result 与独立 CLI surface

但 downstream canonical project cleanup 仍缺少稳定 truth：

- thread archive execute truth 已形成，但 project cleanup 何时允许执行、如何报告结果、如何沉淀 cleanup artifact 还没有 canonical baseline
- operator 和审计链路若继续依赖 thread archive 输出，仍缺少统一 cleanup contract
- 若继续直接编码，容易把 thread archive、project cleanup 与 workspace mutation engine 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Final Proof Archive Project Cleanup Baseline`：

- 先冻结 final proof archive project cleanup 的 truth order、non-goals 与 execute boundary
- 再冻结 cleanup input contract、service boundary、artifact strategy 与 result reporting
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 先行完成。接下来按红绿改进入两个实现切片：`ProgramService final proof archive project cleanup slice`，随后再进入 CLI output + artifact surface。当前仍不扩张 cleanup 范围。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`049` thread archive request/result truth、现有 `ProgramService` / `program_cmd.py`  
**主要约束**：

- final proof archive project cleanup 只能消费 `049` thread archive execute truth
- project cleanup 必须显式确认后执行，并诚实回报 cleanup state、cleanup result、written paths、remaining blockers 与 warnings
- 当前 child work item 只定义 bounded project cleanup baseline，不做任意 workspace mutation
- project cleanup artifact 只记录 canonical cleanup truth，不改写 `049` thread archive truth 或更上游 artifact truth

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Formal docs must be canonical before implementation | 先冻结 `050` 的 spec/plan/tasks，再进入代码 |
| Single-source-of-truth downstream handoff | 明确 `049` thread archive execute truth 是唯一上游真值 |
| Explicit confirmation on operator-facing cleanup action | project cleanup 仅允许显式确认后 execute |
| No hidden side effects in cleanup baseline | 当前 work item 明确排除任意 workspace mutation 与未定义删除 |

## 项目结构

### 文档结构

```text
specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program final proof archive project cleanup 从 `049` downstream requirement 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/050/...` 文档改动。

### Phase 1：Project cleanup truth freeze

**目标**：锁定 final proof archive project cleanup 在 `049 -> 050` 主线中的 truth order。  
**产物**：cleanup truth baseline、non-goals baseline、execute boundary baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Cleanup service / artifact boundary freeze

**目标**：锁定 cleanup input contract、service boundary、artifact strategy 与 result honesty boundary。  
**产物**：cleanup payload baseline、artifact baseline、result reporting baseline、readonly upstream linkage baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、terminal side-effect guard baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：ProgramService final proof archive project cleanup slice

**目标**：在 `ProgramService` 中落下 final proof archive project cleanup service 与 cleanup artifact writer。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program final proof archive project cleanup output slice

**目标**：把 final proof archive project cleanup 暴露到独立 CLI surface，要求显式确认，并输出 cleanup result / remaining blockers / cleanup artifact。  
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 final proof archive project cleanup request / execute / artifact writer
- 再把显式 final proof archive project cleanup surface 暴露到 CLI
- cleanup artifact 只承载 bounded cleanup baseline truth，不引入任意 workspace mutation
