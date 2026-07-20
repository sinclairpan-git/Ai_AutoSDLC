# 开发摘要：ProgramService Bounded Stage Reduction Implementation

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**状态**：T61A authoring；产品实现阻断

## 当前事实

- WI214 closure receipt PR #164 / merge `7922956d` 与 detached fresh-main 已通过，GAP-15/T58 已关闭。
- WI215 是唯一 T66 implementation WI；当前只交付 formal、proof harness 与 legacy baseline receipt。
- Legacy inventory=`45 methods / 3,638 physical / 3,305 executable / branch 386`；目标 selector=
  `165 passed, 474 deselected`，两次独立 basetemp 均通过。
- Round 2 LEAN/SAFETY=`FAIL4/FAIL4`；Round 3=`PASS0/FAIL2`；Round 4=`PASS0/FAIL2`；Round 5=
  `FAIL1/FAIL2`；Round 6=`FAIL2/FAIL3`。所有成立 finding 已最小修正，旧 verdict 均退役，等待
  Round 7 对合同bytes同轮复审。Round 7=`PASS0/PASS0`、findings=0；评审事实writeback使该verdict退为
  authoring receipt，等待Round 8仅复核writeback；仍不是最终T61A GO。
- T61A committed+clean identity 的双 readiness GO 前，`src/**` 保持零差异，两份目标行为测试 blob
  保持不变；只允许 manifest exact inventory/close 数字机械替换。当前机械值=`1131/1131/0/0`、
  close=`215/215`，exact test=`1 passed in 99.06s`。

## 预算与边界

- Recorder≤160 LOC；全部新增 test/harness/normalizer≤190；candidate peak product≤522；terminal≤720；
  净删≥2,918；ProgramService responsibility reduction≥3,278。
- 任一兼容矩阵、hash identity、预算或 reviewer verdict 失败即 NO-GO，保留 legacy，不放宽阈值。
- Candidate、稳定期、独立 deletion 与 exact-merge actual rollback 未完成前，不关闭 T66/GAP-03/WI196/
  RC-08，不创建 tag/GitHub Release/PyPI，也不更新共享 CLI。

## 下一步

- 完成 Round 8 LEAN/SAFETY writeback复核并提交formal authoring source。
- 提交 formal source，执行 truth sync 与 manifest exact 机械更新。
- 先跑 recorder file-missing RED，再实现唯一 proof；最终同身份双 GO 前不写产品或目标行为测试。
