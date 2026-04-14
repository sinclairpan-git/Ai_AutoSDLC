# 执行记录：Program Truth Ledger And Release Audit Baseline

**功能编号**：`140-program-truth-ledger-release-audit-baseline`
**日期**：2026-04-14
**状态**：实现已完成；root truth 已落地；仓库总 release readiness 仍由 truth ledger 判定为 `migration_pending / blocked`

## Batch 2026-04-14-001 | Formal freeze, adversarial review, and framework-order correction

- 起草 `spec.md` 与 `plan.md`，冻结 `closure_state` / `audit_state`、canonical precedence、v1 evidence 边界、migration mode
- 使用 AI-Native expert 与 coding-framework architect 完成两轮对抗评审；首轮回收“不要形成第二真值系统、不要手写总账本、不要让 non-release migration gap 直接假装 release blocker”的关键意见，第二轮确认 `no blocker`
- 用户指出违反框架顺序后，补录 `FD-2026-04-14-004`，新增 `tasks.md`，把口径纠正回 `spec -> plan -> tasks -> execute`
- 将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `140` 推进到 `141`

## Batch 2026-04-14-002 | Truth-ledger schema, service, CLI, and status integration

- 在 `src/ai_sdlc/models/program.py` 扩展 `ProgramManifest` v2 schema，引入 `program / release_targets / capabilities / truth_snapshot`
- 在 `src/ai_sdlc/core/program_service.py` 实现：
  - v2 manifest validation / migration mode
  - release-scope `roles / capability_refs / required_evidence` 校验
  - minimal snapshot 生成（`authoring_hash / source_hashes / snapshot_hash`）
  - `canonical conflict -> audit_state=blocked`
  - `fresh / stale / invalid / migration_pending` 判定
- 在 `src/ai_sdlc/cli/program_cmd.py` 增加 `program truth sync`、`program truth audit`，并让 `program status` 消费 truth ledger
- 在 `src/ai_sdlc/telemetry/readiness.py` 与 `src/ai_sdlc/cli/commands.py` 接入 `truth_ledger` surface，确保 `status --json` 与文本状态面显式暴露 fail-closed 状态
- 在 `src/ai_sdlc/gates/pipeline_gates.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/cli/sub_apps.py` 接入 close gate truth audit hard gate：启用 truth ledger 的仓库在 close/done 时必须经过 `program_truth_audit_ready`
- 在 `program-manifest.yaml` 升级 root schema 为 v2，新增：
  - `program.goal`
  - `release_targets: [frontend-mainline-delivery]`
  - `capabilities.frontend-mainline-delivery`
  - 对应 release-scope specs 的 `roles / capability_refs`
- 显式运行 `program truth sync --execute --yes` 将首份 `truth_snapshot` 写回 root manifest

## Batch 2026-04-14-003 | Focused verification, migration diagnostics, and closure evidence

### 统一验证命令

- `V1`
  - 命令：`uv run pytest tests/unit/test_program_service.py -q`
  - 结果：通过（`236 passed in 7.87s`）
- `V2`
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q -k 'program_validate or program_status_and_plan or bounded_frontend_evidence_class_summary or truth_sync_and_audit_surface_blocked_release_state'`
  - 结果：通过（`6 passed, 127 deselected in 4.30s`）
- `V3`
  - 命令：`uv run pytest tests/integration/test_cli_status.py -q -k 'truth_ledger or capability_closure or bounded_frontend_evidence_class_summary'`
  - 结果：通过（`4 passed, 32 deselected in 3.27s`）
- `V4`
  - 命令：`uv run pytest tests/unit/test_gates.py -q -k 'program_truth_audit_is_not_ready or TestCloseGate or TestDoneGate'`
  - 结果：通过（`5 passed, 67 deselected in 0.69s`）
- `V5`
  - 命令：`uv run ruff check src/ai_sdlc/core/program_service.py src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/cli/commands.py src/ai_sdlc/gates/pipeline_gates.py src/ai_sdlc/core/runner.py src/ai_sdlc/cli/sub_apps.py tests/integration/test_cli_program.py tests/integration/test_cli_status.py tests/unit/test_program_service.py tests/unit/test_gates.py`
  - 结果：通过（`All checks passed!`）
- `V6`
  - 命令：`uv run ai-sdlc program validate`
  - 结果：通过；manifest 为 `PASS`，并显式暴露 37 个 `migration_pending` 缺失 spec entries
- `V7`
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写回 root `truth_snapshot`，当前状态为 `migration_pending`，release capability `frontend-mainline-delivery` 为 `blocked`
- `V8`
  - 命令：`uv run ai-sdlc program truth audit`
  - 结果：按预期失败关闭（exit code `1`）；`snapshot_state=fresh`，`state=migration_pending`，并将 release blocker 与 migration pending 显式暴露
- `V9`
  - 命令：`uv run ai-sdlc status --json`
  - 结果：通过；`truth_ledger` surface 已进入 bounded JSON，包含 `migration_pending_count / migration_pending_specs / migration_suggestions`
- `V10`
  - 命令：`uv run ai-sdlc gate close`
  - 结果：按预期 `RETRY`；当前活跃 work item 不属于 release-scope，因此 close gate 只因 `all_tasks_complete / final_tests_passed` 失败而重试，不再被全局 `migration_pending` 误伤
- `V11`
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过（`verify constraints: no BLOCKERs.`）
- `V12`
  - 命令：`uv run pytest tests/unit/test_program_service.py -q -k 'canonical_conflict or closure_audit_missing' tests/unit/test_gates.py -q -k 'program_truth_audit_is_not_ready'`
  - 结果：通过；对抗评审指出的 `canonical conflict precedence`、`capability_closure_audit missing fail-open`、`close gate release-scope scoping` 已回归锁定

### 代码审查结论（Mandatory）

- 宪章/规格对齐：通过；`140` 没有引入第二套 program truth，也没有夺走 `082/087` 的 field-level canonical owner
- 实现简洁性：通过；truth ledger 的计算集中在 `ProgramService`，CLI/status/gate 只做消费与 fail-closed 接入
- 用户体验：通过；`program truth audit` 与 `status --json` 现在会结构化给出 `migration_pending_count/specs/suggestions`，不要求用户每次全盘人工审计
- 对抗评审修正：已根据 AI-Native 与 framework architect 的 blocker 反馈，补上 `close gate 仅对当前 release-scope spec 消费 truth audit` 与 `canonical conflict 永远落在 blocked 口径`
- 剩余真实状态：仓库整体 release readiness 依旧不是 `ready`，这是 root truth 的显式输出，不是本 work item 遗漏实现
- 结论：无新增 blocker；本 work item 已完成单次 git commit，但当前工作区仍保留允许的 checkpoint 派生物，因此不伪造 clean-tree close-check 结论

### 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：已同步，所有任务项已勾选完成
- `related_plan`（如存在）同步状态：N/A
- 关联 branch/worktree disposition 计划：待最终收口
- 说明：`140` 的 formal docs、实现、manifest v2、truth snapshot、status/readiness/gate 接缝与 focused verification 已在同一批次闭环

### 批次结论

- `140` 已把 root-level truth ledger / release audit baseline 真正落到仓库中，并已接入 status/readiness/close gate
- 当前 root truth 明确告诉我们：仓库仍有 37 个 migration-pending spec entries 尚未纳入 manifest，且 `frontend-mainline-delivery` release capability 仍 blocked；这属于仓库总交付现状，不属于 `140` carrier 缺失

### 归档后动作

- **验证画像**：`code-change`
- **改动范围**：`program-manifest.yaml`、`src/ai_sdlc/models/program.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/telemetry/readiness.py`、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/gates/pipeline_gates.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/cli/sub_apps.py`、`tests/unit/test_program_service.py`、`tests/unit/test_gates.py`、`tests/integration/test_cli_program.py`、`tests/integration/test_cli_status.py`、`specs/140-program-truth-ledger-release-audit-baseline/tasks.md`
- **已完成 git 提交**：是
- **提交哈希**：`latest single-commit close-out (see git history)`
- 当前批次 branch disposition 状态：retained
- 当前批次 worktree disposition 状态：retained
- 是否继续下一批：否；`140` implementation carrier 已完成，后续应转向 root manifest backlog backfill / open capability closure 本身
