# 功能规格：Program 治理命令 IDE Adapter 副作用隔离

**功能编号**：`207-program-adapter-side-effect`
**创建日期**：2026-07-16
**状态**：closed；PR #139 + test-isolation repair PR #141 已合并并通过 fresh-main clean acceptance
**类型**：WI-196 / GAP-12 基础副作用修复（L2，影响 CC-05）
**基线**：`origin/main@506e950dee3469248ef7e6b5e1aac664668d18a1`

## 1. 问题与证据

在 detached、clean 的基线 worktree 中执行：

```text
uv run ai-sdlc program validate
```

命令本身返回 `program validate: PASS`，但在业务命令解析前额外输出
`IDE adapter (cursor): installed 1 file(s)`，并把 tracked
`.cursor/rules/ai-sdlc.mdc` 从 SHA-256
`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`
改为
`02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134`。
同一复现中 canonical handoff 与 resume-pack bytes 未变化；随后执行
`uv run ai-sdlc verify constraints` 也未产生新的 adapter 或 continuity 写入。

根因是 `src/ai_sdlc/cli/main.py::_global_before_command` 只把部分顶层命令族排除出
隐式 adapter hook，`program` 未被排除，于是任何 `program ...` 都先调用
`run_ide_adapter_if_initialized()`。大多数 `program` 命令不消费 IDE adapter 文件，不应把 Program
Truth、方案预览或普通写回与 IDE 提示刷新偶发耦合。

PR #139 的一行 root bypass 进一步暴露了兼容例外：managed delivery 会读取持久化
`adapter_ingress_state`；用户在普通终端 init 后进入真实 AI 宿主时，旧 root hook 会把
`materialized` 刷新为 `verified_loaded`，从而解除 `host_ingress_below_mutate_threshold`。若整个
`program` 永久跳过 hook，首次 `managed-delivery-apply` 或 `solution-confirm --execute --continue`
会被错误阻断。正确边界不是恢复所有 program hook，而是保留顶层 bypass，并只在这两个依赖宿主
验证状态的 managed-delivery 入口局部刷新。

测试侧存在独立但同根的隔离缺口：`tests/integration/test_cli_program.py` 的大量用例只替换
`program_cmd.find_project_root`，全局 hook 仍可从 pytest 的真实 cwd 找到当前仓库并改写真实
`.cursor`。因此只改生产 allowlist 而不补测试隔离，不足以关闭 GAP-12。

PR #139 合并为 `8752aa97` 后，fresh detached `origin/main` 的 real-hook、focused、full 与 Ruff
业务断言全部通过，但 full suite 结束后真实 checkout 的 root resume-pack 与 Cursor rule 发生变化。
pristine worktree 单独运行 `verify constraints`、real-hook 或 focused 均保持 clean；逐测试 teardown
guard 最终定位到 8 组 CLI 测试继承源码仓 cwd，命令内部又从 cwd 独立解析项目根，因而越过各测试
对 command-local `find_project_root` 的 patch。GAP-12 只有在这些用例切到临时 cwd，并把“pytest 不得
新增真实仓库状态变化”固化为 session postcondition 后才能关闭。

## 2. 目标与边界

### 2.1 目标

1. `program` 顶层命令族不得无条件调用 IDE adapter hook；validate、truth audit、truth sync dry-run
   等不依赖宿主验证状态的路径必须零 adapter 写入。
2. `managed-delivery-apply`（dry-run/execute）必须在构建 request 前刷新；`solution-confirm` 只有在
   `--execute/--yes`、preflight、`--continue` 与 effective-change acknowledgement 全部通过后，才在
   managed-delivery request 前保留 `materialized → verified_loaded` 迁移。普通 `solution-confirm
   --execute`、truth sync execute 和其他 program 写回不得恢复 hook。
3. `program` 的输出、退出码、授权和 artifact 语义保持；所有非上述两个 managed 刷新入口的 program
   路径均批准移除 root adapter notice/write，包括 truth sync execute、solution-confirm execute/
   no-continue 与其他普通 handler。solution-confirm continue 的 notice 从 root 前置阶段移动到已
   持久化 solution confirmation 之后、managed-delivery request 之前，符合“persist then continue”。
4. program CLI tests 默认隔离 root 与 program-local 真实 adapter hook；显式 real-hook 测试必须证明
   legacy managed Cursor 文件、project config 和 manifest 在只读 program 命令前后 byte-stable。
5. `init`、显式 `adapter select` 以及不在 bypass 集合中的既有自动适配入口保持可用。
6. 完整 pytest 会话必须允许既有 dirty candidate 作为基线，但不得新增 tracked/index 变化，也不得
   新增或改写 canonical adapter 文件、project config 与任一 scoped resume-pack。

### 2.2 明确非目标

- 不修改 `src/ai_sdlc/integrations/ide_adapter.py`、adapter 模板或 managed-file 保护规则。
- 不拆分或减重 `program_cmd.py` / `program_service.py`，不改变任何 program 公共命令；只允许在
  `program_cmd.py` 两个现有 handler 中复用既有 hook，不新增通用命令分类器。
- 不处理 `status/recover/handoff` 触发的 resume-pack 绝对路径与字段丢失；该问题登记为
  GAP-13 / WI-208。
- 不修复 YAML quoted scalar 中 `#` 被 comment preservation policy 误判的问题；该问题登记为
  GAP-14 / WI-209，不混入本项产品代码。
- 不处理 `verify constraints` telemetry 写入与“read-only”帮助文本的潜在不一致；另行登记后再决策。
- 不改变 managed-delivery-apply 省略 `--request` 时既有 truth-derived request 物化，也不改变 direct
  `--execute` 缺少 `--yes` 时“adapter/request preflight 已发生、mutate/apply 未发生”的既有顺序。
- 不把本项计为 `completed_reduction`，不宣称 GAP-05、WI-196、RC-08 或版本发布完成。

## 3. 用户场景与独立测试

### 用户故事 1：治理命令不污染工作树（P0）

作为框架维护者，我希望运行 program 验证、truth 审计和 dry-run 时不刷新 IDE adapter，
以便治理证据不会因为无关 tracked 文件变化而失真。

**独立测试**：在显式 Cursor target、同时存在 legacy managed `.md` / `.mdc` 的临时已初始化项目中，
运行 `program validate`、`program truth audit`、`program truth sync --dry-run`，逐项比较 adapter、
project config、manifest bytes。

**验收场景**：

1. **Given** 临时项目含可升级的 managed Cursor rule，**When** 执行任一只读 program 命令，
   **Then** adapter hook 不执行，`.md` / `.mdc` / config / manifest bytes 不变。
2. **Given** program 命令返回业务 PASS 或业务 blocker，**When** 检查 transcript 和 exit code，
   **Then** 除移除 `IDE adapter ...` 行外，业务语义与基线一致。

### 用户故事 2：测试不能写真实仓库（P0）

作为测试维护者，我希望 program 集成测试默认禁用真实 adapter hook，以便测试 fixture 即使只替换
program root，也不会从 pytest cwd 发现并修改开发仓库。

**独立测试**：autouse fixture 对非 `real_ide_hook` 用例替换
`ai_sdlc.cli.main.run_ide_adapter_if_initialized` 与
`ai_sdlc.cli.program_cmd.run_ide_adapter_if_initialized`；naive/pre-import 阶段对后者使用
`create=True`，real-hook 用例必须显式切换到临时项目。

**验收场景**：

1. **Given** 普通 `test_cli_program.py` 用例，**When** 调用 Typer root app，**Then** 真实 hook 不可达。
2. **Given** 标记为 `real_ide_hook` 的回归用例，**When** 切换到临时项目，**Then** 测试验证真实
   dispatch 行为且不依赖开发仓库状态。

### 用户故事 3：显式适配和 Program 写入不丢失（P1）

作为普通用户，我希望显式初始化/选择 adapter、已授权 program execute 和首次 managed delivery
宿主验证迁移继续工作，避免修复副作用时误删既有能力。

**独立测试**：运行既有 adapter hook tests、truth sync execute、managed execute，并新增“普通终端
materialized → 进入匹配 AI 宿主 → 首个 managed-delivery dry-run”真实迁移用例。

**验收场景**：

1. **Given** 用户显式运行 adapter/init 入口，**When** 需要 materialize managed rule，**Then** 原路径仍可写入。
2. **Given** program execute 已满足 `--execute --yes`，**When** 执行与 managed delivery 无关的业务
   写回，**Then** 目标 artifact 仍按原合同生成且不会顺带刷新 IDE adapter。
3. **Given** init 只记录 `materialized` 且当前进入匹配 AI 宿主，**When** 首次运行
   `managed-delivery-apply` 或通过全部授权/ack 门禁的 `solution-confirm --execute --continue`，**Then**
   adapter ingress 在 managed request 前持久化为 `verified_loaded`，managed delivery 不产生假 blocker。
4. **Given** solution-confirm 缺少 `--yes`、preflight blocked、未指定 `--continue` 或缺少必要 ack，
   **When** 命令退出，**Then** program-local hook 零调用且 adapter/config bytes 不变。
5. **Given** managed-delivery-apply direct execute 缺少 `--yes`，**When** guard 完成后退出，**Then** 保留
   既有 adapter refresh 与省略 request 时的 request 物化，但不执行 mutate action、不写 apply result。

### 用户故事 4：完整测试不能污染源码仓（P0）

作为框架维护者，我希望所有会触发 CLI root callback 的集成测试都运行在临时 cwd，并在 pytest
会话结束时验证仓库状态与会话开始完全一致，避免新测试再次把真实源码仓当作测试项目。

**独立测试**：对已定位的 index-gate、loop、recover、run、self-update、stage、status 模块执行 focused
集合；再在允许当前候选 diff 的 baseline 上运行完整 suite，由 session guard 比较 tracked status/index/
内容，以及非 tracked canonical adapter 目标、project config 和动态 scoped resume-pack 的路径、类型与
SHA-256。结束后不得恢复文件再制造 PASS。

**验收场景**：

1. **Given** CLI 测试只 patch command-local root，**When** Typer root callback 从 cwd 解析项目，**Then**
   cwd 指向每用例独立的 `tmp_path`；需要 initialized project 的 self-update 场景显式初始化该临时项目。
2. **Given** 测试会话开始时分支已有候选 diff，**When** focused/full 测试完成，**Then** guard 只比较
   前后增量，不要求 baseline clean、不自动恢复文件、不扫描无关普通 untracked 文件。
3. **Given** 测试新增、删除或改写任一受保护路径，或 teardown 无法读取 Git 状态，**When** session
   结束，**Then** pytest fail 并仅报告变化类别和路径，不输出文件内容。

## 4. 兼容与风险合同

| 合同 | 本项约束 |
|---|---|
| NC-01～NC-06 | 只关闭已复现副作用；不混入结构减重、功能扩展、truth 清仓或 continuity 修复。 |
| CC-01 | program 命令名、参数、默认值、help、stdout/stderr 业务文本和 JSON envelope 保持；除两个 managed 刷新入口外，所有 program 路径均批准删除 root adapter notice/write；managed-delivery-apply 保留入口 notice，solution-confirm continue 的 notice 仅批准移动到 solution materialized 后、managed guard 前。 |
| CC-02 | 成功、业务阻断和输入错误退出码保持。 |
| CC-03 | ProgramService 调用、artifact 路径、manifest/artifact schema、字段、顺序和错误文本保持；solution confirmation 先持久化、再 continue 的两阶段语义保持。adapter hook 传播出的异常不得进入 managed request/apply；已处理的 project-config lock 继续 warning-and-continue。 |
| CC-05 | 普通 dry-run 不新增 adapter/config 写入；managed-delivery-apply 保留两项显式 preflight 语义：省略 request 时的既有 truth-derived request 物化，以及幂等 adapter refresh exact delta。direct execute 缺少 `--yes` 时二者仍可发生，但 mutate/apply result 禁止；solution-confirm 只有全部授权/ack 门禁通过后才刷新。 |
| CC-06 | initialized/uninitialized、显式 Cursor target、legacy managed variant 和重复执行保持确定性。 |
| CC-07 | 路由 allowlist 平台无关；byte comparison 不依赖 mtime、sleep 或 POSIX 路径。 |
| RC | 本项是 GAP-12 基础缺陷，不适用 RC-01～RC-10，也不得计入减重收益。 |

风险等级为 L2，并因 CC-05 强制双 reviewer。产品实现预算冻结为：只修改
`src/ai_sdlc/cli/main.py` 与 `src/ai_sdlc/cli/program_cmd.py`，总新增最多 4 行：一个 bypass member、
一个既有 hook import、两个窄调用点；不新增函数、模块、公共 API、依赖、配置或通用分类器。测试只
修改 `tests/integration/test_cli_program.py`，累计新增手写测试不超过 110 行，不创建新 fixture 模块。

fresh-main acceptance repair 使用独立测试预算：不得修改 `src/`；只允许 `tests/conftest.py` 与已定位的
7 个 CLI 集成测试文件，gross additions 不超过 135、net additions 不超过 120，不新增测试模块、插件、
全局 cwd 改写或自动恢复逻辑。共享 cwd fixture 只由明确模块 opt-in；session guard 只在会话边界读取
仓库状态。formatter 对 `conftest.py` 既有等价字符串的机械折叠计入 diff，但不改变 fixture 内容。

## 5. 功能需求

- **FR-001**：`program` 必须加入 root CLI 的 implicit-adapter bypass 集合。
- **FR-002**：`program_managed_delivery_apply` 必须在 `_resolve_root()` 后、构建 request 前调用既有 hook；
  `program_solution_confirm` 必须复用现有 control flow，在 `--execute/--yes`、preflight、`--continue` 与
  effective-change ack 均通过后，紧邻 `build_frontend_managed_delivery_apply_request` 前单行调用；其他
  program handler 不得新增 hook。
- **FR-003**：修复不得通过修改 adapter 同步算法、ProgramService、忽略 tracked 文件或吞掉异常实现。
- **FR-004**：program 集成测试必须使用 autouse 隔离 root/program-local 两个 binding；naive/pre-import
  阶段对 program-local patch 使用 `create=True`，候选阶段验证真实 import/binding；只有
  `real_ide_hook` 测试可运行真实 hook。
- **FR-005**：real-hook 回归必须覆盖 `program validate`、`program truth audit`、
  `program truth sync --dry-run`，并比较 adapter/config/manifest bytes。
- **FR-006**：新增 real-host 测试必须证明 naive 全族 bypass 下 managed-delivery 保持 `materialized` 并
  出现 host blocker，候选实现迁移为 `verified_loaded` 并消除该 blocker；solution-confirm 完整授权
  continue 路径必须断言局部 hook exactly once，missing yes、preflight blocked、no-continue 与 missing ack
  路径必须断言零调用/零 adapter 写入。
- **FR-006A**：truth sync execute、solution-confirm execute/no-continue 至少各一个既有测试必须断言
  root/local hook 零调用、adapter/config bytes 不变且无 adapter notice；业务 artifact 仍按原合同写入。
- **FR-006B**：managed-delivery-apply direct execute missing yes 必须断言 adapter/request preflight 保持、
  exit=2 且无 mutate/apply result；solution-confirm local hook 注入 `RuntimeError` 时必须保留 confirmed
  solution、无 managed request/apply。project-config lock 继续由既有 warning-and-continue test 保护，
  managed request 可据旧 ingress 产生 blocker/artifact。
- **FR-007**：至少一个 truth sync execute 与一个 managed execute 既有测试必须继续通过。
- **FR-008**：显式 adapter/init 路径和其他既有自动 adapter 路径必须由现有测试证明未回归。
- **FR-009**：实现前必须保留双轴证据：原始基线的只读 bytes RED/managed ingress GREEN，以及 naive
  bypass 的只读 bytes GREEN/managed ingress RED；pre-import program-local patch 必须用 `create=True`，
  不得以 fixture、import 或 manifest 无效制造失败。
- **FR-010**：GAP-13 必须保持独立 WI-208，不得把 resume-pack 信任旧字段的快捷修复混入本项。
- **FR-011**：formal 内容由 Pascal/精简直接性与 Confucius/兼容安全对同一内容哈希独立评审；
  任一评审目标变化使双方旧 PASS 同时失效。
- **FR-012**：实现 PR 必须遵守 Codex review、required checks、heartbeat、merge 和 fresh-main 验收协议。
- **FR-013**：已定位的 CLI 测试必须从临时 cwd 运行；需要成功 `status` 分派的 self-update 测试必须在
  该临时 cwd 显式 `init_project`，不得通过禁用 root callback 或扩大产品 bypass 伪造隔离。
- **FR-014**：pytest session guard 必须比较会话前后 tracked status/index/内容、全部 canonical adapter
  目标、project config 与动态 scoped resume-pack；允许 dirty baseline，teardown 读取失败或任何增量
  变化均 fail，不恢复现场。
- **FR-015**：acceptance repair 不得修改产品代码；GAP-13/WI-208 与 GAP-14/WI-209 继续独立处理。

## 6. 成功标准

- **SC-001**：三个只读 real-hook 用例在原始基线稳定 RED、候选 GREEN，受保护 bytes 全不变；
  managed-ingress 用例在 naive bypass RED、候选 GREEN。
- **SC-002**：产品 diff 只含 `main.py` 一个 bypass member、`program_cmd.py` 一个 import/两个调用；
  无新产品抽象，总新增不超过 4 行。
- **SC-003**：`test_cli_program.py` 普通用例无法访问真实 adapter hook，real-hook 用例只写临时项目。
- **SC-004**：focused tests、Ruff、全量 pytest、`verify constraints`、Program Truth validate/audit、
  `git diff --check` 全部通过。
- **SC-005**：实现前后 program 业务输出/退出码与 execute artifact 零未批准差异；expected delta 仅为
  非两个 managed 刷新入口的全部 program 路径移除 root adapter notice/write，以及 solution-confirm
  continue 的 notice/hook 后移至全部门禁通过且 solution 已持久化之后、managed request 之前。传播
  异常时保留 confirmed solution 且无 managed request/apply；config-lock 软失败仍 warning-and-continue。
- **SC-006**：两个对抗 Agent 对同一 formal review target 明确 PASS，且无 Critical、Important 或其他
  actionable finding。
- **SC-007**：PR 合并后 fresh `origin/main` 重跑 real-hook、focused、full、Ruff 和 truth；工作树 clean。
- **SC-008**：父项只把 GAP-12 标为关闭，不关闭 GAP-13、GAP-05、WI-196、RC-08，也不发布版本。
- **SC-009**：受影响 8 文件 focused 集合与 full suite 通过，session guard 未报告状态变化；外部
  pre/post diff、index、project config 与所有 scoped resume 摘要直接相同，不依赖 restore。
- **SC-010**：acceptance repair 的产品 diff 为空，测试 diff 不超过 8 文件、gross `+135`、net `+120`；
  Pascal 与 Confucius 对同一 final tree 均 PASS。

## 7. 停止与回退

以下任一条件成立即停止并回到 design：

1. 需要修改 `ide_adapter.py`、ProgramService、第三个 program handler 或新增命令分类器才能实现；
2. program execute 业务写入、CLI surface、退出码或授权边界出现未批准差异；
3. 显式 adapter/init 路径失效；
4. 产品改动超过 4 行或需要新增抽象/配置；
5. real-hook 测试不能在临时项目稳定复现，或测试仍可能写真实 checkout。

回退方式是对独立实现提交执行 `git revert --no-edit <wi207-implementation-sha>`；回退后 program
恢复旧的隐式 adapter 刷新，不涉及 schema、数据迁移或外部状态清理。

## 8. Formal Review Target

本轮对抗评审同时覆盖：

- `specs/207-program-adapter-side-effect/spec.md`
- `specs/207-program-adapter-side-effect/plan.md`
- `specs/207-program-adapter-side-effect/tasks.md`
- `specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md`
- `specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md`
- `specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md`

六文件组合哈希唯一复用父计划 §9 的 canonical review-target recipe；本项不得另定义第二套编码。
评审记录必须包含 agent、维度、目标哈希、起止 HEAD/tree、时间、findings、处置和 verdict。
