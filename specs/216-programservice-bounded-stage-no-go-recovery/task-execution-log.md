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

## 3. Batch 2026-07-21-003：formal Round 2 FAIL findings

- Exact review identity=`34cf0bb18ef427e93f10725f6a431edb2cb589d5` / tree=
  `13a47e713505e1b3ab1fb131828d8fe397d73d61` / formal-nine=
  `8fed255ab7299df65feb6e9c32ea54bbdf339db839dd578c3a9245b84fa9e42d`；worktree clean。
- Pascal/LEAN=`FAIL`、Confucius/SAFETY=`FAIL2`，结论一致：plan 尚有两处“测试零差异”与 exact 标量例外
  冲突；T35 archive gate 未成为 final review/PR 硬依赖；普通 remote branch 不应被虚构为技术只读；
  WI196/T58 仍有一处旧“当前状态”。
- 处置：所有测试边界统一为“测试逻辑/fixture零差异、唯二 exact 标量”；T34与T41硬依赖T35，
  FR-001/SC-002映射T35；archive改称契约冻结非合入ref并明确无技术只读保护；T58文本标为历史且由
  WI216 supersede。修正后 Round 2 verdict 失效，提交新的 formal-nine 进入 Round 3。

## 4. Batch 2026-07-21-004：formal Round 3 split verdict

- Exact review identity=`4cfff3b0c652c3162abeac7adb26e0fb4187d746` / tree=
  `c4a7539cba4896e7acc00749c050cd21a054933c` / formal-nine=
  `3daf7fb35b72a938662e097bf57837bf85fb1482f133764843fba4ce8a69ea39`；worktree clean。
- Pascal/LEAN=`PASS0`。Confucius/SAFETY=`FAIL1`：root/scoped handoff 虽 byte-identical，但仍停留在
  Round 1 状态和下一步，context restore 会重复旧 remediation。
- 处置：只更新本 execution log 与两份 byte-identical handoff，formal-nine 不变；commit/tree 改变使
  LEAN PASS0 与 SAFETY FAIL1 均不可直接用于最终拼接。Round 4 必须让双方复审同一新 HEAD/tree。

## 5. Batch 2026-07-21-005：formal Round 4 split verdict

- Exact review identity=`50958c5564356a0406c29a43c893cd65464426fc` / tree=
  `ad950e6ba2f9c2eb572731b1059caa8a8722e45e` / formal-nine=
  `3daf7fb35b72a938662e097bf57837bf85fb1482f133764843fba4ce8a69ea39`；worktree clean。
- Confucius/SAFETY=`PASS0/findings=0`。Pascal/LEAN=`FAIL1`：handoff 的首个 next step 仍要求提交 Round 3
  remediation，但当前 HEAD 已是该提交，恢复后会重复已完成动作。
- 处置：把下一步改为与提交时点无关的 fail-closed gate——“当前 committed+clean identity 取得同身份
  双 PASS；未双 PASS 不进入 truth”。只修改 log/handoff，formal-nine仍不变；Round 5 必须双方复审新
  HEAD/tree，不拼接 Round 4 split verdict。

## 6. Batch 2026-07-21-006：formal Round 5 双 PASS 与 archive 持久化

- Exact review identity=`77d984c2c2278259db7d87336f1a900cc4b48c79` / tree=
  `63f2505b4ee09e7391bb3318e207f73cdee3899e` / formal-nine=
  `3daf7fb35b72a938662e097bf57837bf85fb1482f133764843fba4ce8a69ea39`；worktree clean。
- Pascal/LEAN=`PASS0`；Confucius/SAFETY=`PASS0/findings=0`。这是首个同 HEAD/tree/formal-nine 的一致
  authoring verdict；Rounds 1～4 split verdict 仅保留审计，不参与拼接。
- 推送契约冻结的非合入 archive refs，不创建 PR、不合并：
  `refs/heads/codex/archive/215-programservice-bounded-stage-c2-safe` exact=
  `70f19275150831ceea89a6c1e006c056ee98c412`；
  `refs/heads/codex/archive/215-nine-stage-no-dsl-no-go` exact=
  `60dcc4f65f2a332261b765bfe5fff9979397ddc7`。`git ls-remote --heads origin` 逐一匹配。
- WI216 已注册到 manifest source，依赖 WI196/WI213/WI214；terminal truth snapshot 尚未机械同步。

## 7. Batch 2026-07-21-007：truth、exact 与 records-only scope 门禁

- Source receipt commit=`7bdbd68d606935885c15f01f020316a221829243` / tree=
  `ee0ea1ef075ecd0601c351ab3702a3fd1be90b2f`；随后执行 truth sync，snapshot repo_revision=
  `7bdbd68d`、inventory=`1131/1131`、missing/unmapped=`0/0`、各 canonical layer=`215/215`。
- `uv run --python 3.11 ai-sdlc verify constraints`：no BLOCKERs；`program validate`：PASS；
  Cursor SHA before/after均=`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`。
- 计划中的 `program truth status` 在当前CLI不存在；依据 `program truth --help` 修正为正式子命令
  `program truth audit`，结果=`ready/fresh`、release targets ready、source inventory complete `1131/1131`。
- Manifest exact：`tests/integration/test_repo_program_manifest.py`=`1 passed in 158.21s`；Ruff check PASS。
  Ruff format check 对当前与 `origin/main` 同一文件均 exit1，属于已存在 baseline、delta=0；为遵守“两处
  exact标量”白名单不做扩展格式化。
- Scope=`20 files`；无 `src/**`、workflow、依赖、版本、release；测试唯一文件 numstat=`+2/-2`，逐行仅
  `1126→1131` 与 `214→215`；project seq=`217`；handoff byte-identical；archive refs 再次 exact；
  `git diff --check` PASS。
- 本批状态写入后会使当前 snapshot stale；必须提交 source receipt，再做一次 terminal truth sync，final
  committed+clean identity 双 PASS 前不得推送 WI216 PR。
