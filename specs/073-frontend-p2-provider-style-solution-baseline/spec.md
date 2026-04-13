# 功能规格：Frontend P2 Provider Style Solution Baseline

**功能编号**：`073-frontend-p2-provider-style-solution-baseline`  
**创建日期**：2026-04-07  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 P2 formal baseline，用于把“技术方案确认、跨栈 Provider 选择与独立 Style Pack 体系”收敛成 framework 内可继续分解与执行的 canonical truth。它不是 `docs/superpowers/*` 下的设计参考稿，也不是直接进入 `src/` / `tests/` 的实现工单。

P2 不把 `provider` 继续收窄为 Vue2 企业组件映射，而是把它升级为一类可选的正式前端交付单元；同时引入独立于 `provider` 的 `style pack` 视觉语义层，并在“需求确认完成之后、技术设计拆分之前”增加一轮技术方案确认，以结构化方式冻结前端栈、Provider、后端栈、API 协作模式与风格。

## 2. 问题定义

### 2.1 当前问题

当前前端治理基线已经具备：

- `UI Kernel`
- `enterprise-vue2 provider`
- 前端生成约束
- 前端 gate / verify 骨架

但 P2 目标要求已经超出“单一企业 Vue2 Provider”边界，主要缺口有：

1. 缺少用户可见的技术方案确认关口，无法在技术设计拆分前冻结技术方案。
2. 缺少跨栈 Provider 模型，无法同时支撑 `Vue2` 企业方案与 `Vue3` 公开方案。
3. 缺少“安装前探测 + 明确切换确认”的企业 Provider 可用性处理机制。
4. 缺少独立于 Provider 的内置风格系统，无法稳定支撑多风格输出。
5. 缺少审计型技术方案快照，无法解释推荐结果、用户改写和 fallback 原因。

### 2.2 本方案要解决的问题

本方案聚焦解决以下问题：

- 在不破坏现有 UI Kernel / Provider 治理边界的前提下，引入可扩展的多 Provider 产品能力。
- 为小白用户提供“简单模式一键确认”与“高级模式结构化向导”的技术方案确认体验。
- 将企业私有 Provider 的可用性判定、安装前探测、显式 fallback 机制工程化。
- 建立独立于 Provider 的 `style pack` 体系，并给出 P2 内置风格集合与支持矩阵。
- 通过 `solution_snapshot` 记录推荐、请求、生效、降级与阻断信息，支撑审计与后续回放。

### 2.3 非目标

本方案明确不解决以下事项：

- 不在 P2 第一阶段开放 `React` 到 UI 选择器。
- 不在 P2 第一阶段同时落地多个公开 Vue3 Provider。
- 不在 P2 第一阶段建设开放式风格编辑器。
- 不把 Ai_AutoSDLC Core 改造成前端运行时组件平台。
- 不要求企业组件库重构为框架原生实现。

---

## 3. 范围与阶段边界

### 3.1 P2 第一阶段实际落地范围

P2 第一阶段只落地两条实际路径：

- `Vue2 -> enterprise-vue2`
- `Vue3 -> public-primevue`

### 3.2 P2 第一阶段的扩展性预留

P2 第一阶段底层按多栈、多 Provider 扩展设计，预留但不开放：

- `react` 前端栈
- `public-element-plus`
- `public-react-*`
- 更多安装源
- 更多 style pack

### 3.3 当前阶段的公开退路边界

当前阶段如果 `enterprise-vue2` 不可用，允许的退路不是“只切 Provider”，而是：

- 从 `vue2 + enterprise-vue2`
- 切换到 `vue3 + public-primevue`

这本质上是“切换前端技术栈与 Provider”，必须显式确认，不允许自动切换。

---

## 4. 已锁定决策

### 4.1 技术方案确认时机

技术方案确认放在：

`需求确认完成 -> 技术方案确认 -> 技术设计拆分 -> 开发任务生成`

不放在 `init`，也不拖到代码生成前。

### 4.2 简单模式与高级模式

简单模式：

- 系统只展示 `1` 套主推荐方案
- 不展示备选方案
- 用户只能：
  - 接受推荐
  - 查看推荐理由
  - 切换到高级模式

高级模式：

- 使用结构化分步向导
- 所有方案字段都通过选项选择，不允许手打技术栈 / Provider

### 4.3 Provider 判定目标

系统不判断“这个人是不是内部用户”，只判断：

`当前项目是否具备 enterprise-vue2 的使用条件`

判定依据包括：

- 私有包是否可访问
- 当前环境是否具备企业安装条件
- 需求内容是否强烈指向企业组件体系

### 4.4 requested / effective 成对建模

任何可能被系统重写的方案字段，都必须采用：

- `requested_*`
- `effective_*`

成对建模。

固定规则：

- `requested_*` 永远保存用户原始意图
- fallback 只允许改写 `effective_*`
- 不得覆盖 `requested_*`

### 4.5 React 当前状态

`react` 当前只作为内部可建模值存在：

- 可出现在内部枚举和模型中
- 不出现在 UI
- 不参与简单模式推荐
- 不参与高级模式向导
- 不参与当前 Provider 计算

### 4.6 风格真值来源

风格本体定义与支持矩阵严格分离：

- `style_pack_manifest` 只定义风格本体
- `provider_manifest` 是“某个 Provider 是否支持某个 style pack、支持等级是多少”的唯一真值来源

不允许两边各自维护一套支持真值。

### 4.7 风格支持等级统一枚举

全链路只允许使用一套风格支持等级枚举：

- `full`
- `partial`
- `degraded`
- `unsupported`

该枚举同时用于：

- Provider 风格支持矩阵
- 高级模式风格选择卡片
- 最终确认页
- `solution_snapshot.style_fidelity_status`

### 4.8 简单模式默认不推荐 degraded 风格

简单模式主推荐默认只能推荐：

- `full`
- `partial`

支持等级的风格。

`degraded` 只允许在高级模式中由用户显式选择，并展示降级说明。

---

## 5. 总体架构

### 5.1 四层关系

前端方案由四层共同决定：

1. `frontend_stack`
   - 决定技术基座
2. `provider`
   - 决定组件库与前端交付单元
3. `style_pack`
   - 决定视觉风格语义
4. `adapter`
   - 负责把风格和语义组件翻译到真实组件库能力

### 5.2 关键原则

- `provider` 不是简单组件映射，而是正式交付单元。
- `style pack` 必须独立于 Provider。
- 新增 Provider 不改主流程，只增量补 manifest、adapter、scaffold、支持矩阵。

---

## 6. 技术方案确认交互

### 6.1 简单模式

简单模式输出一套主推荐方案，至少包含：

- 前端栈
- 前端 Provider
- 后端栈
- API 协作模式
- 风格包

简单模式界面必须展示：

- 推荐方案内容
- 推荐理由
- 已通过前提
- 未通过前提
- 当前风格支持等级

简单模式不展示备选方案。

### 6.2 高级模式

高级模式采用分步向导，步骤固定为：

1. 项目形态
2. 前端技术栈
3. 前端 Provider
4. 后端技术栈
5. API 协作模式
6. 风格包
7. 最终确认

每一步都只允许结构化选择。

### 6.3 最终确认页

最终确认页必须显式展示最终预检结果区，至少包含：

- `requested_*`
- `effective_*`
- `preflight_status`
- `will_change_on_confirm`
- `fallback_required`

如果确认后会触发 `requested_* != effective_*`，必须显式展示差异，不允许静默改写。

其中 `will_change_on_confirm` 是 UI 基于 `requested_*`、候选 `effective_*` 与最终预检结果计算出的派生字段，用于提示“确认后是否会发生显式差异”；它不是独立的快照真值字段，最终审计仍以 `solution_snapshot` 中的请求值、生效值、`decision_status` 与 fallback / 降级原因字段为准。

---

## 7. 核心模型

### 7.1 `solution_snapshot`

`solution_snapshot` 是技术方案定版快照，也是审计快照，不是“只存最终结果”的简化记录。

行为规则：

- 每次用户完成一次“技术方案最终确认”，都必须生成一个新的 `solution_snapshot` 版本，不覆盖旧快照。
- 任何用户显式改写、显式确认 fallback、或因最终预检导致的生效值变化，也必须通过新版本快照或等价审计事件表达。
- 快照之间通过 `changed_from_snapshot_id` 串联，保证推荐、请求、生效与 fallback 链路可回放。

#### 7.1.1 基础元数据

- `snapshot_id`
- `project_id`
- `version`
- `created_at`
- `confirmed_at`
- `confirmed_by_mode`

#### 7.1.2 决策状态

- `decision_status`
  - `recommended`
  - `user_confirmed`
  - `fallback_required`
  - `fallback_confirmed`
  - `blocked`

#### 7.1.3 推荐结果

- `recommended_project_shape`
- `recommended_frontend_stack`
- `recommended_provider_id`
- `recommended_backend_stack`
- `recommended_api_collab_mode`
- `recommended_style_pack_id`
- `recommendation_source`
- `recommendation_reason_codes`
- `recommendation_reason_text`

前端、后端、API 协作推荐需要分层输出，不允许混成一个推荐结论。

#### 7.1.4 用户请求值

- `requested_project_shape`
- `requested_frontend_stack`
- `requested_provider_id`
- `requested_backend_stack`
- `requested_api_collab_mode`
- `requested_style_pack_id`

#### 7.1.5 最终生效值

- `effective_project_shape`
- `effective_frontend_stack`
- `effective_provider_id`
- `effective_backend_stack`
- `effective_api_collab_mode`
- `effective_style_pack_id`

#### 7.1.6 可用性与预检

- `enterprise_provider_eligible`
- `availability_checks`
- `availability_summary`
- `availability_reason_text`
- `preflight_status`
- `preflight_reason_codes`

其中 `availability_summary` 必须是机器可消费对象，至少包含：

- `overall_status`
- `passed_check_ids`
- `failed_check_ids`
- `blocking_reason_codes`

#### 7.1.7 审计与偏差

- `user_overrode_recommendation`
- `user_override_fields`
- `provider_mode`
  - `normal`
  - `cross_stack_fallback`
- `fallback_reason_code`
- `fallback_reason_text`
- `style_fidelity_status`
- `style_degradation_reason_codes`
- `changed_from_snapshot_id`

### 7.2 `provider_manifest`

`provider_manifest` 描述一个 Provider 的完整交付能力，是 Provider 可用性、安装前提、风格支持和退路声明的唯一真值载体。

#### 7.2.1 标识

- `provider_id`
- `display_name`
- `status`
- `visibility`
- `description`

#### 7.2.2 栈与脚手架

- `frontend_stack`
- `scaffold_template_id`
- `minimum_runtime_version`
- `adapter_package`
- `ui_package`

#### 7.2.3 安装与分发

- `access_mode`
  - `public`
  - `private`
- `install_strategy_ids`
- `registry_requirements`
- `credential_requirements`
- `private_package_required`

#### 7.2.4 可用性前提

- `availability_prerequisites`
- `preflight_check_ids`
- `is_currently_available`
- `unavailable_reason_codes`
- `unavailable_reason_text`

#### 7.2.5 能力声明

- `capabilities`
- `theme_depth`
- `layout_density_profile`
- `supports_custom_theme_tokens`

#### 7.2.6 风格支持真值

- `style_support_matrix`
  - 每个 `style_pack_id` 对应：
    - `fidelity_status`
    - `degradation_reason_codes`
    - `notes`
- `default_style_pack_id`

关于风格支持，统一规则如下：

- 是否支持某个风格
- 支持等级是多少
- 降级原因是什么

唯一真值来源全部放在 `provider_manifest.style_support_matrix`。

#### 7.2.7 退路声明

- `cross_stack_fallback_targets`
- `manual_switch_required`
- `migration_notice_template`

### 7.3 `style_pack_manifest`

`style_pack_manifest` 只定义风格本体，不定义 Provider 支持真值。

建议字段：

- `style_pack_id`
- `display_name`
- `status`
- `visibility`
- `description`
- `recommended_for`
- `not_recommended_for`
- `visual_intent`
- `target_density`
- `target_brand_tone`
- `color_profile`
- `surface_profile`
- `typography_profile`
- `radius_profile`
- `shadow_profile`
- `spacing_profile`
- `density_profile`
- `motion_profile`
- `focus_profile`
- `glass_profile`
- `accessibility_profile`
- `supports_customization`
- `customizable_fields`
- `default_for_recommendation_rules`
- `preview_priority`
- `is_enterprise_safe_default`

### 7.4 `install_strategy`

安装策略作为独立模型存在，用于承载不同分发方式的公共规则。

建议至少支持：

- `public_npm`
- `private_registry`
- `gitlab_package`

---

## 8. 当前阶段 Provider 清单

### 8.1 `enterprise-vue2`

- `frontend_stack = vue2`
- `access_mode = private`
- 依赖企业私有组件库和企业适配包
- 需要私有安装条件和可用性前提满足

### 8.2 `public-primevue`

- `frontend_stack = vue3`
- `access_mode = public`
- 依赖公开可安装的 `PrimeVue` 生态与对应适配包
- 作为 P2 第一阶段唯一公开 Provider

---

## 9. 可用性判定与 fallback 规则

### 9.1 判定目标

系统不判断“是否公司内部用户”，只判断：

`当前项目是否具备 enterprise-vue2 的使用条件`

### 9.2 判定输入

判定至少使用三类信号：

1. 环境与安装信号
   - 私有包是否可访问
   - 私有安装源是否可达
   - 当前环境是否具备企业安装条件
2. 需求语义信号
   - 是否明确要求公司组件库
   - 是否强烈指向内部企业系统
3. Provider Manifest 可用性前提
   - `availability_prerequisites`
   - `preflight_check_ids`

### 9.3 企业 Provider 不可用时的规则

如果用户请求：

- `requested_frontend_stack = vue2`
- `requested_provider_id = enterprise-vue2`

但 preflight 失败，则：

1. 不自动切换
2. 将 `decision_status` 标记为 `fallback_required` 或 `blocked`
3. 明确提示需要“切换前端技术栈与 Provider”
4. 只提供两个动作：
   - 切换到 `vue3 + public-primevue`
   - 保持当前请求，等待权限问题解决
5. 只有在用户显式确认后，才修改 `effective_*`

---

## 10. 简单模式推荐规则

### 10.1 推荐器类型

P2 第一阶段使用规则引擎，不做学习型推荐。

### 10.2 需求信号

推荐器至少抽取以下信号：

- `is_internal_enterprise_system`
- `requires_company_component_system`
- `is_public_delivery`
- `is_data_dense_console`
- `emphasizes_modern_visual`
- `needs_fast_delivery`

### 10.3 主推荐路径

当前阶段简单模式只允许输出两类主路径：

#### 规则 A：企业方案

如果：

- 需求强烈指向内部企业体系
- `enterprise_provider_eligible = true`

则推荐：

- `frontend_stack = vue2`
- `provider = enterprise-vue2`
- `style_pack = enterprise-default`

后端和 API 协作模式按独立规则推荐。

#### 规则 B：公开方案

其他所有情况推荐：

- `frontend_stack = vue3`
- `provider = public-primevue`
- `style_pack = modern-saas` 或 `data-console`

### 10.4 后端与 API 协作推荐

后端推荐与前端推荐分开计算：

- `frontend_only` -> `backend_stack = none`
- 内部企业系统、流程 / 权限 / 集成较重 -> `backend_stack = spring-boot`
- 外部交付、快速上线、接口灵活度优先 -> `backend_stack = fastapi`

API 协作模式独立推荐：

- 纯前端 -> `mock_first`
- 前后端分离 -> `contract_first`
- 已明确对接存量后端 -> `direct_backend`

### 10.5 简单模式展示要求

简单模式虽然只展示一套主推荐，但必须同时展示：

- 推荐理由
- 已通过前提
- 未通过前提
- 风格支持等级

并且默认不推荐 `degraded` 风格。

---

## 11. 高级模式分步向导

### 11.1 第 1 步：项目形态

可选项：

- `frontend_only`
- `frontend_backend_separated`
- `fullstack`

### 11.2 第 2 步：前端技术栈

当前仅开放：

- `Vue2`
- `Vue3`

`React` 不显示。

### 11.3 第 3 步：前端 Provider

只展示当前前端栈兼容项：

- `Vue2 -> enterprise-vue2`
- `Vue3 -> public-primevue`

必须同时展示：

- Provider 名称
- 适用场景
- 当前可用性状态
- 不可用原因

### 11.4 第 4 步：后端技术栈

当前选项：

- `none`
- `spring-boot`
- `fastapi`

### 11.5 第 5 步：API 协作模式

当前选项：

- `mock_first`
- `contract_first`
- `direct_backend`

### 11.6 第 6 步：风格包

仅展示当前 Provider 在 `style_support_matrix` 中定义的支持项。

规则：

- `unsupported` 不可选
- `degraded` 可选，但必须展示降级说明
- Provider 变更时风格列表实时重算

### 11.7 第 7 步：最终确认

最终确认页必须展示：

- 推荐方案
- 用户请求方案
- 预计最终生效方案
- 可用性检查结果
- `will_change_on_confirm`
- `fallback_required`
- 风格支持等级
- 风格降级原因

其中 `will_change_on_confirm` 仅作为确认前 UI 预检提示使用，不作为独立持久化真值字段；一旦用户确认，差异结果必须通过新的 `solution_snapshot` 版本与对应审计字段落盘。

---

## 12. Style Pack 方案

### 12.1 风格定位

`style pack` 是独立于 Provider 的视觉语义层，不是散乱的 CSS 主题集合。

### 12.2 风格语义 Token 范围

P2 第一阶段统一使用以下语义维度：

- `brand`
- `accent`
- `text`
- `surface`
- `border`
- `radius`
- `shadow`
- `spacing`
- `density`
- `motion`

玻璃风格额外允许：

- `glass_blur`
- `glass_opacity`
- `glass_edge_highlight`

### 12.3 风格落地三层

风格落地固定分三层：

1. `style_pack_manifest`
   - 定义语义风格
2. `provider theme adapter`
   - 将风格映射为 Provider 可理解的主题能力
3. 项目生成产物
   - 将生效风格写入项目文件

### 12.4 内置 5 套风格

#### 12.4.1 `enterprise-default`

定位：

- 企业系统默认风格
- 稳、克制、信息清晰

适合：

- OA
- 审批
- 权限管理
- 报表系统

#### 12.4.2 `modern-saas`

定位：

- 面向外部交付的现代管理台风格

适合：

- SaaS 后台
- 对外控制台
- 快速交付项目

#### 12.4.3 `data-console`

定位：

- 数据密集型后台风格

适合：

- 运营台
- 风控台
- 数据管理台

#### 12.4.4 `macos-glass`

定位：

- 品牌感和展示感优先的玻璃态风格

适合：

- 演示环境
- 对外展示型系统

#### 12.4.5 `high-clarity`

定位：

- 高可读性 / 高可访问性优先风格

适合：

- 政企系统
- 培训成本敏感场景
- 对比度要求高的系统

### 12.5 风格推荐规则

简单模式中，风格跟随技术方案一起推荐：

- `enterprise-vue2` 默认推荐 `enterprise-default`
- 企业场景且明显数据密集时，可推荐 `data-console`
- `public-primevue` 默认推荐 `modern-saas`
- 外部数据台场景，可推荐 `data-console`
- 强调品牌展示感时，可推荐 `macos-glass`
- 强调高可读性时，可推荐 `high-clarity`

默认规则下，简单模式不推荐 `degraded` 风格。

---

## 13. Provider 风格支持矩阵真值

### 13.1 真值来源

Provider 是否支持某个风格、支持等级是多少、降级原因是什么，唯一真值来源是：

`provider_manifest.style_support_matrix`

### 13.2 当前阶段建议支持矩阵

#### `enterprise-vue2`

- `enterprise-default -> full`
- `data-console -> full`
- `high-clarity -> full`
- `modern-saas -> partial`
- `macos-glass -> degraded`

#### `public-primevue`

- `enterprise-default -> full`
- `modern-saas -> full`
- `data-console -> full`
- `macos-glass -> full`
- `high-clarity -> full`

---

## 14. 风格生成产物

P2 第一阶段风格落地的最小生成产物固定为：

- `effective_style_pack_id`
- `resolved_style_tokens`
- `provider_theme_adapter_config`
- `style_fidelity_status`
- `style_degradation_reason_codes`

不允许出现“有的项目只落 style id、有的项目只落 CSS vars、没有降级原因记录”的不一致行为。

---

## 15. 成功标准

P2 第一阶段达到以下标准视为方案落地成功：

1. 技术方案确认阶段可输出一份结构化 `solution_snapshot`。
2. 简单模式能给出单套主推荐，并展示推荐依据与可用性前提。
3. 高级模式能通过结构化向导完成方案确认。
4. `enterprise-vue2` 可用性判定和显式跨栈 fallback 流程可运行。
5. `provider_manifest` 成为 Provider 真值来源。
6. `style_pack_manifest` 与 `provider_manifest.style_support_matrix` 形成稳定边界。
7. 内置 5 套风格可被推荐、选择、审计。
8. 生成链路能产出最小风格生成产物。

---

## 16. 后续实现拆分建议

后续 implementation plan 应至少拆成以下工作流：

1. Manifest 模型与 schema
2. 技术方案确认推荐规则
3. 技术方案确认向导 UI
4. 可用性检查与 preflight
5. Provider 风格支持矩阵
6. `solution_snapshot` 持久化与审计
7. 风格生成产物与 Provider Theme Adapter 落地

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
