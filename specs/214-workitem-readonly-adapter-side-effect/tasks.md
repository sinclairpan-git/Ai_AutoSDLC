---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/213-programservice-bounded-stage-reduction/development-summary.md"
---
# 任务分解：Workitem 只读命令 Adapter 副作用隔离

**编号**：`214-workitem-readonly-adapter-side-effect`
**完成定义**：formal、implementation、lifecycle reconciliation 均 mainline/fresh-main；GAP-15 关闭；
不等于 T66/RC-08/release 完成

## Batch 1：formal current-main 冻结

### T11 初始化隔离 WI214

- **状态**：completed
- **范围**：`origin/main@d5ad7616`、docs worktree/branch、canonical 四件套、manifest/project sequence。
- **验收**：root dirty state 未带入；Cursor adapter 恢复 SHA=`d5f04acf...0b6a` 且相对 main diff=0。
- **回退**：删除 docs branch/worktree，不影响产品。

### T12 冻结 observed root cause 与范围

- **状态**：completed
- **依赖**：T11
- **验收**：源码证明 root callback 仅注入 hook；`_workitem_before_command` 对非 `None/init` 统一消费；
  `init` 在 preflight 后显式消费；`link` 依赖 callback。
- **范围**：五个 read-only 命令；不改 ProgramService/T66、adapter 算法、root callback、handler、依赖或版本。

### T13 冻结 expected delta 与兼容矩阵

- **状态**：completed
- **依赖**：T12
- **验收**：15 格只读矩阵只允许 hook 1→0 与 adapter receipt/write 消失；代表性 `plan-check normal` 有
  production real-hook A/B；共享 hook 层只补一例 partial-write；`init/link` 区分 warning+continue 与其他
  异常传播且 §3.2 零差异；
  normalizer=none，stdout/stderr/exit exact。
- **停止**：需要全局 classifier、第二 CLI family 或 handler 变化即回 design。

### T14 formal 双 Agent 对抗评审

- **状态**：completed
- **依赖**：T13
- **review target**：parent+child 各 `spec.md + plan.md + tasks.md` 的同一 committed+clean identity。
- **Pascal/LEAN**：范围、直接性、测试复用、是否过度抽象/过度测试、回退是否原子。
- **Confucius/SAFETY**：help/invalid 解析时机、init/link 负路径、输出/bytes/异常/平台/回退。
- **通过**：双方同 identity `PASS`、actionable findings=0；任一受审文件变化后双方从零复审。
- **完成**：Round 4 HEAD/tree=`3a2b2b6f`/`e99e0ef9`、formal-six=`82351757...9d79`；
  Pascal/LEAN 与 Confucius/SAFETY 均 PASS0。Closure material 改变受审文件后该 receipt 仅保留为
  authoring PASS，T15 final current identity 必须再次双审。

### T15 formal truth、PR 与 fresh-main

- **状态**：in_progress
- **依赖**：T14
- **验收**：constraints/validate/truth/manifest/scope/parity/Cursor/clean 全绿；final identity 再双 PASS0；
  Codex current-head 与 required checks 全绿；merge/reviewed tree 一致；detached fresh-main 通过。
- **完成边界**：只授权 Phase 1；T58/GAP-15 仍 open，T66 T61A 仍 blocked。

## Batch 2：implementation TDD

### T21 从 formal fresh main 建 dev 隔离环境

- **状态**：pending
- **依赖**：T15
- **验收**：branch=`feature/214-workitem-readonly-adapter-side-effect-dev`；clean worktree；formal truth fresh。
- **格式基线**：RED 前把 `FORMAT_BASE_SHA` 冻结为本 amendment detached fresh-main exact SHA，后续 dev/PR/
  merge/fresh-main 不得改用动态 `origin/main`。

### T22 建立 RED 分发与兼容证明

- **状态**：pending
- **依赖**：T21
- **验收**：产品源码未改；唯一新文件=`tests/integration/test_cli_workitem_adapter_dispatch.py`；15 格在
  legacy 上因 hook/write/receipt 至少一项按预期失败；`plan-check normal` 一组 real-hook A/B 记录 guarded
  SHA/status/output；共享 hook 层一例 partial-write；删除 `test_cli_workitem_init.py` 中过时的
  `test_workitem_non_init_runs_adapter_before_handler_once`，其反转断言由新 dispatch 文件的参数化
  `plan-check normal` 格承接；除此迁移外，`init/link` 既有文件只补 call order 与两类 outcome。
- **约束**：优先参数化与复用 fixture；不得复制五套 handler 业务测试。

### T23 实施唯一 callback 修正

- **状态**：pending
- **依赖**：T22
- **范围**：只把 `_workitem_before_command()` 收敛为 `ctx.invoked_subcommand != "link"` 时 return。
- **验收**：一个既有产品函数变化；无命令名单、新产品文件、公共符号、classifier、依赖、配置或版本。
- **回退**：revert 单一实现 commit。

### T24 GREEN 与零差异回归

- **状态**：pending
- **依赖**：T23
- **验收**：15 格 hook=0、sentinel/config/tree bytes stable、no-op-hook stdout/stderr/exit exact；
  `plan-check normal` production A/B bytes/hash/status exact；共享 partial-write 与 `init/link` 全矩阵零未批准差异。
- **精确 targeted**：`uv run --python 3.11 pytest tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py -q`
- **全量/静态门禁**：`uv run --python 3.11 pytest -q`；`uv run --python 3.11 ruff check src tests`；
  `uv run --python 3.11 ruff format --check tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py`；对 formal base 已 formatter-red 的 `workitem_cmd.py` 与
  `test_cli_workitem_init.py` 在 committed+clean identity 执行 plan §5.3 的 fixed-base V4b 程序，要求
  candidate red path set 是 base set 的大小写敏感子集、工具退出与输出可解释，且全部 candidate changed/
  deletion-boundary range format-check 通过；`uv run --python 3.11 ai-sdlc verify constraints`；`git diff --check`。

## Batch 3：implementation truth、review 与 mainline

### T31 冻结 implementation terminal truth 与本地门禁

- **状态**：pending
- **依赖**：T24
- **验收**：先完成 execution log、real-hook/RED/GREEN receipt、program truth、root/scoped handoff；再跑
  `uv run --python 3.11 pytest tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py -q`、
  `uv run --python 3.11 pytest -q`、Ruff check/format、constraints、validate/truth、manifest exact、scope/
  parity/Cursor/clean，最后提交并冻结 terminal identity。

### T32 implementation 最终双审、PR、CI、merge 与 fresh-main

- **状态**：pending
- **依赖**：T31
- **验收**：Pascal/LEAN 与 Confucius/SAFETY 对 T31 后同一 committed+clean identity 双 PASS0；任何修订先
  重跑相关 gate/truth 再重审。Codex reviewed current head 无 actionable finding、required checks success、
  merge；detached fresh-main 重跑
  `uv run --python 3.11 pytest tests/integration/test_cli_workitem_adapter_dispatch.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_link.py tests/unit/test_cli_hooks.py -q`
  及 full/Ruff/治理/real-hook bytes/clean-tree。
- **完成边界**：只声明 implementation accepted；GAP-15/T58 仍 active，T66 T61A 仍 blocked。

## Batch 4：lifecycle reconciliation 与关闭

### T41 创建独立 lifecycle reconciliation

- **状态**：pending
- **依赖**：T32
- **分支**：`codex/214-workitem-readonly-adapter-side-effect-lifecycle`，从 implementation fresh main 创建。
- **验收**：只写 child/parent lifecycle docs、truth/continuity与 manifest exact 机械期望；登记 implementation
  reviewed/merge/fresh-main receipt，把 parent T58/GAP-15 标记 completed/closed；`src/tests` 零差异。

### T42 lifecycle final 双审、PR 与 fresh-main

- **状态**：pending
- **依赖**：T41
- **验收**：truth/handoff/gates 先完成；Pascal/Confucius 对 final current identity 双 PASS0；Codex/
  required checks/merge/detached fresh-main 全绿后，唯一下一步才是创建 T66 implementation WI并先执行
  T61A 双 readiness。
- **回退**：lifecycle 已 merge 时先 revert/修正 closure receipt 以重开 GAP-15、阻断 T66，再 revert
  implementation PR；不得留下 closed truth。
- **边界**：不声明 T66、GAP-03、WI196、RC-08 或 release 完成，不发布版本。

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| FR-001～FR-003、SC-001～SC-002 | T12～T13、T22、T24、T31～T32 |
| FR-004、SC-003 | T13、T22、T24、T31～T32 |
| FR-005～FR-006、SC-004 | T13、T22～T23 |
| FR-007、SC-006 | T14～T15、T31～T32、T41～T42 |
| FR-008～FR-009、SC-005～SC-006 | T15、T21、T31～T32、T41～T42 |
| FR-010～FR-011、SC-007 | T15、T32、T41～T42 |
| NC-01～NC-06 / CC-05 / GAP-15 | T11～T42 |
