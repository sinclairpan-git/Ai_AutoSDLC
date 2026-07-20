# Development Summary：WI-196 Lean-Code Self-Reduction Governance

**状态**：active governance parent；治理基线已合并，路线未关闭
**Owner**：AI-SDLC framework maintainers
**证据性质**：基于 parent spec、tasks、execution log 与 merge 事实的追溯总结

## 已交付

- 冻结统一 gap 台账、NC/CC/RC 合同、原子子项与对抗评审规则。
- 治理基线 PR：`#120`；merge commit：`4dd0f1c9`。
- GAP-07～GAP-11 已分别由 WI-197～WI-201 合入并关闭；WI-211 closure 已物化预登记的
  `development-summary.md`，truth inventory 保持 complete、unmapped=0，并将本项 pre-close missing 恢复为 0。
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
  relocation/focused/full/Ruff/治理门禁全绿且 repository state clean。
- WI-209/GAP-14 已关闭：formal PR #145/merge `46156c24` 与 implementation PR #146/merge `31aad572`
  已完成；Round 15 双 Agent、Codex current-head、22/22 checks 与 fresh-main focused/full/Ruff/治理/
  clean-state 全绿。该验证可靠性修复不计 RC-08；其 closure 已合并并恢复原子减重候选选择。
- WI-210 已以 `completed_reduction` 关闭一个 T63 family：formal PR #148/merge `b2f9997b`，
  implementation PR #149/merge `904fe5de`。28 个 exact text-dedupe body 收敛为现有
  `utils/helpers.py` 中 1 个 private helper + 28 个模块局部 alias，730 calls 不变，产品 raw
  `+39/-252/net -213`、non-empty `+35/-196/net -161`。Round 3 双 Agent、Codex current-head、22/22
  checks、rollback/reapply 与 fresh-main targeted `1283 passed`、full `3276 passed, 3 skipped`、治理/
  clean-state 全部通过；回退 PR #149 会重开该 family。
- WI-211 已以 `completed_reduction` 关闭一个 T63 family：formal PR #151/merge `25de0823`、consumer
  amendment PR #152/merge `96908f2c`、implementation PR #153/merge `cd64d8aa`。10 个 exact
  mapping-dedupe body 收敛为 1 个 private helper + 10 个模块局部 alias，23 calls 不变，产品 raw
  `+25/-147/net -122`、non-empty `+23/-127/net -104`。最终双 Agent、Codex current-head、22/22
  checks、rollback/reapply 与 fresh-main direct 104、impact 1163、full `3277 passed, 3 skipped`、治理/
  clean-state 全部通过；回退 PR #153 会重开该 family。
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
- GAP-12、GAP-13、GAP-14 均已关闭且不计 RC-08 减重收益。WI-209 最终 raw 产品/测试
  `+121/+200`、normalized `+128/+198`，5 private helper、零新产品/测试文件、零公共抽象；Round 15
  candidate/replay 同树且双 Agent PASS，PR #146 的 Codex current-head、22/22 checks 与 fresh-main
  `3275 passed, 3 skipped` 全部通过。回退对应 implementation PR 会重开各自 GAP。
- RC-08 family ledger 已记录 WI-205 `net -109`、WI-206 `net -209`、WI-210 `net -213`、WI-211
  `net -122`，累计产品 raw `net -653`；这只是已关闭重复族的局部收益，不代表路线整体达到 10% 或
  两个超大文件降到 400 行。
- WI-211 closure PR #154 已合并为 `626adb70`，lifecycle reconciliation PR #155 已合并为 `32742a25`；
  双 Agent、Codex、required checks 与 detached fresh-main 验收均通过，下一原子项选择门禁已恢复。
  后续仍须按真实收益、证明成本与 sponsor 从新的 T63/T65/WP-06/WP-07 候选中选择独立 WI。不得恢复
  已 No-Go 且缺少 sponsor 的 T62A，也不得关闭 GAP-05/WI-196、宣称 RC-08 达成或发布版本。
- WI-212 只冻结下一候选与修复 L3 路线合同死锁：WP-06/WP-07 的“稳定发布周期”改为主线预发布
  稳定周期，要求 candidate 合入且 legacy 保留后完成 cross-platform CI、wheel/sdist clean install、
  offline/sibling smoke 与 selector rollback/reapply，再以独立 PR 删旧并重复同等安装与回退证明。
  RC-08 前仍禁止 tag、GitHub Release、PyPI 发布与全局 CLI 更新；该合同修订不关闭 GAP-03/GAP-04。
- WI-212 PR #156 已合并为 `51903b8f`；最终本地双审、Codex current-head、13/13 checks 与 detached
  fresh-main 验收均通过，merge/reviewed tree=`db0dd990`。下一步只恢复新的 T66 bounded-stage formal
  WI 创建；仍须在 current main 重新完成准入、T61A/B、预算和双审，不能把 WI212 当作 execute 或
  release 授权。
- WI-213 已以 Round 9 双 PASS、PR #158、13/13 checks、merge `450d4988` 与 detached fresh-main 完成
  formal-only lifecycle，冻结 T66 terminal≤720、净删≥2,918；truth=`ready/fresh 1121/1121`、
  unmapped/missing=`0/0`，merge/reviewed tree=`9d1c0f69`。Lifecycle reconciliation 又以双 PASS、
  PR #159、merge `d5ad7616` 与 detached fresh-main 收口。独立 T58/GAP-15 WI214 的 formal PR #160、
  amendment PR #161 与 implementation PR #162 / merge `2845fedc` 已完成；reviewed/merge tree=
  `03b4a1ff`，detached fresh-main full=`3303 passed, 3 skipped`、targeted=`50 passed`、truth=`ready/fresh
  1126/1126` 且全部门禁全绿。Lifecycle delivery final tree=`3f6698d7` 同身份双 PASS0，PR #163
  exact-head 10/10 checks、merge=`60fe6d90` 与 detached fresh-main 全绿。Closure receipt PR #164
  reviewed HEAD/tree=`428a316a`/`cc3c6b7f`，本地 LEAN/SAFETY 同身份 PASS0，Codex clean、required
  checks 全绿并 merge=`7922956d`；detached fresh-main truth=`ready/fresh 1126/1126` 与全部治理门禁全绿。
  GAP-15/T58 已关闭；唯一 T66 implementation WI215 已创建，当前停在 T61A 双 readiness 前且产品零改动。
  T66/GAP-03/WI196/RC-08/release 仍未完成，本项不授权提前发布。
- WI215 编码前可实现性对质已统一否决旧160/190 proof合同；parent只把T66 proof个别上限修为290，
  `product+proof≤729`的RC-06 25%组合硬门、路线累计≤1,500、产品与release边界均保持不变。修正后的
  parent/child formal须重新同identity双审，未通过前不得进入candidate。
- 后续两版未提交recorder原型进一步证明集中式T61A动态证明会自然增长至约303～315 LOC并突破组合硬门；
  双方统一`NO-GO`。当前风险分层将T61A限为≤200 LOC的不可变基线，把原动态矩阵完整移到每阶段/T61B/
  selector切换/deletion的三方回放；Round 12与13 findings后已补outer/leaf、三套isolated project命令、
  checkout/import provenance与same-absolute-root-v1；随后补各腿pytest import隔离、receipt exact165直接执行、
  file-qualified helper source SHA及capture/performance专职symbol。Round 17精确formal取得LEAN/SAFETY双PASS0；
  reserve=90、recorder target=170，没有删除证据或放宽RC-06，产品仍零改动。
- 关闭事件：所有子 WI 完成处置并执行 RC-08 route closure；在此事件前保持 active。
