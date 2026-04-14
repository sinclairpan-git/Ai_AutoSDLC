# 功能规格：Frontend Runtime Attachment Verify Gate Readiness Closure Baseline

**功能编号**：`128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 已完成首批 verify/gate/readiness 闭环
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../016-frontend-enterprise-vue2-provider-baseline/spec.md`](../016-frontend-enterprise-vue2-provider-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../127-frontend-contract-observation-producer-runtime-closure-baseline/spec.md`](../127-frontend-contract-observation-producer-runtime-closure-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py`](../../src/ai_sdlc/core/frontend_contract_runtime_attachment.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/verify_cmd.py`](../../src/ai_sdlc/cli/verify_cmd.py)

> 口径：`128` 是 `120/T22` 的 implementation carrier。它不重写 `014-018` 的 formal truth，而是把已经存在的 runtime attachment helper 真正接进 `verify constraints`、frontend gate prerequisite 与 program/frontend readiness 这几条运行链，确保 active `spec_dir` 的 runtime scope、artifact attachment 与 gate/readiness 判定不再分裂成多套本地真值。

## 问题定义

`014` 已冻结 frontend contract runtime attachment 的 scope / freshness / write-policy 约束，`015-018` 又冻结了 frontend kernel/provider/generation/gate 的上游 formal contract。但当前仓库在 `127` 之后仍残留一处关键断层：

- `ProgramService` 已经消费 runtime attachment helper，`verify constraints` 却仍然自己拼 `spec_dir` 路径读取 observations
- active `spec_dir` unresolved 时，verify/gate 侧会把 runtime scope failure 漏掉，导致 JSON / CLI / gate context 无法共享同一条 truth
- verify JSON 只暴露 frontend contract/gate report，不暴露 runtime attachment summary，operator 无法机器读取 attachment status

`128` 的目标是把 runtime attachment helper 变成 verify/gate/readiness 共同依赖的唯一 attachment truth：在 active `012/018` scope 上统一产出 attachment summary，并把 scope failure fail-closed 地投影进 verify gate；同时保持现有 attached artifact PASS 语义不被 freshness advisory 误伤。

## 范围

- **覆盖**：
  - `verify constraints` 改为基于 runtime attachment helper 解析 frontend observations
  - verify gate context / `verify constraints --json` 暴露 `frontend_contract_runtime_attachment`
  - active `spec_dir` unresolved / scope failure 必须进入 verify gate blockers 与 coverage gaps
  - frontend gate prerequisite 与 program/frontend readiness 继续复用同一条 attachment truth
  - 将 `T22` implementation carrier 注册进 backlog/project-state
- **不覆盖**：
  - 新增 observation artifact schema 或 writeback 行为
  - 扩展 browser recheck command surface
  - 改变 runtime attachment freshness advisory 的 formal 语义
  - 补齐 `T23/T25/T33` 的下游 evidence/status/report 主线

## 已锁定决策

- verify/gate 只在 scope failure 上把 runtime attachment 升格为 gate blocker；freshness 继续保留在 attachment summary 中诚实暴露，不改变既有 PASS 语义
- active work item 识别优先使用 `linked_wi_id`，再 fallback 到 checkpoint `feature.id/spec_dir`，避免 `specs/unknown` 时 runtime attachment 被错误跳过
- verify JSON 新增 `frontend_contract_runtime_attachment` 顶层字段，不重排既有 `verification_gate.sources`
- frontend gate prerequisite 继续通过 `build_frontend_gate_verification_report()` 间接消费 attachment truth，不再在 verify 层重复实现 observation loader

## 功能需求

| ID | 需求 |
|----|------|
| FR-128-001 | `verify constraints` 必须通过 runtime attachment helper 解析 active `012/018` 的 frontend observation attachment |
| FR-128-002 | active `spec_dir` unresolved、outside-root 或等价 scope failure 时，verify gate 必须 fail-closed，并暴露 `frontend_contract_runtime_scope` |
| FR-128-003 | `build_verification_gate_context()` 与 `verify constraints --json` 必须输出 `frontend_contract_runtime_attachment` 机器真值 |
| FR-128-004 | frontend gate prerequisite 与 program/frontend readiness 对同一 active scope 必须共享同一份 attachment truth-order |
| FR-128-005 | attached canonical artifact 的现有 PASS/RETRY 语义不得因为 runtime freshness advisory 被无意改写 |
| FR-128-006 | `128` 必须保持 `012/018` sample self-check 链路可运行，并让 unresolved scope 的 CLI JSON 可被下游 report/compatibility surface 直接消费 |

## Exit Criteria

- **SC-128-001**：`verify constraints --json` 能稳定暴露 `frontend_contract_runtime_attachment`，operator 不再需要自己推断 attachment 状态
- **SC-128-002**：active `012/018` 的 unresolved scope 会直接进入 verify gate 的 blocker/coverage gap，不再出现假 PASS
- **SC-128-003**：frontend gate prerequisite、verify summary 与 program/frontend readiness 对同一 canonical artifact 不再各自实现独立 attachment loader

---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/127-frontend-contract-observation-producer-runtime-closure-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_contract_runtime_attachment.py"
  - "src/ai_sdlc/core/verify_constraints.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/verify_cmd.py"
frontend_evidence_class: "framework_capability"
---
