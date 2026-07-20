---
related_plan: "specs/213-programservice-bounded-stage-reduction/plan.md"
related_doc:
  - "specs/213-programservice-bounded-stage-reduction/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 实施计划：ProgramService 九阶段直接减重

**Goal:** 不引入运行时双实现或自定义 proof framework，把九阶段 45 个重复方法原地收敛为一个私有 engine。

**Architecture:** DTO 与 public facade 留在 `program_service.py`；唯一 `_program_bounded_stage.py` 只接收
显式 typed/path/callback binding。每个 stage 使用 characterization checkpoint `Cx` 和 reduction
checkpoint `Rx`，以 immutable legacy/current 两腿、全量测试、同 SHA 双审和 Git revert 控制风险。

**Tech Stack:** Python 3.11、dataclasses、pathlib、PyYAML、Typer、pytest、Ruff、uv；新增依赖为 0。

## 1. 退役旧路线

在任何产品改动前：

1. 删除 `scripts/program_bounded_stage_t61a.py` 与对应 receipt；确认未残留 controller、selector、route。
2. 在 WI196/WI213/WI215 记录旧路线 `cancelled_no_go` 与 natural-format spike 407 行证据。
3. 运行 formal 双审；只有同 identity 双 PASS 后才冻结 implementation-base。
4. 行为 legacy 保持 `7922956d` / `cc3c6b7f`；目标 `src/tests/config/toolchain` hash 不变。

## 2. 文件职责

| 文件 | 职责 |
|---|---|
| `src/ai_sdlc/core/_program_bounded_stage.py` | 唯一 private definition/strategy/engine |
| `src/ai_sdlc/core/program_service.py` | DTO、public facade、显式 typed binding；逐 stage 删除重复 body |
| `tests/unit/test_program_service.py` | 现有 106 nodes 与最小共享 characterization |
| `tests/integration/test_cli_program.py` | 现有 59 nodes、CLI/raw artifact characterization |
| `specs/215-*/task-execution-log.md` | 命令、SHA、JUnit/raw hash、LOC/branch/budget 与 verdict |

不创建第二产品模块、持久 runner、snapshot schema、normalizer、runtime route 或新依赖。

## 3. Pre-product formal gate

- 复算 formal-six/formal-three、legacy commit/tree 和目标 blob identity。
- `src/**` 与两份目标行为测试相对 legacy 零差异。
- Ruff、constraints、validate、truth、manifest exact、scope/parity/clean 全绿。
- Pascal/LEAN 与 Confucius/SAFETY 对同一个 committed+clean identity 双 PASS0。
- 双 PASS 后提交的下一笔只允许开始第一个 `C1`；不得同时写 engine。

## 4. 每阶段原子循环

顺序固定为 cross-spec、guarded、broader、final governance、persistence、persisted proof、publication、
closure、archive。

### 4.1 Characterization `Cx`

1. 映射当前 stage 既有 exact nodes 与分支。
2. 只有覆盖缺口才增加共享参数化测试；新增断言只调用 public API/CLI。
3. 共享用例显式冻结 truthy bypass、`None`/falsey fallback、经 `self` 的 late-bound callback、
   `generated_at` 时钟调用次数/顺序/异常，以及首次 fault 后无 completed artifact、同输入 retry 等价。
4. 在 legacy 产品源码上运行并 PASS；至少用 `or`→`is None`、绕过 `self` callback、eager clock
   evaluation 临时 mutation 证明缺陷会被捕获。
5. 提交 tests-only checkpoint；冻结 test tree/blob/node IDs，不允许 `Rx` 修改断言；同时冻结 public
   name/signature/annotations/defaults/docstring/module/qualname 与整个 DTO definition 的逐 stage denylist。

若无需新增测试，`Cx` 可以是只记录 immutable coverage mapping 的 no-code checkpoint，但仍须先于 `Rx`。

### 4.2 Reduction `Rx`

1. 在唯一 private engine 中实现当前 stage 最小行为。
2. 当前 stage public facade 直接调用 engine，并在同一 diff 删除对应重复 body。
3. 不保留 selector、legacy branch、dead code 或临时 scaffold。
4. 运行当前/累计/exact165/full、legacy/current 两腿及全部治理门。
5. 记录本 stage product/test/proof 增量、目标 LOC/branch 下降和累计预算。
6. 提交 clean `Rx`，取得 LEAN/SAFETY 同 SHA 双 PASS 后才进入下一 `Cx`。

## 5. Legacy/current 两腿

- 使用同一冻结 candidate test definition 与 seed；测试不得 import private engine。
- 建立独立 legacy/current worktree、basetemp、pytest cache 和 artifact root。
- 固定 Python3.11、lockfile、locale/timezone/environment allowlist。
- 先验真 cwd、HEAD/tree、import module path 与 source/test/config SHA。
- 比较 ordered node IDs、JUnit testcase/outcome、CLI stdout/stderr 与 raw artifact bytes/tree。
- 非确定字段必须用冻结输入或现有 canonical YAML/JSON 比较；不得新增 normalizer。
- 原生 artifacts 进入 CI/review evidence；log 只登记 command、locator、SHA-256 与 byte length。

## 6. 预算与结构 gate

- retained product≤522；retained proof≤290；product+proof≤729；roadmap cumulative≤1,500。
- terminal≤720；net delete≥2,918；responsibility reduction≥3,278；branch≤90。
- 每个新增/修改函数≤50行；每 stage 目标 LOC 与 branch 严格下降。
- 禁止 public abstraction、依赖、DSL、registry、反射或字符串 method lookup。
- 预算按真实新增和阶段峰值计量；删除临时代码不返还预算。

## 7. Terminal gates

1. 复算 public/DTO/method/surface/structure legacy/current 对账。
2. full suite、Ruff、constraints、validate、truth、manifest、scope/clean。
3. cross-platform required checks。
4. wheel/sdist；两个 clean env `--no-index --find-links` 安装；offline smoke。
5. 至少两个 sibling project 只使用安装产物 smoke。
6. fresh-main 等价 squash/revert 演练：tree 回到 implementation-base，exact165/full/CLI/smoke PASS。
7. 最终 candidate 再验并由 LEAN/SAFETY 同 SHA PASS0。

## 8. PR、合并与回退

- 九阶段完成后 push/open PR；required checks 与本地双审是硬门，远端 Codex 只作附加信号，不无限等待。
- squash merge；不删除本地分支。
- detached fresh-main 重跑 terminal gates。
- 失败只精确 revert squash SHA；不依赖 runtime selector，不发布版本。
- fresh-main 后另建 lifecycle reconciliation 分支/PR，关闭 WI215/T66/GAP-03；WI196/RC-08/release 仍按总路线处理。
