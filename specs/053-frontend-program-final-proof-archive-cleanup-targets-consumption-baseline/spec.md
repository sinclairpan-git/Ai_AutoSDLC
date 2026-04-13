# 功能规格：Frontend Program Final Proof Archive Cleanup Targets Consumption Baseline

**功能编号**：`053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline`
**创建日期**：2026-04-04
**状态**：已实现（consumption baseline）
**输入**：在 `050` 已建立 final proof archive project cleanup baseline、`052` 已冻结 `cleanup_targets` formal truth surface 后，补齐 `ProgramService` 与 CLI 对 `cleanup_targets` 的消费基线，确保 request/result/artifact/terminal output 以显式 truth 为准，不通过 `written_paths`、目录命名、git 状态或 reports 推断 cleanup target。

**范围**：
- 覆盖 `050` cleanup artifact 中 `cleanup_targets` 的读取、校验、透传与结果表达。
- 覆盖 `missing`、`empty`、`listed` 三种 cleanup target truth state 的可观测行为。
- 覆盖 `ProgramService` 与 CLI 的基线消费，不改变 `050` 的 `deferred` honesty boundary。

**非范围**：
- 不执行任何真实 workspace cleanup mutation。
- 不新增独立 cleanup target artifact。
- 不根据 `written_paths`、reports、目录结构或 working tree 状态推断 cleanup target。

## 用户场景与测试（必填）

### 用户故事 1 - Program cleanup 只消费显式 truth（优先级：P0）

作为框架维护者，我希望 final proof archive project cleanup 仅消费 `050` artifact 中显式声明的 `cleanup_targets`，以便 cleanup baseline 的后续 mutation work 具备单一 truth source。

**优先级说明**：如果当前阶段继续沿用隐式推断或根本不消费 `cleanup_targets`，`052` 的 formal truth 冻结就不会进入执行链，后续 mutation work 也无法建立在可信边界上。

**独立测试**：在单元测试中分别构造 `cleanup_targets` 缺失、空列表、显式列表三类 `050` artifact，断言 request/result/artifact payload 与警告信息符合 truth state。

**验收场景**：

1. **Given** `050` cleanup artifact 未提供 `cleanup_targets` 字段，**When** 构建 project cleanup request，**Then** 系统必须将 cleanup target truth 识别为 `missing`，并阻止任何 target-level readiness 结论。
2. **Given** `050` cleanup artifact 提供 `cleanup_targets: []`，**When** 构建 project cleanup request，**Then** 系统必须将 cleanup target truth 识别为 `empty`，且不得将空列表解释为“字段缺失”。
3. **Given** `050` cleanup artifact 提供显式 `cleanup_targets` 列表，**When** 构建与执行 project cleanup baseline，**Then** 系统必须原样透传 target entries，并继续返回 `deferred`，明确当前 baseline 尚未执行真实 cleanup mutation。

---

### 用户故事 2 - CLI 输出暴露 cleanup target truth state（优先级：P1）

作为框架维护者，我希望 CLI dry-run / execute 输出能直接看到 cleanup target truth state 和 target 数量，以便在不打开 artifact 的情况下判断当前 cleanup baseline 是否具备 formal target truth。

**优先级说明**：CLI 是框架操作者的主要入口，如果 terminal output 不暴露 truth state，实际执行时很容易把 `missing` 与 `empty` 混淆。

**独立测试**：在集成测试中通过 CLI 触发 dry-run 与 execute，断言输出包含 `cleanup_targets_state` 以及 target 数量或缺失提示。

**验收场景**：

1. **Given** `cleanup_targets` 缺失，**When** 运行 `program final-proof-archive-project-cleanup --dry-run`，**Then** 输出必须显式提示 `cleanup_targets_state=missing`。
2. **Given** `cleanup_targets` 为空列表或显式列表，**When** 运行执行命令，**Then** 输出必须反映 `empty` 或 `listed`，并显示 target 数量。

---

### 边界情况

- `cleanup_targets` 字段存在但值不是列表时，系统必须视为 invalid truth，而不是自动纠正。
- target entry 缺失 `052` 规定的必填键时，系统必须暴露结构性警告，而不是 silently drop。
- `cleanup_targets` 已列出 target，但 `050` 仍处于 `deferred` 基线时，系统必须继续保持“不做真实 mutation”的 honesty boundary。

## 需求（必填）

### 功能需求

- **FR-001**：系统必须只从 `050` final proof archive project cleanup artifact 的 `cleanup_targets` 字段读取 cleanup target truth。
- **FR-002**：系统必须区分并暴露 `cleanup_targets_state` 的 `missing`、`empty`、`listed` 三种状态。
- **FR-003**：系统必须在 request/result/artifact payload 中保留显式 target 列表，不得基于目录命名、`written_paths`、reports 或 git 状态推断补全。
- **FR-004**：当 `cleanup_targets` 结构非法或 entry 缺失必填键时，系统必须产出结构性警告，且不得把 invalid truth 伪装成可执行 mutation plan。
- **FR-005**：CLI dry-run 与 execute 输出必须暴露 `cleanup_targets_state` 与 target 数量，帮助操作者区分 `missing`、`empty`、`listed`。
- **FR-006**：即使存在显式 `cleanup_targets`，当前 baseline 仍必须保持 `deferred` 结果，不执行真实 workspace cleanup mutation。

### 关键实体（如涉及数据则必填）

- **CleanupTargetsState**：`missing`、`empty`、`listed` 三态 truth surface，用于表达当前 cleanup artifact 是否具备 formal target truth。
- **CleanupTargetEntry**：由 `target_id`、`path`、`target_kind`、`cleanup_action`、`source_artifact`、`justification` 组成的显式 cleanup target 定义。
- **ProjectCleanupArtifactPayload**：`050/053` 链路中的 canonical payload，需继续承载 project cleanup request/result/summaries，并新增/保留 cleanup target truth 信息。

## 成功标准（必填）

### 可度量结果

- **SC-001**：新增单元测试能够覆盖 `cleanup_targets` 的 `missing`、`empty`、`listed` 三态，并在实现前先失败、实现后通过。
- **SC-002**：`ProgramService` 产出的 request/result/artifact payload 可观测到 `cleanup_targets_state` 与显式 target 列表，且不会从隐式信号推断 target。
- **SC-003**：CLI 集成测试验证 dry-run / execute 输出包含 cleanup target truth state 和 target 数量。
- **SC-004**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints` 全部通过。

---
related_doc:
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
