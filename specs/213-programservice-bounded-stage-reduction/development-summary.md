# 开发摘要：ProgramService 九阶段精益减重正式合同

**功能编号**：`213-programservice-bounded-stage-reduction`
**状态**：formal contract mainline / detached fresh-main 已完成；lifecycle reconciliation 收口中

## 本地已交付

- 在 `main@e184c8e27818aa7950fcc64dbb10fa7a65888f8c` 复算九阶段/五方法族：45 methods=
  `3,638 physical / 3,305 executable / branch proxy 386`；165 个现有测试实跑通过。
- 冻结单一 private module、27 个 public thin facade 和九组显式 binding 的最小结构；禁止反射、DSL、
  stage-name 分支、循环 import、DTO 移动、公共开关、新依赖或第二领域。
- 冻结 `product≤522`、`proof≤190`、`product+proof≤712`、`terminal≤720`、`net delete≥2,918`、
  `ProgramService responsibility reduction≥3,278`；任一超限立即 RC-09 No-Go，不扩大预算。
- T61A/B 覆盖 Python API/DTO surface、late-bound `self` truthiness/clock、CLI、artifact/raw bytes、授权、
  异常、中断恢复、平台、wheelhouse no-index offline install、sibling 与性能。
- Candidate 合入时 legacy 保留；主线预发布稳定期后独立 deletion PR；删除合入后对精确 merge commit
  实际 revert，再回 deletion fresh-main 验证。删除前不关闭 T66。
- Formal 验证新登记 GAP-15：`workitem` 只读子命令会隐式 refresh adapter。该缺陷由独立 T58/WI/PR
  先关闭；其 fresh-main 前不创建 T66 implementation WI/T61A。

## 对抗评审

- Pascal/LEAN 与 Confucius/SAFETY 始终对同一 committed+clean parent+child formal-six 从零评审。
- Round 1～4 的双 FAIL/split verdict 共收敛：错误 WI211 hash 示例、授权矛盾、Python surface、late-bound
  dispatch、truthiness/clock normalizer、portable fingerprint、offline install、NO-GO evidence、post-merge
  rollback、T58 负路径与 normalized-code YAGNI；所有成立 finding 均做最小修正。
- Round 5 HEAD/tree=`e00aea25bc9ddb5da475e22eb6f02ba820cec4c0`/
  `f17e24baf9747488a7a178d175bead33daf8db84`，formal-six=
  `674407cf6ac8c2f726a3975dc6fffeac0cc88786bf50a19d0e1687d09684cf27`；双方均
  `PASS`、actionable findings=0。
- Round 5 只作为 authoring receipt；Round 7 因后续 Codex P2 修订退役。最终 Round 9 身份
  HEAD/tree=`94acfdf424932d354bde33f2bd9a8a554fa63fb8`/
  `9d1c0f6915e31bf79d2d2fd768adc5a5ca8ffe05`、formal-six=
  `283b623babe7b98eb8d62acb79af2cea79e56d36941cb5269ad3ffbd5f61f099`，双方再次
  `PASS`、actionable findings=0。

## 完成与未完成边界

- Program truth terminal sync、最终本地门禁与 Round 9 双审已完成：truth=`ready/fresh 1121/1121`、
  unmapped/missing=`0/0`，manifest exact、165 个目标测试、constraints 与 validate 均通过。
- PR #158 的 current-head review、13/13 checks 与 squash merge `450d4988` 已完成；detached fresh-main
  验证 merge/reviewed tree=`9d1c0f69` 且 truth/tests/scope/parity/clean 全绿。
- 本 WI 没有产品代码、selector、candidate、legacy deletion、版本/tag/Release/PyPI 或全局 CLI 更新。
- GAP-15、T58、T61A/B、T66、GAP-03、WI196、RC-08 和总体版本发布均保持 open。
- 本 lifecycle reconciliation 取得双审/mainline/fresh-main 后，唯一下一项才是创建独立
  T58/GAP-15 WI；T58 fresh-main 后才可创建 T66 implementation WI。
