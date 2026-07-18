---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：共享文本去重重复族减重

**编号**：`210-shared-text-dedupe`
**来源**：`spec.md + plan.md`
**当前授权**：Batch 0～3 已完成；closure 只允许 docs/truth/continuity 与 manifest 测试的两条
pre-close missing `1→0`、close layer `209→210` 机械期望，不再修改产品代码或其他测试逻辑

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

### T02A GAP-09～GAP-11 impact admission

- **依赖**：T02。
- **GAP-09**：frontend capability/inheritance、blocking refs 与 codegen/test admission 零差异。
- **GAP-10**：adapter canonical consumption、CLI transcript 与 adapter 调用集合零差异。
- **GAP-11**：formal 唯一允许缺失预登记 close source；implementation source 新增=0；closure missing=0。
- **证据**：execution log + `.ai-sdlc/work-items/210-shared-text-dedupe/` 下唯一
  `t61-differential-rollback-receipt.json`。
- **停止**：分析不确定、unexpected unmapped/missing、capability/blocking refs 漂移时重开对应 GAP。

### T03 Formal 对抗评审至双 PASS（completed）

- **依赖**：T02A。
- **reviewer A**：Pascal / 精简收益、直接性、YAGNI、预算。
- **reviewer B**：Confucius / 兼容、安全、导入、证据与回退。
- **规则**：按父 plan §9 唯一算法对父子各 spec/plan/tasks 六文件生成 canonical combined；双方独立
  审查同一 identity，任一 finding 修订后从零重审。
- **完成**：两者均 `PASS` 且 findings=none。

### T04 Formal 门禁与 PR（completed）

- **依赖**：T03。
- **范围**：本 WI docs/log、WI-196 索引、manifest/truth、root/scoped handoff、next sequence，以及
  `test_repo_program_manifest.py` 至多两条既有 expectation 的机械同步。
- **验证**：constraints、validate、truth ready/fresh、manifest exact、diff-check、protected path zero diff。
- **交付**：commit、push、PR、Codex current-head review、required checks、merge、fresh-main docs acceptance。
- **停止**：formal merge 前不得创建 implementation diff。

## Batch 1：T61A 与 TDD

### T11 从 formal receipt 后 main 建 implementation branch（completed）

- **依赖**：T04 mainline merge + fresh-main acceptance。
- **完成**：独立 worktree/branch；baseline revision、toolchain、OS、protected blobs 已登记。
- **停止**：implementation branch 若早于 formal merge 创建则删除重建。

### T12 捕获 T61A 基线（completed）

- **依赖**：T11。
- **完成**：重算 28/27/196/730、body digest、private consumers、import graph；跑 behavior/event corpus。
- **测试**：spike 已验证的 32-file / `1282 passed` 集合从 main 重验；exact 构成为 25 unit + 7 CLI
  integration。此前 23-unit/8-integration=`839 passed` 是不同的初始子集，只作递进历史证据，不冒充
  32-file 集合。full baseline 只在 exact implementation base 执行一次。
- **唯一 targeted 命令**：

```powershell
$tests = @(
  'tests/integration/test_cli_program.py'
  'tests/integration/test_cli_run.py'
  'tests/integration/test_cli_status.py'
  'tests/integration/test_cli_verify_constraints.py'
  'tests/integration/test_cli_workitem_close_check.py'
  'tests/integration/test_cli_workitem_plan_check.py'
  'tests/integration/test_cli_workitem_truth_check.py'
  'tests/unit/test_artifact_target_guard.py'
  'tests/unit/test_backlog_breach_guard.py'
  'tests/unit/test_cli_commands.py'
  'tests/unit/test_close_check.py'
  'tests/unit/test_execute_authorization.py'
  'tests/unit/test_frontend_contract_observation_provider.py'
  'tests/unit/test_frontend_contract_runtime_attachment.py'
  'tests/unit/test_frontend_contract_verification.py'
  'tests/unit/test_frontend_cross_provider_consistency_artifacts.py'
  'tests/unit/test_frontend_gate_verification.py'
  'tests/unit/test_frontend_generation_constraint_artifacts.py'
  'tests/unit/test_frontend_page_ui_schema_artifacts.py'
  'tests/unit/test_frontend_provider_expansion_artifacts.py'
  'tests/unit/test_frontend_provider_runtime_adapter_artifacts.py'
  'tests/unit/test_frontend_quality_platform_artifacts.py'
  'tests/unit/test_frontend_theme_token_governance_artifacts.py'
  'tests/unit/test_frontend_visual_a11y_evidence_provider.py'
  'tests/unit/test_p1_artifacts.py'
  'tests/unit/test_plan_check.py'
  'tests/unit/test_program_service.py'
  'tests/unit/test_run_cmd.py'
  'tests/unit/test_runner_confirm.py'
  'tests/unit/test_verify_constraints.py'
  'tests/unit/test_workitem_traceability.py'
  'tests/unit/test_workitem_truth.py'
)
uv run pytest -q $tests
```

- **清单门禁**：必须为 32 个唯一、存在且按 repo-relative 字典序排列的路径；收集数或路径漂移即停止。
- **停止**：任一基线漂移先回 formal，不边写边扩大范围。

### T13 写最小 RED（completed）

- **依赖**：T12。
- **文件**：一个既有测试文件；不得新增 test file/fixture/snapshot。
- **完成**：共享 identity/strip/空值/首次顺序/异常传播的参数化测试在 helper 缺失时 RED。
- **预算**：characterization test non-empty additions≤9；harness/normalizer=0；RC-06 以 Ruff 后
  non-empty 计量，product35+test≤9+truth≤2 计划≤46、硬上限49。禁止 `noqa`、超长压行或只写
  manual probe；空行不计，注释、参数化数据和其他非空新增行均计，raw additions 另行披露。

### T14 实现共享 helper 与 aliases（completed）

- **依赖**：T13 RED。
- **产品文件**：`utils/helpers.py` + spec §2.1 的 27 个模块。
- **完成**：新增 1 个 private helper，删除 28 个 body，保留 28 个局部名与 730 个调用表达式。
- **预算**：产品 raw `+≤39/-≥252/net≤-213`；non-empty `+≤35/-≥196/net≤-161`；
  new module/public export/wrapper=0。
- **停止**：超预算、cycle、调用变化或需要 suppression 立即 No-Go。

### T15 GREEN 与 mutation（completed）

- **依赖**：T14。
- **完成**：RED 测试 GREEN；reverse-order mutation RED；恢复后 shared test 与受影响测试 GREEN。
- **规则**：mutation 不提交，不减少既有测试。

## Batch 2：T61B、回退与双审

### T21 结构与行为 differential（completed）

- **依赖**：T15。
- **结构**：exact body=1、alias=28、calls=730、private consumer approved diff 集合不扩大。
- **行为**：baseline/candidate 结果、异常 type/message、event trace 零未批准差异。
- **导入**：27 个模块在干净子进程逐一 import，无 stderr/cycle/import-time 写入。

### T22 测试与治理门禁（completed）

- **依赖**：T21。
- **测试**：spike 的 32-file / 1282-test 集合、candidate full、Ruff lint、formatter 24-file parity、
  三平台 required CI。
- **治理**：constraints、validate、truth sync/audit、manifest exact、diff-check、clean-state。
- **预算**：记录 raw/non-empty product/test additions/deletions；文档不冒充代码减重。

### T23 rollback/reapply rehearsal（completed）

- **依赖**：T22。
- **完成**：candidate→baseline tree OID exact；targeted/corpus/import 通过；baseline→candidate tree OID exact。
- **停止**：任何树不一致、测试差异或人工 allowlist 非空即 FAIL。

### T24 同一 candidate 双对抗 review（completed）

- **依赖**：T23。
- **identity**：commit、tree、binary diff hash、name-status hash、T61B/rollback receipt。
- **完成**：Pascal 与 Confucius 对同一 identity 均 PASS、findings=none。
- **规则**：内容变化使两份 PASS 同时失效。
- **证据**：Round 3 reviewed HEAD=`6ee2d35f`、tree=`326f8962`；Pascal/Confucius 对相同 identity
  均 PASS、findings=none。

## Batch 3：PR、Fresh Main 与关闭

### T31 Implementation PR（completed）

- **依赖**：T24。
- **完成**：push、PR、Codex current-head clean、required checks 全绿；有 finding 则 focused 修复并重审。
- **heartbeat**：约五分钟监控 review/checks，直至 merge 或用户输入 blocker。
- **证据**：PR #149；Codex 审到 current head `6ee2d35f` 且无 major issue，22/22 checks success，
  merge=`904fe5decc90deba64d09eb6fa94cb3c2a359d93`。

### T32 Fresh-main acceptance（completed）

- **依赖**：T31 merge。
- **完成**：detached current main 上受影响测试/full/Ruff/governance/manifest/clean-state 全绿。
- **证明**：实现产品 non-empty 净删≥161，selected family 100% 清零，回退仍可复算。
- **证据**：detached `main@904fe5de` targeted=`1283 passed in 163.54s`、full=
  `3276 passed, 3 skipped in 661.34s`；Ruff、constraints、validate、truth ready/fresh、manifest exact、
  diff/clean-state 全部通过。

### T33 Closure（in progress）

- **依赖**：T32。
- **完成**：WI-210=`completed_reduction`；更新 WI-196 索引与 RC-08 ledger；closure docs PR 合并并验收。
- **当前状态**：完成事实已物化；等待 closure 同一 identity 双审、PR/Codex/checks/merge 与 fresh-main
  docs acceptance。PR 合并前不提前标记本任务 completed。
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
| GAP-09～GAP-11 | T02A、T21、T22、T32、T33 |
