---
related_doc:
  - "docs/engineering/ai-sdlc-agentops-e2e-smoke.md"
---
# 实施计划：AgentOps self-iteration monitoring

**编号**：`187-agentops-self-iteration-monitoring` | **日期**：2026-05-27 | **规格**：specs/187-agentops-self-iteration-monitoring/spec.md

## 概述

本计划将 Ai_AutoSDLC 自迭代运行事实稳定上报到本地 AgentOps。AgentOps 只作为旁路观测系统，用于质量分析；AI-SDLC 自身的 stage/gate/task guard 仍是唯一开发治理来源。

## 技术背景

**语言/版本**：Python 3.11
**主要依赖**：Typer CLI、AgentOps Gateway runtime ingestion contract、现有 `agentops_bridge`
**存储**：`.ai-sdlc/agentops/outbox`、`.ai-sdlc/agentops/receipts`、`.ai-sdlc/agentops/diagnostics`
**测试**：focused ruff、`tests/integration/test_cli_run.py`、`tests/unit/test_agentops_bridge.py`、`tests/integration/test_cli_agentops.py`
**目标平台**：本地 macOS workspace + local AgentOps compose
**约束**：token 只进入 Authorization Bearer header，不落 JSON；不发送 `X-AgentOps-*` 身份头；不改变 gate 放行语义。

## 宪章检查

| 宪章门禁 | 计划响应 |
| --- | --- |
| 自身治理不可绕过 | 真实 `ai-sdlc run` 仍按 close gate 阻断或放行，AgentOps 只记录旁路事实。 |
| 证据必须可对账 | 使用 SDLC receipt、AgentOps Postgres、trace、evidence summary、Gateway audit、Console workbench 双边核对。 |
| 敏感信息不得落盘 | doctor/status/outbox/receipt/diagnostic 只记录 token present，不记录 token 值。 |
| verified_loaded 不得越权 | Console 中 `verified_loaded` 仍只作为 diagnostic 语义，不作为 L5 或代码修改授权。 |

## 项目结构

```text
src/ai_sdlc/cli/run_cmd.py
src/ai_sdlc/core/agentops_bridge.py
tests/integration/test_cli_run.py
specs/187-agentops-self-iteration-monitoring/
  spec.md
  plan.md
  tasks.md
  task-execution-log.md
```

## 阶段计划

### Phase 0：正式工作项与 guard 对齐

**目标**：建立 187 工作项并链接 checkpoint，使当前代码修改有明确 executable task。
**产物**：spec/plan/tasks/log。
**验证方式**：`uv run ai-sdlc workitem guard --json`。
**回退方式**：删除 187 工作项并恢复 checkpoint linkage。

### Phase 1：AgentOps run payload 补齐

**目标**：补齐 gate event 的 task/title/path/guard/blocking 字段，并支持 producer identity env。
**产物**：`run_cmd.py`、`agentops_bridge.py`、focused tests。
**验证方式**：focused pytest + ruff。
**回退方式**：恢复 reporter payload 到原最小 gate event。

### Phase 2：真实本地上报与 Ops readback

**目标**：用真实 `uv run ai-sdlc run` 产生并发送 outbox，记录 AgentOps 对账结果。
**产物**：receipt summary、trace/evidence/console/Postgres/Gateway audit 摘要。
**验证方式**：`ai-sdlc agentops doctor/status` + AgentOps local API readback。
**回退方式**：保留 outbox/diagnostic，按 diagnostic retry guidance 修复。

### Phase 3：企业 opt-in 与个人默认静默

**目标**：同一发行包同时支持个人单机和企业 AgentOps required 接入；个人默认不连接 Ops，企业通过轻量脚本写入 profile 后强制上报。
**产物**：enterprise profile 读取、`ai-sdlc enterprise configure`、required 模式阻断、独立企业接入文档。
**验证方式**：focused pytest + ruff，覆盖个人默认无 outbox、profile required、token 缺失阻断。
**回退方式**：恢复 AgentOps reporter 到显式 env-only 旁路行为。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
| --- | --- | --- |
| token 安全 | 本地 token 字面值不得出现在 `.ai-sdlc/...` | doctor JSON 只显示 token_present |
| payload 字段 | focused integration test 捕获 batch | AgentOps trace/console readback |
| delivery | receipt delivered accepted/deduplicated > 0 | Postgres receipt 与 Gateway audit |
| governance | workitem guard + close gate | run halt reason 记录为质量信号 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
| --- | --- | --- |
| close gate 当前因 final tests/truth snapshot stale 失败 | open | release/close，不阻塞旁路观测 |
| evidence summary 缺 model/tool/artifact span | resolved | `ai-sdlc run` batch now emits summary-only `trace_span.v1` model span plus SDLC verification/tool and artifact events. |
