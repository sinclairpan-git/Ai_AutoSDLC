# 功能规格：Frontend Mainline Delivery Registry Resolver Baseline

**功能编号**：`099-frontend-mainline-delivery-registry-resolver-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；作为 `097/098` 下游 resolver-only implementable slice  
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../097-frontend-mainline-posture-delivery-registry-baseline/spec.md`](../097-frontend-mainline-posture-delivery-registry-baseline/spec.md)、[`../098-frontend-mainline-posture-detector-baseline/spec.md`](../098-frontend-mainline-posture-detector-baseline/spec.md)、[`../../src/ai_sdlc/models/frontend_provider_profile.py`](../../src/ai_sdlc/models/frontend_provider_profile.py)、[`../../src/ai_sdlc/generators/frontend_provider_profile_artifacts.py`](../../src/ai_sdlc/generators/frontend_provider_profile_artifacts.py)、[`../../src/ai_sdlc/models/frontend_solution_confirmation.py`](../../src/ai_sdlc/models/frontend_solution_confirmation.py)、[`../../src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py`](../../src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)

> 口径：`099` 冻结的不是 detector、installer、action planner 或 sidecar writer，而是 `097` 拆分建议里的第二块正式切片。它只回答四个问题：哪些 built-in provider artifacts 与 solution catalog artifacts 能组成 framework-controlled `frontend_delivery_registry`；如何把 `effective_frontend_stack / effective_provider_id / effective_style_pack_id` 解析成单一 `delivery_bundle_entry`；`provider_manifest_ref` / `resolved_style_support_ref` 如何继续保持单向引用；以及当 artifacts 漂移、缺失或不匹配时 resolver 必须怎样 fail-closed。

## 问题定义

`097` 已把 `frontend_delivery_registry` 与 `delivery_bundle_entry` 的字段面冻结出来，`098` 又把 posture detector 从里面拆成了独立正式切片。但当前仓库仍缺最后一层关键合同：**registry resolver 自身到底如何从现有 artifact reality 里收敛出官方 delivery truth**。

目前仓库已经存在几块明确 reality：

- `src/ai_sdlc/generators/frontend_provider_profile_artifacts.py` 已能把 built-in provider profile materialize 到 `providers/frontend/<provider_id>/...`
- built-in provider 现实已固定为 `enterprise-vue2` 与 `public-primevue`
- `src/ai_sdlc/models/frontend_solution_confirmation.py` 已冻结五个 built-in style pack 与两个 built-in install strategy
- `src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py` 已把 style pack / install strategy artifact 根固定到 `governance/frontend/solution/...`
- `verify_constraints` 已把 `provider.manifest.yaml` 与 `style-support.yaml` 当作可验证 reality 使用

但仍缺一份 formal contract 来统一回答下面几个实现前必须锁死的问题：

1. registry v1 的官方 entry 到底如何从 provider manifest、style-support、install strategy 与 style pack manifest 归并出来。
2. `delivery_bundle_entry` 里的 `component_library_packages`、`adapter_packages`、`runtime_requirements`、`verification_probes` 分别来自哪里；哪些字段允许为空，哪些不允许临时猜测。
3. `073.solution_snapshot`、`098.frontend_posture_assessment` 与 built-in catalog 同时存在时，resolver 该先信谁、后信谁；遇到 mismatch 是降级、阻断还是偷偷 fallback。
4. 当 provider manifest 缺 install strategy、style-support 缺 style pack、provider/access_mode 不匹配时，resolver 应如何诚实 fail-closed，而不是再生成一份“看起来能用”的第二套 registry truth。

如果这层不先冻结，后续实现会继续在四种错误之间漂移：

- 把 `073` 的推荐/生效结果与 built-in artifact reality 分开维护，最后 provider/style truth 出现双写
- 把 `component_library_packages` 与 `adapter_packages` 写成临时推测字段，导致文档 truth 和实际 artifact truth 偏离
- 遇到 style-support 或 install strategy 漂移时静默 fallback，最后 downstream action planning 消费到伪造条目
- 把 `098` posture detector 的 verdict 重新解释成 registry 内容本身，导致 detector truth 与 resolver truth 互相污染

因此，`099` 的目标是冻结一条最小但严格的 Delivery Registry Resolver baseline：先把 built-in provider artifacts、solution catalog artifacts、selection context、fail-closed drift 语义和单向引用规则收敛成 machine truth，再把真正的 runtime materialization、action binding 与 mutating execution 继续留给后续切片。

## 范围

- **覆盖**：
  - `097.frontend_delivery_registry` 与 `delivery_bundle_entry` 的 resolver authority、truth order 与输入来源
  - built-in provider artifact reality、install strategy truth、style pack truth 的 join 规则
  - `effective_frontend_stack / effective_provider_id / effective_style_pack_id` 到单一 `delivery_bundle_entry` 的解析规则
  - `provider_manifest_ref` / `resolved_style_support_ref` 的单向引用格式与 fail-closed 语义
  - `component_library_packages`、`adapter_packages`、`runtime_requirements`、`verification_probes` 的字段来源与 v1 默认值
  - `098` posture verdict 到 resolver `supported_posture_modes` 的受控映射
  - resolver 与 `073 / 096 / 097 / 098` 的 downstream handoff 边界
- **不覆盖**：
  - 在本 work item 中直接实现 registry materializer、bundle writer、installer、planner 或 rollback runtime
  - 重写 `073` 已冻结的 `solution_snapshot`、fallback chain 或 install strategy truth
  - 重写 `098` 的 detector evidence source、五类 `support_status` 或 sidecar recommendation 边界
  - 允许 arbitrary npm URL、arbitrary git repo、arbitrary private registry 地址进入 mainline delivery registry
  - 在 resolver 阶段重新评估 host readiness、执行包安装、创建目录或改写旧工程
  - 把 `managed_frontend_already_attached` 或 `ambiguous_existing_frontend` 直接伪装成可自动解析的 delivery posture mode

## 已锁定决策

- `099` 是 `097` 下游的 resolver-only implementable slice；它只负责 formalize `frontend_delivery_registry` 的 join 规则与 `delivery_bundle_entry` 的解析规则。
- registry v1 必须完全由 framework-controlled built-in artifacts 构成：provider profile artifacts、install strategies、style pack manifests；不接受用户输入的新来源地址来补 registry。
- `073.solution_snapshot` 继续独占 `effective_frontend_stack / effective_provider_id / effective_style_pack_id` 的选择 truth；resolver 只能消费，不得重写或 fallback 到另一组 provider/style。
- `098.frontend_posture_assessment` 继续独占 posture truth；resolver 只能消费其归一化后的 posture mode，不得反向改写 detector verdict。
- `096.host_runtime_plan` 继续独占 readiness truth；resolver 只声明 `runtime_requirements` 需要哪些宿主依赖类别，不负责判断当前机器是否已经满足。
- `provider_manifest_ref` 与 `resolved_style_support_ref` 必须继续指向现有 artifact reality；resolver 不得自持第二份 provider/style compatibility 表。
- `component_library_packages` 只来自 install strategy 的 `packages`；v1 在未声明独立 adapter package 时，`adapter_packages` 必须显式为空列表，而不是猜测补齐。
- resolver 遇到缺 manifest、缺 style-support、缺 install strategy、缺 style pack、provider 不匹配、access mode 不匹配、style 被标记 `unsupported` 等 drift 时，必须 fail-closed。
- registry v1 只正式承认两条 entry：`vue2 + enterprise-vue2`、`vue3 + public-primevue`。
- `preferred_managed_target_kind` 在 v1 默认固定为 `new_controlled_subtree`，以保持 no-touch posture；resolver 不得因为条目可解析就暗示默认 takeover old frontend。

## Resolver Input Model

### 1. ProviderArtifactRefSet

`ProviderArtifactRefSet` 是 resolver 允许消费的 provider-side canonical artifact 集，来源继续以 `frontend_provider_profile_root(root, provider_id)` 为 canonical root。

其最小字段至少包括：

- `provider_id`
- `provider_root`
- `provider_manifest_ref`
- `style_support_ref`
- `access_mode`
- `default_style_pack_id`
- `install_strategy_ids`
- `availability_prerequisites`
- `cross_stack_fallback_targets`

规则：

- `provider_manifest_ref` 必须指向 `providers/frontend/<provider_id>/provider.manifest.yaml`
- `style_support_ref` 必须指向 `providers/frontend/<provider_id>/style-support.yaml`
- `mappings.yaml`、`whitelist.yaml`、`risk-isolation.yaml`、`legacy-adapter.yaml` 属于 provider profile reality，但不直接进入 `delivery_bundle_entry`

### 2. SolutionCatalogArtifactRefSet

`SolutionCatalogArtifactRefSet` 是 resolver 允许消费的 solution-side catalog truth，来源继续以 `frontend_solution_confirmation_root(root)` 与 `frontend_solution_confirmation_memory_root(root)` 为 canonical roots。

其最小字段至少包括：

- `style_pack_manifest_refs`
- `install_strategy_refs`
- `solution_snapshot_ref`
- `effective_frontend_stack`
- `effective_provider_id`
- `effective_style_pack_id`

规则：

- `style_pack_manifest_refs` 必须来自 `governance/frontend/solution/style-packs/*.yaml`
- `install_strategy_refs` 必须来自 `governance/frontend/solution/install-strategies/*.yaml`
- `solution_snapshot_ref` 只提供选择上下文；它不是 provider/style artifact truth 的替代品

### 3. ResolverSelectionContext

`ResolverSelectionContext` 是 resolver 真正的 project-scoped 输入面，用于把 `073` 的 solution truth 与 `098` 的 posture truth 对齐。

其最小字段至少包括：

- `resolution_id`
- `solution_snapshot_ref`
- `posture_assessment_ref`
- `effective_frontend_stack`
- `effective_provider_id`
- `effective_style_pack_id`
- `posture_mode`
- `reason_codes`

其中 `posture_mode` v1 只允许三类：

- `greenfield_new_managed_frontend`
- `supported_existing_candidate`
- `unsupported_existing_frontend_sidecar_only`

规则：

- `ambiguous_existing_frontend` 不得直接被 resolver 当作可解析 posture mode；必须先由 downstream 获得额外确认或新 target mode
- `managed_frontend_already_attached` 不进入 v1 resolver 默认路径；attached root 继续由 `014` attachment truth 与后续 action planner 直接处理

### 4. DeliveryBundleEntry

`delivery_bundle_entry` 是 resolver 对外暴露的唯一 project-scoped delivery truth。它必须继续满足 `097` 的字段面，最小字段至少包括：

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

- `component_library_packages` 只来自 install strategy `packages`
- `adapter_packages` 在 v1 两个 built-in entry 中都固定为空列表
- `runtime_requirements` 只声明宿主依赖类别，不重复 `096.host_runtime_plan` 的 readiness 结果

## Resolver Truth Order

resolver 的 join 与解析顺序固定如下：

1. **Selection context first**
   - 先读取 `073` 的 `effective_frontend_stack / effective_provider_id / effective_style_pack_id`
   - 再读取 `098` 归一化后的 `posture_mode`
2. **Provider artifact truth second**
   - 读取 `provider.manifest.yaml` 与 `style-support.yaml`
   - provider manifest 缺失时直接 fail-closed
3. **Install strategy truth third**
   - 仅解析 provider manifest 中声明的 `install_strategy_ids`
   - 任一 strategy 缺失、provider_id 不匹配或 access_mode 不匹配时直接 fail-closed
4. **Style support truth fourth**
   - 只允许从该 provider 的 `style-support.yaml` 解析 `resolved_style_support_ref`
   - style pack manifest 缺失或 style fidelity 为 `unsupported` 时直接 fail-closed
5. **Posture gating fifth**
   - 仅当 `posture_mode` 落在 entry `supported_posture_modes` 之内时，才允许输出 `delivery_bundle_entry`
6. **Host readiness and planning last**
   - `096.host_runtime_plan` 与后续 action planner 只能消费 resolver 输出；不得反向改写 entry truth

优先级护栏：

- resolver 不得因为某个 provider artifact 可用，就越权覆盖 `073` 已冻结的 effective provider/style
- resolver 不得因为 `098` 给出了保守 sidecar recommendation，就自行切换 provider、style 或 frontend stack
- 当 provider/style/install strategy 三者之间出现任何结构性漂移时，resolver 必须阻断，而不是偷偷生成“次优 entry”

## Registry Materialization Rules

### 1. Built-in Entry Enumeration

registry v1 只允许 materialize 两条 framework-controlled entries：

- `vue2-enterprise-vue2`
- `vue3-public-primevue`

它们分别承接：

- `enterprise-vue2` provider artifact reality
- `public-primevue` provider artifact reality

### 2. Install Strategy Binding

resolver 必须用 provider manifest 中的 `install_strategy_ids` 去匹配 solution catalog 里的 install strategy artifact。

绑定规则：

- `enterprise-vue2` -> `enterprise-vue2-private-registry`
- `public-primevue` -> `public-primevue-default`

并且：

- `component_library_packages = install_strategy.packages`
- `availability_prerequisites = provider.manifest.availability_prerequisites`
- `access_mode` 必须同时满足 provider manifest 与 install strategy 的声明

### 3. Style Support Binding

resolver 必须把 provider `style-support.yaml` 与 style pack manifests 做单向 join。

绑定规则：

- 只有 style pack manifest 与 provider style-support 同时存在，`resolved_style_support_ref` 才能成立
- `resolved_style_support_ref` 必须形如 `providers/frontend/<provider_id>/style-support.yaml#style_pack_id=<style_pack_id>`
- `enterprise-vue2` v1 支持矩阵固定为：
  - `enterprise-default` -> `full`
  - `data-console` -> `full`
  - `high-clarity` -> `full`
  - `modern-saas` -> `partial`
  - `macos-glass` -> `degraded`
- `public-primevue` v1 对全部 built-in style pack 固定为 `full`

### 4. Runtime Requirement Binding

`runtime_requirements` 在 resolver v1 中固定只声明：

- `node_runtime`
- `package_manager`
- `playwright_browsers`

规则：

- `python_runtime` 与 `installed_cli_runtime` 继续属于 `096.bootstrap_acquisition` truth，不得在 bundle entry 中重复声明成 provider-specific requirement
- private/public provider 的差异继续通过 `availability_prerequisites` 表达，而不是通过篡改 runtime requirement taxonomy

## V1 Registry Matrix

| Entry ID | frontend_stack | provider_id | access_mode | install_strategy_ids | availability_prerequisites | default_style_pack_id |
|----|----|----|----|----|----|----|
| `vue2-enterprise-vue2` | `vue2` | `enterprise-vue2` | `private` | `enterprise-vue2-private-registry` | `company-registry-network`, `company-registry-token` | `enterprise-default` |
| `vue3-public-primevue` | `vue3` | `public-primevue` | `public` | `public-primevue-default` | none | `modern-saas` |

v1 两个 entry 的共同规则：

- `adapter_packages = []`
- `preferred_managed_target_kind = new_controlled_subtree`
- `supported_posture_modes` 至少覆盖 `greenfield_new_managed_frontend` 与 `supported_existing_candidate`
- 当 operator 显式选择 sidecar managed frontend 时，两条 entry 都可额外支持 `unsupported_existing_frontend_sidecar_only`

## Drift And Fail-Closed Rules

resolver 至少必须对以下 drift 保持 fail-closed：

- `provider_manifest_ref` 不存在
- `style_support_ref` 不存在
- provider manifest 引用的 install strategy artifact 不存在
- install strategy 的 `provider_id` 与 provider manifest 不一致
- install strategy 的 `access_mode` 与 provider manifest 不一致
- `effective_style_pack_id` 不存在对应 style pack manifest
- `effective_style_pack_id` 不存在对应 provider style-support item
- provider style-support 将该 style 标记为 `unsupported`
- `effective_frontend_stack / effective_provider_id` 组合不在 v1 registry matrix 内
- `posture_mode` 不在 entry `supported_posture_modes` 内

fail-closed 结果必须满足：

- 不输出伪造的 `delivery_bundle_entry`
- 不静默改写 provider/style/access mode
- 必须保留 machine-readable `reason_codes`
- 必须把问题定位到 artifact drift，而不是误归因给用户意图

## 用户故事与验收

### US-099-1

作为 **novice operator**，我希望 framework 官方支持的 delivery entry 是固定且可解释的，而不是文档说一套、artifact reality 又是另一套。

**验收**：

1. Given 当前 built-in provider reality，When reviewer 查看 `099`，Then 必须明确看到 `vue2-enterprise-vue2` 与 `vue3-public-primevue` 两条正式 registry entry  
2. Given `enterprise-vue2` entry 被解析，When 查看其 delivery truth，Then 必须看到 private access、企业 registry 前提、install strategy 与 style-support 来源  
3. Given `public-primevue` entry 被解析，When 查看其 style truth，Then 必须看到全部 built-in style pack 都通过 provider `style-support.yaml` 单向引用

### US-099-2

作为 **reviewer / maintainer**，我希望 resolver 继续使用单向引用，而不是复制 provider/style truth，这样后续 drift 能被诚实暴露。

**验收**：

1. Given resolver 输出 `delivery_bundle_entry`，When 审查 `provider_manifest_ref`，Then 它必须直接指向 provider artifact reality  
2. Given resolver 输出某个 style entry，When 审查 `resolved_style_support_ref`，Then 它必须直接指向 provider `style-support.yaml` 中对应 `style_pack_id` 的 truth  
3. Given v1 没有独立 adapter package 声明，When 审查 `adapter_packages`，Then 必须显式为空列表，而不是临时推测包名

### US-099-3

作为 **downstream planner**，我希望 resolver 只在 posture mode 与 solution selection 都明确时输出 bundle entry，这样 action planning 不会踩进 ambiguous 或 attached truth。

**验收**：

1. Given `posture_mode=greenfield_new_managed_frontend`，When solution 选中某个 built-in provider/style，Then resolver 可以输出对应 `delivery_bundle_entry`  
2. Given `posture_mode=unsupported_existing_frontend_sidecar_only`，When operator 已显式选择 sidecar managed frontend，Then resolver 仍可输出条目，但 `preferred_managed_target_kind` 继续保持 `new_controlled_subtree`  
3. Given 原始 posture 仍是 `ambiguous_existing_frontend` 或 `managed_frontend_already_attached`，When 没有额外归一化 mode，Then resolver 不得直接产出 bundle entry

### US-099-4

作为 **maintainer**，我希望 artifact drift 不再被静默吞掉；一旦 provider/style/install strategy 有结构性错位，resolver 应该直接阻断。

**验收**：

1. Given provider manifest 引用了缺失的 install strategy，When resolver 尝试归并 registry，Then 必须 fail-closed  
2. Given effective style pack 在 provider style-support 中缺失，When resolver 尝试输出 style entry，Then 必须 fail-closed，而不是偷偷选默认 style  
3. Given provider/access mode 与 install strategy 不一致，When resolver 尝试输出 entry，Then 必须把 mismatch 作为 artifact drift 暴露出来

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-099-001 | `099` 必须作为 `097/098` 下游的 resolver-only implementable slice 被正式定义 |
| FR-099-002 | `099` 只能消费 `016 / 073 / 094 / 095 / 096 / 097 / 098` 与 built-in artifact reality；不得回写这些 upstream truth |
| FR-099-003 | `099` 的 canonical machine 输出只允许覆盖 `frontend_delivery_registry` 与 project-scoped `delivery_bundle_entry`；不得偷渡 detector、installer 或 mutate protocol |
| FR-099-004 | `099` 不得把用户输入的新 registry source、任意 npm URL 或任意 git repo 当作 v1 resolver truth |

### Resolver Input Contract

| ID | 需求 |
|----|------|
| FR-099-005 | resolver 必须用 `providers/frontend/<provider_id>/provider.manifest.yaml` 与 `style-support.yaml` 作为 provider-side canonical artifact roots |
| FR-099-006 | resolver 必须用 `governance/frontend/solution/style-packs/*.yaml` 与 `install-strategies/*.yaml` 作为 solution catalog truth |
| FR-099-007 | `solution_snapshot_ref` 只提供 `effective_frontend_stack / effective_provider_id / effective_style_pack_id` 的选择上下文；不得替代 provider/style artifact truth |
| FR-099-008 | resolver v1 的 `posture_mode` 只允许 `greenfield_new_managed_frontend / supported_existing_candidate / unsupported_existing_frontend_sidecar_only` 三类 |
| FR-099-009 | `ambiguous_existing_frontend` 与 `managed_frontend_already_attached` 在未归一化前不得直接进入 v1 resolver 路径 |
| FR-099-010 | resolver 输出必须保留 machine-readable `reason_codes`，以便 downstream 能区分 drift、unsupported 与 posture gate mismatch |

### Registry Materialization

| ID | 需求 |
|----|------|
| FR-099-011 | registry v1 必须只 materialize `vue2-enterprise-vue2` 与 `vue3-public-primevue` 两条 built-in entry |
| FR-099-012 | `component_library_packages` 必须直接来自 install strategy `packages` 字段 |
| FR-099-013 | `adapter_packages` 在未声明独立 adapter package artifact 时必须显式为空列表 |
| FR-099-014 | `runtime_requirements` 在 resolver v1 中必须固定为 `node_runtime / package_manager / playwright_browsers`，不得复制 `096.bootstrap_acquisition` truth |
| FR-099-015 | `availability_prerequisites` 必须继续来自 provider manifest；不得借 runtime requirement 字段重写 private/public access 差异 |
| FR-099-016 | `provider_manifest_ref` 必须单向引用 provider manifest reality；resolver 不得复制 manifest 内容进第二份 compatibility truth |
| FR-099-017 | `resolved_style_support_ref` 必须单向引用 provider `style-support.yaml` 中对应 `style_pack_id` 的 reality |

### Entry Resolution Semantics

| ID | 需求 |
|----|------|
| FR-099-018 | resolver 必须先以 `073` 的 effective stack/provider/style 作为选择上下文，再进行 provider/style/install strategy join |
| FR-099-019 | resolver 不得因为某个 provider artifact 存在就覆盖 `073` 已冻结的 effective provider/style 选择 |
| FR-099-020 | 只有当 `posture_mode` 落在 entry `supported_posture_modes` 内时，resolver 才允许输出 `delivery_bundle_entry` |
| FR-099-021 | `preferred_managed_target_kind` 在 v1 必须默认固定为 `new_controlled_subtree`，不得暗示默认 takeover old frontend |

### Drift Handling And Downstream Handoff

| ID | 需求 |
|----|------|
| FR-099-022 | provider manifest 缺失、style-support 缺失、install strategy 缺失、style pack 缺失、provider/access mode mismatch 或 style 被标记 `unsupported` 时，resolver 必须 fail-closed |
| FR-099-023 | fail-closed 时不得输出伪造 entry、不得静默 fallback 到默认 provider/style，并必须保留 drift `reason_codes` |
| FR-099-024 | downstream `frontend_action_plan` 只能消费 resolver 输出的 `delivery_bundle_entry` 与 `096.host_runtime_plan`，不得再造第三份 registry truth |
| FR-099-025 | `099` 必须明确后续实现优先级应转向 resolver runtime materialization 与 action-plan binding，而不是回退去重写 detector 或 solution truth |

## 关键实体

- **ProviderArtifactRefSet**：承载 provider manifest 与 style-support 的 canonical resolver 输入
- **SolutionCatalogArtifactRefSet**：承载 style pack / install strategy catalog truth 与 solution selection context
- **ResolverSelectionContext**：承载 effective stack/provider/style 与 posture mode 的 project-scoped 选择上下文
- **Frontend Delivery Registry**：承载 v1 built-in entries 的 framework-controlled catalog
- **Delivery Bundle Entry**：承载单个条目的 install/runtime/style/access truth 与 downstream handoff 边界

## 成功标准

- **SC-099-001**：registry v1 的 entry 来源被收敛到 built-in artifacts，本轮不再出现文档 truth 与 artifact truth 双写  
- **SC-099-002**：`provider_manifest_ref` 与 `resolved_style_support_ref` 成为 resolver 唯一允许的 provider/style 单向引用来源  
- **SC-099-003**：artifact drift 会被 fail-closed 暴露，resolver 不再静默 fallback 到伪造条目  
- **SC-099-004**：`099` 与 `098/096/073` 的边界清晰，resolver 只做 join 与 selection，不重写 posture、host readiness 或 solution truth  

## 后续实现拆分建议

`099` 之后的下一正式切片应继续保持 `resolver / planner` 解耦：

1. **Delivery Registry Resolver Runtime**
   - 实现 built-in artifact enumeration、join、drift detection 与 project-scoped entry resolution
   - 输出 canonical `frontend_delivery_registry` 与 `delivery_bundle_entry`
2. **Frontend Action Plan Binding**
   - 吸收 `096.host_runtime_plan`、`098.posture truth` 与 `099.delivery_bundle_entry`
   - 生成可确认、可回滚、可重试的 `frontend_action_plan`

---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
frontend_mainline_scope: "delivery_registry_resolver"
frontend_mainline_status: "formal_baseline_frozen"
frontend_delivery_entries:
  - "vue2-enterprise-vue2"
  - "vue3-public-primevue"
frontend_evidence_class: "framework_capability"
---
