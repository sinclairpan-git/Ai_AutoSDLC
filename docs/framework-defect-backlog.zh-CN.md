# 框架缺陷待办池（人机共读）

> 目的：把开发过程中的**框架缺陷、代理违约、门禁暴露的问题**从“观察/抱怨/会话备注”转成**可执行 backlog**，作为本仓库后续规则、门禁、CLI、workflow 与 eval 的演化输入池。

> 真值说明：自 2026-03-26 起，**新增**的框架缺陷 / 违约记录以本文件为主；[`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../src/ai_sdlc/rules/agent-skip-registry.zh.md) 保留历史审计与兼容来源，不再作为首选新增入口。

### 何时必须记录

- 用户明确要求“记录这个缺陷 / 违约 / 规则问题”。
- `verify` / `gate` / `close-check` / 其他门禁因**框架自身约束、状态漂移、规则缺口**而阻断。
- 代理自检发现自己**跳过了框架约束**、误用规则、选错真值来源，或被代码审查指出有同类问题。
- 生产问题、兼容性问题、回归问题在修复时暴露出**框架层缺口**，需要进入后续演化 backlog。
- 即使该违约 / 缺陷**已被门禁、review 或自检及时拦下，并在当前迭代内完成修复**，只要它曾真实出现过且暴露了框架缺口，仍必须记录；不得因为“已经修好”而只留会话备注、不进 backlog。

### 记录格式

- 每条记录使用 `## FD-YYYY-MM-DD-NNN | 标题`
- 条目正文使用 `- 字段: 内容`
- 必填字段：
  - `现象`
  - `触发场景`
  - `影响范围`
  - `根因分类`
  - `未来杜绝方案摘要`
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
- `未来杜绝方案摘要`：用 1-3 句概括“以后靠什么约束/机制杜绝同类问题再发生”；详细落地仍应展开到 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 字段。
- `建议改动层级`：从 `prompt / context`、`rule / policy`、`middleware`、`workflow`、`tool`、`eval` 中选择一项或多项。
- `风险等级`：建议使用 `低 / 中 / 高 / 极高`。
- `是否需要回归测试补充`：使用 `是：...` / `否：...`。
- `状态`：建议使用 `open / planned / in_progress / closed / migrated`。
- 若条目对应的是“已被拦截且已修复”的违约，`状态` 可记为 `closed`，但正文仍必须写清：`现象`、`根因分类`、`未来杜绝方案摘要`，以及未来如何杜绝同类问题再次出现（应落到 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 等字段）。

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

## FD-2026-03-27-001 | manual telemetry 录入面可伪造 runtime 生命周期与 scope 链

- 日期 (UTC): 2026-03-27
- 来源: self_review, code_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: `ai-sdlc telemetry` 的手工录入面最初允许直接写入从未打开过的 `goal_session_id / workflow_run_id / step_id`，也允许手工事件伪装成 `workflow + framework_runtime + auto` 的 runtime 生命周期事件，进而绕过 session close 的 open-run 守卫。
- 触发场景: 在 Task 4 落地 `open-session / record-event / record-evidence / close-session` 时，只校验了对象 schema，没有把“手工补记”和“runtime 真值写入”做硬隔离。
- 影响范围: telemetry 真值污染、workflow 生命周期伪造、source closure 前提失真、后续 evaluation/violation 生成依据被污染。
- 根因分类: A, B, D
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: “允许人工补记”不等于“允许人工重写 framework runtime 真值”；manual surface 必须被描述成补记层，不是生命周期主写层。
- rule / policy: 明确手工 telemetry 只能写已存在 scope 链，且不得写 runtime-owned lifecycle 形状；凡绕过该边界的实现均视为框架违约。
- middleware: 在 runtime/telemetry facade 中统一校验 session 是否 open、run/step 是否已存在、session 是否已 closed、以及 manual event 是否伪装成 runtime 生命周期。
- workflow: Task 级 code review 默认把“manual 命令能否造假 session/run/step 或关闭未关闭 run”作为必查项。
- tool: `ai-sdlc telemetry open-session`、`ai-sdlc telemetry record-event`、`ai-sdlc telemetry record-evidence`、`ai-sdlc telemetry close-session`
- eval: manual telemetry forged-scope 拦截率、runtime-owned lifecycle 伪造阻断率
- 风险等级: 高
- 可验证成功标准: 手工 telemetry 命令只能写入已存在且仍 open 的合法 scope 链；`record-event` 不能伪装 `workflow/framework_runtime/auto`；`close-session` 不得在 runtime run 未闭合时成功，也不得被手工 run 事件欺骗。
- 是否需要回归测试补充: 是：补充 fresh session/run/step 伪造、closed session 二次写入、runtime lifecycle 伪造、manual run 事件绕过 close-session 的正反用例。

## FD-2026-03-27-002 | verify telemetry 接入时易引入 session 生命周期悬空与 JSON contract 漂移

- 日期 (UTC): 2026-03-27
- 来源: self_review, code_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: `verify constraints` 接 telemetry 后，初版实现会自动打开 telemetry session 但不写 terminal session event，留下 dangling session；同时 `--json` 的非项目路径错误输出一度丢失固定字段 `root`，破坏既有 JSON shape。
- 触发场景: 在 Task 5 把 `verify constraints` 接成 evaluation-layer event/evidence/evaluation/violation 时，只关注治理对象生成，没有同时把自动 source 的 session 生命周期与 JSON 对外契约当成同等级 contract 维护。
- 影响范围: 自动 telemetry source 的生命周期失真、session 累积悬空、机器消费端 schema 不稳定、后续 summary/publisher 读取风险增加。
- 根因分类: A, B, H
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: 给现有命令挂 telemetry 时，必须把“命令外部契约”和“telemetry 内部生命周期”同时视为冻结边界，不能只顾新增对象落盘。
- rule / policy: 任何自动 telemetry source 都必须在同一命令内写完 session terminal event；现有 `--json` surface 扩展字段时不得删除既有保底字段。
- middleware: 为 CLI telemetry hook 提供统一的 auto-session open/close helper，并为 JSON surface 提供 shape-preserving builder，避免手写分支输出。
- workflow: Task 级 review 默认检查两件事：自动 source 是否留下 dangling session；JSON/text 兼容字段是否被破坏。
- tool: `ai-sdlc verify constraints --json`
- eval: auto-session dangling 发生率、JSON shape 兼容性回归数
- 风险等级: 中
- 可验证成功标准: `verify constraints` 每次运行后 session event stream 都以 terminal workflow session event 结束；非项目路径与项目路径的 `--json` 输出均稳定包含 `ok`、`blockers`、`root`。
- 是否需要回归测试补充: 是：补充 verify telemetry session terminal event、out-of-project JSON shape、violation telemetry 落盘的集成回归测试。

## FD-2026-03-27-003 | telemetry artifact contract 漏掉 source refs，source closure 无法成立

- 日期 (UTC): 2026-03-27
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: design baseline 已冻结 artifact publish 必须经过 `source_evidence_refs / source_object_refs` 的最小 source closure 校验，但当前实现里的 `Artifact` contract 还没有这些字段，导致 artifact 即使落盘，也没有规范化来源闭包可供 publisher 校验。
- 触发场景: 进入 Task 6 准备实现 `governance_publisher` 时，按 spec 逆查 contract 与 writer 路径，发现 source closure 依赖已经写进设计与计划，但对象模型未同步冻结到代码。
- 影响范围: published gating 无法基于 canonical contract 执行，artifact status 降级逻辑缺少真值输入，summary/audit 产物的可追溯性不足。
- 根因分类: A, B, D
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: source closure 不是 publisher 里的临时逻辑，而是 artifact contract 的一部分；只在实现阶段补逻辑、不先补 contract，会让 writer 和 resolver 无法共享同一真值。
- rule / policy: 凡 spec 已冻结的 contract 字段，进入对应 task 前必须先核对代码单一来源是否齐全；缺字段不得继续写上层功能。
- middleware: 在 telemetry contracts/writer 层补 `source_evidence_refs / source_object_refs` 与 canonical validation，确保 publisher 只消费 contract，不再自造 side payload。
- workflow: Task 开始前的自检清单加入“spec 冻结字段是否已进入 contract 单一来源”的检查，避免设计边界在任务切换时漂移。
- tool: `src/ai_sdlc/telemetry/contracts.py`、`src/ai_sdlc/telemetry/writer.py`、`src/ai_sdlc/telemetry/governance_publisher.py`
- eval: source-closure contract 漂移数、publisher 前置 contract 缺口发现率
- 风险等级: 高
- 可验证成功标准: artifact contract 明确携带 source refs；publisher 能据此完成 source closure 正反校验；published artifact 失去有效来源时会降级。
- 是否需要回归测试补充: 是：补充 artifact source refs 必填/解析、closure 成功发布、closure 失效降级的正反测试。

## FD-2026-03-27-004 | governance publishing 初版遗漏 writer 级 publish 守卫，且 audit verdict 对 failed evaluation 存在盲区

- 日期 (UTC): 2026-03-27
- 来源: self_review, code_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: Task 6 首版实现虽然引入了 `GovernancePublisher`，但 `TelemetryWriter.write_artifact()` 仍允许业务侧直接持久化 `status=published` 的 artifact，绕过 source closure；同时 `build_audit_report()` 在存在 failed evaluation 但尚未升级出 violation 时，会把 audit verdict 误判为 `clean`。
- 触发场景: 对 `0a8f12a` 做 spec review 时，按 design baseline 逆查 writer 责任边界与 audit verdict 优先级，发现 source closure 只在 publisher 层守卫，audit 结论又只看 open violation，而没有把 failed evaluation 本身视为 `issues_found`。
- 影响范围: published artifact 可被非法写入，source closure 真值不再由 writer 统一保障；audit_report 会低报治理风险，误把存在失败评测的 run/session 归类为 `clean`。
- 根因分类: A, B, D
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: “有 publisher”不等于“writer 边界已守住”；同样，“有 violation 才算有问题”也不等于 audit 可忽略 failed evaluation。Task 级实现必须同时满足 writer 守卫和 verdict 语义。
- rule / policy: 将 `published` 只能经 source closure 守卫写入、以及 failed evaluation 至少应使 audit 进入 `issues_found` 的语义继续视为冻结边界。
- middleware: 在 writer 层拒绝无预检查上下文的非法 `published` 写入；在 generator 层把 failed / warning evaluation 纳入 audit verdict 推导。
- workflow: Task 级 spec review 默认检查“是否仍可绕过 publisher 直接写 published”与“failed evaluation 无 violation 时 audit 是否仍为 clean”。
- tool: `src/ai_sdlc/telemetry/writer.py`、`src/ai_sdlc/telemetry/generators.py`、`src/ai_sdlc/telemetry/governance_publisher.py`
- eval: illegal published bypass 次数、failed-evaluation-clean 误判次数
- 风险等级: 高
- 可验证成功标准: 直接 `write_artifact(status=published)` 在来源闭包不成立时被拒绝；存在 failed / warning evaluation 且无高风险 block 时，audit verdict 至少为 `issues_found`，不会回落到 `clean`。
- 是否需要回归测试补充: 是：补充 writer bypass negative case、failed evaluation audit verdict、warning evaluation audit verdict 的回归测试。

## FD-2026-03-27-005 | governance report 生成初版语义不完整：遗漏 violation_summary，downgrade 后报告状态会陈旧，且非终态 evaluation 易被误判为 clean

- 日期 (UTC): 2026-03-27
- 来源: self_review, code_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: Task 6 初版 `generate_run_reports()` 只生成 `evaluation_summary` 与 `audit_report`，缺少独立 `violation_summary` 报告；同时已发布 artifact 在 `revalidate_published_artifacts()` 中被降级后，`.ai-sdlc/project/reports/telemetry/` 下对应 JSON 报告仍保留 `artifact_status=published`、`source_closure_ok=true` 的旧值；此外当前 summary 语义对 `pending / waived / not_applicable` 等非终态或非通过 evaluation 处理不完整，可能把并不应视为 clean 的 run/session 误判成 `clean`，或让 `evaluation_summary` 内部统计自相矛盾。
- 触发场景: 对 `0a8f12a` 做 Task 6 spec review 时，按 design baseline 对照 `source closure`、summary generators 与 canonical report 行为，发现生成器只满足了部分 happy path，用例未覆盖降级后的报告重写与 summary 语义完整性。
- 影响范围: operator 读取 canonical governance report 时会看到过期 published 状态；V1 缺少独立 `violation_summary` 产物；`evaluation_summary` 与 `audit_report` 对 coverage/evidence/非终态语义表达不完整，影响 audit 与后续 bounded status surfaces 的可信度。
- 根因分类: A, B, H
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: Task 6 不只是“能写一份 report JSON”，而是要形成一组可被后续 status/doctor 消费的 canonical governance artifacts；降级后不回写报告、或只生成部分 summary，都属于 V1 语义不完整。
- rule / policy: `evaluation_summary`、`violation_summary`、`audit_report` 作为 V1 最小治理产物必须同时成立；artifact 状态变化后 canonical report 必须与 snapshot 同步。
- middleware: 在 governance publisher 中集中维护 artifact snapshot 与 report JSON 的一致性；summary generator 统一产出 coverage / evidence quality / open debt 视图，避免由下游 CLI 临时拼装。
- workflow: Task 级 spec review 默认检查“降级后 report 是否同步改写”“是否存在独立 violation_summary”“evaluation_summary 是否包含 coverage/evidence 视图”，代码质量 review 默认检查 `pending / waived / not_applicable` 是否被误渲染成 clean/pass。
- tool: `src/ai_sdlc/telemetry/governance_publisher.py`、`src/ai_sdlc/telemetry/generators.py`
- eval: stale-governance-report 次数、missing-violation-summary 次数、evaluation-summary-semantic-gap 次数、non-terminal-clean-misclassification 次数
- 风险等级: 中
- 可验证成功标准: downgrade 后 artifact snapshot 与 report JSON 状态一致；run 级 canonical artifacts 至少包含 `evaluation_summary`、`violation_summary`、`audit_report`；`evaluation_summary` 包含 coverage 与 evidence quality 的最小聚合字段；`pending / waived / not_applicable` 不会被 audit 或 summary 误判为 clean/pass。
- 是否需要回归测试补充: 是：补充 downgrade report rewrite、standalone violation_summary 生成、evaluation_summary coverage/evidence 视图的回归测试。

## FD-2026-03-27-006 | status --json 仍会经全局 IDE hook 产生写入，破坏 bounded/read-only 语义

- 日期 (UTC): 2026-03-27
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: Task 7 为 `status --json` 增加了 bounded telemetry JSON surface，但 CLI 全局 callback 仍会在 `status` 子命令执行前触发 `run_ide_adapter_if_initialized()`，而该 hook 会调用 `ensure_ide_adaptation()` 持久化 `.ai-sdlc/project/config/project-config.yaml`，使 `status --json` 仍然带有文件写副作用。
- 触发场景: 对 `a2285b6` 做本地 review 时，逆查 `status --json` 执行路径，发现虽然 readiness 逻辑本身不做 telemetry init/rebuild，但命令外围的 IDE adaptation hook 依旧生效。
- 影响范围: `status --json` 的 bounded/read-only 契约被破坏；运维和自动化可能在“只想读状态”时意外改写项目配置；测试若只 patch 掉 hook，容易掩盖真实执行路径。
- 根因分类: A, B, D
- 未来杜绝方案摘要: 把 read-only surface 的“不得隐式写入”约束前移到 CLI 全局 hook 层，并要求 `status --json` / `doctor` 的真实 CLI 路径无写入回归测试长期保留。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: bounded status/doctor surface 不只是“telemetry 不落盘”，还应避免命令外围的其他写副作用；全局 hook 也必须服从只读诊断边界。
- rule / policy: 将 `status --json` / `doctor` 视为只读运维面；任何会落盘的 hook 都不得在这些命令前隐式执行。
- middleware: 在 CLI 全局 callback 中把 `status`（至少 `status --json`）与 `doctor` 排除出 IDE adaptation 写路径，或为 hook 增加显式只读模式。
- workflow: Task 级 review 默认检查“命令本体虽只读，但外围 hook 是否仍可能写文件”。
- tool: `src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/cli_hooks.py`、`src/ai_sdlc/integrations/ide_adapter.py`
- eval: read-only command side-effect 次数、status-json write-side-effect 次数
- 风险等级: 中
- 可验证成功标准: 执行 `status --json` 和 `doctor` 前后，不会新增或改写 IDE adapter / project-config 相关文件；同时仍保持 telemetry `not_initialized` 不隐式创建。
- 是否需要回归测试补充: 是：补充 `status --json` 与 `doctor` 在真实 CLI 路径下不触发 IDE adaptation 写入的回归测试。

## FD-2026-03-27-007 | Task 7 readiness 初版存在 latest/current 指向失真，resolver health 先是假阳性、后又先后出现越界 deep scan 与过窄 probe 假 warn

- 日期 (UTC): 2026-03-27
- 来源: self_review, code_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: `status --json` 的 `latest.artifacts.sample_ids` 起初取的是 `latest-artifacts.json` 的尾部切片，而该索引本身是 newest-first，导致 latest sample 实际上可能返回最旧的一段；随后又暴露出 `latest_goal_session_id / latest_workflow_run_id / latest_step_id` 直接取 manifest dict key 的“最后一个”条目，在 manifest 重写/重载后会丢失真实 recency 语义。同时 `doctor` 的 `resolver health` 检查先是只调用 `resolve(\"unsupported\", ...)` 并把预期的 `ValueError` 视为健康，后续修补为正向解析时又先后出现递归扫描 `events.ndjson` 的 deep scan 越界，以及只探测极少数 manifest 候选 path、导致存在合法 fixture 时仍报 `warn` 的过窄 probe。
- 触发场景: 对 Task 7 的 readiness surface 做 spec review 时，按 store/index 真值和 doctor readiness 要求逆查 `readiness.py`，发现 latest sample 语义与 index 顺序不一致，resolver health 也只验证了拒绝路径。
- 影响范围: `status --json` 的 latest/current 区域会误导运维判断当前与最近 scope；`doctor` 可能把实际损坏的 resolver 误报为 `ok`，或为了一次 health check 而退化成不受控 trace 扫描，或在存在合法 fixture 时误报 `warn`，削弱 readiness 诊断价值并突破 bounded surface 约束。
- 根因分类: A, B, H
- 未来杜绝方案摘要: 将 bounded readiness 的 latest/current 真值与 resolver health 都收敛到共享 helper，禁止为 health check 解析真实 trace payload；Task 级 review 默认核查 recency 依据、探针边界和假阳性/假 warn 风险。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: bounded summary 不只是“字段数量受限”，还必须保持 latest/current 指向的真值方向正确；health check 也必须触达正向路径，但正向路径的验证既不能靠全量 trace 扫描补正确性，也不能缩到只看极少数候选而放过 manifest 已知的合法来源。
- rule / policy: `latest` 采样必须遵循权威 index 的排序语义；`health/readiness` 检查至少覆盖一条真实支持路径。
- middleware: readiness helper 中 latest sample 统一按权威索引顺序切片；resolver health 通过最小合法 source fixture 走一次正向解析，不再以 unsupported guard 代替健康检查。
- workflow: Task 级 spec/code review 默认检查“latest sample 是否和 index 顺序一致”“latest/current id 是否有真实 recency 依据”“health check 是否真正覆盖正向路径”，并额外检查“该正向路径是否仍保持 bounded probe，而不是深扫本地 trace，且不会因为候选过窄而误报 warn”。
- tool: `src/ai_sdlc/telemetry/readiness.py`、`tests/integration/test_cli_status.py`、`tests/integration/test_cli_doctor.py`
- eval: latest-sample-ordering-error 次数、latest-current-id-mispoint 次数、resolver-health-false-positive 次数、resolver-health-deep-scan 次数、resolver-health-false-warn 次数
- 风险等级: 中
- 可验证成功标准: `status --json` 的 latest artifact sample 与 `latest-artifacts.json` 的 newest-first 语义一致；`latest_goal_session_id / latest_workflow_run_id / latest_step_id` 基于可辩护的 recency 信号而不是 dict 顺序；`doctor` 的 resolver health 至少验证一个受支持 source kind 的成功解析，且该验证通过 manifest/index 驱动的 bounded probe 完成，不递归扫描全部 trace，也不会在 manifest 已知存在合法 fixture 时误报 `warn`。
- 是否需要回归测试补充: 是：补充 latest sample 顺序和 resolver health 正向解析的回归测试。

## FD-2026-03-27-008 | status --json 的真实 CLI 合同与 doctor readiness 检查再次分叉

- 日期 (UTC): 2026-03-27
- 来源: spec_review, self_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: `status --json` 的 telemetry surface 虽然已经有 helper，但真实 CLI 路径仍先检查 `project-state.yaml` 是否为 `uninitialized` 并直接 exit 1，导致“项目存在但未初始化”时拿不到 JSON；与此同时 `doctor` 的 `status --json surface` 检查绕过真实命令路径，直接调用 helper 并报告 `ok/not_initialized`，两者对同一 surface 给出了相互矛盾的结论。
- 触发场景: 对 Task 7 的 spec review 在真实 CLI 路径上复现“project found but uninitialized”场景时，发现 `status --json` 与 doctor readiness 对 surface availability 的判断不一致。
- 影响范围: 运维和自动化无法稳定依赖 `status --json` 读取 telemetry readiness；`doctor` 会把实际上不可达的 JSON surface 误报为可用，破坏只读诊断面的可信度。
- 根因分类: A, B, H
- 未来杜绝方案摘要: 将 `status --json` 的真实 CLI 合同收敛到单一 helper，并要求 doctor 的 surface 检查复用同一合同；新增“uninitialized project 仍可返回 bounded JSON”与“doctor/CLI 合同一致”的回归测试，防止 helper 与命令外围分支再次漂移。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: bounded operator surface 的真值不应由“内部 helper 能调用”代替“真实 CLI 是否可达”；命令外围分支和 doctor readiness 必须共享同一合同。
- rule / policy: `status --json` 在 telemetry 缺失时可返回 `not_initialized`，且该 contract 适用于项目存在但 project-state 仍为 `uninitialized` 的场景；doctor 检查的 surface availability 必须与真实 CLI 行为一致。
- middleware: 抽取共享的 bounded status surface builder / availability contract，供 `status` 命令与 doctor readiness 共同复用，避免外围 gate 与内部 helper 分叉。
- workflow: Task 级 spec/code review 默认检查“readiness helper 是否绕过真实命令路径”以及“CLI 对外合同是否与 doctor 判断一致”。
- tool: `src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/telemetry/readiness.py`、`tests/integration/test_cli_status.py`、`tests/integration/test_cli_doctor.py`
- eval: status-surface-contract-drift 次数、doctor-surface-false-availability 次数
- 风险等级: 中
- 可验证成功标准: 当项目根存在但 `project-state.yaml` 仍为 `uninitialized` 时，`ai-sdlc status --json` 仍返回 bounded telemetry JSON 且 `telemetry.state=not_initialized`；`doctor` 对 `status --json surface` 的状态与真实 CLI 行为保持一致。
- 是否需要回归测试补充: 是：补充 uninitialized project 下 `status --json` 可达、doctor surface 检查与真实 CLI 行为一致的回归测试。

## FD-2026-03-27-009 | backlog 关单时批量状态替换误伤无关历史条目，被 diff 复核拦下

- 日期 (UTC): 2026-03-27
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: 在关闭 Task 7 对应的 `FD-006/007/008` 时，使用了过宽的状态替换补丁，误把无关的历史条目 `FD-2026-03-26-002` 一并改成 `closed`；问题在提交前通过 `git diff` 人工复核被发现并立即纠正，没有进入新的 commit 历史。
- 触发场景: 对 backlog 文档执行批量文本替换时，只按 `- 状态: open` 模式做局部修改，没有把标题或 work item 上下文纳入补丁定位条件。
- 影响范围: 若未被复核拦下，会造成无关历史缺陷状态失真，削弱 backlog 作为框架真值台账的可信度。
- 根因分类: A, B
- 未来杜绝方案摘要: 对 backlog 状态变更一律采用“按标题上下文定点修改 + 提交前 diff 复核”的方式，不再对裸 `状态` 行做无上下文批量替换；继续把文档收口前的 `git diff` 检查视为硬步骤。
- 建议改动层级: workflow, tool, eval
- prompt / context: backlog 关单是台账真值修改，不是普通文本清理；任何批量补丁都必须带上下文锚点。
- rule / policy: 对台账状态变更禁止无上下文批量替换；至少要以条目标题或唯一 ID 作为修改锚点。
- middleware: 如后续引入 backlog 自动化编辑，应提供按条目 ID 定位的更新接口，避免自由文本替换。
- workflow: backlog 收口前固定执行 `git diff` 复核，重点检查是否误伤无关条目。
- tool: `git diff`、`git add -p` 或等价的定点变更流程
- eval: backlog-status-collateral-edit 次数、提交前误伤拦截率
- 风险等级: 低
- 可验证成功标准: 后续 backlog 关单仅修改目标条目；若出现误伤，必须在提交前被 diff 复核拦下并修正。
- 是否需要回归测试补充: 否：当前更适合用流程约束和 diff 复核兜底，而不是为纯文档编辑引入自动化测试。

## FD-2026-03-27-010 | telemetry 本地运行态目录未忽略，CLI smoke 会直接弄脏工作树

- 日期 (UTC): 2026-03-27
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: 在 Task 8 smoke 中执行 `verify constraints --json` 后，仓库工作树出现未跟踪的 `.ai-sdlc/local/telemetry/**`，说明 telemetry 本地运行态目录没有被 Git 忽略；如果不手动清理，`git status` 会把正常 smoke 误呈现为脏工作树。
- 触发场景: 在项目根上用真实 CLI 路径执行 `verify constraints --json`，命令会写入本地 telemetry manifest 和 session event/evidence stream。
- 影响范围: 工作树整洁性、收口前状态判断、review 对“是否还有未归档变更”的辨识；也会增加误提交本地运行态文件的风险。
- 根因分类: A, B
- 未来杜绝方案摘要: 将 `.ai-sdlc/local/` 视为本地运行态目录并默认加入忽略规则；把“执行真实 CLI smoke 后 `git status` 仍保持干净”继续作为收口检查项。
- 建议改动层级: rule / policy, workflow, tool
- prompt / context: telemetry 的本地真值可以存在于项目目录，但不应进入版本库候选集；运行态文件和设计/代码产物要有不同的 Git 语义。
- rule / policy: `.ai-sdlc/local/` 归类为本地运行态目录，默认不进入版本控制；真实 CLI smoke 后必须复核工作树是否仍然干净。
- middleware: 需要本地 telemetry 的命令仍按原路径写入，但依赖忽略规则隔离版本控制影响。
- workflow: Task 级 smoke 后固定执行 `git status`；若本地运行态目录未被忽略，需先修复忽略规则或清理再继续收口。
- tool: `.gitignore`、`git check-ignore`、`git status`
- eval: telemetry-local-dirty-worktree 次数、smoke-after-status-clean 通过率
- 风险等级: 低
- 可验证成功标准: `.gitignore` 能匹配 `.ai-sdlc/local/**`；执行 `verify constraints --json` 后，`git status` 不再显示 telemetry 本地运行态目录为未跟踪/已修改文件。
- 是否需要回归测试补充: 否：当前通过真实 CLI smoke + `git status` / `git check-ignore` 复核更贴近问题本身。

## FD-2026-03-27-011 | source closure 父链校验过严，run 级 artifact 无法引用同 run 下的 step 级来源

- 日期 (UTC): 2026-03-27
- 来源: final_review
- 状态: open
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: 当前 `governance_publisher` / `writer` 的 source closure 校验要求 artifact 与其 source 在 `step_id` 上完全相等，导致 run 级 artifact 一旦引用同一 `workflow_run_id` 下的 step 级 evidence/evaluation，就会被误判为跨链，无法从 `generated` 提升到 `published`。
- 触发场景: final review 复现 run 级 report 引用 step 级 evidence/evaluation 的合法父链时，发布仍被拒绝。
- 影响范围: V1 的 run 级治理产物可追溯性被削弱；publisher 无法接受同 run 子步骤来源，source closure 语义比设计要求更窄。
- 根因分类: A, B, D
- 未来杜绝方案摘要: 将 source closure 的父链判断从“完全等值”收敛到“source 属于 artifact 父链之下的合法后代链”，并补 run->step 正向发布回归测试，防止父链兼容性再次被实现成严格相等。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: artifact 的作用域允许高于其来源作用域；同一 session/run 下的子步骤来源应视为合法闭包，而不是跨链。
- rule / policy: source closure 允许父级 artifact 引用同父链下的子级 source，但仍禁止跨 session/run 的引用。
- middleware: writer/publisher 统一使用“前缀父链兼容”而非“step_id 全等”的校验逻辑。
- workflow: final review / publisher 相关测试默认覆盖 session->run、run->step 的合法闭包，以及真正跨链的拒绝用例。
- tool: `src/ai_sdlc/telemetry/governance_publisher.py`、`src/ai_sdlc/telemetry/writer.py`
- eval: legal-descendant-source-rejected 次数、cross-chain-source-bypass 次数
- 风险等级: 高
- 可验证成功标准: run 级 artifact 能发布引用同 run 下 step 级 source 的合法闭包；跨 session/run 的 source 仍被拒绝。
- 是否需要回归测试补充: 是：补充 run->step source closure 正例与真正跨链负例。

## FD-2026-03-27-012 | CCP registry 冻结了 gate/audit 控制点，但 raw trace 里无法证明这些控制点

- 日期 (UTC): 2026-03-27
- 来源: final_review
- 状态: open
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: CCP registry 已冻结 `gate_hit`、`gate_blocked`、`audit_report_generated` 等 V1 控制点，但当前持久化的 `TelemetryEvent` 与 runtime/publisher 写入路径没有对应的 gate/audit 事件形状或最小证据引用，导致 coverage evaluator 无法从 raw trace 证明这些控制点是否真的发生。
- 触发场景: final review 逆查 registry、contracts 与 runtime/publisher 写入路径时，发现 registry 声明的控制点在 persisted trace 中没有可对账的事件表达。
- 影响范围: V1 coverage evaluator 对关键控制点的结论不可信；设计文档要求的“自动采关键控制点 + coverage evaluator”在 gate/audit 维度上无法闭环。
- 根因分类: A, B, H
- 未来杜绝方案摘要: 让 CCP registry 与 raw trace 事件模型保持一一可表示关系，为 gate/audit 类控制点补最小事件形状和证据引用，并用 coverage 测试证明 registry 中的 required CCP 都能从 persisted trace 推导。
- 建议改动层级: contract, rule / policy, middleware, workflow, tool, eval
- prompt / context: registry 不是愿望清单；凡被 registry 冻结为 required 的 CCP，必须能在 raw trace 中被表达和证明。
- rule / policy: gate/audit 控制点若列入 V1 registry，必须同步定义最小事件与证据闭包，不允许只在 registry 里声明、不在 trace 中落真值。
- middleware: 为 runtime/publisher 补 gate/audit 专用 telemetry event 与必要 evidence 引用，coverage evaluator 只消费这些 canonical traces。
- workflow: Task 级 spec review 默认核对 registry 中每个 required CCP 是否有对应 persisted trace 形状和测试。
- tool: `src/ai_sdlc/telemetry/registry.py`、`src/ai_sdlc/telemetry/contracts.py`、`src/ai_sdlc/telemetry/runtime.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/telemetry/governance_publisher.py`
- eval: unprovable-required-ccp 次数、gate/audit-ccp-coverage-gap 次数
- 风险等级: 高
- 可验证成功标准: registry 中的 `gate_hit`、`gate_blocked`、`audit_report_generated` 都能从 persisted trace 中被稳定识别并计入 coverage evaluator。
- 是否需要回归测试补充: 是：补 gate/audit CCP 持久化与 coverage evaluator 的正反测试。

## FD-2026-03-27-013 | status/readiness 的 latest 与 latest-index 视图会陈旧，无法跟随真实写入刷新

- 日期 (UTC): 2026-03-27
- 来源: final_review
- 状态: open
- owner: codex
- wi_id: 003-telemetry-trace-governance
- 现象: `status --json` 的 latest/current 视图当前依赖 scope 根目录 mtime 和派生 index 文件；但 append 事件或 snapshot 时不一定会更新 scope 根目录 mtime，而生产写路径也未自动重建 `open-violations.json` / `latest-artifacts.json` / `timeline-cursor.json`，导致 fresh write 后 readiness 仍可能显示旧的 latest scope 或空的 latest summary。
- 触发场景: final review 在真实写入后复现 readiness 视图，发现向较早 session 追加新事件后 latest id 不变，写入 open violation 后 `open_violations.count` 仍为 0，直到手工 rebuild indexes。
- 影响范围: bounded operator surface 失真，运维对“当前/latest”与 open debt 的判断会落后于真实 trace。
- 根因分类: A, B, H
- 未来杜绝方案摘要: latest/current 的 recency 信号应来自真正随写入变化的对象或索引，而不是不稳定的目录 mtime；同时生产写路径要维护最小派生 index，使 `status --json` 不依赖手工 rebuild 才能看见 fresh state。
- 建议改动层级: middleware, workflow, tool, eval
- prompt / context: bounded status 可以不做深扫，但不能因为避开深扫而长期展示过期状态；只读 surface 仍需消费新鲜的派生真值。
- rule / policy: readiness/status 的 latest/current 输出必须基于可辩护且随写入同步更新的真值来源。
- middleware: 在 writer/store 层维护最小 index 更新或等价 recency 光标；readiness 读取这些 canonical 最新真值，而不是目录 mtime 猜测。
- workflow: final review 默认检查 fresh write 后的 latest/current/open_violations 是否立即可见，不允许依赖手工 `rebuild_indexes()` 才刷新。
- tool: `src/ai_sdlc/telemetry/readiness.py`、`src/ai_sdlc/telemetry/store.py`、`src/ai_sdlc/telemetry/writer.py`
- eval: stale-latest-view 次数、stale-open-violations-count 次数、manual-rebuild-required 次数
- 风险等级: 中
- 可验证成功标准: fresh event / violation / artifact 写入后，`status --json` 的 latest/current 与 latest summary 在不手工 rebuild 的情况下即可反映更新。
- 是否需要回归测试补充: 是：补 fresh write 后 latest/current 与 index summary 即时刷新的回归测试。

## FD-2026-03-27-014 | 001 spec 的 FR 合同被局部实现语义替换，编排型能力长期停留在半闭环

- 日期 (UTC): 2026-03-27
- 来源: traceability_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/001-ai-sdlc-framework/research-pipeline-vs-runner.md, specs/001-ai-sdlc-framework/adr-001-pipeline-vs-runner.md, specs/001-ai-sdlc-framework/task-execution-log.md
- 现象: `001-ai-sdlc-framework` 中多组 FR 已有代码与局部测试，但实现语义与 spec 合同不完全一致，或只完成底层能力而未完成闭环编排。例如 `FR-020~023` 实现成运行时治理检查而不是 spec 定义的 6 项 freeze + `governance.yaml` 落盘；`FR-040~045` 具备 `BatchExecutor` / `ExecutionLogger`，但 `Runner` / CLI 尚未真正按 `tasks.md` 驱动执行、批次提交与开发总结；`FR-052/054` 只有 resume-pack build/save，没有 spec 所述 `load_resume_pack()` 恢复语义；`FR-034` 与 `FR-081` 分别缺统一写拦截与 `work-item.yaml` 状态持久化。
- 触发场景: 实现按小批次围绕 gate、checkpoint、CLI surface 与局部测试推进时，执行侧容易把“当前最易落地的局部语义”当成 FR 真值；close 又主要依据已有测试和入口可用性，而不是逐条回到 FR 合同核对 orchestration、persistence、write-interception 等完整责任。
- 影响范围: 需求可追溯性、spec/plan/tasks 与代码的一致性、执行阶段真实闭环能力、恢复兼容能力、状态机可信度，以及用户对“已实现 / 已完成”表述的判断。
- 根因分类: A, B, D, E, H
- 未来杜绝方案摘要: 把 FR 合同而不是当前 gate/checkpoint/局部测试定义为实现真值；凡实现语义有意偏离 spec，必须在同一迭代同步更新 `spec.md` / `plan.md` / `tasks.md` 或 ADR，而不能让代码暗自替换合同。对编排型、持久化型、写保护型 FR，只有在 end-to-end 行为和 contract-level 回归测试都成立后，才允许标记为“已实现”。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 拆解或实现 FR 时，必须先区分“底层 helper 已存在”与“FR 合同已交付”；不得把 checkpoint 当前行为、单个 gate 通过或局部单测通过，直接等价成 spec 中的完整能力已经成立。
- rule / policy: 增加 FR 合同优先级规则。若代码选择与 spec 不同的语义，必须先更新 spec/plan/tasks 或登记 ADR；若 FR 涉及编排、持久化、恢复、文件保护等跨模块能力，仅有局部对象模型或 helper 不得宣称完成。
- middleware: 为统一写文件入口、`work-item.yaml` 状态持久化、resume-pack load path、execute 主闭环提供单一接入层，避免 FR 长期停在“局部零件已存在、总装件缺失”的状态。
- workflow: 每个实现批次开始前先建立或刷新 `FR -> 设计 -> tasks -> 代码 -> 测试` 对账表；批次收口时必须显式标注哪些 FR 仅完成局部能力、哪些仍缺 orchestration/persistence；close 前把该矩阵作为必查项，而不是只看测试是否全绿。
- tool: 扩展 `workitem close-check` / `verify constraints`，或新增 `workitem trace-check`，对 `spec.md`、`plan.md`、`tasks.md`、实现文件、测试文件做 FR 级对账，并对“只有 helper 没有闭环”的高风险模式给出阻断或告警。
- eval: 为治理冻结、execute 主闭环、resume-pack 加载恢复、`work-item.yaml` 状态持久化、受保护文件真实写拦截建立 contract-level 正反回归测试；close 前必须能证明这些 FR 不是只在单元层存在。
- 风险等级: 高
- Batch 11 处置进展 (2026-03-28):
  - 已闭环: `FR-020~023`（Governance Freeze + `governance.yaml`）、`FR-040~045`（`Executor.run()` 主闭环、批次日志/commit/summary）、`FR-052/054`（`load_resume_pack()` + strict checkpoint 校验 + recover 主路径）、`FR-081`（`work-item.yaml` 状态持久化）。
  - 当时残留: `FR-034` 已从 `open` 降到 `partial`，框架模板与受 guard 写入口已被拦截，但尚未形成“所有文件写入口统一接管”的硬保护；其余接口漂移与门禁缩减项转入 Batch 12。
  - Batch 11 验证: 定向 contract suite 217 passed；全量 `uv run pytest -q` 707 passed；`uv run ruff check src tests` passed。
- 最终收口 (2026-03-28):
  - Batch 12 已闭环: `FR-010~012`（PRD Studio 对外合同 + `structured_output`）、`FR-030/033`（docs branch 命名与 baseline recheck）、`FR-061~063`（INIT / REFINE / EXECUTE Gate）、`FR-073/083`（`index` 自动索引重建）、`FR-074`（`gate <stage>` CLI 形态）。
  - `FR-034` 已闭环: `FileGuard` 现已统一拦截对受保护 `spec.md` / `plan.md` 的 `Path.write_text()` / `Path.write_bytes()` / `open(..., write mode)` / `Path.replace()` / `Path.rename()`，不再只停留在模板写入口保护。
  - 最终验证: 定向 contract suite 111 passed；全量 `uv run pytest -q` 721 passed；`uv run ruff check src tests` passed；`uv run ai-sdlc verify constraints` 无 BLOCKER；`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework` 与 `--all-docs` 全 PASS。
- 可验证成功标准: 对 `FR-020~023`、`FR-034`、`FR-040~045`、`FR-052/054`、`FR-081` 这类合同型 FR，仓库存在对应的实现真值、contract-level 回归测试与 FR 对账结果；若实现只到局部能力，`close-check` / `trace-check` 必须明确标识“部分实现”，不得继续被表述为“已实现”。
- 是否需要回归测试补充: 是：补 governance freeze 落盘、execute end-to-end、resume-pack load/recover、`work-item.yaml` 状态持久化、真实写拦截与 FR 对账阻断的回归测试。

## FD-2026-03-28-001 | checkpoint 与 resume-pack 双状态源失配，recover 反复回到旧断点

- 日期 (UTC): 2026-03-28
- 来源: user_report, self_review
- 状态: planned
- owner: codex
- wi_id: 001-ai-sdlc-framework
- 现象: `checkpoint.yml` 已推进到较新阶段甚至 `close`，但 `resume-pack.yaml` 仍停留在更早的 `execute`/旧 batch；此后再次执行 `ai-sdlc recover` 时，CLI 会继续读取旧 `resume-pack` 并向用户报告过期断点，形成“每次中断都回到同一旧位置”的假象。
- 触发场景: 流水线运行过程中持续写入 `checkpoint.yml`，但 `resume-pack.yaml` 未随阶段推进自动刷新；或用户在已有旧 `resume-pack` 的项目里多次中断/恢复，`recover` 继续把旧 pack 当成可用真值。
- 影响范围: 断点恢复可信度、阶段推进判断、批次续跑、用户对 CLI 状态面的信任，以及“是否已真正恢复到最新位置”的操作决策。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: 断点恢复必须收敛为单一真值来源：`checkpoint.yml` 为唯一恢复真值，`resume-pack.yaml` 仅是由 checkpoint 派生出的上下文快照，且必须在 checkpoint 变更时同步刷新。`recover/status` 需要显式校验两者的一致性，发现 stale pack 时要阻断或自动重建，而不是继续静默复用旧快照。
- 建议改动层级: prompt / context, rule / policy, middleware, workflow, tool, eval
- prompt / context: 所有面向用户的恢复说明必须明确“checkpoint 是恢复真值，resume-pack 是派生快照”；不得把旧快照继续表述成当前断点。
- rule / policy: 规定 checkpoint 为唯一断点真值；resume-pack 不得独立领先或落后于 checkpoint 而仍被视为有效恢复依据。
- middleware: 在 `save_checkpoint()` 后自动重建并写回 resume-pack；`load_resume_pack()` 增加 stage / batch / timestamp / checkpoint pointer 一致性校验；若发现不一致则返回 stale-pack 错误或直接按 checkpoint 重建。
- workflow: 每次 recover / status / run 进入恢复路径前，先做 checkpoint↔resume-pack 对账；若 pack 过期，只允许“自动重建后继续”或“显式报错要求重建”，不再静默沿用。
- tool: `src/ai_sdlc/context/state.py`、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/core/runner.py`、`ai-sdlc recover`、`ai-sdlc status`
- eval: stale-resume-pack 检出率、recover 使用过期 pack 的发生率、checkpoint/save 后 pack 自动刷新覆盖率、恢复位置误报次数
- 风险等级: 高
- 可验证成功标准: 给定“checkpoint 已推进、resume-pack 仍旧”的夹具时，`recover` 与 `status` 必须识别并拒绝陈旧 pack，或自动按最新 checkpoint 重建；正常路径下每次 checkpoint 更新后磁盘上的 resume-pack 都与最新 stage/batch 一致，不再反复回到旧断点。
- 是否需要回归测试补充: 是：补 checkpoint 前进但 resume-pack 未刷新的 stale-pack 正反测试、`save_checkpoint()` 自动同步测试、`recover/status` 遇到双状态源失配时的阻断或自动重建集成测试。
