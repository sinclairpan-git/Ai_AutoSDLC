# 实施计划：Program 治理命令 IDE Adapter 副作用隔离

**编号**：`207-program-adapter-side-effect`
**日期**：2026-07-16
**规格**：`specs/207-program-adapter-side-effect/spec.md`
**父路线**：`specs/196-ai-sdlc-lean-code-self-reduction-governance/`

## 1. 交付策略

采用“formal docs branch → 同哈希双 Agent PASS → formal PR/mainline receipt → 独立 dev branch →
双轴 RED → 四行窄化产品修复 → focused/full/fresh-main”的顺序。产品实现保留 root CLI bypass，并只在
两个 managed-delivery 依赖入口复用既有 adapter hook；测试隔离与 real-hook 证据在同一实现 PR 中完成。

本项不把两个现象包装成“只读命令零写入”大修。Cursor 改写属于 root CLI dispatch；resume-pack
重建属于 continuity canonical source。后者以 GAP-13 / WI-208 单独设计、评审和回滚。

## 2. 技术背景

**语言/版本**：Python 3.11+
**CLI**：Typer root app + nested `program_app`
**主要依赖**：现有 Typer、pytest、unittest.mock；不新增依赖
**状态/存储**：本项不新增状态；测试只观测临时项目内 tracked bytes
**测试**：pytest、CliRunner、`real_ide_hook` marker、现有 Program Truth/managed execute fixtures
**目标平台**：Windows、macOS、Linux
**约束**：产品新增最多 4 行；测试累计新增不超过 110 行；无新模块/函数/API/config/schema

## 3. 冻结设计

### 3.1 产品边界

在 `src/ai_sdlc/cli/main.py::_READ_ONLY_SUBCOMMANDS` 增加 `"program"`。当前 tuple 名称虽不能
完整表达“顶层不应无条件刷新 adapter”，但重命名会扩大无收益 diff，本项保留现名。

同时在 `program_cmd.py` 直接 import 既有 `run_ide_adapter_if_initialized`，只增加两个调用点：

1. `program_managed_delivery_apply` 在 `_resolve_root()` 后、构建 request 前调用，覆盖 dry-run/execute；
2. `program_solution_confirm` 复用现有 early exits：在 `--execute/--yes`、preflight、`--continue` 与
   effective-change ack 全部通过后，紧邻 `build_frontend_managed_delivery_apply_request` 前单行调用。
   此时 solution confirmation 已按“persist then continue”合同持久化；hook 失败不得进入 managed apply。

不得为 33 个命令或 21 个 execute switch 建通用分类器；truth sync execute、普通 solution-confirm
execute 与其他写回继续 bypass。这样只读治理路径零写入，同时保留 managed delivery 对
`verified_loaded` 持久化状态的真实依赖。

### 3.2 测试隔离

在 `tests/integration/test_cli_program.py` 增加 autouse fixture：

1. 普通用例同时 patch `ai_sdlc.cli.main.run_ide_adapter_if_initialized` 与
   `ai_sdlc.cli.program_cmd.run_ide_adapter_if_initialized`；naive/pre-import 阶段对后者使用
   `create=True`，候选阶段再验证真实 binding；
2. 带 `real_ide_hook` marker 的用例不 patch；
3. real-hook 用例必须 `monkeypatch.chdir(tmp_project)`，不得只 patch
   `program_cmd.find_project_root`。

这既防止基线代码在测试期间改写真实仓库，也让真正需要验证 root dispatch 的测试显式可见。

### 3.3 Real-hook fixture

复用现有 project/truth fixture 构造临时 initialized project，并显式持久化 Cursor target。临时项目
同时写入 legacy managed `.cursor/rules/ai-sdlc.md` 与 canonical `.mdc`，使基线 root hook 必然具备
可观察写入。对以下命令参数化验证：

- `program validate`
- `program truth audit`
- `program truth sync --dry-run`

每次调用前后比较 `.md`、`.mdc`、project config 与 `program-manifest.yaml` bytes；不得使用 mtime、
sleep 或当前 OS 路径作为断言。允许命令依据 fixture 返回 PASS 或业务 blocker，但不允许 adapter notice。

### 3.4 兼容回归

- 复用 `test_program_truth_sync_and_audit_surface_blocked_release_state` 证明 truth execute/audit surface 未变。
- 复用一个 `managed-delivery-apply --execute --yes` 既有测试证明业务写入未丢失。
- 新增 real-host managed-delivery dry-run：先在无宿主信号下 materialize Codex adapter，再设置
  `OPENAI_CODEX=1`；naive bypass 必须因状态仍为 `materialized` RED，候选必须持久化
  `verified_loaded` 并移除 `host_ingress_below_mutate_threshold`。
- 在既有 `solution-confirm --execute --continue --yes` 测试中断言 program-local hook exactly once；
  missing yes、preflight blocked、普通 execute/no-continue 与 missing ack 复用既有测试断言零调用和
  adapter/config bytes 不变。adapter notice 只允许出现在 solution materialized 后、managed guard 前。
- 在 truth sync execute 与 solution-confirm execute/no-continue 既有测试中断言 root/local hook 零调用、
  adapter/config bytes 不变且无 adapter notice；这些业务 artifact 仍正常生成。
- 增加 managed-delivery-apply direct execute missing yes 回归：保留入口 adapter refresh，省略 request 时
  仍物化 truth-derived request，exit=2 且无 mutate/apply result。
- 对 solution-confirm local hook 注入 `RuntimeError`，断言 confirmed solution 保留且无 managed
  request/apply；project-config `PermissionError` 仍由 `test_cli_hooks.py` 的 warning-and-continue 合同
  保护，调用方可继续并据旧 ingress 生成 blocker/artifact。
- 运行 `tests/integration/test_cli_ide_adapter.py` 与 `tests/unit/test_cli_hooks.py` 证明显式/其他 adapter
  路径仍工作。
- `ide_adapter.py` 不在变更 allowlist；若测试要求修改它，本设计自动 No-Go。

## 4. 宪章与父合同检查

| 门禁 | 计划响应 |
|---|---|
| MUST-1 范围严控 | 只修已复现 GAP-12；GAP-13、telemetry 与 Program 结构减重不混入。 |
| MUST-2 可验证 | 先写真实 dispatch RED，再跑 execute 与 adapter 兼容回归。 |
| MUST-3 范围/验证/回退 | docs 与 code 分支独立；实现单 commit，可直接 revert。 |
| MUST-4 状态外化 | formal、执行日志、review receipt、PR/CI/fresh-main 证据落盘。 |
| 400/50 行约束 | 不新增产品函数/文件；只允许一个 import、两个调用和一个 bypass；测试不新建模块。 |
| WI-196 FR-08 | 进入、非目标、命令、完成、停止、回退、evidence URI 已冻结。 |
| WI-196 FR-10 | Pascal/Confucius 对六文件同一 combined hash 独立评审。 |
| Reduction Contract | 本项是基础缺陷，RC 不适用且不计减重收益。 |

## 5. 项目结构与 allowlist

```text
specs/207-program-adapter-side-effect/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md

src/ai_sdlc/cli/main.py
src/ai_sdlc/cli/program_cmd.py
tests/integration/test_cli_program.py

specs/196-ai-sdlc-lean-code-self-reduction-governance/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md

specs/206-model-string-dedupe/
├── task-execution-log.md
└── development-summary.md

program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
.ai-sdlc/state/codex-handoff.md
.ai-sdlc/state/resume-pack.yaml
.ai-sdlc/work-items/207-program-adapter-side-effect/
```

Formal branch 禁止修改 `src/**`、runtime rules、provider、workflow；唯一测试例外是
`tests/integration/test_repo_program_manifest.py` 中由新增五件套机械触发的 exact inventory/close 两个
计数值，不新增测试逻辑或行数。Implementation branch 除上述两个产品/测试文件、WI207 归档/
continuity/truth 外不得扩大路径。`.cursor/rules/ai-sdlc.mdc` 即使被基线 CLI 临时刷新，也必须在
提交前精确恢复，不得进入任何 PR。Implementation 产品 allowlist 仅为 `main.py` 与
`program_cmd.py`；`ide_adapter.py`、ProgramService 和第三个 program handler 均禁止修改。

## 6. 阶段计划

### Phase 0：诊断与路线分流

**进入**：WI206 fresh-main acceptance 完成。
**动作**：分别复现 program validate、verify constraints、status；记录各文件 SHA 与 diff。
**完成**：证明 Cursor 和 resume-pack 是不同调用链，冻结 GAP-12/WI207 与 GAP-13/WI208。
**停止**：若 program/verify 直接调用 `load_resume_pack` 或 status 直接调用 adapter，重新划分边界。

### Phase 1：Formal authoring 与对抗评审

**进入**：`feature/207-program-adapter-side-effect-docs` 基于 `origin/main@506e950d`。
**动作**：补齐 child 五件套、父路线 GAP-12/GAP-13、WI206 关闭记录；同步 Program Truth。
**验证**：placeholder/path 检查、formal combined hash、`verify constraints`、truth validate/audit、
focused docs tests、`git diff --check`。
**完成**：Pascal 与 Confucius 对同一六文件 combined hash 双 PASS，formal PR 合入 main。
**回退**：revert formal PR；不涉及产品代码。

### Phase 2：TDD RED 与最小实现

**进入**：从 formal merge main 创建 `feature/207-program-adapter-side-effect-dev` 和独立 worktree。
**双轴证据**：

1. 原始 main 基线：只读 real-hook bytes RED，managed ingress transition GREEN；
2. PR #139 naive bypass：只读 bytes GREEN，managed ingress transition RED；
3. 候选：增加 `program_cmd.py` 一个 import/两个调用；solution-confirm 调用复用现有 early exits，
   不新增条件/分类器，两轴同时 GREEN。

**停止**：失败原因不是 root dispatch/持久化 ingress，或 GREEN 需要修改 `ide_adapter.py`、ProgramService、
第三个 handler、新增 helper/分类器，或产品 additions 超过 4 行。

### Phase 3：兼容、全量与差分

**focused**：

```text
uv run pytest tests/integration/test_cli_program.py tests/integration/test_cli_ide_adapter.py tests/unit/test_cli_hooks.py -q
```

**质量**：

```text
uv run ruff check src tests
uv run pytest -q
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
git diff --check
```

**差分**：记录原始基线、naive bypass 与候选 transcript、退出码、受保护文件 digest 和 ingress state；
expected delta 为除两个 managed 刷新入口外的全部 program 路径移除 root adapter notice/write；
managed-delivery-apply 保持入口刷新和既有 request materialization；solution-confirm continue 的
notice/hook 后移至全部门禁通过且 solution 已持久化之后、request 之前。传播异常可保留 confirmed
solution 但无 managed request/apply；config-lock 软失败仍 warning-and-continue。
**完成**：工作树只含 allowlist，truth fresh/ready、zero blocker。

### Phase 4：Implementation PR 与 fresh-main

**实现事实**：PR #139 已在同 HEAD/tree 双 Agent PASS、current-head Codex 无 finding、22/22 checks
通过后合并为 `8752aa97`。
**fresh-main 发现**：real-hook、focused、full 与 Ruff 业务断言通过，但 full suite 结束后 root resume-pack/
Cursor 变化；pristine worktree 的 verify、real-hook、focused 单独运行均 clean，根因收敛到 CLI tests 继承
真实 cwd，而非 verify 或产品 hook 回归。
**acceptance repair**：仅修改 `tests/conftest.py` 与 7 个已定位 CLI test 文件；共享 cwd fixture 由模块
显式 opt-in，self-update 在临时 cwd 初始化项目；session guard 比较 tracked status/index/content、全部
canonical adapter 目标、project config 与动态 scoped resume-pack。预算为 8 文件、gross `+135`、net
`+120`，产品 diff 必须为空。
**最终 fresh-main**：repair PR 合并后在新 detached worktree 重跑 real-hook nodeids、focused、full、Ruff、
constraints、truth；每个命令结束与总体结束均直接 clean，不允许 restore 后判 PASS。
**关闭**：只关闭 GAP-12；GAP-13 进入 WI208 formal，不发布版本。

## 7. 关键验证矩阵

| 关键路径 | RED/主验证 | 兼容验证 | 失败处置 |
|---|---|---|---|
| program root dispatch | real-hook bytes 在 baseline 变化 | 三个只读 program 命令参数化 | RED 不稳定则修 fixture，不改产品 |
| 普通 program tests 隔离 | autouse hook patch | full `test_cli_program.py` | 仍触碰真实 repo 则阻断 |
| managed ingress transition | naive bypass 保持 materialized/host blocker | apply 入口刷新；solution 在全部门禁后、request 前刷新 | 若需通用分类器或改 ProgramService 则回 design |
| solution authorization | missing yes/preflight blocked/no-continue/missing ack | local hook 零调用、adapter/config bytes 不变 | 任一失败路径写入即阻断 |
| non-managed program paths | truth sync execute、solution execute/no-continue | 无 hook/notice；业务 artifact 保持 | adapter/config 变化即阻断 |
| direct apply missing yes | root hook + request preflight 基线 | adapter/request 保持、无 mutate/apply result | 授权前执行 mutate 即阻断 |
| hook failure modes | RuntimeError 与 config-lock PermissionError | 前者停止 managed phase；后者 warning-and-continue | 吞掉未知异常或停止软失败即阻断 |
| truth execute | 既有 truth sync execute | audit/status surface | 输出/schema 差异即 revert |
| managed execute | 既有 managed apply execute | artifact assertions | 写入丢失即 revert |
| explicit adapter | CLI adapter/hook tests | Cursor/VSCode variants | 失效即 No-Go |
| full-suite checkout isolation | 受影响 8 文件 focused + session guard | full suite 前后 tracked/managed 摘要 | 任一增量变化保留现场并阻断 |
| cross-platform | GitHub Windows/macOS/Linux checks | byte-only assertions | 平台失败不合并 |
| parent route truth | manifest validate/audit | fresh-main audit | non-ready 重开对应 GAP |

## 8. 评审与哈希

Formal review target 使用 spec §8 的六文件集合。两位 Agent 必须分别从：

- Pascal：是否是四行内最直接修复、是否引入分类器/范围蔓延、测试成本是否必要；
- Confucius：program execute、adapter compatibility、真实仓库隔离、跨平台与回退是否完备；

进行只读复核。任一 finding 修订后，重新计算 combined hash，并让双方从零复审；只有双方对同一
hash 明确 PASS 才可提交 formal PR。

Implementation final review 绑定精确 HEAD、tree、binary diff、name-status、formal hash、targeted/full
结果和 fresh truth。review 后若改树，旧 verdict 自动失效。

## 9. 后续顺序

WI207 已合并并完成 fresh-main，WI208
`resume-pack-portable-lossless-reconstruction` 已建立并先裁决 canonical reconstruction source，再允许
修改 `context/state.py` / `core/handoff.py`。WI208 关闭后建立 WI209，单独修复 YAML quoted scalar 的
comment preservation false positive；WI209 fresh-main 后才恢复下一个 T63/T65/WP-06/WP-07 原子减重项。
WI-196 全路线满足 RC-08 前不发布版本。
