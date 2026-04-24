# 任务分解：V0.7.0 Windows 离线 E2E 修复基线

**编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**日期**：2026-04-24
**来源**：[`spec.md`](./spec.md) + [`plan.md`](./plan.md) + [`../../docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md`](../../docs/defects/2026-04-24-v0.7.0-windows-offline-e2e-issues.zh-CN.md)

## 执行清单

- [ ] T179-01 跨平台包管理器命令解析
- [ ] T179-02 前端依赖模式与 mutate 前 preflight
- [ ] T179-03 失败 artifact 和下游阻断合同
- [ ] T179-04 Windows release asset P0 smoke
- [ ] T179-05 中文标题 work item id 降级策略
- [ ] T179-06 业务模板与 framework formal 模板隔离
- [ ] T179-07 artifact-generate 执行顺序和摘要语义
- [ ] T179-08 adapter 状态机与展示一致性
- [ ] T179-09 telemetry artifact/open violation 接线
- [ ] T179-10 verify/final proof 失败语义
- [ ] T179-11 公共 PrimeVue 真实安装与 runtime proof
- [ ] T179-12 企业 Vue2 错误分类与 provider 隔离
- [ ] T179-13 browser gate baseline and final proof E2E
- [ ] T179-14 Windows 安装和文档编码体验
- [ ] T179-15 PRD/Git/default branch/PowerShell 收口前置
- [ ] T179-16 发布口径和 release proof 回链

## Batch 1：P0 Windows dependency runtime closure

### T179-01 跨平台包管理器命令解析

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-007`
- **依赖**：无
- **文件**：`src/ai_sdlc/core/managed_delivery_apply.py`，新增/调整 command resolver helper，相关 unit tests
- **验收标准**：
  1. Windows 下 npm/npx/pnpm/yarn/corepack 解析 `.cmd` 或 `.exe`
  2. macOS/Linux 行为不退化
  3. 不使用 `shell=True` 作为主路径
- **验证**：Windows resolver unit test + managed delivery dependency install focused test

### T179-02 前端依赖模式与 mutate 前 preflight

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-020`、`E2E-WIN-009`、`E2E-WIN-010`
- **依赖**：T179-01
- **文件**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/managed_delivery_apply.py`、provider install strategy fixtures
- **验收标准**：
  1. 支持 `offline_strict`、`enterprise_registry`、`public_registry`
  2. strict 离线缺缓存时 mutate 前 fail-fast
  3. 在线/企业模式记录 registry、lockfile、node_modules、runtime 证据要求
- **验证**：dependency mode unit tests + public/enterprise request integration tests

### T179-03 失败 artifact 和下游阻断合同

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-008`、`E2E-WIN-021`
- **依赖**：T179-01
- **文件**：`src/ai_sdlc/core/managed_delivery_apply.py`、managed delivery models/tests
- **验收标准**：
  1. 失败 artifact 记录 attempted command、resolved executable、cwd、PATH/PATHEXT、stdout/stderr、exception、retry count
  2. 下游 action 标记 `dependency_blocked`
  3. `plain_language_blockers` 和 `recommended_next_steps` 非空
- **验证**：artifact snapshot tests + failure classification tests

### T179-04 Windows release asset P0 smoke

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-007`、`E2E-WIN-008`、`E2E-WIN-020`
- **依赖**：T179-01、T179-02、T179-03
- **文件**：release smoke scripts/fixtures、`packaging/offline/RELEASE_CHECKLIST.md`
- **验收标准**：
  1. 从 Windows zip 解压开始执行
  2. 不依赖源码仓库 venv
  3. 输出 release asset 级证据路径
- **验证**：Windows offline E2E smoke 记录

## Batch 2：P0 work item intake and materialization semantics

### T179-05 中文标题 work item id 降级策略

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-004`
- **依赖**：无
- **文件**：`src/ai_sdlc/core/workitem_scaffold.py`、`src/ai_sdlc/utils/helpers.py`、workitem tests
- **验收标准**：
  1. 纯中文标题能生成合法稳定 WI id，或错误提示给出可复制 `--wi-id`
  2. 覆盖中文、中文加英文、符号标题
- **验证**：`tests/unit/test_workitem_scaffold.py` + CLI integration

### T179-06 业务模板与 framework formal 模板隔离

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-005`
- **依赖**：T179-05
- **文件**：workitem template、`src/ai_sdlc/core/workitem_scaffold.py`、CLI tests
- **验收标准**：
  1. 业务输入生成业务相关 `spec.md/plan.md/tasks.md`
  2. framework self-development 仍可显式选择 formal 模板
  3. `订单运营管理台` 回归样例不再生成 direct-formal 任务
- **验证**：business workitem fixture + formal workitem regression

### T179-07 artifact-generate 执行顺序和摘要语义

- **优先级**：P0
- **覆盖缺陷**：`E2E-WIN-008`
- **依赖**：T179-03
- **文件**：`src/ai_sdlc/core/managed_delivery_apply.py`、README/USER_GUIDE 相关段落
- **验收标准**：
  1. 若依赖失败阻止代码落盘，CLI 明确说明未生成哪些文件
  2. 若允许 scaffold 先落盘，执行顺序和 gate 语义一致
- **验证**：managed delivery success/failure artifact tests

## Batch 3：P1 adapter, telemetry, and proof signal closure

### T179-08 adapter 状态机与展示一致性

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-003`
- **依赖**：无
- **文件**：`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`
- **验收标准**：
  1. status 展示 activation、ingress、canonical consumption、evidence、degrade reason
  2. dry-run 是否写入 adapter 文件被明确声明或移除
  3. mutate gate 与 status 使用同一判定
- **验证**：adapter CLI tests + dry-run side-effect tests

### T179-09 telemetry artifact/open violation 接线

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-022`
- **依赖**：T179-03
- **文件**：telemetry writer/indexer、program service gate surfaces、tests
- **验收标准**：
  1. managed delivery/browser gate/final proof latest artifact 注册到 telemetry
  2. P0/P1 未闭环形成 open violation 或等价 unresolved evidence
  3. 修复后可关闭或转 resolved
- **验证**：telemetry index integration tests

### T179-10 verify/final proof 失败语义

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-011`、`E2E-WIN-012`、`E2E-WIN-017`
- **依赖**：T179-09
- **文件**：`src/ai_sdlc/cli/verify_cmd.py`、`src/ai_sdlc/core/program_service.py`、program CLI tests
- **验收标准**：
  1. `verify constraints` 不把前端闭环失败误报为全项目通过
  2. final proof 区分 `not_applicable`、`blocked_missing_proof`、`ready_to_publish`
  3. browser gate 缺入口/runtime/baseline 时输出可理解 blocker
- **验证**：CLI output tests + program service tests

## Batch 4：P1 provider runtime and browser proof

### T179-11 公共 PrimeVue 真实安装与 runtime proof

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-009`
- **依赖**：T179-01、T179-02
- **文件**：public provider install strategy、browser gate runtime tests
- **验收标准**：
  1. 验证 `primevue`、`@primeuix/themes`
  2. 记录 lockfile、node_modules package manifest、runtime import
  3. browser rendering 证明 PrimeVue adapter 生效
- **验证**：public path integration/E2E

### T179-12 企业 Vue2 错误分类与 provider 隔离

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-010`、`E2E-WIN-019`
- **依赖**：T179-01、T179-02
- **文件**：enterprise provider generator/install strategy/tests
- **验收标准**：
  1. 企业 registry 错误区分命令、网络、认证、包名、版本
  2. 企业 payload 不出现 `publicPrimeVue*`
  3. 具备 registry 条件时形成安装证据
- **验证**：enterprise provider snapshot + failure classification tests

### T179-13 browser gate baseline and final proof E2E

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-011`、`E2E-WIN-017`
- **依赖**：T179-10、T179-11
- **文件**：browser gate runtime, baseline promotion, final proof publication
- **验收标准**：
  1. 生成截图、bootstrap artifact、baseline png/yaml
  2. baseline promotion 后二次 probe pass 或明确 visual blocker
  3. final proof 产出 persisted artifact
- **验证**：browser gate/final proof integration tests

## Batch 5：P2/P3 Windows UX, Git preflight, and release evidence

### T179-14 Windows 安装和文档编码体验

- **优先级**：P2
- **覆盖缺陷**：`E2E-WIN-001`、`E2E-WIN-002`、`E2E-WIN-016`
- **依赖**：无
- **文件**：`packaging/offline/*`、`README.md`、`USER_GUIDE.zh-CN.md`
- **验收标准**：
  1. release zip 内 `install_offline.ps1` 中文内容正确
  2. 终端代理诊断覆盖 Git/curl/pip/npm
  3. Windows 查看 UTF-8 文档有明确命令
- **验证**：offline bundle script tests + doc lint/manual smoke

### T179-15 PRD/Git/default branch/PowerShell 收口前置

- **优先级**：P2
- **覆盖缺陷**：`E2E-WIN-006`、`E2E-WIN-013`、`E2E-WIN-014`、`E2E-WIN-015`
- **依赖**：无
- **文件**：`src/ai_sdlc/core/branch_inventory.py`、`src/ai_sdlc/branch/git_client.py`、docs
- **验收标准**：
  1. PRD warning 说明是否阻塞和如何绑定
  2. 无 Git、`master`、`main`、自定义默认分支均有测试
  3. Windows 示例避免失败后继续执行 close-check
- **验证**：branch lifecycle tests + docs examples

### T179-16 发布口径和 release proof 回链

- **优先级**：P1
- **覆盖缺陷**：`E2E-WIN-018`
- **依赖**：T179-04、T179-13
- **文件**：`docs/releases/v0.7.0.md`、`README.md`、`USER_GUIDE.zh-CN.md`、release checklist
- **验收标准**：
  1. 每条 release-grade 声明有 release asset 级证据
  2. 未修复前有 known issues 或撤回过强表述
  3. Windows/macOS/Linux 各自 smoke 记录可追溯
- **验证**：release checklist + `program truth sync --dry-run`
