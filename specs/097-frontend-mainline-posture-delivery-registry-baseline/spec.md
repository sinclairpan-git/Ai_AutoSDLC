# 功能规格：Frontend Mainline Posture Delivery Registry Baseline

**功能编号**：`097-frontend-mainline-posture-delivery-registry-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；按 `095` 下游 implementable slice 收敛  
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../../src/ai_sdlc/models/frontend_provider_profile.py`](../../src/ai_sdlc/models/frontend_provider_profile.py)、[`../../src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`](../../src/ai_sdlc/generators/frontend_provider_profile_artifacts.py)、[`../../src/ai_sdlc/models/frontend_solution_confirmation.py`](../../src/ai_sdlc/models/frontend_solution_confirmation.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../tests/unit/test_frontend_provider_profile_artifacts.py`](../../tests/unit/test_frontend_provider_profile_artifacts.py)、[`../../tests/unit/test_frontend_solution_confirmation_models.py`](../../tests/unit/test_frontend_solution_confirmation_models.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`097` 冻结的不是“旧项目扫描器 + 包安装器 + sidecar 生成器”的黑盒产品，而是 `095` 七层前端主线中的下一块正式合同。它把 `frontend_posture_assessment`、framework-controlled registry、`delivery_bundle_entry`、`sidecar_root` 与 `will_not_touch` 边界收紧成单一 upstream truth；但它不重写 `094` 的 onboarding truth，不重写 `073` 的 `solution_snapshot` truth，不重写 `014` 的 attachment truth，也不提前吞并 `095` 下游的 Managed Action Engine。

## 问题定义

`095` 已把 frontend mainline product delivery 冻结成总线母规格，`096` 又把第一层 `Host Readiness` 收成了独立切片。当前真正还缺的，不是“再多支持几个 provider”，而是 **brownfield frontend 姿态识别与官方交付条目真值还没有独立 formal baseline**。

当前仓库 reality 已经具备几块零散事实：

- `073` 已冻结 `solution_snapshot`、`requested/effective`、`install_strategy` 与 `public-primevue` 的正式推荐路径
- `016` 与当前代码已经表达了 `enterprise-vue2` provider artifact reality
- `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py` 已能 materialize `enterprise-vue2` 与 `public-primevue` 的最小 provider artifacts
- `verify constraints` 与 `program` 路径已经把 `provider.manifest.yaml`、`style-support.yaml` 当作可验证 reality 使用

但仍然缺少一份 formal contract 来统一回答下面几个问题：

1. existing project 的前端姿态到底如何分类；`React`、未知栈、已有托管前端、没有前端，分别意味着什么。
2. `supported_existing_candidate` 是否等于“可以直接接管旧工程”，还是只代表“可以继续进入后续方案确认”。
3. `unsupported_existing_frontend` 下默认不碰旧工程的 no-touch 边界是什么；`sidecar_root` 又与 root 级 workspace/lockfile/CI/proxy/路由集成有什么关系。
4. 哪些 provider / component-library path 才算 framework 官方托管的交付条目；`public-primevue` 不能继续停留在“已有 reality，但 formal contract 不完整”的状态。
5. downstream 的 `frontend_action_plan` 应该引用哪一份 provider/style/runtime/package truth，而不是再次发明一份可编辑 registry。

如果不把这层先冻结，后续实现会继续在四种错误之间来回漂移：

- 把 `React` 或未知 existing frontend 误报成“可接管候选”，然后静默安装 Vue 依赖污染旧工程
- 把 `public-primevue` 当作示例路径，而不是 framework 官方支持项
- 在 `073.solution_snapshot`、provider artifacts、`095.delivery bundle` 之间维护三份彼此打架的 provider/style compatibility truth
- 把 `sidecar_root` 与 root 级联动动作混成一团，最后既说“旧工程不动”，又在默认路径里改根目录

因此，`097` 的目标是冻结一条最小但严格的 Posture + Delivery Registry baseline：先把 existing project 的 frontend posture、官方 delivery entries、`provider_manifest_ref` / `resolved_style_support_ref` 单一引用、以及 sidecar/no-touch 边界收敛成 machine truth，再把真正的安装、生成、写入与回滚动作留给 `095` 下游 action engine。

## 范围

- **覆盖**：
  - `095` 中 `frontend_posture_assessment` 的正式定位、authority、输入输出与状态语义
  - `no_frontend_detected / supported_existing_candidate / unsupported_existing_frontend / ambiguous_existing_frontend / managed_frontend_already_attached` 的正式区分
  - `sidecar_root_recommendation`、默认 `will_not_touch`、root 级联动动作默认关闭的边界
  - framework-controlled registry 与 `delivery_bundle_entry` 的 machine contract
  - 第一阶段正式条目：`enterprise-vue2` 与 `public-primevue`
  - 每个正式条目与 `install_strategy_ids`、runtime requirements、package sets、adapter sets、`provider_manifest_ref`、`resolved_style_support_ref`、verification probes 的绑定关系
  - `097` 与 `094 / 073 / 014 / 095 / 096` 的 truth order 与 downstream handoff
- **不覆盖**：
  - 在本 work item 中直接实现新的 posture detector、代码扫描器、旧工程 takeover executor 或 sidecar scaffold writer
  - 直接 formalize `frontend_action_plan`、`delivery_execution_confirmation_surface`、rollback / cleanup / retry 协议
  - 允许 arbitrary npm URL、arbitrary git repo、arbitrary private registry 地址进入主流程
  - 把 unsupported existing frontend 自动迁移成 AI-SDLC 托管前端
  - 重写 `073` 已冻结的 `solution_snapshot`、fallback chain、install strategy truth
  - 重新发明第二份 provider/style compatibility 真值，替代现有 `provider.manifest.yaml` 与 `style-support.yaml` reality

## 已锁定决策

- `097` 是 `095` 的下一个 implementable slice，承接 `096.Host Readiness` 之后的 posture / registry / delivery bundle truth，而不是新的母规格。
- `097` 只消费并串联 `094` 的 onboarding truth、`073` 的 solution truth、`014` 的 attachment truth、`016` 与当前代码中的 provider artifact reality；不得回写这些 upstream truth。
- `frontend_posture_assessment` 是 observe-only downstream truth；它的职责是诚实分类与给出后续入口，不是直接执行 takeover、安装或写入。
- `supported_existing_candidate` 只表示“可以继续进入后续受控判断”，不表示“旧工程可被默认接管”。
- `unsupported_existing_frontend` 默认语义固定为：旧 frontend 保持不动；如仍需要 AI-SDLC 托管前端，只能在后续 solution freeze 中显式选择 sidecar/new managed frontend 路径。
- `ambiguous_existing_frontend` 固定表示 evidence 不足；不得被当作 supported 的弱化别名。
- `managed_frontend_already_attached` 必须继续服从 `014` 的 attachment truth；`097` 不得重新定义第二套 attachment state。
- `sidecar_root` 只能是框架新建的受控子树，不是默认允许 root 级 workspace/lockfile/CI/proxy/路由联动的借口。
- framework-controlled registry v1 只正式承认 `enterprise-vue2` 与 `public-primevue` 两类内置 delivery entries；它们都必须是 formal contract，而不是示例或散落 reality。
- `public-primevue` 是 framework 官方支持的外部公开交付路径；它不是文档附注、临时 fallback 文案或“仅测试用 provider”。
- 每个 delivery entry 的 provider/style truth 必须继续单向引用既有 artifacts：`provider_manifest_ref` 与 `resolved_style_support_ref`；`097` 不得自持第二份可编辑 style compatibility matrix。
- `097` 只冻结 observe / plan 侧 truth，不授予 mutate 权；任何包安装、依赖写入、sidecar scaffolding、root 级联动、browser provision 仍留给 `095` 下游 action engine 和 confirmation surface。

## 核心模型

### 1. FrontendPostureAssessment

`frontend_posture_assessment` 是 `094` 之后、`073` 之前或并行前置的独立 downstream truth，用于描述 existing project 当前前端姿态与允许的下一步。

其最小字段至少包括：

- `assessment_id`
- `repo_subject_root`
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
- `evidence_refs`
- `will_not_touch_defaults`

其中：

- `takeover_default` 不允许默认落成“自动 takeover 旧工程”
- `next_step_options` 只表达 downstream 可见入口，不等于已创建 action plan
- `will_not_touch_defaults` 必须把旧 frontend 目录、旧 manifest、旧 lockfile 与未确认的 root 级集成列清楚

### 2. SidecarRootRecommendation

`sidecar_root_recommendation` 是 `frontend_posture_assessment` 的受控子面，用于表达“如果后续显式选择 sidecar 托管前端，推荐落到哪里，以及默认不碰什么”。

其最小字段至少包括：

- `recommended_root`
- `root_kind`
  - `new_controlled_subtree`
- `requires_explicit_confirmation`
- `default_will_not_touch`
- `separate_root_level_actions`
- `blocked_reason_codes`

其中：

- `separate_root_level_actions` 至少能区分：workspace、lockfile、CI、proxy、route integration
- 这些 root 级动作只能作为 downstream 单独 action，被显式展示、可拒绝、默认关闭

### 3. FrontendDeliveryRegistry

`frontend_delivery_registry` 是 `095` framework-controlled registry 原则在 `097` 中的正式化表达。它不是开放市场，而是 framework 官方托管交付条目的受控集合。

其最小字段至少包括：

- `registry_id`
- `protocol_version`
- `entry_ids`
- `entries`

v1 至少必须包含：

- `vue2 + enterprise-vue2`
- `vue3 + public-primevue`

### 4. DeliveryBundleEntry

`delivery_bundle_entry` 是 registry 中可被 downstream 规划层消费的单个正式条目。它承载的不是“现在就去安装”，而是“如果后续进入 action planning，应引用哪一份受控 delivery truth”。

其最小字段至少包括：

- `entry_id`
- `frontend_stack`
- `provider_id`
- `access_mode`
- `install_strategy_ids`
- `availability_prerequisites`
- `runtime_requirements`
- `component_library_packages`
- `adapter_packages`
- `provider_manifest_ref`
- `supported_style_entries`
  - `style_pack_id`
  - `fidelity_status`
  - `resolved_style_support_ref`
- `verification_probes`
- `supported_posture_modes`
- `preferred_managed_target_kind`
- `will_not_touch_defaults`

其中：

- `provider_manifest_ref` 必须单向引用 provider artifact truth，不允许在 `097` 中复制改写 provider manifest 内容
- `resolved_style_support_ref` 必须单向引用 style-support truth，不允许在 `097` 中维护第二份 style compatibility 表
- `supported_posture_modes` 至少要能区分：`greenfield_new_managed_frontend`、`supported_existing_candidate`、`unsupported_existing_frontend_sidecar_only`
- `preferred_managed_target_kind` 只能描述建议目标，不等于已批准执行

## 用户故事与验收

### US-097-1

作为 **brownfield operator**，我希望系统能诚实告诉我 existing project 当前前端是否受支持；如果发现的是 `React` 或未知栈，框架不能借“主线自动化”之名动我的旧工程。

**验收**：

1. Given existing project 检测到 `React` 前端，When `frontend_posture_assessment` 输出结果，Then 必须返回 `unsupported_existing_frontend`，而不是伪装成 `supported_existing_candidate`  
2. Given current evidence 只能看出“有前端痕迹，但无法可靠判定”，When posture assessment 完成，Then 必须返回 `ambiguous_existing_frontend`，并保留 evidence 不足语义  
3. Given existing project 为 unsupported existing frontend，When operator 尚未显式选择 sidecar/new managed frontend，Then 默认 `will_not_touch` 必须覆盖旧 frontend 目录、旧 manifest 与旧 lockfile

### US-097-2

作为 **已有可继续评估前端仓库的 operator**，我希望 `supported_existing_candidate` 只代表“可以继续进后续主线”，而不是系统已经偷偷决定接管旧工程。

**验收**：

1. Given existing project 为可继续评估的 Vue 候选，When posture assessment 输出结果，Then 可以返回 `supported_existing_candidate`，但不得同时声称“已 takeover 完成”  
2. Given 仓库已经有 AI-SDLC 托管前端附着 reality，When posture assessment 输出结果，Then 必须返回 `managed_frontend_already_attached`，并继续服从 `014` 的 attachment truth  
3. Given existing project 没有可识别前端，When posture assessment 输出结果，Then 必须返回 `no_frontend_detected`，而不是因为用户后续可能需要前端就提前假装已有托管目标

### US-097-3

作为 **novice operator**，我希望 framework 官方支持的交付路径是受控且可解释的；我不想在确认前被要求输入任意 npm 地址或仓库地址。

**验收**：

1. Given 我查看 `097` formal docs，When 我确认当前 release 支持矩阵，Then 必须至少明确看到 `enterprise-vue2` 与 `public-primevue` 两条正式 delivery entries  
2. Given delivery entry 被 formalize，When 我查看其结构，Then 能看到 runtime requirements、package sets、adapter sets、`provider_manifest_ref`、`resolved_style_support_ref` 与 verification probes  
3. Given 当前阶段主流程，When operator 未进入高级扩展路径，Then formal docs 必须明确不接受 arbitrary npm URL、arbitrary git repo、arbitrary private registry 地址作为 delivery source

### US-097-4

作为 **reviewer / maintainer**，我希望 `097` 能保证 provider/style truth 不再被复制维护，同时把 sidecar 边界写死，这样后续实现不会再用临时逻辑冲掉 formal contract。

**验收**：

1. Given reviewer 检查 `097` formal docs，When 审查 style truth，Then 可以明确读到 `resolved_style_support_ref` 只能引用既有 style-support reality，而不是第二份矩阵  
2. Given reviewer 检查 `097` formal docs，When 审查 `sidecar_root`，Then 可以明确读到 root 级 workspace/lockfile/CI/proxy/路由联动都是单独 action、默认关闭  
3. Given downstream action engine 以后实现，When 它消费 `097` 输出，Then 它应引用 posture assessment 与 delivery bundle entry，而不是再造一份 registry truth

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-097-001 | `097` 必须作为 `095` 下游的 `Frontend Posture + Controlled Registry + Delivery Bundle` implementable slice 被正式定义 |
| FR-097-002 | `097` 必须明确自身只消费并串联 `094 / 073 / 014 / 095 / 096 / 016` 与现有 provider artifact reality，不得回写这些 upstream truth |
| FR-097-003 | `097` 的 canonical machine 输出只允许覆盖 `frontend_posture_assessment`、`sidecar_root_recommendation`、`frontend_delivery_registry` 与 `delivery_bundle_entry`；不得偷渡 mutate 协议 |
| FR-097-004 | `097` 必须明确 `096.host_runtime_plan` 与 `097.frontend_posture_assessment` / `delivery_bundle_entry` 是并列上游 truth；两者都能被 downstream plan 消费，但都不单独授权执行 |

### Frontend Posture Assessment

| ID | 需求 |
|----|------|
| FR-097-005 | `097` 必须正式定义 `frontend_posture_assessment` 为 `094` 之后的独立 downstream truth，用于识别 existing project 前端姿态 |
| FR-097-006 | `frontend_posture_assessment.support_status` 至少必须区分 `no_frontend_detected / supported_existing_candidate / unsupported_existing_frontend / ambiguous_existing_frontend / managed_frontend_already_attached` |
| FR-097-007 | 当 existing project 检测到 `React` 或其他当前不受支持前端时，系统必须输出 `unsupported_existing_frontend`，并默认保持原前端完全不动 |
| FR-097-008 | `supported_existing_candidate` 只能表达“允许进入后续受控判断”；不得被写成“已可默认 takeover 或 provider binding” |
| FR-097-009 | `ambiguous_existing_frontend` 必须诚实暴露 evidence 不足；它不是 supported 的弱化别名 |
| FR-097-010 | `managed_frontend_already_attached` 必须继续引用 `014` 的 attachment truth；`097` 不得另建第二套 attachment state |
| FR-097-011 | `no_frontend_detected` 必须明确表达“当前没有可识别 existing frontend reality”，而不是把未来可能生成的 managed frontend 伪装成已存在事实 |

### Sidecar And No-Touch Boundary

| ID | 需求 |
|----|------|
| FR-097-012 | `unsupported_existing_frontend` 路径不得自动安装 Vue 依赖、不得自动写 provider binding、不得自动改写原有 frontend 目录 |
| FR-097-013 | `sidecar_root` 必须是框架新建的受控子树；默认 `will_not_touch` 必须列出旧 frontend 目录、旧 manifest、旧 lockfile 与未确认的 root 级联动 |
| FR-097-014 | 任何 root 级 workspace/lockfile/CI/proxy/路由集成都必须被表达为单独 action，默认关闭、可拒绝，且不得伪装成 sidecar 必做步骤 |
| FR-097-015 | 若 unsupported existing frontend 仍需 AI-SDLC 托管前端，系统只能在后续 `073` / `095` 主线中显式确认 sidecar/new managed frontend 路径，不得由 `097` 隐式替 operator 决定 |
| FR-097-016 | `sidecar_root_recommendation` 只能表达推荐位置、默认 no-touch 边界与阻断原因；不得直接创建目录、写入脚手架或改动根工程 |

### Controlled Registry And Delivery Bundle

| ID | 需求 |
|----|------|
| FR-097-017 | `097` 必须冻结 framework-controlled registry 原则：主流程只允许 framework 官方托管的 provider / component-library delivery entries |
| FR-097-018 | 第一阶段 registry 必须至少包含两类正式条目：`enterprise-vue2` 与 `public-primevue` |
| FR-097-019 | `public-primevue` 必须被定义为 framework 内置的外部公开组件库交付路径，而不是非正式 fallback 或示例 |
| FR-097-020 | 每个 `delivery_bundle_entry` 必须绑定对应的 `install_strategy_ids`、runtime requirements、组件库包集合、adapter 包集合、`provider_manifest_ref`、`resolved_style_support_ref` 与 verification probes |
| FR-097-021 | `provider_manifest_ref` 与 `resolved_style_support_ref` 必须继续单向引用既有 provider/style artifact reality；`097` 不得自持第二份可编辑 compatibility truth |
| FR-097-022 | 当前阶段主流程不得接受 arbitrary npm URL、arbitrary git repo、arbitrary private registry 地址作为 delivery source |
| FR-097-023 | delivery entry 必须能够表达 `availability_prerequisites`、`supported_posture_modes` 与 `preferred_managed_target_kind`，以便 downstream 规划层知道该条目适用于什么 posture 与交付目标 |
| FR-097-024 | 未来新增 Vue2 外部组件库、更多 Vue3 外部组件库或其他 provider 时，只能通过新增 registry entry / manifest / adapter 扩展，不得改写 `097` 已冻结的 posture 或 registry state semantics |

### Downstream Handoff And Honest State

| ID | 需求 |
|----|------|
| FR-097-025 | `097` 必须明确 downstream `frontend_action_plan` 只能消费 `frontend_posture_assessment`、`host_runtime_plan` 与 `delivery_bundle_entry`，不得在 planning 层重新发明 posture/registry truth |
| FR-097-026 | `097` 不得直接 formalize 包安装、依赖升级、脚手架写入、browser provision、rollback、cleanup 或 retry 协议；这些仍属于 `095` 下游 action engine |
| FR-097-027 | 即使 `096.minimal_executable_host=false`，`097` 仍可以产出 posture / registry truth；但它不得把“posture 已知”误写成“交付已 ready” |
| FR-097-028 | `097` 必须承认当前仓库已有 `provider.manifest.yaml`、`style-support.yaml`、install strategy 与 solution snapshot reality，并把它们提升为 formal upstream 引用，而不是假装已经存在完整 delivery registry runtime |
| FR-097-029 | 任何 unsupported、ambiguous、credential-missing、registry-prerequisite-missing、sidecar-root-blocked 状态都必须诚实暴露，不得伪装成 ready |
| FR-097-030 | `097` 必须为后续实现明确优先补位方向：existing frontend posture detector、registry materialization surface、delivery bundle resolver 与 downstream action-plan binding |

## 关键实体

- **Frontend Posture Assessment**：承载 existing project 当前前端姿态、支持状态、后续入口、sidecar 建议与默认 no-touch 边界
- **Sidecar Root Recommendation**：承载“若后续显式选择 sidecar 托管前端，应落在哪里，以及默认不碰什么”的受控建议
- **Frontend Delivery Registry**：承载 framework 官方托管 delivery entries 的受控集合，不对 arbitrary source 开放
- **Delivery Bundle Entry**：承载某个 provider/component-library path 对应的 runtime requirements、package sets、adapter sets、`provider_manifest_ref` / `resolved_style_support_ref` 与 verification probes
- **Provider Manifest Ref**：指向 provider artifact truth 的唯一引用句柄，不允许在 `097` 中复制改写
- **Resolved Style Support Ref**：指向 style-support truth 的唯一引用句柄，不允许在 `097` 中维护第二份 compatibility matrix

## 成功标准

- **SC-097-001**：existing project 遇到 `React` 或未知前端时，系统能诚实输出 `unsupported` 或 `ambiguous`，并默认保持旧工程不动  
- **SC-097-002**：`supported_existing_candidate`、`managed_frontend_already_attached` 与 `no_frontend_detected` 不再被混成单一“有前端/没前端”粗粒度状态  
- **SC-097-003**：`enterprise-vue2` 与 `public-primevue` 同时成为 framework-controlled registry 的正式条目，且 `public-primevue` 不再是非正式路径  
- **SC-097-004**：`provider_manifest_ref` 与 `resolved_style_support_ref` 成为 provider/style truth 的单一引用来源，downstream 不再需要第二份 registry truth  
- **SC-097-005**：`sidecar_root` 与 root 级联动动作边界被写死，后续实现不会再用“sidecar”名义默认改根目录  
- **SC-097-006**：后续 Managed Action Engine 能直接消费 `097` 的 posture + delivery bundle truth，而不是再重新定义 brownfield posture 和官方 delivery entries

## 后续实现拆分建议

后续 implementation plan 至少应拆为两个收敛批次：

1. **Frontend Posture Detector**
   - 负责从 repo evidence 生成 `frontend_posture_assessment`
   - 固定五类 `support_status`
   - 固定 `sidecar_root_recommendation` 与默认 `will_not_touch`
2. **Delivery Registry Resolver**
   - 负责把现有 built-in provider artifacts、install strategies、style-support reality 收敛成 `frontend_delivery_registry`
   - 对外输出 `delivery_bundle_entry`
   - 为下游 action planning 提供单一 `provider_manifest_ref` / `resolved_style_support_ref` 引用

这两个批次都必须继续消费 `094 / 073 / 014 / 096` 的既有 truth，而不是再发明一套新状态机。

---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
frontend_mainline_scope: "posture_registry_delivery_bundle"
frontend_mainline_status: "formal_baseline_frozen"
registry_v1_entries:
  - "vue2 + enterprise-vue2"
  - "vue3 + public-primevue"
frontend_evidence_class: "framework_capability"
---
