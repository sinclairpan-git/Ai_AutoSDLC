# 功能规格：Frontend P1 Visual A11y Runtime Foundation Closure Baseline

**功能编号**：`137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md`](../071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md)、[`../../src/ai_sdlc/models/frontend_gate_policy.py`](../../src/ai_sdlc/models/frontend_gate_policy.py)、[`../../src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../tests/unit/test_frontend_gate_policy_models.py`](../../tests/unit/test_frontend_gate_policy_models.py)、[`../../tests/unit/test_frontend_gate_verification.py`](../../tests/unit/test_frontend_gate_verification.py)、[`../../tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`../../tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`137` 是 `120/T42` 的 implementation carrier。它不重写 `071` 的 formal truth，而是把当前仓库里已经落地的 visual / a11y foundation runtime 正式收束为 backlog 可消费的单一 closure carrier。

## 问题定义

`071` 早已不只是 docs-only baseline。当前仓库里已经存在一条完整但分散的 runtime 链：

- `build_p1_frontend_gate_policy_visual_a11y_foundation()` 已将 `071` 的 visual/a11y coverage matrix materialize 为 gate policy truth
- `build_frontend_gate_verification_report()` 已将 explicit evidence input、stable empty evidence、actual visual / a11y issues 映射成 gate-compatible checks / blockers / coverage gaps
- `verify constraints` 与 `program` surface 已持续消费同一 truth，并把 visual/a11y feedback 传播到 remediation / writeback / provider 相关用户面
- 对应 unit / integration tests 已覆盖 evidence gap、stable empty、actual issue 与 report-family reuse

因此 `120/T42` 的真实缺口不再是“还没有 visual / a11y runtime foundation”，而是 backlog 仍缺少正式 carrier 来诚实表达：

- `071` 已从 docs-only baseline 推进到真实检查面
- evidence gap / stable empty / actual issue 的 runtime 边界已经成立
- visual / a11y feedback 已继续服从既有 gate/report family，而没有膨胀成第二套质量系统

`137` 的职责就是把这条已存在的 runtime closure 挂回 `T42`，避免 backlog 继续误报为 `capability_open`。

## 范围

- **覆盖**：
  - 回收 `071` 已落地的 visual / a11y runtime foundation truth
  - 固定 evidence gap / stable empty / actual issue 在 runtime 中的边界
  - 固定 visual / a11y feedback 继续复用既有 gate/report family 的事实
  - 回链 `120/T42`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `137` 推进到 `138`
- **不覆盖**：
  - 改写 `071` formal wording
  - 新增浏览器探针、完整 WCAG 平台、视觉回归平台、interaction quality 平台
  - 推进 `005-008` 的 platform meta 主线
  - 扩张 provider/runtime 或 root truth sync

## 已锁定决策

- `071` 的 runtime foundation 继续以 `frontend_gate_policy -> frontend_gate_verification -> verify/program surfaces` 的单链消费
- visual / a11y evidence 只能来自显式 artifact input；不得引入隐式 source discovery
- `missing_input`、`stable_empty`、`issue` 继续保持三态诚实区分
- visual / a11y feedback 继续复用现有 gate/result/report family，不新增第二套 visual quality runtime
- 本批是 closure carrier / backlog honesty 收束，不引入新的 production 行为

## 功能需求

| ID | 需求 |
|----|------|
| FR-137-001 | `137` 必须明确 `071` 已通过现有代码进入真实 runtime，而不是继续停留在 docs-only baseline |
| FR-137-002 | `137` 必须明确 `build_p1_frontend_gate_policy_visual_a11y_foundation()`、`build_frontend_gate_verification_report()` 与 `verify/program` surfaces 共同构成 `T42` 的运行时主链 |
| FR-137-003 | `137` 必须明确 evidence gap、stable empty 与 actual visual/a11y issue 已在 runtime 中被结构化区分 |
| FR-137-004 | `137` 必须明确 visual / a11y feedback 继续复用既有 gate/report family，而没有形成平行系统 |
| FR-137-005 | `137` 必须明确本批 closure 是 backlog/carrier honesty 收束，而不是新增完整 visual regression 或 a11y platform |
| FR-137-006 | `137` 必须回链 `120/T42`，让 `071` 的 runtime foundation 不再被 backlog 表述为 `capability_open` |

## Runtime Closure Completion（2026-04-14）

- `src/ai_sdlc/models/frontend_gate_policy.py` 已 materialize `071` 的 visual foundation / a11y foundation coverage matrix 与 evidence / feedback boundaries。
- `src/ai_sdlc/core/frontend_gate_verification.py` 已将 missing explicit evidence、stable empty evidence、actual issue 区分为 gate-compatible checks、blockers、coverage gaps 与 visual_a11y_evidence_summary。
- `src/ai_sdlc/core/verify_constraints.py` 与 CLI verify surface 已消费同一 visual/a11y truth，并保持 machine-readable exposure。
- `src/ai_sdlc/core/program_service.py` 与 CLI program surface 已把 visual/a11y feedback 连接到 remediation / propagation 链，而没有重写 `071` truth。
- 当前批次不需要新增 production 代码；所做的是将已有 runtime closure 正式收束到 `T42` carrier，并用 fresh verification 重新确认其成立。

## Exit Criteria

- **SC-137-001**：reviewer 可以从 `137` 直接读出 `071` 已进入真实 runtime，而不是继续误判为 docs-only baseline
- **SC-137-002**：`120/T42` 不再停留在缺少 implementation carrier 的 `capability_open`
- **SC-137-003**：evidence gap / stable empty / actual issue 的 runtime 边界有 fresh verification 作为证据
- **SC-137-004**：visual / a11y foundation 与完整质量平台之间的边界仍保持清晰，没有被 closure carrier 擅自放大

---
related_doc:
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/task-execution-log.md"
  - "src/ai_sdlc/models/frontend_gate_policy.py"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/verify_constraints.py"
  - "src/ai_sdlc/core/program_service.py"
  - "tests/unit/test_frontend_gate_policy_models.py"
  - "tests/unit/test_frontend_gate_verification.py"
  - "tests/unit/test_verify_constraints.py"
  - "tests/integration/test_cli_verify_constraints.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
