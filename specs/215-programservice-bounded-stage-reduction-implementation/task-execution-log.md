# 任务执行日志：ProgramService Bounded Stage Reduction Implementation

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**创建日期**：2026-07-20
**状态**：RC-10 formal review/remediation；产品代码禁止

## 1. 固定归档规则

- 每批开始前预读constitution、WI196、WI213与本WI current formal。
- 每批记录base/HEAD/tree、范围、命令、结果、finding disposition、预算、回退和精确下一步。
- Pascal/Confucius只裁决同一committed+clean identity；任一受审source变化使两 verdict同时退役。
- RC-10 formal同identity双PASS并冻结implementation-base前，`src/**`与两份目标行为测试必须相对
  behavior legacy零diff；随后只允许`C1` characterization，首个`Rx`前不写engine。
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

## 16. Batch 2026-07-20-014：T61A proof 过度实现复核与风险分层修正

- Round 11b 后先后制作两版未提交 recorder 原型。第二版虽压至311 LOC，但仍缺完整状态转移、精确
  provenance、真实public/DTO/raw/late-bound/termination/retry/performance等安全证据；继续补齐的自然下界
  约303～315 LOC，连同manifest和future reserve会使组合量约793，超过RC-06硬门729。
- Pascal/LEAN与Confucius/SAFETY据此对原T61A执行合同统一`NO-GO`；两版原型均已删除，未改`src/**`
  或两份目标行为测试。禁止用压行、弱化证据、删除矩阵或扩大预算伪造可行性。
- 风险分层修正把T61A收敛为编码前不可变基线：45方法结构、27个public surface、27个DTO结构、165节点
  有序身份与真实测试结果、formal/source/toolchain/provenance hash、warmup+20性能基线、原子JSON receipt和
  组合预算。recorder目标≤180/hard cap200，总proof hard cap290，future task reserve合计≥27。
- 原动态矩阵未删除，迁移到每个stage、T61B、默认selector切换和legacy deletion前执行三方回放：冻结旧
  commit/tree的isolated legacy、candidate checkout中的current legacy route、candidate route必须零未授权差异。
  该结构避免共享facade/glue让legacy和candidate同错而被误判通过。
- 两名reviewer对上述风险分层方案均给出`PASS0`。方案评审不替代精确文件字节评审；当前formal bytes仍须
  重新计算identity并由双方从零复核，未取得同identity双PASS0前不得实现recorder或产品代码。

## 17. Batch 2026-07-20-015：风险分层精确字节 Round 12 双 FAIL3 与修正

- Round 12 formal-six=`802adc21...d3d8`、formal-three=`3bed3ac4...093f`由双方独立复算一致；
  Pascal/LEAN=`FAIL3`、Confucius/SAFETY=`FAIL3`。共同finding是旧behavior/direct+CLI T61A措辞残留与
  no_go五section早期失败语义不闭合；LEAN另发现三方runner/机器载体/reserve未可执行，SAFETY另发现
  deletion删除legacy后current-legacy腿无来源。
- 修正删除全部T61A动态hash/双根残留；readiness只绑定receipt file与五section hash。No-go sections只允许
  五section全序的空集/严格前缀，已取得hash须有效；verify保持no_go并非零，绝不补算或升级pass。
- 唯一test-only runner限既有integration测试文件和可选既有conftest seam；单pytest node记录并执行三条
  subprocess命令，原生JUnit与未跟踪raw tree为机器载体，不新增脚本/测试文件/schema。Future reserve固定
  48行，超出时须等量降低product shadow，否则NO-GO；T23～T30/T32均绑定完整§4.2。
- Deletion current-head/fresh-main三腿固定为T61A原始legacy、冻结pre-deletion candidate-merge current
  legacy、deletion candidate，merge前后均完整回放。修正后新formal-six=`b94b563b...0837`、formal-three=
  `741c0308...d50e`，Round 13正在同identity复审；Round 12 verdict全部退役。

## 18. Batch 2026-07-20-016：Round 13 LEAN FAIL2 / SAFETY FAIL3 与隔离runner闭环

- Round 13双方独立复算formal-six=`b94b563b...0837`、formal-three=`741c0308...d50e`一致。LEAN=`FAIL2`：
  runner没有冻结outer/leaf/三条命令，48行reserve无逐symbol自然估算。SAFETY=`FAIL3`：共享editable可能让
  original腿误载candidate、deletion checkout错误重算T61A recorder、outcome/error与目录fsync未闭合。
- 唯一runner现冻结outer/非递归leaf node、五类root输入、每腿commit/tree、test-only route和三条
  `uv run --isolated --project/--directory <leg-root>`命令；先验真cwd/HEAD/tree/interpreter、三模块resolved
  path/source SHA和route，再以同一重置绝对behavior root比较完整§4.2，comparison policy不使用normalizer。
- Future reserve改为逐文件/symbol 80行：conftest fixture10、stage/fault data12、leaf command12、leg runner14、
  provenance12、compare14、leaf/outer6；`466+actual current proof+80≤729`，实际超额只能等量降product或NO-GO。
- Deletion recorder verify只在冻结T61A proof worktree；pass/error=null与no_go/non-empty双向唯一，target-parent
  temp按file fsync→replace→可用时directory fsync。新formal-six=`cc524311...2179`、formal-three=
  `44b4441e...2589`进入Round 14；Round 13 verdict退役。

## 19. Batch 2026-07-20-017：Round 14 SAFETY PASS0 / LEAN FAIL2 与真实leaf职责

- Round 14双方独立复算formal-six=`cc524311...2179`、formal-three=`44b4441e...2589`一致；SAFETY=`PASS0`、
  LEAN=`FAIL2`。LEAN发现candidate test root的pytest `pythonpath=["src"]`仍可能污染旧腿，且80行表只预算
  编排/比较，未明确完整矩阵采集和T61B性能职责；SAFETY PASS因后续bytes变化退役。
- 三条leaf命令现强制`-o pythonpath=<leg-root>/src --import-mode=importlib`，并由command/provenance双重断言。
  精确复用106 unit build/execute/write node families、59 integration CLI node families与九个具名stage seed
  helpers；新增`_capture_three_way_case`只补未输出的late-bound/fault/termination/sentinel/network ledger，
  `_sample_three_way_performance`专职T61B warm-up+20。
- Future reserve按九个symbol重算为90行，recorder目标收紧170；组合门仍为
  `466+actual current proof+90≤729`，不降低证据、不虚降product。新formal-six=`11003407...8799`、
  formal-three=`e9ba27e6...b148`进入Round 15；Round 14 verdict全部退役。

## 20. Batch 2026-07-20-018：Round 15 双 FAIL1 与 exact-node worker接线

- Round 15双方独立复算formal-six=`11003407...8799`、formal-three=`e9ba27e6...b148`一致，LEAN/SAFETY
  均`FAIL1`：合同声称复用165节点，但三条命令只选择supplemental leaf，存在节点完全未执行的共同阻断。
- T61A receipt现按anchored primary-stage grammar冻结九个disjoint exact-node组，计数为
  `16/19/19/19/19/19/20/17/17`，union精确`106+59=165`；同时冻结unit/integration两个文件各九个
  file-qualified seed helper source SHA。
- Outer从receipt展开截至当前stage的累计exact IDs、重写candidate绝对test paths并追加supplemental nodes；
  三腿各只运行一层pytest worker。Supplemental禁止调用test function或嵌套pytest，只补ledger；JUnit必须
  exact-node对账且全部passed，T61B执行exact165+九supplemental。
- 新formal-six=`57598a05...e721`、formal-three=`34ddc951...f8cc`进入Round 16；Round 15 verdict退役。

## 21. Batch 2026-07-20-019：Round 16更正与Round 17同身份双PASS0

- Round 16 LEAN最初因archive grammar可能吞入排除子域给出`FAIL1`；SAFETY复算指出grammar输入已是selector
  排除后的receipt exact165，九组实际完整且无重复。LEAN随后独立复核并撤回该FAIL，改判原identity `PASS0`。
- 为消除实现歧义，仍做最小fail-closed增强：record/verify/worker在分组前显式断言selector来源，并拒绝任一
  `thread_archive`/`project_cleanup` node。该修订不创建第二selector、不改变节点、runner或90行reserve。
- Round 17双方独立复算formal-six=
  `3aa2d6a3d647aaae22fba3a234071031bab68a342348251fbdd1362a299d9abf`、formal-three=
  `abd28b97ba41387db4b936990f0c786ac4b250c49007a30e1d5b893309adcadd`一致，LEAN/SAFETY=`PASS0/PASS0`、
  findings=0。实测collected/assigned/unique=`165/165/165`，forbidden/missing/duplicate=`0/0/0`，九组计数=
  `16/19/19/19/19/19/20/17/17`。该结论是风险分层formal authoring准入，不冒充最终T61A readiness GO。

## 22. Batch 2026-07-20-020：本地双审准入与治理门禁

- 用户明确授权本地SDLC双对抗评审作为合入门槛；远端Codex只作附加信号，不再成为无限等待条件。
- Round 17 formal hash复算仍为`3aa2d6a3...d9abf`/`abd28b97...dcadd`，root/scoped handoff byte-identical，
  `src/**`与两份目标行为测试零diff，T61A recorder仍不存在。
- `verify constraints`、`program validate`通过；`workitem plan-check --wi ... --json`为
  `drift=false/pending_todos=0`。当前CLI不支持旧记录中的`--id`，已按`--help`使用`--wi`。
- `program truth sync --execute --yes`写入ready快照，inventory=`1131/1131/0/0`；随后truth audit为
  `state=ready/snapshot=fresh`，manifest exact为`1 passed in 105.85s`。
- 以上只闭合formal authoring与治理准入；仍须在最终committed+clean identity复核双PASS0，然后以TDD形成
  recorder/receipt和最终T61A双readiness GO，双GO前继续禁止产品代码。

## 23. Batch 2026-07-20-021：Committed identity SAFETY FAIL1处置

- Committed identity=`0c810465`/tree=`81c89ad2`，formal hashes仍为Round 17精确值；LEAN=`PASS0`、
  SAFETY=`FAIL1`。唯一成立finding是development summary误把尚不存在的proof harness/receipt写成已交付。
- 最小修正只把该句改为“当前仅交付formal，harness/receipt尚未生成”；formal spec/plan/tasks、产品、目标测试、
  recorder合同和预算均未改变。旧LEAN PASS与SAFETY FAIL随HEAD/tree变化同时退役，必须对新clean identity双审。

## 24. Batch 2026-07-20-022：Round 19双PASS0与170行recorder GREEN

- Continuity修正提交=`49a1f861`/tree=`4509a1bc`；Round 19 Pascal/LEAN与Confucius/SAFETY对该同一
  committed+clean identity均`PASS0`、findings=0，明确仅批准formal authoring。
- 唯一`scripts/program_bounded_stage_t61a.py`实现为170 physical LOC，最大函数32行；Ruff与`py_compile`通过。
  临时record实测45=`3638/3305/333/386`、27 public、27 DTO、exact165九组计数正确、双basetemp exit0，
  performance=`p50 3.062/p95 3.180`，预算=`170+2 current proof / reserve90 / product466 / combined728`。
- 首次pass receipt因文件级`sort_keys=True`把五section重排为字母序，verify正确fail-closed；已只把receipt
  文件写入改为保持插入顺序，section内容hash仍使用canonical sort。修正后record+verify均exit0。
- `record --route candidate`原子写空prefix合法no_go并exit1；随后`verify --route legacy`保持no_go、文件SHA
  不变且exit1。产品源码与两份目标行为测试继续零diff；canonical receipt须在recorder提交后的clean tree生成。

## 25. Batch 2026-07-20-023：Canonical T61A receipt生成

- Recorder提交=`88b62144378ef87717772856dbf1e194053d0960`/tree=`f479af0923c0a3b2a83e8268dc5cf103f532fe85`；
  在该clean tree执行canonical record与verify均exit0。
- Receipt=`136,314 bytes`、SHA-256=`26a03649bae2fa36606810f9d4cdfea4fbf6f6e89c02b7a138cd1a67a5d02663`；
  outcome=pass，section全序=`identity/structure/tests/performance/budget`。
- Formal-six=`3aa2d6a3...d9abf`、formal-three=`d9b4339f...de19`；section hash依次为
  `92e26368...12e3`、`841660de...6ec5`、`0cdec3d5...46ef`、`c07898e3...22fe`、`10f4beba...d4bc`。
- 双basetemp实际结果=`165 passed, 474 deselected in 2.64s`与`2.62s`；九组计数仍为
  `16/19/19/19/19/19/20/17/17`，public/DTO=`27/27`，budget combined=`728≤729`。
- 本段只登记canonical receipt；receipt尚未提交，最终proof commit/tree、治理全门与T61A双readiness GO待完成。

## 26. Batch 2026-07-20-024：Proof commit终端门禁全绿

- Receipt/truth提交=`ed1ed1f84f1d0c6ae911aa9dd5ffd83d7764d58d`/tree=
  `2d2b62ae8c9dfd92248912ef93f3edb3af23be15`；clean tree上canonical verify exit0、no_go record/verify均exit1。
- Exact selector=`165 passed, 474 deselected in 2.63s`；recorder与全仓Ruff PASS；全量pytest首次误设
  `AI_SDLC_DISABLE_UPDATE_CHECK=1`，使self-update测试预期success却得到disabled，该轮作废。去掉错误环境后
  单节点=`1 passed`，最终全量=`3303 passed, 3 skipped in 642.12s`。
- `verify constraints`无BLOCKER、`program validate` PASS、plan-check=`drift=false/pending=0`、truth audit=
  `ready/fresh 1131/1131/0/0`、manifest exact=`1 passed in 96.21s`，worktree保持clean。
- Harness SHA=`bde479b5...5938`、receipt SHA=`26a03649...2663`；产品源码/目标行为测试仍零diff。
  下一步只允许records-only truth提交与同一final proof tuple双review，不允许提前写产品。

## 27. Batch 2026-07-20-025：Final readiness 双 NO-GO

- Final identity=`fadf8456`上SAFETY发现summary/handoff仍停在proof提交前；LEAN进一步证明recorder依赖
  file-level E305/I001、E731和最长452字符压行。Ruff自然格式=`587`，structure/tests函数分别超50，
  原`172+90+466=728`预算不再有效。
- 主审复核`ruff format --stdin-filename ... | wc -l=587`、format-check失败；两个finding均成立，
  未进入产品代码。

## 28. Batch 2026-07-20-026：Risk-layer spike 与 RC-10 设计共识

- 未提交自然格式风险分层 spike 移出surface/DTO明细后仍=`286 physical / 407 Ruff-formatted`，证明
  recorder≤180不可达，继续压缩会重演过度实现。
- Pascal/LEAN与Confucius/SAFETY最终一致`ACCEPT` RC-10：退役custom recorder/receipt/T20/controller、
  runtime selector、双实现与独立deletion路线；九stage各自Cx/Rx、legacy/current两腿、full、同SHA双审。
- 最小characterization固定为missing/malformed、六状态、path/confirmation与writer fault；原165节点不得
  rename/delete/skip/xfail/deselect。预算729、terminal720、net deletion2918与release边界均不放宽。

## 29. Batch 2026-07-20-027：RC-10 formal remediation authoring

- 已删除未合入recorder/receipt并同步改写WI196/WI213/WI215 canonical formal；当前diff没有`src/**`、
  目标行为测试、workflow、依赖、版本或release变化。
- Formal机器门已通过：constraints无BLOCKER、program validate PASS、plan-check=`drift=false/pending=0`、
  truth=`ready/fresh 1131/1131/0/0`、exact selector=`165 passed, 474 deselected in 2.65s`、manifest exact=
  `1 passed in 113.90s`；产品与目标测试零diff，handoff byte-identical。
- T05 completed，T06进入in_progress；固定committed+clean identity并取得同identity双PASS前，禁止
  characterization或产品代码。
- removed comment reason: `scripts/program_bounded_stage_t61a.py` 删除随过度 recorder 一起退役的
  `# ruff: noqa: E305, I001`；该豁免正是压行finding的一部分，不应在RC-10保留等价注释。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/plan.md` 删除已被
  RC-10取代的 `### 4.1 Candidate interfaces`、`### 4.2 每个 stage 的原子循环`、
  `## 5. Phase 3：T61B 与 candidate PR`、`**回退**：selector-only 指回 legacy；不得删除 legacy。`、
  `## 6. Phase 4：主线预发布稳定周期`、`**停止**：任一平台/package/offline/sibling/performance/rollback失败`、
  `## 7. Phase 5：独立 deletion PR 与 actual rollback`、`## 8. 精确验证命令`、
  `## 9. Review identity 与提交边界`；对应安全意图已由Cx/Rx、terminal gates、squash revert和同SHA双审替代。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/spec.md` 删除已被
  RC-10取代的 `### US-3：可回退的减重完成（P1）`、`**独立测试**：candidate merge tree 与 deletion merge tree`、
  `## 4. T61A 证据合同`、`### 4.2 下沉动态矩阵与三方 replay`、`## 5. Reduction Contract 绑定`、
  `## 6. 功能需求`、`## 7. 成功标准`、`## 8. NO-GO 与回退`；新spec §§3～7完整保留兼容、预算、
  legacy/current A/B、验收与回退语义，不保留失败的proof状态机。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/tasks.md` 删除已退役的
  `### T22 创建唯一 private engine（pending）`、`### T23～T30 逐 stage RED/GREEN（pending）`、
  `### T31 九阶段 selector round-trip（pending）`、`## Batch 3：T61B 与 candidate mainline`、
  `### T32 T61B zero-delta（pending）`、`### T33 Candidate terminal gates（pending）`、
  `### T34 Candidate PR/merge/fresh-main（pending）`、`## Batch 4：主线预发布稳定周期`、
  `### T41 Cross-platform/package/offline（pending）`、`### T42 Sibling 与 selector 稳定（pending）`、
  `## Batch 5：独立 deletion 与 rollback`、`### T51 删除 legacy（pending）`、
  `### T52 Deletion gates/PR/merge（pending）`、`### T53 Exact-merge actual rollback（pending）`、
  `### T54 Lifecycle closure（pending）`、`## 追踪矩阵`；这些未来任务由T21～T35的九stage直接减重、
  terminal、squash revert、final PR与lifecycle reconciliation一一替代。
- removed comment reason: `scripts/program_bounded_stage_t61a.py` 删除 `# ruff: noqa: E305, I001`，因为该格式豁免随已NO-GO的压行recorder整体退役。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/plan.md` 删除并由RC-10等价替代 `## Global Constraints` `## 1. 文件职责` `## 2. Phase 0：Canonical WI 与准入` `**停止**：任何 src/workflow/dependency/version/release 差异、目标行为测试 blob 变化、manifest test 超出` `## 3. Phase 1：T61A proof-only commit` `### 3.1 先固定 legacy inventory` `### 3.2 TDD 编写唯一 recorder` `### 3.3 Proof commit 与 readiness` `**完成**：双 GO、actionable findings=0；否则保留 legacy并停止，不能写产品代码。` `## 4. Phase 2：逐 stage TDD candidate shadow` `### 4.1 Candidate interfaces` `### 4.2 每个 stage 的原子循环` `## 5. Phase 3：T61B 与 candidate PR` `**回退**：selector-only 指回 legacy；不得删除 legacy。` `## 6. Phase 4：主线预发布稳定周期` `**停止**：任一平台/package/offline/sibling/performance/rollback失败` `## 7. Phase 5：独立 deletion PR 与 actual rollback` `## 8. 精确验证命令` `## 9. Review identity 与提交边界`；原因是这些章节属于已cancelled_no_go的proof/shadow/deletion路线，安全意图已迁入Cx/Rx、terminal gates、同SHA双审和squash revert。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/spec.md` 删除并由RC-10等价替代 `### US-3：可回退的减重完成（P1）` `**独立测试**：candidate merge tree 与 deletion merge tree 各自 fresh-main 全绿；deletion terminal≤720` `## 4. T61A 证据合同` `### 4.2 下沉动态矩阵与三方 replay` `## 5. Reduction Contract 绑定` `## 6. 功能需求` `## 7. 成功标准` `## 8. NO-GO 与回退`；原因是新spec §§3～7以更少状态保留兼容、预算、原生A/B、验收和精确revert边界。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/tasks.md` 删除并由RC-10任务替代 `**编号**：215-programservice-bounded-stage-reduction-implementation | **日期**：2026-07-20` `**来源**：本 WI spec/plan + WI213 canonical contract` `**当前门禁**：T61A 双 readiness GO 前 src/** 零差异、两份目标行为测试 blob 不变；tests/**` `### T11 冻结 legacy inventory（completed）` `### T12 采集 selector characterization（completed；非最终性能）` `### T13 TDD 实现唯一 recorder（completed）` `### T16 LEAN/SAFETY 同身份 readiness（pending）` `## Batch 2：Candidate shadow（双 GO 后）` `### T22 创建唯一 private engine（pending）` `### T23～T30 逐 stage RED/GREEN（pending）` `### T31 九阶段 selector round-trip（pending）` `## Batch 3：T61B 与 candidate mainline` `### T32 T61B zero-delta（pending）` `### T33 Candidate terminal gates（pending）` `### T34 Candidate PR/merge/fresh-main（pending）` `## Batch 4：主线预发布稳定周期` `### T41 Cross-platform/package/offline（pending）` `### T42 Sibling 与 selector 稳定（pending）` `## Batch 5：独立 deletion 与 rollback` `### T51 删除 legacy（pending）` `### T52 Deletion gates/PR/merge（pending）` `### T53 Exact-merge actual rollback（pending）` `### T54 Lifecycle closure（pending）` `## 追踪矩阵`；原因是T01～T35已把历史状态映射为completed_no_go、formal、九stage、terminal、final PR和lifecycle任务。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/plan.md` 的compact摘要 `*停止**：任何`src` 与 `*完成**：双`GO`、` 属于已退役T61A/shadow门；RC-10以pre-product双PASS、逐stage NO-GO和精确revert替代。
- removed comment reason: `specs/215-programservice-bounded-stage-reduction-implementation/tasks.md` 的compact摘要 `*编号**：`215-p` 对应旧header；新header保留同一WI编号并把状态改为RC-10 formal。

## 30. Batch 2026-07-20-028：RC-10 formal source commit

- Formal source commit/tree=`385568456f500054a3737d97e451b813fa5df946`/
  `42b253a089c20762ef1334503be8d68695d78ad8`；formal-six=`75d60ac9...519e`、formal-three=
  `2875f9ac...7090`；`+603/-1094`，删除recorder/receipt，产品与目标测试零diff。
- 下一笔仅允许truth/continuity机械收口；最终clean identity形成后再做同identity双审，禁止提前进入Cx。

## 31. Batch 2026-07-20-029：RC-10 首轮同身份评审与最小修订

- 同一 committed+clean identity `c0ff5f28a28c5685ba43f0c7244b35dd19d80f9e` 上，Pascal/LEAN=`FAIL1`：
  formal内容无精简finding，仅 continuity/summary 仍把已完成的 records sync 写成 pending。
- Confucius/SAFETY=`FAIL2`：除同一状态陈旧外，C1 尚未显式冻结 late-bound/truthiness、时钟调用次数/
  顺序/异常与首次 fault 后 retry 等价；public denylist 尚未覆盖 docstring/module/qualname 等完整可观察定义。
- 本批只修订 spec/plan/tasks 与状态记录：增加 truthy/falsey、`self` callback、clock、fault/retry 的共享
  参数化 characterization 和三类必需 mutation；扩全 public/DTO denylist。`src/**` 与目标行为测试继续零差异。
- 只有新的 committed+clean identity 通过治理门并取得同 identity LEAN/SAFETY 双 PASS0，才允许冻结
  implementation-base 并进入 `C1`；此前禁止产品代码。

## 32. Batch 2026-07-20-030：Formal remediation source 与 truth 自引用诊断

- 最小修订 source commit/tree=`b9e3582ac5aeec08679d09559e33b95cbd9682de`/
  `4da3d9a7194c2250b60663acdb2eafbf2f55832e`；八份 formal/continuity 文件=`+60/-28`，无产品或测试差异。
- pre-commit manifest exact 的测试断言通过，但 teardown 守卫报 `tracked:program-manifest.yaml`：当时
  snapshot 仍记录前一 source `c0ff5f28`。根因是 formal dirty tree 先于 source commit 执行 truth sync，
  不是产品或断言失败。
- 未修改/跳过仓库状态守卫；先提交 formal source，再从该 source 同步包含本段 continuity 的 records，
  最终只对 committed+clean records identity 复跑 audit/manifest exact 与双审。

## 33. Batch 2026-07-20-031：RC-10 第二轮同身份评审

- Identity=`793bc533ba59bb34fd03d0d7ce4a1ceba987d555` / tree=
  `458d587fc01d50c763424437a0d7ae9e3394d54c`，formal-six=`75d60ac9...519e`、formal-three=
  `8b97878b...fa1f`；worktree clean，治理门、exact165、truth/manifest exact 全绿。
- Confucius/SAFETY=`PASS0`，上一轮 characterization/denylist finding 已闭合；Pascal/LEAN=`FAIL1`，仅发现
  本log固定规则与WI213 summary仍以现在时引用已 `cancelled_no_go` 的T61A，可能使恢复执行永久阻断。
- 该finding成立；本批仅把三处当前执行语义改为RC-10 gate并明确T61A是已退役历史，不改formal九文件、
  产品或测试。身份变化使本轮两 verdict 同时退役，须对新 committed+clean identity 从零双审。

## 34. Batch 2026-07-20-032：RC-10 双PASS与 C1 characterization

- Formal implementation-base=`dbc02c65a6e648686736f4d4ed3f35e821c7b9e9` / tree=
  `92a80f70d0cb9f62d1459c527e774e14829d16c9`；formal-six=`75d60ac9...519e`、formal-three=
  `8b97878b...fa1f`。Pascal/LEAN=`PASS0`、Confucius/SAFETY=`PASS0`，findings=0，授权范围仅为C1。
- C1只改`tests/unit/test_program_service.py`：共享九stage case表+4个参数化测试，共新增204 physical LOC、
  展开63 nodes；无新文件、runner、snapshot schema或private import，proof=`204≤290`。
- 新用例实跑=`63 passed, 406 deselected`；原165节点保持且新节点进入同一selector，累计=
  `228 passed, 474 deselected`。Ruff PASS，`src/**`相对behavior legacy仍零diff。
- 三类临时mutation均仅作用于cross-spec writer且立即用`apply_patch`恢复：`or`→`is None`、绕过`self`
  builder、eager clock各自使对应新node=`1 failed`；恢复后63/228全绿，产品SHA与legacy一致。
- 新矩阵同时证明truthy bypass、falsey fallback、clock→build→execute顺序/异常传播、mkdir/write首次fault
  不留最终artifact，以及同输入retry与成功artifact逐字节一致。C1同identity双PASS前继续禁止engine/Rx。
- 首次full误带`AI_SDLC_DISABLE_UPDATE_CHECK=1`且窄终端，得到15个与C1无关的update-advisor/换行失败；
  去除该变量并固定宽终端后定向=`31 passed, 1 skipped`，完整重跑=`3366 passed, 3 skipped`。前一轮
  明确作废，不修改产品或断言迎合环境污染。

## 35. Batch 2026-07-20-033：C1 immutable legacy/current 两腿

- C1 source/records identity=`ef1705547d891a9e14546f60a80096eedeb7ff6a` / tree=
  `e38f88280c248a9aba6ab3ccb780aa2a4f0880fa`；test blob unit=`ba117498...fb01`、CLI保持=
  `9628711c...1f3`。独立 detached worktree 为legacy=`7922956d/cc3c6b7f`、current=`ef170554/e38f8828`。
- 首轮两腿均=`228 passed, 474 deselected`，JUnit counts=`228/0/0/0`、ordered classname/name SHA=
  `00e22b70...12e4`一致；raw tree只因既有writer的真实`utc_now_z()`相差数秒而不一致。
- 不增加normalizer或忽略字段；在共享`tests/conftest.py`仅对九stage且排除thread/archive cleanup的节点
  注入固定时钟，新增28行，proof累计=`204+28=232≤290`。当前selector仍=`228 passed`。
- 修正后两腿分别=`228 passed in 2.85s`与`2.84s`；JUnit counts与ordered node SHA相同，移除pytest
  `current`便利symlink后原生basetemp `diff -qr` exit=0，即raw artifact tree逐字节一致。产品仍零diff。
- 该fixture与本段改变C1 identity；必须提交、truth sync、复跑最终两腿/full/governance并对同identity双审，
  旧C1 evidence不得冒充最终PASS。

## 36. Batch 2026-07-20-034：Final C1 review evidence

- Final C1 source/records identity=`a3f14263f7ade6f64824fe6908e427c3cfb42799` / tree=
  `8059edf63461a2a9791efec569ce87d144bd2920`；conftest/unit/CLI blobs=
  `06eb419f...42fb`/`ba117498...fb01`/`9628711c...1f3`，main worktree clean。
- Final detached legacy/current仍分别加载`7922956d`与`a3f14263`产品路径，两腿=
  `228 passed, 474 deselected in 4.29s` / `2.80s`；JUnit=`228/0/0/0`，ordered classname/name SHA均
  `00e22b70...12e4`，原生basetemp移除pytest便利symlink后`diff -qr` exit=0。
- Final C1 identity Ruff、constraints、program validate、plan-check=`drift=false/pending=0`、truth=
  `ready/fresh 1131/1131/0/0`、manifest exact=`1 passed in 99.06s`；产品仍相对legacy零diff。
- Full=`3366 passed, 3 skipped`在C1 core source上完成；之后唯一测试语义变化是28行固定时钟fixture，
  其全部影响节点已由final identity两腿228/228覆盖。当前只待C1同identity双审，仍不授权engine/Rx。

## 37. Batch 2026-07-20-035：C1 双审 FAIL1 最小修正

- `727f8417`同identity评审：Pascal/LEAN=`FAIL1`，指出proof按Ruff自然格式为`298>290`；
  Confucius/SAFETY=`FAIL1`，指出首个cross-spec Rx前尚缺loader、状态与outside-root冻结。
- 共享九stage case改为fixture+默认seed，cross-spec重复setup收敛到单helper；不压行、不删节点。按formal base
  `dbc02c65`与candidate临时副本分别执行固定Ruff format后，conftest/unit净增=`26+244=270≤290`。
- 首stage新增7 nodes：missing/malformed/non-mapping各1、skipped/confirmation_required/partial各1、
  outside-root 1；completed/blocked/relative/non-manifest沿用原节点，union由228增至235，原165不变。
- 四类临时mutation均RED并立即恢复：loader fail-closed=`3 failed`；skipped/confirmation/partial=
  `3 failed`；outside-root guard=`1 failed`；吞掉write fault=`1 failed`。恢复后exact union=
  `235 passed, 474 deselected`，产品blob=`7b2ac507...9c6`与behavior legacy逐字节一致。
- blanket `monkeypatch.undo()`改为局部`monkeypatch.context()`，不再中途撤销HOME/AgentOps/固定时钟fixture。
  returned `failed`经双审确认公开结构不可达；C1冻结write fault传播/零receipt/retry等价，首Rx删除dead branch。
- source commit=`7dbc3f85`。首次full功能断言=`3373 passed, 3 skipped`，但session teardown守卫发现
  `program-manifest.yaml`在运行中由truth sync写入`repo_revision=7dbc3f85`，故该轮以`1 error`作废；不绕过
  repository guard。先固定该records变更，再从clean identity完整重跑full。
- records identity=`0a9944883926b5396916ef426a5fa1c72bb1a98f` / tree=
  `53770c374f05f632db01886c56069eda2753b6cb`；clean full=`3373 passed, 3 skipped in 695.56s`，teardown
  repository guard通过，测试后worktree clean。
- immutable legacy=`7922956d/cc3c6b7f`与current=`0a994488/53770c37`分别从独立detached worktree加载
  产品，两腿均用candidate test blobs运行=`235 passed, 474 deselected`；JUnit=`235/0/0/0`，ordered
  classname/name SHA均=`0d7b6759...57af`。移除两腿各34个pytest便利symlink后raw tree `diff -qr`=0。
- Final gates：全仓Ruff、constraints、program validate、plan-check=`drift=false/pending=0`、truth=
  `ready/fresh 1131/1131/0/0`、manifest exact=`1 passed in 104.56s`；root/scoped handoff同字节。
  formal-six=`75d60ac9...519e`，formal-three=`e498a7f8...cf6c`，产品blob仍为legacy `7b2ac507...9c6`。

## 38. Batch 2026-07-20-036：C1 输出loader SAFETY FAIL1 最小修正

- `bccb6939`同identity评审：Pascal/LEAN=`PASS0`；Confucius/SAFETY=`FAIL1`，指出现有不可用artifact用例
  只冻结provider-patch输入loader，首个Rx同时拥有的cross-spec输出loader仍缺missing/malformed/non-mapping。
- 将原3节点public测试扩为输入/输出loader双consumer参数化矩阵，保留原3节点并净增3节点；两类consumer
  都从public builder/execute进入，冻结`missing_artifact`、warning artifact kind、blocked结果和零markdown副作用。
- 临时绕过cross-spec输出loader的exists/解析异常/mapping guard时，新增3节点全部RED；随后用`apply_patch`
  恢复，产品blob重新核对为legacy `7b2ac507...9c6`。
- 当前exact union=`238 passed, 474 deselected`，原63共享节点和165基线节点均保留；formal base/candidate
  Ruff自然格式副本净增=`26+261=287≤290`。`bccb6939`旧双审结果因测试identity变化而失效，须重新提交
  committed+clean identity、复跑full/immutable两腿/治理门，并取得同identity双`PASS0`。

## 39. Batch 2026-07-20-037：C1 final evidence provenance闭合

- Source/tests commit=`771ae752f60a0e61b99ce8ab5993470b5403d81d`；truth records commit=
  `201be4e54f374f4dd53144c14d146c147887139d` / tree=`e297bdee1a0d2891aa481e19cb2fc7cff9ffdebd`；
  continuity review identity=`15d8a7840b666a78de71783bc20550ecda16cadd` / tree=
  `fcc5a6d3cfa4546f5289e6a95041807027b5419d`。两者间仅两份byte-identical handoff改变。
- 冻结blob：产品`program_service.py=7b2ac50725136b6399b74e898f147a0b1fecd9c6`，与behavior legacy相同；
  candidate tests为`conftest=2f9083d3b712ddfbd2b8984f41053ff38642e642`、
  `unit=d1459fe42c5633e541ff6aba278aeab128545b37`、
  `integration=9628711ce7a41b08fd6bc92f4a6c9639ed5031f3`；config为
  `pyproject=8e4a99fa8f042ba97a0b0fcc581344d2b4d0db21`、`uv.lock=21a34695cb9530add630ee9e52f1747f0aeece2a`。
- Clean full命令=`COLUMNS=240 LINES=60 uv run --python 3.11 pytest -q`，在records identity上退出0；PTY
  combined output=`3376 passed, 3 skipped in 693.41s`，无failure/error诊断，teardown repository guard通过，
  运行后`git status --porcelain`为空。
- A/B共同selector为九stage名称并排除`thread_archive/project_cleanup`；共同命令为
  `uv run --python 3.11 pytest --import-mode=importlib -q <candidate unit> <candidate integration> -k <selector>`，
  并传入`--basetemp=<leg> --junitxml=<leg.xml>`，固定`PYTHONPATH=<leg>/src`。A腿cwd/commit/tree=
  `/tmp/ai-sdlc-wi215-c1-legacy-7922956d` / `7922956d3e248a93c3190240259850ab3498ec9f` /
  `cc3c6b7f7e63dd040034938ff6bb6827f067e41c`，解释器=
  `<cwd>/.venv/bin/python3`，imported module=`<cwd>/src/ai_sdlc/core/program_service.py`；B腿对应=
  `/tmp/ai-sdlc-wi215-c1-current-201be4e5` / `201be4e54f374f4dd53144c14d146c147887139d` /
  `e297bdee1a0d2891aa481e19cb2fc7cff9ffdebd`，解释器与module同样均来自B腿cwd。两腿stdout分别为
  `238 passed, 474 deselected in 3.02s/3.34s`，stderr均为空。
- 原生JUnit locator为`/tmp/ai-sdlc-wi215-c1-ab-238-final/{legacy,current}.xml`，均`39,436 bytes`，SHA256=
  `2ed848b368db90572ed7222a5bc5e0111a85915a3defbf9e0064c00b62dc3f39` /
  `ba50cc7dce4e2ad12ca5df73cf4b97bb1b150026cf8e4bd1dcd34ee9d00e8740`；outcome均=`238/0/0/0`，
  ordered classname/name SHA256均=
  `0064659b58a8b856fd0b85be1e8c2ba9cee6d2f23e1bf52dc03b9c6d62dbba61`。
- stdout locator为同目录`{legacy,current}.stdout`，均`356 bytes`，SHA256=
  `dc7f6f777db97515ef758885d91fb8c00c948a596b6d0419b0ef77d8c6574456` /
  `809fddc7996fbe02759c7f50feea79853973ab42d7b141b7db659fc3e4c63b59`；stderr locator为
  `{legacy,current}.stderr`，均`0 bytes`，SHA256=
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。移除两腿各35个pytest便利
  symlink后，raw locator为同目录`legacy/`与`current/`；
  每腿`767 files / 717,475 bytes`，按排序后的`sha256 length relative-path`清单计算tree SHA256均=
  `ed594c678114f2314c60f594094cd78e0be9c5cc4ce5db9905c6f4e585905a35`，`diff -qr`退出0。
- Final gates：全仓Ruff PASS、constraints无BLOCKER、program validate PASS、plan=
  `drift=false/pending=0`、truth=`ready/fresh 1131/1131/0/0`、manifest exact=`1 passed in 98.38s`；
  root/scoped handoff同字节。`15d8a784`评审得到LEAN=`PASS0`、SAFETY=`FAIL1`，唯一finding是本段证据
  未进入execution log；行为、loader、状态、路径、fault/retry与fixture无其他问题。本段补齐该finding，
  Batch 38 pending已完成；因records identity变化，双审结论须在新clean HEAD重新取得。

## 40. Batch 2026-07-20-038：C1 双 PASS0 与 cross-spec R1 产品实现

- C1 final committed+clean identity=`fa7f7d039c31ec9d821c5475e297342277f61b40` / tree=
  `0f4653342a5b7de787573e194d5a09f450101842`；Pascal/LEAN=`PASS0`、Confucius/SAFETY=`PASS0`，
  findings=0。首个产品 Rx 因此解锁；远端 Codex review 仅作增量信号，不再作为无限等待门。
- R1 只新增唯一 private `src/ai_sdlc/core/_program_bounded_stage.py`，并把 cross-spec 五个目标方法直接
  委托给 typed binding/engine；删除重复 build/execute/write/payload/load body 与失活 provider-patch
  loader。未修改冻结测试、DTO/public 签名、其他 stage body、CLI、依赖、workflow 或 release 状态。
- 两位本地 reviewer 对初稿计量独立给出 HARD FAIL：candidate=`417 LOC / 59 branch` 未严格低于 legacy
  `392/50`，不得以未来 stage 复用摊销。按相同 AST recipe 收敛后，五 facade=`59/6`、全部 active engine
  methods=`326/42`，R1 target slice=`385/48`，两项均严格下降；所有新增/修改函数最大=`49≤50`。
- 当前真实 retained product=`367 engine physical + 47 service added = 414≤522`；C1 proof=`287≤290`；
  combined=`701≤729`。不存在 selector/registry/DSL/reflection/string method lookup、service/CLI import、
  public abstraction、新依赖或 returned `failed` dead branch。
- 冻结 test blobs 与 C1 HEAD 完全相同：conftest=`2f9083d3...e642`、unit=`d1459fe4...b37`、CLI=
  `9628711c...1f3`。R1 当前 group=`33 passed, 3346 deselected`，累计 exact union=
  `238 passed, 3141 deselected`；Ruff 与 diff-check PASS。
- 宽终端、Python3.11 full 命令=`COLUMNS=240 LINES=60 uv run --python 3.11 pytest -q`，退出0，结果=
  `3376 passed, 3 skipped in 819.26s`，无 failure/error，repository teardown guard通过。
- 本段只固定 pre-A/B 产品事实；待提交 immutable R1 identity 后，仍须执行 legacy/current 两腿、全部治理门、
  truth/manifest 与同 identity LEAN/SAFETY 正式双审。双 PASS0 前不得开始 guarded_registry C2/R2。

## 41. Batch 2026-07-20-039：R1 immutable A/B 与治理证据

- R1 product checkpoint=`1e886c232e907cc01880b477252d28389f43a20d` / tree=
  `2392fc998dd5315912d08601af819927c5180f65`；ProgramService/engine blobs=
  `bc8dadea8e05c73bea5d7ad333019327e3e6d901` / `31a2a83b4968e6f668cbedbeb964e3a54ebc4855`。
  冻结 conftest/unit/CLI blobs 仍为 `2f9083d3...e642` / `d1459fe4...b37` / `9628711c...1f3`。
- detached legacy 腿=`/tmp/ai-sdlc-wi215-c1-legacy-7922956d`，commit/tree=
  `7922956d3e248a93c3190240259850ab3498ec9f` / `cc3c6b7f7e63dd040034938ff6bb6827f067e41c`；
  current 腿=`/tmp/ai-sdlc-wi215-r1-current-1e886c23`，commit/tree=`1e886c23` / `2392fc99`。
  两腿 Python3.11 与 imported `program_service.py` 均来自各自 worktree，使用同一 candidate test path、
  `--import-mode=importlib`、独立 basetemp/JUnit、`PYTHONHASHSEED=0` 与 `TZ=UTC`。
- 两腿分别=`238 passed, 474 deselected in 2.98s` / `3.08s`；JUnit outcome均=`238/0/0/0`，
  ordered classname/name SHA256均=`88065f18...8d13`。JUnit locator=
  `/tmp/ai-sdlc-wi215-r1-ab-1e886c23/{legacy,current}.xml`，均39,436 bytes，SHA256分别=
  `8d19cf1e...a43b` / `06d075e7...1810`；stderr均0 bytes且SHA256=`e3b0c442...b855`。
- 移除两腿各35个pytest便利symlink后，raw locator为同目录`legacy/`与`current/`；每腿=
  `767 files / 717,475 bytes`，排序后 `sha256 length relative-path` tree SHA256均=
  `ed594c678114f2314c60f594094cd78e0be9c5cc4ce5db9905c6f4e585905a35`，`diff -qr`退出0。
- Product checkpoint治理门：全仓 Ruff PASS；constraints=`ok=true/blockers=0/advisories=0`；program
  validate PASS；plan-check=`drift=false/pending_todos=0`；truth audit=`ready/fresh 1131/1131/0/0`。
  随后受控 truth sync 将 `repo_revision=1e886c23`、snapshot hash=
  `d190139bbf6402c385e737dbfbe2e11a9f96e4df57dbb1090412d9681543b8db` 写入 manifest。
- Evidence 写入后 truth sync/audit=`ready/fresh 1131/1131/0/0`，snapshot hash=
  `c1fef3101dea2ce3c260872b7f26b83e6e77ba9730aeeb446c7cc62a37506d69`；manifest exact=
  `1 passed in 107.80s`。本段文字进入 records 后再执行一次最终 sync/audit/manifest；此后不再改 formal
  evidence。Full 与 A/B 产品/测试/config blobs不得变化。

## 42. Batch 2026-07-20-040：R1 双审 FAIL 修正

- Formal review identity=`6e3c661bd1fb2a7bd1a1127c601ed1ecc262569a` / tree=
  `8a50e2f9b283011eab6aa193d89ab182ad8b8517`，worktree clean。Pascal/LEAN=`FAIL2`：无约束
  TypeVar 不构成真实 typed contract；`all((...))` 为 branch 计量牺牲可读性。Confucius/SAFETY=`FAIL1`：
  同一 typed-binding 缺口使新 engine 增加47个 mypy error，错误 binding/DTO 组合无法静态发现。
- 两项成立且不降级。最小修正仅触及 engine 与 cross-spec private factory：增加私有 Step/Request/Result
  Protocol，把 factory 返回类型具体化；typed binding 收纳 root/manifest/spec path 与既有 callback；
  `_result`集合收紧为`Sequence[str]`；yaml untyped import使用精确 error-code ignore。未改 frozen tests/DTO/public
  surface/行为分支，未扩到 legacy ProgramService 类型债。
- strict mypy实测：新 engine=`Success: no issues found`；同版本 legacy ProgramService 与 candidate
  ProgramService均=`62 errors`，本 Rx mypy 增量=`0`。直接条件已恢复为
  `request.warnings and not request.artifact_generated_at`，不再通过`all(tuple)`规避 AST branch。
- 修正后 target slice：五 facade=`57/6`、全部 active engine methods=`314/42`，累计=`371 LOC / 48
  branch`，严格低于 legacy=`392/50`；最大实现函数=`49≤50`。retained product=`394 engine physical +
  47 service added =441≤522`，proof=`287≤290`，combined=`728≤729`。
- 修正后 cross group=`33 passed, 3346 deselected`，累计 exact union=`238 passed, 3141 deselected`；
  Ruff、diff-check、engine mypy全绿。原`6e3c661b`双审结论退役；须固定新 product checkpoint，重跑
  full/immutable A-B/全部治理门并取得同一新 clean identity 双 PASS0。

## 43. Batch 2026-07-20-041：typed-binding remediation final evidence

- 新 product checkpoint=`e1bec128d833c5942f2985b77bf9b7cfcd4afdea` / tree=
  `828469f0a3ece0b9711ce94b2fc15acb3436a12b`；ProgramService/engine blobs=
  `23a4968b63651f8fbfebc3174bf737dcce40984e` / `977cad2c25da95b0c2329ca97b9a3b071e70630b`。
  frozen conftest/unit/CLI 与 config blobs均保持C1不变。
- 宽终端、Python3.11 clean full=`3376 passed, 3 skipped in 707.95s`，无failure/error，repository
  teardown guard通过；测试后 product checkpoint worktree clean。
- immutable legacy/current 分别为`7922956d/cc3c6b7f`与`e1bec128/828469f0`，各自Python3.11和imported
  module均来自独立detached worktree；使用同一candidate tests、`--import-mode=importlib`、独立basetemp/
  JUnit、`PYTHONHASHSEED=0`、`TZ=UTC`。两腿分别=`238 passed, 474 deselected in 3.10s/3.40s`。
- JUnit locator=`/tmp/ai-sdlc-wi215-r1-ab-e1bec128/{legacy,current}.xml`，均39,436 bytes，SHA256=
  `d3d35bfb...963c1` / `5d49d9c7...abb84`；outcome均=`238/0/0/0`，ordered classname/name SHA256均=
  `88065f18699b62fdbf82c3eee102548e2d7c7f51a5fc7b16fa801df88e8a8d13`。stderr均0 bytes/hash=
  `e3b0c442...b855`。
- 移除各35个pytest便利symlink后，raw locator为同目录`legacy/`与`current/`；每腿=
  `767 files / 717,475 bytes`，排序tree SHA256均=
  `ed594c678114f2314c60f594094cd78e0be9c5cc4ce5db9905c6f4e585905a35`，`diff -qr`退出0。
- 全仓 Ruff PASS；constraints=`ok=true/blockers=0/advisories=0`；program validate PASS；plan-check=
  `drift=false/pending_todos=0`。新 engine strict mypy=0；legacy/candidate ProgramService strict mypy仍同为
  62 errors，证明本 Rx 无类型债增量。
- 本段进入 formal 后执行 final truth sync/audit 与 manifest exact，再提交 records identity；此后不得改
  product/test/config/formal evidence，直到同 SHA LEAN/SAFETY 复审完成。

## 44. Batch 2026-07-20-042：R1 双 PASS0 与 guarded-registry C2 映射

- R1 final committed+clean identity=`0630fb0ab5170b09321085fc47be0f24ee95a4e2` / tree=
  `7c94b85d0cabafd83dd58d38bfcb9cf906ecef2d`；同一 Pascal/LEAN=`PASS0/findings=0`，同一
  Confucius/SAFETY=`PASS0/findings=0`。R1 完成并解锁 C2；远程 Codex review 仅为附加信号。
- C2 在该 reviewed 产品上执行，无产品、测试、DTO、public surface、CLI、依赖或 workflow 改动。
  `guarded_registry` public API/CLI 收集=`26/712`，由19个 baseline与7个共享 characterization节点组成；
  exact group=`26 passed, 686 deselected in 0.99s`。
- 已完成 stage 的累计 selector=`cross_spec_writeback or guarded_registry`，结果=
  `59 passed, 653 deselected in 1.27s`。覆盖显式确认、六状态可达子集、稳定空输入、视觉/无障碍问题、
  canonical YAML、默认不写、truthy bypass、falsey late-bound fallback、clock/build/execute异常顺序、
  mkdir/write_text fault 与 retry，以及 CLI dry-run/execute/write。
- C2 沿用 C1 已验证的七类共享 mutation 证据，不新增测试或临时 proof；冻结 test/config blobs保持不变。
  下一步只提交 no-code characterization records，并由相同 LEAN/SAFETY identity 复核；双 PASS0 前禁止 R2。
