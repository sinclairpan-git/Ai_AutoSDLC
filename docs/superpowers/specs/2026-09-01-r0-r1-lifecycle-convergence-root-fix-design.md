# R0+R1 生命周期收敛根治设计

## 1. 决策摘要

本轮只批准两项根治性整改，不开发任何新特性：

- **R0：修正工作项生命周期与合并闭环。** 复用现有 `WorkItemStatus` 与 `.ai-sdlc/work-items/<wi-id>/work-item.yaml`，让 sponsor 决策、执行授权、评审就绪和主线包含各自只有一个权威来源。
- **R1：消除证据链写放大。** 把 handoff、resume、Program Truth 快照和清理动作从“每轮必须改动的评审内容”降为可再生或只读证据，并移除仓库测试中的固定库存计数。

实施顺序固定为 R0 后 R1，最多两个修复 PR，总投入上限 5 人日。两个修复完成并通过验收前，继续冻结新特性。

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
- 保留现有 16 个 Program Truth blocker，不用本次整改删除、豁免或重写历史事实。

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
| 生命周期状态 | 当前工作项的 `work-item.yaml` + 状态机 | 是，受合法 transition 与 sponsor 决策约束 |
| 执行证据分类 | `workitem truth-check` 对指定 revision 的只读观察 | 否，只回答是否存在 implementation evidence |
| 评审结论 | PR provider / 本地 review run 对某个候选 head 的 verdict | 否，只决定候选内容是否可进入 merge-ready |
| 主线包含 | 指定 target ref 上的 Git 内容比较 | 否，只回答 reviewed payload 是否已进入主线 |
| 连续性/诊断缓存 | handoff、resume、truth snapshot | 否，可再生，不参与 semantic review identity |

最终状态不是把上述字段压成一个模糊 classification，而是明确组合：

- `SUSPENDED + contained_in_main=true`：正式基线已进入主线，当前明确延期，不启动 execute。
- `FAILED + contained_in_main=true`：正式基线已进入主线，sponsor No-Go，终止本项。
- `DEV_REVIEWED + contained_in_main=false`：评审通过、等待合并，不得宣称完成。
- `DEV_REVIEWED + contained_in_main=true`：只读投影为 `effective_status=COMPLETED`。
- `formal_freeze_only`：仅说明没有实现证据，不能推导“必须开始 execute”。

## 6. R0：生命周期与合并闭环

### 6.1 复用现有工作项账本

新建或当前活跃的正式工作项必须初始化并读取：

```text
.ai-sdlc/work-items/<wi-id>/work-item.yaml
```

不得从全局 checkpoint 中继承上一个工作项的 `current_stage`、feature 或 close 状态。全局 checkpoint 只描述当前运行器位置；一旦命令显式指定 `--wi`，当前工作项账本优先。

兼容策略：

- 新工作项和本次 R0/R1 工作项使用账本。
- 旧工作项没有账本时继续走只读兼容路径，不批量回填。
- 对旧工作项发生新的写操作时，才按当前已知状态最小初始化，不推断未被证据证明的历史 transition。

### 6.2 sponsor 决策映射

正式基线完成后，sponsor 决策必须映射到现有状态，而不是写在自然语言 handoff 里：

| sponsor 决策 | 持久状态 | 后续动作 |
| --- | --- | --- |
| 授权 execute | `DEV_EXECUTING` | 只有显式执行授权通过后才能进入 |
| 延期/等待条件 | `SUSPENDED` | 无 execute next action；以后需显式 resume + execute authorization |
| No-Go/终止 | `FAILED` | 终态，不再申请修复轮次或启动实现 |

因此状态机需要允许 `DOCS_BASELINE -> SUSPENDED` 与 `DOCS_BASELINE -> FAILED`。`DOCS_BASELINE -> DEV_EXECUTING` 保留，但必须经过 execute authorization；close stage、truth classifier、handoff 文案均无权代替该授权。

`SUSPENDED -> RESUMED -> DEV_EXECUTING` 的最后一步同样必须重新校验授权，避免“恢复”被解释为自动开工。

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

`workitem close-check` 的主职责改为验证当前候选是否具备合并条件：

- 任务、验收标准和必要验证已完成。
- 必要 reviewer gate 通过。
- sponsor 授权范围内的 finding 已处理。
- 工作项处于 `DEV_REVIEWED`；如有实际 archive/knowledge refresh 工作，可先经过现有状态再回到可合并终点。
- 当前候选分支尚未包含于主线时，返回 `merge_pending=true`，但不把它当作 readiness blocker。
- 合并 SHA、远端分支删除、工作树删除和主线包含不再是 pre-merge 必填字段。

pre-merge readiness 通过只表示“可合并”，绝不表示“已完成”。

#### B. post-merge reconcile（只读、合并后）

reconcile 接收 PR 编号或显式 reviewed revision，从 provider/Git 读取事实：

- reviewer 实际审查的 head。
- target branch 当前 revision。
- reviewed payload 在 target branch 中的内容等价性。
- 持久生命周期状态。

当 `DEV_REVIEWED` 的 reviewed payload 已包含于 target main 时，CLI 返回：

```text
effective_status=completed
contained_in_main=true
writeback_required=false
```

这个投影不修改仓库，不生成新的 closeout commit，也不要求删除源分支后再证明删除已经发生。若未包含于主线，仍是 merge pending；unmerged 候选永远不能报告 completed。

### 6.5 semantic payload identity

R0 不再用“当前提交 SHA 必须已写入当前提交”这种自引用条件。比较对象改为 reviewed semantic payload：

- 以 PR provider 返回的实际 reviewed head 为起点。
- 计算该 PR 变更中需要评审的内容集合及内容摘要。
- 从 semantic payload 中排除 handoff、resume cache、可再生 truth snapshot、临时 review artifacts 和清理标记。
- runtime、tests、规范正文、约束配置及会影响行为的 manifest 仍属于 semantic payload。
- 在 target main 上对相同路径计算内容摘要，支持 fast-forward、merge commit、squash 和 rebase 后的等价判断。

若 provider 无法给出 reviewed head，reconcile 必须 `needs_user`，允许用户显式提供 `--reviewed-rev`，但不得猜测最近 commit。

若 main 上相关内容与 reviewed payload 不等价，返回 tree mismatch 并停止；不得自动创建修补 PR。

### 6.6 两轮后 sponsor 终局

本地与 GitHub PR 流程统一为：

1. 初始候选 head 接受评审。
2. 最多生成两个包含语义修复的 pushed heads。
3. 达到上限仍有 REQUIRED/BLOCKER 时，进入一次 sponsor 终局决策。

sponsor 若批准最后一次有界处理，必须同时冻结：

- **唯一改动**：明确到稳定 finding 与允许修改的责任面。
- **投入上限**：时间、文件面或测试面至少一项硬上限。
- **终止结果**：成功则合并；未消除同一 finding 或出现越界则 No-Go/延期，不再开启第三轮。

sponsor 决策不是新的常规 repair round。它只处理已稳定复现的 finding 及其直接回归面，不允许重新扫描并扩展无限问题空间。新的高风险安全/数据损坏证据可以 fail closed，但结果是终止或重新立项，不是给当前 PR 增加轮次。

相应地：

- `pr-review fix` 达到上限后的 next action 不再建议增加 `--max-rounds`。
- CLI 参数不得突破项目策略上限。
- 仓库 `AGENTS.md` 的 GitHub heartbeat 规则必须与本地上限一致。
- heartbeat 只监控同一候选和批准范围；达到终局条件后暂停并报告，不继续自动请求评审。

## 7. R1：证据链与验证写放大收敛

### 7.1 handoff/resume 降为操作缓存

handoff 与 resume 的职责是帮助中断恢复，不是证明代码正确。R1 固定以下边界：

- semantic freeze 之前可以更新 handoff。
- 请求评审后，不因“当前 head、下一步、已 push”文案变化刷新 tracked handoff。
- handoff 不参与 semantic payload identity，也不能使既有 reviewer verdict 失效。
- clean clone 缺少本地 cache 时不影响 lifecycle/truth 结论。
- 若仓库策略仍要求 committed continuity，只提交稳定目标、边界和恢复入口，不记录必然随每次 push 变化的瞬时 SHA 或待办语句。

这项修改必须同时覆盖 canonical handoff 与 scoped handoff，避免一份被降级、另一份仍触发写回。

### 7.2 Program Truth 去固定库存计数

`tests/integration/test_repo_program_manifest.py` 不再断言 `1174/1174/0/5`、`223/218` 一类会随正常新增文件变化的绝对数量。保留高价值动态不变量：

- census 发现的 eligible sources 与 manifest inventory 集合一致。
- mapped sources 数量等于实际 mapped 集合长度。
- `unmapped_paths` 与实际差集一致。
- missing sources 与声明存在但远端/工作树缺失的实际集合一致。
- 已知 capability 的关键 truth/close refs 精确匹配。
- 既有 16 个 Program Truth blocker 数量和身份在本次整改中保持不变。

只有产品语义要求固定成员时才断言具体 ref；不再把全仓库总数当作行为契约。

### 7.3 freshness、commit 与内容树分层

Program Truth 输出分别暴露：

- `snapshot_freshness`：快照是否基于当前输入生成。
- `observed_revision`：这次只读观察的 Git revision。
- `semantic_tree_identity`：行为相关内容是否与被评审内容等价。

三者不能再压缩成一个“exact head 是否一致”的 gate。快照过期可以要求重新计算，但重新计算默认写入本地 cache 或直接输出，不自动修改 tracked 文件。

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
  -> reviewer gate approved
  -> DEV_REVIEWED
  -> pre-merge readiness passes with merge_pending=true
  -> merge
  -> read-only reconcile confirms semantic payload in main
  -> effective_status=COMPLETED
```

### 8.4 两轮未收敛

```text
review head 0
  -> focused fix head 1
  -> focused fix head 2
  -> unresolved stable finding
  -> one sponsor terminal decision
       approve bounded action -> merge or terminal no-go
       defer -> SUSPENDED
       reject -> FAILED
```

## 9. 失败处理与安全边界

- 缺少显式 execute authorization：保持 `DOCS_BASELINE` 或 `SUSPENDED`，不生成实现动作。
- 生命周期账本与证据分类冲突：报告冲突并 `needs_user`，不自动改写状态。
- reviewed payload 与 main 内容不一致：阻断 completed 投影，报告最小差异，不开新 PR。
- provider review head 不可确定：要求显式 revision，不猜测。
- sponsor 有界处理越过冻结文件面或投入上限：终止当前工作项，不扩大授权。
- 两轮后出现新的高风险安全或数据损坏 finding：fail closed，进入 No-Go 或新工作项评估；不得把它伪装成第三轮。
- Program Truth snapshot 过期：现场重算并标记 freshness；默认不写 tracked snapshot。
- 清理失败：advisory；只有涉及数据丢失或目标不明确时才停止并请求用户。

## 10. 实现责任面

以下是责任边界，不是要求全部文件都必须修改。实施计划必须通过源码追踪缩减实际 diff。

| 阶段 | 主要责任面 | 设计责任 |
| --- | --- | --- |
| R0 | `src/ai_sdlc/models/work.py` | 复用状态并承载最小 sponsor/lifecycle 语义 |
| R0 | `src/ai_sdlc/core/state_machine.py` | 新增合法 defer/no-go transition；执行 transition 强制授权 |
| R0 | `src/ai_sdlc/core/execute_authorization.py` | 成为进入 execute 的唯一授权入口 |
| R0 | `src/ai_sdlc/core/workitem_truth.py` | classification 只观察证据；next action 读取生命周期 |
| R0 | `src/ai_sdlc/core/close_check.py` | close 改为 pre-merge readiness；未来事实不再阻塞 |
| R0 | `src/ai_sdlc/core/workitem_traceability.py` | 解析当前工作项账本与 review/merge observation |
| R0 | `src/ai_sdlc/core/pr_review_service.py`、loop policy | 两轮后 sponsor 终局，删除扩大轮次指引 |
| R0 | `src/ai_sdlc/cli/workitem_cmd.py` | 清晰区分 readiness 与 read-only reconcile 输出 |
| R0 | `AGENTS.md` | heartbeat 与本地两轮上限一致 |
| R1 | `src/ai_sdlc/core/handoff.py`、`src/ai_sdlc/context/state.py` | operational cache 与 semantic identity 解耦 |
| R1 | `src/ai_sdlc/core/program_service.py` | freshness/revision/tree 分层，默认只读重算 |
| R1 | `tests/integration/test_repo_program_manifest.py` | 用集合不变量替代固定库存计数 |
| R0/R1 | 对应 unit/integration tests | 只覆盖上述责任面与 merge strategy 回归 |

如果源码追踪发现现有模块已能提供某项能力，优先删除重复路径或复用入口，不新建包装层。

## 11. 验收标准

### 11.1 R0 验收

- 当前类似 WI225 的“正式基线已合主线但未授权实现”场景被表示为 `SUSPENDED` 或 `DOCS_BASELINE`，不再输出 start execute。
- sponsor No-Go 映射为 `FAILED`，close-check 对未执行任务返回 not-applicable，而非缺少实现证据 blocker。
- `DOCS_BASELINE -> DEV_EXECUTING` 在无显式授权时失败。
- pre-merge readiness 在所有当前可验证项通过、只差合并时成功并返回 `merge_pending=true`。
- 未合并候选永远不返回 `effective_status=COMPLETED`。
- fast-forward、merge commit、squash、rebase 四类合并策略均能以 semantic payload 正确判断 contained。
- 同一 main/reviewed revision 重复运行 reconcile 两次，第二次及以后产生零仓库变更。
- 达到两轮后 CLI 与 heartbeat 都不允许通过提高 `--max-rounds` 继续；只返回 sponsor terminal decision。

### 11.2 R1 验收

- 请求评审后刷新本地 handoff cache，不改变 semantic payload identity，也不要求重新评审。
- clean clone 不含本地 handoff cache 时，生命周期、truth 和 reconcile 结论与 shared checkout 一致。
- 新增一个正常映射的工作项或设计文档时，不修改固定库存数字测试。
- Program Truth 的 freshness、observed revision、semantic tree identity 可分别断言。
- 合并后保留或删除 feature branch/worktree 都不改变 completed 结论；未清理只产生 advisory。
- 两个阶段完成后，既有 16 个 Program Truth blocker 的身份和数量保持不变。

### 11.3 端到端验收

用一个新的最小 formal-only fixture 和一个最小 implementation fixture 验证：

1. 初始化工作项账本。
2. sponsor defer、No-Go、execute 三种路径各自进入正确状态。
3. execute 路径完成评审和 pre-merge readiness。
4. 通过四种 Git 合并策略验证只读 reconcile。
5. 在 shared checkout、fresh clone 和仅远端 ref 可见环境中得到相同结论。
6. 全流程不创建 post-merge records/truth closeout PR。

## 12. 迁移与 bootstrap

当前仓库本身正受“未来事实必须写回当前提交”的旧规则约束，因此 R0+R1 使用一次性 bootstrap 方式：

- 以精确 base、候选 head、reviewed head 和 required checks 作为外部可验证事实。
- R0 PR 只承载生命周期/close transaction 修复及其直接测试。
- R1 PR 只承载 evidence write-amplification 修复及其直接测试。
- 每个 PR 最多两个语义修复 heads；两轮后按本设计进入 sponsor 终局。
- PR 合并后只在隔离 clone 中运行 reconcile 与验收，不再追加 records PR。
- 不为满足旧固定计数而增加临时例外；R1 直接移除该固定计数契约。

bootstrap 只适用于这两个根治 PR，不成为普通工作项绕过 reviewer gate、checks 或执行授权的永久入口。

## 13. 投入、ROI 与止损边界

| 项目 | 预期投入 | 直接价值 | ROI 判断 |
| --- | ---: | --- | --- |
| R0 生命周期/close transaction | 2.5–3 人日 | 消除错误 execute 授权、未来事实阻塞和 post-merge records PR | 最高，先做 |
| R1 evidence 写放大 | 1.5–2 人日 | 消除 handoff/self-head 漂移、固定库存改测和重复全量验证 | 高，紧随 R0 |
| 总缓冲 | 0–0.5 人日 | 仅处理上述责任面的真实回归 | 不得转为特性投入 |

硬边界：

- 总投入不超过 5 人日。
- 最多两个修复 PR。
- 每个 PR 最多两个语义修复 heads，之后只有一次 sponsor 终局决策。
- 不新增治理 artifact 类型，不批量迁移历史工作项，不进入新特性。
- 若 R0 无法在 3 人日内让“合并后零写回”验收成立，则暂停 R1，提交根因证据并 No-Go，不以更多例外掩盖失败。

## 14. 发布判定

只有以下条件全部成立，才解除新特性冻结：

- R0 与 R1 的直接测试和一次全量测试通过。
- 独立评审无未解决 REQUIRED/BLOCKER。
- 两个 PR 合并后，隔离 clone 的 reconcile 产生零写回。
- 当前正式延期/No-Go 工作项不再被提示自动进入 execute。
- Program Truth 仍如实保留 16 个既有 blocker，没有用本次整改伪造绿色结论。

满足后，下一步不是继续磨治理细节，而是回到已批准产品路线，按 ROI 重新选择一个工作项。
