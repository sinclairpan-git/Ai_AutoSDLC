---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：共享文本去重重复族减重

**编号**：`210-shared-text-dedupe`
**来源**：`spec.md + plan.md`
**当前授权**：只允许 Batch 0；formal merge 前禁止 Batch 1～3 产品修改

## 批次图

```text
Batch 0 Formal ──mainline receipt──> Batch 1 T61A/TDD
                                        │
                                        ▼
                                  Batch 2 T61B/Review
                                        │
                                        ▼
                                  Batch 3 PR/Fresh Main
```

## Batch 0：Formal 冻结

### T01 当前真值与候选选择

- **依赖**：WI-209 closure mainline acceptance。
- **范围**：T63/T65/WP-06/WP-07 只读比较；WI-204 No-Go 复盘。
- **完成**：基线绑定 `4b434864...`；28 defs / 27 modules / 196 LOC / 730 calls；选择 exact text family。
- **验收**：Pascal/Confucius 对候选和 `utils/helpers.py` 承载位置形成一致推荐。

### T02 冻结 spec/plan/tasks

- **依赖**：T01。
- **文件**：本 WI `spec.md`、`plan.md`、`tasks.md`。
- **完成**：范围、语义、CC、RC、T61A/B、停止/回退、分支/PR 边界无占位或冲突。
- **验收**：canonical identity 可复算；产品/测试路径仍为零 diff。

### T03 Formal 对抗评审至双 PASS

- **依赖**：T02。
- **reviewer A**：Pascal / 精简收益、直接性、YAGNI、预算。
- **reviewer B**：Confucius / 兼容、安全、导入、证据与回退。
- **规则**：同一 spec/plan/tasks identity 独立审查；任一 finding 修订后双方从零重审。
- **完成**：两者均 `PASS` 且 findings=none。

### T04 Formal 门禁与 PR

- **依赖**：T03。
- **范围**：本 WI docs/log、WI-196 索引、manifest/truth、root/scoped handoff、next sequence，以及
  `test_repo_program_manifest.py` 至多两条既有 expectation 的机械同步。
- **验证**：constraints、validate、truth ready/fresh、manifest exact、diff-check、protected path zero diff。
- **交付**：commit、push、PR、Codex current-head review、required checks、merge、fresh-main docs acceptance。
- **停止**：formal merge 前不得创建 implementation diff。

## Batch 1：T61A 与 TDD

### T11 从 formal receipt 后 main 建 implementation branch

- **依赖**：T04 mainline merge + fresh-main acceptance。
- **完成**：独立 worktree/branch；baseline revision、toolchain、OS、protected blobs 已登记。
- **停止**：implementation branch 若早于 formal merge 创建则删除重建。

### T12 捕获 T61A 基线

- **依赖**：T11。
- **完成**：重算 28/27/196/730、body digest、private consumers、import graph；跑 behavior/event corpus。
- **测试**：spike 已验证的 32-file / `1282 passed` 集合从 main 重验；其中已含此前 23 unit
  `441 passed` 与 8 CLI integration `398 passed` 的核心面；full baseline 只在 exact implementation
  base 执行一次。
- **停止**：任一基线漂移先回 formal，不边写边扩大范围。

### T13 写最小 RED

- **依赖**：T12。
- **文件**：一个既有测试文件；不得新增 test file/fixture/snapshot。
- **完成**：共享 identity/strip/空值/首次顺序/异常传播的参数化测试在 helper 缺失时 RED。
- **预算**：characterization test non-empty additions≤9；harness/normalizer=0；RC-06 以 Ruff 后
  non-empty 计量，product35+test≤9+truth≤2 计划≤46、硬上限49。禁止 `noqa`、超长压行或只写
  manual probe。

### T14 实现共享 helper 与 aliases

- **依赖**：T13 RED。
- **产品文件**：`utils/helpers.py` + spec §2.1 的 27 个模块。
- **完成**：新增 1 个 private helper，删除 28 个 body，保留 28 个局部名与 730 个调用表达式。
- **预算**：产品 raw `+≤39/-≥252/net≤-213`；non-empty `+≤35/-≥196/net≤-161`；
  new module/public export/wrapper=0。
- **停止**：超预算、cycle、调用变化或需要 suppression 立即 No-Go。

### T15 GREEN 与 mutation

- **依赖**：T14。
- **完成**：RED 测试 GREEN；reverse-order mutation RED；恢复后 shared test 与受影响测试 GREEN。
- **规则**：mutation 不提交，不减少既有测试。

## Batch 2：T61B、回退与双审

### T21 结构与行为 differential

- **依赖**：T15。
- **结构**：exact body=1、alias=28、calls=730、private consumer approved diff 集合不扩大。
- **行为**：baseline/candidate 结果、异常 type/message、event trace 零未批准差异。
- **导入**：27 个模块在干净子进程逐一 import，无 stderr/cycle/import-time 写入。

### T22 测试与治理门禁

- **依赖**：T21。
- **测试**：spike 的 32-file / 1282-test 集合、candidate full、Ruff lint、formatter 24-file parity、
  三平台 required CI。
- **治理**：constraints、validate、truth sync/audit、manifest exact、diff-check、clean-state。
- **预算**：记录 raw/non-empty product/test additions/deletions；文档不冒充代码减重。

### T23 rollback/reapply rehearsal

- **依赖**：T22。
- **完成**：candidate→baseline tree OID exact；targeted/corpus/import 通过；baseline→candidate tree OID exact。
- **停止**：任何树不一致、测试差异或人工 allowlist 非空即 FAIL。

### T24 同一 candidate 双对抗 review

- **依赖**：T23。
- **identity**：commit、tree、binary diff hash、name-status hash、T61B/rollback receipt。
- **完成**：Pascal 与 Confucius 对同一 identity 均 PASS、findings=none。
- **规则**：内容变化使两份 PASS 同时失效。

## Batch 3：PR、Fresh Main 与关闭

### T31 Implementation PR

- **依赖**：T24。
- **完成**：push、PR、Codex current-head clean、required checks 全绿；有 finding 则 focused 修复并重审。
- **heartbeat**：约五分钟监控 review/checks，直至 merge 或用户输入 blocker。

### T32 Fresh-main acceptance

- **依赖**：T31 merge。
- **完成**：detached current main 上受影响测试/full/Ruff/governance/manifest/clean-state 全绿。
- **证明**：实现产品 non-empty 净删≥161，selected family 100% 清零，回退仍可复算。

### T33 Closure

- **依赖**：T32。
- **完成**：WI-210=`completed_reduction`；更新 WI-196 索引与 RC-08 ledger；closure docs PR 合并并验收。
- **边界**：不关闭 GAP-05/WI-196，不恢复 WI-204，不发布版本。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| RC-01～RC-03 | T01、T02、T12～T14 |
| RC-04～RC-07 | T14、T21、T22 |
| RC-08～RC-10 | T23、T32、T33 |
| CC-01～CC-08 | T12、T15、T21、T22 |
| FR-01～FR-03 | T14、T21 |
| FR-04～FR-06 | T03、T04、T24、T31～T33 |
| SC-01～SC-06 | T03、T22～T24、T31～T33 |
