---
related_doc:
  - "/Users/sinclairpan/project/AgentOps/docs/engineering/agentops-api-gateway-runtime-ingestion.md"
---
# 实施计划：AgentOps production runtime integration

**编号**：`186-agentops-production-runtime-integration` | **日期**：2026-05-26 | **规格**：specs/186-agentops-production-runtime-integration/spec.md

## 概述

本计划把 AgentOps API Gateway runtime ingestion 生产边界落到 Ai_AutoSDLC producer 侧。实现重点是：配置解析、Bearer-only Gateway 发送、安全诊断落盘、receipt/status/retry/doctor 操作面，以及定向测试。现有 AO56 batch builder 保持兼容，不改 AgentOps server 或 Console。

## 技术背景

**语言/版本**：Python 3.11+
**主要依赖**：标准库 `urllib`、Typer、Pydantic、PyYAML、Rich
**存储**：`.ai-sdlc/agentops/outbox/*.json`、`.ai-sdlc/agentops/receipts/*.summary.json`、`.ai-sdlc/agentops/diagnostics/*.json`
**测试**：pytest、Typer CliRunner、ruff
**目标平台**：macOS/Linux/Windows CLI；生产网络调用由操作者显式配置后执行
**约束**：不新增网络依赖；token 只读环境变量；生产 Gateway 模式缺 token 必须 fail closed；诊断不得泄露 token、raw payload、diff 或文件内容。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 只实现 SDLC producer 侧最小生产集成，不实现 Gateway/server/Console。 |
| MUST-2 关键路径必须可验证 | 对配置、发送 header、token 缺失、receipt/diagnostic、CLI status/retry/doctor 建测试。 |
| MUST-3 声明范围、验证与回退 | 本工作项限定 `agentops_bridge`、新增 CLI、测试与 186 文档；可单 commit revert。 |
| MUST-4 状态落盘 | outbox、receipt summary、delivery diagnostic 均落在 `.ai-sdlc/agentops/`。 |
| MUST-5 产品代码与框架隔离 | 只修改 `src/ai_sdlc` 产品代码与 `specs/186` formal docs。 |

## 项目结构

### 文档结构

```text
specs/186-agentops-production-runtime-integration/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/agentops_bridge.py      # 配置、发送、receipt、diagnostic、status 核心逻辑
src/ai_sdlc/cli/agentops_cmd.py          # agentops reporter CLI
src/ai_sdlc/cli/main.py                  # 注册 agentops app
tests/unit/test_agentops_bridge.py       # 核心单元测试
tests/integration/test_cli_agentops.py   # CLI 集成测试
tests/unit/test_command_names.py         # command discovery 覆盖
```

## 阶段计划

### Phase 0：需求冻结与安全边界确认

**目标**：把 AgentOps Gateway 文档转写为 SDLC producer 侧规格。
**产物**：spec.md / plan.md / tasks.md 更新。
**验证方式**：人工对账 AgentOps 文档中的 Required Gateway Behavior、Ai_AutoSDLC Request、Rejection Semantics。
**回退方式**：revert 186 文档变更。

### Phase 1：core runtime 落地

**目标**：实现配置解析、Gateway Bearer 发送、fail-closed、receipt/diagnostic/status。
**产物**：`agentops_bridge.py` 扩展。
**验证方式**：`tests/unit/test_agentops_bridge.py`。
**回退方式**：revert core/test 变更，保留既有 AO56 batch builder 行为。

### Phase 2：CLI reporter 落地

**目标**：提供 status/doctor/retry 操作入口。
**产物**：`agentops_cmd.py`、`main.py`、CLI tests、command discovery test。
**验证方式**：`tests/integration/test_cli_agentops.py`、`tests/unit/test_command_names.py`。
**回退方式**：移除 Typer app 注册与新增 CLI 文件。

### Phase 3：约束验证与归档

**目标**：运行定向验证、ruff、约束检查，更新 execution log 与 handoff。
**产物**：task-execution-log.md、`.ai-sdlc/state/codex-handoff.md`。
**验证方式**：`uv run ai-sdlc verify constraints`。
**回退方式**：revert 本工作项单 commit。

## 工作流计划

### 工作流 A：Gateway producer safety

**范围**：配置、send request、token redaction、HTTP/schema/transport diagnostic。
**影响范围**：`src/ai_sdlc/core/agentops_bridge.py`。
**验证方式**：单元测试 monkeypatch `urllib.request.urlopen` 捕获 request。
**回退方式**：恢复原 `send_agentops_batch`。

### 工作流 B：Reporter operations

**范围**：`agentops status`、`agentops doctor`、`agentops retry`。
**影响范围**：`src/ai_sdlc/cli/agentops_cmd.py`、`src/ai_sdlc/cli/main.py`。
**验证方式**：Typer CliRunner JSON/text 输出测试。
**回退方式**：移除 app 注册与新增文件。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Gateway Bearer request | unit test 捕获 Request headers/body | ruff |
| token 缺失 fail-closed | unit test + CLI doctor test | diagnostic JSON 对账 |
| receipt/diagnostic 落盘 | unit test 读取 `.ai-sdlc/agentops/` | CLI status JSON |
| retry 使用持久化 outbox | CLI dry-run integration test | status latest outbox |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| AgentOps live Gateway endpoint/token 是否可用于 smoke | 后续环境验证，不阻塞本仓库 PR | 无 |
| Gateway rate limit/timeout 的最终生产值 | 由部署配置提供，本仓库默认 10 秒 | 无 |

## 实施顺序建议

1. 更新 186 formal docs，确认 scope 与 AgentOps Gateway 文档一致。
2. 编写/调整 `agentops_bridge` 单元测试，覆盖安全发送与诊断。
3. 实现 core runtime 配置、delivery、status。
4. 新增 CLI reporter 与集成测试。
5. 运行定向测试、ruff、constraints，更新 execution log/handoff。
