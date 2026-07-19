# Continuity Handoff

- Updated: 2026-07-19T19:40:00Z
- Reason: WI214 formal Round 4 authoring 双 PASS0 后创建 closure material
- Goal: 关闭 GAP-15/T58，保持五个 workitem 只读入口零副作用且 init/link 零回归
- State: Round 4 authoring 双 PASS0；development summary/T14-T15 已更新；待 source commit、truth sync、terminal gates/final review
- Stage: decompose
- Work Item: 214-workitem-readonly-adapter-side-effect
- Branch: feature/214-workitem-readonly-adapter-side-effect-docs
- Base: origin/main@d5ad7616f7f39f68365d6d39f8701a86c1f599e7

## Changed Files

- .ai-sdlc/project/config/project-state.yaml
- .ai-sdlc/state/codex-handoff.md
- .ai-sdlc/work-items/214-workitem-readonly-adapter-side-effect/codex-handoff.md
- program-manifest.yaml
- specs/214-workitem-readonly-adapter-side-effect/spec.md
- specs/214-workitem-readonly-adapter-side-effect/plan.md
- specs/214-workitem-readonly-adapter-side-effect/tasks.md
- specs/214-workitem-readonly-adapter-side-effect/task-execution-log.md
- specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md
- specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md
- specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md
- specs/196-ai-sdlc-lean-code-self-reduction-governance/task-execution-log.md
- specs/196-ai-sdlc-lean-code-self-reduction-governance/development-summary.md
- specs/213-programservice-bounded-stage-reduction/task-execution-log.md
- specs/213-programservice-bounded-stage-reduction/development-summary.md

## Key Decisions

- WI213 lifecycle reconciliation 已由双 PASS0、PR #159、merge d5ad7616 与 detached fresh-main 收口。
- GAP-15/T58 当前唯一执行项为 WI214；其 implementation fresh-main 前 T66 T61A 继续阻断。
- 根因是 workitem 子应用 callback 对除 init 外全部已识别命令消费 adapter hook。
- 五个只读命令为 plan-check、guard、close-check、branch-check、truth-check；normal/help/invalid 都须 hook=0。
- 最小实现只让 callback 在 invoked_subcommand == link 时消费 hook；init 继续在自身 handler 的 preflight 后消费。
- 不维护五命令名单，不新增 classifier/registry/decorator/配置/依赖/版本，也不改 adapter 算法、handler、root callback 或 ProgramService/T66。
- 唯一批准差异是五个只读入口 hook 1->0 以及 adapter receipt/write 消失；handler stdout/stderr/exit 与 no-op-hook 基线 exact。
- init/link valid、missing、dirty/preflight、no-project、no-checkpoint、hook exception 的适用矩阵全部零未批准差异；init no-checkpoint 明确 N/A。
- formal、implementation、lifecycle reconciliation 分 branch/PR；formal final fresh-main 后才创建 dev branch并以 RED 测试开始。
- Implementation fresh-main 后必须有独立 lifecycle reconciliation branch/PR 承载 closed truth；其
  fresh-main 前 GAP-15/T58 仍 active、T66 仍 blocked。
- Implementation 顺序为 terminal truth/handoff/gates -> committed+clean identity -> 双 PASS0 -> PR；
  review 后任何内容变化都先重跑 gate/truth 再重审。
- 测试布局固定为一个新增参数化 adapter-dispatch 文件 + 两个既有 init/link 文件；V1 targeted 命令已冻结。
- 15 格 sentinel 覆盖全部命令；production real-hook 只对原始 `plan-check normal` 做一组 A/B，避免五次重复。
- 共享 hook 层只补一例 config-lock partial-write；init/link 只验证 warning-return 与 raise 的继续/中断顺序，
  不复制 adapter 内部 fixture且不事务化 adapter。
- Pascal/LEAN 与 Confucius/SAFETY 必须审同一 committed+clean identity；任一受审文件变化使双方 verdict 同时失效。
- T58 不计减重收益，不关闭 T66/GAP-03/WI196/RC-08，不触发版本发布。

## Commands / Evidence

- workitem init 已创建 canonical 四件套、project sequence 214->215、manifest entry。
- Cursor adapter refresh observed SHA=02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134。
- 已通过 apply_patch 恢复 Cursor base SHA=d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a。
- git diff --exit-code origin/main -- .cursor/rules/ai-sdlc.mdc：PASS。
- 源码/测试只读盘点确认 main.py 只注入 hook、workitem callback 管分发、init 显式消费、link 依赖 callback。
- Typer fake-hook 探针确认：五个 read-only help/invalid 当前消费 hook；link help/missing 消费；init help/missing 与 unknown subcommand 不消费。
- Feasibility reviewer：GO；建议一处 link-only 条件 + 一个聚焦矩阵测试，反对全局 classifier、测试 DSL 与笛卡尔积。
- authoring commit=`d3acfedea507a23bb30d53d84906c11a0c03c41a`；15-file formal/state/manifest scope，产品/测试 diff=0。
- `uv run --python 3.11 ai-sdlc program validate`：PASS。
- `uv run --python 3.11 ai-sdlc verify constraints`：首轮发现 handoff 删除旧 review 标题未记理由；补 tracked execution-log 理由后 `no BLOCKERs`。
- `git diff --check` 首次发现 Markdown hard-break trailing spaces；已移除，待 correction commit。
- 尚未运行 RED/GREEN、targeted/full/truth；formal Round 1 已完成但未通过。
- Round 1 identity=`1603d4b1`/tree `2d109ccd`/formal-six `aa24fb80...2f63`；Pascal FAIL1、
  Confucius FAIL4，五项均 ACCEPT，旧 verdict 退役。
- Round 1 correction gates：program validate PASS、constraints no BLOCKER、diff-check、scope、handoff parity、
  Cursor base SHA/diff、frontmatter 全绿；`src/tests` diff=0。
- Round 2 identity=`144c8c50`/tree `37de73e3`/formal-six `53d85b2a...246c`；Pascal FAIL2、
  Confucius FAIL1。三阶段 canonical、代表性 real-hook 与共享 partial-write 三项全部 ACCEPT，旧 verdict 退役。
- Round 2 correction gates：program validate PASS、constraints no BLOCKER、frontmatter、diff-check、scope、
  handoff parity、Cursor base SHA/diff 全绿；`src/tests` diff=0。
- Round 3 identity=`fb08062a`/tree `a654cd60`/formal-six `c92563fb...ee55`；Pascal PASS0、
  Confucius FAIL1。唯一成立项是 parent plan 把 closure 错写成 implementation fresh-main；已改为 lifecycle
  reconciliation fresh-main，Round 3 双方 verdict 同时退役。
- Round 3 correction gates：program validate PASS、constraints no BLOCKER、diff-check、scope、handoff parity、
  Cursor base SHA/diff 全绿；`src/tests` diff=0。
- Round 4 identity=`3a2b2b6f`/tree `e99e0ef9`/formal-six `82351757...9d79`；Pascal/LEAN 与
  Confucius/SAFETY 均 PASS0。Closure material 变化使该 receipt 降为 authoring PASS，final identity 必须重审。

## Blockers / Risks

- formal 双 Agent PASS0 与 formal mainline/fresh-main 前禁止修改 src/tests。
- 最大回归风险是误改 link 在 help/invalid/no-project/no-checkpoint 前的 hook 时序。
- real-hook 测试只能在 tmp_path 项目运行，不得再次对 WI214 worktree 根调用会触发现有缺陷的只读 CLI。
- adapter hook exception 的部分写入事务化不属于 WI214；不得扩到 adapter 算法。
- root worktree 含用户未提交内容，保持完全隔离。
- 本地主机 PowerShell 有既知 .NET regex assembly 问题；必要时 Python/zsh fallback，CI 继续覆盖 Windows。
- RC-08 前禁止 tag、GitHub Release、PyPI 与共享 CLI 更新。

## Exact Next Steps

1. 提交 closure source，确认 clean source identity。
2. 执行一次 terminal `program truth sync --execute --yes`，提交 snapshot/机械 manifest exact 期望。
3. 跑 manifest exact、constraints、validate/truth、scope/parity/Cursor/clean gates；提交必要 receipt。
4. 计算 final current identity，让 Pascal/Confucius 从零双审到同 identity PASS0。
5. Push formal PR、@codex review、等待 required checks，merge 并 detached fresh-main。
6. 仅从 formal fresh main 创建 dev branch/worktree，先 RED 后一处 callback GREEN。
