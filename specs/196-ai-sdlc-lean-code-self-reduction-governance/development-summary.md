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
- WI-207/GAP-12 已关闭：formal PR #140 合入 `8d325a4d`；implementation PR #139 合入 `8752aa97`；
  test-isolation repair PR #141 合入 `8d8b8f96`。最终 fresh-main real-hook/focused/full
  `3224 passed, 3 skipped`、Ruff/format/constraints/validate/truth 全绿，pre/post repository state 相同且 clean。
- WI-208/GAP-13 已由 PR #143 / merge `f51c176a` 关闭，closure PR #144 合并为 `85bdedac`；fresh-main
  relocation/focused/full/Ruff/治理门禁全绿且 repository state clean。WI-209 formal PR #145 已合并为
  `46156c24`；GAP-14/T57 正处于独立 implementation adversarial review，使用 old/new hunk 行号与
  PyYAML quoted token span 的窄边界，只有 fresh-main 后才恢复新的减重候选。
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
- GAP-12、GAP-13 已关闭且不计 RC-08 减重收益；GAP-14 处于 WI-209 implementation adversarial
  review。Round 8 测试覆盖稀释和 canonical receipt 失真 findings 已修订并通过 fresh verification；
  Round 9 Pascal PASS、Confucius 因真实 Git 空格路径假 BLOCKER FAIL；该 finding 已按原范围 GREEN，
  Round 10 fresh full/治理/replay 后双审仍因 mixed Unicode+C-escape、canonical plan、formatter 合同与
  continuity 真值 FAIL。四项已进入 Round 11 修订，其中产品 finding 已 RED/GREEN，预算降至
  raw/normalized `+121/+128`；fresh full `3275 passed, 3 skipped` 与治理门禁已通过，等待 terminal replay
  与同一新身份双审；
  双 PASS、PR 与 fresh-main 前仍是开放的验证可靠性缺口。WI-207 不得混入
  continuity/comment parser，WI-208 不得混入 adapter dispatch，WI-209 不得用 YAML 全局豁免掩盖误报，
  也不得让 added quoted 内容充当真实替代注释。
- 关闭事件：所有子 WI 完成处置并执行 RC-08 route closure；在此事件前保持 active。
