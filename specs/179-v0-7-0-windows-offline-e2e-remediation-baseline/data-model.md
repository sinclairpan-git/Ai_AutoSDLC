# 数据模型：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**日期**：2026-04-24

## CommandResolution

用于记录 Python runtime 实际执行的命令解析结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `requested_command` | string | 逻辑命令，例如 `npm`、`npx`、`pnpm` |
| `resolved_executable` | string | 实际执行文件，例如 `C:\Program Files\nodejs\npm.cmd` |
| `resolution_strategy` | enum | `windows_pathext`、`which`、`explicit_path`、`not_found` |
| `platform` | string | `windows`、`darwin`、`linux` |
| `pathext` | list[string] | Windows 下参与解析的 PATHEXT 摘要 |
| `diagnostic` | string | 失败或降级原因 |

## FrontendDependencyMode

描述 managed delivery 当前是否真正离线。

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | enum | `offline_strict`、`enterprise_registry`、`public_registry` |
| `registry_url` | string | 允许访问的 registry |
| `cache_required` | bool | 是否必须存在本地缓存/tarball |
| `network_allowed` | bool | 是否允许网络访问 |
| `runtime_artifacts_required` | list[string] | 例如 Playwright browser runtime |
| `preflight_status` | enum | `ready`、`blocked`、`warning` |

## DependencyInstallAttempt

记录一次依赖安装尝试。

| 字段 | 类型 | 说明 |
|------|------|------|
| `attempt_id` | string | 稳定 id |
| `action_id` | string | 对应 delivery action |
| `package_manager` | string | `npm`、`pnpm`、`yarn` |
| `command_resolution` | CommandResolution | 命令解析结果 |
| `working_directory` | string | 执行 cwd |
| `packages` | list[string] | 目标包 |
| `registry_url` | string | registry |
| `exit_code` | int? | 进程退出码 |
| `exception_type` | string | 例如 `FileNotFoundError` |
| `stdout_ref` | string | stdout 摘要或 artifact ref |
| `stderr_ref` | string | stderr 摘要或 artifact ref |
| `retry_count` | int | 重试次数 |
| `classification` | enum | `command_not_found`、`registry_unreachable`、`auth_failed`、`package_not_found`、`install_failed`、`verified` |

## ManagedDeliveryActionState

描述 action 执行、跳过和被依赖阻断的真实状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| `action_id` | string | action id |
| `action_type` | string | dependency install / artifact generate 等 |
| `status` | enum | `succeeded`、`failed`、`dependency_blocked`、`skipped` |
| `blocked_by_action_id` | string? | 被哪个 action 阻断 |
| `failure_classification` | string | 结构化失败分类 |
| `recovery_command` | string | 可复制恢复命令 |

## AdapterIngressTruth

统一 adapter 状态展示和 gate 判定。

| 字段 | 类型 | 说明 |
|------|------|------|
| `activation_state` | string | installed / acknowledged 等 |
| `ingress_state` | string | verified_loaded / materialized / degraded / unsupported |
| `canonical_path` | string | AGENTS.md / IDE 规则文件 |
| `canonical_consumption_result` | string | verified / unverified |
| `verification_evidence` | string | env 或 machine-verifiable proof |
| `dry_run_materialized` | bool | dry-run 是否写入 adapter 文件 |
| `degrade_reason` | string | 降级原因 |

## WorkitemGenerationProfile

区分 framework self-development 和业务项目模板。

| 字段 | 类型 | 说明 |
|------|------|------|
| `profile_id` | enum | `framework_formal`、`business_delivery` |
| `slug_strategy` | enum | `ascii_slug`、`fallback_sequence`、`transliteration` |
| `input_summary` | string | 用户输入摘要 |
| `generated_story_refs` | list[string] | 生成的用户故事 |
| `generated_task_refs` | list[string] | 生成的业务任务 |

## TelemetryGateRecord

将 program gate 结果接入 telemetry。

| 字段 | 类型 | 说明 |
|------|------|------|
| `gate_id` | string | managed delivery / browser gate / final proof |
| `latest_artifact_id` | string | latest artifact id |
| `violation_id` | string? | open violation id |
| `status` | enum | `passed`、`blocked`、`incomplete`、`resolved` |
| `source_artifact_ref` | string | 原始 artifact |
| `resolved_at` | datetime? | 关闭时间 |

## ReleaseE2EProof

发布级 E2E 证据。

| 字段 | 类型 | 说明 |
|------|------|------|
| `asset_name` | string | zip/tar.gz |
| `asset_sha256` | string | release asset hash |
| `platform` | string | OS/arch |
| `scenario_id` | string | enterprise/public |
| `commands` | list[string] | 执行命令 |
| `artifacts` | list[string] | 关键证据路径 |
| `result` | enum | `passed`、`failed`、`blocked` |
| `known_issue_refs` | list[string] | 对应 E2E-WIN id |
