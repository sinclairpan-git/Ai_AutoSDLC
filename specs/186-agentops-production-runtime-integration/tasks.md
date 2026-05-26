---
related_doc:
  - "/Users/sinclairpan/project/AgentOps/docs/engineering/agentops-api-gateway-runtime-ingestion.md"
---
# 任务分解：AgentOps production runtime integration

**编号**：`186-agentops-production-runtime-integration` | **日期**：2026-05-26
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal production boundary freeze
Batch 2: core Gateway ingestion runtime
Batch 3: reporter CLI operations
Batch 4: verification and archive
```

---

## Batch 1：formal production boundary freeze

### Task 1.1 冻结 Gateway ingestion producer 侧规格

- **任务编号**：T186-1.1
- **优先级**：P0
- **依赖**：无
- **文件**：specs/186-agentops-production-runtime-integration/spec.md, plan.md, tasks.md
- **可并行**：否
- **验收标准**：
  1. 文档引用 `agentops-api-gateway-runtime-ingestion.md`
  2. scope 明确 Gateway Bearer token、禁止客户端 `X-AgentOps-*`、receipt/diagnostic 落盘
  3. 明确不覆盖 Gateway/server/Console/live smoke
- **验证**：文档对账

## Batch 2：core Gateway ingestion runtime

### Task 2.1 实现配置解析与 readiness

- **任务编号**：T186-2.1
- **优先级**：P0
- **依赖**：T186-1.1
- **文件**：src/ai_sdlc/core/agentops_bridge.py, tests/unit/test_agentops_bridge.py
- **可并行**：否
- **验收标准**：
  1. 支持 env 与 project-config 中的 endpoint/mode/token env var/timeout
  2. gateway 模式 token 缺失 fail closed
  3. CLI/diagnostic 只暴露 token_present，不暴露 token 值
- **验证**：`uv run pytest tests/unit/test_agentops_bridge.py -q`

### Task 2.2 实现 Bearer 发送与安全诊断落盘

- **任务编号**：T186-2.2
- **优先级**：P0
- **依赖**：T186-2.1
- **文件**：src/ai_sdlc/core/agentops_bridge.py, tests/unit/test_agentops_bridge.py
- **可并行**：否
- **验收标准**：
  1. 请求只发送 Authorization/Content-Type/Accept，不发送 `X-AgentOps-*`
  2. token 不进入 JSON body
  3. HTTP/schema/transport/config 错误写出 redacted diagnostic
  4. 成功 receipt 写入 summary
- **验证**：`uv run pytest tests/unit/test_agentops_bridge.py -q`

## Batch 3：reporter CLI operations

### Task 3.1 新增 agentops status/doctor/retry CLI

- **任务编号**：T186-3.1
- **优先级**：P1
- **依赖**：T186-2.2
- **文件**：src/ai_sdlc/cli/agentops_cmd.py, src/ai_sdlc/cli/main.py, tests/integration/test_cli_agentops.py, tests/unit/test_command_names.py
- **可并行**：否
- **验收标准**：
  1. `agentops status --json` 输出 latest outbox/receipt/diagnostic
  2. `agentops doctor --json` 输出 Gateway readiness 与 redacted config
  3. `agentops retry --dry-run` 验证持久化 outbox 和配置但不发网络请求
  4. command discovery 包含新增命令
- **验证**：`uv run pytest tests/integration/test_cli_agentops.py tests/unit/test_command_names.py -q`

## Batch 4：verification and archive

### Task 4.1 定向验证、约束检查与归档

- **任务编号**：T186-4.1
- **优先级**：P0
- **依赖**：T186-3.1
- **文件**：specs/186-agentops-production-runtime-integration/task-execution-log.md, .ai-sdlc/state/codex-handoff.md
- **可并行**：否
- **验收标准**：
  1. 定向 pytest 与 ruff 通过
  2. `uv run ai-sdlc verify constraints` 无 BLOCKER
  3. execution log 与 handoff 记录当前状态、验证结果、风险和下一步
- **验证**：定向命令 + constraints
