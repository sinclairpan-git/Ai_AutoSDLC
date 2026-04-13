# 功能规格：Frontend Program Final Proof Archive Project Cleanup Preview Plan Baseline

**功能编号**：`056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`](../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md)、[`../055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md`](../055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline/spec.md)

> 口径：`056` 不是把 `055` 继续扩张成 real cleanup mutation，而是先冻结“显式 preview plan 应该以什么 canonical truth 形态存在”的 formal baseline。当前 work item 只定义 `cleanup_preview_plan` truth、状态边界、对齐约束与后续接力顺序，不修改 `ProgramService`、CLI 或 tests。

## 问题定义

`055` 已经把 `cleanup_target_eligibility` 接入 `ProgramService` 与 CLI，使系统能够诚实表达哪些 explicit cleanup targets 是 `eligible`、哪些是 `blocked`。但当前链路仍缺一层关键真值：

- 哪些 `eligible` targets 应进入 operator-facing preview plan
- preview plan 内每个条目应以什么最小字段表示
- preview plan 应如何与 `cleanup_targets`、`cleanup_target_eligibility` 保持一一对齐
- 在 preview plan truth 尚未 formalize 前，后续 work item 如何避免从 eligibility 或 target truth 直接推断计划

如果不先冻结这层 truth，后续实现就会出现两类框架违约：

- 从 `cleanup_targets` 或 `cleanup_target_eligibility` 直接推导“计划步骤”，绕开单一 truth source
- 把 preview plan 误写成 real cleanup mutation proposal，破坏 `050` 和 `051` 已锁定的 `deferred` / no-mutation 边界

因此，`056` 要解决的是：

- 定义单一的 `cleanup_preview_plan` canonical truth surface
- 固定它与 `cleanup_targets` / `cleanup_target_eligibility` 的对齐关系
- 固定 preview plan truth 的总体状态：`missing`、`empty`、`listed`
- 固定单条 preview item 的最小字段、排序和合法性约束
- 为未来 child work item 固定接力顺序：先 failing tests，再 service/CLI 消费，再考虑 mutation proposal / real execution

## 范围

- **覆盖**：
  - 将 `cleanup_preview_plan` 定义为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface
  - 规定 `cleanup_preview_plan` 只能引用 `cleanup_targets` 中已存在、且在 `cleanup_target_eligibility` 中标记为 `eligible` 的 target
  - 定义 preview plan truth 的总体状态语义：`missing`、`empty`、`listed`
  - 定义 preview item 的最小字段、排序和与 `cleanup_action` 的一致性约束
  - 规定 future child work item 的接力顺序与 non-goals
- **不覆盖**：
  - 修改 `050`、`051`、`054`、`055` 已冻结或已实现的结论
  - 新增第二套 preview artifact、旁路 plan artifact 或独立 cleanup mutation proposal artifact
  - 执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为
  - 修改 `src/ai_sdlc/core/program_service.py`
  - 修改 `src/ai_sdlc/cli/program_cmd.py`
  - 修改 `tests/unit/test_program_service.py`
  - 修改 `tests/integration/test_cli_program.py`
  - 通过 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名、工作树状态或 `eligible` 标记自动推断 preview plan

## 已锁定决策

- `cleanup_preview_plan` 必须作为 `050` cleanup artifact 的 sibling 字段进入单一 truth source
- `cleanup_preview_plan` 必须是有序列表，顺序必须与其所引用的 `cleanup_targets` 原始顺序一致
- 每个 preview item 必须通过 `target_id` 指向一个已存在的 `cleanup_targets` entry，且该 target 在 `cleanup_target_eligibility` 中必须为 `eligible`
- preview plan truth 的总体状态只允许 `missing`、`empty`、`listed`
- 单个 preview item 的最小字段只允许 `target_id`、`planned_action`、`reason`
- `planned_action` 必须与所引用 target 的 `cleanup_action` 完全一致，不允许在 preview plan 中发明新动作
- `cleanup_preview_plan` 缺失表示“preview plan truth 尚未 formalize”，future child work item 不得自行推断
- `cleanup_preview_plan: []` 只表示“preview plan truth 已 formalize，且当前没有可展示的 preview item”；不得把空列表解释为字段缺失
- `listed` preview plan 只表示“未来 child work item 可以消费明确的 preview planning truth”，不等于当前 baseline 已允许执行 mutation
- `056` 当前阶段只允许修改 `specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/` 内文档与脚手架自动更新的 project state

## Cleanup Preview Plan Canonical Truth

`cleanup_preview_plan` 定义为与 `cleanup_targets` / `cleanup_target_eligibility` 对齐的显式 preview 列表：

```yaml
cleanup_targets:
  - target_id: cleanup-thread-archive-report
    path: .ai-sdlc/reports/program/final-proof-archive/thread-archive/example.md
    target_kind: file
    cleanup_action: archive_or_remove
    source_artifact: final-proof-archive-project-cleanup
    justification: superseded by canonical final proof archive artifact

cleanup_target_eligibility:
  - target_id: cleanup-thread-archive-report
    eligibility: eligible
    reason: target may proceed into preview planning truth

cleanup_preview_plan:
  - target_id: cleanup-thread-archive-report
    planned_action: archive_or_remove
    reason: preview only; mutation remains deferred until a future approved child item
```

### 每个 preview item 的必填字段

| 字段 | 含义 |
|------|------|
| `target_id` | 指向 `cleanup_targets` 中现有条目的稳定标识 |
| `planned_action` | 与目标条目的 `cleanup_action` 完全一致的 preview 动作 |
| `reason` | 简短、可审计的 preview 说明，明确该条目仍处于 preview truth |

### 约束

- `cleanup_preview_plan` 缺失表示“preview plan truth 尚未 formalize”
- `cleanup_preview_plan: []` 允许出现在 `cleanup_targets` 为空，或所有 target 都不是 `eligible` 的场景
- 当 `cleanup_preview_plan` 为非空列表时，列表中的每个 `target_id` 必须存在于 `cleanup_targets`
- 列表中的每个 `target_id` 必须在 `cleanup_target_eligibility` 中被标记为 `eligible`
- 同一列表内不得出现重复 `target_id`
- `cleanup_preview_plan` 不得引入 `cleanup_targets` 中不存在的 target
- `cleanup_preview_plan` 不得包含 `blocked` target
- `planned_action` 必须等于所引用 target 的 `cleanup_action`
- 若存在 `eligible` target 但 `cleanup_preview_plan` 仍缺失，future child work item 必须把它视为 truth 缺失，而不是自动补全
- 若结构非法、目标不对齐、动作不一致或原因缺失，未来实现必须将其视为 invalid truth，而不是自动纠正

## 用户故事与验收

### US-056-1 — Framework Maintainer 需要单一 preview planning truth（优先级：P0）

作为 **框架维护者**，我希望 cleanup preview plan 被正式定义为 `050` artifact 内的 sibling truth surface，以便后续 work item 不会从 `cleanup_targets` / `cleanup_target_eligibility` 旁路推导计划步骤。

**优先级说明**：如果 preview plan truth 不先冻结，后续 CLI/service/mutation 子项就会重新发明“要展示哪些计划项”，直接破坏 `050 -> 054 -> 055` 的单一 truth chain。

**独立测试**：审阅 `056` formal docs，确认 `cleanup_preview_plan` 的位置、字段、状态与 non-goals 被明确锁定，并通过只读约束校验。

**验收场景**：

1. **Given** 我阅读 `056` formal docs，**When** 我查找 preview plan truth 的位置，**Then** 我能明确看到它属于 `050` cleanup artifact，而不是新 artifact。
2. **Given** 我检查 preview item 结构，**When** 我确认最小字段，**Then** 我只能看到 `target_id`、`planned_action`、`reason` 这组字段。

---

### US-056-2 — Reviewer 需要阻止从 eligibility truth 推断 preview plan（优先级：P0）

作为 **reviewer**，我希望 `056` 明确禁止通过 `cleanup_targets`、`cleanup_target_eligibility`、reports、`written_paths` 或工作树状态推断 preview plan，以便未来实现只能消费 formalized preview truth。

**优先级说明**：如果 preview plan 仍允许通过 eligibility truth 隐式生成，`054/055` 冻结和实现的边界就会被绕过，review 也无法判断操作者看到的 preview 是否来自单一真值。

**独立测试**：审阅 `056` 的范围、已锁定决策与约束，确认 inferred preview plan 被明确禁止。

**验收场景**：

1. **Given** 我阅读 `056`，**When** 我确认 preview 来源，**Then** 我只能看到 `cleanup_preview_plan` 与 `cleanup_targets` / `cleanup_target_eligibility` 的显式映射。
2. **Given** 我评审后续实现，**When** 我查找 non-goals，**Then** 我能明确看到 `.ai-sdlc/`、reports、deliverables、`written_paths`、working tree 状态与 `eligible` 标记都不能被直接用来推断 preview item。

---

### US-056-3 — 后续子项执行者需要稳定的 preview handoff（优先级：P1）

作为 **后续子项执行者**，我希望 `056` 明确 preview plan truth 的状态语义和接力顺序，以便我能先写 failing tests，再决定 service/CLI 消费，而不是直接跳到 real cleanup mutation。

**优先级说明**：当前阶段最容易出现的错误是把 `listed` preview plan 误读成“已经批准删除/移动”；必须先把 preview truth 与 execution truth 分开冻结。

**独立测试**：审阅 `056` 成功标准与已锁定决策，确认 future work item 的顺序被固定为 `failing tests -> service/CLI preview consumption -> mutation proposal / execution`。

**验收场景**：

1. **Given** `cleanup_preview_plan` 缺失，**When** 我继续后续 work item，**Then** 我能明确知道必须继续保持 truth 缺失，而不是从 `eligible` target 自动生成 preview。
2. **Given** 某个 target 出现在 `cleanup_preview_plan` 中，**When** 我规划后续实现，**Then** 我能明确知道这只允许进入 preview plan consumption，而不等于 mutation 已被批准。

## 需求

### 功能需求

- **FR-056-001**：系统必须将 `cleanup_preview_plan` 定义为 `050` final proof archive project cleanup artifact 的 sibling truth surface。
- **FR-056-002**：系统必须规定 `cleanup_preview_plan` 只能引用 `cleanup_targets` 中存在且在 `cleanup_target_eligibility` 中标记为 `eligible` 的 target。
- **FR-056-003**：系统必须将 preview plan truth 的总体状态固定为 `missing`、`empty`、`listed` 三种。
- **FR-056-004**：系统必须规定每个 preview item 的必填字段为 `target_id`、`planned_action`、`reason`。
- **FR-056-005**：系统必须规定 `planned_action` 与所引用 target 的 `cleanup_action` 保持完全一致。
- **FR-056-006**：系统必须禁止通过 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名、工作树状态或 `eligible` 标记推断 preview plan。
- **FR-056-007**：系统必须明确 `cleanup_preview_plan` 的 `listed` 只代表 preview planning truth 已 formalize，不代表当前 baseline 已允许执行 mutation。
- **FR-056-008**：系统必须保持 docs-only 范围，不修改 `src/` 或 `tests/`。
- **FR-056-009**：系统必须要求 future child work item 先写 failing tests 固定 preview plan consumption，再进入 service/CLI，再考虑 mutation proposal 或 real execution。
- **FR-056-010**：系统必须将脚手架生成、formal docs 重写与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体

- **Cleanup Preview Plan**：`050` cleanup artifact 内、与 `cleanup_targets` / `cleanup_target_eligibility` 并列的 canonical preview truth 列表。
- **Preview Plan Item**：描述单个 cleanup target 在 preview 阶段应显示什么动作与原因的显式真值对象。
- **Preview Plan Truth State**：`missing`、`empty`、`listed` 三种总体状态，用于表达 preview planning truth 是否已 formalize。

## 成功标准

### 可度量结果

- **SC-056-001**：formal docs 明确把 `cleanup_preview_plan` 固定为 `050` cleanup artifact 的 sibling truth surface。
- **SC-056-002**：formal docs 明确列出 preview item 的最小字段、状态语义和与 eligibility/target truth 的对齐约束。
- **SC-056-003**：formal docs 明确禁止 inferred preview plan，并继续保持 `050/051` 的 no-mutation 边界。
- **SC-056-004**：formal docs 明确 future child work item 的顺序为 `failing tests -> service/CLI preview consumption -> mutation proposal / execution`。
- **SC-056-005**：`task-execution-log.md` 追加记录脚手架、边界冻结与 focused verification 结果。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
