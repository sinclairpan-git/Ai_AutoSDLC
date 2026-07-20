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
- **边界**：receipt尚不存在；本characterization不替代T14单一direct+CLI composite的20个原始样本，
  也不作为T61B基线。

### T13 TDD 实现唯一 recorder（in_progress）

- **Create**：`scripts/program_bounded_stage_t61a.py`。
- **RED**：命令只因文件不存在失败。
- **GREEN**：实现explicit stage inventory；public逐项覆盖signature/parameter/return/raw annotations/doc/
  module/qualname/behavior；DTO逐项覆盖fields顺序/default/factory/equality与post-init presence/module/
  qualname/signature/source/behavior；另覆盖private loaders、upstream与steps的missing/empty/valid/invalid、
  confirmation/outside-root、九CLI help/mode/failure/full-chain、direct/CLI双根、
  late-bound、fault/SystemExit/process termination/interrupt/retry、窗口化sentinel、raw tree/bytes和record/verify；
  目标≤230、hard cap250、函数≤50；总proof目标≤263、hard cap290。
- **失败路径**：schema固定outcome/failure phase/completed checks/error/verdict/closure及stable/performance/raw
  三个status/payload/hash section；pass全complete，no_go按失败点使用not_started/partial/complete且raw至少
  partial。内置spec §4 versioned 15-check全序/section transition。Expected termination必须由parent nonce
  绑定声明，marker紧邻harness termination，post-marker transcript/exit、partial tree与fresh-child retry全部
  匹配时允许完成`fault_recovery`；undeclared/mismatch/timeout/retry failure由仍存活supervisor先原子持久化
  `closed_no_go`再非零退出，supervisor自身不可清理死亡由外部调用者判unclosed NO-GO。
- **复用**：165 tests只按exact node ID/source hash/assertion coverage逐项复用；fixture只seed，不调用
  `test_*`；每个node必须绑定实际seed/helper/fixture/autouse的transitive source SHA set，无法精确绑定就
  不得复用。不得以selector总通过替代新增矩阵。
- **禁止**：第二harness/DSL/依赖/产品模块；未知normalizer/callable fallback。

### T14 生成机器 receipt（pending）

- **Create**：`.ai-sdlc/work-items/215-programservice-bounded-stage-reduction-implementation/t61a-legacy-baseline-receipt.json`。
- **验收**：`record`一次写完整receipt与一个direct+CLI composite的20个真实样本/component duration；
  `verify`只读并重放稳定行为，stable behavior hash一致；性能区独立hash但不要求duration跨运行一致；
  ≤2MiB、全部矩阵PASS；receipt不自绑定commit/tree/hash。Sentinel只包围seed后的被测调用，pytest/git/
  toolchain采集在窗口外。
- **NO-GO验收**：一次正常`record`生成唯一canonical pass candidate；canonicalization/matrix失败和
  unexpected termination分别用独立负向`record`写caller-specified临时durable no_go receipt。每次invocation
  仅一个authoritative output和root-A/root-B两根；三个receipt均可由`verify`按outcome校验，no_go非零且
  不得升级为pass；no_go `verify`创建零行为根且normalizer table为空。三个内容hash严格使用spec §4 canonical
  JSON bytes；产品mapping唯一编码为tagged object并在其
  entries数组保留顺序；
  非UTF-8 bytes/Path/tuple/exception args做type-tag往返与hash复算；非法check前缀/section状态必须被拒绝。
- **进程验收**：pass=`authoritative receipt verify + exit 0`；任一非零/signal退出不得接受现存pass receipt。
  有有效`closed_no_go`则closed；否则外部envelope记录exit/signal、现存文件hash和`unclosed_no_go`。
- **边界验收**：pass/no_go与verdict/closure/failure/error必须双向唯一；performance第20样本写入后、summary/
  hash/check-ID前注入失败仍生成partial durable receipt。计时仅用同一父进程`perf_counter_ns()`，三段非负且
  total≥direct+CLI；wall clock或child自报duration必须失败。

### T15 T61A proof commit 与终端门禁（pending）

- **依赖**：T11～T14。
- **验收**：formal+recorder+receipt+truth/continuity提交；`src/**`零差异、目标测试blob不变、manifest test
  仅机械数字替换；recorder≤250，recorder+manifest diff新增行+后续candidate tests/helper总proof≤290，
  且`candidate_product_shadow + actual_current_proof + reserved_future_proof≤729`；future reserve按后续
  candidate test/helper/normalizer逐文件/任务冻结且不得记0规避；个别上限不得相加使用；Ruff、
  165、recorder verify、constraints/validate/truth/manifest/scope/parity/Cursor/clean全绿。
- **identity**：按spec §4分列legacy/proof commit+tree、WI196+WI213 formal-six、WI215 formal-three、
  harness、receipt file、stable behavior和observed-performance hash。

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
- **验收**：legacy PASS；candidate只因engine未实现FAIL；没有fixture/import假红。

### T22 创建唯一 private engine（pending）

- **Create**：`src/ai_sdlc/core/_program_bounded_stage.py`。
- **Modify**：`src/ai_sdlc/core/program_service.py`，只加显式binding/selector/glue。
- **验收**：private≤360、glue≤90、route/facade≤72、函数≤50；无反射/DSL/registry/循环import。

### T23～T30 逐 stage RED/GREEN（pending）

- **顺序**：guarded registry、broader governance、final governance、writeback persistence、persisted write
  proof、final proof publication、closure、archive。
- **每项验收**：当前stage direct+CLI+differential通过；此前stage不回归；未迁移stage仍legacy；预算ledger更新。

### T31 九阶段 selector round-trip（pending）

- **验收**：legacy→candidate→legacy→candidate四次实际运行；默认仍legacy直到T61B完成。

## Batch 3：T61B 与 candidate mainline

### T32 T61B zero-delta（pending）

- **验收**：surface/DTO/late-bound/exception/trace/raw tree/bytes/mode/side-effect零未批准差异；
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
  responsibility reduction≥3,278、branch≤90。

### T52 Deletion gates/PR/merge（pending）

- **验收**：T61/165/full/Ruff/governance/platform/package/offline/sibling、本地双PASS、Codex/checks全绿；
  merge后T66仍active。

### T53 Exact-merge actual rollback（pending）

- **验收**：一次性worktree实际revert deletion merge；legacy route/surface/selector可用；回到deletion
  fresh-main后重验关键矩阵；保留rollback receipt。

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
