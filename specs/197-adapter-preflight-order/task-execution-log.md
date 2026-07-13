# 任务执行日志：Adapter Mutation 与 Workitem Preflight 顺序修复

**功能编号**：`197-adapter-preflight-order`
**创建日期**：2026-07-13
**状态**：design admission

## 1. 固定合同

- 父项：WI-196 `GAP-07 / T51`。
- 基线：`origin/main@4dd0f1c9cdcc26a359dd0d724f365a3168d66fe8`。
- 分支/worktree：`feature/197-adapter-preflight-order-docs` / `.worktrees/197-adapter-preflight-order`。
- 实现前置：`spec.md + plan.md + tasks.md` 同哈希双 Agent PASS。
- 允许产品文件：`src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/workitem_cmd.py`。
- 允许测试文件：`tests/integration/test_cli_workitem_init.py`、`tests/unit/test_cli_hooks.py`。
- 回退 owner：framework maintainer；实现提交必须可独立 revert。

## 2. Batch 2026-07-13-001：现状审计与未改代码基线

### 2.1 仓库状态

- 根 `main` 有用户 continuity 与文档改动，未切换、未清理、未修改。
- 新 worktree 从 `origin/main` 创建；初始 HEAD 为 `4dd0f1c9`。
- `.worktrees/` 由 `.gitignore` 明确忽略。
- 仓库首选 PowerShell，但本机此前已确认 PowerShell runtime 不可用；本批沿用已诊断的 zsh fallback。

### 2.2 事实审计

- `src/ai_sdlc/cli/main.py:94-97` 在非 bypass 顶层命令前运行 adapter。
- `src/ai_sdlc/cli/workitem_cmd.py:75-118,163-169` 在子命令内部后运行 clean-tree preflight。
- `tests/integration/test_cli_workitem_init.py:34-37` 对整个文件 patch 根 hook，真实冲突未覆盖。
- GAP-10 proof carrier、校验与 blocker 已存在；本项不修改它们。

### 2.3 基线验证

- `uv run pytest tests/unit/test_cli_hooks.py tests/unit/test_workitem_scaffold.py -q`
  - 结果：`9 passed in 0.89s`。
- `uv run pytest -q`
  - 结果：`3145 passed, 3 skipped in 408.98s`。
  - 观察：测试更新了隔离 worktree 内的 `resume-pack.yaml` 与受管 Cursor rule；两处均已用补丁恢复到 HEAD，未带入用户工作或 WI-197 变更。
- `workitem init` 首次尝试被上述测试副作用触发的 clean-tree gate 正确阻断；恢复后通过 patched canonical CLI 成功生成 WI-197。

### 2.4 兼容安全独立审计

- reviewer 结论：WI-196 原子路线 `PASS`，当前没有必然 L4。
- T51 特别约束：保持自动 adapter；execute 前落 GAP-10 impact analysis；不得用关闭 hook 或放宽 proof 解决。
- disposition：全部纳入本项 spec/plan/tasks。

## 3. 下一步

### 3.1 第一轮同哈希评审

- review target hash：`ec47124aeb0bf79ac2b62370a010cca7f262762dba0588a565f264b0d537a928`。
- 兼容安全 Agent：`FAIL`；根 callback 无法可靠识别二级 `init`，GAP-10 proof 持久化时序和参数解析失败路径未冻结。
- 精简效率 Agent：`FAIL`；缺少非 `init` workitem 子命令的可执行回归，错误跳过整个组也可能通过。
- disposition：findings 全部成立。改为 root → workitem group callback 委托；冻结 clean/dirty、缺失参数、非 `init` 与 proof 重试场景。
- 三目标文件已变化，第一轮两个 verdict 全部失效。

### 3.2 下一门禁

第二轮 review target hash：`37db361715fd8de7accdd80084c0a50a351dfcda09908c25467757711e0ba6b6`。

- 兼容安全 Agent：独立复算一致，未发现可操作问题，`VERDICT: PASS`。
- 精简效率 Agent：独立复算一致，未发现可操作问题，`VERDICT: PASS`。
- 结论：T12 admission 通过，三目标文件冻结；后续目标变化会让双方 PASS 同时失效。

下一步：提交 docs batch，切 dev branch，按 T21 开始 RED。

## 4. Batch 2026-07-13-002：设计准入与 truth 基线

### 4.1 双 Agent 设计准入

- 同一 review target hash：`37db361715fd8de7accdd80084c0a50a351dfcda09908c25467757711e0ba6b6`。
- 兼容安全 Agent：独立复算一致，`PASS`，无可操作问题。
- 精简效率 Agent：独立复算一致，`PASS`，无可操作问题。
- 结论：`spec.md`、`plan.md`、`tasks.md` 冻结，允许进入实现。

### 4.2 Program Truth 同步

- snapshot state：`migration_pending`。
- snapshot hash：`65d36f71a1bc2818c20ad8982f5181f689723230ed00c23d93b6f48ff5e16918`。
- frontend blockers：`frontend_inheritance:generation`、`frontend_inheritance:quality`。
- adapter blocker：`adapter_canonical_consumption:unverified`。
- source inventory：`total=1046`、`mapped=1013`、`unmapped=33`、`missing=11`。
- 相对 WI-196 已登记基线，新增 5 个 WI-197 文档使 total/mapped 同增 5；unmapped/missing 债务集合未扩大。

### 4.3 Continuity 临时对齐

- `workitem link` 已把 `linked_wi_id` 和 `linked_plan_uri` 指向 WI-197，但 checkpoint `feature` 仍停留在 WI-196；这与父项 GAP-08 的已知缺口一致。
- 在 GAP-08 尚未修复前，本项用显式补丁把 checkpoint `feature` 对齐到 WI-197 与当前 docs branch；没有修改运行时代码或放宽门禁。
- 后续以 `uv run ai-sdlc handoff update` 生成 canonical/scoped handoff 与 resume pack，并在执行日志中保留该 workaround。
- 当前批次 branch disposition 状态：PR merge carrier。

### 4.4 提交卫生与同哈希复核

- `git diff --cached --check` 发现冻结设计文件含 5 处 Markdown 行尾空格；未绕过门禁，仅移除行尾空格。
- 格式修复后的 review target hash：`0c97361ef27901ef3d207cc1c21980e2cc9cb64c633d4c03caa1e43db74a9236`。
- 兼容安全 Agent：独立复算一致，`PASS`，无可操作问题。
- 精简效率 Agent：独立复算一致，`PASS`，无可操作问题。
- 结论：格式修复未改变设计语义；以新哈希重新冻结三目标文件并进入提交门禁。
