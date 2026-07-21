# 任务分解：ProgramService artifact loader 精确重复族减重

**编号**：`217-programservice-artifact-loader-dedupe`  
**状态**：formal authoring  
**来源**：`spec.md` + `plan.md`  
**父项**：WI-196 / WP-03 / T63 / GAP-05

## Batch 0：候选准入

### T01 Fresh-main 审计与方案对抗

- [x] **范围**：13 个 private YAML loader、18 个内部 callsite、repository consumer、相关测试库存。
- [x] **基线**：403 physical / branch39；12 ordinary loader 各一个 caller；cleanup loader 六个 caller。
- [x] **Clean spike**：product `+48/-406`、proof `+48`、AST terminal44/branch4；16/16 proof、422/422
  ProgramService unit、Ruff、diff-check 全绿。
- [x] **对抗结论**：R1～R3 findings 均已修正；R4 Pascal/LEAN 与 Confucius/SAFETY 对同一 clean spike
  均 `APPROVE A/findings=0`。formatter-polluted 第一棵 spike 明确不进入账本。
- [x] **决策**：选择 common helper + 12 direct label binding + cleanup-only wrapper；formal 与 implementation
  分离；不选择 13 thin wrappers 或 payload-builder 扩张。

## Batch 1：Formal-only PR

### T11 Canonical formal 五件套与 parent linkage

- [ ] **文件**：WI217 五件套；WI196 五件套最小追加；禁止修改产品。
- [ ] **验收**：RC-01～RC-10、CC-01～CC-08、FR/SC、stop/rollback、formal/implementation scope 完整；
  无占位文本、无 WI213/WI215 准入继承。
- [ ] **验证**：formal-six hash 可复算；`git diff --check`；scope scan。

### T12 Program truth、sequence 与 exact inventory

- [ ] **依赖**：T11 source commit。
- [ ] **文件**：`program-manifest.yaml`、project-state、manifest exact 两标量、root/scoped handoff。
- [ ] **验收**：WI217 `depends_on=[WI196]`；`next_work_item_seq=218`；inventory=`1136/1136`、close=
  `216/216`、missing/unmapped=0；handoff byte-identical。
- [ ] **验证**：manifest exact、constraints、validate、truth audit、Cursor bytes unchanged、clean tree。

### T13 Formal same-identity 双审

- [ ] **依赖**：T12。
- [ ] **LEAN**：真实净删、RC-04/05/06、proof成本、YAGNI、RC-08 claim。
- [ ] **SAFETY**：13-label contract、四态 loader、cleanup warnings、路径/异常、scope、回退、continuity。
- [ ] **验收**：双方对同一 committed+clean HEAD/tree/formal-six 均 PASS0/findings=0；修复后必须双重审。

### T14 Formal PR、checks、merge、fresh-main

- [ ] **依赖**：T13。
- [ ] **验收**：PR current-head 无 actionable finding、required checks 全绿、squash merge；本地 branch 保留。
- [ ] **Fresh-main**：重跑 T12 gates；merge tree/formal-six 与 reviewed identity 一致。
- [ ] **阻断**：fresh-main 未通过前禁止创建 implementation branch。

## Batch 2：Implementation T61A/T61B

### T21 RED characterization

- [ ] **依赖**：T14 fresh-main。
- [ ] **分支**：从新的 detached fresh-main 创建独立 implementation worktree/branch。
- [ ] **文件**：只改 `tests/unit/test_program_service.py`，raw additions≤48，无新 test file。
- [ ] **覆盖**：12 caller→label + missing/invalid YAML exact exception/non-mapping/valid 四态；cleanup 复用既有测试。
- [ ] **RED**：16 cases 全部失败，原因仅为 common helper/binding 尚不存在；记录命令与输出。

### T22 Minimal implementation 与 atomic candidate commit

- [ ] **依赖**：T21 RED。
- [ ] **文件**：只改 `src/ai_sdlc/core/program_service.py` 与 T21 test。
- [ ] **实现**：一个 private helper；删除 12 ordinary wrapper；12 exact binding；cleanup wrapper保留。
- [ ] **禁止**：新模块/public API/dependency/registry/reflection/DSL/getattr/type erasure/第二重复族/全文件格式化。
- [ ] **结构验收**：product additions≤48/deletions≥406/net delete≥358；terminal≤44/branch≤4；13→1。
- [ ] **GREEN**：16 passed；Ruff/diff-check PASS；product+proof 使用一个 atomic candidate commit。

### T23 ProgramService/CLI/full/package gates

- [ ] **依赖**：T22 clean commit。
- [ ] **测试**：ProgramService unit=`422 passed`；完整 CLI integration 与 full pytest exit0。
- [ ] **治理**：constraints 无 BLOCKER、validate PASS、truth ready/fresh、manifest exact、scope/consumer scan全绿。
- [ ] **兼容**：required Windows/macOS/Linux、wheel/sdist、clean-install、POSIX/Windows offline smoke全绿。
- [ ] **预算**：proof≤48、truth≤2、combined≤98/101；路线保守累计≤282/1500。

### T24 Rollback/reapply receipt

- [ ] **依赖**：T23 + exact candidate commit/tree。
- [ ] **Revert**：disposable clone revert atomic candidate；两个 code/test blob 与 fresh-main exact，406 unit通过。
- [ ] **Reapply**：恢复 exact candidate tree；16 proof、422 unit、Ruff通过。
- [ ] **验收**：不推临时 clone；commit/tree/blob/命令/输出写入 execution log；失败则 candidate NO-GO。

### T25 Final implementation 双审

- [ ] **依赖**：T24 + terminal truth/gates。
- [ ] **验收**：LEAN/SAFETY 对同一 candidate commit/tree、final HEAD/tree、formal-six、ledger、rollback receipt
  均 PASS0/findings=0；tracked identity 变化后双重审。

## Batch 3：Implementation PR 与 closure

### T31 Implementation PR / merge / fresh-main

- [ ] **依赖**：T25。
- [ ] **验收**：current-head review无 actionable finding、required checks全绿、squash merge、本地 branch保留。
- [ ] **Fresh-main**：重复 T22～T24 验收并确认 reviewed product/test blobs 未变。

### T32 Records-only closure

- [ ] **依赖**：T31 fresh-main。
- [ ] **范围**：独立 closure branch/PR；产品与行为测试零 diff。
- [ ] **状态**：只关闭本 T63 family并登记 product net -358；GAP-03/T66、GAP-05、WI196、RC-08、release
  保持 open。
- [ ] **验收**：同 identity 双审、required checks、merge、detached fresh-main 全绿后才选择下一原子项。

## 合同映射

| 合同 | 任务 |
|---|---|
| FR-217-001～004 | T21～T23 |
| FR-217-005～006 | T11～T14、T24～T31 |
| FR-217-007～008 | T24、T32 |
| RC-01～RC-07 | T01、T11、T21～T24 |
| RC-09～RC-10 | T13～T14、T24～T32 |
| SC-217-001～006 | T22～T32 |
