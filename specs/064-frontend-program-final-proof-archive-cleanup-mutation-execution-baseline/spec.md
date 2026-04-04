# 功能规格：Frontend Program Final Proof Archive Cleanup Mutation Execution Baseline

**功能编号**：`064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline`  
**创建日期**：2026-04-04  
**状态**：已冻结（formal baseline）  
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md`](../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md)、[`../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md`](../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md)

> 口径：`064` 是 `063` 之后的独立 execution child work item。它不再停留在 execution gating truth consumption，而是把已 formalize 且已被 `063` 接入的 `cleanup_mutation_execution_gating` 转换成真正的 bounded cleanup mutation。当前 work item 只允许执行 canonical artifact 已显式列出的 gated action，并要求对实际执行结果、失败原因、written paths 与 remaining blockers 进行诚实回报；它不是新的 cleanup truth source，也不是无边界 workspace janitor。

## 问题定义

`050` 已经冻结 final proof archive project cleanup 的 execute contract 与 `deferred` honesty boundary，`062` 已经把 `cleanup_mutation_execution_gating` 冻结为 canonical sibling truth，`063` 进一步把这层 truth 接入 `ProgramService`、artifact payload 与 CLI/report 输出，但仍然明确保持：

- 当前 execute 路径只消费 execution gating truth，不执行真实 workspace cleanup mutation
- 即便 `cleanup_mutation_execution_gating_state` 为 `listed`，结果仍然只能诚实表示为 `deferred`
- 没有单独的 execution child work item，后续实现就会重新解释什么叫“允许执行”、什么叫“只是 approved/gated 但未执行”

因此，`064` 要解决的是：

- 在不引入第二套 execution truth 的前提下，如何只消费 canonical `cleanup_mutation_execution_gating`
- baseline 到底允许执行哪些 cleanup action，哪些仍然不允许越界处理
- 实际 mutation 发生后，如何诚实回报 per-target outcome、aggregate result、written paths、warnings 与 remaining blockers
- 如果目标缺失、路径不安全、动作不支持或部分 target 执行失败，系统如何避免把结果伪装成“已完成 cleanup”

如果不先把这一层正式冻结，后续实现会出现两类违约：

- 从 `--yes`、approval truth、working tree、report 文本或人工判断推断“现在可以执行”
- 把 real cleanup mutation 扩张成任意删除、任意归档、任意目录清理，而不是只执行 canonical target 已声明的 bounded action

## 范围

- **覆盖**：
  - 将 frontend final proof archive cleanup mutation execution 正式定义为 `063` 之后的独立 child work item
  - 规定 execute 路径只能消费 canonical `cleanup_mutation_execution_gating` listed items 与其已对齐的 target / eligibility / preview / proposal / approval truth
  - 规定 baseline 支持的最小 action matrix、路径安全约束、结果诚实语义与 report surface
  - 为后续 `ProgramService`、CLI、unit tests、integration tests 提供 test-first 的 execution baseline
- **不覆盖**：
  - 新增第二套 cleanup execution artifact、旁路 execution queue、隐式 action discovery 或独立 executor truth
  - 通过 `cleanup_mutation_proposal_approval`、CLI confirm、reports、`written_paths`、目录命名或 working tree 状态反推 execution gating
  - 执行 canonical target 之外的任意 workspace mutation、git mutation 或 janitor 行为
  - 重新定义 `049` thread archive baseline、`050` project cleanup baseline、`062` execution gating truth 或 `063` consumption semantics
  - 扩张为批量通配删除器、目录重写器或根据文件内容动态推断 cleanup 动作的 engine

## 已锁定决策

- `064` 必须只消费 `063` 已接入的 canonical `cleanup_mutation_execution_gating`，不得新造 execution-ready truth
- execute 路径必须来自显式确认后的 project cleanup execute，不得默认触发
- baseline 只允许执行 canonical artifact 中已经列出的 gated target，不得扫描工作区寻找“顺手可清理”的对象
- baseline 当前只支持两类明确动作组合：
  - `target_kind: thread_archive` + `gated_action: archive_thread_report`
  - `target_kind: spec_dir` + `gated_action: remove_spec_dir`
- 对 `archive_thread_report`，实现只允许操作 canonical target 已给出的 `path`；不得额外推断“原始线程位置”或重新设计 archive 路径
- 对 `remove_spec_dir`，实现只允许删除 canonical target 已给出的 spec 目录；不得扩张到 sibling spec、父目录或其他交叉产物
- target path 必须位于当前项目工作区根目录内；若解析后越界，必须诚实失败
- target 若在执行时不存在，系统必须产生显式 non-success outcome 与 warning，不得把“目标已不存在”自动当作成功
- listed execution gating truth 不再等于 `deferred`；一旦开始真实执行，aggregate result 必须根据真实 outcome 反映为 completed / partial / failed / blocked 中的诚实状态
- `064` 允许最小化真实 mutation，但仍然不得改写 upstream canonical truth 本身；新的 project cleanup artifact 只记录 execution 结果，不覆盖 execution gating 来源

## Baseline Action Matrix

| target_kind | gated_action | 允许的 baseline mutation | 明确禁止 |
|-------------|--------------|--------------------------|----------|
| `thread_archive` | `archive_thread_report` | 删除 canonical target `path` 所指向的已归档线程报告文件 | 推断或移动原始 thread 文件、改写 archive 策略、扫描其他 archive 报告 |
| `spec_dir` | `remove_spec_dir` | 递归删除 canonical target `path` 所指向的 spec 目录 | 删除父目录、删除 sibling spec、按名称模式批量清理其他目录 |

## 用户故事与验收

### US-064-1 - Operator 需要执行 canonical gated cleanup mutation（优先级：P0）

作为**operator**，我希望在 `cleanup_mutation_execution_gating` 已 formalize 且我显式确认执行后，系统只对 canonical listed targets 执行真实 cleanup mutation，以便 project cleanup 不再停留在 `deferred`，同时又不扩张为无边界 workspace cleanup engine。

**优先级说明**：如果 `063` 之后仍然没有独立 execution baseline，execution gating truth 就只能停留在“看起来可以执行”的状态，无法完成从 formal truth 到真实 mutation 的闭环。

**独立测试**：在 unit / integration tests 中构造包含 `archive_thread_report` 与 `remove_spec_dir` 的 gated targets，验证 execute 后目标路径真实变化、artifact 记录真实 outcome、CLI/report 暴露真实结果。

**验收场景**：

1. **Given** `cleanup_mutation_execution_gating` listed 了一个 `thread_archive` target，且其 `gated_action` 为 `archive_thread_report`，**When** 我执行 project cleanup，**Then** 系统必须只对该 canonical `path` 执行文件删除，并把结果记录为真实 execution outcome。
2. **Given** `cleanup_mutation_execution_gating` listed 了一个 `spec_dir` target，且其 `gated_action` 为 `remove_spec_dir`，**When** 我执行 project cleanup，**Then** 系统必须只删除该 canonical spec 目录，而不是扩张到其他 spec 或上级目录。

---

### US-064-2 - Framework Maintainer 需要诚实的 aggregate execution result（优先级：P0）

作为**框架维护者**，我希望一旦进入真实 mutation，`ProgramService` 与 CLI/report 能按 per-target outcome 诚实汇总 aggregate result，以便不会再把真实执行伪装成 `deferred`，也不会把部分失败伪装成全部成功。

**优先级说明**：real mutation 一旦发生，原先 `deferred` 的 honesty boundary 就不再成立；如果没有新的诚实结果语义，artifact 与 CLI 会对执行状态撒谎。

**独立测试**：在单元测试中覆盖全部成功、部分成功、全部失败、路径越界、目标缺失与不支持动作等场景，断言 aggregate result、warnings、remaining blockers 与 written paths 符合冻结语义。

**验收场景**：

1. **Given** 多个 gated targets 中只有一部分执行成功，**When** cleanup execute 结束，**Then** aggregate result 必须是 `partial`，并保留失败 target 的 warnings / remaining blockers。
2. **Given** 所有 gated targets 都因路径越界、不支持动作或目标缺失而未执行成功，**When** cleanup execute 结束，**Then** aggregate result 必须是 `failed` 或 `blocked`，不得伪装成 `completed`。

---

### US-064-3 - Reviewer 需要 bounded execution 而不是 inferred janitor（优先级：P1）

作为**reviewer**，我希望 `064` 明确限制 baseline 只允许执行 canonical action matrix 与 workspace-root 内的 target path，以便后续实现不会把 listed execution gating 偷渡成任意 workspace janitor。

**优先级说明**：真实 cleanup mutation 的风险远高于 truth consumption；如果不把执行矩阵、路径边界与 non-goals 钉死，后续实现很容易越过 `050/062/063` 已冻结的边界。

**独立测试**：通过 docs review 与 red tests 同时验证 unsupported action、duplicate target、越界路径与 missing target 均不会被自动修正或 silently ignored。

**验收场景**：

1. **Given** 一个 listed gating item 的 `gated_action` 不属于 baseline action matrix，**When** 我执行 project cleanup，**Then** 系统必须将该 target 标记为 non-success，并保留明确 warning。
2. **Given** 一个 listed gating item 的 `path` 解析后位于项目工作区之外，**When** 我执行 project cleanup，**Then** 系统必须拒绝执行该 target，并把结果诚实表示为 `blocked` 或 `failed`。

## 需求

### 功能需求

- **FR-064-001**：系统必须将 `064` 定义为 `063` 之后的独立 cleanup mutation execution child work item，而不是继续扩张 `063`。
- **FR-064-002**：系统必须只从 canonical project cleanup artifact 中消费 `cleanup_mutation_execution_gating` listed items 作为真实 mutation 的唯一执行输入面。
- **FR-064-003**：系统必须要求每个可执行 gated target 同时与 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal` 与 `cleanup_mutation_proposal_approval` 保持对齐；若任一对齐关系失效，必须诚实返回 non-success outcome。
- **FR-064-004**：系统必须只允许在显式确认后的 project cleanup execute 路径上执行真实 cleanup mutation。
- **FR-064-005**：系统必须将 baseline 支持动作限制为 `thread_archive/archive_thread_report` 与 `spec_dir/remove_spec_dir` 两种组合。
- **FR-064-006**：系统必须对 `archive_thread_report` 只操作 canonical target `path` 所指向的归档线程报告文件，不得推断原始 thread 路径或扩张为“移动到 archive”语义。
- **FR-064-007**：系统必须对 `remove_spec_dir` 只操作 canonical target `path` 所指向的 spec 目录，不得删除父目录、sibling spec 或其他未列出的路径。
- **FR-064-008**：系统必须在执行前验证 target `path` 解析后位于项目工作区根目录内；若越界，必须阻止执行并记录 explicit warning / blocker。
- **FR-064-009**：系统必须在执行时对缺失 target、重复 target、unsupported action、路径类型不匹配或 runtime 删除失败返回显式 per-target non-success outcome，不得 silently drop 或自动修正。
- **FR-064-010**：系统必须在 project cleanup result、artifact payload 与 CLI/report 中记录 per-target execution outcome、aggregate result、written paths、warnings、remaining blockers 与 source linkage。
- **FR-064-011**：当至少一个 listed gated target 被真实尝试执行时，系统不得继续将 aggregate result 伪装为 `deferred`；结果必须诚实反映 `completed`、`partial`、`failed` 或 `blocked`。
- **FR-064-012**：系统必须保持 single-truth-source 边界，不得因为真实 mutation 已发生而回写、改写或重定义 `cleanup_mutation_execution_gating` truth 本身。
- **FR-064-013**：系统必须以 test-first 顺序推进：先补 failing tests 固定 execution semantics，再补 service/CLI 实现与 focused verification。
- **FR-064-014**：系统必须将 formal docs 冻结、red/green 过程与 focused verification 追加记录到 append-only `task-execution-log.md`。

### 关键实体

- **Cleanup Mutation Execution Target**：由 canonical `cleanup_targets` 与 `cleanup_mutation_execution_gating` 对齐后得到的单个可执行 cleanup target，包含稳定 `target_id`、target `path`、`target_kind` 与 `gated_action`。
- **Cleanup Mutation Execution Outcome**：描述单个 gated target 的真实执行结果，至少包含 `target_id`、`outcome`、`action`、`path`、warnings 与 written-path evidence。
- **Program Frontend Final Proof Archive Project Cleanup Result**：承载整次 cleanup mutation execution 的 aggregate state / result、per-target outcome、written paths、remaining blockers 与 source linkage。

## 成功标准

### 可度量结果

- **SC-064-001**：formal docs 明确将 `064` 固定为 `063` 之后的 separate execution child work item，而不是继续在 `063` 内做真实 mutation。
- **SC-064-002**：formal docs 明确锁定 baseline action matrix、路径安全边界与 canonical-target-only 执行语义。
- **SC-064-003**：新增 unit tests 能在实现前失败，并覆盖 `archive_thread_report`、`remove_spec_dir`、missing target、unsupported action、越界路径、部分成功与全部失败的执行语义。
- **SC-064-004**：新增 integration tests 能验证 CLI dry-run / execute / report 对真实 execution outcome、aggregate result 与 written paths 的呈现。
- **SC-064-005**：实现后 `ProgramService` / CLI 不再把真实 mutation 结果显示为 `deferred`，并能在 artifact 中保留诚实 execution evidence。
- **SC-064-006**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ruff check src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`、`uv run ai-sdlc verify constraints` 与 `git diff --check -- specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline src/ai_sdlc/core src/ai_sdlc/cli tests/unit tests/integration` 全部通过。
