# 功能规格：两轮评审终局 Sponsor 决策收敛合同

**功能编号**：`225-review-terminal-sponsor-convergence`
**创建日期**：2026-08-31
**状态**：G1 formal/admission；规则实现未授权
**真值基线**：`origin/main@e8a73ec409a7eb771abc41dcc996dc198c031a5d`
**关联路线图**：`docs/FRAMEWORK_ROADMAP.zh-CN.md`

## 1. 目标与边界

本工作项评估一个最小治理合同：候选默认最多经过两轮修复/复审；仍未收敛时必须停止普通循环，进入一次 terminal sponsor decision。Sponsor 若批准，只能冻结一个改动、一个投入上限和一个终止结果；终局复核只验证稳定 finding 及其直接回归面，不重新开启无限问题空间。

### 1.1 本次覆盖

- 只以精确远端主线、PR #194/#195 的真实收口结果和仓库现有 Local Repository PR Protocol 为证据。
- 核对现有 `LoopRun / LoopRound`、`needs_user`、`finding-history.json`、`risk_accepted`、final report 与 attestation 是否足够复用。
- 比较 repo-local 规则、Local PR Review runtime 和新增 sponsor artifact 三种落地方式。
- 冻结一个后续最小候选、投入上限、终止结果及 No-Go 条件。
- 只在 WI225 formal carrier 内归档结论，并同步 Program Truth、固定库存期望和 continuity；路线图与 defect backlog 保持只读，避免越过 `formal_freeze_only` 控制面。

### 1.2 本次不覆盖

- 不修改 WI224、PR #194/#195 的任何历史记录、workflow、release receipt 或 12 路状态。
- 不修改 `src/` runtime、review schema、状态机、CLI 行为或现有测试逻辑。
- 不新增 waiver、receipt、ledger、certificate、sponsor artifact、命令或并行评审引擎。
- 不启动 P3 其余 11 路、P4、D2、v0.9.9 或全仓治理。
- 不创建 `development-summary.md`；formal/admission 不冒充 runtime execute。
- 不使用参赛版、产品站、本地材料分支或未合并 worktree 作为主线真值。

## 2. 现状证据

| 证据 | 主线事实 | 对 G1 的含义 |
|---|---|---|
| `AGENTS.md` Local Repository PR Protocol | heartbeat 会持续处理 review/check，直到合并或用户输入 blocker，但没有两轮后的 terminal sponsor 分支 | 实际复发层在 repo-local PR/heartbeat 协议 |
| `docs/FRAMEWORK_ROADMAP.zh-CN.md`（只读） | 已写明两轮上限、terminal sponsor decision、唯一改动/投入/结果冻结 | 原则已有，但没有进入实际执行协议；本 Formal 不修改路线图 |
| `src/ai_sdlc/core/loop_models.py` | 已有 `LoopRun`、`LoopRound`、`needs_user` 和默认 `max_rounds=2` | 不需要新状态机 |
| `src/ai_sdlc/core/pr_review_service.py` | rerun 已按 severity/file/line/claim/risk 生成稳定签名并写 `finding-history.json` | 不需要新 finding schema |
| `src/ai_sdlc/core/pr_review_service.py` | 达到上限时返回 `needs_user`，但提示仍允许 `increase --max-rounds` | 证明原则与现有 CLI 提示不一致，但不是本次实际复发的主控制层 |
| `risk_accepted`、final report、attestation | 已能披露未解决 REQUIRED、写最终报告并用 digest 绑定 | 若未来扩展 Local PR Review，可复用现有终态，不应新造 artifact |
| PR #194/#195 收口 | 产品和主线真值已完成；继续创建 WI224 records-only PR 只会修治理自闭环 | terminal decision 必须允许接受已知流程限制并停止；后续 GitHub 编号不代表 WI224 续修 |

## 3. 用户场景与测试

### 用户故事 US-225-1：两轮后获得唯一终局决策（优先级：P0）

作为仓库维护者，我希望两轮修复/复审仍未收敛时，heartbeat 自动暂停并向 Sponsor 给出一次有边界的终局选择，以便不再通过连续“例外”制造新 PR 和新收口循环。

**优先级说明**：PR #194/#195 后已真实出现“为关闭而再开关闭 PR”的递归；继续发生会直接消耗评审和 CI 成本，并使治理代码/记录超过产品价值。

**独立测试**：给定同一候选已完成两轮修复/复审，检查 repo-local 协议必须要求暂停 heartbeat，并且下一步只能是 `No-Go/接受已知限制` 或 `批准一次冻结动作`，不能继续普通第三轮。

**验收场景**：

1. **Given** 两轮后仍有可操作 finding，**When** 代理准备继续修复，**Then** 必须暂停并请求 terminal sponsor decision，不得自行增加轮次。
2. **Given** Sponsor 不批准继续，**When** 终局决策生效，**Then** 必须记录真实 known-blocked/No-Go 结果并删除旧 heartbeat，不再创建 PR。

### 用户故事 US-225-2：保留模型自主性但冻结投入（优先级：P0）

作为 Sponsor，我希望在安全、兼容或恢复证据确实支持时仍能批准一次终局修复，但批准必须同时冻结唯一 delta、投入上限和终止结果，以便保留判断弹性而不恢复无限问题空间。

**优先级说明**：完全禁止终局修复会过度僵化；没有冻结字段又会回到逐轮申请例外。三项同时存在才能兼顾自主性与 ROI。

**独立测试**：检查批准路径必须同时出现 `unique_delta`、`effort_cap`、`terminal_outcome`，缺少任一项时不得恢复 heartbeat 或执行修改。

**验收场景**：

1. **Given** Sponsor 批准终局动作，**When** 代理恢复执行，**Then** 只能修改冻结 delta，复核只覆盖稳定 finding 及直接回归面。
2. **Given** 终局复核出现新的同范围高风险证据或冻结 delta 失败，**When** 形成结果，**Then** 直接按冻结的 terminal outcome 结束，不再开启第二个例外。

### 3.1 边界情况

- 新发现的安全、隐私、数据破坏或发布完整性 BLOCKER 不能被“稳定 finding”过滤掉；它会直接把终局结果变为 No-Go/blocked，但不获得新修复轮次。
- required check 的基础设施重跑不计入修复轮次；只有代码、规则、workflow 或正式记录发生新 delta 才计入。
- Reviewer 仅改写措辞但 severity/file/line/claim/risk 稳定签名不变时，视为同一 finding。
- 同一文件出现无关新建议，不得借终局复核扩入冻结 delta。
- 用户主动提出新的产品目标属于新 work item，不属于终局例外。

## 4. 方案比较与 Admission 决策

### 方案 A：repo-local PR/heartbeat 协议补强（推荐）

- 后续仅修改根 `AGENTS.md` 的 Local Repository PR Protocol。
- 两轮后暂停 heartbeat，要求一次 terminal sponsor decision。
- 批准时要求 `unique_delta / effort_cap / terminal_outcome`；拒绝时删除 heartbeat并接受真实终态。
- 终局复核只验证稳定 finding、冻结 delta 和直接回归；新高风险证据只能改变终局结果，不能增加轮次。
- **投入上限**：实现、验证、评审和合并合计不超过 0.5 人日；只允许一个规则实现 PR，不允许 post-merge records-only PR。
- **优点**：作用于本次真实复发层；不新增 runtime、schema、状态或 artifact。
- **限制**：只约束本仓库自开发协议，不冒充所有普通用户项目的产品能力。

### 方案 B：修改 Local PR Review runtime（本次 No-Go）

- 可修正 `increase --max-rounds` 提示并增加 terminal close 编排。
- 但本次递归来自 GitHub PR heartbeat/代理协议，单改本地 CLI 无法阻止同类复发。
- 会触达 Python runtime、CLI 和测试，投入高于方案 A，且容易误扩成通用状态生命周期。

### 方案 C：新增 SponsorDecision artifact/schema（No-Go）

- 结构化程度最高，但会新增 artifact、schema、迁移、CLI、验证和长期生命周期。
- 支撑成本显著高于一个 repo-local 规则缺口，直接违反“不复制治理”和本次边界。

**Admission 结论**：方案 A 为 `implement-candidate`，但 runtime/rules execute 仍为 `defer`，必须在本 formal PR 合并后取得新的明确授权。方案 B/C 为 No-Go。

## 5. 功能需求

- **FR-225-001**：formal 必须绑定精确 `origin/main@e8a73ec409a7eb771abc41dcc996dc198c031a5d`，并忽略用户排除的本地材料。
- **FR-225-002**：必须把普通修复/复审上限冻结为两轮；达到上限后不得建议增加轮次。
- **FR-225-003**：terminal sponsor decision 只能为 `stop` 或 `approve-one-bounded-action`；批准必须同时冻结 `unique_delta`、`effort_cap`、`terminal_outcome`。
- **FR-225-004**：终局复核必须优先消费稳定 finding 映射及冻结 delta 的直接回归；不得重新打开全量优化空间。
- **FR-225-005**：新的高风险事实可以把终局结果改为 No-Go/blocked，但不能自动获得下一轮修复。
- **FR-225-006**：后续候选必须作为一个语义 delta，只修改根 `AGENTS.md` 的 repo-local 协议，并在现有 `tests/unit/test_verify_constraints.py` 增加一个针对两轮上限与 terminal sponsor 必需标记的静态回归测试；不得修改 `src/`、产品 runtime、review schema、状态机、WI224 或历史日志。
- **FR-225-007**：后续候选总投入不得超过 0.5 人日、一个实现 PR、一次终局复核；超出任一边界立即 No-Go。
- **FR-225-008**：formal/admission 只更新 WI225 的 spec/plan/tasks/task-execution-log、Program Truth 固定库存期望和 continuity；路线图与 defect backlog 保持只读，不创建 `development-summary.md`。

## 6. ROI 与实现边界

1. **用户可观察收益或可复现风险**：减少重复 PR、CI、review 与记录收口；避免治理细节超过产品价值。
2. **现状证据**：WI224 已完成产品/主线交付，但为 lifecycle close-check 继续提出 #196 会形成第二个 post-merge closeout；现有 repo-local 协议没有终局分支。
3. **最小方案**：补 `AGENTS.md` repo-local 协议，并在现有 `tests/unit/test_verify_constraints.py` 增加一个静态回归测试，防止两轮上限或 terminal sponsor 必需标记被静默删除；不改本地 PR runtime，因为它不是本次复发的实际控制层。
4. **总投入**：formal/admission 不超过 0.5 人日；后续规则实现若获批也不超过 0.5 人日。
5. **范围与退出条件**：需要上述两个冻结文件以外的实现文件、静态标记检查以外的测试逻辑、产品 runtime、新 schema/artifact/命令、第二个修复 PR 或 post-merge records PR 时立即 No-Go。
6. **决策**：`defer`；formal admission 支持一个规则候选，等待新的 execute 授权。

## 7. 成功标准

- **SC-225-001**：formal 对账证明现有 `needs_user`、稳定 finding history 和终态 report/attestation 可复用，不新增状态机或 artifact。
- **SC-225-002**：只保留一个后续候选，精确限定为根 `AGENTS.md` 与现有 `tests/unit/test_verify_constraints.py` 的一个语义 delta，投入上限 0.5 人日。
- **SC-225-003**：spec/plan/tasks 均明确 runtime/rules execute 未授权，且没有实现任务被勾选或暗示已落地。
- **SC-225-004**：Program Truth 保持 fresh/blocked、原 16 个历史 blocker 不变；库存为 `1174/1174 mapped`、missing 5、close `218/223`。
- **SC-225-005**：constraints、plan-check、manifest regression、truth audit 与 `git diff --check` 通过；独立 formal/ROI 评审无可操作问题后才允许创建 PR。
