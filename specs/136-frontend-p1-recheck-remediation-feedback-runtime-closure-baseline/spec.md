# 功能规格：Frontend P1 Recheck Remediation Feedback Runtime Closure Baseline

**功能编号**：`136-frontend-p1-recheck-remediation-feedback-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`136` 是 `120/T41` 的 implementation carrier。它不重写 `066-070` 的 formal truth，而是把已有 runtime 中与 `070/FR-070-006` 冲突的分流修正为 machine truth，并把 `T41` 的真实实现边界固定为单一 carrier。

## 问题定义

`066-070` 已经冻结了 P1 diagnostics / drift 到 remediation feedback 的 formal 边界，尤其 `070` 明确要求：

- frontend readiness 仅在 `READY` 时暴露 `frontend_recheck_handoff`
- readiness 未达 `READY` 时必须暴露 `frontend_remediation_input`
- program surface 需要对 author 诚实表达 remediation 与 recheck 的分流

当前仓库真实状态并非完全缺少 runtime。`ProgramService`、CLI integrate surface、frontend remediation runbook / writeback 已经存在，`120/T41` 的真实缺口是更窄的 consumer mismatch：

- `build_integration_dry_run()` 仍把 `recheck_required` 也路由到 `frontend_recheck_handoff`
- 同一状态下 `frontend_remediation_input` 被错误压制
- author-facing 输出因此把“还没 READY 的 gap / stable empty / browser-gate evidence 缺口”伪装成可直接 recheck 的状态

这会导致 `070` 虽然不是 docs-only baseline，但其最关键的 runtime truth 仍未被诚实消费。

## 范围

- **覆盖**：
  - 修正 `ProgramService` 对 frontend readiness 的 remediation / recheck 分流
  - 固定 `READY -> frontend_recheck_handoff`、`non-READY -> frontend_remediation_input` 的 machine truth
  - 让 CLI integrate surface 与后续 remediation/writeback 链消费同一 truth
  - 回链 `120/T41`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `136` 推进到 `137`
- **不覆盖**：
  - 改写 `066-070` formal wording
  - 扩张 `071` visual / a11y runtime foundation 的检查面
  - 新增浏览器探针规则、视觉基线或更宽的 diagnostics taxonomy

## 已锁定决策

- `frontend_recheck_handoff` 只服务于 frontend readiness 已达 `READY` 的场景
- `recheck_required`、`needs_remediation` 与其他 non-`READY` readiness 必须回到 `frontend_remediation_input`
- remediation input 延续既有 `fix_inputs` / `suggested_actions` / `recommended_commands` 口径，不重新定义 `069` 的 gap 分类
- 浏览器 gate 证据缺口仍可在 remediation input 中推荐 `uv run ai-sdlc program browser-gate-probe --execute`，但它不再被表述成“已经 ready，只差 recheck”

## 功能需求

| ID | 需求 |
|----|------|
| FR-136-001 | `136` 必须明确 `ProgramService.build_integration_dry_run()` 是 `070` remediation/recheck 分流的唯一运行时切入口 |
| FR-136-002 | `136` 必须关闭当前 runtime 将 `recheck_required` 误路由为 `frontend_recheck_handoff` 的 consumer mismatch |
| FR-136-003 | `136` 必须确保 `frontend_recheck_handoff` 仅在 readiness `READY` 时暴露，并继续指向单一 verify surface |
| FR-136-004 | `136` 必须确保 readiness 非 `READY` 时暴露 `frontend_remediation_input`，且继续消费 `069` 的 diagnostics / drift 分类 |
| FR-136-005 | `136` 必须让 stable empty visual/a11y evidence、缺失 visual/a11y evidence 与 browser-gate evidence 缺口都回到 remediation truth，而不是错误进入 recheck handoff |
| FR-136-006 | `136` 必须回链 `120/T41`，让 `066-070` 的 runtime consumer 不再停留在抽象 implementation carrier |

## Runtime Closure Completion（2026-04-14）

- `_build_frontend_recheck_handoff()` 已收窄为只在 `effective_state == READY` 时返回 handoff。
- `_build_frontend_remediation_input()` 已改为仅在 `READY` 时抑制输出，因此 `recheck_required` 与其他 non-`READY` 状态会诚实暴露 remediation input。
- browser gate evidence 缺口现在仍保留 `uv run ai-sdlc program browser-gate-probe --execute` 的建议命令，但整体语义回到 remediation，而不是伪装成 recheck-ready。
- CLI `program integrate --execute` 对 stable empty visual/a11y evidence 的用户面已改为 remediation handoff，与 writeback/provider/runtime preservation 口径保持一致。

## Exit Criteria

- **SC-136-001**：`070` 不再只是 docs-only feedback contract，而是被真实 runtime consumer 诚实消费
- **SC-136-002**：reviewer 可以从 `136` 直接看出 `READY` 与 non-`READY` 的 remediation/recheck 分流已经成立
- **SC-136-003**：program surface 不再把 `recheck_required` 误报成 recheck handoff
- **SC-136-004**：`120/T41` 获得正式 implementation carrier，并把下游边界继续固定到 `T42`

---
related_doc:
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
