---
related_plan: "specs/213-programservice-bounded-stage-reduction/plan.md"
related_doc:
  - "specs/213-programservice-bounded-stage-reduction/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 任务分解：ProgramService Bounded Stage Reduction Implementation

**编号**：`215-programservice-bounded-stage-reduction-implementation` | **日期**：2026-07-20
**来源**：本 WI spec/plan + WI213 canonical contract
**当前门禁**：T61A 双 readiness GO 前 `src/**` 零差异、两份目标行为测试 blob 不变；`tests/**`
只允许 manifest inventory/close 数字机械替换

## Batch 0：Canonical WI 与 formal authoring

### T01 从 receipt fresh main 建立唯一 WI（completed）

- **依赖**：WI214 closure receipt merge=`7922956d` 与 detached fresh-main全绿。
- **完成**：独立 worktree；`feature/215-programservice-bounded-stage-reduction-implementation-docs`；
  canonical spec/plan/tasks/log与manifest sequence已创建。
- **边界**：`init` 刷新的Cursor文件恢复为base bytes；`src/tests/workflow/dependency/version/release`未改。

### T02 重写 formal 并绑定 WI213（completed）

- **文件**：本 WI五份canonical文档、`program-manifest.yaml`、project sequence，以及 manifest exact test
  的 inventory/close 数字机械替换。
- **验收**：无placeholder/direct-formal/workitem scaffold漂移；dependency只指向WI213；T61A→candidate→
  stability→deletion/rollback顺序、预算、NO-GO、回退与release边界完整。
- **验证**：placeholder scan、constraints、validate、truth、manifest exact、scope/diff-check。

### T03 Formal authoring commit（completed）

- **依赖**：T02。
- **验收**：逻辑单一commit；relative base为`7922956d`；`src/**`零差异、两份目标测试blob不变、
  manifest test无逻辑/物理LOC变化；worktree clean。
- **后续**：不单独以formal PASS冒充T61A readiness；继续proof-only batch。

## Batch 1：T61A legacy baseline 与双 readiness

### T11 冻结 legacy inventory（completed）

- **文件**：只写execution log/后续receipt，不写产品。
- **验收**：45 methods=`3,638/3,305/333/386`；27 public；27 DTO；18 private外部consumer=0；
  165=`106 unit + 59 CLI`。
- **运行**：exact selector单次、两个独立`--basetemp`、toolchain/source/dependency hashes。

### T12 采集 selector characterization（completed；非最终性能）

- **依赖**：T11 selector健康。
- **完成**：一次warm-up+20个成功selector样本及nearest-rank p50/p95，已写execution log。
- **边界**：receipt尚不存在；本characterization直接作为T14 performance section的20个原始样本，
  T61B仍须三方同机重采。

### T13 TDD 实现唯一 recorder（completed）

- **Create**：`scripts/program_bounded_stage_t61a.py`。
- **RED**：命令只因文件不存在失败。
- **GREEN**：实现45-symbol AST inventory；public signature/parameter/return/raw annotations/doc/module/qualname；
  DTO fields顺序/default/factory/equality与post-init presence/module/qualname/signature/source；formal/source/
  dependency/toolchain identity；exact165 ordered nodes与目标test/fixture/config blob hash；双basetemp结果、既有
  20样本原始duration、预算和工作树前后不变；按spec §4 anchored grammar冻结九组exact node IDs/count，
  record/verify分组前拒绝任何thread_archive/project_cleanup node，并冻结两个测试文件各九个file-qualified
  seed helper source SHA。目标≤170、hard cap200、函数≤50；总proof hard cap290。
- **风险分层**：loader/builder/direct/CLI、late-bound、fault/termination、transient sentinel和raw tree动态
  矩阵迁移至每stage/T61B三方replay，不在T61A重复实现。
- **禁止**：第二harness/DSL/依赖/产品模块、typed canonicalizer、normalizer、per-node transitive AST mapper。

### T14 生成机器 receipt（in_progress）

- **Create**：`.ai-sdlc/work-items/215-programservice-bounded-stage-reduction-implementation/t61a-legacy-baseline-receipt.json`。
- **验收**：`record`写schema v2唯一receipt；identity/structure/tests/performance/budget五个JSON-primitive
  section及hash齐全，双basetemp 165/165、20原始duration、worktree不变、预算全部PASS；`verify`只读重算；≤2MiB。
- **NO-GO验收**：可清理失败以temp+flush+fsync+replace写同schema no_go receipt并非零退出；不可清理死亡
  由外部envelope记录exit/signal与现存文件hash。No-go sections只允许五section全序的空集/严格前缀，
  已取得项hash必须有效；pass/error=null、no_go/non-empty error双向唯一；`verify(no_go)`保持no_go并非零，
  缺失/损坏/跳项/混合状态绝不升级pass。Temp在target parent同文件系统，file fsync→replace→可用时dir fsync。

### T15 T61A proof commit 与终端门禁（pending）

- **依赖**：T11～T14。
- **验收**：formal+recorder+receipt+truth/continuity提交；`src/**`零差异、目标测试blob不变、manifest test
  仅机械数字替换；recorder≤200，recorder+manifest diff新增行+后续candidate tests/helper总proof≤290，
  且`candidate_product_shadow + actual_current_proof + reserved_future_proof≤729`；future reserve按spec §4
  逐文件/symbol固定90行；超出时等量降低product shadow，否则NO-GO；个别上限不得相加使用；Ruff、
  165、recorder verify、constraints/validate/truth/manifest/scope/parity/Cursor/clean全绿。
- **identity**：按spec §4分列legacy/proof commit+tree、WI196+WI213 formal-six、WI215 formal-three、
  harness、receipt file与五个section hash。

### T16 LEAN/SAFETY 同身份 readiness（pending）

- **依赖**：T15 committed+clean。
- **LEAN**：范围/YAGNI/直达性/预算/删除闭环与NO-GO。
- **SAFETY**：surface/DTO/CLI/raw/授权/异常/中断/重试/side-effect/性能/回退。
- **验收**：Pascal和Confucius对完全相同tuple均`GO`、actionable findings=0。
- **停止**：任一NO-GO或identity漂移；不得进入T21。

## Batch 2：Candidate shadow（双 GO 后）

### T21 写 cross-spec candidate RED（pending）

- **依赖**：T16双GO。
- **Test**：既有service/CLI测试文件中的最小candidate seam。
- **Runner**：在既有integration文件创建spec §4固定outer/supplemental node，可在既有conftest创建唯一
  test-only route/root fixture；worker从T61A receipt展开截至当前stage的累计exact node IDs，重写为candidate
  test paths并追加supplemental nodes，使用plan §8三条isolated命令、同一behavior root、原生JUnit/raw目录。
- **禁止**：supplemental调用test function或嵌套pytest；worker只跑一层pytest。JUnit必须逐项匹配expected
  existing/supplemental node IDs且全部passed；九组union精确106+59，seed helper逐file/symbol/source SHA匹配。
- **验收**：legacy PASS；candidate只因engine未实现FAIL；没有fixture/import假红。
- **三方门**：当前stage GREEN前后必须在隔离原始legacy commit、current legacy route、candidate route运行
  spec §4.2动态矩阵；先验真cwd/HEAD/tree/interpreter/module files/source SHA/route，任何未批准差异即停止。

### T22 创建唯一 private engine（pending）

- **Create**：`src/ai_sdlc/core/_program_bounded_stage.py`。
- **Modify**：`src/ai_sdlc/core/program_service.py`，只加显式binding/selector/glue。
- **验收**：private≤360、glue≤90、route/facade≤72、函数≤50；无反射/DSL/registry/循环import。

### T23～T30 逐 stage RED/GREEN（pending）

- **顺序**：guarded registry、broader governance、final governance、writeback persistence、persisted write
  proof、final proof publication、closure、archive。
- **每项验收**：当前stage direct+CLI+differential通过；此前stage不回归；未迁移stage仍legacy；outer在三腿
  各执行一次pytest worker，直接选择累计冻结existing nodes与supplemental nodes，spec §4.2完整矩阵零差异，
  JUnit exact-node对账与raw tree hash入log；预算ledger更新。

### T31 九阶段 selector round-trip（pending）

- **验收**：legacy→candidate→legacy→candidate四次实际运行；默认仍legacy直到T61B完成。

## Batch 3：T61B 与 candidate mainline

### T32 T61B zero-delta（pending）

- **验收**：以唯一test-only runner执行原始legacy/current legacy/candidate三方spec §4.2完整矩阵，
  原生JUnit/raw tree hash入log且零未批准差异；
  candidate p95≤baseline 110%或复测后判NO-GO。

### T33 Candidate terminal gates（pending）

- **验收**：actual peak product≤522、actual proof≤290、actual product+proof≤729；exact tests/full/Ruff/constraints/validate/truth/manifest全绿；
  两本地reviewer同身份PASS0。

### T34 Candidate PR/merge/fresh-main（pending）

- **验收**：默认candidate、legacy完整；Codex current-head无finding、required checks全绿；squash merge；
  detached fresh-main全绿。T66仍active。

## Batch 4：主线预发布稳定周期

### T41 Cross-platform/package/offline（pending）

- **验收**：required CI；wheel/sdist包含private module；两个`--no-index --find-links` clean install；
  build/runtime无联网、无checkout回读。

### T42 Sibling 与 selector 稳定（pending）

- **验收**：至少两个有理由的sibling使用安装产物smoke；rollback/reapply与T61B一致。
- **停止**：任一失败，不创建deletion分支。

## Batch 5：独立 deletion 与 rollback

### T51 删除 legacy（pending）

- **依赖**：T41/T42。
- **分支**：从candidate merge精确commit新建独立deletion branch/worktree。
- **验收**：删45 body、18 private、legacy selector/glue；保留27facade/DTO；terminal≤720、net≥2,918、
  responsibility reduction≥3,278、branch≤90；冻结pre-deletion candidate-merge worktree/current legacy腿。

### T52 Deletion gates/PR/merge（pending）

- **验收**：先在冻结T61A proof worktree运行recorder verify并登记HEAD/tree，禁止在deletion checkout重算
  已删除的45-symbol基线；随后以T61A原始legacy、冻结pre-deletion candidate-merge current legacy、deletion-head candidate三腿
  重跑spec §4.2完整矩阵；165/full/Ruff/governance/platform/package/offline/sibling、本地双PASS、Codex/checks全绿；
  merge后T66仍active。

### T53 Exact-merge actual rollback（pending）

- **验收**：一次性worktree实际revert deletion merge；legacy route/surface/selector可用；回到deletion
  fresh-main后再以T61A原始legacy、冻结pre-deletion current legacy、fresh-main candidate三腿重验§4.2
  完整矩阵；保留rollback receipt。

### T54 Lifecycle closure（pending）

- **依赖**：T53与deletion fresh-main。
- **验收**：关闭WI215/T66、更新GAP-03 ledger；GAP-04～06/WI196/RC-08/release继续open。

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| FR-001～FR-004、SC-001 | T01～T16 |
| FR-005～FR-008、SC-002 | T21～T34 |
| FR-009、SC-003 | T41～T42 |
| FR-010～FR-015、SC-004～SC-005 | T51～T54 |
