# 执行计划：Frontend Mainline Host Runtime Manager Baseline

**编号**：`096-frontend-mainline-host-runtime-manager-baseline`  
**日期**：`2026-04-12`  
**对应规格**：[`spec.md`](./spec.md)

## 目标

把 `095.Host Readiness` 的首个可实施切片落成一个只读、可机器消费的 `host_runtime_plan` producer：

- 对当前宿主环境做 fail-closed readiness 判定；
- 在不执行下载、安装、升级、回滚的前提下给出 acquisition / remediation 计划；
- 为后续 `095.delivery_execution_confirmation_surface` 提供稳定输入，而不是直接接管执行。

## 当前对账

- `095` 是主线母规格，范围覆盖完整前端交付主线，不适合直接进入实现。
- `096` 明确声明自己是 `095.Host Readiness` 的第一块实现切片，适合作为当前续做目标。
- 当前仓库里 `093` 到 `096` 仍处于“只有 `spec.md`”的状态；`src/ai_sdlc/cli/main.py` 尚未存在 Host Runtime Manager 对应命令面。
- `packaging/offline/install_offline.sh` 与 `packaging/offline/install_offline.ps1` 目前仍是“人工可读现实”，尚未产出或消费 `host_runtime_plan`，这与 `FR-096-044` 一致。

## 实施边界

本次实现允许覆盖：

- 新增 Host Runtime Manager 的核心模型、判定器和序列化输出；
- 在 CLI 中增加一个只读入口，输出 `host_runtime_plan`；
- 为最小宿主、离线 bundle profile 匹配、主线可修复缺口增加测试；
- 补充面向用户的中文说明与执行记录。

本次实现明确不做：

- 实际下载、安装、升级、卸载、回滚；
- `093` 的 installed runtime update advisor 落地；
- `095` 的 delivery execution confirmation surface；
- 在无确认的前提下修改全局 Python / Node / npm / pnpm / Playwright 浏览器或用户源码树。

## 批次规划

### Batch 1：契约与证据模型

产物目标：

- 新增 `host_runtime_plan` 相关数据结构，覆盖：
  - `readiness`
  - `bootstrap_acquisition`
  - `remediation_fragment`
  - `reason_codes`
  - `will_download` / `will_install` / `will_modify` / `will_not_touch`
- 固化平台、架构、installer profile、surface binding 的枚举和证据字段；
- 用测试固定 fail-closed 缺省行为，避免“未知状态被误判为可执行宿主”。

### Batch 2：最小宿主判定器

产物目标：

- 判定 `minimal_executable_host`：
  - OS / arch 是否受支持；
  - Python 是否存在且 `>= 3.11`；
  - AI-SDLC runtime 是否可验证；
  - 当前入口是否是允许绑定到主线交付面的 surface。
- 当最小宿主不成立时，仅输出 acquisition handoff，不进入主线 remediation。
- 识别 `source / uv / python -m / IDE unbound` 等非绑定入口，并按规格落 reason code。

### Batch 3：离线 bundle 与主线可修复缺口

产物目标：

- 识别并映射离线安装脚本可表达的 profile：
  - `offline_bundle_posix_shell`
  - `offline_bundle_windows_powershell`
  - `offline_bundle_windows_bat_launcher`
- 在最小宿主成立时，再单独诊断：
  - Node
  - package manager
  - Playwright browsers
- 对这些缺口仅输出 `mainline_remediable` 片段，不触发执行。

### Batch 4：CLI 接口与文档

产物目标：

- 在 CLI 中注册只读命令面，优先采用 `host-runtime plan --json`；
- 输出单一 `host_runtime_plan` JSON 文档，供后续 `095` 消费；
- 在 `USER_GUIDE.zh-CN.md` 中补充“只诊断、不静默修改”的用户预期；
- 更新 `task-execution-log.md`，记录实现批次和验证结果。

## 计划中的文件落点

- `src/ai_sdlc/core/host_runtime_manager.py`
- `src/ai_sdlc/cli/host_runtime_cmd.py`
- `src/ai_sdlc/cli/main.py`
- `tests/unit/test_host_runtime_manager.py`
- `tests/integration/test_cli_host_runtime.py`
- `USER_GUIDE.zh-CN.md`
- `specs/096-frontend-mainline-host-runtime-manager-baseline/task-execution-log.md`

## 验证命令

在实现批次完成后执行：

```bash
uv run pytest tests/unit/test_host_runtime_manager.py -q
uv run pytest tests/integration/test_cli_host_runtime.py -q
uv run ruff check src/ai_sdlc/core/host_runtime_manager.py src/ai_sdlc/cli/host_runtime_cmd.py tests/unit/test_host_runtime_manager.py tests/integration/test_cli_host_runtime.py
uv run ai-sdlc verify constraints
git diff --check
```

## 完成判定

满足以下条件才可把 `096` 判为进入实现完成态：

1. `host_runtime_plan` 的结构、reason codes、evidence 字段由测试固定；
2. 最小宿主不成立时只给 acquisition / handoff，不发生任何副作用；
3. 最小宿主成立但 Node / 包管理器 / Playwright 缺失时，仅给 `mainline_remediable` 计划；
4. CLI 输出可直接被后续 `095.delivery_execution_confirmation_surface` 消费；
5. 文档与执行记录能解释“为什么没有静默安装”。
