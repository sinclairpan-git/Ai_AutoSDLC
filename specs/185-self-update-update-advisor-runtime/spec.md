# 功能规格：Self-update / Update Advisor Runtime

**功能编号**：`185-self-update-update-advisor-runtime`  
**创建日期**：2026-05-01  
**状态**：implementation in progress  
**输入**：[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、用户要求“找到之前的关于更新提醒的需求描述，进行完整落地；先做自动检测 + 明确提醒 + 显式更新命令”

## 目标

把 `093` 的 docs-only update advisor contract 落成可执行 runtime：

- installed CLI runtime 在 Stage 0 自动评估 update advisor
- GitHub stable release 高于本机版本时输出明确提醒
- `github-archive` 渠道给出显式更新命令入口
- `unknown` / `pipx` / `pip-user` 在没有可靠 channel truth 时只给轻提醒
- `uv run`、`python -m ai_sdlc`、editable/source runtime 保持安静
- 网络失败、解析失败、缓存损坏、backoff 均不阻断主命令

## 范围

### In Scope

- 新增 update advisor 核心 runtime、用户级缓存、freshness/backoff、notice ack 去重
- 新增 `ai-sdlc self-update` 子命令：
  - `identity`
  - `evaluate`
  - `check`
  - `ack-notice`
  - `instructions`
- 在全局 CLI callback 中接入 Stage 0 update notice
- 补单元测试与 CLI 集成测试

### Out Of Scope

- 默认静默升级或自动替换正在运行的 CLI
- 企业内部源 / PyPI channel latest truth
- IDE/AI 外部宿主直接联网；本批只提供 helper machine contract，宿主可后续绑定

## 验收标准

- `github-archive` 安装态 + fresh GitHub stable release 高于已装版本时，`evaluate` 返回 `light_upstream_release_notice` 和 `actionable_cli_update_notice`
- `unknown` 渠道只返回 `light_upstream_release_notice`
- source/editable/`python -m`/`uv run` 不触发 update notice
- 连续网络失败进入 backoff，下一次命令不重复联网
- 交互 CLI 自动提醒后写入 ack，下一次相同版本不重复提醒
- `self-update instructions --version <version>` 输出平台资产名与显式下载/安装步骤
