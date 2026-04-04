# 功能规格：Frontend Program Final Proof Archive Cleanup Eligibility Consumption Baseline

**功能编号**：`055-frontend-program-final-proof-archive-cleanup-eligibility-consumption-baseline`
**创建日期**：2026-04-04
**状态**：已实现（eligibility consumption baseline）
**输入**：在 `050` 已建立 final proof archive project cleanup baseline、`053` 已将 `cleanup_targets` 接入 `ProgramService` 与 CLI、`054` 已冻结 `cleanup_target_eligibility` canonical truth surface 后，补齐 service/CLI 对 eligibility truth 的消费基线，确保 request/result/artifact/terminal output 均只消费 formalized truth，并继续保持 `deferred` honesty boundary。

**范围**：
- 覆盖 `050` cleanup artifact 中 `cleanup_target_eligibility` 的读取、校验、透传与结果表达。
- 覆盖 eligibility truth 的 `missing`、`empty`、`listed` 三态，以及 target-level `eligible`、`blocked` 的消费语义。
- 覆盖 `ProgramService` 与 CLI 的 gating/guard 输出，不改变当前 baseline 不执行真实 cleanup mutation 的事实。

**非范围**：
- 不执行任何真实 workspace cleanup mutation、git mutation、删除或 janitor 行为。
- 不新增 preview-only artifact、旁路 plan artifact 或第二套 eligibility truth。
- 不通过 `written_paths`、reports、目录结构或 working tree 状态推断 eligibility。
- 不把 `eligible` 解释成“已经允许 real cleanup”。

## 用户场景与测试（必填）

### 用户故事 1 - Project cleanup 只消费 formalized eligibility truth（优先级：P0）

作为框架维护者，我希望 final proof archive project cleanup 只消费 `050` artifact 中显式声明的 `cleanup_target_eligibility`，以便后续 planning/mutation work 始终建立在单一 truth source 上。

**优先级说明**：如果当前阶段仍然不消费 `cleanup_target_eligibility`，那么 `054` 冻结的资格真值不会进入执行链，后续 child work item 也无法可靠判断哪些 target 可以继续推进。

**独立测试**：在单元测试中分别构造 eligibility truth 缺失、空列表、显式列表与非法映射四类 payload，断言 request/result/artifact payload 与警告信息符合 frozen semantics。

**验收场景**：

1. **Given** `050` cleanup artifact 未提供 `cleanup_target_eligibility` 字段，**When** 构建 project cleanup request，**Then** 系统必须将 eligibility truth 识别为 `missing`，并继续保持 `deferred` 基线。
2. **Given** `050` cleanup artifact 提供 `cleanup_target_eligibility: []` 且 `cleanup_targets: []`，**When** 构建 project cleanup request，**Then** 系统必须将 eligibility truth 识别为 `empty`，且不得把空列表解释为字段缺失。
3. **Given** `050` cleanup artifact 提供与 `cleanup_targets` 一一对应的 eligibility 列表，**When** 构建与执行 project cleanup baseline，**Then** 系统必须原样透传 eligibility entries，并继续返回 `deferred`。

---

### 用户故事 2 - CLI 输出必须暴露 eligibility gating 语义（优先级：P1）

作为框架操作者，我希望 CLI dry-run / execute 输出能直接看到 eligibility truth state 和 eligibility 条目数量，以便不打开 artifact 也能判断当前 cleanup baseline 是否已具备 formalized eligibility truth。

**优先级说明**：CLI 是当前框架操作者的主要入口；如果 terminal output 不暴露 eligibility truth，`missing` 与 `empty`、`listed` 与 invalid mapping 的差异就会被隐藏。

**独立测试**：在集成测试中通过 CLI 触发 dry-run 与 execute，断言输出与 report 包含 `cleanup_target_eligibility_state` 以及 eligibility 数量。

**验收场景**：

1. **Given** `cleanup_target_eligibility` 缺失，**When** 运行 `program final-proof-archive-project-cleanup`，**Then** 输出必须显式提示 `cleanup target eligibility state: missing`。
2. **Given** `cleanup_target_eligibility` 为显式列表，**When** 运行执行命令，**Then** 输出必须反映 `listed`，并显示 eligibility 条目数量与 `deferred` 结果。

---

### 边界情况

- `cleanup_target_eligibility` 字段存在但值不是列表时，系统必须视为 invalid truth，而不是自动纠正。
- eligibility entry 缺失 `target_id`、`eligibility` 或 `reason` 时，系统必须暴露结构性警告，而不是 silently drop。
- `cleanup_target_eligibility` 与 `cleanup_targets` 的 `target_id` 集合不对齐时，系统必须保留显式 warning，并继续维持 `deferred` honesty boundary。
- target 被标记为 `eligible` 时，系统只能把它视为 future child work item 的准入真值，而不是本次 baseline 的 mutation 放行信号。

## 需求（必填）

### 功能需求

- **FR-055-001**：系统必须只从 `050` final proof archive project cleanup artifact 的 `cleanup_target_eligibility` 字段读取 eligibility truth。
- **FR-055-002**：系统必须区分并暴露 `cleanup_target_eligibility_state` 的 `missing`、`empty`、`listed` 三种状态。
- **FR-055-003**：系统必须在 request/result/artifact payload 中保留显式 eligibility 列表，不得基于目录命名、`written_paths`、reports 或 git 状态推断补全。
- **FR-055-004**：当 `cleanup_target_eligibility` 结构非法、entry 缺失必填键或与 `cleanup_targets` 不对齐时，系统必须产出结构性警告，且不得把 invalid truth 伪装成 real cleanup readiness。
- **FR-055-005**：CLI dry-run 与 execute 输出必须暴露 `cleanup_target_eligibility_state` 与 eligibility 条目数量，帮助操作者区分 `missing`、`empty`、`listed`。
- **FR-055-006**：即使存在显式 `cleanup_target_eligibility`，当前 baseline 仍必须保持 `deferred` 结果，不执行真实 workspace cleanup mutation。
- **FR-055-007**：系统必须把 `cleanup_target_eligibility` 作为 `cleanup_targets` 的 sibling truth surface 进行消费，并在 `source_linkage` 中保留 state/path 可追踪信息。
- **FR-055-008**：系统必须将脚手架、red-green 测试、实现接线与 focused verification 记录到 append-only `task-execution-log.md`。

### 关键实体（如涉及数据则必填）

- **CleanupTargetEligibilityState**：`missing`、`empty`、`listed` 三态 truth surface，用于表达当前 cleanup artifact 是否具备 formal eligibility truth。
- **CleanupTargetEligibilityEntry**：由 `target_id`、`eligibility`、`reason` 组成的显式资格定义，消费层只允许读取与透传，不得扩写隐式字段。
- **ProjectCleanupArtifactPayload**：`050/053/055` 链路中的 canonical payload，继续承载 project cleanup request/result/summaries，并新增 eligibility truth 信息。

## 成功标准（必填）

### 可度量结果

- **SC-055-001**：新增单元测试能够覆盖 `cleanup_target_eligibility` 的 `missing`、`empty`、`listed` 与 invalid mapping 行为，并在实现前先失败、实现后通过。
- **SC-055-002**：`ProgramService` 产出的 request/result/artifact payload 可观测到 `cleanup_target_eligibility_state` 与显式 eligibility 列表，且不会从隐式信号推断 target 资格。
- **SC-055-003**：CLI 集成测试验证 dry-run / execute 输出与 report 包含 eligibility truth state 和 eligibility 条目数量。
- **SC-055-004**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 全部通过。
