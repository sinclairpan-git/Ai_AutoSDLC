# 开发摘要：消费项目与框架约束隔离

**状态**：closure-source candidate；本分支合入 `main` 后 WI218 才生效为 closed
**实施结果**：GO

## 交付结果

- formal PR #170 已以 `bf4f4cf8` 合并；lifecycle prerequisite PR #171 已以 `fb75a9d6` 合并。
- implementation PR #172 的 reviewed HEAD=`499b383e`、tree=`c319a6b6`；Codex 对精确 HEAD 未发现
  major issue，required checks=`22/22`，最终以 `fec4c010` squash merge。
- 产品范围严格限制为三个文件，合计 `+80/-31`、净增 `+49`，仅保留一个私有 helper；runner 删除重复注入，
  修复 PrimeVue 空扫描与 consumer `014` 下游呈现两个 P2，`ProgramService` 未修改。
- implementation branch 验收：focused=`233 passed`，full=`3332 passed, 3 skipped`；真实 Agent Store
  framework-only blockers=`0` 且前后零写入；LEAN/SAFETY R5 同一身份 `PASS0/findings=0`。
- detached fresh-main `fec4c010` 验收：focused=`233 passed`，full=`3332 passed, 3 skipped in 944.67s`；
  constraints、program validate 与真实 Agent Store 零写入验收全部通过。

## Closure 边界

- 当前分支仅归档 closure source；在其合入 `main` 前，不提前声明 WI218 已 closed。
- 本分支合入后 WI218 关闭，不创建新的减重 work item，不重启减重路线；剩余结构债保留为非阻塞 backlog，
  恢复正常特性开发。
- 若 closure 失败，只允许 emergency corrective revert，不得借机扩展实现或重启专项。
