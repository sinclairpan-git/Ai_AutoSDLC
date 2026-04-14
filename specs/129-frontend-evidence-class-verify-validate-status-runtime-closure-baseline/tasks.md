# Tasks — 129 Frontend Evidence Class Verify Validate Status Runtime Closure

## Batch A：Closure inventory

### Task 129.1 将现有 runtime truth 收束为 T23 carrier

- 盘点 `verify constraints` 的 authoring malformed 检测
- 盘点 `program validate` 的 mirror drift 检测
- 盘点 `program status` / `status --json` 的 bounded summary 实现
- 盘点 `107/108` 的 readiness/backfill 与当前 truth-order 的衔接

## Batch B：Focused verification

### Task 129.2 证明 verify / validate / status 当前一致

- 运行：
  - `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_program.py tests/integration/test_cli_status.py -q`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program validate`

## Batch C：Formal 回链与评审

### Task 129.3 回填 backlog 并完成对抗评审

- 将 `120/T23` 的建议派生工单升级为正式 `129`
- 用两位 reviewer 确认当前 carrier 与现有 runtime 一致
