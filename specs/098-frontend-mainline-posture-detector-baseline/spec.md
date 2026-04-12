# 功能规格：Frontend Mainline Posture Detector Baseline

**功能编号**：`098-frontend-mainline-posture-detector-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；作为 `097` 下游 detector-only implementable slice  
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../097-frontend-mainline-posture-delivery-registry-baseline/spec.md`](../097-frontend-mainline-posture-delivery-registry-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py`](../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py)、[`../../src/ai_sdlc/scanners/frontend_contract_scanner.py`](../../src/ai_sdlc/scanners/frontend_contract_scanner.py)、[`../../src/ai_sdlc/models/frontend_solution_confirmation.py`](../../src/ai_sdlc/models/frontend_solution_confirmation.py)

> 口径：`098` 冻结的不是 registry resolver、delivery bundle materializer 或 sidecar scaffold writer，而是 `097` 之后第一个可以独立落地的 detector-only 正式切片。它只回答四个问题：detector 允许读取哪些 evidence source、这些 evidence 如何决定优先级、五类 `support_status` 在什么条件下成立、以及 `sidecar_root_recommendation` 最多允许生成到什么边界；但它不重写 `014` attachment truth，不重写 `073` solution truth，不提前吞并 `097` 的 delivery registry contract，也不把 observe 阶段偷渡成 mutate。

## 问题定义

`097` 已经把 `frontend_posture_assessment`、`sidecar_root_recommendation`、`frontend_delivery_registry` 与 `delivery_bundle_entry` 冻结成单一 formal contract，但真正落实现有仓库时，仍然缺少一份 **detector 自身的 formal baseline** 来回答下面这些实现前必须锁死的问题：

1. detector 到底允许读取哪些 repo evidence；哪些只能作为 advisory clue，哪些可以直接决定 `support_status`。
2. 当 attachment truth、manifest/config signal、source-tree signal、component-library clue 彼此冲突时，谁优先，谁只能降级成 `ambiguous`。
3. `supported_existing_candidate` 的成立条件到底是什么；它不能继续被误解成“看到一个 Vue 痕迹就默认可接管”。
4. `managed_frontend_already_attached` 应该如何继续服从 `014`，避免 detector 重新发明第二套 attached state。
5. `sidecar_root_recommendation` 在 detector 阶段最多可以输出到什么粒度；哪些内容必须留给后续 solution freeze / action plan，而不是由 detector 偷偷代 operator 做决定。

如果不先冻结这层 detector contract，后续实现会继续在四种错误之间漂移：

- 把 component-library clue 当成 stack truth，导致 `React + PrimeVue clue` 被误报成 supported candidate
- 把 attachment truth 与 repo scan truth 并列处理，导致已附着托管前端的仓库被重新分类
- 把 evidence 不足与 unsupported 混成一类，最后既不诚实，也无法决定下一步
- 在 detector 阶段就生成带 root-level 联动暗示的 sidecar 建议，提前越过 `073` 与 `095` 的确认边界

因此，`098` 的目标是冻结一条最小但严格的 Frontend Posture Detector baseline：先把 evidence source、判定优先级、状态映射与 sidecar recommendation boundary 收敛成 machine truth，再把 registry resolver、action planning 与实际写入继续留给 `097/095` 下游。

## 范围

- **覆盖**：
  - `097.frontend_posture_assessment` 的 detector authority、输入 evidence 类别与决策顺序
  - v1 detector 允许读取的 evidence source class 与 evidence ref contract
  - 五类 `support_status` 的成立条件、降级规则与诚实边界
  - `managed_frontend_already_attached` 对 `014` attachment truth 的单向服从
  - `sidecar_root_recommendation` 在 detector 阶段的生成边界与默认 no-touch 约束
  - detector 与 `094 / 073 / 095 / 096 / 097` 的 truth order 与 downstream handoff
- **不覆盖**：
  - 在本 work item 中直接实现 scanner、repo walker、manifest parser 或 sidecar scaffold writer
  - formalize `frontend_delivery_registry`、`delivery_bundle_entry` 或 registry materialization runtime
  - 决定最终 provider / component-library / style pack；这些继续属于 `073` 与后续 resolver
  - 直接生成 `frontend_action_plan`、rollback、cleanup、retry 或任何 mutate protocol
  - 允许 detector 在 unsupported / ambiguous 路径下修改旧 frontend、写根目录、写 lockfile 或安装依赖

## 已锁定决策

- `098` 是 `097` 下游的 detector-only implementable slice；它只负责生成 `frontend_posture_assessment` 与受控的 `sidecar_root_recommendation`。
- detector 必须保持 observe-only；任何目录创建、依赖安装、workspace 联动、root-level 路由/CI/proxy 修改都不属于 `098`。
- `014` attachment truth 拥有最高优先级；一旦仓库已具备 `managed_frontend_already_attached` 的 canonical evidence，detector 不得再回退成 supported/unsupported/ambiguous。
- detector 只能使用 machine-observable evidence；不得把用户意图、未来计划、推荐 provider 或 registry availability 当成现状 evidence。
- component-library clue 只能帮助解释 `detected_component_library` 或 reason code；它本身不得把 unsupported/unknown frontend 升级成 supported candidate。
- `supported_existing_candidate` 只表示“可继续进入后续受控判断”；v1 不得把它扩写成默认 takeover、默认绑定 provider，或默认 root integration ready。
- `ambiguous_existing_frontend` 固定表示 evidence 冲突、证据不足或 signal 只到“有前端痕迹”；它不是 unsupported 的柔化措辞，也不是 supported 的弱化别名。
- `sidecar_root_recommendation` 只能输出推荐子树、默认 `will_not_touch` 与被阻断的 root-level action 类别；不得替后续阶段决定 provider、style、workspace linkage 或 install target。

## Evidence Source Model

### 1. AttachmentTruthEvidence

`AttachmentTruthEvidence` 是 detector 唯一允许直接读取的 attachment 类上游 truth，来源继续受 `014` 约束。

其最小字段至少包括：

- `evidence_id`
- `evidence_kind`
  - `attachment_truth`
- `attachment_state_ref`
- `source_path`
- `confidence`
- `reason_codes`

规则：

- 只要 canonical attachment truth 已表明当前仓库存在 AI-SDLC managed frontend attach reality，detector 必须直接产出 `managed_frontend_already_attached`
- attachment truth 的缺失不等于 unsupported；只能说明需要继续看 repo evidence

### 2. RepoFrontendEvidence

`RepoFrontendEvidence` 是 detector v1 允许消费的 repo-level machine-observable evidence class。它至少分为四类：

- `manifest_or_workspace_signal`
  - package manifest、workspace manifest、lockfile、脚本入口等能表达 frontend stack 的 machine evidence
- `framework_config_signal`
  - framework config、build config、routing/config profile 等能表达具体 frontend family 的 evidence
- `source_tree_signal`
  - `.vue`、`.tsx`、`.jsx`、入口文件、目录布局等 source-level evidence
- `component_library_clue`
  - 组件库包名、样式包、adapter clue；只能做解释性信号，不能单独决定 supported

其最小字段至少包括：

- `evidence_id`
- `evidence_kind`
- `source_path`
- `signal_family`
- `observed_value`
- `supports_frontend_family`
- `confidence`
- `reason_codes`

规则：

- `component_library_clue` 不能在缺少 stack-level evidence 时单独决定 `support_status`
- detector 必须保留 `source_path`，以便 downstream 能解释 verdict 来自哪个 repo 事实

### 3. PostureDecisionEvidenceBundle

`PostureDecisionEvidenceBundle` 是 detector 汇总 evidence 时对外保留的最小证据面，至少包括：

- `assessment_id`
- `evidence_refs`
- `dominant_evidence_ref`
- `conflict_evidence_refs`
- `reason_codes`
- `confidence`

其中：

- `dominant_evidence_ref` 表示当前 verdict 主要依据的 evidence
- `conflict_evidence_refs` 只记录真实冲突，不把所有弱 clue 都抬升成冲突

## 判定优先级

detector 的判定顺序固定如下：

1. **Attachment truth first**
   - 若 `014` 已给出 managed attached reality，直接返回 `managed_frontend_already_attached`
2. **Stack-level repo evidence second**
   - 使用 `manifest_or_workspace_signal`、`framework_config_signal`、`source_tree_signal` 决定是否存在可识别 existing frontend
3. **Conflict / insufficiency honesty third**
   - 若 stack-level evidence 互相冲突，或只到“有前端痕迹但不足以可靠分类”，返回 `ambiguous_existing_frontend`
4. **Support policy mapping fourth**
   - 若可靠识别为当前支持矩阵中的 existing frontend candidate，返回 `supported_existing_candidate`
   - 若可靠识别为 `React` 或其他当前不支持 frontend family，返回 `unsupported_existing_frontend`
   - 若可靠识别结果为“没有 existing frontend evidence”，返回 `no_frontend_detected`
5. **Component-library clue last**
   - 仅用于补充 `detected_component_library`、`reason_codes` 与 sidecar 建议文案，不得反向改写第 1~4 步得到的状态

优先级护栏：

- detector 不得用 registry availability、provider availability 或 solution recommendation 反向改写 posture verdict
- 当 evidence 同时包含“旧前端存在”与“AI-SDLC managed attach 已存在”时，attachment truth 始终优先
- 当 stack-level evidence 只能证明“这里可能有前端”，但不能可靠落到 `vue2/vue3/react/unknown` 之一时，必须返回 `ambiguous_existing_frontend`

## 五类 Support Status

### 1. `managed_frontend_already_attached`

成立条件：

- `014` attachment truth 已提供 canonical attached evidence

语义：

- 当前仓库已进入 AI-SDLC managed frontend attachment reality
- detector 不再重新判断 takeover 或 sidecar 默认值

### 2. `supported_existing_candidate`

成立条件：

- 不存在 managed attached truth
- stack-level repo evidence 能可靠识别当前 existing frontend family
- 该 family 在 `097` 规定的 current mainline posture policy 中仍属于可继续评估候选
- 当前 evidence 不存在足以推翻 verdict 的冲突 signal

语义：

- 只表示“允许继续进入后续受控判断”
- 不表示 provider 已选定、registry 已解析、旧工程可默认 takeover、root integration 已允许

### 3. `unsupported_existing_frontend`

成立条件：

- 不存在 managed attached truth
- stack-level repo evidence 能可靠识别 existing frontend
- 当前识别结果落在 v1 不支持矩阵，例如 `React` 或其他明确 unsupported family

语义：

- 默认保持旧 frontend 不动
- 仅允许 downstream 提供 `continue_without_frontend_takeover` 与 `consider_sidecar_managed_frontend` 等后续入口

### 4. `ambiguous_existing_frontend`

成立条件：

- 不存在 managed attached truth
- repo evidence 相互冲突，或只有部分 frontend 痕迹，尚不足以可靠分类

语义：

- 固定表示 evidence insufficient / conflicting
- 不能被解释成弱 supported，也不能被偷换成 unsupported

### 5. `no_frontend_detected`

成立条件：

- 不存在 managed attached truth
- detector 在允许的 evidence source 中没有发现可靠 existing frontend evidence

语义：

- 只表达当前仓库未检测到 existing frontend reality
- 不提前暗示未来一定要创建 managed frontend

## Sidecar Recommendation Boundary

`sidecar_root_recommendation` 在 `098` 中只能由 detector 派生，不能独立发明新计划。其最小字段至少包括：

- `recommended_root`
- `root_kind`
  - `new_controlled_subtree`
- `requires_explicit_confirmation`
- `default_will_not_touch`
- `separate_root_level_actions`
- `blocked_reason_codes`

生成规则：

- `managed_frontend_already_attached`：默认 `sidecar_root_recommendation = null`
- `supported_existing_candidate`：可以返回受控 recommendation，但不得默认要求 sidecar，也不得提前给出 workspace/root integration 方案
- `unsupported_existing_frontend`：允许返回 “若未来显式选择 sidecar，应落到新建受控子树” 的 recommendation
- `ambiguous_existing_frontend`：只能输出保守 recommendation 或 `blocked_reason_codes`；不得假装已经知道最佳根路径
- `no_frontend_detected`：可以提供 greenfield-like managed root suggestion，但仍不得越权到 provider/style/install 决策

强制边界：

- `default_will_not_touch` 至少覆盖旧 frontend 目录、旧 manifest、旧 lockfile 与未确认的 root-level integration
- `separate_root_level_actions` 至少区分：workspace、lockfile、CI、proxy、route integration
- detector 不得创建目录、写脚手架、写 package manifest、写 lockfile、改 CI、改 proxy、改路由

## 用户故事与验收

### US-098-1

作为 **brownfield operator**，我希望 detector 先以 attachment truth 和 repo evidence 做诚实判断，而不是因为看到某些组件库痕迹就把旧项目误判成可接管候选。

**验收**：

1. Given 仓库存在 canonical managed attachment evidence，When detector 运行，Then 必须返回 `managed_frontend_already_attached`  
2. Given 仓库只有 component-library clue，但没有可靠 stack-level evidence，When detector 运行，Then 不得因为 clue 存在而返回 `supported_existing_candidate`  
3. Given repo evidence 明确识别为 `React`，When detector 运行，Then 必须返回 `unsupported_existing_frontend`

### US-098-2

作为 **reviewer / maintainer**，我希望 detector 的优先级和五类状态是固定且可复核的，这样后续实现不会继续把 ambiguity、unsupported 和 attached 混写。

**验收**：

1. Given attachment truth 与 repo signal 同时存在，When 审查 `098`，Then 可以明确读到 attachment truth 拥有更高优先级  
2. Given repo signal 彼此冲突，When detector 输出结果，Then 必须返回 `ambiguous_existing_frontend`，而不是任意挑一个乐观状态  
3. Given repo 中没有 reliable frontend evidence，When detector 输出结果，Then 必须返回 `no_frontend_detected`

### US-098-3

作为 **novice operator**，我希望 detector 生成的 sidecar 建议保持克制，只告诉我“如果以后显式选择 sidecar，大致应落在哪里，以及默认不会碰什么”，而不是在还没确认时就动根工程。

**验收**：

1. Given `unsupported_existing_frontend`，When detector 生成 `sidecar_root_recommendation`，Then 只能推荐 `new_controlled_subtree`，并保留 `requires_explicit_confirmation=true`  
2. Given detector 输出 sidecar recommendation，When reviewer 检查 `default_will_not_touch`，Then 必须看到旧 frontend、旧 manifest、旧 lockfile 与 root-level integration 默认不动  
3. Given 当前仍处于 detector 阶段，When 审查 `098` formal docs，Then 可以明确读到 detector 不得创建目录、写脚手架或决定 provider/style/install 细节

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-098-001 | `098` 必须作为 `097` 下游的 detector-only implementable slice 被正式定义 |
| FR-098-002 | `098` 只能消费 `014 / 073 / 094 / 095 / 096 / 097` 与 machine-observable repo evidence；不得回写这些 upstream truth |
| FR-098-003 | `098` 的 canonical machine 输出只允许覆盖 `frontend_posture_assessment` 与由其派生的 `sidecar_root_recommendation`；不得偷渡 registry resolver 或 mutate protocol |
| FR-098-004 | detector 不得把 registry availability、solution recommendation、未来 provider 选择或用户意图当作现状 posture evidence |

### Evidence Source Contract

| ID | 需求 |
|----|------|
| FR-098-005 | detector 必须先读取 `014` attachment truth；只要 attached evidence 成立，就必须优先返回 `managed_frontend_already_attached` |
| FR-098-006 | detector v1 允许消费的 repo evidence 至少必须区分 `manifest_or_workspace_signal / framework_config_signal / source_tree_signal / component_library_clue` |
| FR-098-007 | `component_library_clue` 只能用于解释 `detected_component_library`、`reason_codes` 或辅助 sidecar recommendation；不得单独决定 supported verdict |
| FR-098-008 | detector 输出必须保留 `evidence_refs` 与 `dominant_evidence_ref`，以便 downstream 可以复核 verdict 来源 |
| FR-098-009 | 当 evidence 冲突或不足时，detector 必须诚实返回 `ambiguous_existing_frontend`，不得通过猜测补齐缺失 signal |

### Support Status Semantics

| ID | 需求 |
|----|------|
| FR-098-010 | `support_status` 必须固定为 `no_frontend_detected / supported_existing_candidate / unsupported_existing_frontend / ambiguous_existing_frontend / managed_frontend_already_attached` 五类 |
| FR-098-011 | `supported_existing_candidate` 只能表示“允许进入后续受控判断”；不得被描述成默认 takeover、默认 provider binding 或默认 root integration ready |
| FR-098-012 | 当 repo evidence 可靠识别为 `React` 或其他当前明确 unsupported family 时，detector 必须返回 `unsupported_existing_frontend` |
| FR-098-013 | `no_frontend_detected` 只能表示 absence of reliable existing frontend evidence；不得把未来 planned managed frontend 伪装成当前存在事实 |
| FR-098-014 | `managed_frontend_already_attached` 必须继续单向服从 `014`；`098` 不得新建第二套 attachment state |

### Sidecar Recommendation Boundary

| ID | 需求 |
|----|------|
| FR-098-015 | `sidecar_root_recommendation` 只能由 detector 从 posture verdict 派生；不得独立决定 provider/style/install 方案 |
| FR-098-016 | `unsupported_existing_frontend` 路径下的 sidecar recommendation 只能指向 `new_controlled_subtree`，且必须要求显式确认 |
| FR-098-017 | `default_will_not_touch` 至少必须覆盖旧 frontend 目录、旧 manifest、旧 lockfile 与未确认的 root-level integration |
| FR-098-018 | `separate_root_level_actions` 至少必须区分 workspace、lockfile、CI、proxy、route integration，且全部默认关闭 |
| FR-098-019 | detector 不得创建目录、写脚手架、写 package manifest、写 lockfile 或改动根工程 |

### Downstream Handoff

| ID | 需求 |
|----|------|
| FR-098-020 | downstream `frontend_action_plan` 与 registry resolver 只能消费 `098` 输出的 posture truth，不得反向改写 detector verdict |
| FR-098-021 | `098` 必须明确把 provider/style/runtime package truth 留给 `097` 下游 resolver；detector 不得自持第二份 registry truth |
| FR-098-022 | `098` 必须为后续实现明确下一优先切片仍是 `Delivery Registry Resolver`，并保持 detector / resolver 分离 |

## 关键实体

- **AttachmentTruthEvidence**：承载 `014` attachment truth 的 canonical detector 输入
- **RepoFrontendEvidence**：承载 manifest/config/source/component-library 四类 repo signal
- **PostureDecisionEvidenceBundle**：承载 detector 对外暴露的 dominant evidence、冲突 evidence 与 confidence
- **Frontend Posture Assessment**：承载五类 `support_status`、`reason_codes`、`evidence_refs` 与 downstream next-step boundary
- **Sidecar Root Recommendation**：承载 detector 阶段允许表达的 sidecar recommendation 与 no-touch 边界

## 成功标准

- **SC-098-001**：attachment truth、repo evidence、component-library clue 的优先级不再混乱，reviewer 能直接复核 detector verdict 来源  
- **SC-098-002**：五类 `support_status` 在 detector 语义上被固定下来，不再出现 attached / ambiguous / unsupported 混写  
- **SC-098-003**：`sidecar_root_recommendation` 被限制在 detector 应有边界内，后续实现不会再借 detector 名义改根工程  
- **SC-098-004**：`098` 与 `097` 的边界清晰，detector 不再混入 registry resolver truth  

## 后续实现拆分建议

`098` 之后的下一正式切片应继续保持 `detector / resolver` 解耦：

1. **Frontend Posture Detector Runtime**
   - 实现 evidence collection、dominant-evidence selection 与五类 status mapping
   - 输出 canonical `frontend_posture_assessment`
2. **Delivery Registry Resolver**
   - 继续承接 `097` 的 controlled registry / delivery bundle truth
   - 消费 `098` posture verdict，但不得反向改写 detector contract

---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/097-frontend-mainline-posture-delivery-registry-baseline/spec.md"
frontend_mainline_scope: "posture_detector"
frontend_mainline_status: "formal_baseline_frozen"
detector_v1_statuses:
  - "no_frontend_detected"
  - "supported_existing_candidate"
  - "unsupported_existing_frontend"
  - "ambiguous_existing_frontend"
  - "managed_frontend_already_attached"
frontend_evidence_class: "framework_capability"
---
