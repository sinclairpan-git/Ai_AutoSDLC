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
receipt file hash、stable behavior hash 与 observed-performance hash 均签发 readiness `GO` 前，
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
- T61A legacy recorder、versioned Python surface、双根 direct/CLI、late-bound dispatch、故障/恢复、
  raw tree/bytes/mode、side-effect sentinel，以及一个可重放 direct+CLI composite 的 20 次 p50/p95 样本。
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

作为框架维护者，我希望在任何产品改动前得到单一、可执行、版本化的 T61A receipt，使 reviewer 能证明
当前 45-method legacy 的行为、surface、副作用和性能是稳定且可比较的。

**独立测试**：在 clean proof commit 上先 `record`、后 `verify`；`src/**` diff=0、两份目标测试 blob
不变、manifest test 仅机械替换 inventory/close 数字，165 个既有测试精确通过，双根与矩阵全部
zero-delta。`verify` 重放稳定行为区并复算相同 behavior hash；性能观测区保留一次 `record` 的 20 个
direct+CLI composite 原始样本、component duration 与独立 hash，不要求跨运行 duration 或整份 receipt 相同。

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

唯一 proof code：`scripts/program_bounded_stage_t61a.py`，目标≤230 physical LOC、硬上限250，
每函数≤50行。唯一机器生成基线：
`.ai-sdlc/work-items/215-programservice-bounded-stage-reduction-implementation/t61a-legacy-baseline-receipt.json`。
不得新增第二套 harness、snapshot schema、依赖或产品模块。

RC-06 的 proof 目标≤263、硬上限290，是全部新增手写 test/harness/normalizer 总和，不是 recorder
单文件额度。Manifest inventory assertion 机械替换按 diff 新增行计费；双 GO 后 candidate unit/CLI seam
与任何其他 test/helper/normalizer 的全部新增行共同使用剩余额度，最终总和必须≤290。现有测试/fixture
不重复计费。Recorder>250、总 proof>290，或后续最小 seam 无法留在总额内即 T61A/T61B NO-GO；
禁止压行、DSL、动态 fallback 或拆分第二脚本规避预算。

Recorder 必须输出：

1. exact legacy commit/tree、formal/source/dependency/toolchain hashes；
2. 45-symbol、LOC/executable/header/branch、call/test inventory；
3. 27 public callable 的 `inspect.signature`、每个 parameter 的 name/kind/default/annotation、return
   annotation、raw `__annotations__`、`__doc__`、module/qualname 与 deterministic behavior digest；27 DTO 的
   module/qualname、`dataclasses.fields` name/type/default/default_factory/order、dataclass equality，以及
   `__post_init__` presence/module/qualname/signature/source SHA-256/deterministic behavior digest；任一字段
   缺失、不可读或不可 canonicalize 均 fail-closed；
4. 九 private loader 的 missing/malformed/non-mapping/empty/valid baseline；builder 的 missing/empty/valid/
   invalid upstream state 与 empty/valid/invalid steps；
5. 九 stage direct/CLI 双根逐项覆盖 confirmation allowed/required/denied、inside/outside-root、help、mode、
   expected failure 与 full-chain；记录 request/result/exception/trace、stdout/stderr、artifact/report raw bytes、
   tree/mode/size/hash 与写入顺序；public callable surface 必须逐字段记录 parameter kind/name/type/default、
   return type、module/qualname 和确定性 behavior digest；
6. execute/writer 对 `self.build_*`/`self.execute_*` 的 `None/truthy/falsey`、clock
   `None/""/fixed truthy` late-bound matrix；
7. builder/executor/payload/step/artifact/renderer/report exception、`SystemExit`、process termination 与
   `KeyboardInterrupt` partial-tree/retry；
8. repo/sibling/outside sentinel 和 subprocess/network 空调用账本；sentinel 只包围 seed 完成后的 direct/CLI
   被测调用窗口，proof 自身的 pytest/git/toolchain 采集在窗口外独立记录，不得混入产品副作用账本；
9. 一个可重放 composite 每次顺序包含代表性 direct-service 与 full-CLI 链；warm-up 后运行≥20次，
   每次保留 direct/CLI component 和 total 原始 duration，并计算 nearest-rank p50/p95；
10. architecture ledger、proof LOC、全部命令/退出码和 readiness invariants。

现有165 tests只能按`requirement ID -> exact pytest node ID -> test function source SHA-256 -> transitive
seed/helper/fixture source SHA-256 set -> asserted outcome`逐项复用。Transitive set必须包含该node实际调用的
source-backed helper、seed writer、fixture与`conftest` autouse hook；任一动态调用或依赖无法精确绑定时，
该node不得计入coverage。Receipt必须保存该mapping及命令结果；不得用“165 passed”替代任何没有精确
断言的合同。既有fixture writer只负责seed，不调用`test_*`。Recorder仍必须自行保存45-symbol/AST、
27 public/27 DTO canonical surface、九loader五态、双根direct/full-CLI raw、九组late-bound/clock、
未被精确覆盖的fault、termination/retry、sentinel/network/subprocess、20 composite及schema/hash/NO-GO证据。

Recorder 只有两个模式：`record` 一次生成 outcome-conditioned receipt；成功时包含完整
`stable_behavior` 与原始 `observed_performance`，失败时按下述 section 状态保留截至失败点的证据。
`verify` 对 pass receipt 重放稳定行为矩阵并比较 `stable_behavior_sha256`，不重采或改写性能样本；对 no_go
receipt 只校验 schema、完成前缀和非空 section hash，保持非零退出且绝不重放或升级。
`observed_performance_sha256` 对选定一次 record 的原始 composite 样本区单独计算；整份 receipt file hash
仅绑定最终证据文件，不要求另一轮运行重现。任何 section 都不得归一化 duration。

“唯一 receipt”指唯一 recorder、唯一 schema，以及每个 T61A identity 至多一份 committed canonical
receipt。每次`record` invocation只能产生一个authoritative receipt。Canonicalization和unexpected-
termination负向验收分别运行独立`record` invocation并写调用者指定的临时同-schema NO-GO receipt；这些
临时receipt不提交、不覆盖canonical baseline，其hash只进入外部review envelope/执行日志。
Pass只在当前invocation的authoritative pass receipt校验成功且recorder进程exit code=0时成立；任一非零/
signal退出均不得接受为pass，即使磁盘上已有`ready_for_review` receipt。若存在有效`closed_no_go` receipt，
外部envelope登记closed NO-GO；否则必须记录exit/signal、任何现存文件原始hash与`unclosed_no_go` disposition。

行为根预算按invocation计算：每次`record`及pass `verify`恰好创建root-A/root-B两个behavior root；
sacrificial child必须继承且只操作这两根，不得创建第三个项目、retry或child sandbox root。独立负向
`record`可创建自己的root-A/root-B；no_go `verify`不重放行为并创建零behavior root。Receipt、IPC、
toolchain和evidence目录不是behavior root，也不得进入normalizer替换；normalizer只替换当前调用的两根。

唯一 receipt schema 的顶层必须包含 `schema_version=program-bounded-stage-t61a.v1`、逐字冻结的
`required_check_ids`、`outcome=pass|no_go`、`failure_phase`、ordered `completed_checks`、canonical
`error={type,message}|null`、`verdict=readiness_candidate|no_go`、
`closure=ready_for_review|closed_no_go` 和 `sections`。三个 section 均为
`{status:not_started|partial|complete,payload:null|object,sha256:null|lowercase_hex}`：

- pass：`outcome=pass`当且仅当failure/error为null、`verdict=readiness_candidate`、
  `closure=ready_for_review`，三个section均complete且payload/hash非空；performance payload精确含warm-up
  标识及20个direct/CLI component+total integer-nanosecond样本；
- no_go：`outcome=no_go`当且仅当failure/error非空、`verdict=no_go`、`closure=closed_no_go`；
  raw_evidence必须partial或complete且payload/hash非空；stable/performance可为
  not_started（payload/hash均null）、partial或complete（payload/hash均非空），其status必须与ordered
  completed_checks和failure_phase一致；不得伪造未完成section；
- verify必须拒绝任何pass/no_go字段混合、缺失/重复/改序required check或未知schema version；
- 外部reviewer verdict写独立review envelope，避免receipt自绑定。

三个内容hash共用`canonical_json_sha256(payload)`：先把所有产品mapping按原始迭代顺序编码为唯一
`{"$type":"mapping","entries":[{"key":...,"value":...}]}`，禁止排序entries；schema控制对象保持普通
JSON object，两者边界由字段类型固定，不允许裸entry数组作为mapping的第二表示。再对schema对象执行Python 3.11
`json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))`，将结果直接
UTF-8编码、无BOM、无末尾LF并做SHA-256。`stable_behavior_sha256`、`observed_performance_sha256`、
`raw_evidence_sha256`分别只输入对应section payload；not_started的hash必须为null。Duration使用integer
nanoseconds，禁止NaN/Infinity。Receipt file SHA继续由review envelope对最终文件原始bytes外部计算。

进入上述JSON前必须递归编码为唯一值域：null/bool/int/finite-float/string保持原类型；list保持原顺序；
mapping编码为`{"$type":"mapping","entries":[{"key":...,"value":...}]}`并保持迭代顺序；tuple编码为
`{"$type":"tuple","items":[...]}`；bytes编码为`{"$type":"bytes","hex":"<lowercase-even-hex>"}`；
`Path`编码为`{"$type":"path","value":"<exact-string-after-allowed-root-substitution>"}`，除双根替换外不做
resolve、separator或大小写归一化；exception编码module/qualname、
递归args与逐字message；type/callable/default/annotation只允许本节既有source-backed/builtin fingerprint并加
明确`$type`。`$type`出现在用户mapping中仍作为普通entry key，不得与tag混合。未知对象、非有限float、
地址型repr或不可逆编码全部fail-closed。T61A必须用非UTF-8 bytes、Path、tuple、exception args做往返与hash复算。

Schema version固定为`program-bounded-stage-t61a.v1`。`required_check_ids`必须逐字等于以下全序：
`identity_toolchain, inventory, public_surface, dto_surface, loader_builder, direct_service, cli,
late_bound_clock, fault_recovery, sentinel_side_effect, performance_composite, architecture_budget,
legacy_tests, command_receipts, readiness_invariants`。Pass的`completed_checks`必须等于完整列表；no_go必须是
严格前缀，`failure_phase`必须等于列表中首个未完成ID，禁止自定义/跳过ID。

Section transition按已完成前缀长度`n`机验：stable在`n=0`为not_started/null，`1≤n<10`为partial，
`n≥10`为complete；performance在`n<10`为not_started/null；`n=10`且尚未进入performance check时为
not_started，进入后到check ID原子追加前一律partial，允许warm-up已完成且正式sample_count=`0..20`，
包括第20个样本后汇总/hash失败；`n≥11`为complete。Raw在`n<14`为partial，`n≥14`
为complete。Partial/complete必须有payload/hash，not_started必须均为null。Pass必须`n=15`且三section
complete；no_go必须`0≤n<15`并严格满足转换表。每个check只在全部子项成功后原子追加ID，因此遗漏任一
§4子项都不能合法完成对应check；`verify`必须内置同一version/list/table，不能信任receipt自报顺序。

Performance composite 的direct、CLI和total三段必须由同一父进程使用`time.perf_counter_ns()`成对采集；
顺序固定为total-start、direct-start/end、CLI-start/end、total-end。每段duration必须非负，且
`total_ns >= direct_ns + cli_ns`（允许固定测量开销）；wall clock、child自报duration或混用计时源均fail-closed。

`fault_recovery`必须区分expected sacrificial-child probe与unexpected termination。Expected probe必须由
持有receipt输出责任的recorder parent在启动child前生成唯一invocation nonce，并冻结声明injection ID、
phase、kind=`SystemExit|KeyboardInterrupt|process_termination`、nonce-bound marker、允许的exit code/signal、
post-marker stdout/stderr/EOF和behavior root。Child先完成产品fault callback，再经IPC发送canonical marker；
marker与harness-owned真实termination必须相邻，中间不得再执行产品callback或输出额外bytes。Parent记录实际
transcript、退出与partial tree，并在fresh child中使用相同两根
完成deterministic retry。声明、marker、phase、退出、partial evidence和retry全部匹配时，该probe是
`fault_recovery`成功子项，可进入pass receipt，不属于同进程吞掉termination。

任何未声明退出、marker缺失、kind/phase/exit不匹配、timeout、partial evidence缺失、retry失败、正常矩阵或
performance worker非预期退出，均为unexpected termination。仍存活且持有receipt输出责任的supervisor
必须按当前completed-check严格前缀原子写`closed_no_go` receipt并非零退出；用于负向验收的固定注入点为
`fault_recovery`，其completed checks截止`late_bound_clock`、stable/raw为partial、performance为
not_started。持有receipt输出责任的supervisor不得作为sacrificial child。Supervisor自身被`SIGKILL`、
`os._exit`或等价不可清理终止时不承诺死后写盘；外部调用者必须把非零/信号退出且缺少authoritative
`closed_no_go` closure视为unclosed NO-GO；即使已有pass receipt也绝不得接受为pass。原子持久化失败时
保留原异常并非零退出。

Formal hash 冻结为两个互不混淆的值。`wi196_wi213_formal_six_sha256` 完全复用 WI213 plan §8：
WI196 与 WI213 各自 `spec.md/plan.md/tasks.md` 六文件按 repo-relative path ordinal 升序，每行写
`<lowercase file sha256><two spaces><repo-relative path>\n`，对含最后 LF 的 UTF-8 payload 做 SHA-256。
`wi215_formal_three_sha256` 对 WI215 `spec.md/plan.md/tasks.md` 使用同一算法和排序。原始文件 bytes 不改
换行。Readiness tuple 必须分列 legacy/proof commit 与 tree，禁止用单个 `HEAD/tree` 或含糊的
`formal combined` 代替。

Normalizer在`record`与pass `verify`中只允许两个行为临时根，substitution table必须精确为root-A/root-B；
no_go `verify`创建零行为根且substitution table必须为空。只可把当前调用两根的精确绝对前缀替换为
`<root-a>`/`<root-b>`，以及把 clock spy 证明来自默认时钟的值替换为 `<clock>`；必须保留 clock 次数/顺序。
禁止排序产品 key/list、改 whitespace/newline/path
separator、用时间正则、去重、删字段或模糊异常文本。

Callable default 只允许 `MISSING`、typed literal 或 source-backed callable fingerprint；
`default_factory` 仅额外允许 `builtins.list/dict`。未知 callable、地址型 repr、DTO hook source 不可读均
fail-closed，禁止 bytecode fallback。Public facade 不比较 body/source，DTO hook 因合同禁止修改而比较 source。

## 5. Reduction Contract 绑定

| 合同 | 本 WI 执行值 |
|---|---|
| RC-01/02 | 45 methods=`3,638 physical / 3,305 executable / branch 386`；165 tests=`106 unit + 59 CLI` |
| RC-03/05 | private module≤360；binding/import/selector glue≤90；candidate route/facade≤72；peak product≤522 |
| RC-04 | terminal≤720；净删≥2,918；ProgramService responsibility reduction≥3,278；terminal branch≤90 |
| RC-06 | recorder≤250；proof≤290；product+proof≤729；个别上限不替代组合硬门；既有测试/fixture 不重复计费 |
| RC-07 | 一个 private module；新/修改函数≤50；公共抽象/依赖=0 |
| RC-09 | 任一超限、差异、不确定恢复、双 GO 缺失或范围扩张即 NO-GO，保留 legacy |
| RC-10 | T61A、candidate、stability、deletion、rollback 均绑定 commit/tree/hash/raw evidence |

当前 T61A candidate shadow 收紧为 private engine 330、binding/glue 85、candidate route/facade 51，
peak product=`466≤522`；其中glue采用WI213已证明机械下界的保守上沿85。Terminal shadow=
`225 header + 42 facade + 85 glue + 330 engine = 682≤720`，预计净删2,956。T61A门禁使用
`candidate_product_shadow + actual_current_proof + reserved_future_proof≤729`：
actual计入当前全部新增test/harness/normalizer和manifest机械新增行，reserved逐文件/任务冻结双GO后尚需的
candidate seam/helper/normalizer非负行数且不得为满足门禁而记0。T33改用
`actual_peak_product + actual_total_proof≤729`。若proof增加，product shadow/actual必须等量下降；个别hard
cap相加不是获准预算。
该预测只用于 readiness；实际自然格式化若超限，不得通过晦涩压缩、反射或缩减场景保留 GO。

## 6. 功能需求

- **FR-001**：T61A 与双 readiness GO 必须发生在任何 `src/**` 或目标行为测试差异之前；只允许 §1 的
  manifest inventory assertion 机械替换。
- **FR-002**：proof harness 必须单文件≤250 LOC、无新依赖，并由机器生成唯一 receipt；全部 proof
  新增行≤290。
- **FR-003**：recorder 必须 fail-closed 实现 §4 全部证据与 durable NO-GO，不能用 165 tests 替代新增矩阵。
- **FR-004**：最终 readiness identity 必须 committed+clean，按 §4 分列全部 commit/tree/hash，且两 reviewer
  tuple 完全相同。
- **FR-005**：candidate 只允许 WI213 §4.1 的一个 private module和九组显式 typed/path binding。
- **FR-006**：candidate 必须逐 stage TDD；默认 legacy，T61B 前不得切默认 candidate。
- **FR-007**：T61B 必须比较 T61A surface、late-bound、raw bytes/tree/trace/异常/性能，未批准差异为0。
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
  替换、recorder≤250、总 proof≤290、`candidate_product_shadow + actual_current_proof +
  reserved_future_proof≤729`、165/165 通过、全部矩阵 PASS，双 readiness GO。
- **SC-002**：candidate peak product≤522、`actual_peak_product + actual_total_proof≤729`、T61B zero-delta、
  full/governance/跨平台 checks 全绿，legacy 保留。
- **SC-003**：稳定期 package/offline/sibling/selector 全绿后才启动 deletion。
- **SC-004**：deletion terminal≤720、净删≥2,918、responsibility reduction≥3,278、branch≤90。
- **SC-005**：deletion merge/fresh-main 和 actual rollback receipt 全绿后才关闭 T66；不提前发布。

## 8. NO-GO 与回退

以下任一成立立即 `NO-GO`：45/3,638/3,305/386 或 165 库存无法解释漂移；recorder>250；proof>290；product>522；
T61A的`candidate_product_shadow + actual_current_proof + reserved_future_proof>729`；candidate/T33的
`actual_peak_product + actual_total_proof>729`；
需要第二模块/DTO迁移/CLI改动/新依赖/公共开关；surface无法 canonicalize；normalizer 越权；双根、异常、
中断、重试、side-effect 或 raw bytes 不稳定；任一 reviewer 非 GO。除§4定义的supervisor不可清理死亡外，
NO-GO 必须先保存不可变 receipt、identity 和 verdict，然后停止产品路线，legacy 保持不变；不可清理死亡
只能由外部envelope保存exit/signal、现存文件hash与`unclosed_no_go` disposition，不能伪造recorder receipt。
Recorder 内部可清理失败必须满足 §4 的 durable
`closed_no_go` 原子落盘；reviewer NO-GO 则在独立 review envelope/执行日志保存同一 tuple 与 disposition，
不得回写并改变已受审 receipt。

Candidate 已存在时先 selector 回 legacy；deletion 已合入时先 revert deletion 恢复 legacy；必要时再
revert candidate。任何回退都不得删除唯一 T61A/T61B evidence。
