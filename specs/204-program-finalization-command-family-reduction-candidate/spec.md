# 功能规格：Program Finalization Command Family Reduction Candidate

**功能编号**：`204-program-finalization-command-family-reduction-candidate`
**创建日期**：2026-07-15
**状态**：对抗复审修订中；candidate/T61A 产品与保护代码仍未授权
**类型**：WP-07 / GAP-04 / GAP-12 / L3 candidate implementation
**父合同**：`specs/203-finalization-command-family-reduction-contract/`
**治理来源**：`specs/196-ai-sdlc-lean-code-self-reduction-governance/`

## 1. 决策与授权边界

本工作项承接 WI-203 已冻结的唯一成熟实际减重候选：收敛 9 个 `program`
finalization handler 的重复 orchestration body。目标族当前 2,020 行，其中 1,804 行可在后续
legacy deletion PR 删除；最终产品新增不超过 303 行、目标族不超过 519 行、产品净删除不少于
1,501 行。

当前 docs branch 冻结 candidate 准入合同，并修复本次 formal PR 自身暴露的 GAP-12 branch
disposition 假绿；除该有界治理缺口外，不得写 candidate 产品代码或 T61A 保护代码。Formal
同 hash 双 PASS 并合入 main 后，独立
implementation branch 先执行 T61A；只有实测保护代码不超过 180 行、运行时基线完整且两个
独立 reviewer 再次给出实现 `GO`，才允许写 candidate 产品代码。Candidate PR 保留完整 legacy
route/body，不执行 stable release 或 legacy deletion；二者仍按 WI-203 作为后续独立交付节点。

Formal PR 只允许 canonical WI-204 docs、manifest/truth/checkpoint/handoff state、下述 GAP-12
精确白名单，以及
`tests/integration/test_repo_program_manifest.py` 中两个既有仓库真值 tuple 的机械同步：source
inventory 从 `1071/1071/0/0` 改为 `1076/1076/0/0`，close layer 从 `203/203` 改为
`204/204`。仓库真值测试仍不得新增逻辑、放宽其他断言或修改其他 tuple；GAP-12 必须先红后绿，
不得借机改变 branch inventory、执行授权或 candidate 路由。两类变更均不属于 candidate 保护 claim。

本规格只写 WI-203 的绑定与执行增量，不复制其 CC-01～CC-08、RC-01～RC-10、T61A/B、
release 和 rollback 正文。发生歧义时采用 WI-203 更严格的约束。

## 2. 不可变基线与范围

- Candidate baseline：`origin/main@6d2dc47fa57b589ecafaff9872a395684e535018`。
- WI-203 receipt：merge `75d3dda5ec8b45d0f9441058da889163d814b717`，formal hash
  `cfcd63d7662175e8e9d413b831e582ee81d00958cb8d9c3c8c717de0987dc57f`。
- `program_cmd.py` blob 在 WI-203 baseline `d19c8b7df66ca43e4fa55a99a6d05fa2d1219586` 与当前 baseline 均为
  `e8aff1d079fb471b0f815dec343348cb0e4afd6e`；文件 SHA-256 均为
  `6a101662f01e11f3e6f9963860b0589a1dabd2ec604d82ad1cfc2d6636729bed`。
- 两个主要既有测试文件的 Git blob 也无漂移：
  CLI=`27bc60ac78453dc8e9708c508ccbcd829c6392be`，
  service=`78347b2bd39df8a80dd69eb330c6cb8ccefcc29b`。

目标只包括下列 9 个 public handler 的 orchestration body；decorator、签名、docstring、command
name、option 与 public Python symbol 全部保留：

1. `program_cross_spec_writeback`
2. `program_guarded_registry`
3. `program_broader_governance`
4. `program_final_governance`
5. `program_writeback_persistence`
6. `program_persisted_write_proof`
7. `program_final_proof_publication`
8. `program_final_proof_closure`
9. `program_final_proof_archive`

明确排除 `ProgramService`、DTO、9 个 renderer、artifact/schema、其他 24 个 `program` command、
`program truth`、thread-archive、project-cleanup、runtime rules、release 配置和 Lean Gate。任一保护区
blob 漂移、范围变化或需要修改排除项，当前 receipt 与 verdict 失效，必须停止并重新 formal。

## 3. GAP-12：PR 中间态不得伪装为已结算

当前 lifecycle parser 把除空值和 `待最终收口` 外的任意文本当作 resolved，导致未合并分支写入
`PR merge carrier` 即可让 `verify constraints` 假绿。修复合同如下：

- branch disposition 必须显式落在 `merge-pending / merged / archived(<非空原因>) / deleted /
  待最终收口`；其他自由文本一律 fail closed，不能作为兼容成功路径。
- `merge-pending` 只证明本地 pre-merge branch 阶段，不声称 GitHub PR 已打开；GitHub PR/head/base
  真值仍由 Codex review 与 required checks 的当前 HEAD 独立证明，避免给本地 constraints 增加网络依赖。
  本地仅在恰好一个关联 branch、该 entry 为当前 checkout、worktree 存在、ahead>0 且 behind=0
  时允许 `branch-check` 与 `verify constraints` 继续；`close-check` 必须阻断。
- `merge-pending` 与 Git inventory 不一致时 fail closed：无关联 branch、ahead=0、behind>0 或
  ahead>0 且 behind>0 的 diverged branch、多个关联 branch、非当前 checkout 或无 worktree 均不得
  作为可继续的 PR 中间态。
- `merged` 要求恰好一个关联 branch 仍存在且 ahead=0；已删除 branch 必须改记 `deleted`，不能仅靠
  日志声称 merged。`deleted` 要求关联 branch 不存在；`archived(<非空原因>)` 要求恰好一个关联
  branch 仍存在、kind=`archive`、ahead>0。多个关联 branch 对任何 final token 均 fail closed；
  不得从日志文本推断 Git 合并事实。
- worktree disposition 只接受缺省/`待最终收口`、`removed`、`retained(<非空原因>)`；显式 unknown
  fail closed。`removed` 要求没有关联 worktree；`retained(<原因>)` 要求恰好一个关联 worktree 存在。
  `merge-pending` 的当前载体必须用 `retained(<原因>)` 或保持未决，不能写 `removed`。
- Final/close 不允许 worktree disposition 缺省或 `待最终收口`：有且仅有一个关联 worktree 时必须
  `retained(<非空原因>)`；没有关联 worktree 时必须 `removed`；多个关联 worktree一律阻断。
- lifecycle analyzer 的所有 blocker 必须保留稳定 namespace `BLOCKER: branch lifecycle `。
  branch-check、constraints、readiness 与 direct close 读取 raw blocker，仍严格阻断；Program Truth
  对历史 `close_check_refs` 继续按既有 normalizer 只过滤 `branch_lifecycle` check 与同 namespace 的
  瞬态 blocker，其他 close blocker 必须保留。不得修改 `program_service.py`、兼容旧 token 或按 WI
  年龄/编号增加 bypass。
- authoring template/rule 必须列出 canonical branch/worktree token，不再引导自由文本。
- GAP-12 的 caller policy 参数必须命名为 `_require_final_branch_disposition`，并只允许内部 helper
  的最小改动，不新增公共 API、状态文件或抽象层；必须以
  unknown fail-closed、pending verify PASS、pending close BLOCK、pending/Git 反例、final branch
  missing/multiple、final worktree unresolved/mismatch、historical raw-block/normalized-pass 与
  non-lifecycle blocker 保留七组测试证明。

GAP-12 路径白名单固定为：

- `src/ai_sdlc/core/workitem_traceability.py`
- `src/ai_sdlc/core/close_check.py`
- `src/ai_sdlc/core/verify_constraints.py`
- `src/ai_sdlc/telemetry/readiness.py`
- `src/ai_sdlc/core/workitem_scaffold.py`
- `src/ai_sdlc/rules/git-branch.md`
- `src/ai_sdlc/templates/execution-log.md.j2`
- `templates/execution-log-template.md`
- `tests/unit/test_workitem_traceability.py`
- `tests/unit/test_program_service.py`
- `tests/unit/test_close_check.py`
- `tests/unit/test_verify_constraints.py`
- `tests/unit/test_telemetry_readiness.py`
- `tests/integration/test_cli_workitem_close_check.py`
- `tests/integration/test_cli_verify_constraints.py`
- `tests/integration/test_cli_workitem_init.py`

`tests/unit/test_program_service.py` 只允许在既有 ephemeral close-check drift 测试中新增≤8 个非空行，
不得修改 ProgramService 产品代码、snapshot 算法或其他测试逻辑。

预算按新增非空手写行数计，不以删除抵扣：runtime/scaffold/rule/template 合计≤80，tests 合计≤180，
总计≤260。任一路径超白名单、任一分项/总预算超限或需要新模块/公共类型，设计 PASS 立即失效，
必须先修改 formal 并重新双审，不能边写边扩范围。

该缺口由 Round 6 对抗复审发现。新 formal target 先获两个 reviewer 的设计 PASS，随后才允许
GAP-12 TDD；代码树变化后两位 reviewer 必须再次对同一 HEAD PASS，才可合并 formal PR。

## 4. Sponsor 与账本

| 字段 | 冻结值 |
|---|---|
| claim key | `wi204:t61ab:program-finalization-family:v1` |
| planned protection claim | 175 行 |
| hard protection cap | 180 行 |
| formal merge 前 effective claim | 0 |
| owner | Codex / `feature/204-program-finalization-command-family-reduction-candidate-dev` |
| handoff URI | `.ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate/codex-handoff.md` |
| activation receipt URI | `.ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate/sponsor-activation.yaml` |
| parent active deadline | `2026-08-14T05:58:55Z` |

175 行来自当前无漂移基线的最低可信设计：surface/route manifest 20～25 行、差分捕获 helper
75～85 行、failure/order/renderer 参数断言 35～45 行、AST ledger 与 allowlist normalizer 15～20
行，并复用既有 59 个 CLI 与 106 个 service 测试。180 是硬上限，不是自动消费值；effective
 claim 按实际新增 test/harness/normalizer 手写行数逐 commit 登记。超出 175 先精简，超过 180
直接 RC-09 No-Go，不能删场景、挪文件逃账或借用旧 WI-202/reserve。

Formal merge 后必须先建立不含产品/测试代码的 activation-only branch，以只读方式重验 baseline，
再把 activation receipt 与 scoped handoff 通过独立 PR 合入 main；receipt 固定 parent receipt/hash、
具体 owner/implementation branch、handoff URI、baseline、`activation_at`、
`t61a_due_at=min(activation_at+30d,parent_active_deadline)`、state=`active`、effective claim=0。
`activation_at` 使用 receipt 文件生成时的 UTC，且只有包含该 exact receipt content 的 commit 成为
`origin/main` ancestor 后 state 才生效；较早起算是保守门槛，不依赖未知 merge 时间。Implementation
branch 必须从该 activation merge 之后的 main 创建。T61A 首个保护写入只能发生在 mainline active
receipt 可见之后；首份同 baseline evidence
使 state 进入 `verified`，effective claim 从 0 按实际新增行数更新。Verified 14 日无 evidence 或
连续 3 个 checkpoint blocked 即 stale；stale 后 7 日内必须恢复同 baseline evidence 或开始
缩减/revert。错过 T61A due、baseline/scope 漂移或 candidate No-Go 立即 revoked，保护代码在下一
mainline PR 或 7 日内（取先到者）缩减/revert。

旧 WI-202 的 170 行 allocation 已 revoked、effective=0、不可复活或转移；candidate 未用额度
也不能自动成为 T62A sponsor。只有 deletion release 与真实 rollback 完成后，才可新建具有
新 ID/hash/unique key 的 replacement sponsor formal；旧 settled receipt 不得新增 claim。

Replacement formal 必须把计算绑定到一个 mainline ledger snapshot commit，并逐项列出：

- `D_actual`：Vn+1 相对 WI-203 baseline 的实际产品净删除，来自 RC-10 deletion ledger；
- `C_actual`：本 claim key 实际新增的 test/harness/normalizer LOC；
- `roadmap_used_elsewhere`：已由其他不重叠 deletion origin 承担的所有有效 actual protection LOC；
- `other_same_origin_claims`：除本 claim key 外，已记到本 deletion origin 且尚未 revoked/reverted 的
  每个 unique key 与 actual LOC；
- `new_risk_buffer`：replacement formal 显式冻结的非负整数，不能从旧 reserve 继承。

按固定顺序计算：
`roadmap_capacity=max(0,1500-roadmap_used_elsewhere)`；
`origin_pool=min(floor(D_actual×25%),roadmap_capacity)`；
`origin_used=C_actual+sum(other_same_origin_claims)`；
`R=max(0,origin_pool-origin_used-new_risk_buffer)`。
这样 roadmap cap 与同源 claim 各扣一次，不重复扣减。WI-202 170、candidate 未用 180 与 reserve 3
均不进入任何变量。只有 R 不小于重新冻结的 T62A 完整预算、replacement formal 合入 main 且
WI-196 新 hash 双 PASS，新的 T62A 才可启动；WI-203 完成本身不代表 T62A 足额。

## 5. 功能需求

- **FR-00 生命周期真值**：GAP-12 显式区分 `merge-pending` 与最终 disposition；unknown fail
  closed，verify 可在真实 PR 中间态继续，close 不得提前通过。
- **FR-01 基线准入**：T61A 前必须重算 2,020/216/1,804/432 与 protected blob；任何漂移停止。
- **FR-02 保护先行**：先复用 165 个既有测试，再以参数化 harness 补齐 surface、raw bytes、
  exit、renderer call/order、失败/中断/重试、side-effect tree、路径/编码、outer hook 与 runtime。
- **FR-03 单一实现**：最多新增一个私有 runner module；显式注入 builder/executor/writer/
  renderer/report callable 与字段 adapter，不按 command name 分支，不用 reflection 或 DSL。
- **FR-04 分阶段迁移**：按 S0→S1→S2 迁移，internal selector 默认保持 legacy；每次只迁一个
  stage，定向测试绿后再继续，完整 legacy body 在 candidate PR 中保留。
- **FR-05 产品预算**：runner≤230，9 adapters+selector≤70，import/glue≤3，聚合≤303；内部
  软目标≤285；所有新函数≤50 行，公共抽象数为 0。
- **FR-06 行为等价**：两份隔离 clone 的 T61B 对 public surface、exit/stdout/stderr、调用顺序、
  raw artifact/report、tree/mode、副作用和完整 9-stage chain 必须零未批准差异。
- **FR-07 性能与回退**：candidate p95 退化≤10%；candidate PR 前完成 selector-only route
  rollback，恢复 9 个 legacy transcript/artifact/side-effect tree。
- **FR-08 审查**：Formal、T61A readiness、candidate tree 均由精简效率与兼容安全两个独立
  read-only reviewer 评审；任一目标变化使旧 verdict 失效。
- **FR-09 停止投资**：保护>180、产品>303、最终预测>519、净删预测<1,501、需要 optional
  writer/公共抽象/保护区修改、差分或平台失败时立即 No-Go，保留 legacy。
- **FR-10 后续边界**：本 WI candidate merge 不能标记 `completed_reduction` 或 sponsor
  `settled`；stable Vn、installed/platform/sibling smoke、独立 deletion Vn+1 与真实 rollback
  receipt 完成后才可结算。

## 6. 成功标准

- **SC-00**：GAP-12 的 unknown/`merge-pending`/final 状态矩阵通过，verify 无假绿且 close 不提前。
- **SC-01**：Formal review target 同一 hash 获两个独立 reviewer `PASS`，findings=none。
- **SC-02**：T61A 新保护代码实际≤180，165 个既有测试无删减，runtime p50/p95 已落盘。
- **SC-03**：Candidate 新产品 LOC≤303（目标≤285），逐 commit shadow peak≤303。
- **SC-04**：post-deletion projection 保持 body delete≥1,804、family≤519、产品净删≥1,501、
  mirror drop≥82.7%；candidate tree 仍保留完整 legacy。
- **SC-05**：T61B 零未批准差异，targeted/full/Ruff/constraints/truth/platform 全绿。
- **SC-06**：删除前 route rollback 通过；candidate PR 合入后状态只到
  `candidate_merged_awaiting_stable_release`。

## 7. Formal review target

Review target 固定为本目录的 `spec.md + plan.md + tasks.md`。算法为：分别计算文件 SHA-256，
生成 `<hash><two spaces><relative path>`，按字节序排序，以 LF 连接且末尾无换行，再对 UTF-8
payload 求 SHA-256。`task-execution-log.md` 与 `development-summary.md` 记录 receipt，不进入 target。
