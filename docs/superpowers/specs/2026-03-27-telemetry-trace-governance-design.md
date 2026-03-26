# Telemetry Trace Governance V1 Design

## Goal

为 AI-SDLC 框架引入第一版 telemetry trace governance 基础设施，使框架能够对 runtime、tool、evaluation 关键控制点形成可追溯证据链，并从 raw trace 提炼最小治理闭环产物，为后续 Harness Engineering 式人机闭环和自演进治理打基础。

## Why Now

当前仓库已经有 `runner`、`dispatcher`、`gate`、`verify constraints`、`doctor`、`status/recover` 等离散状态与诊断入口，但这些能力还没有统一到一套 telemetry 主键链、对象模型、证据层和治理产物层中。因此框架仍然很难稳定回答以下问题：

- 这次 run 到底经历了哪些关键状态跃迁。
- 某个 gate 或验证结论是基于什么 evidence 得出的。
- 为什么会生成某个 violation，为什么 audit verdict 不是 `clean`。
- 哪些关键控制点没有被自动采到，哪些只是 coverage gap。
- 哪些判断是结构化证据，哪些只是 `inferred` 提示。

## Design Summary

V1 采用 `runtime-first` 路线：

- 先打通本地 raw trace 存储。
- 冻结最小 contract、writer、revision、source closure 规则。
- 只自动采集高价值关键控制点。
- 由 evaluator / detector / generator 从 trace 和 evidence 派生 governance objects 与 artifacts。
- 不在 V1 引入外部 tracing 服务，也不追求完整开发会话全文采集。

V1 不只是“先有五类对象”，而是直接冻结一整套最小 contract 和写入纪律，保证未来 V2/V3 扩容时不需要推倒重来。

## V1 Scope

### In Scope

- 本地 raw trace 根目录与最小 manifest。
- `telemetry_event`、`evidence`、`evaluation`、`violation`、`artifact` 五类对象的最小可用实现。
- `goal_session_id -> workflow_run_id -> step_id` 主键链。
- `session/run/step` current snapshot 与 event streams。
- `evaluation/violation/artifact` 的 current snapshot + revisions。
- 关键控制点的最小自动采集。
- `coverage evaluator`、`evaluation generator`、`violation detector`、`audit generator`、`evaluation_summary generator`、`violation_summary generator`。
- publish 前的最小 `source closure` 校验与 published 降级。
- `status --json`、`doctor` 的 telemetry-ready 扩展。
- 最小 manual recording surface，承接 `agent_reported` / `human_reported` 补记。

### Explicitly Out Of Scope For V1 Implementation

- 全量 `file_read` 自动采集。
- 完整开发会话全文采集。
- 复杂 root cause 自动推断。
- improvement proposal 自动生成器。
- 外部 tracing service / remote control plane。
- 跨 session 深度聚合分析与 viewer。

说明：以上只是实现后置，不是模型删除。V1 仍需在 schema、enum、policy、registry 中为后续能力保留位置，不允许为了简化实现而删除未来需要的对象字段或语义槽位。

## Frozen V1 Contract

V1 必须直接继承主设计文档中的以下 contract，不允许降级为“约定即可”：

### Primary Key Chain

- `goal_session_id`
- `workflow_run_id`
- `step_id`
- `event_id`
- `evidence_id`
- `evaluation_id`
- `violation_id`
- `artifact_id`

规则：

- 所有 ID 必须有固定前缀和机器可校验 pattern。
- 所有 ID 全局唯一且不复用。
- 所有 writer 必须走统一 ID 生成器，不允许业务代码拼字符串。

### Scope Model

所有对象必须带 `scope_level`，且校验规则固定：

- `session` 只要求 `goal_session_id`
- `run` 要求 `goal_session_id + workflow_run_id`
- `step` 要求 `goal_session_id + workflow_run_id + step_id`

### Frozen Enums

至少冻结以下 enum：

- `actor_type`
- `capture_mode`
- `confidence`
- `trace_layer`
- `telemetry_event.status`
- `evidence.status`
- `evaluation.result`
- `evaluation.status`
- `violation.status`
- `violation.risk_level`
- `artifact.status`
- `artifact.artifact_type`
- `artifact.artifact_role`
- `artifact.storage_scope`
- `root_cause_class`
- `suggested_change_layer`

### Time Semantics

V1 必须提供满足 RFC3339 UTC `...Z` 格式的时间 helper，不允许继续沿用当前仓库中返回 `+00:00` 的 helper 作为 telemetry canonical timestamp。

固定语义：

- `created_at`: 对象首次落盘时间
- `updated_at`: 最后一次合法修改时间
- `telemetry_event.timestamp`: 事件实际发生时间
- append-only event 的 `updated_at = created_at`

### Mutation Rules

- `telemetry_event`: append-only
- `evidence`: append-only，或仅补 `locator / digest / updated_at`
- `evaluation`: mutable，但状态流转必须写 revisions
- `violation`: mutable，但状态流转必须写 revisions
- `artifact`: mutable，但状态流转必须写 revisions

### Evidence And Source Refs

- `source_ref` 必须按 `source_kind` 语义解释。
- `source_evidence_refs` 与 `source_object_refs` 必须可解析。
- `source_object_refs` 不允许跨 parent chain。
- `published` artifact 不得只依赖 mutable snapshot，必须依赖不可变 evidence 或带 digest 的 blob。

### Current Snapshot + Revisions

V1 必须具备以下最小 revision 语义：

- `evaluation/violation/artifact` 同时拥有 current snapshot 和 `*.revisions.ndjson`
- 每次状态流转先写 revision，再更新 current snapshot
- snapshot 不得删除主键、父链字段、`created_at`

### Parent-Chain Validation

所有 writer 都必须校验：

- `workflow_run_id` 只能属于一个 `goal_session_id`
- `step_id` 只能属于一个 `workflow_run_id`
- 任一 object/evidence/artifact 的父链引用不得跨链
- 跨链写入必须失败，而不是默默重写父链

## Canonical Write Discipline

### Unified Writer API

所有对象型写入只能通过统一 writer API 完成，不允许业务模块直接手写 JSON、NDJSON 或 snapshot 文件。

约束：

- 业务模块可以提交 domain intent，不可以直接写底层文件。
- writer 负责 normalization、ID 分配、timestamp、parent-chain 校验、revision 顺序、source closure 预检查。
- 后续代码评审与 verify 规则应默认把“绕开 writer 直接写文件”视为违约实现。

### Normalization First

contract 校验和 normalization 必须在同一层完成。任何对象在落盘前都要被 canonicalize 到统一形态，而不是“不同模块各自补默认值”。

### Source Ref Resolver

V1 必须有统一的 `source_ref` resolver。不得在 evaluator、publisher、CLI、report generator 中散落多套解析逻辑。

## V1 Governance Generators

V1 的最小治理闭环不是“能生成三种产物”这么粗，而是至少包含以下生成器：

- `coverage evaluator`
- `evaluation generator`
- `violation detector`
- `audit generator`
- `evaluation_summary generator`
- `violation_summary generator`

职责边界如下：

### Coverage Evaluator

- 根据 Critical Control Points Registry 计算控制点覆盖情况。
- 生成 `coverage_gaps`。
- 不直接开 violation，而是先给出 coverage 视角结论。

### Evaluation Generator

- 输入：`telemetry_event(trace_layer=evaluation)` + evidence。
- 输出：`evaluation` 对象。
- 不允许把原始命令输出直接当成 `evaluation` 对象本体。

### Violation Detector

- 基于 evaluation、gate 结果、coverage gap、manual violation report 做升级判断。
- 支持 dedupe/merge。
- `inferred` 不得单独关闭高风险 violation。

### Audit Generator

- 负责按固定优先级计算 `inconclusive > blocked > issues_found > clean`。
- 回答“这次 run/session 的治理结论是什么”。

### Summary Generators

- `evaluation_summary`: 聚合规则/覆盖/证据质量。
- `violation_summary`: 聚合违约状态、风险与 open items。

## Critical Control Points To Auto-Capture In V1

V1 只自动采集以下关键控制点，且名称与 registry 对齐：

- `session_created`
- `workflow_run_started`
- `workflow_run_ended`
- `workflow_step_transitioned`
- `command_completed`
- `patch_applied` 或框架控制的 `file_written`
- `test_result_recorded`
- `gate_hit` / `gate_blocked`
- `audit_report_generated`

其中 `workflow_step_started / transitioned / ended` 的主写入口以调度/状态机层为准。V1 中：

- `runner + dispatcher` 或抽象出的 telemetry runtime facade 负责写 workflow 生命周期事件。
- `executor` 只补 tool 侧事件与 evidence，不重复定义 step 生命周期。

该边界必须在 implementation plan 中继续保持，不允许多个模块重复声明相同 step 生命周期事件。

## Runtime And Evaluation Flow

V1 运行链路如下：

1. CLI/runtime 入口打开 `goal_session`
2. `runner` 创建 `workflow_run`
3. `dispatcher` 驱动 step 生命周期并写 workflow 事件
4. `executor`、CLI 子命令、验证命令写 tool / evaluation 事件与 evidence
5. evaluator 从 evaluation-layer events + evidence 生成 `evaluation`
6. detector 生成或更新 `violation`
7. generator/publisher 输出治理产物

### Evaluation Trace vs Evaluation Object

V1 必须显式区分：

- `telemetry_event(trace_layer=evaluation)`: 评测过程中的行为事件
- `evaluation`: 评测结论对象

例如：

- `doctor`
- `verify constraints --json`
- 测试结果
- gate verdict

都应先形成 evaluation trace event 与相关 evidence，再由 evaluator 生成 `evaluation` 对象。不得直接把命令结果文本落成 `evaluation.json`。

## Source Closure And Publishing

V1 就要带最小 source closure 校验，不能后置到 V1.5。

最小要求：

- artifact 在进入 `published` 前必须执行 source closure 校验
- `source_evidence_refs` / `source_object_refs` 全部必须可解析
- 如来源不可解析、跨链或 evidence 缺失，artifact 不得 `published`
- 来源失效时 artifact 状态应降级为 `reviewed` 或 `draft`

模块命名上，负责这一层的实现应体现其不仅是“写文件”，还承担 publish gating 与 closure 规则。implementation plan 里优先使用 `governance_publisher` 一类命名，而不是含义过窄的通用 `publisher.py`。

## Lazy Init Boundary

V1 支持 telemetry lazy init，但边界固定：

- 只创建最小 telemetry 根目录与 manifest
- 不隐式生成治理产物
- 不修改旧 checkpoint / reconcile 语义
- 不假设仓库是 greenfield 项目

这条是兼容性约束，不允许以“lazy init”名义引入额外状态漂移。

## Owner Boundaries For Planning

implementation plan 必须把 owner boundary 明确成表格，至少覆盖以下责任域：

| owner area | responsibility |
| --- | --- |
| contract/normalization | schema、enum、canonical serialization、timestamp、ID pattern |
| storage/writer | raw trace 路径、writer API、snapshot、revisions、blob、resolver |
| runtime instrumentation | session/run/step 生命周期、tool event、command/test/gate hook |
| evaluator/detector/generator | coverage、evaluation、violation、audit、summary 生成 |
| publisher/source-closure | publish gating、closure 校验、published 降级 |
| CLI/doctor/status | `status --json`、doctor readiness、manual recording surface |
| verification/smoke | positive smoke、negative smoke、compatibility、rebuild 流程 |

## Negative Smoke Set To Freeze In Plan

implementation plan 必须冻结以下最小 negative smoke 集合：

- 跨链 `step/run` 写入被拒绝
- 无法解析的 `source refs` 不能 `published`
- `inferred` 不能单独关闭高风险 violation
- `accepted` 不等于 resolved
- `indexes/` 删除后可 rebuild

## CLI Surface Constraints

### status --json

V1 可以引入 `status --json`，但输出边界必须固定：

- 只暴露 latest/current telemetry summary
- 不扫描所有 blobs
- 不做跨 session 深度聚合
- 不在 status read 时隐式 rebuild indexes

### doctor

V1 的 `doctor` 应从 PATH/venv 诊断扩展为最小 telemetry readiness 检查，但仍保持只读诊断定位。

## Compatibility Constraints

V1 必须兼容当前仓库的旧状态恢复逻辑：

- telemetry 缺失时 lazy init
- 不破坏 `status/recover/reconcile` 现有语义
- 不要求用户手工编辑 checkpoint 来适配 telemetry

## Roadmap After V1

### V1.5

- 完善 dedupe / merge / published 降级细则
- 补强 revision 查询与 artifact index 重建体验

### V2: Human-In-The-Loop Closure

V2 的目标不是“更多 trace”，而是“人机闭环成立”。至少包括：

- `plan_created / plan_updated / plan_abandoned`
- `replan reason`
- `human approval / takeover / correction`
- session-scoped decision events
- 与 `workflow_run` 的归属关系

### V3

- improvement proposal 自动生成
- repeated violation / repeated root cause 聚合
- 更强的自演进治理输入

## Current Repo Anchors

V1 的实现应优先挂接到当前仓库已存在的真实入口：

- [src/ai_sdlc/core/runner.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/runner.py)
- [src/ai_sdlc/core/dispatcher.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/dispatcher.py)
- [src/ai_sdlc/core/executor.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/executor.py)
- [src/ai_sdlc/context/state.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/context/state.py)
- [src/ai_sdlc/cli/commands.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/cli/commands.py)
- [src/ai_sdlc/cli/verify_cmd.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/cli/verify_cmd.py)
- [src/ai_sdlc/cli/doctor_cmd.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/cli/doctor_cmd.py)
- [src/ai_sdlc/core/verify_constraints.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/verify_constraints.py)

说明：`release-check`、merge validation 等 future source 在本仓库当前并无一一对应 CLI 实现。V1 需要保留 adapter/port 语义，但不伪造本仓库不存在的入口。

## Planning Handoff

implementation plan 必须满足以下交接要求：

- 任务拆分到 failing tests、owner boundary、commit slice 级别
- 明确 canonical write path
- 明确 runtime 与 evaluator 的职责分层
- 包含 positive smoke 与 negative smoke
- 包含 upgrade compatibility 和 lazy init 边界
- 使用当前仓库真实文件路径，而不是引用外部计划中的其他仓库结构
