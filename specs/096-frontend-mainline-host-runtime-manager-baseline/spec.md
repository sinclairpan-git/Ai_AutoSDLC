# 功能规格：Frontend Mainline Host Runtime Manager Baseline

**功能编号**：`096-frontend-mainline-host-runtime-manager-baseline`  
**创建日期**：2026-04-12  
**状态**：已完成
**输入**：[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../packaging/offline/install_offline.sh`](../../packaging/offline/install_offline.sh)、[`../../packaging/offline/install_offline.ps1`](../../packaging/offline/install_offline.ps1)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)

> 口径：`096` 冻结的不是“框架帮用户装一切”的黑盒安装器，而是 `095` 七层主线中的第 1 层 `Host Readiness` 正式合同。它把最小可执行宿主、`bootstrap acquisition channel`、`in-mainline remediation`、隔离安装目标、平台 profile、以及确认页前置边界收紧成单一 truth；但它不重写 `093` 的 installed runtime truth，不重写 `094` 的 onboarding truth，也不提前吞并 `095` 里的 Managed Action Engine、Frontend Posture 或 Browser Quality Gate。

## 问题定义

`095` 已经把 frontend mainline 产品主线冻结成：

- `Host Readiness`
- `Stage 0 Onboarding`
- `Frontend Posture Assessment`
- `Solution Freeze`
- `Managed Delivery Planning`
- `Managed Delivery Apply`
- `Browser Quality Gate`

真正还没冻结的，不是“是否需要 host runtime 自愈”，而是**谁在什么时机、凭什么证据、可以对哪些宿主依赖给出什么级别的动作承诺**。当前现实里至少存在四个断层：

- `USER_GUIDE.zh-CN.md` 仍把 Python 3.11 安装、PATH 调整、venv 创建等步骤大量留给用户手工执行
- 仓库已有 `packaging/offline/install_offline.sh` / `install_offline.ps1`，但它们只表达离线 bundle 安装 reality，还不是 mainline 内部的正式 host runtime contract
- `src/ai_sdlc/cli/main.py` 当前没有一条冻结的 host runtime manager 入口边界来说明：什么时候只能诊断、什么时候允许规划、什么时候才允许进入 mutate 前确认
- `095` 虽然要求结构化 `host_runtime_plan`，但没有把“bootstrap 获取最小宿主”和“已有最小宿主后的主线补齐”拆成足够严格的子面

如果这层不先冻结，后续实现会继续在三种错误间漂移：

- 把 source/`uv run`/IDE surface 误当成可直接自愈的 installed runtime，结果越权下载、越权写入
- 把 Python、Node、包管理器、Playwright 浏览器全揉进一个“自动安装”动作，最后既不诚实，也无法回滚/重试
- 把现有 offline bundle reality、未来在线渠道、以及 mainline 内的 runtime remediation 混成一套状态机，导致确认页、动作 ledger、失败恢复全部失真

因此，`096` 的目标是冻结一条最小但严格的 Host Runtime Manager baseline：先把宿主依赖问题收敛成**可观察、可分类、可交接、可确认**的 machine truth，再把真正的 mutating execution 交给 `095` 下游的 Managed Action Engine。

## 范围

- **覆盖**：
  - `095.Host Readiness` 的正式定位、authority、输入输出与边界
  - `minimal_executable_host`、`bootstrap acquisition channel`、`in-mainline remediation` 的区分
  - Python、installed CLI runtime、Node、选定 package manager、Playwright browsers 的 readiness 分类
  - OS / arch 探测、installer profile 选择、offline bundle profile 对接
- `host_runtime_plan` 及其 `readiness / bootstrap_acquisition / remediation_fragment` 子面的 machine contract
  - 隔离安装目标、可回滚边界、不可严格回滚副作用分级
  - source / `uv run` / IDE 未绑定 surface 下的 fail-closed 行为
- **不覆盖**：
  - 在本 work item 中直接实现新的在线安装器、系统级 Python 安装器或跨平台包管理前端
  - 直接 formalize `frontend_action_plan` 全量 schema、`delivery_action_ledger`、rollback executor 或 browser gate executor
  - 重写 `093` 的 update advisor freshness / helper / notice contract
  - 重写 `094` 的 dual-path onboarding classifier，或把 `init` 升级成 host runtime manager 的替代入口
  - 直接 formalize provider/component library 依赖安装细节；这些属于 `095` 的 Managed Action Engine 与 Delivery Registry 下游

## 已锁定决策

- `096` 是 `095` 的实现切片，不是新的安装产品线；它只能冻结 `Host Readiness` 层自身的 truth。
- `minimal_executable_host` 与 `in-mainline remediation` 必须严格拆开：
  - `minimal_executable_host` 负责“框架至少能被正式调用”
  - `in-mainline remediation` 负责“在已具备正式调用能力后，把主线所需依赖补齐”
- v1 中，`python >= 3.11` 与 `installed ai-sdlc runtime` 属于 `bootstrap acquisition channel` 范围；Node、选定 package manager、Playwright browsers 属于 `in-mainline remediation` 范围。
- `bootstrap acquisition channel` 只允许绑定到现有正式渠道或其明确引用：
  - 离线 bundle 安装脚本
  - 已存在的人工安装指引
  - 已安装 runtime 所暴露的可信 helper / installer profile
  `096` 不发明一套新的“从任意 surface 自举整个框架”的黑盒流程。
- source runtime、editable runtime、`uv run ai-sdlc ...`、`python -m ai_sdlc ...`、以及未绑定 installed runtime 的 IDE/AI surface，在 **frontend mainline 的 host runtime mutate 路径** 上最多只能产出诊断与 acquisition handoff；不得直接执行 host runtime mutate 动作。该约束不否定当前 Stage 0 / `init` / `adapter` 等 source-runtime 入口 reality。
- 所有 host runtime 写入、下载、安装、升级动作默认只能落到 framework-managed isolated environment；不默认污染系统全局 Python、Node、npm、pnpm 或浏览器目录。
- `096` 只定义计划与边界，不授予静默执行权；任何 mutating action 仍必须进入 `095.delivery_execution_confirmation_surface`。
- `096` 的 canonical machine 输出必须继续服从 `095` 的单一 `host_runtime_plan` 口径；`readiness`、`bootstrap_acquisition`、`remediation_fragment` 都是同一 plan 内的嵌套子面，不得拆成相互竞争的顶层协议。
- 当前仓库中的 `main.py`、离线安装脚本和用户文档尚未提供上述结构化 producer / consumer；在实现落地前，它们仍然是 human-readable reality 与证据源，不能被误写成“已经输出 host_runtime_plan”。
- 对平台不匹配、profile 缺失、企业网络限制、bundle 缺失、权限不足等情况，系统必须诚实返回 `blocked` / `manual_acquisition_required` / `unsupported_platform`；不得猜测性回退到其他平台或其他安装方式。

## 运行时模型

### 1. MinimalExecutableHost

`minimal_executable_host` 是进入前端主线前唯一允许的宿主底座判定，v1 至少由以下条件共同构成：

- 当前 OS / arch 存在受支持 profile 或可被诚实 handoff 的 acquisition channel
- Python 运行时满足 `>= 3.11`
- 存在可验证的 AI-SDLC 正式调用目标
- 当前 surface 能把主线后续步骤绑定到该调用目标，而不是只拿到一个模糊版本字符串

其中：

- Python 缺失或版本不足，不属于 `in-mainline remediation`
- 只有 source/`uv run`/editable 调用，不构成 `installed runtime ready`

### 2. HostDependencyClass

Host Runtime Manager 必须把宿主依赖固定分为三类：

- `bootstrap_only`
  - `python_runtime`
  - `installed_cli_runtime`
- `mainline_remediable`
  - `node_runtime`
  - `package_manager`
  - `playwright_browsers`
- `informational_only`
  - 仅用于解释平台背景、已有渠道或 operator 选择
  - 不单独触发 mutate 动作

这三类不得混用。`bootstrap_only` 失败时，只允许进入 acquisition handoff；不得伪装成“已生成可直接执行的 remediation 计划”。

### 3. HostRuntimeReadinessState

每个依赖项必须稳定落在以下状态之一：

- `ready`
- `bootstrap_required`
- `remediation_required`
- `blocked`
- `unsupported`
- `unknown_evidence`

状态解释：

- `bootstrap_required` 只允许出现在 `bootstrap_only` 项上
- `remediation_required` 只允许出现在 `mainline_remediable` 项上
- `blocked` 表示理论上受支持，但当前缺 bundle、缺权限、缺凭证、缺磁盘空间、缺网络或其他前置条件
- `unsupported` 表示当前平台/架构/渠道无 formal support
- `unknown_evidence` 表示证据不足，系统必须继续诚实，而不是乐观视为 `ready`

### 4. InstallerProfileRef

`installer_profile_ref` 是 Host Runtime Manager 能引用的唯一平台安装 profile 句柄，至少必须包含：

- `profile_id`
- `target_os`
- `target_arch`
- `channel_kind`
- `supports_offline`
- `supports_interactive_confirmation`
- `writes_scope`
- `rollback_capability`

v1 现有 reality 至少要覆盖：

- `offline_bundle_posix_shell`
- `offline_bundle_windows_powershell`
- `offline_bundle_windows_bat_launcher`

其中 `offline_bundle_windows_bat_launcher` 代表 Windows `.bat` 启动入口；它可以作为 PowerShell 离线安装语义的 launcher alias，但仍必须被 formalize 成可引用的受控入口，不能在模型层缺席。它们共同对应现有离线安装脚本与 `bundle-manifest.json` 平台校验 reality。若未来新增在线 profile，也只能以新增 profile 的方式扩展，不得改写既有状态语义。

### 5. HostRuntimePlan

`host_runtime_plan` 是 Host Runtime Manager 的 canonical machine 输出，必须继续与 `095` 的单一 plan 口径对齐。其最小字段至少包括：

- `plan_id`
- `protocol_version`
- `platform_os`
- `platform_arch`
- `surface_kind`
- `surface_binding_state`
- `minimal_executable_host`
- `installed_runtime_ready`
- `required_runtime_entries`
- `missing_runtime_entries`
- `installer_profile_ids`
- `install_target_root`
- `requires_network`
- `requires_credentials`
- `status`
- `reason_codes`
- `evidence_refs`
- `readiness`
- `bootstrap_acquisition`
- `remediation_fragment`

其中：

- `status` 枚举至少包括：`ready`、`bootstrap_required`、`remediation_required`、`blocked`、`partial`
- `readiness` 是 plan 的 observe 子面，不是独立顶层协议
- `bootstrap_acquisition` 与 `remediation_fragment` 都是同一 plan 内的嵌套子面；可以分别为 `null / deferred / blocked / actionable`
- `evidence_refs` 只引用 machine-observable evidence，不引用愿望性默认值

### 6. Readiness And Bootstrap Acquisition Facet

`readiness` 必须至少包含：

- `python_runtime_status`
- `installed_cli_runtime_status`
- `node_runtime_status`
- `package_manager_status`
- `playwright_browsers_status`
- `candidate_installer_profiles`

当 `minimal_executable_host=false` 时，`bootstrap_acquisition` 子面必须被填充。其最小字段包括：

- `handoff_kind`
- `required_targets`
- `recommended_profile_ref`
- `manual_steps`
- `operator_decisions_needed`
- `blocking_reason_codes`
- `expected_reentry_condition`

其中：

- `handoff_kind` 至少区分：`offline_bundle_required`、`manual_python_install_required`、`installed_runtime_binding_required`
- `expected_reentry_condition` 必须描述“满足什么条件后，同一个 `host_runtime_plan` 才能转入可执行 remediation”

### 7. Remediation Fragment Facet

当 `minimal_executable_host=true` 且存在 `mainline_remediable` 缺口时，`remediation_fragment` 子面必须被填充，供 `095` 下游的 Managed Action Engine 并入总 `frontend_action_plan`。其最小字段包括：

- `readiness_subject_id`
- `managed_runtime_root`
- `required_actions`
- `optional_actions`
- `will_download`
- `will_install`
- `will_modify`
- `will_not_touch`
- `rollback_units`
- `cleanup_units`
- `non_rollbackable_effects`
- `manual_recovery_required`
- `reason_codes`

`096` 只定义同一 `host_runtime_plan` 中的 remediation 子面 truth，不定义整条 action ledger 的最终执行协议。

## 用户故事与验收

### US-096-1

作为 **第一次走前端主线的小白用户**，我希望系统能区分“现在还缺最小宿主”与“已经可以在主线内补依赖”，这样我不会在没有 Python / 正式 CLI runtime 时被误导成可以直接继续自动安装。

**验收**：

1. Given 当前机器没有 `python >= 3.11`，When Host Runtime Manager 评估 readiness，Then 必须输出结构化 `host_runtime_plan`，其中 `bootstrap_acquisition` 子面被填充，而不是只给 free-form 提示  
2. Given 当前是 `python -m ai_sdlc ...` 或 `uv run ai-sdlc ...`，When Host Runtime Manager 评估 **frontend mainline host runtime mutate 路径**，Then 它最多只能诊断 `installed_cli_runtime_status=bootstrap_required` 或等价阻断，不得直接执行 mutate 动作  
3. Given 当前平台无受支持 profile，When Host Runtime Manager 评估 readiness，Then 必须返回 `unsupported` 或 `blocked`，并说明原因

### US-096-2

作为 **已经具备正式 CLI runtime 的用户**，我希望缺失的 Node、包管理器、Playwright 浏览器能被系统规划成结构化 fragment，并在确认后执行到隔离环境，而不是要求我再自己查文档补齐。

**验收**：

1. Given 当前 installed CLI runtime 已可验证，When Node 或 package manager 缺失，Then Host Runtime Manager 必须输出结构化 `host_runtime_plan`，其中 `remediation_fragment` 子面被填充，而不是只报“自己安装后重试”  
2. Given Playwright 浏览器缺失，When 主线需要 browser gate，Then 该缺口必须被表达成结构化 remediation action，而不是隐藏在后续测试失败里  
3. Given host runtime 计划中存在 mutating action，When 进入执行阶段前，Then 这些 action 必须可被 `095.delivery_execution_confirmation_surface` 消费并展示

### US-096-3

作为 **reviewer / maintainer**，我希望所有宿主相关动作都能明确写入范围、回滚边界和不可逆副作用，这样后续执行引擎不会把 host runtime 变成不可审计黑盒。

**验收**：

1. Given 一个 host runtime remediation 计划包含下载、解压、目录写入，When reviewer 查看 `host_runtime_plan.remediation_fragment`，Then 必须能读到 `managed_runtime_root`、`rollback_units`、`cleanup_units` 与 `will_not_touch`  
2. Given 某个动作无法严格回滚，When `host_runtime_plan.remediation_fragment` 输出该动作，Then 必须显式标注 `non_rollbackable_effects` 或 `manual_recovery_required`  
3. Given 当前只是 source-only surface，When reviewer 检查 formal docs，Then 可以明确读到 Host Runtime Manager 不得越权直接改写系统环境

### US-096-4

作为 **企业/离线环境 operator**，我希望系统能优先复用离线 bundle reality，并在 bundle 不匹配时诚实阻断，而不是擅自切到在线下载或别的平台安装方案。

**验收**：

1. Given operator 提供离线 bundle，When Host Runtime Manager 解析 profile，Then 必须校验 OS / arch 与 manifest 一致性；若 manifest 缺失，则必须显式降级成 `platform_unverified_bundle` 而不是假装已验证  
2. Given 离线 bundle 平台不匹配，When 系统生成结果，Then 必须阻断并明确要求更换匹配 bundle  
3. Given 当前环境禁止联网，When 所需 profile 只支持离线 bundle，Then 系统不得偷偷尝试在线下载

## 功能需求

### Positioning And Authority

| ID | 需求 |
|----|------|
| FR-096-001 | `096` 必须把 Host Runtime Manager 正式定义为 `095.Host Readiness` 的 canonical truth owner，负责 observe、classify、handoff、plan fragment 输出 |
| FR-096-002 | `096` 只能消费 `093 / 094 / 095` 的上游 truth，不得重写 installed runtime truth、onboarding truth 或 delivery confirmation truth |
| FR-096-003 | Host Runtime Manager 不得直接执行最终 mutating action；它只能输出单一 `host_runtime_plan` 及其子面，真正执行仍属于 `095` 下游 |
| FR-096-004 | Host Runtime Manager 必须显式区分 `observe` 与 `mutate-ready planning`；无论哪种路径，都不得在本层静默下载、安装或升级 |

### Minimal Executable Host Classification

| ID | 需求 |
|----|------|
| FR-096-005 | `minimal_executable_host` 必须至少绑定 `platform support + python>=3.11 + verifiable AI-SDLC runtime target + surface binding` 四个条件 |
| FR-096-006 | `python_runtime` 与 `installed_cli_runtime` 必须被固定归类为 `bootstrap_only` 依赖，不能伪装成 `mainline_remediable` |
| FR-096-007 | source runtime、editable runtime、`uv run`、`python -m ai_sdlc` 以及 IDE/AI 未绑定 installed runtime surface，在 frontend mainline host runtime mutate 路径上最多只能达成 `diagnose + acquisition handoff`，不得声明 `installed_runtime_ready=true`；这不否定现有 Stage 0 / `init` / `adapter` 的 source-runtime reality |
| FR-096-008 | 若当前 surface 无法证明其真实调用目标是可验证 installed runtime，系统必须把 `surface_binding_state` 标成非 ready，并给出 `reason_codes` |
| FR-096-009 | Host Runtime Manager 不得仅凭版本字符串、PATH 猜测或人工文案就宣布 `minimal_executable_host=true` |

### Platform Detection And Installer Profiles

| ID | 需求 |
|----|------|
| FR-096-010 | Host Runtime Manager 必须显式识别 `windows / macos / linux` 与架构信息，并把结果写入 readiness snapshot |
| FR-096-011 | Host Runtime Manager 只能引用与当前 OS / arch 匹配的 `installer_profile_ref`；不得执行跨平台或跨架构猜测性安装 |
| FR-096-012 | v1 至少必须正式承认现有 `offline_bundle_posix_shell`、`offline_bundle_windows_powershell`、`offline_bundle_windows_bat_launcher` 三类离线 bundle 入口，并把其平台 manifest 校验 reality 提升为 formal contract |
| FR-096-013 | 若找不到匹配 profile，系统必须返回 `unsupported` 或 `blocked`，而不是降级到未声明的渠道 |
| FR-096-014 | 未来新增 profile 时，必须以新增 `installer_profile_ref` 扩展，不得改写已冻结的 readiness state 语义 |

### Bootstrap Acquisition Channel

| ID | 需求 |
|----|------|
| FR-096-015 | 当 `minimal_executable_host=false` 时，系统必须输出结构化 `host_runtime_plan`，其中 `bootstrap_acquisition` 子面被填充 |
| FR-096-016 | `host_runtime_plan.bootstrap_acquisition` 至少必须说明：缺的是什么、推荐哪个 profile、需要 operator 做什么、满足什么条件后可重新进入主线 |
| FR-096-017 | 对 `python>=3.11` 缺失或版本不足，v1 只允许输出 acquisition handoff；不得在 source runtime 内部承诺自动安装系统 Python |
| FR-096-018 | 对 installed CLI runtime 缺失，系统可以引用现有离线 bundle 或人工安装指引，但不得发明未 formalize 的在线自举器 |
| FR-096-019 | `bootstrap_acquisition` 子面不得冒充“主线已经开始执行”；在 handoff 完成前，`095` 下游不得把 host readiness 视为已满足 |
| FR-096-020 | `bootstrap_acquisition` 子面必须保留离线/企业环境 reality：若 operator 已提供离线 bundle，则优先引用匹配 bundle，而不是默认在线方案 |

### In-Mainline Remediation

| ID | 需求 |
|----|------|
| FR-096-021 | 只有当 `minimal_executable_host=true` 时，Node、选定 package manager、Playwright browsers 才允许进入 `mainline_remediable` 规划 |
| FR-096-022 | Node、package manager、Playwright browsers 的缺口必须分别表达，不能被压成一个笼统的“环境不满足” |
| FR-096-023 | Playwright browsers 缺口必须在 host runtime 层被提前暴露，不能等到 browser gate 运行失败后才回填 |
| FR-096-024 | 若某项依赖已存在但版本/兼容性不满足，系统必须把它表达为 `upgrade / replace / reconcile` 候选动作，而不是当作 `ready` |
| FR-096-025 | 若某项依赖证据不足，系统必须返回 `unknown_evidence` 或等价 reason code；不得默认乐观放行 |

### Isolation, Write Scope, And Recovery Semantics

| ID | 需求 |
|----|------|
| FR-096-026 | 所有 host runtime remediation 默认只能写入 framework-managed isolated environment，不得默认污染系统全局安装 |
| FR-096-027 | `host_runtime_plan.remediation_fragment` 必须显式列出 `managed_runtime_root`、`will_download`、`will_install`、`will_modify`、`will_not_touch` |
| FR-096-028 | 对 framework-managed local artifacts，Host Runtime Manager 必须提供可回滚单元；对无法严格回滚的副作用，必须显式标注 `non_rollbackable_effects` |
| FR-096-029 | 对需要人工清理或人工恢复的场景，Host Runtime Manager 必须标注 `manual_recovery_required`，不得把恢复责任隐含给用户 |
| FR-096-030 | Host Runtime Manager 不得把系统 PATH、全局 npm/pnpm、系统浏览器目录当作默认写入目标；若未来允许此类动作，也必须作为新增 profile + 高风险动作单独 formalize |

### Surface And Confirmation Boundary

| ID | 需求 |
|----|------|
| FR-096-031 | Host Runtime Manager 的任何 mutating 候选动作都必须能被 `095.delivery_execution_confirmation_surface` 消费；没有 confirmation surface 的路径不得继续执行 |
| FR-096-032 | Host Runtime Manager 必须把 action 预分类为 `required / optional` 所需的基础事实，但不得自己承担最终确认页协议 |
| FR-096-033 | 对存在 `non_rollbackable_effect` 或 `manual_recovery_required` 的 action，Host Runtime Manager 必须把风险元数据透传给下游确认页 |
| FR-096-034 | 在 `adapter activation` 未满足、solution 未冻结或 `host_runtime_plan.bootstrap_acquisition` 仍为 actionable/blocked 状态时，下游不得把 remediation fragment 误当成 ready-to-apply 全计划 |

### Output Contract

| ID | 需求 |
|----|------|
| FR-096-035 | `host_runtime_plan` 必须是本层 canonical machine 输出；`readiness`、`bootstrap_acquisition`、`remediation_fragment` 只是其中的稳定子面 |
| FR-096-036 | `bootstrap_acquisition` 与 `remediation_fragment` 不得拆成相互竞争的顶层协议；同一次评估允许在同一 `host_runtime_plan` 内同时表达“当前仍需 acquisition”与“后续 remediation 待 re-entry 后执行”的 deferred 事实 |
| FR-096-037 | `reason_codes` 必须覆盖至少：`python_missing`、`python_version_too_low`、`installed_runtime_unverified`、`surface_unbound`、`profile_not_found`、`platform_unsupported`、`bundle_platform_mismatch`、`offline_bundle_missing`、`permission_denied`、`network_restricted`、`playwright_browsers_missing` |
| FR-096-038 | Host Runtime Manager 输出中的 evidence 必须绑定 machine-observable source；不得引用 README、人工注释或默认值作为 readiness 证据 |
| FR-096-039 | Host Runtime Manager 输出必须对 `will_not_touch` 给出诚实边界，至少覆盖系统全局 Python、系统全局 Node/npm/pnpm、existing frontend source tree 与未确认的 root-level workspace 集成 |
| FR-096-044 | 在 `096` 实现落地前，现有 `main.py` 与离线安装脚本仍然是 human-readable reality；spec 不得把它们误表述为已经产出或消费 `host_runtime_plan` |

### Honesty, Offline, And Failure Semantics

| ID | 需求 |
|----|------|
| FR-096-040 | 对离线环境、企业网络限制、权限受限、磁盘空间不足或 bundle 缺失，Host Runtime Manager 必须诚实输出 `blocked` 或相应 reason code，不得静默切换到其他渠道 |
| FR-096-041 | 对离线 bundle 的平台不匹配，系统必须阻断并回报 manifest mismatch；对 manifest 缺失，必须显式标注 `platform_unverified_bundle` 或等价 warning，不得假装已验证 |
| FR-096-042 | 如果当前 profile 只支持人工 acquisition，系统必须返回 `manual_steps`；不得把“用户手工处理”隐藏成空结果 |
| FR-096-043 | Host Runtime Manager 不得把 source runtime 下的诊断结果写回成 installed runtime truth，也不得污染 `093` 的 update advisor cache / notice state |

## 关键实体

- **MinimalExecutableHost**：进入主线前的最小宿主成立条件，决定是进入 acquisition handoff 还是 mainline remediation
- **HostDependencyClass**：把宿主依赖固定拆成 `bootstrap_only / mainline_remediable / informational_only` 的分类器
- **InstallerProfileRef**：指向平台兼容、渠道明确、写入范围受控的安装 profile 句柄
- **HostRuntimePlan**：Host Runtime Manager 的 canonical machine 产物，承载 readiness、bootstrap acquisition 与 remediation fragment
- **Readiness Facet**：`host_runtime_plan` 中的 observe 子面
- **Bootstrap Acquisition Facet**：`host_runtime_plan` 中承载 acquisition handoff 的子面
- **Remediation Fragment Facet**：`host_runtime_plan` 中供 `095` 下游动作引擎吸收的 host runtime remediation 子面
- **Managed Runtime Root**：框架管理的隔离写入根；默认所有 host runtime mutate 动作都应落在这里

## 成功标准

- **SC-096-001**：系统可以稳定区分“需要 bootstrap acquisition”与“可以进入 in-mainline remediation”，不再把两者混成一个环境报错  
- **SC-096-002**：source / `uv run` / IDE 未绑定 surface 在 frontend mainline host runtime mutate 路径上不会越权执行 mutate，只会给出诚实 handoff 或阻断原因，同时不否定现有 Stage 0 入口 reality  
- **SC-096-003**：Node、package manager、Playwright browsers 缺口会在 host runtime 层被结构化暴露，不再等到后续执行或 browser gate 失败后才被动发现  
- **SC-096-004**：每个 host runtime 计划都能明确写出 `managed_runtime_root`、`will_not_touch`、回滚边界和不可逆副作用分级  
- **SC-096-005**：离线 bundle profile、`.bat` 启动器与 manifest 校验 reality 被正式纳入合同；平台不匹配时会阻断，manifest 缺失时会显式降级为未验证  
- **SC-096-006**：`095` 下游能够直接消费单一 `host_runtime_plan`，而不需要再发明第二套宿主状态模型

## 后续实现焦点

后续 implementation plan 至少应按以下顺序落地：

1. **Readiness Probe**
   - OS / arch、Python、surface binding、installed runtime、Node、package manager、Playwright browsers 探测
2. **Profile Resolver**
   - `installer_profile_ref`、offline bundle manifest、平台匹配与渠道能力解析
3. **Plan Builder**
   - 生成单一 `host_runtime_plan`，并填充其中的 `readiness / bootstrap_acquisition / remediation_fragment`
4. **Mainline Integration**
   - 把 host runtime fragment 并入 `095.delivery_execution_confirmation_surface` 与 action engine

这些实现都必须继续服从 `093 / 094 / 095` 的上游 truth，而不是再自持一套 runtime state。

## 两轮对抗收敛记录

- **Round 1 收敛**：
  - 把 `python >= 3.11` 与 `installed cli runtime` 明确收回到 `bootstrap acquisition channel`
  - 阻止 source / `uv run` / IDE 未绑定 surface 在 frontend mainline mutate 路径上越权执行 host runtime mutate，同时不否定 Stage 0 reality
  - 将离线 bundle shell / PowerShell / `.bat` reality 与平台 manifest 校验正式提升为 profile contract
- **Round 2 收敛**：
  - 把 `bootstrap_acquisition` 与 `remediation_fragment` 收回到同一 `host_runtime_plan`，对齐 `095` 的单一 plan 口径
  - 明确当前仓库还没有 producer / consumer；现有 CLI 与离线脚本只是输入 reality，不被伪装成已落地机器协议
  - 把 `will_not_touch`、`non_rollbackable_effects`、`manual_recovery_required` 收进 `host_runtime_plan.remediation_fragment`，防止后续执行黑盒化

---
related_doc:
  - "specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "src/ai_sdlc/cli/main.py"
  - "packaging/offline/install_offline.sh"
  - "packaging/offline/install_offline.ps1"
frontend_mainline_slice: "host_runtime_manager"
frontend_mainline_slice_status: "formal_baseline_frozen_two_round_adversarial_converged"
host_runtime_scope:
  bootstrap_only:
    - "python_runtime"
    - "installed_cli_runtime"
  mainline_remediable:
    - "node_runtime"
    - "package_manager"
    - "playwright_browsers"
frontend_evidence_class: "framework_capability"
---
