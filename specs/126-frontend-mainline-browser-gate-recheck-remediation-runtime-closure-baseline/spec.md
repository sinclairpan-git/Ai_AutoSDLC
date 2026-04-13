# 功能规格：Frontend Mainline Browser Gate Recheck Remediation Runtime Closure Baseline

**功能编号**：`126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 已完成首批闭环
**输入**：[`../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md`](../104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md)、[`../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md`](../105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md)、[`../106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md`](../106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md)、[`../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md`](../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)

> 口径：`126` 是 `120/T14` 的 implementation carrier。它不重写 `104/105/106/125` 的 formal truth，而是把 `125` 已 materialize 的 browser gate artifact 真正接入 `ProgramService`、CLI recheck/remediation handoff 与后续 runbook continuation，使 browser gate 结果不再停留在孤立 `latest.yaml`。

## 问题定义

`125` 已经把 browser gate probe runtime 写成 canonical artifact，但当前主链仍有三个断点：

- `build_status` / `build_integration_dry_run` 仍优先消费旧的 gate verification 结果，browser gate artifact 还不是 execute truth
- `program browser-gate-probe --execute` 只会说 artifact 已 materialize，没有把下一步 recheck/remediation state 直接暴露给 operator
- remediation runbook 还不能把 browser gate artifact 驱动的 recheck continuation 继续串回 `program remediate`

`126` 的目标是补齐这一层闭环：当最新 browser gate artifact 对当前 spec 有效时，它成为 frontend execute gate 的下游真值；recheck 统一落到 `program browser-gate-probe --execute`；scope/linkage 漂移时 fail-closed；没有 browser gate artifact 时继续回退到 `105` 的现有实现。

## 范围

- **覆盖**：
  - 将 browser gate `latest.yaml` 映射为 execute gate decision truth
  - 将 recheck handoff 的下一步命令切换为真实的 browser gate replay 命令
  - 将 remediation runbook / execute 支持 browser gate follow-up command
  - 在 CLI 中直出 browser gate execute gate state / decision reason / next command
  - 对 browser gate artifact 的 scope/linkage mismatch 做 fail-closed
  - 注册 `126` formal carrier，并将 `project-state` 推进到 `127`
- **不覆盖**：
  - 新增 Playwright binary capture、trace 深化、真实 interaction probe materialization
  - 引入自动循环 replay、auto-fix engine 或多 artifact 历史索引
  - 替换 `105` 的 fallback 路径；无 browser gate artifact 时仍沿用原有 readiness 逻辑

## 已锁定决策

- 对当前 spec 有效且结构自洽的 browser gate artifact，优先成为 execute gate source of truth
- browser gate artifact 只要出现 scope/linkage drift、bundle/result inconsistency，就必须 fail-closed 为 `blocked`
- `recheck_required` 的真实 replay 命令固定为 `uv run ai-sdlc program browser-gate-probe --execute`
- remediation runbook 可以把 browser gate replay 作为 follow-up command，但不把它包装成自动修复已完成
- `126` 只补 artifact consumption / handoff closure，不宣称 browser gate probes 已经完全实现

## 功能需求

| ID | 需求 |
|----|------|
| FR-126-001 | `frontend_gate_verification.py` 必须能把 browser gate artifact bundle 映射为 `ready / blocked / recheck_required / needs_remediation` |
| FR-126-002 | `program_service.py` 必须在 browser gate artifact 对当前 spec 生效时，将其作为 execute gate truth 使用 |
| FR-126-003 | browser gate artifact 出现 `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 漂移时，系统必须 fail-closed 为 `blocked` |
| FR-126-004 | `ProgramFrontendRecheckHandoff` 对 browser gate artifact 场景必须输出 `uv run ai-sdlc program browser-gate-probe --execute` |
| FR-126-005 | `ProgramFrontendRemediationInput` 与 remediation execute 必须支持 browser gate follow-up command continuation |
| FR-126-006 | `program browser-gate-probe` CLI 必须展示 execute gate state、decision reason 与下一步命令，而不是停留在 baseline wording |
| FR-126-007 | 没有 browser gate artifact 时，系统必须保留 `105` 既有 fallback 行为 |

## Exit Criteria

- **SC-126-001**：browser gate artifact 驱动的 `recheck_required / needs_remediation / blocked` 能被 `ProgramService` 稳定消费
- **SC-126-002**：`program browser-gate-probe`、`program integrate`、`program remediate` 至少能对 browser gate artifact 驱动场景给出一致的下一步命令
- **SC-126-003**：scope/linkage drift 在 runtime 中稳定 fail-closed，不再放行为旧 readiness 或 advisory

---
related_doc:
  - "specs/104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline/spec.md"
  - "specs/105-frontend-mainline-browser-gate-recheck-remediation-runtime-implementation-baseline/spec.md"
  - "specs/106-frontend-mainline-browser-gate-evidence-class-footer-normalization-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
