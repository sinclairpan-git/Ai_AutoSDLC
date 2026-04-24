# Development Summary

- browser gate 现在具备了真实的 visual regression lane：可以基于 `matrix_id` 和 viewport truth 读取 baseline、执行 deterministic screenshot compare、产出 diff artifact，并让 `visual_verdict` 由 visual regression 结果主导。
- managed frontend 依赖链路已经打通，`playwright`、`pixelmatch`、`pngjs` 会在真实 workspace 中被解析和使用，baseline 缺失时会诚实落到 `evidence_missing`，baseline 存在且 diff 在阈值内时会通过。
- runtime artifact ref 已统一回到仓库相对路径约定，`program status`、truth ledger 和 dry-run 不再因为 `artifact:` 前缀而把已通过的 browser gate 误报成 `scope or linkage invalid`。
- `178` 已补齐 formal docs，并在 manifest / source inventory 中被正式接纳，不再以缺失 `plan/tasks/execution/close` 文档的形式挂在 truth inventory 上。
