# Tasks — 131 Frontend Program Execute, Remediation And Materialization Runtime Closure

## Batch A：Closure inventory

### Task 131.1 将现有 execute / remediation / materialization runtime 收束为 T31 carrier

- 盘点 `program integrate --execute` 的 frontend preflight / recheck handoff
- 盘点 remediation input -> runbook -> bounded execute -> writeback artifact
- 盘点 `rules materialize-frontend-mvp` 作为 runtime consumer 的正式接线

## Batch B：Focused verification

### Task 131.2 证明 execute / remediation / materialization 当前一致

- 运行：
  - `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`

## Batch C：Formal 回链与评审

### Task 131.3 回填 backlog 并完成对抗评审

- 将 `120/T31` 的建议派生工单升级为正式 `131`
- 修正 `120` 中遗留的 `T25 -> T31` 编号漂移
- 用两位 reviewer 确认当前 carrier 与现有 runtime 一致
