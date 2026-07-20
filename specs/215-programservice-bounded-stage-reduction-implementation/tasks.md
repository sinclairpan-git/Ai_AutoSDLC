---
related_plan: "specs/213-programservice-bounded-stage-reduction/plan.md"
related_doc:
  - "specs/213-programservice-bounded-stage-reduction/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 任务分解：ProgramService 九阶段直接减重

**编号**：`215-programservice-bounded-stage-reduction-implementation`
**当前门禁**：RC-10 formal 双 PASS 前禁止 `src/**` 与目标行为测试改动

## Batch 0：旧路线退役与 formal

### T01～T03 原 WI 创建与 formal authoring（completed）

- WI214 closure main=`7922956d` 后建立独立 WI215 worktree；原 formal authoring 已完成。
- 该 authoring 只批准旧 T61A 设计，不授权产品代码。

### T04 旧 T61A 实证（completed_no_go）

- 原压行 recorder=170；Ruff 自然格式=587。
- 风险分层 spike 移出 surface/DTO 明细后仍为286，Ruff自然格式=407。
- LEAN/SAFETY 一致认定 custom proof 路线过度、违反 RC-06/RC-09。

### T05 RC-10 formal 修订（completed）

- 删除 recorder/receipt/T20/controller/selector/deletion 路线。
- 同步 WI196/WI213/WI215；记录 `cancelled_no_go`，产品与目标测试保持零差异。
- 运行 constraints/validate/truth/manifest/scope/clean，提交 committed+clean formal identity。

### T06 RC-10 formal 双审（completed）

- Pascal/LEAN：YAGNI、预算、逐 stage 净下降、无临时预算洗白。
- Confucius/SAFETY：characterization、两腿、SHA 绑定、回退与 package/offline。
- 同 identity 双 PASS0/findings=0 后冻结 implementation-base；否则继续 formal 修正。

## Batch 1：Characterization 缺口

### T11 Shared characterization RED/GREEN（in_review）

- 仅在真实缺口处增加参数化 public API/CLI tests：
  missing/malformed/non-mapping、六状态矩阵、invalid/relative/outside-root、默认确认、truthy bypass、
  `None`/falsey fallback、经 `self` 的 late-bound callback、`generated_at` 时钟次数/顺序/异常、首次写入
  fault 后无 completed artifact与同输入 retry 等价。
- 先在 legacy source 上 PASS；至少用 `or`→`is None`、绕过 `self` callback、eager clock evaluation
  临时 mutation 证明会 RED。
- 不 import private engine，不改 `src/**`，不删除/rename/skip/xfail/deselect 原165节点。
- 提交 `C1`，双审后冻结 test tree/blob/node IDs，以及 public name/signature/annotations/defaults/
  docstring/module/qualname 与整个 DTO definition 的逐 stage denylist。

## Batch 2：九阶段 Cx/Rx

每项都先完成当前 stage coverage mapping/`Cx`，再完成只改实现的 `Rx`：

| Task | Stage | Existing nodes | 状态 |
|---|---|---:|---|
| T21 | `cross_spec_writeback` | 16 | pending |
| T22 | `guarded_registry` | 19 | pending |
| T23 | `broader_governance` | 19 | pending |
| T24 | `final_governance` | 19 | pending |
| T25 | `writeback_persistence` | 19 | pending |
| T26 | `persisted_write_proof` | 19 | pending |
| T27 | `final_proof_publication` | 20 | pending |
| T28 | `final_proof_closure` | 17 | pending |
| T29 | `final_proof_archive` | 17 | pending |

每个 task 的完成定义：

- `Cx` 在上一 reviewed 产品上 PASS，`Rx` 不修改其断言；
- 唯一 private engine 扩展与当前重复 body 删除在同一 `Rx`；无双实现/selector/dead code；
- legacy/current 独立 worktree 两腿 provenance 与 raw/JUnit/CLI 零未批准差异；
- 当前组、累计组、exact165、相关 CLI、full suite 全绿；
- Ruff/constraints/validate/truth/manifest/scope/clean 全绿；
- product/proof/combined 与 LOC/branch ledger 达标，目标 LOC/branch 严格下降；
- LEAN/SAFETY 对同一 `Rx` 双 PASS0 后才能进入下一 task。

## Batch 3：Terminal 与交付

### T31 Surface/DTO/结构终验（pending）

- 一次性可复现命令对账27 public、27 DTO、45 method 与结构/branch。
- 命令和 raw hash 写 log，不新增 recorder/snapshot schema。

### T32 Full/platform/package/offline/sibling（pending）

- full、Ruff、constraints、validate、truth、manifest、required cross-platform checks。
- wheel/sdist；两个 no-index clean install；offline；至少两个 sibling 安装产物 smoke。

### T33 Squash revert rehearsal（pending）

- 在 fresh main 构造等价 squash，实际 revert。
- tree 精确恢复 implementation-base；exact165、full、CLI/smoke PASS。
- 回到 candidate 后再次全绿。

### T34 Final local review 与 PR（pending）

- LEAN/SAFETY 对最终 committed+clean identity 双 PASS0，findings=0。
- push/open PR；required checks全绿；远端Codex仅附加，不作无限等待门。
- squash merge，不删除本地分支；detached fresh-main 完整验收。

### T35 Lifecycle reconciliation（pending）

- fresh-main 后创建独立 lifecycle reconciliation 分支/PR。
- 只在实现、回退、fresh-main证据齐全后关闭 WI215/T66/GAP-03。
- WI196/RC-08/release 未满足部分继续 open；不发版本或更新共享 CLI。
