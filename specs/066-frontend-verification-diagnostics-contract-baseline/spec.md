# 功能规格：Frontend Verification Diagnostics Contract Baseline

**功能编号**：`066-frontend-verification-diagnostics-contract-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)

> 口径：本 work item 承接 `012 / 013 / 014 / 065` 已冻结的 frontend contract truth，并与 `018` 的 gate / compatibility 消费面保持对齐，用于把 `verification truth -> diagnostics truth -> surface adapters` 的分层合同收敛成单一 formal baseline。frontend 是首个 source family，但 `Layer B` 必须保持 source-agnostic。`066` 只冻结 diagnostics contract，不引入新的平行 verify stage、gate family 或 runner truth model。

## 问题定义

`012`、`013`、`014`、`065` 已经分别冻结了：

- frontend contract verify 主链
- observation artifact 的 provider / export / attachment truth
- canonical artifact 的 runtime read-mostly 消费边界
- sample source self-check 对 `pass / drift / gap` 的最小自包含演示

当前缺少的是一层单独的 diagnostics truth，用来回答下面这个问题：

- 当 verification source 已声明存在时，系统如何区分“根本没有 artifact”“artifact 已提供但损坏”“artifact 合法但稳定为空”“artifact 合法且存在 drift”“artifact 合法且 clean”

如果不把这层合同独立冻结，当前和后续实现都很容易滑向同一个错误：

- `verify constraints`、`VerificationGate / VerifyGate`、CLI、`ProgramService` 分别从 `[]`、缺失路径、异常字符串或局部上下文重新推断语义
- `missing_artifact`、`valid_empty`、`drift` 被折叠成同一类 “observations is empty”
- `invalid_artifact` 被误并成 `missing_artifact`
- 下游 recheck / remediation / visual-a11y source family 再各自长出一套私有 diagnostics 口径

因此，`066` 先要解决的不是“再加一条 verify 规则”，而是：

- `Layer A / Layer B / Layer C` 的职责边界是什么
- `diagnostic_status` 与 `policy_projection` 的关系是什么
- frontend 作为第一个 source family 时，`missing_artifact / invalid_artifact / valid_empty / drift / clean` 的判定条件是什么
- `verify constraints`、`VerificationGate / VerifyGate`、CLI、`ProgramService` 如何只消费统一 truth，而不再重算语义
- 后续 source family、recheck、remediation、visual-a11y 如何复用这层 contract，而不触发二次抽象或大面积重构

## 范围

- **覆盖**：
  - 将 diagnostics contract 正式定义为独立于 `verification truth` 和 `surface rendering` 的中间真值层
  - 锁定 `Layer A: Verification Truth`、`Layer B: Diagnostics Truth`、`Layer C: Surface Adapters` 的职责边界
  - 锁定 frontend 首个 source family 的五类状态集：`missing_artifact`、`invalid_artifact`、`valid_empty`、`drift`、`clean`
  - 锁定 `diagnostic_status` 的单向、互斥、短路决议顺序
  - 锁定 `evidence` 与 `policy_projection` 的最小字段集合
  - 锁定 `status -> projection` 的正式规则与 `Layer C` 的消费边界
  - 为后续 `core / gates / cli / program / tests` 的实现与下游 handoff 提供 canonical baseline
- **不覆盖**：
  - 改写 `012 / 013 / 014 / 065` 已冻结的上游 contract
  - 实现 remediation / recheck / visual-a11y 检查本体
  - 引入新的平行 verify stage、gate family、runner truth model 或第二套 diagnostics pipeline
  - 定义第二个 source family 的正式状态机
  - 改写 canonical observation artifact schema 或引入新的 artifact 类型
  - 允许 CLI、runner、`ProgramService`、gate surface 通过空列表、异常字符串、路径缺失等局部信号自行重算 diagnostics 语义

## 已锁定决策

- `Layer A` 继续承载 verification source、check object、verdict、blocker、advisory、coverage gap 等正式判断，但不直接承载 artifact 生命周期细节
- `Layer B` 是本 work item 的核心：负责表达某个 verification source 当前为何处于该 verdict 前状态，并作为所有 surface 的 canonical diagnostics truth
- `Layer C` 只负责显示、路由、序列化与 readiness 投影，不得再拥有独立 diagnostics 规则系统
- frontend 是 `Layer B` 的第一个 source family，但字段、命名和规则必须可扩展到后续非-frontend source
- `missing_artifact` 只表示 absence；`invalid_artifact` 只表示 presence-but-broken；二者不得互并
- `valid_empty` 必须建立在 artifact 已提供、结构合法、可解析、reference resolution 成功且 canonical normalization 完成之后
- `drift` 只能建立在 artifact 已提供、合法、完成 canonical normalization 且比较已完成的前提上
- `policy_projection` 必须由 status resolution 规则单向导出；surface adapters、CLI、runner、`ProgramService` 不得局部覆盖或重新推断 projection
- 下游 source family、recheck、remediation、visual-a11y 只能消费 `Layer B` truth，不得各自发明新的 source-private diagnostics taxonomies

## 定位与 Truth Order

- `diagnostic_status` 必须按单向、互斥、短路的顺序决议；一旦命中前序状态，后续状态不得再参与改判。
- `diagnostic_status` 描述事实状态，`policy_projection` 描述其对 verification truth 的正式影响；两者不得混为单一字段。
- `drift` 只能建立在“artifact 已提供、合法、完成 canonical normalization，且比较已完成”的前提上。
- `066` 只冻结 diagnostics contract，不引入新的平行 verify stage、gate family 或 runner truth model。

正式 truth order 如下：

1. 上游 `012 / 013 / 014 / 065` 固定 contract artifact、observation artifact/reference 与 runtime attachment 的输入边界。
2. source-family normalizer 对给定 `source_family / source_key` 与同一 artifact/reference 输入执行 status resolution。
3. `Layer B` 产出 `diagnostic_status + evidence`。
4. 固定 projection 规则从 `diagnostic_status + evidence` 单向导出 `policy_projection`。
5. `verify constraints`、`VerificationGate / VerifyGate` 与等价 verification consumer 只消费 `policy_projection`，把其投影进 `Layer A` 的 blocker / advisory / coverage gap / readiness 结论。
6. CLI terminal、`--json`、runner、`ProgramService` 只消费已存在的 `diagnostic_status` 与 `policy_projection`，不得重新解释或回推语义。

## 用户故事与验收

### US-066-1 — Framework Maintainer 需要统一的 diagnostics truth 层

作为**框架维护者**，我希望 verification 主链、gate surface、CLI 与 `ProgramService` 之间共享同一套 diagnostics truth，以便后续 source family 升级时不需要再次拆模型或大面积重构。

**验收**：

1. Given 我审阅 `066` formal docs，When 我追踪 truth order，Then 可以明确看到 `Layer A / Layer B / Layer C` 的单向关系与职责边界
2. Given 我审阅 `066` formal docs，When 我检查 non-goals，Then 可以明确读到 `066` 不引入新的平行 verify stage、gate family 或 runner truth model

### US-066-2 — Operator 需要 absence / broken / empty / drift 被诚实区分

作为**operator**，我希望 `missing_artifact`、`invalid_artifact`、`valid_empty`、`drift` 与 `clean` 有清晰且互斥的判定条件，以便不会把“没给输入”“给了坏输入”“给了合法空输入”或“真实 drift”混成一个状态。

**验收**：

1. Given observation artifact 或 reference 根本未提供，When source normalizer 运行，Then `diagnostic_status` 为 `missing_artifact`
2. Given artifact 或 reference 已提供但 envelope / schema / parse / canonical loader / reference resolution 失败，When source normalizer 运行，Then `diagnostic_status` 为 `invalid_artifact`
3. Given artifact 已提供且 canonical normalization 完成，且 `observation_count == 0`，When source normalizer 运行，Then `diagnostic_status` 为 `valid_empty`
4. Given artifact 合法、canonical normalization 完成且比较已完成，When 检测到 contract mismatch，Then `diagnostic_status` 为 `drift`

### US-066-3 — Surface Owner 需要 adapter 只消费 truth 而不重算语义

作为**surface owner**，我希望 `verify constraints`、`VerificationGate / VerifyGate`、CLI 与 `ProgramService` 只消费统一的 `policy_projection`，以便不同入口不会给出不同的 blocker、gap 或 readiness 解释。

**验收**：

1. Given 同一组 `source_family / source_key` 与同一 artifact/reference 输入，When 我从 CLI、runner 与 `ProgramService` 读取结果，Then `diagnostic_status` 与 `policy_projection` 必须一致
2. Given `diagnostic_status` 已经是 `valid_empty`，When 某个 surface 渲染结果，Then 它不得再把该状态重算成 `coverage_gap`
3. Given `diagnostic_status` 已经是 `missing_artifact`，When 某个 surface 渲染结果，Then 它不得把该状态伪装成 `drift`

### US-066-4 — Downstream Implementer 需要可复用的 diagnostics shell

作为**后续实现者**，我希望 recheck、remediation、visual-a11y 与未来 source family 能直接消费 `Layer B`，以便后续扩展是“增加 source normalizer”，而不是回头拆 `verify / gate / program` 的主干模型。

**验收**：

1. Given 我审阅 `066` formal docs，When 我寻找最小 core entity，Then 我可以直接读到 `source_family / source_key / diagnostic_status / evidence / policy_projection`
2. Given 我审阅 `066` formal docs，When 我查看 downstream handoff，Then 可以明确读到下游消费者不得跳过 projection，也不得直接以 `diagnostic_status` 推导 verdict / severity / readiness

## 功能需求

### Layering And Scope

| ID | 需求 |
|----|------|
| FR-066-001 | `066` 必须作为承接 `012 / 013 / 014 / 065`、并与 `018` 对齐的 diagnostics contract baseline 被正式定义 |
| FR-066-002 | `066` 必须明确 `Layer A: Verification Truth`、`Layer B: Diagnostics Truth`、`Layer C: Surface Adapters` 的分层边界 |
| FR-066-003 | `066` 必须明确 `Layer A` 继续承载 verification source / check object / verdict / blocker / advisory / coverage gap，而不是 artifact 生命周期细节 |
| FR-066-004 | `066` 必须明确 `Layer B` 是 source-agnostic diagnostics shell，frontend 只是首个 source family |
| FR-066-005 | `066` 必须明确 `Layer C` 只能消费既有 truth，不得拥有独立 diagnostics 规则系统 |
| FR-066-006 | `066` 不得引入新的平行 verify stage、gate family、runner truth model 或第二套 diagnostics pipeline |

### Status Resolution And Core Entity

| ID | 需求 |
|----|------|
| FR-066-007 | `066` 必须定义 frontend 首个 source family 的最小状态集：`missing_artifact`、`invalid_artifact`、`valid_empty`、`drift`、`clean` |
| FR-066-008 | `missing_artifact` 的成立条件必须限定为 observation artifact 不存在，或上游 attachment / reference 根本未提供 |
| FR-066-009 | `invalid_artifact` 的成立条件必须限定为 artifact 或其引用已提供，但 envelope / schema / parse / canonical loader / reference resolution 任一失败 |
| FR-066-010 | `valid_empty` 的成立条件必须限定为 artifact 已提供、envelope / schema / parse / canonical normalization 全部成功，且 `observation_count == 0` |
| FR-066-011 | `drift` 的成立条件必须限定为 artifact 已提供、合法、完成 canonical normalization、比较已完成且存在 contract mismatch |
| FR-066-012 | `clean` 的成立条件必须限定为 artifact 已提供、合法、完成 canonical normalization、比较已完成且无 diagnostics issue |
| FR-066-013 | `diagnostic_status` 必须按 `missing_artifact -> invalid_artifact -> valid_empty -> drift -> clean` 的顺序单向、互斥、短路决议 |
| FR-066-014 | 对同一 `source_family / source_key` 与同一 artifact/reference 输入，status resolution 必须产生确定性、可重复的结果，不得因 surface、调用入口或展示路径不同而变化 |
| FR-066-015 | `Layer B` 的最小 core entity 必须至少包括 `source_family`、`source_key`、`diagnostic_status`、`evidence`、`policy_projection` |
| FR-066-016 | `evidence` 至少必须能承载 `artifact_ref`、`observation_count`、`parse_error_summary`、`drift_summary`、`source_linkage` |
| FR-066-017 | `policy_projection` 至少必须能承载 `readiness_effect`、`report_family_member`、`severity`、`blocker_class`、`coverage_effect` |
| FR-066-018 | `diagnostic_status` 与 `policy_projection` 不得合并为单一字段，也不得由 surface 以展示文案替代正式字段 |

### Projection Rules And Adapter Boundary

| ID | 需求 |
|----|------|
| FR-066-019 | `policy_projection` 必须由 status resolution 规则单向导出；surface adapters、CLI、runner、`ProgramService` 不得局部覆盖或重新推断 projection |
| FR-066-020 | `missing_artifact` 必须投影为 input gap / coverage gap，默认不得伪装成 `drift` |
| FR-066-021 | `invalid_artifact` 必须投影为独立 invalid-input diagnostics；其 severity / blocker 可按 policy 决定，但不得等价于 `missing_artifact` |
| FR-066-022 | `valid_empty` 必须投影为稳定空结果；它不得自动记为 `coverage_gap`，也不得升级成 `drift` |
| FR-066-023 | `drift` 必须投影为 drift blocker / drift report member，而不是缺失输入或稳定空结果 |
| FR-066-024 | `clean` 必须投影为 no-issue 状态，不得残留 blocker、gap 或 advisory |
| FR-066-025 | `verify constraints`、`VerificationGate / VerifyGate`、CLI、runner、`ProgramService` 只能消费 `policy_projection` 与 `diagnostic_status` 的既有真值，不得自行回推或重算 `gap / invalid / empty / drift` 语义 |
| FR-066-026 | 下游消费者不得直接以 `diagnostic_status` 替代 `policy_projection` 形成 verdict、severity、report family 或 readiness 结论；这些正式影响只能通过已冻结的 projection 规则导出 |

### Downstream Handoff And Non-Goals

| ID | 需求 |
|----|------|
| FR-066-027 | `066` 不得改写 `012 / 013 / 014 / 065` 的上游合同，也不得借机重写 `018` 的 gate / compatibility truth |
| FR-066-028 | `066` 不得在当前工单内实现 remediation / recheck / visual-a11y 检查本体，但必须为这些下游消费者冻结可复用的 diagnostics shell |
| FR-066-029 | `066` 不得定义第二个 source family 的正式状态机；若后续新增 source family，必须复用 `Layer B` core entity 与 projection contract |
| FR-066-030 | `066` 必须为后续 `core / gates / cli / program / tests` 的实现提供单一 canonical baseline，包括推荐触点、测试矩阵与 handoff 边界 |

## 关键实体

- **Verification Truth**：`Layer A` 的正式判断层，承载 verification source、check object、verdict、blocker、advisory、coverage gap 与 readiness 结论
- **Verification Diagnostic**：`Layer B` 的核心对象，承载某个 `source_family / source_key` 当前的 `diagnostic_status`、`evidence` 与 `policy_projection`
- **Diagnostic Evidence**：支撑 `diagnostic_status` 的结构化证据体，至少承载 artifact 引用、observation 计数、parse 错误摘要、drift 摘要与 source linkage
- **Policy Projection**：从 `diagnostic_status + evidence` 单向导出的正式影响体，供 `Layer A` 与 `Layer C` 消费
- **Frontend Diagnostic Normalizer**：frontend 首个 source family 的状态解析器，负责把 observation artifact/reference 归一到 `Layer B`
- **Surface Adapter Consumer**：消费 `policy_projection` 与 `diagnostic_status` 的 CLI、runner、`ProgramService`、gate 或 verify surface，职责仅限显示、序列化与 readiness 投影

## 成功标准

- **SC-066-001**：`066` formal docs 可以独立表达 diagnostics contract 的 scope、truth order、status set 与 non-goals，而无需回到对话或实现细节临时推断
- **SC-066-002**：对同一 `source_family / source_key` 与同一 artifact/reference 输入，status resolution 与 policy projection 产生确定性、可重复的结果，不因 surface 或调用入口不同而变化
- **SC-066-003**：`missing_artifact`、`invalid_artifact`、`valid_empty`、`drift`、`clean` 五类状态在 formal docs 中具有清晰、互斥、可验证的成立条件与 projection 规则
- **SC-066-004**：`verify constraints`、`VerificationGate / VerifyGate`、CLI、runner 与 `ProgramService` 在 formal docs 中共享单一 diagnostics truth，不再需要各自从 `[]`、异常字符串或路径缺失信号重算语义
- **SC-066-005**：后续 source family、recheck、remediation、visual-a11y 能以“新增 normalizer / 新增 consumer”的方式复用 `Layer B`，而不是回头拆 `Layer A` 或 `Layer C`
- **SC-066-006**：后续实现团队能够从 `066` 直接读出核心字段、推荐文件面、测试矩阵与“不得跳过 projection / 不得重算语义”的 guardrail
