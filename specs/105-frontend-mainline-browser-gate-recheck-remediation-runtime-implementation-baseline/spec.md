# 功能规格：Frontend Mainline Browser Gate Recheck Remediation Runtime Implementation Baseline

**功能编号**：`105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline`  
**创建日期**：2026-04-13  
**状态**：formal baseline 已冻结；runtime implementation 已完成首批切片  
**输入**：[`../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`](../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_frontend_gate_verification.py`](../../tests/unit/test_frontend_gate_verification.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`105` 是 `104` 的首个 runtime implementation carrier。`104` 冻结的是 browser gate result-binding contract，本身不得改 `src/` / `tests/`；`105` 负责把这份 formal truth 落到当前可用的 execute gate runtime surface：`frontend_gate_verification` 的 decision mapping、`ProgramService` 的 recheck/remediation handoff，以及 CLI status/execute surface 的稳定呈现。`105` 不实现 browser gate replay runtime、auto-fix engine、后台循环或 program 级聚合重构。

## 问题定义

`104` 已明确冻结以下 truth：

- `evidence_missing` / `transient_run_failure` 主导的 browser gate 结果要进入 `recheck_required`
- evidence-backed `actual_quality_blocker` 要进入 `needs_remediation`
- stale bundle、scope mismatch、linkage 缺失与结果不自洽必须 fail-closed 到 `blocked`
- `ProgramFrontendRecheckBinding` 与 `ProgramFrontendRemediationBinding` 必须分离，不能让 `020` 再次猜测 browser gate 结果语义

但当 `104` 冻结完成时，实际仓库仍然存在一个框架冲突：为了把这些 mapping 落到可执行 surface，必须修改 `src/` / `tests/`，而 `104` 的护栏明确禁止这么做。

因此需要 `105` 作为新的 implementation carrier，专门承接已完成的 runtime cut，给以下改动提供合法写面：

- `frontend_gate_verification.py` 中 `BrowserGateExecuteHandoffDecision` 的映射细化
- `program_service.py` 中 recheck/remediation runbook 的分流与 materialization
- `program_cmd.py` 中 CLI status / execute 对 execute gate state 的稳定呈现
- unit / integration regression，锁定 `recheck_required`、`needs_remediation`、fail-closed `blocked` 与 remediation runbook 的行为边界

## 范围

- **覆盖**：
  - 新建 `105` formal docs 与 execution log
  - 在 `src/ai_sdlc/core/frontend_gate_verification.py` 落地 `104` 的 execute-state mapping
  - 在 `src/ai_sdlc/core/program_service.py` 落地 recheck/remediation handoff 与 runbook 分流
  - 在 `src/ai_sdlc/cli/program_cmd.py` 落地 frontend execute gate state 的 CLI surface
  - 在 unit / integration tests 中补齐 recheck、policy artifact gap、actual blocker 与 remediation runbook 的回归
  - 在 `program-manifest.yaml` 注册 `105`，并将 `.ai-sdlc/project/config/project-state.yaml` 推进到 `106`
- **不覆盖**：
  - 改写 `104` 的 docs-only result-binding contract
  - 实现 browser gate 自动重跑、后台 replay orchestration、auto-fix engine 或无限循环
  - 扩张 `ProgramService` 为新的 browser gate source of truth
  - 修改 `102` 的 bundle contract、`103` 的 probe runtime 或 `020` 的 execute baseline vocabulary

## 已锁定决策

- `105` 只实现 `104` 已定义的 mapping truth，不重新定义 readiness vocabulary
- `recheck_required` 只承接可通过补证据或重跑 browser gate 解决的问题；不得吞并 policy artifact 缺失或 scope/linkage 不可信
- `needs_remediation` 只承接 evidence-backed 真实质量问题；不得把 fail-closed `blocked` 伪装成质量 blocker
- fail-closed 的 `blocked` 必须保留 `scope_or_linkage_invalid` / `result_inconsistency` 诊断语义
- remediation runbook 必须保留 `frontend_visual_a11y_policy_artifacts` 这类非 recheck gap，不能被错误转成 replay 请求

## 用户故事与验收

### US-105-1 — Operator 需要 recheck 与 remediation 的运行时分流

作为 **operator**，我希望 browser gate 结束后系统在运行时层面明确告诉我是应该重跑还是修复，这样 `program --execute` 不会把两种语义混成一个“前端失败”。

**验收**：

1. Given `evidence_missing` 或 `transient_run_failure` 主导 browser gate 结果，When runtime 生成 execute decision，Then `execute_gate_state` 必须为 `recheck_required`
2. Given 存在 evidence-backed `actual_quality_blocker`，When runtime 生成 execute decision，Then `execute_gate_state` 必须为 `needs_remediation`

### US-105-2 — Reviewer 需要 fail-closed `blocked` 不被误判为 recheck

作为 **reviewer**，我希望 policy artifact 缺失、source linkage 缺失或结果不自洽在运行时继续保留 fail-closed `blocked`，这样 remediation 和 replay 路径不会被错误放行。

**验收**：

1. Given `frontend_visual_a11y_policy_artifacts` 缺失，When runtime 处理 browser gate 输入，Then 输出必须保持 `blocked` 且 reason 为 `result_inconsistency` 或 `scope_or_linkage_invalid`
2. Given `passed` 与 per-check blocker 自相矛盾，When runtime 绑定结果，Then 不得输出 `ready` 或 `recheck_required`

### US-105-3 — Maintainer 需要 ProgramService 和 CLI 使用同一 handoff truth

作为 **future maintainer**，我希望 `ProgramService` 与 CLI 都消费同一份 frontend execute gate truth，这样 runbook、status 与 execute surface 不会各讲一套。

**验收**：

1. Given frontend state 为 `recheck_required`，When `ProgramService` 构建 handoff，Then 只 materialize recheck binding，不生成 remediation runbook
2. Given frontend state 为 `blocked` 或 `needs_remediation`，When CLI 展示结果，Then 必须暴露 remediation input / hint，而不是 replay 请求

## 功能需求

| ID | 需求 |
|----|------|
| FR-105-001 | `105` 必须作为 `104` 的 runtime implementation carrier，为已完成的 `src/` / `tests/` 改动提供合法写面 |
| FR-105-002 | `src/ai_sdlc/core/frontend_gate_verification.py` 必须将纯 visual/a11y evidence 缺口映射到 `recheck_required` |
| FR-105-003 | `src/ai_sdlc/core/frontend_gate_verification.py` 必须将 policy artifact 缺失、scope/linkage 不可信与结果不自洽保持为 fail-closed `blocked` |
| FR-105-004 | `src/ai_sdlc/core/frontend_gate_verification.py` 必须将 evidence-backed 真实质量问题映射到 `needs_remediation` |
| FR-105-005 | `src/ai_sdlc/core/program_service.py` 必须仅在 `recheck_required` 时 materialize recheck handoff |
| FR-105-006 | `src/ai_sdlc/core/program_service.py` 必须在 `blocked` / `needs_remediation` 时输出 remediation runbook，并保留 policy artifact gaps |
| FR-105-007 | `src/ai_sdlc/cli/program_cmd.py` 必须在 status / execute surface 呈现 frontend execute gate state 与对应 handoff truth |
| FR-105-008 | `tests/unit/test_frontend_gate_verification.py`、`tests/unit/test_program_service.py` 与 `tests/integration/test_cli_program.py` 必须覆盖 `recheck_required`、`needs_remediation`、fail-closed `blocked` 与 remediation runbook 回归 |
| FR-105-009 | `105` 不得实现 browser gate replay runtime、auto-fix engine、后台循环或 program aggregation 重构 |
| FR-105-010 | `105` 只允许写 `frontend_gate_verification.py`、`program_service.py`、`program_cmd.py`、对应 tests、本工单 docs、`program-manifest.yaml` 与 `project-state.yaml` |

## 成功标准

- **SC-105-001**：browser gate `evidence_missing` / `transient_run_failure` 在 runtime 中稳定落到 `recheck_required`
- **SC-105-002**：policy artifact 缺失与 result inconsistency 在 runtime 中稳定保留 `blocked`
- **SC-105-003**：CLI / ProgramService / runbook 对 `recheck_required` 与 `needs_remediation` 的分流一致
- **SC-105-004**：定向 unit / integration 回归通过，且 `uv run ai-sdlc program validate` 与 `uv run ai-sdlc verify constraints` 通过

---
related_doc:
  - "specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_frontend_gate_verification.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
