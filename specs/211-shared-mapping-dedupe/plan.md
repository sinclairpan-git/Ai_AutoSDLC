---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 实施计划：共享 Mapping 去重重复族减重

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to implement this plan task-by-task. 本仓库额外要求 Pascal/Confucius 两个
> 对抗 reviewer 对同一 identity 均 PASS。

**编号**：`211-shared-mapping-dedupe`
**目标**：把 10 个 exact private mapping-dedupe body 收敛为现有 helper 模块中的一个实现，保持全部公共
行为并实测产品 raw 净删至少 100 行。
**架构**：沿用 `ai_sdlc.utils.helpers` 叶子依赖；目标模块只替换定义绑定，不修改 23 个调用。通过 T61A
行为语料、identity TDD、T61B rollback/reapply、全量/跨平台/PR 证据证明等价。
**技术栈**：Python 3.11+、标准库 `json`、pytest、Ruff、uv、Git/GitHub Actions。
**风险**：L1 实现 / L2 证明面；无公共 API 变化。
**当前阶段**：closure；implementation PR #153 已合并并通过 detached fresh-main acceptance。

## 全局约束

- 候选选择基线为 `236cd00e8f2e9514487d237b47d4cbbf6fb5fe91`；formal amendment 合并后，implementation
  精确 base 为 `96908f2c207dd8e03411d8acd489b2101a5787cf`。
- formal、implementation、closure 使用三个独立 branch/worktree/PR；implementation 没有从未合并 formal 分支派生。
- 只修改 spec §2.1 的 10 个模块、`utils/helpers.py` 与一个既有 unit test；产品/测试均不新增文件。
- 新增注释仅在解释非显然边界时使用简体中文；本项 exact helper 无需复述式注释。
- 23 个调用表达式、CLI、artifact、schema、状态、授权和平台行为零未批准差异。
- 除10个目标 alias imports 与23 calls外，`src/` product/runtime external private consumers=0；tracked identity
  test 精确允许2次 private attribute reads；§3.3 disposable harness 每次进程允许1次代表binding lookup并运行
  4-case。其他 import/attribute/wildcard/monkeypatch/introspection 消费均禁止。
- 产品 raw/non-empty additions≤25/23；representative identity test=4 non-empty；formal executable harness=27
  non-empty；保护成本31=`floor(127×25%)`，总 proof/product raw additions≤58、hard cap=60；truth test仅两行等量机械替换。
- GAP-09～GAP-11 impact analysis 缺失、不确定或 truth 漂移时 fail-closed。
- 任何 formal/implementation review target 内容变化同时作废 Pascal/Confucius 两份 PASS。

---

## 1. 文件职责与边界

### Formal PR

- `specs/211-shared-mapping-dedupe/{spec,plan,tasks,task-execution-log}.md`：唯一 child 合同与证据日志。
- `specs/196-ai-sdlc-lean-code-self-reduction-governance/{spec,plan,tasks,task-execution-log,development-summary}.md`：
  父路线只登记 active child，不提前计入减重收益。
- `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、root/scoped handoff/truth：canonical source。
- `tests/integration/test_repo_program_manifest.py`：只允许已有 inventory/close expectation 的机械值替换。

### Implementation PR

- `src/ai_sdlc/utils/helpers.py`：唯一 exact `_dedupe_mapping_items` body；只新增标准库 `json` import。
- spec §2.1 的 10 个模块：同名 alias import，删除 local body；7 个模块删除失活 `json` import。
- `tests/unit/test_frontend_contract_observation_provider.py`：唯一新增 identity characterization；既有测试不删改。
- `.ai-sdlc/work-items/211-shared-mapping-dedupe/t61-differential-rollback-receipt.json`：唯一 proof receipt。
- implementation 后的 evidence commit chain 只允许 receipt、强制 root/scoped handoff 与必要的机械
  truth/manifest；`implementation_commit` 后产品和行为测试零变化。

### Closure PR

- child/parent docs、manifest/truth、handoff 与 manifest exact expectations：只物化 close source 和最终 ledger；
  产品代码零修改。

## 2. Phase 0：Formal 冻结与交付

1. 从 exact `origin/main@236cd00e8f2e9514487d237b47d4cbbf6fb5fe91` 创建
   `feature/211-shared-mapping-dedupe-docs`。
2. 运行 canonical `uv run ai-sdlc workitem init`，恢复其非范围 Cursor/continuity 副作用。
3. 冻结 child 与 parent formal 六文件、候选清单、CC/RC、T61A/B、停止/回退及分支边界。
4. 计算父 plan §9 canonical combined identity；Pascal 与 Confucius 独立评审同一 identity。
5. 修复成立 finding 后重新计算 identity，并让双方从零复审，直到双 PASS/findings=none。
6. 运行 constraints、validate、truth、manifest exact、diff-check、受保护路径与 handoff parity。
7. push formal branch，创建 PR，`@codex review`，heartbeat required checks；全绿后合并并做 detached fresh-main 验收。

formal PR 不得含 `src/ai_sdlc/**` 或 implementation test diff。

## 3. Phase 1：T61A 与 TDD RED

### 3.1 从 formal merge 创建实现工作树

使用 exact fresh `origin/main` 创建 `feature/211-shared-mapping-dedupe`。记录 HEAD/tree、Python/OS/uv、
10 defs、23 calls、body/full/call digest、72 importers、授权目标边界之外的 product/runtime consumers=0、
tracked identity attribute reads=0、disposable harness binding lookup=1/进程、目标文件和受保护文件 blob。
Python 3.11 的结构 digest 必须逐字采用 spec §2.1 的 AST payload recipe；其中 call nodes 必须同时满足
`isinstance(node, ast.Call)`、`isinstance(node.func, ast.Name)` 与
`node.func.id == "_dedupe_mapping_items"`。先核对 body/full/call 分别为 `6602b868...`、`6fb4192d...`、
`a62a6dee...`，再捕获实现 base；Python 3.12 因 `FunctionDef.type_params` 不复用 3.11 full digest，只做
同解释器 baseline/candidate AST payload 相等和 10→1/23 calls 结构断言；不得用 grep 文本替代。

consumer scan 只按本 family 的精确模块所有权计数：10个目标模块从 `utils.helpers` 的同名 alias import 是授权
边界；其外任一 `src/` 对 helper/目标模块 private symbol 的 import、attribute、wildcard 或 monkeypatch string
均计为 product/runtime external consumer。tracked proof 只在 §3.2 exact test FunctionDef 中计
`_dedupe_mapping_items` 的 `ast.Attribute` loads，baseline/revert=0、candidate/reapply=2；§3.3 marker block 的
representative binding lookup 单独计1/进程。仓库中 telemetry 等其他所有权下的同名函数不计入本 family。

### 3.2 写唯一 failing test

在 `tests/unit/test_frontend_contract_observation_provider.py` 增加：

```python
import ai_sdlc.core.frontend_contract_observation_provider as observation_provider
import ai_sdlc.generators.frontend_theme_token_governance_artifacts as theme_artifacts

def test_mapping_item_dedupe_uses_one_shared_binding() -> None:
    assert observation_provider._dedupe_mapping_items is theme_artifacts._dedupe_mapping_items
```

在现有 import 区增加 `observation_provider` 与 `theme_artifacts` 两个 module alias，共4 non-empty LOC。断言左右
各产生一次 private attribute read，合计2次且只比较 identity；这是唯一批准的 tracked proof consumer。运行该 exact
nodeid，期望 baseline 只因两个对象不同而失败；candidate 的 AST/identity gate 另行断言全部10 个 alias 指向
`utils.helpers`。import/collection/fixture error 不算 RED。

### 3.3 捕获行为与导入基线

以下27 non-empty LOC 的 `wi211-t61-corpus-v1` 是唯一 executable harness。10 个 baseline body 的 AST
完全相同、candidate 10 个 alias identity 相同，因此只对每个 unique implementation 执行一次4-case corpus；
模块级覆盖由103/104 direct、1162/1163 impact 与72 imports承担。每个 case 通过 `cases[name]()` 调用对应
factory 新建对象，每条
observation 规范化为 compact、sorted-key、UTF-8 JSONL；return outcome 另存每个结果 dict 的 key 顺序，
避免外层 `sort_keys=True` 掩盖 first-wins/key-order 回归。baseline/candidate/revert/reapply 先做同环境字节
比较再比较 SHA-256；JSONL 只存 disposable evidence，最终 receipt 登记其 hash/计数/环境，不复制 cases。

<!-- wi211-t61-corpus-v1:start -->
```python
import importlib, json, unittest.mock
def _values(truth, items, events):
    values = unittest.mock.MagicMock()
    values.__bool__.side_effect = lambda: events.append(f"bool:{truth}") or truth
    values.__iter__.side_effect = lambda: events.append("iter") or iter(items)
    return values
def _observe(binding, name):
    events, nested = [], []
    cases = {
        "falsy": lambda: _values(False, [{"never": 1}], events),
        "events_filter_first": lambda: _values(True, [0, {"b": "值", "a": 1}, {"a": 1, "b": "值"}, None], events),
        "json_error": lambda: [{"bad": {1}}],
        "subclass_shallow": lambda: [type("Item", (dict,), {})(nested=nested)],
    }
    values = cases[name]()
    try:
        result = binding(values)
        outcome = {"kind": "return", "keys": [list(item) for item in result], "value": result}
    except Exception as exc:
        outcome = {"kind": "raise", "type": type(exc).__name__, "message": str(exc)}
    if name == "subclass_shallow":
        item = outcome["value"][0]
        outcome["probe"] = [type(item) is dict, item is not values[0], item["nested"] is nested]
    return {"case": name, "events": events, "outcome": outcome}
binding = importlib.import_module("ai_sdlc.core.frontend_contract_observation_provider")._dedupe_mapping_items
rows = [_observe(binding, name) for name in ("falsy", "events_filter_first", "json_error", "subclass_shallow")]
print("".join(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n" for row in rows), end="")
```
<!-- wi211-t61-corpus-v1:end -->

- 当前 Python 3.11 formal baseline/candidate 必须各输出4 observations、digest=
  `8c6d3e21ef597673c767e39a3919864242daed6014d13b1400a95eafabdb54e0`；其他运行时不复用该摘要，
  只要求 candidate/revert/reapply 与同解释器 baseline JSONL 逐字节相等；
- 跑 103 direct tests 与 23-file/1162-test 影响切片 baseline；
- 对 `rg -l 'from ai_sdlc\.utils\.helpers import' src/ai_sdlc` 得到的 72 模块逐个 cold import，要求
  failures/noisy 均为空；
- baseline JSONL/字段先保存在 disposable evidence；implementation commit 前不得创建 repo receipt。

## 4. Phase 2：最小 GREEN

### 4.1 唯一共享实现

在 `src/ai_sdlc/utils/helpers.py` 增加标准库 `json` import 与 exact body：

```python
def _dedupe_mapping_items(values: object) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return deduped
```

### 4.2 十个 local alias

每个目标模块只增加：

```python
from ai_sdlc.utils.helpers import _dedupe_mapping_items as _dedupe_mapping_items
```

删除对应 local FunctionDef；仅在 spec 表中标记“是”的 7 个模块删除 `import json`。另外 3 个模块继续
保留其其他 JSON 使用。不得修改 23 个调用表达式。

### 4.3 GREEN 与预算

1. 运行 identity nodeid，期望 PASS。
2. 运行 Ruff changed paths、`git diff --check`。
3. 复算结构：目标 exact body=1、10 alias binding、23 calls、call digest不变、授权目标边界之外的 `src/`
   product/runtime external consumers=0、唯一 tracked identity attribute reads=2；disposable harness另按§3.3保持
   binding lookup=1/进程。
4. 复算 diff：目标 raw additions≤25/deletions≥147、non-empty additions≤23/deletions≥127；
   超限立即停止，不靠删测试抵消。
5. 提交只含产品与 identity test 的 `implementation_commit/tree`；该提交可独立 revert，之后不得改写产品。

## 5. Phase 3：T61B、回退与验证

1. 在 `implementation_tree` 上逐字执行 §3.3 recipe；当前 Python 3.11 期望4 observations、digest=
   `8c6d3e21ef597673c767e39a3919864242daed6014d13b1400a95eafabdb54e0`，且 JSONL 与 baseline 字节相等。
2. 重跑consumer scan（product/runtime=0、tracked=2、harness=1/进程）、104 direct、23-file/1163 impact、
   72 cold imports、full pytest、Ruff、constraints、validate、truth。
3. 在 disposable clone checkout `implementation_commit` 后 revert 它：tree OID=baseline；重跑结构、consumer
   scan product-runtime/tracked/harness=`0/0/1`、4-case diff、103 direct、1162 impact、72 imports。
4. reapply 同一 commit：tree OID=`implementation_tree`；重跑consumer scan
   product-runtime/tracked/harness=`0/2/1`、4-case、104 direct、
   1163 impact、72 imports。
5. 回到主实现 worktree，新建唯一 receipt，只绑定 baseline、`implementation_commit/tree`、revert/reapply、
   授权目标边界之外的 product/runtime consumers=0、tracked identity attribute reads baseline/revert=0 与
   candidate/reapply=2、disposable harness binding lookup=1/进程、证据；
   evidence commit chain 同步 receipt、AGENTS.md 强制的 root/scoped handoff 及必要机械 truth/manifest，最终
   clean tip 为 `evidence_review_head/tree`。receipt 禁止写入自身所在 evidence commit/tree/hash；review
   envelope 单独绑定 receipt、root/scoped handoff 与 truth/manifest blobs。该 chain 禁止产品或行为测试变化。
6. 验证 GAP-09 capability/inheritance/admission、GAP-10 adapter consumption/CLI、GAP-11 inventory/truth 零漂移。
7. 对 exact `implementation_commit/tree` + `evidence_review_head/tree` + diff/formal-six/receipt blob/truth identity
   让 Pascal/Confucius 双审。
8. finding 成立则最小修复并全部重审；双 PASS 后才 push/PR。
9. Codex current-head 无 actionable findings且 required checks 全绿后 merge；detached fresh-main 重跑
   targeted/full/Ruff/constraints/validate/truth/manifest/clean guard。

## 6. Phase 4：Closure

从 implementation merge exact main 创建 `codex/211-shared-mapping-dedupe-closure`，只登记
`completed_reduction`、最终产品 ledger 和 close source。先让 Pascal/Confucius 审同一 closure identity，
再按 Codex/check/merge/fresh-main 流程交付。closure 不修改产品或行为测试，不关闭父路线或发布版本。

## 7. 验证矩阵

| 路径 | 必须证明 | 命令/证据 |
|---|---|---|
| identity RED/GREEN | 10 distinct→1 shared；module=`utils.helpers`；tracked attribute reads=2 | exact unit nodeid |
| mapping 语义 | unique implementation 的 truthiness/事件+过滤/首次+显式key-order probe/Unicode、JSON异常、浅复制 | 4-case JSONL differential |
| 直接行为 | 10 target test files 场景不减 | baseline/revert 103；candidate/reapply 104 |
| 影响行为 | observation/verification/artifact/CLI/Program | 固定23 files；baseline/revert 1162；candidate/reapply 1163 |
| 共享叶子 import | 全部 72 importer 无失败/输出 | cold-import receipt |
| 结构/预算 | 10→1、23 calls不变、授权边界外 product/runtime consumers=0、tracked reads当前阶段=0/2、harness lookup=1/进程、net达到阈值 | AST + consumer scan + numstat + non-empty counter |
| 回退 | baseline/implementation tree 精确恢复；evidence identity不自引用 | disposable clone + receipt blob |
| 治理 | GAP-09～11、truth、source inventory | constraints/validate/truth/manifest |
| 平台 | Python 3.11/3.12、macOS/Linux/Windows | required GitHub checks |

## 8. 自审

- 规格覆盖：FR-211-001～010 均映射到 Phase 1～4 和 tasks T11～T43。
- 模板占位词扫描为零，且不得伪造未来结果。
- 类型一致：唯一 helper 签名固定为 `object -> list[dict[str, object]]`；所有 target alias 同名。
- 范围：一个 T63 family；不把 T65/T66/T67、T62A、release 或父 closure 混入。

## 9. 精确测试清单

以下 PowerShell 数组是 baseline/candidate/revert/reapply 共用的固定 test surface：

```powershell
$directTests = @(
  'tests/unit/test_frontend_contract_observation_provider.py'
  'tests/unit/test_frontend_contract_runtime_attachment.py'
  'tests/unit/test_frontend_contract_verification.py'
  'tests/unit/test_frontend_gate_verification.py'
  'tests/unit/test_frontend_visual_a11y_evidence_provider.py'
  'tests/unit/test_frontend_cross_provider_consistency_artifacts.py'
  'tests/unit/test_frontend_provider_expansion_artifacts.py'
  'tests/unit/test_frontend_provider_runtime_adapter_artifacts.py'
  'tests/unit/test_frontend_quality_platform_artifacts.py'
  'tests/unit/test_frontend_theme_token_governance_artifacts.py'
)
uv run pytest @directTests -q
```

direct baseline 未增加 identity test 时为 103；candidate 增加唯一 test 后精确为 104。为避免把 spike 的
103 误写成实现终态，本计划后续所有 candidate/reapply acceptance 均要求 104；revert 回 baseline 时为 103。

```powershell
$impactTests = @(
  'tests/integration/test_cli_index_gate.py'
  'tests/integration/test_cli_program.py'
  'tests/integration/test_cli_run.py'
  'tests/integration/test_cli_scan.py'
  'tests/integration/test_cli_verify_constraints.py'
  'tests/unit/test_frontend_browser_gate_runtime.py'
  'tests/unit/test_frontend_contract_gate.py'
  'tests/unit/test_frontend_contract_observation_provider.py'
  'tests/unit/test_frontend_contract_runtime_attachment.py'
  'tests/unit/test_frontend_contract_scanner.py'
  'tests/unit/test_frontend_contract_verification.py'
  'tests/unit/test_frontend_cross_provider_consistency_artifacts.py'
  'tests/unit/test_frontend_gate_verification.py'
  'tests/unit/test_frontend_provider_expansion_artifacts.py'
  'tests/unit/test_frontend_provider_runtime_adapter_artifacts.py'
  'tests/unit/test_frontend_quality_platform_artifacts.py'
  'tests/unit/test_frontend_theme_token_governance_artifacts.py'
  'tests/unit/test_frontend_visual_a11y_evidence_provider.py'
  'tests/unit/test_gates.py'
  'tests/unit/test_program_service.py'
  'tests/unit/test_run_cmd.py'
  'tests/unit/test_runner_confirm.py'
  'tests/unit/test_verify_constraints.py'
)
uv run pytest @impactTests -q
```

impact baseline 为 1162；candidate/reapply 增加唯一 identity test 后精确为 1163；revert 为 1162。
