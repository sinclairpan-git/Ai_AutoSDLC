# 开发总结：161-close-dry-run-program-truth-parity-baseline

**功能编号**：`161-close-dry-run-program-truth-parity-baseline`
**收口状态**：`parity-restored / docs-synced`

## 交付摘要

- `SDLCRunner` 的 close dry-run 现在会继续把 program truth 带入 `run_close_check()`，不再出现 dry-run PASS 而 live close 仍被 stale truth 拦截的分叉。
- dry-run 仍然不会启用独立 `_program_truth_gate_surface()`，所以本次修复只补齐 close-check fanout，不扩大审计面。
- 已补充单元测试与 CLI 集成测试，分别锁定 runner 参数层和用户可见结果层。
