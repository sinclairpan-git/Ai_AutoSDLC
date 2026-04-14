# 功能规格：Frontend Evidence Class Verify Validate Status Runtime Closure Baseline

**功能编号**：`129-frontend-evidence-class-verify-validate-status-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已由现有实现满足并完成 focused verification
**输入**：[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md`](../107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md)、[`../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md`](../108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)

> 口径：`129` 是 `120/T23` 的 implementation carrier。它不再发明新的 evidence-class 语义，而是把已经分散落地在 `verify constraints`、`program validate`、`program status`、`status --json` 与 `107/108` backfill 上的现有 runtime 收成同一条 closure slice，明确这些实现已经满足 `083/085/086/088/107/108` 的 truth-order，并把 `120/T23` 从“抽象 implementation carrier”推进到正式工单。

## 问题定义

`083`、`085`、`086`、`088` 已冻结了 evidence-class 的 detection/mirror/status contract，`107`、`108` 又分别把 readiness gate 与历史 metadata backfill 推到了真实 runtime。当前剩下的缺口不是再造一套新逻辑，而是缺少一个明确的 closure carrier 去回答：

- `verify constraints` 的 authoring malformed 检测，是否已经成为 primary truth
- `program validate` 的 manifest mirror drift，是否已经成为 mirror consistency truth
- `program status` / `status --json` 是否只在 bounded summary 边界内重述 upstream truth，而没有越权成 first-detection surface
- `107/108` 的 readiness/backfill 是否已经被纳入同一条 runtime closure，而不是散落的局部补丁

若这层继续留白，`120/T23` 会一直保持 `partial`，reviewer 也无法从 formal 载体直接确认现有实现已经完成哪一段 closure、剩余哪些后继任务仍未关闭。

## 范围

- **覆盖**：
  - 将现有 evidence-class runtime 汇总为 `120/T23` 的正式 implementation carrier
  - 明确 `verify constraints -> program validate -> status surface` 的 truth-order 已由当前实现满足
  - 明确 `107/108` 的 readiness/backfill 已经进入同一条 runtime closure
  - 回链 `120/T23`、推进 `project-state.yaml` 的下一个工单序号
  - 用 focused verification 证明当前 runtime 与 formal contract 一致
- **不覆盖**：
  - 新增 evidence-class 枚举值、mirror schema 或 writeback 行为
  - 改写 `107`/`108` 已完成的 runtime 语义
  - 将 `status --json` 扩张为 cross-program diagnostics dump
  - 处理 `T24` 的 mirror writeback 或 `T25/T33` 的后继闭环

## 已锁定决策

- `verify constraints` 继续是 `frontend_evidence_class_authoring_malformed` 的 primary detection surface
- `program validate` 继续是 `frontend_evidence_class_mirror_drift` 的 owning surface
- `program status` 与 `status --json` 只允许暴露 bounded summary，不得重新定责
- `107` 的 readiness gate 与 `108` 的历史 metadata backfill 视为 `T23` 已依赖并吸收的现有 runtime，而不是额外平行主线
- `129` 只把现有 passing runtime 写实为 closure slice；若后续要做 mirror writeback 或 close-check 补齐，应落到 `T24` 及下游工单

## 功能需求

| ID | 需求 |
|----|------|
| FR-129-001 | `129` 必须明确 `verify constraints` 已实现 `083/085` 要求的 primary authoring detection |
| FR-129-002 | `129` 必须明确 `program validate` 已实现 `086` 要求的 mirror consistency runtime |
| FR-129-003 | `129` 必须明确 `program status` 与 `status --json` 已按 `088` 保持 bounded summary 边界 |
| FR-129-004 | `129` 必须明确 `107/108` 的 readiness gate 与 legacy backfill 已纳入当前 evidence-class runtime closure |
| FR-129-005 | `129` 必须回链 `120/T23`，让抽象 implementation carrier 升级为正式工单 |
| FR-129-006 | `129` 必须用 focused verification 证明 `verify / validate / status` 三条线当前一致 |

## Exit Criteria

- **SC-129-001**：reviewer 可以从 `129` 直接读出 `verify constraints -> program validate -> status surface` 的单一 truth-order
- **SC-129-002**：`120/T23` 不再停留在抽象 implementation carrier 占位
- **SC-129-003**：focused verification 能证明当前 runtime 已满足 `T23` 的接受标准，而不需要再补额外代码语义

---
related_doc:
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
  - "src/ai_sdlc/core/verify_constraints.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/commands.py"
frontend_evidence_class: "framework_capability"
---
