# 开发摘要：ProgramService 九阶段直接减重

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**状态**：RC-10 formal 双PASS；C1 characterization review，产品实现仍阻断

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
- 当前 `src/**`、`program_cmd.py` 和两份目标行为测试相对 behavior legacy 仍零差异；尚未创建 private engine。
- Formal identity `dbc02c65` 已获 LEAN/SAFETY 同身份双 `PASS0`；只授权 tests-only C1。
- C1 在单一共享参数化矩阵中新增63个九阶段用例/204行，冻结truthy/falsey、经`self` late-bound、
  clock次数/顺序/异常与mkdir/write首次fault后无artifact、同输入retry字节等价；产品仍零差异。

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

1. 将 C1 tests-only tree 固定为 committed+clean identity，并以 immutable legacy/current 两腿复核。
2. 取得 Pascal/LEAN 与 Confucius/SAFETY 对同一 C1 identity 的双 PASS0，冻结测试blob/node IDs与
   public/DTO denylist。
3. C1 双PASS后才允许首个 `cross_spec_writeback` Rx；在该Rx前不写engine。
