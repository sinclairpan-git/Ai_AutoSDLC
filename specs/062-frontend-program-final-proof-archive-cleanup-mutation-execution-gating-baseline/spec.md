# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Execution Gating Baseline

**功能编号**：`062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`](../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md)、[`../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md`](../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md)、[`../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md`](../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md)、[`../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md`](../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md)、[`../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md`](../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md)

> 口径：`062` 不是把 `061` 继续扩张成 real cleanup mutation，而是先冻结“哪些 approved targets 已被显式纳入 future execution handoff”的 canonical truth surface。当前 work item 只定义 `cleanup_mutation_execution_gating` truth、状态边界、对齐约束与接力顺序，不修改 `ProgramService`、CLI 或 tests。

## 问题定义

`060` 已冻结 `cleanup_mutation_proposal_approval` truth，`061` 已将它接入 `ProgramService`、artifact payload 与 CLI 输出，确保 approval truth 成为 single source of truth。但当前链路仍缺一层关键 formal truth：

- 哪些 approved proposal items 已经被显式纳入 future execution gating
- execution gating truth 应以什么最小字段、什么 sibling 位置保留在 `050` cleanup artifact 内
- execution gating truth 应如何与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal`、`cleanup_mutation_proposal_approval` 保持显式对齐
- 在 execution gating truth 未 formalize 前，后续 work item 如何继续保持 `deferred` honesty boundary，而不是把 listed approval 误读成 execution authority

如果不先冻结这一层 truth，后续实现就会出现两类违约：

- 从 `cleanup_mutation_proposal_approval`、CLI confirm、reports、working tree 状态或人工口头结论直接推断 execution gating
- 把 execution gating truth 误写成 real cleanup mutation 指令，跳过后续 service/CLI consumption 与独立 execution child work item

因此，`062` 要解决的是：

- 定义单一的 `cleanup_mutation_execution_gating` canonical truth surface
- 固定 execution gating truth 的总体状态：`missing`、`empty`、`listed`
- 固定 execution gating entry 的最小字段、排序和与 approval/action 的对齐约束
- 固定 execution gating 与 real mutation 的 honesty boundary，以及未来 child work item 的接力顺序

## 范围

- **覆盖**：
  - 将 `cleanup_mutation_execution_gating` 定义为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface
  - 规定 `cleanup_mutation_execution_gating` 只能引用 `cleanup_mutation_proposal_approval` 中已存在的 approved item
  - 定义 execution gating truth 的总体状态语义：`missing`、`empty`、`listed`
  - 定义 execution gating entry 的最小字段、排序与动作一致性约束
  - 规定 execution gating truth 与 real mutation 的边界，以及 future child work item 的接力顺序
- **不覆盖**：
  - 修改 `050`、`054`、`056`、`058`、`060`、`061` 已冻结或已实现的结论
  - 新增第二套 execution gating artifact、旁路 gate artifact 或独立 executor artifact
  - 执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为
  - 修改 `src/ai_sdlc/core/program_service.py`
  - 修改 `src/ai_sdlc/cli/program_cmd.py`
  - 修改 `tests/unit/test_program_service.py`
  - 修改 `tests/integration/test_cli_program.py`
  - 通过 `cleanup_mutation_proposal_approval`、CLI confirm、reports、`written_paths`、目录命名、工作树状态或 operator 口头输入自动推断 execution gating

## 已锁定决策

- `cleanup_mutation_execution_gating` 必须作为 `050` cleanup artifact 的 sibling 字段进入单一 truth source
- `cleanup_mutation_execution_gating` 必须是有序列表；当为 `listed` 时，列表顺序必须与其所引用 approved items 在 `cleanup_mutation_proposal_approval` 中的原始顺序一致
- execution gating truth 的总体状态只允许 `missing`、`empty`、`listed`
- `cleanup_mutation_execution_gating` 允许是 `cleanup_mutation_proposal_approval` 的显式子集；它不要求覆盖全部 approved items
- 每个 execution gating entry 必须通过 `target_id` 指向一个已存在的 approved item，并且该 target 必须继续存在于 `cleanup_targets`
- 每个 execution gating entry 的 `gated_action` 必须同时与 approval `approved_action`、proposal `proposed_action`、preview `planned_action` 以及 target `cleanup_action` 完全一致
- `listed` execution gating truth 只表示“future child work item 可消费显式 execution gating truth”，不等于 mutation 已执行、已完成或已验证成功
- 若 `cleanup_mutation_execution_gating` 缺失，后续 work item 必须继续保持 `deferred`，不得自行把 listed approval 视为已进入 execution
- `062` 当前阶段只允许修改 `specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/` 内文档与脚手架自动更新的 project state

## Cleanup Mutation Execution Gating Canonical Truth

`cleanup_mutation_execution_gating` 定义为与 targets / eligibility / preview / proposal / approval 对齐的显式 execution gating 列表：

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
    reason: target may proceed into formal cleanup planning truth

cleanup_preview_plan:
  - target_id: cleanup-thread-archive-report
    planned_action: archive_or_remove
    reason: preview only; mutation remains deferred

cleanup_mutation_proposal:
  - target_id: cleanup-thread-archive-report
    proposed_action: archive_or_remove
    reason: proposal prepared for explicit operator review

cleanup_mutation_proposal_approval:
  - target_id: cleanup-thread-archive-report
    approved_action: archive_or_remove
    reason: explicitly approved for future execution gating consumption

cleanup_mutation_execution_gating:
  - target_id: cleanup-thread-archive-report
    gated_action: archive_or_remove
    reason: explicitly admitted into future execution consumption truth
```

### 每个 execution gating entry 的必填字段

| 字段 | 含义 |
|------|------|
| `target_id` | 指向 `cleanup_mutation_proposal_approval` 中现有 approved 条目的稳定标识 |
| `gated_action` | 与 approval `approved_action` 及其上游 sibling action 完全一致的 execution gating 动作 |
| `reason` | 简短、可审计的 gating 说明，明确它仍是 execution gating truth 而不是 mutation result |

### 约束

- `cleanup_mutation_execution_gating` 缺失表示“execution gating truth 尚未 formalize”
- `cleanup_mutation_execution_gating: []` 表示“execution gating truth 已 formalize，但当前没有 approved item 被显式纳入 future execution gating”
- 当 `cleanup_mutation_execution_gating` 为非空列表时，列表中的每个 `target_id` 必须存在于 `cleanup_mutation_proposal_approval`
- 列表中的每个 `target_id` 必须继续存在于 `cleanup_targets`，且该 target 在 `cleanup_target_eligibility` 中必须保持 `eligible`
- 列表中的每个 `target_id` 必须与 `cleanup_preview_plan`、`cleanup_mutation_proposal` 中已声明的 item 对齐
- 同一列表内不得出现重复 `target_id`
- `gated_action` 必须等于 approval `approved_action`，并且等于 proposal `proposed_action`、preview `planned_action` 与 target `cleanup_action`
- `cleanup_mutation_execution_gating` 不得引入 `cleanup_mutation_proposal_approval` 中不存在的 target
- `listed` execution gating truth 不得被解释成 mutation side effect；未来实现仍必须经过独立 execution gating consumption 与 separate execution child work item
- 若结构非法、目标不对齐、动作不一致或原因缺失，未来实现必须将其视为 invalid truth，而不是自动纠正

## 用户故事与验收

### US-062-1 - Framework Maintainer 需要单一 execution gating truth（优先级：P0）

作为 **框架维护者**，我希望 cleanup mutation execution gating 被正式定义为 `050` artifact 内的 sibling truth surface，以便后续 execution consumption 和 mutation child work item 都消费同一 truth，而不是从 approval list 或 CLI confirm 推断。

**优先级说明**：如果 execution gating truth 不先冻结，`061` 之后的链路就会重新发明“哪些 approved items 真正进入 execution handoff”，直接破坏 `050 -> 054 -> 056 -> 058 -> 060 -> 061` 的单一 truth chain。

**独立测试**：审阅 `062` formal docs，确认 `cleanup_mutation_execution_gating` 的位置、字段、状态和 non-goals 被明确锁定，并通过只读约束校验。

**验收场景**：

1. **Given** 我阅读 `062` formal docs，**When** 我查找 execution gating truth 的位置，**Then** 我能明确看到它属于 `050` cleanup artifact，而不是新的 execution artifact。
2. **Given** 我检查 execution gating entry 结构，**When** 我确认最小字段，**Then** 我只能看到 `target_id`、`gated_action`、`reason` 这组字段。

---

### US-062-2 - Reviewer 需要阻止 inferred execution gating（优先级：P0）

作为 **reviewer**，我希望 `062` 明确禁止通过 `cleanup_mutation_proposal_approval`、CLI confirm、reports、`written_paths` 或 working tree 状态推断 execution gating，以便未来实现只能消费显式 formalized execution gating truth。

**优先级说明**：如果 execution gating 仍然允许由实现层或操作流程隐式给出，approval truth 与 real mutation 之间就会失去审计边界，review 无法判断 cleanup side effect 是否越权。

**独立测试**：审阅 `062` 的范围、已锁定决策与约束，确认 inferred execution gating 被明确禁止。

**验收场景**：

1. **Given** 我阅读 `062`，**When** 我确认 execution gating 来源，**Then** 我只能看到 `cleanup_mutation_execution_gating` 与 targets/eligibility/preview/proposal/approval 的显式对齐关系。
2. **Given** 我评审后续实现，**When** 我查找 non-goals，**Then** 我能明确看到 CLI confirm、reports、deliverables、`written_paths` 与 working tree 状态都不能直接视为 execution gating。

---

### US-062-3 - 后续子项执行者需要稳定的 execution handoff（优先级：P1）

作为 **后续子项执行者**，我希望 `062` 明确 execution gating truth 的状态语义和接力顺序，以便我先写 execution gating consumption 的 failing tests，再进入 service/CLI 消费，而不是直接跳到 real cleanup mutation。

**优先级说明**：当前阶段最容易犯的错误就是把 `listed` execution gating 误读成“已经可以执行 cleanup”；必须先把 execution gating truth 与 real mutation 明确分离。

**独立测试**：审阅 `062` 成功标准和已锁定决策，确认 future child work item 的顺序被固定为 `failing tests -> service/CLI execution gating consumption -> separate execution child work item`。

**验收场景**：

1. **Given** `cleanup_mutation_execution_gating` 缺失，**When** 我继续后续 work item，**Then** 我能明确知道必须继续保持 `deferred`，不得把 listed approval 直接视为 execution authority。
2. **Given** 某个 target 出现在 `cleanup_mutation_execution_gating` 中，**When** 我规划后续实现，**Then** 我能明确知道这只允许进入 execution gating consumption truth，而不等于 mutation 已被执行。

## 需求

### 功能需求

- **FR-062-001**：系统必须将 `cleanup_mutation_execution_gating` 定义为 `050` final proof archive project cleanup artifact 的 sibling truth surface。
- **FR-062-002**：系统必须规定 `cleanup_mutation_execution_gating` 只能引用 `cleanup_mutation_proposal_approval` 中已存在的 approved item。
- **FR-062-003**：系统必须将 execution gating truth 的总体状态固定为 `missing`、`empty`、`listed` 三种。
- **FR-062-004**：系统必须规定每个 execution gating entry 的必填字段为 `target_id`、`gated_action`、`reason`。
- **FR-062-005**：系统必须规定 `gated_action` 同时与 approval `approved_action`、proposal `proposed_action`、preview `planned_action` 以及 target `cleanup_action` 保持完全一致。
- **FR-062-006**：系统必须规定 `cleanup_mutation_execution_gating` 可作为 approval truth 的显式子集存在，不要求覆盖全部 approved items。
- **FR-062-007**：系统必须禁止通过 `cleanup_mutation_proposal_approval`、CLI confirm、reports、deliverables、`written_paths`、目录命名或 working tree 状态推断 execution gating。
- **FR-062-008**：系统必须明确 `listed` execution gating truth 不等于 mutation 已执行，而只表示 future child work item 可进入 execution gating consumption / execution handoff。
- **FR-062-009**：系统必须保持 docs-only 范围，不修改 `src/` 或 `tests/`。
- **FR-062-010**：系统必须要求 future child work item 先写 failing tests 固定 execution gating truth consumption，再进入 service/CLI，再进入 separate execution child work item。
- **FR-062-011**：系统必须将脚手架生成、formal docs 重写与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体

- **Cleanup Mutation Execution Gating**：`050` cleanup artifact 内、与 `cleanup_mutation_proposal_approval` 并列的 canonical execution gating truth 列表。
- **Execution Gating Entry**：描述单个 approved proposal target 是否被显式纳入 future execution consumption truth 的 canonical 对象。
- **Execution Gating Truth State**：`missing`、`empty`、`listed` 三种总体状态，用于表达 execution gating truth 是否已 formalize。

## 成功标准

### 可度量结果

- **SC-062-001**：formal docs 明确把 `cleanup_mutation_execution_gating` 固定为 `050` cleanup artifact 的 sibling truth surface。
- **SC-062-002**：formal docs 明确列出 execution gating entry 的最小字段、状态语义以及与 targets/eligibility/preview/proposal/approval truth 的对齐约束。
- **SC-062-003**：formal docs 明确禁止 inferred execution gating，并继续保持 `050` 的 `deferred` honesty boundary。
- **SC-062-004**：formal docs 明确 future child work item 的顺序为 `failing tests -> service/CLI execution gating consumption -> separate execution child work item`。
- **SC-062-005**：`task-execution-log.md` 追加记录脚手架、边界冻结与 focused verification 结果。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
