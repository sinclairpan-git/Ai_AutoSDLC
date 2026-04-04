# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Eligibility Baseline

**功能编号**：`054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`](../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md)、[`../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`](../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md)、[`../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md`](../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md)

> 口径：`054` 不是把 `053` 继续扩张成 preview plan 或 real cleanup mutation，而是先冻结“显式 `cleanup_targets` 在当前 truth 下是否具备后续 mutation/planning 资格”的 canonical truth surface。当前 work item 只定义 eligibility truth、状态边界与后续接力条件，不修改 `ProgramService`、CLI 或 tests。

## 问题定义

`050` 已冻结 final proof archive project cleanup baseline，并要求在没有安全且已定义的 cleanup action 时诚实返回 `deferred`。`051` 进一步冻结：当前批准的 cleanup mutation allowlist 为空集合，不能直接跳到真实 mutation。`052` 则将 explicit cleanup targets 固定为 `050` artifact 内的 canonical truth surface，`053` 已把 `cleanup_targets` 的 `missing`、`empty`、`listed` 三态接入 `ProgramService` 与 CLI 消费链。

当前还缺失的真值层是：

- 哪些 explicit `cleanup_targets` 已具备进入后续 mutation/planning work item 的资格
- 哪些 target 仍然被阻塞，以及阻塞原因是什么
- eligibility truth 应以什么字段形态留在单一 truth source 内，而不是新建旁路 artifact
- 在 eligibility truth 未 formalize 前，后续 work item 应如何继续保持 `deferred` honesty boundary

因此，`054` 要解决的是：

- 定义单一的 `cleanup_target_eligibility` canonical truth surface
- 锁定它与 `cleanup_targets` 的一一对应关系
- 锁定 eligibility truth 的 `missing`、`empty`、`listed` 总体状态，以及单 target 的 `eligible`、`blocked` 决策状态
- 为未来 child work item 固定接力顺序：先 failing tests，再 service/CLI 消费，再考虑 preview plan 或 real mutation

## 范围

- **覆盖**：
  - 将 `cleanup_target_eligibility` 定义为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface
  - 规定 `cleanup_target_eligibility` 与 `cleanup_targets` 按 `target_id` 一一对应
  - 定义 eligibility truth 的总体状态语义：`missing`、`empty`、`listed`
  - 定义单 target 的决策语义：`eligible`、`blocked`
  - 规定 eligibility entry 的最小字段、排序、校验约束与原因字段
  - 规定未来 work item 的接力顺序与 non-goals
- **不覆盖**：
  - 修改 `050`、`051`、`052`、`053` 已冻结或已实现的结论
  - 新增第二套 cleanup artifact、preview-only plan artifact 或旁路 truth surface
  - 执行任何真实 workspace cleanup mutation、git mutation、递归删除或 janitor 行为
  - 修改 `src/ai_sdlc/core/program_service.py`
  - 修改 `src/ai_sdlc/cli/program_cmd.py`
  - 修改 `tests/unit/test_program_service.py`
  - 修改 `tests/integration/test_cli_program.py`
  - 通过 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名或工作树状态推断 eligibility

## 已锁定决策

- `cleanup_target_eligibility` 必须作为 `050` cleanup artifact 的 sibling 字段进入单一 truth source
- `cleanup_target_eligibility` 必须是有序列表，顺序与 `cleanup_targets` 完全一致
- 每个 eligibility entry 必须通过 `target_id` 指向一个已存在的 `cleanup_targets` entry；不得凭空新增 target
- eligibility truth 的总体状态只允许 `missing`、`empty`、`listed`
- 单 target 的决策状态只允许 `eligible`、`blocked`
- `eligible` 表示“未来 child work item 可以基于该 target 继续写 failing tests / planning truth”，不等于已执行 cleanup
- `blocked` 表示“该 target 当前不得进入后续 mutation/planning 实现”，必须携带阻塞原因
- 若 `cleanup_target_eligibility` 缺失，后续 work item 必须继续保持 `deferred`，不得自行推断资格
- `054` 当前阶段只允许修改 `specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/` 内文档与脚手架自动更新的 project state

## Cleanup Target Eligibility Canonical Truth

`cleanup_target_eligibility` 定义为与 `cleanup_targets` 一一对应的有序对象列表：

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
    eligibility: blocked
    reason: cleanup mutation eligibility not yet approved for real execution
```

### 每个 eligibility entry 的必填字段

| 字段 | 含义 |
|------|------|
| `target_id` | 指向 `cleanup_targets` 中现有条目的稳定标识 |
| `eligibility` | `eligible` 或 `blocked` |
| `reason` | 简短、可审计的资格说明或阻塞原因 |

### 约束

- `cleanup_target_eligibility` 缺失表示“eligibility truth 尚未 formalize”
- `cleanup_target_eligibility: []` 只允许在 `cleanup_targets: []` 时出现，表示“已 formalize 且当前没有 target 需要判定”
- 当 `cleanup_targets` 为非空列表时，`cleanup_target_eligibility` 必须逐项覆盖全部 `target_id`
- 同一列表内不得出现重复 `target_id`
- `cleanup_target_eligibility` 不得引入 `cleanup_targets` 中不存在的 target
- `eligible` 只授权后续 work item 继续进入 test-first/planning truth，不授权当前执行真实 cleanup
- `blocked` target 必须继续保持对 future mutation/planning implementation 的禁止状态
- 若列表结构非法、目标不对齐或原因缺失，未来实现必须将其视为 invalid truth，而不是自动纠正

## 用户故事与验收

### US-054-1 — Framework Maintainer 需要单一 eligibility truth（优先级：P0）

作为 **框架维护者**，我希望 cleanup mutation eligibility 被正式定义为 `050` artifact 内的 sibling truth surface，以便后续 work item 不会新建旁路 plan artifact 或凭实现猜测 target 资格。

**优先级说明**：如果 eligibility truth 不先冻结，后续 preview plan 或 mutation work item 就会在“哪些 target 可继续推进”这个问题上重新发明真值，直接破坏 `050 -> 052 -> 053` 的单一链路。

**独立测试**：审阅 `054` formal docs，确认 `cleanup_target_eligibility` 的位置、字段、状态和 non-goals 均被明确定义，并通过只读约束校验。

**验收场景**：

1. **Given** 我阅读 `054` formal docs，**When** 我查找 eligibility truth 的位置，**Then** 我能明确看到它属于 `050` cleanup artifact，而不是新 artifact。
2. **Given** 我检查 eligibility entry 结构，**When** 我确认字段定义，**Then** 我只能看到 `target_id`、`eligibility`、`reason` 这组最小字段。

---

### US-054-2 — Reviewer 需要阻止资格推断（优先级：P0）

作为 **reviewer**，我希望 `054` 明确禁止通过路径位置、reports、`written_paths` 或工作树状态推断 target eligibility，以便未来实现只能消费 formalized truth。

**优先级说明**：如果资格仍然允许通过实现层推断，`052` 和 `053` 已经冻结/实现的 explicit target truth 就会被旁路，review 无法判断真实边界是否被破坏。

**独立测试**：审阅 `054` 的范围、已锁定决策与约束，确认 inferred eligibility 被明确禁止。

**验收场景**：

1. **Given** 我阅读 `054`，**When** 我确认资格来源，**Then** 我只能看到 `cleanup_target_eligibility` 与 `cleanup_targets` 的显式映射。
2. **Given** 我评审后续实现，**When** 我查找 non-goals，**Then** 我能明确看到 `.ai-sdlc/`、reports、deliverables、`written_paths` 与 working tree 状态都不能被用来推断 eligibility。

---

### US-054-3 — 后续子项执行者需要稳定的接力前提（优先级：P1）

作为 **后续子项执行者**，我希望 `054` 明确 eligibility truth 的状态语义和接力顺序，以便我可以先写 failing tests，再决定 service/CLI 消费，而不是直接跳到 real mutation。

**优先级说明**：当前阶段最容易犯的错误就是把 `eligible` 误读成“已经允许执行 cleanup”；必须先把 test-first 接力条件冻结下来。

**独立测试**：审阅 `054` 成功标准和已锁定决策，确认未来 work item 的顺序被固定为 `failing tests -> service/CLI -> planning/mutation`。

**验收场景**：

1. **Given** `cleanup_target_eligibility` 缺失，**When** 我继续后续 work item，**Then** 我能明确知道当前必须继续保持 `deferred`，不得自行推断资格。
2. **Given** 某个 target 被标记为 `eligible`，**When** 我规划后续实现，**Then** 我能明确知道这只允许进入 test-first / planning truth，而不等于 real cleanup 已被放行。

## 需求

### 功能需求

- **FR-054-001**：系统必须将 `cleanup_target_eligibility` 定义为 `050` final proof archive project cleanup artifact 的 sibling truth surface。
- **FR-054-002**：系统必须规定 `cleanup_target_eligibility` 与 `cleanup_targets` 按 `target_id` 一一对应，且顺序一致。
- **FR-054-003**：系统必须将 eligibility truth 的总体状态固定为 `missing`、`empty`、`listed` 三种。
- **FR-054-004**：系统必须将单 target 的决策状态固定为 `eligible`、`blocked` 两种。
- **FR-054-005**：系统必须规定每个 eligibility entry 的必填字段为 `target_id`、`eligibility`、`reason`。
- **FR-054-006**：系统必须禁止通过 `.ai-sdlc/`、reports、deliverables、`written_paths`、目录命名或工作树状态推断 eligibility。
- **FR-054-007**：系统必须明确 `eligible` 不等于已执行 cleanup，而只表示未来 child work item 可继续进入 test-first / planning truth。
- **FR-054-008**：系统必须明确 `blocked` target 不得进入 future mutation/planning implementation，且必须保留阻塞原因。
- **FR-054-009**：系统必须保持 docs-only 范围，不修改 `src/` 或 `tests/`。
- **FR-054-010**：系统必须要求 future child work item 先写 failing tests 固定 eligibility consumption，再进入 service/CLI，再考虑 preview plan 或 real mutation。
- **FR-054-011**：系统必须将脚手架生成、formal docs 重写与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体

- **Cleanup Target Eligibility**：`050` cleanup artifact 内、与 `cleanup_targets` 同步排序的资格真值列表。
- **Eligibility Entry**：描述单个 target 当前是 `eligible` 还是 `blocked` 的 canonical truth 对象。
- **Eligibility Truth State**：`missing`、`empty`、`listed` 三种总体状态，用于表达 eligibility truth 是否已 formalize。

## 成功标准

### 可度量结果

- **SC-054-001**：formal docs 明确把 `cleanup_target_eligibility` 固定为 `050` cleanup artifact 的 sibling truth surface。
- **SC-054-002**：formal docs 明确列出 eligibility entry 的最小字段、状态语义和对齐约束。
- **SC-054-003**：formal docs 明确禁止 inferred eligibility，并保留 `050` 的 `deferred` honesty boundary。
- **SC-054-004**：formal docs 明确 future child work item 的顺序为 `failing tests -> service/CLI consumption -> planning/mutation`。
- **SC-054-005**：`task-execution-log.md` 追加记录脚手架、边界冻结与 focused verification 结果。
