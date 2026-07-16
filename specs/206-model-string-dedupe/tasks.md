---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Model String Dedupe Reduction

**编号**：`206-model-string-dedupe`
**日期**：2026-07-16
**来源**：`spec.md + plan.md`
**父任务**：WI-196 `T63 / WP-03 / GAP-05`

## Batch 1：Formal baseline、对抗评审与 receipt

### T11 创建 canonical WI 与隔离工作区

- **状态**：已完成
- **验收**：branch=`feature/206-model-string-dedupe-docs`；worktree 基于
  `origin/main@aa156afe`；五件套、manifest mapping 和 `next_work_item_seq=207` 已生成。

### T12 冻结事实、CC、RC 与 T61

- **状态**：formal target 已冻结；各轮 verdict 与当前完成状态只记录在 `task-execution-log.md`
- **依赖**：T11
- **验收**：18 modules/defs、100 calls、216 LOC、complexity72、body/full FunctionDef/signature digests、
  19-file mapping与281/2基线、distinct-digest event corpus、binding/introspection allowlist、RC与回退可复算。

### T13 同步 root truth expectation

- **状态**：已完成，待同哈希双审
- **依赖**：T12
- **验收**：五件套使 inventory `1081→1086`、close `205→206`；只替换两个既有 tuple；精确 nodeid
  RED 后 GREEN，无新 test function/file。

### T14 Formal 双 Agent 对抗评审

- **状态**：formal review 门禁；各轮 verdict 与当前完成状态只记录在 `task-execution-log.md`
- **依赖**：T13
- **验收**：Pascal/精简效率与 Confucius/兼容安全对同一 formal 三文件哈希均 PASS；内容变化后从零重审。

### T15 Formal 验证、PR 与 mainline receipt

- **状态**：待执行
- **依赖**：T14
- **验收**：constraints、validate/truth、root nodeid、19-file baseline、diff/path、handoff 全绿；commit/push/PR；
  Codex review 无未处置问题、required checks全绿、merge main；implementation只绑定该merge commit。

## Batch 2：Implementation T61A 与 TDD RED

### T21 创建独立 implementation branch/worktree

- **状态**：待执行
- **依赖**：T15
- **验收**：`feature/206-model-string-dedupe-dev` 从 formal merge main 创建；formal worktree不承载源码。

### T22 捕获未改代码 baseline

- **状态**：待执行
- **依赖**：T21
- **验收**：exact revision/Python/Pydantic/OS；defs18/calls100/LOC216/complexity72/body digest；两组
  full FunctionDef/signature digest；18-module inspect/binding；19-file targeted=`281 passed, 2 skipped`；
  full suite通过；一份 digest event corpus；baseline tree OID；truth fresh/ready。

### T23 先写共享 identity 结构 RED

- **状态**：待执行
- **依赖**：T22
- **文件**：`tests/unit/test_program_models.py`
- **验收**：断言 `frontend_contracts._dedupe_strings is program._dedupe_strings is
  state._dedupe_string_items`；baseline因identity不同稳定失败；不是 import/collection/fixture error；
  raw additions≤4，无新 test file/fixture。

## Batch 3：最小产品减重与 mutation

### T31 新增唯一 private helper

- **状态**：待执行
- **依赖**：T23
- **文件**：`src/ai_sdlc/models/_string_lists.py`
- **验收**：future annotations + 两空行 + 原样12 LOC FunctionDef，共15 raw LOC；full FunctionDef/body/
  runtime signature/annotations/default/doc满足合同；无I/O、public export或分支特判。

### T32 删除 18 个 local body

- **状态**：待执行
- **依赖**：T31
- **文件**：spec §1 的18个模型模块
- **验收**：17 exact imports + 1 state alias；删除216 local LOC；validator/call expression不改；defs=1、
  imports=18、calls=100、18/18 binding identity；无wrapper/第二helper；identity test GREEN。

### T33 复算 Reduction Contract

- **状态**：待执行
- **依赖**：T32
- **验收**：算法216→12、complexity72→4；产品 +≤37/-≥216/net≤-179，其中 4 行仅为 Ruff `I001`
  必需 import-block 分隔；identity test≤4、root truth additions=2、全部source additions≤43≤54；
  18 条 import 均在标准顶层 first-party import block，禁止 late/mid-file import、分号/多语句压行、
  noqa/isort/Ruff 配置等 lint suppression；19产品文件精确、新产品文件=1、公共API/依赖=0。

### T34 证明 order mutation RED 并恢复

- **状态**：待执行
- **依赖**：T33
- **验收**：临时反转shared helper输出，既有program order assertion稳定失败；只用`apply_patch`恢复，
  targeted重新GREEN；不提交mutation。

## Batch 4：T61B、回退与全量验收

### T41 运行 behavior/event 与 binding differential

- **状态**：待执行
- **依赖**：T34
- **验收**：每个 distinct body digest 一份 candidate receipt 与 baseline 的 result/exception/event trace
  零差异；18-module digest/import/identity表全绿；19-file targeted、root nodeid、schema/dump/error通过。

### T42 执行 rollback rehearsal

- **状态**：待执行
- **依赖**：T41
- **验收**：disposable clone revert 后 exact tree OID==baseline，targeted+corpus通过；reapply 后 exact tree
  OID==candidate，targeted+corpus通过；不重复full；生成
  `.ai-sdlc/work-items/206-model-string-dedupe/t61-differential-rollback-receipt.json` 并记录SHA-256。

### T43 Candidate 全量与治理验证

- **状态**：待执行
- **依赖**：T42
- **验收**：candidate full pytest、Ruff、constraints、validate/truth、diff check通过；snapshot fresh、state
  ready、exit0、zero blocker、inventory complete；GAP-09～11无回归；工作树只含allowlist。

## Batch 5：Final review、PR 与 fresh-main acceptance

### T51 Final tree 双 Agent 复审

- **状态**：待执行
- **依赖**：T43
- **验收**：两个维度对同一HEAD/tree/binary diff/name-status/receipt/formal hashes均PASS；无可操作finding。

### T52 Implementation PR、Codex review 与 CI

- **状态**：待执行
- **依赖**：T51
- **验收**：逻辑单一、branch pushed、ready PR、`@codex review`、约5分钟heartbeat；finding修复后重跑门禁
  并重新review；required checks全绿。

### T53 Merge 与 fresh-main acceptance

- **状态**：待执行
- **依赖**：T52
- **验收**：fresh clone重跑19-file targeted、root truth、full、结构/binding、Ruff、truth；branch tree与
  mainline内容一致；WI-206=`completed_reduction`。

### T54 回写父路线并继续

- **状态**：待执行
- **依赖**：T53
- **验收**：WI-196记录WI-205/WI-206关闭证据和remaining route；dispatcher重复不冒充已关闭；不误报
  GAP-05/WI-196/RC-08完成；选择下一原子项。父路线全部关闭后才发布新版本。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| GAP-05 / T63 / WP-03 | T11～T54 |
| LP-02 / LP-03 / LP-08 / LP-12 | T12、T23、T31～T43 |
| CC-01～CC-08 | T12、T22、T34、T41～T43 |
| RC-01～RC-10 | T12、T22、T31～T43 |
| FR-08 / FR-09 / FR-10 | T14、T15、T51～T53 |
| SC-01～SC-08 | T14、T15、T23～T54 |
