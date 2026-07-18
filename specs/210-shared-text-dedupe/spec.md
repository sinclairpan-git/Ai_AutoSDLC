# 功能规格：共享文本去重重复族减重

**功能编号**：`210-shared-text-dedupe`
**创建日期**：2026-07-18
**状态**：completed_reduction；formal PR #148、implementation PR #149 与 fresh-main acceptance 已完成
**父项**：WI-196 `T63 / WP-03 / GAP-05`
**基线 revision**：`4b4348646a11cf2e27e488ddad892977958476a9`

## 1. 决策摘要

冻结基线 `main@4b434864` 存在一个可机械证明的私有文本去重重复族：28 个顶层函数、27 个模块、196 行产品代码、
730 个直接调用。28 个函数的 AST body digest 均为
```
08aa3c8fe861c4d69e2fcfcdbc6bc212b7b6d0c52ef6e2e4b382327dd48d962a
```

本项只把该 exact family 收敛到现有
`src/ai_sdlc/utils/helpers.py::_dedupe_text_items`。该模块在冻结基线为 96 raw / 68 non-empty LOC，只依赖标准库，
docstring 已明确覆盖 text processing；repo-wide 已有 55 个 importer，CLI/Core/Generators 中有 42 个，
其中 10 个属于本候选。实现必须保留 28 个模块局部私有名，
730 个调用表达式零修改；不新增模块、公共导出、wrapper、策略或配置。

WI-204 的 Program Finalization 候选保持 RC-09 No-Go：旧 sponsor 已撤销、claim=0，不能由本项复活。
本项选择纯 7 行函数族，是因为其净减重、证明成本和回退粒度优于当前 T65/WP-06/WP-07 候选。

## 2. 冻结范围

### 2.1 目标定义

- CLI（6 defs / 5 files）：
  `commands.py`、`program_cmd.py`、`run_cmd.py`、`sub_apps.py`（2 defs）、
  `workitem_cmd.py`。
- Core（15 defs / 15 files）：
  `artifact_target_guard.py`、`backlog_breach_guard.py`、`close_check.py`、
  `execute_authorization.py`、`frontend_contract_observation_provider.py`、
  `frontend_contract_runtime_attachment.py`、`frontend_contract_verification.py`、
  `frontend_gate_verification.py`、`frontend_visual_a11y_evidence_provider.py`、
  `p1_artifacts.py`、`plan_check.py`、`runner.py`、`verify_constraints.py`、
  `workitem_traceability.py`、`workitem_truth.py`。
- Generators（7 defs / 7 files）：
  `frontend_cross_provider_consistency_artifacts.py`、
  `frontend_generation_constraint_artifacts.py`、
  `frontend_page_ui_schema_artifacts.py`、
  `frontend_provider_expansion_artifacts.py`、
  `frontend_provider_runtime_adapter_artifacts.py`、
  `frontend_quality_platform_artifacts.py`、
  `frontend_theme_token_governance_artifacts.py`。

局部符号分布为 24 个 `_dedupe_text_items`、3 个 `_dedupe_cli_text_items`、1 个
`_dedupe_status_text_items`；完整调用数为 730，其中 `program_cmd.py` 为 489。

### 2.2 冻结语义

共享函数必须原样保持当前 body：

1. 先求值 `values or []`，保留 truthiness 调用和异常时序；
2. 对输入单遍迭代，逐项执行 `str(value).strip()`；
3. 丢弃空字符串；
4. 使用 list membership 去重，保留首次出现顺序，不改为 set/hash；
5. `__bool__`、迭代、`__str__`、strip 或 equality 异常原样传播；
6. 不读取文件、环境、网络、subprocess、状态或配置。

### 2.3 明确排除

- 返回 tuple、无 strip、仅接受 `list[str]`、mapping/model/path 去重等非 exact family；
- `p1_artifacts.py` 以外的 Request/Result/DTO、store、baseline builder；
- `program_service.py`、Program finalization handlers、Lean Gate；
- 新 `utils` 框架、泛型协议、公共 API、`__init__.py` re-export、动态注册或 reflection dispatch；
- 修改 730 个调用表达式、错误文案、artifact/schema、CLI option/exit 或状态机。

## 3. 兼容边界

28 个模块局部符号必须继续存在，因此 repo 内 monkeypatch/import-by-module 仍能工作。允许的私有
introspection 差异仅限函数对象统一后必然发生的 `identity`、`__module__`、`__name__`、
`__qualname__`、`__code__`、源码位置、traceback frame，以及 `p1_artifacts` 的私有 annotation 从窄
union 变为共享 `object`。只读扫描与 corpus 必须证明仓库内没有依赖这些属性的 consumer；若存在且
需要 wrapper 才能兼容，按 RC-09 停止，不新增 wrapper。

除上述明确批准的私有 introspection 差异外，以下均要求零差异：

| 合同 | 必须保持 |
|---|---|
| CC-01 API/CLI | 公共 import、命令、option、help、stdout/stderr、exit code |
| CC-02 错误 | 结果与异常 type/message/event 顺序 |
| CC-03 artifact/schema | 路径、字节、字段、顺序、文件 mode |
| CC-04 状态机 | checkpoint、runtime、truth、close/readiness 结论 |
| CC-05 授权/副作用 | 文件、网络、subprocess、环境与 adapter 调用集合 |
| CC-06 幂等/恢复 | 重复调用、generator 单遍消费与首次出现顺序 |
| CC-07 平台 | Python 3.11/3.12 与 Windows/macOS/Linux |
| CC-08 发布 | 本项不单独发版；最终路线发布仍执行 installed/sibling smoke |

### 3.1 GAP-09～GAP-11 防回归影响分析

| Gap | 本切片影响 | 强制证据与失败处置 |
|---|---|---|
| GAP-09 frontend inheritance | 目标虽含 frontend provider/generator 私有 helper，但不改 capability、provider、style、继承或 codegen/test admission；730 calls 与 artifact/schema 必须零差异 | `program truth audit` 的 frontend capability 必须继续 `closed/ready` 且 blocking refs 集合不变；否则 owner=WI-210 delivery，停止并重开 GAP-09 |
| GAP-10 adapter consumption | 27 个目标模块不含 adapter ingress/canonical consumption 实现；CLI 私有去重不得改变 adapter 调用集合、入口或本机会话诊断 | agent-adapter capability 必须继续 `closed/ready`，truth/close refs 与相关 CLI transcript 不变；否则 owner=WI-210 delivery，停止并重开 GAP-10 |
| GAP-11 source inventory | formal 只新增已映射 WI-210 sources；implementation 新产品/测试文件=0，不新增 source registry 类型 | formal 允许唯一预登记 close source `development-summary.md` 暂未物化；除该项外必须 unmapped=0/missing=0，closure 后总 missing=0；否则 owner=WI-210 delivery，停止并重开 GAP-11 |

命令回执写入 `specs/210-shared-text-dedupe/task-execution-log.md`；implementation differential 与
rollback/reapply 复用一个结构化回执：
`.ai-sdlc/work-items/210-shared-text-dedupe/t61-differential-rollback-receipt.json`。不为同一 L1
候选拆分第二个 evidence schema 或 sidecar。

## 4. Reduction Contract

| 条款 | 冻结值 |
|---|---|
| RC-01 目标切片 | §2 的 28 defs / 27 files / 730 calls |
| RC-02 基线 | definition non-empty=196；机械删除含分隔空行为 raw=252；1 个 body digest；fresh-main full `3275 passed, 3 skipped` |
| RC-03 实现预算 | 产品 raw `+≤39/-≥252/net≤-213`；non-empty `+≤35/-≥196/net≤-161`；characterization test non-empty≤9；truth expectation≤2；RC-06 计划 non-empty additions≤46、硬上限49；harness/normalizer=0；新产品/测试文件=0 |
| RC-04 结果 | defs 28→1；selected family 100% 清零；产品 non-empty 净删≥161；复杂度代理 112→4；空行删除不得计入非空减重收益 |
| RC-05 临时膨胀 | helper 与 28 个旧 body 必须在同一实现提交替换；任一提交不得保留 29 份实现 |
| RC-06 保护成本 | `floor(196×25%)=49`；按 Ruff 后 non-empty additions 计量；产品35+test≤9+truth≤2 计划≤46，保留≥3 行余量；空行不进入分子或分母 |
| RC-07 结构 | helper 插入=9 raw / 7 non-empty，`helpers.py` 实现后≤105 raw LOC；公共抽象/新模块=0 |
| RC-08 父终态 | 只关闭一个 T63 family，不关闭 GAP-05/WI-196，不声称两个 Program 文件≤400 |
| RC-09 停止 | 超预算、cycle、alias/call 漂移、行为/event 差异、需 wrapper/suppression/分支特判即 No-Go |
| RC-10 回退 | exact baseline tree restore + targeted/full 边界 + reapply tree identity |

预算不得通过 `noqa`、压长行、隐藏 JSON/manual probe、删除测试或不计 truth 修改规避。实现 spike 只用于
修正预算，不构成授权或减重完成证据。

## 5. T61A/T61B 证明合同

### T61A（实现前）

1. 在 formal receipt 合入后的 exact `main` 重算 28/27/196/730 与 body digest；任一漂移停止。
2. 扫描 repo 内 private import/introspection/monkeypatch consumer，冻结批准差异集合。
3. 对 distinct body 运行 success、`None`、空/空白、重复、数字/字符串碰撞、裸字符串、generator、
   truthiness/iterator/`str`/equality 失败 corpus，记录结果、异常和事件序列。
4. 运行受影响测试与 full baseline；不得以删减测试换预算。

### T61B（同一 candidate）

1. 先增加≤9 non-empty 行的既有测试文件内 RED，证明共享 helper/顺序合同尚未建立；再实施 GREEN。
2. AST/binding gate 证明只剩 1 个 exact body、28 个局部 alias、730 个调用表达式不变。
3. 干净子进程逐一 import 27 个目标模块；不得有 cycle、import-time 写入或 stderr。
4. baseline/candidate corpus 结果、异常与 event trace 完全一致；临时 reverse-order mutation 必须 RED。
5. 运行 targeted/full、Ruff lint、formatter-debt parity、constraints、Program Truth、manifest exact test
   和三平台 CI；基线与 candidate 当前 format-check 待格式化集合必须同为精确 24 文件，不伪报 PASS。
6. 在隔离 worktree 完成 exact revert/reapply tree identity；同一 candidate identity 由两位 reviewer 双 PASS。

测试预算唯一按 Ruff 后新增 non-empty 行计量：空行不计；注释、参数化数据与其他所有非空新增行均计；
raw additions 另行披露但不形成第二个判定阈值。

## 6. 功能需求

- **FR-01**：系统只保留一份 §2.2 算法实现。
- **FR-02**：28 个局部私有名和 730 个调用表达式保持，公共行为零差异。
- **FR-03**：共享实现只落在现有 `utils/helpers.py` text section，不新增模块或公共导出。
- **FR-04**：formal、implementation、closure 使用独立 branch/PR；formal merge 前不得改产品代码。
- **FR-05**：本项修改父 formal，review target 按父 plan §9 唯一算法覆盖父子各 spec/plan/tasks 六文件；
  任一目标文件变化使旧双审结论失效，Pascal 与 Confucius 必须对同一身份重新 PASS。
- **FR-06**：implementation PR 必须通过 Codex current-head review、required CI、merge 后 fresh-main。
- **FR-07**：formal 只可机械更新 `test_repo_program_manifest.py` 中受 WI-210 source/layer 计数影响的
  既有 expectation（≤2 additions/≤2 deletions），不得新增测试逻辑或改其他断言。

## 7. 成功标准

- **SC-01**：父子六个 formal 文件的 canonical combined identity 获双 Agent PASS，无可操作 finding。
- **SC-02**：产品 raw `+≤39/-≥252/net≤-213`，non-empty `+≤35/-≥196/net≤-161`；
  计划 RC-06 non-empty additions≤46、硬上限49。
- **SC-03**：exact body 28→1、局部 alias=28、调用=730，无 wrapper/new module/public export。
- **SC-04**：T61B corpus、clean imports、targeted/full、三平台 CI 与 rollback/reapply 全绿。
- **SC-05**：implementation 同一 final identity 双 PASS、Codex clean、合并后 fresh-main clean。
- **SC-06**：WI-210 只以 `completed_reduction` 关闭本 family；父路线保持 active。
