# Continuity Handoff

- Updated: 2026-07-21T03:28:16Z
- Reason: 九stage spike-readiness 双审修正自然口径与下界表述
- Goal: 在 C2 双 PASS0 安全基线上完成 R2 预算 formal 仲裁，再实现 guarded_registry 减重
- State: R2=`NO-GO`；产品安全回退完成，本地双审已一致收敛，等待用户授权重审 residual LOC 基准
- Stage: execute
- Work Item: 215-programservice-bounded-stage-reduction-implementation
- Branch: feature/215-programservice-bounded-stage-reduction-implementation-dev
- Review identity: C2-safe rollback checkpoint=`a0872881/20c9b11d`；仅作为formal起点，不是R2 PASS identity。

## Current Decisions

- 本地 Pascal/LEAN 与 Confucius/SAFETY 同一 committed+clean SHA 双 PASS0 是合入硬门；
  远端 Codex review 仅作增量信号，不再无限等待。
- 九 stage 坚持 tests-first `Cx` + direct `Rx`；每个 Rx 双 PASS0 后才进入下一 stage。
- T66/GAP-03/WI196/RC-08/release 保持 open；禁止 version/tag/Release/PyPI/shared CLI。
- 唯一 private engine 位于 `src/ai_sdlc/core/_program_bounded_stage.py`，不 import service/CLI，
  不新增 public abstraction、依赖、selector、registry、DSL 或反射分发。
- 五 facade 加全部 active engine 方法必须严格低于 legacy `392 LOC / 50 branch`，不得按未来复用摊销。
- R1 final identity=`0630fb0a/7c94b85d` 已获 LEAN/SAFETY 同 identity 双 `PASS0/findings=0`。
- C2 `6bcdb477` 双审均FAIL1；findings已转为11个public节点及四类mutation evidence。
- C2 truth source checkpoint=`5622ba10/e4c9a7d1`；records-only identity `ed003ccb/567424e6`
  的 LEAN=`PASS0`、SAFETY=`FAIL1`，唯一finding为本handoff中的已完成动作与身份字段陈旧。
- C2 final identity=`18609c47/fa9d0b08` 已获同 identity LEAN/SAFETY 双 `PASS0/findings=0`。
- `21dccc79/9fbaaad3` 经同一 LEAN/SAFETY 独立仲裁均为 `CONSTRAINT_CONFLICT/NO-GO`；
  远端 Codex 不是 blocker，不得用未接单覆盖本地失败结论。
- Round 3交叉质询后双方一致：不预授权 `StageSemantics` 或任何 virtual hook；仅在用户明确授权后
  进入 RC-03/RC-05 residual LOC 实测审查，并先做隔离、可丢弃的九stage无DSL自然格式spike。

## Changed Files

- `tests/unit/test_program_service.py`：补guarded输出loader、状态、路径、step fault/retry；原节点全保留。
- `specs/215-*/task-execution-log.md` 与 `development-summary.md`：记录FAIL1、mutation、预算、full/A-B。
- 两份 handoff 删除已完成动作与自引用 `Current HEAD`，并保持逐字节一致。
- `program-manifest.yaml` 仅同步 records-only truth；冻结测试、产品、DTO/public surface、其他 stage、
  CLI、依赖均未修改。
- rollback commit `a0872881` 仅恢复 private engine 与 `program_service.py` 到 C2 reviewed blobs；
  后续提交仅修正review/evidence记录，冻结 tests/config 与产品 blobs 保持。

## Evidence

- R1 final target：五 facade=`57/6`，active engine=`314/42`，合计=`371/48`，
  严格低于 legacy `392/50`；最大实现函数=`49≤50`。
- product/proof/combined=`441/287/728`；engine strict mypy=0；legacy/candidate ProgramService
  strict mypy均62 errors，增量0。
- cross=`33 passed`；累计=`238 passed`；full=`3376 passed, 3 skipped in 707.95s`。
- immutable legacy/current各=`238 passed, 474 deselected`；JUnit=`238/0/0/0`、ordered node hash
  相同；移除各35个便利symlink后 raw tree均=`767 files/717475 bytes`、hash=`ed594c67...05a35`，
  `diff -qr=0`。
- 全仓 Ruff、constraints、validate、plan-check已绿；冻结 test/config blobs保持C1不变。
- R1 truth=`ready/fresh 1131/1131/0/0`，snapshot hash=`d22cf16a...d16f2`；manifest exact=
  `1 passed in 104.51s`。
- C2 exact public/CLI group=`37 passed, 686 deselected`；与R1累计=`70 passed, 653 deselected`；
  九stage exact union=`249/723`，原26个guarded节点零缺失。
- mutation RED=`loader 3/state 2/path 4/mkdir 1/write_text 1`；恢复后产品blobs不变。
- proof/product/combined=`285/441/726`；full=`3387 passed, 3 skipped in 693.78s`。
- immutable legacy/current各249通过；JUnit节点hash相同，raw tree各780 files/732745 bytes且hash相同。
- 全仓Ruff、constraints、program validate、plan-check=`drift=false/pending=0`均通过。
- C2 pre-records truth=`ready/fresh 1131/1131/0/0`，snapshot=`4ab61c0d...5cea5`；manifest exact=
  `1 passed in 109.35s`；scope/clean通过。records-only resync后的权威final snapshot读取同提交
  `program-manifest.yaml:truth_snapshot.snapshot_hash`，不硬编码自引用hash。
- R2 product/proof/combined=`444/285/729`，满足 `≤444/≤290/≤729`；engine Ruff format/check、
  Ruff lint 与 strict mypy 均绿；累计 focused=`70 passed, 653 deselected`。调试期间9个失败证明
  ProgramService 默认编排边界不可下沉，修正后测试全绿且测试文件未修改。
- R2 target=`380 LOC/61 branch/max 50`，严格低于 legacy cross+guarded=`792/92/max177`；full=
  `3387 passed, 3 skipped in 665.41s`。immutable legacy/current各249通过，JUnit ordered node hash与
  raw `780 files/732745 bytes` tree hash相同，`diff -qr=0`。
- 全仓 Ruff、constraints、program validate、plan-check均绿；pre-records truth audit=
  `ready/fresh 1131/1131/0/0`。
- evidence source=`de7d4d63`，manifest sync checkpoint=`9a50479a/786dadc4`；clean audit=
  `ready/fresh 1131/1131/0/0`，manifest exact=`1 passed in 102.65s`，scope/clean为空。
- formal records=`fc699502` 后 final truth sync snapshot=
  `5abc99462a653cb5d95238d8cb647b73808d5cc504810b170a05f6ba76439d55`；clean final audit=
  `ready/fresh 1131/1131/0/0`，manifest exact=`1 passed in 102.93s`。
- 修正后的自然格式账本为 engine=`428` physical、service additions=`163`，product=`591`；
  proof=`285`，combined=`876`，分别超过有效 product cap `444` 与 combined cap `729`。
- LEAN 与 SAFETY 共同要求去除 adapter/rules/callback 微型 DSL。按该建议制作的未提交、已恢复
  显式双-stage spike：private engine=`704` physical、strict mypy=`0`，尚未计 facade glue。
- LEAN 独立分解无 DSL 下界为 engine=`704` + service glue约`59` = product约`763`，combined约`1048`；
  SAFETY 独立确认当前无可信 `≤444/≤522` 路线。双方均拒绝删 proof、压行、未来摊销或恢复 DSL。
- `git revert --no-commit 21dccc79` 与 `git revert --no-commit 9855834c` 后，两个产品 blob 已逐一验真
  等于 C2 final identity `18609c47` 对应 blob；回退提交=`a0872881/20c9b11d`。
- 回退后累计 focused 命令=`uv run --python 3.11 pytest --import-mode=importlib -q
  tests/unit/test_program_service.py tests/integration/test_cli_program.py -k 'cross_spec_writeback or guarded_registry'`，
  结果=`70 passed, 653 deselected in 1.58s`。
- spike-readiness复核修正公平口径：45-symbol legacy/C2 raw=`3638/3303`，Ruff-natural=
  `3825/3465`；未来必须 natural-to-natural 比较，并另计C2 private engine=`394`与范围内glue。
- 双stage `704 engine + 45–59 service =749–763` 是未提交、已恢复的单个实现及glue估算，没有可重放
  commit/tree/blob，故只能作为高风险信号，不能称为terminal下界或反证；`2615`也仅是线性投影。
- Round 3及spike-readiness final：LEAN/SAFETY均要求用户只授权隔离实测RC-03/RC-05基准；行为、proof、
  无DSL/registry/reflection/string lookup/stage selector/rule table/callback bundle/virtual hook/type erasure、
  typed、函数≤50、branch≤90均不放宽。

## Blockers / Risks

- 当前 user-input blocker 是是否授权隔离实测 RC-03/RC-05 residual LOC 基准。该授权不等于放宽
  或接受新数字；只允许制作有commit/tree/blob与完整provenance的九stage spike取得`T*`，再由同一双审
  判断旧terminal是否可达、是否仍有实质减重价值。

## Exact Next Steps

1. 请求用户单一授权：允许隔离实测RC-03/RC-05 residual LOC基准并制作可丢弃的九stage spike。
2. 若授权，先新建隔离分支/worktree实测`T*`，不改当前C2-safe分支；再形成formal并双审。
3. 若不授权，保持R2与九stage路线NO-GO，不合入未批准产品改动。
