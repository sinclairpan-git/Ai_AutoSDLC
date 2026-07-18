# 功能规格：共享 Mapping 去重重复族减重

**功能编号**：`211-shared-mapping-dedupe`
**创建日期**：2026-07-18
**状态**：formal review candidate；实现尚未授权
**父项**：WI-196 `T63 / WP-03 / GAP-05`
**基线 revision**：`236cd00e8f2e9514487d237b47d4cbbf6fb5fe91`

## 1. 决策摘要

当前 `main` 存在一个完全同形的私有 mapping 去重函数族：10 个顶层
`_dedupe_mapping_items(values: object) -> list[dict[str, object]]`、10 个模块、120 行产品代码、
23 个直接调用。10 个函数的完整 AST body digest 均为
`6602b8688426cf7ae803c793f9b86a3c3f6759abde0a638ab5953bdf1b58f200`，完整 FunctionDef digest
均为 `6fb4192df6b37d095c3aedf17ac60046f05d3dfc43f3ed38a26f8e4170018929`。

本项只在现有 `src/ai_sdlc/utils/helpers.py` 中保留一份 exact body，并让 10 个目标模块以同名 private
alias 复用。10 个模块已经依赖该 helper 模块，因此不新增模块依赖方向；23 个调用表达式、参数、返回值、
异常、artifact、CLI、状态与授权边界全部保持。一次性隔离 spike 实测产品 raw `+25/-147/net -122`、
non-empty `+23/-127/net -104`，直接测试 `103 passed`，23 文件影响切片 `1162 passed`，72 个现有
`utils.helpers` importer 的 baseline/candidate cold import 均无失败或输出。

Pascal 从精简/YAGNI 维度、Confucius 从兼容/证明/回退维度独立复算后，均只推荐该 family。14-module
exact-text、11-module `_write_yaml`、T65、T66 与 T67 当前均不进入本项；T62A 仍因无 sponsor 禁止恢复。

## 2. 冻结范围

### 2.1 十个目标定义与调用数

| 模块 | 基线行 | 调用数 | 删除本地 `json` import |
|---|---:|---:|---|
| `core/frontend_contract_observation_provider.py` | 19～30 | 3 | 否 |
| `core/frontend_contract_runtime_attachment.py` | 42～53 | 2 | 是 |
| `core/frontend_contract_verification.py` | 37～48 | 1 | 是 |
| `core/frontend_gate_verification.py` | 59～70 | 1 | 是 |
| `core/frontend_visual_a11y_evidence_provider.py` | 24～35 | 3 | 否 |
| `generators/frontend_cross_provider_consistency_artifacts.py` | 25～36 | 4 | 是 |
| `generators/frontend_provider_expansion_artifacts.py` | 25～36 | 2 | 是 |
| `generators/frontend_provider_runtime_adapter_artifacts.py` | 22～33 | 1 | 是 |
| `generators/frontend_quality_platform_artifacts.py` | 24～35 | 4 | 是 |
| `generators/frontend_theme_token_governance_artifacts.py` | 20～31 | 2 | 否 |

完整目标调用 AST digest 为
`a62a6dee4a25647d5088f92912cb1bd063db624a5ff6ee4a6aa4768918789af8`。目标模块总计
4551 raw / 4094 non-empty LOC；共享承载模块基线为 105 raw / 75 non-empty LOC，已有 72 个产品
importer。仓库中其他同名 helper 的类型和语义不同，不属于本 family。

三个冻结 AST digest 只以 Python 3.11 的 `ast.parse` 和 UTF-8 source 复算：full payload 为目标顶层
`FunctionDef` 的 `ast.dump(..., annotate_fields=True, include_attributes=False)`；body payload 为把该
`FunctionDef.body` 放入 `ast.Module(body=..., type_ignores=[])` 后的同参数 dump；call payload 为 10 个
按 repo-relative path 排序的模块中 23 个目标 `ast.Call` dump 再按字符串排序，每条追加一个 `\n` 后连接。
payload 均以 UTF-8 做 SHA-256；不得把行号、文件位置或格式化空白放入 digest。Python 3.12 的
`FunctionDef.type_params` 会改变 full dump，因此3.12只要求同解释器 baseline/candidate payload 相等及
10→1/23 calls 结构断言，不得拿3.11固定 full digest 做跨版本比较。

### 2.2 冻结运行语义

共享函数必须逐语义保持当前 exact body：

1. 先求值 `values or []`，保留 truthiness、迭代及异常时序；
2. 只接受实际 `dict`；其他对象直接跳过，不扩展到任意 `Mapping`；
3. 使用 `json.dumps(value, sort_keys=True, ensure_ascii=False)` 生成唯一键；
4. 用 `set[str]` 记录已见键，保留首次出现顺序；
5. 用 `dict(value)` 返回新的浅复制，嵌套对象 identity 不变；
6. JSON 编码、混合 key 排序、循环引用、truthiness、迭代或浅复制异常原样传播；
7. 不读写文件、环境、网络、subprocess、checkpoint、adapter 或 program truth。

### 2.3 唯一允许的私有可观察差异

- 10 个模块局部 callable 从 10 个对象收敛为同一个 imported private object，因而 `id`、`__module__`、
  `__code__`、`__globals__`、源码位置和 traceback frame 统一到 `ai_sdlc.utils.helpers`；
- 所有只由上述 identity/code/globals/source-owner 派生的 private introspection/serialization 视图随之变化，
  包括 callable/`__annotations__`/`__dict__` 的对象 identity、`inspect.getmodule`、`inspect.getfile`、
  `inspect.getsourcefile`、`inspect.getsourcelines`、`inspect.getsource` 结果，以及 pickle 的 module target 与
  serialized bytes；
- 7 个仅供本地 helper 使用的模块级 `json` binding 被删除；另外 3 个模块因其他 JSON 行为继续保留；
- `utils.helpers` 新增内部标准库 `json` binding。

这些差异只允许作用于未被外部消费的 private introspection/serialization surface；它们不是公共兼容承诺，
也不得被新代码消费。`__name__`、`__qualname__`、签名、annotation 值、doc 值及调用语义仍须相等。已验证
外部 private import、attribute consumer、wildcard consumer 与 monkeypatch consumer 均为 0。不得借此批准
结果、异常 type/message、事件顺序、业务 artifact 字节、schema、CLI transcript 或状态真值差异。

### 2.4 明确排除

- 不修改 23 个调用表达式，不把函数改为泛型、公共 API、protocol、class、registry 或 framework；
- 不合并其他 `_dedupe_mapping_items` 变体、text/path/model 去重或 `_write_yaml`；
- 不修改 `program_service.py`、`program_cmd.py`、adapter、resume-pack、Lean Gate、baseline builder；
- 不新增产品模块、测试文件、fixture、schema、loader、配置、flag 或公共 re-export；
- 不减少测试场景、断言、平台和错误路径；不顺带格式化无关文件；
- 不关闭 GAP-05、WI-196、RC-08，不恢复 WI-204/T62A，不发布版本。

## 3. 用户故事与验收场景

### US-1：行为无损地删除重复实现（P0）

作为框架使用者，我希望 observation、verification 与 frontend artifact 产物在减重前后完全一致，以便升级
框架时无需承担功能回归。

1. **Given** 10 个基线 body 完全相同且 candidate 10 个 alias identity 相同，**When** 对每个 unique
   implementation 运行6类代表输入，**Then** candidate、revert、reapply 的同环境 JSONL 与 baseline 字节相等。
2. **Given** falsy/true iterable、非 dict/重复项、key order/Unicode、JSON失败与 dict subclass，**When**
   执行 canonical harness，**Then** 结果、异常 type/message、事件顺序、top-level copy 与 nested identity 不变；
   模块级场景由固定 direct/impact tests 覆盖。

### US-2：真实减重而非搬家（P0）

作为框架维护者，我希望重复函数只保留一个 exact body，不引入第二套抽象成本。

1. **Given** 冻结的 10 个定义与 23 个调用，**When** 实现完成，**Then** exact body 为 1、局部 alias 为
   10、调用 AST digest 不变，产品 raw 净减少至少 100 行、non-empty 净减少至少 90 行。
2. **Given** 现有 `utils.helpers` 依赖边，**When** 新 helper 落地，**Then** 不新增产品文件、公共导出、
   wrapper、配置或模块 SCC，7 个失活 `json` import 被删除。

### US-3：可证明、可回退、可发布（P0）

作为发布维护者，我希望候选可在隔离环境精确回退并重放，以控制精简引发的 bug 风险。

1. **Given** 独立 `implementation_commit/tree`，**When** 在 disposable clone revert implementation commit，
   **Then** tree OID 精确等于 baseline，结构、6-case JSONL、direct tests 与 cold imports 全部通过。
2. **Given** revert 状态，**When** reapply implementation commit，**Then** tree OID 精确恢复
   `implementation_tree`；只含 receipt 的后续提交形成不同的 `evidence_review_head/tree`，不允许 receipt
   自绑定，随后 full、跨平台 CI、Codex 与 fresh-main acceptance 全绿。

## 4. Differential 与 TDD 合同

### 4.1 T61A baseline

- `plan.md` §3.3 的24 non-empty LOC `wi211-t61-corpus-v1` 是唯一 canonical factory、事件与 JSONL
  normalizer；只对每个 unique implementation 执行 `falsy`、`events`、`filter_first`、`key_unicode`、
  `json_error`、`subclass_shallow` 六类 fresh case；
- 当前 Python 3.11 formal baseline/candidate 均为6 observations、digest=
  `bf4a6deebf6ad5ce83f3147ec02fab29e7b7bab4fca280480016d7abac72980e`；跨 Python/OS 不固定摘要，只要求
  同解释器 baseline/candidate/revert/reapply JSONL 字节完全一致；历史 14×10 spike digest 不再承担 admission；
- 10 个 direct test files 精确为 103 tests；23 个影响测试文件在 candidate spike 为 1162 tests；
- 72 个现有 `utils.helpers` importer 必须全部 cold import，failure=0、stdout/stderr=0；
- baseline revision、Python、OS、toolchain、body/full/call digest、private consumer 与 protected blobs 写入唯一 receipt。

### 4.2 TDD RED/GREEN

只在现有 `tests/unit/test_frontend_contract_observation_provider.py` 增加一个 binding identity test，连同
`importlib` 最多12 non-empty LOC。
RED 必须是 10 个 local function 对象不相同；不得以 import、collection 或 fixture 错误代替。GREEN 只允许：

1. `utils/helpers.py` 增加 exact body；
2. 10 个目标模块增加同名 private alias import 并删除本地 body；
3. 删除 7 个失活 `json` import；
4. 不修改任何目标调用表达式或既有测试场景。

### 4.3 T61B implementation / rollback / evidence review

唯一结构化回执：
`.ai-sdlc/work-items/211-shared-mapping-dedupe/t61-differential-rollback-receipt.json`。它只绑定 baseline、
`implementation_commit/tree`、revert/reapply、6-case JSONL、结构/调用 digest、72 cold imports、product/test
LOC 与受保护文件 hash；baseline/revert 测试数为 direct 103 / impact 1162，implementation/reapply 为
104 / 1163。随后只含 receipt 的 evidence commit 形成 `evidence_review_head/tree`；receipt 禁止包含自身所在
commit/tree/hash，review envelope 另行绑定 receipt blob SHA-256。receipt 不构成第二套 schema 或产品能力。

## 5. GAP-09～GAP-11 防回归影响分析

| 已关闭 GAP | 本项影响 | fail-closed admission |
|---|---|---|
| GAP-09 frontend inheritance | 目标覆盖 observation/verification 与 frontend artifacts，但不改变 capability、inheritance 或 admission | blocking refs、codegen/test admission、artifact/schema 任一漂移即停止并重开 |
| GAP-10 adapter consumption | 仅 runtime-adapter artifact helper 被复用；adapter/Program/CLI 调用集合为零 diff | canonical consumption、adapter capability、CLI transcript 任一漂移即停止并重开 |
| GAP-11 source inventory | 实现新增 source=0；formal 的唯一 expected missing 是 mapped/`exists=false` 的本 child `development-summary.md`，close=211/210；closure 必须归零为211/211 | 任一 unmapped、第二个 missing、其他 missing type/path/layer、source 集合或 truth state 未解释漂移即停止并重开 |

## 6. Reduction Contract

| 合同 | 冻结值 |
|---|---|
| RC-01 | 10 exact defs、120 raw/non-empty family LOC、23 calls、0 private external consumers |
| RC-02 | base `236cd00e`；10 target modules=4551/4094；helper=105/75；body/full/call digest 如 §1/§2 |
| RC-03 | CC-01/02/03/05/06/07 预期零公共差异；§2.3 private introspection 为唯一 expected delta |
| RC-04 | exact body 10→1；family duplicate LOC 120→12；raw net≤-100；non-empty net≤-90 |
| RC-05 | 无 staged dual runtime；candidate 单提交可完整 revert/reapply |
| RC-06 | 产品 raw/non-empty additions≤25/23；identity test含import≤12 non-empty；formal harness=24；保护成本36=`floor(147×25%)`；总 raw additions≤61、hard cap61；truth test两行等量替换；0 fixture/新测试文件 |
| RC-07 | helper 模块 candidate≤125 raw、≤90 non-empty；其他目标函数大小不增长；0 新产品文件 |
| RC-08 | 只登记一个 completed_reduction family；不声称路线 10%、两个大文件≤400 或发布完成 |
| RC-09 | 任一语义差异、预算超限、外部 private consumer、新 dependency cycle 或 proof 成本超预算立即 No-Go |
| RC-10 | before/after、TDD、6-case JSONL、103→104 direct、1162→1163 impact、72 imports、implementation/evidence 双身份、rollback/reapply、full/platform/fresh-main |

## 7. 功能需求

- **FR-211-001**：系统必须只保留一份本 family exact body，并由 10 个模块以 local private alias 复用。
- **FR-211-002**：23 个调用表达式及 call AST digest 必须保持不变。
- **FR-211-003**：§2.2 结果、异常和事件语义必须零未批准差异。
- **FR-211-004**：只允许 §2.3 私有 introspection/import delta；任何公共 delta 均为 blocker。
- **FR-211-005**：实现必须先有 identity RED，再做最小 GREEN；不得新增产品/测试文件。
- **FR-211-006**：baseline/revert 必须通过6-case JSONL、103 direct、1162 impact 与72 cold imports；
  implementation/reapply 必须通过同一行为集加唯一 identity test，即104 direct、1163 impact，并通过full suite。
- **FR-211-007**：rollback/reapply 必须绑定 `implementation_commit/tree`；receipt 由独立
  `evidence_review_head/tree` 携带并禁止自绑定，双 Agent 同时审查两组 identity。
- **FR-211-008**：GAP-09～GAP-11 impact admission 必须 fail-closed，不得复活或伪关闭历史项。
- **FR-211-009**：formal、implementation、closure 必须使用独立 branch/worktree/PR；formal merge/fresh
  acceptance 前不得创建 implementation branch。
- **FR-211-010**：父子 formal 六文件任一变化使两位 Agent PASS 同时失效；实现内容变化同样使实现 PASS 失效。

## 8. 成功标准与停止条件

- **SC-211-001**：formal 六文件同一 canonical combined identity 获 Pascal/Confucius 双 PASS、findings=none。
- **SC-211-002**：产品 raw additions≤25/deletions≥147、non-empty additions≤23/deletions≥127，
  净值分别≤-100/-90；10→1 body、
  10 aliases、23 calls、0 private consumer、0 新模块/公共抽象。
- **SC-211-003**：TDD RED 根因精确；implementation 为6-case JSONL、104 direct、1163 impact、72 cold imports、full、
  Ruff、constraints、validate、truth 全绿。
- **SC-211-004**：rollback tree=baseline，reapply tree=`implementation_tree`；evidence review identity携带精确
  receipt blob，receipt 不包含自身 commit/tree/hash。
- **SC-211-005**：Codex current-head 无 actionable findings，macOS/Linux/Windows Python 3.11/3.12 与 required
  checks 全绿；fresh `origin/main` 重跑 targeted/full/truth 且 Git clean。
- **SC-211-006**：closure 只登记本 family；GAP-05、WI-196、RC-08 与 release 保持 open。

任一行为、artifact、schema、CLI、状态、授权、平台差异，任一新增 dependency cycle/private consumer，或
任一预算/测试/回退门禁失败，立即停止本 candidate；按独立 implementation commit revert，不扩大为相邻 family。
