---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：共享文本去重重复族减重

**编号**：`210-shared-text-dedupe`
**基线**：`origin/main@4b4348646a11cf2e27e488ddad892977958476a9`
**风险**：L1 / T63 / WP-03
**当前阶段**：formal freeze；产品实现未授权

## 1. 目标与原则

一次只关闭 28 个 exact AST body 组成的重复族。实现采用现有
`src/ai_sdlc/utils/helpers.py` 的 text section 作为唯一承载点，保持 28 个局部私有 alias 和 730 个
调用表达式。计划优先减少实现与证明总量，不创建第二个 helper module、wrapper、公共工具框架或配置。

本项不处理 ProgramService/Program Stage/baseline/store，也不恢复 WI-204 sponsor。formal 和产品实现
分为独立 branch/PR；只有 formal mainline receipt 后才能从新的 `main` 建 implementation branch。

## 2. 当前真值

| 指标 | 基线 |
|---|---:|
| exact definitions | 28 |
| modules | 27 |
| product LOC | 196 |
| direct calls | 730 |
| body digest | `08aa3c8f...d48d962a` |
| existing helpers.py importers | 55 repo-wide / 42 in CLI/Core/Generators |
| target modules already consuming helpers.py | 10 / 27 |
| fresh-main full | `3275 passed, 3 skipped` |
| implementation spike | raw `+39/-252/net -213`; non-empty `+35/-196/net -161`; 1282 tests passed |

选择次序已经过双维度只读审计：

1. T65 会先增加 loader/schema，尚无可删除的第二真值，当前收益不确定；
2. WP-06 仍是约 17K 行、250 方法的 L3 分解，未冻结可避免纯搬运的单领域切片；
3. WP-07 的 WI-204 因最低可信 proof 超 sponsor cap 已 RC-09 No-Go；
4. 当前 T63 为无 I/O 的 7 行 exact body，可用低成本 differential 和整库测试证明。

## 3. 交付拓扑

```text
formal branch / PR
  spec + plan + tasks + log + parent index + truth/continuity
        │ mainline receipt
        ▼
implementation branch / PR
  T61A → RED → helper/import aliases → T61B → rollback → dual review
        │ Codex current-head + required CI + merge
        ▼
fresh-main acceptance / closure
  completed_reduction for one T63 family; parent remains active
```

## 4. Phase 0：Formal 冻结

### 4.1 范围

- 物化 WI-210 canonical docs；
- 把 28/27/196/730、目标文件、允许的私有 introspection 差异和全部 RC 写成单一合同；
- 更新 WI-196 索引、manifest、continuity；
- 不修改 `src/`、workflow、release 或 runtime state machine；`tests/` 唯一允许差分是
  `test_repo_program_manifest.py` 中≤2条 source/layer expectation 的机械同步，不得新增逻辑。

### 4.2 门禁

- Pascal 从净减重、直接性、YAGNI、预算评审；
- Confucius 从行为、导入、安全、回退、证据完整性评审；
- 本项修改父 formal，因此 review target 按父 plan §9 唯一算法包含父子各 spec/plan/tasks 六文件；
  两者必须对相同 canonical combined identity 独立 PASS，任一目标文件修订使两份 verdict 同时失效。

### 4.3 GAP-09～GAP-11 admission

- GAP-09：frontend capability/inheritance、blocking refs 与 codegen/test admission 不得变化；
- GAP-10：adapter canonical consumption、CLI transcript 与 adapter 调用集合不得变化；
- GAP-11：除预登记且关闭前缺失的 WI-210 `development-summary.md` 外，unmapped/missing 必须为 0；
  implementation 不新增产品/测试 source，closure 后 missing 必须回到 0；
- 任一分析不确定或 truth/audit 结论漂移时，由 WI-210 delivery owner 停止本项并重开对应 GAP。

## 5. Phase 1：T61A 与 TDD

从 formal merge 后 exact `main` 创建独立 implementation branch。

1. 重算 body/function digests、定义/文件/调用数和 protected blobs；漂移即停。
2. 扫描 private consumer、import graph 与现有测试，生成实现前 corpus 结果。
3. 在一个既有测试文件中增加≤9 non-empty 行；先以 shared binding 缺失形成 RED；空行不计，注释、
   参数化数据及其他非空新增行全部计入，raw additions 另行披露。
4. 临时 reverse-order mutation 必须被该测试或既有顺序断言杀死；mutation 不提交。

T61A 不新增独立 harness、snapshot、fixture 或 JSON evidence 文件；命令、digest 和结果写入既有
`task-execution-log.md`。

## 6. Phase 2：最小实现

1. 在 `utils/helpers.py` 的 text helpers 区原样加入一个私有 7 行函数。
2. 27 个目标模块删除 28 个本地 body，通过 import/alias 保留局部名称。
3. 不修改 730 个调用表达式，不改函数调用参数或返回处理。
4. 同一实现提交完成 helper/add-import/delete-body，禁止中间树长期保留 29 份实现。
5. 运行 Ruff probe 后核算 raw/non-empty diff；产品必须满足 raw `+≤39/-≥252/net≤-213` 与
   non-empty `+≤35/-≥196/net≤-161`。RC-06 按 non-empty 计量：product35+test≤9+truth≤2
   计划≤46、硬上限49，保留至少 3 行余量。

## 7. Phase 3：T61B 与回退

### 7.1 Differential

- 复跑 baseline corpus，逐 case 比较结果、异常 type/message 和 event trace；
- AST gate：exact body=1、module-local aliases=28、calls=730；
- clean subprocess import 27 个目标模块；
- public CLI/artifact/state 由受影响测试和 full suite 覆盖；
- Ruff lint、constraints、validate、Program Truth、manifest exact 与 required CI 全绿；format-check 的
  inherited 24-file debt 集合必须 baseline/candidate 精确一致，不把 parity 误报为 formatter PASS。

### 7.2 Rollback

在隔离 worktree：

1. candidate→baseline，tree OID 必须等于 frozen baseline；
2. 重跑 helper corpus、受影响测试和 import gate；
3. baseline→candidate，tree OID 必须等于 reviewed candidate；
4. full suite 只需在 baseline 和最终 candidate 各完整执行一次，不为仪式重复第三次。

## 8. Phase 4：Review、PR 与 Fresh Main

1. 把最终 commit/tree/diff/corpus/LOC/rollback identity 绑定到 review invocation；
2. Pascal 与 Confucius 对同一 identity 双 PASS；
3. push、创建 PR、请求 Codex current-head review，保持约五分钟 heartbeat；
4. actionable finding 只做 focused 修复，内容变化后重跑双审与 Codex review；
5. required checks 全绿后 merge；
6. detached fresh `main` 跑 targeted/full/Ruff/governance/clean-state acceptance；
7. closure 只登记一个 T63 `completed_reduction`，不关闭 WI-196 或发布版本。

## 9. 停止与回退条件

- 28/27/196/730 或 body digest 漂移；
- 新 import 形成 cycle、import-time 写入或 CLI 启动失败；
- alias 缺失、调用表达式变化、repo 内 private consumer 需要 wrapper；
- corpus、artifact、状态、exit、平台或 performance 出现未批准差异；
- 产品 raw/non-empty 超 `+39/+35`、删除低于 `252/196`、产品 non-empty 净删<161，或 RC-06
  non-empty additions>49；
- 需要新模块、公共导出、配置、suppression、动态 dispatch 或分支特判。

发生任一项立即恢复 baseline、状态记为 `cancelled_no_go`，不得用缩减测试或扩大预算继续。

## 10. 验证命令族

- 结构/预算：AST inventory、`git diff --numstat`、non-empty counter、private consumer scan；
- 质量：`uv run ruff check ...`、`uv run ruff format --check ...`；
- 测试：shared helper RED/GREEN、受影响 tests、`uv run pytest -q`；
- 治理：`uv run ai-sdlc verify constraints`、`program validate`、`program truth sync/audit`；
- 回退：exact tree OID + revert/reapply + clean-state guard。

32-file targeted 命令唯一冻结在 `tasks.md` T12；T61A 从 formal receipt 后 main 机械校验该清单的
存在性、顺序和收集数，不在 plan/spec 重复维护第二份文件列表。
