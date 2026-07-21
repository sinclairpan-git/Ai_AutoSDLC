# 开发摘要：ProgramService artifact loader 精确重复族减重

**状态**：closure-source candidate；本分支合入 `main` 后 WI217/WI196 才生效为 `completed_go` / `closed`
**实施结果**：`GO`
**版本边界**：不创建 tag、GitHub Release、PyPI 发布，不更新全局 CLI

## 交付结果

- Formal PR #167 已 squash merge 为 `4e4971d4625b5cf7f3381653bb6288a95fb4aa54`，其 detached
  fresh-main governance/truth/clean gates 全绿。
- 唯一 implementation PR #168 的 final reviewed HEAD 为
  `533363f4950546a744722b8f19d9d323aed12114`；Codex current-head 未发现 major issue，22/22 required
  checks 全绿，squash merge 为 `4d98039d21f2c94f50f3c5224d0c52bc929428b9`，本地 branch 保留。
- 最终产品改动严格为 `+48/-406/net -358`，proof 为 `+48`，canonical truth 为3行，combined=
  `99/101`；13个同形 loader body 收敛为一个33 LOC/branch3 helper与一个11 LOC/branch1 cleanup wrapper，
  terminal family=`44 LOC / 4 branch`。
- 未新增产品模块、public API、依赖、registry、reflection、DSL、`getattr`、type erasure、第二重复族或
  formatter churn。最终 product/proof blobs 分别为
  `77827e018ae192e1d33d739310c0c7754309d7a2` / `25ef1acdd616f89b001b96973ced37fdf5f073ff`。

## 兼容与回退证据

- Final implementation LEAN/SAFETY 对同一 committed+clean HEAD/tree/formal-six 均
  `PASS0/findings=0`。本地 proof=`6 passed`、ProgramService=`412 passed`、CLI program=`233 passed`、
  full=`3309 passed, 3 skipped`；Ruff、constraints、validate、truth、manifest exact、wheel/sdist与
  clean-install CLI smoke均通过。
- Detached fresh-main 在 exact implementation merge 上重复确认上述两个 blobs；full=
  `3309 passed, 3 skipped in 815.07s`，manifest exact、constraints、validate、truth、build与clean-install
  smoke全绿。
- Portable atomic candidate=`eb8dc0f8bc726816e97cd5bb0f027e35216651c0`。隔离clone revert=
  `da29c10cbbd6f9bcf8dbbc6ebd622c6a1811fa48`，精确恢复baseline product/proof blobs并通过406 unit；
  reapply=`866d4c4805d5dadc525351d0d00c4ba1cea84f08`，精确恢复最终blobs并通过6 proof、412 unit与Ruff。
  该clone未推送。

## 路线终局

- WI217 实际产品净删358行；与此前已关闭 family ledger 的653行合计，WI196 路线累计产品 raw净删
  `1,011` 行，约占初始 `107,482` 行产品基线的 `0.94%`。该结果按实际账本登记，不宣称达到10%。
- 用户终止路线的原因正式登记为：专项接近7天仍无可预测终点，减重效果不透明，Token、对抗评审与CI
  成本持续上升并挤压正常特性开发；没有新特性交付、只持续减重不具备产品意义，减重必须保持均衡。
- 本 closure source 合入 `main` 时关闭 WI217 与 WI196；RC-08 以
  `retired_unrealistic_composite_target` 退役，不写成达成或 waiver。
- GAP-01、GAP-03～GAP-06 与 T62～T67 的剩余结构债统一转为 `non_blocking_backlog`，不再阻塞正常
  特性/缺陷开发；禁止选择或创建新的减重 work item，正常特性开发立即恢复。
- 本 closure PR 是路线唯一 closure PR。它相对 implementation merge 的产品文件与行为 proof 零差异；
  merge 后仍须完成 detached fresh-main governance/truth/scope/clean acceptance，失败只允许修正本 closure
  receipt，不得重启减重路线或创建新的减重 work item。
