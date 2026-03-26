# 框架缺陷待办池（人机共读）

> 目的：把开发过程中的**框架缺陷、代理违约、门禁暴露的问题**从“观察/抱怨/会话备注”转成**可执行 backlog**，作为本仓库后续规则、门禁、CLI、workflow 与 eval 的演化输入池。

> 真值说明：自 2026-03-26 起，**新增**的框架缺陷 / 违约记录以本文件为主；[`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../src/ai_sdlc/rules/agent-skip-registry.zh.md) 保留历史审计与兼容来源，不再作为首选新增入口。

### 何时必须记录

- 用户明确要求“记录这个缺陷 / 违约 / 规则问题”。
- `verify` / `gate` / `close-check` / 其他门禁因**框架自身约束、状态漂移、规则缺口**而阻断。
- 代理自检发现自己**跳过了框架约束**、误用规则、选错真值来源，或被代码审查指出有同类问题。
- 生产问题、兼容性问题、回归问题在修复时暴露出**框架层缺口**，需要进入后续演化 backlog。

### 记录格式

- 每条记录使用 `## FD-YYYY-MM-DD-NNN | 标题`
- 条目正文使用 `- 字段: 内容`
- 必填字段：
  - `现象`
  - `触发场景`
  - `影响范围`
  - `根因分类`
  - `建议改动层级`
  - `prompt / context`
  - `rule / policy`
  - `middleware`
  - `workflow`
  - `tool`
  - `eval`
  - `风险等级`
  - `可验证成功标准`
  - `是否需要回归测试补充`
- 推荐补充字段：
  - `日期 (UTC)`
  - `来源`
  - `状态`
  - `wi_id`
  - `legacy_ref`
  - `owner`

### 字段约定

- `根因分类`：沿用 legacy registry 的 A-H 归类，可多选。
- `建议改动层级`：从 `prompt / context`、`rule / policy`、`middleware`、`workflow`、`tool`、`eval` 中选择一项或多项。
- `风险等级`：建议使用 `低 / 中 / 高 / 极高`。
- `是否需要回归测试补充`：使用 `是：...` / `否：...`。
- `状态`：建议使用 `open / planned / in_progress / closed / migrated`。

### 迁移说明

- 下列历史条目已从 legacy registry 迁移并结构化补全。
- 迁移补齐的字段若原始材料未显式给出，会以“基于历史记录推断”的方式写入，但会保留 `legacy_ref`。
- 新增条目应直接写入本文件；若需要回溯历史来源，再反向链接到 legacy registry。

## FD-2026-03-24-001 | IDE 计划待办与仓库实现事实长期漂移

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: migrated
- wi_id: 001-ai-sdlc-framework
- legacy_ref: src/ai_sdlc/rules/agent-skip-registry.zh.md（“计划待办与实现事实不对齐”节 + 2026-03-24 登记行）
- 现象: 仓库中的规则、文档与实现已更新并经过测试，但 IDE 计划文件 frontmatter 中的 `todos[].status` 仍长期停留在 `pending`，与仓库事实不一致。
- 触发场景: 开发过程中只更新仓库代码/文档，不同步更新 IDE 计划文件；或交付前只依赖会话记忆判断“已完成”。
- 影响范围: 交付状态判断、PR 审阅、close 前对账、用户对框架完成度的信任。
- 根因分类: H, A, B
- 建议改动层级: workflow, tool, eval
- prompt / context: 当用户或代理使用 IDE 计划文件辅助实施时，计划状态不得被视为“可选元数据”，而应与仓库事实对账。
- rule / policy: DoD 必须显式要求计划状态与仓库事实一致；close 前必须完成计划/任务对账。
- middleware: 为外部计划文件提供只读对账逻辑与可选关联元数据。
- workflow: 合并前执行 `plan-check`；若有漂移则先修正计划状态或登记延期原因，再继续 close。
- tool: `ai-sdlc workitem plan-check`、`ai-sdlc workitem link`
- eval: 计划漂移检出率、close 前对账覆盖率
- 风险等级: 中
- 可验证成功标准: 给定存在外部计划文件的工作项，`plan-check` 能稳定发现待办状态漂移；close 清单要求显式处理漂移。
- 是否需要回归测试补充: 是：补充 `plan-check` 与 close 对账的正反用例。

## FD-2026-03-24-002 | design 未落到 tasks 即直接进入执行

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: migrated
- wi_id: 001-ai-sdlc-framework
- legacy_ref: src/ai_sdlc/rules/agent-skip-registry.zh.md（2026-03-24 “在 design 未落到 tasks.md 前催促执行”行）
- 现象: 设计尚未完成 decompose、`tasks.md` 未形成带验收标准的可执行任务时，执行侧仍倾向直接改产品代码。
- 触发场景: 对话或规划阶段把“方案已经想清楚”误当成“仓库阶段已可执行”；或把宿主计划文件与仓库阶段真值混淆。
- 影响范围: 阶段顺序失真、任务不可追溯、测试与验收缺失、执行阶段边做边改设计。
- 根因分类: A, C
- 建议改动层级: prompt / context, rule / policy, workflow, tool
- prompt / context: 宿主规划或会话提纲不等于仓库内 decompose 完成，执行前必须有法定 `tasks.md` 产物。
- rule / policy: 明确“规划收敛后的法定下一步是 decompose，不是 execute”。
- middleware: execute 前增加基于 `tasks.md` 的硬前置校验。
- workflow: 先补 `spec.md` / `plan.md` / `tasks.md`，再验证，再执行。
- tool: `gate check decompose`、`verify constraints`
- eval: 执行前缺任务级验收的阻断率
- 风险等级: 高
- 可验证成功标准: 缺少 `tasks.md` 或任务级 AC 时，decompose/execute 相关门禁必须非零阻断，且提示首个不合规任务。
- 是否需要回归测试补充: 是：补充 decompose gate、execute prerequisite 与 verify constraints 的一致性测试。

## FD-2026-03-24-003 | 未完成全量验证即声称交付

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: migrated
- wi_id: 001-ai-sdlc-framework
- legacy_ref: src/ai_sdlc/rules/agent-skip-registry.zh.md（2026-03-24 “未先跑全量 pytest 即声称交付”行）
- 现象: 在未完成仓库约定的全量验证、阶段收口与证据落盘前，就基于局部变更或主观判断声称“已完成”。
- 触发场景: 文档/规则类改动被误判为“无需完整验证”；或疲劳、赶进度时跳过最终验证。
- 影响范围: 完成状态失真、回归缺陷、审阅成本上升、用户对代理输出可信度下降。
- 根因分类: A, B
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: 任何完成性表述都必须有新鲜验证证据支撑，不区分代码变更还是规则/文档变更。
- rule / policy: 完成前验证协议必须覆盖文档类变更；无验证证据不得声称完成。
- middleware: 只读检查与 close 清单应能承接文档/规则类验证要求。
- workflow: 合并前执行 `pytest`、`ruff`、`verify constraints` 等仓库约定命令，并在必要时落盘执行证据。
- tool: `uv run pytest`、`uv run ruff check src tests`、`ai-sdlc verify constraints`
- eval: “声称完成但缺验证证据”事件数
- 风险等级: 高
- 可验证成功标准: PR/交付前清单与规则均要求新鲜验证证据；相关测试或流程检查能阻止无证据完成声明。
- 是否需要回归测试补充: 是：补充文档变更与规则变更下的 verify/close-check 覆盖。

## FD-2026-03-25-001 | 收口动作与文档事实未同步闭环

- 日期 (UTC): 2026-03-25
- 来源: migrated_from_legacy_registry
- 状态: migrated
- wi_id: 001-ai-sdlc-framework
- legacy_ref: src/ai_sdlc/rules/agent-skip-registry.zh.md（2026-03-25 FR-087/088/089 收口漂移行）
- 现象: 功能实现已存在，但 `execution-log`、code review 记录、git 提交、用户手册等收口材料未在同一迭代及时同步，导致“实现事实”和“文档/归档事实”分叉。
- 触发场景: 先实现并测试，再把归档、文档、commit、push 当作稍后补做事项。
- 影响范围: close 阶段、审计追溯、版本说明、用户手册可信度。
- 根因分类: A, B, H
- 建议改动层级: workflow, rule / policy, tool
- prompt / context: 完成功能 ≠ 完成收口；归档、审查、文档同步、提交属于同一批次的法定尾部动作。
- rule / policy: “归档先于继续”“完成前必须验证”要覆盖文档/指南同步与 commit 收口。
- middleware: close-check / verify constraints 负责只读核对收口材料的结构一致性。
- workflow: 批次完成后先更新 execution-log、文档、checklist，再提交；不允许长期积压“收口 TODO”。
- tool: `ai-sdlc workitem close-check`、`ai-sdlc verify constraints`
- eval: 收口漂移项数量、文档与实现一致性缺陷数
- 风险等级: 中
- 可验证成功标准: close-check 与清单能够在收口遗漏时发出明确 BLOCKER；文档与实现事实不再长期漂移。
- 是否需要回归测试补充: 是：补充 close-check 与用户手册一致性的验证用例。

## FD-2026-03-26-001 | 用户要求“先落需求再实现”时仍默认进入编码

- 日期 (UTC): 2026-03-26
- 来源: migrated_from_legacy_registry
- 状态: migrated
- wi_id: 001-ai-sdlc-framework
- legacy_ref: src/ai_sdlc/rules/agent-skip-registry.zh.md（2026-03-26 回顾行）
- 现象: 即使用户明确要求“先按框架约束把优化项转成需求/plan/tasks，再决定是否动手”，执行侧仍易下意识直接进入代码改动。
- 触发场景: 用户给出优化想法或规则反馈，代理把它误解成“默认要立刻编码”的实现请求。
- 影响范围: 需求治理、阶段顺序、规格一致性、用户控制权。
- 根因分类: A, B, C
- 建议改动层级: prompt / context, rule / policy, workflow, eval
- prompt / context: 用户强调“先文档/先需求”时，默认动作必须切换到 design/decompose，而非 execute。
- rule / policy: 把“文档契约先于实现”“用户显式要求先落盘时禁止直接编码”写入主规则。
- middleware: 执行前校验当前任务是否属于“仅文档/仅需求沉淀”范围。
- workflow: 先完成 `spec.md` / `plan.md` / `tasks.md` 或等价 backlog 条目，再决定是否进入实现。
- tool: `stage run design`、`stage run decompose`、`verify constraints`
- eval: 用户明确要求“先落盘”场景下的违规率
- 风险等级: 高
- 可验证成功标准: 在“仅文档 / 先需求”指令下，规则文本与流程检查均指向 design/decompose，且不鼓励直接修改代码。
- 是否需要回归测试补充: 是：补充规则文本与执行前判定的覆盖。

## FD-2026-03-26-002 | CLI 升级后无法认领旧产物，流水线长期停留在 init

- 日期 (UTC): 2026-03-26
- 来源: user_report
- 状态: open
- owner: codex
- related_doc: docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md
- 现象: 旧版本 CLI 已生成 `product-requirements.md`、`spec.md`、`research.md`、`data-model.md`、`plan.md`、`tasks.md` 等产物，但升级到 `0.2.4` 后重新执行 `ai-sdlc`，`status` / `recover` / `run --dry-run` 仍停留在 `init`，`Feature ID` 为 `unknown`。
- 触发场景: 用户在其他生产环境用旧版本 CLI 开发一段时间后，本地重新下载 `0.2.4` 并在原项目上继续执行 `ai-sdlc`。
- 影响范围: 旧项目升级兼容性、断点恢复、阶段推进、现有产物复用、生产问题修复效率。
- 根因分类: E, D, B
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 规则文本承认“已有产物可从下一阶段开始”，但 Runner/CLI 不会自动根据已有产物回填 checkpoint；同时旧版根目录布局与新版 `specs/<WI>/` 假设存在断层。
- rule / policy: 明确“已有产物例外”的正式落地路径，并规定旧版状态文件与新版 checkpoint 的兼容迁移策略。
- middleware: 增加 checkpoint reconcile / recover backfill 逻辑，兼容旧版根目录布局与旧状态字段。
- workflow: 升级后先执行状态对齐，再运行 gate / stage / recover；不得要求用户手工编辑多份状态文件。
- tool: `ai-sdlc recover`、`ai-sdlc status`、`ai-sdlc run`、`ai-sdlc stage run`
- eval: 旧项目升级后的恢复成功率、误报 `init/unknown` 的发生率
- 风险等级: 高
- 可验证成功标准: 给定“旧版根目录产物 + 过时/空白 checkpoint”的夹具，CLI 能识别真实阶段或提供显式 reconcile 入口，使 `status/recover/run` 不再长期停留于 `init/unknown`。
- 是否需要回归测试补充: 是：补充根目录旧布局、旧 `project-state.yaml` 字段、空白 checkpoint、stale checkpoint 的兼容回归测试。
