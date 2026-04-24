# 技术调研：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**日期**：2026-04-24

## 决策 D1：跨平台包管理器命令解析

**结论**：新增内部 command resolver，Windows 下显式解析 `.cmd` / `.exe` shim，macOS/Linux 保持裸命令或 `shutil.which` 解析结果。不得用 `shell=True` 作为主方案。

**依据**：
- Windows Python `CreateProcess` 不等同于 PowerShell/cmd shell 解析。
- E2E 中 `where npm` 可找到 `npm.cmd`，但 `subprocess.run(["npm", ...])` 失败为 `[WinError 2]`。
- `npx`、`pnpm`、`yarn`、`corepack` 与 npm 有同类风险。

**备选方案**：
- `shell=True`：放弃，跨平台 quoting 和注入风险更高。
- 强制用户在 PowerShell 中运行 npm：放弃，managed delivery 是 Python runtime 触发，不应依赖用户 shell。

## 决策 D2：前端依赖执行模式

**结论**：把前端依赖执行模式分为 `offline_strict`、`enterprise_registry`、`public_registry`。

**语义**：
- `offline_strict`：不得访问公网或企业 registry；缺缓存时 mutate 前 fail-fast。
- `enterprise_registry`：允许访问企业 registry；必须记录 registry URL、认证/代理前置、包存在性和错误分类。
- `public_registry`：允许访问公共 npm registry；必须记录代理、lockfile、node_modules resolution 和 browser runtime 下载证据。

**依据**：当前“离线包”只覆盖 Python/CLI 安装，不覆盖前端依赖闭环；如果不显式分模式，用户会误以为 managed frontend 也是离线可完成。

## 决策 D3：失败 artifact 合同

**结论**：P0/P1 failure artifact 必须既是人可读的错误报告，也是 agent 可执行的恢复 contract。

**最小字段**：
- `attempted_command`
- `resolved_executable`
- `cwd`
- `package_manager`
- `registry_url`
- `env_summary`，至少包含 PATH/PATHEXT 诊断摘要
- `stdout_ref` / `stderr_ref` 或内联裁剪
- `exception_type`
- `retry_count`
- `blocked_downstream_action_ids`
- `plain_language_blockers`
- `recommended_next_steps`
- `recovery_command`

## 决策 D4：业务 work item 模板隔离

**结论**：framework self-development 与普通业务项目必须使用不同模板。普通业务输入不能再默认生成 direct-formal 框架任务。

**依据**：E2E 输入“订单运营管理台”，但生成任务仍是 `direct-formal baseline freeze`，这会让 close-check 对错误目标收口。

## 决策 D5：adapter 状态机一致性

**结论**：adapter surface 必须同时展示 activation、ingress、canonical path、canonical consumption、evidence、degrade reason。`run --dry-run` 是否写入 adapter 文件必须变成显式 contract。

**依据**：E2E 中 project-config、status、dry-run、mutate gate 对同一状态给出不同口径，容易让用户误以为治理已加载。

## 决策 D6：遥测与 violation 真值

**结论**：managed delivery、browser gate、baseline、persisted write proof、final proof 均应注册 latest artifact；P0/P1 未闭环应形成 open violation 或 equivalent unresolved evidence item。

**依据**：E2E 中 latest artifacts 与 open violations 为空，但实际前端闭环失败。

## 决策 D7：发布证据级别

**结论**：release notes 的闭环声明必须以 release asset 级 E2E 为证据，不得只引用源码仓库测试。

**依据**：V0.7.0 Windows zip 现场未完成前端闭环，但文档表述强于证据。
