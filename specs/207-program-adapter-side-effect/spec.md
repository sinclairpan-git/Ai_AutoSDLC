# 功能规格：Program 治理命令 IDE Adapter 副作用隔离

**功能编号**：`207-program-adapter-side-effect`
**创建日期**：2026-07-16
**状态**：对抗评审门禁
**类型**：WI-196 / GAP-12 基础副作用修复（L1）
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
`run_ide_adapter_if_initialized()`。`program` 自身既不消费 IDE adapter 文件，也不应把
Program Truth、方案确认、交付写回与 IDE 提示刷新偶发耦合。

测试侧存在独立但同根的隔离缺口：`tests/integration/test_cli_program.py` 的大量用例只替换
`program_cmd.find_project_root`，全局 hook 仍可从 pytest 的真实 cwd 找到当前仓库并改写真实
`.cursor`。因此只改生产 allowlist 而不补测试隔离，不足以关闭 GAP-12。

## 2. 目标与边界

### 2.1 目标

1. 整个 `program` 顶层命令族不得隐式调用 IDE adapter hook。
2. `program` 的 validate、truth audit、truth sync dry-run 与 execute/writeback 能力保持原有输出、
   退出码、授权和 artifact 语义；唯一批准差异是移除命令前的 adapter 刷新及其文件写入。
3. program CLI tests 默认隔离真实 adapter hook；显式 real-hook 测试必须证明 legacy managed
   Cursor 文件、project config 和 manifest 在只读 program 命令前后 byte-stable。
4. `init`、显式 `adapter select` 以及不在 bypass 集合中的既有自动适配入口保持可用。

### 2.2 明确非目标

- 不修改 `src/ai_sdlc/integrations/ide_adapter.py`、adapter 模板或 managed-file 保护规则。
- 不拆分或减重 `program_cmd.py` / `program_service.py`，不改变任何 program 公共命令。
- 不处理 `status/recover/handoff` 触发的 resume-pack 绝对路径与字段丢失；该问题登记为
  GAP-13 / WI-208。
- 不处理 `verify constraints` telemetry 写入与“read-only”帮助文本的潜在不一致；另行登记后再决策。
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
`ai_sdlc.cli.main.run_ide_adapter_if_initialized`；real-hook 用例必须显式切换到临时项目。

**验收场景**：

1. **Given** 普通 `test_cli_program.py` 用例，**When** 调用 Typer root app，**Then** 真实 hook 不可达。
2. **Given** 标记为 `real_ide_hook` 的回归用例，**When** 切换到临时项目，**Then** 测试验证真实
   dispatch 行为且不依赖开发仓库状态。

### 用户故事 3：显式适配和 Program 写入不丢失（P1）

作为普通用户，我希望显式初始化/选择 adapter 和已授权 program execute 继续工作，避免修复副作用时
误删既有能力。

**独立测试**：运行既有 adapter hook tests、truth sync execute 与一个 managed execute 用例。

**验收场景**：

1. **Given** 用户显式运行 adapter/init 入口，**When** 需要 materialize managed rule，**Then** 原路径仍可写入。
2. **Given** program execute 已满足 `--execute --yes`，**When** 执行业务写回，**Then** 目标 artifact
   仍按原合同生成，但不会顺带刷新 IDE adapter。

## 4. 兼容与风险合同

| 合同 | 本项约束 |
|---|---|
| NC-01～NC-06 | 只关闭已复现副作用；不混入结构减重、功能扩展、truth 清仓或 continuity 修复。 |
| CC-01 | program 命令名、参数、默认值、help、stdout/stderr 业务文本和 JSON envelope 保持；只批准删除 adapter notice。 |
| CC-02 | 成功、业务阻断和输入错误退出码保持。 |
| CC-03 | ProgramService 调用、artifact 路径、manifest/artifact schema、字段、顺序和错误文本保持。 |
| CC-05 | dry-run 不产生 adapter/config 写入；execute 只保留命令自身已授权写入。 |
| CC-06 | initialized/uninitialized、显式 Cursor target、legacy managed variant 和重复执行保持确定性。 |
| CC-07 | 路由 allowlist 平台无关；byte comparison 不依赖 mtime、sleep 或 POSIX 路径。 |
| RC | 本项是 GAP-12 基础缺陷，不适用 RC-01～RC-10，也不得计入减重收益。 |

风险等级为 L1。产品实现预算冻结为：只修改 `src/ai_sdlc/cli/main.py`，新增最多 1 个
tuple member，不新增函数、模块、公共 API、依赖、配置或分支特判。测试只修改
`tests/integration/test_cli_program.py`，新增手写测试不超过 90 行，不创建新 fixture 模块。

## 5. 功能需求

- **FR-001**：`program` 必须加入 root CLI 的 implicit-adapter bypass 集合。
- **FR-002**：修复不得通过修改 adapter 同步算法、忽略 tracked 文件或吞掉异常实现。
- **FR-003**：program 集成测试必须使用 autouse 隔离；只有 `real_ide_hook` 测试可运行真实 hook。
- **FR-004**：real-hook 回归必须覆盖 `program validate`、`program truth audit`、
  `program truth sync --dry-run`，并比较 adapter/config/manifest bytes。
- **FR-005**：至少一个 truth sync execute 与一个 managed execute 既有测试必须继续通过。
- **FR-006**：显式 adapter/init 路径和其他既有自动 adapter 路径必须由现有测试证明未回归。
- **FR-007**：实现前必须有 RED，RED 原因必须是 program dispatch 触发真实 adapter 写入，不得是 fixture、
  import 或 manifest 无效。
- **FR-008**：GAP-13 必须保持独立 WI-208，不得把 resume-pack 信任旧字段的快捷修复混入本项。
- **FR-009**：formal 内容由 Pascal/精简直接性与 Confucius/兼容安全对同一内容哈希独立评审；
  任一评审目标变化使双方旧 PASS 同时失效。
- **FR-010**：实现 PR 必须遵守 Codex review、required checks、heartbeat、merge 和 fresh-main 验收协议。

## 6. 成功标准

- **SC-001**：基线 real-hook 用例稳定 RED；候选实现后同一用例 GREEN，且三个命令的受保护文件 bytes 全不变。
- **SC-002**：产品 diff 仅包含 `main.py` 一个 bypass member；无新产品抽象，预算不超过 1 行。
- **SC-003**：`test_cli_program.py` 普通用例无法访问真实 adapter hook，real-hook 用例只写临时项目。
- **SC-004**：focused tests、Ruff、全量 pytest、`verify constraints`、Program Truth validate/audit、
  `git diff --check` 全部通过。
- **SC-005**：实现前后 program 业务输出/退出码与 execute artifact 零未批准差异；唯一 expected delta
  是 adapter notice 与 adapter/config 写入消失。
- **SC-006**：两个对抗 Agent 对同一 formal review target 明确 PASS，且无 Critical、Important 或其他
  actionable finding。
- **SC-007**：PR 合并后 fresh `origin/main` 重跑 real-hook、focused、full、Ruff 和 truth；工作树 clean。
- **SC-008**：父项只把 GAP-12 标为关闭，不关闭 GAP-13、GAP-05、WI-196、RC-08，也不发布版本。

## 7. 停止与回退

以下任一条件成立即停止并回到 design：

1. 需要修改 `ide_adapter.py`、ProgramService 或多个 program handler 才能实现；
2. program execute 业务写入、CLI surface、退出码或授权边界出现未批准差异；
3. 显式 adapter/init 路径失效；
4. 产品改动超过 1 行或需要新增抽象/配置；
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

六文件按 repo-relative path 排序后，以 `path + NUL + 8-byte big-endian length + bytes` 计算组合
SHA-256。评审记录必须包含 agent、维度、目标哈希、起止 HEAD/tree、时间、findings、处置和 verdict。
