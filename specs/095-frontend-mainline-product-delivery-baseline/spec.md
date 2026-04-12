# 功能规格：Frontend Mainline Product Delivery Baseline

**功能编号**：`095-frontend-mainline-product-delivery-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；已完成两轮对抗收敛  
**输入**：[`../010-agent-adapter-activation-contract/spec.md`](../010-agent-adapter-activation-contract/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../../pyproject.toml`](../../pyproject.toml)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)、[`../../packaging/offline/install_offline.sh`](../../packaging/offline/install_offline.sh)、[`../../packaging/offline/install_offline.ps1`](../../packaging/offline/install_offline.ps1)

> 口径：`095` 冻结的不是某一个前端 provider，也不是某一个安装脚本，而是“框架前端主线产品交付”这条总合同。它把 novice-friendly 安装初始化、existing project 前端姿态识别、需求确认后的技术方案推荐、受控组件库与适配包安装、`delivery_execution_confirmation_surface`、全链路审计回滚重试、以及真实浏览器质量门禁串成一个单一上游 truth；但它不重写 `094` 的 init 双路径真值，不重写 `073` 的 solution truth，不提前吞并 backend / test 深度优化工单。

## 问题定义

当前仓库已经分别冻结了几条关键真值：

- `094` 冻结了 `init` 的 dual-path onboarding truth
- `073` 冻结了“需求确认完成后”的前端技术方案确认 truth
- `016` 冻结了 `enterprise-vue2` provider 边界
- `071` 冻结了 P1 基础 visual / a11y foundation
- `020` 冻结了 program execute 的 frontend runtime / recheck handoff 边界

但用户真正感知到的“前端主线体验”仍然是碎的，主要缺口不是单点能力，而是**没有一份总合同把这些真值串起来**。当前仍缺少下面八个回答：

1. 用户第一次拿到框架时，如果本机 Python 不是 `3.11+`、Node 缺失、Playwright 浏览器没装，框架是否能自己解决，而不是让用户先手工装环境。
2. existing project 在 `init` 后如何判定“当前前端能不能接管、该不该接管、遇到 React/未知栈怎么办”。
3. 需求确认后，系统如何在“小白默认推荐”和“高级用户显式定制”之间切换，而不是一上来扔一长串技术问题。
4. “内置企业组件库”和“内置外部组件库”在产品上如何并列成为框架官方支持项，而不是一个是正式能力、一个只是零散建议。
5. 选择技术栈、组件库、风格之后，如何自动检测本地已有依赖、缺失依赖、适配包和浏览器依赖，并在不静默安装的前提下完成自动化。
6. 所有自动动作如何做到可审计、可回滚、可重试，而不是一次性黑盒脚本。
7. 现有 frontend quality 只到 P1 visual / a11y foundation，离“真实浏览器里是否好用、是否符合常人交互逻辑、视觉是否偏离要求”还有明显缺口。
8. 上述能力如何先按窄支持矩阵落地，但未来扩到更多 Vue2/Vue3 外部组件库、更多 style pack，甚至 React，而不触发主流程重写。

如果不先冻结这层总合同，后续实现会继续在三种错误之间来回漂移：

- 把 install / init 写成“继续要求用户自己补环境”的工程工具，而不是用户可用产品入口
- 把 solution confirmation、provider install、browser gate 各自做成孤岛，最后小白用户依然走不通
- 为了追求自动化而走向静默安装、不可审计、不可回滚的黑盒行为，反而破坏信任与可维护性

因此，`095` 的目标是冻结一条严格但可扩展的 frontend mainline product delivery baseline：让框架在“拿到框架 -> 进入项目 -> 冻结方案 -> 安装依赖 -> 生成交付 -> 真实浏览器验收”这条主线上具备单一真值与单一边界。

## 范围

- **覆盖**：
  - 前端主线与 `094 / 073 / 071 / 014 / 020` 的总线关系与 truth order
  - host runtime self-healing 的正式边界，包括 `bootstrap acquisition channel` 与 `in-mainline remediation`
  - existing project 的 frontend posture assessment 与 unsupported existing frontend 边界
  - 需求确认后的推荐式技术方案确认体验与高级定制入口
  - framework-controlled registry、provider delivery bundle、适配包与组件库安装计划
  - `solution_confirmation_surface` 与 `delivery_execution_confirmation_surface` 的正式分工
  - 最终确认页、action ledger、rollback、retry、partial failure honesty
  - mandatory browser quality gate，包括 Playwright、visual、a11y 与 `interaction_anti_pattern_checks`
  - 对 backend / test 的浅层 handoff contract
  - 扩展性原则：后续新增 provider / 外部组件库 / style pack 时不重写主流程
- **不覆盖**：
  - 在本 work item 中直接 formalize backend 框架深度优化、测试框架深度优化或全栈 runtime 统一编排
  - 当前阶段直接支持 React runtime、React provider、React 组件库迁移或既有 React 工程自动改造
  - 允许用户在主流程里输入任意 npm URL、任意私有包地址或任意 git 仓库作为组件来源
  - 把 existing project 的旧前端静默迁移成 AI-SDLC 托管前端
  - 把浏览器质量 gate 扩张成“纯主观审美打分模型”或无边界的 AI 审片系统
  - 重写 `073` 已冻结的 provider/style/support matrix 真值，或重写 `094` 已冻结的 init dual-path truth

## 已锁定决策

- `095` 是 frontend mainline 的**总线母规格**；`094` 负责 Stage 0 onboarding truth，`073` 负责 solution truth，`071` 负责 P1 visual/a11y foundation truth，`014` 负责 runtime attachment truth，`020` 负责 execute/recheck truth；`095` 只能消费并串联，不得重写它们。
- `073` 继续独占 `solution_snapshot` 与 `solution_confirmation_surface`；`095` 只在 `solution_snapshot confirmed` 之后生成 `frontend_action_plan`，并独占 `delivery_execution_confirmation_surface`。主线顺序固定为：`solution_snapshot confirmed -> frontend_action_plan generated -> delivery_execution_confirmation -> managed_delivery_apply`。
- 前端主线的执行相位固定拆成三段：`observe`、`plan`、`mutate`。`observe` 只允许识别与评估，`plan` 只允许生成推荐与动作计划，`mutate` 只允许发生在 `delivery_execution_confirmation_surface` 之后。
- 安装与初始化的小白化目标必须包含 **host runtime 自愈**；主线 happy path 不允许把“请先自己安装 Python 3.11 / Node / 浏览器依赖”当作默认前提。
- host runtime 自愈合同固定拆成两层：
  - `bootstrap acquisition channel`：负责拿到“最小可执行宿主”，它依赖既有安装器/离线包渠道，不由 `095` 直接吞并成新的黑盒安装器
  - `in-mainline remediation`：只在已有最小可执行宿主时生效，负责隔离补齐 Node、包管理器、Playwright browsers 等主线依赖
- 自愈不等于静默动作：所有自动下载、安装、写入、升级、scaffold、browser dependency provision，都必须先经过 `delivery_execution_confirmation_surface`。
- 所有自动动作必须同时满足：
  - 可审计
  - 可回滚或可清理
  - 可重试
- 回滚合同必须诚实分层：
  - `framework-managed local artifacts` 必须可回滚
  - 无法严格回滚的外部副作用必须至少可清理、可重试，并显式标记 `non_rollbackable_effect`
- host runtime 自愈默认只允许写入**框架管理的隔离环境**，不默认修改系统全局 Python、Node、npm、pnpm 或浏览器环境。
- 运行平台必须显式区分：
  - `windows`
  - `macos`
  - `linux`
  不允许跨平台乱装，也不允许对未知 OS/架构执行猜测性安装。
- 任何进入写入型阶段的前端主线，在 `managed_delivery_planning` 前必须先检查 `010` 的 `agent_target + activation_state + support_tier + evidence`；未激活状态最多允许查看推荐与阻断原因，不得宣称进入受控交付。
- existing project 如果发现当前前端是 `React` 或其他当前不受支持栈，系统默认行为必须是：
  - 保持原工程不动
  - 标记为 `unsupported_existing_frontend`
  - 继续提供后续非前端托管能力
  - 显示后续选项：`保留现状继续后端/测试`、`显式创建 sidecar 托管前端`
  - 若项目仍需要 AI-SDLC 托管前端，只能通过**显式确认**创建 sidecar/新托管前端路径
- `sidecar_root` 必须是框架新建的受控子树；默认 `will_not_touch` 必须列出旧 frontend 目录、旧 manifest、旧 lockfile。任何 root 级 workspace/CI/proxy/路由集成都必须是单独 action、可拒绝、默认关闭。
- 需求确认后，如果项目需要 frontend，默认必须先展示**一套完整推荐方案**，给用户三个入口：
  - 接受推荐
  - 查看理由
  - 进入高级定制
  不允许默认把所有用户都推入长向导。
- 推荐方案与高级定制不能裂成两条互不相干的流程；高级模式必须支持 `只改这一项` 的字段级 override，以及 `回到推荐方案` 的显式返回，不允许回退成自由文本。
- 第一阶段公开支持矩阵必须收窄，但底层必须按扩展设计冻结。当前受控支持路径固定为：
  - `vue2 + enterprise-vue2`
  - `vue3 + public-primevue`
- 第一阶段必须同时具备：
  - 内置企业组件库托管路径
  - 内置外部公开组件库托管路径
  其中外部公开路径当前固定为 `public-primevue`，它是 framework-controlled registry 的正式一员，不是文档附注。
- 选择技术栈、provider、style 之后，系统必须自动检测本地是否已具备对应 runtime、组件库、adapter、lockfile / package manifest 与浏览器依赖；缺失项可自动下载安装，但只能在确认之后执行。
- browser quality gate 是主线 mandatory gate，不是锦上添花。Phase 1 必须在真实浏览器中验证“功能是否可用、视觉与布局是否明显失真、a11y 底线是否满足、是否命中一组可执行的交互反模式”，而不只是做静态代码检查或主观审美打分。
- backend / test 的深度优化留给后续工单；`095` 当前只冻结前端与 backend / test 的 handoff surface，不抢跑后续深度设计。

## 总体主线分层

前端主线固定拆成七层，每层只有一个明确职责：

1. **Host Readiness**
   - 检查 Python、Node、包管理器、Playwright 浏览器等宿主依赖是否满足
   - 区分 `bootstrap acquisition channel` 与 `in-mainline remediation`
   - 若不满足，生成隔离安装计划或诚实阻断
2. **Stage 0 Onboarding**
   - 继续完全服从 `094`
   - 只负责 `greenfield / existing` dual-path 基线建立
3. **Frontend Posture Assessment**
   - 在不改动现有工程的前提下识别当前仓库 frontend posture
   - 判定 supported / unsupported / ambiguous / none
4. **Solution Freeze**
   - 对“需要托管前端”的项目进入 `073`
   - 冻结 `frontend_stack / provider / style / backend_stack / api_collab_mode`
5. **Managed Delivery Planning**
   - 在 `010` activation truth 满足后，把 host runtime、依赖安装、adapter、脚手架、生成改动收敛为可审计 `frontend_action_plan`
   - 明确区分 `observe` 动作与 `mutating` 动作
   - 生成 `delivery_execution_confirmation_surface`
6. **Managed Delivery Apply**
   - 在用户确认后执行受控下载、安装、写入、scaffold
   - 产生日志、回滚点、清理点与重试点
7. **Browser Quality Gate**
   - 在真实浏览器验证可用性、视觉、a11y 与 `interaction_anti_pattern_checks`
   - 产出 evidence bundle 供 `020` 消费，但不重写 `014/020` 的 attachment / execute gate

这七层的责任顺序不可逆转：

- `095` 不允许先写前端代码、后补确认页
- 不允许先自动安装、后告诉用户改了什么
- 不允许先把 unsupported existing frontend 接管，再事后解释
- 不允许只有代码测试通过，却没有真实浏览器质量证据
- `095` 不定义 `014` 的 attachment state；它只产出可供 `020` 消费的 evidence bundle，是否阻断 execute 仍由 `020` 的 per-spec gate 决定

## 场景模型

### 1. 场景 A：existing project 初始化/接入阶段

该场景的入口仍然由 `094` 的 dual-path onboarding 决定；`095` 只在 onboarding 完成后，引入单独的 frontend posture assessment。

该 assessment 至少区分：

- `no_frontend_detected`
- `supported_existing_candidate`
- `unsupported_existing_frontend`
- `ambiguous_existing_frontend`
- `managed_frontend_already_attached`

行为规则：

- `supported_existing_candidate`
  - 允许给出“可继续评估托管接入”的后续引导
  - 不在 assessment 阶段直接写 provider/runtime 绑定
- `unsupported_existing_frontend`
  - 不得自动迁移
  - 不得自动安装不匹配的 Vue 依赖覆盖现有工程
  - 默认建议是“保持原前端不接管”
  - 必须同时提供可理解的下一步：`保留现状继续后端/测试`、`显式创建 sidecar 托管前端`
  - 若需求仍要求 AI-SDLC 托管前端，只能在后续方案确认中显式选择 sidecar 托管路径
  - `sidecar_root` 只能落在新建受控子树；root 级联动默认关闭且必须单独确认
- `ambiguous_existing_frontend`
  - 只能诚实输出 evidence insufficient / ambiguous
  - 不得伪装成 supported
- `managed_frontend_already_attached`
  - 继续服从 `014` 的 attachment truth
  - `095` 不重复定义第二套 attachment state

### 2. 场景 B：需求确认完成后的技术方案确认阶段

当需求确认表明项目需要 frontend 或 full-stack frontend-delivery 时，必须进入 `073` 的 solution freeze 主线。

默认体验固定为：

1. 先展示完整推荐方案
2. 用户可查看推荐理由与可用性前提
3. 只有在用户显式要求时才进入高级定制向导
4. 高级定制中允许字段级 `只改这一项`，并允许 `回到推荐方案`

该推荐方案必须覆盖：

- `frontend_stack`
- `provider`
- `style_pack`
- `backend_stack`
- `api_collab_mode`

`095` 不重写这些字段真值；其职责是把 `073` 的结果继续接到后续安装计划与浏览器质量 gate。

## 用户故事与验收

### US-095-1

作为 **novice operator**，我希望拿到框架后即使本机没有正确的 Python / Node / 浏览器依赖，也能被框架自动规划并在确认后完成隔离安装，而不是先自己找教程补环境。

**验收**：

1. Given 本机 Python 低于 `3.11` 或缺失，When 我进入前端主线，Then 系统必须生成 host runtime plan，而不是只报错让我自己处理  
2. Given 当前平台是 `Windows / macOS / Linux`，When 系统给出安装动作，Then 只能使用当前 OS 允许的 installer profile，不得跨平台乱装  
3. Given 存在自动下载/安装动作，When 我确认执行前，Then 必须先看到 `delivery_execution_confirmation_surface`，且能看到将要改动的内容、不会改动的内容、失败后的恢复路径

### US-095-2

作为 **brownfield operator**，我希望框架能识别已有项目前端是否受支持；如果它发现的是 React 或未知栈，框架不能擅自改动原工程，但也不能让我整条主线卡死。

**验收**：

1. Given existing project 存在 React 前端，When 系统执行 frontend posture assessment，Then 必须输出 `unsupported_existing_frontend`，而不是假装支持  
2. Given existing project 为 unsupported existing frontend，When 我继续使用框架，Then 原前端工程不得被静默迁移、静默安装 Vue 依赖或静默改写  
3. Given 我仍然需要 AI-SDLC 托管前端，When 我进入方案确认，Then formal docs 必须允许显式 sidecar 托管路径，而不是要求接管旧 React 工程  
4. Given 我处于 unsupported existing frontend，When 系统展示后续路径，Then 必须至少提供 `保留现状继续后端/测试` 与 `创建 sidecar 托管前端` 两种清晰选项

### US-095-3

作为 **需要快速落地产品的用户**，我希望在需求确认之后看到系统先给我一套能落地的完整推荐方案，再决定是否进入高级模式；确认后缺什么依赖就自动补什么，但整个过程可审计、可回滚、可重试。

**验收**：

1. Given 项目需要 frontend，When 我进入方案确认，Then 默认先看到完整推荐方案，而不是直接进入长向导  
2. Given 我确认了 stack/provider/style，When 本地缺少组件库、adapter 或浏览器依赖，Then 系统必须自动检测这些缺失项并生成 action plan  
3. Given action plan 中存在自动动作，When 我查看 `delivery_execution_confirmation_surface`，Then 必须能看到将下载/安装/写入的对象、不会改动的对象、回滚点和可重试单元  
4. Given 我想在推荐方案上只调整一个字段，When 我进入高级定制，Then 系统必须支持字段级 override，并允许一键回到推荐方案

### US-095-4

作为 **reviewer / maintainer**，我希望前端主线最后不是只产出“代码能运行”，而是有真实浏览器下的质量证据，能说明功能是否符合需求、交互是否反人类、视觉是否明显偏离预期。

**验收**：

1. Given 托管前端已生成并可运行，When 系统进入 quality gate，Then 必须在真实浏览器里运行 Playwright 路径，而不是只做静态检查  
2. Given quality gate 通过，When reviewer 查看证据，Then 至少能看到 smoke、visual、a11y 与 `interaction_anti_pattern_checks` 四类 evidence-backed 结果  
3. Given quality gate 失败，When 系统输出结果，Then 必须诚实区分“证据缺失”“可重试失败”“真实 blocker”和“仅建议项”，而不是统一报成代码失败

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-095-001 | `095` 必须作为 frontend mainline product delivery 的母规格被正式定义，用于冻结 install/init → solution → install/apply → browser gate 的总线真值 |
| FR-095-002 | `095` 必须明确自身只消费并串联 `094 / 073 / 014 / 071 / 020 / 016`，不得回写或重写这些已冻结 truth |
| FR-095-003 | `073.solution_snapshot` 与 `073.solution_confirmation_surface` 必须继续是技术方案 canonical truth；`095` 只能新增 `frontend_action_plan` 与 `delivery_execution_confirmation_surface`，不得额外发明第二套 solution truth |
| FR-095-004 | `095` 必须明确 frontend mainline 的最终 ready verdict 必须同时满足方案已冻结、动作计划已确认、动作已执行完毕、browser quality gate 已落证据，而不是只满足其一 |
| FR-095-054 | `095` 必须把前端主线动作分成 `observe / plan / mutate` 三类；任何 `mutate` 动作都不得发生在 `delivery_execution_confirmation_surface` 之前 |
| FR-095-055 | 在进入 `managed_delivery_planning` 前，系统必须检查 `010` 的 `agent_target + activation_state + support_tier + evidence`；未激活状态最多允许查看推荐与阻断原因，不得进入受控交付 |

### Host Runtime Self-Healing

| ID | 需求 |
|----|------|
| FR-095-005 | `095` 必须正式定义 host runtime self-healing contract，至少覆盖 `python >= 3.11`、Node LTS、选定 package manager、Playwright browsers 四类主线依赖，并显式拆分 `bootstrap acquisition channel` 与 `in-mainline remediation` |
| FR-095-006 | host runtime 检查必须显式识别 `windows / macos / linux` 与架构信息，并只允许执行与当前平台匹配的 installer profile |
| FR-095-007 | host runtime self-healing 默认只能落到 framework-managed isolated environment，不得默认污染系统全局运行时 |
| FR-095-008 | 当主线所需 runtime 缺失或版本不满足时，系统必须生成结构化 `host_runtime_plan`，而不是要求用户手工安装后重试 |
| FR-095-009 | 若当前 OS/架构没有受支持 installer profile，系统必须诚实阻断并暴露原因，不得执行猜测性安装 |
| FR-095-010 | host runtime self-healing 的任何下载、安装、升级动作都必须进入 `delivery_execution_confirmation_surface`，不允许静默执行 |
| FR-095-056 | 对 host runtime 相关动作，`framework-managed local artifacts` 必须可回滚；无法严格回滚的外部副作用必须至少可清理、可重试，并显式标记 `non_rollbackable_effect` |

### Existing Project Frontend Posture

| ID | 需求 |
|----|------|
| FR-095-011 | `095` 必须定义 `frontend_posture_assessment` 为 `094` 之后的独立 downstream truth，用于识别 existing project 前端姿态 |
| FR-095-012 | `frontend_posture_assessment` 至少必须区分 `no_frontend_detected / supported_existing_candidate / unsupported_existing_frontend / ambiguous_existing_frontend / managed_frontend_already_attached` |
| FR-095-013 | 当 existing project 检测到 `React` 或其他当前不受支持前端时，系统必须输出 `unsupported_existing_frontend`，并默认保持原前端完全不动 |
| FR-095-014 | `unsupported_existing_frontend` 路径不得自动安装 Vue 依赖、不得自动写 provider binding、不得自动改写原有 frontend 目录 |
| FR-095-015 | 若项目在 unsupported existing frontend 下仍需要 AI-SDLC 托管前端，系统只能在后续方案确认中提供显式 sidecar/new managed frontend 选项，不得隐式接管旧工程 |
| FR-095-016 | `ambiguous_existing_frontend` 必须诚实暴露 evidence 不足；它不是 supported 的弱化别名 |
| FR-095-057 | `sidecar_root` 必须是框架新建的受控子树；默认 `will_not_touch` 必须列出旧 frontend 目录、旧 manifest、旧 lockfile |
| FR-095-058 | 任何 root 级 workspace/lockfile/CI/proxy/路由集成都必须被表达为单独 action，默认关闭、可拒绝、且不得伪装成 sidecar 必做步骤 |

### Requirements-Driven Solution Entry

| ID | 需求 |
|----|------|
| FR-095-017 | 当需求确认表明项目需要 frontend 时，`095` 必须要求进入 `073` 的 solution freeze 主线，而不是跳过方案确认直接安装 runtime |
| FR-095-018 | 默认交互必须先展示一套完整推荐方案，并提供 `接受推荐 / 查看理由 / 进入高级定制` 三种入口 |
| FR-095-019 | 高级模式仍然完全服从 `073` 的结构化选择与 requested/effective truth，不允许回退为自由文本输入技术栈/Provider；同时必须支持字段级 `只改这一项` 与 `回到推荐方案` |
| FR-095-020 | 若 existing project 为 unsupported existing frontend，但需求仍要求托管前端，系统必须支持“原前端保持不动 + 新托管前端 sidecar”这一路径的显式确认 |

### Controlled Registry And Managed Delivery Bundle

| ID | 需求 |
|----|------|
| FR-095-021 | `095` 必须冻结 framework-controlled registry 原则：主流程只允许 framework 官方托管的 provider / component-library delivery entries |
| FR-095-022 | 第一阶段 registry 必须至少包含两类正式条目：`enterprise-vue2` 与 `public-primevue` |
| FR-095-023 | `public-primevue` 必须被定义为 framework 内置的外部公开组件库交付路径，而不是非正式示例 |
| FR-095-024 | 每个可交付条目必须绑定对应的 runtime requirements、组件库包集合、adapter 包集合、`provider_manifest_ref` / `resolved_style_support_ref` 与 verification probes；`095` 不得自持第二份可编辑 style compatibility 真值 |
| FR-095-025 | 当前阶段主流程不得接受任意 npm URL、任意 git repo、任意私有 registry 地址作为用户输入来源 |
| FR-095-026 | 后续新增 Vue2 外部组件库、更多 Vue3 外部组件库或其他 provider 时，必须通过新增 registry entry / adapter / manifest 扩展，而不是改写主流程状态机 |

### Local Detection And Action Planning

| ID | 需求 |
|----|------|
| FR-095-027 | 在 stack/provider/style 冻结后，系统必须自动检测本地是否已具备对应 runtime、组件库、adapter、脚手架基础与浏览器依赖 |
| FR-095-028 | 若本地已存在依赖但版本或兼容性不满足，系统必须把它表达为 `upgrade/replace/reconcile` 动作，而不是简单视为“已存在” |
| FR-095-029 | 若本地缺失依赖，系统必须把缺失项收敛成结构化 `frontend_action_plan`，并在确认后自动执行下载/安装 |
| FR-095-030 | 对私有 enterprise delivery path，如果可用性/凭证前提不满足，系统必须显式进入 `fallback_required` 或 `blocked`，并继续服从 `073` 的 requested/effective/fallback truth |
| FR-095-031 | `frontend_action_plan` 必须显式列出 `will_install / will_download / will_modify / will_generate / will_not_touch` 五类结果面，并区分 `observe` 与 `mutating` 动作，不允许让用户在黑盒执行后再猜变更范围 |

### Delivery Execution Confirmation, Audit, Rollback, Retry

| ID | 需求 |
|----|------|
| FR-095-032 | 主线任何自动动作执行前都必须出现 `delivery_execution_confirmation_surface`；没有确认页就不得执行安装、下载、写入、scaffold 或 browser dependency provision |
| FR-095-033 | `delivery_execution_confirmation_surface` 至少必须展示：`本次会做什么 / 不会改什么 / 为什么需要这样做 / 失败后怎么退回 / 现在可以继续、返回修改、取消`，并列出 host runtime 动作、dependency 动作、写入路径、fallback 差异、回滚点、可重试单元、不可逆副作用分级 |
| FR-095-034 | 所有自动动作都必须写入结构化 `delivery_action_ledger`，记录 action id、目标对象、前置状态、结果状态、失败原因、重试指针与回滚指针 |
| FR-095-035 | `delivery_action_ledger` 必须支持 whole-plan rollback 与 per-action retry；不得只支持“全部重来” |
| FR-095-036 | 当 action plan 部分成功、部分失败时，系统必须保留 honest partial-progress state，并允许按 action 粒度继续重试或回滚 |
| FR-095-037 | rollback 不得依赖“用户自己知道怎么恢复”；系统必须至少记录可以自动恢复的文件/依赖/锁文件/运行时对象边界，并对无法严格回滚的外部副作用显式标记 `non_rollbackable_effect` 与对应清理路径 |
| FR-095-059 | `delivery_execution_confirmation_surface` 必须把 action 明确区分为 `required / optional`；高级用户可以在不回到 solution freeze 的前提下取消或延后 `optional` 动作，但不得取消满足主线约束所必需的 `required` 动作 |
| FR-095-060 | 当 action plan 含有 `non_rollbackable_effect` 或 `manual_recovery_required` 时，`delivery_execution_confirmation_surface` 必须单独展示风险说明、恢复方式，并要求二次确认后才能继续 |

### Browser Quality Gate

| ID | 需求 |
|----|------|
| FR-095-038 | `095` 必须把 browser quality gate 定义为 frontend mainline mandatory gate，且该 gate 必须运行在真实浏览器中 |
| FR-095-039 | browser quality gate 至少必须包含：`playwright_smoke`、`visual_expectation`、`basic_a11y`、`interaction_anti_pattern_checks` 四类检查面 |
| FR-095-040 | `playwright_smoke` 必须验证当前实现的关键主路径是否真实可操作，而不是只检查页面能打开 |
| FR-095-041 | `visual_expectation` 必须基于 `073.solution_snapshot` 中已确认的 `effective_provider / effective_style_pack / style_fidelity_status` 进行判定，并结合关键区域可见性、明显布局断裂、文字溢出、遮挡、空白主视图等规则生成 evidence-backed verdict；它是 requirement-linked 可执行检查，不是完整 visual regression 替代品 |
| FR-095-042 | `basic_a11y` 必须至少消费 `071` 已冻结的 perceivability / semantics / keyboard / focus 底线，不得额外发明第二套 a11y truth |
| FR-095-043 | `interaction_anti_pattern_checks` Phase 1 只允许覆盖 machine-checkable 反模式：主操作不可见、关键反馈脱离上下文、交互路径死胡同、异常 focus trap、 destructive action 默认化、文本溢出/遮挡；每个 blocker 都必须绑定 probe、anchor 与 evidence |
| FR-095-044 | browser quality gate 失败时，系统必须区分 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only`；其中 `advisory_only` 明确定义为非阻断结果，必须附带通俗下一步建议，不得全部混报成“前端测试失败” |
| FR-095-045 | browser quality gate 必须产出结构化 `browser_quality_bundle`，至少包含 trace、截图、检查 verdict、失败锚点、requirement linkage、`spec_dir`、`attachment_scope_ref`、`managed_frontend_target` 与 `readiness_subject_id` |
| FR-095-061 | `browser_quality_bundle` 必须满足 `one bundle == one active spec scope == one managed frontend target`；`020` 只允许消费已完成 scope 绑定的 bundle，不得把 latest bundle 伪装成项目级全局结论 |

### Backend/Test Handoff Boundary

| ID | 需求 |
|----|------|
| FR-095-046 | `095` 当前只冻结 frontend 与 backend/test 的 handoff surface，不 formalize backend/test 深度优化本体 |
| FR-095-047 | frontend mainline 在方案冻结后必须继续带出 `backend_stack` 与 `api_collab_mode`，以保证 frontend 生成与浏览器验证有稳定对接目标 |
| FR-095-048 | frontend mainline 必须为后续 backend/test 深化保留至少三类接口面：API contract mode、browser evidence bundle、frontend test entrypoints |
| FR-095-049 | backend/test 深化工单未来新增时，不得要求重写 `095` 的 install/confirmation/action-ledger/browser-gate 主流程 |

### Extensibility And Honest State

| ID | 需求 |
|----|------|
| FR-095-050 | `095` 必须明确第一阶段支持矩阵可以窄，但主流程状态机、action ledger、registry model 与 browser gate model 必须按扩展设计冻结 |
| FR-095-051 | 未来新增 provider、style pack、外部组件库时，只能通过新增 manifest/registry entry/adapter/gate profile 扩展，不得重写确认页协议或 action ledger 协议 |
| FR-095-052 | 任何 unsupported、blocked、credential-missing、network-failed、ambiguous、partial-progress 状态都必须诚实暴露，不得伪装成 ready |
| FR-095-053 | 主线任何“自动化”能力都不得以牺牲用户可理解性为代价；系统必须始终能回答“它要做什么、为什么要做、做完改了什么、失败后怎么恢复” |

## 关键实体

- **Host Runtime Plan**：承载 Python、Node、包管理器与 Playwright 浏览器的宿主依赖检测结果、平台 profile、安装目标与阻断原因
- **Bootstrap Acquisition Channel**：承载“拿到最小可执行宿主”的既有安装渠道、离线包渠道与平台 profile
- **Frontend Posture Assessment**：承载 existing project 当前前端姿态、支持状态、接管建议与 sidecar 必要性
- **Frontend Action Plan**：承载 solution freeze 之后所有待执行的下载、安装、写入、生成动作集合，并区分 `observe / mutate`
- **Delivery Action Ledger**：承载 action 级审计、回滚点、重试点、partial failure state 与结果回放
- **Delivery Bundle Entry**：承载某个 framework-controlled provider/component-library path 对应的 runtime requirements、包集合、adapter 集合、`provider_manifest_ref` / `resolved_style_support_ref` 与 verification probes
- **Delivery Execution Confirmation Surface**：承载确认前必须完整展示的动作、差异、fallback、不会改动项、恢复路径、可选动作控制、不可逆副作用提示与用户决策入口
- **Browser Quality Bundle**：承载 Playwright 轨迹、截图、visual/a11y/interaction anti-pattern verdict、per-spec scope 绑定与 requirement linkage

## 建议模型

### 1. `host_runtime_plan`

建议字段：

- `plan_id`
- `os_family`
- `arch`
- `required_runtime_entries`
- `missing_runtime_entries`
- `bootstrap_acquisition_channel`
- `remediation_scope`
- `installer_profile_ids`
- `install_target_root`
- `requires_network`
- `requires_credentials`
- `non_rollbackable_effects`
- `status`
  - `ready`
  - `confirm_required`
  - `blocked`
- `blocking_reason_codes`

### 2. `frontend_posture_assessment`

建议字段：

- `assessment_id`
- `detected_frontend_family`
  - `none`
  - `vue2`
  - `vue3`
  - `react`
  - `unknown`
- `detected_component_library`
- `support_status`
  - `no_frontend_detected`
  - `supported_existing_candidate`
  - `unsupported_existing_frontend`
  - `ambiguous_existing_frontend`
  - `managed_frontend_already_attached`
- `takeover_default`
- `next_step_options`
- `sidecar_root_recommendation`
- `source_paths`
- `confidence`
- `reason_codes`

### 3. `frontend_action_plan`

建议字段：

- `action_plan_id`
- `solution_snapshot_id`
- `host_runtime_plan_id`
- `requested_actions`
- `effective_actions`
- `action_items[]`
  - `action_id`
  - `effect_kind`
    - `observe`
    - `plan`
    - `mutate`
  - `target`
  - `requiredness`
    - `required`
    - `optional`
  - `default_selected`
- `will_install`
- `will_download`
- `will_modify`
- `will_generate`
- `will_not_touch`
- `rollback_checkpoint_ids`
- `retryable_action_ids`
- `status`

### 4. `delivery_action_ledger`

建议字段：

- `ledger_id`
- `action_plan_id`
- `actions[]`
  - `action_id`
  - `action_type`
  - `target`
  - `before_state`
  - `after_state`
  - `result_status`
  - `error_code`
  - `rollback_ref`
  - `retry_ref`
  - `cleanup_ref`
  - `non_rollbackable_effect`
  - `manual_recovery_required`
- `created_at`
- `updated_at`

### 5. `browser_quality_bundle`

建议字段：

- `bundle_id`
- `solution_snapshot_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `source_artifact_ref`
- `readiness_subject_id`
- `playwright_trace_refs`
- `screenshot_refs`
- `smoke_verdict`
- `visual_verdict`
- `a11y_verdict`
- `interaction_anti_pattern_verdict`
- `requirement_linkage`
- `blocking_reason_codes`
- `advisory_reason_codes`
- `generated_at`

## 成功标准

- **SC-095-001**：用户拿到框架后，前端主线 happy path 不再把“手工安装 Python 3.11 / Node / 浏览器依赖”当作默认前提
- **SC-095-002**：existing project 遇到 React 或未知前端时，系统能诚实保持原工程不动，并给出后续 sidecar/不接管路径，而不是误接管
- **SC-095-003**：需求确认后，默认交互先展示完整推荐方案，而不是把 novice 用户直接扔进高级技术问卷
- **SC-095-003A**：推荐方案与高级定制之间可以平滑切换，用户能够只改某一个字段并回到推荐方案，不会因为想改一项而掉进整套专家向导
- **SC-095-004**：当前阶段同时具备 enterprise 与 external public component library 两条正式托管路径，且 `public-primevue` 明确是 framework 官方支持项
- **SC-095-005**：所有自动动作在执行前都有 `delivery_execution_confirmation_surface`，执行后都有 action ledger，失败后可回滚或可清理、可重试
- **SC-095-006**：前端主线 ready verdict 不再只依赖代码检查，而是至少具备 Playwright、visual、a11y 与 `interaction_anti_pattern_checks` 的真实浏览器证据
- **SC-095-007**：后续新增 provider / style pack / 外部组件库时，不需要重写主流程状态机、确认页协议或 action ledger 协议

## 后续实现拆分建议

后续 implementation plan 至少应拆为四个实现切片：

1. **Host Runtime Manager**
   - 负责 OS/arch 识别、`bootstrap acquisition channel` 对接、隔离 runtime plan、确认页接入与 installer profile
2. **Frontend Posture And Delivery Registry**
   - 负责 existing project posture assessment、registry entry、delivery bundle、`provider_manifest_ref` 引用与 sidecar 策略
3. **Managed Action Engine**
   - 负责 dependency detection、action plan、action ledger、rollback / cleanup / retry
4. **Browser Quality Gate**
   - 负责 Playwright smoke、visual/a11y/interaction anti-pattern evidence bundle 与 gate verdict

这些切片都必须继续消费 `094 / 073 / 014 / 071 / 020` 的上游 truth，而不是各自再发明一套状态模型。

## 两轮对抗收敛记录

- **Round 1 收敛**：
  - 拆清 `073.solution_confirmation_surface` 与 `095.delivery_execution_confirmation_surface`
  - 把 host runtime 自愈收紧成 `bootstrap acquisition channel` + `in-mainline remediation`
  - 加入 `010` activation gate、`sidecar_root` 不碰旧前端边界、`provider_manifest_ref` 单一 style 真值引用
  - 把 browser gate 从主观 `human_experience` 收紧为可执行的 `interaction_anti_pattern_checks`
- **Round 2 收敛**：
  - 为确认页补齐 `required / optional`、`non_rollbackable_effect`、`manual_recovery_required` 与二次确认
  - 将 `visual_expectation` 绑定到 `073` 已确认的 `effective_*` / `style_fidelity_status`
  - 将 `browser_quality_bundle` 绑定到 `spec_dir + attachment_scope_ref + managed_frontend_target + readiness_subject_id`
  - 修正尾部 hard constraints 与建议模型，确保与主文规范一致

---
related_doc:
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
frontend_mainline_scope: "install_onboarding_solution_delivery_browser_gate"
frontend_mainline_status: "formal_baseline_frozen_two_round_adversarial_converged"
first_release_support_matrix:
  - "vue2 + enterprise-vue2"
  - "vue3 + public-primevue"
hard_constraints:
  - "no_silent_install"
  - "final_confirmation_required"
  - "all_actions_auditable"
  - "all_actions_rollbackable_or_cleanable"
  - "all_actions_retryable"
  - "unsupported_existing_frontend_leave_untouched"
  - "playwright_browser_gate_required"
frontend_evidence_class: "framework_capability"
---
