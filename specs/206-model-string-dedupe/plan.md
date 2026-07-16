---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：Model String Dedupe Reduction

**编号**：`206-model-string-dedupe`
**日期**：2026-07-16
**规格**：`specs/206-model-string-dedupe/spec.md`
**当前阶段**：Phase 0 formal admission；未授权产品实现
**风险等级**：L1

## 1. 概述

以两个独立 PR 完成一个 WP-03 原子项：formal receipt 合入后，再从最新 main 新建 implementation
branch。实现只新增 `models/_string_lists.py`，让 18 个顶层 models helper 绑定一份原样算法，删除
216 行本地重复，不修改 validator、model、schema 或 100 个调用表达式。

结构 TDD 证明多个函数对象收敛为一个；一份 distinct-digest behavior/event corpus 证明语义；18-module
binding matrix、19-file targeted 和 full suite 证明所有消费者接入。证据不重复保存 18 份同义 corpus。

## 2. 技术背景

**语言/版本**：Python >=3.11；T61A 记录 exact Python/Pydantic 版本
**主要依赖**：现有 Pydantic；禁止新增依赖
**存储**：无新存储；现有 model serialization 保持
**测试**：pytest、AST/inspect、event corpus、mutation、tree-OID rollback、full CI
**目标平台**：Windows、macOS、Linux；项目命令按 PowerShell 语法给出
**硬约束**：1 私有文件、算法12 LOC、文件15 raw LOC、产品 +≤37/-≥216、source additions≤43

## 3. 宪章与治理检查

| 门禁 | 计划响应 |
|---|---|
| MVP / 原子范围 | 只处理 models 顶层一参数 string helper；dispatcher class validator 排除。 |
| 先规格后实现 | formal 双审和 mainline receipt 之前不修改 `src/ai_sdlc/`。 |
| TDD | 既有 test 中先加入三模块共享函数 identity assertion，baseline 精确 RED。 |
| 兼容性 | binding matrix、event corpus、19-file targeted、candidate full、required CI。 |
| 减重有效性 | 18→1、216→12、product net≤-179；wrapper/纯移动 No-Go。 |
| 400/50 | 新文件15 raw LOC、函数12 LOC；历史文件只减少。 |
| RC-06 | cap54，全部 source additions≤43，保留≥11。 |
| 回退 | exact baseline/candidate tree OID + targeted/corpus；full 不重复跑。 |
| 对抗评审 | formal 与 final tree 均由精简效率、兼容安全 Agent 同哈希复审。 |
| PR 协议 | push、Codex review、约5分钟 heartbeat、required checks、merge、fresh-main acceptance。 |

## 4. 文件结构

### 4.1 Formal 阶段

```text
specs/206-model-string-dedupe/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

另允许更新 manifest/project-state、root inventory 两行、canonical/scoped continuity 与 WI-196 路线索引。

### 4.2 Implementation 阶段

```text
src/ai_sdlc/models/
├── _string_lists.py                 # future annotations + 12 LOC algorithm
├── frontend_browser_gate.py         # import + 删除 local body
├── ...                              # spec §1 的其余 16 个 _dedupe_strings 模块
└── state.py                         # alias import + 删除 _dedupe_string_items body

tests/unit/test_program_models.py    # 最小 identity TDD RED
```

`models/__init__.py` 不修改；禁止 public re-export。

## 5. 阶段计划

### Phase 0：Formal admission

**目标**：冻结事实、CC/RC/T61、停止/回退，不授权产品代码。
**动作**：五件套、root truth、父路线；docs/constraints/truth；双 Agent 同哈希 review。
**完成**：formal PR 合入 main，merge commit 成为 implementation 唯一基线。
**停止**：事实不可复算、测试映射缺失、预算不成立或 reviewer 未共同 PASS。
**回退**：revert formal PR；产品行为未改变。

### Phase 1：T61A 与结构 TDD RED

**进入**：从 formal merge main 创建 `feature/206-model-string-dedupe-dev` 和独立 worktree。
**baseline**：记录 Python/Pydantic/OS、18 defs/100 calls、FunctionDef/inspect/binding、19-file targeted、
full suite、一个 distinct-digest event corpus、baseline tree OID。
**RED**：只修改既有 `test_program_models.py`，断言 `frontend_contracts._dedupe_strings is
program._dedupe_strings is state._dedupe_string_items`；baseline 因 identity 不同失败。
**停止**：baseline 不稳定、现有测试失败、corpus 事件不确定或 truth non-ready。

### Phase 2：最小产品减重

1. 新增 `_string_lists.py`：future annotations、两个空行、原样 12 LOC FunctionDef；
2. 17 个模块导入 `_dedupe_strings`；state 使用单行 alias import；
3. 删除 18 个 local body，保持 validators 和 100 calls 不动；
4. 运行 identity GREEN、binding/FunctionDef gate、19-file targeted。

**硬门禁**：body/full FunctionDef/signature/annotations 满足 spec；defs=1、imports=18、calls=100；产品
additions≤37、deletions≥216、net≤-179；新增上限含 4 条 Ruff `I001` 必需 import-block 分隔空行；
18 条 import 均位于标准顶层 first-party import block；不得使用 late/mid-file import、分号/多语句压行、
`# noqa`、`# ruff: noqa`、isort skip/off、修改 Ruff 配置或等价 suppression；无 wrapper、public export、
依赖或额外代码。
**停止/回退**：任一指标不满足，revert implementation commit，保留 legacy。

### Phase 3：T61B、mutation 与 rollback

**行为**：candidate distinct-digest corpus 与 baseline 的 result/exception/event trace 零差异；binding matrix
覆盖全部18模块；model schema/dump/error tests通过。
**mutation**：临时反转 shared helper 输出，既有 program order test RED；`apply_patch` 恢复 GREEN。
**candidate full**：targeted、root truth、full pytest、Ruff、constraints、validate/truth。
**rollback**：disposable clone revert 后 tree OID 等于 baseline；reapply 后等于 candidate；两侧重跑
19-file targeted+corpus，不重复 full。生成一个 differential+rollback receipt。

### Phase 4：Final review、PR 与 mainline

**本地评审**：两个 Agent 对同一 HEAD/tree/diff/receipt/formal hashes 复审；内容变化重审。
**PR**：push、ready PR、`@codex review`、heartbeat required checks；finding 修复后重新 review。
**合并后**：fresh main 重跑19-file targeted、root truth、full、结构/binding、truth audit。
**关闭**：只把 WI-206 标为 `completed_reduction`；RC-08 未满足前不发布。

## 6. 19-file targeted 与模块映射

| 产品模块 | 定向测试 |
|---|---|
| `frontend_browser_gate.py` | `test_frontend_browser_gate_runtime.py` |
| `frontend_contracts.py` | `test_frontend_contract_models.py` |
| `frontend_cross_provider_consistency.py` | `test_frontend_cross_provider_consistency_models.py` |
| `frontend_gate_policy.py` | `test_frontend_gate_policy_models.py` |
| `frontend_generation_constraints.py` | `test_frontend_generation_constraints.py` |
| `frontend_managed_delivery.py` | `test_managed_delivery_apply.py` |
| `frontend_page_ui_schema.py` | `test_frontend_page_ui_schema_models.py` |
| `frontend_provider_expansion.py` | `test_frontend_provider_expansion_models.py` |
| `frontend_provider_profile.py` | `test_frontend_provider_profile_models.py` |
| `frontend_provider_runtime_adapter.py` | `test_frontend_provider_runtime_adapter_models.py` |
| `frontend_quality_platform.py` | `test_frontend_quality_platform_models.py` |
| `frontend_solution_confirmation.py` | `test_frontend_solution_confirmation_models.py` |
| `frontend_theme_token_governance.py` | `test_frontend_theme_token_governance_models.py` |
| `frontend_ui_kernel.py` | `test_frontend_ui_kernel_models.py` |
| `host_runtime_plan.py` | `test_host_runtime_manager.py` |
| `program.py` | `test_program_models.py` |
| `scanner.py` | `test_scanners.py`、`test_p1_models.py` |
| `state.py` | `test_models.py`、`test_p1_models.py` |

PowerShell 命令使用上述 19 个唯一文件；基线为 `281 passed, 2 skipped`、10,537 raw / 9,646
non-empty LOC。实施时自动断言每个 §1 module 至少出现在映射表一次，测试路径存在且唯一列表为19。

## 7. 结构、签名与 binding ledger

- body serializer：`ast.dump(ast.Module(body=node.body, type_ignores=[]), include_attributes=False)`；
- full FunctionDef serializer：`ast.dump(node, include_attributes=False)`；
- signature contract：FunctionDef name/args/defaults/returns/decorators/type_comment + `Pass` body；
- runtime：`inspect.signature`、`__annotations__`、`__defaults__`、`__kwdefaults__`、`__doc__`、
  `__name__`、`__qualname__`、`__module__`、`__globals__` module name、source path，及
  `__code__` identity/filename/firstlineno/argcount/kwonlyargcount；
- calls：92 个 `_dedupe_strings` + 8 个 `_dedupe_string_items`；
- candidate imports：17 exact import + 1 state alias；binding identity 18/18；
- private-consumer scan：除 owning modules/tests 外不得存在旧 helper 的 cross-module import，或对
  `__globals__`/`__code__`/source/name 等私有 introspection 属性的消费者；
- raw ledger：固定19产品文件运行 `git diff --numstat <baseline> -- <paths>`。

批准差异只按 spec §5 的枚举 allowlist；其他 signature/annotation/default/doc/name/code-arity 漂移
fail-closed。

## 8. Behavior/event corpus v2

每个 distinct body digest 只保存一份 baseline/candidate receipt。输入 case 每次重新构造，记录事件数组、
result 或 fully-qualified exception type + message：

- `none`、`empty`、`repeat_order`、`mixed_str_collision`、`empty_whitespace`、`tuple`；
- `bare_string`：`"aba" -> ["a", "b"]`；
- `generator_success`；
- `iter_raises`；
- `next_raises_before_yield`；
- `next_raises_after_partial_yield`；
- `str_raises`；
- `hash_raises`：`__str__` 返回恶意 `str` subclass；
- `eq_raises`：两个同 hash 恶意 `str` subclass 在 membership 比较抛错。

事件至少包含 `iter`、每次 `next`、`str:<id>`、`hash:<id>`、`eq:<left>:<right>`，以证明部分处理后
异常的调用顺序。18-module digest/import/identity binding 表关联该唯一 corpus，不复制结果。

## 9. 最终门禁

```powershell
uv run pytest -q
uv run ruff check src/ai_sdlc/models tests/unit/test_program_models.py
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
git diff --check origin/main...HEAD
```

Program Truth 必须 `fresh + ready + exit 0 + zero blocker`，inventory mapped/total相等且 unmapped/missing=0。

## 10. 风险与处置

| 风险 | 处置 |
|---|---|
| 私有 import cycle | `_string_lists.py` 只含 future import 和函数；18-module import smoke。 |
| Pydantic validator 漂移 | decorator/call不改；19-file tests + event corpus + candidate full。 |
| signature/introspection 漂移 | full FunctionDef + inspect + binding gate；仅批准差异 allowlist。 |
| 首次出现顺序失守 | 既有 program order test 对 reverse mutation 必须 RED。 |
| 证据自身臃肿 | corpus按 distinct digest 一份；module binding表替代18份重复结果。 |
| 回退假等价 | exact tree OID + targeted/corpus 两侧；full baseline/candidate各一次。 |
| 路线误报 | WI-206只关闭一个T63 family；dispatcher和WI-196/RC-08保持open。 |

## 11. 实施顺序

1. 当前 formal target 同哈希双 PASS、truth、formal PR/merge。
2. 独立 implementation branch 完成 baseline、identity RED。
3. helper/import/local-body 删除，运行 GREEN 与 RC ledger。
4. event differential、mutation、tree-OID rollback、candidate full/governance。
5. final tree 双 PASS、Codex/CI、merge、fresh-main acceptance。
6. 回写 WI-196 并继续下一原子项；总体终态前不发布。
