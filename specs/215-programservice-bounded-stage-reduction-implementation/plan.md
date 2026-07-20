---
related_plan: "specs/213-programservice-bounded-stage-reduction/plan.md"
related_doc:
  - "specs/213-programservice-bounded-stage-reduction/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# ProgramService Bounded Stage Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变公共行为的前提下，把九阶段 45 个 ProgramService legacy body 收敛为一个 bounded-stage private engine，并通过独立 deletion/rollback 完成可逆减重。

**Architecture:** DTO 与 27 个 public facade 留在 `program_service.py`；一个 `_program_bounded_stage.py` 只接收显式 typed/path/callback binding，不 import service/CLI、不按 stage name 分支。T61A proof 与 candidate 产品严格分离，candidate 保留 legacy 并经过 T61B/稳定期后才允许独立删除。

**Tech Stack:** Python 3.11+、dataclasses、pathlib、PyYAML、Typer、pytest、Ruff、uv；新增依赖为 0。

## Global Constraints

- Canonical 合同是 WI213 `spec.md + plan.md + tasks.md`；本计划不得放宽其 CC/RC。
- 双 readiness GO 前 `src/**` 零差异，两份目标行为测试 blob 不变；`tests/**` 只允许 manifest
  inventory/close 数字机械替换，不得改变逻辑或物理 LOC。
- Recorder目标≤170、硬上限200；全部新增 test/harness/normalizer硬上限290；private engine≤360；glue≤90；candidate
  route/facade≤72；peak product≤522。
- Product+proof组合硬上限仍为729；个别hard cap不能相加使用。当前candidate product shadow为
  `330 engine + 85 proven-lower-bound glue + 51 route/facade = 466`；
  T61A使用`shadow + actual current proof + frozen future proof reserve≤729`，future reserve固定90行，
  T33使用actual+actual；proof每
  超出一行，product至少等量下降，否则RC-06 NO-GO。
- Terminal≤720、净删≥2,918、ProgramService responsibility reduction≥3,278、branch proxy≤90。
- 只允许一个 private 产品模块；每个新/修改函数≤50行；禁止公共抽象、反射分发、DSL、registry、循环 import。
- Candidate 与 deletion 是同一 T66 work package 的两个独立 PR；删除前不关闭 T66。
- 不修改版本/tag/Release/PyPI/共享 CLI；T66 完成不等于 WI196/RC-08/release 完成。

---

## 1. 文件职责

| 文件 | 职责 | 阶段 |
|---|---|---|
| `scripts/program_bounded_stage_t61a.py` | 唯一 T61A 最小baseline recorder与receipt verifier | T61A |
| `.ai-sdlc/work-items/215-programservice-bounded-stage-reduction-implementation/t61a-legacy-baseline-receipt.json` | 机器生成 legacy raw evidence；不自绑定自身 hash | T61A |
| `src/ai_sdlc/core/_program_bounded_stage.py` | 唯一 private definitions、cross-spec strategy、bounded strategy 与 engine | candidate |
| `src/ai_sdlc/core/program_service.py` | 现有 DTO；九组显式 binding；27 public facade/selector；删除期移除 legacy body | candidate/deletion |
| `tests/unit/test_program_service.py` | 复用 106 legacy tests；candidate 只加最小 RED/differential seam | candidate |
| `tests/integration/test_cli_program.py` | 复用59 CLI tests；承载唯一test-only三方runner；保持九命令surface/exit/stdout/stderr | candidate |
| `tests/conftest.py` | 最多增加test-only route/root seam；产品不得读取 | candidate |
| `tests/integration/test_repo_program_manifest.py` | 只机械替换 WI215 inventory/close 精确数字；不改逻辑/LOC | formal |
| `specs/215-*/task-execution-log.md` | identity、命令、结果、finding、预算与回退的唯一人工执行归档 | 全阶段 |
| `specs/215-*/development-summary.md` | pre-close current truth；不宣称 T61A/T66 完成 | 全阶段 |

不新增第二个proof/helper/test DSL、第二个产品模块、第二份receipt schema或新测试文件。Future reserve按
spec §4逐文件/symbol固定90行；任一symbol自然实现超额时必须等量降低product shadow，否则NO-GO。

## 2. Phase 0：Canonical WI 与准入

1. 从 `origin/main@7922956d` 建立独立 worktree；确认 merge tree=`cc3c6b7f` 且 receipt fresh-main 全绿。
2. 运行 `workitem init` 创建 WI215；恢复 `init` 预期刷新但不属于 T66 scope 的 Cursor bytes。
3. 用本 spec/plan/tasks/log/summary 替换通用模板；manifest dependency 只指向 WI213。
4. 将 manifest exact test 仅机械替换为 inventory=`1131/1131/0/0`、close=`215/215`；该 diff 新增行
   计入 proof，目标行为测试 blob 不变。
5. 执行 truth sync、constraints、validate、truth audit、manifest exact、scope/diff/clean；提交 formal authoring。

**停止**：任何 `src/workflow/dependency/version/release` 差异、目标行为测试 blob 变化、manifest test 超出
inventory/close 数字机械替换，或 WI213 dependency/预算被放宽。

## 3. Phase 1：T61A proof-only commit

### 3.1 先固定 legacy inventory

1. 在创建 proof code 前运行 WI213 精确 selector，必须为 `165 passed, 474 deselected`。
2. Python 3.11 AST 复算45 methods及调用图：`3,638/3,305/333/386`，18 private 外部 consumer=0。
3. 记录 Python/OS/uv/pytest/Pydantic/Typer/PyYAML、`uv.lock`、`pyproject.toml` 和三份 legacy source/test hash。
4. 用两个独立 `--basetemp` 重跑 exact 165，均必须通过；selector warm-up+20 原始duration作为T61A
   性能基线，T61B三方同机重采。

### 3.2 TDD 编写唯一 recorder

1. 先运行不存在的recorder命令，RED必须只因文件不存在。
2. 以目标≤170、hard cap200实现45-symbol inventory、public/DTO结构指纹、formal/source/dependency/toolchain
   identity、exact165 ordered nodes与目标test/fixture/config blob hash、双basetemp命令结果、20个原始duration、
   proof/combined预算和工作树前后不变证明；按spec §4 anchored grammar冻结九组exact node IDs/count及两个
   测试文件各九个seed helper的file/symbol/source SHA；record/verify在分组前均拒绝任何`thread_archive`/
   `project_cleanup` node，再断言九组计数和disjoint union；每函数≤50。
3. 不在T61A重复实现loader/builder/direct/CLI、late-bound、fault/termination或sentinel动态矩阵；按spec §4.2
   将其冻结到每stage/T61B的原始legacy/current legacy/candidate三方replay。
4. `record`只写调用者指定evidence路径；schema v2使用identity/structure/tests/performance/budget五个
   JSON-primitive section及canonical hash。`verify`只读重算，不重写性能样本或receipt。
5. Pass要求`error=null`、五section、双basetemp、预算、worktree不变与exit0；no_go要求非空error且只允许五section全序的空集/严格
   前缀且已取得hash有效，temp+flush+fsync+replace后非零退出；`verify(no_go)`保持no_go并非零，绝不
   补算/升级pass；temp位于target parent，file fsync→replace→平台支持时directory fsync；不可清理死亡由外部envelope记录。
6. 生成唯一`t61a-legacy-baseline-receipt.json`并检查≤2MiB；不得新增typed canonicalizer、normalizer、
   transitive AST mapper、第二schema或第二harness。

### 3.3 Proof commit 与 readiness

1. 提交 formal、recorder、receipt、manifest/truth 与 root/scoped handoff；worktree必须 clean，且
   `src/**`零差异、两份目标行为测试blob不变、manifest test仅机械数字替换。
2. 固定 legacy commit/tree、proof commit/tree、WI196+WI213 canonical formal-six SHA、WI215
   spec/plan/tasks SHA、harness SHA、receipt file SHA和五个section SHA。
   Formal SHA 均按spec §4/WI213 plan §8 的 per-file SHA line payload 算法计算。
3. 重跑 recorder verification、165、constraints/validate/truth/manifest、Ruff、scope/clean。
4. 预算tuple另列candidate product shadow、actual current proof和逐stage/T61B/stability任务future proof
   reserve（固定90行），三者≤729；Pascal/LEAN与Confucius/SAFETY对完全相同tuple各自裁决
   `GO/NO-GO`；任何文件变化双 verdict 同时退役。

**完成**：双 `GO`、actionable findings=0；否则保留 legacy并停止，不能写产品代码。

## 4. Phase 2：逐 stage TDD candidate shadow

### 4.1 Candidate interfaces

Private module 只产生内部 frozen/slots definition、九个静态 definition、一个 cross-spec strategy、一个其余
八阶段 strategy，以及 request/execute/write/payload/load 小函数。`program_service.py` 在 DTO 定义后建立
九组显式 binding，包含 Request/Step/Result factory、source/output path、step-dir或cross filename和从
`self` 解析的 callback。不得使用字符串 method lookup。

### 4.2 每个 stage 的原子循环

按 `cross_spec_writeback → guarded_registry → broader_governance → final_governance →
writeback_persistence → persisted_write_proof → final_proof_publication → final_proof_closure →
final_proof_archive` 顺序：

1. 在既有两个测试文件写 candidate seam/differential RED；legacy path仍通过，candidate path因未实现失败。
2. 运行单个 nodeid，确认 failure 是缺少当前最小 engine行为而不是fixture/import错误。
3. 实现当前 stage 最小 definition/strategy/engine；未迁移 stage selector 仍为 legacy。
4. 通过spec §4冻结的outer/supplemental node和三条`uv run --isolated --project <leg-root>`worker命令执行三腿；先对
   cwd/HEAD/tree/interpreter/resolved module file/source SHA/route做fail-closed attestation，再用同一重置后的
   绝对behavior root、原生JUnit及未跟踪raw artifact证明当前stage和此前stage的§4.2完整矩阵零差异。
5. 记录 module/route/glue/total LOC 与 branch；任一预算不可达立即 NO-GO，不扩大预算。
6. 每个可独立审查的 stage批次提交一次；不得提交只有中间 routing、无通过测试的状态。

九阶段全部完成前生产默认 selector 仍为 legacy。

## 5. Phase 3：T61B 与 candidate PR

1. 固定candidate commit/tree；用同一test-only runner和byte-identical seed三方运行原始legacy/current
   legacy/candidate，runner记录三条subprocess命令、原生JUnit与raw tree hash。
2. Spec §4.2完整矩阵三方未批准差异必须为0；candidate p95使用同机三方样本，超过baseline 110%且复测成立即停止。
3. 实际运行 legacy→candidate→legacy→candidate；每次重跑九stage完整矩阵，task log登记JUnit/raw tree hash。
4. 将默认 selector切到 candidate，legacy body完整保留。
5. 运行 exact165+新增tests、full suite、Ruff、constraints、validate/truth、manifest、双 PASS0。
6. Push/open candidate PR；current-head Codex、required checks 全绿后 merge并 detached fresh-main。

**回退**：selector-only 指回 legacy；不得删除 legacy。

## 6. Phase 4：主线预发布稳定周期

1. 绑定 candidate merge tree，核验 required cross-platform checks。
2. 构建 wheel/sdist，检查 private module打包；预置 build/runtime dependencies 到受控 wheelhouse。
3. 断网后两个 clean env 分别用 `--no-index --find-links` 安装 wheel/sdist；禁止读取源码 checkout。
4. 在安装产物上运行 Python surface、九命令 help/dry-run/full chain 和 offline sentinel。
5. 选择至少两个 sibling project，记录选择理由，只使用安装产物 smoke。
6. selector rollback/reapply；结果必须与 T61B receipt 一致。

**停止**：任一平台/package/offline/sibling/performance/rollback失败；在 candidate work package修复，
不得开始 deletion，也不得 tag/Release/PyPI。

## 7. Phase 5：独立 deletion PR 与 actual rollback

1. 从已通过稳定周期的 candidate merge commit 建独立 deletion branch/worktree。
2. 删除45个 legacy full body、18个失活 private方法、legacy selector branch和仅legacy使用的glue；
   保留27 public facade/DTO。
3. 复算 terminal≤720、net delete≥2,918、responsibility reduction≥3,278、branch≤90。
4. 先在冻结T61A proof worktree运行recorder verify并登记其HEAD/tree；deletion checkout不得用自身重算
   已删除的45-symbol基线。再以T61A原始legacy、冻结pre-deletion candidate-merge current legacy、
   deletion-head candidate三腿重跑§4.2完整矩阵，并运行165/full/Ruff/governance/platform/package/offline/sibling和本地双审。
5. Current-head Codex、required checks全绿后 merge；T66仍active。
6. 从精确deletion merge commit建一次性rollback worktree，实际revert deletion merge；证明legacy route、
   surface与selector round-trip；随后回到deletion fresh-main，以T61A原始legacy、冻结pre-deletion
   candidate-merge current legacy、fresh-main candidate三腿再次重验spec §4.2完整矩阵与关键证据。
7. 只有 actual rollback receipt 与 deletion fresh-main全绿后，lifecycle receipt 才关闭WI215/T66并更新GAP-03。

## 8. 精确验证命令

```powershell
$env:AI_SDLC_DISABLE_UPDATE_CHECK = '1'
uv run --python 3.11 pytest -p no:cacheprovider `
  tests/unit/test_program_service.py tests/integration/test_cli_program.py `
  -k '(cross_spec_writeback or guarded_registry or broader_governance or final_governance or writeback_persistence or persisted_write_proof or final_proof_publication or final_proof_closure or final_proof_archive) and not thread_archive and not project_cleanup' -q
uv run --python 3.11 python scripts/program_bounded_stage_t61a.py record --route legacy --output <temp-json>
uv run --python 3.11 python scripts/program_bounded_stage_t61a.py verify --route legacy --input <receipt-json>
uv run --python 3.11 ruff check scripts/program_bounded_stage_t61a.py
uv run --python 3.11 pytest -q
uv run --python 3.11 ai-sdlc verify constraints
uv run --python 3.11 ai-sdlc program validate
uv run --python 3.11 ai-sdlc program truth audit
uv run --python 3.11 pytest -q tests/integration/test_repo_program_manifest.py
```

三方outer命令及其内部三条单层pytest worker模板固定如下；`<...>`均由当前stage ledger替换为绝对路径或精确hash：

```powershell
$env:AI_SDLC_THREE_WAY_ORIGINAL_ROOT = '<original-root>'
$env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_ROOT = '<current-legacy-root>'
$env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT = '<candidate-root>'
$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT = '<untracked-evidence-root>'
$env:AI_SDLC_THREE_WAY_BEHAVIOR_ROOT = '<single-resettable-behavior-root>'
$env:AI_SDLC_THREE_WAY_ORIGINAL_COMMIT = '<original-commit>'
$env:AI_SDLC_THREE_WAY_ORIGINAL_TREE = '<original-tree>'
$env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_COMMIT = '<current-legacy-commit>'
$env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_TREE = '<current-legacy-tree>'
$env:AI_SDLC_THREE_WAY_CANDIDATE_COMMIT = '<candidate-commit>'
$env:AI_SDLC_THREE_WAY_CANDIDATE_TREE = '<candidate-tree>'
$Stage = '<stage>'
uv run --python 3.11 pytest -p no:cacheprovider `
  "tests/integration/test_cli_program.py::test_program_bounded_stage_three_way_replay[$Stage]" `
  --basetemp "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/outer" `
  --junitxml "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/outer.xml" -q

$Nodes = @('<outer-expanded absolute candidate test node IDs from T61A receipt>', '<supplemental node IDs>')
$env:AI_SDLC_TEST_PROGRAM_ROUTE = 'original'
uv run --isolated --project $env:AI_SDLC_THREE_WAY_ORIGINAL_ROOT --directory $env:AI_SDLC_THREE_WAY_ORIGINAL_ROOT `
  --python 3.11 python -I -m pytest -p no:cacheprovider -o "pythonpath=$env:AI_SDLC_THREE_WAY_ORIGINAL_ROOT/src" `
  --import-mode=importlib @Nodes --rootdir $env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT `
  --basetemp "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/original/tmp" --junitxml "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/original.xml" -q
$env:AI_SDLC_TEST_PROGRAM_ROUTE = 'legacy'
uv run --isolated --project $env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_ROOT --directory $env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_ROOT `
  --python 3.11 python -I -m pytest -p no:cacheprovider -o "pythonpath=$env:AI_SDLC_THREE_WAY_CURRENT_LEGACY_ROOT/src" `
  --import-mode=importlib @Nodes --rootdir $env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT `
  --basetemp "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/current-legacy/tmp" --junitxml "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/current-legacy.xml" -q
$env:AI_SDLC_TEST_PROGRAM_ROUTE = 'candidate'
uv run --isolated --project $env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT --directory $env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT `
  --python 3.11 python -I -m pytest -p no:cacheprovider -o "pythonpath=$env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT/src" `
  --import-mode=importlib @Nodes --rootdir $env:AI_SDLC_THREE_WAY_CANDIDATE_ROOT `
  --basetemp "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/candidate/tmp" --junitxml "$env:AI_SDLC_THREE_WAY_EVIDENCE_ROOT/candidate.xml" -q
```

Outer从T61A receipt按spec §4 anchored grammar展开截至当前stage的累计exact node IDs，重写为candidate
checkout绝对test paths并追加对应supplemental nodes；展开前再次拒绝`thread_archive`/`project_cleanup`；
不得调用test function、嵌套pytest或选择outer。每腿
JUnit须逐项等于expanded nodes且全部passed。每腿前重置同一behavior root，先验真provenance，再比较完整
动态矩阵；共享`.venv`或解析到另一腿editable source立即失败。

每次命令记录 exit code、duration、HEAD/tree和输出hash。PowerShell placeholder `<temp-json>` 必须替换为
隔离临时路径，不能原样执行。

## 9. Review identity 与提交边界

- Formal/T61A proof、candidate、stability、deletion、rollback各自形成独立identity/receipt；不得预写future hash。
- Receipt不嵌入自身commit/tree/hash；独立review envelope按spec §4分列legacy/proof commit+tree、两个
  formal hash、harness/receipt file SHA、五个section SHA和verdict。
- 任一受审文件变化使两位本地reviewer旧结论同时失效。
- Candidate和deletion分支均保留；不删除本地分支。
