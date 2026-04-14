# 功能规格：Branch Lifecycle Direct Formal Runtime Closure Baseline

**功能编号**：`139-branch-lifecycle-direct-formal-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../007-branch-lifecycle-truth-guard/spec.md`](../007-branch-lifecycle-truth-guard/spec.md)、[`../007-branch-lifecycle-truth-guard/task-execution-log.md`](../007-branch-lifecycle-truth-guard/task-execution-log.md)、[`../008-direct-formal-workitem-entry/spec.md`](../008-direct-formal-workitem-entry/spec.md)、[`../008-direct-formal-workitem-entry/task-execution-log.md`](../008-direct-formal-workitem-entry/task-execution-log.md)、[`../../src/ai_sdlc/core/branch_inventory.py`](../../src/ai_sdlc/core/branch_inventory.py)、[`../../src/ai_sdlc/core/workitem_traceability.py`](../../src/ai_sdlc/core/workitem_traceability.py)、[`../../src/ai_sdlc/core/workitem_scaffold.py`](../../src/ai_sdlc/core/workitem_scaffold.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`../../tests/unit/test_branch_inventory.py`](../../tests/unit/test_branch_inventory.py)、[`../../tests/unit/test_workitem_scaffold.py`](../../tests/unit/test_workitem_scaffold.py)、[`../../tests/integration/test_cli_workitem_init.py`](../../tests/integration/test_cli_workitem_init.py)

> 口径：`139` 是 `120/T44` 的 implementation carrier。它不重写 `007/008` 的 formal truth，而是把当前仓库里已经落地的 branch lifecycle truth 与 direct-formal entry runtime 正式收束为 backlog 可消费的单一 closure carrier。

## 问题定义

`007` 与 `008` 当前都不是“只有 formal baseline”。现有仓库已经具备一条完整而稳定的 runtime 链：

- `src/ai_sdlc/core/branch_inventory.py`、`src/ai_sdlc/core/workitem_traceability.py`、`src/ai_sdlc/core/close_check.py` 已提供 branch/worktree inventory、associated lifecycle truth、close-stage bounded checks
- `src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/telemetry/readiness.py` 与 `src/ai_sdlc/cli/workitem_cmd.py` 已提供 `workitem branch-check`、`verify constraints`、`status --json`、`doctor` 等 branch lifecycle bounded surfaces
- `src/ai_sdlc/core/workitem_scaffold.py` 与 `src/ai_sdlc/cli/workitem_cmd.py` 已提供 direct-formal scaffold helper 与 `ai-sdlc workitem init`
- `tests/unit/test_branch_inventory.py`、`tests/unit/test_workitem_scaffold.py`、`tests/integration/test_cli_workitem_init.py`、`tests/integration/test_cli_workitem_close_check.py`、`tests/integration/test_cli_status.py`、`tests/integration/test_cli_doctor.py` 已持续锁定 branch lifecycle truth、direct-formal entry、CLI discoverability 与 bounded governance/readiness 边界

因此 `120/T44` 的真实缺口不再是“尚未形成 branch lifecycle/direct-formal runtime surface”，而是 backlog 仍然停在 `formal_only`，缺少一个正式 carrier 来诚实表达：

- `007-008` 已经形成真实 repo truth / entry runtime
- branch lifecycle 与 direct-formal entry 已不再只靠约定或局部 guard
- formal entry 与 branch truth 已能为后续 work item 主链提供稳定边界

`139` 的职责就是把这条已存在的 runtime closure 挂回 `T44`，避免后续继续把 `007/008` 误导成尚未进入 machine truth。

## 范围

- **覆盖**：
  - 回收 `007/008` 已落地的 branch lifecycle truth 与 direct-formal entry runtime
  - 固定 `workitem branch-check`、`close-check`、`verify constraints`、`status --json`、`doctor` 与 `workitem init` 的 closure 边界
  - 固定 branch lifecycle 保持 bounded read-only、direct-formal 保持 single canonical doc set 的事实
  - 回链 `120/T44`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `139` 推进到 `140`
- **不覆盖**：
  - 改写 `007/008` formal wording
  - 新增自动 merge / delete / prune / archive 等 branch mutation
  - 把 branch lifecycle 接入 execute blocker 或扩张为 repo-wide cleanup orchestrator
  - 为 direct-formal 重新生成第二套 canonical docs 或回退到 `docs/superpowers/*` 双轨

## 已锁定决策

- branch lifecycle 继续以 read-only inventory、associated truth、bounded governance/readiness surface 的单链消费为准
- direct-formal 继续以 `specs/<WI>/spec.md + plan.md + tasks.md + task-execution-log.md` 作为单一 canonical doc set
- `workitem init` 继续只生成 canonical formal docs，不生成第二套 design truth
- 本批是 closure carrier / backlog honesty 收束，不引入新的 production 行为

## 功能需求

| ID | 需求 |
|----|------|
| FR-139-001 | `139` 必须明确 `007/008` 已通过现有代码进入真实 runtime，而不是继续停留在 formal baseline |
| FR-139-002 | `139` 必须明确 branch inventory / traceability / close-check / branch-check / readiness surfaces 共同构成 `T44` 的 branch lifecycle 主链 |
| FR-139-003 | `139` 必须明确 direct-formal scaffold helper 与 `workitem init` 已形成稳定 formal entry surface |
| FR-139-004 | `139` 必须明确 branch lifecycle 仍保持 bounded read-only，不引入自动 branch/worktree mutation |
| FR-139-005 | `139` 必须明确 direct-formal entry 仍保持 single canonical doc set，不回退到双轨文档路径 |
| FR-139-006 | `139` 必须回链 `120/T44`，让 `007-008` 不再被 backlog 表述为 `formal_only` |

## Runtime Closure Completion（2026-04-14）

- `src/ai_sdlc/core/branch_inventory.py`、`workitem_traceability.py`、`close_check.py` 已形成 branch/worktree inventory、associated lifecycle truth 与 close-stage bounded truth 主链。
- `src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/telemetry/readiness.py` 与 `src/ai_sdlc/cli/workitem_cmd.py` 已提供 `verify constraints`、`status --json`、`doctor` 与 `workitem branch-check` 的 branch lifecycle bounded surface。
- `src/ai_sdlc/core/workitem_scaffold.py` 与 `src/ai_sdlc/cli/workitem_cmd.py` 已提供 direct-formal scaffold helper、`workitem init` 与 command discovery surface。
- unit 与 integration tests 已覆盖 branch lifecycle inventory/disposition、direct-formal scaffold、CLI init/branch-check/close-check，以及 bounded governance/readiness 边界。
- 当前批次不需要新增 production 代码；所做的是将已有 branch lifecycle/direct-formal runtime closure 正式收束到 `T44` carrier，并用 fresh verification 重新确认其成立。
- 当前 carrier 已完成 `T44` 主链 closure；`120/T44` 继续保留 `partial`，仅表示 tranche/root closure 仍保持保守态，而不是 `139` 仍缺实现 carrier。

## Exit Criteria

- **SC-139-001**：reviewer 可以从 `139` 直接读出 `007/008` 已进入真实 branch lifecycle/direct-formal runtime，而不是继续误判为 formal-only
- **SC-139-002**：`120/T44` 不再停留在缺少 implementation carrier 的 `formal_only`
- **SC-139-003**：`workitem init`、branch lifecycle surfaces 与 focused verification 形成可复核证据
- **SC-139-004**：branch lifecycle 的 read-only 边界与 direct-formal 的 single-canonical 边界仍保持清晰，没有被 closure carrier 擅自放大

---
related_doc:
  - "specs/007-branch-lifecycle-truth-guard/spec.md"
  - "specs/007-branch-lifecycle-truth-guard/task-execution-log.md"
  - "specs/008-direct-formal-workitem-entry/spec.md"
  - "specs/008-direct-formal-workitem-entry/task-execution-log.md"
  - "src/ai_sdlc/core/branch_inventory.py"
  - "src/ai_sdlc/core/workitem_traceability.py"
  - "src/ai_sdlc/core/workitem_scaffold.py"
  - "src/ai_sdlc/core/verify_constraints.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/cli/workitem_cmd.py"
  - "tests/unit/test_branch_inventory.py"
  - "tests/unit/test_workitem_scaffold.py"
  - "tests/integration/test_cli_workitem_init.py"
frontend_evidence_class: "framework_capability"
---
