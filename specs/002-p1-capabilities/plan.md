# 实施计划：AI-SDLC P1 能力扩展缺口收敛

**编号**：`002-p1-capabilities` | **日期**：2026-03-28 | **规格**：specs/002-p1-capabilities/spec.md

## 概述

本计划只处理 `002` 在原 PRD P1 范围内的缺口收敛，聚焦 **RG-010 ~ RG-015**：Incident close、Change runtime pause/resume、Maintenance execution path、Multi-Agent runtime orchestration、Knowledge Refresh 主链接入。推荐实现顺序是先补数据合同与 artifact，再补 Studio / Parallel / Close 主链，最后用 flow / integration tests 锁住运行态行为。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Typer、Pydantic v2、PyYAML、Rich、pytest  
**存储**：`.ai-sdlc/work-items/<WI>/` 下的 YAML / Markdown artifact  
**测试**：pytest unit + flow + integration  
**目标平台**：macOS + Linux  
**约束**：遵循 `001` 已锁定的状态落盘、docs/dev 真值隔离、gate 前置与 close-check 对账规则

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 只补 `002` 对应的原 PRD P1 旧债，不引入 `003/004` 范围的新能力 |
| MUST-2 关键路径可验证 | 每个 runtime gap 都要求 unit + flow 至少一条 contract-level 验证 |
| MUST-3 范围声明与回退 | 以 Studios / Parallel / Knowledge / Gates 分批提交，可逐批回退 |
| MUST-4 状态落盘 | pause/resume、assignment freeze、refresh evidence、postmortem gate 结果全部落盘 |
| MUST-5 产品代码隔离 | 只修改 `src/ai_sdlc/`、`tests/` 与 `specs/002-p1-capabilities/` 下的计划文档 |

## 项目结构

### 文档结构

```text
specs/002-p1-capabilities/
├── spec.md
├── plan.md          ← 本文件
└── tasks.md         ← 本次补齐
```

### 源码结构

```text
src/ai_sdlc/
├── models/
│   ├── work.py                  # Incident / Change / Maintenance models
│   └── state.py                 # ParallelPolicy / WorkerAssignment / ExecutionPlan
├── studios/
│   ├── incident_studio.py       # incident artifacts
│   ├── change_studio.py         # freeze snapshot / impact / rebaseline
│   ├── maintenance_studio.py    # lightweight maintenance path
│   └── router.py                # StudioProtocol + dispatch
├── parallel/engine.py           # split / overlap / assign / merge simulation
├── knowledge/engine.py          # refresh level + refresh apply
├── gates/extra_gates.py         # KnowledgeGate / ParallelGate / PostmortemGate
├── core/
│   ├── runner.py                # stage orchestration
│   └── state_machine.py         # work item state transitions
├── cli/commands.py              # refresh command and status helpers
└── tests/
    ├── unit/test_studios.py
    ├── unit/test_parallel.py
    ├── unit/test_gates.py
    ├── flow/test_incident_flow.py
    ├── flow/test_parallel_flow.py
    └── flow/test_knowledge_refresh_flow.py
```

## 阶段计划

### Phase 0：P1 contract 与 artifact 模型补齐

**目标**：先让 `resume-point`、`execution-path`、parallel coordination artifact、refresh evidence 等对象成为正式真值。  
**产物**：`models/work.py`、`models/state.py` 增量字段/对象与对应单测。  
**验证方式**：`tests/unit/test_p1_models.py`、`tests/unit/test_studios.py`。  
**回退方式**：按模型批次独立提交，可单独 revert。

### Phase 1：Change / Maintenance runtime 主链补齐

**目标**：把 ChangeStudio 的暂停与恢复入口、MaintenanceStudio 的 execution path 从“文档产物”升级为主链可消费合同。  
**产物**：`change_studio.py`、`maintenance_studio.py`、`state_machine.py`、相关 flow tests。  
**验证方式**：`tests/unit/test_studios.py` + 变更/维护 flow。  
**回退方式**：按 Studio 分批提交。

### Phase 2：Parallel runtime orchestration 落地

**目标**：把 parallel 从 planning/simulation 推进到 assignment freeze、worker lifecycle、merge verify 的正式运行时合同。  
**产物**：`parallel/engine.py`、`gates/extra_gates.py`、`runner.py`、parallel tests。  
**验证方式**：`tests/unit/test_parallel.py` + `tests/flow/test_parallel_flow.py`。  
**回退方式**：与 single-agent 主链解耦提交。

### Phase 3：Knowledge Refresh / Incident Close 接入 Done/Close 主链

**目标**：让 refresh 与 postmortem 不再是旁路命令，而是 completed 前的正式 gate。  
**产物**：`knowledge/engine.py`、`gates/extra_gates.py`、`runner.py`、incident/refresh flows。  
**验证方式**：`tests/flow/test_knowledge_refresh_flow.py`、`tests/flow/test_incident_flow.py`、`tests/unit/test_gates.py`。  
**回退方式**：先补 gate 判断，再补 runner 绑定，避免一次性耦合过大。

### Phase 4：Status / Recover / Report surface 对账

**目标**：让新的 P1 artifact 可被 status/recover/report 读取，避免只存在于 Studio 返回值或自由文本。  
**产物**：必要的 CLI / report surface 回填与 traceability 更新。  
**验证方式**：定向 integration tests + `verify constraints` / `close-check`。  
**回退方式**：文档和 surface 对账可独立提交。

## 工作流计划

### 工作流 A：Change runtime pause / resume

**范围**：`change_request -> suspended -> impact analysis -> resume-point -> recover/run`  
**影响范围**：`studios/change_studio.py`、`state_machine.py`、`runner.py`、status/recover surface  
**验证方式**：unit + flow，证明 `resume-point` 可消费  
**回退方式**：保留原 ChangeStudio 产物写盘路径，逐步替换主链消费点

### 工作流 B：Parallel runtime orchestration

**范围**：task split -> assignment freeze -> overlap/merge verify -> integration verify  
**影响范围**：`parallel/engine.py`、`models/state.py`、`gates/extra_gates.py`、`runner.py`  
**验证方式**：parallel unit + flow  
**回退方式**：保持 single-agent fallback 可用

### 工作流 C：Close path integration

**范围**：incident close / knowledge refresh / done-close blocker  
**影响范围**：`knowledge/engine.py`、`gates/extra_gates.py`、`runner.py`、`cli/commands.py`  
**验证方式**：incident + refresh flows  
**回退方式**：以 gate 配置与 runner 绑定点分开提交

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Change request 暂停后可恢复 | `tests/unit/test_studios.py` + 新增 flow | `status/recover` surface 夹具 |
| Maintenance execution path 成为正式真值 | `tests/unit/test_studios.py` | close-check / verify constraints 对账 |
| Parallel assignment freeze + merge verify | `tests/unit/test_parallel.py` | `tests/flow/test_parallel_flow.py` |
| Level 1+ refresh 阻断 completed | `tests/unit/test_gates.py` | `tests/flow/test_knowledge_refresh_flow.py` |
| Incident close 经过 Postmortem Gate | `tests/unit/test_gates.py` | `tests/flow/test_incident_flow.py` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `resume-point` 采用结构化 YAML 还是 canonical string + payload 文件 | 待在 Phase 0 锁定 | Phase 1 |
| parallel coordination artifact 是落在 work-item 目录还是 execution-plan 子目录 | 待锁定 | Phase 2 |
| refresh evidence 由 `knowledge-refresh-log.yaml` 直接承载还是增加 summary artifact | 待锁定 | Phase 3 |

## 实施顺序建议

1. 先补模型与 artifact，避免 Studio / runner 各自发明 payload。
2. 先打通 Change / Maintenance，再推进 Parallel runtime。
3. Knowledge Refresh 与 Incident Close 最后接入 Done/Close，避免中途把主链 gate 打断。
