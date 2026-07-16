# 实施计划：Frontend Artifact Path Dedupe Reduction

**编号**：`205-frontend-artifact-path-dedupe`\
**日期**：2026-07-15\
**规格**：`specs/205-frontend-artifact-path-dedupe/spec.md`\
**父项**：WI-196 `T63 / WP-03`

## 1. 概述

本项使用一个私有、无选项的 path helper 替换 12 个 frontend artifact generator 中完全相同的
`_dedupe_paths` body。实施只包含一个新模块、12 条 import、12 个本地 body 删除，以及在现有
dedupe test function 内增加两行 direct-binding 顺序断言；不新增 test function/file 或 harness，
不改变 artifact/CLI/schema/runtime behavior。

## 2. 技术背景

- **语言/版本**：Python 3.11+
- **依赖**：标准库 `pathlib.Path`；不新增依赖
- **数据/存储**：不新增产品 schema、配置或 fixture；生成一个 scoped compatibility receipt
- **测试**：pytest；14 个既有 dedupe tests（一个增加两行断言）、76-test artifact slice、full suite、跨平台 CI
- **基线**：`e4f395e3b2247c0968d61aebd53814b1602f7845`，`3220 passed, 3 skipped`
- **冻结指标**：产品 modules=2602 raw/2275 non-empty；算法=108/108 LOC、complexity 36、
  12 defs/13 calls、syntactic fan-out 36/internal fan-out 0；test files=2723 raw/2317 non-empty，
  14 dedupe=280/239；targeted median=.73s/p95=.74s；CLI/Program=78 passed
- **约束**：RC-04/06/07/09/10；产品 raw additions≤24；既有 test raw additions=2；
  product+test source additions≤26≤RC-06 cap 27

## 3. 宪章与 Lean Gate

| 门禁 | 计划响应 |
|---|---|
| 行为优先 | 既有 test 增加两行顺序断言 + mutation RED + candidate GREEN |
| 稳定重复才抽取 | 12 个同 AST body、13 个现有调用点、相同异常与副作用语义 |
| 不造扩展点 | 私有函数、无参数策略、无 public export、无 `utils` 扩张 |
| 测试不减 | 不新增/删除 test function；14 个既有 dedupe tests 全保留，其中一个强化两行 |
| 可量化净减重 | AST 108→9、complexity 36→3；产品 raw additions≤24、deletions≥108、net≤-84 |
| 增量与原子 | 独立 WI/branch/PR，只处理 path duplicate family |
| 兼容与回退 | CC-03/05/06/07 differential；单个实现 commit 可整体 revert |
| 对抗评审 | formal 与 final tree 都需 Pascal/Confucius 同 hash PASS |

## 4. 结构与文件边界

```text
src/ai_sdlc/generators/
├── _artifact_paths.py                         # 新增：唯一 private helper
├── frontend_contract_artifacts.py            # import + 删除 local body
├── frontend_cross_provider_consistency_artifacts.py
├── frontend_gate_policy_artifacts.py
├── frontend_generation_constraint_artifacts.py
├── frontend_page_ui_schema_artifacts.py
├── frontend_provider_expansion_artifacts.py
├── frontend_provider_profile_artifacts.py
├── frontend_provider_runtime_adapter_artifacts.py
├── frontend_quality_platform_artifacts.py
├── frontend_solution_confirmation_artifacts.py
├── frontend_theme_token_governance_artifacts.py
└── frontend_ui_kernel_artifacts.py
```

允许的非产品改动仅为：

- `specs/205-frontend-artifact-path-dedupe/*`
- `tests/unit/test_frontend_contract_artifacts.py`（仅在既有 dedupe test function 内新增两行断言）
- `.ai-sdlc/state/*` 与 scoped continuity/runtime metadata
- `.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`
- `.ai-sdlc/project/config/project-state.yaml`
- `program-manifest.yaml`
- WI-196 development summary / execution log / continuity 的关闭索引

不修改其他 `tests/`、`generators/__init__.py`、models/core/cli、provider/governance artifact、
workflow 或版本发布面。

## 5. 分阶段实施

### Phase 0：formal freeze 与双 Agent 评审

1. 运行 Appendix A 的 AST/test ledger，冻结完整 product/test LOC、12 defs、13 calls、fan-in
   distribution、108 LOC、complexity/fan-out 36、internal fan-out 0、完整 body digest、14 tests/
   280 raw/239 non-empty LOC、76-test runtime、CLI surface 与 CC/GAP impact。
2. 比较 private helper、inline expression、generic utility 三种方案。
3. 计算 `spec.md + plan.md + tasks.md` 内容 hash。
4. Pascal 从精简/直接性、Confucius 从兼容/证明性独立评审；任一修改使旧 PASS 失效。

**门禁**：两者对同一 hash 都为 PASS，才允许进入 T61A。

### Phase 1：T61A baseline 与 mutation RED

1. 在未改产品的基线运行 12 个 artifact test module 五次，记录通过数、OS/Python、revision、
   median/p95；冻结 12 个 expected-file-set tests/94 paths、payload parser/assertion 清单。
2. 按 Appendix A.4 在本地 target platform 运行 `wi205-git-tree-v1` 两次 baseline stability：同一
   绝对 shared `--basetemp`、同 Git/attribute 配置、外置 Git dir、每次 fresh index、
   `allowlist=[]`；两次 tree OID/
   entry count 必须相等。审前两个独立 fixed-root probe 均为 463 entries（418 regular +45
   symlinks），各自在自己的 absolute root 内两次 OID 相同；T61A paired run 才生成权威 baseline OID。
3. 在 `test_frontend_contract_artifacts.py` 现有 materialize dedupe test function 内增加两行：
   构造 `[Path("first"), Path("second"), Path("first")]`，并通过已导入的 module private binding
   断言结果等于前两个元素；不新增 test function/fixture/helper/file。
4. 用可恢复临时 patch 将该 module 的 local helper `unique` 返回值故意反转；断言必须因期望
   `[first, second]`、实际 `[second, first]` 稳定 RED，而非 import/fixture 错误。
5. 用 `apply_patch` 恢复临时 mutation；重跑被强化 test 与 76-test targeted GREEN。
6. 重跑 Appendix A ledger；确认 test raw additions=2、无新 test function。

**门禁**：断言不能捕获 `reverse(unique_output)` mutation、test additions≠2、恢复后不绿、
expected-path/payload baseline、Git tree stability 或 ledger 不一致时停止。

### Phase 2：最小实现

1. 新增 `_artifact_paths.py`，原样保留当前 9 LOC 算法；不加选项、包装器、类或多余注释。
2. 12 个 module 各增加一条 private import，删除 local body；调用代码不改名。
3. Ruff 排序 imports；Phase 1 的两行断言继续通过原模块 private binding 观察 imported canonical
   helper；除这两行外，不修改测试或 artifact payload。
4. Appendix A AST gate 复算 defs 12→1、算法 108→9、complexity 36→3、fan-out 36→3、
   calls=13、body digest 不变；raw ledger 与 source-addition gate 复算固定 changed-file set。

**门禁**：产品 raw additions>24、deletions<108、net>-84、product+test additions>26、
实现数不为 1、调用点不为 13、body digest 改变或 changed files 越界时按 RC-09 停止。

### Phase 3：T61B differential、回退与验证

1. 在隔离 candidate clone 以与 baseline 相同的 shared `--basetemp` 运行 76 tests；12 个
   expected-file-set tests/94 paths 与既有 YAML/JSON payload semantic assertions 必须保持 GREEN。
2. 运行 14 个 dedupe tests、broad frontend slice 67 tests、`test_cli_rules.py` 9 tests 与两个精确
   solution-confirm nodeid；这些既有 semantic assertions 保护 path/count/parsed payload/可见文本，
   不宣称 raw stdout/stderr equality，renderer normalizer 为空。
3. 用同一 `wi205-git-tree-v1` Git object database 生成 candidate tree；必须与该平台 baseline 的
   tree OID 和 entry count 相同。不同则 `git diff-tree --binary` 诊断并 fail-closed，allowlist 保持空。
4. exact source diff 必须证明 13 个 call expression、writer body/顺序与 serialization 未改；在
   disposable clone 对候选实现 commit 做 revert rehearsal，targeted 与 Git tree 必须恢复 baseline，
   再恢复 candidate 后重新相等。
5. 生成唯一 scoped JSON receipt，包含 schema/version、surface manifest、baseline/candidate/revert
   revision 与 GoldenSnapshot、Git toolchain/config/commands、DifferentialResult、rollback 与 test verdict；
   execution log 记录 receipt SHA-256。
6. 运行 full pytest、Ruff、constraints、Program validate/truth、diff-check。
7. Program Truth 只接受目标 commit 三元组、fresh/ready/exit 0/zero blocker 与 exact capability/
   inventory；GAP-09～11 回归即 fail-closed/reopen。
8. 复用现有 CI 在 Windows/macOS/Linux 运行 full pytest；该 suite 必须包含强化后的顺序 test 与
   76 个 artifact tests。paired Git-tree/rollback 是本地 T61A/B gate，不宣称现有 CI 生成 baseline↔
   candidate OID，也不修改 workflow 或新增跨平台 harness。

**门禁**：零未批准差异、回退可用、RC 账本达标后才能提交 final review。

### Phase 4：final 双审、PR 与 mainline 关闭

1. 计算 final source tree/diff hash，两个 Agent 独立复审到一致 PASS。
2. 提交、推送 implementation branch、创建 ready PR、请求 Codex review。
3. 维持约五分钟 heartbeat；actionable finding 只做定向修复并重新双审/重请 review。
4. required checks 全绿后 merge；fresh main clone 重跑 targeted/full/truth。
5. 将 WI-205 与 WI-196 T63 关闭证据写入 canonical truth；不把 WP-03 单一族等同于整个路线完成。

## 6. 关键验证矩阵

| 关键路径 | 主证据 | 补充证据 |
|---|---|---|
| 首次出现顺序 | 既有 test 两行 direct-binding 断言 + mutation RED | 14 个既有 dedupe tests |
| Path equality/hash | 原算法逐行等价 + tests | 三平台 CI |
| artifact tree/payload | `wi205-git-tree-v1` raw tree identity + 12 expected-file-set tests/94 paths | parser assertions + unchanged-writer diff + 76 tests |
| 无新增副作用 | code review + no filesystem call | temp root tree diff |
| 重复族清零 | AST/text count 12→1 | call-site count=13 |
| 净减重 | AST/complexity/fan-in/out gate | 固定 changed-file set 的 git numstat + source-addition gate |
| 回退 | disposable clone revert rehearsal + scoped structured receipt | baseline targeted/tree GREEN |
| truth/inventory | 目标 commit fresh/ready/exit 0 | zero blocker + exact set + unmapped/missing=0 |

## 7. 验证命令（Appendix A）

Targeted artifact suite 使用 12 个显式文件，避免依赖 shell glob：

```text
uv run pytest -q tests/unit/test_frontend_contract_artifacts.py tests/unit/test_frontend_cross_provider_consistency_artifacts.py tests/unit/test_frontend_gate_policy_artifacts.py tests/unit/test_frontend_generation_constraint_artifacts.py tests/unit/test_frontend_page_ui_schema_artifacts.py tests/unit/test_frontend_provider_expansion_artifacts.py tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_frontend_provider_runtime_adapter_artifacts.py tests/unit/test_frontend_quality_platform_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py tests/unit/test_frontend_theme_token_governance_artifacts.py tests/unit/test_frontend_ui_kernel_artifacts.py
uv run pytest -q tests/integration/test_cli_program.py tests/integration/test_cli_verify_constraints.py -k frontend
uv run pytest -q tests/integration/test_cli_rules.py tests/integration/test_cli_program.py::TestCliProgram::test_program_solution_confirm_execute_writes_snapshot_without_preview_only_fields tests/integration/test_cli_program.py::TestCliProgram::test_program_solution_confirm_execute_blocks_unknown_provider_artifact_materialization
uv run pytest -q
uv run ruff check src tests
uv run ai-sdlc verify constraints
uv run ai-sdlc program validate
uv run ai-sdlc program truth audit
git diff --check
```

### A.1 AST / complexity / fan-in-out ledger

以下命令固定 AST body serializer、完整 SHA-256、definition location/count、non-empty LOC、
decision-node complexity、syntactic call fan-out、call distribution、module import fan-in 和完整产品
module LOC；baseline 必须输出 2602/2275、12/108/36/36/13/imports 0，candidate 必须输出
1/9/3/3/13/imports 12，且 digest 均为 spec §1 的完整值：

```text
uv run python -c "import ast,collections,hashlib,pathlib; product=sorted(pathlib.Path('src/ai_sdlc/generators').glob('frontend_*_artifacts.py')); fs=product+[pathlib.Path('src/ai_sdlc/generators/_artifact_paths.py')]; ts=[(p,ast.parse(p.read_text(encoding='utf-8'))) for p in fs if p.exists()]; ds=[(p,n) for p,t in ts for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='_dedupe_paths']; cs=[(p,n.lineno) for p,t in ts for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_dedupe_paths']; imports=sum(isinstance(n,ast.ImportFrom) and n.module=='ai_sdlc.generators._artifact_paths' and any(a.name=='_dedupe_paths' for a in n.names) for p,t in ts for n in ast.walk(t)); dec=(ast.If,ast.For,ast.AsyncFor,ast.While,ast.Try,ast.BoolOp,ast.IfExp,ast.comprehension); target=lambda f:f.id if isinstance(f,ast.Name) else f.attr if isinstance(f,ast.Attribute) else type(f).__name__; rows=[{'path':str(p),'line':n.lineno,'nonempty_loc':sum(bool(x.strip()) for x in p.read_text(encoding='utf-8').splitlines()[n.lineno-1:n.end_lineno]),'complexity':1+sum(isinstance(x,dec) for x in ast.walk(n)),'body_sha256':hashlib.sha256(ast.dump(ast.Module(body=n.body,type_ignores=[]),include_attributes=False).encode()).hexdigest(),'call_targets':sorted(target(x.func) for x in ast.walk(n) if isinstance(x,ast.Call))} for p,n in ds]; raw=sum(len(p.read_text(encoding='utf-8').splitlines()) for p in product); nonempty=sum(sum(bool(x.strip()) for x in p.read_text(encoding='utf-8').splitlines()) for p in product); print(*rows,sep='\n'); print({'product_raw':raw,'product_nonempty':nonempty,'definitions':len(ds),'call_sites':len(cs),'call_distribution':dict(collections.Counter(str(p) for p,_ in cs)),'module_import_fan_in':imports,'aggregate_nonempty_loc':sum(x['nonempty_loc'] for x in rows),'aggregate_complexity':sum(x['complexity'] for x in rows),'aggregate_syntactic_fan_out':sum(len(x['call_targets']) for x in rows)})"
```

### A.2 既有 dedupe test ledger

以下命令同时复算 12 个 test files 的 2723 raw/2317 non-empty LOC，以及 14 dedupe symbols 的
280 raw/239 non-empty LOC；candidate files/symbols 只允许因两行断言变为 2725/2319 与 282/241：

```text
uv run python -c "import ast,pathlib; fs=sorted(pathlib.Path('tests/unit').glob('test_frontend_*_artifacts.py')); rows=[]; exec(compile('for p in fs:\n s=p.read_text(encoding=\"utf-8\"); ls=s.splitlines(); t=ast.parse(s)\n for n in ast.walk(t):\n  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and \"deduplicates_\" in n.name and \"returned_paths\" in n.name:\n   rows.append((str(p),n.name,n.lineno,n.end_lineno,n.end_lineno-n.lineno+1,sum(bool(x.strip()) for x in ls[n.lineno-1:n.end_lineno])))','<wi205-test-ledger>','exec')); file_raw=sum(len(p.read_text(encoding='utf-8').splitlines()) for p in fs); file_nonempty=sum(sum(bool(x.strip()) for x in p.read_text(encoding='utf-8').splitlines()) for p in fs); print(*rows,sep='\n'); print({'test_files':len(fs),'file_raw':file_raw,'file_nonempty':file_nonempty,'dedupe_tests':len(rows),'dedupe_raw':sum(r[4] for r in rows),'dedupe_nonempty':sum(r[5] for r in rows)})"
```

### A.3 raw LOC 与 RC-06 合并预算

候选形成 local commit 后执行；只统计冻结的产品目录与唯一 test file，避免未跟踪 helper 被漏算。
输出必须满足 product additions≤24/deletions≥108/net≤-84、test additions=2/deletions=0，
product+test additions≤26≤27：

```text
git diff --numstat e4f395e3 HEAD -- src/ai_sdlc/generators tests/unit/test_frontend_contract_artifacts.py
```

### A.4 `wi205-git-tree-v1` raw Golden

本协议只调用标准 Git；命令不是 product/test/harness/normalizer source。PowerShell 中先固定同一
absolute basetemp 与外置 object repository。baseline 1、baseline 2、candidate 与 rollback sample
都按同一顺序执行：

```powershell
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion -lt [Version]'7.3') {
  throw 'wi205-git-tree-v1 requires PowerShell 7.3+ native-command fail-fast'
}
$PSNativeCommandUseErrorActionPreference = $true
$ArtifactTests = @(
  'tests/unit/test_frontend_contract_artifacts.py'
  'tests/unit/test_frontend_cross_provider_consistency_artifacts.py'
  'tests/unit/test_frontend_gate_policy_artifacts.py'
  'tests/unit/test_frontend_generation_constraint_artifacts.py'
  'tests/unit/test_frontend_page_ui_schema_artifacts.py'
  'tests/unit/test_frontend_provider_expansion_artifacts.py'
  'tests/unit/test_frontend_provider_profile_artifacts.py'
  'tests/unit/test_frontend_provider_runtime_adapter_artifacts.py'
  'tests/unit/test_frontend_quality_platform_artifacts.py'
  'tests/unit/test_frontend_solution_confirmation_artifacts.py'
  'tests/unit/test_frontend_theme_token_governance_artifacts.py'
  'tests/unit/test_frontend_ui_kernel_artifacts.py'
)
$SharedTemp = Join-Path ([IO.Path]::GetTempPath()) 'ai-sdlc-wi205-shared'
$GitObjectRepo = Join-Path ([IO.Path]::GetTempPath()) 'ai-sdlc-wi205-git-objects'
$EmptyAttributes = Join-Path ([IO.Path]::GetTempPath()) 'ai-sdlc-wi205-empty-attributes'
Remove-Item -LiteralPath $GitObjectRepo -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $EmptyAttributes -Force -ErrorAction SilentlyContinue
New-Item -ItemType File -Path $EmptyAttributes | Out-Null
$env:GIT_ATTR_NOSYSTEM = '1'
git init --quiet --object-format=sha1 $GitObjectRepo
$GitDir = Join-Path $GitObjectRepo '.git'

Remove-Item -LiteralPath $SharedTemp -Recurse -Force -ErrorAction SilentlyContinue
uv run pytest -q @ArtifactTests --basetemp $SharedTemp
if (Get-ChildItem -LiteralPath $SharedTemp -Recurse -Force -Filter '.gitattributes') {
  throw 'wi205-git-tree-v1 refuses worktree .gitattributes'
}
$InfoAttributes = Join-Path $GitDir 'info/attributes'
if ((Test-Path -LiteralPath $InfoAttributes) -and (Get-Item -LiteralPath $InfoAttributes).Length -ne 0) {
  throw 'wi205-git-tree-v1 refuses non-empty info/attributes'
}
Remove-Item -LiteralPath (Join-Path $GitDir 'index') -Force -ErrorAction SilentlyContinue
git -C $SharedTemp --git-dir=$GitDir --work-tree=$SharedTemp -c core.autocrlf=false -c core.attributesFile=$EmptyAttributes add -A -f -- .
$TreeOid = git --git-dir=$GitDir write-tree
```

每个 sample 后还必须记录以下只读命令结果：

```powershell
git --version
git --git-dir=$GitDir rev-parse --show-object-format
git --git-dir=$GitDir config --bool --get --default=true core.filemode
git --git-dir=$GitDir config --bool --get --default=true core.symlinks
git --git-dir=$GitDir ls-tree -r $TreeOid
git --git-dir=$GitDir diff-tree --binary $BaselineTreeOid $CandidateTreeOid
```

`add -A -f -- .` 不带 exclude；normalizer allowlist 精确为 `[]`。`GIT_ATTR_NOSYSTEM=1`、空
`core.attributesFile`、零 worktree/info attributes 与 `core.autocrlf=false` 共同阻断 attributes/clean
filter 转换；这些检查结果必须进入 receipt。本地两次 baseline 必须 OID/
entry count 相等，candidate 与 restored candidate 必须等于该 baseline；revert sample 也必须等于
baseline。`diff-tree --binary` 在相等时零输出；有输出只用于诊断并直接 fail-closed，不允许据此增加
exclude。macOS 预审使用 Git 2.54.0、SHA-1 object format；两个独立 fixed-root probe 都得到
463 entries，并各自在自己的 absolute basetemp 内两次稳定。由于 45 个 symlink target 包含 absolute
basetemp，不同 root 的 OID 合理不同；OID/count 不是跨 root 或跨 OS 常量。现有三平台 CI 只跑
full pytest，不执行该 paired-tree 协议。

唯一 receipt 写入
`.ai-sdlc/work-items/205-frontend-artifact-path-dedupe/t61-differential-rollback-receipt.json`，必须包含：
`schema_version`、versioned surface manifest、normalizer id/commands/allowlist、baseline/candidate/revert
revision、平台/Python/pytest/Git/shell 版本（使用上述 block 时 PowerShell≥7.3）、object format/config、
attribute isolation checks、
每次 test result/tree OID/entry count、
`GoldenSnapshot`、`DifferentialResult`、rollback verdict、full/CLI/truth results。execution log 记录该文件
SHA-256；receipt 必须 <2 MiB。

## 8. 开放问题

无。若实现需要新 test function/file/harness、既有 test 增量不等于两行、helper 选项或 path
normalization，按冻结的 RC-09 直接停止并回到 formal，不在 execute 中扩大范围。
