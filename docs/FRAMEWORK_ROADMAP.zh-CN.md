# AI-SDLC 主线 ROI 路线图

> **文档职责**：这是 `v0.9.8` 之后产品优化、验证观察与延后候选的唯一人机共读路线图。它保存“接下来为什么做、按什么顺序做、做到什么程度停止”，避免新会话重新规划。
>
> **授权边界**：路线图不是 execute 授权，也不是第二套 Program Truth。只有当前优先项被建立为独立 work item，完成 formal review，并获得用户明确批准后，才允许进入实现。

## 1. 冻结基线与适用范围

- 路线图冻结日期：`2026-08-27`。
- 主仓远端定位符：`https://github.com/sinclairpan-git/Ai_AutoSDLC.git`；在主仓 checkout 中默认远端名为 `origin`，冻结基线为 `origin/main@4f3e55c300dab20fb4fea93818d79394a927f77e`，已发布 `v0.9.8`。
- 参赛版远端定位符：`https://github.com/SinclairPan/Ai_AutoSDLC.git`；在参赛版 checkout 中默认远端名为 `origin`，冻结参考基线为 `origin/main@b6addbab22ab069ea1d6d7306fe1c676bd056333`。
- 比较范围只包含两个仓库的远端 `main`；产品站、比赛材料、本地分支和未合并 worktree 均不作为路线真值。
- 主仓不被参赛版覆盖，不 cherry-pick 参赛版实现。只借鉴经过验证的行为边界、失败经验和投入产出结论，由主仓按自身架构重新实现。
- 若远端主线已经变化，恢复者先核对相关能力是否已落地；只有真实证据改变价值、投入或依赖时才修订本路线图，不因会话切换重新从零规划。

## 2. 决策原则

1. **ROI 优先**：优先做用户价值高、投入可控、能降低后续开发成本的事项。
2. **特性主导、局部收敛**：不启动独立全仓减重；正常特性经过旧代码时允许做与该特性直接相关的局部收敛。
3. **信号不等于裁决**：文件行数、函数行数、支撑/核心比例、调用方数量只能触发复核，不能单独成为 blocker。
4. **保留模型自主性**：模型可以根据安全、兼容、恢复、迁移、跨平台和外部协议证据保留较大的必要实现，但必须说明价值、替代方案和退出条件。
5. **有界评审**：一个候选默认最多一个 work item、一个实现 PR 和两轮修复/复审；超过边界必须停到 `needs_user` 或 No-Go。Sponsor 若基于 ROI 批准终局动作，必须同时冻结唯一改动、投入上限和终止结果；随后只验证稳定 finding 及其回归面，不重新开启无限问题空间。
6. **不复制治理**：优先复用现有 Loop、Local PR Review、handoff 和 Program Truth，不新建平行状态机、ledger、certificate、waiver 或 retry engine。

## 3. 总体队列

估算口径：一名熟悉仓库的工程师配合 AI；投入包含 formal、实现、测试、CI、对抗评审、合并和记录收口。ROI 指数只用于相对排序。

| 顺序 | 事项 | 状态 | 用户/工程价值 | 预计投入 | ROI | 前置条件 |
|---|---|---|---:|---:|---:|---|
| P0 | 主线真值复位 + 轻量 ROI 合同 | **已完成** | 9.5/10 | 实际已投入 | 4.5（原估） | 无 |
| P1 | Diff-local Lean Advisory | **No-Go 已关闭（未合并）** | 8.0/10 | 实际：1 个 WI + 2 轮评审 | No-Go（及时止损） | P0 与 v0.9.8 已完成 |
| P2 | 普通用户单入口收敛 | **已完成（WI220）** | 9.0/10 | 实际已投入 | 1.5（原估） | P1 已有证据 No-Go |
| D2 | 历史 release-target provenance 恢复 | **WI221 admission No-Go；待用户决策** | 7.5/10 | 审计 <0.5 人日；补缺粗估 8–13 人日 | 0.6–0.9 | v0.9.9 的硬前置 |
| P3 | 跨平台首次用户 12 路完整闭环 | **WI224 实现已合并；R02 等待自然 release receipt** | 9.5/10 | R02 实际完成 bounded execute；完整实现仍估 6–10 人日 | 先证一条路线 | P2 默认入口稳定 |
| P4 | 五类 Loop 有界动态专家 | **条件候选** | 10/10 | 10–15 人日 | 0.6 | P1–P3 的真实收益支持继续投资 |

此外保留两个非产品队列：`O1` 是发布后真实项目观察；`D1` 是无当前实现授权的延后候选。它们不得抢占 P1–P4 的正常产品顺序。

## 4. P0：主线真值复位 + 轻量 ROI 合同

### 4.1 状态

**完成，不重新打开。** WI219 已经由 PR #175、#176、#177 合入主线，并由 PR #178 发布为 `v0.9.8`。

### 4.2 已交付行为

- status、readiness、execute authorization 和 resume 统一使用 linked-first work item 身份。
- stale local main、formal-only 变更和 squash merge 后的历史归因不再把主线下一步错误指回 execute。
- 两个 canonical spec 模板都要求在实施前回答用户价值、当前证据、最小方案、替代方案、总投入、范围、退出条件和决策。
- 小修复允许 `not-applicable`；ROI 提示没有新增评分系统、CLI 命令、持久化状态或 blocker。

### 4.3 完成证据

- 发布说明：`docs/releases/v0.9.8.md`。
- 正式合同：`specs/219-mainline-truth-roi-contract/`。
- 发布 tag 与远端主线：`4f3e55c300dab20fb4fea93818d79394a927f77e`。

### 4.4 后续边界

- `O1` 的真实项目观察可以发现新缺陷，但不得把 P0 整体重新包装成长期维护专项。
- 若出现可复现问题，只建立聚焦缺陷 work item；不重启 WI219，不扩大成真值平台重构。

## 5. P1：Diff-local Lean Advisory

**状态：已按有证据 No-Go 关闭，主线未合并任何 P1 实现。** 候选在 1 个 formal work item、实现和两轮独立评审预算内完成验证；focused 38、provider/service 122、full 3402（另 3 skipped）、Ruff 与 constraints 均通过，但 exact-head 独立评审及真实 `local-unstaged` ReviewPack 复现了运行时合同缺陷：当 Git 启用 `diff.mnemonicPrefix=true` 时，ReviewPack 仍返回 `ready`，Lean advisory 却静默缺失。

继续修复需要扩大到已冻结范围之外的 runtime prefix/parser/Git diff 合同，当前新增价值不足以支撑继续投入，因此触发有界评审硬停止。候选分支未 push、未创建 PR、未合并；主线继续保留 WI219 的轻量 ROI prompt，不保留 collector、schema、状态或其他治理膨胀。只有新的 Formal 明确批准 runtime prefix contract 时才可重新立项；本节其余内容保留为冻结方案与 No-Go 审计依据，不再作为当前待办。

### 5.1 目标与价值

在实现和修复过程中，以当前 diff 为输入，向模型提供少量高信号的代码膨胀提示，让模型在提交前重新比较核心价值与支撑成本。P1 只帮助判断，不代替模型判断，也不改变 close 权力。

参赛版值得借鉴的边界是：单次扫描、失败可容忍、只返回建议，没有 status、verdict、exception、waiver、receipt、history 或 policy lifecycle。参赛版的固定阈值、模块结构和扫描实现不是主仓合同。

### 5.2 冻结范围

- 输入只来自当前 base/head 或 PR pack 已经冻结的 changed paths，不扫描整个仓库，也不把宽泛 declared scope 当作实际变更。
- 只读取仓库内普通文件；外部 symlink、不可读文件、二进制文件必须安全跳过。
- 默认最多展示 3 条按风险和可行动性排序的建议；其余低优先信号只汇总数量，避免 advisory 自身膨胀。
- 可用信号：
  - 新增公共 API、命令、依赖或持久化状态；
  - 同一 diff 内的明显重复、包装层堆叠、耦合或职责混杂；
  - 测试/fixture/治理支撑远大于核心行为，且没有安全、兼容、迁移或回归证据说明必要性；
  - 单调用方公共抽象、配置转移复杂度或仅改名的中间层；
  - 文件/函数规模显著增长，但数值只能作为要求说明的信号。
- 输出只进入现有 Implementation Loop 或 Local PR Review 的展示面；不新增命令、schema、状态、ledger、parser、waiver、receipt、certificate 或 blocker。
- Advisory 不得改变 Loop status、next action、close、merge 或 release 判定。

### 5.3 可直接派生的实施任务

- [ ] 以 `origin/main` 重新核对 Implementation Loop、Local PR Review 和 changed-path 现有接口，选定唯一接入面。
- [ ] 用三个方案比较后冻结 formal：纯 prompt 提示、确定性 diff collector、完整 Lean engine；默认推荐“最小确定性 collector + 现有 review 展示”。
- [ ] 先写 RED：只检查 changed paths、跳过仓库外 symlink/二进制/缺失文件、输出有界、失败不阻断。
- [ ] 先写 RED：行数或单调用方信号不能改变 status/close；安全与兼容支撑可以保留并给出解释。
- [ ] 实现最小 collector；不复制参赛版 `slimming_advice.py`，不新增 Markdown parser 或策略生命周期。
- [ ] 在一个现有报告展示面输出最多 3 条建议和低优先信号计数，不产生新的持久化工件类型。
- [ ] 用至少三类历史 diff 做噪声校准：小型缺陷修复、WI219 式支撑膨胀候选、包含必要兼容/跨平台证据的较大变更。
- [ ] 完成 focused/full tests、Ruff、constraints、diff-check、独立只读评审、PR/Codex review 和合并后验证。

### 5.4 成功标准

- 小型直接修复没有无意义建议。
- 已知膨胀候选能稳定出现至少一条可执行建议。
- 必要的安全、兼容、迁移和跨平台支撑不会仅因规模被判错。
- 输出确定、失败可容忍、最多 3 条，并且不改变任何生命周期或授权结果。
- 产品实现、测试和接入仍在 2–3 人日边界内；没有出现新的治理子系统。

### 5.5 停止与回退

出现以下任一条件即 No-Go 或回到用户：

- 必须新增状态机、ledger、waiver、certificate、receipt、长期 policy lifecycle 或新命令；
- 必须扫描全仓或解析自由格式 Markdown 才能工作；
- 两轮校准后仍对小修复产生高噪声，或无法识别已知膨胀候选；
- Advisory 开始参与 close/merge/release 阻断；
- 预计总投入超过 3 人日且没有新增可验证价值。

回退方式：原子移除 collector 与展示接入，保留 WI219 的模板 ROI 提示。

## 6. P2：普通用户单入口收敛

### 6.1 目标与价值

让普通用户和 AI 通过一个默认入口得到当前结果与下一步，不再先理解大量内部命令组。高级能力继续兼容，但退出默认认知路径。

冻结基线上的差距信号：主仓注册 18 个顶层命令组，`src/ai_sdlc/cli/run_cmd.py` 约 728 行；参赛版远端主线为 7 个命令组、`run_cmd.py` 约 136 行。这些数字只说明入口复杂度差距，不是删减目标。

### 6.2 冻结范围

- `ai-sdlc init .` 仍是普通用户初始化入口。
- `ai-sdlc run` 默认输出：当前 Loop、Result、Next、Blockers、最多两段 Applicable Rules。
- `status` 默认只展示普通用户需要的信息；详细诊断留在现有 `--details` / `--json` 或高级命令。
- Program、Telemetry、Provenance、AgentOps 等能力不一次性删除；优先从默认 help 隐藏、分组或迁入 advanced 帮助，并保留兼容调用。
- 只在本特性经过的 `run`/status 路径局部收敛重复逻辑，不重构无关 ProgramService，不追逐文件行数。

### 6.3 可直接派生的实施任务

- [x] 盘点 18 个顶层命令组的普通用户使用频率、文档入口、脚本调用和兼容风险。
- [x] 冻结“小白默认路径”和“高级自定义路径”的命令/帮助矩阵。
- [x] 为 `run` 的五项默认输出写 characterization 和失败路径 RED。
- [x] 为 Applicable Rules 写有界规则：按当前任务选择，最多两段，不倾倒整份规则文本。
- [x] 收敛 `status` 默认终端输出，同时保持 JSON 机器合同兼容。
- [x] 对高级命令采用 hide/group/advanced help；不得直接删除已有命令或改变脚本 exit contract。
- [x] 对 `run_cmd.py` 只做伴随本特性的职责提取；每个抽取必须有复用或可测试边界，不做纯机械拆文件。
- [ ] 运行普通新用户 E2E、存量高级用户兼容 E2E、文档一致性、全量测试和跨平台 CI。

### 6.4 成功标准

- 新用户只通过 `init` 和 `run` 就能得到可信 Result/Next，不需要手动运行诊断命令。
- 默认输出不暴露内部状态噪声；阻断原因和下一条命令明确。
- 高级命令仍可调用，JSON/exit code 和历史自动化保持兼容。
- 用户指南、adapter guidance、CLI help 和实际输出口径一致。

### 6.5 停止与回退

- 若需要删除高级能力、重写 ProgramService 或破坏机器合同，停止并拆分。
- 若默认输出需要新增第二套状态聚合器，停止并复用现有 truth/status 数据。
- 若范围超过 6 人日，先交付最小 `run` 输出闭环，其余入口隐藏另行评估。

## 7. P3：跨平台首次用户 12 路完整闭环

**状态：WI222 P3-A formal 与 WI224 原生发布证明实现均已合并；R02 等待未来自然 `release.published` receipt。** 基于
WI222 的严格证据合同，当前仍为
`0/12 proven、12/12 partial、0/12 missing`：指南覆盖了全部组合，三平台安装/发布 smoke 提供了共享基础，
但没有任何一路形成同时包含正式资产完整性、`init/adopt`、`Result / Next`、主动恢复和版本绑定的自包含证据链。
WI223 自定义 sidecar 方向已 No-Go 且未合并；exact remote spike 已证明 GitHub 原生 Artifact Attestation 能绑定
repo、signer workflow、tag ref/commit 与 build trigger。WI224 只允许修改 Release Build 和现有 Windows R02 workflow，
不启动 v0.9.9，也不在真实自然 release receipt 出现前提升路线状态。

### 7.1 目标与价值

把“发布资产存在”升级为“新用户在干净环境中能完成安装、初始化/接入、得到成功证据，并能就地恢复”。

### 7.2 十二条路线

每个平台覆盖四种路线，共 12 条：

| 平台 | 空项目在线 | 已有项目在线 | 空项目离线 | 已有项目离线 |
|---|---|---|---|---|
| Windows AMD64 | 路线 1 | 路线 2 | 路线 3 | 路线 4 |
| macOS Apple Silicon（arm64） | 路线 5 | 路线 6 | 路线 7 | 路线 8 |
| Linux AMD64 | 路线 9 | 路线 10 | 路线 11 | 路线 12 |

每条路线都必须自包含：环境准备、获取正式版本或平台资产、版本与 SHA256（或在线渠道的等价完整性证据）验证、安装/升级、`init` 或 adopt、正常 Result/Next、成功证据、失败后的本地恢复、产物/版本绑定。不得把资产获取或完整性验证留给路线外的共享说明。

### 7.3 可直接派生的实施任务

- [x] WI222 冻结 12 路证据合同，定义每条路线的准备、命令、证据、恢复和版本绑定字段。
- [x] WI222 复用已有 Windows E2E、离线安装和三平台 release smoke 完成差距映射，不重写安装系统。
- [x] WI224 前置 spike 证明原生 Artifact Attestation 可替代自定义 sidecar，PR #191 已止损关闭。
- [x] WI224 只为 Release Build producer 与 R02 natural-release consumer 增加签发、强验证、恢复和临时 receipt；实现已合并，尚未发生自然 release receipt。
- [ ] 抽取跨平台共享步骤，使用矩阵参数化；禁止复制一份超过核心安装逻辑数倍的 POSIX workflow。
- [ ] 补齐 macOS/Linux 完整 user-guide E2E、在线 bootstrap、系统 Python、下载工具和 glibc 等真实兼容边界。
- [ ] 在干净 Windows/macOS/Linux 环境执行 12 条路线；模拟测试或文档 lint 不能替代真实 E2E。
- [ ] 将指南、安装器、release assets、SHA256 和恢复路径加入同一发布一致性门禁。

### 7.4 成功标准

- 12 条路线全部具有真实 clean-environment E2E 证据。
- 在线/离线产物绑定同一正式版本和校验值。
- 任一路线失败时，用户无需重装 Python、手工建 venv 或猜测 PATH；CLI/指南给出就地恢复。
- 发布门在缺少任一路线证据时明确 No-Go。

### 7.5 停止与回退

- 若矩阵实现开始大量复制，先抽取共享步骤再继续。
- 若平台环境暂时不可获得，状态必须是 `needs_user`/No-Go，不得用模拟结果宣称完成。
- 不把内部补丁发版机械升级为必须重跑全部 12 路；仅在影响安装、初始化、adopt、恢复或分发合同时触发完整矩阵。

## 8. P4：五类 Loop 有界动态专家

### 8.1 目标与价值

根据当前工作项风险动态选择少量独立只读专家，在 Requirement、Design Contract、Implementation、Frontend Evidence 和 Local PR Review 阶段发现单一模型容易遗漏的问题，同时保持输入绑定、有限轮次和用户决策权。

### 8.2 分阶段范围

**Phase A：先证明纵向闭环**

- Requirement Loop；
- Design Contract Loop；
- Implementation Loop。

**Phase B：只有 Phase A 的投入产出成立后再扩展**

- Frontend Evidence Loop；
- Local PR Review。

### 8.3 冻结行为合同

- 复用现有 LoopRun/LoopRound、状态、artifact 和 close 语义，不建立第二套 stage-review 状态机。
- 每个 Loop 必须选择一个与当前阶段语义匹配的 primary 只读专家；只有当前风险证据需要时，才额外选择至多一个不重复的 cross-risk 只读专家。最多一次修复后的复审。
- 输入绑定 work item、tasks/acceptance、declared scope、base/head、changed files、diff hash、verification evidence 和前轮结论。
- 输入或 diff 变化立即使旧 PASS 失效；复审必须重新绑定当前 identity。
- Reviewer 不能写代码、不能 close、不能 merge；Implementation Agent 才能修改代码。
- 两轮后仍有有效 Critical/Important，进入 `needs_user` 或 No-Go，不自动开启第三轮。
- 不建立长期专家身份、review session 平台、Finding Ledger、评分系统、证书体系或离线优化控制器。

### 8.4 可直接派生的实施任务

- [ ] 重新核对主仓五类 Loop 现状和参赛版远端稳定行为，只提取缺口，不复制 stage-review 实现。
- [ ] 为 Phase A 冻结统一 Candidate/Input Digest/Reviewer Result 的最小合同，优先复用现有模型。
- [ ] 定义阶段到 primary 角色、风险证据到可选 cross-risk 角色的有界映射；始终保留一个阶段 primary，不因缺少额外风险信号降为零 reviewer，也不生成无限角色。
- [ ] 实现 Requirement 单 Loop 纵向薄片并验证输入变化使旧结果失效。
- [ ] 证明投入产出后扩展 Design Contract、Implementation；每次扩展独立 Go/No-Go。
- [ ] Phase A 在真实项目中证明缺陷拦截收益后，才评估 Frontend Evidence 与 Local PR Review。
- [ ] 完成隔离性、只读性、两轮上限、同输入复审、close authority 和 crash/recovery 回归。

### 8.5 成功标准

- Phase A 在不新增平行状态机的前提下，对至少三类真实工作项产生可复核的增量发现。
- 同一 frozen input 的独立评审可重复，diff 变化会稳定失效旧结论。
- 两轮上限、Reviewer 只读和 close authority 均由测试证明。
- 评审产品代码、测试和治理支撑没有再次远大于被保护的核心行为。

### 8.6 停止与回退

- 需要一次铺满五类 Loop、长期 session、ledger、certificate、评分或第二套状态机时停止。
- Phase A 没有稳定增量发现，或评审成本超过其拦截价值时，不进入 Phase B。
- 两轮无法收敛时返回用户，不追加第三轮实现。

## 9. O1：v0.9.8 发布后真实项目观察

### 9.1 状态

**观察项，不阻断 P1。** 目标是在 3–5 个真实项目中验证 WI219 的主线真值修复，而不是继续打磨 WI219。

### 9.2 观察矩阵

- stale local main、remote main 更新；
- formal-only 候选；
- linked work item 与历史 checkpoint 不一致；
- squash merge 后实现已包含于主线；
- linked 路径缺失、损坏或 symlink 边界。

### 9.3 记录指标与退出条件

- 记录误报、漏报、错误 Next、人工干预和恢复是否正确。
- 3–5 个项目完成且无高价值缺陷时关闭观察项。
- 若发现可复现缺陷，只建立聚焦缺陷 work item；不得把观察结果直接升级为新平台或重新打开整个 P0。

## 10. D1：active-WI path validation centralization

### 10.1 状态

**延后，未批准实现。** 该候选来自 WI219 的 C2，当前只有“多个 active-WI 消费面可能重复路径校验”的结构信号，没有足够用户价值证据。

### 10.2 重新评估触发器

只有出现以下任一真实证据才重新评估：

- 两个或以上 active-WI 消费面出现同族路径安全/一致性缺陷；
- 重复路径判定已经造成不同 status、execute、resume 或 readiness 结果；
- 正常特性经过这些消费面时，可以用更小共享边界同时减少代码和回归风险。

### 10.3 约束

- 不为代码整齐单独立项；不在没有缺陷证据时抽象 helper。
- 若获批，只统一已有纯路径判定；不修改 checkpoint schema、work item identity、状态机或用户可见合同。
- 预计超过 1–2 人日、需要新公共 API 或迁移时 No-Go。

### 10.4 D2：历史 release-target provenance 回填

**已进入 WI221；provenance-only admission 为 No-Go，等待用户决定是否补真实能力。** 在真实
`origin/main@263abb3d0171a58762d382e73db9a9a692707268` 刷新 Program Truth 时，前端 14 个、Adapter 2 个历史 truth refs 仍被判定为
`formal_freeze_only`。旧 ready snapshot 生成于未进入主线的 squash 前 release branch，其发布改动被误归为这些
历史 work item 的执行证据；因此当前必须保留真实 `blocked`，不得删 gate 换取假 ready。

- 价值：7.5/10；审计投入小于 0.5 人日；若补齐真实能力，当前粗估 8–13 人日、ROI 约 0.6–0.9。价值集中在恢复未来发布可信度，不新增用户特性。
- 触发器：准备下一次依赖 Program Truth release target 的发布，或有独立证据能把这些 work item 与真实主线实现提交、
  路径和批次一一绑定。
- 实施边界：建立独立 formal work item，逐项验证实际 implementation carrier；只回填可证明的 provenance，无法证明的
  项保持 blocker。不得修改历史叙事伪造执行，不得让无关提交充当证据。
- 停止条件：需要放宽 `formal_freeze_only`、删除 WI200 明确冻结的 121/122/159/200 truth refs、修改 3 个以上真值子系统，
  或两轮整改后仍不能形成确定归因时 No-Go，返回用户决定是否接受 blocked release target。
- 2026-08-30 WI221 admission 结果：11/16 可绑定完整主线载体；`098` 缺少五态 posture detector / evidence precedence /
  sidecar recommendation，`099` 未消费 posture gate，`100/101` 缺少完整的 ledger whole-plan rollback 与同 action retry，
  `095` 因继承这些子合同只能部分归因。不得批量改历史 log 伪造 16/16。
- 当前推荐保持 release target blocked。若业务仍要求解除发布门，需由用户另行批准一个重新定界的多能力实现批次；粗估
  8–13 人日，已超过 WI221 的 provenance-only 边界。在新范围获批前不进入 runtime execute，也不启动 v0.9.9 版本变更。

## 11. 明确 No-Go 清单

以下内容不进入当前路线：

- 用参赛版覆盖主仓、复制模块、cherry-pick 参赛版实现或迁移参赛版历史；
- 依据产品站、比赛材料、本地分支或未合并 worktree 规划主线；
- ProgramService 全面拆分、`program_cmd.py`/`run_cmd.py` 全面重写或新一轮 WI219 式全仓减重；
- 为达到 400/50 等数字机械拆文件、删必要测试或把复杂度转移到配置/包装层；
- 新建 ROI/Lean 平台、命令、状态、ledger、waiver、receipt 或 blocker 生命周期；
- 把 advisory 直接用于 close、merge 或 release 阻断；
- 一次性实现五类动态专家、长期专家身份、评分、Finding Ledger、StageCloseCertificate 或第二套状态机；
- 在选中当前项之前，为所有未来候选预建空 spec/plan/tasks；
- 因对抗评审提出推测性边界而无限追加修复；两轮后必须返回用户。
- 为让 Program Truth 变绿而删除正式 truth refs、放宽 `formal_freeze_only` 或手改 computed snapshot。

## 12. 恢复与启动协议

任何新会话或中断恢复都按以下顺序执行：

1. 分别用上文两个仓库 URL 定位远端，并以 `git ls-remote <仓库 URL> refs/heads/main` 核对 `main` 精确 SHA；需要读取树时，只在各自独立 checkout 中 fetch 对应 `origin/main`。不得把两个 checkout 的 `origin` 当作同一仓库，也不读取产品站和本地材料分支作为决策真值。
2. 阅读本文件，核对“总体队列”和当前项状态，不重新从零生成 P0–P4。
3. 核对当前远端主线是否已经改变相关能力。若没有改变，直接选择队列中第一个“下一项/排队”事项。
4. P2 已由 WI220 完成。当前 v0.9.9 固定门禁是 **WI221 release-target provenance recovery**；其 admission 审计为 11/16，默认保持 blocked。若要解除该发布门，必须先由用户另行批准覆盖 `098/099/100/101` 缺口的新范围，不能直接进入 v0.9.9。
5. 路线图只作为规划输入；formal spec、plan、tasks、评审和用户 execute 批准仍分别完成。
6. 每完成一个事项，在同一收口 PR 或紧随其后的 records-only PR 中更新：状态、实际投入、证据、未完成项、下一项和 handoff。
7. 只有出现新事实导致价值、投入、风险或依赖显著变化时才重新排序；修订时保留旧决策和变化原因。

## 13. 可恢复检查表

- [x] P0 主线真值复位与轻量 ROI 合同已发布为 v0.9.8。
- [ ] O1 在 3–5 个真实项目完成 v0.9.8 真值观察。
- [x] P1 Diff-local Lean Advisory 已按运行时合同缺陷有证据 No-Go 关闭；实现未合并，主线保留 WI219 轻量 ROI prompt。
- [x] P2 普通用户单入口完成默认路径与高级兼容验证（WI220）。
- [ ] P3 十二条首次用户路线完成真实 clean-environment E2E；WI224 的 R02 bounded runtime 已合并并等待自然 release receipt，其余 11 路 runtime 仍未授权。
- [ ] P4 Phase A 证明 Requirement/Design/Implementation 动态专家 ROI。
- [ ] P4 Phase B 仅在 Phase A 获得批准后评估 Frontend Evidence/Local PR Review。
- [ ] D1 仅在满足真实触发器后重新评估；当前保持 defer。
- [ ] D2/WI221 已完成 11/16 admission audit；当前保持真实 blocked，等待用户决定是否另行批准多能力补缺范围。
- [ ] G1 已进入 WI225 formal/admission：现有稳定 finding history、`needs_user` 与终态 report/attestation 足够复用；唯一后续候选是补强根 `AGENTS.md` 的 repo-local PR/heartbeat 协议，总投入上限 0.5 人日。规则 execute 未授权，不得修改 WI224、通用 runtime、review schema 或状态机。

当检查表与聊天记忆冲突时，以远端主线事实、正式 work item 和本文件最近一次经评审的更新为准。
