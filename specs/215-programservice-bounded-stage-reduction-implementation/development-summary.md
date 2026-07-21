# 开发摘要：ProgramService 九阶段直接减重

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**状态**：cross-spec R1、guarded-registry C2 已完成；guarded-registry R2 本地双审一致 NO-GO，产品回退到 C2 安全点，待预算 formal 仲裁

## 当前事实

- WI214 closure receipt merge=`7922956d` 已通过 detached fresh-main，GAP-15/T58 保持关闭。
- 目标仍是九阶段45 methods=`3,638 physical / 3,305 executable / branch 386`，保留27 public、27 DTO、
  106 unit + 59 integration=`165` 个既有行为节点。
- 原 T61A recorder/receipt/shadow selector/T61B/deletion 路线未进入 main，也从未授权产品改动。
- 原压行 recorder=170行，但 Ruff 自然格式=587行；风险分层 spike 即使移出 public/DTO 明细，仍为
  286物理行、Ruff自然格式407行。两位 reviewer 一致判定 custom proof 体系本身过度实现。
- 旧路线按 RC-09 标记 `cancelled_no_go`；recorder 与 receipt 已从当前 RC-10 formal diff 删除。
- LEAN/SAFETY 设计评审一致接受 RC-10：九个 stage 分别采用 tests-first `Cx` 和 direct reduction `Rx`，
  每个 Rx 原生 legacy/current 两腿、exact/full/governance、同 SHA 双审，失败回到上一 reviewed tree。
- C1 final identity=`fa7f7d03/0f465334` 已获 LEAN/SAFETY 同identity双 `PASS0`，首个产品 Rx 已解锁。
- Formal identity `dbc02c65` 已获 LEAN/SAFETY 同身份双 `PASS0`；只授权 tests-only C1。
- C1 保留63个共享九阶段节点，并为首stage补10个public节点；结构去重后Ruff自然格式proof=`287≤290`，
  当前union=`238`。覆盖truthy/falsey、经`self` late-bound、clock顺序/异常、输入与输出loader的
  missing/malformed/non-mapping、可达状态、relative/outside-root、write fault与retry；产品仍零差异。
- `cross_spec_writeback` 的 returned `failed` 无公开可达输入：成功写入必登记路径，失败直接传播。C1冻结
  真实fault语义，首个Rx删除该dead branch，不伪造状态。
- cross-spec R1 已新增唯一 private engine 并删除五个重复 body；两位 reviewer 对初稿 `417/59` 一致
  HARD FAIL，修正后 target slice=`385 LOC / 48 branch`，严格低于 legacy `392/50`；最大函数49行。
- 首轮 review 前 retained product/proof/combined=`414/287/701`，定向=`33 passed`、累计=`238 passed`、full=
  `3376 passed, 3 skipped`；immutable A/B 两腿均238通过，JUnit节点顺序与raw tree逐字节一致；
  Ruff/constraints/validate/plan/truth全绿，manifest exact=`1 passed`。待final records identity与本地双审。
- 首轮 R1 review identity=`6e3c661b` 得到 LEAN=`FAIL2`、SAFETY=`FAIL1`；共同 typed-binding finding已用
  私有 Protocol/具体泛型修正，`all(tuple)`已恢复直接布尔条件。candidate engine mypy=0，
  ProgramService strict mypy与legacy同为62 error、增量0。
- 修正后 target/product/proof/combined=`371/441/287/728`，branch=48、最大函数49；定向33与累计238
  已重跑全绿。新 checkpoint full=`3376 passed, 3 skipped`；A/B两腿各238通过，JUnit顺序和raw tree
  逐字节相同；Ruff/constraints/validate/plan全绿。
- R1 final committed+clean identity=`0630fb0a/7c94b85d` 已由同一 Pascal/LEAN 与 Confucius/SAFETY
  分别给出 `PASS0/findings=0`；R1 完成，远程 Codex 不构成进入下一阶段的阻塞。
- C2 在上一 reviewed 产品上仅做覆盖映射，不修改产品或冻结测试：`guarded_registry` public/CLI
  exact group=`26 passed, 686 deselected`，与已完成 cross-spec 的累计组=`59 passed, 653 deselected`；
  19 个 baseline 与 7 个共享 characterization 节点全部保留。
- C2 no-code identity=`6bcdb477/f17f065b` 的 LEAN/SAFETY 均为 `FAIL1`：缺 guarded-registry
  skipped/partial、非法 target、step fault/retry、returned failed不可达证据与该 stage 输出 loader。
- 最小修正保留原26节点并净增11个 public 节点，当前 group=`37 passed`、累计=`70 passed`、九stage
  exact union=`249`；四类临时 mutation 分别得到3/2/4/1+1个预期失败后恢复产品原哈希。
- 测试 helper 复用使 test checkpoint 实际 diff=`151 additions/207 deletions`；独立 Ruff 格式化双副本
  复算 proof=`285≤290`，product+proof=`441+285=726≤729`，没有为补缺口增加测试臃肿。
- C2 clean full=`3387 passed, 3 skipped in 693.78s`；immutable legacy/current产品两腿各249通过，
  JUnit节点顺序与raw tree逐字节一致。Ruff/constraints/validate/plan全绿；pre-records truth=
  `ready/fresh 1131/1131/0/0`、snapshot=`4ab61c0d...5cea5`，manifest exact=`1 passed in 109.35s`，
  scope/clean通过；records-only resync后的权威final snapshot以`program-manifest.yaml`为准。
- records identity=`5622ba10/e4c9a7d1` 已获 LEAN=`PASS0`；SAFETY=`FAIL1`仅指出上述final gate
  provenance尚未写回文档。本次只做records-only收口，产品与测试blobs不变。
- C2 final identity=`18609c47/fa9d0b08` 已获同一 LEAN/SAFETY 双 `PASS0/findings=0`；R2 随后只改
  private engine 与 cross/guarded facade，产品 checkpoint=`9855834c/def015ef`，冻结测试/config未改。
- R2 删除双层 binding 与回绕职责，保留 public 默认 clock/build/execute 边界。累计 focused=`70 passed`，
  full=`3387 passed, 3 skipped`；immutable legacy/current各249通过，JUnit节点和raw tree相同。
- R2 target=`380 LOC/61 branch/max 50`，严格低于 legacy cross+guarded=`792/92/max177`；
  product/proof/combined=`444/285/729`均在硬上限内。Ruff/mypy/constraints/validate/plan/truth audit全绿。
- R2 evidence source=`de7d4d63`、首轮 manifest sync=`9a50479a`；clean audit=`ready/fresh
  1131/1131/0/0`，manifest exact=`1 passed in 102.65s`。本记录进入 source 后执行最后一次机械 sync，
  final snapshot权威值以同一提交的`program-manifest.yaml`为准。
- 上述 R2 数值随后被正式双审推翻：自然 Ruff 格式后 candidate product=`591`、combined=`876`，且
  `payload()`=59行；`93963a37` 的 LEAN/SAFETY 均为 `FAIL3`，旧`444/729/max50`证据退役。
- 修正 identity=`21dccc79/9fbaaad3` 保持行为测试与mypy增量0，但仍保留adapter/rules/callback微型DSL；
  同一两位reviewer均返回`CONSTRAINT_CONFLICT / R2 NO-GO`。
- 共同建议的无DSL显式双-stage spike经Ruff自然格式后仅engine即704行；当时必要facade估算使
  product约`749–763`、combined约`1034–1048`，证明当前实现不达预算，但不是最小下界。
- 未批准R2产品已暂存回退到C2 final blobs；冻结proof、tests/config和失败证据保留。按WI213 §10，
  后续只先仲裁自然LOC预算度量/上限，不以删proof、压行、未来摊销或恢复DSL伪造减重。
- Round 3双方最终`CONVERGED`：不预授权新行为接口，只在用户明确授权后以隔离九stage无DSL自然spike
  实测RC-03/RC-05 residual LOC。spike-readiness复核纠正：双stage `749–763`缺可重放source且仅代表
  一个实现，不能称为terminal反证；`2615`也只是线性投影。
- 后续公平比较必须报告45-symbol raw legacy/C2=`3638/3303`和Ruff-natural=`3825/3465`，另计private
  engine与glue；不得用raw legacy对natural candidate或把cross facade `57`冒充完整实现成本。

## 兼容与减重边界

- 不保留双实现、runtime selector、dead branch、持久 controller、custom receipt/schema 或 normalizer。
- 只允许唯一 private engine；DTO 与 public facade 留在 `program_service.py`；测试只调用 public API/CLI。
- 真实缺口 characterization 最小覆盖 missing/malformed、六状态、path/confirmation、late-bound/truthiness、
  时钟求值与 fault/retry；public/DTO denylist 覆盖完整可观察定义。
- retained product≤522、proof≤290、combined≤729、route cumulative≤1,500、terminal≤720、
  net delete≥2,918、responsibility reduction≥3,278、branch≤90、新/改函数≤50。
- 每 stage 目标 LOC/branch 必须下降；任何临时 scaffold 都按峰值计费，删除不返还预算。
- 不改版本/tag/Release/PyPI/共享 CLI；T66/GAP-03/WI196/RC-08/release 继续 open。

## 下一步

1. 用户已于 2026-07-21 授权隔离实测；首轮 cross-only identity 经双 `STOP_SPIKE_FAIL3` 发现漏计 DTO
   glue、六个单调用层级及两项行为漂移。最小修正后 public/full/exact 全绿、27 public/DTO零变化、
   mypy增量0、max function47，完整账本=`451 engine + 75 exact + 85 glue =611 LOC / 88 branch`；
   behavior-legacy canonical product=`572>522`、combined=`857>729`。该结果只证明当前单 stage 结构仍
   没有净减重，尚不是九stage终态 `T*`；新产品 immutable A/B与review缺口public probes已等价，
   必须先提交records identity并由
   同一 LEAN/SAFETY 双审，才能决定是否
   继续扩展，绝不能把功能全绿解释为预算通过或可合入。
   第二轮复审为LEAN PASS0、SAFETY FAIL1；新增manifest `../outside`异常漂移已用public RED/GREEN修复。
   第三轮为LEAN PASS0、SAFETY FAIL2；重复spec id末项覆盖和空格path解析两项public RED均成立，现已在
   唯一private resolver中最小修正。新完整target=`614/88`、canonical product/combined=`575/860`；
   checkpoint=`b71e4147/d23ddd0f`的immutable A/B各249通过，raw/JUnit与六类public probes均等价；
   records identity=`01a69268/35ff5a36`已获同一 LEAN/SAFETY 双
   `CONTINUE_SPIKE_PASS0/findings=0`，只解锁继续实测下一stage，不构成formal预算或合并通过。
2. 双审只仲裁当前结构是否适合作为九stage实测样本；未取得同一 committed+clean 身份一致结论前，
   不扩展下一 stage，不修改 C2-safe 产品分支，也不调整 formal 预算。
3. 九stage `T*` 取得后再由同一 LEAN/SAFETY评审新 formal；远端 Codex 仅作附加信号，不无限等待。
4. 隔离实测在第二个`guarded_registry` stage即得到完整target=`1209 LOC / 164 branch`，高于两stage legacy
   `842/92`并超过branch≤90；checkpoint=`6c945b40/6341bcb2`由LEAN/SAFETY一致判定
   `STOP_SPIKE_NO_GO/findings=0`。按hard-stop省略full/A-B、停止第三stage；spike仅留审计，formal继续以
   clean C2-safe `70f19275/2fdd9aaa`为上一reviewed tree。
