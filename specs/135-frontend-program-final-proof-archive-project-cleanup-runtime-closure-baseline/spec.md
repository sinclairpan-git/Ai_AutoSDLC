# 功能规格：Frontend Program Final Proof Archive Project Cleanup Runtime Closure Baseline

**功能编号**：`135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md`](../050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md)、[`../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`](../051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md)、[`../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md`](../052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md)、[`../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md`](../053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md)、[`../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md`](../054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md)、[`../055-frontend-program-final-proof-archive-cleanup-mutation-eligibility-consumption-baseline/spec.md`](../055-frontend-program-final-proof-archive-cleanup-mutation-eligibility-consumption-baseline/spec.md)、[`../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md`](../056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md)、[`../057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md`](../057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md)、[`../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md`](../058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md)、[`../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md`](../059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md)、[`../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md`](../060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md)、[`../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md`](../061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md)、[`../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md`](../062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md)、[`../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md`](../063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md)、[`../064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md`](../064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`135` 是 `120/T35` 的 implementation carrier。它不重新定义 `050-064` 的 formal truth，而是把已经散落在 cleanup request/result/artifact、CLI 输出与真实 mutation 路径中的实现正式收束到单一 runtime closure，并补齐 `064/FR-064-003` 要求的 fail-closed alignment gate。

## 问题定义

`050-064` 已经冻结了 final proof archive project cleanup 的 canonical cleanup truth：`cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal`、`cleanup_mutation_proposal_approval` 与 `cleanup_mutation_execution_gating` 的 sibling surfaces，以及 `064` 定义的 bounded mutation action matrix。

当前仓库真实状态比 backlog 更前一步：

- `build_frontend_final_proof_archive_project_cleanup_request()` 已能消费 `049`/`050-063` 的 canonical cleanup truth
- `execute_frontend_final_proof_archive_project_cleanup()` 已能真实执行 `thread_archive/archive_thread_report` 与 `spec_dir/remove_spec_dir`
- CLI 与 cleanup artifact 已能回报 aggregate result、written paths、warnings 与 source linkage

但 `120/T35` 仍缺少正式 implementation carrier，导致两类问题：

- backlog 仍把 cleanup 主线视为 `capability_open`，无法从单一 carrier 判断 `050-064` 哪些 truth 已进入 machine truth
- execute 路径对 invalid canonical cleanup alignment 仍存在 fail-open 漏口：即使 `eligibility / preview / approval` 已经报出 invalid artifact warning，真实 mutation 仍可能继续执行

因此 `135` 要解决的是：

- 将 `050-064` cleanup 主线的真实 runtime closure 正式挂到 `T35`
- 固定 cleanup runtime 的已实现边界，避免它继续被误判为“尚未进入 machine truth”
- 补齐 invalid canonical cleanup truth 的 fail-closed execute gate，让真实 mutation 不再绕过 `064/FR-064-003`

## 范围

- **覆盖**：
  - 将 `050-064` 的 cleanup request/result/artifact/CLI/runtime mutation 真值收束为 `T35` 的正式 implementation carrier
  - 固定 canonical cleanup truth 的 single-source consumption 与 bounded mutation action matrix
  - 补齐 invalid canonical cleanup truth 的 execute fail-closed gate
  - 回链 `120/T35`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `135` 推进到 `136`
- **不覆盖**：
  - 改写 `050-064` formal baseline wording
  - 扩张 cleanup action matrix 到 `archive_thread_report` / `remove_spec_dir` 之外
  - 将 cleanup 扩张为 workspace janitor、git cleanup 或更宽的 post-cleanup workflow
  - 推进 `T41/T42` 等 P1 runtime 主线

## 已锁定决策

- cleanup execute 只能消费 canonical cleanup artifact truth，不得从 CLI intent、working tree 状态或 report 文本反推 execution readiness
- cleanup execute 只能在显式确认后运行
- cleanup runtime 只允许 baseline action matrix：
  - `thread_archive/archive_thread_report`
  - `spec_dir/remove_spec_dir`
- cleanup builder / dry-run 不得隐式触发 thread archive materialization；thread archive side effect 仍属于 `T34`
- 如果 canonical cleanup truth 存在 invalid artifact / alignment warning，execute 必须 fail-closed，不能继续真实 mutation

## 功能需求

| ID | 需求 |
|----|------|
| FR-135-001 | `135` 必须明确 `build_frontend_final_proof_archive_project_cleanup_request()`、`execute_frontend_final_proof_archive_project_cleanup()` 与 `write_frontend_final_proof_archive_project_cleanup_artifact()` 是 `050-064` cleanup 主线的唯一实现切入口 |
| FR-135-002 | `135` 必须明确当前 cleanup runtime 已经具备 canonical cleanup truth consumption、bounded mutation execution 与 CLI/artifact 回报能力 |
| FR-135-003 | `135` 必须把 invalid canonical cleanup truth 的 execute fail-open 漏口固定为本批需要关闭的真实 gap |
| FR-135-004 | `135` 必须明确 cleanup execute 只允许在 explicit confirmation 与 canonical truth alignment 同时满足时运行 |
| FR-135-005 | `135` 必须明确 `archive_thread_report` 与 `remove_spec_dir` 仍是当前 baseline 的唯一允许动作 |
| FR-135-006 | `135` 必须回链 `120/T35`，让 cleanup 主线从抽象 backlog 状态升级为正式 implementation carrier |

## Runtime Closure Completion（2026-04-14）

- cleanup request builder 已对接 `cleanup_targets`、`cleanup_target_eligibility`、`cleanup_preview_plan`、`cleanup_mutation_proposal`、`cleanup_mutation_proposal_approval` 与 `cleanup_mutation_execution_gating` 的 canonical truth surfaces。
- cleanup execute 已能在显式确认后真实执行 `archive_thread_report` 与 `remove_spec_dir`，并将 aggregate result、written paths、warnings、remaining blockers 与 source linkage 回写到 canonical cleanup artifact。
- CLI `program final-proof-archive-project-cleanup --execute --yes` 已能呈现真实 cleanup result，而不是继续伪装成 `deferred`。
- 本批补齐了 invalid canonical cleanup truth 的 fail-closed gate：若 cleanup artifact 已经报出 invalid alignment warning，execute 将直接 blocked，而不会继续删除文件/目录。

## Exit Criteria

- **SC-135-001**：reviewer 可以从 `135` 直接读出 `050-064` cleanup 主线已经具备真实 runtime，而不是只剩 docs-only baseline
- **SC-135-002**：`120/T35` 不再停留在没有 formal carrier 的 `capability_open` 占位
- **SC-135-003**：cleanup execute 对 invalid canonical cleanup truth 不再 fail-open
- **SC-135-004**：后续 batch 不会把 `T35` cleanup 与 `T41/T42` 等下游 P1 主线混线

---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "specs/053-frontend-program-final-proof-archive-cleanup-targets-consumption-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
  - "specs/055-frontend-program-final-proof-archive-cleanup-mutation-eligibility-consumption-baseline/spec.md"
  - "specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md"
  - "specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md"
  - "specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md"
  - "specs/059-frontend-program-final-proof-archive-cleanup-mutation-proposal-consumption-baseline/spec.md"
  - "specs/060-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-baseline/spec.md"
  - "specs/061-frontend-program-final-proof-archive-cleanup-mutation-proposal-approval-consumption-baseline/spec.md"
  - "specs/062-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-baseline/spec.md"
  - "specs/063-frontend-program-final-proof-archive-cleanup-mutation-execution-gating-consumption-baseline/spec.md"
  - "specs/064-frontend-program-final-proof-archive-cleanup-mutation-execution-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
