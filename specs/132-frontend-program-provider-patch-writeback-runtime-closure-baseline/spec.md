# 功能规格：Frontend Program Provider, Patch Apply And Cross-Spec Writeback Runtime Closure Baseline

**功能编号**：`132-frontend-program-provider-patch-writeback-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；本批已补齐 runtime closure 并完成 focused verification
**输入**：[`../025-frontend-program-provider-handoff-baseline/spec.md`](../025-frontend-program-provider-handoff-baseline/spec.md)、[`../026-frontend-program-guarded-provider-runtime-baseline/spec.md`](../026-frontend-program-guarded-provider-runtime-baseline/spec.md)、[`../027-frontend-program-provider-runtime-artifact-baseline/spec.md`](../027-frontend-program-provider-runtime-artifact-baseline/spec.md)、[`../028-frontend-program-provider-patch-handoff-baseline/spec.md`](../028-frontend-program-provider-patch-handoff-baseline/spec.md)、[`../029-frontend-program-guarded-patch-apply-baseline/spec.md`](../029-frontend-program-guarded-patch-apply-baseline/spec.md)、[`../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md`](../030-frontend-program-provider-patch-apply-artifact-baseline/spec.md)、[`../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md`](../031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`132` 是 `120/T32` 的 implementation carrier。它不再引入新的 registry/governance 语义，而是把 `025-031` 已经分散落地在 provider handoff、guarded provider runtime、patch apply 与 cross-spec writeback 上的现有 runtime 收成同一条 closure slice，明确 `T32` 要求的 provider invocation / patch apply / cross-spec writeback 主线已经进入真实运行面。

## 问题定义

`025-031` 已经分别冻结了 provider handoff、guarded provider runtime、runtime artifact、patch handoff、guarded patch apply、patch apply artifact 与 cross-spec writeback orchestration 的 formal truth。此前仓库缺的不是 CLI surface，而是这些 surface 背后的真实执行链：

- `program provider-runtime --execute --yes` 仍停留在 `deferred`，handoff payload 没有真正进入 provider runtime
- `program provider-patch-apply --execute --yes` 仍停留在 `deferred`，没有真实 apply engine 写出受控结果
- `program cross-spec-writeback --execute --yes` 仍停留在 `deferred`，没有真实跨 spec writeback 文件

如果这层继续空缺，`120/T32` 会一直停留在“已有 handoff / artifact contract，但 runtime 仍是 deferred baseline”的抽象占位；reviewer 也无法从 formal 载体判断哪些能力已经成为当前 machine truth，哪些仍应留给 `T33+` 的 registry/governance/persistence 主线。

## 范围

- **覆盖**：
  - 将 `025-031` 已落地的 provider runtime、patch apply、cross-spec writeback 收束为 `120/T32` 的正式 implementation carrier
  - 明确 remediation writeback -> provider handoff -> provider runtime -> patch apply -> cross-spec writeback 已形成真实执行链
  - 明确 guarded provider runtime 不再返回 `deferred`，而是生成 concrete patch summaries
  - 明确 guarded patch apply 会显式写出受控 step 文件到 `.ai-sdlc/memory/frontend-provider-patch-apply/steps/*.md`
  - 明确 cross-spec writeback 会显式写出各 spec 的 canonical writeback receipt `frontend-provider-writeback.md`
  - 回链 `120/T32`、推进 `project-state.yaml` 的下一个工单序号
  - 用 focused verification 证明 provider/apply/writeback 当前一致
- **不覆盖**：
  - 新增 guarded registry、broader governance、final governance 或 persisted truth 主线
  - 将 bounded provider/apply/writeback 扩张成默认 side effect 或开放式 code rewrite engine
  - 引入外部 provider 网络调用或更宽的自动页面改写协议
  - 把 `132` 误写成 `T33/T34/T41` 之后的 program automation 总闭环

## 已锁定决策

- provider runtime 继续需要显式确认，但执行后不再返回 `deferred`；当前实现以 bounded 内建 patch-plan 生成器收敛 provider invocation
- patch apply 继续只消费 readonly handoff truth，并将结果写到受控 memory step files，而不是直接扩张成开放式文件改写器
- cross-spec writeback 继续只把 apply 结果写回各 spec 的 canonical bounded receipt，不前推到 registry/governance
- `132` 只把现有 passing runtime 写实为 closure slice；registry/governance/persistence 仍留给 `T33`

## 功能需求

| ID | 需求 |
|----|------|
| FR-132-001 | `132` 必须明确 `build_frontend_provider_runtime_request()` 与 `execute_frontend_provider_runtime()` 已满足 `025-027` 所要求的 provider handoff consume、guarded runtime 与 runtime artifact truth |
| FR-132-002 | `132` 必须明确 `execute_frontend_provider_runtime()` 不再返回纯 `deferred`，而是生成 concrete patch summaries 与完成态 source linkage |
| FR-132-003 | `132` 必须明确 `build_frontend_provider_patch_apply_request()` 与 `execute_frontend_provider_patch_apply()` 已满足 `028-030` 所要求的 patch handoff consume、真实 apply engine 与 apply artifact truth |
| FR-132-004 | `132` 必须明确 patch apply execute 会显式写出 bounded step files，并通过 artifact 暴露 written paths |
| FR-132-005 | `132` 必须明确 `build_frontend_cross_spec_writeback_request()` 与 `execute_frontend_cross_spec_writeback()` 已满足 `031` 所要求的 guarded orchestration 与真实跨 spec writeback |
| FR-132-006 | `132` 必须明确 cross-spec writeback execute 会显式写出 spec-level `frontend-provider-writeback.md` receipt |
| FR-132-007 | `132` 必须回链 `120/T32`，让抽象 implementation carrier 升级为正式工单 |
| FR-132-008 | `132` 必须用 focused verification 证明 provider/apply/writeback 当前 runtime 一致 |

## Exit Criteria

- **SC-132-001**：reviewer 可以从 `132` 直接读出 `025-031` 已从 handoff/artifact baseline 进入真实 provider/apply/writeback runtime
- **SC-132-002**：`120/T32` 不再停留在抽象 implementation carrier 占位
- **SC-132-003**：focused verification 能证明 `T32` 当前缺口主要是 formal carrier 缺失，而非 provider/apply/writeback 主线未实现

---
related_doc:
  - "specs/025-frontend-program-provider-handoff-baseline/spec.md"
  - "specs/026-frontend-program-guarded-provider-runtime-baseline/spec.md"
  - "specs/027-frontend-program-provider-runtime-artifact-baseline/spec.md"
  - "specs/028-frontend-program-provider-patch-handoff-baseline/spec.md"
  - "specs/029-frontend-program-guarded-patch-apply-baseline/spec.md"
  - "specs/030-frontend-program-provider-patch-apply-artifact-baseline/spec.md"
  - "specs/031-frontend-program-cross-spec-writeback-orchestration-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
