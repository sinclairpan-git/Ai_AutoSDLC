# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Proposal Approval Consumption Baseline

**功能编号**：`061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline`
**创建日期**：2026-04-04
**状态**：已实现（mutation proposal approval consumption baseline）
**输入**：在 `050` 已建立 final proof archive project cleanup baseline、`054` 已冻结 eligibility truth、`056` 已冻结 preview plan truth、`058` 已冻结 mutation proposal truth、`059` 已完成 proposal consumption、`060` 已冻结 proposal approval truth 后，补齐 `ProgramService`、artifact payload 与 CLI 对 `cleanup_mutation_proposal_approval` 的最小消费链路，确保 request/result/report 只消费 formalized approval truth，并继续保持 `deferred` honesty boundary。

**范围**：
- 覆盖 `050` cleanup artifact 中 `cleanup_mutation_proposal_approval` 的读取、校验、透传与结果表达。
- 覆盖 `cleanup_mutation_proposal_approval_state` 的 `missing`、`empty`、`listed` 三态，以及 approval item 与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal` 的对齐消费语义。
- 覆盖 `ProgramService`、artifact payload 与 CLI/report 的 approval state/count 输出与结构性 warning，不改变当前 baseline 不执行真实 cleanup mutation 的事实。

**非范围**：
- 不执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为。
- 不新增 approval-only artifact、execution artifact、旁路 truth 或第二套 canonical approval source。
- 不把 `cleanup_mutation_proposal_approval` 解释成 mutation completion、executor readiness、implicit cleanup authority 或成功执行证明。
- 不通过 `--yes`、reports、`written_paths`、目录结构、working tree 状态或 preview/proposal truth 反推 approval truth。

## 用户场景与测试（必填）

### 用户故事 1 - Project cleanup 只消费 formalized approval truth（优先级：P0）

作为框架维护者，我希望 final proof archive project cleanup 只消费 `050` artifact 中显式声明的 `cleanup_mutation_proposal_approval`，以便后续 execution gating 只建立在单一 truth source 上，而不是从 proposal、preview 或 CLI confirm 旁路推断。

**优先级说明**：如果当前阶段仍然不消费 `cleanup_mutation_proposal_approval`，那么 `060` 冻结的 approval truth 不会进入执行链，后续 child work item 也无法可靠判断哪些 proposal items 已获得显式批准。

**独立测试**：在单元测试中分别构造 approval truth 缺失、空列表、显式列表、非法结构、target 不存在、target 不 eligible、target 未出现在 preview plan、target 未出现在 mutation proposal、`approved_action` 不匹配与缺失必填键等 payload，断言 request/result/artifact payload 与 warning 符合 frozen semantics。

**验收场景**：

1. **Given** `050` cleanup artifact 未提供 `cleanup_mutation_proposal_approval` 字段，**When** 构建 project cleanup request，**Then** 系统必须将 approval truth 识别为 `missing`，并继续保持 `deferred` 基线。
2. **Given** `050` cleanup artifact 提供 `cleanup_mutation_proposal_approval: []` 且 `cleanup_targets: []`，**When** 构建 project cleanup request，**Then** 系统必须将 approval truth 识别为 `empty`，且不得把空列表解释为字段缺失。
3. **Given** `050` cleanup artifact 提供与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal` 对齐的 approval 列表，**When** 构建与执行 project cleanup baseline，**Then** 系统必须原样透传 approval items，并继续返回 `deferred`。

---

### 用户故事 2 - CLI 输出必须暴露 approval gating 语义（优先级：P1）

作为框架操作者，我希望 CLI dry-run / execute 输出与 markdown report 能直接看到 approval truth state 和 approval 数量，以便不打开 artifact 也能判断当前 cleanup baseline 是否已具备 formalized approval truth。

**优先级说明**：CLI 是当前框架操作者的主要入口；如果 terminal output 和 report 不暴露 approval truth，`missing`、`empty`、`listed` 与 invalid alignment 的差异就会被隐藏，后续 handoff 也无法判定 proposal approval 是否已正式进入 truth chain。

**独立测试**：在集成测试中通过 CLI 触发 dry-run 与 execute，断言输出与 report 包含 `cleanup mutation proposal approval state` 以及 approval 数量。

**验收场景**：

1. **Given** `cleanup_mutation_proposal_approval` 缺失，**When** 运行 `program final-proof-archive-project-cleanup`，**Then** 输出必须显式提示 `cleanup mutation proposal approval state: missing`。
2. **Given** `cleanup_mutation_proposal_approval` 为显式列表，**When** 运行执行命令，**Then** 输出必须反映 `listed`，并显示 approval 数量与 `deferred` 结果。

---

### 边界情况

- `cleanup_mutation_proposal_approval` 字段存在但值不是列表时，系统必须视为 invalid truth，而不是自动纠正。
- approval item 缺失 `target_id`、`approved_action` 或 `reason` 时，系统必须暴露结构性 warning，而不是 silently drop。
- approval item 的 `target_id` 若不在 `cleanup_targets` 中、未出现在 `cleanup_preview_plan` 中、未出现在 `cleanup_mutation_proposal` 中、或 eligibility 不是 `eligible`，系统必须保留显式 warning，并继续维持 `deferred` honesty boundary。
- `approved_action` 若与 target `cleanup_action` 或 proposal `proposed_action` 不一致，系统必须暴露 mismatch warning，而不是自动修正。
- `listed` approval truth 只表示 future child work item 可以消费明确的 approval truth，不等于当前 baseline 已允许执行 real cleanup mutation。

## 需求（必填）

### 功能需求

- **FR-061-001**：系统必须只从 `050` final proof archive project cleanup artifact 的 `cleanup_mutation_proposal_approval` 字段读取 approval truth。
- **FR-061-002**：系统必须区分并暴露 `cleanup_mutation_proposal_approval_state` 的 `missing`、`empty`、`listed` 三种状态。
- **FR-061-003**：系统必须在 request/result/artifact payload 中保留显式 approval item 列表，不得基于 CLI confirm、reports、`written_paths`、working tree 状态、preview truth 或 proposal truth 推断补全。
- **FR-061-004**：当 `cleanup_mutation_proposal_approval` 结构非法、entry 缺失必填键、与 `cleanup_targets` 不对齐、引用非 `eligible` target、未出现在 `cleanup_preview_plan`、未出现在 `cleanup_mutation_proposal`、或 `approved_action` 不匹配时，系统必须产出结构性 warning，且不得把 invalid truth 伪装成 real cleanup readiness。
- **FR-061-005**：CLI dry-run、execute 输出与 markdown report 必须暴露 `cleanup_mutation_proposal_approval_state` 与 approval 条目数量，帮助操作者区分 `missing`、`empty`、`listed`。
- **FR-061-006**：即使存在显式 `cleanup_mutation_proposal_approval`，当前 baseline 仍必须保持 `deferred` 结果，不执行真实 workspace cleanup mutation。
- **FR-061-007**：系统必须把 `cleanup_mutation_proposal_approval` 作为 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan` 与 `cleanup_mutation_proposal` 的 sibling truth surface 进行消费，并在 `source_linkage` 中保留 state/path 可追踪信息。
- **FR-061-008**：系统必须将 red-green 测试、实现接线与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体（如涉及数据则必填）

- **CleanupMutationProposalApprovalState**：`missing`、`empty`、`listed` 三态 truth surface，用于表达当前 cleanup artifact 是否具备 formal approval truth。
- **CleanupMutationProposalApprovalEntry**：由 `target_id`、`approved_action`、`reason` 组成的显式 approval 定义，消费层只允许读取与透传，不得扩写隐式字段。
- **ProjectCleanupArtifactPayload**：`050/057/059/061` 链路中的 canonical payload，继续承载 project cleanup request/result/summaries，并新增 approval truth 信息。

## 成功标准（必填）

### 可度量结果

- **SC-061-001**：新增单元测试能够覆盖 `cleanup_mutation_proposal_approval` 的 `missing`、`empty`、`listed` 与 invalid mapping / unknown target / ineligible target / preview mismatch / proposal mismatch / action mismatch 行为，并在实现前先失败、实现后通过。
- **SC-061-002**：`ProgramService` 产出的 request/result/artifact payload 可观测到 `cleanup_mutation_proposal_approval_state` 与显式 approval 列表，且不会从隐式信号推断 approval truth。
- **SC-061-003**：CLI 集成测试验证 dry-run / execute 输出与 report 包含 approval truth state 和 approval 数量。
- **SC-061-004**：`uv run pytest tests/unit/test_program_service.py -q`、`uv run pytest tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 全部通过。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
