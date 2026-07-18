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

## 全局约束

- 基线必须是 formal PR 合并并完成 fresh-main acceptance 后的精确 `origin/main`；当前选择基线为
  `236cd00e8f2e9514487d237b47d4cbbf6fb5fe91`，实现 base 将在 formal merge 后重新冻结。
- formal、implementation、closure 分三个独立 branch/worktree/PR；implementation 不从未合并 formal 分支派生。
- 只修改 spec §2.1 的 10 个模块、`utils/helpers.py` 与一个既有 unit test；产品/测试均不新增文件。
- 新增注释仅在解释非显然边界时使用简体中文；本项 exact helper 无需复述式注释。
- 23 个调用表达式、CLI、artifact、schema、状态、授权和平台行为零未批准差异。
- 产品 non-empty additions≤23，test additions≤20，truth test机械 additions≤2，合计≤45、hard cap=49。
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
10 defs、23 calls、body/full/call digest、72 importers、private consumers、目标文件和受保护文件 blob。

### 3.2 写唯一 failing test

在 `tests/unit/test_frontend_contract_observation_provider.py` 增加：

```python
def test_mapping_item_dedupe_uses_one_shared_binding() -> None:
    module_names = (
        "ai_sdlc.core.frontend_contract_observation_provider",
        "ai_sdlc.core.frontend_contract_runtime_attachment",
        "ai_sdlc.core.frontend_contract_verification",
        "ai_sdlc.core.frontend_gate_verification",
        "ai_sdlc.core.frontend_visual_a11y_evidence_provider",
        "ai_sdlc.generators.frontend_cross_provider_consistency_artifacts",
        "ai_sdlc.generators.frontend_provider_expansion_artifacts",
        "ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts",
        "ai_sdlc.generators.frontend_quality_platform_artifacts",
        "ai_sdlc.generators.frontend_theme_token_governance_artifacts",
    )
    bindings = [
        importlib.import_module(name)._dedupe_mapping_items for name in module_names
    ]
    assert len({id(binding) for binding in bindings}) == 1
    assert bindings[0].__module__ == "ai_sdlc.utils.helpers"
```

若现有文件尚未导入 `importlib`，增加一个标准库 import。运行该 exact nodeid，期望 baseline 因
`len(ids)==10` 失败；import/collection/fixture error 不算 RED。

### 3.3 捕获行为与导入基线

- 对 spec §4 的 14 个 case factory 逐 binding 创建新对象，记录 `outcome + exception + side events`；
- 本机 Python 3.11 baseline 140 observations digest 应为
  `05b7908685c415a6dada0b1530ca0bd310afb4f8ca4b950343752a5ea6643aab`；其他运行时先记录自己的
  baseline，再要求 candidate/revert/reapply 同环境相等；
- 跑 103 direct tests 与 23-file/1162-test 影响切片 baseline；
- 对 `rg -l 'from ai_sdlc\.utils\.helpers import' src/ai_sdlc` 得到的 72 模块逐个 cold import，要求
  failures/noisy 均为空；
- 将 baseline 字段先写入唯一 receipt，candidate 字段保持 absent 而非伪造占位。

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
3. 复算结构：目标 exact body=1、10 alias binding、23 calls、call digest不变、external consumer=0。
4. 复算 diff：目标 raw additions≤25/deletions≥147、non-empty additions≤23/deletions≥127；
   超限立即停止，不靠删测试抵消。
5. 提交一个可独立 revert 的 implementation commit；不在提交后改写产品内容。

## 5. Phase 3：T61B、回退与验证

1. 在 candidate 上重跑 140 observations，当前 Python 3.11 期望 digest=
   `05b7908685c415a6dada0b1530ca0bd310afb4f8ca4b950343752a5ea6643aab`。
2. 重跑 104 direct、23-file/1163 impact、72 cold imports、full pytest、Ruff、constraints、validate、truth。
3. 在 disposable clone revert implementation commit：tree OID=baseline；重跑结构、140 diff、
   103 direct、1162 impact、72 imports。
4. reapply 同一 commit：tree OID=reviewed candidate；重跑140、104 direct、1163 impact、72 imports并生成 receipt SHA-256。
5. 验证 GAP-09 capability/inheritance/admission、GAP-10 adapter consumption/CLI、GAP-11 inventory/truth 零漂移。
6. 对 exact candidate HEAD/tree/binary/name-status/formal-six/receipt/truth identity 让 Pascal/Confucius 双审。
7. finding 成立则最小修复并全部重审；双 PASS 后才 push/PR。
8. Codex current-head 无 actionable findings且 required checks 全绿后 merge；detached fresh-main 重跑
   targeted/full/Ruff/constraints/validate/truth/manifest/clean guard。

## 6. Phase 4：Closure

从 implementation merge exact main 创建 `codex/211-shared-mapping-dedupe-closure`，只登记
`completed_reduction`、最终产品 ledger 和 close source。先让 Pascal/Confucius 审同一 closure identity，
再按 Codex/check/merge/fresh-main 流程交付。closure 不修改产品或行为测试，不关闭父路线或发布版本。

## 7. 验证矩阵

| 路径 | 必须证明 | 命令/证据 |
|---|---|---|
| identity RED/GREEN | 10 distinct→1 shared；module=`utils.helpers` | exact unit nodeid |
| mapping 语义 | 结果、异常、truthiness/dict 事件、浅复制 | 10×14=140 differential |
| 直接行为 | 10 target test files 场景不减 | baseline/revert 103；candidate/reapply 104 |
| 影响行为 | observation/verification/artifact/CLI/Program | 固定23 files；baseline/revert 1162；candidate/reapply 1163 |
| 共享叶子 import | 全部 72 importer 无失败/输出 | cold-import receipt |
| 结构/预算 | 10→1、23 calls不变、net达到阈值 | AST + numstat + non-empty counter |
| 回退 | baseline/candidate tree 精确恢复 | disposable clone receipt |
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
