# 任务分解：ProgramService artifact loader 精确重复族减重

**编号**：`217-programservice-artifact-loader-dedupe`
**状态**：implementation local gates passed / final review pending
**来源**：`spec.md` + `plan.md`
**父项**：WI-196 / WP-03 / T63 / GAP-05

## Batch 0：候选准入

### T01 Fresh-main 审计与方案对抗

- [x] **范围**：13 个 private YAML loader、18 个内部 callsite、repository consumer、相关测试库存。
- [x] **基线**：403 physical / branch39；12 ordinary loader 各一个 caller；cleanup loader 六个 caller。
- [x] **Clean spike**：product `+48/-406`、proof `+48`、AST terminal44/branch4；加强后legacy=
  5behavior GREEN/1binding RED，candidate=6/6 proof、412/412 ProgramService unit；Ruff/diff-check全绿。
- [x] **对抗结论**：R1～R3 findings 均已修正；R4 Pascal/LEAN 与 Confucius/SAFETY 对同一 clean spike
  均 `APPROVE A/findings=0`。formatter-polluted 第一棵 spike 明确不进入账本。
- [x] **决策**：选择 common helper + 12 direct label binding + cleanup-only wrapper；formal 与 implementation
  分离；不选择 13 thin wrappers 或 payload-builder 扩张。

## Batch 1：Formal-only PR

### T11 Canonical pre-close 四文档与 parent linkage

- [x] **文件**：WI217 spec/plan/tasks/log；summary只注册且保持不存在；WI196五件套最小追加；禁止修改产品。
- [x] **验收**：RC-01～RC-10、CC-01～CC-08、FR/SC、stop/rollback、formal/implementation scope 完整；
  无占位文本、无 WI213/WI215 准入继承。
- [x] **验证**：formal-six hash 可复算；`git diff --check`；scope scan。

### T12 Program truth、sequence 与 exact inventory

- [x] **依赖**：T11 source commit。
- [x] **文件**：`program-manifest.yaml`、project-state、manifest exact 两标量、root/scoped handoff。
- [x] **验收**：WI217 `depends_on=[WI196]`；`next_work_item_seq=218`；inventory state=`complete`、
  mapped=`1136/1136`、close=`216/215`、missing/unmapped=`1/0`且唯一missing为WI217 summary；handoff
  byte-identical。
- [x] **验证**：manifest exact、constraints、validate、truth audit、Cursor bytes unchanged、clean tree。

### T13 Formal same-identity 双审

- [x] **依赖**：T12。
- [x] **LEAN**：真实净删、RC-04/05/06、proof成本、YAGNI、RC-08 claim。
- [x] **SAFETY**：13-label contract、五态loader、root外绝对路径、read/YAML异常、cleanup warnings、scope、
  回退、continuity。
- [x] **验收**：双方对同一 committed+clean HEAD/tree/formal-six 均 PASS0/findings=0；修复后必须双重审。

### T14 Formal PR、checks、merge、fresh-main

- [x] **依赖**：T13。
- [x] **验收**：PR current-head 无 actionable finding、required checks 全绿、squash merge；本地 branch 保留。
- [x] **Fresh-main**：重跑 T12 gates；merge tree/formal-six 与 reviewed identity 一致。
- [x] **阻断**：fresh-main 未通过前禁止创建 implementation branch。

## Batch 2：Implementation T61A/T61B

### T21 RED characterization

- [x] **依赖**：T14 fresh-main。
- [x] **分支**：从新的 detached fresh-main 创建独立 implementation worktree/branch。
- [x] **文件**：只改 `tests/unit/test_program_service.py`，raw additions≤48，无新 test file。
- [x] **覆盖**：一个case内部断言12 caller→label；persistent representative覆盖root外path的missing、
  invalid YAML exact exception、non-mapping、valid、directory read failure五态；cleanup复用既有测试。
- [x] **RED**：legacy五个behavior cases全绿，binding case单独RED；记录`1 failed, 5 passed`输出。

### T22 Minimal implementation 与 atomic candidate commit

- [x] **依赖**：T21 RED。
- [x] **文件**：只改 `src/ai_sdlc/core/program_service.py` 与 T21 test。
- [x] **实现**：一个 private helper；删除 12 ordinary wrapper；12 exact binding；cleanup wrapper保留。
- [x] **禁止**：产品/runtime新模块、public API、dependency、registry、reflection、DSL、getattr、type
  erasure、第二重复族或全文件格式化；T61A test-only inspection 例外按spec执行。
- [x] **结构验收**：product additions≤48/deletions≥406/net delete≥358；terminal≤44/branch≤4；13→1。
- [x] **GREEN**：6 proof passed；Ruff/diff-check PASS；product+proof 使用一个 atomic candidate commit。

### T23 ProgramService/CLI/full/package gates

- [x] **依赖**：T22 clean commit。
- [x] **测试**：ProgramService unit=`412 passed`；完整 CLI integration 与 full pytest exit0。
- [x] **治理**：constraints无BLOCKER、validate PASS、truth ready/fresh且只有WI217 summary missing、manifest
  exact、scope/consumer scan全绿。
- [ ] **兼容**：required Windows/macOS/Linux、wheel/sdist、clean-install、POSIX/Windows offline smoke全绿。
- [x] **预算**：proof≤48、truth≤2、combined≤98/101；路线保守累计≤282/1500。

### T24 Rollback/reapply receipt

- [x] **依赖**：T23 + exact candidate commit/tree。
- [x] **RED来源**：legacy 5 behavior GREEN/1 binding RED只绑定T21独立proof-red worktree；atomic revert后
  proof已不存在，不要求重跑该结果。
- [x] **Revert**：disposable clone revert atomic candidate；两个 code/test blob 与 fresh-main exact，406 unit通过。
- [x] **Reapply**：恢复 exact candidate tree；6 proof、412 unit、Ruff通过。
- [x] **验收**：不推临时 clone；commit/tree/blob/命令/输出写入 execution log；失败则 candidate NO-GO。

### T25 Final implementation 双审

- [ ] **依赖**：T24 + terminal truth/gates。
- [ ] **验收**：LEAN/SAFETY 对同一 candidate commit/tree、final HEAD/tree、formal-six、ledger、rollback receipt
  均 PASS0/findings=0；tracked identity 变化后双重审。

## Batch 3：Implementation PR 与 closure

### T31 唯一 implementation attempt / outcome

- [ ] **依赖**：T14 formal fresh-main，以及 T25 GO 或 T21～T25 任一门的 exact NO-GO receipt。
- [ ] **数量**：最多一个 implementation PR；所有最小修复、重审与重跑留在同一分支/PR，不创建替代 PR。
- [ ] **GO**：current-head review无 actionable finding、required checks全绿、squash merge、本地 branch保留；
  fresh-main重复 T22～T24 并确认 reviewed product/test blobs 未变；只有该验收通过才形成final GO。
- [ ] **NO-GO**：若本地已确定则可以不创建PR；若PR已创建则关闭且不合入产品，记录exact head/tree、原因与
  零产品合入，直接进入T32；若PR已合并后fresh-main失败，记录exact merge/failure并由T32同一closure回退。

### T32 唯一 route closure / post-merge rollback

- [ ] **依赖**：T14 formal fresh-main，以及 T31 的 GO fresh-main、pre-merge NO-GO exact receipt或post-merge
  fresh-main failure exact receipt。
- [ ] **范围**：独立且唯一closure branch/PR；GO/pre-merge NO-GO时产品与行为测试零diff；post-merge NO-GO时
  只允许reviewed implementation product/proof diff的精确逆变更，禁止其他产品修改或独立rollback PR。
- [ ] **Close source**：创建 WI217 `development-summary.md`，missing归零、close恢复`216/216`。
- [ ] **GO状态**：关闭本 T63 family并登记实际 product net -358。
- [ ] **NO-GO状态**：关闭本次候选为`cancelled_no_go`；pre-merge路径登记零产品合入，post-merge路径先恢复
  pre-implementation exact product/proof blobs并登记最终零产品净变化；均不得伪造减重收益。
- [ ] **共同终态**：关闭 WI217/WI196；RC-08=`retired_unrealistic_composite_target`；GAP-01/GAP-03～06、
  T62～T67 剩余结构债=`non_blocking_backlog`；禁止创建新减重 work item，恢复正常特性开发。
- [ ] **验收**：同 identity 双审、required checks、merge、detached fresh-main 全绿；本路线不发布版本。

## 合同映射

| 合同 | 任务 |
|---|---|
| FR-217-001～004 | T21～T23 |
| FR-217-005～006 | T11～T14、T24～T31 |
| FR-217-007～009 | T24、T31～T32 |
| RC-01～RC-07 | T01、T11、T21～T24 |
| RC-09～RC-10 | T13～T14、T24～T32 |
| SC-217-001～006 | T22～T32 |
