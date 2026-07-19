# 开发摘要：Workitem 只读命令 Adapter 副作用隔离

**功能编号**：`214-workitem-readonly-adapter-side-effect`
**当前状态**：formal PR #160 已 merge/fresh-main；V4 amendment Round 2 correction 与 terminal gates 已完成，待新身份双审；产品实现暂停

## 已冻结合同

- 产品设计只有一处直接谓词：workitem 子应用 callback 仅让当前 `link` 消费 hook，`init` 继续由 handler
  在 preflight 后消费；五个 read-only 命令与未来未显式授权命令默认不产生隐式写副作用。
- 只读证据分层为 15 个 normal/help/invalid sentinel case、原始 `plan-check normal` 一组 production/no-op
  real-hook A/B，以及共享 hook 层一例 config-lock partial-write；不构造五命令 real-hook 笛卡尔积。
- `init/link` 只回归本次分发相关的 hook count/order、warning-return 后 handler continuation、其他异常传播、
  output/exit/write set；不复制 adapter 内部 fixture、不新增事务化。
- 测试布局固定为一个新增参数化 dispatch 文件、两个既有 init/link integration 文件和既有 hook unit 文件；
  V1 targeted、full、Ruff、constraints 与 diff-check 命令已明确。
- Formal、implementation、lifecycle reconciliation 分三个 branch/PR；每阶段都 truth/gates first、final
  current-identity 双 PASS0、Codex/current-head checks、merge 与 detached fresh-main。
- Lifecycle fresh-main 才关闭 GAP-15/T58并授权 T66 T61A。关闭后回退必须先重开 truth/阻断 T66，再
  revert implementation，禁止代码与状态分裂。

## 对抗评审

- Round 1 Pascal FAIL1 / Confucius FAIL4：补精确测试布局与命令、lifecycle PR、truth-before-review、
  两类异常和 production-hook evidence。
- Round 2 Pascal FAIL2 / Confucius FAIL1：把五组 production A/B 收敛为一组，把两套 partial-write 收敛为
  共享一例，并统一三阶段 canonical 定义。
- Round 3 Pascal PASS0 / Confucius FAIL1：只修正 parent plan 遗留的 implementation closure 旧措辞。
- Round 4 对同一 clean identity `3a2b2b6f`/tree `e99e0ef9`/formal-six `82351757...9d79`，
  Pascal/LEAN 与 Confucius/SAFETY 均 PASS、actionable findings=0。
- Round 4 是 authoring receipt；本 summary/T14/T15/truth/handoff 变化后，formal PR 前必须对 final current
  identity 重新双审，不能拼接历史 verdict。
- Round 5 修正 T66 lifecycle 准入与 canonical review identity；Round 6 同一 identity 双 PASS0。PR #160
  Codex current-head P2 又发现既有 init 测试中的 `plan-check` 旧断言未获迁移授权；formal 已显式允许删除
  该单一旧测试并由新 dispatch 参数格承接，Round 6 verdict 因 formal 变化全部退役。

## 完成与未完成边界

- 已完成：current-main 根因、范围、expected delta、最小设计、测试与异常矩阵、生命周期/回退合同、
  authoring 对抗评审收敛；formal PR #160 merge、detached fresh-main；amendment Round 2 correction 与 terminal
  truth/audit/gates。
- 尚未完成：amendment continuity correction 后同一 final identity 双 PASS0、PR/checks/merge/detached fresh-main。
- 已开始但暂停：RED/GREEN、产品 callback 与测试实现；须等待 amendment fresh-main 后重放、复验。尚未开始：
  implementation/lifecycle PR、T66 T61A。
- GAP-15/T58、T66、GAP-03、WI196、RC-08 与 release 均保持 open；当前禁止版本/tag/Release/PyPI/
  共享 CLI 更新。
- Implementation 预审发现 formal V4 错把主线 273 个历史 formatter-red 文件设为全库零债务门禁；独立
  amendment 仅改为 changed-file strict + legacy baseline-delta，不授权格式化非范围文件或放宽其他门禁。
- Amendment final review Round 1 对 `a91bbba3` 一致否决动态 base/count-only 判定；当前改为固定
  `FORMAT_BASE_SHA`、red path set subset 与 changed-range Ruff check；terminal truth/gates 已全绿。Round 2
  对 `5cad2581` 否决 range 终点/删除边界、native failure、dirty candidate 与路径大小写假绿，并指出 summary/
  handoff 下一步陈旧；成立项已最小修正并通过 terminal gates。Round 3 对 `67455e7e` 的技术审查无新增问题，
  两位 reviewer 均只报 P3 continuity 仍停留在 pre-sync；本次同步修正后，Round 3 verdict 全部退役。
