# 功能规格：Frontend Mainline Host Remediation And Workspace Integration Closure Baseline

**功能编号**：`144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 待评审；implementation 未开始
**输入**：[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../097-frontend-mainline-posture-delivery-registry-baseline/spec.md`](../097-frontend-mainline-posture-delivery-registry-baseline/spec.md)、[`../098-frontend-mainline-posture-detector-baseline/spec.md`](../098-frontend-mainline-posture-detector-baseline/spec.md)、[`../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`](../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md`](../123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md)、[`../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md`](../124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md)、[`../../src/ai_sdlc/core/host_runtime_manager.py`](../../src/ai_sdlc/core/host_runtime_manager.py)、[`../../src/ai_sdlc/core/managed_delivery_apply.py`](../../src/ai_sdlc/core/managed_delivery_apply.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/models/host_runtime_plan.py`](../../src/ai_sdlc/models/host_runtime_plan.py)、[`../../src/ai_sdlc/models/frontend_managed_delivery.py`](../../src/ai_sdlc/models/frontend_managed_delivery.py)、[`../../src/ai_sdlc/models/frontend_solution_confirmation.py`](../../src/ai_sdlc/models/frontend_solution_confirmation.py)、[`../../program-manifest.yaml`](../../program-manifest.yaml)

> 口径：`144` 是 `frontend-mainline-delivery` 在 `143` 之后的下一条 closure carrier。它只补三条还没真正接通的主线：`096.host_runtime_plan` 到可执行 `runtime_remediation` 的桥接、`099.delivery_bundle_entry` 到真实 provider/component package install 的桥接、以及 `097/098/100` 已冻结的 sidecar/root recommendation 到受控 `workspace_integration` action 的桥接。这里的 provider/component package 仅指已经写入 `073.solution_snapshot + install_strategy + 099.delivery_bundle_entry` 真值的 public/private package 集合；`144` 不补 browser gate、多浏览器矩阵、任意 shell、隐式 old-frontend takeover，也不把 root-level mutate 扩张成无边界工程改写器。

## 问题定义

`143` 已把 browser gate 的真实 probe runtime 落地，但当前 `frontend-mainline-delivery` 仍然不能诚实宣称“从方案选择到工程落地已经闭环”。剩下的缺口集中在三个地方：

- `096.host_runtime_plan` 目前只有 read-only `remediation_fragment`；缺失 Node / package manager / Playwright browser 时，系统只能给 generic reason code，不能把它稳定投影到可执行 apply action 或明确的新手向阻断
- `124` 虽然已经真实执行 `dependency_install` 与 `artifact_generate`，但它仍依赖手写 apply request YAML；选了 `enterprise-vue2` 或 `public-primevue` 后，provider/component packages 还不能从 `073 + 099` 自动流入 canonical apply payload
- `100` 已冻结 `workspace_integration` 的 truth boundary，`097/098` 也已冻结 `sidecar_root_recommendation` 与 `separate_root_level_actions`，但 apply runtime 仍把 `workspace_integration` 视为 unsupported；root-level workspace / lockfile / CI / proxy / route integration 还停留在“文档有、执行没有”

这会直接制造你已经指出的两类问题：

- 用户选了企业组件包或已纳入 registry truth 的外部公共组件包后，框架并不能稳定接管“宿主前置 -> 包安装 -> 工程落盘”的后半程，导致“已实现”的说法不可信
- 老版本升级或 brownfield 接入时，用户会被卡在半自动状态：框架知道哪里缺，但不能把缺口转成单一 machine truth 和单一下一步动作

`144` 的目标就是把这条剩余主线补成真正的 delivery closure：

1. 方案与 registry truth 可以自动生成 canonical managed delivery request
2. selected provider 与其 registry-declared component/adapter packages 可以自动进入 bounded install
3. sidecar/root recommendation 可以进入受控、可拒绝、默认关闭的 root-level integration action
4. bootstrap/mainline prerequisites 缺失时，系统仍然 fail-closed，但输出的是可执行或可理解的 framework truth，而不是把用户扔回手工猜测

## 范围

- **覆盖**：
  - `096.host_runtime_plan.remediation_fragment` 到 `runtime_remediation` action payload 的桥接与 execute truth
  - `073.solution_snapshot + 099.delivery_bundle_entry + 100.action family binding` 到 canonical managed delivery request 的桥接
  - registry-declared install strategy 的 `package_manager + packages` 真值进入 `dependency_install` payload；同时纳入 bundle entry 的 `adapter_packages`
  - `managed_target_prepare` 的真实 materialization，确保 managed subtree 不再只是 nominal action
  - `workspace_integration` 的结构化 payload、独立 optional requiredness、bounded root target 校验与 execute truth
  - public/private package install 的 prerequisite gating：缺 registry token / private access prerequisite 时 fail-closed 为 beginner-friendly blocker
  - focused tests，覆盖 request materialization、runtime remediation gating、bundle-driven package install、workspace integration 默认关闭与显式执行
- **不覆盖**：
  - browser gate、多浏览器矩阵、visual regression、Playwright probe runtime
  - 任意 shell 命令、operator 手填的任意 npm URL / git repo / 任意私有源地址
  - 默认 takeover old frontend root；`supported_existing_candidate` 仍不得被自动接管
  - 无边界 root 写入、自由 patch engine、整仓库重构或跨 spec 任意写回
  - 新 provider、新 style pack、新 registry entry；`144` 只消费已经被 `073/099` 纳入真值的 package / bundle entries

## 已锁定决策

- `144` 继续服从 `073 -> 096 -> 097/098 -> 099 -> 100 -> 123/124` 的 truth order；不得自持第二份 provider/runtime/target 真值
- `external component package` 在 `144` 中特指已经写入 `solution_snapshot/install_strategy/delivery_bundle_entry` 真值的 public/private package 集合；不支持 operator 直接输入任意 package 坐标
- canonical managed delivery request 必须直接从现有 truth 派生，并物化到既有 canonical 路径 `.ai-sdlc/memory/frontend-managed-delivery/latest.yaml`；CLI 允许显式 request path 仅作调试/回放，不得再成为主线必需入口
- `.ai-sdlc/memory/frontend-managed-delivery/latest.yaml` 在 `144` 中保持 request schema 单一职责；apply result / ledger truth 必须以独立返回值或独立 artifact 表达，不得把 request 文件覆盖成结果文件
- `runtime_remediation` 只允许修改 framework-managed runtime root（默认 `.ai-sdlc/runtime`）或其显式派生的受控缓存目录；不得静默污染 system Python、system Node、global package manager 或用户未确认的浏览器目录
- `runtime_remediation` 的默认执行器在 v1 只支持 framework-managed runtime root；不复用独立 offline profile launcher，也不向 system/global runtime 升级
- `dependency_install` 的 canonical payload 必须来自 install strategy `package_manager + packages`，并追加当前 bundle entry 的 `adapter_packages`；若 adapter packages 为空，必须显式保持空列表，不得猜测补齐
- `managed_target_prepare` 必须成为真实 action：至少要创建 managed target root 与 apply/runtime 所需的最小骨架，而不是 ledger 中的 no-op 成功
- `workspace_integration` 只能来自 `sidecar_root_recommendation.separate_root_level_actions` 与显式选择；它必须是独立 optional action，默认关闭，且 root-level target 集必须白名单化
- `workspace_integration` 的 v1 `mutation_kind` 冻结为 `write_new` 与 `overwrite_existing`；不支持 append/merge，避免把 root-level integration 扩成自由 patch engine
- root-level integration 在 v1 中只允许受控 target class：
  - `workspace`
  - `lockfile`
  - `ci`
  - `proxy`
  - `route`
  超出这五类的 integration payload 必须 fail-closed
- 当 host bootstrap prerequisites 未满足时，系统不得假装可以继续执行 install；必须阻断并给出 plain-language 的 reentry condition
- `enterprise-vue2` 的 private registry prerequisites 若未满足，系统必须在 request/preflight 阶段就给出阻断，而不是等 `pnpm/npm` 真执行后再报错

## 用户故事与验收

### US-144-1 — 选择 provider 后，框架要能自动生成可执行交付请求

作为 **operator**，我希望在 solution/provider 已确认后，系统能自动生成 canonical managed delivery request，把 host remediation、包安装、生成产物和可选 root integration 一次性收敛成可审计 truth，而不是要求我自己拼 YAML。

**优先级说明**：P0；没有这一层，`124` 的真实执行器仍然只能靠手工喂数据，不能证明主线闭环。

**独立测试**：用 `enterprise-vue2` 与 `public-primevue` 的 public/private registry-declared package 集合构造 request，验证 `runtime_remediation / managed_target_prepare / dependency_install / artifact_generate / workspace_integration` 的 requiredness、payload 和 `will_not_touch` 一致。

**验收场景**：

1. **Given** 当前 solution snapshot 生效 provider=`public-primevue`、style=`modern-saas`，**When** 系统生成 canonical managed delivery request，**Then** `dependency_install` payload 必须直接包含 `public-primevue-default` 的 package manager 与 packages
2. **Given** 当前 solution snapshot 生效 provider=`enterprise-vue2` 且 access mode=`private`，**When** 系统生成 canonical managed delivery request，**Then** `dependency_install` payload 必须包含 enterprise registry-declared package set 与 prerequisite blockers
3. **Given** posture 只允许 sidecar、root integration 默认关闭，**When** 系统生成 request，**Then** `workspace_integration` 必须作为独立 optional action 出现，而不是默认必做

### US-144-2 — Host prerequisites 缺失时，框架要给出单一 truth，而不是把人扔回手工排障

作为 **小白用户**，我希望缺 Node / package manager / private registry prerequisites 时，框架能在 apply 之前就告诉我缺什么、为什么缺、下一步是什么，而不是让我在安装失败后自己猜。

**优先级说明**：P0；这是“历史升级后不会把用户卡死”的核心闭环。

**独立测试**：mock `HostRuntimePlan` 与 private registry prerequisite 缺失，验证 request/preflight 会 fail-closed，且 blocker/reentry condition 是 plain-language、单一下一步。

**验收场景**：

1. **Given** `host_runtime_plan.status=remediation_required` 且缺 `node_runtime`，**When** 系统生成 apply request/preflight，**Then** 必须输出结构化 `runtime_remediation` 或明确 blocker，而不是允许 dependency install 继续盲跑
2. **Given** `enterprise-vue2` 选中但缺 `company-registry-token`，**When** 系统生成 request/preflight，**Then** 必须在执行前阻断，并明确提示需要补齐 registry token

### US-144-3 — Brownfield root integration 必须受控、可拒绝、默认关闭

作为 **brownfield maintainer**，我希望 workspace / lockfile / CI / proxy / route integration 继续是独立 optional action，只有在明确选择后才会执行，而且只能写入预先声明的 root target。

**优先级说明**：P0；这是 root takeover 不越界的最后一道约束。

**独立测试**：验证未选择 `workspace_integration` 时 old root 不变；选择后只能写 approved target；越界 path 或不支持的 target class 会在 preflight 阻断。

**验收场景**：

1. **Given** root-level integration action 未被选择，**When** apply execute 完成，**Then** root manifest / lockfile / CI / proxy / route 文件不得被改动
2. **Given** 选择了 `workspace_integration` 且 payload 只声明 `workspace` 与 `route` target，**When** apply execute 完成，**Then** 系统只能改动这两个已声明 target，其他 root targets 保持 no-touch

### US-144-4 — 执行结果必须诚实进入 ledger，而不是把 no-op 当成功

作为 **reviewer**，我希望 `runtime_remediation`、`managed_target_prepare` 和 `workspace_integration` 都有真实 before/after state 与 blocker 口径，这样 close 证据不会再靠“action type 已出现”冒充“action 已执行”。

**优先级说明**：P1；这是 close 可信收尾和后续 audit 的基础。

**独立测试**：验证三类 action 的 ledger entry 不再是 generic after-state；失败时能区分 preflight block、execute failed 与 explicit skip。

**验收场景**：

1. **Given** `managed_target_prepare` 真实创建 managed subtree，**When** ledger 写回，**Then** `after_state` 必须包含真实 target path / generated artifacts
2. **Given** `workspace_integration` payload 越界，**When** preflight 执行，**Then** ledger 必须记录 `blocked` 而不是 no-op success

### 边界情况

- builtin bundle entry 的 `adapter_packages=[]`；系统必须保持空列表，不得为“看起来完整”而追加猜测包
- root integration payload 包含不支持的 `target_class`；系统必须 `blocked_before_start`
- root integration payload 在路径规范化后逃逸 repo、借 symlink 穿透 repo 边界、或混入未批准 `target_class`；系统必须在任何写入前 `blocked_before_start`
- managed target root 已存在且含旧生成物；系统必须在 `managed_target_prepare` 中诚实表达 reconcile/overwrite truth，不能静默覆盖
- source/runtime surface 未达到 mutate threshold；系统不得生成可执行 apply request
- private/public provider 在 access mode、registry requirement、credential requirement 上出现 drift；系统必须 fail-closed

## 功能需求

| ID | 需求 |
|----|------|
| FR-144-001 | 系统必须提供 canonical managed delivery request materializer，直接消费 `073 + 096 + 097/098 + 099 + 100` 已冻结 truth，生成可执行 `execution_view` 与确认面输入 |
| FR-144-002 | `runtime_remediation` 必须从 `HostRuntimePlan.remediation_fragment` 派生，而不是执行期临时猜测 |
| FR-144-003 | `runtime_remediation` execute path 只能改动 framework-managed runtime root 与其受控缓存；不得静默污染 system-level runtime |
| FR-144-004 | `dependency_install` payload 必须从 registry-declared install strategy `package_manager + packages` 和 bundle entry `adapter_packages` 自动派生 |
| FR-144-005 | `managed_target_prepare` 必须成为真实 materialization action，而不是 generic no-op success |
| FR-144-006 | `workspace_integration` 必须拥有结构化 payload，并且只允许 `workspace / lockfile / ci / proxy / route` 五类 root target |
| FR-144-007 | `workspace_integration` 必须保持独立 optional action、默认关闭；未显式选择时 root-level targets 必须保持 no-touch |
| FR-144-008 | 对缺 host prerequisites、缺 private registry credential、缺可写 target、path 越界或 unsupported root target，系统必须在 preflight 阶段 `blocked_before_start` |
| FR-144-009 | CLI / ProgramService 必须输出 plain-language blocker、reentry condition 与单一下一步动作，不得把新手卡在抽象 reason code 上 |
| FR-144-010 | registry-declared bundle entry 即使当前 `adapter_packages` 为空，也必须保留统一装配链路；未来非空时不得改协议 |
| FR-144-011 | `144` 不得实现 browser gate、多浏览器矩阵、任意 shell 执行、默认 old-root takeover 或无边界 root 写入 |

## 关键实体

### 1. ManagedDeliveryMaterializationRequest

`ManagedDeliveryMaterializationRequest` 是 `144` 新增的 canonical binding artifact，用来把 `host_runtime_plan`、`delivery_bundle_entry`、`sidecar_root_recommendation` 与 local evidence 收敛成 apply runtime 可直接消费的 request truth。

其最小字段至少包括：

- `request_id`
- `solution_snapshot_ref`
- `host_runtime_plan_ref`
- `delivery_bundle_entry_ref`
- `posture_assessment_ref`
- `execution_view`
- `decision_surface_seed`
- `plain_language_blockers`
- `reentry_condition`

规则：

- 任何上游 ref 缺失或冲突时，request 必须 fail-closed
- request 是 canonical machine truth，不是临时导出的 user-authored YAML

### 2. RuntimeRemediationExecutionPayload

`RuntimeRemediationExecutionPayload` 是 `runtime_remediation` action 的唯一结构化 execute 面。

其最小字段至少包括：

- `managed_runtime_root`
- `required_runtime_entries`
- `install_profile_id`
- `acquisition_mode`
- `will_download`
- `will_install`
- `will_modify`
- `manual_prerequisites`
- `reentry_condition`

规则：

- 只能承接 `node_runtime / package_manager / playwright_browsers`
- 若当前仍处于 bootstrap-only 缺口，payload 不得伪装成可直接执行

### 3. WorkspaceIntegrationExecutionPayload

`WorkspaceIntegrationExecutionPayload` 是 `workspace_integration` action 的唯一结构化 root-level mutate 面。

其最小字段至少包括：

- `integration_id`
- `target_class`
  - `workspace`
  - `lockfile`
  - `ci`
  - `proxy`
  - `route`
- `target_path`
- `mutation_kind`
- `content`
- `requires_explicit_confirmation`
- `will_not_touch_refs`

规则：

- `target_path` 必须是 repo 内 path，且必须落入 action plan 声明的 approved root targets
- `mutation_kind` 必须是受控枚举；不得携带自由 shell 或任意 patch script

### 4. ResolvedBundleInstallSelection

`ResolvedBundleInstallSelection` 是 `144` 用来把 bundle entry + install strategy 变成真实 install payload 的中间 truth。

其最小字段至少包括：

- `provider_id`
- `install_strategy_id`
- `package_manager`
- `component_library_packages`
- `adapter_packages`
- `registry_requirements`
- `credential_requirements`
- `access_mode`

规则：

- `package_manager` 必须直接继承 install strategy truth
- `component_library_packages` 与 `adapter_packages` 必须分开保留，不能合并后丢失语义

## 成功标准

### 可度量结果

- **SC-144-001**：系统能从当前 solution/bundle/host truth 自动生成 canonical managed delivery request，不再依赖手写 apply request YAML
- **SC-144-002**：`public-primevue` 与 `enterprise-vue2` 的 registry-declared install strategy 都能自动进入 `dependency_install` payload，并在 host-ready 场景下进入真实 apply 执行
- **SC-144-003**：host prerequisites 或 private registry prerequisites 缺失时，request/preflight 会 fail-closed，并给出 plain-language blocker 与 reentry condition
- **SC-144-004**：`workspace_integration` 作为默认关闭的 optional action 落地，未选择时 root no-touch、选择后只改 approved root targets
- **SC-144-005**：focused tests、`uv run ai-sdlc program validate`、`uv run ai-sdlc verify constraints` 与本 work item `truth-check` 通过

---
related_doc:
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline/spec.md"
  - "specs/124-frontend-mainline-delivery-materialization-runtime-baseline/spec.md"
  - "src/ai_sdlc/core/host_runtime_manager.py"
  - "src/ai_sdlc/core/managed_delivery_apply.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/models/host_runtime_plan.py"
  - "src/ai_sdlc/models/frontend_managed_delivery.py"
frontend_evidence_class: "framework_capability"
---
