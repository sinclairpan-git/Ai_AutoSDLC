# 任务分解：Program 治理命令 IDE Adapter 副作用隔离

**编号**：`207-program-adapter-side-effect`
**日期**：2026-07-16
**来源**：`spec.md` + `plan.md`
**风险**：L2 / GAP-12 基础副作用修复（影响 CC-05）；不计 `completed_reduction`

## Batch 1：诊断、分流与 formal baseline

### T11 复现并隔离两个根因

- **状态**：已完成
- **依赖**：WI206 fresh-main acceptance
- **证据**：detached `origin/main@506e950d`
- **验收**：
  1. `program validate` 只改 `.cursor/rules/ai-sdlc.mdc`，记录 before/after SHA；
  2. `verify constraints` 不产生新的 adapter/continuity diff；
  3. `status` 重建两份 resume-pack 为 worktree 绝对路径并清空 branch/active/context；
  4. 调用链证明 Cursor 属于 root CLI hook，resume-pack 属于 `load_resume_pack()`。
- **结论**：创建 GAP-12/WI207 与 GAP-13/WI208，不合并实现。

### T12 初始化 WI207 canonical formal

- **状态**：已完成
- **依赖**：T11
- **文件**：child 五件套、project-state、program manifest
- **验收**：docs branch=`feature/207-program-adapter-side-effect-docs`；worktree 基于
  `origin/main@506e950d`；`next_work_item_seq=208`；canonical spec entry 存在。

### T13 回写 WI206 与父路线

- **状态**：已完成
- **依赖**：T12
- **文件**：WI206 execution/summary、WI196 五件套
- **验收**：
  1. 记录 PR #137、merge `506e950d`、fresh-main full `3220 passed, 3 skipped`；
  2. WI206=`completed_reduction`，只关闭一个 T63 family；
  3. 父台账新增 GAP-12/GAP-13 和 T55/T56；
  4. 不误报 GAP-05、WI196、RC-08 或 release 完成。

### T14 同步 formal truth 与 continuity

- **状态**：已完成
- **依赖**：T13
- **命令**：
  1. `uv run ai-sdlc program truth sync --execute --yes`
  2. `uv run ai-sdlc program validate`
  3. `uv run ai-sdlc program truth audit`
  4. `uv run ai-sdlc verify constraints`
- **验收**：truth fresh/ready、zero blocker、inventory complete；由已知 GAP-12 临时刷新的 Cursor rule
  使用 `apply_patch` 精确恢复 HEAD；continuity 使用 repo-relative path，WI207 root/scoped copy 一致；
  root exact truth test 只机械更新 inventory/close 两个计数并通过。

## Batch 2：Formal 对抗评审与 mainline receipt

### T21 运行 formal 静态门禁

- **状态**：已完成
- **依赖**：T14
- **验收**：六文件无 placeholder/矛盾/未分配责任；路径 allowlist、`git diff --check`、root exact truth
  test、working/cached diff-check 通过；记录每文件 SHA 与 combined SHA。

### T22 Pascal 精简直接性评审

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；历史轮次仅保留在日志
- **依赖**：T21
- **验收**：只读复核同一 combined hash；确认四行窄边界、无分类器、测试最小充分、GAP-13 未混入；记录
  findings/disposition/verdict 与起止 HEAD/tree。

### T23 Confucius 兼容安全评审

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；历史轮次仅保留在日志
- **依赖**：T21
- **验收**：只读复核与 T22 完全相同的 combined hash；确认 execute、adapter、测试隔离、跨平台、
  rollback 与 fresh-main 合同；记录 findings/disposition/verdict 与起止 HEAD/tree。

### T24 修订直到同哈希双 PASS

- **状态**：以 execution log 最新 formal 同哈希终态回执为准；formal 文件不内嵌动态 verdict/hash
- **依赖**：T22、T23
- **验收**：任一 FAIL 都先修订、重跑 T14/T21、生成新 combined hash，再让双方从零复审；只有同一
  hash 双 PASS 才结束。用户不承担 formal 逐条评审。

### T25 Formal PR、Codex review、CI 与 merge

- **状态**：已完成；PR #140 合并为 `8d325a4d`，fresh-main formal gates 全绿
- **依赖**：T24
- **验收**：单一 docs commit、push、PR、`@codex review`、heartbeat、required checks 全绿；actionable
  finding 修复后重新双审/重跑；formal PR 合入 main，fresh-main truth/constraints 通过。

## Batch 3：Implementation TDD

### T31 创建独立 implementation branch/worktree

- **状态**：已完成；implementation branch 已基于 formal merge `8d325a4d` rebase，过期 docs commits 已跳过
- **依赖**：T25
- **验收**：`feature/207-program-adapter-side-effect-dev` 从 formal merge main 创建；formal worktree
  不承载源码；implementation baseline clean。

### T32 添加 program test autouse 隔离

- **状态**：已完成；root/program-local 双 binding 已隔离，真实 hook 用例显式豁免
- **依赖**：T31
- **文件**：`tests/integration/test_cli_program.py`
- **验收**：普通用例同时 patch root/program-local hook；naive/pre-import 阶段对 local binding 使用
  `create=True`，候选阶段确认真实 import；`real_ide_hook` 明确豁免；不创建新 fixture 文件；测试本身
  不会写 implementation checkout。

### T33 添加 real-hook byte-stability RED

- **状态**：已完成原始基线/naive bypass 两态证据
- **依赖**：T32
- **文件**：`tests/integration/test_cli_program.py`
- **验收**：参数化覆盖 validate、truth audit、truth sync dry-run；临时 Cursor target 同时含 legacy `.md`
  与 `.mdc`；比较 adapter/config/manifest bytes；baseline 稳定失败于 adapter 写入/notice，而非 fixture。

### T34 记录 naive bypass 兼容 RED

- **状态**：已完成；PR #139 Codex P2 已接受，candidate 前兼容 RED 已固定
- **依赖**：T33
- **文件**：`tests/integration/test_cli_program.py`
- **验收**：无宿主信号 materialize Codex adapter 后设置 `OPENAI_CODEX=1`；naive bypass 下
  managed-delivery dry-run 仍为 `materialized`、保留 host blocker；solution-confirm continue 未刷新。

### T35 实施四行窄化 gating

- **状态**：已完成；implementation commit `c4e5f07d`，产品 additions=4、测试 additions=110
- **依赖**：T34、兼容 formal 双 PASS/mainline
- **文件**：`src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/program_cmd.py`
- **验收**：保留 `"program"` tuple member；新增一个既有 hook import；managed-delivery-apply 在 root
  resolution 后/request 前调用；solution-confirm 复用现有 early exits，在 yes/preflight/continue/ack
  全通过且 solution 已持久化后、request 前单行调用。产品 additions≤4；不改 `ide_adapter.py`/
  ProgramService，不新增函数/模块/API/config/dependency/分类器；只读与 ingress 两轴同时 GREEN。

## Batch 4：兼容、全量与 final tree

### T41 运行 focused 与 execute compatibility

- **状态**：已完成；focused `238 passed`
- **依赖**：T35
- **命令**：
  `uv run pytest tests/integration/test_cli_program.py tests/integration/test_cli_ide_adapter.py tests/unit/test_cli_hooks.py -q`
- **验收**：full program integration、adapter/hook tests 全绿；truth sync execute 和 managed execute 既有
  用例通过；首次 managed ingress 从 materialized 升级为 verified_loaded；solution-confirm 完整授权路径
  exactly once，missing yes/preflight blocked/no-continue/missing ack 均零调用/零 adapter 写入；无未批准差异。
- **补充验收**：truth sync execute 与 solution execute/no-continue 无 hook/notice、adapter/config bytes
  不变且业务 artifact 正常；direct managed execute missing yes 保留 adapter/request preflight、无
  mutate/apply result；RuntimeError 停止 managed phase，config-lock 继续 warning-and-continue。

### T42 运行 full、Ruff 与治理门禁

- **状态**：已完成；Ruff PASS、full `3224 passed, 3 skipped`、治理门禁全绿
- **依赖**：T41
- **命令**：
  1. `uv run ruff check src tests`
  2. `uv run pytest -q`
  3. `uv run ai-sdlc verify constraints`
  4. `uv run ai-sdlc program validate`
  5. `uv run ai-sdlc program truth audit`
  6. `git diff --check`
- **验收**：全部通过；三个只读 program 命令不改 Cursor；managed-delivery 两入口保留兼容刷新；truth
  fresh/ready、zero blocker；工作树只含 allowlist。

### T43 生成差分与回退证据

- **状态**：已完成；implementation commit 精确 revert/reapply 后 tree 均逐字节匹配目标
- **依赖**：T42
- **验收**：记录原始基线/naive bypass/候选 transcript、exit、受保护 digests 与 ingress state；非两个
  managed 刷新入口的全部 program 路径移除 root adapter notice/write；direct apply missing yes 的
  adapter/request preflight 保持；solution-confirm notice/hook 后移，传播异常无 managed request/apply，
  config-lock 软失败继续；`git revert` rehearsal 后原始行为恢复，reapply 后 candidate 恢复。

### T44 Final tree 双 Agent 复审

- **状态**：以外部 final-tree 同 HEAD/tree 双 Agent 回执为准；本表不内嵌动态 verdict
- **依赖**：T43
- **验收**：Pascal/Confucius 对同一 HEAD/tree/binary diff/name-status/formal hash/test evidence 均 PASS，
  无 actionable finding；评审后不再修改树，若修改则 verdict 作废。

## Batch 5：Implementation PR 与 fresh-main

### T51 Push、PR、Codex review 与 required checks

- **状态**：PR #139 draft；formal/实现修订已完成，待 final-tree 双 PASS 后重请求 Codex review
- **依赖**：T44
- **验收**：单逻辑实现 commit、push、ready PR、`@codex review`、约五分钟 heartbeat；findings focused
  修复并重新验证/复审；required checks 全绿。

### T52 Merge 与 fresh-main acceptance

- **状态**：待执行
- **依赖**：T51
- **验收**：fresh detached `origin/main` 重跑 real-hook nodeids、focused、full、Ruff、constraints、truth；
  branch tree 与 mainline 内容一致、工作树 clean；GAP-12 具备关闭证据。

### T53 启动 WI208 并继续父路线

- **状态**：待执行
- **依赖**：T52
- **验收**：下一 work item 为 WI208 `resume-pack-portable-lossless-reconstruction-sources`；更新父台账时
  GAP-12=closed、GAP-13=active；不关闭 GAP-05/WI196/RC-08，不发布版本。WI208 关闭后再选下一个
  T63/T65/WP-06/WP-07 原子减重项。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| GAP-12 / T55 | T11～T53 |
| GAP-13 / T56 分流 | T11、T13、T53 |
| NC-01～NC-06 | T11～T14、T21～T24、T34～T35 |
| CC-01～CC-03 | T33～T43、T52 |
| CC-05 / CC-06 | T32～T43、T52 |
| CC-07 | T33、T41、T51、T52 |
| FR-001～FR-012 | T14、T21～T53 |
| SC-001～SC-008 | T21～T53 |
| WI-196 FR-08 / FR-10 | T13、T21～T25、T44 |
