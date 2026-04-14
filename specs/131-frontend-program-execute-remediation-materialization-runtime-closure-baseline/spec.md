# 功能规格：Frontend Program Execute, Remediation And Materialization Runtime Closure Baseline

**功能编号**：`131-frontend-program-execute-remediation-materialization-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已由现有实现满足并完成 focused verification
**输入**：[`../019-frontend-program-orchestration-baseline/spec.md`](../019-frontend-program-orchestration-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../021-frontend-program-remediation-runtime-baseline/spec.md`](../021-frontend-program-remediation-runtime-baseline/spec.md)、[`../022-frontend-governance-materialization-runtime-baseline/spec.md`](../022-frontend-governance-materialization-runtime-baseline/spec.md)、[`../023-frontend-program-bounded-remediation-execute-baseline/spec.md`](../023-frontend-program-bounded-remediation-execute-baseline/spec.md)、[`../024-frontend-program-bounded-remediation-writeback-baseline/spec.md`](../024-frontend-program-bounded-remediation-writeback-baseline/spec.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`131` 是 `120/T31` 的 implementation carrier。它不再引入新的 program automation 语义，而是把 `019-024` 已经分散落地在 `ProgramService`、`program integrate --execute`、`program remediate`、bounded governance materialization command 与 remediation writeback artifact 上的现有 runtime 收成同一条 closure slice，明确 `T31` 要求的 execute/remediation/materialization 主线已经进入真实运行面。

## 问题定义

`019-024` 已经分别冻结了 orchestration、execute gate、remediation runtime、materialization command surface、bounded remediation execute 与 remediation writeback 的 formal truth。当前缺的不是再补一层新 runtime，而是缺少一个总 carrier 去回答：

- `program integrate --execute` 是否已经真实消费 per-spec frontend readiness，而不只是 dry-run 文案
- remediation hint 是否已经进入 bounded runbook / execute / writeback 链，而不只是 formal handoff
- `022` 定义的 materialization command surface 是否已经被 runtime consumer 正式吸收，而不是只存在于 spec 文本

如果这层继续空缺，`120/T31` 会长期停留在抽象 implementation carrier 占位；reviewer 也无法从 formal 载体直接判断哪些能力已经是当前 machine truth，哪些仍应留给 `T32+` 的 provider/apply/cross-spec writeback 主线。

## 范围

- **覆盖**：
  - 将 `019-024` 已落地的 execute gate、recheck handoff、remediation runbook、bounded execute、materialization command consume 与 writeback artifact 收束为 `120/T31` 的正式 implementation carrier
  - 明确 `program integrate --execute` 已成为 frontend execute preflight 的真实 consumer
  - 明确 `program remediate` 已形成 bounded remediation runbook、显式确认执行与 canonical writeback artifact
  - 明确 `uv run ai-sdlc rules materialize-frontend-mvp` 已被 remediation runtime 作为受控 command consume
  - 回链 `120/T31`、推进 `project-state.yaml` 的下一个工单序号
  - 用 focused verification 证明 execute/remediation/materialization/writeback 当前一致
- **不覆盖**：
  - 新增 provider invocation、patch apply、cross-spec writeback、guarded registry 或 persisted write proof
  - 改写 `019-024` 的既有 formal truth 或重新定义 remediation boundary
  - 将 bounded remediation execute 扩张成默认 `program integrate --execute` side effect
  - 把 `131` 误写成 `T32/T41` 之后的 program automation 总闭环

## 已锁定决策

- `program integrate --execute` 继续只做 bounded execute gate / recheck handoff / remediation honesty，不默认触发 remediation execute
- `program remediate --execute --yes` 继续是显式确认的 bounded remediation entrypoint
- remediation runtime 只允许调度已知 command，其中 governance materialization 通过 `uv run ai-sdlc rules materialize-frontend-mvp` 被正式消费
- remediation writeback 继续只记录 bounded execute 的 canonical truth，不前推到 provider runtime 或 cross-spec code writeback
- `131` 只把现有 passing runtime 写实为 closure slice；后续扩链留给 `T32`、`T41` 及其后继任务

## 功能需求

| ID | 需求 |
|----|------|
| FR-131-001 | `131` 必须明确 `ProgramService.build_integration_dry_run()` 与 `program integrate --execute` 已满足 `020` 所要求的 execute preflight / recheck handoff runtime |
| FR-131-002 | `131` 必须明确 `ProgramService._build_frontend_remediation_input()` 与 `build_frontend_remediation_runbook()` 已满足 `021` 所要求的 remediation input packaging / runbook truth |
| FR-131-003 | `131` 必须明确 `PROGRAM_FRONTEND_GOVERNANCE_MATERIALIZE_COMMAND` 与 `_execute_known_frontend_remediation_command()` 已满足 `022` 所要求的 materialization command runtime consumer |
| FR-131-004 | `131` 必须明确 `execute_frontend_remediation_runbook()` 已满足 `023` 所要求的 bounded remediation execute / follow-up verification |
| FR-131-005 | `131` 必须明确 `write_frontend_remediation_writeback_artifact()` 与 `program remediate --execute` 已满足 `024` 所要求的 canonical writeback artifact surface |
| FR-131-006 | `131` 必须回链 `120/T31`，让抽象 implementation carrier 升级为正式工单 |
| FR-131-007 | `131` 必须用 focused verification 证明 execute/remediation/materialization/writeback 当前 runtime 一致 |

## Exit Criteria

- **SC-131-001**：reviewer 可以从 `131` 直接读出 `019-024` 已从 orchestration baseline 进入可执行 program runtime
- **SC-131-002**：`120/T31` 不再停留在抽象 implementation carrier 占位
- **SC-131-003**：focused verification 能证明 `T31` 当前缺口主要是 formal carrier 缺失，而非 execute/remediation/materialization 主线未实现

---
related_doc:
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
  - "specs/021-frontend-program-remediation-runtime-baseline/spec.md"
  - "specs/022-frontend-governance-materialization-runtime-baseline/spec.md"
  - "specs/023-frontend-program-bounded-remediation-execute-baseline/spec.md"
  - "specs/024-frontend-program-bounded-remediation-writeback-baseline/spec.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
