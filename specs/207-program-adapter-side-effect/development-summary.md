# WI-207 Development Summary

**状态**：closed；implementation PR #139 与 test-isolation repair PR #141 已合并并完成 fresh-main

WI207 关闭 WI196 新登记的 GAP-12：任意 `program ...` 在业务命令前隐式刷新 IDE adapter，导致
Program Truth/验证命令和 program 集成测试可能改写真实 checkout 的 tracked Cursor rule。

当前修订后的最小实现是：`main.py` 保留一个 `"program"` bypass member；`program_cmd.py` 只新增一个
既有 hook import，并在 `managed-delivery-apply` 与 `solution-confirm --execute --continue` 增加两个局部
调用；测试同时隔离 root/local binding，并新增首次 host-ingress 迁移证据。产品预算最多 4 行，不修改
adapter 实现、ProgramService、第三个 handler、resume-pack 或 verify telemetry。

Formal PR #140 已合并为 `8d325a4d`，fresh-main constraints、root exact、validate/truth audit 全绿。
Implementation branch 随后 rebase；最终实现 HEAD `8bbff9bd` 的产品 diff 为严格 4 行，测试
`+110/-22`，focused=`238 passed`、full=`3224 passed, 3 skipped`；Pascal/Confucius 对同一 HEAD/tree
双 PASS，current-head Codex 无 finding、22/22 checks 通过。PR #139 已合并为 `8752aa97`，对实现提交的
detached revert/reapply 演练分别与 formal main/candidate tree 完全一致。

首轮 fresh detached main 的 real-hook、focused、full 与 Ruff 业务断言全部通过，但 full suite 结束后
root resume-pack 与 Cursor rule 变化；pristine verify、real-hook、focused 单独运行均 clean。逐测试 guard
定位到 8 组 CLI tests 继承真实 cwd。当前 repair 只改 8 个测试文件：共享临时 cwd fixture、self-update
临时项目初始化，以及 session-level repository state guard；产品 diff 为空。精简/安全两位 Agent 已对
  约 99 行 guard 设计达成一致，最终 affected=`196 passed, 1 skipped`、full=`3224 passed, 3 skipped`，
  guard 与外部 pre/post 摘要均直接相同。repair final tree 取得双方同目标双 PASS，PR #141 current-head
  Codex 无 actionable issue、13 checks 全绿并合入 `8d8b8f96`；fresh detached main 再次得到 real-hook 4、
  focused 238、full 3224/3、Ruff/format/constraints/validate/truth 全绿且 clean，GAP-12 因而关闭。

Round 4 双审发现父 CC-05、pre-import fixture 与 solution-confirm 时序仍不够精确。当前冻结为两阶段
语义：managed-delivery-apply 在 request 前刷新；solution-confirm 先完成已授权的 solution 持久化，
只有 preflight/continue/ack 全通过后才紧邻 managed request 前刷新。失败或未授权路径零调用；notice
后移与“solution 保留、managed artifact 不生成”是唯一批准差分。naive fixture 对尚不存在的 local
binding 使用 `create=True`，候选再验证真实 import。

Round 5 Pascal PASS、Confucius FAIL 后，合同进一步明确：root bypass 的批准差分覆盖除两个 managed
刷新入口外的全部 program 路径；managed apply 省略 request 的物化和 direct execute missing yes 的
adapter/request preflight 是既有语义，不属于 WI207 新写入；未知/传播异常停止 managed phase，而
project-config lock 继续 warning-and-continue。Round 6 仍不增加产品行数或抽象。

Round 6 combined `2eaa2c0fa7aa18f9cd3598a89dbb85db78d0369d4f9342182f027bd0fedf5fcd`
已由 Pascal/精简直接性与 Confucius/兼容安全独立重算并双 PASS，无 actionable finding。六份 formal
目标自此冻结；formal PR 合入前 PR #139 继续 draft。

PR #140 Codex P2 仅发现 T22～T25 状态未随 Round 6 receipt 更新。机械修订后的 Round 7 combined
`4394016e7d7af59090bf0a8ecaea82be0286c1fbbafaf5976467a3bf99ebc8c5` 再次取得 Pascal/Confucius
同哈希双 PASS。随后第二轮 Codex P2 指出 canonical task ledger 仍绑定已经退役的 Round 6 hash；
该轮修订把动态 verdict/hash 移出 formal 六文件，任务状态只引用 execution log 最新终态回执，避免
每次写回 hash 都使自身失效。Round 8 双审进一步发现任务表仍提前声明“已完成”，已删除该假完成
措辞；Round 7/8 均已退役。Round 9 又因 child spec 重复定义组合哈希编码而失效：旧
`6a661de8...73b4` 不是父计划 §9 canonical recipe 的结果。PR #140 该 HEAD 上的 Codex P1 与
Pascal/Confucius 独立复算一致确认该问题；child spec 现只引用父计划唯一 recipe。Round 10 canonical
combined `2d19a12c...4fa9` 曾取得双方同哈希双 PASS、findings=`none`；该 HEAD 上的 Codex P2 随后
发现 T31 在 formal merge/rebase 前提前标记 completed。finding 已接受，Round 10 退役；T31 最小修订后
Round 11 门禁已全绿，canonical combined `46b63b1c...c2efb` 已由双方从零复审并双 PASS、
findings=`none`；动态 PASS receipt 后 final terminal gates 已全绿，随后已更新并合并 PR #140。

只读证据已证明 resume-pack 绝对路径/字段丢失属于 `status/recover/handoff` 的另一条 continuity
重建链，已拆为 GAP-13 / WI208。WI207 不是减重成果，不计 `completed_reduction`；其价值是消除
减重验收过程中的无关工作树污染和测试越界写入。

首轮 fresh-main 还暴露了另一项独立问题：comment preservation policy 会把 YAML quoted scalar
续行中以 `#` 开头的内容误判为被删除注释。该问题登记为 GAP-14 / WI209；本 repair 不修改
`comment_policy.py`，也不以记录“删除注释原因”掩盖误报。

Implementation 前置已经满足：child 与父路线六份 formal 文件在同一 combined hash 上取得
Pascal/精简直接性和 Confucius/兼容安全双 PASS，formal PR 已合入 main。实现 fresh-main 后只关闭
GAP-12；WI208、WI209 依次关闭后才继续下一个原子减重候选，WI196/RC08 全部满足前不发布版本。

Round 11 formal truth 为 ready/fresh、inventory complete、zero blocker，root exact/constraints/
validate/audit/diff-check 已通过。精确 snapshot/hash 和可变计数只以 terminal `program-manifest.yaml`
为准。

## 历史轮次（均已退役）

Round 1 combined `f74a06ab...de75` 被 Pascal 与 Confucius 双 FAIL：父测试例外、NC 适用矩阵、
CC 编号、T56 全局恢复门禁及 continuity Exact Next 存在合同脱节。产品一行方案、测试必要性、
execute/adapter 兼容和 WI207/WI208 边界未被否定。随后已按 findings 统一修订，旧 verdict 作废；新
combined hash 已由双方从零复审。

Round 1 findings 已全部按共同合同闭环并重跑 truth/constraints/root exact/diff-check。Round 2 使用了新
combined hash；后续 finding 又使该 target 作废并重新执行终态同步与复审。

Round 2 两位 reviewer 仅发现父 formal 顶层范围措辞仍落后于已经修正的 FR-12/SC-04 和当时的五件套
allowlist；随后已同步。Round 1 的实质合同 findings 继续保持闭环。Round 3 复审了新的六文件 hash，
旧 `f74a06ab...` 与 `262d2613...` verdict 均只保留为审计历史。

Round 3 formal 后的一行 naive bypass 在 PR #139 被 Codex 指出兼容缺口：managed delivery 依赖
`adapter_ingress_state=verified_loaded`，全族 bypass 会让“普通终端 init → 进入真实 AI 宿主 → 首次
managed delivery”错误保留 materialized blocker。Pascal 与 Confucius 已独立 ACCEPT finding；PR #139
转 draft，旧 final PASS 作废。Round 4 formal 只允许两个 managed 入口局部复用既有 hook，不接受全面
execute gating 或通用分类器。
