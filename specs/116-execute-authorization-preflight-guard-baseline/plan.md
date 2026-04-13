---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "docs/框架自迭代开发与发布约定.md"
  - "USER_GUIDE.zh-CN.md"
  - "src/ai_sdlc/rules/pipeline.md"
  - "src/ai_sdlc/core/workitem_truth.py"
---
# 实施计划：Execute Authorization Preflight Guard Baseline

**编号**：`116-execute-authorization-preflight-guard-baseline` | **日期**：2026-04-13 | **规格**：specs/116-execute-authorization-preflight-guard-baseline/spec.md

## 概述

`116` 的交付目标是把 `plan freeze != execute authorization` 从文档规则落成稳定的仓库真值。推荐实现方式是在现有 `workitem truth-check` 基础上新增一个可复用的 execute authorization preflight helper，再将它接入 `status --json` 与 `status` 输出，形成可测试、可消费的单一 readiness surface。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：Typer、Rich、Pydantic、本仓库现有 `workitem_truth` / checkpoint / telemetry readiness helpers  
**存储**：`.ai-sdlc/state/checkpoint.yml`、`specs/<WI>/spec.md|plan.md|tasks.md|task-execution-log.md`  
**测试**：`pytest` unit + integration  
**目标平台**：本地 CLI / status surface / bounded JSON consumer  
**约束**：
- 不发明第二套阶段真值，优先复用 `checkpoint.current_stage` 与 `run_truth_check`
- 不从聊天文本反推用户授权，只认仓库内已落盘的 execute readiness
- 输出必须 bounded，避免把 status surface 变成长文解释器

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一真值优先 | 复用 `checkpoint.current_stage` 与 `workitem truth-check`，避免并行状态机 |
| 先证据后结论 | 用 focused unit/integration tests 覆盖 blocker / ready 三类 preflight 结果 |
| 最小实现面 | 只新增 execute authorization helper 与 status surface 接线，不扩展 runner 阶段机 |

## 项目结构

### 文档结构

```text
specs/116-execute-authorization-preflight-guard-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/
├── workitem_truth.py
└── execute_authorization.py        # 新增：active work item execute preflight

src/ai_sdlc/telemetry/
└── readiness.py                    # status --json bounded surface

src/ai_sdlc/cli/
└── commands.py                     # status 表格输出

tests/unit/
└── test_execute_authorization.py   # 新增：preflight core logic

tests/integration/
└── test_cli_status.py              # status / status --json surface regression
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：纠正 `116` formal docs，使其与 `FD-2026-04-07-003` 对齐  
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`  
**验证方式**：文档自检 + `uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `116` 自身 formal docs，不碰 runtime files

### Phase 1：Execute authorization preflight core

**目标**：定义并实现结构化 preflight result，覆盖 `tasks.md` 缺失与 stage 未进入 execute 两类 blocker  
**产物**：`src/ai_sdlc/core/execute_authorization.py`、`tests/unit/test_execute_authorization.py`  
**验证方式**：focused unit tests  
**回退方式**：回退新增 helper 与对应测试

### Phase 2：Status surface integration

**目标**：将 execute authorization preflight 接入 `status --json` 与 `status` 文本输出  
**产物**：`src/ai_sdlc/telemetry/readiness.py`、`src/ai_sdlc/cli/commands.py`、integration tests  
**验证方式**：focused integration tests  
**回退方式**：回退 status surface 接线，保留 core helper

## 工作流计划

### 工作流 A：Preflight truth freeze

**范围**：preflight result schema、reason codes、detail wording  
**影响范围**：`core` 与 `tests/unit`  
**验证方式**：unit tests 覆盖 blocked / ready / unavailable  
**回退方式**：helper 独立回退，不影响其他 status surface

### 工作流 B：Status surface wiring

**范围**：`status --json` payload 与 `status` 文本表格  
**影响范围**：`telemetry/readiness.py`、`cli/commands.py`、`tests/integration/test_cli_status.py`  
**验证方式**：integration tests 验证 bounded JSON 与文本 blocker 呈现  
**回退方式**：移除 `execute_authorization` surface 接线，恢复原有 status 结构

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| 缺少 `tasks.md` 时阻断 execute | unit test | `status --json` integration |
| `tasks.md` 已存在但 stage 仍在 `verify` | unit test | `status` text integration |
| 已进入 `execute` / `close` 时返回 ready | unit test | `status --json` integration |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否需要未来暴露独立 CLI `workitem execute-preflight` | 暂不覆盖 | 不阻塞 |
| 是否需要把该 preflight 接入 `doctor` | 暂不覆盖 | 不阻塞 |

## 实施顺序建议

1. 先冻结 `116` 自身 formal docs，避免继续在错误题目上写代码
2. 先写 failing unit/integration tests，确认缺口真实可复现
3. 实现 execute authorization preflight helper
4. 将 helper 接入 `status --json` 与 `status`
5. 跑 focused verification，并回填 `task-execution-log.md`
