---
related_plan: "specs/203-finalization-command-family-reduction-contract/plan.md"
related_doc:
  - "specs/203-finalization-command-family-reduction-contract/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Program Finalization Command Family Reduction Candidate

**编号**：`204-program-finalization-command-family-reduction-candidate`
**日期**：2026-07-15
**来源**：本 WI `spec.md + plan.md`，规范性父合同为 WI-203

## 1. 执行规则

- Formal、implementation、candidate PR 使用独立分支节点；formal 合入前只允许 GAP-12，RC-09
  disposition review 只允许 GAP-13 的精确白名单代码/测试；均不写 candidate 产品代码或 T61A 保护代码。
- 每个代码批次先红后绿并在同一 commit 更新 RC-05/RC-06 ledger 与 execution log。
- 两个 reviewer 可并行，但必须独立、只读、对同一 hash/tree 给 verdict。
- 任一受审目标变化使旧 verdict 失效；任一硬门失败按 RC-09 停止，不以 waiver 继续。

## Batch 0：Formal admission（历史阶段，已完成）

### T01 冻结 current baseline 与 claim

- **状态**：已完成；formal baseline 与 claim 已冻结
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、manifest/state
- **验收**：
  1. baseline=`6d2dc47fa57b589ecafaff9872a395684e535018`，WI-203 receipt/hash 可复算；
  2. target/test blobs 与 WI-203 baseline 无漂移；
  3. claim key 唯一，planned=175、hard=180、effective=0、deadline 明确；
  4. 旧 WI-202 allocation 与 reserve 明确不可使用。

### T02 Formal 双 Agent 对抗评审

- **状态**：已完成；Round 11 修订 target 双 PASS
- **依赖**：T01
- **维度 A**：精简收益、预算数学、直接性、无过度抽象。
- **维度 B**：功能等价、副作用、回退、sponsor 生命周期与零重复计算。
- **验收**：同一 formal hash 两方 `PASS`、findings=none；修改后重新评审。

### T03 GAP-12 branch disposition 真值修复

- **状态**：已完成；产品修复与 CI checkout topology 已验证并合入
- **依赖**：T02
- **文件**：仅允许 spec GAP-12/CI proof 所列 18 个精确路径；不得新建模块或公共类型。
- **预算**：Round 10 已用 production/tests/total=`79/171/250`；Round 11 仅允许 workflow≤7、
  workflow test≤3，最终 production=`79/80`、tests≤`174/180`、workflow≤7、total≤260；删除不抵扣；
  `test_program_service.py` 仍仅可给既有 ephemeral drift 测试新增≤8 个非空行；超任一门槛先修改
  formal 并重新双审。
- **验收**：
  1. RED 证明自由文本可假绿、pending 与 final 无法区分；
  2. branch allowlist 只接受 `merge-pending/merged/archived(<非空原因>)/deleted/待最终收口`，
     unknown fail closed；caller policy 参数固定为 private `_require_final_branch_disposition`；
  3. `merge-pending` 仅在唯一 associated branch 为当前 checkout、有 worktree、ahead>0 且 behind=0
     时通过 branch-check/constraints，但不声称 GitHub PR 或 merged，close-check 必须阻断；
  4. branch missing/multiple、ahead=0、behind>0/diverged、非当前或无 worktree全部 fail closed；
  5. `merged` 唯一 branch 存在且 ahead=0、`deleted` 无 branch、archive 唯一且 kind=archive；
     final/close 下唯一 worktree 必须 `retained(<原因>)`、无 worktree 必须 `removed`，缺省/未决/多个
     均阻断；unknown branch/worktree token fail closed；
  6. lifecycle blocker 保留稳定 namespace；historical Program Truth normalization 过滤该瞬态分类，
     但 direct close 仍 BLOCK，且任一 non-lifecycle close blocker 仍保留；
  7. PR CI 保留默认 merge checkout 跑 Ruff/Pytest；checkout 为完整历史且不持久化凭据；仅在
     constraints 前用 `HEAD^1`/`HEAD^2` 固定本地 main/current head，顺序断言完整；保持唯一
     `pull_request` + `contents: read`、不用 PAT/secrets，head ref=main 必须 collision fail closed；
  8. 两个 reviewer 对同一代码 HEAD `PASS`、findings=none。

### T04 Formal 验证与 mainline receipt

- **状态**：已完成；PR #128 已合入 main
- **依赖**：T03
- **验收**：constraints/truth/path whitelist/diff check 通过；授权 GAP-12 窄修、
  docs/state/manifest 与
  `test_repo_program_manifest.py` 两个既有 tuple 的 `1071/203→1076/204` 精确同步进入 PR，
  不修改其他仓库真值测试逻辑；Codex review 与 required checks clean；PR 合入 main 并记录 merge commit。
- **回退**：revert formal PR，claim 不激活。

## Batch 1：T61A 与 readiness（implementation branch）

### T11 Activation-only mainline receipt

- **状态**：已完成；PR #129 已合入 main，implementation branch 从 activation merge 创建
- **依赖**：T04
- **验收**：
  1. 从 formal merge 后 main 建立 activation-only branch/worktree，不含产品/测试代码；
  2. 9 target、9 renderer、ProgramService/test blobs、2,020/216/1,804/432、33 command surface
     与 runtime 环境只读重验通过；
  3. 生成 scoped handoff 与 `sponsor-activation.yaml`：parent receipt/hash、具体 owner/implementation branch、
     handoff、baseline、activation_at、T61A due、state=active、effective=0 完整；
  4. activation-only PR 通过 constraints/truth/Codex/required checks 并合入 main；receipt content
     所在 commit 成为 `origin/main` ancestor 后才 active；
  5. `t61a_due_at` 不晚于 parent deadline；错过即 revoked，禁止进入 T12；
  6. implementation branch/worktree 必须从 activation merge 后 main 新建。

### T12 实现最小参数化保护 harness

- **状态**：RC-09 No-Go；首版 175 LOC harness 被 readiness 拒绝，分支终态零保留
- **依赖**：T11
- **验收**：覆盖 raw transcript/tree/bytes、failure/order/renderer、interrupt/retry、path/encoding、
  outer hook、AST ledger；不复制九套 snapshot；首份 evidence 将 active 转 verified；actual
  protection≤180，effective claim 与逐 commit ledger 一致；mainline receipt 不可见时测试必须
  fail closed，禁止首个保护写入。
- **验证**：逐 commit RC-06 ledger + targeted/full tests。

### T13 捕获 runtime 与 T61A receipt

- **状态**：未通过；首版 runtime/evidence 已执行，但被 readiness 拒绝并移除
- **依赖**：T12
- **验收**：warmup、采样命令、p50/p95、normalizer allowlist、side-effect inventory、9-stage chain
  完整；verified `last_evidence_at`、14 日 freshness、3 blocked stale、stale 后 7 日缩减/revert、
  revoked 后下一个 PR 或 7 日缩减/revert规则已落盘。

### T14 Readiness 双 Agent `GO/No-Go`

- **状态**：已完成；Pascal 与 Confucius 独立一致判定 RC-09 No-Go
- **依赖**：T13
- **验收**：两方独立审查相同 T61A evidence；仅共同 `GO` 允许 T21。

### T15 GAP-13 pre-close / zero-task 真值修复

- **状态**：第二轮 Codex findings 已修复且本地全量验证完成；等待 fresh-clone proof、最终双 Agent 与 Codex review
- **依赖**：T14 No-Go、PR #130 Codex findings
- **文件/预算**：仅 spec 3.1 节 8 项白名单；runtime≤90、tests≤325（实测 89/322）；零 candidate LOC/claim。
- **验收**：
  1. `stage: close-pending` 下 detect/reconcile/status/recover/`recover --reconcile` 均停在 execute，
     已污染 close checkpoint/runtime/packs 可原地回退且第二次 recover 不写入；
  2. 无 marker 与未知 marker 继续保持历史 close 推断；
  3. parser 零任务时 real/dry/check_gate 均 RETRY，`_build_executor` 不调用，runtime/plan/working-set 不写；
  4. summary gate 仍通过，但 `merge-pending` final close 继续阻断；
  5. force-track scoped ResumePack；fresh clone 连续 load 后与 root byte-identical 且 Git clean；
  6. 两个 reviewer 对同一 tree `PASS`，findings=none。

## Batch 2：TDD 与 candidate migration

### T21 建立 candidate seam 红灯

- **状态**：已取消；T14 No-Go，禁止进入 candidate seam
- **依赖**：T14
- **验收**：legacy 全绿、candidate seam 失败；不修改 public surface 或保护区。

### T22 单 stage private runner

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T21
- **验收**：仅迁 `cross-spec-writeback`；runner≤230、helper≤50、公共抽象=0、产品软目标≤285
  可达；selector 默认 legacy。

### T23 逐 stage 迁移剩余 8 个 handler

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T22
- **验收**：每个切片 targeted/differential/ledger 绿；9 adapters+selector≤70、glue≤3、聚合
  product≤303；renderer/ProgramService/DTO hash 不变。

### T24 切换 candidate route

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T23
- **验收**：
  1. 无 public flag；candidate+route 产品新增与 shadow peak≤303；完整 legacy route/body 仍存在；
  2. post-deletion projection：family≤519、net delete≥1,501、mirror drop≥82.7%、migrated
     responsibility≤83、full-responsibility handler=0；
  3. stable Vn 与 installed/platform/offline/sibling gate 前禁止任何实际 legacy deletion；删除只可
     在后续独立 Vn+1 PR 执行。

## Batch 3：T61B、rollback 与 candidate PR

### T31 完整 T61B differential

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T24
- **验收**：隔离 clone 零未批准差异；p95≤10%；targeted/full/Ruff/constraints/truth/platform
  全绿。

### T32 删除前 route rollback rehearsal

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T31
- **验收**：selector-only 切回 legacy 后 9 transcript/artifact/tree 恢复，再恢复 candidate。

### T33 Candidate tree 双 Agent 与 Codex review

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T32
- **验收**：两个维度同 tree PASS；actionable findings 全处置并重审。

### T34 Candidate PR mainline merge

- **状态**：已取消；RC-09 停止 candidate
- **依赖**：T33
- **验收**：required checks clean、heartbeat 到 merge；保留 legacy body；状态仅写为
  `candidate_merged_awaiting_stable_release`，不得写 `completed_reduction/settled`。

## 2. 后续强制 handoff

T34 后创建 stable Vn 与独立 deletion Vn+1 节点，执行 installed/platform/offline/sibling smoke、
真实 rollback 与 actual `D/C` settlement。未完成这些步骤，GAP-04 与路线图减重成果保持 open。
