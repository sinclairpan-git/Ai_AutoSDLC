# 功能规格：Requirement Loop 有界动态专家评审纵向薄片

**功能编号**：`228-requirement-bounded-dynamic-expert-review`
**创建日期**：2026-09-05
**状态**：G3 implementation GO；三例盲测通过，待同一候选 head 双专家终审与 terminal PR
**真值基线**：`origin/main@71e4ff5098505d0c6321c9162c1b9b1647d155d1`
**关联路线图**：`docs/FRAMEWORK_ROADMAP.zh-CN.md` P4 Phase A

## 1. 目标与边界

当前 Requirement Loop 能把需求与验收标准确定性落盘，并由用户显式 `freeze --yes` 关闭，但 `needs_review` 到 `closed` 之间没有独立专家输入、风险匹配或 reviewed-input 漂移保护。本工作项只实现 Requirement Loop 的一个纵向薄片：为当前需求结果生成只读、摘要绑定、最多两个临时角色的评审输入；允许一次修改后复审；冻结时拒绝已经失效的评审摘要。

这不是现有 freeze 逻辑失效，而是主仓相对参赛版的新能力差距。目标是先用最小实现和三个盲测价值回放证明增量价值，再决定是否另立工作项扩展 Design Contract 或 Implementation。

### 1.1 本次覆盖

- 只覆盖 `Requirement`，不同时铺开五类 Loop。
- 复用现有 `LoopRun / LoopRound / LoopPolicyProfile.max_rounds=2`、`needs_review` 与原 freeze writer。
- 新增一个 Requirement 命名空间下的只读 review 输入入口；输出当前轮、canonical requirement projection、输入摘要、风险信号、一个阶段主角色和至多一个交叉风险角色。
- active agent 必须按返回角色在独立只读上下文中执行评审，并生成一个临时 `RequirementReviewExecution` 文件；finding 交回原 requirement writer 修订，该文件不进入 Loop artifact 或 Git。
- 新 loop 以现有 `RequirementIntake.review_required=true` 标记新合同；旧 artifact 缺字段时按 `false` 读取，继续原 freeze 行为并明确提示 legacy 路径，不做批量迁移。
- 只有 round 1 初始 `needs_user` 的正常澄清不消耗轮次；`needs_review` 后只有携带当前 completed review execution 的实质修订才能从 round 1 进入 round 2。round 2 后第三个实质版本返回现有 command `blocked`，不持久化 `needs_user`、新 intake 或 round 3，因而不能伪装成免 execution 的澄清。
- freeze 必须同时校验当前输入摘要、完整角色集合、执行成功和无 `blocker/required` finding；摘要本身不能冒充“评审已通过”。
- 用路由合同测试与三个盲测价值回放分别验证机制和 ROI；至少包含一个无预埋缺口的负向对照。

### 1.2 本次不覆盖

- 不实现 Design Contract、Implementation、Frontend Evidence 或 Local PR Review 的动态专家。
- 不新增第二套状态机、review session、Finding Ledger、certificate、attestation、quorum、lease、score/search/learning、provider registry、optimizer 或阻断式 Lean。
- 不在 review 内核中写 Loop 状态、自动修改需求、自动 freeze、提交、push、创建 PR 或发布。
- 不持久化专家身份、完整 finding 历史或独立“PASS 凭证”；只允许在现有 `RequirementFreeze` 中记录最终摘要、实际角色和审查时间。
- 不复制参赛版的通用五阶段 review kernel/mapping；其两份主要文件已超过 1400 行，完整通用审查面更大，参赛版只作为行为证据。
- 不启动 R09 完整 12 路发布矩阵；它继续作为安装/分发变更触发的非阻塞 backlog。
- 不重新开启 Lean 减重路线或 RC-08。

## 2. 现状证据

| 证据 | 当前事实 | 本工作项结论 |
|---|---|---|
| `src/ai_sdlc/core/requirement_loop.py` | 有 `RequirementIntake`、`LoopRun/LoopRound`、`needs_review` 和显式 freeze；freeze 不接收 reviewed-input identity | 缺口位于 review 输入与 freeze 漂移保护之间，不需要替换原 writer |
| `src/ai_sdlc/core/loop_models.py` | 已有 `LoopRound` 与默认 `max_rounds=2` | 轮次与终止语义可复用，不新增 review run/state |
| `src/ai_sdlc/cli/loop_cmd.py` | Requirement 只有 `start/status/freeze` | 最小公共入口应放在现有 Requirement 命名空间，而非新增顶级平台 |
| 主仓路线图 P4 | 要求阶段 primary、按风险可选一个 cross-risk、最多一次复审、输入变化使旧结论失效 | 本薄片严格取 Requirement 子集 |
| 参赛版稳定基线 `b6addbab` | 已证明动态角色与 digest-bound close 可运行，但通用 kernel 与五阶段 mapper 合计约 1400 行 | 复用行为，不复制体量或已退役治理机制 |

## 3. 用户场景与测试

### 用户故事 US-228-1：先得到独立的需求质量审查（P0）

作为使用 AI-SDLC 澄清需求的用户，我希望 freeze 前至少有一个与 writer 上下文隔离的 Requirement 主专家检查目标、边界和验收可判定性，以减少“需求看似完整但无法验收”的遗漏。

**独立测试**：启动一个含验收标准的 requirement loop，执行 review 输入命令，确认只读输出始终包含一个 Requirement 主角色、canonical projection、当前轮和 64 位摘要，且仓库状态前后不变；缺少完整 execution 时 freeze 必须失败。

**验收场景**：

1. **Given** 当前需求已进入 `needs_review`，**When** 构建 review 输入，**Then** 返回恰好一个阶段主角色、可供独立 reviewer 直接读取的 canonical projection 与关注点。
2. **Given** 没有明确交叉风险，**When** 选择角色，**Then** 不为凑数量生成第二个角色。
3. **Given** 调用方只取得 digest 或伪造不完整角色结果，**When** 请求 freeze，**Then** 关闭失败且原状态不变。

### 用户故事 US-228-2：按明确风险增加一个反方专家（P0）

作为处理权限、隐私、数据或兼容需求的用户，我希望框架只在文本中存在可解释风险证据时增加一个不重复的 cross-risk 专家，以提高发现密度而不启动专家委员会。

**独立测试**：分别输入安全/权限和数据迁移/兼容需求，确认每次最多两个角色，第二角色与风险信号及理由可追溯；多种信号同时存在时按冻结优先级只选一个。该测试只证明路由合同，不计入 ROI。

**验收场景**：

1. **Given** 需求明确涉及鉴权或隐私，**When** 构建 review 输入，**Then** 返回主角色加一个安全/隐私 cross-risk 角色。
2. **Given** 文本同时命中多个风险族，**When** 选择角色，**Then** 使用固定优先级选一个交叉角色，不扩展第三角色。

### 用户故事 US-228-3：修改后旧评审不能被复用（P0）

作为维护者，我希望需求或验收标准变化后旧 review 摘要立即失效，并且最多只允许一次实质修订，以避免 stale PASS 或无限复审。

**独立测试**：对同一 loop 完成 round-1 execution，用它驱动一次实质修订后再尝试 freeze，旧 execution 必须失败并给出重新 review 的下一步；当前 clean execution 可 freeze；第三个实质版本不能自动创建第三轮。

**验收场景**：

1. **Given** round 1 已产生 review 摘要，**When** writer 形成 round 2，**Then** 旧摘要不能关闭 round 2。
2. **Given** round 2 已存在，**When** 再提交实质不同输入，**Then** 命令返回 `blocked`/No-Go，已持久化的 round-2 intake/status 保持不变，不能生成 round 3 或借 `needs_user` 澄清路径覆盖 round 2。
3. **Given** 相同输入被幂等重跑，**When** 比较轮次，**Then** 不增加 `LoopRound`。

### 用户故事 US-228-4：用盲测而非预设 finding 证明价值（P0）

作为决定是否继续投资 P4 的 Sponsor，我希望路由正确性与专家增量价值分开验收，避免用预埋关键词和缺口制造“成功”。

**独立测试**：先冻结三个 baseline writer 输出，再隐藏 seed/预期结果交给专家；独立裁决者依据来源真值判断 finding 是否为 baseline 未覆盖、事实正确、影响验收或风险边界且可执行。三例至少包含一个 clean 负向对照。

**验收场景**：

1. **Given** 专家不知道缺口标签和预期答案，**When** 完成三个回放，**Then** 至少两个样例各有一个经裁决的有效增量 finding。
2. **Given** clean 负向对照，**When** 专家审查，**Then** 不产生错误的 `blocker/required`；三个样例合计错误 actionable finding 为 0。

## 4. 功能需求

- **FR-228-001**：必须新增 Requirement 专属只读 review 输入入口；不得新建顶级 review 平台或通用五阶段状态机。
- **FR-228-002**：review 输入必须绑定 loop id、当前 round 和规范化后的 `RequirementIntake` 实质内容，并把同一 canonical projection 直接返回给 reviewer；artifact 路径只作信息引用，不能成为摘要外的第二内容源。
- **FR-228-003**：角色选择必须始终产生一个 Requirement 主角色；只有明确风险信号存在时增加至多一个不重复 cross-risk 角色，并返回选择理由。每个 `RequirementReviewRole` 必须直接带稳定 canonical `role_id`；execution 只能用该字段匹配精确唯一角色集合，不能从展示名推导。
- **FR-228-004**：风险映射必须是小型、确定性、可测试的 heuristic 白名单；使用 NFKC + casefold、英文 token 边界和中文完整短语；多信号只按固定优先级选择一个，不宣称风险覆盖，不做评分、搜索、学习或 provider/model 路由。
- **FR-228-005**：review 命令必须只读；调用前后不得新增或修改 Loop artifact、指针、源码、Git index 或工作树文件。
- **FR-228-006**：新合同的 `freeze` 必须消费临时 `RequirementReviewExecution`；CLI 须先定位项目并通过纯读取 preflight，重建 current projection，校验 digest/round、角色集合完整且唯一、全部执行成功、无 `blocker/required` finding，只有通过后才可调用 writer adapter；最终 requirement 写入前必须再次校验。缺失、失败、格式错误或漂移均 fail closed，且被拒绝时整个工作树不得变化。
- **FR-228-007**：原 `freeze` writer 和用户 close authority 保持唯一；reviewer 不能写需求、推进状态或调用 close。
- **FR-228-008**：同一 loop 的评审后实质版本必须使用现有 `LoopRound` 记录，最多两轮；只有 round 1 且 durable status 为初始 `needs_user` 的正常澄清和幂等重跑不增加轮次；`needs_review` 后须通过现有 `requirement start --loop-id <id> ... --review-result-file <path>` 显式携带当前 completed execution，只有该路径可进入 round 2。`start` 允许该 execution 含 `blocker/required` finding，因为它们正是修订依据。round 2 后第三个实质版本返回现有 `RequirementCommandStatus.BLOCKED`，不得持久化 `needs_user`、替换 intake/status 或创建 round 3。missing、malformed、stale、failed、角色不完整/重复/未知的执行文件必须在 writer adapter 之前拒绝。
- **FR-228-009**：实现不得新增持久化 review/finding/pass artifact、外部依赖、workflow、required check、网络 API 或全局配置。临时 execution 文件必须为普通非 symlink 文件并设大小上限，消费后不由框架复制或保留。
- **FR-228-010**：普通输出与 JSON 输出都必须明确显示 canonical projection、角色上限、当前摘要、execution schema、失败原因和下一步；共享 pipeline rule 与用户文档必须给出 review→独立只读角色→execution→必要时修订→freeze 的最短路径。
- **FR-228-011**：新建 requirement 默认 `review_required=true`；旧 intake 缺字段时兼容为 `false`，未关闭旧 loop 可继续 `freeze --yes` 并收到 legacy warning，已关闭旧 loop 继续无摘要幂等返回。不得批量迁移旧 artifact。
- **FR-228-012**：从 formal merge base 到候选 HEAD，`src/ai_sdlc/**` gross added lines 大于 600 即 No-Go；行为代码只允许一个新 core 模块及两个现有接线文件，兼容调用方只允许冻结 allowlist，任何 allowlist 外产品源码改动即 No-Go。

## 5. 关键实体

- **RequirementReviewInput（瞬时返回值）**：`loop_id`、`round_number`、`input_digest`、canonical `requirement` projection、信息性 `artifact_paths`、`risk_signals`、`roles`；不落盘，不含 close verdict。
- **RequirementReviewRole（瞬时返回值）**：稳定 canonical `role_id`、展示 `name`、`focus`、`reason`、`kind=primary|cross-risk`；列表长度为 1–2。`role_id` 直接出现在 review JSON/schema 中，与 execution 一一对应。
- **RequirementReviewExecution（临时调用输入）**：绑定 digest/round，且为每个必需 role 提供 `completed|failed` 与结构化 findings；只作为本次 start/freeze 的输入，不成为持久 authority。
- **LoopRun / LoopRound（复用）**：保存原 requirement 的最多两个实质版本；不新增 review 状态。
- **RequirementIntake / RequirementFreeze（复用并最小扩展）**：前者用默认兼容字段区分新旧合同；后者只记录最终 digest、实际角色和审查时间。它不是证书或可跨输入复用的授权。

## 6. 方案比较与 Admission

### 方案 A：Requirement 专属薄片（推荐）

在现有 Requirement namespace 增加一个轻量 review 输入构建器和严格的临时 execution schema；最小修改 start 的轮次复用和 freeze 的 execution 校验。优点是直接覆盖用户路径、改动集中、可以删除；限制是它提供结构化流程证据而非密码学身份或远端证明，且暂不共享给其余四类 Loop。

### 方案 B：复制参赛版通用 review kernel（No-Go）

可以最快获得五阶段能力，但会一次引入远超本阶段验证需要的通用路径、安全读取、映射和兼容面，直接违背先证明 Requirement ROI 的边界。

### 方案 C：只写 agent 提示、不改 freeze（No-Go）

代码最少，但旧摘要可以在输入变化后继续被口头当作 PASS，无法验证专家实际执行、stale review 保护或 LoopRound 上限。

**Admission 结论**：方案 A 为 `implement`。用户已授权按对抗结论继续，但必须先完成本 formal 的双专家一致 PASS；若评审不能在最多两轮内收敛，转 No-Go，不进入实现。

## 7. ROI 与实现边界

1. **用户可观察收益**：freeze 前获得独立需求审查；权限/数据类需求有针对性的第二视角；修改后不会误用旧评审。
2. **现状证据**：主仓 `needs_review` 可直接通过 `freeze --yes` 关闭；没有 review 入口、角色选择或摘要校验。参赛版证明能力可行，但实现面过大。
3. **最小方案**：Requirement 专属瞬时 input/execution 模型、现有 CLI 子命令、start/freeze 的最小接线及定向测试；不先做通用抽象。CLI 返回平台无关的 agent 指令，共享 pipeline rule 承接宿主自动执行，不分别维护 adapter 逻辑。
4. **总投入**：预计 1–2 人日；`src/ai_sdlc/**` gross additions 上限 600 行；测试和三个盲测回放另计但必须逐条映射验收合同。
5. **长期维护**：只维护一个确定性风险表和一组 input/execution 合同；Phase A-1 No-Go 时整体删除 review 入口并回退新合同要求，原 Requirement Loop 可恢复。
6. **退出条件**：三个盲测回放未达到 SC-228-007、角色路由无法解释、实现需要新状态/ledger/平台，或实现体量越过 FR-228-012 时，结论为 No-Go；候选 runtime 不得合并，不得以“已经投入”为由扩展。

## 8. 成功标准

- **SC-228-001**：无风险需求返回 1 个角色；安全/权限或数据/兼容需求返回 2 个角色；任何输入都不超过 2 个；相同角色始终返回同一 canonical `role_id`，execution 不依赖展示名匹配。
- **SC-228-002**：review 命令前后 tracked/untracked 文件集合与内容一致，且不写任何 review artifact；临时 execution 由宿主产生，框架不复制。
- **SC-228-003**：只提供 digest、missing/malformed/stale/failed/incomplete/duplicate/unknown role、输入或 round 漂移均不能 start 修订或 freeze；当前完整 completed execution（可含 actionable finding）可以驱动 round 2 修订，只有当前 clean execution + `--yes` 才能 freeze。每个被拒绝的 execution 用整个工作树文件集合与逐文件内容哈希证明调用前后完全不变，尤其不得先刷新 adapter metadata。
- **SC-228-004**：仅初始 round-1 `needs_user` 澄清留在 round 1；第一轮 execution 后修订进入 round 2；幂等重跑不增加；第三个实质版本 command blocked 且不写任何 intake/status/round 变化，重复调用仍 blocked；freeze 关闭实际 current round。
- **SC-228-005**：无验收标准、非法 loop id、损坏 artifact、新合同重复 freeze、legacy open/closed freeze 和显式用户确认行为均通过回归。
- **SC-228-006**：`src/ai_sdlc/**` gross additions 不超过 600 行、产品源码不越过 allowlist、不新增依赖/状态机/持久化 review artifact/workflow，constraints 与全量测试通过。
- **SC-228-007**：三次盲测价值回放均归档 baseline、专家原始输出、独立裁决、修订和终态；至少两个样例各有一个有效增量 finding，clean 对照无错误 actionable finding，三例合计错误 actionable finding 为 0；否则 runtime 候选不合并。
- **SC-228-008**：formal 与实现各最多一轮对抗评审加一轮整改复审；实现只允许一个 implementation PR，不创建为收口而收口的第二实现 PR。
