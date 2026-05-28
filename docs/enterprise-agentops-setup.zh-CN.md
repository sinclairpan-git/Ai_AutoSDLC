# 企业 AgentOps 接入指南

本文只面向需要强制接入 AgentOps 的企业或部门用户。个人单机用户不需要执行本文步骤；未配置企业 profile 时，AI-SDLC 默认不连接 AgentOps、不生成 AgentOps outbox、不影响本地 `init/run`。

## 推荐方案

部门内部准备一个轻量 PowerShell 脚本，让企业用户安装最新版 AI-SDLC 后运行一次。脚本完成两件事：

1. 写入用户级企业 profile，声明 AgentOps `required` 模式。
2. 将用户输入的 AgentOps token 写入用户环境变量。

profile 不保存 token，项目仓库也不会保存 token。

## 企业 Profile

AI-SDLC 会自动读取以下 profile：

| 平台 | 默认路径 |
| --- | --- |
| Windows | `%APPDATA%\AI-SDLC\enterprise.yaml` |
| macOS / Linux | `~/.config/ai-sdlc/enterprise.yaml` |

也可以用 `AI_SDLC_ENTERPRISE_PROFILE` 指向自定义路径。

profile 示例：

```yaml
schema_version: ai_sdlc_enterprise_profile.v1
managed: true
enterprise_id: your-dept
agentops_reporting_mode: required
agentops_ingestion_endpoint: https://ops.your-company.internal
agentops_ingestion_mode: gateway
agentops_token_env: AGENTOPS_INGESTION_TOKEN
```

## 一次性接入脚本

Windows PowerShell 示例：

```powershell
$ErrorActionPreference = "Stop"

$EnterpriseId = "your-dept"
$Endpoint = "https://ops.your-company.internal"
$TokenEnv = "AGENTOPS_INGESTION_TOKEN"

ai-sdlc enterprise configure `
  --endpoint $Endpoint `
  --enterprise-id $EnterpriseId `
  --reporting-mode required `
  --token-env $TokenEnv

$Token = Read-Host "Enter AgentOps token" -AsSecureString
$PlainToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
  [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Token)
)
[Environment]::SetEnvironmentVariable($TokenEnv, $PlainToken, "User")

Write-Host "Enterprise AgentOps profile configured. Open a new terminal, then run:"
Write-Host "  ai-sdlc agentops doctor"
```

macOS / Linux 示例：

```bash
#!/usr/bin/env bash
set -euo pipefail

enterprise_id="your-dept"
endpoint="https://ops.your-company.internal"
token_env="AGENTOPS_INGESTION_TOKEN"

ai-sdlc enterprise configure \
  --endpoint "$endpoint" \
  --enterprise-id "$enterprise_id" \
  --reporting-mode required \
  --token-env "$token_env"

printf "Enter AgentOps token: "
stty -echo
read -r token
stty echo
printf "\n"

profile_file="${HOME}/.config/ai-sdlc/agentops.env"
mkdir -p "$(dirname "$profile_file")"
chmod 700 "$(dirname "$profile_file")"
printf 'export %s=%q\n' "$token_env" "$token" > "$profile_file"
chmod 600 "$profile_file"

echo "Add this line to your shell profile, then open a new terminal:"
echo "  source $profile_file"
echo "Then run:"
echo "  ai-sdlc agentops doctor"
```

## 验证

运行：

```powershell
ai-sdlc agentops doctor
ai-sdlc run --dry-run
```

预期结果：

- `agentops doctor` 显示 `ready`。
- `config.reporting_mode` 为 `required`。
- 输出只显示 `token_present: true`，不会显示 token 值。
- `ai-sdlc run` 会向 AgentOps 上报摘要事件。

## Required 模式行为

企业 profile 配置 `agentops_reporting_mode: required` 后：

- `endpoint` 缺失会阻断。
- token 缺失会阻断。
- AgentOps receipt 出现 rejected 或 DLQ 会阻断。
- 成功上报不会改变 AI-SDLC 原有 stage/gate/task guard 语义，只增加企业观测要求。

## 个人用户边界

未执行企业接入脚本、未设置企业 profile 的个人用户：

- 不连接 AgentOps。
- 不生成 `.ai-sdlc/agentops/` outbox 或 diagnostic。
- 不看到 `missing_endpoint` 等企业接入提示。
- 继续按普通 `ai-sdlc init .`、`ai-sdlc run` 使用。
