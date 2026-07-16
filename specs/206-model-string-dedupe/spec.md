# 功能规格：Model String Dedupe Reduction

**功能编号**：`206-model-string-dedupe`
**创建日期**：2026-07-16
**状态**：formal review candidate；未授权实现
**父项**：WI-196 `T63 / WP-03 / GAP-05`
**基线 revision**：`aa156afe53534a10b1379348c532eb554ccf9ad3`

## 1. 问题与事实基线

`src/ai_sdlc/models/` 下存在 18 个顶层私有 helper：17 个名为
`_dedupe_strings(value: object) -> list[str]`，`state.py` 的同语义符号名为
`_dedupe_string_items(value: object) -> list[str]`。18 个函数的完整 AST body digest 均为
`3a0faf9ac553d0701610620b2b17ee0dda2fa014442a3eebf0a0c6c11067042d`；每份 12 个非空产品
LOC，共 216 LOC、100 个现有调用点、聚合圈复杂度代理 72。

| 模块 | 本地符号 | 调用点 |
|---|---|---:|
| `frontend_browser_gate.py` | `_dedupe_strings` | 9 |
| `frontend_contracts.py` | `_dedupe_strings` | 4 |
| `frontend_cross_provider_consistency.py` | `_dedupe_strings` | 8 |
| `frontend_gate_policy.py` | `_dedupe_strings` | 9 |
| `frontend_generation_constraints.py` | `_dedupe_strings` | 5 |
| `frontend_managed_delivery.py` | `_dedupe_strings` | 9 |
| `frontend_page_ui_schema.py` | `_dedupe_strings` | 3 |
| `frontend_provider_expansion.py` | `_dedupe_strings` | 4 |
| `frontend_provider_profile.py` | `_dedupe_strings` | 6 |
| `frontend_provider_runtime_adapter.py` | `_dedupe_strings` | 4 |
| `frontend_quality_platform.py` | `_dedupe_strings` | 6 |
| `frontend_solution_confirmation.py` | `_dedupe_strings` | 4 |
| `frontend_theme_token_governance.py` | `_dedupe_strings` | 3 |
| `frontend_ui_kernel.py` | `_dedupe_strings` | 4 |
| `host_runtime_plan.py` | `_dedupe_strings` | 3 |
| `program.py` | `_dedupe_strings` | 7 |
| `scanner.py` | `_dedupe_strings` | 4 |
| `state.py` | `_dedupe_string_items` | 8 |

18 个 helper 均被 Pydantic `field_validator(..., mode="before")` 调用，语义一致：

1. `None` 返回 `[]`；
2. 其他输入按原迭代顺序逐项执行 `str(item)`；裸字符串因此按字符迭代；
3. 以转换后的字符串做 hash/equality 去重，保留首次出现顺序；`1` 与 `"1"` 会碰撞；
4. 不 `strip()`、不丢空串、不大小写折叠、不排序；
5. `__iter__`、`__next__`、`__str__`、转换后字符串的 `__hash__`/`__eq__` 异常不包装；
6. 无 I/O、状态写入、配置读取或外部副作用。

18 个基线产品模块当前共 8,556 raw / 7,454 non-empty LOC。受影响测试清单固定为 19 个文件，
共 10,537 raw / 9,646 non-empty LOC；PowerShell fresh run 为
`281 passed, 2 skipped in 1.65s`。fresh-main 全量基线为 `3220 passed, 3 skipped`。

## 2. 目标、范围与非目标

### 2.1 目标

1. 在 `src/ai_sdlc/models/_string_lists.py` 保留唯一一份原样 12 LOC 算法。
2. 新模块使用 `from __future__ import annotations`，保持运行时 `__annotations__` 与
   `inspect.signature`；文件预测 15 raw LOC。
3. 17 个模块导入 `_dedupe_strings`；`state.py` 以
   `_dedupe_strings as _dedupe_string_items` 保留本地符号和 8 个调用表达式。
   18 条 import 必须位于各模块标准顶层 first-party import block；不得使用 late/mid-file import、
   分号或多语句压行、`# noqa`、`# ruff: noqa`、`# isort: skip`、`# isort: off/on`、修改 Ruff
   配置或等价 suppression 规避正常分组与行数成本。
4. 重复算法族从 216 LOC 降为 12 LOC，下降 94.4%；包含新文件、18 条 import 与 Ruff 要求的
   4 条 import-block 分隔空行后，raw replacement slice 从 216 降为 37 LOC，下降 82.9%。
5. 固定 19 个产品文件 raw diff 为 additions≤37、deletions≥216、net≤-179；定义数 18→1，
   imports=18、calls=100、complexity proxy 72→4。

实现探针证明 `frontend_contracts.py`、`frontend_provider_expansion.py`、
`frontend_solution_confirmation.py` 与 `frontend_ui_kernel.py` 原先没有 first-party import block；为同时
满足 Ruff `I001` 与顶层定义间距，每个文件必需新增 1 条分隔空行。在标准顶层 import、无 suppression
的实现合同下，该 4 行是格式正确性的必要成本，不是新抽象、wrapper、测试或行为代码；其余 14 个
模块可复用删除首个本地 helper 后释放的既有空行，不产生第二条 addition。

### 2.2 范围

- 一个新的私有模块 `_string_lists.py`，不经 `ai_sdlc.models.__init__` re-export。
- §1 的 18 个模型模块，只删除本地 body 并导入同一 helper；validators 与调用表达式不改。
- 在既有 `tests/unit/test_program_models.py` 增加最小共享身份断言，先证明三个代表性本地函数对象
  不同，再证明 17 个 `_dedupe_strings` 和 state alias 绑定同一 helper；不新增测试文件或 fixture。
- 使用既有 program 首次出现顺序断言执行 reverse-output mutation RED；不重复增加行为测试。
- WI-206 五件套物化后，将 root inventory expectation 从 `1081/1081/0/0` 更新为
  `1086/1086/0/0`，close layer 从 `205/205` 更新为 `206/206`；只替换两个既有 assertion line。
- 更新本 WI execution log、development summary、continuity、Program Truth 和父 WI-196 执行索引。

### 2.3 明确排除

- `src/ai_sdlc/core/dispatcher.py::StageManifest._dedupe_string_lists` 的 body digest 相同，但它是带
  `field_validator + classmethod`、含 `cls` 参数的 class-local validator。纳入本项必须保留 wrapper
  或改变 decorator binding，违反“顶层一参数 models helper”原子边界；它留给后续独立候选。
- 不收敛其他 `_dedupe_text_items`、mapping/model/path 去重或 `state.py` 的 int/dict helper。
- 不修改 validator decorator/field、Pydantic model、默认值、schema、serialization 或错误规则。
- 不建立公共 `utils`、泛型协议、基类、mixin、策略、配置或依赖。
- 不修改 `program_service.py`、`program_cmd.py`、Loop Store、baseline builder 或 Lean Gate。
- 不触发 frontend solution-confirm：本项不改变技术栈、provider、页面、组件或浏览器行为。

## 3. 方案比较与冻结决策

### 方案 A：单个 models 私有 helper（采用）

把现有 FunctionDef 原样放入 `_string_lists.py`，18 个模块显式 import；state 仅使用 import alias。
算法、签名、annotation、调用表达式和异常时序不引入分支。修订后产品上限 +37/-216/net -179，满足
LP-02、RC-04、RC-06。

### 方案 B：每个 validator 内联表达式（拒绝）

该方案仍保留 100 个语义真值，并改变 `None`、惰性迭代、hash/equality 调用时序和异常栈；短行数不等于
低风险减重。

### 方案 C：扩展为通用 dedupe framework（拒绝）

不同 dedupe helper 对返回类型、字符串转换、mapping/model 相等性和失败语义不一致。打包会扩大范围并
引入分支特判，违反 WP-03 单重复族和 RC-09。

## 4. 用户故事与验收场景

### US-1：删除重复实现（P0）

作为框架维护者，我希望 100 个现有调用表达式只依赖一份清晰实现，以便修改语义时不再同步 18 份代码。

1. **Given** 基线存在 18 个相同 body，**When** 完成 candidate，**Then** 只剩
   `_string_lists.py` 中 1 个定义，18 个模块绑定它且 100 个调用保留。
2. **Given** 任一模块保留 wrapper、本地 body 或第二算法，**When** 运行 AST/binding gate，**Then**
   candidate 失败并按 RC-09 停止。

### US-2：保持模型兼容（P0）

作为框架使用者，我希望现有模型校验、错误和序列化完全不变。

1. **Given** success、裸字符串、惰性迭代和可达异常 corpus，**When** 对每个 distinct body digest
   比较 baseline/candidate，**Then** 结果、异常 type/message 和事件轨迹一致。
2. **Given** 18-module binding matrix，**When** candidate 导入 helper，**Then** 每个本地符号 identity、
   signature、annotations 和调用数满足冻结合同。
3. **Given** reverse-output mutation，**When** 运行既有 program model tests，**Then** 首次出现顺序
   断言稳定 RED；恢复后 GREEN。

### US-3：控制减重成本（P0）

1. **Given** 删除基线 216 LOC，**When** 复算 RC-06，**Then**产品、测试、harness、normalizer 与
   root truth test 的 raw additions 合计不超过 `floor(216×25%)=54`。
2. **Given** 产品 additions≤37、共享身份 test≤4、root truth replacement additions=2，
   **When** 计算最终 ledger，**Then** 总计≤43、余量≥11；文档不冒充代码预算。

## 5. 兼容合同（CC）

| CC | 影响与冻结内容 |
|---|---|
| CC-01 公共 API/CLI | 无公共命令、option、import surface 变化；helper 不 re-export。 |
| CC-02 错误/退出 | Pydantic validation、异常 type/message、CLI exit 行为零未批准差异。 |
| CC-03 artifact/schema | model schema、`model_dump`、JSON/YAML 字段和值/顺序不变。 |
| CC-04 状态机 | state 模型使用同一算法，但不改变 checkpoint/work item/loop/review 状态规则。 |
| CC-05 授权/副作用 | helper 无 I/O；不得新增文件、网络、subprocess、环境或配置访问。 |
| CC-06 幂等/恢复 | 同一输入重复校验结果一致；迭代与异常事件时序保持。 |
| CC-07 平台 | Python 3.11、Windows/macOS/Linux、PowerShell、Unicode 由 full CI 与现有 tests 保护。 |
| CC-08 发布 | 无需单独 sibling execute；最终版本发布仍执行仓库 release smoke。 |

本项的私有 introspection 合同只覆盖下列枚举属性，不声称穷尽 Python 函数对象的所有可观察状态。
批准差异：全部 binding 的函数对象 identity、`__module__`、`__globals__`、`__code__` identity/
`co_filename`/`co_firstlineno`、源码文件和 traceback frame 指向 `_string_lists.py`；
`state._dedupe_string_items` 的本地符号保持，但 callable `__name__`/`__qualname__` 变为
`_dedupe_strings`。只读扫描必须证明没有外部 private import 或 introspection consumer 依赖这些属性。

必须保持：17 个 `_dedupe_strings` binding 的 callable name/qualname、全部 18 个 binding 的
`inspect.signature == "(value: 'object') -> 'list[str]'"`、
`__annotations__ == {'value': 'object', 'return': 'list[str]'}`、defaults/kwdefaults/doc、
`__code__.co_argcount/co_kwonlyargcount`、100 个调用和公共模型行为。

## 6. Reduction Contract

- **RC-01 目标切片**：§1 的 18 个顶层 models helper 和 100 个调用；dispatcher class validator 排除。
- **RC-02 基线**：18 defs、100 calls、216 non-empty algorithm LOC、complexity 72、body digest
  `3a0faf9a...7042d`；19-file targeted `281 passed, 2 skipped`；full `3220 passed, 3 skipped`。
- **RC-03 预算**：新增私有模块=1、产品 raw additions≤37；其中 4 行仅为 Ruff `I001` 必需分隔；
  import 必须位于标准顶层 first-party block，禁止 late/mid-file import、压行、lint suppression 或
  修改 lint 配置；
  新测试文件/fixture/harness/normalizer=0；
  共享身份 test≤4；root truth additions=2。
- **RC-04 结果**：重复族 18→1；算法 216→12（-94.4%）；raw replacement 216→37（-82.9%）；
  product net≤-179；complexity 72→4；纯移动、wrapper 或第二 helper 均 No-Go。
- **RC-05 临时膨胀**：implementation commit 同时加入 helper/import 并删除 local body；不得长期保留
  19 份实现。任一 commit 产品 additions>37 即停止。
- **RC-06 保护成本**：删除 216 对应 cap 54；最终 source additions≤43，余量≥11；删除不抵扣新增。
- **RC-07 结构**：新文件 15 raw LOC、函数 12 LOC，低于 400/50；不增加 public dependency edge。
- **RC-08 父终态**：本项只关闭一个 T63 重复族，不宣称 WI-196、GAP-05 或 10%/400 行终态完成。
- **RC-09 停止**：行为/事件差异、import cycle、Pydantic schema/error 漂移、预算超限、调用数变化或
  需要分支特判时立即 No-Go 并保留 18 份 legacy。
- **RC-10 回退**：baseline 和 candidate 各完成一次 full suite；rollback rehearsal 不重复 full，改以
  exact Git tree OID 恢复 + 19-file targeted + behavior/event corpus 证明 revert/reapply 两侧身份。

## 7. T61 证明合同

### 7.1 结构与绑定基线

- 17 个 `_dedupe_strings` 完整 FunctionDef digest：
  `1d9a0a053fb07dcb666d1f78a1b2e3bbae2a01662b55b757a61e40cdd1addefa`；签名合同 digest：
  `c4900c7972a05d3b0542e3fd17d92e2741d7a0cd89d875359e216a148e21a99f`。
- state 完整 FunctionDef digest：
  `a445f2702e6fad95f1ae23fdabe3c2b9995b1a397acf52dd1fc047a45686591b`；签名合同 digest：
  `76fe23d1efd7f9b676fb1bccb8787ba977f9fb9863ff4d93217c220f1fbcf9da`。
- candidate shared helper 的完整 FunctionDef 必须等于第一组 digest；18-module binding matrix 另验证
  state alias、本地符号、identity、signature、annotations、defaults/doc 和无外部 private consumer。

### 7.2 Behavior/event corpus

所有 baseline body digest 相同，因此每个 distinct body digest 只保存一份 baseline/candidate corpus；
不重复保存 18 份同义结果。binding matrix 证明该结果适用于全部模块。

corpus 至少覆盖：`None`、空列表、重复列表、`1`/`"1"` 碰撞、空串/空白、tuple、裸字符串、普通
generator、`__iter__` 抛错、`__next__` 首项前抛错、部分 yield 后抛错、`__str__` 抛错、恶意 str
subclass 的 hash 抛错、相同 hash 下 equality 抛错。每个 case 新建输入并记录
`__iter__/__next__/__str__/__hash__/__eq__` event trace、结果或 fully-qualified exception type + message。

### 7.3 T61A/T61B

1. Formal receipt 合入后，从 exact main 新建 implementation branch，记录 Python/Pydantic/OS。
2. baseline 运行 19-file targeted、full suite、结构/binding ledger 与一份 digest corpus。
3. 先在既有 `test_program_models.py` 加共享 identity assertion，baseline 必须精确 RED。
4. candidate 运行同一结构/binding/corpus、targeted、root truth、full suite、Ruff 和治理门禁。
5. 临时 reverse-output mutation 必须使既有 program order test RED；用 `apply_patch` 恢复 GREEN。
6. disposable clone 验证 revert tree OID==baseline tree、reapply tree OID==candidate tree；两侧重跑
   targeted+corpus，不重复 full；生成一个 differential/rollback receipt。

## 8. GAP 影响与生命周期

- GAP-05/T63：WI-205 已关闭 artifact path family；WI-206 只关闭 top-level models string family。
  dispatcher class validator 与其他重复族仍可由后续审计决定，因此父 T63/GAP-05 不自动关闭。
- GAP-01/WP-02：WI-202 No-Go 与 sponsor=0 保持；本项预算不得转移给 Lean Gate。
- GAP-03/04/06：ProgramService、Program Stage 和 baseline builder 不在 diff 中。
- GAP-09～11：truth blocker 或 unmapped/missing source 再现时 fail-closed 并重开对应 GAP。
- formal branch 只允许五件套、manifest/project-state、root inventory 两行、父执行索引和 continuity；
  formal 双 PASS 与 mainline receipt 前不得修改产品代码。

## 9. 成功标准

- **SC-01**：formal 三文件无占位或矛盾，两个 Agent 对同一哈希均 PASS。
- **SC-02**：formal PR 合入 main 后，implementation 从该 receipt 新建独立 branch/worktree。
- **SC-03**：结构 identity RED 先于产品实现；reverse mutation RED、恢复 GREEN。
- **SC-04**：最终 defs=1、imports=18、calls=100、body/FunctionDef/signature/binding 合同通过，无 wrapper、
  public export 或新依赖。
- **SC-05**：产品 +≤37/-≥216/net≤-179；全部 source additions≤43≤54。
- **SC-06**：19-file targeted、root truth、candidate full、Ruff、constraints、truth 和 required CI 通过。
- **SC-07**：两个 Agent 对同一 final tree/diff hash 再次 PASS，Codex review 无未处置问题。
- **SC-08**：rollback exact tree OID + targeted/corpus receipt 可复算；fresh-main acceptance 后只关闭 WI-206。

## 10. 冻结决策

1. 选择 18-module top-level models string family，优先于 L2 Page/UI、RC-06 No-Go Loop Store、L3
   ProgramService 与已被 WI-204 停止的 Program Finalization candidate。
2. 纳入 `state.py` exact body；dispatcher class validator因 decorator/signature 边界明确排除。
3. helper 保留 future annotations 与原样 12 LOC body，不进行表达式压缩。
4. behavior corpus 按 distinct digest 保存一次，以 binding matrix 代替 18 份重复证据。
5. formal 与 implementation 分支/PR 分离；任何 formal 内容变化使双 Agent verdict 失效。
