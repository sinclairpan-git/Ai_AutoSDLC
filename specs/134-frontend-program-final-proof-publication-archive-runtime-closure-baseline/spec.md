# 功能规格：Frontend Program Final Proof Publication And Archive Runtime Closure Baseline

**功能编号**：`134-frontend-program-final-proof-publication-archive-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md`](../041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md)、[`../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md`](../042-frontend-program-persisted-write-proof-artifact-baseline/spec.md)、[`../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md`](../043-frontend-program-final-proof-publication-orchestration-baseline/spec.md)、[`../044-frontend-program-final-proof-publication-artifact-baseline/spec.md`](../044-frontend-program-final-proof-publication-artifact-baseline/spec.md)、[`../045-frontend-program-final-proof-closure-orchestration-baseline/spec.md`](../045-frontend-program-final-proof-closure-orchestration-baseline/spec.md)、[`../046-frontend-program-final-proof-closure-artifact-baseline/spec.md`](../046-frontend-program-final-proof-closure-artifact-baseline/spec.md)、[`../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md`](../047-frontend-program-final-proof-archive-orchestration-baseline/spec.md)、[`../048-frontend-program-final-proof-archive-artifact-baseline/spec.md`](../048-frontend-program-final-proof-archive-artifact-baseline/spec.md)、[`../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md`](../049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`134` 是 `120/T34` 的 implementation carrier。它承接 `041-049` 已冻结的 persisted write proof、final proof publication、final proof closure、final proof archive 与 thread archive formal truth，目的不是发明新的 cleanup 语义，而是把当前仍停留在 `deferred` 的 final proof / archive 主线收束成下一批明确可执行的 runtime closure slice，并保持与 `T35` cleanup 主线分界清楚。

## 问题定义

`041-049` 已经冻结了 persisted write proof orchestration/artifact、final proof publication orchestration/artifact、final proof closure orchestration/artifact、final proof archive orchestration/artifact 与 thread archive baseline 的 formal truth。当前真实缺口仍在 execute 面：

- `program persisted-write-proof --execute --yes` 仍返回 `deferred`
- `program final-proof-publication --execute --yes` 仍返回 `deferred`
- `program final-proof-closure --execute --yes` 仍返回 `deferred`
- `program final-proof-archive --execute --yes` 仍返回 `deferred`
- `program final-proof-archive-thread-archive --execute --yes` 仍返回 `deferred`

也就是说，`042/044/046/048/049` 已有 canonical artifact / result contract，但上游 execute truth 仍未进入 bounded runtime closure。若继续缺失：

- `120/T34` 会一直停留在“已有 contract、runtime 仍 deferred”的抽象 implementation carrier
- final proof publication / closure / archive / thread archive 很容易与 `T35` cleanup 混线
- reviewer 无法从单一 formal carrier 判断 proof/publication/archive 当前哪些能力已是 machine truth，哪些仍只是 downstream contract

## 范围

- **覆盖**：
  - 将 `041-049` 的 persisted write proof、final proof publication、final proof closure、final proof archive、thread archive 主线收束为 `120/T34` 的正式 implementation carrier
  - 明确当前真实 gap 位于 execute/orchestration runtime，而不是 formal artifact contract 缺失
  - 固定 `T34` 的受控实现边界：proof/publication/archive/thread archive 到此为止，不越过到 project cleanup
  - 回链 `120/T34`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `134` 推进到 `135`
- **不覆盖**：
  - `050+` cleanup runtime、workspace cleanup、额外 mutation 或更宽的 conversation/archive side effect
  - 改写 `041-049` 已冻结的上游 contract
  - 把 `134` 误写成 `T35` 或后续总闭环

## 已锁定决策

- `134` 只承接 `041-049`，不吸收 cleanup 主线
- proof/publication/closure/archive/thread archive 继续要求显式确认，不引入默认 side effect
- 后续实现必须以 fail-closed 方式消费上游 artifact truth 与 remaining blockers，不得把 deferred/missing upstream 偷渡成 skipped/completed
- `T35` 继续单独承接 final proof archive project cleanup

## 功能需求

| ID | 需求 |
|----|------|
| FR-134-001 | `134` 必须明确 `build_frontend_persisted_write_proof_request()`、`execute_frontend_persisted_write_proof()` 与 `write_frontend_persisted_write_proof_artifact()` 是 `041-042` 的唯一实现切入口 |
| FR-134-002 | `134` 必须明确 `build_frontend_final_proof_publication_request()`、`execute_frontend_final_proof_publication()` 与 `write_frontend_final_proof_publication_artifact()` 是 `043-044` 的唯一实现切入口 |
| FR-134-003 | `134` 必须明确 `build_frontend_final_proof_closure_request()`、`execute_frontend_final_proof_closure()` 与 `write_frontend_final_proof_closure_artifact()` 是 `045-046` 的唯一实现切入口 |
| FR-134-004 | `134` 必须明确 `build_frontend_final_proof_archive_request()`、`execute_frontend_final_proof_archive()`、`write_frontend_final_proof_archive_artifact()` 与 `build/execute_frontend_final_proof_archive_thread_archive_*()` 是 `047-049` 的唯一实现切入口 |
| FR-134-005 | `134` 必须明确上述 execute surfaces 当前仍停留在 `deferred`，这是 `T34` 需要关闭的真实 runtime gap |
| FR-134-006 | `134` 必须明确 `T34` 的完成口径只到 bounded proof/publication/archive/thread archive truth，不包含 cleanup |
| FR-134-007 | `134` 必须明确后续实现优先补齐 runtime gating、bounded materialization/result truth 与 thread archive honesty，而不是扩张到 cleanup |
| FR-134-008 | `134` 必须回链 `120/T34`，让抽象 implementation carrier 升级为正式工单 |

## Exit Criteria

- **SC-134-001**：reviewer 可以从 `134` 直接读出 `041-049` 的真实 gap 在 execute/orchestration runtime，而不是 formal contract
- **SC-134-002**：`120/T34` 不再停留在抽象 implementation carrier 占位
- **SC-134-003**：后续实现不会把 `T34` 与 `T35` cleanup 边界混淆

## Runtime Closure Completion（2026-04-14）

- `execute_frontend_persisted_write_proof()`、`execute_frontend_final_proof_publication()`、`execute_frontend_final_proof_closure()`、`execute_frontend_final_proof_archive()` 与 `execute_frontend_final_proof_archive_thread_archive()` 已按 `041-049` contract 收束为显式确认、upstream `completed`、blocker-free 三重 fail-closed gate。
- 上述 execute surfaces 现在只在显式执行路径下 materialize bounded step files，分别落到 persisted write proof、final proof publication、final proof closure、final proof archive 与 thread archive 的 canonical `steps/` 目录。
- `T34` 与 `T35` 的边界已固定：cleanup request / dry-run 只评估 thread archive truth，不再隐式 materialize thread archive step files；任何 thread archive side effect 仍要求显式走 `final-proof-archive-thread-archive --execute --yes`。
- focused verification 已覆盖 blocker-carrying upstream artifact、`required=False` 手工绕过、显式 `steps=[]` 空 artifact 与 cleanup builder side-effect 回归面，确保 `041-049` 的 runtime truth 不再停留在 `deferred` 占位。

---
related_doc:
  - "specs/041-frontend-program-persisted-write-proof-orchestration-baseline/spec.md"
  - "specs/042-frontend-program-persisted-write-proof-artifact-baseline/spec.md"
  - "specs/043-frontend-program-final-proof-publication-orchestration-baseline/spec.md"
  - "specs/044-frontend-program-final-proof-publication-artifact-baseline/spec.md"
  - "specs/045-frontend-program-final-proof-closure-orchestration-baseline/spec.md"
  - "specs/046-frontend-program-final-proof-closure-artifact-baseline/spec.md"
  - "specs/047-frontend-program-final-proof-archive-orchestration-baseline/spec.md"
  - "specs/048-frontend-program-final-proof-archive-artifact-baseline/spec.md"
  - "specs/049-frontend-program-final-proof-archive-thread-archive-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
