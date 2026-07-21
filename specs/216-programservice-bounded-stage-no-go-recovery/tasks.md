# 任务：ProgramService 有界阶段减重 NO-GO 恢复

## Batch 1：不可变事实与恢复合同

### T11 核验隔离证据

- **状态**：completed
- **输入**：fresh main、C2-safe worktree、nine-stage no-DSL spike worktree。
- **验收**：commit/tree/blob 均可解析；三个 worktree clean；量化账本与已审记录一致。
- **完成**：基线=`7922956d/cc3c6b7f`，C2=`70f19275/2fdd9aaa`，spike 产品=
  `6c945b40/6341bcb2`，spike records=`60dcc4f6/44420f6d`。

### T12 写 WI216 五件套

- **状态**：completed
- **依赖**：T11
- **验收**：目标、允许/禁止范围、完整台账、状态转换、成功标准和回退无占位。

### T13 修正 WI196 / WI213 主线真值

- **状态**：completed
- **依赖**：T12
- **验收**：历史 receipt 保留；追加 superseding NO-GO；T66 本次尝试 `cancelled_no_go`；
  GAP-03/WI196/RC-08/release open。

## Batch 2：同身份对抗评审

### T21 提交 authoring identity 并计算 formal-nine

- **状态**：completed
- **依赖**：T12、T13
- **验收**：commit clean；formal-nine 算法与 WI216 plan 一致；review prompt 绑定 HEAD/tree/hash。

### T22 Pascal / LEAN 审查

- **状态**：completed（Rounds 1～2 FAIL，findings 已进入 T24）
- **依赖**：T21
- **验收**：完整 LOC/branch/product/proof 计数、真实净删、YAGNI、未来入口和 records-only scope；
  返回 actionable findings 与 verdict。

### T23 Confucius / SAFETY 审查

- **状态**：completed（Rounds 1～2 FAIL，findings 已进入 T24）
- **依赖**：T21
- **验收**：功能保持、证据 provenance、状态/回退、truth/continuity/release 边界；返回 findings 与 verdict。

### T24 处置 findings 并同身份复审

- **状态**：completed
- **依赖**：T22、T23
- **验收**：所有成立 finding 最小修正；双方对新的同一 HEAD/tree/formal-nine `PASS0/findings=0`。

## Batch 3：truth、continuity 与最终验证

### T31 注册 WI216 并同步 truth

- **状态**：completed
- **依赖**：T24
- **验收**：manifest 注册依赖；project-state seq=217；manifest exact 只机械更新 `1131/215`；truth sync 后
  ready/fresh、inventory exact、missing/unmapped=0。

### T32 更新 byte-identical handoff

- **状态**：completed（Round 1 safety finding 后提前修复）
- **依赖**：T12
- **验收**：root/scoped WI216 handoff byte-identical，指向当前分支和精确下一步。

### T33 执行 records-only 门禁

- **状态**：completed
- **依赖**：T31、T32
- **验收**：constraints、validate、truth、manifest exact、scope、handoff parity、diff-check、clean 全绿；
  `src/**`、测试逻辑/fixture、workflow、依赖、版本、release 零差异；测试只含两个 exact 标量。

### T34 最终同身份双审

- **状态**：completed
- **依赖**：T33、T35
- **验收/收据**：Pascal/LEAN 与 Confucius/SAFETY 对同一 final reviewed delivery identity
  HEAD/tree/formal-nine=`57c22f60618ed85df5e0f51b90b4bd3aa2e4b2b8` /
  `6d0946c85c8a12c3821861523e780a0d3829e1ed` /
  `75351a47a7c98b98881e2cfc878850295535d7e73b657bc48a3615028b3d164a` 均为
  `PASS0/findings=0`；records-only receipt 不改变 formal-nine。

### T35 持久化非合入审计 refs

- **状态**：completed
- **依赖**：T24
- **验收**：两个 `codex/archive/215-*` remote ref 分别 exact 指向 `70f19275`、`60dcc4f6`；
  no PR/no merge/no force-push，fresh clone 可解析 C2 与 spike commit/tree/blob。

## Batch 4：PR 与主线验收

### T41 推送并创建 records-only PR

- **状态**：completed
- **依赖**：T34、T35
- **验收/收据**：PR #165 对应 reviewed exact HEAD
  `57c22f60618ed85df5e0f51b90b4bd3aa2e4b2b8`，scope 与 reviewed tree 一致；13/13 checks
  success，zero reviews、zero review threads。Codex bot 明确返回 code-review usage-limit，未接受该
  review；用户授权使用本地 SDLC LEAN+SAFETY 作为替代，但未豁免 CI。

### T42 current-head 评审与 required checks

- **状态**：completed
- **依赖**：T41
- **验收/收据**：PR #165 的 current HEAD 保持
  `57c22f60618ed85df5e0f51b90b4bd3aa2e4b2b8`；13/13 required checks success，zero reviews、zero
  review threads，未发现 actionable finding。Codex bot 的 code-review usage-limit 由用户授权的本地
  SDLC LEAN+SAFETY substitute 覆盖；CI 仍完整通过，未被 waive。

### T43 squash merge 与 detached fresh-main

- **状态**：completed
- **依赖**：T42
- **验收/收据**：squash merge=`19809f3ac0b1c7f648fa36ed326be7b2c367b3b1`，delivery branch 已保留。
  detached fresh-main acceptance：manifest exact=`1 passed in 109.86s`；constraints no BLOCKERs；
  validate PASS 且 Cursor SHA 不变=`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`；
  truth ready/fresh=`1131/1131`、missing/unmapped=`0/0`、all canonical layers=`215/215`；Ruff exact
  和 diff-check PASS，worktree clean。只关闭 WI216 records recovery。

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| FR-001、SC-002 | T11～T12、T21～T24、T35 |
| FR-002、SC-001、SC-006 | T13、T31、T33～T35、T42～T43 |
| FR-003～FR-005、SC-003 | T12～T13、T22～T24 |
| FR-006、SC-005 | T21～T24、T34、T42 |
| FR-007～FR-008、SC-004 | T31～T33、T35、T43 |
