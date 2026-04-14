# 功能规格：Frontend Program Registry, Governance And Persistence Runtime Closure Baseline

**功能编号**：`133-frontend-program-registry-governance-persistence-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime gap 已定位，待 implementation batch 补齐
**输入**：[`../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md`](../032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md)、[`../033-frontend-program-guarded-registry-orchestration-baseline/spec.md`](../033-frontend-program-guarded-registry-orchestration-baseline/spec.md)、[`../034-frontend-program-guarded-registry-artifact-baseline/spec.md`](../034-frontend-program-guarded-registry-artifact-baseline/spec.md)、[`../035-frontend-program-broader-governance-orchestration-baseline/spec.md`](../035-frontend-program-broader-governance-orchestration-baseline/spec.md)、[`../036-frontend-program-broader-governance-artifact-baseline/spec.md`](../036-frontend-program-broader-governance-artifact-baseline/spec.md)、[`../037-frontend-program-final-governance-orchestration-baseline/spec.md`](../037-frontend-program-final-governance-orchestration-baseline/spec.md)、[`../038-frontend-program-final-governance-artifact-baseline/spec.md`](../038-frontend-program-final-governance-artifact-baseline/spec.md)、[`../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md`](../039-frontend-program-writeback-persistence-orchestration-baseline/spec.md)、[`../040-frontend-program-writeback-persistence-artifact-baseline/spec.md`](../040-frontend-program-writeback-persistence-artifact-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`133` 是 `120/T33` 的 implementation carrier。它当前不宣称 `032-040` 已经完成 runtime closure，而是把 guarded registry、broader governance、final governance、writeback persistence 的真实 deferred gap、受控实现边界与下游依赖固定成同一条执行切片，避免后续实现时把 `T33`、`T34`、`T35` 混成一条失控总链。

## 问题定义

`032-040` 已经冻结了 cross-spec writeback artifact、guarded registry orchestration/artifact、broader governance orchestration/artifact、final governance orchestration/artifact 与 writeback persistence orchestration/artifact 的 formal truth。当前真实缺口仍在 execute 面：

- `program guarded-registry --execute --yes` 仍返回 `deferred`
- `program broader-governance --execute --yes` 仍返回 `deferred`
- `program final-governance --execute --yes` 仍返回 `deferred`
- `program writeback-persistence --execute --yes` 仍返回 `deferred`

如果这一层继续空缺，`120/T33` 会长期停留在抽象 implementation carrier 占位；`T34` 的 final proof publication / archive 主线也拿不到稳定的 persisted truth 上游输入。

## 范围

- **覆盖**：
  - 将 `032-040` 的 guarded registry、broader governance、final governance、writeback persistence 主线收束为 `120/T33` 的正式 implementation carrier
  - 明确当前 runtime gap 位于 execute/orchestration 本身，而不是 artifact contract 缺失
  - 固定 `T33` 的受控实现边界：只补 registry/governance/persistence，不越过到 final proof publication / archive / cleanup
  - 回链 `120/T33`、推进 `project-state.yaml` 的下一个工单序号
- **不覆盖**：
  - persisted write proof、final proof publication / closure / archive、thread archive、cleanup runtime
  - 外部发布、开放式 workspace mutation 或更宽的自动代码交付语义
  - 把 `133` 误写成 `T34/T35` 的总闭环

## 已锁定决策

- `133` 只承接 `032-040`，不吸收 `041-064`
- guarded registry / governance / persistence 继续要求显式确认，不引入默认 side effect
- 后续实现只允许写出 bounded registry/governance/persistence truth，不得提前宣称 final proof 已完成
- `T34` 继续承接 persisted write proof 与 final proof publication / archive 主线

## 功能需求

| ID | 需求 |
|----|------|
| FR-133-001 | `133` 必须明确 `build_frontend_guarded_registry_request()`、`execute_frontend_guarded_registry()` 与 `write_frontend_guarded_registry_artifact()` 是 `033-034` 的唯一实现切入口 |
| FR-133-002 | `133` 必须明确 `build_frontend_broader_governance_request()`、`execute_frontend_broader_governance()` 与 `write_frontend_broader_governance_artifact()` 是 `035-036` 的唯一实现切入口 |
| FR-133-003 | `133` 必须明确 `build_frontend_final_governance_request()`、`execute_frontend_final_governance()` 与 `write_frontend_final_governance_artifact()` 是 `037-038` 的唯一实现切入口 |
| FR-133-004 | `133` 必须明确 `build_frontend_writeback_persistence_request()`、`execute_frontend_writeback_persistence()` 与 `write_frontend_writeback_persistence_artifact()` 是 `039-040` 的唯一实现切入口 |
| FR-133-005 | `133` 必须记录当前上述 execute surfaces 仍停留在 `deferred`，并要求后续实现将其推进到 bounded runtime truth |
| FR-133-006 | `133` 必须明确 `T33` 的完成口径只到 persisted truth 上游 ready，不包含 final proof publication / archive |
| FR-133-007 | `133` 必须回链 `120/T33`，让抽象 implementation carrier 升级为正式工单 |

## Exit Criteria

- **SC-133-001**：reviewer 可以从 `133` 直接读出 `032-040` 的当前 gap 在 execute/orchestration，而不是 artifact contract
- **SC-133-002**：`120/T33` 不再停留在“implementation carrier”占位文字
- **SC-133-003**：后续实现不会把 `T33` 与 `T34/T35` 边界混淆

---
related_doc:
  - "specs/032-frontend-program-cross-spec-writeback-artifact-baseline/spec.md"
  - "specs/033-frontend-program-guarded-registry-orchestration-baseline/spec.md"
  - "specs/034-frontend-program-guarded-registry-artifact-baseline/spec.md"
  - "specs/035-frontend-program-broader-governance-orchestration-baseline/spec.md"
  - "specs/036-frontend-program-broader-governance-artifact-baseline/spec.md"
  - "specs/037-frontend-program-final-governance-orchestration-baseline/spec.md"
  - "specs/038-frontend-program-final-governance-artifact-baseline/spec.md"
  - "specs/039-frontend-program-writeback-persistence-orchestration-baseline/spec.md"
  - "specs/040-frontend-program-writeback-persistence-artifact-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
