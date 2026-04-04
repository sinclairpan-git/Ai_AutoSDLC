# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Proposal Baseline

**功能编号**：`058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline`
**创建日期**：2026-04-04
**状态**：已冻结（docs-only mutation proposal baseline）
**输入**：在 `050` 已建立 final proof archive project cleanup baseline、`052` 已冻结 `cleanup_targets` truth、`054` 已冻结 `cleanup_target_eligibility` truth、`056` 已冻结 `cleanup_preview_plan` truth、`057` 已完成 preview plan consumption baseline 后，继续将下一层显式 truth 冻结为 `cleanup_mutation_proposal`，为未来 proposal consumption / approval / execution 子项提供单一事实源。

**范围**：
- 覆盖 `050` final proof archive project cleanup artifact 中 `cleanup_mutation_proposal` 的 canonical truth surface 定义。
- 覆盖 `cleanup_mutation_proposal` 的 `missing`、`empty`、`listed` 三态，以及 proposal item 与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan` 的对齐约束。
- 覆盖 proposal truth 与 real cleanup execution 之间的 honesty boundary，并固定下一子项的接力顺序。

**非范围**：
- 不改动 `ProgramService`、CLI、tests 或任何 `src/` 代码。
- 不执行任何真实 workspace cleanup mutation、git mutation、删除、移动或 janitor 行为。
- 不新增 preview/proposal 旁路 artifact、第二套 canonical truth 或自动推导逻辑。
- 不把 `cleanup_mutation_proposal` 解释成“已经允许执行”或“已经完成执行”。

## 用户场景与测试（必填）

### 用户故事 1 - Cleanup mutation proposal 必须成为显式 formal truth（优先级：P0）

作为框架维护者，我希望 future cleanup mutation work 只消费 `050` artifact 中显式声明的 `cleanup_mutation_proposal`，以便 proposal review、approval 与 execution 都建立在单一 truth source 上，而不是从 `cleanup_targets`、eligibility 或 preview plan 隐式推断。

**优先级说明**：如果当前阶段不先冻结 proposal truth，那么 `057` 之后的链路只能继续依赖隐式“看起来可以清理”的判断，后续 child work item 会重新引入双轨语义。

**独立测试**：本 work item 为 docs-only；独立验证方式为文档对账、`uv run ai-sdlc verify constraints` 与 `git diff --check`。

**验收场景**：

1. **Given** `050` cleanup artifact 尚未包含 `cleanup_mutation_proposal`，**When** 审阅 `058` formal docs，**Then** 文档必须把 proposal truth 明确定义为 `missing`，而不是默认从 preview plan 或 eligibility 推出 proposal。
2. **Given** `050` cleanup artifact 显式声明 `cleanup_mutation_proposal: []`，**When** 审阅 `058` formal docs，**Then** 文档必须把 proposal truth 明确定义为 `empty`，且不得与字段缺失混淆。
3. **Given** `050` cleanup artifact 显式声明 proposal item 列表，**When** 审阅 `058` formal docs，**Then** 文档必须要求 proposal item 只引用已声明的 target、`eligible` truth 与 preview plan item，并继续保持 no-execution boundary。

---

### 用户故事 2 - Proposal truth 不得伪装成 execution approval（优先级：P1）

作为框架操作者，我希望 `cleanup_mutation_proposal` 被明确标记为“未来消费的提案真值”，而不是“当前已获批准的执行指令”，以便 CLI/service 在后续子项接线时不会跳过 approval/gating semantics。

**优先级说明**：proposal 与 execution 一旦混淆，框架就会从 formal planning truth 直接滑向 mutation side effect，破坏 `050/051/054/056/057` 已经建立的 honesty boundary。

**独立测试**：审阅 `058` 文档中的非范围、功能需求、成功标准与实施顺序，确认全部保持 docs-only、no-execution 语义。

**验收场景**：

1. **Given** `cleanup_mutation_proposal` 为显式列表，**When** 审阅 `058` formal docs，**Then** 文档必须明确 `listed` 仅表示 future child work item 可消费 proposal truth，不代表 mutation 已被允许或执行。
2. **Given** 后续需要进入 service/CLI 接线，**When** 审阅 `058` 的 handoff 说明，**Then** 文档必须固定顺序为 `failing tests -> proposal consumption -> approval/gating semantics -> execution`。

---

### 边界情况

- `cleanup_mutation_proposal` 字段存在但值不是列表时，未来消费层必须将其视为 invalid truth，而不是自动纠正。
- proposal item 缺失 `target_id`、`proposed_action` 或 `reason` 时，未来消费层必须暴露结构性 warning，而不是 silently drop。
- proposal item 若引用不存在于 `cleanup_targets` 的 `target_id`、引用 `blocked` target、或不在 `cleanup_preview_plan` 中出现，未来消费层必须视为 misaligned truth。
- `proposed_action` 若与 target `cleanup_action` 不一致，未来消费层必须保留 mismatch warning，而不是自动修正。
- `listed` proposal truth 只表示存在显式 proposal surface，不等于 operator approval、executor readiness 或真实 cleanup side effect。

## 需求（必填）

### 功能需求

- **FR-058-001**：系统必须将 `cleanup_mutation_proposal` 冻结为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface。
- **FR-058-002**：系统必须将 `cleanup_mutation_proposal_state` 冻结为 `missing`、`empty`、`listed` 三态，并明确 `missing` 与 `empty` 语义不可混淆。
- **FR-058-003**：系统必须明确 proposal truth 只能来自显式 artifact 字段，不得从 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`written_paths`、reports、目录命名或 working tree 状态推断补全。
- **FR-058-004**：系统必须将 proposal item 的最小字段冻结为 `target_id`、`proposed_action`、`reason`，并禁止在本项扩张额外隐式字段。
- **FR-058-005**：系统必须明确 proposal item 只能引用 `cleanup_targets` 中已声明的 target，且该 target 的 eligibility 必须为 `eligible`。
- **FR-058-006**：系统必须明确 proposal item 只能对齐已显式出现在 `cleanup_preview_plan` 中的 preview item，且 `proposed_action` 必须与 target `cleanup_action` 对齐。
- **FR-058-007**：系统必须明确 `cleanup_mutation_proposal` 只是 future child work item 可消费的提案真值，不得被解释为 approval、readiness 或 execution completion。
- **FR-058-008**：系统必须将下一步接力顺序固定为 `failing tests -> service/CLI proposal consumption -> approval/gating semantics -> separate execution child work item`。
- **FR-058-009**：系统必须将脚手架、formal truth freeze 与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体（如涉及数据则必填）

- **CleanupMutationProposalState**：`missing`、`empty`、`listed` 三态 truth surface，用于表达当前 cleanup artifact 是否已具备显式 mutation proposal truth。
- **CleanupMutationProposalEntry**：由 `target_id`、`proposed_action`、`reason` 组成的显式提案条目，未来只能被消费与校验，不得由消费层隐式生成。
- **ProjectCleanupArtifactPayload**：`050/052/054/056/057/058` 链路中的 canonical payload，继续承载 cleanup targets、eligibility、preview plan 与 proposal truth。

## 成功标准（必填）

### 可度量结果

- **SC-058-001**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md` 全部对齐为 docs-only 的 `cleanup_mutation_proposal` formal baseline。
- **SC-058-002**：文档明确将 `cleanup_mutation_proposal` 冻结为单一 truth source，并禁止从 sibling truths 或隐式信号推断 proposal。
- **SC-058-003**：文档明确 proposal truth 与 approval/execution 的边界，且固定下一子项顺序为 `failing tests -> proposal consumption -> approval/gating -> execution`。
- **SC-058-004**：`uv run ai-sdlc verify constraints` 与 `git diff --check -- specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline .ai-sdlc/project/config/project-state.yaml` 全部通过。
