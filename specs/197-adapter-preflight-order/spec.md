# 功能规格：Adapter Mutation 与 Workitem Preflight 顺序修复

**功能编号**：`197-adapter-preflight-order`
**创建日期**：2026-07-13
**状态**：本地实现与验收完成，PR 复审中
**父项**：WI-196 `GAP-07 / T51`

## 1. 问题与范围

在 `origin/main@4dd0f1c9cdcc26a359dd0d724f365a3168d66fe8` 上，根 CLI callback 会在进入 `workitem init` 前执行 IDE adapter；adapter 可能写入受管入口或 `project-config.yaml`，随后 `workitem init` 的 clean-tree preflight 把本次自动写入误判为用户已有脏改动并阻断自身。

现有 `tests/integration/test_cli_workitem_init.py` 通过 autouse patch 关闭根 adapter hook，因此没有覆盖真实调用顺序。

本项让根 callback 把整个 `workitem` 组的 adapter 时机委托给 `workitem_app` callback：合法非 `init` 子命令仍在 handler 前执行一次；`init` 先验证用户工作树原本干净，再执行同一 hook 并生成 canonical 四件套；参数解析失败或 preflight 失败时不产生 adapter 写入。

### 1.1 明确非目标

- 不关闭、弱化或替换自动 IDE adapter。
- 不改变 adapter 的 canonical path、内容摘要、proof 校验或授权语义；只接受 §5 冻结的 fail-closed 持久化时序差异。
- 不改变其他顶层命令及 `workitem` 其他子命令的 adapter 时机。
- 不放宽 docs branch 或 clean-tree preflight。
- 不改 work item schema、manifest schema、CLI 参数、成功输出或退出码合同。
- 不做结构减重、公共抽象或无关 truth 清仓。

## 2. 可复现行为

| 项目 | 冻结值 |
|---|---|
| 基线 revision | `4dd0f1c9cdcc26a359dd0d724f365a3168d66fe8` |
| observed | 原本干净的 docs branch 因根 callback 的 adapter-managed 写入，在 `_ensure_workitem_init_git_preflight` 返回 exit 1 |
| expected | 根 callback 委托 `workitem` 组；非 `init` 合法子命令仍在 handler 前执行一次；合法 `init` 先 preflight，干净时 adapter 一次并生成四件套，脏树或参数解析失败时 adapter 零次 |
| 已有掩盖 | `tests/integration/test_cli_workitem_init.py` 的 autouse patch 跳过根 hook |
| 基线定向测试 | `9 passed in 0.89s` |
| 基线全量测试 | `3145 passed, 3 skipped in 408.98s` |

## 3. 用户故事与验收

### US-01：干净 docs branch 可直接初始化工作项（P0）

作为框架维护者，我希望 `workitem init` 在 adapter 自动维护入口文件时不自我阻断，以便 canonical 工作项入口可一次成功完成。

**独立验收**：在临时已初始化 Git 仓库的合法 docs branch 上，让 adapter hook 写入一个受管文件；调用 `workitem init` 后必须 exit 0、生成四件套，且 adapter 调用次数为 1。

### US-02：真实用户脏改动仍被阻断（P0）

作为仓库维护者，我希望既有未提交改动仍被 clean-tree preflight 拦截，避免自动化覆盖或混入用户工作。

**独立验收**：preflight 前放入用户脏文件；调用 `workitem init` 后必须 exit 1，且 adapter 尚未执行、目标 spec 目录不存在。

### US-03：普通 adapter 语义不变（P0）

作为 CLI 用户，我希望本修复只改变发生顺序，不改变自动适配、错误传播和持久化行为。

**独立验收**：现有 hook 单元测试和 `workitem init` 成功/失败集保持绿色；一个非 `init` 的 workitem 子命令在 handler 前执行 adapter 恰好一次；缺失 `--title` 的 `init` 保持原退出码和错误文本且 adapter 零次。

## 4. 非减重变更合同

| 合同 | 冻结内容 |
|---|---|
| NC-01 | observed/expected、基线 revision 与复现测试按 §2 冻结 |
| NC-02 | 受影响 CC 为 CC-01、CC-02、CC-05、CC-06、CC-07；只触及 root callback、workitem group callback、init 顺序与 `WorkitemScaffolder` 的无写入重复目标校验 |
| NC-03 | 最多新增 25 行手写产品代码、80 行测试代码；0 个新产品文件、0 个公共抽象、0 个依赖 |
| NC-04 | 严格 RED→GREEN；定向、全量、ruff、constraints、diff check 全部通过 |
| NC-05 | 独立提交可 `git revert`；失败时恢复原 hook 顺序，owner 为 framework maintainer |
| NC-06 | 禁止混入减重、功能扩展、schema 变化或 GAP-09～GAP-11 清仓 |

### 4.1 兼容契约

- **CC-01**：参数、帮助、成功/失败文本保持；缺失必填参数或非法 option 仍在解析层失败，但不再先执行 adapter。
- **CC-02**：真实用户脏树继续 exit 1；合法干净 docs branch 继续/恢复 exit 0。
- **CC-05**：adapter 仍是唯一受管写入来源；preflight 不忽略任何用户预存改动；脏树、重复 canonical docs 或其他无效 `init` 为零 adapter 写入。
- **CC-06**：合法 `init` 与非 `init` workitem 子命令的 adapter 均恰好一次；脏树/无效 `init` 不消费新 proof，恢复干净后重试才持久化 proof；既有 idempotence 不变。
- **CC-07**：实现不得依赖 POSIX shell、文件锁或平台特定路径。

## 5. GAP-10 影响分析

T51 触及 adapter 入口和 proof 的持久化时机，但不改变 canonical consumption proof 的校验合同：

- proof carrier 仍由 `adapter exec` 与现有 digest/path 环境变量负责；
- proof 校验、release blocker 和 persisted field schema 均不修改；
- approved expected delta：脏树、缺失必填参数或非法 option 的 `workitem init` 不再消费/持久化本次 proof，现有 blocker 状态保持；仓库恢复干净并用合法参数重试后，proof 正常持久化且 hook 恰好一次；
- 其他合法 workitem 子命令仍在 handler 前消费 proof，时机不变；
- 若实现需要放宽 digest/path 校验、把文件存在视为已消费、绕过 `unverified` blocker 或伪造静态 proof，立即停止并转 T53B/L4 决策。

结论：该时序差异是更严格的 fail-closed 行为，GAP-10 当前债务不阻断本项；不得用放宽 proof 校验补偿，且必须由脏树→干净重试和非 `init` 黑盒回归证明。

## 6. 功能需求

- **FR-197-01**：根 callback 必须把整个 `workitem` 组委托给 `workitem_app` callback，不能依赖 `sys.argv` 猜测二级命令。
- **FR-197-02**：合法非 `init` workitem 子命令必须仍在 handler 前执行 adapter 恰好一次。
- **FR-197-03**：`init` 的重复目标校验与 clean-tree preflight 必须在 adapter hook 之前完成；通过后 hook 恰好一次。
- **FR-197-04**：重复 canonical docs、preflight 或参数解析失败时 adapter 不得运行，不得持久化新 proof，不得改写既有 spec 目录。
- **FR-197-05**：不得新增“忽略 adapter 路径”的脏树白名单。
- **FR-197-06**：现有 adapter PermissionError/异常传播、proof 校验和 blocker 合同保持。
- **FR-197-07**：新增测试必须覆盖 clean/dirty 重试、重复 canonical docs、缺失必填参数和非 `init` 子命令，且至少一个用例在修复前因调用顺序失败。
- **FR-197-08**：提交必须包含 TDD、全量回归、回退和 GAP-10 expected-delta 证据。

## 7. 成功标准

- **SC-197-01**：新 characterization test 在生产修复前稳定失败，失败原因为 adapter 写入先于 preflight。
- **SC-197-02**：修复后 clean/dirty、重复 canonical docs、缺失参数、非 `init` 黑盒测试及三个 focused 文件全绿。
- **SC-197-03**：真实用户脏树测试证明 adapter/proof 零写入且 exit 1，恢复干净后重试一次成功；duplicate-init 测试证明第二次调用不增加 adapter 计数且不重建 proof。
- **SC-197-04**：产品新增 LOC ≤25，测试新增 LOC ≤80，无新公共抽象或依赖。
- **SC-197-05**：`uv run pytest -q`、ruff、constraints、diff check 全部通过。
- **SC-197-06**：兼容安全与精简效率 Agent 对同一 `spec.md + plan.md + tasks.md` 哈希均 PASS。
- **SC-197-07**：独立任务 review 与最终 branch review 均无 Critical/Important finding。

## 8. 停止与回退

出现以下任一情况立即停止：需要关闭自动 adapter、放宽 clean-tree、改变 proof/授权边界、修改第二个业务领域、超出 NC-03，或出现跨平台差异。

回退方式为 revert 本项实现提交；四件套与测试证据保留，运行时恢复原顺序。发布后若出现回归，先回滚包含本项的版本，再 revert 实现提交。
