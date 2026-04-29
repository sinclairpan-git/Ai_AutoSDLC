# 实施计划：V0.7.0 Windows 离线 E2E 修复基线

**编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**日期**：2026-04-24
**规格**：[`spec.md`](./spec.md)
**设计输入**：[`research.md`](./research.md)、[`data-model.md`](./data-model.md)

## 1. 目标

把缺陷归档中的 22 个问题转成可执行、可验证、可收口的正式修复链路。优先恢复 Windows release asset 的真实前端闭环，再补齐 adapter、artifact、telemetry、发布口径和 Windows 新用户体验。

## 2. 宪章响应

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 第一批只处理 P0 闭环阻断：包管理器解析、依赖模式、失败 artifact、业务任务分解 |
| MUST-2 关键路径必须可验证 | 每个批次都要求 unit/integration/E2E 或 release asset 级证据 |
| MUST-3 每次改动声明范围、验证与回退 | `tasks.md` 每个任务列出影响文件、验证命令和回退策略 |
| MUST-4 状态落盘 | managed delivery、browser gate、telemetry、release proof 均要求 artifact 持久化 |
| MUST-5 产品代码与开发框架隔离 | 普通业务 work item 模板和 framework formal 模板必须隔离 |

## 3. 阶段计划

### Phase 0：证据冻结与失败合同

- 冻结 `docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md` 为修复输入
- 将 E2E-WIN id 映射到 FR/SC/任务
- 明确 release asset 级回归证据格式

### Phase 1：P0 Windows 依赖安装与前端依赖模式

- 实现跨平台命令 resolver
- 修复 npm/npx/pnpm/yarn/corepack Windows `.cmd` 解析
- 定义并接入 `offline_strict / enterprise_registry / public_registry`
- 让 dependency failure artifact 包含 agent 可执行恢复信息

### Phase 2：P0 业务 work item 与前端代码落盘语义

- 修复中文标题 work item id 生成
- 隔离 business delivery 模板与 framework formal 模板
- 明确 dependency-install 与 artifact-generate 的执行顺序和失败摘要
- 补足订单业务需求到任务分解的回归样例

### Phase 3：P1 adapter、telemetry 与 proof 链路

- 统一 adapter status、project-config、dry-run、mutate gate 的判定口径
- 定义 dry-run 物化行为
- 将 managed delivery/browser gate/final proof 接入 telemetry index/open violation
- 修复 `verify constraints`、`final-proof-publication` 的误导性绿色输出

### Phase 4：P1 provider 真实安装和 browser gate 闭环

- 公共 PrimeVue 路径补真实安装、runtime import、browser rendering 证据
- 企业 Vue2 路径补 registry/认证/包名错误分类
- 修复企业 payload 混入 public PrimeVue 命名
- 补跑 browser gate、baseline promotion、二次 probe

### Phase 5：P2/P3 Windows 用户体验、Git preflight 与发布口径

- 修复 release asset 脚本中文编码校验
- 增加终端代理、PRD 绑定、Git preflight、默认分支、PowerShell 串联命令说明
- 修正 release notes/README/USER_GUIDE 的闭环声明
- 形成 Windows zip、macOS/Linux 包 release smoke 证据

## 4. 影响范围

- `src/ai_sdlc/core/managed_delivery_apply.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/core/workitem_scaffold.py`
- `src/ai_sdlc/integrations/ide_adapter.py`
- `src/ai_sdlc/cli/adapter_cmd.py`
- `src/ai_sdlc/cli/run_cmd.py`
- `src/ai_sdlc/cli/verify_cmd.py`
- `src/ai_sdlc/branch/git_client.py`
- `src/ai_sdlc/core/branch_inventory.py`
- `packaging/offline/*`
- `README.md`
- `USER_GUIDE.zh-CN.md`
- `docs/releases/v0.7.0.md`
- `tests/unit/*`
- `tests/integration/*`
- release asset E2E scripts or fixtures to be added in the implementation batch

## 5. 验证策略

- 单元测试：command resolver、dependency mode、artifact contract、slug fallback、adapter truth surface、branch default resolution
- 集成测试：`managed-delivery-apply` public/enterprise request、workitem init 中文业务输入、telemetry index/open violation
- CLI 测试：adapter status、run dry-run、verify constraints、final proof publication
- Release asset E2E：Windows zip 从解压开始执行，不依赖源码仓库环境
- 文档验证：release docs 每条闭环声明有 artifact 或命令证据回链

## 6. 回退策略

- 每批单独提交，可用 `git revert` 独立回退
- command resolver 和 dependency mode 先通过内部 helper 接入，避免大范围替换
- release docs 调整与 runtime 修复分批提交，避免文档和实现互相掩盖

## 7. 风险

- 企业 registry 可能无法在公共 CI 中验证，需要 fixture 或可注入 fake registry
- Playwright browser runtime 下载可能受网络/代理影响，需要缓存或 skip 语义
- adapter canonical consumption proof 可能依赖宿主能力，需要明确 unsupported/degraded 分支
- 修改 workitem 模板会影响现有 framework self-development 流程，必须保持旧路径可选
