# Development Summary：WI-196 Lean-Code Self-Reduction Governance

**状态**：active governance parent；治理基线已合并，路线未关闭
**Owner**：AI-SDLC framework maintainers
**证据性质**：基于 parent spec、tasks、execution log 与 merge 事实的追溯总结

## 已交付

- 冻结统一 gap 台账、NC/CC/RC 合同、原子子项与对抗评审规则。
- 治理基线 PR：`#120`；merge commit：`4dd0f1c9`。
- GAP-07～GAP-11 已分别由 WI-197～WI-201 合入并关闭；当前 truth inventory 为 complete，
  unmapped/missing 均为 0。
- WI-203 / PR #126 已冻结减重候选和保护预算 sponsor；不等于候选实现或删除完成。
- WI-205 / PR #134 / merge `aa156afe` 已关闭一个 T63 artifact path 重复族，产品净减少 109 行，
  fresh-main 全量 `3220 passed, 3 skipped`；这不是 GAP-05 或路线整体关闭。
- WI-206 / PR #137 / merge `506e950d` 已把18个models顶层string helper收敛为一个private helper，
  product `+37/-246/net -209`；fresh-main full `3220 passed, 3 skipped`，以
  `completed_reduction` 关闭一个 T63 family。
- WI-207/GAP-12 兼容 formal PR #140 已合入 `8d325a4d`；implementation candidate `c4e5f07d` 已按
  root bypass + 两个 managed 入口局部 hook + root/local test isolation 落地，严格产品 additions=4、
  测试 additions=110，focused/full/治理/回滚门禁全绿，待 final-tree 双审与 PR #139/fresh-main。
  WI-208/GAP-13 继续独立处理 resume-pack reconstruction；二者先后关闭后再恢复新的减重候选。
- **历史（已退役）**：WI-207 Round 4 formal 被 Pascal/Confucius 同哈希双 FAIL；Round 5 随后把
  managed dry-run 唯一例外、pre-import `create=True` 隔离及 solution-confirm 全部门禁后/request 前刷新
  写成可执行合同，旧 verdict 同时失效。
- **历史（已退役）**：WI-207 Round 5 取得 Pascal PASS、Confucius FAIL；Round 6 随后补齐全部
  non-managed path 的批准差分、direct apply missing-yes preflight 与 propagated/soft hook failure 区分。
  产品始终限 root bypass + 一个 import + 两个调用。
- **历史（已退役）**：WI-207 Round 6 formal 曾在 combined `2eaa2c0f...edf5fcd` 上取得
  Pascal/Confucius 同哈希双 PASS，
  无 actionable finding。六文件冻结，formal PR 合入 main 前 implementation PR #139 继续 draft。
- **历史（已退役）**：PR #140 早期 Codex P2 要求把 child tasks T22～T25 更新到当时状态；Round 7
  `4394016e...ebc8c5` 已再次同哈希双 PASS。第二轮 Codex P2 又发现 task ledger 仍绑定退役的
  Round 6 hash；Round 8 双审又消除了“已完成”的假完成措辞。Round 9 的 `6a661de8...73b4`
  后被随后到达的 Codex P1 证明来自 child spec 的重复算法，不是父计划 §9 canonical recipe；双方重新独立
  复算后均 `FAIL`，旧 PASS 已退役。child spec 现只引用父计划唯一 recipe，合同与四行产品预算未改变；
  Round 10 canonical combined `2d19a12c...4fa9` 曾取得 Pascal/Confucius 同哈希双 PASS；该 HEAD 上的
  Codex P2 随后发现 child T31 在 formal merge/rebase 前提前标记 completed。finding 已接受，Round 10
  退役；Round 11 canonical combined `46b63b1c...c2efb` 已取得 Pascal/Confucius 同哈希双 PASS、
  findings=`none`。动态 PASS receipt 后 final terminal gates 已全绿，随后 PR #140 已合并；本段只保留
  formal 历史，不代表 PR #139 已完成。

## 未完成边界

- GAP/WP 子项仍按独立 WI/branch/PR 推进；本 summary 不宣称整体减重完成。
- WI-202 的首个 T62A 候选因完整 proof 明显超过 RC-06 预算，已按 RC-09 停止且未合入；
  GAP-01/T62A 仍 open，T62B/T62C 未开始，FR-08 双 reviewer fallback 继续有效。
- GAP-12、GAP-13 是验证/连续性可靠性缺口，不计 RC-08 减重收益；WI-207 不得混入 continuity，
  WI-208 不得混入 adapter dispatch。
- 关闭事件：所有子 WI 完成处置并执行 RC-08 route closure；在此事件前保持 active。
