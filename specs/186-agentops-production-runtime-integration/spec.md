# 功能规格：AgentOps production runtime integration

**功能编号**：`186-agentops-production-runtime-integration`
**创建日期**：2026-05-26
**状态**：草稿
**输入**：`/Users/sinclairpan/project/AgentOps/docs/engineering/agentops-api-gateway-runtime-ingestion.md`

**范围**：本工作项把 AgentOps AO57 API Gateway runtime ingestion 生产边界落到 Ai_AutoSDLC producer 侧。Ai_AutoSDLC 必须继续生成 AO56 `runtime.ingestion.v1` batch，但生产发送只能面向 Gateway endpoint，并通过 `Authorization: Bearer <AGENTOPS_INGESTION_TOKEN>` 认证；token 不得进入 JSON payload，客户端不得发送或伪造 `X-AgentOps-*` 身份头。

**明确不覆盖**：不实现 AgentOps API Gateway、AgentOps Console UI、AgentOps server auth enforcement，也不把 live smoke 绑定为本仓库 PR 的必过门禁；跨仓库真实联调作为后续环境验证入口。

## 用户场景与测试（必填）

### 用户故事 1 - 生产 Gateway 安全发送（优先级：P0）

作为 Ai_AutoSDLC runtime producer，我希望 runtime outbox 发送到 AgentOps Gateway 时只使用 Bearer token 认证，以便 AgentOps 由可信 Gateway 注入上游身份，而不是信任客户端提交的身份头。

**优先级说明**：AgentOps 文档明确生产边界不接受 end-user supplied identity headers；若 SDLC 侧继续依赖或发送 `X-AgentOps-*`，会破坏生产认证模型。

**独立测试**：单元测试构造发送请求，断言 `Authorization: Bearer ...` 存在、`Content-Type`/`Accept` 正确、请求目标规范化为 `/v1/runtime/events`，且没有任何 `X-AgentOps-*` header。

**验收场景**：

1. **Given** 配置中存在 Gateway endpoint 和 token，**When** Ai_AutoSDLC retry outbox，**Then** 请求必须发往 `<gateway>/v1/runtime/events` 并携带 Bearer token。
2. **Given** 使用生产模式但 token 缺失，**When** 执行发送，**Then** 系统必须 fail closed，写出诊断，不得发出匿名生产请求。
3. **Given** 调用方传入或历史实现残留 `X-AgentOps-*` header，**When** 构建请求，**Then** 客户端请求不得包含这些身份头。

### 用户故事 2 - outbox/receipt/diagnostic 状态可恢复（优先级：P0）

作为框架维护者，我希望每次 outbox 发送、失败和 receipt 都落盘，以便中断后可以查看状态、重试并排查 Gateway/AgentOps 拒绝原因。

**优先级说明**：宪章 MUST-4 要求运行时状态落盘；AgentOps rejection semantics 也要求 receipt 和 diagnostic 可审计且不泄露 token、payload body 或文件内容。

**独立测试**：单元测试验证 receipt summary 和 delivery diagnostic 写入 `.ai-sdlc/agentops/`，HTTP auth/schema/transport 错误不会把 Bearer token 或 raw payload 写入消息与诊断。

**验收场景**：

1. **Given** Gateway 返回 `202 runtime_outbox_receipt.v1`，**When** 发送完成，**Then** receipt summary 写入 `.ai-sdlc/agentops/receipts/`。
2. **Given** Gateway 返回 `401 UPSTREAM_IDENTITY_REQUIRED`，**When** 发送失败，**Then** diagnostic 写入 `.ai-sdlc/agentops/diagnostics/` 且包含 retry guidance。
3. **Given** outbox 已存在且发送失败，**When** 用户运行 status，**Then** 能看到 latest outbox、latest receipt、latest diagnostic 和下一步建议。

### 用户故事 3 - reporter CLI status/retry/doctor（优先级：P1）

作为操作者，我希望通过 Ai_AutoSDLC CLI 查看 AgentOps runtime integration 状态、重试本地 outbox，并诊断配置是否满足生产 Gateway 要求。

**优先级说明**：生产集成需要可操作入口；但首要风险仍是安全发送和状态落盘，因此 reporter CLI 排在 P1。

**独立测试**：集成测试通过 Typer runner 覆盖 `ai-sdlc agentops status --json`、`ai-sdlc agentops doctor --json` 和 `ai-sdlc agentops retry --outbox-id ... --dry-run`。

**验收场景**：

1. **Given** endpoint/token 已配置，**When** 运行 `agentops doctor --json`，**Then** 输出 `ready=true` 且 token 仅显示是否存在。
2. **Given** token 缺失，**When** 运行 `agentops doctor --json`，**Then** 输出 `ready=false` 与 `missing_token`，不输出 token 值。
3. **Given** outbox JSON 已落盘，**When** 运行 `agentops retry --dry-run`，**Then** CLI 只验证配置和 outbox 解析，不发网络请求。

### 边界情况

- Endpoint 既可能是 Gateway 根 URL，也可能已包含 `/v1/runtime/events`，规范化后必须只出现一次 route。
- 本地开发可配置为 `direct_local` 且允许无 token；生产 Gateway 模式必须要求 token。
- HTTP 错误体可能包含服务端诊断，但持久化前必须过滤 token、credential secret、raw payload 等敏感内容。
- Receipt item diagnostics 只持久化 event id/state/code/message/retryable 等摘要字段，不持久化 payload body。
- 重试必须使用已落盘 outbox，不重新生成 batch，避免 replay 时 idempotency key 漂移。

## 需求（必填）

### 功能需求

- **FR-186-001**：系统必须提供 AgentOps runtime ingestion 配置解析，支持环境变量和 `.ai-sdlc/project/config/project-config.yaml` 中的 endpoint、mode、timeout 与 token env var 名称。
- **FR-186-002**：系统必须在 `gateway` 模式下要求 Bearer token；token 只能来自环境变量，且不得写入任何 outbox、receipt、diagnostic 或 CLI JSON。
- **FR-186-003**：系统发送 AgentOps runtime batch 时必须使用 `Authorization: Bearer <token>`、`Content-Type: application/json`、`Accept: application/json`，且不得发送 `X-AgentOps-*` 客户端身份头。
- **FR-186-004**：系统必须保留 AO56 `runtime.ingestion.v1` payload，不把 token 或 Gateway identity 信息放入 JSON body。
- **FR-186-005**：系统必须把 outbox delivery receipt summary 写入 `.ai-sdlc/agentops/receipts/`。
- **FR-186-006**：系统必须把 HTTP、schema、transport、配置错误诊断写入 `.ai-sdlc/agentops/diagnostics/`，并给出 retry guidance。
- **FR-186-007**：系统必须提供 `ai-sdlc agentops status`、`ai-sdlc agentops doctor`、`ai-sdlc agentops retry` reporter commands。
- **FR-186-008**：系统必须让 `agentops retry` 从持久化 outbox 读取 batch 并重用原 outbox id/batch id。

### 关键实体（如涉及数据则必填）

- **AgentOpsIngestionConfig**：producer 侧 runtime ingestion 配置，包含 endpoint、mode、token env var、timeout 与 readiness 状态。
- **AgentOpsDeliveryDiagnostic**：一次发送失败或诊断结论的可持久化摘要，不包含 token 或 raw payload。
- **AgentOpsOutboxStatus**：本地 outbox/receipt/diagnostic 的最新状态视图，用于 CLI status。

## 成功标准（必填）

### 可度量结果

- **SC-186-001**：新增/调整测试覆盖 Gateway Bearer header、禁止 `X-AgentOps-*` header、token 缺失 fail-closed、receipt 和 diagnostic 落盘。
- **SC-186-002**：`uv run pytest tests/unit/test_agentops_bridge.py tests/integration/test_cli_agentops.py tests/unit/test_command_names.py -q` 通过。
- **SC-186-003**：`uv run ruff check src/ai_sdlc/core/agentops_bridge.py src/ai_sdlc/cli/agentops_cmd.py tests/unit/test_agentops_bridge.py tests/integration/test_cli_agentops.py tests/unit/test_command_names.py` 通过。
- **SC-186-004**：`uv run ai-sdlc verify constraints` 无 BLOCKER。
