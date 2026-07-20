# 开发摘要：ProgramService 九阶段直接减重

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**状态**：C1 同identity双PASS；cross-spec R1 已实现，待 immutable A/B、治理门与同identity双审

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
- 当前 retained product/proof/combined=`414/287/701`，定向=`33 passed`、累计=`238 passed`、full=
  `3376 passed, 3 skipped`；immutable A/B 两腿均238通过，JUnit节点顺序与raw tree逐字节一致；
  Ruff/constraints/validate/plan/truth全绿，manifest exact=`1 passed`。待final records identity与本地双审。

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

1. 对最终 records 文字执行最后一次 truth sync、truth audit、manifest exact 与 scope/clean。
2. 提交 final R1 records，核验 product/test/config blobs 与 checkpoint 不变。
3. 取得 Pascal/LEAN 与 Confucius/SAFETY 对同一 clean R1 identity 的双 PASS0；通过后才允许进入
   guarded_registry C2/R2。
