# 功能规格：ProgramService 九阶段直接减重

**功能编号**：`215-programservice-bounded-stage-reduction-implementation`
**创建日期**：2026-07-20
**状态**：RC-10 formal remediation；产品实现阻断
**类型**：WI-196 / WP-06 / T66 / GAP-03 / L3 implementation
**父合同**：`specs/213-programservice-bounded-stage-reduction/spec.md`
**行为基线**：`7922956d3e248a93c3190240259850ab3498ec9f` / tree
`cc3c6b7f7e63dd040034938ff6bb6827f067e41c`

## 1. 决策与授权边界

原 `T61A recorder + receipt + shadow selector + T61B + independent deletion` 路线已判定
`cancelled_no_go`。其自然格式 spike 为 286 行，Ruff 格式化后为 407 行，无法满足 recorder≤180、
proof≤290、product+proof≤729；继续压行、拆脚本或删除安全证据均违反 RC-06/RC-09。

因此本 WI 删除尚未进入 main 的 recorder、receipt、test controller、runtime selector 和双实现计划，
改为九个 stage 原地、小步、可回退的直接重构。删除的是未合入的证明基础设施，不是产品能力。

任何 `src/**` 改动前必须同时满足：

1. WI196、WI213、WI215 的 RC-10 formal 对同一 committed+clean identity 取得 LEAN/SAFETY 双 PASS；
2. 行为基线 commit/tree 仍可达，目标源码、测试、配置与工具链身份已冻结；
3. formal 修订后的 pre-product implementation-base commit/tree 已冻结；
4. 工作树 clean，产品和两份目标行为测试相对行为基线仍零差异。

本 WI 不修改版本、tag、GitHub Release、PyPI、共享 CLI、依赖、workflow 或其他 ProgramService domain。
T66/GAP-03/WI196/RC-08 在最终 fresh-main、回退演练和 lifecycle receipt 前保持 open。

## 2. 目标与范围

目标是把九个 frontend bounded stage 的 45 个重复方法收敛到一个私有 engine，同时保持：

- 27 个 public callable 的名称、签名、annotation、doc、module/qualname；
- 27 个 DTO 的字段顺序、type/default/factory、equality 与 post-init；
- CLI 命令、option、exit/stdout/stderr、授权、异常、路径和 artifact bytes/tree；
- loader/builder/direct/CLI、late-bound、fault、retry、partial、missing/malformed 与写入异常语义。

Stage 顺序与 exact165 分组固定为：

| Stage | Existing nodes |
|---|---:|
| `cross_spec_writeback` | 16 |
| `guarded_registry` | 19 |
| `broader_governance` | 19 |
| `final_governance` | 19 |
| `writeback_persistence` | 19 |
| `persisted_write_proof` | 19 |
| `final_proof_publication` | 20 |
| `final_proof_closure` | 17 |
| `final_proof_archive` | 17 |

九组必须 disjoint，union 精确为 106 unit + 59 integration = 165；不得 rename、delete、skip、xfail、
deselect 或以新测试替换原节点。`thread_archive`、project cleanup 与其他 domain 不在范围内。

## 3. RC-10 直接重构模型

每个 stage 必须形成两个不可变 checkpoint：

1. `Cx` characterization-only：在重构前产品上 PASS；只有真实覆盖缺口才新增测试，并用临时负向变异
   证明测试会失败。没有缺口时只登记 coverage mapping，不增加测试。
2. `Rx` reduction-only：禁止修改 `Cx` 断言；只扩展唯一 private engine、替换当前 stage body，并删除
   该 stage 已失活重复职责。不得保留双实现、selector、dead branch 或临时 scaffold。

每个 `Rx` 从上一 clean、已双审 commit 开始。LEAN/SAFETY 必须对同一个 committed+clean `Rx` 给出
PASS0 且 findings=0，才允许进入下一 stage。任何身份变化使旧 verdict 失效。

### 3.1 最小 characterization 补强

补强只允许参数化复用，不复制九套测试体：

- missing/malformed/non-mapping upstream artifact：warning、blocked/missing 状态与零副作用；
- `skipped / confirmation_required / blocked / partial / failed / completed` 状态矩阵；
- invalid/outside-root/relative target、默认未确认写入与 path resolution；
- `provided_value or callback()` 与 `generated_at or utc_now_z()` 的 truthy bypass、`None`/falsey fallback、
  经 `self` late-bound 的 subclass/patch override、调用次数/顺序与异常传播；
- 目录创建/写入首次 fault 必须向上传播且不留下 completed artifact；同一输入重试的结果、调用顺序与
  artifact 必须与 legacy 一致；
- public/DTO 只用 public API/CLI 验证；测试不得 import private engine。

若某个 legacy 状态分支无法由 public 输入正常返回，coverage mapping 必须给出控制流证据，并用 public
fault/retry 冻结实际可观察语义；对应 `Rx` 直接删除该不可达分支，不得通过 private helper、内部容器篡改或
异常吞噬伪造可达状态。`cross_spec_writeback` 的 returned `failed` 属于此类：可执行目标在写入前计数，
成功写入后立即登记路径，写入失败则向上传播，因此不存在正常返回 `failed` 的 public 输入。

每类新增断言必须用临时 mutation 证明会 RED；至少覆盖 `or` 改为 `is None`、绕过 `self` callback、
eager clock evaluation。Public method 的 name/signature/annotations/defaults/docstring/module/qualname 与整个
DTO class definition 默认属于逐 stage diff denylist。若无法机器保证，才允许增加一份紧凑参数化 contract
test，不恢复 custom snapshot/recorder。

### 3.2 原生 legacy/current 两腿

每个 stage 在两个独立 clean worktree 中使用同一冻结测试定义、seed、Python3.11 和 lockfile：

- A 腿加载 immutable behavior legacy `7922956d` 的产品源码；
- B 腿加载当前 `Rx` 的产品源码。

两腿必须先验真 cwd、commit/tree、`sys.executable`、imported module `__file__`、源码/测试/config hash，
再比较当前 stage 与累计节点的 ordered IDs、JUnit outcome、CLI/stdout/stderr 及确定性 raw artifact bytes/tree。
含时间等非确定字段时，只允许使用冻结输入或现有 canonical YAML/JSON 语义比较。

不新增持久 controller、normalizer、custom receipt 或第二 schema。命令、原生 JUnit、stdout/stderr、
raw artifact locator/hash/length 和 review verdict 进入 CI/review evidence 与 execution log。任一 evidence、
ref、import provenance、required check 或双审缺失即 NO-GO。

## 4. 架构与预算

- 新增唯一 `src/ai_sdlc/core/_program_bounded_stage.py`；不 import service/CLI。
- DTO 与 27 个 public facade 留在 `program_service.py`；每个 facade 直接调用 typed binding/engine。
- 禁止 public abstraction、新依赖、反射分发、字符串 method lookup、stage-name `if/match`、registry、DSL、
  monkeypatch runtime route 或循环 import。
- 新增/修改函数≤50行；每 stage 的目标切片 LOC 和 branch 必须严格下降。

预算仍是硬门，不因退役 proof 路线而放宽：

| 约束 | 上限/目标 |
|---|---:|
| peak retained product | ≤522 |
| retained test/harness/normalizer proof | ≤290 |
| product + proof | ≤729 |
| roadmap cumulative protection | ≤1,500 |
| terminal target slice | ≤720 |
| net deletion | ≥2,918 |
| responsibility reduction | ≥3,278 |
| terminal branch proxy | ≤90 |

只计最终保留或阶段峰值真实新增行；必要测试不能记零。不得先加临时 scaffold 再删除以洗白峰值预算。

## 5. Stage 门禁

每个 `Cx/Rx` 至少执行：

1. 当前 stage exact group、累计 groups、exact165 与相关 CLI；
2. full suite，原 3303-node 基线必须仍是 candidate suite 子集；
3. legacy/current 两腿与 characterization mutation probe；
4. Ruff lint/format debt parity、constraints、program validate/truth、manifest exact、diff/scope/clean；
5. public/DTO denylist、目标测试 node identity、LOC/branch/budget ledger；
6. LEAN/SAFETY 同 SHA 双 PASS0。

失败时回到上一 reviewed tree 并重跑门禁。若回退较早 stage，必须回退从该 stage 开始的连续后缀，
不得抽走后续已经依赖的中间 stage。

## 6. 最终验收与回退

九阶段完成后还必须通过：

- 27 public、27 DTO、45 method/surface/结构的 legacy/current 可复现一次性对账；
- full、cross-platform required checks、wheel/sdist、两个 `--no-index` clean install、offline smoke；
- 至少两个有理由的 sibling project 安装产物 smoke；
- fresh-main 上构造等价 squash，实际 revert 并证明 tree 回到 implementation-base；
- revert 后 exact165、full、CLI/smoke 全绿；最终 candidate 再次全绿并双审。

真正 squash merge 后只记录唯一 merge SHA；生产回退只允许精确 revert 该 SHA。当前不发布版本，因此不保留
runtime selector 或 legacy 双实现。

## 7. 成功与 NO-GO

成功必须同时满足：九个 `Cx/Rx` 全部通过、所有公共/DTO/CLI/artifact 语义零未批准差异、预算达标、
required checks 全绿、最终双审通过、squash revert 演练可恢复 implementation-base。

以下任一成立立即 NO-GO 并保留上一 reviewed tree：测试节点减少或被弱化；legacy/current 未原生两腿；
import provenance 不可信；产品/测试/预算未对账；新增双实现/selector/proof framework；任一 stage LOC 不降；
full/package/offline/sibling/revert 失败；review/check 未绑定当前 SHA；需要发布版本才能回退。
