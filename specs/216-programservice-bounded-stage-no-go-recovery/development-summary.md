# 开发摘要：ProgramService 有界阶段减重 NO-GO 恢复

**状态**：records-only authoring；等待 formal-nine 对抗评审、truth、PR 与 fresh-main

## 已确认

- fresh main 的 legacy ProgramService 行为保持原样；本项不会合入候选产品、测试逻辑/fixture或proof；
  测试唯一变更是 manifest exact 的两个计数标量。
- C2-safe 完整自然账本为 `558 LOC / 64 branch`，legacy 为 `495/63`；产品净增35 LOC、proof净增285，
  因而不是框架减重。
- 无 DSL 九阶段 spike 在第二阶段达到 `1209/164`，高于两阶段 legacy `842/92` 且超过 branch≤90；
  双 reviewer 一致 `STOP_SPIKE_NO_GO/findings=0`。
- C2-safe 与 spike 均保持 `archived_not_merged`；formal 已冻结两个契约性非合入 remote archive ref，
  待最终门禁前持久化并验证 exact SHA，不声称存在技术只读保护。

## 状态边界

- T66 本次实现尝试：`cancelled_no_go`。
- GAP-03、WI196、RC-08、总体 release：继续 open。
- WI216 完成只表示失败事实已安全写回主线，不表示用户要求的“补缺口并减重”已经完成。
- 未来只有新的 formal WI 以完整自然账本证明产品净删、复杂度下降、兼容与证明成本可控后，才能重启
  T66；不得继承 WI215 的 GO、hash、预算或 reviewer receipt。

## 已完成的 authoring

- WI196/WI213 superseding 状态已经更新；Round 1 指出的旧“当前”措辞继续在 remediation commit 修正。
- WI216 root/scoped handoff 已提前建立，防止在 formal 复审前恢复到旧 WI214/T66 路线。

## 待完成

- 对 committed+clean formal-nine 完成 Pascal/LEAN 与 Confucius/SAFETY 同身份 PASS0。
- 推送并验证两个契约冻结的非合入 remote archive ref；同步 program truth，完成 records-only 门禁。
- 推送 PR、required checks/Codex review、merge 与 detached fresh-main 验收。
