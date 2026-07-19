# Development Summary：WI-212 Reduction Candidate Selection

**状态**：候选选择与父合同修订已完成本地双审；mainline PR/fresh-main 验收待完成

## 已交付

- 基于 fresh main `32742a25` 扫描 T63～T67，排除无 sponsor 的 T62A 与 revoked claim。
- 当前 T63、T64 和六个 T65 均因 product+proof 合并成本违反 RC-06 而 No-Go；T67 因旧 claim=0
  且与 T66 baseline 重叠保持 Deferred，不复用 WI203/WI204 formal。
- 唯一下一候选为 T66 bounded-stage ProgramService domain：九阶段、45 methods、3,638 physical、
  3,305 executable、225 public header；预备终态≤691，产品净删≥2,947。
- T66 shadow additions≤466≤545；product+proof≤686≤736；按当前口径历史保守 subtotal=184，
  纳入候选后路线累计≤870≤1,500。上述值只授权下一独立 formal WI 重新复算，不授权实现。
- 父 WI196 已消除 L3 死锁：candidate 合入且 legacy 保留后完成 cross-platform、wheel/sdist、clean
  install、offline/sibling smoke 与 selector rollback/reapply，再用独立 PR 删除 legacy 并重复同等证明。
  该预发布稳定周期不创建 tag、GitHub Release、PyPI 或全局 CLI 更新。
- 父 RC-06 文案已与适用矩阵统一；既有双审/mainline receipt 不追溯撤销，后续路线累计按当前
  product+proof 合并口径保守重列。

## 对抗评审

- Pascal 从 LEAN/YAGNI、Confucius 从 SAFETY/COMPAT 独立审查；任何 parent+child formal-six 变化
  同时废止双方 verdict。
- Round 1 因 manifest test scope 矛盾在 verdict 前中止；Round 2 双 FAIL、Round 3/4 split、Round 5
  双 FAIL 的 findings 均做最小修正，没有扩大产品、测试逻辑或发布范围。
- Round 6 精确 HEAD/tree=`a3cfbfc9f07823cc0e97b1ccb3b3706632c5c7f0`/
  `32b75650e4a49ef41b2d724d4ba9c57259f1a5cd`，formal-six=
  `f7c38d07bb969690698586ac1d81bce8b97d5a622a9235b06e1fed96c27b593c`；两位 reviewer 均
  PASS、actionable findings=0。

## 未完成边界

- T66 产品实现必须在 WI212 mainline/fresh-main 验收后创建新的独立 formal WI；本分支不得实现。
- GAP-03～GAP-06、WI-196、RC-08 与版本发布保持 open；`program_service.py` / `program_cmd.py` 的
  400 行终态仍未达到。
- mainline PR、Codex current-head、required checks、merge 与 detached fresh-main receipt 完成前，
  WI212 不得被用作 T66 execute 或发布授权。
