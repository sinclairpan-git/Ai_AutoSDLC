# PRD：AI-SDLC Loop Engine 与本地对抗 PR Review

**功能编号**：`189-loop-engine-local-adversarial-pr-review`  
**创建日期**：2026-06-29  
**状态**：已冻结（2026-06-29），已完成两轮对抗评审并经用户确认冻结  
**目标读者**：Codex 开发 agent、AI-SDLC 框架维护者、质量负责人  
**实现入口约束**：本 PRD 已冻结；必须以本 PRD 为需求真值补齐并遵守 `plan.md` 与 `tasks.md`，不得绕过任务分解直接进入无边界实现。

## 1. 背景

AI-SDLC 已具备阶段式治理、formal work item、验证门禁、前端 browser gate、handoff 和本仓库自开发 PR heartbeat 经验。但普通用户项目存在一个关键缺口：开发完成后，AI-SDLC 还缺少一个可在用户本地仓库运行的、独立于 CI 网络和 Codex 云端 PR review 服务的代码审查与修复闭环。

当前约束如下：

1. 普通用户拥有自己的代码仓和 Git 远端，AI-SDLC 不能假定所有用户都使用本仓库的 GitHub PR 流程。
2. 许多用户的 CI/CD 网络不能访问 GPT、Claude、DeepSeek、GLM 等模型服务，因此模型审查应由本地开发机启动的独立 review agent 完成，而不是由 CI/CD 流水线发起。
3. 使用同一个实现 agent 进行自审容易被实现上下文、已有假设和修复理由污染，导致 review 客观性下降。
4. 现有 AI-SDLC 的 `refine / design / decompose / verify / execute / close` 是阶段式流程，还需要一个通用 Loop Engine 将“生成、验证、修复、复审、收口”显式产品化。

本 PRD 要求新增 **AI-SDLC Loop Engine**，并将 **Local Adversarial PR Review Loop** 作为核心 P0 能力。该能力必须在本地启动独立专职 review agent，默认调用用户当前开发环境已配置的模型，也允许用户显式选择 GPT、Claude、DeepSeek、GLM 或其他模型；不得调用 Codex 云端 PR review，不得要求 CI/CD 流水线发起模型请求。

## 2. 产品目标

### 2.1 总目标

让 AI-SDLC 从阶段式流程升级为可恢复、可审计、可验证、可停止的闭环交付系统，使需求、设计、实现、前端证据、本地 PR review 与修复收口都具有统一状态、统一 artifact 和明确的人工升级点。

### 2.2 质量目标

1. 提升需求完整度：需求必须能经过澄清、PRD、验收标准和对抗评审。
2. 提升设计一致性：`spec.md -> plan.md -> tasks.md -> tests` 不得漂移。
3. 提升实现可靠性：实现必须小步修复、小步验证，并记录证据。
4. 提升前端可信度：前端必须能在浏览器中验证，不以“文件生成”冒充“可用”。
5. 提升代码审查质量：开发完成后必须支持本地独立 review agent 进行对抗审查，避免实现 agent 自审污染。
6. 提升收口可信度：每个 loop 都必须落盘状态、证据、结论和下一步。

## 3. 范围

### 3.1 覆盖范围

本 PRD 覆盖五类一等闭环：

1. **Requirement Loop**：自然语言需求到 formal PRD/spec 的澄清、评审和冻结闭环。
2. **Design Contract Loop**：`spec / plan / tasks / tests` 的覆盖、漂移和执行前置检查闭环。
3. **Implementation Loop**：bounded task 的实现、验证、修复和升级闭环。
4. **Frontend Evidence Loop**：前端技术栈确认、生成、浏览器验证、截图和基础交互/a11y 证据闭环。
5. **Local Adversarial PR Review Loop**：本地 diff/PR review pack、独立 review agent、结构化 findings、bounded fix/rerun、final report 闭环。

本 PRD 的 P0 实现重点是：

1. Loop Engine 的通用数据模型、状态机和 artifact 布局。
2. 本地对抗 PR review loop 的 CLI、review pack、独立 agent 调用合同、findings/resolution/final-report。
3. 与现有 work item、handoff、verify、close-check 的最小集成。

### 3.2 明确不覆盖

1. 不使用 Codex 云端 PR review 服务。
2. 不要求 CI/CD 流水线调用 GPT、Claude、DeepSeek、GLM、Codex 或其他模型；模型调用发生在用户本地开发环境启动的独立 review agent 中。
3. 不要求普通用户必须创建远端 GitHub PR；本地 diff pseudo PR 必须可用。
4. 不在 P0 中实现 GitHub/GitLab inline comment 同步。
5. 不在 P0 中实现多 reviewer 投票、artifact 签名、组织级策略中心。
6. 不把 AI review 作为测试或人工确认的替代品。
7. 不允许 review agent 修改代码；修复必须由 implementation agent 或用户执行。

## 4. 关键原则

1. **独立性**：Local Review Agent 必须是独立会话或独立进程，不能复用实现 agent 的对话上下文。
2. **只读性**：Review Agent 默认只能读取 review pack、diff、必要文件和测试证据，不能直接修改代码。
3. **机械输入**：review pack 必须由 AI-SDLC 根据 Git、formal docs 和验证 artifact 机械生成，不能依赖实现 agent 手写总结。
4. **结构化输出**：review findings 必须机器可消费，并支持 `fixed / waived / not_applicable / unresolved` resolution。
5. **有界循环**：每个 loop 必须有最大轮次、停止条件、升级条件和 artifact。
6. **证据优先**：任何 passed/closed 结论必须指向具体 artifact、命令或文件。
7. **CI 分工清晰**：CI 可以验证本地 review artifact 是否覆盖当前 commit，但不得发起模型请求；模型调用属于本地 review agent 的职责。
8. **默认 fail-closed**：当 reviewer 隔离性、review pack 完整性、敏感信息处理或 findings schema 无法证明时，PR review loop 必须进入 `blocked` 或 `needs_user`，不得给出通过结论。
9. **小白友好**：普通用户必须能通过少量命令看懂当前结果、下一步和失败原因；CLI 不得把 provider、base branch、redaction 或 artifact schema 问题暴露成只有框架维护者才能理解的错误。
10. **企业可治理**：所有长期落盘 artifact 必须有 schema version、policy profile 和稳定兼容策略，避免大型组织多仓接入后因格式漂移无法审计或升级。

## 5. 用户场景与验收

### 用户故事 1 - 本地独立 PR review（优先级：P0）

作为普通 AI-SDLC 用户，我希望在本地开发完成后，对当前分支相对 `main` 或指定 base 的 diff 启动独立 review agent，并默认使用我当前开发环境已配置的模型，以便在 CI 无法访问模型服务的情况下仍能获得对抗式代码审查。

**独立测试**：在一个 fixture Git 仓库中创建 feature 分支和代码 diff，先执行 `ai-sdlc pr-review start --base main --provider local-agent --model current --provider-command "my-local-reviewer" --dry-run` 断言只预览将生成的 artifact、provider、model selector 和命令且不写入 review run、不启动模型；再执行 `ai-sdlc pr-review start --base main --provider mock-reviewer` 断言生成 review pack、findings 和状态文件，且不调用云端 PR review 服务。

**验收场景**：

1. **Given** 当前仓库有 feature 分支相对 `main` 的 diff，**When** 用户执行 `ai-sdlc pr-review start --base main --provider local-agent --model current --provider-command "my-local-reviewer"`，**Then** 系统必须生成一个本地 review run，并写入 `.ai-sdlc/reviews/pr/<review-id>/review-pack.json`。
2. **Given** CI 网络不可访问模型服务，**When** 用户在本地执行 PR review，**Then** review agent 默认调用用户当前开发环境已配置的模型，也可以按用户显式指定调用 GPT、Claude、DeepSeek、GLM 或其他模型；系统不得要求 CI 发起模型请求。
3. **Given** review provider 为 `local-agent`，**When** 系统启动 review，**Then** 它必须使用独立 reviewer 会话或进程，不得复用当前实现 agent 上下文。

### 用户故事 2 - 结构化 findings 与有界修复闭环（优先级：P0）

作为开发 agent，我希望 review 结果是结构化 findings，并且每轮只修复 `BLOCKER` 和 `REQUIRED`，以便修复过程可追踪、可停止、不会无限扩大范围。

**独立测试**：使用模拟 reviewer 输出包含 `BLOCKER / REQUIRED / ADVISORY` 的 `findings.json`，执行 `ai-sdlc pr-review fix --max-rounds 2 --dry-run`，断言系统只选择必须修复项，并在超过轮次或未解决时进入 `needs_user` 或 `blocked`。

**验收场景**：

1. **Given** reviewer 输出包含 `BLOCKER`、`REQUIRED` 和 `ADVISORY`，**When** 用户执行修复 loop，**Then** 默认只处理 `BLOCKER` 与 `REQUIRED`，`ADVISORY` 不得自动进入修复计划。
2. **Given** 同一 finding 连续两轮仍 unresolved，**When** 继续 rerun，**Then** 系统必须停止自动修复并升级为 user-input blocker。
3. **Given** 用户对某个 `REQUIRED` finding 提供 waiver，**When** 执行 close，**Then** final report 必须记录 waiver 原因、操作者和时间。

### 用户故事 3 - Review pack 防污染（优先级：P0）

作为质量负责人，我希望 review agent 只看到机械生成的 review pack，而不是实现 agent 对自己代码的解释，以便降低自审污染和锚定偏差。

**独立测试**：构造实现 agent handoff 中包含自我辩护内容的 fixture，生成 review pack，断言 pack 不包含实现 agent chat transcript、非必要 handoff 叙述或主观总结，只包含 Git diff、formal refs、测试证据和必要仓库上下文。

**验收场景**：

1. **Given** 当前工作区存在 Codex 会话 handoff，**When** 生成 review pack，**Then** pack 不得包含实现 agent 的聊天历史或主观解释。
2. **Given** formal work item 已存在 `spec.md / plan.md / tasks.md`，**When** 生成 review pack，**Then** pack 可以包含这些文件的 bounded 摘要和路径引用。
3. **Given** 当前 diff 很大，**When** 生成 review pack，**Then** 系统必须按策略截断、分片或提示用户缩小范围，不得静默丢弃关键变更。

### 用户故事 4 - Loop Engine 通用状态与恢复（优先级：P0）

作为 AI-SDLC 用户，我希望任一 loop 中断后都能从 `.ai-sdlc/` 状态恢复，以便长任务不会依赖聊天窗口记忆。

**独立测试**：在 loop run 生成后中断进程，重新执行 `ai-sdlc loop status` 或 `ai-sdlc pr-review status`，断言能读取当前 run、round、findings、resolution、next action。

**验收场景**：

1. **Given** PR review loop 已完成第一轮 review，**When** 进程中断后重新执行 status，**Then** 系统必须显示当前 review id、状态、未解决 findings 和下一步命令。
2. **Given** loop 状态为 `needs_fix`，**When** 用户执行 rerun 而未先记录修复结果，**Then** 系统必须提示先更新 resolution 或运行验证。
3. **Given** loop 状态为 `passed`，**When** 用户执行 close，**Then** 系统必须生成 final report 并标记 run 为 `closed`。

### 用户故事 5 - 需求与设计闭环（优先级：P1）

作为产品负责人，我希望 AI-SDLC 能将需求和设计也纳入 loop engine，以便 PRD、plan、tasks 和 tests 在进入实现前完成一致性对账。

**独立测试**：构造 spec 中有 AC 但 tasks 缺失对应任务的 fixture，执行 design contract loop dry-run，断言输出 blocker 级合同缺口。

**验收场景**：

1. **Given** `spec.md` 包含 P0 验收场景但 `tasks.md` 没有覆盖，**When** 执行 design contract loop，**Then** 系统必须报告 blocker。
2. **Given** `plan.md` 引入 spec 未授权的能力，**When** 执行 design contract loop，**Then** 系统必须报告范围蔓延。
3. **Given** 用户仍未冻结 PRD，**When** agent 尝试进入实现，**Then** 系统必须阻断 execute handoff。

### 用户故事 6 - 前端证据闭环接入（优先级：P1）

作为前端项目用户，我希望现有 Frontend Managed Delivery Loop 能被纳入 Loop Engine 状态和报告，以便 browser gate、截图、交互/a11y findings 进入统一证据体系。

**独立测试**：运行模拟 browser gate artifact，执行 frontend evidence loop status，断言 browser gate 结果、截图路径和 warning/blocker 能进入 loop report。

**验收场景**：

1. **Given** 前端 browser gate 生成 latest artifact，**When** 查询 loop report，**Then** 系统必须展示 Web smoke、desktop/mobile screenshot 和 fatal console 状态。
2. **Given** 页面白屏或 fatal console error，**When** 执行 frontend evidence loop，**Then** 必须输出 blocker。
3. **Given** 只有轻微 a11y warning，**When** 执行 close，**Then** 可在 warning 未修复但已记录的情况下允许用户确认收口。

### 用户故事 7 - 本地 review 的隐私和敏感文件预检（优先级：P0）

作为企业或个人用户，我希望本地 PR review 在调用任何可能外发代码的 provider 前先完成敏感信息和文件范围预检，以便避免把 secret、二进制资产、超大文件或明确排除的路径发送给模型服务。

**独立测试**：构造 diff 中包含 `.env`、疑似密钥、二进制文件和超大文件的 fixture，执行 review pack 生成，断言系统输出 `redaction-report.json`，并在外部 provider 未获确认时进入 `needs_user`。

**验收场景**：

1. **Given** diff 包含疑似 secret，**When** 生成 review pack，**Then** secret 必须被 redacted 或该文件必须被 omitted，并在 redaction report 中记录。
2. **Given** provider 可能把代码发送到远程模型服务，**When** 项目策略要求外发确认且用户未确认，**Then** review loop 必须停止在 `needs_user`；未启用该策略时，系统必须至少披露 provider/model 与代码外发状态。
3. **Given** 文件被 omit 或 redacted，**When** review agent 运行，**Then** final report 必须披露 omission/redaction 对 review 完整性的影响。

### 用户故事 8 - 技术小白可完成本地 PR review（优先级：P0）

作为不熟悉 Git、provider 和 AI-SDLC 内部概念的普通用户，我希望 `pr-review` 能先检查环境并给出可执行下一步，以便我不需要理解所有 artifact 和 provider 细节也能安全启动本地 review。

**独立测试**：构造未初始化项目、非 Git 仓库、无 base branch、无 provider 配置、存在 high-risk secret 的 fixture，分别执行 `ai-sdlc pr-review doctor` 与 `ai-sdlc pr-review start`，断言输出包含“当前结果 / Result”和“下一步 / Next”，且给出唯一或有限个可执行命令。

**验收场景**：

1. **Given** 项目尚未初始化，**When** 用户执行 `ai-sdlc pr-review start`，**Then** 系统必须提示先运行 `ai-sdlc init .`，不得输出 Python traceback。
2. **Given** base branch 不明确，**When** 用户执行 `ai-sdlc pr-review start`，**Then** 系统必须展示检测到的候选 base 和推荐命令，而不是要求用户理解 `merge-base`。
3. **Given** `local-agent` 尚未配置且无法解析当前模型，**When** 用户执行 `pr-review start`，**Then** 系统必须给出 provider/model 配置指引和可用的 `mock-reviewer --dry-run` 预演命令。

### 用户故事 9 - 大型组织可治理地推广 Loop Engine（优先级：P0）

作为在多个大型公司落地 AI-Native 闭环实践的架构负责人，我希望 Loop Engine 的 artifact、policy 和 provider runner 都有稳定合同，以便多个仓库、多个团队和多个版本之间能审计、迁移和逐步升级。

**独立测试**：构造不同 schema version、不同 policy profile、不同 provider runner 的 artifact fixture，执行 status/validate/close 检查，断言兼容版本可读、未知必填字段 fail-closed、policy profile 能影响 close 和 provider 外发策略。

**验收场景**：

1. **Given** 一个旧版本 review artifact，**When** 新版 AI-SDLC 读取 status，**Then** 系统必须识别 schema version，并在兼容范围内正常显示或给出迁移建议。
2. **Given** 企业策略禁止代码外发到远程模型服务，**When** 用户选择会外发代码的 provider/model，**Then** policy profile 必须阻断启动；若策略允许，GPT、Claude、DeepSeek、GLM 等模型都应可通过本地 agent runner 使用。
3. **Given** provider runner 退出码非零或未生成合法 findings，**When** loop 收口，**Then** 系统必须进入 `blocked` 并给出 plain-language blocker。

## 6. 功能需求

### 6.1 Loop Engine 通用能力

- **FR-189-001**：系统必须新增统一 Loop Engine 概念；P0 的数据模型、状态枚举和 artifact schema 必须能表达 `requirement`、`design-contract`、`implementation`、`frontend-evidence`、`local-pr-review` 五类 loop，P0 可执行命令只要求完整落地 `local-pr-review`，其余 loop 的专用命令和横向编排按 P1 范围处理。
- **FR-189-002**：每个 loop run 必须有稳定 `loop_id`、`loop_type`、`status`、`created_at`、`updated_at`、`base_ref`、`head_ref`、`work_item_id`、`next_action`。
- **FR-189-003**：每个 loop run 必须支持 round 概念，记录 round number、输入 artifact、输出 artifact、执行命令、结果和下一步。
- **FR-189-004**：Loop 状态必须至少覆盖 `created`、`running`、`needs_fix`、`needs_review`、`needs_user`、`blocked`、`passed`、`closed`。
- **FR-189-005**：Loop artifacts 必须写入 `.ai-sdlc/loops/<loop-type>/<loop-id>/` 或更具体的兼容路径，并可由 status 命令恢复。
- **FR-189-006**：系统必须提供 read-only status 命令，展示当前 loop、round、未解决 findings、验证结果和下一步。
- **FR-189-007**：系统必须支持 dry-run 模式，展示将生成的 artifacts、将启动的 provider 和将执行的命令，但不调用模型、不修改代码。
- **FR-189-008**：任一 loop 达到最大轮次、验证环境不可用、scope 扩大或需要用户判断时，必须进入 `needs_user` 或 `blocked`，不得无限重试。
- **FR-189-009**：所有 Loop Engine artifact 必须包含 `schema_version`、`artifact_kind`、`created_by`、`created_at`、`ai_sdlc_version` 和兼容性字段。
- **FR-189-010**：系统必须提供 artifact schema validation；未知必填字段、缺失必填字段或不兼容 schema version 必须 fail-closed。
- **FR-189-011**：系统必须支持项目级 loop policy profile，P0 至少覆盖 provider 外发策略、max rounds、default close mode、redaction strictness 和 allowed omitted file policy。
- **FR-189-012**：当 policy profile 与命令参数冲突时，policy profile 必须优先，并在 CLI 输出中说明被阻断的原因。

### 6.2 Local Adversarial PR Review CLI

- **FR-189-020**：系统必须新增 `ai-sdlc pr-review` 命令组。
- **FR-189-021**：`ai-sdlc pr-review start --base <ref> --provider <provider>` 必须能基于当前 checkout 生成本地 PR review run。
- **FR-189-022**：`ai-sdlc pr-review start --pr <id>` 必须作为 P1 能力读取远端 PR diff；P0 必须优先支持本地 `base..HEAD` diff。
- **FR-189-023**：`ai-sdlc pr-review status` 必须只读展示当前 review run 状态。
- **FR-189-024**：`ai-sdlc pr-review fix --max-rounds <n>` 必须根据 unresolved `BLOCKER`/`REQUIRED` findings 生成修复计划；实际代码修改可由当前 implementation agent 执行。
- **FR-189-025**：`ai-sdlc pr-review rerun` 必须重新生成 review pack，并启动新的独立 review agent 或清空上下文的 reviewer。
- **FR-189-026**：`ai-sdlc pr-review close` 默认必须在无 unresolved `BLOCKER` 且无 unresolved `REQUIRED` 时生成 final report；`REQUIRED` 只能通过 `fixed`、`waived` 或 `not_applicable` 收口。
- **FR-189-027**：`ai-sdlc pr-review` 不得调用 Codex 云端 PR review 服务，不得依赖 GitHub `@codex review`。
- **FR-189-028**：`ai-sdlc pr-review close --require-no-blockers` 必须作为宽松模式明确标注 remaining `REQUIRED` 风险；该模式不得被默认 close-check 或 release gate 当作 fully clean。
- **FR-189-029**：`ai-sdlc pr-review fix` 在 P0 中默认生成 `fix-plan.md` 和 `resolution.yaml` 待办，不直接修改代码；若未来接入实现 agent 自动修复，必须使用单独显式参数和 scope guard。
- **FR-189-030**：`ai-sdlc pr-review start` 必须在未初始化项目中输出 `ai-sdlc init .` 引导，不得只创建局部 review artifact。
- **FR-189-031**：系统必须新增 `ai-sdlc pr-review doctor` 作为 P0 只读诊断命令，检查 init 状态、Git 状态、base branch、provider 配置、policy profile、redaction 配置和 artifact 可写性。
- **FR-189-032**：`ai-sdlc pr-review start` 不带 `--base` 时必须尝试自动检测默认 base；若检测结果唯一，输出使用的 base；若不唯一，进入 `needs_user` 并给出候选命令。
- **FR-189-033**：`ai-sdlc pr-review start` 不带 `--provider` 时必须使用项目 policy 或用户当前开发环境配置的默认本地 agent provider；不带 `--model` 时默认使用 `current`，即当前 agent/CLI 环境正在使用的模型。若无法解析默认 provider 或当前模型，必须给出配置指引和 `mock-reviewer --dry-run` 预演命令。
- **FR-189-034**：所有 `pr-review` 命令的人类输出必须包含“当前结果 / Result”和“下一步 / Next”；失败时必须包含 plain-language blocker 和建议命令。
- **FR-189-035**：CLI 必须提供 `--json` 输出，供高级用户和自动化读取；human 输出不得只暴露 JSON。

### 6.3 Review Agent 独立性与 provider 合同

- **FR-189-040**：系统必须支持 `local-agent` provider，用于在本地启动独立 reviewer 会话或进程；该 provider 默认使用 `--model current`，并支持显式选择 GPT、Claude、DeepSeek、GLM 或用户配置的其他模型。
- **FR-189-041**：P0 可提供 `mock-reviewer` provider 作为测试和离线验证用 provider。
- **FR-189-042**：Review Agent 必须只接收 review pack 和必要文件读取权限，不能接收实现 agent 的聊天 transcript。
- **FR-189-043**：Review Agent 默认只读；任何文件写入能力必须在 P0 禁止。
- **FR-189-044**：Review Agent 输出必须是结构化 `findings.json`；若输出无法解析，loop 必须进入 `blocked` 并保留原始输出。
- **FR-189-045**：Provider 配置必须显式披露代码是否会发送到远程模型服务，且支持项目 policy 禁用代码外发或要求用户确认；不得把“远程模型服务”误解为禁止使用 GPT、Claude、DeepSeek、GLM 等模型。
- **FR-189-046**：系统必须记录 provider id、provider mode、model selector、resolved model、模型调用是否由本地 agent runner 发起、是否外发代码、redaction 状态。
- **FR-189-047**：`local-agent` provider 必须通过可配置的本地 reviewer 命令或等价本地 agent 启动接口运行，输入只能是 review pack 路径、model selector 和允许读取的文件列表；`codex-local` 可作为兼容 alias 或具体本地 agent 适配，不得作为唯一真实 provider。
- **FR-189-047A**：`--model current` 必须通过稳定优先级解析：显式 CLI `--model` 非 current > project policy default model > provider config default model > 当前 agent/CLI 环境模型。解析结果必须写入 `ModelResolution`，包含 provider id、provider mode、model selector、resolved model、resolution source、status、code egress 和 blocker；无法解析时必须进入 `needs_user`。
- **FR-189-048**：每次 reviewer 启动必须写入 `reviewer-invocation.json`，包含 command、argv、cwd、input_paths、output_paths、isolation_mode、external_model_disclosure 和 exit status。
- **FR-189-049**：如果系统无法证明 reviewer 是新会话、独立进程或已清空上下文的 reviewer，loop 必须进入 `blocked`，不得把结果标记为对抗 review。
- **FR-189-050**：Review Agent prompt 必须由 AI-SDLC 生成，并明确要求只读、结构化输出、禁止修代码、禁止引用实现 agent 聊天上下文。
- **FR-189-051**：`mock-reviewer` 必须用于单元/集成测试，且不得访问网络或真实模型。
- **FR-189-052**：`local-agent` 未配置本地 reviewer 命令或无法解析 `--model current` 时，CLI 必须进入 `needs_user` 并输出 provider/model 配置指引，而不是 fallback 到 Codex 云端 PR review。
- **FR-189-053**：Provider runner 合同必须标准化退出码：`0` 表示 findings 生成成功，`10` 表示 changes required，`20` 表示 blocked，其他非零退出码表示 runner failure。
- **FR-189-054**：Provider runner 必须在声明的 output path 写入 findings；缺失输出、非 JSON 输出或 schema validation 失败必须将 loop 标记为 `blocked`。
- **FR-189-055**：Provider runner 不得直接读取未列入 review pack allowlist 的路径；P0 至少在 invocation artifact 中记录 allowlist，P1 可强化为执行时约束。

### 6.4 Review Pack

- **FR-189-060**：系统必须生成 `.ai-sdlc/reviews/pr/<review-id>/review-pack.json`。
- **FR-189-061**：Review pack 必须包含 repo root、base ref、head ref、base commit、head commit、diff summary、changed files、work item refs、test results refs、policy refs。
- **FR-189-062**：Review pack 必须包含 `diff.patch` 或分片 diff 文件，并记录 diff 截断/分片策略。
- **FR-189-063**：Review pack 必须包含 `changed-files.txt`。
- **FR-189-064**：Review pack 可以包含 `spec-summary.md`、`task-summary.md`、`test-results.md`，但这些摘要必须来自 formal docs 和命令输出，不得来自实现 agent 自述。
- **FR-189-065**：Review pack 必须标记 omitted files、large files、binary files、generated files 和 secrets redaction 状态。
- **FR-189-066**：当 diff 超过配置阈值时，系统必须分片、要求缩小范围或进入 `needs_user`，不得静默丢弃。
- **FR-189-067**：Review pack 必须绑定当前 head commit；head commit 变化后，旧 findings 不得被当作当前 commit 已审查证明。
- **FR-189-068**：Review pack 生成前必须执行敏感路径和 secret 预检，至少覆盖 `.env*`、私钥文件、常见 token/key 模式和用户配置的 exclude patterns。
- **FR-189-069**：Review pack 必须写入 `redaction-report.json`，记录 redacted、omitted、binary、large、generated 文件及原因。
- **FR-189-070**：对会把代码发送到远程模型服务的 provider/model，若 redaction report 中存在 high-risk secret，或项目 policy 要求外发确认但用户未确认，review loop 必须进入 `needs_user`。
- **FR-189-071**：Review pack 必须记录 diff 覆盖率，包括 changed files 总数、included files、omitted files 和 omitted line count。
- **FR-189-072**：Review Agent 的最终 verdict 必须披露 review pack 是否完整；若关键文件被 omit，verdict 最高只能是 `blocked` 或 `changes_required`，除非用户显式 waiver。
- **FR-189-073**：Review pack 摘要不得包含实现 agent 的主观解释；如需上下文，只能引用 formal docs、命令输出和仓库文件摘要。
- **FR-189-074**：Review pack 必须写入 `schema_version`，并由 schema validation 覆盖；schema 文件或 Pydantic 模型必须纳入 focused tests。
- **FR-189-075**：Review pack 必须记录 policy profile id 和本次 policy decisions，包括 provider、model selector、resolved model、是否代码外发、redaction strictness、max rounds 和 close mode。

### 6.5 Findings 与 Resolution

- **FR-189-080**：Findings 必须支持 severity：`BLOCKER`、`REQUIRED`、`ADVISORY`。
- **FR-189-081**：每条 finding 必须包含 `id`、`severity`、`file`、`line`、`claim`、`evidence`、`risk`、`suggested_fix`、`confidence`、`resolution`。
- **FR-189-082**：`resolution` 必须支持 `unresolved`、`fixed`、`waived`、`not_applicable`。
- **FR-189-083**：`BLOCKER` 未解决时不得 close。
- **FR-189-084**：默认 close 必须要求 `REQUIRED` 已 fixed、waived 或 not_applicable；`--require-no-blockers` 宽松模式可以生成 risk-accepted report，但不得标记为 `fully_clean`。
- **FR-189-085**：`ADVISORY` 默认不进入自动修复计划，但必须保留在 final report。
- **FR-189-086**：Waiver 必须记录 reason、operator、timestamp 和关联 finding id。
- **FR-189-087**：Rerun 时必须对 findings 做稳定匹配或保留历史映射，避免同一问题因 id 变化重复出现。

### 6.6 修复与验证闭环

- **FR-189-100**：默认 fix loop 只处理 `BLOCKER` 和 `REQUIRED`。
- **FR-189-101**：Fix loop 必须支持最大轮次，默认不超过 2 轮，配置不得无限。
- **FR-189-102**：每轮 fix 后必须要求 targeted verification，并将命令和结果写入 review artifact。
- **FR-189-103**：同一 finding 连续两轮仍 unresolved 时，loop 必须进入 `needs_user`。
- **FR-189-104**：Fix loop 不得自动修改 review pack 之外的无关范围；发现范围扩大必须报告 scope drift。
- **FR-189-105**：修复后 rerun 必须重新生成 review pack，不能复用旧 diff。
- **FR-189-106**：Final report 必须展示每个 finding 的最终 resolution、验证证据和残留风险。
- **FR-189-107**：`fix-plan.md` 必须列出每个待修 finding、建议修改文件、允许范围、需要运行的验证命令和不得触碰的路径。
- **FR-189-108**：implementation agent 完成修复后，必须更新 `resolution.yaml`，记录 fixed evidence 或 waiver，不得由 reviewer 代写修复结论。
- **FR-189-109**：rerun 前必须检查 working tree 与 previous review head commit 的差异；如果 diff 包含非 finding 相关扩大范围，必须报告 scope drift。

### 6.7 CI 与 Attestation 分工

- **FR-189-120**：系统不得要求 CI/CD 流水线调用 GPT、Claude、DeepSeek、GLM、Codex 或其他模型；模型调用必须由用户本地开发环境中的独立 review agent 发起。
- **FR-189-121**：P1 可生成 `.ai-sdlc/reviews/pr/latest-attestation.json`，供 CI 检查当前 commit 是否已有本地 review。
- **FR-189-122**：Attestation 必须包含 review id、head commit、verdict、unresolved blocker count、generated_at 和 artifact paths。
- **FR-189-123**：CI 只允许检查 attestation 与 commit hash、unresolved blocker count、artifact schema，不得发起模型请求。
- **FR-189-124**：P0 文档必须给出“本地模型 review 与 CI 确定性检查如何配合”的普通用户解释，避免用户误以为 CI 不再需要测试。

### 6.8 与现有 AI-SDLC 的集成

- **FR-189-140**：Local PR Review Loop 必须可关联当前 work item id。
- **FR-189-141**：Review final report 必须可被 `close-check` 或等价 close-stage 检查读取。
- **FR-189-142**：Handoff 更新必须记录 current loop、unresolved findings、验证结果和下一步。
- **FR-189-143**：`verify constraints` 或 focused tests 必须覆盖 PR review artifact schema、禁止 Codex 云端 PR review 替代本地 agent 的策略面，以及 CI 不发起模型请求的边界。
- **FR-189-144**：Loop Engine 不得破坏现有 `ai-sdlc run`、`stage`、`workitem`、`program` 命令。
- **FR-189-145**：`close-check` 集成本地 PR review 时必须区分 `fully_clean`、`risk_accepted`、`blocked` 三种 verdict，不得把 `--require-no-blockers` 宽松结果等同为 fully clean。
- **FR-189-146**：Handoff 中必须记录 beginner-facing next command，不能只记录内部 artifact 路径。

## 7. 关键实体

- **LoopRun**：一个 loop 的持久化运行实例，包含类型、状态、关联 work item、base/head、rounds 和 next action。
- **LoopRound**：一次具体迭代，包含输入 artifact、输出 artifact、命令、结果和错误。
- **ReviewRun**：Local PR Review Loop 的具体运行，包含 review id、provider、diff scope、findings 和 verdict。
- **ReviewPack**：交给 review agent 的机械生成输入包。
- **ReviewFinding**：结构化 review 问题。
- **FindingResolution**：对 finding 的 fixed/waived/not_applicable/unresolved 状态记录。
- **VerificationEvidence**：测试、lint、build、browser gate 或人工验证证据。
- **ReviewFinalReport**：可供 close/check/人工审阅的最终报告。
- **ReviewAttestation**：P1 能力，供 CI 或外部工具只读检查本地 review 覆盖状态。
- **LoopPolicyProfile**：项目级 loop 策略，定义默认 provider、默认 model selector、代码外发披露/确认、redaction、round limit、close mode 和 omitted file 策略。
- **ModelResolution**：一次 provider/model 解析结果，包含 `model_selector`、`resolved_model`、`provider_mode`、`resolution_source`、`status`、`code_egress` 和 blocker。
- **ProviderRunnerInvocation**：一次 reviewer runner 调用记录，包含命令、model selector、resolved model、代码外发状态、输入、输出、退出码、allowlist 和隔离状态。
- **SchemaValidationReport**：artifact schema 校验结果，包含 schema version、兼容性、错误列表和 next action。

## 8. Artifact 布局

P0 必须支持以下布局：

```text
.ai-sdlc/
├── loops/
│   └── local-pr-review/
│       └── <loop-id>/
│           ├── loop-run.json
│           ├── rounds/
│           │   └── 001/
│           │       ├── input.json
│           │       ├── output.json
│           │       └── command-log.txt
│           └── final-report.md
└── reviews/
    └── pr/
        └── <review-id>/
            ├── review-pack.json
            ├── diff.patch
            ├── changed-files.txt
            ├── spec-summary.md
            ├── task-summary.md
            ├── test-results.md
            ├── redaction-report.json
            ├── reviewer-invocation.json
            ├── schema-validation.json
            ├── findings.json
            ├── fix-plan.md
            ├── resolution.yaml
            └── final-report.md
```

实现可在设计阶段合并 `loops` 与 `reviews` 的冗余路径，但必须保留对用户可理解、可恢复、可审计的稳定路径。

## 9. 命令合同

P0 命令：

```bash
ai-sdlc pr-review start --base main --provider local-agent --model current --provider-command "my-local-reviewer"
ai-sdlc pr-review start --base main --provider local-agent --model claude --provider-command "my-local-reviewer"
ai-sdlc pr-review start --base main --provider mock-reviewer --dry-run
ai-sdlc pr-review doctor
ai-sdlc pr-review status
ai-sdlc pr-review fix --max-rounds 2
ai-sdlc pr-review rerun
ai-sdlc pr-review close
ai-sdlc pr-review close --require-no-blockers
```

P1 命令：

```bash
ai-sdlc loop status
ai-sdlc loop list
ai-sdlc pr-review start --pr 123 --provider local-agent --model current --provider-command "my-local-reviewer"
ai-sdlc pr-review close --strict
ai-sdlc pr-review attest
```

命令输出必须包含：

1. 当前结果 / Result。
2. 下一步 / Next。
3. artifact path。
4. unresolved blocker/required/advisory count。
5. provider、model selector、resolved model，以及是否会把代码发送到远程模型服务的明确提示。
6. reviewer 隔离状态和 redaction/omission 摘要。
7. 对普通用户可直接复制执行的下一条命令；如果存在多个选择，必须解释推荐项。

## 10. 成功标准

- **SC-189-001**：在本地 fixture 仓库中，`pr-review start --base main --provider mock-reviewer` 能生成 review pack、findings、loop state，并可由 status 恢复。
- **SC-189-002**：`local-agent` provider 合同明确要求独立 reviewer 会话/进程，默认使用 `--model current`，支持显式模型选择，并禁止复用实现 agent transcript。
- **SC-189-003**：`pr-review fix --max-rounds 2` 默认只选择 `BLOCKER` 和 `REQUIRED`，不自动修复 `ADVISORY`。
- **SC-189-004**：未解决 `BLOCKER` 时，`pr-review close` 和 `pr-review close --require-no-blockers` 都必须失败并指向 unresolved finding。
- **SC-189-005**：head commit 改变后，旧 review attestation 或 final report 不得被当作当前 commit 的有效 review。
- **SC-189-006**：CI 相关文档和 artifact 设计明确禁止由流水线发起模型请求，同时明确本地 review agent 可以调用用户当前模型或显式选择的 GPT、Claude、DeepSeek、GLM 等模型。
- **SC-189-007**：Review pack 不包含实现 agent 聊天记录或自我辩护式总结。
- **SC-189-008**：Loop status 能在中断后恢复 current loop、round、findings 和 next action。
- **SC-189-009**：`verify constraints` 或 focused tests 能发现 findings schema 缺失、review pack schema 漂移、云端 PR review 服务误用。
- **SC-189-010**：PRD、plan、tasks、用户文档和测试 fixture 对 P0 命令、artifact、状态、findings schema 保持一致。
- **SC-189-011**：当 `local-agent` 无法证明独立 reviewer 启动时，loop 必须 blocked，不能产出 pass verdict。
- **SC-189-012**：当 review pack 含 high-risk secret，或项目 policy 要求代码外发确认但用户未确认时，loop 必须进入 `needs_user`。
- **SC-189-013**：默认 `pr-review close` 在 unresolved `REQUIRED` 存在时失败；只有 waiver/not_applicable/fixed 后才能 clean close。
- **SC-189-014**：`pr-review doctor` 在未初始化、非 Git、base 不明确、provider 未配置和 secret 高风险场景下均给出 plain-language blocker 和下一条建议命令。
- **SC-189-015**：artifact schema validation 能阻断缺失 `schema_version`、不兼容 version 和 findings schema 漂移。
- **SC-189-016**：policy profile 禁止代码外发到远程模型服务时，任何会外发代码的 provider/model 启动必须被阻断；policy 未禁止时，系统不得因模型品牌是 GPT、Claude、DeepSeek、GLM 等而阻断。
- **SC-189-017**：`close-check` 能区分 `fully_clean` 与 `risk_accepted`，不会把宽松 close 误当作干净收口。

## 11. 风险与控制

| 风险 | 影响 | 控制方式 |
|------|------|----------|
| 代码外发模型服务 | 可能违反用户隐私和企业合规要求 | provider/model 必须显式披露是否外发；P0 做敏感路径/secret 预检和 redaction report；支持通过 policy 禁止代码外发或要求确认 |
| Review Agent 误报/漏报 | 可能造成错误修复或虚假通过 | AI review 不替代测试；findings 分级；required waiver 必须记录 |
| 实现 agent 自审污染 | review 结果偏向自我辩护 | 独立 reviewer 会话/进程；review pack 不含聊天 transcript |
| 大 diff 成本高 | 模型费用和上下文溢出 | diff 分片、阈值、needs_user、文件过滤 |
| 自动修复扩大范围 | 引入无关变更或回归 | 只修 blocker/required；scope drift 检测；最大轮次 |
| 本地 artifact 可篡改 | 不能作为强合规证明 | P0 只作为本地治理证据；P1 attestation 绑定 commit；P2 可签名 |
| CI 无模型网络 | 流水线无法运行模型审查 | 模型调用由本地独立 review agent 发起，默认使用用户当前模型；CI 只检查 artifact/commit hash/schema |
| 普通用户不会配置 provider 或 base branch | 启动失败、学习成本过高 | P0 提供 `pr-review doctor`、base 自动检测、默认 provider 指引和 plain-language next command |
| 多仓推广时 artifact/schema 漂移 | 企业无法审计、升级和自动化消费 | P0 增加 schema version、schema validation 和 policy profile |

## 12. 发布与迁移要求

1. 新能力必须默认不影响现有项目，只有用户执行 `pr-review` 或 `loop` 命令时才生成 artifact。
2. 普通用户文档必须说明：本地 PR review 不等于 Codex 云端 PR review。
3. 用户文档必须说明：本地 review 默认使用用户当前模型，也允许显式选择 GPT、Claude、DeepSeek、GLM 或其他模型；是否向远程模型服务发送代码取决于 provider/model 配置和项目 policy。
4. Release notes 必须说明 CI 不发起模型请求的设计边界。
5. 如果项目未初始化，`pr-review` 必须给出 `ai-sdlc init .` 引导，而不是静默创建局部状态。
6. 用户指南必须给出 3 步小白路径：`ai-sdlc init .`、`ai-sdlc pr-review doctor`、`ai-sdlc pr-review start`。
7. 用户指南必须给出企业策略路径：如何配置 policy profile、禁用代码外发或要求确认、查看 redaction report 和识别 risk-accepted close。

## 13. P0 / P1 / P2 切分

### P0：最小可用本地对抗 PR Review Loop

1. `ai-sdlc pr-review start/status/fix/rerun/close`。
2. `ai-sdlc pr-review doctor`。
3. `mock-reviewer` 与 `local-agent` provider/model runner 合同。
4. Review pack、findings、resolution、final report。
5. schema version、schema validation 和 policy profile 最小实现。
6. beginner-friendly Result/Next/plain-language blocker 输出。
7. 本地 diff pseudo PR。
8. focused tests 与 schema 校验。

### P1：Loop Engine 横向扩展

1. `ai-sdlc loop status/list`。
2. Requirement Loop 与 Design Contract Loop 的 dry-run/check 模式。
3. Frontend Evidence Loop 接入已有 browser gate artifact。
4. GitHub/GitLab PR diff 读取。
5. Attestation artifact 和 CI 只读检查。
6. Finding 去重和历史映射。

### P2：团队与企业增强

1. 多 reviewer 角色。
2. provider 策略中心。
3. redaction 策略与敏感文件过滤。
4. artifact 签名。
5. 组织级 waiver 审批。
6. 远端 PR inline comments 同步。

## 14. 开放问题

| 问题 | 默认决策 | 阻塞阶段 |
|------|----------|----------|
| `local-agent` 如何具体启动独立 reviewer 会话并解析 `--model current` | P0 先定义 provider/model runner 合同与 mock provider；具体 host 集成在 plan 阶段确认，`codex-local` 仅作为可能 alias | design |
| Review pack 摘要是否允许包含 handoff | 默认不允许包含实现 agent 主观 handoff；只允许 bounded formal docs 和命令证据 | design |
| `REQUIRED` 在 `--require-no-blockers` 下如何表达 | 默认 close 阻断 unresolved `REQUIRED`；`--require-no-blockers` 只生成 `risk_accepted` 报告，不可标记为 `fully_clean` | design |
| CI 是否强制检查 attestation | P1 可选，不作为 P0 阻断 | design |
| policy profile 首版文件名与位置 | 默认建议 `.ai-sdlc/project/config/loop-policy.yaml`，计划阶段确认是否与 project config 合并 | design |
| schema 使用 JSON Schema 还是 Pydantic-only | P0 至少要有 Pydantic validation；是否导出 JSON Schema 在 plan 阶段定 | design |

## 15. 对抗评审记录

### Round 1：本地架构/测试/安全对抗评审

**评审结论**：第一轮发现 5 个 P0 blocker，均已在本版 PRD 中修订。

| Finding | 严重级别 | 问题 | 修订结果 |
|---------|----------|------|----------|
| ADV-PRD-001 | P0 | 本地 reviewer provider 只写“独立会话/进程”，没有可验证启动合同，开发 agent 不知道如何证明 reviewer 未被实现上下文污染。 | 新增 `reviewer-invocation.json`、本地 reviewer 命令合同、隔离失败 blocked、prompt 合同。 |
| ADV-PRD-002 | P0 | `pr-review fix` 容易被误解为 CLI 自动改代码，与 reviewer 只读和 implementation agent 修复职责冲突。 | 明确 P0 `fix` 只生成 `fix-plan.md`，实际修复由 implementation agent/用户执行。 |
| ADV-PRD-003 | P0 | `REQUIRED` close 语义前后不一致，可能让 unresolved required 在默认 close 中被误放行。 | 改为默认 close 阻断 unresolved `BLOCKER` 和 `REQUIRED`；`--require-no-blockers` 只是 risk-accepted 宽松报告。 |
| ADV-PRD-004 | P0 | 隐私与 redaction 只作为风险提示，不足以阻止 `.env`、私钥或 token 被送入远程模型服务。 | 新增敏感路径/secret 预检、`redaction-report.json`、外发披露/确认和 high-risk needs_user 规则。 |
| ADV-PRD-005 | P0 | Review pack 完整性缺少可测覆盖率，omit 大文件/二进制/生成文件后 reviewer 可能仍给 pass。 | 新增 diff coverage、omitted line count、关键文件 omit 时 verdict 上限和 final report 披露。 |

**剩余非阻塞问题**：

1. `local-agent` 的具体 host 集成方式仍需在 `plan.md` 中选择：命令行子进程、Codex/Claude/DeepSeek/GLM 等本地 agent launcher、或用户配置的 custom command；`codex-local` 仅作为兼容 alias。
2. 是否把 attestation 纳入 CI 必检仍保持 P1 可选。
3. 多 reviewer 和 artifact 签名保持 P2。

### Round 2：AI-Native 架构师 + 技术小白对抗评审

**评审角色 A：AI-Native 架构师**

画像：在多个大型公司落地过 AI-Native 研发闭环，关注多仓推广、治理策略、artifact 稳定性、可审计性、跨版本升级和失败模式。

**评审角色 B：技术小白**

画像：不熟悉 Git、provider、artifact 和模型调用边界，只关心能不能少记命令、看懂失败原因、知道下一步做什么。

**评审结论**：第二轮发现 4 个 P0 blocker，均已在本版 PRD 中修订。

| Finding | 角色 | 严重级别 | 问题 | 修订结果 |
|---------|------|----------|------|----------|
| ADV2-ARCH-001 | AI-Native 架构师 | P0 | artifact 没有 schema version / validation / compatibility 规则，多仓落地后无法稳定审计和升级。 | 新增 schema version、schema validation、`schema-validation.json`、SC-189-015。 |
| ADV2-ARCH-002 | AI-Native 架构师 | P0 | 缺少项目级 policy profile，外发策略、round limit、close mode 和 redaction strictness 会散落在命令参数里。 | 新增 `LoopPolicyProfile`、FR-189-011/012/075、企业策略用户指南要求。 |
| ADV2-ARCH-003 | AI-Native 架构师 | P0 | Provider runner 退出码、输出路径和 allowlist 未标准化，无法在失败时形成稳定 blocker。 | 新增 FR-189-053/054/055 和 `ProviderRunnerInvocation`。 |
| ADV2-UX-001 | 技术小白 | P0 | 普通用户路径仍然太难：不知道 base、provider、外发风险和失败下一步。 | 新增 `pr-review doctor`、base 自动检测、默认 provider 指引、Result/Next/plain-language blocker 和 3 步小白路径。 |

**第二轮后仍保留到 plan 阶段的问题**：

1. `loop-policy.yaml` 是否独立于 project config，或合并进既有 project config。
2. schema 是否导出 JSON Schema 文件，或仅通过 Pydantic validation 和 tests 固化。
3. `local-agent` 具体 host 集成方式与 `--model current` 解析方式仍需在 plan 阶段实测。

## 17. Codex 开发 Agent 执行提示

后续 Codex 开发 agent 必须遵守以下顺序：

1. 以本已冻结 PRD 为需求真值，不得弱化独立 reviewer、本地 agent 默认当前模型、显式模型选择、CI 不发起模型请求、schema validation、policy profile 或小白路径。
2. 实现前必须读取并遵守 `plan.md` 与 `tasks.md`。
3. 每个任务必须绑定文件范围、验收标准和验证命令。
4. 进入实现前必须确认当前阶段允许 execute。
5. 实现必须优先完成 `mock-reviewer` 和 schema tests，再接 `local-agent` provider/model runner 合同。
6. 不得调用 Codex 云端 PR review，不得把 GitHub `@codex review` 作为实现路径。
7. 不得在 CI workflow 中加入 GPT、Claude、DeepSeek、GLM、Codex 或其他模型调用；模型调用只能由本地独立 review agent 发起。
