# Tasks — 130 Frontend Evidence Class Writeback Close-Check Runtime Closure

## Batch A：Closure inventory

### Task 130.1 将现有 writeback / close-check / backfill runtime 收束为 T24 carrier

- 盘点 explicit program-level mirror writer
- 盘点 close-check late resurfacing runtime
- 盘点 runtime reality sync 与 backfill closeout

## Batch B：Focused verification

### Task 130.2 证明 close-check / explicit sync / backfill 当前一致

- 运行：
  - `uv run pytest tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_program.py -q`

## Batch C：Formal 回链与评审

### Task 130.3 回填 backlog 并完成对抗评审

- 将 `120/T24` 的建议派生工单升级为正式 `130`
- 用两位 reviewer 确认当前 carrier 与现有 runtime 一致
