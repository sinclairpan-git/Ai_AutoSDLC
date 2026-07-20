# 任务执行日志：ProgramService Bounded Stage Reduction Implementation

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**创建日期**：2026-07-20
**状态**：T61A authoring；产品代码禁止

## 1. 固定归档规则

- 每批开始前预读constitution、WI196、WI213与本WI current formal。
- 每批记录base/HEAD/tree、范围、命令、结果、finding disposition、预算、回退和精确下一步。
- Pascal/Confucius只裁决同一committed+clean identity；任一受审source变化使两 verdict同时退役。
- T61A双readiness GO前`src/**`必须相对legacy base零差异。
- Future merge/hash不预写；实际发生后只追加到log/summary/continuity，不反写已冻结formal合同。

## 2. Batch 2026-07-20-001：Receipt fresh-main 与 WI215 初始化

- PR #164 closure receipt exact HEAD/tree=`428a316a`/`cc3c6b7f`；LEAN/SAFETY同身份PASS0，Codex
  reviewed commit `428a316a08`且无major issue，required checks全绿。
- PR #164 squash merge=`7922956d3e248a93c3190240259850ab3498ec9f`；heartbeat已删除，本地receipt
  branch保留。
- Detached fresh-main HEAD=`origin/main@7922956d`，tree=`cc3c6b7f`与reviewed tree完全相同；Python3.11
  constraints无BLOCKER、validate PASS、truth=`ready/fresh 1126/1126`、manifest exact=`1 passed in98.14s`、
  17-file scope/parity/Cursor/clean全绿。
- 验收首次并行启动不同Python版本的`uv run`时发生共享`.venv`竞争；该结果已中止作废。随后统一
  `--python 3.11`顺序重跑全部通过，未把编排竞争冒充产品失败。
- 从exact main创建worktree `.worktrees/215-programservice-bounded-stage-reduction-implementation`；
  `codex/*`分支不满足Stage-1 docs branch规则，按CLI明确提示切换为
  `feature/215-programservice-bounded-stage-reduction-implementation-docs` 后初始化成功。
- `workitem init`创建canonical四件套、sequence`215→216`与manifest entry；其保留的valid-init adapter
  写路径把Cursor `.mdc`刷为`02d9656d...e134`，已用最小patch恢复base bytes/SHA
  `d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`。
- 当前未修改`src/**`、`tests/**`、workflow、dependency、version、release。

## 3. Batch 2026-07-20-002：T61A 预审与 legacy inventory

### 3.1 双预审

- Pascal/LEAN与Confucius/SAFETY均判定generated scaffold含placeholder和错误direct-formal/workitem任务，
  必须重写后才具备readiness资格；两者均明确本轮不是最终GO。
- 两者共同收敛为“一份可执行proof harness + 一份机器生成receipt”、proof hard cap190、`src/**`零改动、
  最终同identity双GO。对harness位置经二次对账，双方均对
  `scripts/program_bounded_stage_t61a.py`回复`NO_OBJECTION`。

### 3.2 Exact legacy evidence

- legacy HEAD/tree=`7922956d3e248a93c3190240259850ab3498ec9f`/
  `cc3c6b7f7e63dd040034938ff6bb6827f067e41c`。
- ProgramService blob=`7b2ac50725136b6399b74e898f147a0b1fecd9c6`；unit test blob=
  `735b505f72c4f2cfb1a378397e4f15faa79ed219`；CLI test blob=
  `9628711ce7a41b08fd6bc92f4a6c9639ed5031f3`。
- Python=`3.11.15`、macOS=`27.0 arm64`、uv=`0.10.12`、pytest=`9.0.2`、Pydantic=`2.12.5`、
  Typer=`0.24.1`、PyYAML=`6.0.3`；`uv.lock` SHA-256=`ea8f4d3f...18b2d`，`pyproject.toml`=
  `18bd95fc...dc9cb`。
- AST复算九stage/45methods与WI213一致：request=`961/898/63`、execute=`1589/1517/72`、writer=
  `378/288/90`、payload build=`431/359/72`、payload load=`279/243/36`，合计=`3638/3305/333`；
  branch inventory=`386`，18 private外部consumer=0。
- Exact selector=`165 passed, 474 deselected in 2.57s`；两个独立`--basetemp`分别为
  `165 passed ... 2.55s`与`165 passed ... 2.57s`。
- Performance：warm-up后20个成功样本=`[3.086,3.131,3.094,3.280,3.131,3.058,3.120,3.046,
  3.084,3.056,3.042,3.133,3.048,3.047,3.048,3.067,3.180,3.062,3.047,3.054]`秒；nearest-rank
  p50=`3.062s`、p95=`3.180s`。该样本只属于本toolchain的legacy selector，不替代direct/CLI recorder
  各自性能矩阵。
- 首个PowerShell采样脚本误用保留变量`$args`，只返回uv usage且sample1退出；已明确作废，改用
  `$uvArgs`后完整重跑成功。

## 4. 当前边界与精确下一步

- 当前formal authoring尚未提交；T61A receipt、最终proof identity和readiness GO均不存在。
- 先完成formal placeholder/self-review、dependency、truth/gates并提交单一authoring commit。
- 然后按TDD创建≤190 LOC唯一recorder，生成machine receipt；任何产品代码仍禁止。
- Proof committed+clean且全部矩阵/gates通过后，才让Pascal与Confucius对同一tuple裁决GO/NO-GO。

## 5. Batch 2026-07-20-003：Authoring review Round 2 FAIL4/FAIL4 disposition

### 5.1 同轮 verdict

- Confucius/SAFETY=`FAIL4`：真实性能样本与整份receipt重复hash矛盾；child执行矩阵漏写upstream/steps/
  confirmation/outside-root/SystemExit/process termination/九CLI/sentinel窗口；formal combined集合与算法不明；
  pre-GO行为测试冻结不足。
- Pascal/LEAN=`FAIL4`：pre-close summary缺失导致truth/manifest exact不可达；recorder单独吃满190会遗漏
  candidate tests；receipt raw duration矛盾；child把双根/单一≥20样本扩张为四根/direct和CLI各20。
- 两轮均为authoring review，不是最终T61A readiness GO；所有finding成立，不拒绝或降级。

### 5.2 最小修正

- `record`一次保存stable behavior与真实performance；`verify`只读receipt并复算stable behavior hash。
  Performance使用一个可重放direct+CLI composite的20个样本，保留component/total duration与独立hash；
  整份receipt file hash只绑定最终选定证据，不要求跨运行相同。
- 每次record/verify严格只有两个行为临时根；seed/evidence/output不进入normalizer。补齐public surface逐字段、
  upstream/steps、confirmation/outside-root、九CLI help/mode/failure/full-chain、SystemExit/process termination，
  sentinel仅包围seed后的被测调用窗口。
- Formal tuple分列legacy/proof commit+tree；WI196+WI213 formal-six完全复用WI213 plan §8算法，WI215
  formal-three使用相同per-file-SHA-line算法，另列harness/receipt/stable/performance hash。
- Recorder目标≤150、hard cap≤160；manifest assertion diff新增行、双GO后candidate tests与任何helper共同
  计入总proof≤190。自然实现超限即NO-GO，不压缩语义或放宽预算。
- 新增pre-close `development-summary.md`；`src/**`和两份目标行为测试blob在双GO前不变。唯一`tests/**`
  例外是`test_repo_program_manifest.py`的inventory/close精确数字机械替换，新增行计入proof且不改逻辑/LOC。

### 5.3 验证与调试事实

- `workitem plan-check --wi 215...` 首次把ID误作路径，返回directory not found；该调用作废。改为
  `--wi specs/215-programservice-bounded-stage-reduction-implementation --json` 后exit=0、drift=false，
  Cursor SHA前后均=`d5f04acf...0b6a`。
- 新summary前manifest exact实测actual=`1131/1131/missing 1`并FAIL；补summary、机械替换期望为
  inventory=`1131/1131/0/0`、close=`215/215`后，manifest exact=`1 passed in 99.06s`。
- 第二轮review自检：target selector=`165 passed, 474 deselected in 2.88s`；constraints无BLOCKER、validate
  PASS、current `src/**`/目标测试/scripts/workflow/dependency零差异、root/scoped handoff byte-identical。
- 由于本批修订改变formal，Round 2 verdict已退役；必须让两位reviewer对新bytes重新从零审查到同轮PASS0。

## 6. Batch 2026-07-20-004：Authoring review Round 3 LEAN PASS0 / SAFETY FAIL2

- Pascal/LEAN=`PASS0`、findings=0；确认Round 2四项均关闭、预算数学闭合、manifest机械更新与边界正确。
- Confucius/SAFETY=`FAIL2`；一是Python surface仍未显式枚举raw annotations/doc及DTO hook完整字段和
  dataclass equality，二是NO-GO只有原则、没有“原子持久化失败receipt后非零退出”的可验收路径。
- 两项均成立：spec/plan/tasks已补齐public signature/parameter/return/raw annotations/doc/module/qualname/
  behavior与DTO fields/equality/post-init presence/module/qualname/signature/source/behavior；任一字段不可读即
  fail-closed。
- 唯一receipt新增outcome/failure phase/completed checks/raw evidence+hash/error/verdict/closure；
  canonicalization/matrix fault和isolated termination均须由外层temp+fsync+replace原子写`closed_no_go`
  后非零退出，verify不得升级。Reviewer verdict仍写独立envelope，避免receipt自绑定。
- 本次formal变化使Round 3 LEAN PASS0和SAFETY FAIL2同时退役；Round 4必须对新bytes重新同轮双审。

## 7. Batch 2026-07-20-005：Authoring review Round 4 LEAN PASS0 / SAFETY FAIL2

- Pascal/LEAN=`PASS0`、findings=0；确认单recorder/schema/receipt、总proof预算和durable NO-GO没有过度实现。
- Confucius/SAFETY=`FAIL2`；surface/DTO finding已关闭，但pass/no_go未冻结section条件，三个内容hash也缺
  精确JSON bytes算法，导致早期失败receipt与独立复算仍有歧义。
- 两项均成立：schema改为stable/performance/raw三个status/payload/hash section。Pass全complete；no_go的
  raw至少partial，stable/performance按failure phase为not_started/null或partial/complete非空；verify只校验
  no_go完成前缀/hash并保持非零，绝不重放或升级。
- 内容hash算法冻结为Python3.11 `json.dumps` 的UTF-8/no-BOM/no-LF、`ensure_ascii=False`、
  `allow_nan=False`、`sort_keys=True`、compact separators。产品mapping先按原顺序编码成entry数组，数组禁止
  排序；duration为integer nanoseconds。三个hash只输入各自payload，receipt file SHA仍在外部envelope计算。
- 本次formal变化使Round 4 LEAN PASS0和SAFETY FAIL2同时退役；Round 5必须对新bytes重新同轮双审。

## 8. Batch 2026-07-20-006：Authoring review Round 5 LEAN FAIL1 / SAFETY FAIL2

- Pascal/LEAN=`FAIL1`：development summary“下一步”仍写第二轮，与当前Round 5不一致；其余精简/预算/
  单schema/hash审查通过。
- Confucius/SAFETY=`FAIL2`：canonical JSON未定义bytes/Path/tuple等非JSON原生值；completed checks/failure
  phase没有version/check全序/section transition，verify无法证明strict prefix或发现漏项。
- 三项均成立：summary下一步更新为Round 6；递归值域冻结JSON primitive/list、有序mapping entries、
  tuple、lowercase-even-hex bytes、Path、exception及既有type/callable fingerprint，未知值fail-closed；新增
  非UTF-8 bytes等往返/hash验收。
- Schema version=`program-bounded-stage-t61a.v1`，冻结15个required check全序。Pass必须full list；no_go
  必须strict prefix且failure phase为首个未完成ID；stable/performance/raw status按prefix长度和样本数由固定
  transition表计算，verify内置同一表而不信任receipt自报。
- 本次formal变化使Round 5全部verdict退役；Round 6必须对新bytes重新同轮双审。

## 9. Batch 2026-07-20-007：Authoring review Round 6 LEAN FAIL2 / SAFETY FAIL3

- Pascal/LEAN=`FAIL2`：mapping同时存在裸entry数组与tagged object两种表示；performance第20样本后、check
  ID前失败无合法partial状态。
- Confucius/SAFETY=`FAIL3`：outcome未与verdict/closure双向唯一且schema version未列顶层；同一第20样本
  边界空洞；性能硬门未冻结单调计时源。
- 五项finding全部成立并最小修正：产品mapping唯一为`$type=mapping + ordered entries`，schema控制对象
  才是普通JSON object；顶层显式携带固定schema version/required list，pass/no_go与failure/error/verdict/
  closure/sections双向唯一，verify拒绝混合状态。
- Performance check进入后到ID原子追加前，warm-up完成且0～20样本都为partial；新增第20样本后、finalize
  前故障验收。Direct/CLI/total只由同一父进程`time.perf_counter_ns()`顺序成对采集，三段非负且
  total≥direct+CLI；wall clock/child自报duration fail-closed。
- 本次formal变化使Round 6全部verdict退役；Round 7必须对新bytes重新同轮双审。

## 10. Batch 2026-07-20-008：Authoring review Round 7 双 PASS0

- Pascal/LEAN=`PASS0`、findings=0；确认mapping唯一表示、performance 0～20 partial边界、单调计时、
  单recorder/schema/receipt与≤160/总≤190预算均无可操作问题。
- Confucius/SAFETY=`PASS0`、findings=0；确认Round 6三项阻断全部关闭，并主动复核canonical值域、
  state machine、NO-GO原子落盘、双根normalizer、surface/DTO/CLI/异常/sentinel/formal hash与pre-GO冻结。
- Round 7 是authoring合同准入，不是最终T61A readiness GO。由于本段与状态writeback改变受审bytes，
  Round 7 verdict退为authoring receipt；提交前必须对仅含writeback的新bytes再取得同轮双PASS0。

## 11. Batch 2026-07-20-009：Round 8 双 PASS0、formal commits 与 T61A RED

- Round 8 仅复核Round 7事实/任务writeback；Pascal/LEAN与Confucius/SAFETY同轮`PASS0`、findings=0，
  均确认未把authoring receipt冒充最终T61A GO，pre-GO边界保持锁定。
- Formal source commit=`60f1132830664504c83185d47dc452eb48c8800a`、tree=
  `8704db2cffd24607e2c2317d35424a1317fb906c`；提交后worktree clean。
- 在clean source commit执行truth sync：state=ready、snapshot=`dccdb689...914e2`、inventory=
  `1131/1131`、missing/unmapped=`0/0`、layers spec/plan/tasks/execution/close=`215/215`；机械diff只有
  `program-manifest.yaml`，truth commit=`884c2c86f8e89fcd5cb61a86a5d2248493dba7b0`、tree=
  `f052e54d9940d43f8cd45b65211f9f3822e72fb9`。
- T61A RED：`python scripts/program_bounded_stage_t61a.py record --route legacy --output <tmp>` exit=2，
  唯一失败为文件不存在，输出文件不存在；RED成立。当前仍无`src/**`/目标测试/script产品实现差异。
- 下一步只允许实现唯一≤160 LOC recorder并保持总proof≤190；receipt与最终readiness GO仍不存在。

## 12. Batch 2026-07-20-010：T61A 实现可行性对质 NO-GO 与最小 formal correction

- Pascal/LEAN最初认为150 LOC可行；Confucius/SAFETY逐项展开现有165 tests未覆盖的loader、outside-root、
  late-bound、fault/termination、sentinel、raw和performance矩阵后拒绝该估算。Pascal按实际语句重算后撤回
  原判断：自然可读实现下界约220～235 LOC，完整未复用展开约276 LOC；双方统一`NO-GO`。
- 另发现合同语义冲突：pass要求真实SystemExit/process termination/KeyboardInterrupt partial+retry，但旧条款
  又无条件要求parent观察任何termination即`closed_no_go`，同一次record无法同时满足。
- 产品代码与目标行为测试仍为零差异；未通过压行、DSL、只记pytest hash或删矩阵绕过。旧Round 7/8 authoring
  verdict因本次finding和formal bytes变化全部退役。
- 最小修正只调整proof个别合同：recorder目标≤230/hard cap250，总proof目标≤270/hard cap290，product≤522、
  terminal≤720、净删≥2,918、responsibility reduction≥3,278等产品预算不变。父RC-06的25%规则继续生效，
  product+proof组合硬门保持≤729；当前product预测496时proof必须≤233，个别上限不得相加使用。
- Termination拆为预声明expected sacrificial-child probe与unexpected termination。前者marker/exit/partial/retry
  全匹配后可完成fault_recovery；后者固定写caller临时同-schema `closed_no_go` receipt。每invocation只写一个
  authoritative receipt、只用root-A/root-B两行为根；最终只提交一个canonical baseline。
- 165 tests只按requirement/node/source SHA/assertion coverage逐项复用；fixture只seed，缺失矩阵仍由recorder
  实测。下一步对修正后的formal重新取得同一bytes LEAN/SAFETY双PASS0，未通过前仍不创建recorder或改产品。
- 首次准备Round 9时发现WI213/WI196仍冻结190/712，已中止旧hash复审；parent canonical只同步proof个别
  上限290与组合硬门729，不放宽RC-06的25%分母或产品范围，再计算新formal identity。

## 13. Batch 2026-07-20-011：Authoring review Round 9 LEAN FAIL1 / SAFETY FAIL5

- Round 9 identity formal-six=`e2dcf310...ca43`、formal-three=`51c86641...f9f2`由双方复算一致；
  Pascal/LEAN=`FAIL1`、Confucius/SAFETY=`FAIL5`。共同P1是§8/SC遗漏组合预算终局门，产品尚未编码时
  可能错误按actual product=0放行。
- 其余SAFETY findings均成立：已死亡supervisor无法承诺原子写receipt；record/pass-verify两根与no-go
  verify零根表述冲突；marker后到termination存在误认同exit真实崩溃窗口；coverage未绑定helper/fixture。
- 最小修正冻结T61A三项组合门`candidate shadow + actual current proof + reserved future proof≤729`，T33改
  actual+actual；shadow收紧为459，future reserve逐文件/任务非零登记。§8显式加入两个阶段的combined NO-GO。
- Durable保证只属于仍存活的receipt-owning supervisor；其自身不可清理死亡由外部调用者判unclosed NO-GO。
  Expected marker加入parent nonce、精确post-marker transcript/EOF和marker→harness termination相邻性。
- Normalizer按模式固定两项或空表；复用node增加transitive helper/seed/fixture/autouse source SHA set，
  无法精确绑定即不复用。Round 9 verdict全部退役，Round 10必须审新bytes。

## 14. Batch 2026-07-20-012：Authoring review Round 10 双 FAIL1

- Pascal/LEAN=`FAIL1`：candidate shadow使用glue 78，低于WI213已证明的83～85机械下界；其余Round 9
  finding均关闭。Confucius/SAFETY=`FAIL1`：supervisor在写pass receipt后、正常exit前不可清理死亡时，
  旧条款仍可能误接受磁盘pass，且与§8 receipt-first绝对规则冲突。
- 两项均成立。Shadow改为`330 engine + 85 glue + 51 route/facade = 466`，terminal shadow=682、预计净删
  2,956；总proof目标由270收紧为263，使目标组合仍为729，个别hard cap不变。
- Pass现在必须同时满足authoritative receipt verify和process exit 0；任一非零/signal退出都不能接受pass。
  有有效closed_no_go则closed，否则外部envelope记录exit/signal、现存文件hash和unclosed_no_go；§8明确
  排除supervisor不可清理死亡的receipt-first承诺。Round 10 verdict退役，Round 11审新bytes。

## 15. Batch 2026-07-20-013：Authoring review Round 11b 双 PASS0

- 主代理首次发起Round 11时误把WI196 execution log/summary列入formal-six；两名reviewer均以`FAIL1`
  拒绝错误identity。合同未改，按冻结算法恢复WI196与WI213各自`spec/plan/tasks`六文件。
- 正确identity由双方独立复算一致：formal-six=
  `2504969100c7e89dbc3d475afb4c8ac3ae51969a6db42f16db3be3b130db4285`，formal-three=
  `4ad0c9a0154baa02023153b8ceab5736c8035a257babecf13b7387f10c8d6c11`。
- Round 11b Pascal/LEAN=`PASS0`、Confucius/SAFETY=`PASS0`，均未发现可操作问题；85/466/263/729预算、
  supervisor死亡封闭、pass receipt+exit 0、expected termination、两根/零根和coverage provenance全部通过。
- 同批治理验证：constraints无BLOCKER、program validate PASS、plan-check pending=0/drift=NO、manifest exact=
  `1 passed in 104.20s`；产品源码与目标行为测试仍为零差异。该结论仅完成authoring准入，不冒充最终T61A GO。
