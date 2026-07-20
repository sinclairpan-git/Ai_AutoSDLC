# 功能规格：ProgramService Bounded Stage Reduction Implementation

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**创建日期**：2026-07-20
**状态**：T61A authoring；产品实现阻断
**类型**：WI-196 / WP-06 / T66 / GAP-03 / L3 implementation
**父合同**：`specs/213-programservice-bounded-stage-reduction/spec.md`
**输入**：在 exact fresh main 上执行 WI213 已冻结的 T66 九阶段 ProgramService bounded-stage 减重。首先只创建 T61A legacy baseline 与 raw evidence，禁止任何产品代码；只有 Pascal/LEAN 与 Confucius/SAFETY 对同一 committed+clean T61A identity 均给出 readiness GO 后，才允许以 TDD 开始 candidate。Candidate PR 必须保留 legacy，完成 T61B、跨平台/安装/offline/sibling/selector rollback 稳定证据；稳定后再用同一 T66 工作包的独立 deletion PR 删除 legacy并做真实回退。candidate、stability、deletion、post-deletion rollback 未全部完成前，不关闭 T66/GAP-03/WI196/RC-08，不发布版本或更新共享 CLI。 参考：`specs/213-programservice-bounded-stage-reduction/plan.md`、`specs/213-programservice-bounded-stage-reduction/spec.md`、`specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md`、`specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md`

## 1. 目的与准入

WI214 closure receipt 已在 `main@7922956d` 完成 detached fresh-main 验收，GAP-15/T58 已关闭，
因此本 WI 是唯一获准进入 T66 T61A 的 implementation work item。本 WI 不复制或改写 WI213 的
Reduction Contract；WI213 `spec.md`、`plan.md`、`tasks.md` 仍是结构、兼容矩阵与预算的 canonical
合同，本文件只绑定当前执行身份、证据载体和阶段门禁。

当前阶段只允许 formal 与 proof 资产。Pascal/LEAN 和 Confucius/SAFETY 对同一个 legacy commit/tree、
proof commit/tree、WI196+WI213 canonical formal-six hash、WI215 formal-three hash、harness hash、
receipt file hash与`identity/structure/tests/performance/budget`五个section hash均签发readiness `GO`前，
`src/**` 必须相对 `7922956d` 零差异，两份目标行为测试 blob 必须不变。`tests/**` 唯一例外是
`tests/integration/test_repo_program_manifest.py` 的 inventory/close 精确数字机械替换；不得改变测试逻辑或
物理 LOC，diff 中该替换的新增行仍计入 proof 预算。

## 2. 范围

### 2.1 覆盖范围

- 九个 stage：`cross_spec_writeback`、`guarded_registry`、`broader_governance`、
  `final_governance`、`writeback_persistence`、`persisted_write_proof`、
  `final_proof_publication`、`final_proof_closure`、`final_proof_archive`。
- 每个 stage 的 request builder、executor、artifact writer、private payload builder、private payload
  loader，共 45 个现有方法；保留 27 个 public facade 和 27 个 DTO。
- T61A legacy recorder、versioned Python surface、exact165身份与双basetemp结果，以及既有selector
  characterization的warm-up+20次p50/p95样本；动态行为矩阵只属于每stage/T61B及后续三方回放。
- 双 readiness GO 后的单 private module candidate、T61B、candidate PR、主线预发布稳定周期、
  独立 legacy deletion PR、exact-merge actual rollback 与最终 lifecycle receipt。

### 2.2 明确不覆盖

- `final_proof_archive_thread_archive`、project cleanup 或其他 ProgramService domain。
- `program_cmd.py` 减重、DTO 搬迁/合并、公共命令/option/schema/config/env、公共 executor 或新增依赖。
- 字符串 method name + `getattr` 产品分发、stage-name `if/elif/match`、runtime registry、DSL、
  循环 import、反射驱动产品路由或第二个产品模块。
- 借本项修复历史行为、改 adapter、更新版本/tag/GitHub Release/PyPI/共享 CLI，或提前关闭
  T66/GAP-03/WI196/RC-08。

## 3. 用户故事与独立验收

### US-1：编码前可复算的 legacy 基线（P0）

作为框架维护者，我希望在任何产品改动前得到单一、可执行、版本化的 T61A receipt，使 reviewer 能冻结
当前45-method legacy的结构、surface、测试身份、既有selector性能和预算基线。

**独立测试**：在 clean proof commit 上先 `record`、后 `verify`；`src/**` diff=0、两份目标测试 blob
不变、manifest test 仅机械替换 inventory/close 数字，165个既有测试在两个独立basetemp精确通过；
`verify`只读复算identity/structure/tests/budget与performance样本结构，不重放动态行为或改写duration。
动态zero-delta从首个stage GREEN起按§4.2三方执行。

### US-2：受预算约束的 candidate shadow（P0）

作为框架维护者，我希望在保留完整 legacy 的同时用一个 private engine 按 stage 做 TDD/differential，
避免一次性大改导致功能丢失。

**独立测试**：每个 stage 先 RED 后 GREEN；未迁移 stage 仍走 legacy；九 stage 完成后
legacy→candidate→legacy→candidate 四次 route receipt 均通过，T61B 未批准差异为 0。

### US-3：可回退的减重完成（P1）

作为发布维护者，我希望 candidate 在 main 完成平台、安装、offline、sibling 和 selector 稳定验证后，
再用独立 PR 删除 legacy，并对真实 deletion merge 做 revert 演练。

**独立测试**：candidate merge tree 与 deletion merge tree 各自 fresh-main 全绿；deletion terminal≤720、
净删≥2,918；一次性 rollback worktree 实际 revert deletion merge 后 legacy route 可用，再回到 deletion
fresh-main 重验关键证据。

## 4. T61A 证据合同

唯一 proof code：`scripts/program_bounded_stage_t61a.py`，目标≤170 physical LOC、硬上限200，
每函数≤50行。唯一机器生成基线：
`.ai-sdlc/work-items/215-programservice-bounded-stage-reduction-implementation/t61a-legacy-baseline-receipt.json`。
不得新增第二套 harness、snapshot schema、依赖或产品模块。

RC-06 的 proof 硬上限290，是全部新增手写 test/harness/normalizer 总和，不是 recorder
单文件额度。Manifest inventory assertion 机械替换按 diff 新增行计费；双 GO 后 candidate unit/CLI seam
与任何其他 test/helper/normalizer 的全部新增行共同使用剩余额度，最终总和必须≤290。现有测试/fixture
不重复计费。T61A actual current proof只计recorder与manifest机械新增行；future reserve固定为90行：

| 文件 / symbol | 职责 | 自然 LOC |
|---|---|---:|
| `tests/conftest.py::_program_three_way_route` | test-only route/root fixture与产品不可见断言 | 8 |
| `tests/integration/test_cli_program.py::THREE_WAY_STAGE_CASES` | 九stage及fault/sentinel case data | 10 |
| `::_three_way_leaf_command` | 三腿isolated命令、非递归selector与路径 | 12 |
| `::_run_three_way_leg` | 同根reset、child执行、JUnit/raw/provenance采集 | 12 |
| `::_assert_three_way_provenance` | cwd/HEAD/tree/interpreter/module/source/route断言 | 10 |
| `::_capture_three_way_case` | 复用165节点并补fault/termination/sentinel/network语义ledger | 16 |
| `::_assert_three_way_equal` | §4.2行为、raw、write-order与ledger零差异 | 10 |
| `::_sample_three_way_performance` | T61B warm-up+20同机三腿duration/p50/p95 | 6 |
| `::test_program_bounded_stage_three_way_{supplemental,replay}` | supplemental与outer入口 | 6 |

Recorder>200、总proof>290、`466+actual current proof+90>729`，或后续自然实现超过上述逐symbol reserve且
product shadow无法等量下降，即T61A/T61B NO-GO；
禁止压行、DSL、动态 fallback 或拆分第二脚本规避预算。

T61A recorder 只输出编码前不可变基线：

1. exact legacy commit/tree、formal/source/dependency/toolchain hashes；
2. 45-symbol、LOC/executable/header/branch、call/test inventory；
3. 27 public callable 的 `inspect.signature`、每个 parameter 的 name/kind/default/annotation、return
   annotation、raw `__annotations__`、`__doc__`、module/qualname；27 DTO 的
   module/qualname、`dataclasses.fields` name/type/default/default_factory/order、dataclass equality，以及
   `__post_init__` presence/module/qualname/signature/source SHA-256；任一字段缺失或不可读取均fail-closed；
4. exact 165 ordered node IDs、两份目标测试、实际`conftest`/seed-helper/config文件hash，以及两个独立
   `--basetemp`的命令、exit/stdout/stderr和165/165 PASS；tests section同时按§4.2 anchored primary-stage
   grammar冻结九组exact node IDs/计数，并冻结18个file-qualified seed helper的`inspect.getsource` UTF-8
   SHA-256；不构造逐node transitive AST mapper；
5. 既有selector characterization的warm-up与20个原始duration、nearest-rank p50/p95；T61B三方同机重采；
6. recorder/proof LOC、candidate shadow、逐任务future proof reserve、组合门和工作树前后不变证明。

Exact165在T61A只作为冻结的整体回归基线：ordered node IDs、目标test blob、实际fixture/helper/config blob
和双basetemp命令共同绑定。不得只保存“165 passed”摘要，也不得在T61A重复实现测试已经覆盖的行为。
动态loader/builder/direct/CLI、late-bound、fault/termination、transient sentinel与raw tree矩阵移到§4.2三方
replay；这是阶段迁移，不是删除验收。

Recorder只有`record`与`verify`两个用户模式。`record`生成唯一canonical receipt；`verify`只读重算
identity、inventory、surface/DTO、ordered nodes、blob hash、section hash与预算，不重写receipt。Schema固定为
`program-bounded-stage-t61a.v2`，顶层只含`schema_version`、`outcome=pass|no_go`、`error`、`sections`。
`pass ↔ error=null`、`no_go ↔ error为非空string`双向唯一；其他组合均invalid。
Section全序固定为`identity → structure → tests → performance → budget`；每个已取得section只含
JSON-primitive payload与SHA-256。`pass`必须精确包含五项；`no_go`只允许空集或该全序的严格前缀，
禁止跳项、混合或未知key。
内容hash使用Python3.11 `json.dumps(... ensure_ascii=False, allow_nan=False, sort_keys=True,
separators=(",", ":"))`的UTF-8 bytes；receipt file hash由外部review envelope计算。

Pass必须五section齐全且hash复算一致、两个basetemp均165/165、工作树前后不变、recorder/proof/combined预算
全部通过，并且进程exit 0。可清理失败以同schema原子写`outcome=no_go`、非空error和已取得的严格前缀
sections后非零退出；每个已取得section仍须hash复算一致。`verify`遇有效no_go必须保持no_go并非零退出，
不得补算缺项或升级pass；缺失、损坏、跳项、未知key、混合状态同样非零退出。不可清理进程死亡由外部
envelope记录exit/signal与现存文件hash。临时文件必须创建在target parent同一文件系统；原子顺序固定为
temp write→flush→file fsync→replace→平台支持时parent-directory fsync。任一步失败都非零退出并由外部
envelope裁决，不能保留或接受PASS结论；不允许
使用产品私有writer证明自身安全。Receipt只保存JSON primitive/list/object，不保存任意产品对象，因此不引入
第二套typed canonicalizer、normalizer或receipt状态机。

### 4.2 下沉动态矩阵与三方 replay

每个stage RED/GREEN、T61B、默认selector切换前和deletion前，动态矩阵必须三方运行：

1. 在隔离只读worktree执行T61A冻结的原始legacy commit/tree；
2. 在candidate checkout执行current legacy route；
3. 在同一candidate checkout执行candidate route。

三方使用byte-identical seed并比较loader/builder、direct/full-CLI、confirmation/outside-root/help/mode、
request/result/exception/trace、raw tree/bytes/mode/size/hash/write order、late-bound truthiness/clock、fault/
`SystemExit`/`KeyboardInterrupt`/process termination、partial-tree/retry、repo/sibling/outside transient sentinel及
subprocess/network ledger。原始legacy是独立历史oracle；任何未批准差异立即NO-GO，防止current legacy与
candidate因共享facade/glue回归而“同错同过”。这些矩阵从T61A移到最早能观察新代码的阶段，不得省略、
推迟到合并后或只比较current legacy/candidate两方。

唯一outer node固定为`tests/integration/test_cli_program.py::test_program_bounded_stage_three_way_replay[<stage>]`，
唯一补充node固定为同文件`::test_program_bounded_stage_three_way_supplemental[<stage>]`。
`_three_way_leaf_command`不是测试/runner层；它只构造一次pytest worker命令，直接选择冻结的existing nodes与
supplemental node，必须显式`-p no:cacheprovider`且不得选中outer。Outer输入固定为test-only环境变量
`AI_SDLC_THREE_WAY_{ORIGINAL,CURRENT_LEGACY,CANDIDATE,EVIDENCE,BEHAVIOR}_ROOT`及每腿独立的
`AI_SDLC_THREE_WAY_<LEG>_{COMMIT,TREE}`；
leaf只读取`AI_SDLC_TEST_PROGRAM_ROUTE=original|legacy|candidate`。产品代码不得读取这些变量。

Outer依次使用`uv run --isolated --project <leg-root> --python 3.11 python -I -m pytest`执行三条worker命令；
每腿cwd、project与expected commit/tree必须指向对应worktree，禁止复用共享或指向另一腿的editable path。
每条命令必须同时使用`-o pythonpath=<leg-root>/src --import-mode=importlib`，禁止candidate root的pytest
`pythonpath=["src"]`污染original/current-legacy产品导入；`_three_way_leaf_command`必须生成并断言这两个参数。
Supplemental node在矩阵前fail-closed记录并断言cwd、HEAD/tree、`sys.executable`、`ai_sdlc.__file__`、
`program_service.__file__`、`program_cmd.__file__`及三份source SHA-256和effective route marker；模块路径必须
位于指定leg root，任一不符先于行为比较失败。

三腿复用同一个绝对behavior seed/output root，并在每腿前byte-identical reset，因此比较策略固定为
`same-absolute-root-v1`且不使用normalizer。各腿使用独立basetemp/JUnit/raw capture目录；命令、exit/stdout/
stderr和raw artifact写入调用者指定的未跟踪evidence root。Pytest原生`--junitxml`是机器结果载体，task log
只登记命令及JUnit/raw tree SHA-256，不自造第二schema。Outer内部比较§4.2完整行为矩阵；provenance按各腿
expected identity验真但不混入行为zero-delta。

Worker不得调用pytest test function或再次启动pytest。它从T61A receipt读取ordered node IDs，并用以下
anchored primary-stage grammar唯一分组。Record与verify在分组前都必须先断言输入集合精确来自
`... and not thread_archive and not project_cleanup`的T61A selector，且任一node ID含`thread_archive`或
`project_cleanup`立即NO-GO；之后unit node匹配
`::test_(build|execute|write)_frontend_<stage>(_|$)`；integration node匹配
`::TestCliProgram::test_program_<stage>(_|$)`。冻结计数依次为cross-spec `10+6=16`、guarded `12+7=19`、
broader `12+7=19`、final governance `12+7=19`、persistence `12+7=19`、persisted proof `12+7=19`、
publication `12+8=20`、closure `12+5=17`、archive `12+5=17`；九组disjoint union必须精确等于有序
`106 unit + 59 integration = 165`。每stage worker选择截至当前stage的累计exact IDs并追加对应supplemental
nodes；T61B选择exact165并追加九个supplemental nodes。

三腿运行candidate checkout中相同的测试定义，但分别通过各自`<leg-root>/src`加载产品。每腿JUnit必须与
本轮expected existing/supplemental node IDs逐项相等且全部passed；missing/extra/skip/xfail/duplicate均NO-GO。
零新增LOC复用职责固定为：106个unit selector中的`test_build_frontend_<stage>_request_*`覆盖builder/request/
confirmation/input，`test_execute_frontend_<stage>_*`覆盖direct/result/block/exception/write-order/retry，
`test_write_frontend_<stage>_artifact_*`覆盖raw YAML/tree/bytes；59个integration selector中的
`TestCliProgram::test_program_<stage>_*`覆盖full CLI/help/dry-run/execute/exit/stdout/stderr/artifact。

Seed helper来源固定为`tests/unit/test_program_service.py`和`tests/integration/test_cli_program.py`两个文件中
各自同名的以下九个module-level symbol，并按T61A receipt逐symbol source SHA验真：
`_write_frontend_cross_spec_writeback_artifact`、`_write_frontend_guarded_registry_artifact`、
`_write_frontend_broader_governance_artifact`、`_write_frontend_final_governance_artifact`、
`_write_frontend_writeback_persistence_artifact`、`_write_frontend_persisted_write_proof_artifact`、
`_write_frontend_final_proof_publication_artifact`、`_write_frontend_final_proof_closure_artifact`、
`_write_frontend_final_proof_archive_artifact`。Supplemental node只调用`_capture_three_way_case`，不得调用任何
test function或嵌套pytest；capture只补existing nodes未输出的late-bound clock/truthiness、fault/termination/
retry、sentinel、subprocess/network ledger并交给comparator；性能只由`_sample_three_way_performance`承担。

Deletion current-head与deletion fresh-main不再假设已删除的current legacy存在；三腿固定为T61A原始legacy、
冻结pre-deletion candidate-merge worktree的current legacy route、deletion-head/fresh-main candidate route。
三者使用同一runner、seed和完整矩阵，merge前后均须零未批准差异。

Formal hash 冻结为两个互不混淆的值。`wi196_wi213_formal_six_sha256` 完全复用 WI213 plan §8：
WI196 与 WI213 各自 `spec.md/plan.md/tasks.md` 六文件按 repo-relative path ordinal 升序，每行写
`<lowercase file sha256><two spaces><repo-relative path>\n`，对含最后 LF 的 UTF-8 payload 做 SHA-256。
`wi215_formal_three_sha256` 对 WI215 `spec.md/plan.md/tasks.md` 使用同一算法和排序。原始文件 bytes 不改
换行。Readiness tuple 必须分列 legacy/proof commit 与 tree，禁止用单个 `HEAD/tree` 或含糊的
`formal combined` 代替。

T61A structure section只使用稳定文本/数字/布尔表示signature、annotation/default/doc与DTO字段；不得使用
`repr()`中的对象地址、`id()`或bytecode fallback。`default_factory`只允许`MISSING`、typed literal、
source-backed callable fingerprint及当前`builtins.list/dict`。未知值或DTO hook source不可读即fail-closed。

## 5. Reduction Contract 绑定

| 合同 | 本 WI 执行值 |
|---|---|
| RC-01/02 | 45 methods=`3,638 physical / 3,305 executable / branch 386`；165 tests=`106 unit + 59 CLI` |
| RC-03/05 | private module≤360；binding/import/selector glue≤90；candidate route/facade≤72；peak product≤522 |
| RC-04 | terminal≤720；净删≥2,918；ProgramService responsibility reduction≥3,278；terminal branch≤90 |
| RC-06 | recorder≤200；proof≤290；product+proof≤729；个别上限不替代组合硬门；既有测试/fixture 不重复计费 |
| RC-07 | 一个 private module；新/修改函数≤50；公共抽象/依赖=0 |
| RC-09 | 任一超限、差异、不确定恢复、双 GO 缺失或范围扩张即 NO-GO，保留 legacy |
| RC-10 | T61A、candidate、stability、deletion、rollback 均绑定 commit/tree/hash/raw evidence |

当前 T61A candidate shadow 收紧为 private engine 330、binding/glue 85、candidate route/facade 51，
peak product=`466≤522`；其中glue采用WI213已证明机械下界的保守上沿85。Terminal shadow=
`225 header + 42 facade + 85 glue + 330 engine = 682≤720`，预计净删2,956。T61A门禁使用
`candidate_product_shadow + actual_current_proof + reserved_future_proof≤729`：
actual计入当前全部新增test/harness/normalizer和manifest机械新增行，reserved逐文件/任务冻结双GO后尚需的
candidate seam/helper/normalizer固定90行；实际超过时product shadow必须等量下降，否则NO-GO。T33改用
`actual_peak_product + actual_total_proof≤729`。若proof增加，product shadow/actual必须等量下降；个别hard
cap相加不是获准预算。
该预测只用于 readiness；实际自然格式化若超限，不得通过晦涩压缩、反射或缩减场景保留 GO。

## 6. 功能需求

- **FR-001**：T61A 与双 readiness GO 必须发生在任何 `src/**` 或目标行为测试差异之前；只允许 §1 的
  manifest inventory assertion 机械替换。
- **FR-002**：proof harness 必须单文件≤200 LOC、无新依赖，并由机器生成唯一 receipt；全部 proof
  新增行≤290。
- **FR-003**：recorder必须fail-closed实现§4.1最小基线；§4.2动态矩阵必须在每stage/T61B按原始legacy/
  current legacy/candidate三方执行，不能从任务中删除。
- **FR-004**：最终 readiness identity 必须 committed+clean，按 §4 分列全部 commit/tree/hash，且两 reviewer
  tuple 完全相同。
- **FR-005**：candidate 只允许 WI213 §4.1 的一个 private module和九组显式 typed/path binding。
- **FR-006**：candidate 必须逐 stage TDD；默认 legacy，T61B 前不得切默认 candidate。
- **FR-007**：T61B必须以T61A冻结原始legacy为独立oracle，三方比较surface、late-bound、raw bytes/tree/
  trace/异常/性能，未批准差异为0。
- **FR-008**：candidate PR 合入时 legacy 完整保留；selector rollback/reapply 必须真实运行。
- **FR-009**：稳定周期必须覆盖 required CI、wheel/sdist、两个 no-index clean install、offline smoke、
  至少两个有选择理由的 sibling project。
- **FR-010**：deletion 必须独立 branch/PR，且只有稳定周期全绿后创建。
- **FR-011**：deletion 后必须实际 revert 精确 merge commit，再回到 deletion fresh-main 重验。
- **FR-012**：candidate/deletion 任一失败按 selector→deletion→candidate 的安全顺序恢复 legacy。
- **FR-013**：T66 完成只更新 GAP-03 ledger；WI196/RC-08/release 继续 open。
- **FR-014**：receipt/raw evidence 总量≤2 MiB；每个冻结 CC 场景 snapshot≤2。
- **FR-015**：任何 reviewed source 变化使两位 reviewer 的旧 verdict 同时失效。

## 7. 成功标准

- **SC-001**：T61A proof identity 上 `src/**` 零差异、目标测试 blob 不变、manifest test 仅机械数字
  替换、recorder≤200、总 proof≤290、`candidate_product_shadow + actual_current_proof +
  reserved_future_proof≤729`且reserved=90、双basetemp 165/165通过、最小baseline receipt PASS，双 readiness GO。
- **SC-002**：candidate peak product≤522、`actual_peak_product + actual_total_proof≤729`、T61B zero-delta、
  full/governance/跨平台 checks 全绿，legacy 保留。
- **SC-003**：稳定期 package/offline/sibling/selector 全绿后才启动 deletion。
- **SC-004**：deletion terminal≤720、净删≥2,918、responsibility reduction≥3,278、branch≤90。
- **SC-005**：deletion merge/fresh-main 和 actual rollback receipt 全绿后才关闭 T66；不提前发布。

## 8. NO-GO 与回退

以下任一成立立即 `NO-GO`：45/3,638/3,305/386 或 165 库存无法解释漂移；recorder>200；proof>290；product>522；
T61A的`candidate_product_shadow + actual_current_proof + reserved_future_proof>729`；candidate/T33的
`actual_peak_product + actual_total_proof>729`；
需要第二模块/DTO迁移/CLI改动/新依赖/公共开关；surface不可稳定表示；三方动态矩阵任一差异；任一reviewer
非GO。Recorder可清理失败必须先原子写同schema no_go receipt；不可清理死亡只由外部envelope保存
exit/signal与现存文件hash，不能伪造recorder receipt。Reviewer NO-GO在独立review envelope/执行日志保存，
不得回写并改变已受审 receipt。

Candidate 已存在时先 selector 回 legacy；deletion 已合入时先 revert deletion 恢复 legacy；必要时再
revert candidate。任何回退都不得删除唯一 T61A/T61B evidence。
