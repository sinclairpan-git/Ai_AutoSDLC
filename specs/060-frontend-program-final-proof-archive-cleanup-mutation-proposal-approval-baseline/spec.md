# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Proposal Approval Baseline

**功能编号**：`060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`](../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md)、[`../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md`](../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md)、[`../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md`](../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md)、[`../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md`](../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md)

> 口径：`060` 不是把 `059` 继续扩张成 real cleanup mutation，而是先冻结“哪些 proposal items 获得了显式 approval/gating truth”的 canonical truth surface。当前 work item 只定义 `cleanup_mutation_proposal_approval` truth、状态边界、对齐约束与接力顺序，不修改 `ProgramService`、CLI 或 tests。

## 问题定义

`058` 已冻结 `cleanup_mutation_proposal` truth，`059` 已将它接入 `ProgramService`、artifact payload 与 CLI 输出，确保 proposal truth 成为 single source of truth。但当前链路仍缺一层关键 formal truth：

- 哪些 proposal items 已经获得显式批准，可以进入未来 execution gating
- approval truth 应以什么最小字段、什么 sibling 位置保留在 `050` cleanup artifact 内
- approval truth 应如何与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal` 保持显式对齐
- 在 approval truth 未 formalize 前，后续 work item 如何继续保持 `deferred` honesty boundary，而不是把 listed proposal 误读成 execution authority

如果不先冻结这一层 truth，后续实现就会出现两类违约：

- 从 `cleanup_mutation_proposal`、CLI confirm、reports、working tree 状态或人工口头结论直接推断 approval
- 把 approval truth 误写成 execution 指令，跳过后续 service/CLI consumption 与独立 execution child work item

因此，`060` 要解决的是：

- 定义单一的 `cleanup_mutation_proposal_approval` canonical truth surface
- 固定 approval truth 的总体状态：`missing`、`empty`、`listed`
- 固定 approval entry 的最小字段、排序和与 proposal/action 的对齐约束
- 固定 approval 与 execution 的 honesty boundary，以及未来 child work item 的接力顺序

## 范围

- **覆盖**：
  - 将 `cleanup_mutation_proposal_approval` 定义为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface
  - 规定 `cleanup_mutation_proposal_approval` 只能引用 `cleanup_mutation_proposal` 中已存在的 proposal item
  - 定义 approval truth 的总体状态语义：`missing`、`empty`、`listed`
  - 定义 approval entry 的最小字段、排序与动作一致性约束
  - 规定 approval truth 与 execution truth 的边界，以及 future child work item 的接力顺序
- **不覆盖**：
  - 修改 `050`、`054`、`056`、`058`、`059` 已冻结或已实现的结论
  - 新增第二套 approval artifact、旁路 gate artifact 或独立 execution artifact
  - 执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为
  - 修改 `src/ai_sdlc/core/program_service.py`
  - 修改 `src/ai_sdlc/cli/program_cmd.py`
  - 修改 `tests/unit/test_program_service.py`
  - 修改 `tests/integration/test_cli_program.py`
  - 通过 `cleanup_mutation_proposal`、CLI confirm、reports、`written_paths`、目录命名、工作树状态或 operator 口头输入自动推断 approval

## 已锁定决策

- `cleanup_mutation_proposal_approval` 必须作为 `050` cleanup artifact 的 sibling 字段进入单一 truth source
- `cleanup_mutation_proposal_approval` 必须是有序列表；当为 `listed` 时，列表顺序必须与其所引用 proposal items 在 `cleanup_mutation_proposal` 中的原始顺序一致
- approval truth 的总体状态只允许 `missing`、`empty`、`listed`
- `cleanup_mutation_proposal_approval` 允许是 `cleanup_mutation_proposal` 的显式子集；它不要求覆盖全部 proposal items
- 每个 approval entry 必须通过 `target_id` 指向一个已存在的 proposal item，并且该 target 必须继续存在于 `cleanup_targets`
- 每个 approval entry 的 `approved_action` 必须同时与 proposal `proposed_action` 以及 target `cleanup_action` 完全一致
- `listed` approval truth 只表示“future child work item 可消费显式 approval/gating truth”，不等于 mutation 已执行、已完成或已验证成功
- 若 `cleanup_mutation_proposal_approval` 缺失，后续 work item 必须继续保持 `deferred`，不得自行把 listed proposal 视为 approved
- `060` 当前阶段只允许修改 `specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/` 内文档与脚手架自动更新的 project state

## Cleanup Mutation Proposal Approval Canonical Truth

`cleanup_mutation_proposal_approval` 定义为与 `cleanup_mutation_proposal` 对齐的显式 approval 列表：

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
```

### 每个 approval entry 的必填字段

| 字段 | 含义 |
|------|------|
| `target_id` | 指向 `cleanup_mutation_proposal` 中现有 proposal 条目的稳定标识 |
| `approved_action` | 与 proposal `proposed_action` 及 target `cleanup_action` 完全一致的批准动作 |
| `reason` | 简短、可审计的批准说明，明确它仍是 approval truth 而不是 execution result |

### 约束

- `cleanup_mutation_proposal_approval` 缺失表示“approval truth 尚未 formalize”
- `cleanup_mutation_proposal_approval: []` 表示“approval truth 已 formalize，但当前没有 proposal item 获得显式批准”
- 当 `cleanup_mutation_proposal_approval` 为非空列表时，列表中的每个 `target_id` 必须存在于 `cleanup_mutation_proposal`
- 列表中的每个 `target_id` 必须继续存在于 `cleanup_targets`，且该 target 在 `cleanup_target_eligibility` 中必须保持 `eligible`
- 列表中的每个 `target_id` 必须与 `cleanup_preview_plan` 中已声明的 preview item 对齐
- 同一列表内不得出现重复 `target_id`
- `approved_action` 必须等于 proposal `proposed_action`，并且等于 target `cleanup_action`
- `cleanup_mutation_proposal_approval` 不得引入 `cleanup_mutation_proposal` 中不存在的 target
- `listed` approval truth 不得被解释成 mutation side effect；未来实现仍必须经过独立 approval consumption 与 execution handoff
- 若结构非法、目标不对齐、动作不一致或原因缺失，未来实现必须将其视为 invalid truth，而不是自动纠正

## 用户故事与验收

### US-060-1 - Framework Maintainer 需要单一 approval truth（优先级：P0）

作为 **框架维护者**，我希望 cleanup mutation proposal approval 被正式定义为 `050` artifact 内的 sibling truth surface，以便后续 approval consumption 和 execution work item 都消费同一 truth，而不是从 proposal list 或 CLI confirm 推断。

**优先级说明**：如果 approval truth 不先冻结，`059` 之后的链路就会重新发明“哪些 proposal 真正获批”，直接破坏 `050 -> 054 -> 056 -> 058 -> 059` 的单一 truth chain。

**独立测试**：审阅 `060` formal docs，确认 `cleanup_mutation_proposal_approval` 的位置、字段、状态和 non-goals 被明确锁定，并通过只读约束校验。

**验收场景**：

1. **Given** 我阅读 `060` formal docs，**When** 我查找 approval truth 的位置，**Then** 我能明确看到它属于 `050` cleanup artifact，而不是新的 approval artifact。
2. **Given** 我检查 approval entry 结构，**When** 我确认最小字段，**Then** 我只能看到 `target_id`、`approved_action`、`reason` 这组字段。

---

### US-060-2 - Reviewer 需要阻止 inferred approval（优先级：P0）

作为 **reviewer**，我希望 `060` 明确禁止通过 `cleanup_mutation_proposal`、CLI confirm、reports、`written_paths` 或 working tree 状态推断 approval，以便未来实现只能消费显式 formalized approval truth。

**优先级说明**：如果 approval 仍然允许由实现层或操作流程隐式给出，proposal truth 与 execution truth 之间就会失去审计边界，review 无法判断 real mutation 是否越权。

**独立测试**：审阅 `060` 的范围、已锁定决策与约束，确认 inferred approval 被明确禁止。

**验收场景**：

1. **Given** 我阅读 `060`，**When** 我确认 approval 来源，**Then** 我只能看到 `cleanup_mutation_proposal_approval` 与 proposal/preview/eligibility/targets 的显式对齐关系。
2. **Given** 我评审后续实现，**When** 我查找 non-goals，**Then** 我能明确看到 CLI confirm、reports、deliverables、`written_paths` 与 working tree 状态都不能直接视为 approval。

---

### US-060-3 - 后续子项执行者需要稳定的 approval handoff（优先级：P1）

作为 **后续子项执行者**，我希望 `060` 明确 approval truth 的状态语义和接力顺序，以便我先写 approval consumption 的 failing tests，再进入 service/CLI 消费，而不是直接跳到 real cleanup mutation。

**优先级说明**：当前阶段最容易犯的错误就是把 `listed` approval 误读成“已经可以执行 cleanup”；必须先把 approval truth 与 execution truth 明确分离。

**独立测试**：审阅 `060` 成功标准和已锁定决策，确认 future child work item 的顺序被固定为 `failing tests -> service/CLI approval consumption -> separate execution child work item`。

**验收场景**：

1. **Given** `cleanup_mutation_proposal_approval` 缺失，**When** 我继续后续 work item，**Then** 我能明确知道必须继续保持 `deferred`，不得把 listed proposal 直接视为 approved。
2. **Given** 某个 target 出现在 `cleanup_mutation_proposal_approval` 中，**When** 我规划后续实现，**Then** 我能明确知道这只允许进入 approval consumption / execution gating truth，而不等于 mutation 已被执行。

## 需求

### 功能需求

- **FR-060-001**：系统必须将 `cleanup_mutation_proposal_approval` 定义为 `050` final proof archive project cleanup artifact 的 sibling truth surface。
- **FR-060-002**：系统必须规定 `cleanup_mutation_proposal_approval` 只能引用 `cleanup_mutation_proposal` 中已存在的 proposal item。
- **FR-060-003**：系统必须将 approval truth 的总体状态固定为 `missing`、`empty`、`listed` 三种。
- **FR-060-004**：系统必须规定每个 approval entry 的必填字段为 `target_id`、`approved_action`、`reason`。
- **FR-060-005**：系统必须规定 `approved_action` 同时与 proposal `proposed_action` 和 target `cleanup_action` 保持完全一致。
- **FR-060-006**：系统必须规定 `cleanup_mutation_proposal_approval` 可作为 proposal truth 的显式子集存在，不要求覆盖全部 proposal items。
- **FR-060-007**：系统必须禁止通过 `cleanup_mutation_proposal`、CLI confirm、reports、deliverables、`written_paths`、目录命名或 working tree 状态推断 approval。
- **FR-060-008**：系统必须明确 `listed` approval truth 不等于 mutation 已执行，而只表示 future child work item 可进入 approval consumption / execution gating。
- **FR-060-009**：系统必须保持 docs-only 范围，不修改 `src/` 或 `tests/`。
- **FR-060-010**：系统必须要求 future child work item 先写 failing tests 固定 approval truth consumption，再进入 service/CLI，再进入 separate execution child work item。
- **FR-060-011**：系统必须将脚手架生成、formal docs 重写与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体

- **Cleanup Mutation Proposal Approval**：`050` cleanup artifact 内、与 `cleanup_mutation_proposal` 并列的 canonical approval truth 列表。
- **Approval Entry**：描述单个 proposal target 是否被显式纳入 future execution gating truth 的 canonical 对象。
- **Approval Truth State**：`missing`、`empty`、`listed` 三种总体状态，用于表达 approval truth 是否已 formalize。

## 成功标准

### 可度量结果

- **SC-060-001**：formal docs 明确把 `cleanup_mutation_proposal_approval` 固定为 `050` cleanup artifact 的 sibling truth surface。
- **SC-060-002**：formal docs 明确列出 approval entry 的最小字段、状态语义以及与 targets/eligibility/preview/proposal truth 的对齐约束。
- **SC-060-003**：formal docs 明确禁止 inferred approval，并继续保持 `050` 的 `deferred` honesty boundary。
- **SC-060-004**：formal docs 明确 future child work item 的顺序为 `failing tests -> service/CLI approval consumption -> separate execution child work item`。
- **SC-060-005**：`task-execution-log.md` 追加记录脚手架、边界冻结与 focused verification 结果。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
