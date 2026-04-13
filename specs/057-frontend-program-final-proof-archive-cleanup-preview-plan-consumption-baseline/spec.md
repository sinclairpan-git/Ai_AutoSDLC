# 功能规格：Frontend Program Final Proof Archive Cleanup Preview Plan Consumption Baseline

**功能编号**：`057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline`
**创建日期**：2026-04-04
**状态**：已实现（preview plan consumption baseline）
**输入**：在 `050` 已建立 final proof archive project cleanup baseline、`055` 已将 `cleanup_target_eligibility` 接入 `ProgramService` 与 CLI、`056` 已冻结 `cleanup_preview_plan` canonical truth surface 后，补齐 service/CLI 对 preview plan truth 的消费基线，确保 request/result/artifact/terminal output 均只消费 formalized preview truth，并继续保持 `deferred` honesty boundary。

**范围**：
- 覆盖 `050` cleanup artifact 中 `cleanup_preview_plan` 的读取、校验、透传与结果表达。
- 覆盖 preview plan truth 的 `missing`、`empty`、`listed` 三态，以及 preview item 与 `cleanup_targets` / `cleanup_target_eligibility` 的对齐消费语义。
- 覆盖 `ProgramService` 与 CLI 的 preview-plan state/count 输出与结构性警告，不改变当前 baseline 不执行真实 cleanup mutation 的事实。

**非范围**：
- 不执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为。
- 不新增 preview-only artifact、旁路 plan artifact 或第二套 preview truth。
- 不通过 `written_paths`、reports、目录结构、working tree 状态或 `eligible` truth 推断 preview plan。
- 不把 `listed` preview plan 解释成“已经允许 real cleanup”。

## 用户场景与测试（必填）

### 用户故事 1 - Project cleanup 只消费 formalized preview plan truth（优先级：P0）

作为框架维护者，我希望 final proof archive project cleanup 只消费 `050` artifact 中显式声明的 `cleanup_preview_plan`，以便后续 planning/mutation work 始终建立在单一 truth source 上，而不是从 eligibility truth 旁路推断。

**优先级说明**：如果当前阶段仍然不消费 `cleanup_preview_plan`，那么 `056` 冻结的 preview truth 不会进入执行链，后续 child work item 也无法可靠判断 operator-facing preview 到底来自 formal truth 还是隐式推导。

**独立测试**：在单元测试中分别构造 preview plan truth 缺失、空列表、显式列表、非法结构、target 对不齐、blocked target、planned action 不匹配与缺失必填键等 payload，断言 request/result/artifact payload 与警告信息符合 frozen semantics。

**验收场景**：

1. **Given** `050` cleanup artifact 未提供 `cleanup_preview_plan` 字段，**When** 构建 project cleanup request，**Then** 系统必须将 preview truth 识别为 `missing`，并继续保持 `deferred` 基线。
2. **Given** `050` cleanup artifact 提供 `cleanup_preview_plan: []` 且 `cleanup_targets: []`，**When** 构建 project cleanup request，**Then** 系统必须将 preview truth 识别为 `empty`，且不得把空列表解释为字段缺失。
3. **Given** `050` cleanup artifact 提供与 `cleanup_targets` / `cleanup_target_eligibility` 对齐的 preview 列表，**When** 构建与执行 project cleanup baseline，**Then** 系统必须原样透传 preview items，并继续返回 `deferred`。

---

### 用户故事 2 - CLI 输出必须暴露 preview plan gating 语义（优先级：P1）

作为框架操作者，我希望 CLI dry-run / execute 输出能直接看到 preview plan truth state 和 preview item 数量，以便不打开 artifact 也能判断当前 cleanup baseline 是否已具备 formalized preview planning truth。

**优先级说明**：CLI 是当前框架操作者的主要入口；如果 terminal output 不暴露 preview truth，`missing` 与 `empty`、`listed` 与 invalid mapping 的差异就会被隐藏，后续 handoff 也无法判定。

**独立测试**：在集成测试中通过 CLI 触发 dry-run 与 execute，断言输出与 report 包含 `cleanup preview plan state` 以及 preview item 数量。

**验收场景**：

1. **Given** `cleanup_preview_plan` 缺失，**When** 运行 `program final-proof-archive-project-cleanup`，**Then** 输出必须显式提示 `cleanup preview plan state: missing`。
2. **Given** `cleanup_preview_plan` 为显式列表，**When** 运行执行命令，**Then** 输出必须反映 `listed`，并显示 preview item 数量与 `deferred` 结果。

---

### 边界情况

- `cleanup_preview_plan` 字段存在但值不是列表时，系统必须视为 invalid truth，而不是自动纠正。
- preview item 缺失 `target_id`、`planned_action` 或 `reason` 时，系统必须暴露结构性警告，而不是 silently drop。
- `cleanup_preview_plan` 中的 `target_id` 若不在 `cleanup_targets` 中，系统必须保留显式 warning，并继续维持 `deferred` honesty boundary。
- `cleanup_preview_plan` 中若引用 `blocked` target 或 `planned_action` 与 target `cleanup_action` 不一致，系统必须暴露结构性 warning，而不是自动修正。
- `listed` preview plan 只表示 future child work item 可以消费明确的 preview truth，不等于当前 baseline 已允许执行 mutation。

## 需求（必填）

### 功能需求

- **FR-057-001**：系统必须只从 `050` final proof archive project cleanup artifact 的 `cleanup_preview_plan` 字段读取 preview truth。
- **FR-057-002**：系统必须区分并暴露 `cleanup_preview_plan_state` 的 `missing`、`empty`、`listed` 三种状态。
- **FR-057-003**：系统必须在 request/result/artifact payload 中保留显式 preview item 列表，不得基于目录命名、`written_paths`、reports、working tree 状态或 `eligible` 资格推断补全。
- **FR-057-004**：当 `cleanup_preview_plan` 结构非法、entry 缺失必填键、与 `cleanup_targets` 不对齐、引用 `blocked` target 或 `planned_action` 不匹配时，系统必须产出结构性警告，且不得把 invalid truth 伪装成 real cleanup readiness。
- **FR-057-005**：CLI dry-run 与 execute 输出必须暴露 `cleanup_preview_plan_state` 与 preview item 条目数量，帮助操作者区分 `missing`、`empty`、`listed`。
- **FR-057-006**：即使存在显式 `cleanup_preview_plan`，当前 baseline 仍必须保持 `deferred` 结果，不执行真实 workspace cleanup mutation。
- **FR-057-007**：系统必须把 `cleanup_preview_plan` 作为 `cleanup_targets` 与 `cleanup_target_eligibility` 的 sibling truth surface 进行消费，并在 `source_linkage` 中保留 state/path 可追踪信息。
- **FR-057-008**：系统必须将脚手架、red-green 测试、实现接线与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体（如涉及数据则必填）

- **CleanupPreviewPlanState**：`missing`、`empty`、`listed` 三态 truth surface，用于表达当前 cleanup artifact 是否具备 formal preview planning truth。
- **CleanupPreviewPlanEntry**：由 `target_id`、`planned_action`、`reason` 组成的显式 preview 定义，消费层只允许读取与透传，不得扩写隐式字段。
- **ProjectCleanupArtifactPayload**：`050/055/057` 链路中的 canonical payload，继续承载 project cleanup request/result/summaries，并新增 preview truth 信息。

## 成功标准（必填）

### 可度量结果

- **SC-057-001**：新增单元测试能够覆盖 `cleanup_preview_plan` 的 `missing`、`empty`、`listed` 与 invalid mapping / blocked target / action mismatch 行为，并在实现前先失败、实现后通过。
- **SC-057-002**：`ProgramService` 产出的 request/result/artifact payload 可观测到 `cleanup_preview_plan_state` 与显式 preview item 列表，且不会从隐式信号推断 preview truth。
- **SC-057-003**：CLI 集成测试验证 dry-run / execute 输出与 report 包含 preview plan truth state 和 preview item 数量。
- **SC-057-004**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 全部通过。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
