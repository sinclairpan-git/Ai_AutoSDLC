# 功能规格：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**状态**：草案（待评审）
**创建日期**：2026-04-24
**输入**：[`../../docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md`](../../docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md)、`.ai-sdlc/memory/constitution.md`

> 口径：本 work item 只负责把 V0.7.0 Windows 离线包 E2E 缺陷归档转入正式 SDLC 修复流程。它不在同一批里直接修复全部代码，而是先冻结需求边界、设计决策、任务拆分、验收证据和回归路径，后续实现必须按 `tasks.md` 分批推进。

## 问题定义

V0.7.0 Windows 离线包 E2E 已证明：CLI 安装、基础初始化、solution confirmation 可以走通，但 Windows 普通用户路径无法完成真实前端托管交付闭环。两条组件库路径均失败在 `dependency-install`，前端代码未落盘，browser gate、baseline、final proof 和 close-stage readiness 均没有形成完整证据。

这不是单点 bug。缺陷归档已经拆出 22 个问题，覆盖以下失败簇：

1. Windows 包管理器执行与前端依赖模式失败：`E2E-WIN-007`、`E2E-WIN-008`、`E2E-WIN-020`
2. 业务需求录入与任务分解断链：`E2E-WIN-004`、`E2E-WIN-005`
3. adapter 状态机与治理加载证据不一致：`E2E-WIN-003`
4. 公共/企业组件库真实安装与 provider 隔离未验证：`E2E-WIN-009`、`E2E-WIN-010`、`E2E-WIN-019`
5. browser gate、verify constraints、final proof 与 telemetry 证据缺口：`E2E-WIN-011`、`E2E-WIN-012`、`E2E-WIN-017`、`E2E-WIN-021`、`E2E-WIN-022`
6. Windows 新用户体验和收口前置条件不足：`E2E-WIN-001`、`E2E-WIN-002`、`E2E-WIN-006`、`E2E-WIN-013`、`E2E-WIN-014`、`E2E-WIN-015`、`E2E-WIN-016`
7. 发布口径强于 release asset 级证据：`E2E-WIN-018`

## 范围

### 覆盖

- 修复 Windows 下 `npm`、`npx`、`pnpm`、`yarn`、`corepack` 的跨平台命令解析策略
- 定义前端依赖执行模式：`offline_strict`、`enterprise_registry`、`public_registry`
- 让 managed delivery 失败 artifact 对人和 AI agent 都可执行
- 让下游 action 正确标记为 `dependency_blocked`
- 修复中文标题 work item id 生成与业务需求任务分解
- 修复 adapter status、dry-run、mutate gate、project-config 的状态口径
- 将 managed delivery、browser gate、baseline、persisted write proof、final proof 接回 telemetry/open violation 证据链
- 补齐公共 PrimeVue 与企业 Vue2 两条路径的真实安装、运行时、browser gate 与 release asset 级回归证据
- 修正 release notes、README、USER_GUIDE 中强于证据的表述

### 不覆盖

- 不在本 work item 中引入新的前端 UI 框架或替换现有 provider 体系
- 不改变宪章中 docs/dev 分支纪律
- 不把企业私有 registry 凭证写入仓库
- 不把 Windows 专用 shell hack 作为跨平台通用方案
- 不把 release asset E2E 伪装成源码仓库单元测试已经覆盖的事实

## 用户故事

### US-179-001：Windows 普通用户可以从离线包进入真实前端闭环

作为 Windows 普通用户，我希望离线包安装后能明确知道哪些步骤离线、哪些步骤需要 npm registry，并且在依赖安装失败时得到可复制的恢复命令，以便我能完成 managed delivery、browser gate、baseline 和 final proof。

### US-179-002：AI-Coding agent 可以从 artifact 自动判断下一步

作为 AI-Coding agent，我希望 managed delivery 失败 artifact 记录 attempted command、resolved executable、cwd、env 摘要、下游阻断 action 和恢复命令，以便我不需要猜测 `[WinError 2]` 的真实含义。

### US-179-003：中文业务需求会生成业务相关任务

作为中文用户，我希望 `workitem init --title "订单运营管理台"` 能生成合法 work item id，并且 `spec.md/tasks.md` 的主语是订单业务交付，而不是框架 direct-formal 自开发模板。

### US-179-004：发布负责人可以用 release asset 级证据支撑发布声明

作为发布负责人，我希望 Windows zip、macOS/Linux 包分别有可追溯 E2E 证据，以便 release notes 中的“release-grade”声明可被 artifact、日志和 telemetry 证明。

## 功能需求

| ID | 需求 |
|----|------|
| FR-179-001 | 系统必须在 Windows 下解析 npm 系列 `.cmd` shim，并保持 macOS/Linux 裸命令行为不退化 |
| FR-179-002 | 系统必须在 managed delivery mutate 前明确当前前端依赖模式：`offline_strict`、`enterprise_registry` 或 `public_registry` |
| FR-179-003 | `offline_strict` 缺少前端依赖缓存或 Playwright runtime 时必须 fail-fast，不得进入部分写入 |
| FR-179-004 | managed delivery failure artifact 必须记录 command、resolved executable、cwd、env 摘要、stdout/stderr、exception、retry count、blocked downstream actions 和 recovery command |
| FR-179-005 | dependency failure 后，`visual-regression-runtime-install`、`artifact-generate`、`workspace-integration` 等下游 action 必须标记为 `dependency_blocked` 或等价结构化状态 |
| FR-179-006 | 中文标题无 ASCII slug 时必须自动生成合法稳定 work item id，或给出可复制 `--wi-id` 重试命令 |
| FR-179-007 | 普通业务项目的 `workitem init --input` 必须生成与输入业务相关的 spec/plan/tasks，不得默认使用 framework direct-formal 自开发任务 |
| FR-179-008 | adapter status、project-config、dry-run、mutate gate 必须使用一致的 activation/ingress/canonical consumption 判定口径 |
| FR-179-009 | `run --dry-run` 如果会物化 adapter 文件，必须显式声明；若承诺只读，则不得写入 |
| FR-179-010 | managed delivery、browser gate、baseline、persisted write proof、final proof 的 latest artifact 必须进入 telemetry index，并在失败时形成 open violation 或等价未闭环证据 |
| FR-179-011 | 公共 PrimeVue 路径必须验证 package manifest、lockfile、node_modules resolution、runtime import 和 browser rendering |
| FR-179-012 | 企业 Vue2 路径必须区分命令不可执行、registry 不可达、认证失败、包不存在和版本冲突 |
| FR-179-013 | 企业 provider 生成 payload 不得出现 `publicPrimeVue*` 等公共 provider 专有符号 |
| FR-179-014 | `verify constraints` 和 `final-proof-publication` 在前端闭环失败时不得输出误导性绿色完成语义 |
| FR-179-015 | Git preflight 必须覆盖无 Git、`master`、`main`、自定义默认分支四类空项目状态 |
| FR-179-016 | Windows release asset 必须校验 zip 内脚本中文内容、PowerShell 输出编码和 README 下一步命令 |
| FR-179-017 | release docs 中每个闭环声明必须回链到 release asset 级 E2E 证据 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-179-001 | Windows 上 `subprocess.run(["npm.cmd", "--version"])` 等效路径被框架 resolver 自动选择，`["npm", ...]` 不再导致 managed delivery 停在 `[WinError 2]` |
| SC-179-002 | 两条 E2E 场景均生成 `managed/frontend/index.html`、`src/App.vue`、`src/generated/frontend-delivery-context.ts`、lockfile 和 dependency resolution 证据 |
| SC-179-003 | 公共 PrimeVue 场景 browser gate 有截图、baseline promotion 和二次 probe pass 或明确 visual blocker |
| SC-179-004 | 企业 Vue2 场景至少能进入 registry/认证/包名层面的真实错误分类；在具备 registry 条件时形成成功安装证据 |
| SC-179-005 | 中文标题和中文输入生成的 `spec.md/tasks.md` 可追溯到业务对象、前后端交付和验收命令 |
| SC-179-006 | P0/P1 失败 artifact 的 `plain_language_blockers` 和 `recommended_next_steps` 非空，AI agent 可从 artifact 直接恢复 |
| SC-179-007 | telemetry latest artifacts/open violations 与 managed delivery/browser gate/final proof 状态一致 |
| SC-179-008 | Windows zip release smoke 从解压开始执行，不依赖源码仓库环境，并产出可归档报告 |

## 依赖和追踪

- 上游缺陷归档：`docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md`
- 相关能力：`101` managed delivery apply runtime、`103/125/143` browser gate runtime、`121/122/159/160/162/163` adapter ingress/canonical consumption、`140/141` program truth ledger、`178` visual regression drift
- 主要修复文件预计见 `plan.md` 和 `tasks.md`

---
related_doc:
  - "docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md"
frontend_evidence_class: "framework_capability"
---
