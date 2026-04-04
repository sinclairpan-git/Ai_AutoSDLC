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
  - `缺陷类型`
  - `wi_id`
  - `legacy_ref`
  - `owner`
  - `related_doc`
  - `detection_surface`
  - `trace_anchor`
  - `observed_scope`
  - `subject_ref`
  - `chain_status`
  - `highest_confidence_source`
  - `key_gaps`
  - `evidence_refs`

### 字段约定

- `根因分类`：沿用 legacy registry 的 A-H 归类，可多选。
- `根因分类` 字典（沿用 [`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../src/ai_sdlc/rules/agent-skip-registry.zh.md)）：
  - `A`：隐性目标（求快、求一次答完）压过强制顺序
  - `B`：软约束（仅 Markdown）无失败即停的硬闸门
  - `C`：词汇碰撞（如 `plan` 指宿主提纲 vs `specs/.../plan.md`）
  - `D`：工具语义误解（如 `stage run` vs `run`）
  - `E`：多真值来源下选错依据（checkpoint vs 手写 YAML）
  - `F`：宿主平台专有流程被当成通用规范
  - `G`：其他（需在条目正文注明）
  - `H`：计划/任务状态未与仓库事实同步（如实现已存在但 `tasks.md`、execution-log、计划状态未对齐）
- `未来杜绝方案摘要`：用 1-3 句概括“以后靠什么约束/机制杜绝同类问题再发生”；详细落地仍应展开到 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 字段。
- `建议改动层级`：从 `prompt / context`、`rule / policy`、`middleware`、`workflow`、`tool`、`eval` 中选择一项或多项。
- `风险等级`：建议使用 `低 / 中 / 高 / 极高`。
- `是否需要回归测试补充`：使用 `是：...` / `否：...`。
- `状态`：建议使用 `open / planned / in_progress / closed / migrated`。
- `缺陷类型`：建议使用稳定的 `snake_case` 标签，描述“这是什么缺陷族群”（如 `close_check_false_green`、`execution_log_contract_drift`）。若现有类型不能准确覆盖，可新增，但必须在条目正文或字段值中写清新类型的边界，避免把不同问题继续混成“其他”。
- 若条目对应的是“已被拦截且已修复”的违约，`状态` 可记为 `closed`，但正文仍必须写清：`现象`、`根因分类`、`未来杜绝方案摘要`，以及未来如何杜绝同类问题再次出现（应落到 `rule / policy`、`middleware`、`workflow`、`tool`、`eval` 等字段）。
- `related_doc`：记录与该条目直接相关的规则、代码、spec、plan、tasks、execution-log 或用户文档，优先写 canonical 路径，而不是会话描述。
- `detection_surface`：记录首次稳定暴露该问题的面，建议使用 `user_review`、`self_review`、`observer`、`close-check`、`verify constraints`、`doctor`、`release gate` 等 bounded 名称；可多值并列。
- `trace_anchor`：记录这条缺陷对应的稳定锚点。优先使用 repo 内可复核的 bounded anchor，如 `rev:<commit>`、`goal_session:<id>`、`run:<id>`、`step:<id>`；若只有人工复盘，可写 `manual_review_only`。
- `observed_scope`：说明问题是在 `revision / repo / session / run / step` 哪一层被观察到；若并非由运行期 telemetry 暴露，而是人工或 review 首次识别，可写 `manual_review`。
- `subject_ref`：若该问题已能映射到 provenance inspection subject，则记录一个稳定 `subject_ref`，用于后续执行 `provenance summary / explain / gaps` 回放；没有可稳定映射的 subject 时可留空。
- `chain_status`：若已有 provenance inspection 结论，沿用 `closed / partial / unknown`；没有 provenance 结论时不要臆造 `closed`，宁可省略或在正文说明“当前无 provenance 结论”。
- `highest_confidence_source`：若 inspection 已给出最高置信来源，直接记录其 bounded 值；否则留空，不做主观归因升级。
- `key_gaps`：优先记录当前阻止更强结论的 gap 语义与关键位置，建议沿用 `unknown / unobserved / incomplete / unsupported`；如无 gap，可写 `无`。
- `evidence_refs`：优先记录 canonical evidence id、稳定 command output anchor 或等价只读证据引用；若当前仅有人审结论、没有 canonical evidence，应显式写 `manual_review_only`，不要伪装成 trace 完整闭环。

### Trace / Provenance 填写原则

- backlog 仍是 remediation / governance 输入池，不是 telemetry 数据库；新增 trace 字段的目标是让条目更可审计，而不是复制整份运行日志。
- 只要仓库里已经存在 telemetry / provenance 只读结论，优先引用 bounded 输出，而不是在 backlog 里重新自由描述一遍调用链。
- `chain_status`、`key_gaps`、`highest_confidence_source` 反映的是“证据链闭合程度”，不等于“缺陷是否已关闭”；缺陷是否收口仍以 `状态`、`收口说明`、验证结果和主线事实为准。
- 当前 provenance 仍是 Phase 1 read-only / advisory-only 能力，且不是 host-native full coverage；因此“没有 provenance 证据”不能被写成“问题不存在”，而 `partial / unknown` 也不应被误写成实现失败。
- 若条目来自人工 review、用户追问或代码审查，而非 observer 自动暴露，仍应照常登记 backlog；trace 字段此时用于披露证据边界，而不是把人工发现硬包装成自动检测。

### 迁移说明

- 下列历史条目已从 legacy registry 迁移并结构化补全。
- 迁移补齐的字段若原始材料未显式给出，会以“基于历史记录推断”的方式写入，但会保留 `legacy_ref`。
- 新增条目应直接写入本文件；若需要回溯历史来源，再反向链接到 legacy registry。

## 下一波待修优先级（2026-04-05）

- 当前待修：
  - 无
- 本轮已收口：
  - `框架线` `FD-2026-04-05-001`
  - `框架线` `FD-2026-04-04-001`
  - `009` 线 `FD-2026-04-02-001`
  - `010` 线 `FD-2026-04-02-002`、`FD-2026-04-02-003`、`FD-2026-04-02-004`、`FD-2026-04-03-005`
  - `008` 线 `FD-2026-03-31-003`
  - `007` 线 `FD-2026-03-31-002`
  - `006` 线 `FD-2026-03-31-004`、`FD-2026-03-31-001`
  - `005` 线 `FD-2026-03-30-001`、`FD-2026-03-30-002`
  - `003` 线 `FD-2026-03-29-001`、`FD-2026-03-29-002`、`FD-2026-03-29-003`
  - `003` 线 `FD-2026-03-27-011`、`FD-2026-03-27-012`
  - `004` 线 `FD-2026-03-27-013`
- 挂靠原则：
  - `003` 线：已全部收口
  - `004` 线：已全部收口

## FD-2026-04-05-001 | RefineGate 对验收场景的识别仅接受窄格式，导致常见 Markdown 场景标题被误判缺失

- 日期 (UTC): 2026-04-05
- 来源: user_review, self_review
- 状态: closed
- 缺陷类型: refine_gate_scenario_contract_drift
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: src/ai_sdlc/gates/pipeline_gates.py, tests/unit/test_gates.py, src/ai_sdlc/templates/spec.md.j2, src/ai_sdlc/rules/quality-gate.md, docs/framework-defect-backlog.zh-CN.md
- detection_surface: user_review, self_review
- trace_anchor: manual_review_only
- observed_scope: manual_review
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以 gate 实现、模板、文档与手工复盘为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: `RefineGate` 当前只接受行首纯文本 `场景|scenario` 前缀，未兼容常见 Markdown 标题/列表/加粗写法；split_truth: gate、模板、规则文档都要求“每个用户故事必须有验收场景”，但没有对可接受语法收敛到同一合同；unobserved: 单测只覆盖窄格式，通过性主要依赖当前正则而不是语义合同
- evidence_refs: file:src/ai_sdlc/gates/pipeline_gates.py; file:tests/unit/test_gates.py; file:src/ai_sdlc/templates/spec.md.j2; file:src/ai_sdlc/rules/quality-gate.md; manual_review_only
- 现象: 用户故事中已存在语义上明确的验收场景，但只要采用 `**场景 1**`、`#### 场景 1`、`- 场景 1` 等常见 Markdown 写法，`RefineGate` 仍会把该故事判定为缺少 acceptance scenario，并返回 `acceptance_scenarios_present=False`。只有 `场景 1:` / `scenario 1:` 这类窄格式可以稳定通过。
- 触发场景: 在 refine/spec 文档中按常见 Markdown 习惯书写验收场景标题，随后执行 `RefineGate` 或依赖同一检查逻辑的质量门禁。
- 影响范围: 所有依赖 RefineGate 的 refine/spec 校验路径、用户对“场景已写但 gate 仍失败”的理解成本、模板/提示词/人工编辑的一致性，以及框架对语义完整性的判断可信度。若不修复，用户会持续把排版差异误判为自己未写场景，或反复为了过 gate 而改写文档形状。
- 根因分类: D, G（G: acceptance-scenario syntax contract drift across gate / template / docs / tests）
- 未来杜绝方案摘要: “每个用户故事必须有验收场景”应是语义合同，不应被实现成只接受单一纯文本前缀的脆弱排版规则。框架需要先定义可接受的场景标题合同，再同步收敛 gate、模板、文档和测试，避免继续出现“文档语义正确但 gate 误判失败”的系统性缺陷。
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: 当用户或代理编写 spec/refine 文档时，框架应把“验收场景”视为结构语义，而不是要求操作者猜测唯一合法排版。若当前仍存在格式约束，必须明确告诉用户 accepted forms，而不是在 gate 失败后让用户自行试错。
- rule / policy: 在质量门禁与模板文档中明确写出验收场景的 canonical 推荐写法，并声明支持的 Markdown 变体边界。推荐把 `场景 1:` / `Scenario 1:` 作为首选示例，但允许常见等价形式如加粗标题、ATX heading、列表项标题。
- middleware: 为 RefineGate 增加轻量的场景标题归一化/识别 helper，在判断前剥离常见 Markdown 包装（如 `**...**`、`#### `、`- `），将识别从“裸正则命中”提升为“归一化后判断是否为场景标题”。
- workflow: refine/spec 生成、人工编辑、门禁校验三条路径必须共享同一场景语法合同。后续若调整 gate 合同，应同步更新模板示例、用户文档与回归测试，不得只改 gate 实现。
- tool: src/ai_sdlc/gates/pipeline_gates.py, tests/unit/test_gates.py, src/ai_sdlc/templates/spec.md.j2, src/ai_sdlc/rules/quality-gate.md
- eval: refine-gate-scenario-false-negative 次数、因场景格式误判导致的 retry 次数、模板示例与 gate 合同不一致的回归次数、场景识别矩阵测试覆盖率
- 风险等级: 中
- 收口说明（2026-04-05）: `RefineGate` 已改为“逐行归一化 Markdown 包装后再判断场景标题”，当前主线工作树已兼容 `场景 1:`、`Scenario 1:`、`**场景 1**`、`#### 场景 1`、`- 场景 1` 与 `- **场景 1**`；`tests/unit/test_gates.py` 已补格式矩阵与“正文仅提到场景但不是标题”反例，`src/ai_sdlc/templates/spec.md.j2` 与 `src/ai_sdlc/rules/quality-gate.md` 也已同步补上 accepted forms 示例。定向回归 `uv run pytest tests/unit/test_gates.py tests/integration/test_cli_stage.py tests/integration/test_cli_run.py tests/integration/test_cli_status.py tests/integration/test_cli_recover.py` 已通过（`116 passed`），本条 defect 不再停留在 backlog 讨论层，已完成框架真值、模板示例与测试矩阵的同步收口。
- 可验证成功标准: 1) `场景 1:`、`Scenario 1:`、`**场景 1**`、`#### 场景 1`、`- 场景 1` 在用户故事块内都能被稳定识别为验收场景。 2) 明确非法的非场景标题不会被误判通过。 3) 模板与质量门禁文档明确列出推荐写法和支持边界。 4) 对应单元测试在识别逻辑再次收窄或漂移时会直接失败。
- 是否需要回归测试补充: 是：补 acceptance-scenario heading 的格式矩阵测试，并增加 gate、模板示例、规则文档三者一致性的回归覆盖。

## FD-2026-04-04-001 | execution-log 模板、脚手架与 close-check 契约漂移，导致新旧 workitem 的收口证据格式系统性失配

- 日期 (UTC): 2026-04-04
- 来源: self_review, user_review
- 状态: closed
- 缺陷类型: execution_log_contract_drift
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: docs/framework-defect-backlog.zh-CN.md, src/ai_sdlc/templates/execution-log.md.j2, src/ai_sdlc/generators/doc_gen.py, src/ai_sdlc/core/workitem_scaffold.py, src/ai_sdlc/core/close_check.py, tests/unit/test_doc_gen.py, tests/unit/test_workitem_scaffold.py, tests/integration/test_cli_workitem_init.py, specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md, specs/027-frontend-program-provider-runtime-artifact-baseline/task-execution-log.md
- detection_surface: self_review, user_review, close-check
- trace_anchor: rev:46b50e0
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以 repo 内 contract、模板、scaffold 与 remediation commit 复盘为准）
- highest_confidence_source: rev:46b50e0
- key_gaps: split_truth: execution-log 的 canonical close-out 契约已在规则与 close-check 落地，但 `execution-log.md.j2`、`DocScaffolder` 与 direct-formal scaffold 没有同步到同一真值；unsupported: 新建 workitem 时缺少对 canonical `task-execution-log.md` 的强制生成与 mandatory close-out 字段预置；ambiguous: 历史 workitem 的最新 batch 格式不合规时，表面上像“文档欠补”，实际暴露的是模板/脚手架/生成器三处漂移
- evidence_refs: rev:46b50e0; rev:045360b; file:src/ai_sdlc/templates/execution-log.md.j2; file:src/ai_sdlc/core/workitem_scaffold.py; file:src/ai_sdlc/generators/doc_gen.py; file:tests/unit/test_doc_gen.py; file:tests/unit/test_workitem_scaffold.py; file:tests/integration/test_cli_workitem_init.py
- 现象: 在重新核对 frontend framework closure 时，一批 workitem 的 `task-execution-log.md` 无法通过当前 `close-check`：部分最新 batch 仍停留在旧极简格式，缺少 `统一验证命令`、`代码审查结论`、`任务/计划同步状态` 与 git close-out 字段；另一些则直接缺 canonical `task-execution-log.md` 起始模板。这不是单个文档遗漏，而是 execution-log 的模板、脚手架和检查契约已经分叉，导致“新生成的文档先天不合规，历史文档只能靠后补 remediation batch 才能过 gate”。
- 触发场景: 在“总览规格状态已全部收口”之后，对 frontend workitems 再做全量 `close-check` 复核时，发现 `014`、`018-062` 这一批 workitem 的收口证据仍存在系统性失败；继续下钻可见当前规则与检查器要求的 mandatory close-out 字段，未被历史 `execution-log.md.j2` 和 direct-formal scaffold 同步生成。
- 影响范围: 新建 workitem 的默认文档正确性、历史 workitem 的 close-check 通过率、execution-log 作为收口真值的可信度，以及“顶层 spec 看起来已闭环但底层 close-out 证据仍系统性失配”的治理判断。若不记录并修复，后续每次契约加严都会再次制造同类 backlog 欠账。
- 根因分类: B, G（G: execution-log canonical contract drift across template / scaffold / generator surfaces）, H
- 未来杜绝方案摘要: execution-log 的文件名、章节结构和 close-out mandatory 字段必须收敛到单一真值，由同一模板同时服务 legacy doc scaffold 与 direct-formal scaffold；一旦 close-check 契约升级，scaffold、模板、测试和历史回填必须作为同一收口链执行，不能再先改 gate、后补生成器。
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: 当用户或代理把“spec 已生成”“tasks 已完成”近似理解为“可收口”时，框架上下文必须提醒：`task-execution-log.md` 才是 close-out 真值的一部分，而且它的 scaffold 必须从首写开始就满足当前 mandatory contract，不能依赖事后人工补格式。
- rule / policy: 明确 `task-execution-log.md` 是 execution log 的 canonical 文件名，且默认模板必须包含 `统一验证命令`、`代码审查结论`、`任务/计划同步状态`、`验证画像`、`已完成 git 提交`、`提交哈希` 等 mandatory close-out 字段；任何新的 close-check 契约升级，都必须同步更新模板、脚手架与回归测试。
- middleware: 将 execution-log scaffold 统一到单一模板真值，禁止 legacy doc generator 与 direct-formal scaffold 各自产生不同结构；对新建 workitem，scaffold 必须直接生成 canonical `task-execution-log.md`，而不是依赖后续人工改名或补块。
- workflow: 当 close-check 新增 mandatory contract 时，收口流程必须显式包含“模板/脚手架对齐检查 + 历史 workitem sweep + backlog 记账”三步；只有三步都完成，才能把问题记为真正 closed，而不是停留在“局部文档已补”。
- tool: src/ai_sdlc/templates/execution-log.md.j2, src/ai_sdlc/core/workitem_scaffold.py, src/ai_sdlc/generators/doc_gen.py, src/ai_sdlc/core/close_check.py, tests/unit/test_doc_gen.py, tests/unit/test_workitem_scaffold.py, tests/integration/test_cli_workitem_init.py
- eval: 新建 workitem 后 canonical `task-execution-log.md` 的 mandatory-field 命中率、`DocScaffolder` 与 direct-formal scaffold 的 execution-log 输出一致性、close-check 契约升级后的历史 workitem sweep 失败数、以及“模板变更但脚手架未变更”的 diff-time guard 次数
- 风险等级: 高
- 可验证成功标准: 1) 新执行 `ai-sdlc workitem init` 或等价脚手架入口时，生成的 `task-execution-log.md` 默认包含当前 close-check 所需的 mandatory close-out 字段与 canonical 文件名。 2) `DocScaffolder` 输出名与 direct-formal scaffold 输出名一致，不再存在 `execution-log.md` / `task-execution-log.md` 分叉。 3) 针对 execution-log scaffold 的单元/集成测试能在模板或输出名再次漂移时直接失败。 4) 历史受影响 workitem 的 remediation batch 已补齐并可被后续 close-check 复核通过。
- 是否需要回归测试补充: 是：补 execution-log 模板内容断言、canonical 输出文件名断言、direct-formal scaffold 自动生成 `task-execution-log.md` 的集成测试，以及 close-check 契约升级后对历史 workitem sweep 的回归校验。
- 收口说明（2026-04-04）: 已通过 `rev:46b50e0` 将 `execution-log.md.j2`、`DocScaffolder` 与 direct-formal `workitem_scaffold` 对齐到同一 canonical contract，并补上相应单元/集成测试；随后通过 `rev:045360b` 为历史受影响 frontend workitems 回填 remediation batch 的真实提交锚点。该缺陷已不再停留在“人工补文档”层，而是完成了框架真值修正与历史账务对齐。

## FD-2026-04-02-001 | 自迭代仓库存在历史 `.ai-sdlc` 痕迹但缺 formal bootstrap 标记时，direct-formal workitem 入口会先撞硬前置且缺少引导

- 日期 (UTC): 2026-04-02
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- wi_id: 009-frontend-governance-ui-kernel
- related_doc: src/ai_sdlc/core/workitem_scaffold.py, src/ai_sdlc/routers/bootstrap.py, docs/USER_GUIDE.zh-CN.md, src/ai_sdlc/rules/pipeline.md, docs/framework-defect-backlog.zh-CN.md, specs/009-frontend-governance-ui-kernel/spec.md, specs/009-frontend-governance-ui-kernel/plan.md, specs/009-frontend-governance-ui-kernel/tasks.md
- detection_surface: self_review, user_review
- trace_anchor: rev:697ae34
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以 CLI 行为与 formal docs 复盘为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: “已有 `.ai-sdlc` 历史痕迹但缺 `project-state.yaml`” 未被识别为需要 formal bootstrap reconcile 的自解释状态；unobserved: `workitem init` 未输出“先运行 `ai-sdlc init .`”的显式引导；ambiguous: `stage run init` / `stage show init` 容易被误读为 formal 初始化落盘入口
- evidence_refs: command:uv run ai-sdlc workitem init --title "前端治理与 UI Kernel"; command:uv run ai-sdlc init .; file:.ai-sdlc/project/config/project-state.yaml
- 现象: 在 AI-SDLC 框架自身的自迭代仓库中，虽然仓库长期存在 `.ai-sdlc` 相关目录和历史使用痕迹，操作者从语义上会自然认为“项目本身已经初始化过”；但 `ai-sdlc workitem init` 仍会先因为 `.ai-sdlc/project/config/project-state.yaml` 缺失而直接报错，且错误信息只暴露底层文件前置，不明确指出“这是 formal bootstrap 未完成、需要先执行 `ai-sdlc init .` 的场景”。结果是 direct-formal 入口先撞硬前置，操作者必须自行推断该走 formal init，而不是被 CLI 明确引导。
- 触发场景: 在框架自身仓库里继续做自迭代能力时，用户要求“按框架约束继续下一步”，代理按 canonical 入口直接执行 `uv run ai-sdlc workitem init ...`；仓库存在历史 `.ai-sdlc` 痕迹，但缺当前 bootstrap 所要求的 `project-state.yaml` 与 project baseline 资产，于是 `workitem init` 按“未初始化项目”处理并停止。与此同时，用户文档把 `workitem init` 描述为 direct-formal canonical 入口，但没有把“必须先 `ai-sdlc init .`”作为显式首要前提写死。
- 影响范围: direct-formal work item 入口的可用性与可理解性、自迭代仓库的 onboarding 体验、用户对“项目已在用”和“formal bootstrap 已完成”之间差异的理解，以及 CLI/文档/规则的一致性。若该缺口持续存在，未来在其他已有 `.ai-sdlc` 历史痕迹但缺 formal state 的仓库里会重复出现同类阻塞，并增加把 `stage run init`、宿主工作流提示或手工补文件误当成正确修复路径的风险。
- 根因分类: D, E, H
- 未来杜绝方案摘要: 框架需要把“历史上已在用，但缺当前 formal bootstrap 标记”的仓库识别为一个明确的中间状态，并在 direct-formal 入口上提供可操作 guidance，而不是只抛出底层缺文件错误。用户文档也需要把 `workitem init` 的适用前提显式补齐，避免 direct-formal canonical 入口与 formal bootstrap 前置之间继续靠人工推断衔接。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 当用户在框架自身仓库里要求“按框架约束继续下一步”或“直接进入 formal work item”时，代理不应假设“仓库既然一直在自迭代就一定已经 formal init 完成”；同时 CLI 不应把这种差异只隐藏为底层文件缺失。上下文应显式区分“历史 `.ai-sdlc` 痕迹”与“当前 formal bootstrap 已完成”的差异。
- rule / policy: 在 `pipeline.md`、用户指南与自迭代约定中补充 direct-formal 入口的前置条件：`workitem init` 只适用于已完成 `ai-sdlc init` 的项目；对“已有 `.ai-sdlc` 痕迹但缺 `project-state.yaml`”的场景，应视为 formal bootstrap 缺口，而不是要求操作者自行推断。若后续定义 `existing_project_partially_initialized` 一类状态，也应在规则中明确其与 direct-formal 的衔接关系。
- middleware: bootstrap/router 层应能识别“历史 `.ai-sdlc` 痕迹 + 缺 formal state”这一 reconcile 场景，并向上层命令返回结构化状态，而不是仅在 `workitem_scaffold` 里做文件存在判断。`workitem init` 失败时应输出明确下一步，例如“Project found but formal bootstrap incomplete. Run `ai-sdlc init .` first.”，必要时可附带 bounded reconcile hint。
- workflow: direct-formal canonical 路径应收敛为 `确认 formal bootstrap -> workitem init -> freeze spec/plan/tasks`。对于框架自身这类自迭代仓库，若发现历史 `.ai-sdlc` 痕迹但 formal bootstrap 缺失，应先进入“补 formal init / reconcile”而不是让操作者在 `workitem init` 失败后自行摸索。`stage run init` / `stage show init` 的说明也应明确它们不是 formal 初始化落盘入口。
- tool: src/ai_sdlc/core/workitem_scaffold.py, src/ai_sdlc/routers/bootstrap.py, src/ai_sdlc/cli/workitem_cmd.py, src/ai_sdlc/cli/commands.py, docs/USER_GUIDE.zh-CN.md, docs/框架自迭代开发与发布约定.md
- eval: direct-formal-init-precondition-fail 次数、自迭代仓库 “existing project but missing formal bootstrap” 场景的首次成功率、`workitem init` 失败后仍需人工判读下一步的次数、是否出现把 `stage run init` 误当成 formal 初始化入口的复现事件
- 风险等级: 中
- 可验证成功标准: 给定“仓库存在历史 `.ai-sdlc` 痕迹但缺 `.ai-sdlc/project/config/project-state.yaml`”的夹具时，`ai-sdlc workitem init` 不再只抛出底层缺文件错误，而会明确给出“先执行 `ai-sdlc init .`”的 formal guidance，或直接输出结构化 reconcile 状态；用户文档在 `workitem init` 条目中也明确写出该前置条件。给定已 formal init 的项目时，`workitem init` 仍按当前 direct-formal 入口正常生成 `specs/<WI>/spec.md + plan.md + tasks.md`。
- 是否需要回归测试补充: 是：补“existing project with legacy `.ai-sdlc` traces but missing `project-state.yaml`”的 CLI 夹具，覆盖 `workitem init` 的 guidance 文案、`ai-sdlc init .` 衔接路径，以及用户文档/帮助文本的一致性检查。

## FD-2026-04-02-002 | VS Code + Codex 插件组合场景被误识别为 VS Code 适配，导致框架约束未真正注入 Codex 对话入口

- 日期 (UTC): 2026-04-02
- 来源: user_review, self_review
- 状态: closed
- owner: codex
- wi_id: 009-frontend-governance-ui-kernel
- related_doc: src/ai_sdlc/integrations/ide_adapter.py, src/ai_sdlc/adapters/vscode/AI-SDLC.md, src/ai_sdlc/adapters/codex/AI-SDLC.md, docs/USER_GUIDE.zh-CN.md, tests/unit/test_ide_adapter.py, tests/integration/test_cli_ide_adapter.py, tests/integration/test_cli_run.py, docs/framework-defect-backlog.zh-CN.md
- detection_surface: user_review, self_review
- trace_anchor: rev:783f688
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以代码实现、文档和测试覆盖复盘为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: “VS Code 作为编辑器宿主 + Codex 作为对话代理宿主”未被建模为组合场景；unobserved: 现有测试只覆盖单一 VS Code / 单一 Codex / Cursor>VSCode 优先级，未覆盖 `.vscode + .codex` 或 `TERM_PROGRAM=vscode + OPENAI_CODEX=1`；ambiguous: 用户文档默认把“先打开 IDE 再 init”视为足够条件，但未说明当编辑器宿主与 AI 代理宿主不同步时，适配文件可能落到错误入口
- evidence_refs: file:src/ai_sdlc/integrations/ide_adapter.py; command:uv run ai-sdlc init .; command:uv run ai-sdlc run --dry-run; file:src/ai_sdlc/adapters/vscode/AI-SDLC.md; file:src/ai_sdlc/adapters/codex/AI-SDLC.md
- 现象: 用户在 VS Code 中使用 Codex 插件时，执行 `init` 和 `run --dry-run` 后，`.ai-sdlc/` 和 project state 等初始化目录会正常生成，但 Codex 聊天并没有按照 AI-SDLC 约束推进开发。复盘现有实现可见，IDE 检测优先级把 `.vscode` / `TERM_PROGRAM=vscode` 放在 `.codex` / `OPENAI_CODEX` 之前，导致框架常只安装 `.vscode/AI-SDLC.md`，而不是 Codex 实际消费的 `.codex/AI-SDLC.md`。
- 触发场景: 项目在 VS Code 中打开，存在 `.vscode/` 或终端环境暴露 `TERM_PROGRAM=vscode`；同时用户实际通过 Codex 插件进行对话开发。执行 `ai-sdlc init .` 或后续会触发 IDE adapter 的命令时，当前实现先把宿主识别为 VS Code，而不是 Codex，因此约束提示落到了 VS Code 适配文件，而未真正注入 Codex 对话入口。
- 影响范围: VS Code + Codex 插件组合场景下的 adapter 注入正确性、用户对“init/dry-run 已成功但约束未生效”的信任、IDE 识别模型的正确性，以及后续对多宿主 / 多代理场景的可扩展性。若不修复，用户会误以为框架已接管对话，而实际上真正的 AI 代理侧并未收到约束。
- 根因分类: D, E, H
- 未来杜绝方案摘要: adapter 选择目标必须收敛为“实际消费约束的 AI 代理入口”，而不是外层编辑器宿主。`init` 时应提供一个可交互的适配方案选择器：自动识别结果只负责默认聚焦，不自动确认；用户可用上下方向键和回车在 `Claude Code / Codex / Cursor / VS Code / 其他-通用` 中显式确认，也可通过命令行参数手动指定。对 `VS Code + Codex 插件`、`VS Code + Claude Code 插件` 这类组合场景，应分别选择 `Codex` 或 `Claude Code`，而不是 `VS Code`。非交互环境下必须有明确 fallback，不能强依赖交互。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 当用户处于“VS Code + Codex 插件”或“VS Code + Claude Code 插件”这类组合场景时，框架不能把“打开的是 VS Code”直接等同于“约束应写入 VS Code adapter”。上下文必须优先回答“当前实际用于聊天开发的 AI 代理入口是谁”，并把选择权明确交给用户确认。
- rule / policy: 在用户文档和适配规则中明确：adapter 选择目标是**实际消费约束的 AI 代理入口**，不是单纯的编辑器外壳。对存在多个候选宿主的场景，默认应进入“自动识别 + 用户确认”的选择流程，而不是静默按固定优先级落盘。列表只保留 `Claude Code / Codex / Cursor / VS Code / 其他-通用` 五项，不再把“VS Code + 某插件”拆成组合选项；若无交互能力，则要求通过 `--ide` 或等价参数显式指定，或退回 deterministic fallback 并清楚提示。
- middleware: `ide_adapter` 需要从单一 `detect_ide() -> IDEKind` 模型演进为“候选方案收集 + 默认候选排序 + 用户确认 / 手动指定”的流程。建议新增交互式 adapter selector：启动时列表显示 `Claude Code`、`Codex`、`Cursor`、`VS Code`、`其他-通用`，自动检测命中的方案仅做默认聚焦，不自动确认；用户可通过上下方向键与回车选择，也可通过 `--ide claude-code|codex|cursor|vscode|generic` 直接指定。选择器的文案应聚焦“请选择当前实际用于聊天开发的 AI 代理入口”，而不是“请选择 IDE”。非 TTY / CI 场景下不得阻塞等待交互，应按显式参数优先、其后采用 deterministic fallback，并打印清晰提示。
- workflow: `ai-sdlc init .` 应收敛为 `探测候选 AI 代理入口 -> 默认聚焦推荐项 -> 用户确认/手动指定 -> 安装对应 adapter -> 后续 dry-run / run 使用同一已确认结果`。若后续检测到宿主变化，也应允许显式重新选择，而不是继续沿用历史错误判定。`run --dry-run` 等非只读入口应尊重已确认的 adapter 选择结果，而不是重新静默改判。
- tool: src/ai_sdlc/integrations/ide_adapter.py, src/ai_sdlc/cli/commands.py, src/ai_sdlc/cli/cli_hooks.py, src/ai_sdlc/adapters/vscode/AI-SDLC.md, src/ai_sdlc/adapters/codex/AI-SDLC.md, docs/USER_GUIDE.zh-CN.md, tests/unit/test_ide_adapter.py, tests/integration/test_cli_ide_adapter.py, tests/integration/test_cli_run.py
- eval: mixed-host-adapter-mismatch 次数、VS Code + Codex 场景首次适配成功率、`.codex/AI-SDLC.md` 缺失但 `.vscode/AI-SDLC.md` 已生成的误装率、用户手动重新适配次数、非交互环境下 adapter 选择失败次数
- 风险等级: 高
- 可验证成功标准: 给定 `.vscode + .codex` 并存或 `TERM_PROGRAM=vscode + OPENAI_CODEX=1` 的夹具时，`ai-sdlc init .` 不再静默只安装 VS Code adapter，而会默认聚焦 `Codex` 并要求用户确认，或允许通过 `--ide codex` 明确指定；确认后 `.codex/AI-SDLC.md` 必须存在，且后续 `run --dry-run` 不会把适配重新改回 VS Code。给定非交互环境时，CLI 不会卡在选择器上，而会要求显式 `--ide` 或采用可解释的 fallback。现有单一 IDE 场景（Cursor、VS Code、Codex、Claude Code、generic）仍保持幂等与不覆盖用户改动。
- 是否需要回归测试补充: 是：补混合宿主夹具（`.vscode + .codex`、`TERM_PROGRAM=vscode + OPENAI_CODEX=1`）、交互选择器默认聚焦与回车确认流程、`--ide` 显式指定路径、非 TTY fallback 路径、以及“已选择 Codex 后 subsequent run 不被静默改判”为 VS Code 的回归测试。

## FD-2026-04-02-003 | Codex 插件即使已读取 `.codex/AI-SDLC.md` 并执行 `run --dry-run`，仍会把适配提示当软参考，缺少可验证的治理激活合同

- 日期 (UTC): 2026-04-02
- 来源: production_report, user_review, self_review
- 状态: open
- owner: codex
- wi_id: 009-frontend-governance-ui-kernel
- related_doc: src/ai_sdlc/adapters/codex/AI-SDLC.md, docs/USER_GUIDE.zh-CN.md, src/ai_sdlc/integrations/ide_adapter.py, docs/framework-defect-backlog.zh-CN.md
- detection_surface: production_report, user_review
- trace_anchor: manual_review_only
- observed_scope: manual_review
- subject_ref: 无（当前无插件级可回放 subject）
- chain_status: unknown（当前以用户截图与行为复盘为准）
- highest_confidence_source: 无（当前无插件级 activation telemetry 输出）
- key_gaps: unsupported: 当前框架没有“adapter installed / adapter file read / governance activated”三层状态区分；unobserved: 缺少插件是否真正采纳约束的 activation handshake；ambiguous: 文档与实现默认把“写入 `.codex/AI-SDLC.md`”近似等同于“Codex 将按框架约束开发”
- evidence_refs: image:用户截图显示已运行 `Get-Content .codex/AI-SDLC.md`、已运行 `python -m ai_sdlc run --dry-run`，但后续仍直接继续实现；file:src/ai_sdlc/adapters/codex/AI-SDLC.md
- 现象: 在用户提供的生产截图中，Codex 插件已经读取了 `.codex/AI-SDLC.md`，并执行了 `python -m ai_sdlc run --dry-run`，说明“适配文件存在”和“启动入口被执行”这两步都已发生；但随后的对话仍直接进入普通编码路径，并明确表示“启动入口已经通过，可以继续按现有流程往下做”，没有真正进入 AI-SDLC 的框架约束链。这说明当前适配文件对 Codex 插件而言最多只是软提示，而不是可验证、可阻断、可判定的治理激活合同。
- 触发场景: 用户在 Codex 插件中手动建立 `.codex/AI-SDLC.md`，或由框架自动安装该文件后，直接在聊天中输入需求；插件会读取适配文件，也可能按提示运行一次 `ai-sdlc run --dry-run`，但之后并未把“必须继续遵守框架约束、不得直接脱离 Contract / stage / gate 链路”当作硬执行前提。
- 影响范围: Codex 适配的可信度、用户对“init / dry-run 成功是否代表框架已接管”的理解、框架对外宣称的 IDE/agent 适配能力，以及所有依赖 `.codex/AI-SDLC.md` 的治理场景。若不修复，用户即使正确安装并选择 Codex adapter，也仍可能得到“看起来读了文件、实际上继续自由编码”的假激活结果。
- 根因分类: B, D, E, F, H
- 未来杜绝方案摘要: 框架必须停止把“adapter 文件已写入/已读取”当作“治理已激活”的等价条件。需要新增可验证的 activation contract，至少区分 `adapter_installed`、`adapter_acknowledged`、`governance_activated` 三层状态；如果 Codex 插件无法提供可靠 handshake，就必须在产品口径上明确它当前只是软提示适配，而不是已可证明生效的硬约束接管。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 当用户看到 `.codex/AI-SDLC.md` 已存在，或插件已读取该文件并执行过 `run --dry-run` 时，框架不能默认宣称“约束已经生效”。上下文必须区分“提示已展示”和“治理已激活”，并对后者要求额外证据。
- rule / policy: 在用户文档、适配规则和产品说明里明确：当前 Codex/Claude 类 adapter 若仅通过本地 Markdown 提示文件接入，则默认只代表“提示面已安装”，不等于“框架约束已被代理硬采纳”。除非后续补上 activation contract，否则不得把这类 adapter 描述为已经可靠接管对话执行。
- middleware: 为 adapter 引入 activation state 模型，例如 `installed / acknowledged / activated`，并让后续 `run --dry-run`、`status` 或显式握手命令能够更新该状态。若目标代理产品无法反馈已采纳约束，则框架应显式停留在 `installed` 或 `acknowledged`，而不是虚构 `activated`。
- workflow: 用户在聊天中输入需求后，框架应有一条可验证的“激活确认”路径，而不是只要求读文件和跑 dry-run。若没有激活确认能力，工作流必须退回到“软提示 + 人工确认”模式，并在文案上明确当前仍存在代理不遵守框架约束的风险。
- tool: src/ai_sdlc/adapters/codex/AI-SDLC.md, src/ai_sdlc/integrations/ide_adapter.py, docs/USER_GUIDE.zh-CN.md, future activation handshake / status surface
- eval: adapter-installed-but-not-activated 次数、Codex 读取 adapter 后仍偏离框架链路的事件数、用户误以为“dry-run 成功=治理已接管”的次数、是否存在可验证 activation signal
- 风险等级: 高
- 可验证成功标准: 给定 Codex 插件场景时，框架能够明确区分“文件已安装”“插件已读取”“治理已激活”三层状态；若插件无法提供 activation signal，产品文档与 CLI 状态不会再把 `.codex/AI-SDLC.md` 存在或 `run --dry-run` 执行成功表述为“约束已生效”。若后续提供 handshake，则在用户输入需求后可通过稳定信号证明 Codex 已进入框架治理路径。
- 是否需要回归测试补充: 是：补 activation-state contract 的单元/集成测试，以及“adapter 文件存在 + dry-run 成功但未获得 activation signal”时不得误报已激活的回归测试。

## FD-2026-04-02-004 | Windows 下 project-config.yaml 原子替换易因句柄占用失败，且 adapter 元数据存在无差别重写

- 日期 (UTC): 2026-04-02
- 来源: user_review, self_review
- 状态: closed
- owner: codex
- wi_id: 010-agent-adapter-activation-contract
- related_doc: src/ai_sdlc/core/config.py, src/ai_sdlc/integrations/ide_adapter.py, tests/unit/test_project_config.py, tests/integration/test_cli_status.py, tests/integration/test_cli_doctor.py, docs/USER_GUIDE.zh-CN.md, docs/framework-defect-backlog.zh-CN.md
- detection_surface: user_review, self_review
- trace_anchor: rev:5dc28b8
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以代码实现、平台语义与测试覆盖复盘为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: `YamlStore.save()` 当前没有 “serialize -> compare -> conditional write” no-op 路径；unsupported: `Path.replace()` 的 Windows `PermissionError` 当前没有 bounded retry/backoff；unobserved: 现有测试未覆盖 “内容未变不写” 与 “replace 短暂失败后重试成功”；ambiguous: adapter 持久化目前会在配置字段未变时刷新 `adapter_applied_at` 并强制落盘
- evidence_refs: file:src/ai_sdlc/core/config.py; file:src/ai_sdlc/integrations/ide_adapter.py; file:tests/unit/test_project_config.py; file:tests/integration/test_cli_status.py; file:tests/integration/test_cli_doctor.py
- 现象: 生产环境用户在 Windows 上使用框架时，写回 `.ai-sdlc/project/config/project-config.yaml` 会间歇性触发 `PermissionError: [WinError 5]`。文件本身未只读时仍会失败，且同目录可见残留临时文件，表现更符合“原子替换阶段撞上目标文件句柄占用”而非静态权限配置错误。复盘当前实现可见，`YamlStore.save()` 每次都会写临时文件并直接 `Path.replace()`，同时 `ide_adapter` 在状态未变时仍会刷新 `adapter_applied_at` 并保存，放大了无意义写入与撞锁概率。
- 触发场景: 已初始化项目中执行会触发 IDE adapter 元数据持久化的命令；当 IDE、索引器、杀软、同步工具或并发的 `ai-sdlc` 进程短暂持有 `project-config.yaml` 句柄时，`tempfile.NamedTemporaryFile(..., delete=False)` 生成的临时文件在 `Path(tmp).replace(path)` 阶段失败。重复调用 `status`、`doctor`、adapter 相关命令时，即使配置语义未变化，也可能因为时间戳刷新而再次写同一文件。
- 影响范围: Windows 生产用户的 CLI 稳定性、operator 对“只读/轻量命令”的预期、adapter 元数据持久化可靠性，以及项目配置文件的跨平台兼容性。若不修复，轻量命令会继续制造不必要写入，并在 Windows 平台周期性触发 `WinError 5`。
- 根因分类: B, D, G（G: Windows 文件锁语义与当前写策略不兼容）
- 未来杜绝方案摘要: 将 `project-config.yaml` 的写路径收敛为“序列化到内存 -> 内容未变化则跳过写入 -> 必要时再落盘”，并把 Windows `replace` 的短暂句柄占用视为受支持的兼容性约束，增加 bounded retry/backoff。adapter 持久化也必须只在配置字段真实变化时才刷新时间戳并保存，避免无意义重写放大平台问题。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: `project-config.yaml` 是本地运行态元数据，不应因为重复执行轻量命令而被无条件重写；Windows 上“文件存在且非只读”也不代表可安全 `replace`。
- rule / policy: 本地运行态 YAML 的持久化必须满足“无状态变化不落盘”；对 Windows 兼容路径，允许针对短暂锁冲突做有界重试，但不得吞掉持续性权限错误。
- middleware: 为 YAML store 增加 `serialize -> compare -> conditional write` 路径；在 `replace` 阶段对 `PermissionError` 做短退避重试，并在失败时保留可诊断上下文。`ide_adapter` 只在配置字段真实变化时才更新 `adapter_applied_at` 并保存。
- workflow: 将“Windows 句柄占用下的配置持久化”纳入跨平台回归清单；排查此类问题时优先核对是否存在无意义重写，而不是先假设 ACL 或只读属性错误。
- tool: src/ai_sdlc/core/config.py, src/ai_sdlc/integrations/ide_adapter.py, tests/unit/test_project_config.py, tests/integration/test_cli_status.py, tests/integration/test_cli_doctor.py
- eval: project-config-write-noop 命中率、Windows replace 重试成功率、`WinError 5` 复现次数、重复命令导致的 `project-config.yaml` 改写次数
- 风险等级: 中
- 收口说明（2026-04-03）: `YamlStore.save()` 已补 `serialize -> compare -> conditional write`，并为 Windows `PermissionError` 添加 bounded retry/backoff；`ide_adapter` 现在只在配置字段真实变化时刷新 `adapter_applied_at`。对应单测已覆盖 no-op save、Windows replace retry，以及重复 adapter 持久化不刷新时间戳。
- 可验证成功标准: 在配置内容未变化时，重复执行相关命令不会改写 `project-config.yaml`；模拟一次或多次短暂 `PermissionError` 后，保存路径可在有界重试内恢复成功；持续性权限问题仍会显式报错。
- 是否需要回归测试补充: 是：补 YAML save 的 no-op 与 Windows replace 重试单测，以及重复 CLI 调用不改写 project-config 的集成回归。

## FD-2026-04-03-005 | Adapter activation contract 实现偏移：init 交互式选择器未落地，显式参数路径取代了主 UX

- 日期 (UTC): 2026-04-03
- 来源: user_review, self_review
- 状态: closed
- owner: codex
- wi_id: 010-agent-adapter-activation-contract
- related_doc: specs/010-agent-adapter-activation-contract/spec.md, specs/010-agent-adapter-activation-contract/plan.md, specs/010-agent-adapter-activation-contract/tasks.md, src/ai_sdlc/cli/commands.py, src/ai_sdlc/cli/adapter_cmd.py, tests/integration/test_cli_adapter.py, tests/integration/test_cli_init.py, tests/unit/test_ide_adapter.py, docs/USER_GUIDE.zh-CN.md, docs/framework-defect-backlog.zh-CN.md
- detection_surface: user_review, self_review
- trace_anchor: rev:5dc28b8
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以 formal docs、CLI 实现、测试与用户文档复盘为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: `init` 当前没有实现 formal spec 要求的交互式五项 selector；unsupported: 现有测试只锁住 `--agent-target` 显式路径，没有锁住 “TTY 下 selector 默认聚焦 + 上下键确认” 主路径；ambiguous: 用户文档把 `adapter select --agent-target ...` 教成主要纠偏方式；incomplete: `010` formal docs 已冻结，但缺少 `task-execution-log.md`，close-check 仍无法证明实现与工单收口一致
- evidence_refs: file:specs/010-agent-adapter-activation-contract/spec.md; file:src/ai_sdlc/cli/commands.py; file:src/ai_sdlc/cli/adapter_cmd.py; file:tests/integration/test_cli_adapter.py; file:tests/integration/test_cli_init.py; file:docs/USER_GUIDE.zh-CN.md; command:uv run ai-sdlc workitem close-check --wi specs/010-agent-adapter-activation-contract
- 现象: `010` formal truth 明确要求 `ai-sdlc init` 提供交互式 AI 代理入口选择器，自动探测只负责默认聚焦，用户通过上下方向键和回车确认；当前实现没有 selector，主要依赖 `--agent-target` 与 `adapter select --agent-target ...` 完成选择，产品形态与需求不一致。当前代码把显式参数 fallback/override 做成了主 UX，导致用户必须记住命令值，而不是通过直观选项完成确认。
- 触发场景: operator 在交互式终端首次执行 `ai-sdlc init .`，期望看到固定五项列表并确认真实聊天 AI 入口；实际 CLI 直接走自动探测或要求手工输入参数，没有进入选择器。后续用户文档和测试也都围绕显式参数路径展开，进一步固化了偏差。
- 影响范围: adapter activation contract 的主 UX、mixed-host 场景下的目标确认可信度、用户对框架“认的是谁”的理解、USER_GUIDE 教程路径、以及 `010` 工单的 formal truth 与实现一致性。若不修复，用户会持续把命令参数当作“唯一修正方法”，而不是得到预期的交互式产品形态。
- 根因分类: B, D, H
- 未来杜绝方案摘要: 当 spec 明确要求交互式 selector 时，显式命令参数只能作为 non-interactive fallback 或 override，不得替代主交互路径。实现必须先把主 UX、fallback UX、测试矩阵和 work item execution evidence 对齐，再允许 close。
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: “有 `--agent-target` 可用”不等于“交互式 selector 已实现”；当 spec 写的是交互确认流程时，评估实现是否完成必须优先检查主 UX 是否存在。
- rule / policy: 若 formal spec 写明 `init` 提供交互式选择器，且自动探测仅用于默认聚焦，则任何只提供显式参数的实现都不得视为已满足 FR；`adapter select` 也不能反向替代 `init` 主入口的交互体验。
- middleware: 抽出统一的 agent-target selector helper，承载 fixed options、default focus、TTY/非 TTY 分流、用户确认结果与 fallback 原因；让 `init` 和后续显式改选路径复用同一 selector truth。
- workflow: `010` 必须回到正式 execute 路径，按 `T21 / T22 / T32` 补 selector、CLI surface 和回归矩阵，并补 `task-execution-log.md`，不得继续以散落代码替代 work item 收口。
- tool: src/ai_sdlc/cli/commands.py, src/ai_sdlc/cli/adapter_cmd.py, src/ai_sdlc/integrations/ide_adapter.py, tests/integration/test_cli_init.py, tests/integration/test_cli_adapter.py, tests/unit/test_ide_adapter.py, docs/USER_GUIDE.zh-CN.md
- eval: TTY selector 回归通过率、mixed-host 默认聚焦命中率、non-interactive fallback 成功率、用户通过 `adapter select --agent-target ...` 手工纠偏次数、`010` formal docs 与实现一致性检查命中率
- 风险等级: 高
- 收口说明（2026-04-03）: `init` 与 `adapter select` 现在共享交互式五项 selector；TTY 下默认进入选项确认，`--agent-target` 退回 non-interactive fallback/override。mixed-host env precedence、selector 回归、CLI 文档与 `010` formal docs 已同步补齐，`010` 不再停留在 `formal_freeze_only`。
- 可验证成功标准: 在交互式 TTY 中执行 `ai-sdlc init .` 时，CLI 会展示五项固定列表，自动探测只做默认聚焦，用户可通过上下方向键与回车确认；在非交互环境中，CLI 不会卡住，而是优先接受 `--agent-target`，否则走 deterministic fallback 并打印说明；`adapter select --agent-target ...` 仍可作为显式纠正路径，但不再替代主 UX。
- 是否需要回归测试补充: 是：补 `init` 交互 selector、mixed-host 默认聚焦、non-interactive fallback、`adapter select` 二次改选，以及 USER_GUIDE/command surface 一致性回归。

## FD-2026-03-31-001 | 宿主 skills 的默认 workflow 会把 superpowers plan 完成态继续推向 execute 倾向，稀释仓库法定阶段真值

- 日期 (UTC): 2026-03-31
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- wi_id: 006-provenance-trace-phase-1
- related_doc: src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, docs/framework-defect-backlog.zh-CN.md, specs/006-provenance-trace-phase-1/spec.md, specs/006-provenance-trace-phase-1/plan.md, specs/006-provenance-trace-phase-1/tasks.md
- detection_surface: user_review, self_review
- trace_anchor: manual_review_only
- observed_scope: manual_review
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前只完成人工复盘，未形成可回放 provenance subject）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: 宿主 skill handoff / repo execute authorization 冲突当前未落成 canonical provenance subject
- evidence_refs: manual_review_only
- 现象: 在 provenance trace 这条 framework capability 上，spec 与 implementation plan 已冻结后，代理沿着宿主 superpowers skill 的默认 handoff 继续推进，把“Inline Execution / Subagent-Driven”表述成自然下一步；如果用户没有当场拦截，会从 `docs/superpowers/plans/*.md` 的 plan 完成态直接滑向开发编码阶段，而不是停留在 plan review / repo 真值对账状态。
- 触发场景: 宿主 skill（尤其 `brainstorming` / `writing-plans`）把“plan complete -> implementation handoff”视为默认工作流，而仓库规则只把 `docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 视为 design input。两层约束缺少“谁只管工作流、谁定义法定 execute 真值”的显式收束时，执行侧会沿宿主 workflow 继续推进。
- 影响范围: 仓库阶段真值被宿主 workflow 稀释、用户 review spec/plan 时被误导为“下一步默认就是编码”、`explicit execute authorization` 语义变弱，以及“plan 已冻结”被错误外推成“已授权进入实现”。
- 根因分类: A, B, C, F, H
- 未来杜绝方案摘要: 必须明确“宿主 skills / workflow 只约束 agent 的工作方式，不改变仓库法定阶段真值”；superpowers spec/plan 完成后的默认下一步应停在 review / 对账 / 等待用户明确 execute 指令，而不是自动 handoff 到编码。只有同时满足“用户明确要求进入实现”和“repo 法定 execute 前置已成立”时，才允许进入开发编码阶段。
- 建议改动层级: prompt / context, rule / policy, workflow, tool, eval
- prompt / context: 当宿主 skill 给出 implementation handoff、执行选项或“next step”提示时，必须先用仓库阶段真值过滤；若当前仍在 spec/plan review、流程讨论或 docs-only 修正中，默认动作保持在文档/规则层，不得把编码作为自然下一步。
- rule / policy: 在 `pipeline.md` 与框架自迭代约定中显式写明：宿主 skill 的 terminal state、plan-complete 提示、execution options 均不构成 execute 授权；repo 阶段切换仍以用户明确指令与 `tasks.md` / gate readiness 等法定前置为准。
- middleware: 后续 provenance / traceability 应把“宿主 skill 触发了什么工作流建议、最终又被哪条 repo 规则拦住或允许”落成正式可审计链路；必要时增加 execute 前 preflight，识别“只有 superpowers plan、没有 explicit execute authorization / repo 前置”的场景。
- workflow: 顺序应收紧为 `spec freeze -> plan freeze -> user review / repo truth check -> explicit execute authorization -> verify / execute`，而不是 `plan complete -> implementation handoff -> coding`。
- tool: `src/ai_sdlc/rules/pipeline.md`、`docs/框架自迭代开发与发布约定.md`、后续 provenance inspection / preflight / execute guard surfaces
- eval: “plan 完成后在无明确 execute 授权下继续向编码推进”的事件数、需要用户手动拦截的次数、宿主 workflow 与 repo 真值冲突被自动识别/阻断的命中率
- 风险等级: 极高
- 收口说明（2026-03-31）: `src/ai_sdlc/rules/pipeline.md` 与 `docs/框架自迭代开发与发布约定.md` 已补充显式规则，声明宿主 skills / plan-complete prompts 只是工作流提示，不等于 execute 授权；spec/plan 完成后默认必须停在 review / 对账状态，只有用户明确要求进入实现且 repo 前置满足时，才能继续编码。本次违约已被正式登记，即使同轮被用户及时拦下也不再只留会话备注。
- 可验证成功标准: 当会话中只有 superpowers spec/plan 完成、但用户仍在 review 文档或讨论流程时，代理不得把编码表述为默认下一步；若用户未明确要求进入实现，或 repo 未满足法定 execute 前置，代理必须停在文档/对账/规则修正状态。只有在用户明确要求实现且前置满足后，才允许进入 execute。
- 是否需要回归测试补充: 是：补一类流程级正反夹具，验证“plan complete 但无 explicit execute authorization”会被识别为仍停留在 docs/review 状态；后续 provenance trace 还应补 `skill invocation / rule provenance / conversation trigger` 链路，用于审计这类阶段切换。

## FD-2026-03-31-002 | 分支 / worktree 生命周期未被正式门禁化，导致长期偏离 `main` 的遗留分支只能靠人工巡检发现

- 日期 (UTC): 2026-03-31
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- wi_id: 007-branch-lifecycle-truth-guard
- related_doc: src/ai_sdlc/rules/git-branch.md, src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md, specs/007-branch-lifecycle-truth-guard/spec.md, specs/007-branch-lifecycle-truth-guard/plan.md, specs/007-branch-lifecycle-truth-guard/tasks.md
- detection_surface: user_review, self_review
- trace_anchor: manual_review_only, rev:4fc4d4e
- observed_scope: repo
- subject_ref: 无（当前以 branch inventory / branch-check bounded surface 为准）
- chain_status: unknown（当前不通过 provenance inspection 建模）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: branch/worktree lifecycle 当前不映射为 provenance subject；unobserved: 旧流程缺少 canonical disposition truth
- evidence_refs: command:uv run ai-sdlc workitem branch-check --wi specs/007-branch-lifecycle-truth-guard --json
- 现象: 仓库中可以长期残留只存在于本地或远端、且与 `main` 已明显偏离的分支 / worktree；即便相关工作项已经收口或主线已有后续实现，现有框架也不会通过 `verify constraints`、`close-check`、`status --json` 或 `doctor` 主动暴露这些“未处置分支真值”，最终仍需依赖人工执行 `git branch`、`git worktree list`、`git rev-list --left-right --count` 才能发现。
- 触发场景: 独立 worktree 或 feature scratch 分支完成了局部实现、验证或文档回填，但 branch close-out 没有与主线合流、execution-log 归档、任务对账和 disposition（`merged / archived / deleted`）放在同一轮法定尾部动作里完成；同时 `git-branch.md` 只建模 `design/NNN` 与 `feature/NNN`，没有把 `codex/*`、backup、历史 feature 分支和 worktree 生命周期纳入正式 guardrail。
- 影响范围: 主线真值判断、close-out 可信度、用户对“分支已实现”与“主线已兑现”的区分、历史 worktree 清理成本，以及后续 framework capability 是否仍被旧分支误表示为“已有未合并实现”的治理判断。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: 必须把 branch/worktree inventory 与 disposition 升格为正式框架约束，而不是 Git 使用习惯。框架需要显式建模 `design / feature / scratch / archive` 等生命周期类型，并在 close 前检查“关联分支是否已合流或已归档说明”；对长期偏离 `main` 的遗留分支，至少要在 read-only surface 中持续暴露，在 work item close-out 中对关联分支给出 blocker 或高优先级告警。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 当代理基于某个分支或 worktree 回答“已实现 / 已收口 / 还有未合内容”时，必须明确区分“仅分支存在”与“主线已兑现”，不得把本地 scratch 分支事实外推成主线真值。
- rule / policy: 扩展 `git-branch.md` 与 `pipeline.md`，把 branch/worktree close-out 从“可选清理”提升为正式 disposition 约束；close 前必须说明关联分支是 `merged`、`archived` 还是 `deleted`，否则不得宣称收口完整。
- middleware: 为分支治理增加只读 inventory / divergence helper，统一产出 branch kind、upstream、worktree 绑定、相对 `main` 的 ahead/behind、以及是否缺失 disposition；不得靠会话临时命令拼接判断。
- workflow: 顺序应收紧为 `branch/worktree create -> implementation / docs update -> main merge or archive decision -> execution-log / tasks 对账 -> close-check`；若某分支仍仅存在于本地 scratch/worktree 且未处置，最终答复必须披露“尚未完成 branch close-out”。
- tool: `src/ai_sdlc/branch/git_client.py`、新增 branch inventory helper、`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/telemetry/readiness.py`、`ai-sdlc workitem branch-check`（或等价只读面）
- eval: work-item 关联分支未处置次数、长期偏离 `main` 的本地分支数、close 前 branch disposition 缺口检出率、需要人工巡检后才发现的遗留 worktree 次数
- 风险等级: 高
- 收口说明（2026-03-31）: `007` 已把 branch/worktree inventory、disposition parsing、`workitem branch-check`、`close-check`、`verify constraints`、`status --json` 与 `doctor` 的 branch lifecycle bounded surfaces 正式落到主线；`git-branch.md`、`pipeline.md`、用户文档与自迭代约定也已同步收紧。当前 work item 已合流 `main`，execution log 已补齐 `merged / removed` disposition 真值，本条 defect 不再停留在 planned。
- 可验证成功标准: 给定一个 work item 关联的 scratch/worktree 分支仍比 `main` 多提交、且未登记 `merged / archived / deleted` disposition 时，`close-check` 或等价 branch-check 必须返回明确 blocker 或 warning；`status --json` / `doctor` 至少能稳定暴露 branch inventory 摘要；当分支已合回主线或已完成归档处置后，相关告警消失。
- 是否需要回归测试补充: 是：补 `branch inventory`、`branch-vs-main divergence`、`unresolved worktree disposition`、`archived-but-not-merged`、`unrelated historical branch only warns` 等正反夹具。

## FD-2026-03-31-003 | 新 framework capability 仍默认先写入 `docs/superpowers/*` 再补 formal work item，导致双轨产物和重复劳动

- 日期 (UTC): 2026-03-31
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- wi_id: 008-direct-formal-workitem-entry
- related_doc: src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, docs/framework-defect-backlog.zh-CN.md, specs/008-direct-formal-workitem-entry/spec.md, specs/008-direct-formal-workitem-entry/plan.md, specs/008-direct-formal-workitem-entry/tasks.md
- detection_surface: user_review, self_review
- trace_anchor: manual_review_only, rev:b66f7e6
- observed_scope: repo
- subject_ref: 无（当前无稳定 provenance inspection subject）
- chain_status: unknown（当前以 formal docs / CLI truth 为准）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unsupported: docs/superpowers draft path 与 formal work item 入口冲突当前不映射为 provenance subject；unobserved: 旧流程未提供 canonical direct-formal entry
- evidence_refs: command:uv run ai-sdlc workitem init --title "<新的 framework capability 标题>"
- 现象: 即使已经把“`docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 只是 design input、不是 execute 真值”写进规则，新的 framework capability 仍常常先在 `docs/superpowers/*` 下生成一套 design / implementation 文档，等到仓库审核或准备执行时，再人工补一套 `specs/<WI>/spec.md + plan.md + tasks.md`。结果不是直接违规进入 execute，而是形成双轨产物、重复搬运和 traceability 噪音。
- 触发场景: 宿主 `brainstorming` / `writing-plans` skill 的默认保存路径仍指向 `docs/superpowers/*`，而仓库法定执行真值又要求回到 `specs/<WI>/...`。当前规则虽然已阻止“只有 superpowers plan 就进入实现”，但还没有提供一个 direct-to-formal 的 canonical entry path，因此实际操作往往变成“先写 superpowers，再 formalize 到 work item”。
- 影响范围: spec/plan/tasks 的重复维护成本、formal work item 生成延迟、review 面噪音、agent 工作流与仓库真值之间的额外摩擦，以及“哪个文件才是 canonical spec/plan”的认知负担。
- 根因分类: A, B, C, H
- 未来杜绝方案摘要: 对新 framework capability，canonical spec/plan/tasks 应从一开始就直接落到 `specs/<WI>/`，而不是先把 `docs/superpowers/*` 当作最终落点。框架需要提供 direct-formal scaffold / init path，使 formal work item 成为默认入口；`docs/superpowers/*` 如继续存在，只能作为草稿、参考或可选设计输入，而不是必须先写一套再搬运。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: 当用户要求“先 spec/plan/tasks”或正在做 framework capability design freeze 时，默认动作应直接创建 formal `specs/<WI>/spec.md + plan.md + tasks.md`，而不是先在 `docs/superpowers/*` 生成 canonical 文档再补录。
- rule / policy: 在 `pipeline.md` 与自迭代约定中，把“新 framework capability 的 canonical 设计/计划入口直接位于 `specs/<WI>/`”写成显式规则；`docs/superpowers/*` 若存在，仅能作为 design input / auxiliary reference。
- middleware: 提供 direct-formal 的 work item scaffold/init 能力，使用现有 spec/plan/tasks 模板一次性创建 parser-friendly formal docs，并允许可选挂接 `related_doc` / `related_plan` 引用，而不是强制复制内容。
- workflow: 顺序应收紧为 `allocate WI -> init formal spec/plan/tasks -> review / freeze -> execute`；若有 superpowers 草稿，只能选择“引用”而不是“再抄一套”。
- tool: `src/ai_sdlc/cli/workitem_cmd.py`、新增 work item scaffold helper、`templates/spec-template.md`、`templates/plan-template.md`、`templates/tasks-template.md`、`docs/USER_GUIDE.zh-CN.md`
- eval: 新 framework capability 中“先写 `docs/superpowers/*` 再补 formal work item”的事件数、formal work item 从首次设计到落盘的延迟时间、需要重复搬运 spec/plan 内容的次数
- 风险等级: 高
- 收口说明（2026-03-31）: `src/ai_sdlc/core/workitem_scaffold.py`、`ai-sdlc workitem init`、`pipeline.md`、自迭代约定与用户文档已经把新 framework capability 的 canonical 入口统一到 `specs/<WI>/spec.md + plan.md + tasks.md`；当前 `008` 也已直接以 formal work item 启动并合流主线，不再依赖“先写 `docs/superpowers/*` 再 formalize”的双轨路径。
- 可验证成功标准: 给定一个新的 framework capability 场景时，仓库可以直接生成 `specs/<WI>/spec.md + plan.md + tasks.md` 的 canonical skeleton，并把后续 review / execute 全部挂到这套 formal docs；不存在“必须先写 `docs/superpowers/*` 才能继续”的前置。若存在外部 design notes，它们也只作为 reference，而不是第二套 canonical 文档。
- 是否需要回归测试补充: 是：补 direct-formal scaffold CLI、parser-friendly formal doc 生成、`related_doc / related_plan` 引用、以及“无须先写 `docs/superpowers/*`”的正反夹具。

## FD-2026-03-31-004 | 未先绑定用户指定 branch/commit/work item，就用当前工作区证据误判 execute 状态

- 日期 (UTC): 2026-03-31
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- wi_id: 006-provenance-trace-phase-1
- related_doc: src/ai_sdlc/branch/git_client.py, src/ai_sdlc/core/workitem_truth.py, src/ai_sdlc/cli/workitem_cmd.py, tests/integration/test_cli_workitem_truth_check.py, tests/unit/test_command_names.py, docs/USER_GUIDE.zh-CN.md, docs/框架自迭代开发与发布约定.md
- detection_surface: user_review, self_review
- trace_anchor: rev:67dda48
- observed_scope: revision
- subject_ref: 无（当前以 revision-scoped truth-check 为准）
- chain_status: unknown（当前不通过 provenance inspection 建模）
- highest_confidence_source: 无（当前无 provenance inspection 输出）
- key_gaps: unobserved: 当时缺少 revision-scoped truth preflight；unsupported: 该误判属于 revision truth surface，不是 provenance subject
- evidence_refs: command:uv run ai-sdlc workitem truth-check --wi specs/006-provenance-trace-phase-1 --rev 67dda48
- 现象: 用户明确指向分支 `codex/006-provenance-trace-phase-1` 与提交 `67dda48`，且该修订只包含 `spec.md / plan.md / tasks.md` 的 formal freeze；但代理先扫描当前工作区 `main` 上的其他 work item 证据，并一度把 `008` 的实现、`task-execution-log.md` 与收口状态外推到 `006`，误表述成“这条线很可能不是待执行，而是已实现待核验/收口”。
- 触发场景: 用户给出了明确的 branch、commit 或 work item 锚点，但代理没有先绑定 `revision -> work item -> execution evidence` 查询上下文，就直接读取当前 checkout 的 `specs/*`、close-check 结果和现成 execution-log；仓库也缺少“当前 HEAD 与用户指定 revision 不一致”时的显式告警和只读 preflight。
- 影响范围: work item 阶段真值、execute 授权判断、是否已开始实施/是否仅 formal freeze 的口径、close-out 可信度，以及用户对“当前到底在讨论哪条线”的信任。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: 只要用户给出 branch、commit、work item 目录中的任一锚点，所有阶段判断都必须先锚定到该 revision 的 formal docs、execution-log 与代码/测试变更面，再决定是否已经进入 execute。不得把当前 cwd、`main` 或其他 work item 的证据跨上下文套用到目标 work item。
- 建议改动层级: prompt / context, rule / policy, middleware, workflow, tool, eval
- prompt / context: 只要问题涉及“这条线现在处于什么阶段”“有没有执行过”“是否可以开始执行”，且用户给出了 branch / commit / WI id 任一锚点，代理必须先复述并绑定该锚点；在核对完成前，不得引用当前工作区里其他 work item 的 execution evidence 作为结论。
- rule / policy: 把“阶段真值查询必须以用户指定 revision / WI 为先”写成显式规则；若当前工作区 HEAD 与用户指定 branch/commit 不一致，默认动作必须先说明正在跨 revision 核对，并禁止把当前分支状态外推成目标 WI 的 execute 状态。
- middleware: 增加 branch/commit-scoped truth resolver 或 preflight，能从指定 revision 只读提取 `spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md` 是否存在，以及 `src/`、`tests/`、`docs/` 的变更分布，输出 `formal_freeze_only / branch_only_implemented / mainline_merged` 等 bounded classification。
- workflow: 顺序应收紧为 `bind target revision -> locate formal work item -> inspect task-execution-log presence -> inspect code/test diff -> inspect branch/main relationship -> then state execute status`；不得先扫描当前仓库已有 work item，再反推用户正在询问的目标线状态。
- tool: `src/ai_sdlc/branch/git_client.py`、`src/ai_sdlc/core/workitem_truth.py`、`src/ai_sdlc/cli/workitem_cmd.py`、`ai-sdlc workitem truth-check --wi specs/<WI> --rev <branch|commit>`
- eval: “用户已指定 revision 但代理仍引用当前 checkout 真值”的事件数、cross-work-item execute 误判次数、HEAD/revision mismatch 被自动识别并显式披露的命中率
- 风险等级: 高
- 收口说明（2026-03-31）: 已新增只读 `ai-sdlc workitem truth-check`，可在当前 checkout 或指定 `--rev` 上解析 formal docs、`task-execution-log.md`、相对 `main` 的 divergence 与代码/测试变更面，并输出 `formal_freeze_only`、`branch_only_implemented`、`mainline_merged` 三类 bounded classification；当当前 HEAD 与目标 revision 不一致时，结果会显式暴露 mismatch，而不是再把当前工作区证据外推到目标 work item。对应 focused regression：`uv run pytest tests/integration/test_cli_workitem_truth_check.py tests/unit/test_command_names.py -q` 通过，`uv run ruff check src/ai_sdlc/branch/git_client.py src/ai_sdlc/core/workitem_truth.py src/ai_sdlc/cli/workitem_cmd.py tests/integration/test_cli_workitem_truth_check.py tests/unit/test_command_names.py` 通过。
- 可验证成功标准: 给定用户指定 `codex/006-provenance-trace-phase-1` / `67dda48`，且该修订只有 `spec.md`、`plan.md`、`tasks.md`、不存在 `task-execution-log.md`、也无 `src/` / `tests/` 变更时，代理必须明确回答“formal freeze 已完成，但 execute 尚未开始”，即使当前 `main` 上存在其他 work item 的实现与 execution-log 也不得外推。若用户指定的 revision 与当前工作区 HEAD 不一致，响应中必须显式披露该不一致及实际核对的绝对锚点。
- 是否需要回归测试补充: 已完成：补 branch/commit-scoped 阶段真值正反夹具，覆盖“当前 HEAD=main，但目标 revision 只有 formal docs”“目标分支仅实现未合主线”“目标 revision 已有 execution-log 与代码变更”三类场景。

## FD-2026-03-30-001 | 新 framework capability 的 architecture/plan 已冻结，但仍把 `docs/superpowers/plans/*.md` 误当作可直接进入实施的法定入口，未先落到 `specs/<WI>/tasks.md`

- 日期 (UTC): 2026-03-30
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- related_doc: docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md, docs/superpowers/plans/2026-03-30-harness-grade-telemetry-observer-v1.md, docs/框架自迭代开发与发布约定.md
- 现象: 在 `Harness-Grade Telemetry & Observer Architecture` 这条新 framework capability 线上，architecture baseline 和 implementation plan 已写入 `docs/superpowers/`，但随后仍把 `docs/superpowers/plans/*.md` 误表述成“可直接从 Task 1 开始实施”的入口，没有先把设计收敛成正式 `specs/<WI>/spec.md + plan.md + tasks.md`。该问题被用户追问后才显式承认。
- 触发场景: 对全新 framework 级能力先产出全景设计文档与实施计划后，执行侧沿着普通工程计划思维继续推进，把“已有 implementation plan”误当作“已满足框架执行前置条件”，而没有回到仓库法定真值入口 `tasks.md`。
- 影响范围: 阶段顺序失真、`tasks.md` 法定地位被弱化、`TasksParser` / work item traceability / close-check 无法接入正式执行真值，以及后续 execution log / defect 挂靠 / close verdict 的单一真值被破坏。
- 根因分类: A, B, C, H
- 未来杜绝方案摘要: 对任何新 framework capability，只要执行目标是进入实现，就必须把 `docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 视为“设计输入”，而不是法定执行入口；在出现“可以开始 Task 1”这类完成性或执行性表述前，必须先落成 `specs/<WI>/spec.md`、`plan.md`、`tasks.md`。必要时应增加显式检查，阻断“只有 superpowers plan、没有正式 work item tasks”时的实施宣称。
- 建议改动层级: prompt / context, rule / policy, workflow, tool, eval
- prompt / context: `docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 负责 architecture baseline 和 planning frame，不自动等价于框架 work item 的法定执行入口；执行性表述前必须先核对 `specs/<WI>/tasks.md` 是否存在。
- rule / policy: 将“新 framework capability 的设计文档与 superpowers implementation plan 不是执行真值；正式执行入口仍是 `specs/<WI>/tasks.md`”补成显式规则，并纳入自迭代约束。
- middleware: 为后续 `trace-check`、`close-check` 或等价 guard 增加检测：若当前能力只有 `docs/superpowers/plans/*.md` 而没有正式 `specs/<WI>/tasks.md`，则不得进入实现完成态或对外宣称“可直接开做”。
- workflow: 完整顺序必须收敛为 `architecture baseline -> implementation plan -> specs/<WI>/spec.md -> specs/<WI>/plan.md -> specs/<WI>/tasks.md -> execute -> task-execution-log`；任何在 `tasks.md` 之前的实现性推进都应视为流程违约。
- tool: `src/ai_sdlc/context/state.py`、`src/ai_sdlc/generators/doc_gen.py`、后续 `workitem close-check` / `trace-check`、以及相关 `verify constraints` surface。
- eval: “仅有 superpowers plan 即宣称可执行”事件数、`tasks.md` 缺失下的实施宣称拦截率、framework capability 从 design 到正式 work item 的转换完整率
- 风险等级: 高
- 收口说明（2026-03-31）: `docs/superpowers/specs/2026-03-30-harness-grade-telemetry-observer-architecture-design.md` 与 `docs/superpowers/plans/2026-03-30-harness-grade-telemetry-observer-v1.md` 已明确把 `evaluation summary` / `incident report` 维持为 deferred，并写清 formal execution truth 应回到 `specs/005-harness-grade-telemetry-observer-v1/`；`src/ai_sdlc/rules/pipeline.md` 与 `docs/框架自迭代开发与发布约定.md` 也已把“superpowers plan 只是 design input，不是法定执行入口”收紧成显式规则与流程说明。后续 execute/close 的法定真值已回到 `tasks.md`、`task-execution-log.md` 与主线提交链。
- 可验证成功标准: 给定“只有 `docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md`、但尚未创建 `specs/<WI>/tasks.md`”的场景时，流程检查或 review 能明确指出“尚未满足法定执行前置”；完成正式 `specs/<WI>/tasks.md` 后，才能进入 Task 级实施与 execution log。
- 是否需要回归测试补充: 是：补一类正反夹具，验证框架 capability 在只有 superpowers plan 时不会被表述为“可直接开做”，而在正式 `tasks.md` 落成后才允许进入实施路径。

## FD-2026-03-30-002 | 已识别流程违约后，代理仍未按框架约束主动登记 `framework-defect-backlog`，而是等用户追问后才补录

- 日期 (UTC): 2026-03-30
- 来源: self_review, user_review
- 状态: closed
- owner: codex
- related_doc: docs/framework-defect-backlog.zh-CN.md, docs/框架自迭代开发与发布约定.md, src/ai_sdlc/rules/pipeline.md, src/ai_sdlc/rules/verification.md
- 现象: 在已经识别出“把 `docs/superpowers/plans/*.md` 误当成可直接进入实施入口”的流程违约后，代理没有立即按仓库约束把该违约登记到 `docs/framework-defect-backlog.zh-CN.md`，而是先停留在口头承认，直到用户再次追问“违约的记录约束呢”之后才补录 backlog。
- 触发场景: 代理已经完成违约识别与口头确认，但没有把“识别违约 -> 立即登记 backlog”视为同一轮法定动作，而是把 backlog 记录误当成可选后续步骤。
- 影响范围: 框架违约归档时效性、缺陷真值单一来源、execution close-out 的可信度，以及“发现违约后是否会自动回挂演进输入池”的框架行为预期。
- 根因分类: A, B, H
- 未来杜绝方案摘要: “识别出框架违约”与“登记 framework-defect-backlog”必须被视为同一轮原子动作，而不是两个可分离步骤；一旦命中规则条件，代理应先补 backlog，再继续讨论补正路径或实施计划。
- 建议改动层级: prompt / context, rule / policy, workflow, eval
- prompt / context: 当代理自己已经明确说出“这是违约 / 这是框架缺口”时，下一动作默认应切到 backlog 记录，而不是继续停留在解释或等待用户提醒。
- rule / policy: 把“识别违约后必须立即登记 backlog”从一般性描述收紧为明确执行顺序；若未登记，不得继续把该问题表述为已完整处理。
- middleware: 后续可在 review checklist、trace-check 或等价自检面增加检测：若会话或执行归档中已明确识别违约，但 backlog 未新增对应条目，则给出流程 blocker 或高优先级告警。
- workflow: 顺序固定为 `识别违约 -> 写 backlog 条目 -> 只读校验 -> 再讨论补正/修复/计划`，不得颠倒。
- tool: `docs/framework-defect-backlog.zh-CN.md`、`uv run ai-sdlc verify constraints`、后续 `trace-check` / close-out checklist
- eval: “已识别违约但未即时登记 backlog”事件数、违约识别到 backlog 落盘的延迟时间、需要用户二次提醒才补录的次数
- 风险等级: 中
- 收口说明（2026-03-31）: `src/ai_sdlc/rules/pipeline.md` 已把顺序固定为 `识别违约 -> 写 backlog 条目 -> 只读校验 -> 再讨论补正/修复/计划`，`docs/框架自迭代开发与发布约定.md` 也同步声明不得继续停留在解释或等待二次提醒；`src/ai_sdlc/rules/verification.md` 的框架缺陷落盘协议继续作为验证面约束。该违约已被正式登记且不再停留在会话备注，backlog 真值恢复单一来源。
- 可验证成功标准: 当代理在一次迭代中明确识别出框架违约时，同轮必须新增对应 backlog 条目，并在继续补正动作前完成只读校验；后续 review / traceability 不再出现“口头承认了违约，但 backlog 为空”的状态。
- 是否需要回归测试补充: 是：补一类流程级正反夹具，验证“识别违约但未登记 backlog”会被明确视为未完成的流程缺口。

## FD-2026-03-29-001 | close-check 会把部分实现的 work item 误判为可收口

- 日期 (UTC): 2026-03-29
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/003-cross-cutting-authoring-and-extension-contracts/spec.md, specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md
- 现象: `ai-sdlc workitem close-check` 当前只检查 `tasks.md` 中是否存在未勾选 checkbox、`task-execution-log.md` 是否具备最小字段、latest batch 是否记录 fresh verification 与 git closure，因此当 work item 规划了多批任务但前序批次并未真正实现时，只要最新一次局部 batch 写了合规 execution log，仍可能返回 `ready for completion`。
- 触发场景: 对 `003-cross-cutting-authoring-and-extension-contracts` 执行 close-check 时，虽然 Batch 1~5 的 PRD authoring / reviewer / backend / release gate 主需求并无对应实现真值，但因为 Batch 6 的 telemetry backlog 收口材料完整，close-check 仍返回 PASS。
- 影响范围: work item 完成状态判断、close gate 可信度、traceability 审阅、用户对“已收口”表述的信任，以及后续 spec/plan/tasks 与实现事实的一致性。
- 根因分类: A, B, H
- 未来杜绝方案摘要: `close-check` 必须从“文档字段完备性”升级为“合同完成真值”校验：同时验证 planned task/batch 覆盖、FR/SC 对应实现证据与 execution-log 覆盖范围，不能再把单次局部收口当成整个 work item 的完成证明。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: `close-check` 的 PASS 语义必须是“当前 work item 的法定完成条件已满足”，而不是“最新一批执行记录写得合规”。
- rule / policy: 若 `tasks.md` / `spec.md` 声明了多个 batch、多个 FR/SC cluster 或重开状态，close-check 必须验证这些范围是否均有实现与执行证据；只完成局部 batch 不得返回 ready for completion。
- middleware: 增加 `work item completion truth` 聚合逻辑，解析 `tasks.md` / `task-execution-log.md` / 相关实现测试信号，识别“未执行 batch”“仅文档声明”“局部收口外推”等高风险模式。
- workflow: 每次 close 前先运行 FR/SC 级 traceability / planned-batch coverage 校验；发现未覆盖范围时先回挂任务或补 execution evidence，再允许继续 close。
- tool: `src/ai_sdlc/core/close_check.py`、新增 `src/ai_sdlc/core/workitem_traceability.py`（或等价聚合层）、`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`
- eval: false-green-close-check 次数、planned-batch-missing-evidence 检出率、partial-implementation-misclosed 次数
- 风险等级: 高
- 收口说明（2026-03-29）: `src/ai_sdlc/core/workitem_traceability.py`、`src/ai_sdlc/core/close_check.py` 及对应 unit/integration tests 已补齐 planned-batch coverage、reopened-status blocker 与 FR/SC traceability 校验；`003` 的 execution log 也已补成 Batch `1~5` + Batch `6` 的完整覆盖，`close-check` 不再把局部 batch 误判成整项可收口。
- 可验证成功标准: 给定一个 work item 只完成最新局部 batch 而前序 batch 无 execution evidence / 无实现映射时，`close-check` 必须返回 BLOCKER；当所有 planned batch 与 FR/SC 覆盖完整后才允许 PASS。
- 是否需要回归测试补充: 是：补“仅最新 batch 有 execution log”“tasks 无 checkbox 但前序 batch 未实现”“FR/SC 无代码映射”三类正反回归。

## FD-2026-03-29-002 | verify constraints 缺少 feature-contract coverage，无法发现 spec 主需求未实现

- 日期 (UTC): 2026-03-29
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/003-cross-cutting-authoring-and-extension-contracts/spec.md
- 现象: `ai-sdlc verify constraints` 当前只校验治理文件、framework backlog、doc-first / verification profile surface、checkpoint spec_dir、task acceptance 与 skip-registry mapping 等仓库规则面；对于 `003` 中的 draft PRD authoring、reviewer checkpoint、backend delegation/fallback、release gate evidence 等 feature-contract 主需求没有任何检查对象，因此仓库规则面为绿时，命令仍可能返回 `no BLOCKERs`。
- 触发场景: 对仓库执行 `uv run ai-sdlc verify constraints` 时，即使 `003` 的 `FR-003-001 ~ 015` 仅存在于 spec/plan/tasks，代码侧没有对应模型、路由、fallback 或 release-gate 实现，命令仍返回通过。
- 影响范围: verification gate 的覆盖声明、work item readiness 判断、contract review、回归策略设计，以及“仓库全绿”被误解为“spec 主需求已实现”。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: `verify constraints` 需要引入 feature-contract coverage 面，至少能对当前活动 work item 的关键 FR/SC cluster 做 presence/shape 校验，并为“spec 只有声明、无实现对象/测试/执行证据”的情况给出 BLOCKER 或高优先级告警。
- 建议改动层级: rule / policy, middleware, workflow, tool, eval
- prompt / context: `verify constraints` 不应只验证仓库治理文档是否齐全；当它被用作 close 前新鲜证据时，必须同时对当前 work item 的关键合同面负责。
- rule / policy: 对活动 work item 的核心合同（authoring、reviewer、backend、release gate 等）建立最小 feature-coverage object 清单；缺少对象或对象形状不符时，verification gate 不得静默通过。
- middleware: 扩展 verification gate object registry，使其可声明并校验 work-item-scoped feature contract surfaces，而不只是 repo-wide governance files。
- workflow: 执行 `verify constraints` 时默认读取当前 spec/work item 上下文，输出“规则面 PASS / feature-contract FAIL”之类的分层结论，避免单一绿灯掩盖主需求未实现。
- tool: `src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/verify_cmd.py`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`
- eval: missing-feature-contract-surface 次数、verify-false-green 次数、spec-only-without-implementation 检出率
- 风险等级: 高
- 收口说明（2026-03-29）: `src/ai_sdlc/core/verify_constraints.py` 与 `src/ai_sdlc/cli/verify_cmd.py` 已引入 `003` authoring / reviewer / backend / release-gate feature-contract coverage surfaces，缺面即 BLOCK；对应 unit/integration tests 已覆盖缺失与完整两类正反场景。
- 可验证成功标准: 当活动 work item 的关键 FR/SC cluster 没有对应实现 surface 或测试覆盖时，`verify constraints` 必须输出明确 BLOCKER；当 surface 完整且测试/证据存在时才允许 PASS。
- 是否需要回归测试补充: 是：补 `003` 类 feature-contract surface 缺失/存在的 CLI 与 unit 正反测试。

## FD-2026-03-29-003 | work item 台账允许“最新 batch 局部成功”掩盖“前序 batch 未实现”

- 日期 (UTC): 2026-03-29
- 来源: self_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md, specs/003-cross-cutting-authoring-and-extension-contracts/task-execution-log.md
- 现象: work item 当前允许 `tasks.md` 声明多个 batch / task cluster，而 `task-execution-log.md` 只记录最近一次局部执行批次；若没有额外校验 planned batch 覆盖或“已完成”标记来源，读者很容易把“Batch 6 已关闭”误读成“整个 003 已收口”。
- 触发场景: `003` 的 `tasks.md` 明确规划了 Batch 1~6，但 `task-execution-log.md` 只存在 Batch 6 的执行记录；同时 close-check/verify 也没有要求 execution-log 覆盖 Batch 1~5，从而让台账真值出现歧义。
- 影响范围: execution evidence 可读性、任务真值一致性、缺陷归属判断、后续开发排期，以及 framework defect / requirement gap 的边界管理。
- 根因分类: B, D, H
- 未来杜绝方案摘要: 建立“planned batches/tasks -> execution evidence -> close verdict”强映射；凡 `tasks.md` 声明的 batch/task 尚无执行证据或显式延期状态，台账与 close surface 都必须给出未收口提示，避免局部成功覆盖全局未完成。
- 建议改动层级: middleware, workflow, tool, eval
- prompt / context: execution log 是工作项事实的一部分，不是任意追加的证明材料；读到单个 batch 的成功时，框架必须同时说明其覆盖边界。
- rule / policy: `tasks.md` 中每个 planned batch/task cluster 必须有对应 execution evidence、明确的未开始/延期状态，或显式重开说明；缺其一即不能宣称整体完成。
- middleware: 提供 planned-batch coverage parser，对比 `tasks.md` 与 `task-execution-log.md`，生成“missing execution evidence”清单。
- workflow: 每次追加 execution log 或关闭 defect 时，同步更新 batch 覆盖状态；批次局部成功后若前序 batch 仍空缺，应在文档顶部显式写明“仅覆盖某 batch，不代表整体收口”。
- tool: `src/ai_sdlc/core/close_check.py`、新增 `src/ai_sdlc/core/workitem_traceability.py`（或等价层）、`tests/unit/test_close_check.py`、`docs/framework-defect-backlog.zh-CN.md`
- eval: latest-batch-overgeneralization 次数、missing-execution-coverage 检出率、traceability-ambiguity 事件数
- 风险等级: 中
- 收口说明（2026-03-29）: `003` 的 `tasks.md`、`task-execution-log.md` 与 `release-gate-evidence.md` 已重新对账，Batch `1~5` 的真实实现提交、验证命令与 release-gate evidence 均已补齐，台账不再允许“只看最新 batch”外推整项完成。
- 可验证成功标准: 当 `tasks.md` 声明多个 batch 而 execution-log 只覆盖部分 batch 时，close surface 必须显式显示缺口；补齐所有 batch 的 execution evidence 或显式未开始状态后，台账口径恢复单一真值。
- 是否需要回归测试补充: 是：补 planned batch 与 execution-log 覆盖对比的 parser / close-check 回归测试。

## FD-2026-03-24-001 | IDE 计划待办与仓库实现事实长期漂移

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: closed
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
- 收口说明（2026-03-28）: `001` 已通过 plan/traceability/close-check 收口链把“计划状态必须回到仓库真值”固化为正式约束；该缺口不再保留为独立待修项。
- 可验证成功标准: 给定存在外部计划文件的工作项，`plan-check` 能稳定发现待办状态漂移；close 清单要求显式处理漂移。
- 是否需要回归测试补充: 是：补充 `plan-check` 与 close 对账的正反用例。

## FD-2026-03-24-002 | design 未落到 tasks 即直接进入执行

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: closed
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
- 收口说明（2026-03-28）: `001` 的 decompose / execute 前置校验、`task_ac_checks` 与相关规则文本已把“先落 `tasks.md` 再进入实现”收敛为正式约束，本条按已闭环归档。
- 可验证成功标准: 缺少 `tasks.md` 或任务级 AC 时，decompose/execute 相关门禁必须非零阻断，且提示首个不合规任务。
- 是否需要回归测试补充: 是：补充 decompose gate、execute prerequisite 与 verify constraints 的一致性测试。

## FD-2026-03-24-003 | 未完成全量验证即声称交付

- 日期 (UTC): 2026-03-24
- 来源: migrated_from_legacy_registry
- 状态: closed
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
- 处置进展（2026-03-28）: `001` Batch 16 Task 6.43 已完成两轮收口：第一轮把“未 commit 收口”落成 `close-check.git_closure` blocker；第二轮把 `docs-only / rules-only / code-change` 最小 fresh verification 画像写入 `verification.md`、PR checklist、execution-log 模板，并让 `close-check` 校验 latest batch 画像与证据、`verify constraints` 校验规则 surface 完整性。定向回归 **55 passed**，仓库级 `uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 与 `uv run ai-sdlc verify constraints` 均已通过，因此本条 defect 关单。
- 下一步任务归属（2026-03-28）: 已在 `001-ai-sdlc-framework` Batch 16 Task 6.43 收口，无新增 action item。
- 可验证成功标准: PR/交付前清单与规则均要求新鲜验证证据；相关测试或流程检查能阻止无证据完成声明。
- 是否需要回归测试补充: 是：补充文档变更与规则变更下的 verify/close-check 覆盖。

## FD-2026-03-25-001 | 收口动作与文档事实未同步闭环

- 日期 (UTC): 2026-03-25
- 来源: migrated_from_legacy_registry
- 状态: closed
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
- 收口说明（2026-03-28）: `001` 已把 execution-log、里程碑、close-check 与 backlog 对账纳入同一收口链，本条不再作为独立未收口项保留。
- 可验证成功标准: close-check 与清单能够在收口遗漏时发出明确 BLOCKER；文档与实现事实不再长期漂移。
- 是否需要回归测试补充: 是：补充 close-check 与用户手册一致性的验证用例。

## FD-2026-03-26-001 | 用户要求“先落需求再实现”时仍默认进入编码

- 日期 (UTC): 2026-03-26
- 来源: migrated_from_legacy_registry
- 状态: closed
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
- 处置进展（2026-03-28）: `001` Batch 16 Task 6.44 已完成收口：`task_ac_checks` 新增 doc-first / requirements-first 共享判定，`ExecuteGate` 会对目标任务为“仅文档 / 仅需求沉淀 / 先 spec-plan-tasks”时直接报 `doc_first_prerequisite`，并在默认改动 `src/` 非 Markdown 代码或 `tests/` 路径时给出阻断提示；`verify constraints` 同步校验 `pipeline.md` / `agent-skip-registry.zh.md` 的术语 surface 与当前 `tasks.md` 中 doc-first 任务的路径范围。定向回归 **101 passed**，`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 已通过，因此本条 defect 关单。
- 可验证成功标准: 在“仅文档 / 先需求”指令下，规则文本与流程检查均指向 design/decompose，且不鼓励直接修改代码。
- 是否需要回归测试补充: 是：补充规则文本与执行前判定的覆盖。

## FD-2026-03-26-002 | CLI 升级后无法认领旧产物，流水线长期停留在 init

- 日期 (UTC): 2026-03-26
- 来源: user_report
- 状态: closed
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
- 处置进展（2026-03-28）: `001` Batch 15 的 Task 6.40 / 6.41 已收口：blank checkpoint 场景下 `status` 会直接给 reconcile guidance，`recover` 在 stale `init/unknown` checkpoint 且未执行 `--reconcile` 时会停止，`specs/<WI>/` 旧布局与旧 `project-state.yaml` 残留字段已进入自动化回归；`status/recover/run/stage` 定向回归、reconcile/context 单测、`workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 与 `verify constraints` 均已通过，因此本条 defect 关单。
- 下一步任务归属（2026-03-28）: 已在 `001-ai-sdlc-framework` Batch 15 Task 6.41 对账收口，无新增 action item。
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
- 状态: closed
- owner: codex
- wi_id: 003-cross-cutting-authoring-and-extension-contracts
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
- 处置进展（2026-03-28）: `source_chain_compatible()` 已按 session/run 前缀父链兼容生效，run 级 artifact 现在可以合法引用同一 `workflow_run_id` 下的 step 级 evidence / evaluation；跨 session / run 的 source 仍被拒绝。配套 `tests/unit/test_telemetry_publisher.py` 与 Batch 6 的综合 telemetry 回归 **73 passed**，本条 defect 已在 `003` Batch 6 收口。
- 下一步任务归属（2026-03-28）: 已在 `003-cross-cutting-authoring-and-extension-contracts` Batch 6 Task 6.1 / 6.3 收口，无新增 action item。
- 可验证成功标准: run 级 artifact 能发布引用同 run 下 step 级 source 的合法闭包；跨 session/run 的 source 仍被拒绝。
- 是否需要回归测试补充: 是：补充 run->step source closure 正例与真正跨链负例。

## FD-2026-03-27-012 | CCP registry 冻结了 gate/audit 控制点，但 raw trace 里无法证明这些控制点

- 日期 (UTC): 2026-03-27
- 来源: final_review
- 状态: closed
- owner: codex
- wi_id: 003-cross-cutting-authoring-and-extension-contracts
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
- 处置进展（2026-03-28）: 新增 `src/ai_sdlc/telemetry/control_points.py` 作为 gate/audit canonical control-point helper；`RuntimeTelemetry.record_gate_control_point()` 与 `GovernancePublisher` 复用同一套 canonical event 形状，`calculate_ccp_coverage_gaps()` 改为同时校验 canonical raw trace 事件形状与 registry 的 `minimum_evidence_closure`，不再接受错误 scope / writer 或缺最小证据闭包的伪覆盖。相关 telemetry governance / runner / publisher / contract 回归 **73 passed**，`uv run ai-sdlc verify constraints` 无 BLOCKER，本条 defect 已在 `003` Batch 6 收口。
- 下一步任务归属（2026-03-28）: 已在 `003-cross-cutting-authoring-and-extension-contracts` Batch 6 Task 6.2 / 6.3 收口，无新增 action item。
- 可验证成功标准: registry 中的 `gate_hit`、`gate_blocked`、`audit_report_generated` 都能从 persisted trace 中被稳定识别并计入 coverage evaluator。
- 是否需要回归测试补充: 是：补 gate/audit CCP 持久化与 coverage evaluator 的正反测试。

## FD-2026-03-27-013 | status/readiness 的 latest 与 latest-index 视图会陈旧，无法跟随真实写入刷新

- 日期 (UTC): 2026-03-27
- 来源: final_review
- 状态: closed
- owner: codex
- wi_id: 004-operator-surfaces-and-post-prd-extensions
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
- 处置进展（2026-03-28）: `TelemetryStore` 新增只读 `derive_index_payloads()`，把 `timeline-cursor` / `open-violations` / `latest-artifacts` 的 canonical 派生真值抽成共享逻辑；`readiness.py` 在 index 缺失或无效时改为回退到内存派生索引，而不是目录 `mtime` 或 manifest/dict 顺序猜测。新增回归覆盖“删掉 indexes 后 latest summary 仍反映 fresh violation/artifact”“伪造 `mtime` 也不会带偏 latest/current”，`tests/unit/test_telemetry_store.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py` **50 passed**，`uv run ai-sdlc verify constraints` 通过，因此本条 defect 已在 `004` Batch 6 收口。
- 下一步任务归属（2026-03-28）: 已在 `004-operator-surfaces-and-post-prd-extensions` Batch 6 Task 6.1 / 6.2 收口，无新增 action item。
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
- 状态: fixed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- 现象: `checkpoint.yml` 已推进到较新阶段甚至 `close`，但 `resume-pack.yaml` 仍停留在更早的 `execute`/旧 batch；此后再次执行 `ai-sdlc recover` 时，CLI 会继续读取旧 `resume-pack` 并向用户报告过期断点，形成“每次中断都回到同一旧位置”的假象。
- 触发场景: 流水线运行过程中持续写入 `checkpoint.yml`，但 `resume-pack.yaml` 未随阶段推进自动刷新；或用户在已有旧 `resume-pack` 的项目里多次中断/恢复，`recover` 继续把旧 pack 当成可用真值。
- 影响范围: 断点恢复可信度、阶段推进判断、批次续跑、用户对 CLI 状态面的信任，以及“是否已真正恢复到最新位置”的操作决策。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: 断点恢复必须收敛为单一真值来源：`checkpoint.yml` 为唯一恢复真值，`resume-pack.yaml` 仅是由 checkpoint 派生出的上下文快照，且必须在 checkpoint 变更时同步刷新。`recover/status` 需要显式校验两者的一致性，发现 stale pack 时要阻断或自动重建，而不是继续静默复用旧快照。
- 收口说明（2026-03-28）: `load_resume_pack()` 已改为统一执行 strict checkpoint 校验，并以 `checkpoint_last_updated` + `checkpoint_fingerprint` 判定 root/work-item `resume-pack` 是否 stale；当 pack 缺失、损坏或 stale 且 checkpoint 有效时，自动重建并原子写回派生快照；当 checkpoint 无效或不兼容时，直接失败，不再回退信任旧 pack。`ai-sdlc recover` 与 `ai-sdlc status` 现已统一走该入口，并输出 `stale` / `rebuilding from checkpoint` / `rebuilt successfully` 等可观测提示。
- 建议改动层级: prompt / context, rule / policy, middleware, workflow, tool, eval
- prompt / context: 所有面向用户的恢复说明必须明确“checkpoint 是恢复真值，resume-pack 是派生快照”；不得把旧快照继续表述成当前断点。
- rule / policy: 规定 checkpoint 为唯一断点真值；resume-pack 不得独立领先或落后于 checkpoint 而仍被视为有效恢复依据。
- middleware: `load_resume_pack()` 统一执行 checkpoint 校验、stale 判定与 root/work-item pack 原子重建；旧 pack 不再被视为可独立信任的恢复真值。
- workflow: 每次 `recover` / `status` 进入恢复路径前，先做 checkpoint↔resume-pack 对账；pack 缺失、损坏、stale 时只允许“自动重建后继续”，checkpoint 无效时直接中断。
- tool: `src/ai_sdlc/context/state.py`、`src/ai_sdlc/models/state.py`、`src/ai_sdlc/cli/commands.py`、`ai-sdlc recover`、`ai-sdlc status`
- eval: stale-resume-pack 检出率、recover 使用过期 pack 的发生率、checkpoint/save 后 pack 自动刷新覆盖率、恢复位置误报次数
- 风险等级: 高
- 可验证成功标准: 给定“checkpoint 已推进、resume-pack 仍旧”的夹具时，`recover` 与 `status` 必须识别并拒绝陈旧 pack，或自动按最新 checkpoint 重建；正常路径下每次 checkpoint 更新后磁盘上的 resume-pack 都与最新 stage/batch 一致，不再反复回到旧断点。
- 是否需要回归测试补充: 已完成：补 pack 缺失 / 损坏 / stale 自动重建、checkpoint 不兼容失败、`recover/status` 遇到双状态源失配时的自动重建与显示语义测试。

## FD-2026-03-28-002 | 001 Batch 13/14 曾出现里程碑先于 execution-log 的假完成漂移

- 日期 (UTC): 2026-03-28
- 来源: self_review, traceability_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/001-ai-sdlc-framework/tasks.md, specs/001-ai-sdlc-framework/task-execution-log.md
- 现象: `001` 的 Batch 13 / 14 一度出现“代码实现与聊天收口已存在，但 `tasks.md` 里程碑先于 execution-log 真值更新”的漂移：`M13` 曾被记成已完成，而主线 [`task-execution-log.md`](../specs/001-ai-sdlc-framework/task-execution-log.md) 当时仍只有到 Batch 12 的归档证据。
- 触发场景: Batch 13 / 14 实现先落在本地 worktree 分支 `codex/batch13-rg001-rg006`，聊天结论与 `tasks.md` 先引用了该实现结果，但 execution-log 归档和主线合流动作没有在同一轮同步完成。
- 影响范围: `001` 完成度判断、后续任务调度、人工 traceability 对账，以及用户对框架“已完成/未完成”口径的信任。
- 根因分类: A, B, H
- 未来杜绝方案摘要: 里程碑、Batch 收口和“已完成”表述必须回到 execution-log / 收口块真值，不允许只因为某个分支已有实现或会话里提到“已完成”就提前宣称主线已收口。close 前应增加“里程碑是否存在对应 execution-log 批次证据”的一致性检查。
- 建议改动层级: rule / policy, workflow, tool, eval
- prompt / context: “某个分支已有实现”不等于“主线已执行完成”；凡涉及完成性表述，都必须先核对 execution-log、收口块和主线 Git 真值。
- rule / policy: 里程碑表只能索引已存在的 execution-log / 收口证据；若 Batch 尚无对应归档，不得在 `tasks.md` 中标注“完成”。
- middleware: 为 `close-check` 或后续 `trace-check` 增加“任务/里程碑完成表述 vs execution-log 批次证据”一致性校验。
- workflow: 更新 `tasks.md` 的 Batch / milestone 状态前，先核对对应 batch 是否已合入主线并写入 execution-log、验证命令和收口块；缺其一则只能记为 `planned` / `pending`。
- tool: `ai-sdlc workitem close-check`、后续 `trace-check`、`specs/001-ai-sdlc-framework/tasks.md`
- eval: 假完成里程碑检出率、里程碑与 execution-log 漂移次数
- 风险等级: 高
- 最终收口 (2026-03-28):
  - 已将 [`task-execution-log.md`](../specs/001-ai-sdlc-framework/task-execution-log.md) 补齐 Batch `2026-03-28-019` / `2026-03-28-020` 的正式归档。
  - 已将 [`tasks.md`](../specs/001-ai-sdlc-framework/tasks.md) 的 Batch 13 / 14 状态与 `M13` 重新对齐到 execution-log 真值。
  - 收口验证以本次合流后的 `uv run pytest -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 为准。
- 可验证成功标准: 给定“里程碑写完成但 execution-log 无对应批次”的夹具时，close/trace 对账能稳定发现并阻断；正常路径下，里程碑只引用已存在的 Batch 收口证据。
- 是否需要回归测试补充: 是：补 milestone/execution-log 漂移的正反夹具，验证 close-check 或等价 trace-check 能发现假完成状态。

## FD-2026-03-28-003 | 001 新补 RG-001~009 合同曾在分支实现后未及时合入主线，且主线/归档真值滞后

- 日期 (UTC): 2026-03-28
- 来源: self_review, traceability_review
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: specs/001-ai-sdlc-framework/spec.md, specs/001-ai-sdlc-framework/tasks.md, specs/001-ai-sdlc-framework/task-execution-log.md
- 现象: `001` 在 2026-03-28 新增的 `RG-001~009` 合同，其实现曾先落在 worktree 分支 `codex/batch13-rg001-rg006`（提交 `ef63c2a` / `f21115a`）而未及时合入 `main`，导致按主线审视时会看到“spec/tasks 已补、当前分支聊天也称已收口，但主线代码与归档仍停留在 Batch 12”的错位。
- 触发场景: Batch 13 / 14 在独立分支完成了代码、测试与局部文档回填，但 branch close-out 没有与主线 merge、execution-log 补录、milestone 对账放在同一收口动作里完成。
- 影响范围: `001` 的 traceability、需求真值可信度、后续执行优先级、用户对“spec 已补齐是否等于主线已支持”的判断，以及主线代码/文档/归档的一致性。
- 根因分类: A, B, D, H
- 未来杜绝方案摘要: 对“补 spec 后立即实现”的合同，必须把 branch 实现、主线合流、execution-log 归档和 milestone 对账视为同一批次的法定尾部动作。只在 worktree 分支上完成实现和测试，不得向主线用户表述为“已收口”。
- 建议改动层级: prompt / context, rule / policy, middleware, workflow, tool, eval
- prompt / context: 将新合同写进 `spec.md` 只是冻结需求边界；即便某个分支已完成代码，也必须区分“分支已实现”和“主线已兑现”。
- rule / policy: 凡涉及新增 FR / SC / RG 合同的完成性表述，必须同时满足主线代码可见、execution-log 已归档、tasks/milestone 已对账三项条件。
- middleware: 为最终交付路径增加 branch-vs-main 真值检查；在 close-out 前自动核对当前实现是否仅存在于 worktree 分支。
- workflow: 每次缺口收敛后，必须同步完成 `spec -> tasks -> code -> tests -> execution-log -> merge-to-main` 的最小映射；若实现尚未合回主线，最终答复必须明确披露“仅分支已完成”。
- tool: `git branch --contains`、`git rev-list --left-right --count`、`ai-sdlc workitem close-check`、后续 `trace-check`
- eval: “分支已实现但主线未合流” 缺口数、RG/SC 主线兑现延迟次数、spec / main / execution-log 漂移次数
- 风险等级: 高
- 最终收口 (2026-03-28):
  - 已完成 `codex/batch13-rg001-rg006` 的代码审查，并将 Batch 13 / 14 实现合回 `main`。
  - 已把 `RG-001~009` 对应的主线代码、`tasks.md`、`task-execution-log.md` 与 backlog 真值同步到同一状态。
  - 新鲜验证包括：Batch 13 定向回归 `87 passed`、Batch 14 定向回归 `111 passed`、全量 `uv run pytest -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`。
- 可验证成功标准: 给定“分支已有实现但主线 / execution-log 未同步”的夹具时，traceability 检查能报出明确 blocker 或 warning；正常路径下，`RG-001~009` 都能在主线代码、测试和 execution-log 中找到一致映射。
- 是否需要回归测试补充: 是：补“分支已实现但主线未合流”的检测夹具，并继续保留 `RG-001~009` 的 unit/flow/integration/traceability 回归。

## FD-2026-03-28-004 | 并行 Git 写命令未被 guardrail 阻断，导致 `.git/index.lock` 争抢与假失败

- 日期 (UTC): 2026-03-28
- 来源: self_review, user_report
- 状态: closed
- owner: codex
- wi_id: 001-ai-sdlc-framework
- related_doc: docs/框架自迭代开发与发布约定.md
- 现象: 当代理把同一仓库内的 Git 写命令并行发起时，例如 `git add` 与 `git commit` 或其他会写 index / refs 的命令重叠执行，后发命令会报 `fatal: Unable to create '.git/index.lock': File exists.`。这类失败通常不是仓库内容冲突，而是本地 Git 临界区被并发踩踏，随后又容易诱发“先删锁文件再继续”的次生操作。
- 触发场景: 使用并行工具同时执行多个 Git 写操作，或在前一个 Git 写命令尚未完成时继续触发 `commit` / `merge` / `checkout` / `branch -d` / `worktree remove` 等后续写操作。
- 影响范围: 提交/合并流程稳定性、代理对 Git 真值的判断、收口效率，以及误删仍被活跃 Git 进程持有的锁文件所带来的额外风险。
- 根因分类: A, B, H
- 未来杜绝方案摘要: 把同仓库内的 Git 写操作明确视为互斥临界区，禁止并行调度；在执行 `commit` / `merge` / `checkout` 等命令前先做仓库级写锁预检查。只有在确认没有活跃 Git 进程、且锁文件确属遗留垃圾时，才允许进入“移除 stale lock”分支，不能把删锁当成默认恢复手段。
- 建议改动层级: prompt / context, rule / policy, middleware, workflow, tool, eval
- prompt / context: 明确声明 Git 写命令不得并行；`git add`、`git commit`、`git merge`、`git checkout`、`git branch -d/-D`、`git worktree remove` 等都属于需要串行化的仓库写操作。
- rule / policy: 在同一仓库内，禁止通过并行执行器同时发起两个及以上 Git 写命令；任何完成性收口前，必须保证 Git 写操作已经串行结束。
- middleware: 为 Git 命令执行增加写命令分类和互斥 guard；发现 `.git/index.lock` 时先检查是否仍有活跃 Git 进程，而不是直接建议删除。
- workflow: 收口顺序固定为 `git add -> git status/diff -> git commit -> git push`，不允许把这些步骤打包进并行工具；若出现锁文件错误，先判定是并发导致还是陈旧锁，再决定是否清理。
- tool: `multi_tool_use.parallel` 使用约束、Git 执行封装、future close-out helper、`git status --short`
- eval: `.git/index.lock` 争抢事件数、Git 写命令重叠调度次数、误删活跃锁文件的险情次数、dirty-worktree 收口中断次数
- 风险等级: 中
- 下一步任务归属（2026-03-28）: `001-ai-sdlc-framework` Batch 16 Task 6.42（已完成）。
- 处置进展（2026-03-28）: `001` Batch 16 Task 6.42 已完成收口：[`GitClient`](../src/ai_sdlc/branch/git_client.py) 新增仓库级 Git 写锁，统一把 `git add`、`git commit`、`git merge`、`git checkout`、`git branch` 写操作、`git worktree remove/add`、`git push` 等归入互斥临界区；`add_and_commit()` 固化为 `git add -> git status/diff -> git commit` 顺序，`push()` 明确为后置单独步骤。遇到 `.git/index.lock` 时，helper 会先区分 active vs stale：若存在活跃 Git 进程则直接阻断，若无活跃进程也只允许显式 `remove_stale_index_lock()` 路径，不再默认删锁。定向回归 **58 passed**，`uv run ruff check`、`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 已通过，因此本条 defect 关单。
- 可验证成功标准: 给定“同一仓库内连续发起两个 Git 写命令”的场景时，代理必须串行化或直接拒绝并行执行，不再出现 `.git/index.lock` 争抢；给定“锁文件已存在”的场景时，只有在确认没有活跃 Git 进程后才允许清理陈旧锁文件。
- 是否需要回归测试补充: 是：补一条针对 Git 写命令分类/串行化的 guardrail 检查，并增加“遇到 `.git/index.lock` 时先做进程与锁状态判断”的流程约束测试。
