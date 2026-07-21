# 执行日志：ProgramService 有界阶段减重 NO-GO 恢复

## 1. Batch 2026-07-21-001：隔离授权与不可变证据复核

- 用户明确允许隔离继续；从 fresh `origin/main@7922956d3e248a93c3190240259850ab3498ec9f`
  创建 `codex/216-programservice-bounded-stage-no-go-recovery`，base tree=
  `cc3c6b7f7e63dd040034938ff6bb6827f067e41c`，worktree 初始 clean。
- C2-safe records worktree=`70f19275150831ceea89a6c1e006c056ee98c412` /
  `2fdd9aaa5fde71711f8ec706338f9bdcbfd860e4`，engine/service blobs=
  `977cad2c25da95b0c2329ca97b9a3b071e70630b` / `23a4968b63651f8fbfebc3174bf737dcce40984e`。
- Nine-stage spike product=`6c945b40c8b488728f718287dc6458f15db50d96` /
  `6341bcb20526be9fdfcd1c273fc15f33dac7e5f4`，engine/service blobs=
  `4ab00c369a0414b76f6dda4e49a1c9e2b4d97a79` / `ddc417c8203b6bce8458587a98258e233f2d79d0`；
  final records=`60dcc4f65f2a332261b765bfe5fff9979397ddc7` /
  `44420f6d86b55f8995c3a4ffe9e0e3ba7ce7eb00`。
- Spike 自然账本为 target=`1209 LOC / 164 branch`、两阶段 legacy=`842/92`；Pascal/LEAN 与
  Confucius/SAFETY 对产品及 records-only 身份均返回 `STOP_SPIKE_NO_GO/findings=0`。
- 后续两位 reviewer 交叉复算 C2 完整边界，统一 engine 394/43 + facade 57/6 + renderer 78/13 +
  factory 27/2 + aliases 2/0 = `558/64`，legacy=`495/63`；产品源码净增35，proof净增285。Round 1
  确认 diff `+N/-M` 会随工具分段变化，因此删除该不稳定分解，只冻结完整 before/after 与净增值。
  双方结论收敛为 records-only recovery；不得宣称 C2 是减重或合入其产品。
- 本批只读复核，没有修改任何产品、测试或证据分支。

## 2. Batch 2026-07-21-002：formal Round 1 FAIL findings

- Exact review identity=`9718b33035bcf490e192f103241a4502c874390f` / tree=
  `c060ab24225eb6f0fc41ec88ae4929aa54b9488f` / formal-nine=
  `b8fc1ace4dde4028264f56fb20a6df51c2ea11155af605550977cbb7d2642dae`；worktree clean。
- Pascal/LEAN=`FAIL`：manifest exact 需要 `1126/214→1131/215` 两个机械测试标量；C2 `+N/-M` recipe
  不稳定；summary 状态滞后；父项仍有旧“当前可进入实现”措辞。
- Confucius/SAFETY=`FAIL5`：root handoff 仍指向 WI214；本地-only SHA 不构成持久证据；full revert 会误
  解锁 T66；`next_work_item_seq=215` 会复用失败实验编号；summary 状态滞后。
- 处置：立即创建 WI216 byte-identical handoff；允许且仅允许 exact-test 两标量；seq推进217；将两个 exact
  证据身份持久化为禁止 PR/merge/force-push/delete 的 remote archive refs；回退保持 T66 fail-closed；
  修正全部历史时点和 summary。任何变更使 Round 1 verdict 失效，修正后重新提交同身份复审。
