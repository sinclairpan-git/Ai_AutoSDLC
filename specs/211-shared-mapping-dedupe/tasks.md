---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：共享 Mapping 去重重复族减重

**编号**：`211-shared-mapping-dedupe` | **日期**：2026-07-18
**来源**：`spec.md + plan.md`
**当前授权**：Batch 0～4 全部完成；closure PR #154 已合并并通过 detached fresh-main 验收。
本次 post-merge reconciliation 只允许同步已完成的生命周期证据，不得修改产品代码、测试逻辑、
RC-08 ledger 或开放边界

## 批次图

```text
Batch 0 Formal ──mainline receipt──> Batch 1 T61A/TDD
                                        │
                                        ▼
                                  Batch 2 T61B/Review
                                        │
                                        ▼
                                  Batch 3 PR/Fresh Main
                                        │
                                        ▼
                                  Batch 4 Closure
```

## Batch 0：Formal 冻结

### T01 当前真值与候选选择

- **状态**：completed。
- **依赖**：WI210 closure fresh-main acceptance。
- **完成**：绑定 `main@236cd00e8f2e9514487d237b47d4cbbf6fb5fe91`；比较 T63/T65/T66/T67；
  T62A 无 sponsor 不参与。
- **证据**：10 defs/10 modules/120 LOC/23 calls；spike raw net -122、non-empty net -104；103/1162 tests；
  72 imports；Pascal/Confucius 唯一推荐 mapping family。

### T02 冻结 child/parent formal

- **状态**：completed。
- **依赖**：T01。
- **文件**：父子 `spec.md`、`plan.md`、`tasks.md`，child execution log 与父路线索引。
- **验收**：范围、语义、允许差异、CC/RC、T61A/B、停止/回退、branch/PR 边界无占位或冲突。

### T02A GAP-09～GAP-11 impact admission

- **状态**：completed。
- **GAP-09**：capability/inheritance、blocking refs、codegen/test admission、artifact/schema 零漂移。
- **GAP-10**：adapter capability/consumption、runtime-adapter artifact 与 CLI transcript 零漂移。
- **GAP-11**：implementation 新增 source=0；formal 唯一 expected missing 是 mapped/`exists=false` 的本 child
  `development-summary.md` 且 close=211/210；closure 必须归零为211/211。任一 unmapped、第二个 missing 或
  其他 type/path/layer 的 missing 阻断。
- **停止**：分析不确定或 truth 漂移时重开对应 GAP，不得继续 candidate。

### T03 Formal 双 Agent 评审

- **状态**：completed。
- **依赖**：T02/T02A。
- **reviewer A**：Pascal / 精简收益、直接性、YAGNI、预算。
- **reviewer B**：Confucius / 兼容、安全、导入、证据与回退。
- **验收**：父 plan §9 canonical combined identity 相同；双方 PASS/findings=none。
- **失效**：父子任一 formal 目标变化使两份 PASS 同时失效并从零重审。

### T04 Formal 门禁与 PR

- **状态**：completed。
- **依赖**：T03。
- **范围**：child/parent docs、manifest/truth、project seq、root/scoped handoff；manifest test至多两条机械值。
- **验证**：constraints、validate、truth ready/fresh、manifest exact、diff-check、protected zero diff、handoff parity。
- **交付**：push/PR、Codex current-head、required checks、merge、detached fresh-main docs acceptance。

## Batch 1：T61A 与 TDD

### T11 从 formal merge main 创建实现分支

- **状态**：completed。
- **依赖**：T04 mainline merge + fresh-main acceptance。
- **完成**：独立 `feature/211-shared-mapping-dedupe` worktree；冻结 base/toolchain/protected blobs。
- **停止**：分支早于 formal merge 创建则删除重建。

### T12 捕获 T61A 基线

- **状态**：completed。
- **依赖**：T11。
- **完成**：10/10/120/23、Python 3.11 固定 digest + Python 3.12 同解释器 AST equality、授权目标边界之外的
  `src/` product/runtime consumer=0、tracked identity attribute reads=0、72 importers、`plan.md` §3.3 唯一27
  non-empty LOC executable 4-case corpus且binding lookup=1/进程。
- **验证**：当前 Python 3.11 baseline 为4 observations、digest=`8c6d3e21ef...54e0`；return outcome显式保存
  每个结果dict的key顺序；103 direct、1162
  impact、72 cold imports；full baseline 只在 exact implementation base 跑一次。

### T13 Identity TDD RED

- **状态**：completed。
- **依赖**：T12。
- **文件**：现有 `tests/unit/test_frontend_contract_observation_provider.py`。
- **验收**：新增一个4 non-empty LOC identity test；baseline 只因两个代表模块 objects 不同失败；该测试精确
  产生2次 tracked proof-only private attribute reads且不做其他消费；结构门禁另证全部10 aliases 指向同一 helper；
  与27 LOC harness 合计保护成本=31，0 新测试文件/fixture。

### T14 最小 GREEN

- **状态**：completed。
- **依赖**：T13。
- **产品**：`utils/helpers.py` exact body；10 alias imports；删 10 local bodies 与 7失活 `json` imports。
- **禁止**：23 calls、公共 surface、其他 family、产品/测试新文件。
- **验收**：identity GREEN；结构 10→1、aliases=10、calls=23；raw net≤-100、non-empty net≤-90。

## Batch 2：T61B、治理与对抗评审

### T21 Implementation differential

- **状态**：completed。
- **依赖**：T14。
- **验收**：implementation 4-case JSONL 与同环境 baseline 字节完全一致；Python 3.11 digest=
  `8c6d3e21ef...54e0`；104 direct、
  1163 impact、72 imports 全绿；consumer scan为product/runtime=0、tracked identity reads=2、harness lookup=1/进程。

### T22 Rollback/reapply rehearsal

- **状态**：completed。
- **依赖**：T21 + exact `implementation_commit/tree`。
- **验收**：disposable clone revert tree=baseline、reapply tree=`implementation_tree`；revert 重跑结构/consumer
  scan product-runtime/tracked/harness=`0/0/1`/4-case/103 direct/1162 impact/72 imports，reapply 重跑consumer
  scan product-runtime/tracked/harness=`0/2/1`/4-case/104 direct/1163 impact/72 imports。
- **回执**：之后的 evidence commit chain 只允许唯一 `t61-differential-rollback-receipt.json`、强制 root/scoped
  handoff 与必要机械 truth/manifest，形成 `evidence_review_head/tree`；`implementation_commit` 后产品和行为测试
  零变化。receipt 绑定 implementation/revert/reapply，禁止绑定自身 commit/tree/hash；review envelope 绑定
  receipt、root/scoped handoff 与 truth/manifest blobs；receipt 必须分栏证明授权目标边界之外的 product/runtime
  consumers=0、tracked identity attribute reads baseline/revert=0 与 candidate/reapply=2、disposable harness
  binding lookup=1/进程，不得把测试或harness读取混入产品零值。

### T23 全量与 GAP 防回归

- **状态**：completed。
- **依赖**：T22。
- **验证**：full pytest、Ruff、constraints、validate、truth、manifest；GAP-09～11 admission 全绿；Git clean。

### T24 同 identity 双 Agent PASS

- **状态**：completed。
- **依赖**：T23。
- **验收**：Pascal/Confucius 对 exact `implementation_commit/tree`、`evidence_review_head/tree`、diff、
  formal-six、receipt blob、truth 均 PASS/findings=none。
- **规则**：内容变化使双方 PASS 失效；修复后全量复审。
- **证据**：最终 reviewed HEAD=`fbfb07e7fa878331bd4ce48862890d7ef0e3741c`、tree=
  `f4c0b60d9d2be9a8cc364e55e2ab709f1cb5eda4`；Pascal/Confucius 均 PASS、findings=none。

## Batch 3：PR 与 fresh main

### T31 Implementation PR

- **状态**：completed。
- **依赖**：T24。
- **验收**：push、PR、Codex current-head 无 actionable findings；required checks 和跨平台矩阵全绿。
- **证据**：PR #153；Codex 对 current head `fbfb07e7` 两次均未发现 major issue，22/22 checks
  success，merge=`cd64d8aad415853102cf3c8dc647af34759ad197`。

### T32 Merge 与 fresh-main acceptance

- **状态**：completed。
- **依赖**：T31。
- **验收**：PR merge；detached `origin/main` 重跑4-case/104/1163/full/Ruff/constraints/validate/truth/
  manifest/clean；product ledger 与 reviewed `implementation_tree` 一致，receipt 与 evidence review blob一致。
- **证据**：detached `main@cd64d8aa`、Python 3.11.15：direct 104、impact 1163、full
  `3277 passed, 3 skipped in 728.11s`；4-case、Ruff、治理、manifest、blob/ledger 与 clean-state 全绿。

## Batch 4：Closure

### T41 Closure truth/docs

- **状态**：completed。
- **依赖**：T32。
- **范围**：独立 closure branch；产品零 diff；物化 child summary、parent ledger、manifest close source与handoff。
- **边界**：只关闭一个 T63 family；GAP-05/WI196/RC-08/release保持 open。

### T42 Closure 双 Agent / Codex / CI

- **状态**：completed。
- **依赖**：T41。
- **验收**：Pascal/Confucius 同 identity PASS；Codex current-head clean；required checks全绿。
- **证据**：reviewed HEAD/tree=`ed7934fccb7161f85ad391c4466a658add2e1247`/
  `57973d2ff1d334ae87b9cd8384684cfc2bfc0b7e`；Pascal/Confucius 均 PASS、findings=none；Codex
  reviewed commit `ed7934fccb` 未发现 major issue；PR #154 的 13/13 checks success。

### T43 Closure merge / fresh-main

- **状态**：completed。
- **依赖**：T42。
- **验收**：closure merge；fresh-main docs/truth/manifest/clean guard PASS；随后才允许选择下一原子项。
- **证据**：PR #154 squash merge=`626adb70cb9e7333e5bd690765b4336c1f260769`；detached fresh main
  Python 3.11.15 上 constraints、validate、truth `ready/fresh 1111/1111`、manifest exact、Ruff、
  protected/src/test-scope/handoff parity 与 clean guard 全绿；merge tree 与 reviewed tree 同为
  `57973d2ff1d334ae87b9cd8384684cfc2bfc0b7e`。

## 合同映射

| 合同 | 任务 |
|---|---|
| FR-211-001～005 | T02、T13、T14、T24 |
| FR-211-006～008 | T12、T21～T23、T32 |
| FR-211-009～010 | T03、T04、T11、T24、T31～T43 |
| GAP-09～GAP-11 | T02A、T23、T32、T43 |
| RC-01～RC-10 | T02、T12～T24、T32、T41 |
| SC-211-001～006 | T03、T14、T21～T24、T31～T43 |
