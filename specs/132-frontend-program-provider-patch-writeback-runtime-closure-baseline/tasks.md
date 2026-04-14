# Tasks — 132 Frontend Program Provider, Patch Apply And Cross-Spec Writeback Runtime Closure

## Batch A：Runtime closure implementation

### Task 132.1 将 provider/apply/writeback 从 deferred baseline 推进到真实执行链

- 让 `program provider-runtime --execute --yes` 生成真实 patch summaries
- 让 `program provider-patch-apply --execute --yes` 写出受控 step files
- 让 `program cross-spec-writeback --execute --yes` 写出各 spec 的 canonical writeback receipt

## Batch B：Focused verification

### Task 132.2 证明 provider/apply/writeback 当前一致

- 运行：
  - `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program validate`

## Batch C：Formal 回链与评审

### Task 132.3 回填 backlog 并完成对抗评审

- 将 `120/T32` 的建议派生工单升级为正式 `132`
- 回填 `T31/T32` 的派生状态与剩余下游依赖
- 用两位 reviewer 确认当前 carrier、实现与现有 runtime 一致
