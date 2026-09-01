# R0+R1 生命周期收敛根治设计

> Revision 2：已按两位独立专家的定向对抗评审整改；仍处于设计冻结阶段，未授权运行时实现。

## 1. 决策摘要

本轮只批准两项根治性整改，不开发任何新特性：

- **R0：修正工作项生命周期与合并闭环。** 复用现有 `WorkItemStatus` 与 `.ai-sdlc/work-items/<wi-id>/work-item.yaml`，让 sponsor 决策、执行授权、评审就绪和主线包含各自只有一个权威来源。
- **R1：消除证据链写放大。** 把 handoff、resume、Program Truth 快照和清理动作从“每轮必须改动的评审内容”降为可再生或只读证据，并移除仓库测试中的固定库存计数。

实施顺序不按编号，而是固定为 **先 R1、后 R0**：PR1 先拆除会让候选自失效的 evidence writer 与固定库存契约，PR2 再修正生命周期与 close transaction。最多两个修复 PR，总投入上限 5 人日。两个修复完成并通过验收前，继续冻结新特性。

这不是再增加一套治理规则或机械 envelope。设计优先复用现有状态机、工作项账本、PR 评审和 truth/close-check 入口，只删掉互相矛盾的职责与未来事实依赖。

## 2. 问题定义

近期工作项反复出现同一模式：

1. 正式文档已经合入主线，但 `formal_freeze_only` 被解释成“下一步启动 execute”，即使 sponsor 实际决策是延期或不执行。
2. close-check 在合并前要求合并 SHA、主线包含和分支/工作树删除等未来事实，导致一个提交无法证明自身满足关闭条件。
3. 合并后为了补齐这些事实再开 records/truth closeout PR；新 PR 又改变 exact head、handoff、快照和库存计数，产生下一轮自失效。
4. 本地 review loop 限制两轮，但 GitHub heartbeat 和人工流程仍可继续请求复评，且 CLI 还建议增加 `--max-rounds`，所以“额度耗尽”没有导向唯一终局决策。
5. Program Truth 集成测试固定断言全仓库源文件数量。每新增一个已登记工作项或设计文档，都需要修改测试期望并触发大范围验证。
6. tracked handoff/resume pack 同时充当操作缓存、评审输入和提交身份的一部分。每次“刷新连续性”都会改变待评审 head，形成证据自引用。

这些不是单个 finding 修得不够，而是生命周期、证据分类、关闭事务和复评预算四个控制面的职责重叠。继续逐条补例外只会放大治理代码与材料数量。

## 3. 证据基线

本设计基于 `origin/main@f0e0e4d6162557e55371afcf0ed85c785cf97329` 的隔离工作树。当前直接相关基线为：

- `uv run ai-sdlc verify constraints`：无 BLOCKER。
- 状态机、close-check、workitem truth 定向测试：`144 passed`。
- 现有状态枚举已经包含 `DOCS_BASELINE`、`DEV_EXECUTING`、`DEV_VERIFYING`、`DEV_REVIEWED`、`SUSPENDED`、`FAILED`、`COMPLETED`，不需要再造第二套生命周期。
- `workitem truth-check` 当前在 `formal_freeze_only` 时固定生成“start execute work”动作，说明 evidence classification 被错误地用作下一步授权。
- `pr-review fix` 已把有效修复轮次限制为策略值与 CLI 值的较小者，但达到上限后仍提示增加 `--max-rounds`，与两轮后进入 sponsor 终局决策的规则冲突。
- 仓库 Program Truth 测试直接断言 `total_sources/mapped_sources/missing_sources/close` 的固定数量，构成确定性的写放大源。
- 本设计文档提交后，根 manifest 集成测试已经实证得到 `1175 total / 1174 mapped / 1 unmapped` 并失败，耗时 168.70 秒。这证明 R0 若先于 R1，会在进入生命周期实现前就被旧库存契约阻断。

历史 closeout 中已观察到：reviewed PR head 与合并后主线可以拥有相同内容树，但仍因 commit SHA、handoff 文案或清理标记不同而被判定需要新 records PR。R0 必须以内容和生命周期语义闭环，而不是要求未来提交预先记录自身 SHA。

## 4. 设计目标与非目标

### 4.1 目标

- sponsor 的批准、延期和 No-Go 能稳定决定工作项下一步，evidence classifier 不得越权授权执行。
- 合并前可以完成全部可写状态收口；合并后只做只读核验，不再创建 records/truth closeout PR。
- 同一 reviewed payload 在 fast-forward、merge commit、squash 或 rebase 合并后都能被一致识别。
- 两轮修复预算耗尽后只允许一次有界 sponsor 决策，不允许扩大轮次或重新打开无限问题空间。
- handoff、truth snapshot 和清理动作不再改变 semantic review identity。
- 新增一个正常映射的工作项不再要求修改固定库存数字或因此运行全量测试。
- shared checkout、clean clone 和 remote-only 检查对同一远端事实给出一致结论。
- 以本次整改前的 16 个 Program Truth blocker ID 集合作为两个 PR 的前后对账基线，不用本次整改删除、豁免或重写历史事实；该数量不是永久产品常量。

### 4.2 非目标

- 不开发 R02、P3/P4 或其他产品特性。
- 不批量迁移全部历史工作项，不要求 225 个旧目录补建 `work-item.yaml`。
- 不增加 `mechanical-envelope.yaml`、第二份 sponsor ledger 或新的 closeout 文档类型。
- 不重写所有 Program Truth 分类器，不清理历史 execution log。
- 不把所有建议都升级成强制 gate；只固化会造成状态矛盾、无限复评或自失效的最小规则。
- 不要求 post-merge 修改主线记录，也不以自动 push、自动开 PR 作为核验手段。

## 5. 核心概念分离

R0+R1 将当前混在一起的五类事实拆开：

| 事实 | 权威来源 | 可否授权动作 |
| --- | --- | --- |
| 生命周期状态 | 统一 `LifecycleView` resolver；输入为 `work-item.yaml`、sponsor decision、review terminal decision 与只读 merge observation | 是，只有合法 transition 与 sponsor 决策事务可以改变持久状态 |
| 执行证据分类 | `workitem truth-check` 对指定 revision 的只读观察 | 否，只回答是否存在 implementation evidence |
| 评审结论 | PR provider / 本地 review run 对某个候选 head 的 verdict | 否，只决定候选内容是否可进入 merge-ready |
| 主线包含 | 指定 target ref 上的 Git 内容比较 | 否，只回答 reviewed payload 是否已进入主线 |
| 连续性/诊断缓存 | ignored local handoff/resume/truth cache | 否，可再生，不参与 semantic review identity；legacy tracked copy 冻结且仍属于评审内容 |

最终状态不是把上述字段压成一个模糊 classification，而是明确组合：

- `SUSPENDED + contained_in_main=true`：正式基线已进入主线，当前明确延期，不启动 execute。
- `FAILED + contained_in_main=true`：正式基线已进入主线，sponsor No-Go，终止本项。
- `DEV_VERIFYING + ApprovedReviewIdentity + contained_in_main=false`：账本保持不变，只读投影为 `effective_status=DEV_REVIEWED`，等待 readiness/check 收口。
- `DEV_VERIFYING + MergeReadyTuple + contained_in_main=true`：只读投影为 `effective_status=COMPLETED`。
- `formal_freeze_only`：仅说明没有实现证据，不能推导“必须开始 execute”。

所有公开消费者必须调用同一个 `resolve_lifecycle_view(...)`，不得直接用 raw `WorkItem.status`、truth classification 或 checkpoint stage 推导下一步。统一返回至少包含：

```text
persisted_status
effective_status
sponsor_decision
readiness_profile
contained_in_main
writeback_required
```

PR 流程在送审前把持久状态冻结于 `DEV_VERIFYING`；review 通过后不得再提交 `work-item.yaml` 状态变化。`effective_status=DEV_REVIEWED` 只能由 `DEV_VERIFYING + ApprovedReviewIdentity` 投影；`effective_status=COMPLETED` 必须再具备 `MergeReadyTuple + verified merge observation`。现有持久 `DEV_REVIEWED/COMPLETED` 仅作为 legacy/non-PR 兼容状态，truth、close、status、Program Truth、release 与 next-action 均不得绕过 resolver 直接读取它们。

## 6. R0：生命周期与合并闭环

### 6.1 复用现有工作项账本

新建或当前活跃的正式工作项必须初始化并读取：

```text
.ai-sdlc/work-items/<wi-id>/work-item.yaml
```

不得从全局 checkpoint 中继承上一个工作项的 `current_stage`、feature 或 close 状态。全局 checkpoint 只描述当前运行器位置；一旦命令显式指定 `--wi`，当前工作项账本优先。

兼容策略采用确定性矩阵：

| 场景 | 行为 |
| --- | --- |
| 新工作项或本次 R0/R1 工作项 | 创建账本，从明确入口状态开始 |
| legacy 工作项只读查询且无账本 | 不创建账本；只返回 evidence observation，生命周期为 `unavailable` |
| legacy 工作项首次 sponsor mutation | 必须显式提供 `--initial-status`、sponsor decision 与 formal payload digest 后才初始化 |
| legacy 证据冲突或不足 | `needs_user`，禁止自动推断已授权、已完成或历史 transition |

不批量回填历史工作项。WI225 已有明确 defer 决策，本次回归的唯一合法初始化结果是 `SUSPENDED`，不能在 `SUSPENDED` 与 `DOCS_BASELINE` 之间任选。

### 6.2 sponsor 决策映射

正式基线完成后，sponsor 决策必须与状态 transition 一起写入现有 `work-item.yaml`，而不是只写在自然语言 handoff 里。最小决策字段为：

```text
decision
actor
decided_at
scope
formal_payload_digest
lifecycle_revision
```

terminal remediation 还必须带 `single_change`、`investment_cap` 与 `terminal_outcome`。这些字段属于现有工作项账本，不新增 sponsor ledger 或 receipt artifact。

写入采用 compare-and-set：调用方提交 `expected_status + expected_lifecycle_revision`，实现必须在同一 repository write guard 内重新加载、校验 formal digest/scope、执行 transition、递增 revision 并原子替换文件。复用现有 `.git/ai-sdlc-write.lock` 机制，不增加第二把仓库写锁；并行 heartbeat 或人工操作看到 revision 不一致时返回 conflict，不允许最后写入者覆盖先前 defer/No-Go。

完整 sponsor transition 矩阵如下：

| 来源状态 | sponsor 事件 | 目标状态 | 限制 |
| --- | --- | --- | --- |
| `DOCS_BASELINE` | execute | `DEV_EXECUTING` | formal digest、scope 与 execute authorization 全部匹配 |
| `DOCS_BASELINE` | defer | `SUSPENDED` | 不生成 execute next action |
| `DOCS_BASELINE` | no-go | `FAILED` | 终态 |
| `SUSPENDED` | resume | `RESUMED` | 只恢复评估，不自动授权 execute |
| `RESUMED` | execute | `DEV_EXECUTING` | 重新校验 formal digest 与 scope |
| `RESUMED` | defer / no-go | `SUSPENDED` / `FAILED` | 原子决策 |
| `DEV_EXECUTING` | defer / no-go | `SUSPENDED` / `FAILED` | 保留已有执行证据，不再继续改动 |
| `DEV_VERIFYING` | terminal remediation | `DEV_EXECUTING` | 仅允许冻结 finding 的唯一修复 |
| `DEV_VERIFYING` | defer / no-go | `SUSPENDED` / `FAILED` | 两轮终局出口 |
| `DEV_REVIEWED`（legacy persisted） | terminal remediation | `DEV_EXECUTING` | 仅兼容旧流程；新 PR 流程使用上方 `DEV_VERIFYING` 行 |
| `DEV_REVIEWED`（legacy persisted） | defer / no-go | `SUSPENDED` / `FAILED` | 仅兼容旧流程；不再合并实现候选 |

`FAILED` 无出边。`DOCS_BASELINE/RESUMED -> DEV_EXECUTING` 只能调用上述事务入口；禁止任何直接状态写入绕过 decision 校验。close stage 从 `_AUTHORIZED_STAGES` 删除，truth classifier、handoff 文案和 checkpoint stage 均无权代替执行授权。

`ARCHIVING`、`KNOWLEDGE_REFRESHING`、持久 `DEV_REVIEWED` 和持久 `COMPLETED` 保留给 legacy/non-PR 流程。新的 PR 流程若有 archive 或 knowledge refresh 工作，必须在 `DEV_VERIFYING` 内完成；`ApprovedReviewIdentity` 成立后只投影有效 `DEV_REVIEWED`，不执行持久 transition，也不设计不存在的“回到可合并终点”transition。

### 6.3 evidence classification 不生成执行授权

`formal_freeze_only`、`branch_only_implemented`、`mainline_merged` 保留为证据观察分类，但 `next_required_actions` 改为读取生命周期：

- `formal_freeze_only + SUSPENDED`：等待 sponsor 恢复，不建议 execute。
- `formal_freeze_only + FAILED`：无下一步，终止。
- `formal_freeze_only + DOCS_BASELINE`：请求一次 sponsor 决策，而不是直接启动 execute。
- `formal_freeze_only + DEV_EXECUTING`：报告“已授权但未发现执行证据”，作为异常诊断。
- 未找到工作项账本的 legacy 工作项：只报告证据，不生成具有授权语义的动作。

### 6.4 pre-merge readiness 与 post-merge reconcile

关闭事务拆成两个不会互相写回的阶段：

#### A. pre-merge readiness（可写、合并前）

`workitem close-check` 的主职责改为按 readiness profile 验证当前候选是否具备合并条件：

| profile | 必须状态 | 验证范围 | 合并后的有效状态 |
| --- | --- | --- | --- |
| `formal-defer` | `SUSPENDED` | 正式文档、defer 决策、必要 review/check；实现任务 not-applicable | 保持 `SUSPENDED` |
| `formal-no-go` | `FAILED` | 正式文档、No-Go 决策、必要 review/check；实现任务 not-applicable | 保持 `FAILED` |
| `implementation` | 持久 `DEV_VERIFYING`；`ApprovedReviewIdentity` 投影有效 `DEV_REVIEWED` | 授权范围内任务、验收、验证与 required checks；通过后形成 `MergeReadyTuple` | merge observation 成立后投影 `COMPLETED` |

共同规则：

- 只验证 profile 范围内的任务、验收标准和必要验证；formal-defer/no-go 的实现任务明确为 not-applicable。
- 任务完成判定复用 task guard 的结构化 status：implementation profile 中 `done` 通过，`todo/doing/blocked/needs-review` 阻断。Markdown checkbox 只作 legacy/advisory 输入，不能覆盖结构化状态；两者冲突时 `needs_user`，不靠删除 checkbox 获得通过。
- 必要 reviewer gate 通过。
- sponsor 授权范围内的 finding 已处理。
- `LifecycleView` 的持久/有效状态组合与所选 profile 精确匹配；不得为通过 readiness 在 review 后改写账本。
- 当前候选分支尚未包含于主线时，返回 `merge_pending=true`，但不把它当作 readiness blocker。
- 合并 SHA、远端分支删除、工作树删除和主线包含不再是 pre-merge 必填字段。

pre-merge readiness 通过只表示“可合并”，绝不表示“已完成”。

#### B. post-merge reconcile（只读、合并后）

reconcile 接收 PR 编号或本地 immutable review run，从 provider/Git 读取事实：

- reviewer 实际审查的 head、PR base 与 required-check 集合。
- provider 记录的 merge result 及其合并时点 target/base。
- reviewed payload 与实际 merged PR payload 的完整内容等价性。
- merge result 是否仍可从当前 target branch 到达。
- 持久生命周期状态。

当持久 `DEV_VERIFYING` 已由 `ApprovedReviewIdentity` 投影为有效 `DEV_REVIEWED`，`MergeReadyTuple` 已证明候选可合并，且 reviewed payload 已包含于 target main 时，CLI 返回：

```text
effective_status=completed
contained_in_main=true
writeback_required=false
```

这个 `LifecycleView` 投影是唯一完成视图，不修改仓库、不生成新的 closeout commit，也不要求删除源分支后再证明删除已经发生。若未包含于主线，仍是 merge pending；unmerged 候选永远不能报告 completed。

### 6.5 semantic payload identity

R0 不再用“当前提交 SHA 必须已写入当前提交”这种自引用条件。评审身份和合并就绪拆成两个外部只读证明。

`ApprovedReviewIdentity` 只证明“谁审了什么”，不要求 checks 已经结束：

```text
PR identity
base OID
reviewed head OID
complete semantic payload digest
approved review verdict
expected required-check context set
policy version
```

`MergeReadyTuple` 只在 `ApprovedReviewIdentity` 已投影有效 `DEV_REVIEWED` 后生成：

```text
ApprovedReviewIdentity digest
current head OID and semantic payload digest
readiness-core result
required-check context set and successful results
policy version
```

完整 payload digest 覆盖 PR base 到 reviewed head 的全部 tracked 语义改动，包括新增、删除、rename、Git object type、file mode、路径和 blob 内容。只有已迁移到 ignored local path、且所有消费者都不能据其授权动作的 cache 才可排除。legacy tracked handoff/resume 在评审后冻结并继续计入 payload；不得一边让代理消费 tracked 指令，一边把它排除在评审身份之外。

pre-merge readiness 分两步且禁止递归：

1. `readiness-core` 验证 `ApprovedReviewIdentity`、当前 head/payload、生命周期有效状态、任务、授权和非递归本地门禁；它不读取 `MergeReadyTuple`，也不要求自己的 GitHub check 结果已经存在。
2. 外部只读 aggregator 在 `readiness-core` 结束后收集 required-check 结果并形成 `MergeReadyTuple`。aggregator 本身不是 required-check context；若 `close-check` 是 required check，它只承载 `readiness-core`，不得再验证 aggregate tuple。

最终 tuple 必须证明当前 PR head OID 或完整 semantic digest 与评审身份一致、required checks 全部绑定同一候选、无旧 head 成功结果复用，且当前 PR payload 不比 reviewed payload 多出任何 tracked 语义项。

post-merge 绑定 `MergeReadyTuple`，不拿“当前 main 同一路径的最终内容”直接比较，而是读取 provider 的实际 merge result，在**合并时点**比较 reviewed payload 与 merged PR payload，并确认：

- 无缺失、无额外语义项；
- squash/rebase 后 semantic patch 等价；
- merge conflict 没有引入未经评审的语义差异；
- merge result 仍可从当前 target branch 到达。

因此，合并后同一路径被后续 PR 合法修改，不会抹掉历史 contained 证明。若 provider/local review run 无法证明 reviewed head、checks 或 merge result，reconcile 返回 `needs_user`；显式 `--reviewed-rev` 只能用于已有本地 immutable review run，不能单独伪造远端 check binding。任何 payload mismatch 都 fail closed，且不得自动创建修补 PR。

### 6.6 两轮后 sponsor 终局

本地与 GitHub PR 流程统一为：

1. 初始候选 `H0` 接受评审。
2. 最多生成两个常规语义修复候选 `H1`、`H2`，每个都必须重新接受定向评审与 required checks。
3. `H2` 仍有稳定 REQUIRED/BLOCKER 时，进入一次 sponsor 终局决策。

sponsor 若批准最后一次有界处理，必须同时冻结：

- **唯一改动**：明确到稳定 finding 与允许修改的责任面。
- **投入上限**：时间、文件面或测试面至少一项硬上限。
- **终止结果**：成功则合并；未消除同一 finding 或出现越界则 No-Go/延期。

sponsor 可以无改动风险接受 `H2`、延期或 No-Go，也可以授权唯一 terminal remediation `H3`。`H3` 不是新的常规 round：它只处理冻结 finding 及直接回归面，只接受一次定向复评和 required checks；未通过即 `SUSPENDED/FAILED`，不得产生 `H4`。新的高风险安全/数据损坏证据可以 fail closed，但结果是终止或重新立项，不是给当前 PR 增加 head。

为避免 sponsor 决策本身再次改变已评审 head，review-budget 终局使用现有 provider PR review/approval 或现有 local immutable review run 记录，并绑定当前 `ApprovedReviewIdentity`：

- 无改动风险接受 `H2`：记录 merge approval，不修改 repo。
- 授权 `H3`：在 provider 决策中冻结唯一改动、投入上限和终止结果；`H3` 内的 lifecycle mutation 仍按 6.2 的账本 CAS 执行。
- defer/No-Go：不合并当前实现候选；`LifecycleView` 从绑定当前 tuple 的 terminal decision observation 投影 `SUSPENDED/FAILED`，不另开 records PR。

该 provider/local review 记录只负责评审预算终局，不能授权 execute。常规 lifecycle sponsor decision 仍必须通过 6.2 的 `work-item.yaml` CAS；两者冲突时 fail closed。

相应地：

- `pr-review fix` 达到上限后的 next action 不再建议增加 `--max-rounds`。
- CLI 参数不得突破项目策略上限。
- 仓库 `AGENTS.md` 的 GitHub heartbeat 规则必须与本地上限一致。
- heartbeat 只监控同一候选和批准范围；`H3` 评审结束后无条件停止自动修复路径。

## 7. R1：证据链与验证写放大收敛

### 7.1 handoff/resume 降为操作缓存

handoff 与 resume 的职责是帮助中断恢复，不是证明代码正确。R1 固定唯一持久化模型：

- canonical handoff、scoped handoff 和 resume pack 的**活动写入口**全部迁移到现有 ignored local cache；语义变更、测试、push 或每 20 分钟 checkpoint 都只能更新该 cache。
- 仓库内已有 tracked handoff/resume 仅作 legacy 只读兼容，R1 起不再由任何 writer 刷新；它们在评审后保持冻结并计入 semantic payload。
- 所有授权和 lifecycle consumer 禁止从 local cache 或 legacy handoff 推导 sponsor decision、execute authorization 或 completed。
- clean clone 缺少 local cache 时不影响 lifecycle/truth 结论。
- `AGENTS.md` 的连续性协议同步改为 local-cache 语义，不能继续要求产生 tracked dirty tree。

这项修改必须同时覆盖 canonical、scoped 与 resume-pack 三个入口。验收必须在评审后依次运行 handoff update 与 truth recompute，并证明 `git status --porcelain`、reviewed head OID 和 semantic digest 均不变化。

### 7.2 Program Truth 去固定库存计数

`tests/integration/test_repo_program_manifest.py` 不再断言 `1174/1174/0/5`、`223/218` 一类会随正常新增文件变化的绝对数量。保留高价值动态不变量：

- census 发现的 eligible sources 与 manifest inventory 集合一致。
- mapped sources 数量等于实际 mapped 集合长度。
- `unmapped_paths` 与实际差集一致。
- missing sources 与声明存在但远端/工作树缺失的实际集合一致。
- 已知 capability 的关键 truth/close refs 精确匹配。
- 既有 16 个 Program Truth blocker ID 集合只用于本次两个 PR 的 before/after 验收，不写入长期 `assert count == 16`。

只有产品语义要求固定成员时才断言具体 ref；不再把全仓库总数当作行为契约。

### 7.3 freshness、commit 与内容树分层

Program Truth 输出分别暴露：

- `snapshot_freshness`：快照是否基于当前输入生成。
- `observed_revision`：这次只读观察的 Git revision。
- `semantic_tree_identity`：行为相关内容是否与被评审内容等价。

三者不能再压缩成一个“exact head 是否一致”的 gate。Program Truth 默认现场计算或写 ignored local cache，不自动修改 tracked 文件。现有 `program-manifest.yaml.truth_snapshot` 只作 legacy/advisory 输入：继续兼容解析，但不再是 freshness gate，R1 起不由 sync 命令重写。

### 7.4 清理动作改为运维结果

远端 feature ref 删除、本地 branch 删除和 worktree 删除属于合并后的运维卫生：

- 可以由工具提示或自动化执行，但不构成 pre-merge blocker。
- 未清理时返回 advisory，不否定已验证的主线包含事实。
- 删除失败时报告具体占用或权限原因，不生成 records PR。
- 删除动作不能作为工作项 semantic completion 的证据来源。

### 7.5 验证分层

每个修复 batch 只运行与改动责任面匹配的测试：

- R0：状态机、execute authorization、truth-check、close-check、PR round limit、Git merge strategy matrix。
- R1：handoff、Program Truth inventory/freshness、shared checkout/clean clone 一致性。
- 全量测试只在 R0 和 R1 各自形成稳定候选后运行一次。

review finding 只触发直接责任面和回归面，不因库存数字变化或 continuity 文案变化重复跑全量测试。

## 8. 状态与数据流

### 8.1 正式基线延期

```text
formal docs ready
  -> DOCS_BASELINE
  -> sponsor defer
  -> SUSPENDED
  -> docs PR merged
  -> reconcile: SUSPENDED + contained_in_main=true
  -> no execute action, no records PR
```

### 8.2 正式基线 No-Go

```text
formal docs ready
  -> DOCS_BASELINE
  -> sponsor no-go
  -> FAILED
  -> docs PR may merge as decision record
  -> reconcile: FAILED + contained_in_main=true
  -> terminal, no repair round
```

### 8.3 已授权实现

```text
DOCS_BASELINE
  -> explicit execute authorization
  -> DEV_EXECUTING
  -> DEV_VERIFYING
  -> semantic freeze; work-item.yaml remains DEV_VERIFYING
  -> reviewer gate approved; ApprovedReviewIdentity projects effective_status=DEV_REVIEWED
  -> readiness-core and required checks produce MergeReadyTuple
  -> pre-merge readiness passes with merge_pending=true
  -> merge
  -> read-only reconcile confirms semantic payload in main
  -> effective_status=COMPLETED
```

### 8.4 两轮未收敛

```text
initial review H0
  -> regular focused fix H1 + review/checks
  -> regular focused fix H2 + review/checks
  -> unresolved stable finding
  -> one sponsor terminal decision
       accept H2 without changes -> merge
       authorize one terminal remediation H3 -> one review/check run -> merge or terminal no-go
       defer -> SUSPENDED
       reject -> FAILED
  -> H4 is forbidden
```

## 9. 失败处理与安全边界

- 缺少显式 execute authorization：保持 `DOCS_BASELINE` 或 `SUSPENDED`，不生成实现动作。
- 生命周期账本与证据分类冲突：报告冲突并 `needs_user`，不自动改写状态。
- reviewed payload 与 main 内容不一致：阻断 completed 投影，报告最小差异，不开新 PR。
- provider 的 reviewed head、required-check binding 或 merge result 不可确定：`needs_user`，不猜测、不用单独 SHA 代替完整 tuple。
- 生命周期 compare-and-set revision 冲突：重新读取并报告冲突；不得自动覆盖 sponsor decision。
- sponsor 有界处理越过冻结文件面或投入上限：终止当前工作项，不扩大授权。
- `H3` 后任何 REQUIRED/BLOCKER 或新的高风险安全/数据损坏 finding：fail closed，进入 No-Go、延期或新工作项评估；不得产生 `H4`。
- Program Truth snapshot 过期：现场重算并标记 freshness；默认不写 tracked snapshot。
- 清理失败：advisory；只有涉及数据丢失或目标不明确时才停止并请求用户。

## 10. 实现责任面

以下是责任边界，不是要求全部文件都必须修改。实施计划必须通过源码追踪缩减实际 diff。

| 阶段 | 主要责任面 | 设计责任 |
| --- | --- | --- |
| R0 | `src/ai_sdlc/models/work.py` | 复用状态并承载最小 sponsor/lifecycle 语义 |
| R0 | `src/ai_sdlc/core/state_machine.py` | sponsor CAS transaction、完整 transition matrix 与统一 lifecycle resolver |
| R0 | `src/ai_sdlc/core/execute_authorization.py` | 成为进入 execute 的唯一授权入口 |
| R0 | `src/ai_sdlc/core/workitem_truth.py` | classification 只观察证据；next action 读取生命周期 |
| R0 | `src/ai_sdlc/core/close_check.py` | close 改为 pre-merge readiness；未来事实不再阻塞 |
| R0 | `src/ai_sdlc/core/workitem_traceability.py` | 在不新增 ledger 的前提下提供 merge observation 与 `LifecycleView` 输入 |
| R0 | `src/ai_sdlc/core/pr_review_service.py`、loop policy | 两轮后 sponsor 终局，删除扩大轮次指引 |
| R0 | `src/ai_sdlc/cli/workitem_cmd.py` | 清晰区分 readiness 与 read-only reconcile 输出 |
| R0 | `AGENTS.md` | heartbeat 与本地两轮上限一致 |
| R1 | `src/ai_sdlc/core/handoff.py`、`src/ai_sdlc/context/state.py` | operational cache 与 semantic identity 解耦 |
| R1 | `src/ai_sdlc/core/program_service.py` | freshness/revision/tree 分层，默认只读重算 |
| R1 | `tests/integration/test_repo_program_manifest.py` | 用集合不变量替代固定库存计数 |
| R0/R1 | 对应 unit/integration tests | 只覆盖上述责任面与 merge strategy 回归 |

如果源码追踪发现现有模块已能提供某项能力，优先删除重复路径或复用入口，不新建包装层。实施计划必须在写代码前冻结每个 PR 的 `planned_production_files`；不允许新增 production module，任何计划外 production file 都必须先回到 sponsor 重估，不能以“顺手重构”扩大责任面。测试采用参数化单测覆盖状态/策略组合，仅保留一条代表性 clean-clone E2E，禁止形成合并策略 × 环境的全笛卡尔积。

## 11. 验收标准

### 11.1 R0 验收

- WI225 的已有 defer 决策精确解析为 `SUSPENDED`，不再输出 start execute。
- sponsor No-Go 映射为 `FAILED`，close-check 对未执行任务返回 not-applicable，而非缺少实现证据 blocker。
- `DOCS_BASELINE/RESUMED -> DEV_EXECUTING` 在缺少同一 formal digest/scope 的显式授权时失败；close stage 永不授权 execute。
- formal-defer、formal-no-go、implementation 三种 readiness profile 分别接受持久 `SUSPENDED`、持久 `FAILED`、以及“持久 `DEV_VERIFYING` + `ApprovedReviewIdentity` 投影的有效 `DEV_REVIEWED`”；implementation 还必须生成非递归 `MergeReadyTuple`，只差合并时成功并返回 `merge_pending=true`。
- reviewer approval 不修改 `work-item.yaml`；review 前后 `git status --porcelain` 与候选 head 均不变化。
- `readiness-core` 不依赖自身 check 结果，`MergeReadyTuple` aggregator 不在 required-check context 集合中。
- 未合并候选永远不返回 `effective_status=COMPLETED`。
- fast-forward、merge commit、squash、rebase 四类合并策略均能以合并时点 semantic payload 正确判断 contained。
- 评审后追加任一 tracked 语义路径、复用旧 head checks 或 merge conflict 引入语义差异时 fail closed。
- 合并后同一路径被后续 PR 修改，历史 merge result 仍能证明原 payload contained。
- 同一 main/reviewed revision 重复运行 reconcile 两次，第二次及以后产生零仓库变更。
- sponsor decision 的并发 CAS 冲突不会覆盖 defer/No-Go；达到两轮后 CLI 与 heartbeat 都不允许提高 `--max-rounds`。
- H3 只评审一次；失败后不产生 H4。

### 11.2 R1 验收

- 请求评审后运行 canonical/scoped handoff update、resume refresh 与 truth recompute，`git status --porcelain`、reviewed head 和 semantic digest 均不变化。
- legacy tracked handoff/resume 保持只读冻结，且仍计入 semantic payload。
- clean clone 不含本地 handoff cache 时，生命周期、truth 和 reconcile 结论与 shared checkout 一致。
- 新增一个正常映射的工作项或设计文档时，不修改固定库存数字测试。
- Program Truth 的 freshness、observed revision、semantic tree identity 可分别断言。
- 现有 manifest truth snapshot 过期只产生 advisory/live recompute，不产生 tracked diff。
- 合并后保留或删除 feature branch/worktree 都不改变 completed 结论；未清理只产生 advisory。
- 两个阶段完成后，本次基线中的 16 个 Program Truth blocker ID 集合保持不变；长期测试不固定数量。

### 11.3 端到端验收

用一个新的最小 formal-only fixture 和一个最小 implementation fixture 验证：

1. 验证 legacy 只读查询不建账，显式 sponsor mutation 才按给定 initial status 初始化。
2. sponsor defer、No-Go、execute 三种路径各自进入正确状态。
3. execute 路径依次形成 `ApprovedReviewIdentity`、非递归 `MergeReadyTuple` 和 pre-merge readiness。
4. 用参数化 Git fixture 覆盖四种合并策略，并用一条 clean-clone E2E 验证只读 reconcile。
5. 在 shared checkout、fresh clone 和仅远端 ref 可见环境中得到相同结论。
6. 全流程不创建 post-merge records/truth closeout PR。

## 12. 迁移与 bootstrap

当前仓库本身正受“未来事实必须写回当前提交”的旧规则约束，因此 R0+R1 使用一次性 bootstrap，且顺序固定如下：

### PR1：R1 evidence substrate

- 只承载动态 inventory、ignored continuity cache、live/ignored truth recompute、legacy tracked snapshot/advisory 兼容及直接测试。
- 同一 PR 登记本设计文档，但不临时把 `1174` 改成 `1175`；测试改为集合不变量后自然通过。
- 本地候选门禁：`verify constraints`、handoff unit/integration、Program Service 定向单测、根 manifest 集成测试、`git diff --check`；稳定候选只运行一次全量测试。
- `ApprovedReviewIdentity` 冻结 GitHub target branch 当时要求的完整 check context 集合，`MergeReadyTuple` 收集的所有成功结果必须绑定当前候选。
- 合并后只读验收：handoff update 与 truth recompute 均为零 tracked diff。

### PR2：R0 lifecycle transaction

- 只承载 sponsor CAS、完整 transition/readiness matrix、唯一 `LifecycleView`、review/merge tuple、close/reconcile 及直接测试。
- 本地候选门禁：`verify constraints`、state machine、execute authorization、truth/close、PR round limit、semantic merge matrix、`git diff --check`；稳定候选只运行一次全量测试。
- 同样通过 `ApprovedReviewIdentity` 冻结 required-check context 集合，再由 `MergeReadyTuple` 验证结果，禁止复用旧 head 成功结果。
- 合并后只在隔离 clone 中运行 reconcile；重复运行零写回，不追加 records PR。

PR1 合并后的过渡主线只改变 evidence writer/验证契约，不改变 lifecycle verdict；R0 未合并前仍不授权新特性。PR2 从这个无 tracked write-amplification 的基线启动。

两个 PR 都遵守 `H0/H1/H2 + 可选唯一 H3` 规则。bootstrap 允许用外部 provider tuple 证明 review/merge 事实，但不允许绕过 reviewer gate、required checks 或执行授权。

bootstrap 只适用于这两个根治 PR，不成为普通工作项绕过 reviewer gate、checks 或执行授权的永久入口。

## 13. 投入、ROI 与止损边界

| 项目 | 预期投入 | 直接价值 | ROI 判断 |
| --- | ---: | --- | --- |
| R1 evidence substrate | 1.5–2 人日 | 先消除 handoff/self-head 漂移、固定库存改测和重复全量验证，为 R0 建立可合并基线 | 高，先做 |
| R0 生命周期/close transaction | 2.5–3 人日 | 消除错误 execute 授权、未来事实阻塞和 post-merge records PR | 最高价值，第二个 PR 完成根治 |
| 总缓冲 | 0–0.5 人日 | 仅处理上述责任面的真实回归 | 不得转为特性投入 |

硬边界：

- 总投入不超过 5 人日。
- 最多两个修复 PR。
- 每个 PR 固定 H0 加最多 H1/H2 两个常规修复 heads；sponsor 最多再授权唯一 H3，H3 后禁止 H4。
- 不新增治理 artifact 类型，不批量迁移历史工作项，不进入新特性。
- 实施计划必须冻结每个 PR 的 production file 集；新增 module 或计划外 production file 先进入 sponsor 重估。
- 若 R1 无法在 2 人日内让“handoff/truth 重算零 tracked diff”成立，则停止，不启动 R0。
- 若 R0 无法在剩余总预算内让“合并后零写回”成立，则 No-Go，不以更多例外掩盖失败。

## 14. 发布判定

只有以下条件全部成立，才解除新特性冻结：

- R0 与 R1 的直接测试和一次全量测试通过。
- 独立评审无未解决 REQUIRED/BLOCKER。
- 两个 PR 合并后，隔离 clone 的 reconcile 产生零写回。
- 当前正式延期/No-Go 工作项不再被提示自动进入 execute。
- Program Truth 对整改前 16 个 blocker ID 集合完成前后对账，没有吞掉 blocker，也没有把数量固化成永久断言。

满足后，下一步不是继续磨治理细节，而是回到已批准产品路线，按 ROI 重新选择一个工作项。
